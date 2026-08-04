# syncservice — DB 操作邊界

> 產出時間：2025-04-15 16:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| PostgreSQL Games | reader | 按遊戲類型分表（games_{gtype}），存放比賽基本資訊、比分、狀態等。Schema：[db/games.json](../../db/games.json) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- 本服務僅從 `games_{gtype}` 表讀取數據，不執行 INSERT / UPDATE / DELETE，所有寫入操作由外部資料源維護。

### 讀取規則

- **動態分表查詢**：任何對 `games` 的存取都必須指定 `gtype`，以決定實際操作的 `games_{gtype}` 分表。未指定 `gtype` 或無法解析為合法表名應視為錯誤。
- **增量同步比賽**：`WHERE create_at > {last_sync_timestamp} ORDER BY create_at` — 透過 `create_at`（毫秒時間戳）增量拉取新進或更新的比賽，適用於定時同步流程。
- **依來源站點過濾**：`WHERE source = ?` — 常用於針對特定來源（如 "panda"）進行批次同步或檢查。
- **查詢今日比賽**：`WHERE gdate = CURRENT_DATE` — 用於每日排程處理，避免掃描歷史資料。
- **依狀態過濾**：`WHERE status IN ('PreGame', 'Live')` — 只處理尚未結束的賽事，避免重複操作已結束（Final）的比賽。
- **透過聯賽 ID 查詢**：`WHERE lid = ?` — 用於撈取特定聯賽下的所有賽事，常與日期範圍搭配。

### 不可回傳欄位

- 本服務不對外暴露 `games` 表，內部傳輸無欄位遮蔽需求；若未來對外提供，需評估遮蔽 `siteidmaps` 等可能含敏感映射資訊的欄位。

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

### 讀取規則

- **同步帳戶資訊**：讀取 `accounts_*` 表時，應明確過濾條件：若僅同步啟用帳戶，需添加 `enabled = 1`；全量同步時應在應用層標記狀態。
- **操作日誌查詢**：`SELECT * FROM actionlog WHERE date = ? ORDER BY addtime DESC` — 按日期分區並依時間降序獲取最新操作記錄。

### 不可回傳欄位

- **accounts.password**：不得經任何對外 API 回傳（包含雜湊值），僅用於內部同步傳輸且必須通過安全通道。
- **accounts.phone**：除必要通知場景（如簡訊網關）外，不對外暴露。
- **accounts.handler**：若內含密鑰、令牌等敏感配置，應在對外介面遮蔽此欄位。
- **actionlog.detail**：對外查詢時，可遮蔽部分敏感操作參數（如密碼、令牌），僅保留審計所需摘要。

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
- ❌ 查詢 `games` 時未傳入 `gtype` 或企圖 `SELECT * FROM games` 而實際不存在總表，導致執行期錯誤或掃描所有分表 → 正確做法：要求呼叫方提供 `gtype`，並動態拼出目標表名 `games_{gtype}` 進行操作。