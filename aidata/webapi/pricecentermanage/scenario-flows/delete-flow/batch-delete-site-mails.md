# 批次刪除站內信

## 1. 場景目的

管理員透過後台 API **批次刪除指定帳號的站內信記錄**，並同步清除對應帳號的 Redis 快取，確保前台查詢一致性。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/sport/notifications/sitemails/delete` | 管理員權限，批次刪除多筆站內信 |

---

## 3. 流程總覽

1. 接收 request body（`List<SportSiteMail>`），每筆至少包含 `Account` 與 `ID`。  
2. 驗證 JWT token，確認使用者具備管理後台權限。  
3. 依 `(Account, ID)` 對 `notification_sitemails` 執行 DELETE。  
4. 收集所有被刪除記錄的 `Account`（去重），對每個帳號執行 `DEL SiteMails_{account}`。  
5. 回傳成功（HTTP 200）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `NotificationController.DeleteSiteMails` | 接收 `List<SportSiteMail>` 請求體，授權過濾後呼叫 Service |
| 2 | Validator | `AuthorizeAttribute` (ECFramework 統一認證) | 驗證 JWT 並檢查後台角色權限 |
| 3 | Service | `INotificationService.BatchDeleteSiteMails` | 遍歷請求列表，逐筆呼叫 Provider 刪除 |
| 4 | Provider | `ISportDbProvider.DeleteSiteMail` | 執行 SQL `DELETE FROM notification_sitemails WHERE Account = @Account AND ID = @ID` |
| 5 | Service | （同上） | 收集所有成功刪除的 `Account`，呼叫 Redis Provider 清除快取 |
| 6 | Provider | `IRedisCacheProvider.RemoveAsync(key)` | 針對每個 Account 執行 `DEL SiteMails_{account}` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (MySQL) | `sport.notification_sitemails` | DELETE | 刪除指定 `(Account, ID)` 的站內信記錄 |
| Redis | `SiteMails_{account}` (Hash) | DEL | 清除該帳號站內信主旨快取，確保前台查詢立即可見變更 |
| Queue / Kafka | 無 | 無 | 此流程不涉及訊息佇列 |

---

## 6. 重要規則

- **權限限制**：僅後台管理員（具備 `NotificationManagement` 角色或同等權限）能呼叫此 API。
- **欄位限制**：請求體中 `Account` 與 `ID` 為必填；不可傳入其他欄位。
- **不可暴露資料**：刪除操作不可回傳任何站內信內容。
- **TTL 規則**：`SiteMails_{account}` 為永久快取（無 TTL），資料變更後**必須主動刪除**。
- **Transaction 規則**：本流程未使用跨儲存體交易；刪除成功但 Redis DEL 失敗時，快取可能殘留舊資料（需人工確認是否補刪）。
- **Retry 規則**：不支援 Retry；若單筆 DELETE 失敗（例如 ID 不存在），**不影響其他筆**，此為軟性批次。
- **狀態值限制**：無（直接物理刪除）。
- **不可修改欄位**：無。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 缺少 JWT 或權限不足 | HTTP 401/403 |
| 請求體為空或格式錯誤 | HTTP 400 Bad Request |
| 部分 `ID` 不存在 | HTTP 200（忽略不存在記錄，不報錯） |
| DB 連線失敗或 timeout | HTTP 500，伺服器錯誤（不執行後續 Redis 清除） |
| Redis 寫入失敗或連線中斷 | HTTP 200（DB 已刪除，Redis 殘留舊資料；應有監控告警） |
| 傳入不存在的 `Account` | 仍執行 DELETE（不影響 DB），後續 `DEL` 亦無作用，回傳 200 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | API Test | 提供合法 JWT 與一組有效的 `(Account, ID)` | 200 OK，DB 中記錄消失，Redis Key 被刪除 |
| T02 | Permission Test | 使用無後台權限的 Token | 403 Forbidden |
| T03 | Flow Test | 傳入多筆，其中一筆 ID 不存在 | 仍回 200，存在筆被刪除，不存在筆無影響 |
| T04 | Integration Test | Redis 連線異常時呼叫 | 200 OK，DB 刪除成功，Redis 操作失敗（日誌記錄錯誤） |
| T05 | Flow Test | 傳入空陣列 | 200 OK，無任何操作 |

---

## 9. 高風險區域

- **高風險 table**：`notification_sitemails`（直接執行 DELETE，無軟刪除機制，誤刪無法恢復）。
- **高風險 API**：`POST /api/v1/sport/notifications/sitemails/delete`（須嚴控權限）。
- **Cache consistency**：Redis `SiteMails_{account}` 快取清除與 DB 操作非原子性；若 Redis DEL 失敗，前端可能仍看到已刪除的站內信主旨，需監控補救策略。
- **Idempotency**：當前設計為 **非冪等**，重覆呼叫會導致第一次之後的請求因記錄不存在而無實際影響，無負面作用但無防護。
- **Batch 效能**：大量筆數（如 1000+）可能造成 SQL 語句過長或連線耗盡；建議限制批次上限（需人工確認當前是否有限制）。

---

## 10. 常見錯誤

- ❌ **誤認為是軟刪除** → 此 API 為物理刪除（DELETE），沒有 `IsDeleted` 欄位，刪除後無法回復。
- ❌ **忘記清除 Redis 快取** → 刪除 DB 後若未 `DEL SiteMails_{account}`，前台 `GET /api/v1/sport/notifications/sitemails/{account}/subjects` 仍會回傳舊資料。
- ❌ **未對帳號去重就重複 DEL** → 同一帳號多筆站內信刪除時，只需清除一次 Redis Key，重複 DEL 無害但建議去重。
- ❌ **在請求中傳入 `ReadStatus` 或其他欄位** → 只需 `Account` 與 `ID`，其他欄位應忽略。
- ❌ **未驗證 Account 格式** → 可能受到 SQL injection（但使用參數化查詢可避免）；`Account` 格式為 `char(11)`，需確保不會截斷。
- ❌ **Redis 鍵名寫死而無前綴** → 應使用 `SportAccountCache` 管理器確保存取一致 `SiteMails_{account}`。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/sport/notifications/sitemails/delete` (README.md, OpenAPI) |
| DB 操作 | `sport.notification_sitemails` (DELETE Statement) (sport-detail.md, db schema) |
| Redis | `SiteMails_{account}` (DEL 操作) (pricecentermanage Redis 說明) |
| 權限驗證 | ECFramework.ECService 統一驗證 (README.md) |
| 服務角色 | `pricecentermanage` 對 `notification_sitemails` 具有寫入權限 (sport-detail.md 服務角色總覽) |