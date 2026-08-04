# 刪除 Webhook 組態

## 1. 場景目的
讓操作員移除不再需要的 Webhook 端點組態，確保刪除後不再觸發通知派送，並妥善處理既有的待處理任務。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| DELETE | /api/webhooks/{webhook_id} | 刪除指定 ID 的 Webhook 組態 |

---

## 3. 流程總覽

1. 接收 DELETE 請求，解析路徑參數 `webhook_id`
2. 驗證 `webhook_id` 是否存在於 `webhooks` 表
3. 檢查是否有關聯的 `webhook_pending` 記錄正在處理中
4. 執行刪除（可能為軟刪除或硬刪除）
5. 清理相關的待處理任務（`webhook_pending`）
6. 記錄操作稽核
7. 回傳 200 OK 或適當的錯誤回應

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Resource | WebhookResource | 接收 DELETE 請求，提取 `webhook_id` |
| 2 | Service | WebhookService | 驗證 Webhook 存在性，檢查相依資源 |
| 3 | Provider | WebhookProvider | 查詢 `webhooks` 表確認記錄存在 |
| 4 | Service | WebhookService | 檢查 `webhook_pending` 是否有進行中任務 |
| 5 | Provider | WebhookProvider | 執行 `webhooks` 表刪除操作 |
| 6 | Provider | WebhookPendingProvider | 批量更新或刪除關聯的 `webhook_pending` 記錄 |
| 7 | Service | WebhookService | 註銷相關背景 Worker 的排程任務 |
| 8 | Resource | WebhookResource | 回傳 200 OK |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | webhooks | Read → Delete | 確認存在後移除組態 |
| DB | webhook_pending | Read → Update/Delete | 清理未發送的待處理任務 |
| DB | webhook_logs | Read（可選） | 檢查歷史記錄（視商務需求保留或清理） |
| Redis | webhook:config:{id} | Delete | 清除快取的 Webhook 組態 |
| Queue | Kafka / Internal Queue | Publish | 通知背景 Worker 停止處理該 Webhook |

---

## 6. 重要規則

- **權限限制**：需驗證操作員帳號（`operator_account`）具備刪除權限
- **存在性檢查**：`webhook_id` 不存在時必須回傳 404
- **外鍵約束**：`webhook_pending.webhook_config_id` 參照 `webhooks.id`，刪除前需處理關聯記錄
- **不可恢復**：刪除操作應為不可逆（或實作軟刪除，需人工確認）
- **Worker 同步**：刪除後需確保背景 Webhook Worker 不再讀取該組態
- **快取失效**：刪除後需立即清除 Redis 中相關快取，避免幽靈組態
- **日誌保留**：`webhook_logs` 歷史記錄通常保留，不因組態刪除而 cascade 刪除

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| webhook_id 不存在 | 回傳 404 Not Found |
| 存在正在處理的 webhook_pending 任務 | 回傳 409 Conflict，提示需等待任務完成或強制取消（需人工確認） |
| 資料庫連線失敗 | 回傳 500 Internal Server Error |
| 刪除後 Redis 快取清除失敗 | 記錄錯誤日誌，但刪除操作仍視為成功（需人工確認是否需強制一致性） |
| 重複刪除相同 webhook_id | 第二次請求回傳 404（冪等性處理） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| WH-DEL-01 | 正常流程 | 刪除存在的 Webhook 組態 | 200 OK，webhooks 記錄移除，pending 任務清理 |
| WH-DEL-02 | 錯誤情境 | 刪除不存在的 webhook_id | 404 Not Found |
| WH-DEL-03 | 相依性檢查 | 刪除有 pending 任務的 Webhook | 409 Conflict 或成功清理（依實作） |
| WH-DEL-04 | 冪等性 | 重複刪除相同 ID | 第二次回傳 404 |
| WH-DEL-05 | 權限驗證 | 無權限操作員嘗試刪除 | 403 Forbidden |
| WH-DEL-06 | 背景同步 | 刪除後觸發新 alert，確認 Webhook 不再觸發 | 無 webhook_pending 新記錄產生 |
| WH-DEL-07 | 快取驗證 | 刪除後查詢組態（若存在 GET API） | 404 或空回應 |

---

## 9. 高風險區域

- **高風險 table**：`webhook_pending`（刪除 `webhooks` 時需確保沒有 dangling references）
- **高風險 API**：`DELETE /api/webhooks/{webhook_id}`（直接影響通知派送鏈路）
- **跨服務資料同步**：背景 Worker 可能仍持有舊組態快取，需確保即時失效
- **Transaction**：刪除 `webhooks` 與清理 `webhook_pending` 應在同一 Transaction 內執行
- **Cache consistency**：Redis 快取需同步清除，避免幽靈組態
- **Queue retry**：若刪除時仍有 `webhook_pending` 記錄狀態為 `sending`，需決定是否等待或強制取消

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 未檢查 `webhook_pending` 關聯，直接 DELETE 導致 foreign key 錯誤
  - 忽略 Redis 快取清除，導致 Worker 仍使用舊組態發送
  - 未考慮冪等性，重複刪除時回傳 500 而非 404
- **AI 容易誤解**：
  - 誤以為 `webhook_logs` 也需 cascade 刪除（通常保留）
  - 未考量背景 Worker 的狀態同步
- **常見漏檢查項目**：
  - 刪除前未通知背景 Worker 停止相關排程
  - 未記錄操作稽核日誌（誰在何時刪除了哪個 Webhook）

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | DELETE /api/webhooks/{webhook_id}（OpenAPI） |
| DB | webhooks.id 為主鍵，webhook_pending.webhook_config_id 為外鍵（db-usage） |
| DB | webhooks 表結構見 `migrations/002_create_supplement_tables.sql` |
| DB | webhook_pending 表結構見 `migrations/002_create_supplement_tables.sql` |
| Redis | webhook 組態快取（需人工確認確切 key pattern） |
| Code | WebhookProvider.delete_by_id（需人工確認 method 名稱） |
| Worker | Tasks.py 中的 Webhook Worker 負責發送與重試（README） |