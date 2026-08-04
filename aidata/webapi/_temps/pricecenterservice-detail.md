# pricecenterservice — DB 操作邊界

> 產出時間：2025-07-24 12:00  
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）  
> ⚠️ AI 產出，需資深工程師審核後生效  

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Games PostgreSQL | writer / reader（部分表唯讀） | Schema：[db/games.json](../../db/games.json) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- **aimerge_label_overrides**：人工審核時僅可寫入 `override_label`（是否為同一場比賽）、`excluded_from_training`（是否排除訓練）、`reason`（變更原因）、`reviewed_by`（審核人員）、`reviewed_at`（審核時間）。嚴禁修改 `game_type`、`gdate`、`prediction_id`、`source_b`、`game_a_sitegid`、`source_b_sitegid` 等關聯欄位。更新前需驗證審核者權限。
- **aimerge_source_mapping**：確認操作時可寫入 `confirmed_at` 與 `confirmed_by`，並須與 `prediction_id` 關聯。`game_type`、`gdate`、`game_a_sitegid`、`source_b`、`source_b_sitegid` 等映射關係不可人工直接修改，僅能透過對應預測記錄或自動化流程建立。
- **aimerge_runtime_config**：限授權管理員透過專用 API 新增或更新配置。修改時必須記錄 `updated_by`、`updated_at` 與 `change_reason`。不可直接刪除記錄，停用時應將 `is_active` 設為 `false`。`params`（JSONB 配置參數）格式需符合定義結構，變更前應進行版本控制（`version_id`、`parent_version_id`）。
- **其他表**（`aimerge_match_predictions`、`aimerge_daily_reports`、`aimerge_backtest_runs`、`aimerge_historical_runs`、`aimerge_team_aliases`）：**唯讀**。這些表的數據由 AI 合併排程、回測系統或資料導入服務維護，本服務不得執行 INSERT / UPDATE / DELETE。

### 讀取規則

- **配對審核查詢**：查詢 `aimerge_match_predictions` 時需依業務場景過濾 `status`（如 `'pending'`、`'auto_confirmed'`），並結合 `game_type`、`gdate` 等條件縮小範圍，避免全表掃描。
- **映射確認查詢**：讀取 `aimerge_source_mapping` 時以 `game_type + gdate` 為核心條件，可附加 `source_b` 等過濾，確保僅查詢已由預測關聯之記錄。
- **人工覆蓋查詢**：查詢 `aimerge_label_overrides` 時須指定 `game_type` 與 `gdate`，可依 `reviewed_by` 或 `reviewed_at` 排序，避免未經篩選的全表讀取。
- **配置讀取**：讀取 `aimerge_runtime_config` 時應取 `is_active = true` 且 `effective_from <= NOW()` 的最新版本，確保應用的配置為目前啟用版本。
- **報告與回測記錄**：查詢 `aimerge_daily_reports`、`aimerge_backtest_runs`、`aimerge_historical_runs` 時需帶入 `game_type` 及日期範圍（`report_date`/`backtest_date`/`target_date`），不可全表掃描。回測數據僅供內部分析，不對外提供原始樣本。
- **隊伍別名**：`aimerge_team_aliases` 僅供內部匹配演算法使用，一般業務 API 不應暴露原始別名資料。

### 不可回傳欄位

- `aimerge_match_predictions.score_detail`：內部評分細節（如名稱相似度、日期接近度等），不建議直接回傳給前端，避免揭露演算法邏輯。
- `aimerge_backtest_runs.improved_samples` / `regression_samples`：包含樣本 ID 的 JSON 陣列，屬內部回測資料，對外 API **禁止回傳**。
- `aimerge_runtime_config.params`：配置參數可能包含機密閾值或策略細節，僅限管理後台可讀取，一般服務查詢不得暴露。
- `aimerge_team_aliases.alias_text` / `canonical_team_id`：內部隊伍映射資訊，不應在普通使用者介面顯示。
- `aimerge_daily_reports.error_breakdown`：詳細錯誤分類數據，若無必要不應對外提供，可改為彙總統計。

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| 開獎中心 Cassandra (pricecenter) | owner / writer / reader | Schema：[db/pricecenter.json](../../db/pricecenter.json) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

