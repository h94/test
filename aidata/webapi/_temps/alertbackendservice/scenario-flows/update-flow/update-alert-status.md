# 更新警示狀態

## 1. 場景目的
將警示的處理狀態變更為 `pending` 或 `ignored`，同時記錄變更履歷（變更前後狀態值及操作者），並透過背景 Webhook 廣播此次狀態異動給所有已啟用的訂閱端點。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/alertbackendservice/api/alerts/{alert_id}` | 更新指定警示狀態，request body 需包含 `status` 與 `operator_account` |

---

## 3. 流程總覽

1. **接收更新請求**：取得路徑參數 `alert_id` 及請求本體（`AlertUpdateBody`）。
2. **查詢警示**：依 `alert_id` 查詢 `alerts` 資料表，確保存取的是最新狀態（FOR UPDATE 鎖定，避免並行衝突）。
3. **狀態驗證**：只允許 `pending` 與 `ignored`，且與原有狀態不同時才進行後續處理（禁止無效轉換）。
4. **更新警示資料**：將 `status` 與 `operator_account` 寫入 `alerts` 表，並更新 `updated_at` 時間戳。
5. **寫入變更記錄**：將變更前後的狀態值寫入 `alert_change_log` 表。
6. **觸發 Webhook 廣播**：將本次警示變更事件包裝為 payload，寫入 `webhook_pending` 佇列（狀態為 `pending`），由背景 Worker 後續處理。
7. **回傳成功**：回傳 `200` 及更新後的警示摘要。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `Resources/alerts.py` 中的 `update_alert` 路由處理函式 | 接收 PUT 請求，擷取 `alert_id` 與 body |
| 2 | Service | `Service/AlertsService.update_status(alert_id, body)` | 協調 Provider 進行原子更新 |
| 3 | Provider | `Provider/alerts.py` 中的方法（如 `find_by_id_for_update`） | 以 `SELECT ... FOR UPDATE` 鎖定該警示列 |
| 4 | Validator | 內嵌於 Service 或 Provider | 檢查 status 合法（`pending`, `ignored`），且與舊值不同 |
| 5 | Provider | `Provider/alerts.py` 中的 `update_status` | 執行 `UPDATE alerts SET status, operator_account, updated_at = NOW()` |
| 6 | Provider | `Provider/alerts.py` 中的 `insert_change_log` | 寫入 `alert_change_log`（`alert_id`, `field_name='status'`, `old_value`, `new_value`, `operator_account`） |
| 7 | Provider | `Provider/webhooks.py` 中的 `enqueue_pending` | 將 webhook 投遞任務寫入 `webhook_pending` |
| 8 | Service | 同上 | 回傳更新後的警示物件（不含 detail / 大量 JSONB 欄位，僅必要摘要） |
| 9 | Controller | 同上 | 回傳 HTTP 200 及資料 |

> **需人工確認**：Service 與 Provider 的實際類別名稱與方法名稱需對照實際程式碼，此處為合理推導。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `alerts` | Read（FOR UPDATE）、Update | 鎖定並更新警示狀態與操作者 |
| DB | `alert_change_log` | Insert | 記錄狀態變更的審計軌跡 |
| DB | `webhook_pending` | Insert | 新增一筆待發送的 Webhook 任務（狀態 `pending`） |
| DB | `webhooks` | Read | （由背景 Worker 讀取，非 API 流程）取得已啟用、符合事件的 webhook 設定 |
| Queue | （疑似 Kafka 或純 DB 輪詢） | 無直接 Publish | 背景 Worker 輪詢 `webhook_pending`，非 API 直接呼叫 |
| Cache | Redis | 無 | 此場景未使用快取 |
| Queue | Kafka | 未確認 | **需人工確認**是否利用 Kafka 通知 Worker，目前程式證據僅顯示 DB 佇列 |

---

## 6. 重要規則

- **狀態限制**：只接受 `pending` 與 `ignored`，其他值（如 `resolved`）視為無效。
- **不可修改欄位**：除 `status` 與 `operator_account` 外，不可透過此 API 修改其他警示欄位（例如 `detail`, `threshold_snapshot` 等）。
- **變更記錄**：每次狀態變更（若新值不同於舊值）必須寫入一筆 `alert_change_log`，欄位名稱固定為 `status`。
- **Webhook 觸發條件**：僅當變更成功且存在對應事件（例如 `alert_status_changed`）的已啟用 Webhook 時，才產生待送任務。
- **並行控制**：更新時必須用 `SELECT ... FOR UPDATE` 防止兩個操作員同時變更同一警示。
- **操作者帳號**：從請求本體取得，**需人工確認**是否應由閘道注入或由前端帶入（安全性考量）。
- **TTL 規則**：`webhook_pending` 中的任務若有設定 max_retry_attempts，則超過次數後標記 `failed`；無自動清理機制（依排程或手動處理）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `alert_id` 不存在 | HTTP 404，錯誤訊息 "Alert not found" |
| 請求 status 不是 `pending` 或 `ignored` | HTTP 422，驗證錯誤詳情 |
| 新狀態與目前狀態相同 | HTTP 200（無實際變更，不寫 change log，不觸發 Webhook）或 HTTP 409（**需人工確認**實際行為） |
| `operator_account` 未提供或為空 | HTTP 422，驗證錯誤 |
| 資料庫鎖定逾時（因其他交易持有鎖） | HTTP 500 或 503，錯誤訊息 "Update conflict" |
| Webhook 任務寫入 `webhook_pending` 失敗 | 警示狀態已更新，但 Webhook 通知遺失；**需人工確認**此時服務是否有 rollback 機制，或僅記錄錯誤後放行 |
| 更新 `alerts` 成功但寫入 `alert_change_log` 失敗 | **需人工確認**是否使用 DB transaction 包覆，否則可能造成審計遺漏 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| UA_001 | API Test | 正常更新 status 為 `ignored`，提供 `operator_account` | 200，回應中 `status` 為 `ignored`；`alert_change_log` 新增一筆記錄 |
| UA_002 | API Test | 更新 status 為 `pending` | 200，成功 |
| UA_003 | API Test | 嘗試更新為無效值（如 `resolved`） | 422 驗證錯誤 |
| UA_004 | API Test | `alert_id` 不存在 | 404 |
| UA_005 | Flow Test | 無變更（相同的 status 再送一次） | 200（或 409），無 change log，無 Webhook 任務 |
| UA_006 | Integration Test | Webhook 任務產生 | 成功更新後，`webhook_pending` 中存在對應 `alert_id` 的新任務，狀態 `pending` |
| UA_007 | Permission Test | 未提供 `operator_account` | 422（依實作而定） |
| UA_008 | Concurrency Test | 兩個請求同時更新同一警示，一個應等待鎖釋放 | 兩個請求皆成功，且 change log 有兩筆（最終狀態為最後一個請求的值） |

---

## 9. 高風險區域

- **高風險 table**：`alerts`（直接狀態修改）、`alert_change_log`（審計完整性）。
- **高風險 API**：本端點若無適當交易邊界，可能使狀態寫入成功但 change log 遺失。
- **Transaction**：**需人工確認**更新 `alerts` 與 insert `change_log`、insert `webhook_pending` 是否在同一個 DB transaction 中。若分離，可能導致部分成功。
- **Cache consistency**：此流程無快取，無一致性風險。
- **Queue retry**：Webhook 任務由 Worker 處理，若 Worker 故障，任務可能堆積；需要有監控告警。
- **Idempotency**：相同 payload 重複請求（重送 PUT）可能產生多筆 changelog 與 webhook 任務，**需人工確認**是否需要冪等鍵（例如依 alert_id + 舊狀態判斷），目前推測僅以新舊狀態相同時跳過。

---

## 10. 常見錯誤

- 以為所有狀態（如 `resolved`, `closed`）都能更新，導致非法值錯誤。
- 忘了帶 `operator_account`，請求被拒。
- 誤解 Webhook 是同步發送，實際上此 API 僅寫入任務，發送為非同步。
- 更新後未檢查 change log 是否正確寫入，導致審計缺失。
- 在高併發下未考慮鎖定機制，造成狀態遺失（lost update）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 定義 | OpenAPI：`PUT /api/alerts/{alert_id}`，request schema `AlertUpdateBody` |
| DB 表 | `alerts`（status, operator_account），`alert_change_log`（alert_id, field_name, old_value, new_value, operator_account） |
| 遷移腳本 | `migrations/001_create_core_tables.sql`（alerts schema）、`migrations/002_create_supplement_tables.sql`（alert_change_log, webhook_pending） |
| 程式 | `project/Provider/alerts.py` 中的 `insert_change_log` 方法 (phase1 證據) |
| 業務邏輯 | README「警示查詢與狀態更新」說明可更新為 pending／ignored 並透過 Webhook 廣播 |
| Webhook 機制 | `webhook_pending` 表作為佇列，`Tasks.py` 背景 Worker 發送（README 提及） |