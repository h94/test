# gamecombineservice — DB 操作邊界

> 產出時間：2025-04-12 14:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| PriceCenter Cassandra | writer / reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **`pricecenter.accounts_{brand}.password`**：僅 `gamecombineservice` 內部建立或更新遊戲平台帳號流程可寫入，必須雜湊處理，不可明文儲存。涵蓋 `AU8`、`Fortuna888`、`HGA`、`HGA2`、`KKK`、`KU`、`NK`、`Panda`、`PinnacleV2`、`TG`、`TG999` 等所有 `accounts_*` 表。
- **`pricecenter.accounts_{brand}.phone`**：與帳號建立或更新流程綁定，寫入後不可由前端要求直接修改，須驗證後才能更新。
- **`pricecenter.accounts_{brand}.enabled`**：僅特定管理或狀態變更流程可修改其值（0 或 1），一般 UPDATE 不可無故變動啟用狀態。
- **`pricecenter.accounts_{brand}.handler`**：僅在建立或更新處理器配置映射時寫入；更新時必須使用合併寫入（如 INSERT JSON），不可直接以空 map 覆蓋已有細項，避免設定遺失。
- **`pricecenter.sitegames_{gtype}.gid`**：僅執行遊戲映射流程（SetGidToEmpty）時可將 `gid` 設為空字串；其他場景不可直接寫入或修改 `gid`。
- **`pricecenter.games_{gtype}.gtime`**：僅 `UpdGameTime` 操作可更新遊戲時間，不可逕行由其他 API 修改。
- **`pricecenter.actionlog`**：所有欄位僅可透過記錄操作日誌的寫入點新增（INSERT），不支援 UPDATE 或 DELETE；`detail` 必須為合法的 JSON 結構，不可事後修改。

### 讀取規則

- **平台帳號查詢**：讀取 `pricecenter.accounts_{brand}` 時必須以 `account` 作為 WHERE 條件（partition key）；嚴禁僅使用 `username` 或 `phone` 進行查詢，否則將導致全表掃描。
- **帳號啟用檢查**：遊戲平台登入或操作前，須篩選 `enabled = 1`；`enabled = 0` 表示已停用，不可允許任何操作。
- **關閉時間過濾**：`closetime` 若為非空值（非空字串）表示帳號已關閉，該帳號不可被選用於任何流程。
- **站點遊戲查詢**：讀取 `pricecenter.sitegames_{gtype}` 時必須指定 `site`（partition key），並結合 `gdate` 範圍及 `status = 2` 過濾，避免掃描大量非生效遊戲。
- **中心遊戲查詢**：讀取 `pricecenter.games_{gtype}` 時應以 `gdate` 和 `status` 為主要過濾條件；非生效狀態的遊戲不可提供給前端選擇。
- **賠率歷史查詢**：讀取 `pricecenter.odds_his_{gtype}_{gdate}` 時，必須同時提供完整 partition key 條件：`site`、`sitelid`、`sitegid`，並限定 `gdate` 聚簇鍵範圍；未帶齊 partition key 將觸發全表掃描。
- **站點聯賽／球隊映射查詢**：讀取 `pricecenter.siteleagues_{gtype}`、`pricecenter.siteteams_{gtype}` 時，應以 `site` 為 partition key，並可搭配 `sitelid`、`sitetid` 進行精確查找。
- **操作日誌查詢**：讀取 `pricecenter.actionlog` 須以 `date`（partition key）為主軸，輔以 `addtime`、`user`、`gametype` 進行範圍查詢；不可僅以 `user` 作為 WHERE 條件。

### 不可回傳欄位

