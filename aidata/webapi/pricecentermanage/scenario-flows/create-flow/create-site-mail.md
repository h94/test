# 建立站內信

## 1. 場景目的

後台客服或行銷人員發送站內信給特定會員帳號。系統將信件內容寫入 `sport.notification_sitemails`，並同步更新 Redis 快取 `SportAccountCache`，確保前台會員可即時看到最新的站內信主旨。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/sport/notifications/sitemails` | 建立站內信 |

- **需要驗證**：✅（後台管理員權限）
- **Request Body**：`SportSiteMailDTO`（依 OpenAPI）
- **Response**：`200`（無特定 response content）

---

## 3. 流程總覽

1. 接收後台管理員 request，包含 `Account`、`Subject`、`Content` 等資訊。
2. 驗證管理員權限（ECFramework 驗證框架）。
3. 驗證 `Account` 是否存在於會員系統（需人工確認：目前 context 未看到此驗證步驟，但 db-detail 提及應檢查帳號是否存在）。
4. 寫入一筆記錄至 MySQL `sport.notification_sitemails`（`ReadStatus` 設為 0）。
5. 更新 Redis `SportAccountCache` 中對應的 `SiteMails_{Account}` Hash 快取，加入新的站內信主旨。
6. 回傳成功。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `NotificationController.CreateSiteMail` | 接收 `SportSiteMailDTO`，呼叫 Service。 |
| 2 | Service | `INotificationService.CreateSiteMail` | 負責業務邏輯：驗證、呼叫 Provider / Redis。 |
| 3 | Provider | `ISportNotificationProvider.CreateSiteMail`（推測） | 執行 MySQL INSERT 至 `sport.notification_sitemails`。 |
| 4 | Service | `INotificationService.CreateSiteMail` | 呼叫 Redis 更新 `SiteMails_{Account}` 快取。 |
| - | - | - | 需人工確認：確切 Class/Method 名稱以實際 code 為準；若未實作 Account 驗證，應補上。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (MySQL Sport) | notification_sitemails | Write (INSERT) | 寫入站內信完整記錄（含 Content）。 |
| Redis (SportAccountCache) | SiteMails_{Account} | Write (HSET) | 更新該帳號的站內信主旨快取。 |

**注意**：無 Queue / Kafka 操作。

---

## 6. 重要規則

- **權限限制**：只有後台管理員可呼叫此 API。
- **欄位限制**：
  - `SportSiteMailDTO`（依 OpenAPI 推測）應至少包含 `Account`（char 11）、`Subject`（varchar 50）、`Content`（mediumtext）。
  - `SendTime` 為伺服器端生成之 UTC 時間戳（bigint）。
  - `ReadStatus` 初始值強制設為 `0`（未讀），不可由 request 給定。
- **不可暴露資料**：無。此 API 本身不回傳任何會員資料。
- **TTL 規則**：Redis Key `SiteMails_{Account}` 為永久，但 1) 當使用者讀取後可能更新（需人工確認），2）管理後台刪除站內信時會主動清除快取。
- **Transaction 規則**：需人工確認 DB 寫入失敗時是否有 rollback 機制；目前無 evidence 顯示有強 transaction。
- **Retry 規則**：需人工確認。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 帳號不存在 | （需人工確認）預期回傳錯誤，拒絕發送。 |
| 權限不足 | 401 / 403。 |
| Account 為空或格式錯誤 | 400 Bad Request。 |
| Subject 或 Content 為空 | 400 Bad Request。 |
| DB timeout / 寫入失敗 | 500 Internal Server Error。 |
| Redis 寫入失敗 | （需人工確認）依實作決定：可能報錯，但 DB 已寫入。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SITEM-01 | API Test | 正常發送站內信（含正確權限） | 200 OK；DB 新增一筆，ReadStatus=0。 |
| SITEM-02 | API Test | 無權限呼叫 | 401 / 403。 |
| SITEM-03 | API Test | Account 為空 | 400 Bad Request。 |
| SITEM-04 | Flow Test | 發送後查詢 `GET /subjects` | Redis 中 `SiteMails_{Account}` 包含新主旨。 |
| SITEM-05 | Integration Test | DB 寫入成功但 Redis 不可用 | （需人工確認）依實作決定：整體失敗或僅 DB 寫入。 |

---

## 9. 高風險區域

- **站內信 Write / Delete API**：為敏感操作，權限需嚴格控管。
- **Cache consistency**：Redis `SiteMails_{Account}` 更新在寫入 DB 之後，若更新失敗會導致不一致；需確認有無補償或警報機制。
- **無搜尋功能**：`notification_sitemails` Table 無 `SendTime` 等索引，大量查詢可能直接依賴快取，需確保快取正確性。
- **ID 生成**：`ID` 欄位（char 10）需保證唯一性。

---

## 10. 常見錯誤

- ❌ **發送站內信時 `Account` 填錯** → 前台使用者無法收到信，應有帳號清單 UI 供選擇。
- ❌ **忘記同步更新 Redis 快取** → 會員端 `/subjects` 查不到新主旨，疑為 bug。
- ❌ **`ReadStatus` 初始化錯誤（設為 1）** → 站內信一發送就變成已讀。
- ❌ **Request Body 允許傳入 `SendTime`** → 可能造成時間錯亂或偽造，應由後端賦值。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `NotificationController.CreateSiteMail`（推測）|
| DB | `sport.notification_sitemails`（DB Schema sport.md） |
| Redis | `SiteMails_{Account}`（Service detail Redis 章節）|
| Schema | OpenAPI `paths./api/v1/sport/notifications/sitemails.post` |
| 權限 | README 說明「需要驗證」 |