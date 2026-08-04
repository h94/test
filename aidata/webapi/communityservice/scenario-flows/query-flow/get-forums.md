# 查詢所有論壇看板

## 1. 場景目的
讓已驗證的使用者查詢所有已啟用（`status=1`）的新彩票論壇看板列表，並可選擇性地依國家代碼（`country_code`）過濾結果，以利前端顯示可瀏覽的討論區。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/newlottery/forums` | 查詢啟用中的新彩票論壇看板。支援選填 query `country_code`。 |

- 需要驗證：✅（需帶入有效的 `authkey`）
- 權限角色：`player` / `admin`（所有已登入使用者）

---

## 3. 流程總覽

1. API Gateway 將請求轉發至 communityservice，並注入 `authkey`。
2. communityservice 驗證 `authkey` 有效性（由 auth / member service 負責，communityservice 僅檢查其存在性，具體驗證結果依賴上游網關）。
3. communityservice 從 Cassandra `community` keyspace 中的 `newlottery_forums` 表查詢論壇資料。
4. 過濾條件：
   - **必定條件**：`status = 1`（只回傳啟用看板）。
   - **選填條件**：若請求中包含 `country_code`，則加上該過濾條件。
5. 遮蔽 `authkey` 相關欄位（若存在於回傳結構）後，直接回傳查詢結果列表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `newlottery.forums.ForumsController.get_forums` | 接收 GET 請求，提取 query `country_code`；透過 flask-smorest 的 `@blp.response(200, ForumsSchema(many=True))` 定義回應結構。 |
| 2 | Service | `NewLotteryService.get_forums` | 組合查詢條件，調用 Provider 層讀取論壇列表。執行讀取規則。 |
| 3 | Provider | `NewLotteryForumProvider.get_enabled_forums` | 實作 Cassandra CQL 查詢：`SELECT id, country_code, icon, names, status FROM community.newlottery_forums WHERE status=1;`。若 `country_code` 不為空，附加 `AND country_code=?`。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Cassandra | `community.newlottery_forums` | Read | 查詢 `id`, `country_code`, `icon`, `names`, `status` 等欄位。 |
| Redis | `community:*` | 未使用 | 根據 communityservice 細則，此流程無 Redis 快取。 |
| Kafka | 日誌主題 | 未使用於此流程 | 僅作為服務日誌傳送，不影響業務流程。 |

---

## 6. 重要規則

- **權限限制**：
  - 所有已登入使用者均可呼叫此 API。
- **讀取規則**：
  - 一律過濾 `status = 1`（啟用）的看板，不可回傳已隱藏（`status = 0`）的看板。
  - 支援以 `country_code` 過濾（可為空，表示不限制國家）。
- **欄位規則**：
  - **不可暴露欄位**：對外 API 不可回傳 `edit_timestamp`（內部維護用）及原始 `user` (authkey)。
  - **多語言處理**：`names` 為 `map<text, text>`，查詢時直接回傳完整 map，前端依使用者語系選擇對應名稱。
- **Transaction 規則**：單一查詢，無跨表事務。
- **Retry 規則**：Cassandra 查詢失敗時由 flask-smorest 框架返回 500；無自動重試，由客戶端處理。
- **狀態值限制**：`status` 只允許 `0`（停用/隱藏）或 `1`（啟用）；本 API 只回傳 `status=1`。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| authkey 缺失或無效 | 由 API Gateway 攔截，回傳 `401 Unauthorized`。 |
| 資料庫中沒有任何 `status=1` 的看板 | 回傳空陣列 `[]` 與 `200 OK`。 |
| 指定的 `country_code` 無對應看板 | 回傳空陣列 `[]` 與 `200 OK`。 |
| Cassandra 連線失敗或超時 | 回傳 `500 Internal Server Error`，並記錄錯誤日誌至 Kafka。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC-FORUM-01 | API Test | 不帶 `country_code` 查詢所有啟用看板 | `200 OK`，回傳所有 `status=1` 的看板列表。 |
| TC-FORUM-02 | API Test | 帶合法 `country_code` (如 `"tw"`) 查詢 | `200 OK`，僅回傳 `country_code` 為 `"tw"` 且 `status=1` 的看板。 |
| TC-FORUM-03 | API Test | 查詢無看板的國家代碼 | `200 OK`，回傳 `[]`。 |
| TC-FORUM-04 | Auth Test | 未帶 authkey 請求 | `401 Unauthorized`。 |
| TC-FORUM-05 | Flow Test | 資料庫同時存在 `status=1` 和 `status=0` 的看板 | 只回傳 `status=1` 的看板。 |
| TC-FORUM-06 | Data Test | 驗證回傳的 `names` map 內容 | 應包含多語系 key，且每個 key 有對應名稱。 |

---

## 9. 高風險區域

- **高風險 Table**：無寫入操作，讀取風險低。
- **高風險 API**：無。
- **跨服務資料同步**：無。此場景僅讀取 `community` keyspace。
- **Transaction**：無。
- **Cache consistency**：無 Redis 快取，無一致性風險。
- **Queue retry**：無。
- **Idempotency**：`GET` 請求天生冪等。

---

## 10. 常見錯誤

- ❌ 忘記過濾 `status=1`，導致前端顯示被後台隱藏的看板。
- ❌ 回傳了 `edit_timestamp` 或內部 `user` 等不必要欄位，違反數據安全規則。
- ❌ 將 `country_code` 當作必填參數，導致無法查詢全域看板。
- ❌ 認為此 API 需要 Redis 快取，進行了錯誤的快取設計（根據現有文件，此場景無快取）。
- ❌ 前端直接將 `names` map 整份顯示，而未根據使用者語系選擇 key，導致顯示 `object Object` 之類的錯誤。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由 | README.md: `GET /api/newlottery/forums` |
| API 用途 | README.md: 新彩票論壇表格，說明為「查詢所有論壇看板」 |
| DB Table | `community.newlottery_forums` 於 `db/community.md` |
| 讀取規則 | `community-detail.md`：論壇列表查詢僅回傳 `status=1`，可選依 `country_code` 過濾。 |
| 多語言欄位 | `community.newlottery_forums` 的 `names` 欄位（map<text, text>）於 `db/community.md`。 |
| 不可回傳欄位 | `community-detail.md`：對外 API 不可回傳 `user`(authkey) 與 `edit_timestamp`。 |
| 無 Redis 快取 | `webapi/communityservice/communityservice-detail.md`：community 無使用 Redis 快取。 |