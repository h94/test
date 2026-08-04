# syncservice — DB 操作邊界

> 產出時間：2025-07-14 10:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| PostgreSQL Games | reader | Schema：[db/games.json](../../db/games.json) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- 本服務僅從 `games_{gtype}` 表讀取數據，不執行 INSERT / UPDATE / DELETE，所有寫入操作由外部資料源維護。

### 讀取規則

- **增量同步比賽**：`SELECT * FROM games_{gtype} WHERE create_at > {last_sync_timestamp} ORDER BY create_at` — 透過 create_at（毫秒時間戳）增量拉取新進比賽。
- **依來源站點同步**：`SELECT * FROM games_{gtype} WHERE source = ?` — 針對特定來源（如 "panda"）進行同步。
- **查詢今日比賽**：`SELECT * FROM games_{gtype} WHERE gdate = CURRENT_DATE` — 用於每日批次處理。
- **依狀態過濾**：`SELECT * FROM games_{gtype} WHERE status IN ('PreGame', 'Live')` — 只處理尚未結束的比賽，避免重複處理 Final 賽事。
- **透過聯賽 ID 查詢**：`SELECT * FROM games_{gtype} WHERE lid = ?` — 針對指定聯賽取得比賽清單。

### 不可回傳欄位

- 本服務不對外暴露 games 表，內部傳輸無欄位遮蔽需求；若未來對外提供，需評估遮蔽 `siteidmaps` 等可能含敏感映射資訊的欄位。

---

## gamesettings

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra gamesettings | owner / writer / reader | Schema：[db/gamesettings.md](../../db/gamesettings.md) · 語意：[db/gamesettings-detail.md](../../db/gamesettings-detail.md) |

### 寫入限制

- **business_accounts.password**：僅業務帳戶新增/密碼修改 API 可寫入；須經雜湊（BCrypt 或等價演算法）後儲存，不得明文寫入。
- **businesses.authtoken**：僅授權刷新 API 可更新；Token 生成須包含過期時間簽章，不得由其他 API 直接修改。
- **businesses.subenddate**：僅訂閱管理後台 API 可寫入；寫入前須驗證日期格式為 `YYYY-MM-DD` 且不小於當前日期。
- **game_settings.settings**：寫入時須為合法 JSON 字串；若包含 `odds`、`limits` 等嵌套結構，需通過格式校驗。
- **gametype_settings.settings**：同上，寫入時須為合法 JSON 字串；若值涉及啟用/停用邏輯，須校驗與對應 company + gametype 的一致性。
- **league_logs**：僅由同步完成後的寫入程式寫入（非用戶端直接寫入）；每次寫入應為追加（upsert 主鍵為 company + gametype）。
- **game_settings.enabled / showstopplaymode / swap**：僅透過遊戲設定管理 API 寫入；不得批量 UPDATE 跳過業務邏輯。

### 讀取規則

- **業務帳戶登入**：`WHERE businesscode = ? AND account = ? AND status = 1` — 僅查詢啟用狀態的帳戶，禁用（status=0）帳戶不可登入。
- **遊戲設定查詢（前台顯示）**：`WHERE enabled = 1` — 只回傳啟用的設定，停用設定不提供給遊戲前台。
- **業務訂閱有效性檢查**：讀取 `businesses.subenddate` 時須比對當前日期，已過期（subenddate < today）之業務不應回傳遊戲設定資料。
- **聯賽日誌查詢**：`WHERE company = ? AND gametype = ? ORDER BY updatetime DESC` — 取最新一筆作為該 game type 的聯賽清單，不需要歷史資料。

### 不可回傳欄位

- **business_accounts.password**：任何對外 API 不得回傳密碼雜湊值，僅可回傳 `是否存在` 或 `最後修改時間`。
- **businesses.authtoken**：不得經由 GET / PUT 端點回傳；僅在登入/刷新 Token 時於 Response Body 回傳新 Token。
- **businesses.email**：除管理後台外，前台 API 不應回傳業務聯絡人 email。

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter | reader, writer | Schema：[db/pricecenter.json](../../db/pricecenter.json) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **actionlog.detail**：寫入時須為合法 JSON 字串，且應包含 `operation`、`target`、`status` 等結構化欄位。
- **actionlog.date / addtime**：由系統自動填入（分區鍵 `date` 依當前日期，`addtime` 依當前時間戳），不允許手動指定。
- **actionlog.action / actionclass**：須從預定義的動作枚舉中選取，不得寫入任意字串。
- **accounts_* 表**：syncservice 不負責此類表的寫入，寫入權限歸屬於 pricecenter 管理服務。
- **games_{gtype}**：僅由同步程式（SourceDB → TargetDB）寫入；`status` 欄位須依賽事生命週期依序更新（PreGame → Live → Final），禁止跳躍式狀態變更；`addtime` 為 Unix 毫秒時間戳，由系統自動填入。
- **odds_{gtype}**：僅由賠率同步程式寫入；每次寫入應以 `site + sitelid + gdate + sitegid` 為複合主鍵進行 upsert，避免重複記錄。
- **sitegames_{gtype}**：由遊戲同步程式維護；`sitegid` 與 `gid` 的映射關係一經建立不得直接修改，僅可整筆刪除後重建。
- **leagues_{gameType} / teams_{gameType}**：主檔資料，由後台管理介面或外部同步程式寫入；`name_map` 欄位須為合法 JSON 字串（用於多語言名稱映射）。
- **siteteams_{gtype} / siteleagues_{gtype}**：來源端（SourceDB）的站點映射表，僅供讀取以建立內部查詢索引，不得由 syncservice 寫入目標端。

### 讀取規則

