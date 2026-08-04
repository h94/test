# gamesettingsite — DB 操作邊界

> 產出時間：2025-04-13 16:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

<!--
【產出規則 — 完成後刪除本段與所有 HTML 註解】
✅ 只寫：欄位誰能改、WHERE 業務理由、敏感欄位、Redis Key/TTL、服務邊界、易錯點
❌ 不要寫：職責描述、技術棧、完整 API 表、Table 用途表、註冊/登入流程步驟（README 已有）
📁 結構：每個相關 DB 一個「## {dbName}」章節；增量更新時只改本次觸發的 dbName 章節，其餘保留
🔗 Schema 連結 db/{dbname}.json；語意總覽連結 db/{dbname}-detail.md（正式路徑，勿連 _temps）
-->

---

## gamesettings

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| gamesettings Cassandra | owner / writer / reader | Schema：[db/gamesettings.json](../../db/gamesettings.json) · 語意：[db/gamesettings-detail.md](../../db/gamesettings-detail.md) |

### 寫入限制

- **business_accounts.password**：密碼必須經雜湊（hash）後寫入，禁止儲存明文；任何外部 API 不可直接回傳此欄位。
- **business_accounts.businesscode + account**：複合主鍵，寫入後不可更改；新增僅能用 `INSERT … IF NOT EXISTS`，不可用 `UPDATE`。
- **businesses.businesscode**：主鍵，新增後不可修改。
- **businesses.authtoken**：認證令牌應由內部認證機制（如金鑰服務）產生並寫入，不允許外部請求直接指定。
- **businesses.inplaycount**：該欄位為商務號允許的走地賽事數量上限（配置值），僅可由管理後台或具權限的服務寫入；不應由一般使用者或內部計數邏輯自動更新。
- **businesses 的訂閱設定欄位（subgametypes、subinprogresssites、subpregamesites、extraplaymodes）**：僅可由管理 API 寫入，寫入前須驗證值為合法 JSON 結構（如 subinprogresssites 的 value 應為有效的 JSON 站台陣列字串）。
- **game_settings.id**：主鍵，寫入後不可變更。
- **gametype_settings.company + gametype**：複合主鍵，不可更新。
- **league_logs.company + gametype**：複合主鍵，不可更新。
- **所有表的 settings 欄位（game_settings.settings、gametype_settings.settings）**：必須為合法 JSON 字串，寫入前應由服務端驗證結構完整性。
- **所有表的 updater 欄位**：應由服務端自動填入目前登入操作者帳號（若存在），不可由請求端自行指定。
- **business_accounts.role**：角色（admin/operator）不可隨意變更，僅管理員 API 可修改。

### 讀取規則

- **登入驗證**：查詢 `business_accounts` 時必須以 `businesscode` + `account` 為完整條件（Cassandra 需全部主鍵），不可省略 `businesscode` 做全範圍掃描。
- **查詢 `businesses`**：僅支援以 `businesscode`（主鍵）精確查詢，不支援無條件掃描。
- **訂閱有效性檢查**：讀取 `businesses` 後若需判斷商務號是否有效，應額外比對 `subenddate >= 當前日期`；過期商務號不應繼續提供服務。
- **查詢 `game_settings`**：至少須帶入 `company`（分區鍵），必要時加上 `id`、`game` + `gametype` + `gdate` 等查詢條件；不支援無 `company` 的掃描。
- **查詢 `gametype_settings`**：必須帶入 `company` + `gametype`（完整主鍵）。
- **查詢 `league_logs`**：必須帶入 `company` + `gametype`（完整主鍵）。

### 不可回傳欄位

- **business_accounts.password**：任何 GET 路由（含管理後台）都不可回傳密碼欄位。
- **businesses.authtoken**：認證令牌視為內部機密，對外查詢（特別是前端介面）不得暴露。
- **businesses 中的站台設定（subinprogresssites, subpregamesites, extraplaymodes）**：可能包含協力廠商站台域名或內部配置，對外公開前須確認授權，一般公開 API 不應直接暴露。
- **game_settings.settings / gametype_settings.settings**：視業務需求決定是否回傳；若回傳，須確認無機密配置（如站點私鑰、內部 API 位址）外洩。

---

## news

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| news Cassandra | primary writer / reader | Schema：[db/news.json](../../db/news.json) · 語意：[db/news-detail.md](../../db/news-detail.md) |

### 寫入限制

