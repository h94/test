# predictservice — DB 操作邊界

> 產出時間：2025-12-12 10:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra predict keyspace | owner | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **betpool_games**：
  - `status`、`payout`、`winresult` 僅由內部結算排程寫入，不可由外部 API 直接修改
  - `starttime`、`endtime` 僅在遊戲建立時寫入，不可事後延長或縮短
  - `viponly`、`hot` 僅由後台管理 API 設定
- **betpool_bets**：
  - `betzcoin`、`betoption` 僅於下注時寫入，不可修改
  - `profitzcoin`、`winlose` 僅由結算程序回填，外部不可直接更新（`winlose` 取值 `W`/`L`/`C`）
  - `id`（投注單號）在下注時生成，不可事後修改
- **activities_cycles**：
  - `startdate`、`starttime`、`enddate`、`endtime` 僅於週期建立時寫入，不可事後修改
  - `resultcount` 僅由結算完成後寫入
  - `activityevent` 與 `site` 構成複合主鍵，新增週期時必須一併指定
- **activities_record**：
  - `restday`、`winbets`、`updatedate` 僅由活動處理邏輯（如連勝活動結算）寫入，不可人工修改
  - `winbets` 為序列化投注紀錄列表，不可透過 API 直接寫入
- **activities_winneraccounts**：
  - `predictcount`、`profitpoint`、`rank`、`winpercentage` 僅由結算排程依演算法計算寫入，不可人工調整
- **calculatelog**：
  - `done`、`addtime` 僅由內部計算任務（如 ReportService）寫入
  - `weekid` 為分區鍵，新增時必須指定
- **killeraccounts_{gameType}**（例：`killeraccounts_BK`）：
  - `avgodd`、`profitpoint` 等統計資料僅由內部排程計算寫入，不可經由 API 修改
- **strategy_bet_log**：
  - `result` 欄位僅由策略執行模組透過 UPDATE 寫入，外部不可寫入
- **predictfilterreports, predictfilterreports_mainbet**：
  - 統計欄位（`avgwinodd`, `predictcount`, `predictwin`, `profitpoint`, `winlose_detail`, `seq_score`, `seq_score_fix`, `winstreakdays`）僅由內部報表產生排程寫入，不可經由 API 或人工修改。
  - 所有分區鍵與集群鍵（`reportdate`, `gametype`, `lid`, `filtertype`, `startdate`, `enddate`, `account`）在產生時寫入，不可事後變更。
- **predictbets_BK**：
  - `id`, `addtime`, `gid`, `account`, `mode`, `odd`, `point`, `betoption`, `usezcoins`, `args` 等投注相關欄位僅於下注時寫入，不可修改。
  - `profitpoint`, `winloss`, `match_a`, `match_h` 僅由結算程式回填，外部不可直接更新。
  - `status` 由系統結算流程更新，不可手動設定。
  - `strategy_id` 僅由策略模組關聯設定。
- **predictgames_BK_lock_2024**：
  - `unlock_accounts` 與 `unlock_rb_accounts` 僅由內部鎖定/解鎖邏輯寫入，外部 API 不可直接修改。
  - 其餘欄位（`lid`, `gdate`, `account`, `gid`, `gtime`）為遊戲建立時設定，不可變更。
- **settings_league**：
  - `gametype`, `lids`, `classified`, `enabled` 由後台管理服務寫入，predictservice 僅讀取，**無寫入權限**。
- **settings_playmode**：
  - `gametype`, `playmodes` 由後台管理服務寫入，predictservice 僅讀取，**無寫入權限**。
- **settings_killer_cycle_BK**：
  - `lid`, `cid`, `startdate`, `starttime`, `enddate`, `endtime`, `resultcount`, `payout` 由後台設定寫入，predictservice 僅讀取，**無寫入權限**。
- **settings_killer_conditions_BK**：
  - `lid`, `cid`, `mincount`, `minwinpercentage`, `avgodd`, `firstweekmincount`, `secondweekmincount`, `superminwinpercentage`, `minprofits` 由後台設定寫入，predictservice 僅讀取，**無寫入權限**。
- **weeklyreport**：
  - `account`, `weekid`, `reports`, `weekdate` 由報表排程寫入，predictservice 僅讀取，**無寫入權限**。

