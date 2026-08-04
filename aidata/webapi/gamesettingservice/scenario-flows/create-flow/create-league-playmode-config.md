# 建立聯賽玩法設定

## 1. 場景目的

為特定聯賽建立一組玩法模式配置（PlayMode Settings），用於控制該聯賽下各玩法（如讓球、大小）的開關與參數。此設定供前台下注時讀取，決定可投注的玩法。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/playmodeconfigs/league` | 建立聯賽玩法設定（需驗證） |

---

## 3. 流程總覽

1. 後台用戶發送 POST 請求，攜帶聯賽 ID、公司代碼、遊戲類型、設定 JSON 等資料。
2. 驗證中間件檢查請求合法性（認證）。
3. Controller 接收請求，調用驗證器校驗 request body。
4. Controller 調用 Service 層建立聯賽設定。
5. Service 層檢查公司、遊戲類型是否合法，建構 entity。
6. Service 層將 data 寫入 Cassandra `league_settings` 表，並自動填入 `updater`（當前操作者帳號）與 `updatetime`。
7. 成功回傳 200。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Middleware | ECFramework Auth | 驗證 Authorization header / token |
| 2 | Controller | ConfigController.PostLeaguePlayModeConfig | 接收請求，調用 Validator |
| 3 | Validator | LeaguePlayModeConfigValidator | 校驗 settings 為合法 JSON 以及其他必填欄位 |
| 4 | Service | ILeagueService.CreateLeagueSetting | 檢查業務邏輯（如 company/gametype 是否存在），組裝 entity |
| 5 | Service | LeagueService 實作 | 寫入 Cassandra `league_settings` |
| 6 | Service | (optional) LogService | 寫入操作日誌（可能至 `pricecenter.action_logs`） |

*註：具體類別名稱需人工確認，推測基準為 README 路由與 Phase0/1 語意表。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | gamesettings.league_settings | INSERT | 儲存聯賽玩法設定 |
| DB (Cassandra) | pricecenter.action_logs | INSERT (推測) | 記錄操作日誌 |
| Queue | 不涉及 Kafka | – | – |
| Redis | 不直接讀寫 | – | 後續前台可能透過 syncservice 快取，但建立操作本身不操作 Redis |

---

## 6. 重要規則

- **權限限制**：僅通過驗證的後台管理者可呼叫。
- **欄位限制**：
  - `settings` 必須為合法 JSON 字串，不可包含非序列化物件。
  - `updater` 自動填入當前操作者帳號，不接受客戶端傳入。
  - `id` 一旦建立，不可更新（主鍵語意）。
- **不可暴露資料**：`settings` 內容若包含敏感資訊，需由前台服務解析後過濾。
- **Transaction 規則**：Cassandra 單一 partition 寫入，無跨表事務。
- **Retry 規則**：若寫入失敗，客戶端可重試，但需注意 idempotency（透過 id 唯一性避免重複建立）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未登入或 token 過期 | 回傳 401 Unauthorized |
| settings 欄位非合法 JSON | 回傳 400 Bad Request，提示 JSON 格式錯誤 |
| 必要欄位缺失（如 company, gametype） | 回傳 400 Bad Request |
| 嘗試建立已存在的 id | 回傳 409 Conflict 或覆蓋行為（需人工確認） |
| Cassandra 寫入失敗 | 回傳 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| TC-LC-01 | API Test | 使用合法資料建立聯賽設定 | 200，資料寫入 league_settings，可透過 GET 查詢 |
| TC-LC-02 | Validation | settings 提供非法 JSON 字串 | 400 |
| TC-LC-03 | Permission | 無 token 請求 | 401 |
| TC-LC-04 | Flow Test | 建立後取得該設定，檢查 updater | updater 為當前操作者，非由 request body 傳入 |
| TC-LC-05 | Integration | 確認寫入後讀取聯賽玩法設定 | 資料一致 |

---

## 9. 高風險區域

- **高風險 table**：`league_settings`，若 `settings` 內容格式錯誤，可能導致前台解析崩潰。
- **高風險 API**：POST 時未妥善驗證 JSON，可能儲存無效設定，影響下注功能。
- **跨服務資料同步**：建立後需確保 `syncservice` 能將此設定同步至前台快取（Redis），否則前台無法立刻生效。本服務不直接操作 Redis，需通知或由 syncservice 輪詢。
- **Idempotency**：若前端因網路問題重送相同 id 的建立請求，可能導致錯誤或重複。建議後端處理 idempotency key。
- **操作日誌**：所有變更應記錄，以利審計。

---

## 10. 常見錯誤

- ❌ 建立時 `settings` 傳入未序列化物件而非 JSON 字串。
- ❌ 前端將 `updater` 欄位傳入 request body，違反不可由客戶端傳入規則。
- ❌ 忘記設定 `company` 或 `gametype` 導致查詢隔離失效。
- ❌ 建立後未主動清除相關快取，導致前台讀到舊配置（若前台有快取）。
- ❌ 直接使用明文或包含機敏資料於 `settings` 中。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | README ConfigController: `POST /api/v1/playmodeconfigs/league` |
| DB Table | Cassandra `gamesettings.league_settings` |
| Service 方法 | Phase0/1 Semantics: ILeagueService.CreateLeagueSetting |
| 寫入規則 | gamesettings service detail: `settings` 須合法 JSON，`updater` 自動填入 |
| 驗證 | README: 需要驗證 ✅ |