- **`pricecenter.accounts_{brand}.password`**：密碼為極敏感個資，任何對外 API 不可回傳。
- **`pricecenter.accounts_{brand}.phone`**：電話號碼為使用者個人資料，不可於查詢列表或詳情中回傳。
- **`pricecenter.accounts_{brand}.handler`**：處理器內部配置映射，屬設定細節，對外僅需要知悉存在與否，不可回傳細部鍵值。
- **`pricecenter.actionlog.detail`**：原始操作細節可能包含敏感資訊，對外查詢時應進行遮蔽或僅回傳摘要欄位。
- **`pricecenter.odds_his_{gtype}_{gdate}.logs`**：原始賠率變動 JSON，前端不應直接取得完整結構，需由服務層進行轉換或摘要後提供。

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Predict Cassandra | writer / reader | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **`activities_cycles.activityevent` / `cid`**：僅由管理後台或活動排程建立，不可經由前端或外部 API 直接寫入。
- **`activities_record.account` / `eventname`**：僅於預測活動參與時寫入，寫入後不可修改。
- **`activities_winneraccounts.rank` / `profitpoint` / `winpercentage`**：由結算排程計算後寫入，不可透過一般 API 手動修改。
- **`betpool_bets.betzcoin` / `profitzcoin`**：僅在下注時寫入，寫入後不可更新金額欄位。
- **`betpool_bets.winlose`**：僅結算時由排程設定，外部不具直接寫入權限。
- **`betpool_games.status` / `payout` / `winresult`**：僅限結算排程更新，外部不允許直接變更。
- **`calculatelog.done`**：僅內部計算任務可寫入 `done=1`，前端或外部 API 不可操作計算完成旗標。
- **`settings_league`**：由其他配置服務管理，本服務不具寫入權限（僅讀取）。
- **`predictbets_{gtype}`**：由預測服務寫入，本服務僅在特定場景下讀取關聯資訊，不直接寫入。

### 讀取規則

- **活動週期查詢**：必須同時限制 `activityevent` 與 `cid`（clustering key），不可僅用 `site` 掃描整個 Partition。
- **進行中競猜遊戲**：讀取 `betpool_games` 時須過濾 `status`（如 `status=1` 表示進行中），且應搭配 `starttime <= now` 與 `endtime >= now`，已結束或尚未開始的遊戲不可提供下注。
- **下注記錄查詢**：查詢 `betpool_bets` 必須帶入 `gid`（partition key），再依 `id` 或 `account` 進行範圍過濾；嚴禁僅使用 `account` 進行全表掃描。
- **贏家排行**：讀取 `activities_winneraccounts` 必須以 `site`、`activityevent`、`cid` 限定週期，並按 `rank` 排序；不同週期資料不可混合。
- **計算日誌檢查**：讀取 `calculatelog` 時，應以 `weekid` 或 `weekdate` 為主要條件，判斷某週是否已完成計算。
- **聯盟設定讀取**：查詢 `settings_league` 時，需以 `gametype` 為條件，並可依 `classified` 進行過濾；不可進行全表掃描。
- **預測投注明細讀取**：需查詢 `predictbets_{gtype}` 時，必須同時提供 `gid` 與 `gdate` 作為篩選條件，不得僅以 `account` 或 `iid` 進行跨分區掃描。

### 不可回傳欄位

- **`betpool_bets.account`**：使用者帳號為個人識別資訊，任何對外查詢不得回傳。
- **`betpool_bets.betzcoin` / `profitzcoin`**：內部結算用原始金額，前端僅應看到聚合後的投注總量或派彩總額，不可暴露單筆明細。
- **`activities_record.winbets`**：內含投注 ID 列表，為內部關聯資料，不應直接回傳前端。
- **`betpool_games.feedrate`**：抽水比例為內部營運參數，不適合對外揭露。
- **`predictbets_{gtype}.account`**：同為帳號資訊，不可於查詢結果中回傳。

---

## sport

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport MySQL | reader | Schema：[db/sport.md](../../db/sport.md) · 語意：[db/sport-detail.md](../../db/sport-detail.md) |

### 寫入限制

不適用。本服務對 sport 資料庫僅具讀取權限，所有寫入由其他服務（如 wallet‑service、sport 內部模組）負責。

### 讀取規則

