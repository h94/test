# gameliveservice — DB 操作邊界

> 產出時間：2025-06-14 10:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## sport

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra sport | writer / reader | Schema：[db/sport.md](../../db/sport.md) · 語意：[db/sport-detail.md](../../db/sport-detail.md) |

> **主要表格**：`bk_siteplayers`（站點球員資訊）、`predictdailyeport`（預測每日報表）、`chatroomhistories_backup`（聊天室備份）、`community_groups`（社群群組）、`gameusers_wallet`（錢包）、`gameusers_wallet_transactions`（錢包交易）、`notification_messages`（通知訊息）。

### 寫入限制

- **`bk_siteplayers.Site`、`bk_siteplayers.SiteID`、`bk_siteplayers.Year`**：複合主鍵，建立後不可修改；由資料同步服務（如 `GameDataSyncService`）寫入，本服務僅讀取
- **`bk_siteplayers.Name`、`bk_siteplayers.TeamID`、`bk_siteplayers.Team`**：球員與隊伍資訊，僅可由管理後台 API 更新，避免直接修改影響前端顯示
- **`bk_siteplayers.Record`**：比賽記錄（JSON 或文本），僅在賽程結束後由同步服務寫入，不可手動修改
- **`predictdailyeport.Reportdate`**：複合主鍵（搭配 `Gametype`），建立後不可修改；由排程服務每日定時寫入
- **`predictdailyeport.Gametype`**：複合主鍵，建立後不可修改；由排程服務按遊戲類型寫入
- **`chatroomhistories_backup`**：所有欄位由 Community 服務或資料同步流程寫入；本服務為讀取方，不可直接 INSERT / UPDATE / DELETE
- **`community_groups`**：整表由 Community 服務維護；本服務不可直接寫入任何欄位，避免雙寫不一致或權限繞過
- **`gameusers_wallet.AuthKey`**：錢包唯一認證鍵，建立後不可變更；本服務不可修改
- **`gameusers_wallet.Balance`**：僅能透過 `gameusers_wallet_transactions` 的原子操作調整；任何直接 UPDATE 都會破壞帳務一致性，本服務嚴禁執行
- **`gameusers_wallet_transactions`**：每一筆交易由 Wallet 服務依業務邏輯新增；本服務不可插入或刪除記錄，否則會造成對帳錯誤
- **`notification_messages`**：所有欄位（`TID`, `ID`, `Enabled`, 各語言內容等）由通知管理服務或後台寫入；本服務僅讀取，不可修改

### 讀取規則

- **球員列表查詢**：查 `bk_siteplayers` 時須帶 `Site`、`SiteID`、`Year` 作為過濾條件（避免跨站點／跨賽季全表掃描）；若需查詢特定聯賽，應加 `League` 過濾
- **預測報表查詢**：查 `predictdailyeport` 時須帶 `Reportdate`（日期）或 `Gametype` 作為 partition key，不可全表掃描；通常以日期範圍查詢
- **球員展示**：前端頁面展示球員時，只回傳 `Site`、`Year`、`League`、`Name`、`Team`、`Record` 與 `LastUpdateTime`，不應回傳 `SiteID`（僅內部用）
- **聯盟/球隊/球員查詢**：若 `Site`、`SiteID`、`Year` 任一不存在（例如資料未同步完成時），應回傳空列表而非報錯
- **聊天室備份**：僅用於資料回溯或審計。查詢時必須帶 `GID` 作為 partition key，並可搭配 `AddTime` 時間範圍；不應在一般線上業務使用
- **社群群組**：本服務若需讀取（如透過直播頻道關聯群組資訊），應遵循 Community DB 規則：前台只查 `Enabled=1`，以 `ID` 為主要過濾條件，避免全表掃描
- **錢包餘額**：查詢 `gameusers_wallet` 必須指定 `AuthKey`，不可全表掃描；若有餘額顯示需求，應進行點查或少量查詢，並在業務層處理同步延遲
- **錢包交易記錄**：查詢 `gameusers_wallet_transactions` 必須以 `AuthKey` 為過濾條件，可輔以 `TDate` 或 `AddTime` 範圍；不可僅依 `Type` 或 `TypeInfo` 內容進行搜索
- **通知訊息**：查詢 `notification_messages` 通常使用 `TID` + `ID` 精確查找，或依 `Enabled=1` 過濾啟用中的通知；大量列表查詢時應確保有索引

### 不可回傳欄位