### 讀取規則

- **betpool_games 查詢**：
  - 排行榜查詢僅回傳 `payout = true` 且 `status = 1` 的已完成遊戲
  - 開放投注列表查詢須過濾 `starttime <= 目前時間 < endtime` 且 `status = 0`
  - 遊戲內容修改（如名稱、選項）僅在 `status = 0` 時允許
- **betpool_bets 查詢**：
  - 查詢個人投注記錄時須依 `account` 過濾，不可跨帳號查詢
  - 查詢特定遊戲總投注時須依 `gid` 過濾
  - 結算查詢需考慮 `winlose` 為 `W`/`L`/`C` 分別處理
- **activities_cycles 查詢**：
  - 取當前活動週期須檢查目前時間落在 `startdate starttime` 至 `enddate endtime` 之間
  - 時間比較時應將 `startdate`+`starttime`、`enddate`+`endtime` 合併為 DateTime 物件再與目前時間比對
- **activities_record 查詢**：
  - 查詢連勝紀錄或活動參與紀錄須依 `site`、`eventname`、`account` 過濾，不可跨帳號查詢
  - 查詢特定活動所有參與者紀錄時，需加上 `site`、`eventname` 條件避免全表掃描
- **activities_winneraccounts 查詢**：
  - 排行榜查詢須依 `site`、`activityevent`、`cid` 過濾，並以 `rank` 排序
- **calculatelog 查詢**：
  - 查詢計算任務須以 `weekid`（分區鍵）為必要條件，可搭配 `weekdate`、`done` 篩選
  - 嚴禁無 `weekid` 的全表掃描
- **killeraccounts_{gameType} 查詢**：
  - 殺手列表查詢須依 `lid`、`cid` 過濾，並按 `profitpoint` 排序
  - 查詢時必須指定對應的 `gameType` 表名（如 `killeraccounts_BK`），不可跨表
- **predictfilterreports 與 predictfilterreports_mainbet**：
  - 報表查詢須依 `reportdate`、`gametype`、`lid`、`filtertype` 過濾，不可全表掃描
- **predictbets_BK 查詢**：
  - 個人投注記錄查詢須以 `account` 及 `lid`、`gdate` 等分區鍵過濾，不可跨帳號讀取。
  - 排行榜查詢應僅取 `status = 1`（已結算）且 `profitpoint` 排序，並隱藏帳號。
- **predictgames_BK_lock_2024 查詢**：
  - 查詢特定遊戲鎖定狀態須提供 `lid`、`gdate`、`gid`、`account`。
- **settings_league 查詢**：
  - 依 `gametype` 過濾，可取 `enabled = 1` 的聯賽列表
- **settings_playmode 查詢**：
  - 依 `gametype` 過濾，取得可用玩法模式
- **settings_killer_cycle_BK 查詢**：
  - 必須以 `lid` 為分區鍵，搭配 `cid` 查詢特定週期
- **settings_killer_conditions_BK 查詢**：
  - 必須以 `lid` 為分區鍵，搭配 `cid` 查詢條件
- **weeklyreport 查詢**：
  - 查詢個人週報須以 `account` 為過濾條件，搭配 `weekid` 或 `weekdate`

### 不可回傳欄位

- **betpool_bets.account**：排行榜 API 不可回傳，避免洩漏其他用戶投注明細
- **betpool_bets.id**：對外排行榜結果不應包含投注單 ID
- **activities_winneraccounts.account**：公開排行榜不可包含帳號，僅顯示 rank 與 profitpoint
- **activities_record.winbets**：內含序列化投注明細，不應對外暴露
- **betpool_games.betoptions**：內部選項映射不應回傳給前端（僅用作後端計算）
- **killeraccounts_{gameType}.account**：殺手榜公開 API 不可回傳帳號，僅回傳統計數據
- **strategy_bet_log.result**：策略內部紀錄不應暴露給外部 API
- **predictfilterreports.account**：公開報表應去除或匿名化帳號欄位，不可直接暴露。
- **predictfilterreports.winlose_detail**：內含個人預測序列，不宜對外暴露。
- **predictbets_BK.account**：排行榜或公開 API 不可回傳。
- **predictbets_BK.args**：可能包含用戶自定義參數，應避免暴露。
- **predictbets_BK.strategy_id**：內部策略編號不應對外。
- **predictgames_BK_lock_2024.unlock_accounts**：內部解鎖帳號映射，不可回傳。
- **predictgames_BK_lock_2024.unlock_rb_accounts**：同上。
- **weeklyreport.reports**：內含個人預測記錄與成績明細，公開 API 不應直接暴露原始映射。
- **settings 系列表**：內部設定資料，不應經由公開 API 回傳（僅供內部使用）。

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member keyspace | reader | Schema：[db/member.md](../../db/member.md) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **本服務對 member keyspace 無寫入權限**，所有會員資料變更由 MemberService 負責