- **錢包餘額查詢**：讀取 `GameUsers_Wallet` 時必須以 `AuthKey` 作為主鍵進行單點查詢，禁止全表掃描；查詢後應快取，避免高頻衝擊。
- **交易記錄查詢**：讀取 `GameUsers_Wallet_Transactions` 需搭配 `AuthKey` 與日期範圍（`TDate`），不可僅依 `Type` 進行過濾。
- **球員資料查詢**：查詢 `BK_SitePlayers` 時，必須同時指定 `Site`、`SiteID`、`Year`（複合 partition key），並可依 `League` 或 `TeamID` 輔助過濾；不得單獨使用 `Name` 進行搜尋。
- **聊天記錄查詢**：讀取 `ChatRoomHistories_Backup` 必須帶上 `GID`（partition key），並依 `Account`、`ID` 或 `AddTime` 範圍限縮；未附 `GID` 禁止查詢。
- **社群群組查詢**：讀取 `Community_Groups` 時應使用 `ID` 主鍵，或搭配 `Enabled = 1` 過濾，不可全表讀取。
- **通知訊息查詢**：查詢 `Notification_Messages` 時，若以模板查詢，須使用 `TID`；若以消息 ID 查詢，須使用 `ID`；應同時過濾 `Enabled` 狀態。

### 不可回傳欄位

- **`GameUsers_Wallet.AuthKey`**：作為使用者唯一標識，對外 API 不應直接暴露原始 AuthKey，僅可在內部流轉。
- **`GameUsers_Wallet_Transactions.TypeInfo`**：可能包含內部交易細節 JSON，前端僅需摘要，不得回傳完整原始內容。
- **`ChatRoomHistories_Backup.LikeAccount`**：涉及其他使用者帳號，不應於公開回傳中顯示。
- **`ChatRoomHistories_Backup.HeadShotPath`**：頭像路徑可暴露內部儲存結構，回傳時應轉換為安全 URL。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport MySQL | reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |
| Games PostgreSQL | reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

不適用。本服務對 games 資料庫（含 MySQL 與 PostgreSQL）僅具讀取權限。

### 讀取規則

- **比賽查詢 (MySQL)**：必須以 `gdate` 和/或 `lid` 作為主要過濾條件，避免全表掃描。
- **啟用中比賽 (MySQL)**：查詢 `games_bk`、`games_bm`、`games_bs` 等分表時，通常需過濾 `status`，例如排除 `PreGame` 等尚未開始的比賽。
- **特定來源查詢 (MySQL)**：若需查詢特定資料來源（如 '1xbet.com'）的比賽，必須附帶 `source` 作為 `WHERE` 條件。
- **AI 合併預測紀錄 (PostgreSQL)**：查詢 `aimerge_match_predictions` 必須同時限定 `game_type`、`gdate`，並可加入 `status` 或 `source_b` 進一步過濾；不可僅用 `prediction_id` 進行跨日期掃描。
- **來源對應查詢 (PostgreSQL)**：讀取 `aimerge_source_mapping` 需以 `game_type`、`gdate` 及所需關聯的 `game_a_sitegid` 為核心條件。
- **隊伍別名查詢 (PostgreSQL)**：查詢 `aimerge_team_aliases` 須以 `game_type` 及 `source_id` 為索引，避免全表搜尋。
- **標籤覆寫查詢 (PostgreSQL)**：讀取 `aimerge_label_overrides` 時，應使用 `game_type`、`gdate`、`prediction_id` 組合查詢。
- **日報／回測／歷史執行紀錄 (PostgreSQL)**：此類統計表（`aimerge_daily_reports`、`aimerge_backtest_runs`、`aimerge_historical_runs`）查詢時需以 `game_type` 搭配 `report_date`、`backtest_date` 或 `target_date` 進行範圍過濾，不得全表彙總。
- **運行時配置 (PostgreSQL)**：讀取 `aimerge_runtime_config` 需依 `scope` 及 `is_active` 進行過濾，僅取當前生效版本。

### 不可回傳欄位

- **`games_bk.otherinfo`**：為內部備註或爬蟲原始資訊，可能包含未結構化的雜訊，不應直接回傳。
- **`aimerge_match_predictions.score_detail`**：內部 AI 模型計分細節，前端應僅取得摘要分數，不得暴露原始 JSON。
- **`aimerge_backtest_runs.improved_samples` / `regression_samples`**：包含樣本原始數據，回傳時需遮蔽或僅供內部檢視。
- **`aimerge_daily_reports.error_breakdown`**：內部錯誤分類，可能間接暴露系統弱點，不可對外直接展示。
- **`aimerge_runtime_config.params`**：系統配置參數，直接回傳可能造成安全風險，應限制僅在必要時局部提供。

