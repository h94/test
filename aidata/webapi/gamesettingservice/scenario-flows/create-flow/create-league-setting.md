# 建立聯賽設定

## 1. 場景目的
為特定公司（company）與遊戲類型（gameType）建立聯賽級別的遊戲設定（league settings）。透過此流程，運營人員可在後台配置聯賽維度的玩法模式、賠率限制等設定，並自動記錄操作日誌。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/league/{gameType}` | 建立聯賽設定（包含 settings JSON） |

需驗證 ✅

---

## 3. 流程總覽

1. 接收聯賽設定建立 request（含 `company`, `gameType`, `id`, `settings` 等）。
2. 驗證 request 結構（`settings` 須為合法 JSON）。
3. 寫入 `gamesettings.league_settings` 表。
4. 記錄操作日誌至 `pricecenter.action_logs`（透過 Kafka 或 Cassandra）。
5. 回傳成功訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GameSettingServiceController.CreateLeagueSetting` | 接收 HTTP POST request，呼叫 Service |
| 2 | Service | `ILeagueService.CreateLeagueSetting` | 驗證 JSON 格式，組裝 insert 語句 |
| 3 | Provider | `LeagueSettingProvider.InsertAsync` | 寫入 `gamesettings.league_settings` |
| 4 | Service | `ILogService.InsertActionLog` | 非同步寫入操作日誌 |
| 5 | Controller | `GameSettingServiceController` | 回傳 HTTP 200 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `gamesettings.league_settings` | INSERT | 新增聯賽設定 |
| DB (Cassandra) | `pricecenter.action_logs` | INSERT | 記錄操作日誌（via Kafka or direct） |
| Redis | 無直接寫入 | - | 需人工確認：本服務不直接管理 Redis，但 `syncservice` 後續可能設定 `gamesettings:game:{id}` 快取 |

---

## 6. 重要規則

- **權限限制**：需通過 ECFramework 統一驗證，僅授權帳號可操作。
- **欄位限制**：
  - `settings` 欄位須為合法 JSON 字串，不可包含非序列化物件或非法格式。
  - `id` 欄位為聯賽設定主鍵，建立後不可更新。
  - `updater` 欄位由系統自動填入當前操作者帳號，禁止客戶端傳入。
- **不可暴露資料**：任何 API 回傳皆不可包含 `password` 或 `authtoken`。
- **TTL 規則**：`league_settings` 表未設定 TTL（`default_time_to_live = 0`），資料永久儲存。
- **Transaction 規則**：Cassandra 無跨表事務，寫入 `league_settings` 與 `action_logs` 為非原子操作，失敗時可能導致日誌遺漏。需人工確認：是否有補償機制。
- **狀態值限制**：`enabled` 欄位（如存在）限 0（停用）或 1（啟用）。需人工確認：`league_settings` 是否包含 `enabled` 欄位，根據 partial schema 推斷可能存在。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `settings` 欄位為非法 JSON 字串 | 回傳 400 Bad Request，拒寫入 |
| `company` + `gameType` 組合不存在於 `gametype_settings` | 回傳 400 或 422，提示無此 gameType 設定 |
| Cassandra `league_settings` 寫入失敗（timeout 或 unavailable） | 回傳 503 Service Unavailable |
| `action_logs` 寫入失敗 | 聯賽設定已寫入，但操作日誌遺失（需人工確認：是否影響審計） |
| 未通過 ECFramework 驗證 | 回傳 401 Unauthorized |
| `id` 已存在 | 回傳 409 Conflict（Cassandra INSERT 主鍵衝突） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| CLS-01 | API Test | 正常建立聯賽設定（合法 JSON） | 200 OK，資料寫入 `league_settings` |
| CLS-02 | Permission Test | 無效 token 呼叫 | 401 Unauthorized |
| CLS-03 | Integration Test | `settings` 為非法 JSON 字串 | 400 Bad Request |
| CLS-04 | Flow Test | 寫入後查詢 `GET /api/v1/league/{gameType}/{id}` | 回傳與建立時相同資料 |
| CLS-05 | Integration Test | Cassandra 暫時不可用 | 503 Service Unavailable，資料未寫入 |

---

## 9. 高風險區域

- **高風險 table**：`gamesettings.league_settings` — 若 `settings` 格式錯誤，可能導致前台下注顯示異常或玩法無法解析。
- **高風險 API**：`POST /api/v1/league/{gameType}` — 直接影響玩家看到的聯賽玩法選項。
- **跨服務資料同步**：需人工確認：聯賽設定變更後，是否需要通知 `pricecenterservice` 或 `gameengine` 進行賠率重算或賽事重新派發。
- **Transaction**：聯賽設定與日誌非原子寫入，可能導致審計缺口。
- **Cache consistency**：需人工確認：`syncservice` 是否在寫入後清除 Redis 快取 `gamesettings:game:{id}`，否則前台可能看到過期設定。
- **Idempotency**：`id` 為主鍵，重複請求會報錯。需人工確認：是否支援 PUT 或 upsert 以支援冪等。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 在 `settings` 傳入非 JSON 格式字串，導致 Service 層拋出例外。
  - 未設定 `updater` 欄位，但 Service 應自動填入。
  - 以 `email` 或 `authtoken` 作為查詢條件（無索引支援），在本場景不適用但易混淆。
- **AI 容易誤解**：
  - 以為此服務直接用 Redis 快取聯賽設定（實際由 `syncservice` 管理）。
  - 誤判 `league_settings` 的主鍵結構（schema 截斷，實際為 `company` + `gametype` + `id` 複合主鍵，需人工確認）。
- **常見漏檢查項目**：
  - 未驗證 `settings` JSON 結構的完整性（例如缺少必要 play mode key）。
  - 未記錄操作日誌，導致審計追蹤中斷。
- **常見錯誤流程**：
  - 直接呼叫 Provider 插入 `league_settings`，而忽略 Service 層的驗證與日誌邏輯。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | GameSettingServiceController (POST `/api/v1/league/{gameType}`) |
| DB (寫入) | `gamesettings.league_settings` INSERT |
| DB (日誌) | `pricecenter.action_logs` INSERT (via `ILogService`) |
| Code | `ILeagueService.CreateLeagueSetting` |
| SQL | `INSERT INTO gamesettings.league_settings (company, gametype, id, settings, updater) VALUES (?, ?, ?, ?, ?)` |
| 驗證 | `settings` 欄位須為合法 JSON（from `gamesettings-detail.md`） |
| 日誌 | 操作日誌寫入 `pricecenter.action_logs`（from `gamesettings-detail.md`） |

---

## 12. 建議新增文件 / 規則 / 測試

- **建議新增文件**：`league_settings` table 完整 schema 與主鍵定義（目前部分截斷）。
- **建議新增規則**：聯賽設定變更時，應定義跨服務通知協定（如 Kafka event）以同步設定至下游服務。
- **建議新增測試**：
  - 整合測試：驗證 `action_logs` 寫入成功與失敗時的系統行為。
  - 冪等性測試：重複 POST 相同 `id`，確認回傳 409 Conflict 或支援 upsert。