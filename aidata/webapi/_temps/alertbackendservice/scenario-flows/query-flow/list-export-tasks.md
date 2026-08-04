# 查詢匯出任務狀態

## 1. 場景目的

供前端或操作人員在發起匯出請求後，查詢該任務的當前執行狀態、執行進度與結果（如檔案路徑、錯誤訊息），以決定後續動作（例如：等待、重新查詢或下載結果檔案）。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| `GET` | `/alertbackendservice/api/export/task` | 查詢單一匯出任務狀態。需傳入 `task_id`。 |

---

## 3. 流程總覽

1. 接收查詢請求，取得 `task_id` 參數。
2. 驗證 `task_id` 格式（需為非空字串）。
3. 查詢 `export_tasks` 資料表，依據 `id` 欄位取得任務記錄。
4. 若任務不存在，回傳 404 錯誤。
5. 若任務存在，回傳任務狀態資訊（status、file_path、error_message、row_count 等）。
6. 此流程為純查詢，**不會**觸發任何非同步作業、Webhook、Kafka 訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Router | `exports.py:router` | 映射 `GET /export/task` 至 `get_task_status` |
| 2 | Resource | `exports.py:get_task_status` | 接收 `task_id` 查詢參數 |
| 3 | Service | `exports.py:ExportService.get_task_status` | 呼叫 Provider 查詢任務 |
| 4 | Provider | `exports.py:ExportTaskProvider.get_by_id` | 執行 `SELECT` 查詢 `export_tasks` |
| 5 | Transfer | `exports.py:ExportTaskSerializer` | 將 DB 記錄序列化為 API 回應格式 |
| 6 | Router | `exports.py:router` | 回傳 JSON 回應 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `export_tasks` | Read | 查詢任務狀態、結果檔案路徑、錯誤訊息等 |

> 此場景**不使用** Redis Cache、Kafka 或任何佇列。

---

## 6. 重要規則

- **權限限制**：需人工確認（OpenAPI 未明確宣告此端點的驗證機制，需檢查 Middleware 或 Gateway 設定）。
- **不可暴露資料**：回應中不應包含 `query_params` 中的敏感個資（若有的話，需人工確認）。
- **狀態值限制**：`status` 欄位僅可為 `pending`、`processing`、`completed`、`failed` 四種。
- **不可修改欄位**：此端點僅供查詢，任何對 `export_tasks` 的寫入皆由背景 Worker 或建立任務的 API 負責。
- **查詢條件**：僅允許以 `task_id` 查詢，不支援批次或模糊查詢。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未提供 `task_id` 或為空字串 | 回傳 422 Validation Error |
| 提供的 `task_id` 格式無效（長度不符、包含特殊字元） | 回傳 422 Validation Error |
| 查詢的 `task_id` 不存在於 `export_tasks` | 回傳 404，訊息說明任務不存在 |
| 資料庫執行 `SELECT` 時發生例外 | 回傳 500 Internal Server Error，記錄錯誤日誌 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| ET01 | API Test | 傳入有效的 `task_id`（狀態為 `completed`） | 200 OK，回傳完整狀態與檔案路徑 |
| ET02 | API Test | 傳入有效的 `task_id`（狀態為 `failed`） | 200 OK，回傳狀態與 `error_message` |
| ET03 | API Test | 傳入不存在的 `task_id` | 404 Not Found |
| ET04 | API Test | 不帶 `task_id` 參數 | 422 Validation Error |
| ET05 | API Test | `task_id` 為空字串 | 422 Validation Error |
| ET06 | Permission Test | 無認證資訊呼叫 API | 需人工確認（401 或 403） |

---

## 9. 高風險區域

- **無高風險操作**：此場景為唯讀查詢，不涉及 Transaction、跨服務同步、Cache 一致性更新或 Queue 操作。
- **潛在風險**：若未來將 `export_tasks` 遷移至 Archive 表後，查詢歷史任務失敗，需人工確認任務生命週期管理政策。

---

## 10. 常見錯誤

- 新人或 AI 誤解此端點為**建立**或**更新**匯出任務。
- 呼叫端未處理 404 情境，導致畫面卡在等待狀態。
- 前端過度頻繁輪詢（polling）此 API，可能對 DB 造成壓力。建議前端實作指數退避（exponential backoff）。
- 誤將 `task_id` 與 `alert_id` 混淆。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `exports.py` Router 映射 |
| DB | `export_tasks` table，欄位定義自 `migrations/002_create_supplement_tables.sql` |
| Code | `exports.py:get_task_status` |
| Code | `exports.py:ExportService.get_task_status` |
| Code | `exports.py:ExportTaskProvider.get_by_id` |
| Schema | `export_tasks.id`（VARCHAR(32)）為 Task ID |
| Schema | `export_tasks.status` 限定 pending/processing/completed/failed |