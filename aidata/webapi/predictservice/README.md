# PredictService WebAPI

- **Git Repository**：https://git.zbdigital.net/biz/predictservice.git

## 職責
負責管理平台所有**競猜預測**業務，包含下注管理、Killer 機制、獎池賽事（BetPool）、篩選報表、策略分析、特殊活動排行榜，以及新彩票競猜。是競猜核心運算與資料儲存服務，透過 `pricebackendservice` 代理後台操作，也直接提供前台查詢。

## 技術棧
- 框架：ASP.NET Core (.NET 8.0)
- 資料庫：Cassandra（Keyspace: `predict` / `member` / `pricecenter`），另有 PostgreSQL（`games`）
- 快取：Redis
- 驗證：ECFramework.ECService（內部統一驗證框架）
- 配置中心：Zookeeper
- 日誌：Kafka（Topic: `applogs`）+ Cassandra
- 其他套件：ECCore 3.0.4、ECFramework.ECService 3.0.1

## 資料庫重要 Table

| Table 名稱（Cassandra） | 用途 | 重要欄位 |
|----------------------|------|---------|
| `predict.predictbets_{gameType}`（如 `predictbets_BK`） | 競猜下注記錄（依 gameType 區分） | `game_type`, `lid`, `g_date`, `gid`, `account`, `amount`, `result` |
| `predict.predict_settings` | 競猜遊戲設定（整體開關與玩法） | `game_type`, `play_modes`, `killer_enabled` |
| `predict.killer_cycle_settings` | Killer 周期設定 | `game_type`, `lid`, `cid`, `pay_out` |
| `predict.killeraccounts_{gameType}`（如 `killeraccounts_BK`） | Killer 帳號名單 | `game_type`, `lid`, `cid`, `account`, `profitpoint` |
| `predict.betpool_games` | 獎池賽事 | `id`, `status`, `starttime`, `endtime`, `payout`, `winresult`, `zcoinprice`, `betoptions`, `names` |
| `predict.betpool_bets` | 獎池下注 | `gid`, `account`, `id`, `betoption`, `betzcoin`, `profitzcoin`, `winlose` |
| `predict.predictfilterreports` | 篩選器報表 | `reportdate`, `game_type`, `lid`, `account`, `win_rate` |
| `predict.weekly_reports` | 週報表 | `week_id`, `account`, `total_bets`, `profit` |
| `predict.calculatelog` | 計算日誌 | `weekid`, `done`, `weekdate`, `addtime` |
| `predict.activities_cycles` | 活動週期設定 | `site`, `activityevent`, `cid`, `startdate`, `enddate` |
| `predict.activities_record` | 特殊活動記錄 | `site`, `eventname`, `account`, `winbets`, `restday` |
| `predict.activities_winneraccounts` | 特殊活動得獎名單 | `site`, `activityevent`, `cid`, `account`, `rank`, `profitpoint`, `winpercentage` |
| `predict.strategy_bet_log` | 策略下注紀錄（存在性需人工確認） | `id`, `result` |
| `predict.result_log` | 賽事結果日誌 | `gdate`, `game_type`, `lid`, `gid`, `status` |
| `predict.championships_{gameType}`（如 `championships_BK`） | 錦標賽設定 | `GameType`, `ID`, `Names`, `Leagues` |
| `predict.alliance_bet_options_{gameType}` | 聯盟下注選項 | 待人工確認 |
| `predict.predictgames_{gameType}_lock_{year}`（如 `predictgames_BK_lock_2025`） | 賽事解鎖會員 | `lid`, `gdate`, `account`, `gid`, `unlock_accounts`, `unlock_rb_accounts` |

## 對外 API 重點

