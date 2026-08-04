# 查詢單則留言

## 1. 場景目的

此場景提供「依據留言 ID 查詢特定留言詳細內容」的功能。使用者可以查看某一篇文章下的特定留言及其回覆，以便進行內容審核、互動或後續操作。此流程適用於「體育社群」模組。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/community/{game_type}/articles/{article_id}/comments/{comment_id}` | 查詢指定文章的特定留言詳細內容 |

---

## 3. 流程總覽

1. 客戶端透過 API Gateway 傳入 `game_type`、`article_id` 與 `comment_id`。
2. 系統驗證請求者的 `authkey`（由 auth/member service 預先驗證，communityservice 僅接收已認證的 authkey）。
3. 根據 `comment_id` 從主要儲存層（Cassandra `comments` table）讀取留言文件。
4. 依據業務規則處理資料（例如遮蔽帳號、過濾狀態），組裝回應。
5. 若留言存在且狀態合法，則回傳成功；若無此留言或無權限，則回傳對應錯誤。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `CommunityController.get_comment` | 接收 GET 請求，解析路徑參數，調用 Service。 |
| 2 | Service | `CommentService.get_comment_detail` | 接收 `game_type`, `article_id`, `comment_id`，處理業務邏輯。 |
| 3 | Provider | `CassandraProvider.get_comment_by_id` | 以 `comment_id` 查詢 Cassandra `community.comments` 表。 |
| 4 | Service | `CommentService.get_comment_detail` | 驗證留言狀態（例如 `status=1`），判斷是否需遮蔽作者帳號，並組裝 DTO。 |
| 5 | Controller | `CommunityController.get_comment` | 將 DTO 序列化為 JSON response 回傳。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB（Cassandra） | `community.comments` | Read | 依據 `comment_id` 取得留言詳細內容（包含內容、作者、狀態、時間戳、按讚數等）。 |
| DB（MeiliSearch） | `community` index | 未使用 | 此為「精確查詢」情境，不需透過搜尋引擎。 |

> **需人工確認**：目前 code evidence 中，MeiliSearch 可能快取留言資料，此情境是否需優先查詢 MeiliSearch？若無相關實作，應視為直接查 Cassandra。

---

## 6. 重要規則

- **權限限制**：
  - 所有請求都必須經過 auth/member service 驗證 `authkey`。
  - 留言若有 `is_hidden` 或 `status=0`（隱藏），只有作者或管理員可查閱。
- **欄位限制**：
  - 根據 `db-usage` 規則，對外 API 回傳的 `account` 欄位必須被遮蔽（例如 `name***`），不得暴露完整帳號。
  - 被檢舉或屏蔽的內容，一般使用者不可見。
- **不可暴露資料**：
  - `report_table` 中的檢舉狀態與被檢舉者資訊，不可在此 API 中回傳。
- **狀態值限制**：
  - 僅回傳 `status=1`（公開）的留言；若留言 `status=0` 且請求者非作者或管理員，回傳 404。
- **不可修改欄位**：
  - 此為查詢流程，無任何寫入操作。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 留言 ID 不存在或 `article_id` 不匹配 | 回應 404 Not Found。 |
| 使用者未通過驗證或未提供有效 token | 回應 401 Unauthorized。 |
| 留言 `status=0`（隱藏）且請求者非作者或管理員 | 回應 404 Not Found（或 403 Forbidden，視業務邏輯而定）。 |
| 使用者遭禁言（muted） | 仍可查閱留言，此 API 不影響。 |
| Cassandra 查詢逾時 | 回應 500 Internal Server Error，並記錄錯誤日誌。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC-01 | API Test | 以有效 `comment_id` 查詢公開留言 | 200 OK，回傳正確留言內容。 |
| TC-02 | Permission Test | 查詢自己發布的隱藏留言 | 200 OK，回傳留言內容。 |
| TC-03 | Permission Test | 查詢他人發布的隱藏留言 | 404 Not Found 或 403 Forbidden。 |
| TC-04 | API Test | 以不存在的 `comment_id` 查詢 | 404 Not Found。 |
| TC-05 | Flow Test | 未帶 token 或 token 無效 | 401 Unauthorized。 |
| TC-06 | Data Masking | 確認回應中的 `account` 欄位已遮蔽 | 回應中 `account` 顯示為 `nam***` 而非完整帳號。 |

---

## 9. 高風險區域

- **高風險 table**：`community.comments`，因其為主要讀取來源，若 partition key 設計不佳可能導致熱點。
- **高風險 API**：若此 API 未正確驗證 `article_id` 與 `comment_id` 的關聯性，攻擊者可列舉 `comment_id` 跨文章竊取留言（IDOR 漏洞）。
- **Cache consistency**：若後續為留言加入 Redis 快取，必須在留言編輯或刪除時主動失效（`DEL`）相關快取鍵，避免回傳過時或已刪除的留言。
- **Queue retry**：此為同步查詢流程，不涉及 Queue。

---

## 10. 常見錯誤

- ❌ 直接回傳 Cassandra 查詢結果，未過濾 `status=0` 的隱藏留言。
- ❌ 對外回傳留言時，`account` 欄位未被遮蔽，導致帳號資訊外洩。
- ❌ 錯誤地將 MeiliSearch 中的非結構化搜尋結果直接作為單一留言查詢的依據，忽略可能存在的索引延遲。
- ❌ 未正確區分 `game_type` 為「體育社群」或「新彩票論壇」，導致 SQL 查詢錯誤的 table。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `CommunityController.get_comment` |
| DB（Cassandra） | `community.comments` |
| DB（MeiliSearch） | `community` index（用於搜索，於此單筆查詢場景中未使用） |
| README | 路由表：`GET /api/community/{game_type}/articles/{article_id}/comments/{comment_id}` |
| db-usage | `community` 區段：讀取留言時須過濾 `status`，且對外回傳需遮蔽 `account`。 |