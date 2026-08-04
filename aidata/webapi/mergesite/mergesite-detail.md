# mergesite — DB 操作邊界

> 產出時間：2025-04-12 18:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter keyspace（accounts_*, actionlog, leagues, games, teams, site_games, site_leagues, site_teams, openclaw_merge） | writer（合併流程、日誌記錄）/ reader（查詢合併結果、站點對照、帳戶驗證） | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **accounts_* 表**
  - `account`：主鍵，一經建立禁止更新。
  - `password`：僅建立帳戶或重設密碼 API 可寫入；必須以不可逆雜湊（如 bcrypt）儲存；禁止明文寫入。
  - `enabled`：僅帳戶建立時設為 1，關閉時改為 0；不允許其他 API 直接更新此欄位。
  - `closetime`：僅帳戶關閉流程寫入；寫入後該帳戶視為停用，不可再次啟用。
  - `handler`：map 型態，僅由帳戶管理後台寫入，客戶端 API 禁止更新。
  - `phone`：電話號碼，更新須透過驗證流程；對外展示時依規範遮蔽。
  - `username`：部分站點無此欄位；可更新，但須符合命名規則。

- **leagues 表**
  - `LID`：主鍵，建立後不可變更。
  - `Locked`：僅管理後台可寫入，用於鎖定聯賽避免異動。
  - `NameMap`、`AbbrNameMap`（或 `LNameMap`、`Abbr_Map`）：多語言名稱對照，僅允許透過正規編輯介面更新，不得由前端直接篡改。
  - `AddTime`：建立時寫入，之後不允許修改。

- **games 表**
  - `GID`、`GDate`、`LID`：主鍵與分割鍵，建立後禁止更新。
  - `Status`：僅允許依狀態機轉換（例如未開始→進行中→已結束），不可跳躍或回溯，合併流程可更新。
  - `MergedGID`（若存在於合併邏輯）：僅合併 API 可設定，不允許手動修改。
  - `Datum`：標記主站代碼，建立後不應變更。
  - `TeamID_H`、`TeamID_A`：可更新，但必須確保參照到存在的 `teams` 記錄。
  - `Logs`：系統內部追加操作記錄，禁止外部 API 直接 INSERT/UPDATE。

- **teams 表**
  - `TID`：主鍵，不可更改。
  - `NameMap`、`Abbr_Map`：僅管理工具可編輯。
  - `LID`：若隊伍重新分配聯賽，須保持資料一致性（須同步更新相關 `games`）。

- **site_games / site_leagues / site_teams 表**
  - 組合主鍵（`Site`, `SiteLID`, `SiteGID` 等）：建立後不可修改。
  - 僅合併流程可更新對應的合併後 ID（如 `MergedGID`, `TID`），不應允許前端直接寫入。

- **openclaw_merge 表**
  - `Game`、`MainSiteGame`：JSON 欄位，僅合併流程建立時寫入，禁止任何外部 UPDATE。
  - 記錄為不可變動的合併快照，刪除須經審核。

- **actionlog 表**
  - 全部欄位由內部日誌元件 (SystemTransfer) 負責寫入，禁止任何服務或 API 直接 INSERT 或 UPDATE。
  - 寫入時必須提供完整的分割鍵（`date`）與必要的群集鍵（`gametype`, `user`, `addtime`）。
  - `detail` 為 JSON 字串，記錄操作明細，不得為空。

### 讀取規則

- **accounts_* 查詢**：
  - 登入驗證：須搭配 `account = ? AND enabled = 1`，且 `closetime` 為空（或 null），才視為有效。
  - 禁止全表掃描，一律以主鍵 `account` 精確查詢。
- **games 查詢**：
  - 必須包含分割鍵 `GDate`（日期格式 yyyy-MM-dd），可額外指定 `GameType`、`LID` 等條件；禁止無分割鍵的全表掃描。
  - 對外前台僅查詢有效 `Status`（非刪除），管理後台可查全部。