- **`bk_siteplayers.SiteID`**：對外 API 不可回傳，僅內部用於關聯球隊識別
- **`bk_siteplayers.TeamID`**：對外 API 不可回傳，僅內部用於資料關聯
- **`gameusers_wallet.AuthKey`**：用戶認證金鑰，任何對外 API 不得直接回傳
- **`gameusers_wallet.Balance`**：財務敏感欄位，僅允許在本人身份驗證後回傳；通用 API 不可暴露
- **`gameusers_wallet_transactions.AuthKey`**：同錢包，不可回傳
- **`gameusers_wallet_transactions.TypeInfo`**：JSON 內容可能包含帳號、遊戲識別等隱私資訊，對外回傳時須移除或脫敏內部欄位（如 Account）
- **`community_groups.Name`**（多語言 JSON）與 `notification_messages` 的語言欄位：回傳時建議在 DTO 層依請求語言提取對應文字，避免傳輸完整多語言結構

---

## community

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra community | writer | Schema：[db/community.md](../../db/community.md) · 語意：[db/community-detail.md](../../db/community-detail.md) |

> **主要表格**：`Community_Groups`（社群群組）、`ChatRoomHistories`（聊天室訊息）、`ChatRoomHistories_Backup`（訊息備份）、`newlottery_forums`（論壇）。

### 寫入限制

- **`Community_Groups.ID`**：建立後不可修改，由 `CreateCommunityGroup` API 一次寫入
- **`Community_Groups.Owner`**：創建時設定，不可變更；群組轉移需由管理後台專用 API 處理
- **`Community_Groups.GType`**：類別（`official`/`normal`/`vip`/`personal`/`test`），創建後不可變更
- **`Community_Groups.Enabled`**：僅管理員可切換（0 停用 / 1 啟用）；一般使用者不得直接修改
- **`Community_Groups.Name`、`Community_Groups.Description`、`Community_Groups.IconPath`**：可由群組擁有者或管理員修改；Name 為多語言 JSON，更新時需保持各語系完整性
- **`Community_Groups.Seq`**：排序序號，僅後台管理員可調整
- **`Community_Groups.UpdateTime`**：每次更新時自動設為當前時間戳（毫秒），不可手動設定

- **`ChatRoomHistories.ID`**：訊息唯一識別碼，建立後不可修改；由 `CreateGroupChatRoomMessages` 產生
- **`ChatRoomHistories.Message`**：發送後不可直接 UPDATE，除非有明確編輯功能
- **`ChatRoomHistories.LikeAccount`**：可由點讚 / 取消點讚 API 更新（整個 JSON 陣列替換）；其他欄位不可變更
- **`ChatRoomHistories.Account`、`Rank`、`UserName`、`HeadShotPath`**：寫入後原則上不變，因歷史訊息不應追隨使用者當前資料

- **`ChatRoomHistories_Backup`**：備份表，僅供資料同步或歸檔流程寫入，本服務不直接操作

- **`newlottery_forums.id`**：建立後不可修改；由論壇建立 API 一次寫入
- **`newlottery_forums.names`**：多語言名稱（`map<text,text>`），更新時須維護所有已使用語系的對應，不可出現空值
- **`newlottery_forums.status`**：僅允許 0（停用）或 1（啟用）；由管理後台控制，本服務不可越權修改
- **`newlottery_forums.edit_timestamp`**：每次欄位更新時需同步更新為當前時間戳（毫秒）

### 讀取規則

- **群組列表**：查詢 `Community_Groups` 時，前台僅回傳 `Enabled=1` 的群組；後台可查全部
- **聊天記錄**：查詢 `ChatRoomHistories` 必須帶 `GID` 作為 partition key，並依 `AddTime` 排序，不可全表掃描
- **訊息多媒體解析**：若 `Message` 為 JSON 格式（如預測），應在業務層正確解析，避免直接暴露原始結構
- **論壇列表（前台）**：只回傳 `status=1` 的記錄；停用論壇僅管理後台查詢
- **多語言回傳**：查詢 `newlottery_forums.names` 或 `Community_Groups.Name` 時，應依請求語言偏好選擇對應語系的值；若缺失則回退至預設語言（如 `en`）
- **排序**：論壇無內建排序欄位，必要時可使用 `edit_timestamp` 降序；群組列表可按 `Seq` 升序

### 不可回傳欄位

- 無高度敏感欄位，但為減少傳輸量，`Community_Groups.Name`（多語言 JSON）與 `newlottery_forums.names` 建議在 DTO 轉換為單一語言字串後回傳，而非完整 map

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| PostgreSQL Games | reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |

> **主要表格**：`games_bk`、`games_bm`、`games_bs`、`games_ck`（各遊戲類型賽程表，結構相同）。

### 寫入限制

- 所有 `games_*` 表由「遊戲數據同步服務」寫入，本服務為唯讀，**不可直接 INSERT / UPDATE / DELETE**
- `id`、`lid`、`gdate`、`gtime`、`team_h`、`team_a` 等比賽基本資訊：同步寫入後不可修改（除更正外由同步服務更新）
- `match_h`、`match_a`、`match_detail`、`resultinfo` 等賽果欄位：僅在比賽結束後由同步服務寫入
- `status`：由同步服務更新，本服務不變更（如 `PreGame` → `InPlay` → `Final`）
- `create_at`：記錄建立時間，由同步服務自動寫入

### 讀取規則

- **直播頻道相關查詢**：查詢 `games_*` 時需帶 `gdate` 與 `gametype`（透過對應表名區分，如 `games_bk` 代表籃球）作為過濾條件；僅查詢 `gdate` >= 今日且 `status` 不為取消/延遲的比賽（如需顯示特定狀態由業務層過濾）
- **聯賽過濾**：若前端指定聯賽，應以 `lid` 為篩選，避免跨聯賽全表掃描
- **時間排序**：多按 `gdate` + `gtime` 升序排列
- **前端展示**：一般直播列表只回傳 `id`、`gdate`、`gtime`、`team_h`、`team_a`、`status` 等必要欄位；避免一次載入大量 JSON 欄位（如 `teams`、`match_detail`）
- **賽事詳細**：僅在需要詳細資訊時（如後台）才回傳 `teams`、`siteidmaps`、`match_detail`、`resultinfo`

### 不可回傳欄位

- **`teamid_h`、`teamid_a`**：內部 ID，對外 API 不可暴露（前端僅用隊伍名稱）
- **`siteidmaps`**：站台內部映射資料，不可回傳至前端
- **`match_detail`、`resultinfo`、`otherinfo`**：除非為特定內部 API，否則不應在一般直播介面中回傳（資料量大且非必要）

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra predict | writer | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

> **主要表格**：`betpool_games`（投注遊戲）、`betpool_bets`（投注記錄）、`activities_cycles`（活動週期）、`activities_record`（活動參與記錄）、`activities_winneraccounts`（活動排名）、`calculatelog`（結算日誌）、`killeraccounts_BK`（殺手帳戶記錄）。

### 寫入限制

- **`betpool_games.id`**：創建後不可修改，由管理後台定義
- **`betpool_games.winresult`**：僅在遊戲結束（`status=2`）且 `payout=false` 時由派彩流程寫入；不可直接 UPDATE
- **`betpool_games.payout`**：僅派彩完成後由 `false` → `true`，寫入後不可再修改 `winresult` 或相關獲利資料
- **`betpool_games.status`**：僅允許正向變更（0 → 1 → 2），不可跳躍或回退
- **`betpool_games.zcoinprice`、`viponly`、`hot`、`feedrate`、`betoptions`、`names`**：創建時設定；`hot` 可由管理後台動態調整，其餘僅管理後台可修改
- **`betpool_bets.account`、`betpool_bets.gid`、`betpool_bets.id`**：建立後不可修改，由投注流程一次寫入
- **`betpool_bets.profitzcoin`、`betpool_bets.winlose`**：僅在遊戲結算時由派彩流程寫入
- **`activities_cycles.site`、`activityevent`、`cid`**：複合主鍵，由活動管理後台或排程創建；`startdate`、`enddate`、`starttime`、`endtime` 設定後不可人工修改，以免影響活動一致性
- **`activities_cycles.resultcount`**：由結算服務更新，本服務不可手動寫入
- **`activities_record.site`、`eventname`、`account`**：複合主鍵，建立後不可變更；`restday`、`updatedate`、`winbets` 由活動參與邏輯更新，`winbets` 僅可追加
- **`activities_winneraccounts`**：整表由活動排名結算服務寫入，本服務僅讀取；任何欄位（`predictcount`、`profitpoint`、`rank`、`winpercentage`）本服務不可直接修改
- **`calculatelog.weekid`、`weekdate`**：由結算排程寫入，建立後不可修改；`done` 僅允許從 0 → 1，表示該週結算完成
- **`killeraccounts_BK.lid`、`cid`、`account`**：複合主鍵，由殺手帳戶管理排程寫入，建立後不可修改；`addtime`、`avgodd` 同樣由排程設定，本服務唯讀

