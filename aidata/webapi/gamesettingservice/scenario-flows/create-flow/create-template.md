# 建立玩法模板

## 1. 場景目的
供後台管理員為指定遊戲類型（GameType）建立新的玩法模板，以便後續快速配置聯賽或單場遊戲的玩法模式。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/template/{gameType}` | 建立玩法模板 |

---

## 3. 流程總覽
1. 接收 POST 請求，路徑包含 `{gameType}`（如 FT、BK）。
2. 驗證操作者身分（使用 ECFramework.ECService 統一驗證）。
3. 檢查 `gameType` 是否合法（需人工確認是否存在白名單）。
4. 從請求 Body 讀取模板設定 JSON 與模板名稱。
5. 校驗 `settings` 欄位為合法 JSON 字串。
6. 組合寫入資料：自動填入 `updater`（當前操作者帳號）、`updatetime`（當前時間戳）。
7. 寫入 Cassandra `gamesettings.template_settings` 表。
8. 回傳成功或失敗。

> **需人工確認**：是否寫入操作日誌至 `pricecenter.action_logs` 或 `gamesettings.league_logs` 類型表？  
> **需人工確認**：是否需清除 Redis 快取（如 `gamesettings:template:{id}`）？

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `GameSettingServiceController` | 接收 HTTP 請求，調用 Service |
| 2 | Service | `ITemplateService.CreateTemplate` | 驗證參數、組裝 Template 物件 |
| 3 | Provider / Repository | Cassandra `template_settings` 寫入 | 執行 `INSERT` 至 `gamesettings.template_settings` |
| 4 | Log Provider（若實現） | 寫入操作日誌 | 將操作者、動作、內容寫入審計表 |

> **需人工確認**：具體 Service 方法名稱與依賴注入介面，請查閱源碼。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `gamesettings.template_settings` | Write | 儲存新建的玩法模板 |
| DB | Cassandra `pricecenter.action_logs`（若實作） | Write | 記錄本次建立操作 |
| Redis | `gamesettings:template:{id}` 或類似 pattern | Delete（可選） | 建立後使快取失效，避免後續讀取舊資料 |
| Queue | Kafka（日誌） | Publish（若實作） | 將操作事件送往日誌中心 |

> **需人工確認**：Redis 快取的 key pattern 與 TTL 規則，以及是否有 Queue 發佈行為。

---

## 6. 重要規則
- **權限限制**：僅已驗證並有對應權限的後台管理者可呼叫。
- **欄位限制**：
  - `settings` 必須為合法 JSON 字串，不可包含非序列化物件。
  - `updater` 由後端自動填入當前操作者，不接受客戶端傳入。
  - `template id`（主鍵）應由服務生成，不可由客戶端指定。
- **不可暴露資料**：回傳內容不得包含 `password`、`authtoken` 等敏感欄位。
- **狀態值限制**：`showstopplaymode`、`swap` 等布林值應有預設值（如 `false`）；狀態值不可為 NULL（需人工確認）。
- **不可修改欄位**：主鍵（id）一經建立不可更新。
- **跨服務限制**：本服務為 `gamesettings` 的 owner；其他服務僅讀取，不可直接寫入 `template_settings`。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|-----------|
| `gameType` 不存在或不被支援 | 回傳 400 或 404，提示無效的 GameType |
| `settings` 不是合法 JSON | 回傳 400，提示格式錯誤 |
| 操作者未通過驗證 | 回傳 401 或 403 |
| Cassandra 寫入失敗（逾時、不可用） | 回傳 500，不創建模板 |
| 試圖重複建立相同模板（需人工確認唯一約束） | 回傳 409 衝突 |
| 請求 Body 缺少必填欄位（如 `name`） | 回傳 400 驗證失敗 |
| Redis 快取清除失敗 | 不影響主流程，可記錄警告並繼續 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|-----------|
| TC01 | API Test | 使用合法參數建立模板 | 回傳 200，模板成功建立 |
| TC02 | API Test | 不含驗證 Token 呼叫 | 回傳 401 |
| TC03 | API Test | `settings` 傳入非法 JSON | 回傳 400 |
| TC04 | DB Test | 建立後驗證 `updater` 正確填入 | 模板記錄中的 updater 應為當前使用者 |
| TC05 | Flow Test | 建立後立即查詢列表 | 新模板應出現在 GET `/api/v1/template/{gameType}` 結果中 |
| TC06 | Permission Test | 使用低權限帳號（如僅讀者）呼叫 | 回傳 403 |
| TC07 | Redis Test | 建立後確認相關快取已失效 | 後續讀取應從 DB 獲取最新資料（若快取存在） |

---

## 9. 高風險區域
- **高風險 Table**：`gamesettings.template_settings`，為核心設定表，損壞或空值會影響前台下注玩法顯示。
- **高風險 API**：此 API 為設定入口，若未正確管控可能造成全站遊戲顯示異常。
- **Cache consistency**：若建立後未清除對應的模板快取，前台可能無法立即取得新模板。
- **Idempotency**：無冪等設計，重複呼叫會建立多個模板（除非有唯一約束）。需人工確認是否允許同名模板。
- **Transaction**：Cassandra 寫入為非交易性，應確保所有必要欄位一次寫入。
- **跨服務資料同步**：模板建立後，若有 `syncservice` 同步任務，需確認其能識別新增模板並推送到其他站點。

---

## 10. 常見錯誤
- ❌ `settings` 欄位未驗證 JSON 格式，直接寫入導致後續讀取失敗。
- ❌ 手動傳入 `updater` 欄位覆蓋自動記錄，失去審計準確性。
- ❌ 忘記設定預設啟用狀態（例如 `enabled`），導致模板建立後前台未顯示。
- ❌ 模板名稱重複未處理，導致管理端查詢混淆。
- ❌ 建立後未清除相關快取，造成前台顯示舊資料。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `GameSettingServiceController` - POST `/api/v1/template/{gameType}` |
| DB | Cassandra keyspace `gamesettings` → table `template_settings` |
| DB 規則 | `gamesettings-detail.md` — settings 欄位必須為合法 JSON，updater 自動填入 |
| Service 語意 | `ITemplateService.CreateTemplate`（推測存在） |
| 權限 | 所有 `/api/v1/template/*` 路由標註需要驗證 |
| 快取 | Redis `gamesettings:template:{id}` 可能由 syncservice 管理（需人工確認） |
| 日誌 | 可能寫入 `pricecenter.action_logs`，需確認源碼 |