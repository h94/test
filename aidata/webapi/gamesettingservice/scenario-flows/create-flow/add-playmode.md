# 新增玩法模式

## 1. 場景目的
後台運營人員為指定 GameType（如足球、籃球）新增一組系統級玩法模式（PlayMode），例如新增一種投注玩法，並可選擇性更新相關商家設定與快取。此流程確保新增的玩法模式能正確寫入設定儲存層，並間接觸發前台可使用此新模式。

## 2. 入口 API

| Method | Path                               | 說明                         |
|--------|------------------------------------|------------------------------|
| PATCH  | `/api/v1/settings/playmodes/add/{gameType}` | 新增玩法模式，需驗證 Token。 |

## 3. 流程總覽

1. 接收請求，從路徑參數取得 `gameType`，從 body 取得玩法設定。
2. 驗證呼叫者權限（必須為後台管理員角色）。
3. 驗證 `gameType` 是否為系統支援的合法類型。
4. 驗證 request body 結構與必要欄位（name、settings 等），並確認 `settings` 為合法 JSON 字串。
5. 從認證資訊中解析 `company`（公司代碼）。
6. （視業務規則）查詢 `gametype_settings` 確認是否已存在同名玩法，避免重複。
7. 組裝 `gametype_settings` 物件，自動填入 `updater`（當前操作者帳號）與 `updatetime`。
8. 寫入 Cassandra `gamesettings.gametype_settings` 表。
9. （可選）若需連動商家設定，更新 `businesses` 表中相關商家的 `extraplaymodes` 或 `subgametypes`（需人工確認）。
10. （可選）觸發快取更新機制（可能透過 Kafka 訊息或由其他服務監聽後更新 Redis BusinessCache）（需人工確認）。
11. 回傳成功（200 OK），不帶回敏感欄位。

## 4. 程式流程

| 順序 | Layer      | Class / Method（推測）                       | 動作                                                            |
|------|------------|----------------------------------------------|-----------------------------------------------------------------|
| 1    | Controller | `GameSettingServiceController.AddPlayMode`   | 接收 PATCH 請求，提取參數與 body。                                |
| 2    | Validator  | `AddPlayModeRequestValidator`               | 校驗 gameType、必填欄位、JSON 格式。                              |
| 3    | Service    | `IPlayModeService.AddPlayMode`               | 呼叫 Provider 查詢是否已存在，處理商業邏輯，觸發寫入與快取更新。     |
| 4    | Provider   | `GameTypeSettingsProvider` (Cassandra)       | 執行 `INSERT INTO gametype_settings ...`。                       |
| 5    | Service    | `IPlayModeService.AddPlayMode`              | 可選：觸發商家設定更新與快取清除事件。                             |
| 6    | Controller | `GameSettingServiceController`               | 回傳 200 OK（可能包含新建立的模式摘要）。                           |

> ⚠️ 實際類別名稱需人工確認，目前依據常見命名慣例推測。

## 5. DB / Cache / Queue 使用

| 類型          | 資源                                | 操作                 | 用途                                        |
|---------------|-------------------------------------|----------------------|---------------------------------------------|
| DB (Cassandra)| `gamesettings.gametype_settings`    | Write (INSERT/UPSERT)| 寫入新的玩法模式設定（主鍵 company + gametype） |
| DB (Cassandra)| `gamesettings.businesses`           | Read / Update (選擇性) | 同步更新商家的 extraplaymodes 或 subgametypes（需人工確認） |
| Cache (Redis) | `BusinessCache`（由 syncservice 管理） | 間接更新（透過事件）   | README 場景提及更新 Redis，但 detail 文件指出本服務未直接操作 Redis，需確認實現方式 |

## 6. 重要規則

- **權限限制**：需要有效的後台管理員 Token，具備 `遊戲設定` 寫入權限。
- **欄位限制**：
    - `settings` 必須為合法 JSON 字串，不可包含無法序列化的物件。
    - `updater` 應由後端自動填入當前登入者帳號，客戶端不可傳入。
    - `company` 須由後端從認證資訊取得，客戶端不可自行設定。
