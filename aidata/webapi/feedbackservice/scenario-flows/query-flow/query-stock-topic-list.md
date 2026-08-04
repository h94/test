# 查詢股票主題列表

## 1. 場景目的

用戶於股票站點提交反饋前，需選擇一個反饋主題。此場景提供前端一個已啟用的股票反饋主題列表，資料來源為 `stock` 資料庫中的 `topics_stock` 表，查詢結果依排序欄位升冪排列。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | /api/Stock/Topics | 查詢已啟用的股票反饋主題列表 |

需人工確認：確切的 API 路由需從 Controller 定義中確認。

---

## 3. 流程總覽

1. 接收前端 GET 請求。
2. 呼叫 Service 層方法查詢主題列表。
3. Service 層透過 DataProvider 查詢 `stock.topics_stock` 表。
4. 查詢條件：`Enabled` 欄位值必須為 `1`（啟用）。
5. 結果依 `Sort` 欄位進行升冪排序。
6. 回傳主題列表，包含 `ID`、`Name`、`Sort` 等資訊。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | 需人工確認 | 接收 HTTP GET 請求 |
| 2 | Service | 需人工確認 | 呼叫查找主題方法，可能為 `GetTopics` |
| 3 | Provider | `TopicDataProvider` | 執行資料庫查詢 `SELECT id, name, sort FROM topics_stock WHERE enabled = 1` |
| 4 | Transfer | 需人工確認 | 將資料庫結果映射為 DTO 物件回傳 |

需人工確認：具體的 Controller 及 Service 類別與方法名稱。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `stock.topics_stock` | Read | 查詢所有 `enabled = 1` 的主題記錄 |
| DB | `stock.topics_stock` | Read | 讀取 `id`, `name`, `enabled`, `sort` 欄位 |

此為純查詢流程，未涉及 Redis、Kafka 或 Queue 操作。

---

## 6. 重要規則

- **查詢限制**：前端列表查詢僅顯示 `Enabled = 1` 的主題。已停用的主題不應出現在列表中。此邏輯繼承自整個系統對於 `Enabled` 欄位的一貫處理方式。
- **排序規則**：結果應根據 `Sort` 欄位進行排序，以確保前端展示順序與管理後台設定一致。
- **唯讀操作**：feedbackservice 對 `stock.topics_stock` 表僅有讀取權限，嚴禁任何 INSERT、UPDATE 或 DELETE 操作。
- **資料庫**：此場景操作的是 ScyllaDB 的 `stock` keyspace 中的 `topics_stock` 表，而非 MySQL `stock` 資料庫。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 資料庫中沒有 `enabled=1` 的主題 | 回傳空列表，不報錯 |
| 資料庫連線失敗或查詢逾時 | Service 層拋出例外，Controller 返回 HTTP 500 內部伺服器錯誤 |

需人工確認：是否需要更精細的錯誤碼與訊息處理。

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| ST-01 | API Test | 查詢所有主題，當存在多個啟用主題時 | 回傳列表包含所有 `enabled=1` 的主題，依 `sort` 升冪排列 |
| ST-02 | API Test | 查詢所有主題，當所有主題皆停用 (`enabled=0`) 時 | 回傳空陣列 `[]`，HTTP Status 200 |
| ST-03 | DB Test | 直接查詢 `topics_stock` 表 | 確認回傳的資料與 API 回傳結果一致 |
| ST-04 | Flow Test | 模擬資料庫連線失敗 | API 應返回 HTTP 500 錯誤 |

---

## 9. 高風險區域

此查詢場景風險較低，屬於單純的讀取操作。

- **無 Transaction 需求**：單一簡單查詢，不涉及跨表或跨服務的資料一致性。
- **無 Cache 一致性風險**：此流程未使用 Redis 或任何應用層快取，資料皆為即時查詢，無快取過期或不同步的問題。
- **無 Queue / Kafka 操作**：沒有任何非同步或訊息佇列的處理，不會有重試或冪等性問題。

---

## 10. 常見錯誤

- **新人容易犯錯**：查詢時忘記過濾 `Enabled = 1`，導致前端顯示出已停用的主題。
- **AI 容易誤解**：誤用 MySQL `stock` 資料庫結構，而實際上應使用 ScyllaDB 的表定義（`topics_stock`）。
- **常見漏檢查項目**：未檢查 `Sort` 欄位是否存在或為 `NULL`，可能導致排序異常。
- **常見錯誤流程**：在查詢時對 `topics_stock` 表執行寫入操作，這違反了 feedbackservice 的唯讀角色限制。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB Table | `stock.topics_stock` |
| DB Schema | `db/stock-detail.md` 中對 `topics_stock` 的說明 |
| Code (Provider) | `TopicDataProvider.cs` (根據 semantics 推斷) |
| Semantic Mapping | 查詢 `topics_stock` 表的 `enabled`, `name`, `sort` 欄位 |
| Business Rule | 所有服務的 `Enabled` 欄位處理規則，僅讀取 `Enabled=1` 的記錄 |

需人工確認：確切的 Controller 和 Service 類別名稱。