### 競猜下注
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/bets/{gameType}` | 建立競猜下注 | ✅ |
| POST | `/api/v1/bets/accumulator` | 建立串關下注 | ✅ |
| POST | `/api/v1/merge/{gameType}/bets` | 合併競猜下注 | ✅ |
| GET | `/api/v1/bets` | 查詢全部下注（日期範圍） | ✅ |
| GET | `/api/v1/bets/{gameType}` | 查詢遊戲類型下注（可帶 `startDate`, `endDate`, `account`） | ✅ |
| GET | `/api/v1/bets/{gameType}/{lid}` | 查詢聯賽下注（可帶 `startDate`, `endDate`, `account`） | ✅ |
| GET | `/api/v1/bets/{gameType}/{lid}/{gDate}` | 查詢指定日期聯賽下注 | ✅ |
| GET | `/api/v1/bets/{gameType}/{lid}/{gDate}/{gid}` | 查詢指定賽事下注 | ✅ |
| GET | `/api/v1/bets/zcoinReports/{gtype}` | 查詢 ZCoin 報表（可帶 `start_date`, `end_date`, `lid`, `gid`） | ✅ |
| PUT | `/api/v1/bets/results/{gameType}` | 更新競猜結果 | ✅ |
| DELETE | `/api/v1/bets/{gameType}/{lid}/{gDate}/{gid}` | 刪除賽事下注 | ✅ |

### 競猜設定
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/settings/predict/{gameType}` | 建立遊戲競猜設定 | ✅ |
| POST | `/api/v1/settings/killer/cycles/{gameType}` | 建立 Killer 周期設定 | ✅ |
| POST | `/api/v1/settings/killer/conditions/{gameType}/{lid}/{cid}` | 建立 Killer 條件設定 | ✅ |
| GET | `/api/v1/settings/predict` | 查詢所有競猜設定 | ✅ |
| GET | `/api/v1/settings/predict/{gameType}` | 查詢遊戲競猜設定 | ✅ |
| GET | `/api/v1/settings/playmodes/{gameType}` | 查詢玩法設定 | ✅ |
| GET | `/api/v1/settings/killer/cycles` | 查詢 Killer 周期設定 | ✅ |
| PUT | `/api/v1/settings/predict/{gameType}` | 更新競猜設定 | ✅ |
| PUT | `/api/v1/settings/killer/cycles/{gameType}/{lid}/{cid}` | 更新 Killer 周期設定 | ✅ |
| PUT | `/api/v1/settings/killer/cycles/{gameType}/{lid}/{cid}/payout` | 更新 Killer 派彩 | ✅ |

### Killer 機制
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/v1/killers/{account}` | 查詢帳號 Killer 記錄 | ✅ |
| GET | `/api/v1/killers/{gameType}/{lid}` | 查詢聯賽 Killer 帳號 | ✅ |
| GET | `/api/v1/killers/{gameType}/{lid}/{cid}` | 查詢周期 Killer 帳號 | ✅ |

### 獎池賽事（BetPool）
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/betpool/games` | 建立獎池賽事 | ✅ |
| POST | `/api/v1/betpool/games/{id}/bets` | 建立獎池下注 | ✅ |
| GET | `/api/v1/betpool/games` | 查詢獎池賽事列表 | ✅ |
| GET | `/api/v1/betpool/games/{id}` | 查詢單一獎池賽事 | ✅ |
| GET | `/api/v1/betpool/games/{id}/bets` | 查詢獎池下注 | ✅ |
| GET | `/api/v1/betpool/games/accounts/{account}/bets` | 查詢帳號獎池下注 | ✅ |
| PUT | `/api/v1/betpool/games/{id}` | 更新獎池賽事內容（管理員） | ✅ |
| PUT | `/api/v1/betpool/games/{id}/result` | 更新獎池結果 | ✅ |
| PUT | `/api/v1/betpool/games/{id}/payoutdtatus` | 更新派彩狀態 | ✅ |
| PUT | `/api/v1/betpool/games/{id}/bets/result` | 更新獎池下注結果 | ✅ |

