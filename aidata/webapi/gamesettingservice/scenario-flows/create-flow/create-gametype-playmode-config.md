# 建立 GameType 玩法設定

## 1. 場景目的
為指定商家 (businessCode) 的特定遊戲類型 (gameType) 建立一筆玩法模式設定，核心寫入合法 JSON 至 `gametype_settings`，供下游服務（前台、定價）讀取以決定顯示或隱藏玩法。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/playmodeconfigs/gametype` | 建立 GameType 級別玩法設定 |

---

## 3. 流程總覽

1. 接收 HTTP POST 請求，body 包含 `company`、`gametype`、`name`、`settings`（JSON 字串）、`showstopplaymode`、`swap` 等欄位。  
2. 系統驗證請求合法性（權限、必要欄位、JSON 格式）。  
3. 提取當前操作者帳號（來自認證資訊），並填入 `updater`。  
4. 寫入 Cassandra `gametype_settings` 表，`company` + `gametype` 作為複合主鍵。  
5. 回傳成功訊息（或錯誤）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ConfigController.CreateGameTypePlayModeConfig` | 接收 request，參數綁定，呼叫 Service |
| 2 | Service | `IConfigService.CreateGameTypePlayModeConfig` | 執行業務邏輯 |
| 3 | Validator | （內部或 FluentValidation） | 驗證 `settings` 為合法 JSON，必要欄位非空 |
| 4 | Provider / Repository | `GametypeSettingsRepository`（或透過 Cassandra Driver） | 寫入 `gametype_settings`，自動帶入 `updater` 與 `updatetime` |
| 5 | Response | – | 回傳 HTTP 200 或錯誤狀態碼 |

需人工確認：實際 Controller 與 Service 完整名稱（如 `PlayModeConfigController` 或 `ConfigController`）及驗證框架細節。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `gamesettings.gametype_settings` | Write (INSERT) | 儲存該 company+gametype 的玩法設定 |
| DB | Cassandra `gamesettings.logs`（若實作） | Write (INSERT) | 記錄操作日誌（`action=create`） |
| Queue | 可能透過內部事件發布 | Publish | 通知下游（如 pricecenterservice）設定變更，實作視情況而定 |
| Cache | Redis（由其他服務操作） | 無直接操作 | `gamesettingservice` 本身不直接寫入 Redis，但變更後需由 `syncservice` 或快取管理方清除 `gamesettings:company:{company}:gametypes` 等快取鍵 |

---

## 6. 重要規則

- **權限限制**：僅允許已驗證且具有對應商家權限的管理員/操作者呼叫。  
- **欄位限制**：`company`、`gametype`、`settings` 不可為空；`settings` 必須為合法 JSON，否則返還 400 Bad Request。  
- **不可暴露資料**：`updater` 僅記錄操作者，回傳內容應避免洩漏密碼或 token。  
- **不可修改欄位**：`updater` 由後端填入，不接受請求攜帶；`company` + `gametype` 為複合主鍵，建立後不可更新（若相同 key 已存在需改用 PUT）。  
- **隔離規則**：`company` 必須屬於當前業務授權範圍，不可跨公司寫入。  
- **Transaction 規則**：Cassandra 無跨分區事務，確保單一寫入原子性即可。  
- **狀態值限制**：`showstopplaymode` 為 boolean；`swap` 為 boolean，預設值依業務定義。  

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未攜帶有效認證 Token | 返回 401 Unauthorized |
| 權限不足（非該商家操作者） | 返回 403 Forbidden |
| `settings` 不是合法 JSON | 返回 400 Bad Request，訊息標明格式錯誤 |
| 必要欄位缺失（如 `company`） | 返回 400 Bad Request，列出缺失欄位 |
| Cassandra 寫入失敗或超時 | 返回 500 Internal Server Error，並記錄錯誤日誌 |
| 同一 `company` + `gametype` 已存在 | 依設計可能返回 409 Conflict，或由業務層決定直接覆蓋（此 API 為 POST，預期若已存在應使用 PUT 更新） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | API Test | 成功建立，傳入合法 JSON `settings` | 200，DB 出現新紀錄，`updater` 正確 |
| T2 | Validation Test | `settings` 為無效 JSON (缺少引號) | 400，錯誤碼對應 JSON 格式 |
| T3 | Permission Test | 使用無權限帳號呼叫 | 403 |
| T4 | Integration Test | 寫入後檢查 `gametype_settings` 內容 | `settings` 原樣儲存，`updater` 為當前登入帳號 |
| T5 | Flow Test | 建立後前台查詢 `GET /api/v1/playmodeconfigs/gametype/{businessCode}/{gameType}` | 應能回傳新建立的設定 |

---

## 9. 高風險區域

- **高風險 table**：`gametype_settings`，若 `settings` 非法 JSON 或寫入錯誤將直接影響所有下游服務的玩法讀取。  
- **高風險 API**：`POST /api/v1/playmodeconfigs/gametype`，無 idempotency key，重複點擊可能建立重複資料（需確認是否由服務端檢查複合主鍵唯一性）。  
- **跨服務資料同步**：變更後需確保 pricecenterservice / gamesettingsite 的快取被刷新，否則前後台設定不一致。  
- **Cache consistency**：本服務不直接操作 Redis，若未觸發其他服務快取清除，可能導致舊設定持續生效。  

---

## 10. 常見錯誤

- ❌ 在請求 body 中傳入 `updater` 欄位（應由後端填寫）。  
- ❌ 傳入的 `settings` 為 JavaScript 物件而非 JSON 字串。  
- ❌ 誤將 `company` 填成不屬於該商家的代碼（忽略隔離規則）。  
- ❌ 更新設定時誤用 POST 而非 PUT 導致重複建立（若未處理唯一約束）。  

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | `README` ConfigController：`POST /api/v1/playmodeconfigs/gametype` |
| DB Table | `gamesettings.gametype_settings` schema |
| 寫入限制 | `gamesettings-detail.md`：`settings` 須為合法 JSON；`updater` 自動填入 |
| 操作者自動填入 | `gamesettings-detail.md` 常見錯誤：「建立遊戲設定後未記錄 updater」 |
| 權限要求 | README 所有 API 標記 ✅ 需要驗證 |