### 讀取規則

- **gameusers 查詢**：
  - 透過 `authkey`（主鍵）查詢單一用戶基本資料（`GetUsersName`、`GetUserName`）
  - 需過濾 `status` 欄位確認帳號未被停用／封鎖
  - `GetAllGameUsers` 全表掃描僅供後台管理使用，需限制呼叫頻率
- **gamesublogs 查詢**：
  - `GetGreaterThanOrEqualTimeVIPSublogs`：查詢特定 `authkey` 且 `subtime >= 指定時間` 的 VIP 訂閱記錄
  - 依據 `subendtime` 判斷 VIP 會員資格是否有效
- **gamerobots 查詢**：
  - `GetRobotAccounts`：僅取 `enabled = 1` 的機器人帳號
- **forbidden_email_domains 查詢**：
  - 註冊／變更 email 時需檢查網域是否在禁止清單
- **gameuserviewsv2 查詢**：
  - 以 `year` 為分區鍵，`datetime` 範圍查詢用戶瀏覽記錄
  - `GetUsersViewByMember`：可額外過濾 `account`、`gtype`、`lid`

### 不可回傳欄位

- **gameusers.password**：任何 API 回傳都不可包含此欄位
- **gameusers.email**：僅在用戶本人查詢或後台管理時可見，公開 API（如排行榜、殺手榜）不可暴露
- **gameusers.authkey**：內部索引鍵，對外 API 不應回傳
- **gameusers_banned 整張表**：封禁資訊不應透過公開 API 查詢

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter keyspace | reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **本服務對 pricecenter keyspace 無寫入權限**，所有帳號資料（如 accounts_AU8、accounts_Fortuna888、accounts_HGA、accounts_HGA2、accounts_KKK、accounts_KU、accounts_NK、accounts_Panda、accounts_TG、accounts_TG999 等表）以及操作日誌（actionlog）均由其他服務負責維護。

### 讀取規則

- **帳號驗證（accounts_{suffix} 系列表）**：
  - 查詢時須以 `account` 為主鍵，僅取 `enabled = 1`（啟用）的記錄；不存在或 `enabled = 0` 時視為無效帳號，應拒絕下注等操作。
  - 必須根據登入站點（如 AU8、Fortuna888、HGA 等）選擇對應的 `accounts_{suffix}` 表，不可跨站查詢。
  - `handler` 欄位為內部處理設定（如客服人員、備註），僅供內部程式使用，不應作為對外 API 的過濾條件或回傳欄位。
- **操作日誌查詢（actionlog）**：
  - `actionlog` 表以 `date` 為分區鍵，查詢時必須指定 `date` 範圍；集群鍵包含 `addtime`、`user`、`gametype`，查詢應至少包含 `date` 與 `user` 等條件，嚴禁全表掃描。
  - `detail` 欄位為 JSON 字串，內含完整操作上下文，僅限後台審計使用，對外 API 須脫敏或過濾掉敏感內容。

### 不可回傳欄位

