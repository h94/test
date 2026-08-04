# zbaparser — DB 操作邊界

> 產出時間：2025-12-04 14:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| pricecenter (Cassandra) | writer / reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

#### accounts_{platform}（所有平台帳號表，例：accounts_AU8、accounts_Fortuna888 等）

- `account`（主鍵）：僅由 zbaparser 內部帳號初始化或同步流程寫入，禁止外部 API 或直接 UPDATE 修改主鍵。
- `password`：必須經過雜湊（hash）後儲存，禁止明文寫入或透過 UPDATE 直接覆寫。
- `enabled`：僅 zbaparser 內部狀態管理邏輯可更新（如啟用/停用），外部不可直接 UPDATE。
- `handler`（map<text,text> 配置映射）：僅在帳號關聯的 provider handler 初始化時寫入，不允許任意欄位覆寫或部分更新。
- `closetime`：帳號關閉或到期時間，僅由 zbaparser 內部關閉流程或排程更新，外部不可直接修改。
- `phone`：電話號碼，僅在帳號建立或後台授權操作時可更新，不可隨意由外部 API 變更。
- `username`（若存在）：使用者名稱，由初始化寫入，後續異動需透過授權後台操作，不可由一般業務 API 修改。

#### actionlog（操作日誌）

- 所有欄位（`action`、`actionclass`、`detail`、`addtime`、`date`、`user`、`gametype`）：僅 zbaparser 在執行業務操作時自動寫入，嚴禁外部直接 INSERT 或 UPDATE。
- `addtime`、`date` 必須使用服務端時間，禁止由客戶端傳入。

#### games_{gameType}（各遊戲類型比賽主表）

- `id`（主鍵）：由 zbaparser 從上游資料解析後生成或指派，禁止任何外部寫入或修改。
- `lid`、`teamid_a`、`teamid_h`、`gdate`、`gtime`：僅由 zbaparser 根據上游比賽資訊解析後寫入，不允許直接 INSERT/UPDATE。
- `status`：比賽狀態（0=未開賽, 1=結束, 2=滾球, -1=異常），僅 zbaparser 根據比賽生命週期更新，外部 API 不得直接改寫。
- `match_h`、`match_a`：主客隊分數，僅在比賽結果確認後由 zbaparser 寫入，禁止手動修改。
- `otherinfo`、`resultinfo`（JSON 文字）：僅由 zbaparser 整筆覆寫，不允許部分更新或由外部傳入。
- `addtime`：記錄時間戳（毫秒），由系統插入時自動設定，禁止後續修改或客戶端提供。

#### sitesgames_{gameType}（站點比賽對應表）

- `site`、`sitegid`、`gid`、`gdate`、`gtime`：僅由 zbaparser 解析站點賽事資料後寫入，不可外部直接操作。
- `status`、`match_h`、`match_a`：由 zbaparser 根據比賽進程更新，外部不得直接修改。
- `odds`（JSON 文字）：僅由 zbaparser 根據站點回傳的賠率資料整筆寫入，不支援部分修改。
- `team_a`、`team_h`、`teamid_a`、`teamid_h`、`sitelid`：由 zbaparser 寫入，外部不可修改。
- `addtime`：系統自動設定，禁止客戶端提供。

#### leagues_{gameType}（聯盟資訊表）

- `id`（主鍵）：由 zbaparser 同步聯盟資料時寫入，外部不可修改。
- `lname`、`name_map`：名稱資訊僅由 zbaparser 更新，不允許外部 API 直接操作。
- `addtime`：系統自動產生。

#### teams_{gameType}（球隊資訊表）

- `id`（主鍵）：由 zbaparser 寫入。
- `tname`、`name_map`、`otherinfo`：僅由 zbaparser 整筆寫入或更新，外部不可直接修改。
- `addtime`：系統自動設定。

#### siteleagues_{gameType}（站點聯盟對應表）

- `sitelid`、`lid`：由 zbaparser 解析站點聯盟資訊後寫入，外部不可修改。
- `name_map`、`en_name`：僅由 zbaparser 更新。
- `addtime`：系統自動產生。

### 讀取規則

#### accounts_{platform}

- 所有帳號使用場景（登入、索取賠率等）必須同時檢查 `enabled = 1` 且 `closetime` 為空或大於當前時間。
- 查詢一律依主鍵 `account` 精確查找，無全表掃描場景。

#### actionlog

- 僅供內部稽核使用，不對外提供業務查詢。如需讀取，必須帶上分區鍵 `date`，搭配集群鍵（`user`、`gametype`、`addtime`）過濾，禁止全表掃描。
- 不得用於業務流程的即時決策。

#### games_{gameType}

- 查詢必須指定遊戲類型（表名後綴 `_{gameType}`），並強制帶上 `gdate` 範圍過濾，禁止全分區掃描。
- 對外提供賽事列表時，應根據 `status` 和 `gdate` 篩選有效範圍（如 `status IN (0,2)`）。
- 透過 `id` 精確查詢時，仍需帶上 `gdate` 分區條件以提升效能。

#### sitesgames_{gameType}