#### 帳號相關 (accounts_*)

- **password**：僅帳號建立或密碼重設 API 可寫入；須經雜湊儲存；不允許以明文方式直接 UPDATE。
- **handler**：處理程序配置（map<text, text> 結構，如處理器鍵值對）；僅本站 handler 設定相關 API 可寫入；寫入前須驗證 map 結構合法性（key/value 格式）。
- **enabled**：帳號啟用狀態（0 禁用、1 啟用）；僅管理員介面可修改；不得與帳號建立 API 同時變更。
- **closetime**：帳號關閉時間；僅帳號關閉操作由系統自動設定；一般業務不應手動寫入。
- **phone**：電話號碼；僅帳號建立或個人資料修改 API 可寫入。
- **username**：使用者名稱；僅帳號建立或個人資料修改 API 可寫入。

#### 比賽中心主表
- **games_<gameType>**：僅對應的賽事管理服務（如 collector、後台管理）可寫入，pricecenterservice **唯讀**；不允許直接 INSERT / UPDATE / DELETE。
- **leagues_<gameType>、teams_<gameType>**：聯賽與隊伍基礎資料由後台或同步服務維護，本服務**唯讀**。
- **date_leagues**：每日聯賽快取，由排程程序自動產生，本服務**唯讀**。
- **automapteams、automaperrs**：自動映射結果由映射演算法寫入，本服務僅能讀取，不可直接修改 ratio、errtype 等欄位。
- **datum_log**：比賽相關變更日誌僅由賽事同步服務寫入，本服務**唯讀**。
- **inplayspreadlogs**：滾球讓分記錄僅由滾球系統寫入，本服務**唯讀**。
- **actionlog**：操作記錄僅由特定業務操作（如賽事比分拆分/合併、隊伍校正等）時 INSERT；寫入時務必正確設定 `date`（分區鍵，格式 yyyyMMdd）、`addtime`（操作時間戳）、`actionclass`（操作類別，如 SiteTeam、Auto）及 `action`（操作名稱）。
- **alertlog**：告警記錄由告警系統寫入，本服務**唯讀**。

### 讀取規則

- **帳號查詢（登入/驗證）**：須篩選 `enabled = 1`，已關閉或凍結帳號不可登入。依帳號 `account`（主鍵）精確查詢。
- **帳號關停查詢**：查詢已關閉帳號時，應使用 `closetime IS NOT NULL` 且 `enabled = 0`。
- **跨站點帳號查詢**：`accounts_*` 系列表對應不同站點，查詢時需根據站點代碼（AU8, Fortuna888, HGA, HGA2, KKK, KU, NK, Panda, PinnacleV2, TG, TG999）選擇正確的表名。
- **賽事查詢**：
  - `games_<gameType>`：必須以 `lid`（聯賽ID）和 `gdate`（比賽日期）為分區鍵條件，不可跨大量分區查詢；可搭配 `status`（比賽狀態）、`teamid_a`、`teamid_h` 等集群鍵過濾。
  - `leagues_<gameType>`：按 `id` 精確查詢或依 `continent` 等條件過濾。
  - `teams_<gameType>`：按 `id` 或 `lid` 過濾。
  - `date_leagues`：依 `gdate + gametype` 取得當日活躍聯賽清單。
- **自動映射查詢**：`automapteams`、`automaperrs` 以 `gametype, site, sitelid, sitetid` 等分區鍵精確查詢；禁止列舉全表。
- **日誌查詢**：
  - `actionlog`：必須指定 `date`（分區鍵），再依 `addtime`、`user` 等集群鍵排序，並可過濾 `actionclass`。
  - `datum_log`：以 `gdate, gametype, league, gid` 分區鍵組合查詢。
  - `alertlog`：按 `site, gtype` 過濾，可限制時間範圍（`addtime`）。
  - `inplayspreadlogs`：以 `gdate, gtype, gid` 過濾特定比賽的滾球讓分記錄。
