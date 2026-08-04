# 查詢所有玩法設定

## 1. 場景目的
後台管理人員查詢指定商家（businessCode）在所有維度（GameType、聯賽、模板、單場）下的玩法設定，以便進行配置管理或審查。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/playmodeconfigs/all/{businessCode}` | 查詢所有玩法設定（需驗證） |

---

## 3. 流程總覽

1. 接收請求，從路徑取得 `businessCode`。
2. 驗證操作者權限（透過 ECFramework 驗證）。
3. 呼叫 `IConfigService.GetBusinessAllPlayModeConfig(businessCode)`（推測方法名，需人工確認）。
4. Service 層將 `businessCode` 當作 `company` 查詢 Cassandra `gamesettings` keyspace：
   - 查詢 `gametype_settings` 表（無 `enabled` 過濾，全部回傳）。
   - 查詢 `league_settings` 表，過濾條件 `enabled = 1`。
   - 查詢 `template_settings` 表，過濾條件推測為 `enabled = 1`（需人工確認）。
   - 查詢 `game_settings` 表，過濾條件 `enabled = 1` 且 `company = businessCode`。
5. 將查詢結果組裝為統一的回應結構（可能依維度分組）。
6. 回傳 JSON，各設定的 `settings` 欄位為合法 JSON 字串。
7. 過程中不涉及 Redis 快取（本服務不直接使用 Redis），不發布 Kafka 訊息（僅記錄日誌）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `ConfigController.GetAllPlayModeConfig` (推測) | 接收 GET 請求，驗證路由參數 |
| 2 | Service | `IConfigService.GetBusinessAllPlayModeConfig` (推測) | 調用多個 Provider 取得各維度設定 |
| 3 | Provider | `GameTypePlayModeProvider` (推測) | `SELECT * FROM gametype_settings WHERE company = ?` |
| 4 | Provider | `LeaguePlayModeProvider` (推測) | `SELECT * FROM league_settings WHERE company = ? AND enabled = 1` |
| 5 | Provider | `TemplatePlayModeProvider` (推測) | 查詢 `template_settings`，推測條件 `company = ? AND enabled = 1` |
| 6 | Provider | `GamePlayModeProvider` (推測) | `SELECT * FROM game_settings WHERE company = ? AND enabled = 1` |
| 7 | Service | 同上 | 合併結果，轉換為 DTO，排除敏感欄位（若有） |
| 8 | Controller | 同上 | 回傳 `200 OK` 與 JSON 陣列或物件 |

> **⚠ 需人工確認**：實際 Service 方法名、Provider 類別名以及 template_settings 的 `enabled` 欄位是否存在。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `gamesettings.gametype_settings` | Read (SELECT) | 取得 GameType 維度設定 |
| DB (Cassandra) | `gamesettings.league_settings` | Read (SELECT) | 取得聯賽維度設定（僅啟用） |
| DB (Cassandra) | `gamesettings.template_settings` | Read (SELECT) | 取得模板維度設定 |
| DB (Cassandra) | `gamesettings.game_settings` | Read (SELECT) | 取得單場維度設定（僅啟用） |
| Cache (Redis) | 無 | - | 本查詢未使用 Redis 快取 |
| Queue (Kafka) | 無 | - | 本查詢未涉及佇列操作 |

---

## 6. 重要規則

- **權限限制**：必須通過 ECFramework 驗證，且操作者須有對應商家權限（由驗證框架確保）。
- **公司隔離**：所有查詢均以 `businessCode` 為 `company` 條件，**不可跨公司查詢**。
- **啟用過濾**：
  - `league_settings`、`template_settings`（若存在）、`game_settings` 必須過濾 `enabled = 1`；`gametype_settings` 無 `enabled` 欄位，故不過濾。
  - 需求文件未強制查詢停用設定，後台如需顯示停用設定需另開 API 或加入參數。
- **不可回傳欄位**：
  - 任何設定表中的 `password`、`authtoken` 等敏感欄位不出現於回應（本場景設定表無此類欄位，但仍須注意）。
  - `settings` 欄位需為合法 JSON 字串，不可未序列化直接回傳 Cassandra 原始 binary。
- **欄位不可修改**：本查詢為唯讀，僅供查詢。
- **TTL**：無。
- **Transaction**：非必要，各表查詢獨立執行。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| `businessCode` 不存在（對應 `company` 不存在於設定表） | 回傳空結果或 404（視業務規則，需人工確認） |
| 操作者未通過驗證或無權限 | HTTP 401 或 403 |
| Cassandra 連線超時 | HTTP 500，後端記錄錯誤日誌 |
| `settings` 欄位內容非合法 JSON | 可能導致回應序列化錯誤，應由 Provider 層在讀取後驗證並修正（或記錄異常） |
| 查詢 `template_settings` 時未知 `enabled` 欄位導致錯誤 | 若欄位不存在，架構師需修復 Schema 或調整查詢條件 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| APM001 | API Test | 使用有效 `businessCode` 且透過驗證 | 200，回傳含 GamType/League/Template/Game 四個維度的完整結構 |
| APM002 | Permission Test | 未帶 Token 或 Token 過期 | 401 |
| APM003 | Flow Test | 指定一個僅有 GameType 設定而無 League 設定的商家 | 回傳的 League 區塊為空陣列或無該鍵 |
| APM004 | Integration Test | 查詢後比對遊戲設定中的 `enabled=0` 是否被排除 | 回應中不出現任何 `enabled=0` 的單場設定 |
| APM005 | DB Test | 直接查詢 Cassandra 檢查 `league_settings` 過濾條件 | 僅查詢 `enabled=1` 記錄 |

---

## 9. 高風險區域

- **跨公司資料洩漏**：若 Service 層未正確使用 `businessCode` 作為 `company` 過濾，會導致回傳其他公司設定。
- **`template_settings` 結構未知**：Schema 文件中未完整揭露此表，若存在 `enabled` 欄位但未過濾，可能回傳停用模板。
- **JSON 解析風險**：`settings` 欄位為歷程遺留格式，若解析失敗可能導致整個 API 崩潰，建議增加 try-catch 並記錄。
- **無快取**：每次請求直接查詢 Cassandra，若後台頻繁呼叫可能增加 DB 負載，未來可考慮導入 Redis 快取。

---

## 10. 常見錯誤

- ❌ 直接 `SELECT * FROM game_settings` 未加 `enabled = 1`，導致前台看到停用設定。
- ❌ 將 `businessCode` 當作 MySQL `businesses` 表的查詢條件，但未正確對應到 Cassandra 的 `company`。
- ❌ 未排除敏感欄位（如無意中回傳 `updater` 帳號，雖非高敏感但仍需注意）。
- ❌ 在無 `template_settings` 完整 Schema 時，AI 或新人可能直接寫死查詢所有行，忽略 `enabled` 過濾。
- ❌ 未處理 Cassandra 無資料時的邊界（如 `SELECT` 回傳空結果集），導致回應格式與預期不符。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | `README.md - ConfigController：GET /api/v1/playmodeconfigs/all/{businessCode}` |
| DB 表格 | `gamesettings.gametype_settings`、`gamesettings.league_settings`、`gamesettings.template_settings`、`gamesettings.game_settings` (來自 `README` 及 `db/*.json`) |
| 啟用過濾規則 | `gamesettings-detail.md`：「取得遊戲設定…需確保 company 為該業務所屬公司」；`pricecenter-detail.md` 提及 `enabled` 限制，間接證明其他設定表亦遵循 |
| 權限驗證 | `README.md` 對應路由標示「需要驗證 ✅」 |
| 無 Redis 操作 | `gamesettings-detail.md`：「本服務未直接使用 Redis（所有查詢均直接存取 Cassandra）」 |

> **需人工確認**：
> - `template_settings` 的 `enabled` 欄位是否存在及其過濾規則；
> - 回應結構是否應包含停用設定（或僅回傳啟用）；
> - Service 層的實際方法簽名與 DTO 結構。