- 查詢需指定 `site` 及 `gdate` 作為過濾條件，避免跨分區掃描。
- 透過 `gid` 尋找對應統一比賽時，應結合 `site` 與 `gdate` 查詢。

#### leagues_{gameType}、teams_{gameType}

- 依主鍵 `id` 精確查詢，如需列舉應限制 `addtime` 範圍。

#### siteleagues_{gameType}

- 依 `sitelid` 查詢，可搭配 `addtime` 過濾。

### 不可回傳欄位

- `password`：所有 accounts 表，任何對外 GET API 均不可回傳。
- `phone`：accounts 表，預設不回傳，僅在後台授權且必要時可控揭露。
- `actionlog` 所有欄位：不對外提供 API 查詢，若特殊情境需回傳，`detail` 中的敏感資訊必須脫敏。
- `otherinfo` 與 `resultinfo`（games 表、teams 表）：可能包含內部調試資訊，對外提供時需過濾或清洗。
- `odds`（sitesgames 表）：屬外部站點賠率資料，原則上不對終端用戶直接回傳原始內容，可依授權揭露給特定管理端。

---

## gamesettings

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| gamesettings (Cassandra) | owner / writer / reader | Schema：[db/gamesettings.md](../../db/gamesettings.md) · 語意：[db/gamesettings-detail.md](../../db/gamesettings-detail.md) |

### 寫入限制

- **password**（business_accounts）：必須經過哈希（hash）後儲存，禁止明文寫入或透過 UPDATE 直接覆寫。
- **authtoken**（businesses）：僅商家初始化或 API 金鑰輪換流程可寫入，不可由外部 API 任意修改。
- **subenddate**（businesses）：僅上游訂閱管理系統可更新；zbaparser 不得直接變更該欄位。
- **subinprogresssites** 與 **subpregamesites**（businesses）：僅上游商家管理系統可更新，且必須為合法 JSON 陣列字串；zbaparser 僅讀取這些配置。
- **subgametypes**（businesses）：僅上游訂閱管理系統可更新，且必須為合法遊戲類型代碼列表（如 BK, BS, FL 等）；zbaparser 僅讀取並用於過濾對應賽事。
- **extraplaymodes**（businesses）：僅上游設定，必須為合法 JSON 物件；zbaparser 僅讀取，不負責寫入。
- **inplaycount**（businesses）：僅上游設定，必須為非負整數；zbaparser 僅讀取並作為並發處理上限的參考值。
- **enabled**（game_settings）：僅對應 API 透過 status 參數控制啟用/停用，不可直接 UPDATE 原始值。
- **settings**（game_settings / gametype_settings）：寫入時必須為合法 JSON 字串，服務層須做 JSON 格式驗證。
- **updater、updatetime**：每次寫入時由服務自動填充（updater=登入帳號，updatetime=當前毫秒時間戳），不允許外部傳入。

### 讀取規則

- **帳號登入（business_accounts）**：查詢時必須同時檢查 `status = 1`（啟用），已停用帳號不可用於任何後續操作。
- **商家驗證與配置讀取（businesses）**：依 `businesscode` 精確查詢。讀取時須確認：
  - 商家訂閱未過期（`subenddate` >= 當日，格式 YYYY-MM-DD）。
  - `subgametypes` 包含所需的遊戲類型，且對應的 `subinprogresssites` 或 `subpregamesites` 中有合法的站點配置列表（非空 JSON 陣列）。
  - `inplaycount` 可作為並發處理上限的參考值。
- **遊戲設置（game_settings）**：依 `id` 或 `company` + `gametype` + `game` 組合條件查詢，無全表掃描場景。
- **遊戲類型設置（gametype_settings）**：依 `company`（partition key）搭配 `gametype`（clustering key）查詢，不可省略 partition key。
- **聯盟日誌（league_logs）**：依 `company` + `gametype` 讀取，僅返回最近更新紀錄。

### 不可回傳欄位

- **password**（business_accounts）：任何對外 GET API 均不可回傳。
- **authtoken**（businesses）：僅限內部後台或授權 API 揭露，一般查詢不回傳。
- **settings**（若包含敏感內部配置）：預設不回傳，僅在特定管理端 API 中可控揭露。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| games (PostgreSQL，按比賽類型分表: `games_bk`, `games_bm`, `games_bs`, `games_ck`) | owner / writer / reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- `id`：主鍵，由 zbaparser 在插入時決定（DB 自增或業務生成），禁止任何外部修改。
- `source`：數據來源站點標識，僅由 zbaparser 在解析時寫入，不可直接 UPDATE。
- `create_at`：記錄建立時間戳（Unix 毫秒），僅在 INSERT 時由 zbaparser 設定，後續更新不得修改。
- `teams`、`siteidmaps`、`match_detail`、`resultinfo`、`otherinfo`：JSONB 欄位，僅由 zbaparser 根據上游解析結果整筆覆寫，不允許直接操作 JSON 內部區段或部分更新。
- `status`：比賽狀態，僅由 zbaparser 根據比賽歷程（PreGame → InPlay → Final）更新，外部 API 不得直接改寫。
- 其餘欄位（`lid`, `gdate`, `gtime`, `team_h`, `team_a`, `teamid_h`, `teamid_a`, `match_h`, `match_a`）均由 zbaparser 從上游資料解析後寫入，禁止未經過 parser 邏輯的直接 INSERT/UPDATE。

