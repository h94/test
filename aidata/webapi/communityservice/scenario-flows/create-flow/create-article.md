# 發布社群文章

## 1. 場景目的

會員於前台體育社群頁面發佈一篇賽事預測／競猜文章，系統將其內容寫入 Cassandra `community.articles` 進行持久化儲存，並同步建立 MeiliSearch 索引以供後續快速查詢與篩選，同時支援 HashTag 關聯與潛在的圖片上傳流程。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/community/{game_type}/articles` | 發佈社群文章，需驗證 |

---

## 3. 流程總覽

1. 接收已授權的 `authkey` 與 `game_type`，驗證會員身份及狀態。
2. 檢查使用者是否被禁言（mute）。
3. 驗證文章內容格式（包含長度、HashTag、圖片等）。
4. 寫入文章至 Cassandra `community.articles`。
5. 將文章資料同步寫入 MeiliSearch `community` 索引。
6. 若包含 HashTag，寫入／更新相關 HashTag 關聯。
7. 若包含圖片，處理圖片上傳至 NAS（SFTP），並更新內文圖片路徑。
8. 回傳完整文章文件。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `ArticleController.CreateArticle` | 解析參數，呼叫 Service |
| 2 | Validator | （BaseSchema） | 驗證 `game_type`、`content`、`hashtags` 等欄位格式 |
| 3 | Service | `ArticleService.Create` | 組裝文章主體，呼叫權限檢查 |
| 4 | Provider | `CommunityDBProvider` | 透過 `MemberService` 驗證會員狀態（需人工確認） |
| 5 | Provider | `CommunityDBProvider` | 檢查 `mute` 禁言名單 |
| 6 | Provider | `CommunityDBProvider` | **寫入** Cassandra `community.articles` |
| 7 | Provider | `SearchProvider` | **寫入** MeiliSearch `community` 索引 |
| 8 | Provider | `CommunityDBProvider` | **寫入** HashTag 關聯（若存在） |
| 9 | Provider | `ImageProvider` | 處理圖片上傳 SFTP（若存在） |
| 10 | Controller | `ArticleController.CreateArticle` | 回傳可被前端解析的 `ArticleDocumentResponse` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `community.articles` | Write | 持久化儲存文章全文 |
| DB | Cassandra `community.comments` | — | 此步驟無操作，但屬同一領域 |
| Search | MeiliSearch `community` | Write | 建立全文搜尋與篩選索引 |
| Search | MeiliSearch `hashtag` | Write | 建立或更新文章關聯的 HashTag |
| File | NAS SFTP `/downloads/sport/img/community` | Write | 上傳文章內嵌圖片 |
| Cache | Redis | — | ReadMe 明確指出目前未使用於此場景 |
| Queue | Kafka | — | 非同步日誌（Logger），非核心流程 |

---

## 6. 重要規則

- **權限限制**：所有操作必須基於 auth / member service 已驗證的 `authkey`；communityservice 不自行做登入驗證。
- **會員狀態**：發文前需驗證會員存在且狀態正常（`gameusers.status = 1`）。需人工確認確切調用服務。
- **禁言檢查**：發文前需查詢該會員是否在特定 `game_type` 被禁言。
- **帳號遮蔽**：回傳給前端時，文章作者帳號不得直接暴露 `authkey` 或原始帳號名，需轉為 `username` 或遮蔽格式。
- **HashTag 唯一性**：寫入 MeiliSearch hashtag 索引時需處理重複與關聯。
- **圖片限制**：圖片僅允許特定格式與大小，儲存至指定 NAS 路徑，不得透過 URL 引用外部資源（需人工確認）。
- **不可修改欄位**：文章建立後，`id`、`account`（authkey）、`create_timestamp` 不可由前端覆寫。
- **內容長度**：`content` 欄位長度需符合 Cassandra 定義（需人工確認），通常為 text 型態。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未傳遞 authkey 或 authkey 無效 | 回傳 401 未授權 |
| 會員狀態非正常（停用、凍結） | 回傳 403 禁止發文 |
| 會員處於禁言狀態 | 回傳 403 權限不足，並附帶禁言結束時間 |
| `game_type` 不存在或不支援 | 回傳 422，參數錯誤 |
| 文章內容包含違反規範詞彙 | 回傳 422，並拒絕寫入 |
| Cassandra 寫入失敗或逾時 | 回傳 500，確保 MeiliSearch 未被部分寫入，觸發重試 |
| MeiliSearch 同步失敗 | 紀錄錯誤日誌，回傳 500，或根據最終一致性接受 Cassandra 成功，標記需人工修復 |
| 圖片上傳 NAS 失敗 | 回傳 400/500，拒絕文章建立，避免圖文不一致 |
| 請求速率過高 | 回傳 429，配合上游限流 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| TC-01 | API Test | 正常發文，含有效 authkey、內容、HashTag | 201，MeiliSearch 可查得 |
| TC-02 | Permission Test | 使用停用 / 凍結會員 authkey | 403，拒絕發文 |
| TC-03 | Permission Test | 遭禁言會員發文 | 403，含禁言資訊 |
| TC-04 | Validation Test | 傳入不支援的 `game_type` | 422，錯誤訊息 |
| TC-05 | Flow Test | 模擬 Cassandra 寫入失敗 | 500，MeiliSearch 無孤立記錄 |
| TC-06 | Flow Test | 模擬 MeiliSearch 寫入失敗 | 寫入 Cassandra 成功後，記錄錯誤並回傳 500 |
| TC-07 | Flow Test | 上傳無效格式圖片 | 400 拒絕，無文章產生 |
| TC-08 | Integration Test | 完整的發文讀文週期 | 透過 GET API 驗證資料完整性與一致性 |

---

## 9. 高風險區域

- **Cassandra 與 MeiliSearch 雙寫一致性**：此為最終一致性模型的核心風險。應優先確保 Cassandra 寫入成功再同步 MeiliSearch；同步失敗需有補償機制（人工或排程修復）。
- **帳號個資洩漏**：絕不可在 API 回應中直接暴露內部 `authkey` 或完整帳號，必須以顯示名稱或遮罩替代。
- **禁言機制**：需確認禁言名單的快取或查詢效能，避免因查詢不及時使得禁言會員仍可發文。
- **圖片上傳**：若為同步上傳，大檔案可能拖慢 API 響應時間，建議確認是否有非同步處理或前端直傳機制。
- **內容安全**：發文內容與 HashTag 須經敏感詞過濾，避免平台風險。

---

## 10. 常見錯誤

- ❌ 忘記檢查會員狀態與禁言，導致凍結帳號仍可發文。
- ❌ 在回傳文章時直接暴露 `authkey` 或原始帳號，導致資安破口。
- ❌ 僅寫入 Cassandra 或 MeiliSearch 其中之一，未處理失敗回滾或重試，導致查詢不到文章。
- ❌ 未正確處理 `game_type` 參數，查詢或寫入錯誤的 keyspace/索引。
- ❌ 對 MeiliSearch 的操作忽略異步結果，阻塞主流程過久。
- ❌ 圖片路徑格式未檢查，可能導致任意檔案上傳或路徑遍歷漏洞。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/community/{game_type}/articles`（ReadMe） |
| DB | Cassandra `community.articles`（ReadMe） |
| Search | MeiliSearch `community`、`hashtag` 索引（ReadMe） |
| Image | NAS SFTP `/downloads/sport/img/community`（ReadMe） |
| Auth | 依賴外部 auth / member service（communityservice-detail.md） |
| Code | （需人工審查實際 Service / Provider 以補充具體 Method） |
| Code | 程式語意僅揭示基本表單欄位，未揭露完整 Controller 流程 |