- **password**：任何 API 回傳均不可包含密碼欄位。
- **phone**：電話號碼為個人隱私，不應暴露給公開 API（如排行榜、他人查詢）。
- **handler**：內部處理器映射，不應對外暴露。
- **actionlog.detail**：操作詳情可能包含帳號、金流等敏感資訊，公開 API 及非審計用途禁止回傳。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| PostgreSQL Games | reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- **本服務對 games 資料庫中所有表均只有讀取權限，無寫入權限**。包括：
  - 比賽資料表：`games_bk`、`games_bm`、`games_bs`、`games_ck` 等。
  - AI 匹配合併相關表：`aimerge_match_predictions`、`aimerge_source_mapping`、`aimerge_label_overrides`、`aimerge_backtest_runs`、`aimerge_daily_reports`、`aimerge_historical_runs`、`aimerge_runtime_config`、`aimerge_team_aliases`。
  所有資料的寫入與維護均由 GameDataService、aimerge 服務或其他上游服務負責。

### 讀取規則

#### 比賽資料表（games_{gameType}）
- 根據 `gameType`（如 `bk`、`bm`、`bs`、`ck`）對應到正確的 `games_{gameType}` 表，不可跨表掃描。
- 篩選進行中或尚未開始的比賽，使用 `status = 'PreGame'` 或類似狀態，並搭配日期時間條件。
- 查詢特定聯賽比賽時，必須加上 `lid` 條件，避免全表掃描。
- `create_at` 欄位為 Unix 毫秒時間戳，用於查詢時間範圍時須注意轉換。
- 查詢特定比賽結果時，應以 `status = 'Final'` 過濾。

#### AI 匹配合併表（aimerge_*）
- **aimerge_match_predictions**：查詢預測匹配結果時，必須指定 `game_type`、`gdate`、`source_b`、`game_a_sitegid`、`source_b_sitegid` 等必要過濾條件；可用於獲取比賽的匹配合併結果供預測分析。
- **aimerge_source_mapping**：查詢來源映射時，需以 `game_type`、`gdate`、`game_a_sitegid` 為條件。
- **aimerge_label_overrides**：查詢人工覆蓋標籤，可根據 `game_type`、`gdate`、`prediction_id` 過濾。
- **aimerge_backtest_runs**：查詢回測運行結果時，需以 `game_type`、`backtest_date` 為條件。
- **aimerge_daily_reports**：查詢每日報告時，需以 `game_type`、`report_date` 為條件。
- **aimerge_historical_runs**：查詢歷史運行狀態，需以 `game_type`、`target_date` 為條件。
- **aimerge_runtime_config**：讀取運行時配置，可過濾 `scope`、`is_active` 等條件。
- **aimerge_team_aliases**：查詢球隊別名時，需以 `game_type`、`source_id`、`alias_text` 等為條件。
- 所有查詢均應加上必要的索引或分區鍵條件，嚴禁全表掃描；時間欄位（如 `predicted_at`）在範圍查詢時應注意時區轉換。

### 不可回傳欄位

- **siteidmaps**：內部跨站點 ID 映射資訊，不應對外暴露。
- **aimerge_match_predictions.score_detail**：內部匹配細節評分，公開 API 不應直接回傳。
- **aimerge_match_predictions.inferred_via**：推斷方式，僅供內部記錄。
- **aimerge_label_overrides.reviewed_by**, **reviewed_at**：審核人資訊，非審計用途不應對外暴露。
- **aimerge_backtest_runs.improved_samples**, **regression_samples**：內含詳細樣本數據，不宜對外。
- **aimerge_runtime_config.params**：配置參數，可能包含敏感閾值，限制對外回傳。
- 所有表內的內部時間戳或稽核欄位（如 `executed_at`, `predicted_at` 等）若無必要，不應直接暴露給前端使用者。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| GET | `EventGameUserCache:{EventName}` | 活動相關查詢（如連勝活動） | 由 `LastCheckTime` 控制快取新鮮度，非固定 TTL |
| GET | `GameUser:{authkey}` | 高頻用戶資料查詢（如會員資格驗證） | 建議 5-10 分鐘，避免 VIP 狀態延遲更新 |