- **leagues 查詢**：
  - 應以 `GameType` + `LID` 為主要過濾條件；避免單一 `GameType` 全表撈取。
  - 前臺不顯示 `Locked=1` 的聯賽。
- **teams 查詢**：
  - 按 `TID` 或 `LID` 過濾；不支援大量模糊查詢。
- **site_* 查詢**：
  - 必須指定 `Site` 及對應的分割鍵（例如 `SiteLID`、`GDate`）。
- **openclaw_merge 查詢**：
  - 依 `GameType` + `GDate` + `LID` 查找，僅內部管理使用。
- **actionlog 查詢**：
  - 必須提供 `date`（yyyy-MM-dd）分割鍵，可選 `gametype`、`user` 等群集鍵；禁止跨日全掃。

### 不可回傳欄位

- **accounts_* 的 `password`、`handler`**：任何 API 皆不可回傳。
- **accounts_* 的 `phone`**：僅限帳戶本人或授權管理後台查詢；一般列表應遮蔽，回傳時僅保留部分碼（如 09*****123）。
- **leagues / games / teams 的 `Logs`**：內部操作軌跡，不對一般使用者回傳；管理後台可視需求選擇性提供。
- **actionlog 的 `detail`**：可能包含敏感參數，僅管理後台有權限查看完整內容。
- **openclaw_merge 的 `Game` / `MainSiteGame`**：合併原始 JSON，不對外暴露。

---

## sport

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport MySQL | writer（後台管理、聊天備份、錢包相關只讀）/ reader（前端查詢、餘額顯示、交易查詢） | Schema：[db/sport.md](../../db/sport.md) · 語意：[db/sport-detail.md](../../db/sport-detail.md) |

### 寫入限制

- **BK_SitePlayers**
  - `Site`, `SiteID`, `Year`：複合主鍵，禁止更新。
  - `Record`（mediumtext）：僅供後台資料同步或匯入 API 寫入；寫入時須確保單筆不超過 MySQL `max_allowed_packet`，避免被截斷。
  - `LastUpdateTime`：由同步流程自動填入 Unix 秒時間戳，不允許手動設定。

- **ChatRoomHistories_Backup**
  - `GID`, `Account`, `ID`：主鍵，禁止更新。
  - `AddTime`：系統自動產生（毫秒 Unix 時間戳），不允許程式或手動覆蓋。
  - `Message`（varchar(500)）：僅訊息發送 API 可 INSERT；寫入前必須驗證長度，超過上限應拒絕請求。
  - `ResponseID`：可為空，僅「回覆訊息」API 可設定；設定後不得修改。
  - `LikeAccount`：僅按讚 / 取消讚 API 維護；格式為逗號分隔帳號，寫入時須確保無重複帳號且無前後空白。
  - `ChatType`, `Rank`, `UserName`, `HeadShotPath`：發送訊息時根據當前使用者資訊填入，不允許單獨 UPDATE。

- **Community_Groups**
  - `ID`：主鍵，建立後禁止更新。
  - `Name`：存放 JSON 格式多語系內容，僅後台管理 API 可更新；必須為合法 JSON。
  - `Enabled`：僅群組管理 API 可設為 0 或 1，不允許前端直接變更。
  - `IconPath`, `Seq`, `GType`, `Description`：僅後台可寫入；`Seq` 用於排序，變更時須注意唯一性（建議使用浮點數排序法避免衝突）。
  - `Owner`：建立時指派；轉移擁有者須透過管理 API。
  - `UpdateTime`：由系統自動更新，禁止手動設定。

- **GameUsers_Wallet**
  - `AuthKey`：主鍵，錢包建立時寫入，禁止任何 API 修改。
  - `Balance`（int，單位為分）：**只允許錢包交易服務透過原子操作更新**，本服務的任何 API 嚴禁直接 `SET Balance`。
  - `LastUpdateTime`：交易變更餘額時由交易服務自動維護，禁止手動修改。

- **GameUsers_Wallet_Transactions**
  - `TID`：自增主鍵，禁止手動 INSERT 或 UPDATE。
  - `AddTime`, `Amount`, `AuthKey`, `TDate`, `Type`, `TypeInfo`：全由錢包交易服務負責寫入，**本服務對該表僅有讀取權限**。
  - 若業務需建立交易記錄，應透過錢包服務 API，不得直接操作此表。

