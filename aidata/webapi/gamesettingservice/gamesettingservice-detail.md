# gamesettingservice — DB 操作邊界

> 產出時間：2025-04-14 16:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| pricecenter (Cassandra) | reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **無**：`gamesettingservice` 僅讀取 `pricecenter` 中的帳戶與操作記錄，不具備任何寫入權限。所有帳戶管理（建立、狀態變更、密碼重設）均由 `userservice` 或其他帳戶服務負責。

### 讀取規則

- **操作記錄關聯查詢**：當 `gamesettingservice` 需要記錄設定變更的操作者資訊時，透過 `account` 欄位關聯至 `accounts_{brand}` 表，並附加 `gametype` 條件進行過濾，以確保取得正確品牌下的帳戶資訊。
- **品牌隔離**：所有對 `accounts_{brand}` 的查詢必須明確指定品牌後綴（如 `AU8`, `Fortuna888`），不可進行跨品牌的全表掃描。
- **帳戶狀態校驗**：讀取帳戶資訊時，僅查詢 `enabled = 1` 且 `closetime` 為空的記錄，確保只針對有效帳號進行操作。

### 不可回傳欄位

- **password**：帳戶密碼（通常已雜湊）在任何對外回應、日誌記錄或快取中皆不得包含。
- **handler**：內含平台特定的處理器配置，屬於內部路由資訊，不可回傳至客戶端或未經授權的服務。

---

## gamesettings

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| gamesettings (Cassandra) | owner | Schema：[db/gamesettings.md](../../db/gamesettings.md) · 語意：[db/gamesettings-detail.md](../../db/gamesettings-detail.md) |

### 寫入限制

- **businesscode（businesses）**：建立後不可更新（主鍵）。
- **authtoken（businesses）**：僅 `CreateBusiness` / `UpdateBusiness` 可寫入；應以單向雜湊（如 SHA256）儲存，禁止明文。
- **email（businesses）**：僅 `CreateBusiness` 可設定；建立後不可更新（關聯預設管理員帳號）。
- **extraplaymodes（businesses）**：僅 `UpdateBusinessExtraPlayModes` 可寫入；值須為合法 map<text, text>，更新時應確認合併邏輯。
- **inplaycount（businesses）**：僅 `SetBusinessInplayGame` 可遞增或遞減；客戶端不可直接設定。
- **subenddate（businesses）**：僅訂閱相關流程（`CreateBusiness` / `UpdateBusiness`）可設定；格式 `yyyy-MM-dd`，不可由客戶端隨意指定過期日。
- **subgametypes（businesses）**：僅 `CreateBusiness` / `UpdateBusiness` 可設定；值須與系統支援的遊戲類型代碼（BK、BS 等）比對。
- **subinprogresssites（businesses）**：僅 `CreateBusiness` / `UpdateBusiness` 可設定；值為合法 JSON 字串（每個遊戲類型對應站台陣列），須校驗站台有效性。
- **subpregamesites（businesses）**：同 subinprogresssites 規則。
- **updatetime（businesses）**：由系統自動填入當前 Unix 時間戳（秒），不接受用戶端傳入。
- **account（business_accounts）**：建立後不可更新（為複合主鍵 `businesscode`+`account` 的一部分）。
- **password（business_accounts）**：僅 `CreateBusinessAccount` / `UpdateBusinessAccountPassword` 可寫入；須以強雜湊演算法（如 bcrypt）儲存，禁止明文。
- **role（business_accounts）**：建立時指定（Admin 或 Trader），建立後不可變更。
- **status（business_accounts）**：僅 `UpdateBusinessAccountStatus` 可變更；值限 0（凍結）或 1（啟用）。
- **updatetime（business_accounts）**：系統自動填入。
- **sites（siteconfigs）**：僅專用配置 API 可更新清單，必須與 `site_enabled` 中啟用的站台比對；更新時記錄 updater。
- **leagues（leagueinprogressconfig）**：僅專用配置 API 可更新，須校驗聯賽存在性。
- **updater（siteconfigs, leagueinprogressconfig, playmodeconfigs_*, game_settings, gametype_settings, site_settings, league_settings, template_settings）**：自動填入當前操作者帳號，不接受用戶端傳入。
- **updatetime（siteconfigs 等多數配置表）**：由系統自動設定為當時時間戳，不接受局部修改。
- **settings（game_settings, gametype_settings, league_settings, template_settings, playmodeconfigs_*）**：僅對應的 Create/Update API 可寫入；須為合法 JSON 字串，不可包含非序列化物件。
- **enabled（playmodeconfigs_game, playmodeconfigs_league, game_settings, league_settings, site_enabled）**：僅經由對應設定 API 或狀態管理 API 調整，值限 0 或 1。
- **gid, lid, gdate（playmodeconfigs_game）**：代表外部比賽標識，應與 games 資料庫同步，不可由用戶端隨意新建或修改。
- **game, gdate（game_settings）**：須與實際比賽資料對應，由內部流程寫入，不可由終端使用者直接指定無效值。
- **password（users）**：僅使用者管理 API 可寫入，須以雜湊儲存；任何對外回傳皆不可包含。
- **account（users）**：建立後不可更新。
- **company（users, gametype_settings, site_settings 等）**：建立後不可變更（主鍵約束）。

### 讀取規則

