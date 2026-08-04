# 查詢主題留言列表

## 1. 場景目的

此場景用於新彩票社群前台，使用者進入特定討論主題後，系統需回傳該主題下所有「公開」且「未隱藏」的留言，以建立討論串內容。查詢結果須對發文者帳號進行去識別化處理，確保個資不外洩。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/newlottery/subjects/{subject_id}/comments` | 查詢指定主題下的留言列表 |

---

## 3. 流程總覽

1. 前端請求送達，攜帶 `subject_id` 路徑參數與 `authKey` 驗證資訊。
2. 權限驗證：確認請求者為合法登入使用者（`authKey` 有效）。
3. 搜尋查詢：以 `subject_id` 為主要過濾條件，並附加 `status=1`（公開）條件查詢 `newlottery_comments` 索引。
4. 結果處理：將查詢結果中的 `account` 欄位進行遮蔽處理。
5. 回傳處理後的留言列表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `NewlotteryController.GetSubjectComments` | 接收請求，解析 `subject_id`，呼叫服務層 |
| 2 | Service | `NewlotteryService.GetCommentsBySubjectId` | 協調查詢與資料處理邏輯 |
| 3 | Repository | `MeiliSearchRepository.Search` | 對 `newlottery_comments` 索引執行搜尋 |
| 4 | Service | `NewlotteryService.GetCommentsBySubjectId` | 處理查詢結果：遮蔽帳號、排序、分頁（若有） |
| 5 | Controller | `NewlotteryController.GetSubjectComments` | 封裝並回傳處理後的留言列表 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| MeiliSearch | `newlottery_comments` 索引 | Read | 查詢符合 `subject_id` 且 `status=1` 的留言資料 |
| Redis / Cache | 無 | - | 根據 [Service detail]，此服務無使用 Redis 快取。 |

---

## 6. 重要規則

- **權限限制**：所有對外API皆需要驗證，僅允許已登入使用者查詢。
- **狀態過濾**：必須過濾 `newlottery_comments_index.status=1`（公開），隱藏的留言 (`status=0`) 不應回傳。 (Evidence: `db-usage` 文件「查詢主題留言」)
- **帳號遮蔽**：對外列表（非個人頁面）時，`account` 欄位須遮蔽（如 `name***`），不可回傳完整帳號。 (Evidence: `db-usage` 文件「不可回傳欄位」與「讀取規則」)
- **不可暴露資料**：
    - 不可回傳 `user` (authkey)。 (Evidence: `db-usage` 文件「不可回傳欄位」)
    - 不可回傳完整 `account`。
- **排序規則**：資料依建立時間 (`create_timestamp`) 或 `last_comment_timestamp` 排序，具體由前端或 API 參數決定。需人工確認。
- **使用者黑名單/隱藏過濾**：若使用者已隱藏特定討論串或留言，查詢時應在應用層過濾 (`hidden=true` 的不顯示)，此過濾不在資料庫層處理。 (Evidence: `db-usage` 文件「讀取規則」)

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| subject_id 不存在 | 回傳空列表或明確的「主題不存在」錯誤訊息。需人工確認確切行為。 |
| 請求方未登入或 `authKey` 無效 | 回傳 HTTP 401 Unauthorized。 |
| 查詢的 MeiliSearch 索引 `newlottery_comments` 中斷或逾時 | 回傳 HTTP 500 Internal Server Error。 |
| 主題 `status=0` (隱藏) | 回傳空列表或明確的錯誤訊息。需人工確認確切行為。 |
| 留言內容包含使用者被禁言的關鍵字 | 不應在前端顯示該留言，或在查詢結果中將其標記為已隱藏。需人工確認過濾時機。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| QT-01 | API Test | 驗證特定 `subject_id` 能成功回傳留言列表 | 狀態碼 200，回應體為符合規格的留言列表 |
| QT-02 | Permission Test | 未攜帶有效的 access token 請求 | 狀態碼 401 Unauthorized |
| QT-03 | Flow Test | 驗證留言列表不包含 `status=0` 的留言 | 回傳的留言列表中，所有物件皆為公開狀態 |
| QT-04 | Data Test | 驗證留言列表中的帳號已被遮蔽 | 回應體中的 `account` 欄位格式為 `test***` 而非完整帳號 |
| QT-05 | API Test | 請求不存在的 `subject_id` | 回傳 HTTP 404 或空列表 (需依規格明確定義) |

---

## 9. 高風險區域

- **資料一致性**：MeiliSearch 索引與 Cassandra 主資料庫的同步延遲，可能導致剛發布的留言無法立即查詢到。
- **大量留言**：若某主題留言數極多，未實作分頁或限制最大回傳數量的查詢，可能導致 API 回應緩慢甚至逾時。需人工確認是否有分頁機制。

---

## 10. 常見錯誤

- ❌ **未過濾 `status`**：查詢時只使用 `subject_id` 過濾，導致回傳了包含隱藏（`status=0`）的留言。
- ❌ **直接回傳原始帳號**：忘記對 `account` 欄位進行遮蔽處理，導致個資外洩。
- ❌ **誤用或不實作快取**：由於文件標示無快取使用，若開發者自行加入快取機制卻未妥善設計失效策略，將導致資料不一致。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `GET /api/newlottery/subjects/{subject_id}/comments` (README.md) |
| DB | `newlottery_comments` index in MeiliSearch (README.md) |
| 規則 | `db-usage` 文件：`newlottery_comments_index` 讀取規則、不可回傳欄位 |
| 流程 | 基於 `Service detail` 與 `Code semantics` 推斷。確切類別與方法名需人工確認。 |