- **Notification_Messages**
  - `TID`, `ID`：複合主鍵，禁止更新。
  - `Enabled`：僅通知管理後台可變更 0/1。
  - `Title`, `TW_Content`, `EN_Content`, `CN_Content`, `JP_Content`, `TH_Content`：僅後台可編輯；寫入時不應超過 text 欄位合理長度。
  - `UpdateTime`：系統自動更新，禁止手動設定。

- **notification_sitemails**（站內信）
  - `ID`：主鍵，建立後不可改。
  - `Sender`, `Receiver`：建立時寫入，不可更新。
  - `Title`, `Content`：建立時寫入，管理 API 可撤回（設為空或標記刪除）。
  - `ReadStatus`：僅收件人可將其設為 1（已讀），且設定後不可回復為 0。
  - `SendTime`：系統自動產生，禁止修改。

### 讀取規則

- **BK_SitePlayers**：必須提供 `Site` + `League`，並搭配 `Year` 條件；建議使用對應複合索引，禁止無 `Year` 全表掃描。
- **ChatRoomHistories_Backup**：查詢強制包含 `GID` 與 `AddTime` 範圍（起訖）；不允許跨群組或無時間範圍大範圍撈取。公開聊天可過濾 `Rank` >= 正常值（軟刪除標記）。
- **Community_Groups**：前台列表預設只取 `Enabled = 1`；後台可查全部。可依 `GType` 或 `Owner` 進一步過濾。
- **GameUsers_Wallet**：僅接受 `AuthKey` 精確查詢，**不支援批量 IN 或模糊**，亦不可列出多用戶餘額。
- **GameUsers_Wallet_Transactions**：必須帶 `AuthKey` 且指定 `TDate` 或 `AddTime` 範圍；禁止全表掃描。前台僅能查詢本人交易。
- **Notification_Messages**：前台查詢須過濾 `Enabled = 1`；後台可查所有。不可回傳未啟用的通知。
- **notification_sitemails**：查詢必須過濾 `Receiver`（或 `Sender`）為當前用戶；後台可跨用戶查詢。

### 不可回傳欄位

- **GameUsers_Wallet.AuthKey**：絕對禁止洩漏至任何前端 API。
- **ChatRoomHistories_Backup.Account**：公開聊天歷史查詢時必須遮蔽真實帳號，僅回傳 `UserName` 顯示。
- **GameUsers_Wallet_Transactions.TypeInfo**：JSON 內含關聯帳號、投注詳情等敏感資訊，前台 API 不可完整回傳；若需顯示摘要，僅取必要欄位（如金額、時間）。
- **Notification_Messages.TID / ID**：對外不應曝露內部模板或訊息 ID（防止推播資訊外洩）。
- **notification_sitemails.Content**：信件列表 API 不顯示完整內文，僅單封查詢時允許回傳。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| PostgreSQL games 資料庫（public schema，aimerge_* 表） | writer（合併歷程、預測結果、人工標記、運行設定）/ reader（查詢合併對照、模型訓練標籤、回測報告） | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- **aimerge_match_predictions**
  - `prediction_id`：系統生成唯一預測 ID，禁止手動設定。
  - `game_type`, `gdate`, `source_b`, `game_a_sitegid`, `source_b_sitegid`：建立時由合併請求提供，寫入後不可變更。
  - `score`, `score_detail`：由 AI 模型計算，不允許手動修改；`score_detail` 為權重明細，僅供後台參考。
  - `status`：初始一律為 `pending`；可經審核流程轉為 `confirmed` 或 `rejected`，轉換後不可反向。
  - `inferred_via`：自動推斷方式記錄，禁止手動覆蓋。
  - `predicted_at`：自動寫入預測產生時間。
  - `reviewed_at`, `reviewed_by`：審核時設定，未審核前為空。