### 讀取規則

- **活動排名查詢**：查詢 `activities_winneraccounts` 時須帶 `site`、`activityevent`、`cid`（完整 partition key），避免跨活動全掃
- **投注記錄查詢**：查詢 `betpool_bets` 時須帶 `gid` 或 `account`（視場景），不可全表掃描
- **遊戲列表**：查詢 `betpool_games` 時前台只回傳 `status=1`（進行中）或 `status=0`（未開始）；已 `payout=true` 之遊戲不回傳至前台參與區
- **活動週期**：查詢 `activities_cycles` 時須檢查 `startdate` ≤ 當前日期 ≤ `enddate`，僅回傳有效週期；必要時過濾 `resultcount > 0`
- **活動參與記錄**：查詢 `activities_record` 須帶 `site` + `eventname`，可附加 `account` 做單一用戶查詢
- **結算日誌**：結算服務應先查 `calculatelog`，確認 `done` 狀態避免重複結算；查詢時帶 `weekid` 或 `weekdate`
- **殺手帳戶**：查詢 `killeraccounts_BK` 必須帶 `lid` 或 `lid` + `cid`，不可跨聯賽全表掃描；列表查詢可依 `cid` 篩選並排序

### 不可回傳欄位

- **`betpool_bets.account`**：非本人 API 不可回傳（隱私敏感）；社群排行榜需脫敏
- **`betpool_bets.profitzcoin`、`betpool_bets.betzcoin`**：非本人 API 不可回傳（財務敏感）
- **`betpool_games.feedrate`**：僅內部管理後台可見，前端不可暴露
- **`activities_winneraccounts.account`**：排行榜回傳時須脫敏（如僅顯示部分帳號）
- **`activities_record.account`**：非本人不得直接取得完整帳號
- **`calculatelog`**：內部結算邏輯表，不對外開放
- **`killeraccounts_BK.account`**：殺手帳戶名單具隱私性，對外回傳需遮蔽或限制權限
- **`killeraccounts_BK.avgodd`**：賠率資訊僅供內部參考，避免對外直接回傳

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter | reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

> **說明**：`pricecenter` 主要存放遊戲直播頻道（`gamelive`）、賽程（`games_{gameType}`、`leagues_{gameType}`、`teams_{gameType}`）以及各站台玩家帳號（`accounts_*`）。本服務僅讀取遊戲相關與帳號資料，帳號寫入由外部帳號服務處理；直播頻道資料由管理後台寫入，本服務僅讀取。

### 寫入限制

- **`gamelive`**：頻道資料（`channelid`、`url`、`date`、`gametype`、`league`、`team_H`、`team_A`、`gtime` 等）由管理後台透過外部 API 寫入，本服務不直接寫入此表。
- **`accounts_*`**：`password`、`phone`、`handler` 等敏感欄位僅由帳號管理服務寫入；本服務不可寫入 `password`（僅用於驗證比對）。其餘欄位如 `enabled`、`closetime` 等亦由帳號服務維護，本服務唯讀。
- **`games_{gameType}.id`、`leagues_{gameType}.id`、`teams_{gameType}.id`**：主鍵由資料同步服務寫入，本服務為只讀。所有 `games_*`、`leagues_*`、`teams_*` 表中的欄位均不可由本服務直接修改。

### 讀取規則

- **直播頻道列表**：查 `gamelive` 時預設只回傳 `enabled=1` 且 `date` 為當前或未來日期的記錄（避免顯示已下線或過期頻道）。可依 `gametype` 或 `league` 過濾。
- **玩家帳號驗證**：登入 / 連線 Hub 時需查 `accounts_*` 並檢查 `enabled=1`；`enabled=0` 或 `closetime` 不為空且 `closetime` 時間早於當前時間的帳號視為已關閉，拒絕服務。
- **賽程查詢**：查 `games_{gameType}` 時須帶 `gdate` 與 `lid` 作為過濾條件（避免跨聯賽全表掃描）。若需查詢特定比賽，應同時指定 `id`。
- **球隊 / 聯賽查詢**：查 `leagues_{gameType}` 或 `teams_{gameType}` 時，應以 `id` 或 `lid` 為過濾（`teams` 可用 `lid` 查找同聯賽所有球隊）。前端展示時，`leagues_*` 僅需 `id`、`lname`；`teams_*` 僅需 `id`、`tname`、`lid`。
- **排序**：`gamelive` 可按 `gtime` 或 `date` 排序；`games_{gameType}` 一般按 `gdate`、`gtime` 升序。