- **aifunshits.funsname**：主鍵，僅初始化或管理 API 可寫入；不允許更新後變更，僅可用 `INSERT … IF NOT EXISTS` 寫入。
- **ainews.\{anwser, reanwser\}**：僅 LLM 回調服務可寫入；不可由外部 API 直接修改。
- **ainews.status**：狀態值（0：待處理，1：已回應，2：已修正），僅可遞增不得回退；`status=1` 後不可再回寫 `reanwser`。
- **ainews.used**：標記是否已被使用（1 已使用），僅可由使用方（如展示服務）透過 `UPDATE … SET used=1` 遞增，不應重設為 0。
- **ainews.llmsettings**：包含 LLM 溫度、模型等參數，僅由內部 AI 管理介面寫入，不對外開放。
- **aireports.bets / results / others**：`map<text, text>` 中鍵值對結構由業務協定約束，不可隨意增減未知鍵。

### 讀取規則

- **ainews 系列表查詢**：必須指定 `gdate`（分區鍵） + 至少 `gtype` 或 `lid` 之一，否則會觸發全表掃描（Cassandra 禁止且實務無意義）。
- **前台展示新聞**：只讀 `status=1` 的記錄（已回應且無待修正），`status=0`（待處理）與 `status=2`（修正中）不對外顯示。
- **AI 重新回答**：僅讀 `used=0` 且 `status=1` 或 `status=2` 的記錄，避免重複使用同一筆。
- **aireports 查詢**：須以 `gdate` + `gtype` + `lid` 為條件，用於產生賽前預測報告，不支援全範圍掃描。

### 不可回傳欄位

- **anwser / reanwser**：包含 AI 內部產生的初版與修正版回答，對外只應回傳最終校稿版本（由上游服務決定），不應直接暴露原始 AI 回覆。
- **llmsettings**：LLM 參數（溫度、max_tokens 等）視為內部配置，不對外提供 GET 回傳。
- **bets / results（aireports）**：內部預測邏輯與投注映射，不對外暴露詳細內容。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Games PostgreSQL（aimerge schema） | owner / writer / reader | Schema：[db/games.json](../../db/games.json) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- **aimerge_runtime_config**
  - `version_id`：UUID，由系統自動生成，不可由外部指定。
  - `params`：JSONB，必須符合約定的結構（如包含合併權重、門檻值等），寫入前服務端應驗證。
  - `is_active`：預設 `false`，僅可在配置正式發布後設為 `true`；每個 `scope` 同一時間應只有一個啟用中的版本（由應用層控制）。
  - `scope`、`effective_from`：可由管理後台寫入，`effective_from` 不得晚於當前時間（必須是過去或現在）。
  - `change_reason`：必填，記錄變更原因。
  - `updated_by`、`updated_at`：由系統自動填入操作者與時間，不可由前端指定。

- **aimerge_team_aliases**
  - `game_type`、`source_id`、`alias_text`、`language`：組合後應唯一（應用層保證）。
  - `canonical_team_id`：必須參照已存在的標準球隊 ID，不可隨意捏造。
  - `confidence`：介於 0~1，由系統計算或人工審核後填入。
  - 此表僅供管理或數據對齊服務寫入，不應由一般 API 直接操作。

- **aimerge_label_overrides**
  - `override_label`、`excluded_from_training`：由審查人員透過專用審核介面設定。
  - `reason`：人工覆寫時必填原因。
  - `reviewed_by`、`reviewed_at`：由系統自動帶入當前審查者與時間。
  - 此表僅對指定審查角色開放寫入，不可交由自動化流程隨意修改。

- **aimerge_match_predictions**
  - `prediction_id`：由預測服務生成，外部不可修改。
  - `status`：狀態值（如 `pending`、`auto_confirmed`、`confirmed`、`rejected`）只能由特定狀態流轉，不允許由外部任意設置。
  - `reviewed_by`、`reviewed_at`、`inferred_via`：僅審核或內部邏輯可寫入。
  - 一般 API 對此表僅具讀取權限。

- **aimerge_source_mapping**
  - `confirmed_at`、`confirmed_by`：僅在人工確認映射後由系統寫入。
  - `prediction_id`：關聯的預測 ID，必須對應存在的預測紀錄。
  - 寫入此表須有對應的管理權限。

- **aimerge_backtest_runs、aimerge_daily_reports、aimerge_historical_runs**
  - 這類統計/報告表僅由排程任務或內部服務寫入，對外一律為唯讀；不允許任何外部請求執行 INSERT/UPDATE/DELETE。

### 讀取規則