- **aimerge_source_mapping**
  - 此表記錄經確認的合併對應，寫入時須確保 `(game_type, gdate, game_a_sitegid, source_b, source_b_sitegid)` 組合唯一。
  - `confirmed_at`, `confirmed_by`：確認時間與操作者，由合併確認 API 寫入。
  - `prediction_id`：必須關聯至有效的 `aimerge_match_predictions.prediction_id`。
  - 不允許直接刪除已確認的映射；若需撤銷，須透過管理後台覆蓋標記。

- **aimerge_label_overrides**
  - 基於 `prediction_id` 的人工介入記錄，不可重複插入同一預測的多筆覆蓋（每個預測最多一筆記錄）。
  - `override_label`：`true` 表示強制視為正確，`false` 表示強制視為錯誤；設定後不可再透過正常審核流程更改。
  - `excluded_from_training`：決定該樣本是否納入模型訓練；由審核者決定，不可由非授權者更改。
  - `reason`、`reviewed_by`、`reviewed_at`：必須填寫原因、審核人及時間。
  - 一旦存在覆蓋記錄，對應 `aimerge_match_predictions.status` 應同步更新為 `confirmed` 或 `rejected`。

- **aimerge_team_aliases**
  - `(game_type, source_id, alias_text, language)` 應唯一；別名只能用來映射至標準隊伍，不可取代原始 team ID。
  - `canonical_team_id`：必須參照有效的 teams 主鍵，不允許指向不存在的隊伍。
  - `confidence`：由 AI 估算或人工標記，範圍 0.0~1.0；寫入時須校驗範圍。
  - 僅後台管理 API 可新增或修改別名；前台只讀。

- **aimerge_runtime_config**
  - 採版本管理，`version_id` 為 UUID，新增配置時 `is_active` 預設為 `true`，舊版本應手動停用。
  - 不允許直接修改已生效 (`is_active = true`) 的 `params`；變更時須先停用舊版，並建立新版本。
  - `effective_from`：指定生效時間，不可設為過去的時間。
  - `updated_by`、`updated_at`、`change_reason` 記錄變更歷史，必須填寫。
  - `parent_version_id` 用於版本鍵結，刪除版本時須確保無子版本參照。

- **aimerge_backtest_runs / aimerge_daily_reports / aimerge_historical_runs**
  - 這些表由內部排程或合併流程自動寫入，**禁止任何 AP I或外部系統手動 INSERT 或 UPDATE**。
  - 特別注意：`aimerge_daily_reports` 每日僅應產生一筆記錄（per `game_type`），重複執行時應覆蓋或跳過，避免多筆日報。

### 讀取規則

- **aimerge_match_predictions**：查詢必須帶 `game_type` 與 `gdate`，可選 `source_b` 或 `status`；禁止跨類型全表掃描。前台僅可查詢自身相關遊戲的預測狀態，後台可查所有。
- **aimerge_source_mapping**：以 `game_type`、`gdate`、`game_a_sitegid` 為主查詢條件，用於確認合併結果，不開放給一般使用者。
- **aimerge_label_overrides**：按 `prediction_id` 或組合條件查詢，僅管理後台使用。
- **aimerge_team_aliases**：查詢須提供 `game_type`，可加 `source_id` 過濾；前臺呼叫時，回應不應包含 `confidence` 細節。
- **aimerge_runtime_config**：後台取用時以 `scope` 及 `is_active = true` 取得當前設定；歷史版本按 `version_id` 查詢。
- **報告類表**：查詢必須限定 `game_type` 與時間範圍（`backtest_date` / `report_date` / `target_date`），禁止無範圍掃描；非管理人員不可直接存取。

### 不可回傳欄位

