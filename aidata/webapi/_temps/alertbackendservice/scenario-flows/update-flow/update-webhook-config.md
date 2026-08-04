# 更新 Webhook 組態

## 1. 場景目的

允許操作人員修改既有的 Webhook 端點組態，包括名稱、URL、觸發事件、速率限制、重試次數及啟用狀態，以便調整通知派送行為。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/webhooks/{webhook_id}` | 修改指定 Webhook 組態 |

---

## 3. 流程總覽

1. 接收更新請求，攜帶 webhook_id 與新的組態內容
2. 驗證 webhook_id 是否存在於 `webhooks` 表
3. 驗證請求參數格式（URL 格式、正整數欄位等）
4. 使用資料庫交易更新 `webhooks` 表
5. 若更新成功，清除相關 Redis 快取（如有），確保背景 Worker 能讀取到最新組態
6. 回傳更新後的 Webhook 完整資訊

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `Resources/Webhook.py` | 接收 PUT 請求，解析 `webhook_id` 與 request body |
| 2 | Service | `WebhookService.update`（需人工確認方法名） | 調用 Provider 查詢 `webhooks` 確認存在 |
| 3 | Service | `WebhookService.update` | 驗證 request body 欄位（URL 格式、數值範圍） |
| 4 | Provider | `WebhookProvider.update`（需人工確認） | 執行 SQL UPDATE `webhooks` 語句，同時更新 `updated_at` 為 `NOW()` |
| 5 | Service | `WebhookService.update` | 若組態啟用狀態或速率限制變更，需通知背景 Worker 重載組態（機制需人工確認，可能透過 Redis pub/sub 或直接清除快取 key） |
| 6 | Controller | `Resources/Webhook.py` | 回傳 200 與更新後的 Webhook 物件 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `webhooks` | Read | 確認 `webhook_id` 存在 |
| DB | `webhooks` | Update | 更新 `name`、`url`、`enabled`、`trigger_events`、`rate_limit_per_sec`、`max_retry_attempts`、`operator_account` |
| Redis | 需人工確認 | Delete | 若系統有快取 Webhook 組態，需清除對應 key 以強制 Worker 重載 |
| Queue | 需人工確認 | - | 若需通知背景 Worker 重載組態，可能透過 Kafka 或 Redis pub/sub 發送變更事件 |

---

## 6. 重要規則

- **權限限制**：需人工確認（OpenAPI 未定義安全機制，需檢查 Controller 層是否驗證 operator_account）
- **欄位限制**：
  - `url` 必須為合法的 HTTP/HTTPS URL
  - `rate_limit_per_sec` 若提供，必須為正整數或 null
  - `max_retry_attempts` 若提供，必須為非負整數
  - `trigger_events` 必須為有效的 JSON array，內容需符合系統定義的事件類型
- **不可修改欄位**：`id`、`created_at` 不可修改
- **Transaction 規則**：建議使用資料庫交易確保更新與後續日誌記錄的原子性（需人工確認是否有寫入 `threshold_changelog` 或其他稽核表的需求）
- **狀態值限制**：`enabled` 僅接受 `true`/`false`

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| webhook_id 不存在 | 回傳 404 Not Found |
| url 格式無效 | 回傳 422 Validation Error |
| rate_limit_per_sec 為負數 | 回傳 422 Validation Error |
| trigger_events 包含未定義事件 | 回傳 422 Validation Error（需人工確認驗證邏輯是否存在） |
| 資料庫寫入失敗 | 回傳 500 Internal Server Error |
| 更新成功但 Redis 清除失敗 | 需人工確認處理策略（可能僅記錄錯誤，不影響回應） |
| 無效的 JSON body | 回傳 422 Validation Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-WEBHOOK-UPDATE-001 | API Test | 正常更新所有欄位 | 200, 回傳更新後的完整 Webhook 物件 |
| UT-WEBHOOK-UPDATE-002 | API Test | 更新不存在的 webhook_id | 404 |
| UT-WEBHOOK-UPDATE-003 | API Test | 更新時僅傳遞部分欄位 | 200, 未傳遞的欄位保持原值（需人工確認是否支援部分更新） |
| UT-WEBHOOK-UPDATE-004 | Validation Test | url 欄位傳入 "invalid-url" | 422 |
| UT-WEBHOOK-UPDATE-005 | Validation Test | rate_limit_per_sec 設為 -1 | 422 |
| UT-WEBHOOK-UPDATE-006 | Permission Test | 不帶 operator_account 或帶無效帳號 | 需人工確認（401 或 403） |
| UT-WEBHOOK-UPDATE-007 | Flow Test | 更新 `enabled` 從 false 改為 true，驗證背景 Worker 是否能取得最新組態 | 背景 Worker 應使用更新後的組態派送 Webhook |

---

## 9. 高風險區域

- **高風險 table**：`webhooks` — 背景 Worker 可能同時讀取此表進行派送，更新時需注意競爭條件
- **Cache consistency**：若系統對 Webhook 組態有 Redis 快取，更新後未正確清除將導致背景 Worker 持續使用舊組態
- **跨服務資料同步**：背景 Worker 需即時反映組態變更，需確認通知機制（Redis pub/sub 或輪詢）是否可靠
- **Idempotency**：重複發送相同的 PUT 請求應維持相同結果，不應產生重複的組態記錄

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 傳入的 `trigger_events` 格式錯誤（應為 JSON array 卻傳入字串）
  - 忘記提供必填欄位或提供錯誤的欄位名稱
- **AI 容易誤解**：
  - 誤以為此 API 會同時修改 `webhook_pending` 或 `webhook_logs` 表（這些表僅供背景 Worker 操作）
  - 誤以為更新 Webhook 後需要手動觸發背景 Worker 重啟
- **常見漏檢查項目**：
  - 未驗證 `trigger_events` 陣列中的事件類型是否為系統定義的合法值
  - 更新後未回傳完整的 Webhook 物件給前端

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI `PUT /api/webhooks/{webhook_id}` |
| DB | `webhooks` 表定義 (migrations/002_create_supplement_tables.sql) |
| Code | `Resources/Webhook.py`、`Service/WebhookService.py`、`Provider/WebhookProvider.py`（需人工確認實際實作） |
| Flow | README 描述：背景 Worker 負責發送與重試，並具備速率控制（組態來源為 `webhooks` 表） |