### 篩選報表
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/reports/predictfilterreports` | 建立篩選報表（接收已計算數據） | ✅ |
| GET | `/api/v1/reports/calculalogs` | 查詢計算日誌 | ✅ |
| GET | `/api/v1/reports/predictfilterreports/{date}` | 查詢日期篩選報表（需提供 `gameType`, `lid` 查詢參數） | ✅ |
| GET | `/api/v1/reports/predictfilterreports/accounts/{account}` | 查詢帳號篩選報表 | ✅ |
| GET | `/api/v1/reports/weeklyreports/{account}` | 查詢帳號週報表 | ✅ |
| PUT | `/api/v1/reports/calculalogs/{weekID}/result` | 更新計算結果 | ✅ |

### 特殊活動
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/special/records/{site}/{activityEvent}` | 設定活動記錄 | ✅ |
| POST | `/api/v1/special/{site}/{activityEvent}/leaderboards/mainstreak` | 建立主連勝排行榜 | ✅ |
| POST | `/api/v1/special/winners/{site}/{activityEvent}` | 設定活動得獎帳號 | ✅ |
| GET | `/api/v1/special/records/{site}/{activityEvent}/{account}` | 查詢帳號活動記錄 | ✅ |
| GET | `/api/v1/special/winners/{site}/{activityEvent}/{cid}` | 查詢周期得獎帳號 | ✅ |
| PUT | `/api/v1/special/records/{site}/{activityEvent}/{account}/winbets` | 更新活動獲勝注單（追加） | ✅ |
| DELETE | `/api/v1/special/records/{site}/{activityEvent}/{account}` | 刪除帳號活動記錄 | ✅ |

### 策略分析
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| PUT | `/api/v1/strategies/result` | 更新策略結果 | ✅ |
| DELETE | `/api/v1/strategies` | 刪除策略結果 | ✅ |

### 系統工具
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/system/tables` | 自動建立 Cassandra Table | ✅ |
| POST | `/api/v1/system/leaderboard/predicet` | 建立競猜排行榜 | ✅ |
| POST | `/api/v1/system/leaderboard/killeraccount` | 建立 Killer 排行榜 | ✅ |
| POST | `/api/v1/system/leaderboard/winningrate/{gameType}` | 建立勝率排行榜 | ✅ |
| GET | `/api/heart` | Health Check | ❌ |
| GET | `/api/version` | 查詢版本號 | ❌ |

## 服務相依

| 相依服務 | 用途 |
|---------|------|
| `memberservice` | 查詢錢包餘額、會員狀態、VIP 資格；實際執行扣點、發放獎金等金流操作由 `MemberService` 或 `TransactionService` 經 `memberservice` 代理 |
| `pricecenter` | 讀取賽事資料（賽果、比分）進行結算 |
| `TransactionService` / `WalletService` | 透過 `memberservice` 間接完成金流作業（predictservice 僅計算 profit 後通知派發） |

## 常見使用場景

1. **會員競猜下注**
   - 觸發：前台使用者在競猜頁面選擇賽事下注
   - 流程：`POST /api/v1/bets/{gameType}` → 驗證錢包餘額 → 扣點（透過 memberservice） → 寫入 Cassandra

2. **賽事結算與競猜結果更新**
   - 觸發：pricecenter 賽事結束後觸發
   - 流程：`PUT /api/v1/bets/results/{gameType}` → 計算賽果 → 通知金流服務（MemberService/TransactionService）發放獎金

3. **Killer 周期結算**
   - 觸發：後台排程或管理員手動觸發
   - 流程：GET Killer 帳號 → `PUT /api/v1/settings/killer/cycles/{gameType}/{lid}/{cid}/payout` → 通知金流服務發放 Killer 獎金

4. **獎池賽事開獎**
   - 觸發：獎池賽事結束
   - 流程：`PUT /api/v1/betpool/games/{id}/result` → `PUT /api/v1/betpool/games/{id}/payoutdtatus` → 批次通知發放獎金

5. **篩選排行榜報表產生**
   - 觸發：定時排程每日執行
   - 流程：`POST /api/v1/reports/predictfilterreports` → 接收已計算的報表資料寫入 Cassandra（實際計算邏輯可能由外部排程完成，需人工確認）

## AI 判斷關鍵字

競猜, 預測, 下注, 賽事, 結算, Killer, 獎池, BetPool, 串關, 篩選報表, 勝率, 週報, ZCoin, 活動排行, 策略分析, 新彩票競猜, 冠軍錦標賽