- **aimerge_match_predictions.score_detail**：內部權重細節，禁止洩漏給非管理人員。
- **aimerge_label_overrides.reason**：可能包含審核者的主觀評語，對外不可見。
- **aimerge_runtime_config.params**：模型參數與閾值，對所有前端 API 隱藏。
- **報告類表的 `samples` 欄位（improved_samples, regression_samples）**：列出特定樣本 ID，間接暴露內部關聯，禁止回傳。
- **aimerge_backtest_runs / aimerge_historical_runs 的 `error_message`**：內部錯誤堆疊，不可對外。

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra predict keyspace（activities_cycles, activities_record, activities_winneraccounts, betpool_bets, betpool_games, calculatelog, killeraccounts_BK） | reader（合併站台查詢預測活動、排行榜、投注資訊；本服務無寫入權限） | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

本服務對 predict keyspace 內所有表不具備寫入權限，以下約束僅供資料維護參考，實際寫入由預測活動服務 (prediction-service) 與投注池服務 (betpool-service) 負責：

- **activities_cycles**：`site` 與 `activityevent` 組合主鍵，建立後不可修改。`startdate`、`enddate`、`starttime`、`endtime` 及 `resultcount` 僅由活動管理服務設定，任何前端 API 禁止直接調整。
- **activities_record**：`site`、`eventname`、`account` 為組合主鍵，`restday`、`winbets`、`updatedate` 僅由活動參加邏輯更新，不可手動篡改。
- **activities_winneraccounts**：`site`、`activityevent`、`cid`、`account` 組合鍵；`predictcount`、`profitpoint`、`rank`、`winpercentage` 由結算服務寫入，不允許外部直接修改或僞造排名。
- **betpool_bets**：`gid` 為分割鍵，投注內容（`betoption`, `betzcoin`, `winlose`, `profitzcoin`）僅投注服務可寫，禁止任何應用層直接 INSERT 或 UPDATE。
- **betpool_games**：`id` 主鍵，遊戲定義（`betoptions`, `names`, `starttime`, `endtime`, `status`, `winresult`, `payout` 等）由投注池管理服務設定，必須遵守狀態機，尤其 `payout` 僅在最終結算後變為 true。
- **calculatelog**：`weekid` 分割鍵，`done` 旗標由週結算任務更改，其他欄位（`addtime`, `weekdate`）僅供參考；不可直接以 SQL 手動插值。
- **killeraccounts_BK**：備份表，僅內部批次作業讀寫，不應讓任何線上 API 觸及。

### 讀取規則

- **activities_cycles**：查詢強制包含分割鍵 `site`；可選 `activityevent` 和 `cid` 過濾。無 `site` 的全表掃描一律禁止。前台僅需回傳當前活動週期（根據時間篩選），後台可撈取歷史。
- **activities_record**：必須提供 `site` 與 `eventname`，並以 `account` 精確查詢；使用者只能讀取自己的記錄。不允許跨帳號批次查詢。
- **activities_winneraccounts**：必須包含 `site` 與 `activityevent`；對外排行榜查詢應限制回傳前 N 名，並可依 `cid` 過濾不同週期。禁止無 partition key 的查詢。
- **betpool_bets**：必須以 `gid`（遊戲 ID）作為 partition key，可選 `account` 或 `id` 進一步限縮；使用者僅能查詢自身投注明細，管理後台可查全部，但仍需 `gid` 條件。
- **betpool_games**：一律以 `id` 精確查詢，不支援批次或範圍查詢；前台應只存取有效遊戲（依 `status` 過濾非結束或非隱藏）。
- **calculatelog**：必須指定 `weekid` 作為分割鍵，可依 `weekdate` 範圍查詢；僅內部排程或管理後台使用，不對外開放。
- **killeraccounts_BK**：查詢須帶 `lid`（分割鍵），並可指定 `cid`、`account`；純內部使用，不對任何前端 API 暴露。

### 不可回傳欄位

- **activities_record.winbets**：包含內部投注編號清單，前台 API 不應完整回傳；若需展示，應只提供統計摘要（如勝場數）。
- **betpool_bets.winlose**：用戶可查看自己的輸贏代碼，但後台查詢時不應將他人詳細結果洩漏給無權限者；對外列表應遮蔽其他用戶的 `winlose`。
- **betpool_games.winresult**：在遊戲未結束（`status` 非最終且 `payout=false`）時嚴禁回傳，防止提前洩漏中獎選項。
- **calculatelog.done**：結算內部旗標，不可對外暴露。
- **killeraccounts_BK 全部欄位**：因包含敏感玩家平均賠率，僅限內部風控或管理使用，任何對外 API 均不得回傳。
- **各表 account 欄位隱私處理**：對外排行榜或公開頁面中，`account` 應依業務政策進行遮蔽（如顯示 `usr***@example`），除非使用者查看自己資訊。