### 不可回傳欄位

- **`accounts_*.password`**：任何 API 皆不可回傳（資安敏感）。
- **`accounts_*.phone`**：對外 API 不可回傳（個資敏感；僅可用於內部驗證）。
- **`accounts_*.handler`**：內部 metadata 不可暴露至前端。
- **`accounts_*.closetime`**：不建議回傳，避免暴露帳號關閉資訊。
- **`gamelive`** 中的 `url` 若為內部串流位址，亦建議避免直接暴露。
- **`games_{gameType}`** 無特殊敏感欄位，但應避免回傳 `lid` 以外的內部映射資料（如有）。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET | `predict:activity:{site}:{eventname}:{cid}:leaderboard` | 活動排名載入時 | 60s；活動期間頻繁更新排名 |
| GET | `predict:game:{gid}:status` | API / Hub 查詢遊戲狀態 | 30s；減少對 Cassandra 讀取 |
| DEL | `predict:game:{gid}:status` | 遊戲狀態變更通知（status/winresult 更新）時 | 主動刪除，下次查詢回源 |
| SET | `predict:bet:{gid}:{account}:like` | 用戶對注單點讚時 | 永久（作為 like 記錄）；TTL=0 表示不自動過期 |
| GET | `predict:bet:{gid}:{account}:like` | 查詢用戶是否已點讚 | 無 TTL 自動失效，僅主動 DEL |
| DEL | `predict:bet:{gid}:{account}:like` | 取消點讚時 | 避免重複點讚 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 活動結果計算與排名結算 | ActivitySettlementService (或其他排程服務) | 本服務僅記錄預測行為與排名展示；最終獲獎計算由外部排程寫入 `activities_winneraccounts` |
| 遊戲數據同步（賽程、比分） | GameDataSyncService | `betpool_games` 的 `winresult`、`status` 更新由外部或管理後台寫入；本服務為消費端 |
| 用戶積分（ZCoin）結算 | WalletService | 本服務僅記錄 `profitzcoin`；實際扣款／發放由錢包服務處理 |
| 操作日誌（actionlog）寫入 | pricecenter 服務 | `actionlog` 表記錄價格中心操作；gameliveservice 不負責寫入或讀取該表 |

---

## 常見錯誤

- ❌ 直接修改 `betpool_games.winresult` 或 `betpool_games.payout` 未檢查 `status` → ✅ 應先確認遊戲狀態 `status=2`（已結束），且 `payout=false` 才可派彩
- ❌ 查詢 `activities_winneraccounts` 時未加 `site` / `activityevent` / `cid` 過濾 → ✅ 必須帶齊 partition key，否則導致全表掃描 timeout
- ❌ 前端取得未結算遊戲狀態直接顯示 `winresult` → ✅ 前端不應顯示 `winresult`；應由本服務過濾僅回傳 `payout=true` 之結果
- ❌ 活動週期查詢未檢查日期邊界，回傳已過期活動 → ✅ 須過濾 `startdate ≤ today ≤ enddate`，且僅回傳有效週期
- ❌ 查詢 `bk_siteplayers` 時未加 `Site` / `SiteID` / `Year` 條件 → ✅ 必須帶齊複合主鍵，否則導致全表掃描 timeout 或回傳過大資料集
- ❌ 誤將 `predictdailyeport` 中的 `Gametype` 當過濾條件時未加 `Reportdate` → ✅ 必須同時指定 `Reportdate` 和 `Gametype`，不可僅用後者查詢
- ❌ 球員資料中 `SiteID` 直接回傳至前端 → ✅ 前端僅需 `Site`、`Year`、`League`、`Name`、`Team`、`Record`，`SiteID` 及 `TeamID` 應在 DTO 層移除
- ❌ 查詢 `bk_siteplayers` 時對 `League` 或 `Team` 欄位使用 LIKE 前綴搜尋未做長度限制 → ✅ 若需模糊查詢，應限制輸入長度（`varchar(25)` 及 `varchar(5)`）並先以 `Site`、`Year` 縮小範圍
- ❌ 後台查詢 `killeraccounts_BK` 未指定 `lid`，造成跨聯賽全表掃描 → ✅ 需傳入 `lid`，可輔以 `cid` 縮小範圍