- **不可暴露資料**：API 回應中不可包含 `password`、`authtoken` 等敏感欄位。
- **Transaction**：對 `gametype_settings` 的寫入可視為單一操作（Cassandra 支援 UPSERT 語意）；若涉及多個表（如 businesses），需考慮最終一致性或補償機制。
- **主鍵不可變**：一旦寫入後，`company` 和 `gametype` 不可修改。
- **狀態**：初次新增時，相關啟用旗標（如 `showstopplaymode`）可能採用預設值。

## 7. 錯誤情境

| 情境                                    | 預期結果                                  |
|-----------------------------------------|-------------------------------------------|
| `gameType` 為空或非系統定義值            | 400 Bad Request，錯誤訊息提示無效遊戲類型      |
| Request body 缺少 `name` 或 `settings`  | 400 Bad Request，驗證失敗                   |
| `settings` 欄位非合法 JSON               | 400 Bad Request，JSON 格式錯誤              |
| Token 過期或權限不足                    | 401 Unauthorized 或 403 Forbidden          |
| 玩法名稱已存在（若禁止重複）            | 409 Conflict，提示模式已存在                 |
| Cassandra 寫入失敗                      | 500 Internal Server Error，記錄錯誤日誌      |
| 後續商家設定或快取更新失敗（非核心）      | 仍回傳 200，但記錄警告，需監控非同步流程       |

## 8. 測試重點

| Test ID | 類型            | 情境                                      | 預期結果                 |
|---------|-----------------|-------------------------------------------|--------------------------|
| T-01    | API Test        | 合法輸入新增玩法模式                        | 200，DB 中出現新記錄       |
| T-02    | Validation Test | 缺少必要欄位                               | 400                      |
| T-03    | Validation Test | settings 為非法 JSON                       | 400                      |
| T-04    | Permission Test | 使用一般使用者或無 token 請求               | 401/403                  |
| T-05    | Integration Test| 確認新增後商家設定或快取是否正確更新（若相關） | 前台下注時可看到新模式     |
| T-06    | Error Test      | 模擬 Cassandra 連線異常                     | 500                      |

## 9. 高風險區域

- **高風險 table**：`gametype_settings`，任何錯誤寫入可能影響所有商家對該 GameType 的玩法顯示。
- **權限控管**：若驗證層未正確攔截無權限請求，可能導致非預期的全局設定變更。
- **跨服務同步**：若新增後需通知 `gamesettingsite` 或更新 `BusinessCache`，而同步機制失效，會導致線上與後台設定不一致。
- **一致性**：若同步更新 `businesses` 表，卻在部分寫入時失敗，可能造成資料不完全。
- **冪等性**：重複呼叫不應該造成同一 GameType 下出現多筆同名記錄，若系統未實作 UPSERT 邏輯，需由應用層檢查。

## 10. 常見錯誤

- **新人易犯錯**：忘記自動寫入 `updater` 與 `updatetime`，造成審計追蹤缺失。
- **AI 易誤解**：可能誤以為操作對象是 `game_settings`（單場設定），正確應是 `gametype_settings`。
- **常見漏檢查**：未校驗 `settings` JSON 結構是否符合規範（如必須含有哪些 key），導致下游服務解析錯誤。
- **流程錯誤**：直接使用客戶端傳入的 `company`，而非從後端 token 中提取，可能被用於跨公司寫入。

## 11. Evidence

| 類型 | 來源                                                                 |
|------|----------------------------------------------------------------------|
| API  | GameSettingServiceController：PATCH `/api/v1/settings/playmodes/add/{gameType}` (README.md) |
| DB   | `gamesettings.gametype_settings` 表格定義 (gamesettings.md)         |
| 場景 | README「常見使用場景」第1項                                          |
| 規則 | gamesettingservice-detail.md：`settings` 須為合法 JSON，`updater` 自動填入 |
| 快取 | README 提及更新 Redis BusinessCache，但 detail 文檔指出本服務未直接操作 Redis，需人工確認實際機制 |

---

**建議新增文件／規則**：  
- 玩法模式 `settings` JSON Schema 規範文檔  
- 確認 Redis 快取更新方式（事件驅動／定時同步）  
- 明確 company 獲取方式（JWT claim 名稱）  
- 若涉及多表更新，應定義補償或最終一致性處理流程