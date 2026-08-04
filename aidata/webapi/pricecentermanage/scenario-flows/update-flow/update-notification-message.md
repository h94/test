# 更新通知訊息

## 1. 場景目的

管理員更新特定通知訊息的內容（如多語系內文、標題），或變更其啟用狀態（Enabled）。更新成功後，系統必須立即清除對應的 Redis 快取，確保前台查詢能取得最新資料。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/sport/notifications/messages/{tid}/{id}` | 更新通知訊息 |
| 權限 | 需要驗證 | 後台管理員權限 |
| 參數 | `tid` (路徑): 通知主題ID<br>`id` (路徑): 訊息ID | - |
| 請求體 | `SportMessageDTO` | 包含 `Enabled`, `Title`, 各語系內容等 |

---

## 3. 流程總覽

1. 接收 PUT 更新請求，含 `tid` 與 `id` 及新的訊息內容
2. 驗證已登入管理員權限（透過 ECFramework 驗證）
3. 查詢 MySQL `sport.notification_messages` 確認該 `(TID, ID)` 組合存在
4. 更新符合條件的記錄（Enabled、Title、多語系內容、UpdateTime）
5. 清除對應的 Redis 快取 `NotificationMessages_{hashKey}`（使用與訊息關聯的 TID 生成 hashKey）
6. 回傳操作成功 (200 OK)

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | NotificationController.PutMessage | 接收 `SportMessageDTO`，呼叫 Service |
| 2 | Service | MessageService.UpdateMessage | 驗證權限，檢查訊息存在性，呼叫 Repository |
| 3 | Repository | NotificationRepository | 執行 UPDATE SQL 寫入 `notification_messages` 表 |
| 4 | Provider | RedisProvider | 刪除 Redis Key：`NotificationMessages_{hashKey}` |
| 5 | Controller | NotificationController.PutMessage | 回傳 200 OK |

> **說明**：`hashKey` 是基於通知主題 ID (`tid`) 的 hash 運算結果，用於定義快取分片。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (MySQL) | `sport.notification_messages` | Read (確認存在) | 確保訊息存在 |
| DB (MySQL) | `sport.notification_messages` | Update | 更新 Enabled、Title、各語系內容、UpdateTime |
| Redis (SportCache) | `NotificationMessages_{hashKey}` | Delete | 清除快取，確保持續一致性 |

> **Queue 使用**：本流程未直接涉及 Kafka 或 Message Queue。

---

## 6. 重要規則

- **權限限制**：僅允許已驗證的後台管理員執行。缺乏合法身份憑證或權限不足時需阻擋（回傳 401/403）。
- **欄位限制**：`TID` 欄位不得透過更新變更（訊息只能隸屬於原主題）。`ID` 作為主鍵不可修改。
- **不可暴露資料**：API 回傳中不應包含內部運算的 `hashKey` 或完整 Redis Key。
- **TTL 規則**：此 Redis Key 無 TTL，為永久保存，單純依賴主動刪除來失效。
- **Transaction 規則**：**需人工確認**是否應在 DB 寫入成功後才刪除快取（Cache-Aside 模式）；若快取刪除失敗，不可影響 DB 更新成功回傳，但應記錄錯誤。
- **狀態值限制**：`Enabled` 僅可為 `1`（啟用）或 `0`（停用）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 管理員未登入或 Token 無效 | 回傳 401 Unauthorized |
| 帳號權限不足 | 回傳 403 Forbidden |
| 目標訊息 (TID+ID) 不存在 | 回傳 404 Not Found 或明確錯誤訊息 |
| 請求體內必要欄位遺失或格式錯誤 | 回傳 400 Bad Request |
| 資料庫更新失敗（Timeout / Lock） | 回傳 500 Internal Server Error，並記錄 Log |
| Redis 刪除錯誤（Timeout） | 不影響主流程回應 200，但需記錄錯誤，並依賴後續清除機制補救 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| UC-UPD-MSG-01 | API Test | 提供完整且合法的訊息內容與 Token | 200 OK，DB 欄位正確更新 |
| UC-UPD-MSG-02 | Flow Test | 成功更新後立刻查詢訊息列表 API | 查詢結果與更新後資料一致 |
| UC-UPD-MSG-03 | Permission Test | 使用一般使用者權限 Token | 403 Forbidden |
| UC-UPD-MSG-04 | Error Test | 請求體缺少 `Title` 欄位 | 400 Bad Request |
| UC-UPD-MSG-05 | Cache Test | 成功更新後檢查 Redis Key 存在性 | `NotificationMessages_{hashKey}` 已被刪除 |

---

## 9. 高風險區域

- **Cache consistency**：若 Redis 快取刪除失敗，短時間內前台可能讀到舊的快取資料。需考慮重試機制或短 TTL 來輔助。
- **跨服務資料同步**：若外部服務（如 pricecentersite、memberservice）依賴此 Redis 快取，更新訊息時未同步失效可能導致跨服務資料不一致。
- **高風險 table**：`sport.notification_messages`（寫入錯誤的 TID/ID 或覆蓋歷史資料的風險）。
- **Queue retry**：無直接使用隊列，但若未來擴展非同步快取清除，必須考慮冪等性。

---

## 10. 常見錯誤

- ❌ 更新訊息時，一併變更了 `TID`（把訊息從原本主題移到別的主題）。
- ❌ 刪除 Redis 快取時，使用了錯誤的 `hashKey` 演算法或忘記此步驟，導致前台持續顯示舊資料。
- ❌ 忘記更新 `UpdateTime` 欄位，影響前台依時間排序或顯示。
- ❌ 前端傳入的 `Enabled` 值非 int 或非 0/1，未在後端做嚴格驗證就直接寫入 DB。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | NotificationController.PutMessage |
| DB | Sport DB, notification_messages table |
| Redis | Redis SportCache, NotificationMessages_{hashKey} |
| 寫入規則 | pricecentermanage-detail.md: Redis DEL 時機 |
| DB 欄位 | notification_messages schema (TID, ID, Enabled, Title, ...) |