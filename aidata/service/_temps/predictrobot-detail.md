# predictrobot — DB 操作邊界

> 產出時間：2025-04-04 10:00  
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）  
> ⚠️ AI 產出，需資深工程師審核後生效

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra predict | reader | Schema：[db/predict.json](../../db/predict.json) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **本服務不寫入** predict schema 中任何表，所有寫入由其他服務（如下注服務、結算服務、活動服務）負責

### 讀取規則

#### betpool_games

- **待開始遊戲**：`status=0` — 策略僅對未開始的比賽進行預測；已結束或進行中的比賽不應納入
- **未派彩遊戲**：`payout=false` — 避免讀取已結算遊戲的賠率資料，防止重複下注或錯誤賠率判斷
- **特定遊戲單筆查詢**：依 `id` 直接獲取單一遊戲詳細資訊（賠率、狀態、時間等）

#### betpool_bets

- **單一用戶在某遊戲的下注記錄**：主鍵查詢 `gid=? and account=? and id=?` — 用於計算歷史投注模式或重複下注檢查
- **時間範圍查詢**：可依 `addtime` 區間過濾，避免全表掃描

#### activities_cycles

- **有效活動週期**：`site=? and activityevent=?` 且 `startdate <= 今日日期 <= enddate` — 僅取目前正在進行的週期
- **特定週期查詢**：主鍵 `site, activityevent, cid` 精確取得某個週期的結果數量與時間範圍

#### activities_winneraccounts

- **活動排行榜**：主鍵查詢 `site=? and activityevent=? and cid=?` — 依 rank 排序後取得該週期的贏家列表（含預測次數、利潤點數、勝率）
- **無條件全量讀取**：展示排行榜時需附帶活動週期識別，避免讀取錯誤週期的資料

#### activities_record

- **用戶活動狀態**：主鍵查詢 `site=? and eventname=? and account=?` — 取得用戶在特定活動的剩餘天數、贏取投注列表
- **更新日期過濾**：可依 `updatedate` 限制查詢最近更新之紀錄

#### calculatelog

- **週次計算狀態檢查**：依 `weekid` 查詢，過濾 `done=1`，確保每週計算任務僅執行一次
- **無直接寫入**：僅讀取，由其他服務維護計算記錄

#### killeraccounts_BK

- **殺手帳號查詢**：主鍵 `lid=? and cid=? and account=?` — 讀取特定帳號在聯賽週期的平均賠率 (`avgodd`)，用於策略評估
- **無需全表掃描**：需搭配分區鍵 `lid` 執行查詢

### 不可回傳欄位

- **account**：用戶帳號，涉及個資，對外服務不應包含
- **betzcoin**：投注金額，用戶財務敏感資訊
- **profitzcoin**：利潤金額，財務敏感資訊
- **winlose**：輸贏狀態，投注隱私
- **betoption**：投注選項，具體選擇行為應受保護
- **winbets**：贏取投注列表，含多筆投注 ID，暴露用戶投注歷史
- **predictcount**（活動表）：用戶預測次數，雖為統計值，但結合 account 可分析用戶活躍度
- **profitpoint**（活動表）：利潤點數，財務相關
- **winpercentage**（活動表）：勝率，可能被用於不當誘導或歧視，建議對外遮蔽
- **restday**（活動記錄）：剩餘天數，可能反映用戶參與頻率
- **resultcount**（活動週期）：結果數量，非直接敏感但可結合推測活動規模
- **done**（計算記錄）：內部狀態，無需對外暴露
- **avgodd**（殺手帳號）：平均賠率，結合帳號可透漏投注行為，屬內部分析數據

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| PostgreSQL games | reader | Schema：[db/games.json](../../db/games.json) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- **本服務不寫入** games 中的任何表，所有寫入（例如 AI 合併結果、運行記錄）由其他服務負責

### 讀取規則

#### aimerge_match_predictions

- **已確認匹配預測**：`status='confirmed'` — 作為策略分析或訓練資料的可靠對照
- **特定日期與遊戲類型**：`game_type=? and gdate=?` — 批量提取某日所有預測對，用於每日統計或模型評估
- **特定預測單筆查詢**：`prediction_id=?` — 快速取得單一預測的詳細評分與狀態

#### aimerge_source_mapping

- **已確認來源對應**：`game_type=? and gdate=? and game_a_sitegid=? and source_b=? and source_b_sitegid=?` — 取得某對應關係的確切確認資訊
- **依預測 ID 關聯**：`prediction_id=?` — 查找該預測對應的實際來源映射

#### aimerge_label_overrides