### 讀取規則

- 所有查詢必須附帶 `source` 或 `lid` 作為過濾條件，避免全表掃描；建議使用索引 `(source, gdate)` 或 `(lid, gdate)`。
- 對外提供比賽列表時，應根據 `status` 和 `gdate` 篩選有效範圍（例如當前進行中比賽使用 `status IN ('PreGame', 'InPlay')`）。
- 透過 `siteidmaps` 查詢特定站台 GID 時，需使用 JSONB 查詢函數並搭配 `source` 限制，不可單獨針對 JSONB 進行全表掃描。

### 不可回傳欄位

- 無明確敏感欄位；若 `resultinfo`、`otherinfo` 內部含有追蹤或調試資訊，應由對外 GET API 在輸出前過濾。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `gamesettings:game:{id}` | 讀取或更新 game_settings 單筆資料時 | 60 秒；資料變更時主動 DEL |

*註：games 相關操作未使用 Redis，查詢直接存取 PostgreSQL。*

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 帳戶註冊 / 建立 | `account-service` 或上游後台 | zbaparser 僅管理已存在帳戶的啟用狀態與配置，不處理帳號創建邏輯 |
| 密碼驗證 / 登入認證 | `auth-service` | zbaparser 僅儲存密碼雜湊，不進行密碼比對或 token 發放 |
| 跨服務帳戶同步 | `sync-service` | 若需將帳戶狀態同步至下游，由 sync-service 處理，zbaparser 不負責 |
| 操作日誌分析 / 告警 | `log-service` 或獨立監控系統 | zbaparser 僅負責寫入 actionlog，不處理日誌分析或觸發通知 |
| 商家註冊 / 資料建立 | `admin-service` 或上游後台 | zbaparser 僅管理遊戲設置，商家基本資料（businesses）由上游建立 |
| 商家訂閱管理 | `subscription-service` | zbaparser 僅讀取 `subenddate`、`subgametypes` 檢查有效性，不負責變更或續約 |
| 遊戲賽程同步 | `game-sync-service` | zbaparser 不負責從外部站點拉取賽程資料，僅處理已存在的遊戲設置 |
| API 令牌簽發 | `auth-service` | zbaparser 不負責 `authtoken` 的生成或驗證，僅儲存與讀取 |
| 比賽數據的即時來源抓取與前處理 | `game-fetcher` 或上游服務 | zbaparser 負責解析已正規化的數據並寫入 games 表，不負責原始拉取或清洗 |
| 比賽結果的結算與派彩 | `settlement-service` | zbaparser 僅記錄比賽結果，不執行任何交易、結算或派彩邏輯 |
| 比賽數據的快取與讀取加速 | `cache-service` | games 表查詢直接進入 DB，未使用 Redis 快取層，加速應由其他層實現 |

---

## 常見錯誤

- ❌ 直接在 zbaparser 內新增帳戶（INSERT accounts_XX） → 應由上游 account-service 統一建立，zbaparser 僅讀取及管理啟用狀態。
- ❌ 將 `password` 或 `phone` 欄位回傳至前端 → 應於 DTO 或查詢層過濾，僅服務內部使用。
- ❌ 未檢查 `enabled=1` 且 `closetime` 未過期即使用帳戶 → 任何後續操作都必須攔截已禁用/已過期帳戶。
- ❌ 手動插入 actionlog 記錄 → 應由系統在執行操作時自動寫入，確保一致性與審計完整性。
- ❌ 使用客戶端傳入的時間作為 `addtime` 或 `date` → 必須以服務端時間為準，避免時序錯亂或竄改。
- ❌ 直接對 accounts_XX 執行 UPDATE 修改 `account` 主鍵 → 主鍵不可變更，需透過刪除重建流程處理。
- ❌ 寫入 game_settings 時未驗證 `settings` 是否為合法 JSON → 應在服務層先做 JSON 解析嘗試，失敗則拒絕寫入。
- ❌ 讀取 business_accounts 時忽略 `status = 1` 過濾 → 可能導致停用帳號被用於操作，需攔截。
- ❌ 直接回傳 `password` 或 `authtoken` 至前端 → 應在查詢層或 DTO 轉換時過濾敏感欄位。
- ❌ 在 zbaparser 內直接修改 `subenddate` → 應由 subscription-service 統一處理，zbaparser 僅讀取。
- ❌ 直接對 games 表執行 UPDATE 修改比分或 `status` → 應由 zbaparser 根據上游數據更新，確保狀態一致性與審計完整性。
- ❌ 查詢 games 表未指定 `source` 或 `lid` 過濾條件 → 可能導致全表掃描與性能問題，必須強制帶入業務索引條件。
- ❌ 手動修改 `create_at` 以變更記錄順序 → `create_at` 為系統內部時間戳，禁止任何形式的後續修改，需透過正常解析流程重新產生記錄。