---

## Redis

無使用 Redis 快取。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 活動週期建立 | acmanagement-service | predict 僅讀取活動週期資料，不負責週期生成與時間控制 |
| 使用者帳戶驗證 | auth-service | predict 僅記錄帳號，不處理驗證或登入 |
| 投注池派彩金流 | wallet-service | betpool 結算結果產生後由 wallet-service 執行轉帳 |
| 平台密碼驗證 | auth-service | pricecenter 儲存密碼但由 `auth-service` 進行驗證比對，本服務不處理登入驗證邏輯 |
| 遊戲賽程管理 | schedule-service | pricecenter 負責儲存站點遊戲與賠率，但賽程與時間變更由外部排程服務控制 |
| 預測結果統計與排名計算 | 內部結算排程 | predict `activities_winneraccounts` 及 `calculatelog` 由專責排程生成，本服務僅寫入基礎記錄 |
| 錢包扣款與交易 | wallet-service | sport 資料庫中的 `GameUsers_Wallet` 及 `GameUsers_Wallet_Transactions` 僅供本服務讀取，所有交易與餘額變更均由 wallet‑service 負責 |
| 聊天訊息與社群管理 | sport 內部模組 | `ChatRoomHistories_Backup`、`Community_Groups` 等表為既有系統功能，不應透過本服務修改 |

---

## 常見錯誤

- ❌ 直接對 `betpool_bets` 執行跨遊戲批量更新 → ✅ 每次更新應限定單一 `gid`（partition key），避免全表掃描或逾時。
- ❌ 未檢查 `betpool_games.status` 即允許下注 → ✅ 下注前須驗證該遊戲狀態為「進行中」或「可下注」，已結束或暫停的遊戲應拒絕。
- ❌ 下注時未檢查 `betpool_games.starttime` 與 `endtime` 範圍 → ✅ 必須確認當前時間位於投注時間窗內，否則拒絕請求。
- ❌ 查詢下注記錄時僅使用 `account` 作為條件 → ✅ 必須連同 `gid`（partition key）一起查詢，否則引發全表掃描。
- ❌ 直接將 `password` 寫入明文 → ✅ 寫入前須雜湊處理，即使測試資料亦不可使用明碼。
- ❌ 對 `accounts_{brand}` 執行 UPDATE 時未使用 `account` 或 `username` 進行 WHERE 過濾 → ✅ 必須指定帳號唯一鍵，避免單次更新影響整個 Partition。
- ❌ 為省事對 `enabled` 狀態執行 UPDATE 時不帶 `closetime` 檢查 → ✅ 若 `closetime` 非空，帳號已關閉，不應再變更其啟用狀態。
- ❌ 誤認 `handler` 為可選的純文字欄位，直接寫入空值導致設定遺失 → ✅ 寫入前須確保 map 結構正確，僅透過特定流程更新其中鍵值對。
- ❌ 前端顯示判賠等場景時回傳 `password` 或 `phone` → ✅ 任何對外輸出必須遮蔽或排除這兩欄位。
- ❌ 查詢 `odds_his_{gtype}_{gdate}` 時未限定 `gdate` 範圍 → ✅ `gdate` 為 CLUSTERING ORDER BY 欄位，需配合 `site` + `sitelid` + `sitegid` 查詢單一遊戲的賠率歷史，不可無限制掃描。
- ❌ 對 `accounts_{brand}` 使用 `username` 或 `phone` 作為查詢鍵時忽略 `account` 為 partition key → ✅ 必須以 `account` (唯一值) 作為 WHERE 篩選條件，否則可能觸發全表掃描。
- ❌ 對 `aimerge_match_predictions` 僅以 `source_b_sitegid` 進行跨日期查詢 → ✅ 須同時帶入 `game_type`、`gdate` 條件，利用複合索引。
- ❌ 在讀取 `GameUsers_Wallet` 時未限制結果筆數，或逐筆查詢未做快取 → ✅ 單次查詢須直接用 `AuthKey` 定位，併考慮短暫快取以降低資料庫壓力。
- ❌ 將 `aimerge_runtime_config.params` 整體回傳給前端 → ✅ 應僅萃取必要參數，或由後端封裝後再提供。