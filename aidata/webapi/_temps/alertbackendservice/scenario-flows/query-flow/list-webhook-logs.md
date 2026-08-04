# 查詢 Webhook 發送記錄

## 1. 場景目的

提供後台人員查詢 Webhook 的歷史派送記錄，包含成功／失敗狀態、請求與回應內容、耗時等，用以追蹤通知是否確實送達目標端點。

---

## 2. 入口 API

需人工確認，OpenAPI 截斷未露出完整路徑。依專案設計慣例，推測為：

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/webhooks/logs` | 查詢 Webhook 發送記錄，支援條件篩選與分頁 |

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，附帶查詢參數（`config_id`、`alert_id`、`start_time`、`end_time`、分頁…）。
2. 通過 FastAPI Resource 呼叫 Service，Service 再呼叫 Provider。
3. Provider 組合動態查詢條件，對 `webhook_logs` 表執行 SELECT，含 `ORDER BY sent_at DESC` 及 `LIMIT/OFFSET`。
4. 將查詢結果封裝為列表與總筆數（不含 `request_payload` 過大欄位可選摘要）。
5. 回傳 JSON，包含 `data`、`total`、`page`、`size`。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Resource | `WebhookLogsResource` | 接收 query params，呼叫 Service |
| 2 | Service | `WebhookService.get_logs(params)` | 處理業務邏輯（如時間範圍預設、敏感欄位過濾） |
| 3 | Provider | `WebhookProvider.list_logs(conn, filters, order, limit, offset)` | 建構 SQL 查詢 `webhook_logs`，執行並回傳 rows |
| 4 | Provider | `WebhookProvider.count_logs(conn, filters)` | 計算總筆數供分頁 |

Evidence 來源：`webhooks.py` Provider 含有 `list_logs`、`insert_log` 等函式；`webhook_logs` 表結構來源於 `migrations/002_create_supplement_tables.sql`。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `webhook_logs` | Read | 查詢發送記錄（主要資料源） |

此流程不涉及 Redis Cache、Kafka/Queue，單純讀取 PostgreSQL。

---

## 6. 重要規則

- **權限限制**：需人工確認，通常只有擁有 Webhook 管理權限的操作員可查詢。目前未看到強制權限檢查程式碼，需補上。
- **分頁強制**：Provider 層可能未強制 limit，需檢核是否預設至少 limit=20，最大 page size 建議 100。
- **敏感欄位**：`request_payload` 可能包含第三方 API 完整請求，如需回傳應做脫敏或只顯示部分摘要，需人工確認規則。
- **時間預設值**：若未帶 `start`／`end`，預設查詢近 24 小時記錄（台灣時間），避免全表掃描。
- **不可暴露資料**：`response_body` 可能包含 token，應避免完整回傳。
- **索引使用**：必須保證至少 `(config_id, sent_at)` 複合索引存在，若經常依 `alert_id` 查詢也需索引。目前 migration 中未明確建立，**需人工確認**。
- **排序**：固定依 `sent_at DESC`（最新在前）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未提供任何查詢條件且時間區間過大 | 回應 422 或強制套用 24 小時預設 |
| `config_id` 不存在 | 回應空陣列，非錯誤 |
| 查詢時間範圍超過 30 天 | 需人工確認限制，否則可能影響效能 |
| DB 連線失敗 | 回應 500，記錄錯誤 |
| `limit` 超過上限 | 自動調整為 100 或 回應 400 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| WH01 | API Test | 無參數查詢，取預設時間範圍 | 回傳今日記錄列表，分頁結構正確 |
| WH02 | API Test | 指定 `config_id=1` 查詢 | 僅回傳該 webhook 組態的紀錄 |
| WH03 | API Test | 指定 `alert_id=xxx` | 僅回傳與該警示相關的紀錄 |
| WH04 | API Test | 指定 `start/end` 跨越大區間 | 若有限制，應回傳 422 或限制範圍 |
| WH05 | DB Performance | 在百萬筆資料下，透過 `config_id` + 時間查詢 | 需使用索引，回應 < 500ms |
| WH06 | Permission | 未授權的使用者呼叫 | 需人工確認：若實作有權限控制應 403，否則跳過 |

---

## 9. 高風險區域

- **高風險 table**：`webhook_logs` – 表快速成長，無清理機制可能效能惡化。
- **效能**：缺乏必要索引會導致 seq scan，尤其在未帶 `config_id` 條件時。
- **資料安全**：`request_payload` 與 `response_body` 含敏感資訊（如 API key），應避免直接回傳。
- **一致性問題**：皆為只讀查詢，無交易風險。
- **依賴**：僅依賴 PostgreSQL，無其他服務。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 未限制 `limit` 或 `time_range`，執行全表查詢拖垮 DB。
  - 忘記加入 `ORDER BY`，導致前端無法使用游標分頁。
- **AI 容易誤解**：
  - 產生的 API 路徑可能與實際不同（建議確認 OpenAPI）。
  - 可能誤寫成搜尋最近 N 筆不區分 `config_id`，忽略多租戶隔離。
- **常見漏檢查項目**：
  - 未確認 Webhook 記錄是否需要保留永久，必要時加入資料保留策略。
  - 未處理前端時間格式轉換（UTC ↔ Asia/Taipei）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB 結構 | `migrations/002_create_supplement_tables.sql` → `webhook_logs` table |
| Provider 方法 | `webhooks.py` → `list_logs` / `count_logs` （推測存在） |
| API 路徑 | 需人工確認，OpenAPI 截斷區段可能為 `paths./api/webhooks/logs.get` |
| 時間處理規則 | README：容器時區預設 `Asia/Taipei`，所有時間以台灣時間為準 |
| 敏感資料風險 | `webhook_logs` 欄位含 `request_payload` 與 `response_body`，無脫敏機制 |

---

## 12. 建議新增事項（如有）

- **可選新增規則文件**：說明 Webhook 記錄保留天數與清理排程。
- **建議新增測試**：驗證敏感字串是否被過濾（如 response_body 內的 token）。
- **建議新增監控**：`webhook_logs` 表大小監控，索引使用率追蹤。