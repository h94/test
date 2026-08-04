# 列出球種警示來源設定

## 1. 場景目的

提供一個唯讀查詢端點，回傳系統內所有球種的主要資料來源 (`primary_source`) 與次要資料來源 (`secondary_sources`) 設定。這些設定決定了各球種（如足球、籃球）的賠率異常監控警示必須參照哪些上游數據。此流程僅涉及讀取 `sport_alert_sources` 資料表，不涉及任何寫入、快取或佇列操作。

---

## 2. 入口 API

需人工確認：提供的 OpenAPI 片段未明確包含 `sport_alert_sources` 的路徑。根據其餘設定（如 `monitored_play_modes`、`source_type`）的命名慣例，預測如下。

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/sport_alert_sources` | 列出所有球種的主要與次要警示來源設定。可能支援以 `game_type` 查詢參數篩選單一球種。 |

---

## 3. 流程總覽

1. 客戶端發送 GET 請求至 `/api/sport_alert_sources`（可選帶 `game_type` 查詢參數）。
2. Resource 層接收請求，並將查詢參數傳遞至 Service 層。
3. Service 層呼叫 Provider 層執行查詢。
4. Provider 層執行 SQL 查詢 `sport_alert_sources` 資料表。
   - 若提供 `game_type`，則加入 `WHERE game_type = $1`。
   - 若未提供，則查詢全表。
5. Provider 層將查詢結果（Row 物件或字典列表）回傳給 Service 層。
6. Service 層進行必要的資料轉換（例如將 `secondary_sources` 從 JSON 字串反序列化為列表）。
7. Service 層將格式化後的列表回傳給 Resource 層。
8. Resource 層包裝為 HTTP 200 JSON 回應並回傳給客戶端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SportAlertSourcesResource` (推測) | 接收 GET 請求與查詢參數 `game_type`，呼叫 Service 層的 `list_sources` 方法。 |
| 2 | Service | `SportAlertSourcesService.list_all(game_type)` | 接收查詢參數，呼叫 Provider 層的 `list_all` 方法。將 Provider 回傳的資料轉換為 DTO 列表後回傳。 |
| 3 | Provider | `sport_alert_sources.py:list_all` | 使用 `asyncpg` 或 `psycopg2` 連線池執行查詢，並返回原始資料。 |
| 4 | Transfer | (待確認) | 可能定義 `SportAlertSourceDTO` 用於序列化。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `sport_alert_sources` | Read | 讀取所有或指定球種的主要與次要警示來源設定。 |
| Redis | - | - | 此查詢流程未使用快取。 |
| Kafka / Queue | - | - | 此查詢流程未涉及任何佇列操作。 |

---

## 6. 重要規則

- **唯讀操作**：此 API 僅提供查詢功能，不進行任何狀態變更。
- **欄位限制**：回傳的 `secondary_sources` 應為 JSON 陣列，而非原始字串。
- **權限**：需人工確認此端點的權限要求。根據其他設定 API 的規則，可能僅限後台管理員存取。
- **不可暴露資料**：無。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 查詢的 `game_type` 不存在 | 回傳 HTTP 200 與空陣列 `[]`。 |
| 資料庫連線失敗或查詢逾時 | 回傳 HTTP 500 Internal Server Error。 |
| 資料庫回傳格式異常（如 `secondary_sources` 無法解析） | 取決於 Service 層錯誤處理，預期回傳 HTTP 500 或記錄錯誤後回傳部分資料。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SAS-GET-ALL | API Test | 不帶任何參數呼叫端點。 | HTTP 200，回應體為包含所有球種來源設定的 JSON 陣列。 |
| SAS-GET-FILTER | API Test | 帶 `?game_type=soccer` 呼叫端點。 | HTTP 200，回應體為僅包含 `soccer` 設定的 JSON 陣列。 |
| SAS-GET-NONE | API Test | 帶 `?game_type=unknown` 呼叫端點。 | HTTP 200，回應體為空陣列 `[]`。 |
| SAS-FLOW | Integration Test | 預先於 `sport_alert_sources` 寫入測試資料後呼叫。 | 驗證回傳的 `game_type`、`primary_source`、`secondary_sources` 與寫入資料完全一致。 |
| SAS-PERM | Permission Test | 使用無權限的帳號呼叫端點。 | （需人工確認）預期 HTTP 403 Forbidden。 |

---

## 9. 高風險區域

- 無明顯高風險。此為簡單的唯讀操作。
- **資料一致性**：無 Cache 機制，因此不會有 Cache 不一致的風險。資料即時性完全依賴資料庫。

---

## 10. 常見錯誤

- **新人容易犯錯**：誤解 `secondary_sources` 為字串而非列表。在處理 Provider 回傳的 Row 物件時，忘記對 `JSONB` 欄位進行反序列化。
- **AI 容易誤解**：誤以為此端點需要 Redis 快取或 Kafka 發送。根據系統中其他設定 API 的實作模式，這是個簡單的查詢。
- **常見漏檢查項目**：忘記驗證 `game_type` 參數是否包含特殊字元或大小寫問題，可能導致意外查詢失敗。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB Schema | `sport_alert_sources` 資料表定義於 `migrations/001_create_core_tables.sql`，含 `game_type`, `primary_source`, `secondary_sources` 欄位。 |
| Provider | `sport_alert_sources.py:list_all` 提供 `sport_alert_sources` 表的查詢邏輯。 |
| API Definition | 需人工確認 OpenAPI 路徑。 |
| Controller/Service | 需人工確認對應的 `Resources/` 和 `Service/` 程式碼路徑。 |