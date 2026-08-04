# 編輯留言

## 1. 場景目的

讓留言者在體育社群文章中編輯自己先前留下的留言內容，並將變更同步至 Cassandra 與 MeiliSearch 索引。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/community/{game_type}/edit_comments` | 編輯留言 |

---

## 3. 流程總覽

1. 接收 PUT request，內含 `comment_id`、`article_id`、`content` 與 `game_type`。
2. 從 request context 取得已驗證的 authkey（由上游 auth/member service 驗證）。
3. 依 `comment_id` 查詢 Cassandra `community.comments` 取得原始留言。
4. 驗證留言存在且該留言的 `author`（authkey）與當前使用者 authkey 一致，非作者不可編輯。
5. 驗證留言 `status` 為有效值（未被刪除或隱藏）。
6. 使用 `INSERT` 或更新 Cassandra `community.comments`（Cassandra 無 UPDATE 語法，應使用 INSERT 覆寫）。
7. 同步更新 MeiliSearch `community` 索引中該留言的 `content`。
8. 回傳 JSON 成功訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `CommentController.edit_comment` | 接收 PUT request，調用 Service |
| 2 | Service | `CommentService.edit_comment` | 執行主要邏輯：查詢留言、驗證身份、更新留言 |
| 3 | Service | `CommentService.edit_comment` | 調用 `CommentRepository` 查詢 Cassandra |
| 4 | Service | `CommentService.edit_comment` | 比較 `comment.author` 與當前使用者 authkey |
| 5 | Service | `CommentService.edit_comment` | 生成新的時間戳，調用 `CommentRepository` 寫入 Cassandra |
| 6 | Service | `CommentService.edit_comment` | 調用 `MeiliSearchProvider` 更新索引 |
| 7 | Transfer | `CommentTransfer` | 轉換 Cassandra model 至 API response |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | community.comments (Cassandra) | Read (SELECT) | 查詢原始留言 |
| DB | community.comments (Cassandra) | Write (INSERT) | 更新留言內容 |
| Search | MeiliSearch `community` index | Write (UPDATE) | 同步更新留言內容索引 |
| — | — | — | 本場景無使用 Redis 快取；留言查詢多以 MeiliSearch 為主，無快取需求 |

---

## 6. 重要規則

- **權限限制**：僅留言原作者（authkey 相同）可編輯；非作者應回傳 HTTP 403。
- **欄位限制**：`content` 長度不得為空，需人工確認是否有最大長度限制（DB Schema 未明確標示，需查 Table `comments` 定義）。
- **不可暴露資料**：`author`（authkey）不可對外回傳。
- **不可變更欄位**：`comment_id`、`article_id`、`author`、`addtimestamp`（原始建立時間）不可變更。
- **Transaction 規則**：Cassandra 不支援跨語句 Transaction，建議先更新 MeiliSearch，成功後再寫 Cassandra，或寫 Cassandra 後再更新 MeiliSearch（失敗時需手動補償，需**人工確認**實作優先順序）。
- **狀態值限制**：若留言存在 `status` 欄位（如 `deleted`、`hidden`），已刪除或隱藏的留言不可編輯，需回傳 HTTP 404 或 403（需**人工確認** Table `comments` 完整結構）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 留言不存在 | 回傳 404，JSON error message |
| 使用者非原作者 | 回傳 403，JSON error message |
| `content` 為空字串 | 回傳 422 驗證錯誤 |
| Cassandra 寫入失敗 | 需**人工確認**：若 MeiliSearch 已更新，可能產生資料不一致 |
| MeiliSearch 更新失敗 | 需**人工確認**：Cassandra 已寫入成功，索引與 DB 資料不同步 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SC-EDIT-01 | API Test | 正常編輯自己的留言 | 200 OK，留言內容更新 |
| SC-EDIT-02 | Permission Test | 非作者嘗試編輯他人留言 | 403 Forbidden |
| SC-EDIT-03 | Flow Test | 編輯不存在的留言 | 404 Not Found |
| SC-EDIT-04 | Flow Test | 內容為空或格式不符 | 422 Unprocessable Entity |
| SC-EDIT-05 | Integration Test | Cassandra 寫入失敗後的回滾 | 需人工確認是否含補償邏輯，應回傳 500 且避免 MeiliSearch 資料異常 |

---

## 9. 高風險區域

- **Cassandra 實體化視圖與索引一致性**：留言寫入 `community.comments` 後，需確保 MeiliSearch 同步成功。失敗時遺留髒資料。
- **Cache consistency**：雖無 Redis 快取，但 MeiliSearch 索引與 Cassandra 是同階寫入，可能出現短暫不一致。
- **Idempotency**：連續兩次相同請求可能產生兩次 MeiliSearch update，但結果一致（冪等），風險較低。

---

## 10. 常見錯誤

- 新人誤用 `comments` table 的 `UPDATE` 語法覆蓋所有欄位，應保留原始 `author`、`article_id`、`comment_id` 不變。
- 未檢查留言作者身份，直接更新導致非作者可編輯。
- 內容長度未驗證，允許空白或超長內容寫入。
- 直接回傳 `author`（authkey）欄位。
- 誤認為需要 image 上傳步驟（留言編輯通常不包含圖片，需查原始碼確認）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | PUT `/api/community/{game_type}/edit_comments`（README: 體育社群留言） |
| DB | `community.comments` (Cassandra)（README: 社群文章留言） |
| Search | `MeiliSearch community` index（README: 文章搜尋索引） |
| Code | `CommentService.edit_comment`（Phase1 code semantics, 由 Controller 調用） |
| Auth | 上游 auth/member service 驗證 authkey（communityservice-detail.md: 本服務不負責） |
| Permission | community-detail.md: comments account 遮蔽規則，暗示 author 為 authkey |