- **通用查詢**：所有查詢必須帶入 `game_type` 作為主要過濾條件，避免跨遊戲類型全表掃描。
- **aimerge_match_predictions**：查詢時必須提供 `gdate` 範圍（分區欄位），並可選 `source_b`、`status` 等精確條件。
- **aimerge_label_overrides**：通常與 `prediction_id` 關聯查詢；若無特定預測 ID，也必須帶 `gdate` + `game_type`。
- **aimerge_runtime_config**：查詢啟用中的配置時須過濾 `is_active = true` 並可能依 `effective_from` 排序取最新一筆。
- **aimerge_backtest_runs、aimerge_daily_reports**：依 `game_type` + `report_date` / `backtest_date` 查詢，需注意時間範圍。
- **aimerge_team_aliases**：查詢別名建議同時提供 `source_id` 與 `language`，避免大量回傳。
- **aimerge_source_mapping**：主要透過 `game_type` + `gdate` 以及 `game_a_sitegid` 進行關聯查詢。

### 不可回傳欄位

- **aimerge_runtime_config.params**：內部參數細節，部分鍵可能包含排程認證或私密設定，對外公開時需過濾。
- **aimerge_label_overrides.reason**：可能包含審查者主觀意見，僅在審核介面中顯示，不對一般使用者暴露。
- **aimerge_match_predictions.score_detail**：詳細評分因子屬於內部演算邏輯，前台通常不需要，可選擇性回傳摘要分數。

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| pricecenter Cassandra | owner / writer / reader | Schema：[db/pricecenter.json](../../db/pricecenter.json) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **accounts_*\ 系列表的 `account`（主鍵）**：僅管理 API 可初始寫入（`INSERT … IF NOT EXISTS`），寫入後不可變更；禁止對主鍵執行 `UPDATE`。
- **`password`**：必須經雜湊（如 bcrypt）後寫入，禁止儲存明文；任何外部 API 不得接收或回傳此欄位。
- **`handler`**：`map<text, text>` 型態，內含第三方站台 API 端點、Token 等機密配置；僅可由具管理權限的內部服務或後台介面寫入，寫入前須驗證鍵值格式合法性。
- **`enabled`**：帳號啟用狀態（0=停用，1=啟用），僅管理員或有權限的內部服務可變更，禁止由一般請求直接控制。
- **`closetime`**：帳號關閉／失效時間，僅管理操作或系統內部機制可設置，不應由外部常規 API 寫入。
- **`username` / `phone`**：須經合法介面寫入，並進行基本格式驗證（長度、字元類型）。
- **`actionlog` 整表**：僅內部受信任服務可寫入（如操作觸發時由服務端自動記錄），嚴禁對外暴露寫入端點。
- **`actionlog.detail`**：寫入時必須為合法 JSON 字串，內容應如實反映操作變更；不允許任意構造。
- **`actionlog.date`, `addtime`, `user`, `gametype`**：由服務端從操作語境自動產生或提取，**不允許調用方指定**，防止日誌偽造。

### 讀取規則

