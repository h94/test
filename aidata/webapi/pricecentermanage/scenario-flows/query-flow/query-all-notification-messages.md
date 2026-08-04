# 查詢所有通知訊息

## 1. 場景目的

供管理後台查詢所有已啟用的通知訊息，不限定主題，用於全局檢視或管理通知內容。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sport/notifications/messages` | 查詢所有通知訊息（需驗證） |

---

## 3. 流程總覽

1. 請求進入 `NotificationController`，呼叫 `INotificationService`。
2. `Service` 層嘗試從 Redis 快取讀取 `NotificationMessages_{hashKey}`。
3. 若 Redis 命中的話，直接回傳快取資料。
4. 若 Redis 未命中（miss），需人工確認：是由排程預載入，還是此次查詢會回源 DB 重組並回寫快取。
5. 最終回傳 `SportMessageDTO` 列表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `NotificationController.Messages()` | 接收 GET，呼叫 `INotificationService.Messages()` |
| 2 | Service | `NotificationService.Messages()` （推測） | 組合 Redis key，呼叫 `NotificationMessageCacheProvider` |
| 3 | Provider | `NotificationMessageCacheProvider.GetMessages()` （推測） | 讀取 Redis `NotificationMessages_{hashKey}` |
| 4 | 可能分支 | `NotificationMessageProvider` （推測） | 若 Redis miss，查詢 MySQL `notification_messages WHERE Enabled = 1` |

> **注意**：`hashKey` 的產生規則需人工確認。可能是一個常數（例如 "all"），代表全量快取。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | `NotificationMessages_{hashKey}` (SportCache) | Read | 快取全量已啟用訊息 |
| MySQL | `notification_messages` (Sport) | Read (if miss) | Redis miss 時回源查詢 |

---

## 6. 重要規則

### 權限限制
- **API 需驗證**：`[Auth]`。

### 欄位限制
- **不可回傳欄位**：無。
- **過濾規則**：`Enabled = 1`（僅查詢已啟用的訊息）。
- **語系欄位**：`TW_Content`、`EN_Content`、`CN_Content` 等應全部回傳，由前端決定顯示哪個語系。

### 快取規則
- **Redis Key**：`NotificationMessages_{hashKey}` （Hash 結構，field 為 message id）。
- **快取失效**：任何一筆通知訊息變更（Create / Update）時，需**主動刪除**（DEL）此 Key，確保快取與 DB 一致性。
- **快取載入**：需人工確認：可能是首次查詢時動態載入，也可能是後台排程預載。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| Redis 連線失敗 / Timeout | 回傳 5xx 或 fallback 至 MySQL 查詢（需人工確認 fallback 行為） |
| MySQL 查詢失敗 | 回傳 5xx Server Error |
| Redis miss 且無預載機制 | 需人工確認：是否直接查 MySQL 或回傳空列表 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | API Test + Cache Test | Redis 存在 `NotificationMessages` 快取 | 直接回傳快取資料，不查 MySQL |
| T2 | API Test + DB Test | 清除 Redis 快取後請求 | 回傳 MySQL 中所有 `Enabled=1` 的記錄 |
| T3 | API Test | MySQL 無任何 `Enabled=1` 的記錄 | 回傳空陣列 `[]` |
| T4 | Permission Test | 未帶合法 token | 回傳 401 Unauthorized |

---

## 9. 高風險區域

- **Cache Consistency**：清除快取的時機至關重要。若 `PUT /api/v1/sport/notifications/messages/{tid}/{id}` 更新後忘記清除 `NotificationMessages_{hashKey}`，會導致管理後台顯示過時資料。
- **Cache Key 命名**：`hashKey` 必須唯一對應「全量已啟用訊息」這個業務範圍，避免與其他快取混淆。
- **全表查詢**：若 `SELECT * FROM notification_messages WHERE Enabled = 1` 無 Redis 緩衝，且訊息量極大，可能導致查詢效能瓶頸，需確認 MySQL 上有 `Enabled` 索引或已強制分頁。

---

## 10. 常見錯誤

- ❌ **更新訊息後忘記清除 `NotificationMessages_{hashKey}`**：導致 API 持續回傳舊資料。
- ❌ **直接查詢 MySQL 而不經過 Redis**：在無快取的狀況下，增加不必要的資料庫壓力。
- ❌ **只回傳特定語系內容**：API 無義務做語系過濾，應回傳所有語系欄位。
- ❌ **錯誤的 `hashKey` 組合方式**：若 `hashKey` 與 `tid` 掛鉤，會導致此 API 無法正確回傳所有主題的訊息。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `PriceCenterManage.WebAPI.Controllers.NotificationController.Messages()` |
| DB | `sport.notification_messages` |
| Redis | `NotificationMessages_{hashKey}` （pricecentermanage-detail.md） |
| Code | `NotificationService.Messages`，`NotificationMessageProvider`（Phase0/1 分析） |
| 規則 | 更新通知訊息後需 DEL 快取（pricecentermanage-detail.md） |