- **同步帳戶資訊**：讀取 `accounts_*` 表時，應明確過濾條件：若僅同步啟用帳戶，需添加 `enabled = 1`；全量同步時應在應用層標記狀態。
- **操作日誌查詢**：`SELECT * FROM actionlog WHERE date = ? ORDER BY addtime DESC` — 按日期分區並依時間降序獲取最新操作記錄。
- **依站點查詢比賽映射**：`SELECT * FROM sitegames_{gtype} WHERE site = ?` — 取得指定站點的所有比賽 ID 對照表，用於跨站點資料關聯。
- **依日期取得賠率**：`SELECT * FROM odds_{gtype} WHERE gdate = ?` — 按比賽日期批次拉取賠率；若需細粒度查詢，可附加 `site` 或 `sitelid` 條件。
- **比賽狀態同步過濾**：`SELECT * FROM games_{gtype} WHERE status IN ('PreGame', 'Live')` — 僅同步尚未完賽的比賽，Final 狀態不再更新。
- **聯賽/隊伍名稱解析**：讀取 `leagues_{gameType}` 或 `teams_{gameType}` 時，須解析 `name_map` JSON 欄位，依據請求端語言（如 `zh-TW`、`en`）回傳對應名稱。
- **站點隊伍/聯賽映射查詢**：`SELECT * FROM siteteams_{gtype} WHERE site = ? AND sitelid = ?` — 用於建立站點隊伍 ID 與內部隊伍 ID 的對照關係。

### 不可回傳欄位

- **accounts_*.password**：不得經任何對外 API 回傳（包含雜湊值），僅用於內部同步傳輸且必須通過安全通道。
- **accounts_*.phone**：除必要通知場景（如簡訊網關）外，不對外暴露。
- **accounts_*.handler**：若內含密鑰、令牌等敏感配置，應在對外介面遮蔽此欄位。
- **actionlog.detail**：對外查詢時，可遮蔽部分敏感操作參數（如密碼、令牌），僅保留審計所需摘要。
- **games_{gtype}.match_a / match_h**：可能內含站點原始映射資料或內部結構化資訊，對外回傳時應僅提供必要的客隊/主隊名稱與 ID，不暴露原始資料塊。
- **odds_{gtype} 整表**：賠率資料視為業務機密，僅供內部服務間同步使用，未經授權不得對外暴露任何欄位。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET | `gamesettings:company:{company}:gametypes` | 啟動或重新讀取 gametype 設定 | 3600s；用於快取該 company 下所有啟用的 game type 列表 |
| DEL | `gamesettings:company:{company}:gametypes` | 當 company 的 gametype 設定變更時主動清除 | — |
| GET | `gamesettings:game:{id}` | 查詢特定 game_setting 時 | 無 TTL，寫入時主動更新 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 業務帳戶密碼驗證 | authservice | syncservice 僅負責讀取帳戶狀態與角色，不執行密碼比對 |
| 遊戲賽程資料同步 | gamesyncservice | 遊戲主檔（games_{gtype}、sitegames_{gtype}）由另專服務同步 |
| 玩家註冊/登入 | userservice | 使用者（users table）管理由 user service 負責 |
| 站點設定維護 | siteservice | site_settings 表由站點管理服務維護 |
| 訂閱金流處理 | billingservice | 訂閱週期、付款、過期通知由 billing service 處理 |
| 帳戶的建立、刪除與屬性修改 | pricecenter 管理模組 | syncservice 僅讀取帳戶資料進行同步，不變更帳戶生命週期 |
| 價格中心主檔維護 | pricecenter 服務 | 定價、匯率等核心資料由 pricecenter 維護，syncservice 不干預 |

---

## 常見錯誤

- ❌ 直接在前端 API 回傳 `business_accounts.password` 用於「檢查是否已設定密碼」 → 正確做法：設計專用端點或僅回傳 `"hasPassword": true/false`。
- ❌ 在同步遊戲設定時未檢查 `enabled` 狀態，導致停用設定被同步到前台 → 正確做法：讀取時固定加上 `WHERE enabled = 1`。
- ❌ 寫入 `game_settings.settings` 時未驗證 JSON 格式，導致後續讀取 JSON parse 失敗 → 正確做法：寫入前執行 JSON parse 校驗，失敗則拋 400。
- ❌ 直接使用 `SELECT * FROM game_settings` 無 WHERE 條件，造成大量資料傳輸與效能問題 → 正確做法：依業務場景（如 company、gametype、gdate）添加索引過濾條件。
- ❌ 在同步 `accounts` 時不加過濾直接全表掃描，導致同步大量歷史帳戶 → 正確做法：根據業務需求限定查詢條件（如 `enabled = 1` 或增量同步 `closetime > last_sync_time`）。
- ❌ 寫入 `actionlog.detail` 時，直接拼接字串而不校驗 JSON 格式，導致後續解析錯誤 → 正確做法：序列化物件為 JSON 後寫入，必要時使用結構體強制欄位。
- ❌ 將 `accounts.password` 透過 HTTP 明碼傳輸給其他服務 → 正確做法：使用內部 gRPC 加密通道，或傳遞令牌代替。
- ❌ 未正確處理 `date` 分區鍵，導致日誌寫入分佈不均 → 正確做法：確保 `date` 格式為 `yyyy-MM-dd` 並與 `addtime` 日期一致。
- ❌ 寫入 `games_{gtype}` 的 `status` 時，直接從 `Live` 跳至 `Final` 而跳過中間狀態 → 正確做法：嚴格遵循狀態機，每步變更都應寫入對應的轉換記錄。
- ❌ 同步 `odds_{gtype}` 時，未使用 upsert 而使用 insert，導致重複主鍵錯誤 → 正確做法：以 `site + sitelid + gdate + sitegid` 為鍵進行 upsert。