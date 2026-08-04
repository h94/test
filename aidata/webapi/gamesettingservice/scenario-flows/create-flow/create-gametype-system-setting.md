# 建立 GameType 系統設定

## 1. 場景目的

為指定的公司（company）與遊戲類型（gameType）建立一筆系統層級的玩法設定，包含名稱、玩法內容（JSON）、showstopplaymode 等開關。寫入 `gamesettings.gametype_settings` 表，後續由前台服務讀取展示對應的玩法選項。

---

## 2. 入口 API

| Method | Path                      | 說明                                       |
|--------|---------------------------|--------------------------------------------|
| POST   | `/api/v1/system/{gameType}` | 建立指定 gameType 的系統設定，需驗證權限。 |

（來源：README GameSettingServiceController 路由表，OpenAPI 路徑定義）

---

## 3. 流程總覽

1. 後台操作者透過管理界面發起建立請求。
2. API 驗證操作者身分（Team Auth Token / Business Account）。
3. 檢查 `company` 是否存在（可能讀取 `gamesettings.businesses`）。
4. 校驗 `gameType` 是否合法（非空、格式符合）。
5. 確認 `company` + `gameType` 組合尚未存在（不允許重複建立，或按商業規則處理）。
6. 校驗 `settings` 欄位為合法 JSON 字串。
7. 自動填入 `updater` 為當前操作者帳號，`updatetime` 為當前時間戳。
8. 寫入 `gamesettings.gametype_settings`（INSERT）。
9. 記錄操作日誌（寫入 `pricecenter.action_logs` 或 `logs` 表）。
10. 回傳成功。

---

## 4. 程式流程

| 順序 | Layer       | Class / Method                     | 動作 |
|------|-------------|-----------------------------------|------|
| 1    | Middleware  | ECFramework Auth Filter           | 驗證請求的 `AuthToken` 或 Session |
| 2    | Controller  | `GameSettingServiceController.PostSystemSetting(gameType)` | 接收 DTO（含 company、settings 等） |
| 3    | Validator   | 可能內建 FluentValidation 或自訂  | 校驗必填欄位、JSON 格式合法性 |
| 4    | Service     | `IGameSettingService.CreateSystemSetting(company, gameType, ...)` | 檢查 company 有效性、主鍵衝突、組裝 entity |
| 5    | Provider    | `IGameSettingRepository.InsertGametypeSetting(record)` | 執行 Cassandra INSERT |
| 6    | Provider    | `ILogRepository.LogAction(...)`   | 寫入操作日誌（異步） |

（依據：README 服務建置、code semantics 推測分層）

---

## 5. DB / Cache / Queue 使用

| 類型    | 資源                          | 操作   | 用途                                  |
|---------|-------------------------------|--------|---------------------------------------|
| DB      | `gamesettings.gametype_settings` | Write  | 寫入新的系統設定                      |
| DB      | `gamesettings.businesses`       | Read   | 驗證 `company` 是否存在               |
| DB      | `pricecenter.action_logs`       | Write  | 記錄操作日誌（用於審計）              |
| Redis   | 未使用                        | -      | 本次流程不直接操作 Redis，後續更新快取由其他服務處理 |
| Queue   | Kafka（日誌）                 | Publish | 非同步寫入日誌（若採用 Kafka 日誌架構）|

---

## 6. 重要規則

- **權限驗證**：僅已驗證的管理後台帳號可建立設定（`gamesettingservice` 所有相關 API 皆需 ✅）。
- **settings 格式**：須為合法的 JSON 字串，不可包含非序列化物件。（`gamesettingservice-detail.md`）
- **updater 自動填入**：不允許客戶端傳入，由後端從當前 session 取得操作者帳號。（`gamesettings-detail.md`）
- **不可重複建立**：`company` + `gameType` 為主鍵，POST 若已存在應回傳 409 Conflict（需人工確認實作細節）。
- **company 有效性**：寫入前必須確認 `company` 存在於 `businesses` 表，否則拒絕。
- **showstopplaymode / swap**：boolean 值，接受 true/false，無額外限制。

---

## 7. 錯誤情境

| 情境                        | 預期結果                                   |
|----------------------------|--------------------------------------------|
| 未帶合法認證資訊            | HTTP 401                                   |
| 權限不足（非 admin 角色）   | HTTP 403                                   |
| `company` 不存在             | HTTP 400 或 404，訊息提示 company 無效      |
| `settings` 不是合法 JSON     | HTTP 400，指明格式錯誤                       |
| (company, gametype) 已存在   | 若實作禁止重複建立則回傳 409 Conflict       |
| Cassandra 寫入失敗           | HTTP 500，錯誤訊息不暴露細節                |
| 操作日誌寫入失敗            | 不影響主流程，僅記錄告警（可能非同步處理） |

---

## 8. 測試重點

| Test ID | 類型             | 情境                          | 預期結果                   |
|---------|------------------|-------------------------------|----------------------------|
| SYS01   | API Test         | 一般正常建立                  | 200, 回傳成功              |
| SYS02   | Permission Test  | 無 token 請求                 | 401                        |
| SYS03   | Functional Test  | settings 傳入非法 JSON         | 400                        |
| SYS04   | Flow Test        | 已存在相同 company+gameType   | 409 (若適用)               |
| SYS05   | DB Verify        | 寫入後查詢 gametype_settings  | 資料正確，updater 為操作者   |
| SYS06   | Audit Test       | 檢查 action_logs 是否寫入      | 有對應的 create 記錄       |

---

## 9. 高風險區域

- **settings 欄位**：若內容過大或結構複雜，可能導致序列化/反序列化異常，影響讀取服務。
- **company 驗證遺漏**：未檢查 `businesses` 表即寫入，產生孤立設定。
- **日誌漏失**：若操作日誌寫入失敗且未處理，將失去審計軌跡。
- **快取一致性**：更新後未通知相關服務清除快取（如 Redis key `gamesettings:…`），可能導致前端顯示舊資料。（此清除通常由 `syncservice` 或其他服務監聽變更後執行，非本次場景直接負責，但仍需留意）

---

## 10. 常見錯誤

- ❌ 請求時將 `updater` 作為參數傳入 → 應完全由後端填入，前端不傳。
- ❌ 未先驗證 `company` 是否存在 → 可能存入無效 company 的設定。
- ❌ `settings` 以物件而非字串傳遞 → 必須以 JSON 字串格式傳送。
- ❌ 誤用 PUT 等其他方法建立 → 此接口定義為 POST，需依循 REST 語意。
- ❌ 認為寫入後前台會立刻生效 → 可能尚有快取延遲，需了解系統同步機制。

---

## 11. Evidence

| 類型     | 來源                                      |
|----------|-------------------------------------------|
| API      | `POST /api/v1/system/{gameType}`          |
| DB       | `gamesettings.gametype_settings`          |
| Code     | `GameSettingServiceController.PostSystemSetting`（推測） |
| Rule     | `gamesettingservice-detail.md`：settings 必須為合法 JSON  |
| Rule     | `gamesettings-detail.md`：updater 自動填入，不接受 client 傳入 |
| Rule     | `gamesettingservice-detail.md`：寫入前應驗證 company 有效性 |