- 查詢 `businesses`：僅應以 `businesscode` 主鍵查詢；避免以 `email` 或 `authtoken` 為條件進行全表掃描（無索引支援）。
- 查詢 `business_accounts`：必須指定 `businesscode`；登入驗證時限制 `status = 1`，凍結帳戶不可登入。
- 查詢 `game_settings`：必須指定 `company`，避免跨公司訪問。
- 查詢 `siteconfigs`：需要 `businesscode` 與 `gametype` 共同約束。
- 查詢 `playmodeconfigs_gametype` / `_league` / `_template` / `_game`：依業務需求透過 businesscode + gametype (±id) 過濾；`_game` 層級可配合 `gdate` 範圍查詢，以提升效能。
- 查詢 `site_enabled`：透過 `site` 主鍵查詢是否啟用（`enabled = 1`），作為站台可用性校驗。
- 查詢 `league_settings`：需指定 `company` + `gametype`。
- 日誌表（`logs`, `logs_business` 等）：僅供內部稽核查詢，對外 API 不開放即時查詢；若有開放，須依權限過濾 `company` 或 `businesscode`。

### 不可回傳欄位

- **password**（`business_accounts.password`, `users.password`）：任何對外 GET API 皆不可包含，僅後端驗證時使用。
- **authtoken**（`businesses.authtoken`）：用於內部服務認證，不得洩漏給客戶端。
- **ip**（`logs.ip`, `logs_business.ip`）：客戶端 IP 屬於隱私資訊，常規日誌查詢回傳應遮蔽或排除。

### Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| 無 | – | – | 本服務目前未直接使用 Redis 快取配置；若需要可於上游應用層自行快取 game_settings 查詢結果。 |

### 本服務不負責

- **比賽即時數據（比分、狀態）寫入**：遊戲數據寫入由 `gamedataservice` 負責；本服務僅管理設定元數據，不參與比賽過程更新。
- **外部站台數據同步**：`siteconfigs` 僅儲存配置，實際將配置推送至外部系統或從資訊源拉取資料，由訊息處理服務或網關服務承擔。

### 常見錯誤

- ❌ 使用明文密碼建立帳號 → ✅ 密碼必須經由 bcrypt 雜湊再儲存。
- ❌ 在查詢 `business_accounts` 時未帶 `businesscode` 進行全表掃描 → ✅ 所有查詢必須以 `businesscode` 作為分區鍵條件，避免跨業務誤查。
- ❌ 直接返回 `authtoken` 欄位給客戶端 → ✅ 應在序列化時排除該欄位。
- ❌ 忽略 `subenddate`，允許已過期的商務帳戶繼續建立遊戲設定 → ✅ 建立遊戲設定前應先檢查 `businesses.subenddate` 是否未過期。
- ❌ 修改 `game_settings` 時未驗證 `game` 與 `gdate` 是否存在於 games 資料庫 → ✅ 寫入前應參考 games 表確認合法性。
- ❌ 硬編碼 `company` 值導致跨公司資料污染 → ✅ 始終從身份驗證上下文取得當前 company，不依賴請求參數中的 company。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Games PostgreSQL (games_bk, games_bm, games_bs, games_ck) | reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- **無**：本服務僅讀取比賽記錄，所有寫入（含比分、狀態、賽程）由遊戲數據同步服務（gamedataservice）負責。

### 讀取規則

- **取得單一比賽**：根據內部 `id` 或 `siteidmaps` 中的 `SiteGID` 查詢；通常經由 `IGameService.GetGameSettingByGID` 觸發。
- **查詢可設定之比賽**：僅選取 `status` 為 `PreGame`、`Live` 或等同狀態的記錄，避免對已完賽（如 `Final`）比賽進行設定。
- **按聯賽或日期篩選**：可搭配 `lid`（聯賽 ID）與 `gdate` 範圍進行批量查詢，用於賽程管理或遊戲設定初始化。
- **跨資料表查詢**：須根據遊戲類型後綴（`_bk`, `_bm`, `_bs`, `_ck`）選取對應的表，不可跨表混合查詢（如 `games_bk` 與 `games_bm` 互為獨立邏輯表）。

### 不可回傳欄位

- **無**：本表無密碼或系統內部處理標記，所有欄位可隨比賽資訊一起回傳。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| 無 | – | – | 本服務對 games DB 無直接 Redis 操作；若需要快取比賽資料，由上游或消費端自行維護。 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 比賽結果更新（比分、狀態） | gamedataservice | 比賽 `match_h`, `match_a`, `status`, `resultinfo` 等欄位由專責數據同步服務寫入，本服務僅讀取。 |
| 賽程與隊伍主檔維護 | gamedataservice / teamservice | 隊伍名稱、ID、聯賽等資料的同步與維護不屬 gamesettingservice 職責。 |

---

## 常見錯誤

- ❌ 嘗試直接 UPDATE `games_bk` 的 `match_h` 或 `status` → ✅ 比賽結果應由數據同步服務寫入，本服務僅應讀取。
- ❌ 跨遊戲類型查詢時未切換正確的表（例如用 `games_bk` 處理 `bm` 類型的遊戲）→ ✅ 應根據 `gametype` 參數選取對應的 `games_{type}` 表。
- ❌ 向使用者回傳 `siteidmaps` 時未過濾過長的原始 JSON → ✅ 如有必要可精簡回傳結構，但無敏感性，無需強制排除。