- **人工修正查詢**：`game_type=? and gdate=? and prediction_id=?` — 取得審核員對該預測的修正標籤與排除訓練狀態

#### aimerge_runtime_config

- **當前有效配置**：`scope=? and is_active=true` — 取得特定範圍（如遊戲類型）的最新參數版本

#### aimerge_daily_reports

- **每日報告**：`game_type=? and report_date=?` — 讀取某天的 AI 合併統計，用於監控或儀表板

#### aimerge_historical_runs

- **歷史運行記錄**：`game_type=? and target_date=?` — 查詢某一日 AI 合併任務的執行狀態與處理量

#### aimerge_backtest_runs

- **回測結果**：`game_type=? and backtest_date=?` — 取得該回測的錯誤率與改善/退化樣本

#### aimerge_team_aliases

- **球隊別名查詢**：`game_type=? and source_id=? and canonical_team_id=?` — 獲取特定來源與標準球隊間的別名對應

### 不可回傳欄位

- **game_a_sitegid, source_b_sitegid**：包含外部站台的比賽 ID，屬商業機密，對外 API 不可暴露
- **score_detail**：內部評分演算法細節，可能透露模型邏輯，不宜回傳
- **params**（runtime_config）：動態配置參數，內部調整使用，不應對外公開
- **updated_by, reviewed_by, confirmed_by**：內部帳號或審核者資訊
- **source_b**：具體數據來源標識，可能揭示合作供應商，應遮罩
- **prediction_id, job_id, version_id**：內部系統生成的 ID，對外無業務含義，非必要不暴露
- **improved_samples, regression_samples, error_breakdown**：內部分析細節，含樣本識別碼，不應回傳
- **error_message**：錯誤訊息，可能包含內部架構資訊
- **score（預測分數）**：可選遮罩，避免對外顯示演算法置信度

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member | reader | Schema：[db/member.json](../../db/member.json) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **本服務不寫入** member schema，所有寫入由其他服務負責

### 讀取規則

#### gamerobots

- **機器人帳號篩選**：
  - Service.py：`enabled=1` — 僅取可用於預測的機器人帳號
  - Service2.py：`enabled=3` — 僅取每日限 200 次下注的機器人帳號
- **直接查詢**：以 `account` 為主鍵取得機器人資料，取得 `account` 與 `enabled` 欄位即可

#### gameusers

- **用戶基本資料查詢**：以 `authkey` 為主鍵讀取，取得 `account`、`username`、`rank`、`memberships`、`headshotpath` 等公開資訊。
- **帳號有效性檢查**：查詢後須確認 `status=1`，排除停權或凍結帳號。
- **會員角色判斷**：讀取 `memberships` 欄位識別 admin、moderator 等角色，用於功能權限控制。

#### gameusers_banned

- **停權狀態查詢**：以 `authkey` 查詢單一用戶的封禁記錄，過濾 `endtime > 當前時間` 判斷是否仍在禁言期。
- **避免使用被封禁帳號**：在執行預測動作前確認用戶未被停權。

#### gamesublogs

- **訂閱有效性檢查**：以 `authkey` 查詢，過濾 `autosub=true` 或 `subendtime > 當前時間`，確保用戶具備有效訂閱。
- **VIP 權限判斷**：結合 `viponly` 遊戲設定，確認玩家是否可參與限 VIP 活動。

#### appleinfos_game

- **Apple 帳號綁定資訊**：以 `id` (Apple ID) 查詢，取得使用者的 `email` 與 `name`，用於第三方登入驗證。

#### forbidden_email_domains

- **域名黑名單驗證**：以 `name` (域名) 查詢，篩選是否在禁止註冊清單內，避免使用特定郵箱的帳號。

#### gameusers_recommend

- **推薦關係查詢**：以 `authkey` 查詢被推薦人，或依 `recommendaccount` 檢索推薦人列表；通常用於獎勵計算。

#### gameuserviews

- **瀏覽量統計**：以 `account` 和 `year` 分區，按日期查詢特定用戶的每日瀏覽次數 (`views`)，用於分析活躍度。

### 不可回傳欄位

