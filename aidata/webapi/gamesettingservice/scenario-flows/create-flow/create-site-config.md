# 建立站台設定

## 1. 場景目的

此場景描述管理員為特定商家（Business）建立對應的站台設定（SiteConfig），定義該商家在各遊戲類型（gameType）下的啟動狀態、是否顯示停止賽事玩法、是否交換主客隊等核心控制參數。該設定將直接影響前台玩家看到的玩法選項。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/siteconfigs` | 為指定商家建立一筆新的站台設定 |

---

## 3. 流程總覽

1. 接收包含 `businessCode`, `gameType`, `settings` 等參數的建立請求。
2. 由 `ConfigController` 接收並呼叫對應的 Service。
3. Service 層負責：
   - 驗證 `businessCode` 是否為已存在的有效商家。
   - 驗證 `settings` 欄位是否為合法的 JSON 字串。
   - 自動填寫 `updater` 為當前操作者帳號。
   - 將包含 `company`, `gametype`, `settings`, `enabled` 等欄位的資料寫入 `gamesettings.gametype_settings` 表。
   - 預設將該設定設為啟用（`enabled = 1`）。
4. 系統回傳操作成功狀態。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `ConfigController.CreateSiteConfig` | 接收請求、驗證 Token 與參數，呼叫對應的 Service。 |
| 2 | Service | `IConfigService.CreateGameTypePlayModeConfig` | 處理核心商業邏輯：驗證商家、驗證輸入、寫入資料。 |
| 3 | Provider | （需人工確認） `GamesettingProvider` | 執行對 Cassandra `gamesettings.gametype_settings` 表的 INSERT 操作。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `gamesettings.gametype_settings` | Write | 儲存該商家於特定 gameType 的站台設定。 |
| DB (Cassandra) | `gamesettings.businesses` | Read | 驗證 `businessCode` 是否存在且有效，用於隔離驗證。 |
| Queue | Kafka | Publish | **需人工確認**；建立設定後是否需要發布事件以達成快取一致性。 |

---

## 6. 重要規則

- **權限限制**：呼叫此 API 需要通過驗證，且操作者需具備對應商家的管理權限。
- **欄位限制**：
  - `settings` 欄位寫入時**必須是合法的 JSON 字串**，不可包含非序列化物件。
  - `updater` 欄位**不接受用戶端傳入**，必須由後端自動填入當前操作者帳號。
- **不可暴露資料**：任何 GET API 的回傳結果中，都不可包含商家（`businesses`）的 `authtoken` 或商家帳號（`business_accounts`）的 `password` 欄位。
- **狀態值限制**：`enabled` 預設為 1（啟用），若需停用，應透過更新 API (`PUT /api/v1/siteconfigs`) 進行，不可於建立時直接設為 0。
- **不可修改欄位**：記錄建立後，其複合主鍵（`company` + `gametype`）不可修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求中的 `businessCode` 不存在於 `gamesettings.businesses` 表中 | 拒絕請求，回傳錯誤：商家不存在。 |
| 請求中的 `settings` 包含非法 JSON 格式 | 拒絕寫入，回傳 HTTP 400 及格式錯誤訊息。 |
| 該 `company` 與 `gametype` 的設定已存在 | 拒絕建立，回傳衝突錯誤，提示應使用更新 API。 |
| 未經驗證的請求或無效的 Token | 阻擋於 Controller 層，回傳 HTTP 401 Unauthorized。 |
| Cassandra 寫入失敗或逾時 | 回傳 HTTP 500 內部伺服器錯誤，並記錄詳細日誌。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| IT-SC-01 | API Test | 以有效參數建立一筆新站台設定 | HTTP 200，且資料正確寫入 `gametype_settings` 表。 |
| IT-SC-02 | Flow Test | 驗證 `settings` 為非法 JSON 字串的請求 | HTTP 400。 |
| IT-SC-03 | API Test | 嘗試為不存在的 `businessCode` 建立設定 | HTTP 400 或 404，並有明確錯誤訊息。 |
| IT-SC-04 | API Test | 驗證 `updater` 欄位無視客戶端傳入值，正確顯示操作者帳號 | 檢查資料庫中的 `updater` 欄位不因請求內容而改變。 |
| IT-SC-05 | Permission Test | 使用不具備該商家管理權限的帳號呼叫 API | HTTP 401 或 403。 |

---

## 9. 高風險區域

- **高風險 table**：`gamesettings.gametype_settings`
- **Cache consistency**：若下游服務依賴此設定，寫入成功後需確保相關快取（如 Redis）被正確更新或失效，以避免資料不一致。
- **Idempotency**：由於 `company` + `gametype` 為複合主鍵，重複呼叫同內容的 API 會導致主鍵衝突錯誤，前端需妥善處理此回應。

---

## 10. 常見錯誤

- ❌ **新人容易犯錯**：將未經驗證的 JSON 字串或純文字直接傳入 `settings` 欄位，導致資料損毀。
- ❌ **AI 容易誤解**：誤以為此 API 處理的是 `game_settings` 表而非 `gametype_settings` 表。
- ❌ **常見漏檢查項目**：忘記驗證 `settings` 是否為合法 JSON 就進行寫入。
- ❌ **常見錯誤流程**：更新設定時，直接使用此建立 API，而非 PUT API，意圖覆蓋原有資料，應引導使用者使用正確的更新端點。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/siteconfigs` (ConfigController) |
| DB | `gamesettings.gametype_settings` |
| Code | `IConfigService.CreateGameTypePlayModeConfig` |
| Schema | `CREATE TABLE gamesettings.gametype_settings (... company text, gametype text, ..., PRIMARY KEY (company, gametype))` |
| Rule | `gamesettings-detail.md` - `settings` 欄位須為合法 JSON 字串 |
| Rule | `gamesettings-detail.md` - `updater` 欄位不接受用戶端傳入 |