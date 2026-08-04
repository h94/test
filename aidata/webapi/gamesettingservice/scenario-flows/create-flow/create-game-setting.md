# 建立單場遊戲設定

## 1. 場景目的
後台管理員為指定遊戲類型與賽事（gid）建立一筆單場遊戲設定，內容包含遊戲日期、玩法參數等，供前台下注時讀取對應玩法配置。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/game/{gameType}/{gid}` | 建立單場遊戲設定 |

---

## 3. 流程總覽

1. 接收已驗證的 HTTP POST 請求，路徑參數包含 `gameType`、`gid`，請求體（JSON）包含 `game`、`gdate`、`settings` 等欄位。
2. 驗證 `settings` 欄位是否為合法 JSON 字串，若非合法 JSON 則拒絕請求。
3. 組合 `game_settings` 資料列：設定 `enabled = 1`（預設啟用）、`updater` 自動擷取自當前操作者帳號、`updatetime` 設為當前 Unix timestamp。
4. 將資料寫入 Cassandra keyspace `gamesettings` 的 `game_settings` 表。
5. 回傳成功（200）或失敗狀態。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `GameSettingServiceController`（推測） | 接收請求、呼叫 Service |
| 2 | Service | `IGameService.CreateGameSetting` | 驗證 settings JSON、組裝 entity |
| 3 | Provider | `GameSettingProvider`（推測） | 執行 Cassandra `INSERT` |
| 4 | - | - | 回傳結果給 Controller |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB（Cassandra） | `gamesettings.game_settings` | Write（INSERT） | 新增一筆遊戲設定 |
| Cache（Redis） | 無直接操作 | - | 需人工確認：後續是否需通知 syncservice 清除 `gamesettings:game:{id}` 快取 |
| Queue（Kafka） | 未使用 | - | - |

---

## 6. 重要規則

- **權限**：API 需要驗證（✅），僅限具有管理權限的帳號（如 `role = Admin`）呼叫。
- **settings 欄位**：必須為合法 JSON 字串，寫入前需通過 `JSON.parse()` 等校驗，禁止寫入非法字串或非序列化物件。
- **id 主鍵**：寫入後不可更新，建立時必須確保唯一性（可能由 `gameType`、`gid`、`gdate` 組合而成，具體生成規則需人工確認）。
- **enabled**：預設值為 `1`（啟用），不可由客戶端傳入。
- **updater**：由後端自動填入當前操作者帳號，客戶端傳入值會被忽略。
- **不可回傳欄位**：`settings` 內容本身可回傳，但下游服務應妥善解析，避免直接暴露原始 JSON 中的敏感內部設定。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `settings` 不是合法 JSON 字串 | HTTP 400，明確告知設定格式錯誤 |
| 缺少必要欄位（如 `gdate`、`game`） | HTTP 400，說明缺少的欄位 |
| 請求未攜帶有效驗證 token | HTTP 401／403 |
| 嘗試建立已存在的 `id`（主鍵衝突） | Cassandra 拋出寫入衝突錯誤，HTTP 500 或 409（視實作） |
| Cassandra 寫入逾時或失敗 | HTTP 500，記錄錯誤日誌 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T01 | API Test | 使用合法管理員 token 傳入完整且正確的 JSON settings | 200，資料正確寫入 `game_settings` |
| T02 | API Test | settings 為 `"invalid json"` | 400，錯誤訊息包含「settings 非合法 JSON」 |
| T03 | API Test | 缺少 `gdate` 欄位 | 400，錯誤訊息指明缺少欄位 |
| T04 | Permission Test | 使用無效 token 或檢視者角色 token | 401／403 |
| T05 | Flow Test | 建立後立即以 GET `/api/v1/game/{gameType}/{gid}` 查詢 | 回傳剛建立的資料，`updater` 為操作者，`enabled=1` |
| T06 | Integration Test | 嘗試重複建立相同 id | 第二次返回錯誤（409 或 500） |

---

## 9. 高風險區域

- **`game_settings` 表是前台下注玩法的核心依據**：寫入錯誤的 `settings` JSON 結構可能導致前端無法顯示或下注異常，需嚴格驗證 JSON schema。
- **id 唯一性**：若 id 生成規則不當，可能導致無意覆蓋既有設定（Cassandra INSERT 會拒絕重複主鍵，但若使用 UPDATE 則會覆蓋，需確保使用 INSERT 語義）。
- **快取一致性**：本服務不管理 Redis，但 `syncservice` 維護 `gamesettings:game:{id}` 快取，建立後若未主動失效，前臺可能讀取不到新設定；需確認是否有機制（如監聽 CDC）或由呼叫方手動通知清除。
- **操作日誌**：若未記錄建立動作至 `action_logs`，可能違反稽核要求；需人工確認是否需在此流程中寫入日誌。

---

## 10. 常見錯誤

- ❌ 呼叫方直接傳入未序列化的物件作為 `settings`（應使用 `JSON.stringify()`）。
- ❌ 管理後台表單允許輸入 `updater` 欄位，導致覆蓋自動填入值（後端應忽略）。
- ❌ 未對 `settings` 進行 JSON 校驗，允許 `"undefined"` 或 `"null"` 等字串寫入。
- ❌ 誤以為 `id` 可由服務端自動生成而不在請求中提供，導致寫入時缺少主鍵（需確認介面合約是否要求客戶端提供 id）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/v1/game/{gameType}/{gid}` — README GameSettingServiceController 路由 |
| DB | `gamesettings.game_settings` — Cassandra schema（`id`, `game`, `gdate`, `settings`, `enabled`, `updater`…） |
| Code | `IGameService.CreateGameSetting` — Phase1 語義解析 |
| Rule | settings 須為合法 JSON — `gamesettings-detail.md` 寫入限制 |
| Rule | updater 自動填入 — db-usage 文件 |
| Rule | 權限需要驗證 — README API 需驗證標記 |

## 12. 需人工確認

- `id` 欄位的生成規則（由客戶端提供？組合生成？）。
- 是否需在建立後觸發 `syncservice` 的 Redis 快取清除。
- 是否需要同步寫入操作日誌（`action_logs`／`logs` 表）。