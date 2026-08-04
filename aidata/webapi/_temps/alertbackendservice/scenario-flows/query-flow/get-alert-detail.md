# 查詢警示詳情

## 1. 場景目的
提供單一警示記錄的完整內容查詢，包含基本欄位以及三個關鍵 JSONB 資料：`detail`（警示詳細內容）、`threshold_snapshot`（觸發時的閥值快照）、`game_info`（賽事補充資訊）。此查詢為唯讀操作，不變更任何資料。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/alerts/{alert_id}` | 查詢指定 alert_id 的完整警示資訊 |

---

## 3. 流程總覽
1. 客戶端以 `alert_id` 發起 GET 請求。
2. API 層接收 `alert_id` 並傳遞至服務層。
3. 服務層查詢 `alerts` 資料表，返回該 ID 的完整記錄（所有欄位）。
4. 若無匹配記錄，返回 404 錯誤。
5. 若有匹配記錄，將資料庫查詢結果轉換為回應格式並返回。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `Resources/Alerts.py`（預期） | 接收 GET 請求，提取 `alert_id` 路徑參數 |
| 2 | Service | `Service/Alerts.py`（預期） | 呼叫 Provider 層查詢單筆警示 |
| 3 | Provider | `Provider/Alerts.py`（預期） | 執行 SQL：`SELECT * FROM alerts WHERE id = $1` |
| 4 | Transfer | `Resources/Alerts.py`（預期） | 將查詢結果序列化為 JSON response |

> **需人工確認**：具體的類別與方法名稱需依據實際原始碼路徑（`Resources/Alerts.py`、`Service/Alerts.py`、`Provider/Alerts.py`）進行確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `alerts` | Read | 依主鍵 `id` 查詢單筆警示記錄 |

* 此查詢流程未使用 Redis 快取、Kafka 或其他訊息佇列。

---

## 6. 重要規則
- **主鍵格式**：`alert_id` 為 shortuuid 格式（VARCHAR(22)）。
- **回傳欄位**：必須回傳所有基本欄位，包含三個 JSONB 欄位（`detail`、`threshold_snapshot`、`game_info`）。
- **唯讀操作**：此 API 為 GET 方法，不得觸發任何資料變更、Webhook 通知或事件記錄。
- **權限限制**：上下文未明確說明此端點的權限驗證機制。**需人工確認**是否需要驗證操作者身份。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `alert_id` 不存在於 `alerts` 表中 | 返回 404 Not Found，回應內容**需人工確認** |
| 資料庫連線失敗或查詢逾時 | 返回 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| GET-ALERT-001 | API Test | 以存在的 `alert_id` 發送請求 | 200 OK，回應包含 `detail`、`threshold_snapshot`、`game_info` 等完整欄位 |
| GET-ALERT-002 | API Test | 以不存在的 `alert_id` 發送請求 | 404 Not Found |
| GET-ALERT-003 | Flow Test | 查詢一筆包含 JSONB 資料的警示 | 回應中的 `detail`、`threshold_snapshot`、`game_info` 為有效 JSON 結構 |

---

## 9. 高風險區域
- **無**：此操作為簡單的單表主鍵查詢，不涉及跨服務同步、交易（Transaction）或資料異動，風險極低。

---

## 10. 常見錯誤
- **誤解回應格式**：誤以為查詢警示清單（Search Alerts）的回應也包含 `detail` 等 JSONB 欄位。根據 OpenAPI 描述，清單查詢不包含這些大型欄位，此 API 才是取得完整內容的唯一途徑。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `openapi.json` -> `paths./api/alerts/{alert_id}.get` |
| DB | `migrations/001_create_core_tables.sql` -> `alerts` 表結構 |
| DB Fields | `dbschema detail` -> `alerts.id`, `alerts.detail`, `alerts.threshold_snapshot`, `alerts.game_info` |
| Code | `Provider/Alerts.py`（預期） -> 執行查詢 |
| Code | `Resources/Alerts.py`（預期） -> 定義路由與回應模型 |