---

## Redis

（本服務未使用 Redis，故略）

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 遊戲幣充值 / 提現 | wallet-service | MergeSite 不處理錢包增減，僅負責讀取顯示餘額 |
| 賽事資料爬取與更新 | data-feed-service | bk_siteplayers 資料由外部同步，非本服務即時寫入 |
| 聊天訊息即時推送 | chat-websocket | 聊天歷史僅儲存，即時推送由其他服務負責 |
| 通知發送時機控制 | notification-dispatcher | notification_messages 僅做內容存放，發送排程由 dedicated service 管理 |
| 站內信發送行為 | mail-sender | notification_sitemails 僅儲存，實際寄送由其他服務處理 |
| 錢包交易處理 | wallet-service | GameUsers_Wallet_Transactions 由交易服務寫入，本服務僅讀取 |
| 預測活動週期建立與管理 | prediction-service | activities_cycles 等活動定義由專屬服務維護 |
| 投注池遊戲建立與派彩 | betpool-service | betpool_games 與 betpool_bets 的開獎、結算由投注池服務負責 |
| 排行榜結算與生成 | prediction-service / batch-job | activities_winneraccounts 排名由結算批次產生，非即時計算 |
| AI 模型訓練與預測推斷 | ai-merge-engine | 合併預測分數計算、隊名別名學習由獨立 AI 服務負責，本服務僅儲存結果 |

---

## 常見錯誤

- ❌ 在聊天歷史查詢中未按 `GID` 分區，導致全表掃描效能問題 → ✅ 強制要求查詢條件包含 `GID` 並加上時間範圍限制
- ❌ 直接回傳 `gameusers_wallet.AuthKey` 給前端 → ✅ 使用 DTO 只回傳 `Balance` 與 `LastUpdateTime`
- ❌ 寫入 `chatroomhistories.Message` 時未檢查長度，導致隱含截斷 → ✅ 應在 API 層驗證字串長度並拒絕超長請求
- ❌ 群組列表查詢時未過濾 `Enabled=1`，回傳已停用群組 → ✅ 預設只顯示啟用群組，管理後台可額外顯示全部
- ❌ 混用 `bk_siteplayers` 與 `community_groups` 的 `ID` 欄位（名稱衝突） → ✅ 在 SQL 中使用別名區分，確保邏輯正確
- ❌ 嘗試直接 INSERT 或 UPDATE `GameUsers_Wallet_Transactions` → ✅ 所有交易寫入都必須透過錢包服務 API，確保一致性與安全
- ❌ 查詢 `activities_winneraccounts` 時未帶 `site`，造成跨站掃描 → ✅ 必須強制帶入分割鍵 `site`，並可搭配 `activityevent` 限縮
- ❌ 在遊戲尚未結束時回傳 `betpool_games.winresult`，提前暴露中獎結果 → ✅ 應檢查 `payout` 狀態，僅在已派彩後才可回傳
- ❌ 對外排行榜直接回傳完整 `account`，違反隱私規範 → ✅ 應以部分遮蔽或用戶暱稱取代，確保匿名性
- ❌ 手動修改 `aimerge_match_predictions.score` 或 `score_detail` → ✅ 分數僅應由 AI 服務產生，若需修正應透過覆蓋機制或重新預測
- ❌ 在 `aimerge_runtime_config` 中直接修改 `params` 而不建立新版本 → ✅ 一律停用舊版並新增版本，變更原因必須記錄
- ❌ 未帶分割鍵查詢 `aimerge_match_predictions` 或 `aimerge_source_mapping` → ✅ 強制帶入 `game_type` 與日期條件，杜絕全表掃描