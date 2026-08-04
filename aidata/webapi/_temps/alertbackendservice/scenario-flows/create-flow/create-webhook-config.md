# 建立 Webhook 組態

## 1. 場景目的
提供系統管理員設定新的 Webhook 端點組態，定義接收端 URL、監聽的觸發事件、速率限制與重試次數。設定完成後，背景 Worker 即可依據此組態派送警示通知。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | /api/webhooks | 建立新的 Webhook 組態。 |

---

## 3. 流程總覽
1. 接收包含 Webhook 設定資訊的 POST request。
2. 驗證 request body 格式與必要欄位（URL、name、trigger_events 等）。
3. 將新的 Webhook 組態寫入 `webhooks` 資料表。
4. 回傳建立成功的 Webhook 組態資料。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `Resources/Webhook.py` → `create_webhook` | 接收 HTTP request，調用 Service 層。 |
| 2 | Service | `Service/WebhookService.py` → `create` | 接收參數，調用 Provider 插入資料庫。 |
| 3 | Provider | `Provider/WebhookProvider.py` → `insert` | 執行 SQL INSERT，將組態寫入 `webhooks` 表。 |
| 4 | Provider | `Provider/WebhookProvider.py` → `insert` | 回傳新建立的 webhook ID。 |
| 5 | Service | `Service/WebhookService.py` → `create` | 寫入操作日誌（threshold_changelog，此處需人工確認是否確實用此表）。 |
| 6 | Controller | `Resources/Webhook.py` → `create_webhook` | 將新建的 Webhook 資料序列化後回傳。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `webhooks` | Write (INSERT) | 儲存新的 Webhook 組態。 |

---

## 6. 重要規則
- **ID 自動生成**：`webhooks.id` 為 SERIAL 型別，由資料庫自動遞增，不應由 client 指定。
- **欄位格式驗證**：`trigger_events` 必須為合法的 JSON 陣列；`url` 格式需有效（需人工確認是否有 URL validator）。
- **非必填欄位**：`rate_limit_per_sec` 與 `max_retry_attempts` 可為 null，表示不限制或不重試。
- **操作者紀錄**：`operator_account` 為必填，用於稽核。
- **稽核日誌**：需人工確認 Service 層是否對此次建立寫入 `threshold_changelog`，或是由背景 Worker 自行偵測。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| Request body 缺少必要欄位（如 url） | 回傳 HTTP 422 Validation Error。 |
| trigger_events 格式錯誤（非陣列） | 回傳 HTTP 422 Validation Error。 |
| 資料庫寫入失敗（例如連線超時） | 回傳 HTTP 500 Internal Server Error，組態未儲存。 |
| url 格式非法（需人工確認是否有檢查） | 可能回傳 HTTP 422 或 400（需人工確認）。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| WH-CREATE-01 | API Test | 提供完整且合法的 Webhook 設定 | HTTP 200，回應包含 id 且狀態為 enabled。 |
| WH-CREATE-02 | API Test | 缺少 url 欄位 | HTTP 422，回應欄位驗證錯誤。 |
| WH-CREATE-03 | API Test | 提供空的 trigger_events 陣列 | HTTP 200，允許建立不觸發任何事件的 Webhook（需人工確認規則是否允許）。 |
| WH-CREATE-04 | Flow Test | 建立後查詢 `GET /api/webhooks` | 列表中應包含新建立的 Webhook。 |

---

## 9. 高風險區域
- **Webhook 組態表 (`webhooks`)**：寫入錯誤的 URL 或速率限制過低，可能導致背景 Worker 大量送信失敗或被限流，影響整體通知可靠性。
- **URL 驗證**：若無嚴格驗證，可能儲存無效端點，導致後續排程作業浪費資源重試。
- **速率與重試設定**：`rate_limit_per_sec` 與 `max_retry_attempts` 若為 0 或極小值，將直接影響訊息送達率，需確保 UI 或 API 有合理的預設值或提示。

---

## 10. 常見錯誤
- **trigger_events 格式錯誤**：誤傳字串而非 JSON 陣列。
- **Rate Limit 誤解**：將 `rate_limit_per_sec` 設為 0，誤以為代表無限制，實際上可能完全阻止送信（需人工確認 0 的語義）。
- **URL 格式錯誤**：忘記加上 `https://` 或包含多餘的空格。
- **忽略 operator_account**：未帶入操作者帳號，導致稽核日誌缺失。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 定義 | OpenAPI: POST /api/webhooks |
| DB Schema | `migrations/002_create_supplement_tables.sql` → `webhooks` 表 |
| Controller | `Resources/Webhook.py` → `create_webhook` 函數 |
| Service | `Service/WebhookService.py` → `create` 函數 |
| Provider (SQL 寫入) | `Provider/WebhookProvider.py` → `insert` 函數 |