# 更新通知主題

## 1. 場景目的
管理員更新通知主題（如啟用狀態、圖示、排序）並清除對應 Redis 快取，確保前台查詢立即生效。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/sport/notifications/topics/{id}` | 更新指定通知主題欄位 |

---

## 3. 流程總覽

1. 管理員透過後台發送 PUT 請求，請求體包含欲更新的欄位（例如 `Enabled`、`IconPath`、`Seq`）。
2. ECFramework 驗證框架攔截並檢查管理員身份與權限。
3. 依 `id` 查詢 MySQL `sport.notification_topics` 確認主題存在（不存在則回 404）。
4. 更新該筆記錄的對應欄位，系統自動寫入 `UpdateTime`。
5. 刪除 Redis SportCache 中的 `NotificationTopics` 鍵，以失效快取。
6. 回傳 200 成功。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | NotificationController.PutTopic | 接收請求，呼叫 Service。預期名稱需人工確認（可能為 SportNotificationController） |
| 2 | Service | NotificationService.UpdateTopicAsync | 驗證輸入欄位格式、呼叫 Repository |
| 3 | Repository | NotificationRepository.UpdateTopic | 對 `sport.notification_topics` 執行 `UPDATE` 語句 |
| 4 | Service | NotificationService.InvalidateTopicCacheAsync | 呼叫 Redis 提供者刪除快取鍵 |
| 5 | Cache | RedisCacheProvider.DeleteKey | 對 `NotificationTopics` 執行 `DEL` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | MySQL `sport.notification_topics` | Read / Update | 確認主題存在並修改欄位 |
| Redis | SportCache `NotificationTopics`（Hash） | Delete | 刪除整個鍵，強制後續查詢回源 DB |

---

## 6. 重要規則

- **權限限制**：必須通過 ECService 驗證且具備後台通知管理權限；未登入回 401，權限不足回 403。
- **欄位限制**：
  - `Enabled` 僅允許 0 或 1。
  - `IconPath` 需為伺服器合法路徑，禁止外部 URL。
  - `IconColorCode` 需符合顏色格式（如 `#RRGGBB`）。
  - `Seq` 為整數。
- **不可修改欄位**：`ID` 主鍵不可更新；`UpdateTime` 由系統自動設定。
- **TTL 規則**：Redis `NotificationTopics` 為永久快取（無 TTL），僅靠主動刪除維持一致性。
- **Transaction 規則**：DB 更新與 Redis 刪除屬不同資料源，無分散式交易。DB 成功後才刪除快取；若 Redis 刪除失敗仍回傳 200，但須記錄錯誤日誌。
- **Retry 規則**：Redis 刪除失敗不自動重試；可透過監控或排程清理。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 主題 ID 不存在 | 404 Not Found |
| 請求欄位格式無效（例如 `Enabled` 輸入 3） | 400 Bad Request，附錯誤訊息 |
| 未帶驗證 token 或 token 無效 | 401 Unauthorized |
| 有 token 但使用者無通知管理權限 | 403 Forbidden |
| DB 連線超時或更新失敗 | 500 Internal Server Error |
| Redis 刪除失敗（網路瞬斷） | 回傳 200 OK，記錄 Warning log，快取暫時未清除 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| UT-01 | API Test | 正常更新 `Enabled` 與 `Seq` | 200，DB 欄位變更，Redis `NotificationTopics` 被刪除 |
| UT-02 | API Test | 更新不存在的 `id` | 404，DB 無異動 |
| UT-03 | Permission Test | 無效 token 呼叫 | 401 |
| UT-04 | Permission Test | 使用無管理權限帳號呼叫 | 403 |
| UT-05 | Flow Test | DB 更新成功但 Redis `DEL` 失敗 | 200，DB 已更新，log 出現錯誤 |
| UT-06 | API Test | 傳入外部連結作為 `IconPath` | 400 驗證失敗 |
| UT-07 | Integration Test | 更新後立即查詢 GET `/topics` | 取得最新資料（Redis 已被清除，回源 DB） |

---

## 9. 高風險區域

- **高風險 table**：`sport.notification_topics` — 錯誤的 `Enabled` 變更可能導致前端消失或顯示停用主題。
- **高風險 API**：PUT `/topics/{id}` — 若未充分檢查輸入，可能被注入非法內容。
- **Cache consistency**：Redis 刪除失敗時，前端可能讀取過期快取；須監控 Redis 可用性。
- **並發更新**：若多人同時更新同一主題，後寫者覆蓋先寫者，尚可接受；但若同時更新 Redis，需確保 DEL 操作冪等。

---

## 10. 常見錯誤

- 更新前未檢查主題是否存在，導致更新影響０行仍回傳成功。
- 忘記在成功更新 DB 後刪除 Redis 快取，導致前後台資料不一致。
- 未限制 `IconPath` 來源，可能寫入惡意路徑。
- 誤解權限模型：以為一般登入者即可呼叫（實則需要管理後台角色）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md 中 PUT `/api/v1/sport/notifications/topics/{id}` |
| DB | 表 `sport.notification_topics`（sport-detail.md） |
| Redis | `NotificationTopics`（SportCache）見 pricecentermanage-detail.md Redis 章節 |
| Code | Controller／Service 具體名稱需人工確認（推測為 `NotificationController` 與對應 Service） |
| SQL | `UPDATE sport.notification_topics SET ... WHERE ID = ?` |