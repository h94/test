# 查詢主題下的通知訊息

## 1. 場景目的
後台管理員或前台用戶依主題 TID 取得該主題下所有已啟用的通知訊息列表，作為推播通知內容。查詢優先使用 Redis 快取，以減輕 MySQL 負擔並提升回應速度。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/sport/notifications/messages/{tid}` | 依主題 ID 查詢訊息列表 |

> **需驗證**：是  
> **參數**：`tid` (path, required, string)  

---

## 3. 流程總覽

1. 客戶端攜帶驗證 token 請求 API  
2. `ECFramework` 驗證通過  
3. Controller 接收 `tid` 參數，呼叫 Service  
4. Service 嘗試從 Redis `NotificationMessages_{tid}` 讀取全部欄位（Hash）  
   - **命中**：反序列化為訊息列表直接回傳  
   - **未命中**：查詢 MySQL `sport.notification_messages`  
5. MySQL 查詢：`WHERE TID = ? AND Enabled = 1`  
6. 將查詢結果批次寫入 Redis Hash（field = ID, value = SportMessageJSON）  
7. 回傳 `SportMessageDTO` 列表

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Middleware | ECFramework | 驗證請求權限 |
| 2 | Controller | `NotificationController.GetMessages(int tid)` | 接收 tid，調用 Service |
| 3 | Service | `SportNotificationService.GetMessagesAsync(int tid)` | 查詢快取或 DB |
| 4 | Provider | 快取層 `SportCacheProvider` | `HashGetAll("NotificationMessages_{tid}")` |
| 5 | Provider | SQL 層 (若快取未命中) | `SELECT * FROM notification_messages WHERE TID=@tid AND Enabled=1` |
| 6 | Provider | 快取層 | `HashSet("NotificationMessages_{tid}", fields)` |
| 7 | Transfer | DTO 映射 | 將 Entity 轉為 `SportMessageDTO` 回傳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `sport.notification_messages` | Read (`WHERE TID = ? AND Enabled = 1`) | 取得該主題下所有啟用訊息 |
| Redis | `NotificationMessages_{tid}` (SportCache) | GET (Hash) / SET (Hash) | 快取訊息列表，避免重複查 DB |

---

## 6. 重要規則

- **權限限制**：僅通過 ECFramework 驗證的請求可存取，未區分角色（需人工確認是否需要管理員權限）  
- **欄位限制**：回傳 `SportMessageDTO`，不包含內部稽核欄位或密碼相關資訊  
- **不可暴露資料**：`notification_messages.Content` 依語系回傳對應內容，不可同時回傳所有語系內容（由前端選擇，但後端可能全回傳）？[需人工確認]  
- **TTL 規則**：Redis Key `NotificationMessages_{tid}` 無 TTL（永久），但 DB 資料變更時需透過管理後台或其他流程主動 DEL 此 Key  
- **查詢條件**：必須指定 `TID` 且過濾 `Enabled = 1`，避免回傳已停用的訊息  
- **不可修改欄位**：本流程僅讀取，不可修改任何 DB 或快取中的資料  

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `tid` 不存在 (DB 中無任何訊息) | 回傳空陣列 `[]` |
| `tid` 存在但所有訊息 `Enabled=0` | 回傳空陣列 `[]` |
| Redis 連線失敗 | 降級直接查詢 DB 並回傳，不寫入快取；可記錄錯誤 log |
| DB 查詢失敗 (timeout / 異常) | 回傳 500 或適當錯誤碼 |
| 請求未帶合法 token | ECFramework 攔截，回傳 401 |
| `tid` 格式非法 (非預期長度/型別) | 回傳 400 Bad Request |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T01 | API Test | 正常 tid，有啟用訊息 | 200，回傳訊息列表 |
| T02 | Cache Test | 二次請求相同 tid | 第二次應命中 Redis，不查 DB（可透過 log 驗證） |
| T03 | Cache Miss Test | 清除 Redis 後請求 | 觸發 DB 查詢並重新寫入 Redis |
| T04 | DB Fallback | 停用 Redis 後請求 | 正確回傳 DB 結果 |
| T05 | Permission | 無 token 請求 | 401 |
| T06 | Empty Result | tid 無任何訊息或全部停用 | 200，回傳空陣列 |
| T07 | 語系回傳 | 不同 Accept-Language | 需人工確認：回傳是否過濾語系內容，或由前端處理 |

---

## 9. 高風險區域

- **Cache consistency**：若訊息內容被更新或停用，但 Redis 快取未即時刪除，會導致前端看到舊資料或已停用訊息。需確保管理後台更新訊息時主動 `DEL NotificationMessages_{tid}`。  
- **Redis 故障**：若 Redis 完全不可用，每次請求都查 DB，可能造成 DB 壓力。應考慮熔斷機制 (未實作風險)。  
- **批次寫入**：將整個主題下的訊息寫入一個 Hash，若訊息數量極大可能影響 Redis 效能。`NotificationMessages_{tid}` 目前設計為永久且無 TTL，需監控記憶體使用。  
- **DB 查詢**：未指定 `ID` 只查 `TID`，若單一主題訊息過多可能產生慢查詢。需確保 `TID` 有索引（根據 schema 推測為複合主鍵 `(TID, ID)`，應可高效查詢）。

---

## 10. 常見錯誤

- ❌ **查詢時忘記過濾 `Enabled=1`** → 可能回傳已停用的訊息  
- ❌ **寫入 Redis 時未使用 Hash 結構** → 破壞與其他服務的快取一致性約定  
- ❌ **快取命中後仍查 DB** → 失去快取意義，浪費資源  
- ❌ **只在特定 API 設定快取，未更新訊息時同步刪除快取** → 快取與 DB 不一致  
- ❌ **假設 `tid` 一定存在** → 未處理空結果導致 500  
- ❌ **直接回傳 Entity 而洩漏不必要欄位** → 應透過 DTO 映射  

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI: `GET /api/v1/sport/notifications/messages/{tid}` |
| DB 結構 | MySQL `sport.notification_messages` (TID, ID, Enabled, ...) |
| Redis Key | `pricecentermanage-detail.md` 中定義 `NotificationMessages_{hashKey}` Hash 結構 |
| 驗證 | README: 所有通知相關 API 需要驗證 |
| DTO | OpenAPI schema: `SportMessageDTO` |
| 服務角色 | `pricecentermanage` 對 `notification_messages` 有讀寫權限 (sport-detail.md) |