**注意**：
- VIP 會員資格變更由 MemberService 負責清除相關快取
- 用戶基本資料（username, headshotpath）變更時需主動失效快取

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 會員註冊／登入／密碼管理 | MemberService | predictservice 僅讀取會員資料做權限驗證 |
| VIP 訂閱購買／續訂 | MemberService | predictservice 僅查詢 VIP 狀態判斷功能權限 |
| 用戶封禁／解禁 | MemberService | predictservice 讀取 `gameusers.status` 與 `gameusers_banned` 做存取控制 |
| 用戶關注／黑名單管理 | MemberService | predictservice 讀取 `focus_account`/`black_account` 做內容過濾 |
| 用戶頭像上傳 | MemberService | predictservice 僅讀取 `headshotpath` 做顯示 |
| 彩金派發（實際扣/加錢） | TransactionService / WalletService | predictservice 僅計算 profitpoint / profitzcoin 後通知其他服務執行金流 |
| 活動週期動態開關 | Activity management service | predictservice 僅讀取週期設定，不負責建立或刪除活動 |
| 策略管理（新增/刪除） | Strategy service | predictservice 僅執行策略下注與記錄結果 |
| 比賽資料的擷取與寫入（games_bk, games_bm, games_bs, games_ck） | GameDataService / 其他資料來源 | predictservice 僅讀取比賽資料進行分析與預測，不負責資料的建立、更新或同步 |
| AI 合併匹配數據（aimerge 系列表）的產生與維護 | aimerge 服務 | predictservice 僅讀取匹配結果輔助預測，不參與合併計算或標籤管理 |

---

## 常見錯誤

- ❌ 直接用 `account` 欄位查詢 gameusers → ✅ 必須先透過 MemberService 取得 `authkey` 再查詢（Cassandra 主鍵限制）
- ❌ 快取 VIP 狀態超過 10 分鐘 → ✅ VIP 到期判斷需即時，快取 TTL 不應過長或需訂閱 MemberService 訂閱狀態變更事件
- ❌ 公開 API 回傳完整 `GameUser` 物件 → ✅ 需移除 `password`/`email`/`authkey` 等敏感欄位
- ❌ 用 `GetAllGameUsers` 做列表查詢 → ✅ 全表掃描僅供後台，一般查詢應透過索引（如 email index）或改由 MemberService 提供分頁 API
- ❌ 假設 `follow_account` 是雙向關係 → ✅ `focus_account`（我關注的）與 `follow_account`（關注我的）需分別維護，且由 MemberService 負責同步
- ❌ 直接使用 `betpool_bets.account` 做排行榜 API 回傳 → ✅ 排行榜應僅顯示排名與利潤，避免洩漏用戶投注隱私
- ❌ 在結算前直接修改 `betpool_games.status` → ✅ 狀態變更須透過結算排程依時間與派彩邏輯自動推進
- ❌ 查詢 `killeraccounts_{gameType}` 未加 `lid`、`cid` 條件 → ✅ 會導致跨週期/跨聯盟掃描，應依主鍵過濾
- ❌ 活動開始/結束時間判斷僅用字串比對 → ✅ 應將 `startdate`+`starttime`、`enddate`+`endtime` 合併為 DateTime 物件後與目前時間比較，避免時區與格式問題
- ❌ 直接回傳 `accounts_{suffix}` 的 `password` 或 `phone` 欄位 → ✅ 僅回傳 `enabled`、`username` 等非敏感資訊，敏感欄位一律遮蔽
- ❌ 查詢 `actionlog` 未帶 `date` 分區條件 → ✅ 會觸發全表掃描，必須限定 `date` 範圍與必要集群鍵
- ❌ 查詢比賽資料時不指定 `gameType` 而直接進行跨表查詢或全表掃描 → ✅ 必須根據業務指定的類型（`bk`、`bm` 等）精確查詢對應的 `games_{gameType}` 表
- ❌ 直接寫入或修改 `games_{gameType}` 的比賽狀態或比分 → ✅ predictservice 沒有寫入權限，這些欄位更新應由 GameDataService 等上游服務負責
- ❌ 在公開 API 中回傳 `siteidmaps` 欄位 → ✅ 此欄位包含內部對照資訊，屬於敏感數據，必須從 API 回應中排除
- ❌ 查詢 `aimerge_match_predictions` 未帶 `game_type` 或 `gdate` → ✅ 會導致全表掃描，必須加入分區鍵條件
- ❌ 將 `aimerge_*` 表內完整的審核人、推斷方式等內部資訊直接暴露給前端 → ✅ 需摘取必要欄位，審核相關細節應遮蔽或僅限後台