- **操作記錄查詢**：同上 actionlog。

### 不可回傳欄位

- **password**：任何對外 GET API 皆不可回傳；包含雜湊值亦不應暴露。
- **phone**：一般帳號查詢不應回傳；僅特定管理端 API 可依權限回傳。
- **closetime**：一般查詢不應回傳，僅關停記錄查詢可回傳。
- **handler**：內部處理程序配置資訊，一般前端無需獲知，管理端方可有限度讀取。
- **games_<gameType>.siteidmaps**：內部站點比賽 ID 映射，不應直接暴露。
- **automapteams.ratio、automaperrs.errtype**：技術細節，若無業務需求，不建議直接暴露。
- **actionlog.user**：可能涉及操作者隱私，對外展示時應評估去識別化或僅管理端可用。
- **datum_log.beforetime / aftertime**：比賽時間變更原始記錄，除非管理分析需求，不宜直接暴露。

---

## sport

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport MySQL | reader（大部分表）/ writer（特定 API） | Schema：[db/sport.json](../../db/sport.json) · 語意：[db/sport-detail.md](../../db/sport-detail.md) |

### 寫入限制

- **GameUsers_Wallet.Balance**：僅錢包交易服務（walletService）可透過交易紀錄更新；禁止本服務直接 UPDATE 該欄位。
- **GameUsers_Wallet_Transactions**：僅錢包服務可 INSERT，pricecenterservice **唯讀**（用於報表統計）。
- **Notification_Messages**：僅站內信服務（notificationService）可寫入；pricecenterservice **唯讀**（如提供站內信列表 API）。
- **ChatRoomHistories_Backup**：僅聊天服務（chatService）可寫入；pricecenterservice **唯讀**（如用於聊天歷史查詢）。
- **Community_Groups**：僅社群管理服務（communityService）可寫入；pricecenterservice **唯讀**群組資訊。
- **BK_SitePlayers**：僅後台管理介面或資料同步作業可寫入；不得由一般 API 直接變更。

### 讀取規則

- **錢包餘額查詢**：須使用 `AuthKey` 精確匹配，且只讀取對應使用者的錢包記錄；避免未授權的跨使用者查詢。
- **聊天歷史查詢**：須依 `GID`（群組 ID）過濾，且需驗證使用者是否具有該群組的存取權限（通常由 chatService 控制，pricecenter 僅提供讀取介面）。
- **站內信查詢**：須以 `Account` 精確對應收件者，不可跨帳號讀取；查詢啟用訊息應過濾 `Enabled = 1`。
- **社群群組列表**：若 API 需要啟用群組，應過濾 `Enabled = 1`，禁用群組不應顯示。
- **球員資料 (BK_SitePlayers)**：查詢時通常以 `Site + SiteID + Year` 複合條件獲取單一球員資料；無需特殊業務過濾。

### 不可回傳欄位

- **GameUsers_Wallet.Balance**：錢包餘額屬敏感財務資料，一般對外查詢 API 不應回傳（僅限有權限的管理端可回傳）。
- **GameUsers_Wallet.AuthKey**：認證金鑰，等同使用者憑證，任何 API 皆不可回傳。
- **ChatRoomHistories_Backup.Account**：發送者帳號（若須顯示名稱應使用 UserName 或去識別化處理）。
- **Notification_Messages.Content**：站內信內容屬個人隱私，僅限收件者本人可讀取；列表 API 不應回傳全文。
- **Community_Groups.Owner**：群主帳號，一般列表查詢不應暴露。

---

## Redis