- **password**：用戶密碼，絕不可對外暴露
- **authkey**：認證金鑰，僅供內部驗證使用
- **email**：電子郵件，涉及個資保護
- **black_account, focus_account, follow_account**：社交關係清單，不可外洩用戶行為
- **memberships**：會員資格清單，涉及訂閱敏感資訊
- **headshotpath**：頭像路徑，可能洩漏用戶隱私
- **lastactiontime, lastchecktime**：用戶行為時間戳，可推測活躍模式
- **showcode**：展示碼，可能用於邀請或優惠
- **signindate, signindays**：簽到記錄，可分析用戶規律
- **adsource**：廣告來源，屬商業數據
- **site, siteid**：第三方登入資訊，涉及帳號綁定關聯
- **addtime**：帳號建立時間，非必要不應回傳
- **status**：帳號狀態，僅內部使用，不應直接暴露
- **rank**：若業務需要可回傳，但建議僅在需要顯示排名時回傳，預設可列為敏感保護
- **gamecount**：遊戲次數，可能反映用戶活躍度，可選保護
- **renamecount**：改名次數，非必要
- **subid, tradeno** (gamesublogs)：訂閱產品與交易流水號，財務隱私
- **paymethod, paytype**：付款方式，敏感
- **autosub, subendtime, subtime**：訂閱詳細時程，可推斷用戶消費習慣
- **cost, deducted** (gameusers_banned)：罰款資訊，財務敏感
- **description** (gameusers_banned)：停權原因，涉及用戶行為評價
- **recommendaccount** (gameusers_recommend)：推薦人帳號，可能涉及社交關係
- **views** (gameuserviews)：瀏覽次數，統計值可選保護
- **gamerobots.account**：機器人帳號，內部使用，不應外洩
- **appleinfos_game.email, name**：Apple 帳號資訊，個資保護
- **forbidden_email_domains.name, addtime**：黑名單資訊，內部營運使用

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| 未使用 | — | — | 本服務目前無 Redis 操作 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 用戶註冊/登入/密碼管理 | member-api (推測) | predictrobot 僅讀取機器人與用戶帳號，不處理認證流程 |
| 會員訂閱記錄寫入 | subscription-service (推測) | gamesublogs 表由訂閱服務維護 |
| 用戶帳號狀態變更 | user-management (推測) | gameusers.status、gameusers_banned 由用戶管理服務負責 |
| 下注記錄寫入 | predict-bet-service (推測) | predictbets_* 表由下注服務寫入，本服務僅讀取歷史記錄 |
| 活動週期寫入與結算 | activity-service (推測) | activities_cycles、activities_winneraccounts 由活動服務維護 |
| 遊戲資料寫入 | game-service (推測) | betpool_games 表由遊戲服務新增與更新（如派彩） |
| AI 合併結果寫入與模型訓練 | aimerge-service (推測) | games 中 aimerge_* 表的資料由 AI 合併服務維護，predictrobot 僅讀取 |
| 殺手帳號資料維護 | 策略分析服務 (推測) | killeraccounts_BK 等表由專門的分析服務更新 |

---

## 常見錯誤

- ❌ **混用機器人類型**：將 `enabled=1` 與 `enabled=3` 的機器人混用在同一策略  
  ✅ Service.py 固定使用 `enabled=1`，Service2.py 固定使用 `enabled=3`

- ❌ **直接 JOIN gameusers 取帳號**：在 Cassandra 執行複雜 JOIN 查詢  
  ✅ 從排行榜 API 取得帳號清單後，透過 `split_account` 批次處理

- ❌ **回傳完整 gameusers 物件給前端**：包含 password/authkey 等敏感欄位  
  ✅ 僅回傳 account、username、rank 等公開欄位

- ❌ **快取機器人清單未設失效機制**：當 gamerobots.enabled 變更時仍使用舊快取  
  ✅ 每次查詢前重新從 DB 取得最新機器人清單，或設定合理 TTL（如 5 分鐘）

- ❌ **對 betpool_games 讀取未過濾 status**：可能取得已結束遊戲的過期賠率  
  ✅ 預測前必須檢查 `status=0`，並確認 `endtime > 當前時間`（毫秒時間戳比較）

- ❌ **對 activities_cycles 讀取未檢查日期範圍**：取得已結束或未開始的週期，導致排行榜／獎勵判斷錯誤  
  ✅ 讀取時須同時比較 `startdate` 與 `enddate` 與當前日期（格式 YYYYMMDD 文字比對）

- ❌ **對 aimerge 表查詢未指定分區鍵**：例如直接掃描全表，造成效能瓶頸  
  ✅ 所有查詢須搭配 `game_type`、`gdate` 等必要條件，利用 PostgreSQL 索引；避免 `SELECT *` 查詢大表

- ❌ **洩漏別名映射或站台資訊**：將 `aimerge_team_aliases.source_id` 或 `aimerge_source_mapping.source_b` 直接回傳給前端  
  ✅ 對外 API 應遮蔽所有外部站台標識與映射細節，僅回傳必要結果