# 建立通知訊息

## 1. 場景目的

管理員在後台選擇一個已存在的通知主題後，為該主題新增一則多語系的通知訊息內容。此操作會將數據寫入 MySQL `sport.notification_messages` 表，並刪除對應的 Redis 快取，以確保前台能即時取得最新資料。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/sport/notifications/messages/{tid}` | 在指定主題下新增一則訊息，需驗證 |

- **Path 參數**：`tid` (string) 為已存在於 `notification_topics` 的主題 ID。
- **Request Body**：`SportMessageDTO` (JSON)，包含 `Title` 及多語系內容，如 `TW_Content`, `EN_Content` 等。
- **需要驗證**：是，需通過 ECFramework 驗證。

---

## 3. 流程總覽

1.  **接收請求與驗證**：Controller 接收 HTTP POST 請求，框架自動驗證使用者身份與權限。
2.  **主題存在性檢查**：Service 層執行業務邏輯，先查詢 `sport.notification_topics`，確認指定的 `TID` 確實存在。若主題不存在，則拋出錯誤。
3.  **資料組裝與寫入**：Service 組裝 `SportMessage` 物件，設定 `Enabled` 預設為 1（啟用），並產生新的 `ID` 和 `UpdateTime`。Provider 層執行 SQL `INSERT` 語句，將訊息寫入 MySQL `sport.notification_messages` 表。
4.  **清除快取**：寫入成功後，Service 層負責刪除 Redis 中對應的快取 Key `NotificationMessages_{hashKey}`，確保快取一致性。此操作為非同步，失敗僅記錄不影響主流程。
5.  **回傳成功**：回傳 HTTP 200 OK。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `NotificationController.CreateMessage` | 接收請求，呼叫 SportService 的對應方法。 |
| 2 | Service | `SportService.CreateMessage` (推測) | 查詢主題存在性；組裝 SportMessage 物件；呼叫 Provider 寫入 DB。 |
| 3 | Provider | `SportProvider.InsertMessage` (推測) | 執行 SQL `INSERT` 至 `sport.notification_messages`。 |
| 4 | Service | `SportService.CreateMessage` (推測) | 呼叫 `ClearMessageCache` 來刪除 Redis 快取。 |
| 5 | Service | `CacheService.Del` (推測) | 執行 Redis `DEL` 指令，刪除 `NotificationMessages_{hashKey}`。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| **DB** | `sport.notification_topics` | Read | 驗證 `{tid}` 是否存在於主題表中。 |
| **DB** | `sport.notification_messages` | Write | 將新的通知訊息（含多語系內容）寫入此表。 |
| **Redis** | `NotificationMessages_{hashKey}` | Delete | 寫入成功後，刪除該主題下的訊息列表快取，以強制下次查詢時重建。 |

---

## 6. 重要規則

- **權限限制**：僅 `pricecentermanage` 服務具有寫入 `sport.notification_messages` 的權限。
- **欄位限制**：
    - `Enabled`：此場景寫入時預設值為 1（啟用）。
    - 多語系欄位 (`TW_Content`, `EN_Content`, ...)：`TW_Content` 不可為空，其他語系可為空，前台需有 fallback 機制。
- **不可暴露資料**：無額外限制，此為管理後台專用 API。
- **TTL 規則**：No TTL，快取為永久保存，直到因 DB 更新而被動刪除。
- **Transaction 規則**：需人工確認，此流程為單一 SQL INSERT 操作，除非涉及後續會計或紀錄，否則 DB Transaction 非必要。
- **快取規則**：DB 寫入成功後，**必須主動** `DEL` Redis Key `NotificationMessages_{hashKey}`，不可僅依賴 TTL。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求的 `{tid}` 在 `notification_topics` 中不存在 | 回傳 HTTP 400 Bad Request 或 404 Not Found，並附帶明確錯誤訊息，如 "通知主題不存在"。 |
| 缺乏管理員權限或未登入 | ECFramework 驗證攔截，回傳 HTTP 401 Unauthorized 或 403 Forbidden。 |
| MySQL INSERT 失敗 (e.g. 連線中斷、約束違反) | 回傳 HTTP 500 Internal Server Error，並記錄錯誤日誌。 |
| Redis DEL 操作失敗 (e.g. 連線中斷) | 僅記錄警告日誌，不影響主要流程，仍回傳 HTTP 200 OK。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | Flow Test | 以有效主題 ID 和完整內容請求。 | 成功寫入一筆啟用的訊息至 `notification_messages`；Redis 對應 Key 被刪除。 |
| T02 | API Test | 以不存在的 `{tid}` 請求。 | API 回傳 400，且 DB 中無新增任何記錄。 |
| T03 | Permission Test | 以未授權（一般使用者）的 Token 請求。 | API 回傳 403。 |
| T04 | Flow Test | 模擬 Redis 連線失敗，但 MySQL 寫入成功。 | API 仍回傳 200 OK，但系統日誌中會記錄快取清除失敗的警告。 |

---

## 9. 高風險區域

- **高風險 Table**：`sport.notification_messages`。寫入資料不完整（如缺少主要語系）可能導致前台顯示異常。
- **高風險 API**：此寫入 API。需要確保併發請求下的 ID 生成唯一性，或在 DB 層處理衝突。
- **Cache Consistency**：若 Redis DEL 操作與讀取請求交錯，或有短暫的時間窗口，前台可能會讀到舊的訊息列表。此風險為可接受。

---

## 10. 常見錯誤

- ❌ **新增訊息時未檢查 `TID` 是否存在** → 導致 `notification_messages` 中產生孤立記錄。
- ❌ **忘記在寫入成功後清除 Redis 快取** → 前台管理或查詢訊息時，看不到新建立的訊息，造成資料不一致的假象。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `README.md`, OpenAPI `paths./api/v1/sport/notifications/messages/{tid}.post` |
| DB | `sport.notification_messages` schema, `db/sport-detail.md` (寫入權限、欄位說明) |
| Redis | `pricecentermanage-detail.md` (操作 `NotificationMessages_{hashKey}`, 時機) |
| Code | `SportService.CreateMessage`, `SportProvider.InsertMessage`, `ClearMessageCache` (推測，基於 .NET 分層慣例) |