- **查詢 `accounts_*\` 表**：必須提供完整 `account` 主鍵（Cassandra 強制）；不支援無主鍵的全表掃描。若需按 `enabled` 過濾，應在應用層處理（例如僅回傳啟用帳號）。
- **查詢 `actionlog`**：必須提供 `date` 分區鍵；需跨日時應逐分區查詢，**嚴禁全表掃描**。可搭配 `addtime`、`user`、`gametype` 進行範圍或精確過濾。
- **稽核日誌讀取**：`actionlog` 僅限內部審計或監控服務存取，不應對外（尤其前端）直接暴露查詢 API。
- **商務帳號過濾**：讀取帳號資訊時，應至少過濾 `enabled = 1` 的帳號，避免對已停用帳號進行後續操作。

### 不可回傳欄位

- **`password`**：任何 GET 介面（包含管理後台）均**不得回傳**密碼欄位。
- **`handler`**：含有第三方站台 API 密鑰、Token 等機密，對外及對前端皆不可暴露，僅供服務內部使用。
- **`actionlog.detail`**：可能包含操作變更前後的敏感數據，對外查詢時應脫敏處理或直接限制存取。

---

## sport

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport MySQL | owner / writer / reader | Schema：[db/sport.json](../../db/sport.json) · 語意：[db/sport-detail.md](../../db/sport-detail.md) |

### 寫入限制

- **BK_SitePlayers**  
  - `Site`, `SiteID`, `Year`：複合主鍵，寫入後不可變更。新增／更新時應使用 `INSERT … ON DUPLICATE KEY UPDATE` 機制（主鍵衝突時僅更新 `Record` 及 `LastUpdateTime`），嚴禁直接 `UPDATE` 主鍵欄位。  
  - `Record`：必須為合法 JSON，寫入前服務端應驗證結構（包含得分、籃板、助攻等必要鍵），不可寫入任意字串。  
  - `LastUpdateTime`：Unix 時間戳（bigint），**必須由系統自動填入當前時間**，不可由外部請求指定；若 `Record` 實際未變更，不應更新此欄位以降低寫入放大。

- **ChatRoomHistories_Backup**  
  - 歷史聊天備份，**僅支援 INSERT 新增，禁止 UPDATE 或 DELETE**。  
  - `GID`, `Account`, `ID`：三欄複合主鍵，組合後必須唯一；新增前應透過應用層檢查或依賴唯一索引防止重複。  
  - `AddTime`：毫秒級時間戳，由系統自動生成，不可由外部指定。  
  - `Message`：內容寫入前須經過 XSS／注入過濾並限制長度（如 ≤ 2000 字元）。  
  - `LikeAccount`：點讚帳號清單，**僅可由內部服務更新**（如透過受信任的點讚 API），前端不可直接設定此欄位。  
  - `ResponseID`：若為回覆訊息，必須引用已存在的 `ID`，服務端應校驗該 `ID` 存在性。

- **Community_Groups**  
  - `ID`：主鍵，新增後不可變更，僅可用 `INSERT`，不得用 `UPDATE` 變更 ID。  
  - `Name`：多語言 JSON 字串（至少包含 `zh-TW`），寫入前驗證 JSON 格式及必要語言鍵。  
  - `Enabled`：啟用旗標（1 啟用，0 停用），僅管理後台或具權限的 API 可變更，禁止一般使用者控制。  
  - `Owner`：群主帳號，設定後僅管理員可變更，一般操作不可修改。  
  - `UpdateTime`：系統自動填入當前時間戳（bigint 秒級），外部不可指定。

- **GameUsers_Wallet**  
  - **本服務僅具讀取權限，不執行任何寫入操作（INSERT/UPDATE/DELETE）**。餘額變更由專責的 wallet-service 透過交易機制處理。  
  - `AuthKey`：主鍵，不可變更。

- **GameUsers_Wallet_Transactions**  
  - **本服務僅具讀取權限**，交易記錄由交易服務寫入。  
  - `TID`：自動遞增主鍵，不可由外部指定。  
  - `AddTime`／`TDate`：由交易服務依業務邏輯自動填寫。  
  - `TypeInfo`：必須為合法 JSON 字串，記錄完整交易上下文（如遊戲 ID、帳號等），不可短少必要欄位。

- **Notification_Messages**  
  - `TID`, `ID`：複合主鍵，寫入後不可變更；新增訊息須保證組合唯一。  
  - `Title`, `TW_Content`, `EN_Content` 等多語言欄位：由內容管理服務寫入，寫入前檢查字元長度限制，且至少 `TW_Content` 必填（繁體中文為主要語言）。  
  - `Enabled`：僅可由管理操作啟用／停用，不可經由未授權 API 切換。  
  - `UpdateTime`：系統自動更新時間戳（bigint 秒級），外部不可指定。

### 讀取規則

- **BK_SitePlayers**  
  - 查詢時必須指定 `Site` 條件（主要過濾欄位），缺少時可能導致全表掃描，應由應用層強制要求。可選用 `Year`, `League`, `Name`, `Team` 等進行二級過濾，但建議搭配適當索引。  
  - 對外展示時僅查詢有效紀錄（例如 `Record` 非空或依業務狀態過濾），避免回傳無效球員數據。

- **ChatRoomHistories_Backup**  
  - 查詢歷史訊息必須提供 `GID`，**嚴禁跨聊天室全表掃描**。  
  - 應搭配 `AddTime` 範圍限制（如 `AddTime >= ? AND AddTime <= ?`）以控制結果集大小，建議依 `AddTime` 倒序分頁。  
  - 取得訊息時，若需過濾敏感訊息，應在應用層處理（例如管理員可查看全部，一般用戶僅看自己的）。

- **Community_Groups**  
  - 查詢群組列表時，應強制過濾 `Enabled = 1`，避免回傳停用群組。  
  - 排序可使用 `Seq` 欄位；若有其他排序需求，需確保不影響效能。

- **GameUsers_Wallet**  
  - 必須以完整 `AuthKey` 為查詢條件，不支援模糊或範圍查詢。

- **GameUsers_Wallet_Transactions**  
  - 查詢時必須提供 `AuthKey` 以及合理的時間範圍（`TDate` 或 `AddTime` 區間），禁止全表掃描。實務上建議以 `TDate` 作為分區條件提升效能。  
  - 對外提供交易明細時，可能需要依 `Type` 過濾或限制回傳筆數。

- **Notification_Messages**  
  - 對用戶推播或查詢通知時，必須過濾 `Enabled = 1`。  
  - 可根據 `TID` 精確查詢特定模板的有效訊息；多語言欄位按客戶端偏好語言擇一回傳。

### 不可回傳欄位

- **GameUsers_Wallet.AuthKey**：用於內部關聯，外部 API 不得暴露用戶錢包金鑰。
- **GameUsers_Wallet_Transactions.TypeInfo**：可能包含交易對手、內部標記等敏感資訊，對外回傳前應過濾或脫敏處理。
- **ChatRoomHistories_Backup.Account**：用戶帳號屬於個資，公眾聊天記錄或非管理情境下不應回傳；僅在用戶本人授權或管理審計時可揭露。
- **ChatRoomHistories_Backup.LikeAccount**：點讚帳號列表，非相關用戶不應取得。
- **Community_Groups.Owner**：群主帳號，對外公開清單時建議匿名或直接隱藏。

---

## Redis

本服務目前**未使用 Redis**。若未來引入快取，應遵從以下規範：

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| — | — | — | 待擴充 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| AI 回答生成 | gamesetting-llm | 僅負責儲存 `anwser/reanwser`，實際生成由 LLM 服務處理 |
| 賽事資料維護 | gamesetting-match | `gdate / gtype / lid / gid` 等比賽主鍵由賽事服務維護 |
| 投注盤口資料 | gamesetting-betting | `bets`、盤口相關欄位僅作關聯，不負責更新盤口實時數據 |
| 預測模型訓練與自動合併 | games-aimerge-internal | 預測分數、狀態推斷等由內部服務計算，本服務僅提供配置與人工審核入口 |

---

## 常見錯誤

- ❌ 查詢 `ainews` 時未帶 `gdate` → ✅ 必須強制帶入 `gdate`，否則 Cassandra 會拒絕（或引發高延遲全表掃描）。
- ❌ 將 `status` 直接設為 `2` 跳過 `1` → ✅ 狀態機必須依序：0 → 1 → 2（若需修正）。
- ❌ 外部服務直接寫入 `llmsettings` → ✅ `llmsettings` 僅供管理後台寫入，其他服務應呼叫對應 API。
- ❌ 更新 `aifunshits` 時使用 `UPDATE` 而非 `INSERT … IF NOT EXISTS` → ✅ 主鍵不允許重複，應使用條件寫入。
- ❌ 查詢 `bk_siteplayers` 時未帶 `Site` → ✅ `Site` 為主要過濾欄位，缺少時會觸發全表掃描，應由應用層強制帶入。
- ❌ 直接由外部請求設定 `businesses.inplaycount` 或忽略其配置性質 → ✅ `inplaycount` 是商務號的上限配置，僅管理後台可寫入，不應由內部服務自動更新為當前計數。
- ❌ 未檢查 `subenddate` 即提供服務 → ✅ 必須過濾已過期商務號，避免向無效訂閱提供資料。
- ❌ 儲存明文密碼或 handler 中的 Token 時未加密 → ✅ password 必須雜湊處理，handler 內的 Token／密鑰應由密鑰管理服務保護，僅在後端解密使用。
- ❌ 查詢 accounts_* 時未提供完整 `account` 主鍵 → ✅ Cassandra 必須提供完整主鍵，否則導致全表掃描或查詢失敗。
- ❌ 直接對外暴露 handler 欄位內容 (如 Token) → ✅ handler 僅用於內部服務呼叫第三方 API，任何 GET 回應都應移除該欄位。
- ❌ 允許外部呼叫直接寫入 actionlog → ✅ actionlog 為內部操作記錄，僅由受信任的內部服務寫入，不應暴露寫入端點。
- ❌ 查詢 `actionlog` 時未帶 `date` 分區鍵 → ✅ 必須強制帶入 `date`，禁止跨分區全表掃描。
- ❌ 對 `aimerge_runtime_config` 直接執行 `UPDATE` 而不記錄變更原因 → ✅ 應使用版本控制，每次修改插入新版本並填寫 `change_reason`。
- ❌ 任意指定 `aimerge_label_overrides.prediction_id` 而不檢查是否存在 → ✅ 必須確保關聯的預測記錄存在，否則視為無效操作。