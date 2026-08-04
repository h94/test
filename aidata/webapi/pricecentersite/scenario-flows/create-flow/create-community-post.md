# 發佈社群文章

## 1. 場景目的

接收使用者提交的社群文章，經過身份驗證、內容長度驗證，並過濾已被封鎖的使用者後，將文章寫入社群資料表。此流程確保只有合法且未被封鎖的使用者可以發佈符合規範的社群內容。

---

## 2. 入口 API

**⚠️ 需人工確認**：OpenAPI 文件中未明確定義「發佈社群文章」的 API 端點。此場景根據 context 描述與 db-usage 規則推斷。

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/Community/CreatePost`（推測） | 發佈社群文章。需提供 authKey 以驗證身份。 |

---

## 3. 流程總覽

1.  接收帶有 `authKey` 的發佈文章 request。
2.  驗證 `authKey` 對應的會員是否存在且狀態為正常 (`status=1`)。
3.  檢查該會員的 `authKey` 是否存在於 `gameusers_banned` 表中，且封禁有效。
4.  驗證文章內容長度是否介於 10 到 2000 個字元之間。
5.  將文章內容寫入社群文章相關的 Cassandra 資料表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `CommunityController.CreatePost` | 接收 HTTP POST 請求。 |
| 2 | Validator | （內建或自訂） | 驗證文章內容長度。 |
| 3 | Service | `CommunityService.CreatePost` | 協調整個業務流程。 |
| 4 | Provider | `MemberProvider.GetGameUser` | 根據 `authKey` 查詢 `member.gameusers` 表。 |
| 5 | Provider | `MemberProvider.IsUserBanned` | 根據 `authKey` 查詢 `member.gameusers_banned` 表。 |
| 6 | Provider | `CommunityProvider.CreatePost` | 將文章內容寫入社群相關的 Cassandra 資料表。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `member.gameusers` | Read | 根據 `authKey` 讀取會員資料，驗證 `status=1`。 |
| DB | `member.gameusers_banned` | Read | 查詢使用者的 `authKey` 是否在封鎖清單中，且封禁 `endtime` 仍有效。 |
| DB | `community.newlottery_forums` | Read | 驗證發佈目標論壇是否存在且 `status=1`（若適用）。 |
| DB | 社群文章表（未明確） | Write | 寫入驗證通過後的社群文章內容。 |

---

## 6. 重要規則

-   **權限限制**：僅有通過驗證且狀態為正常 (`status=1`) 的會員可以發佈文章。
-   **欄位限制**：文章內容長度必須在 10 到 2000 個字元之間。
-   **不可暴露資料**：錯誤回應中不可暴露 `authKey` 或資料庫內部錯誤細節。
-   **狀態值限制**：僅有 `member.gameusers.status=1` 且不存在於 `gameusers_banned` 或尚未過期的使用者可以發文。
-   **不可修改欄位**：文章一經發佈，部分核心欄位（如作者、發佈時間）可能不允許修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 帳號不存在 (`authKey` 無效) | 回傳 `401 Unauthorized` 或 `User not found` 錯誤。 |
| 帳號已停用或凍結 (`status != 1`) | 回傳 `403 Forbidden` 或 `Account disabled` 錯誤。 |
| 使用者已被封鎖 (`gameusers_banned` 有有效記錄) | 回傳 `403 Forbidden` 或 `Account banned` 錯誤。 |
| 權限不足（非正常會員） | 回傳 `403 Forbidden`。 |
| 請求參數無效（文章內容過短或過長） | 回傳 `400 Bad Request` 並附上驗證失敗訊息。 |
| DB timeout | 回傳 `500 Internal Server Error`。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| `TC01` | Flow Test | 使用合法帳號發佈一篇長度合規的文章。 | 成功發佈，回傳 `200 OK`。 |
| `TC02` | API Test | 使用無效的 `authKey` 發文。 | 回傳 `401` 錯誤。 |
| `TC03` | Permission Test | 使用已停用帳號 (`status=0`) 發文。 | 回傳 `403` 錯誤。 |
| `TC04` | Permission Test | 使用已被封鎖的帳號發文。 | 回傳 `403` 錯誤。 |
| `TC05` | API Test | 發送內容少於 10 字的文章。 | 回傳 `400` 驗證錯誤。 |

---

## 9. 高風險區域

-   **高風險 API**：此發佈 API 可能被用於發送垃圾內容，需考慮 rate limiting。
-   **Transaction**：寫入社群文章表的操作應確保原子性，避免資料不一致。

---

## 10. 常見錯誤

-   **新人容易犯錯**：未檢查 `member.gameusers_banned` 表就直接讓通過 `status=1` 驗證的使用者發文。
-   **AI 容易誤解**：混淆 `member.gameusers.status` 和 `gameusers_banned` 的用途，誤以為 `status=1` 就代表未被封鎖。
-   **常見漏檢查項目**：忘記過濾 `gameusers_banned.endtime`，導致已過封禁期的使用者仍被拒絕發文。
-   **常見錯誤流程**：文章長度驗證放在程式流程的最前端，但未對請求來源進行基本驗證。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | 推測為 `CommunityController.CreatePost` |
| DB | `member.gameusers`, `member.gameusers_banned`, `community.newlottery_forums` |
| Code | 推測為 `CommunityService.CreatePost` |
| Rule | `pricecentersite-detail.md` > member > 讀取規則：社群文章過濾；寫入限制：社群文章內容驗證 (10-2000 字) |
| Rule | `member-detail.md` > Table：gameusers_banned > endtime 欄位 |