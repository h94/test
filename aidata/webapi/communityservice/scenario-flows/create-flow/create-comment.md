# 發布文章留言

## 1. 場景目的

會員在指定社群文章下發布留言，系統將留言內容寫入 Cassandra `comments` table，並同步更新 MeiliSearch 中該文章的 `total_comment` 數量，以保持搜尋索引與實際留言數一致。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/community/{game_type}/articles/{id}/comments` | 發布文章留言 |

---

## 3. 流程總覽

1. 接收已驗證 authkey 的 request
2. 解析 path parameter 取得 `game_type` 與文章 `id`
3. 驗證 `id` 格式（22 位字母數字）
4. 檢查使用者禁言狀態（由外部服務負責）
5. 產生留言 comment_id（UUID）
6. 寫入 Cassandra `community.comments` table
7. 將文章 `id` 與 `total_comment` 更新至 MeiliSearch `community` 索引
8. 回傳新建立的留言資料

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | CommentController.create_comment | 接收 request，提取 authkey、game_type、文章 id 與留言內容 |
| 2 | Validator | CommentSchema | 驗證留言內容不為空、長度限制 |
| 3 | Service | CommentService.create_comment | 組合參數，調用 Provider 寫入 Cassandra |
| 4 | Provider | CommentProvider.add_comment | 寫入 `community.comments`，若失敗拋出異常 |
| 5 | Service | CommentService.sync_meilisearch_comment_count | 調用 Provider 更新 MeiliSearch 文章索引的 `total_comment` |
| 6 | Provider | ArticleProvider.update_meilisearch_article | 取得當前文章文件，遞增 `total_comment` 後 PUT 回 MeiliSearch |
| 7 | Controller | CommentController.create_comment | 回傳 HTTP 200 及新留言 JSON |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `community.comments` | Write | 儲存新留言主體 |
| Search Index | MeiliSearch `community` | Read / Write | 先 GET 文章文件，遞增 `total_comment` 後再 PUT 更新 |
| Log Queue | Kafka（TCZB Logger） | Publish | 記錄操作日誌，非業務流程強依賴 |

註：community 無使用 Redis 快取。

---

## 6. 重要規則

- **權限限制**：
  - `authkey` 須已通過外部 auth service 驗證，communityservice 不自行處理 token 驗證
  - 需人工確認：禁言檢查是否於 communityservice 內執行，或由閘道層攔截
- **欄位限制**：
  - 文章 `id` 須為 22 位字母數字格式
  - 留言內容不可為空，長度上限需人工確認（推測 500 字，建議從 code 確認）
- **不可暴露資料**：
  - 對外回傳的 `account` 欄位須遮蔽（如 `name***`），不可回傳完整帳號；comment schema 中若無 account 欄位則此條不適用
- **TTL 規則**：
  - 無 Redis，MeiliSearch 索引視為永久保留
- **Transaction 規則**：
  - Cassandra 寫入與 MeiliSearch 更新為非交易性操作；若 MeiliSearch 更新失敗，Cassandra 中的留言仍存在，可能造成 `total_comment` 不一致，屬高風險行為
- **Retry 規則**：
  - 需人工確認：MeiliSearch 更新失敗是否有 retry 或補償機制
- **狀態值限制**：
  - 新留言預設狀態為可見，無需 `status` 欄位（需人工確認 comment table schema 是否包含 status）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 文章 `id` 格式不符（非 22 位字母數字） | 回傳 422 錯誤，拒絶寫入 |
| 留言內容為空或超長 | 回傳 422 錯誤 |
| Cassandra `comments` 寫入失敗 | 回傳 500 錯誤，MeiliSearch 不更新 |
| MeiliSearch 更新失敗 | 回傳 200 成功（Cassandra 已寫入），但 `total_comment` 不一致；需人工確認是否有後續修正或錯誤日誌警示 |
| 使用者被禁言 | 預期回傳 403 Forbidden（需人工確認由 communityservice 還是閘道攔截） |
| 文章不存在於 Cassandra `articles` | 需人工確認：目前流程未檢查文章是否存在，可能允許對不存在文章留言 → 建議新增驗證 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 正常發布留言，內容合法 | 回傳 200，Cassandra 與 MeiliSearch 正確更新 |
| TC02 | API Test | 留言內容為空字串 | 回傳 422 |
| TC03 | API Test | 文章 `id` 格式錯誤 | 回傳 422 |
| TC04 | API Test | 不帶 authkey header | 預期閘道攔截，回傳 401 |
| TC05 | Flow Test | Cassandra 寫入成功，MeiliSearch 更新失敗 | Cassandra 有留言，MeiliSearch `total_comment` 未變，需確認系統行為（目前 code 推測不回滾 Cassandra，建議確認） |
| TC06 | Permission Test | 被禁言使用者發留言 | 預期回傳 403 |

---

## 9. 高風險區域

- **高風險 table**：
  - `community.comments`：大量寫入，需注意 Cassandra partition key 設計是否造成熱點
- **跨服務資料同步**：
  - Cassandra ↔ MeiliSearch：非交易性更新，`total_comment` 可能與實際留言數不一致
- **Transaction**：
  - 無跨儲存 transaction，需人工確認補償或 reconciliation 機制
- **Cache consistency**：
  - 無 Redis，無快取一致性風險
- **Queue retry**：
  - 不涉及 Queue
- **Idempotency**：
  - 需人工確認：是否在同一文章重複發送相同內容時允許建立多筆留言，或應有冪等機制

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 忘記檢查文章是否真實存在，直接寫入 comments
  - 直接回傳 `account` 完整帳號而非遮蔽
- **AI 容易誤解**：
  - 誤認為 comments 寫入與 MeiliSearch 更新在同一個 transaction 中
  - 誤認為 community 有使用 Redis 快取留言數
- **常見漏檢查項目**：
  - 文章 id 格式驗證
  - 留言內容長度限制
- **常見錯誤流程**：
  - Cassandra 寫入失敗後仍嘗試更新 MeiliSearch（應依賴 Cassandra 寫入結果決定是否繼續）
  - MeiliSearch 更新失敗時未記錄足夠 log，導致後續難以排查 `total_comment` 不一致

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README：POST `/api/community/{game_type}/articles/{id}/comments` |
| DB | `community` keyspace 含 `comments` table（README + detail doc） |
| Search Index | MeiliSearch `community` 索引（README） |
| Code | CommentService.create_comment（推測，需人工確認實際 class/method） |
| Redis | 無（README + detail doc 明確指出 community 無 Redis 快取） |
| 權限 | communityservice 僅接收已驗證 authkey（detail doc） |