本服務未使用 Redis。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 帳號註冊 | accountsService | 新帳號建立由 accountsService 負責，pricecenter 僅查驗與啟用停用 |
| 帳號刪除 / 軟刪除 | usercenter | 帳號邏輯刪除由 usercenter 處理，pricecenter 僅讀取啟用狀態 |
| 密碼修改 | memberSecurityService | 密碼變更流程由 memberSecurityService 負責，pricecenter 僅儲存密文 |
| 錢包交易處理 | walletService | 錢包出入金、交易紀錄寫入由 walletService 負責，pricecenter 僅讀取錢包資料用於報表或會員中心 |
| 站內信發送 | notificationService | 站內信的派送與收件管理由 notificationService 處理，pricecenter 僅提供查詢介面 |
| 聊天訊息發送 | chatService | 聊天室訊息的新增與編輯由 chatService 處理，pricecenter 僅讀取歷史記錄 |
| 社群群組管理 | communityService | 群組的建立、啟用、成員管理等由 communityService 負責，pricecenter 僅讀取群組列表與資訊 |
| 運動數據同步 | （外部資料源） | 球員、聯盟等基礎資料由外部資料源匯入，pricecenter 僅負責映射與查詢 |
| 賽事資料寫入（聯賽、比賽、隊伍） | 後台管理/數據同步 | leagues、games、teams 等表的建立與更新由專門的後台或數據同步服務處理，pricecenter 僅讀取 |
| 自動隊伍映射處理 | automapService | automapteams / automaperrs 表的寫入與映射邏輯由特定映射服務負責 |
| Games DB 賽事數據維護 | collector（數據同步） | games_* 表的數據落地與更新由 collector 處理，pricecenterservice 僅能讀取 |

---

## 常見錯誤

- ❌ 直接對 `password` 欄位做明文 UPDATE → ✅ 應經雜湊後寫入，且僅允許特定帳號管理 API 操作。
- ❌ 查詢帳號時未過濾 `enabled = 1` → ✅ 所有登入/驗證查詢必須加上啟用條件，避免已關閉帳號被使用。
- ❌ 對外 GET API 回傳完整帳號欄位（含 password、phone） → ✅ 需明確過濾不可回傳欄位，避免敏感資料外洩。
- ❌ 在一般業務中直接修改 `handler` 的 map 結構 → ✅ 應透過專用 handler 管理 API 操作，避免資料結構錯亂。
- ❌ 直接對 `GameUsers_Wallet.Balance` 欄位進行 UPDATE 或 SET → ✅ 錢包餘額僅能透過 walletService 的交易接口異動，任何直接寫入將導致帳務不一致。
- ❌ 未經授權讀取 `ChatRoomHistories_Backup` 中其他使用者的聊天內容 → ✅ 查詢時必須綁定使用者所屬群組（GID）或帳戶，並配合 chatService 權限驗證。
- ❌ 站內信列表 API 回傳完整 `Content` 欄位 → ✅ 列表應僅回傳主旨（Title）與發送時間，全文內容應另提供單封查詢 API（且需驗證收件者身份）。
- ❌ 社群群組查詢未過濾 `Enabled = 1`，導致前端顯示已停用群組 → ✅ 預設查詢應加上啟用條件，若後台管理需要則由特定 API 提供。
- ❌ 查詢 `games_<gameType>` 時未限制 `gdate` 與 `lid` 分區鍵 → ✅ 必須帶入日期與聯賽條件，避免掃描過多分區，影響效能。
- ❌ 直接回傳 games 表中的 `siteidmaps` 給前端 → ✅ 應僅傳遞業務所需的標準資料，內部映射不應暴露。
- ❌ 在 Cassandra 唯讀表中嘗試 INSERT 或 UPDATE → ✅ 除 accounts_* 與 actionlog 明確允許寫入外，一律以只讀方式操作，避免資料錯亂。
- ❌ 跨站點查詢時未使用正確的 `accounts_*` 表名 → ✅ 必須根據站點代碼（如 AU8、HGA、TG999）選取對應的帳號表。
- ❌ 操作記錄查詢未指定 `date` 分區鍵 → ✅ 必須以 `date` 為查詢條件，避免全表掃描導致效能問題。