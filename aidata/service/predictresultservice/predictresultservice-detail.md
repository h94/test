# predictresultservice — DB 操作邊界

> 產出時間：2025-04-01 16:20
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member keyspace | reader / writer | Schema：[db/member.md](../../db/member.md) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **gameusers.gamecount**：僅由結算邏輯自動累加；每次結算 +1；不可由前端直接修改
- **gameusers.lastchecktime**：僅由 `UpdUserLastCheck` / `UpdUsersLastRankCheck` API 更新；用於判斷用戶排名是否需重新計算
- **gameusers.rank**：僅由排名計算邏輯（CalculateService.UpgradeRank）更新；不可由前端直接修改
- **gamerobots.enabled**：當機器人需停止（status=3）時，僅由 `SetRobotStop` API 寫入此欄位；不可直接 UPDATE

### 讀取規則

- **排名升級判斷**：`GetAllGameUsers` 須過濾 `lastchecktime` 早於指定檢查時間的用戶；避免重複計算已檢查的用戶
- **機器人過濾**：結算時需檢查 `gamerobots.enabled`；已停用（enabled=3）的機器人不參與結果統計
- **帳號狀態檢查**：查詢 `gameusers` 時，若涉及活躍用戶操作，應過濾 `status = 1`（啟用狀態）；凍結或未激活帳號不可參與結算

### 不可回傳欄位

- **password**：任何 API 回應不得包含密碼欄位
- **authkey**：僅內部服務間使用；對外 API 應改用 `account` 或脫敏識別碼

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra predict keyspace | owner | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **betpool_games.winresult**：僅由結算邏輯（`PredictModeResult` / `ResultService`）在確認比賽結果後寫入；不可由外部 API 或排程任意更新
- **betpool_games.payout**：僅在派獎完成後設為 true；重複派獎前須確認尚未設為 true，並在回滾後重置
- **betpool_bets.winlose** / **betpool_bets.profitzcoin**：僅由結算邏輯根據遊戲 `winresult` 與玩家投注選項計算後寫入；不可直接 UPDATE
- **betpool_bets.betzcoin**：投注時寫入，結算後即為歷史紀錄，不可修改；投注後不允許變更金額
- **predictbets_%s.winloss** / **predictbets_%s.profitpoint**：僅由結算邏輯 (`PredictProvider` / `NewLotteryPredictProvider`) 計算後寫入；與 `betpool_bets` 對應欄位同步
- **predictbets_%s.status**：僅由結算邏輯設為 `2`（已結算）或 `3`（取消）；不得跳過計算直接修改
- **resultlogs**：僅在結果處理成功後 INSERT 一筆記錄；不得對同一遊戲重複寫入
- **activities_cycles.resultcount**：僅由活動結算邏輯累加；不可直接 SET 數值
- **activities_winneraccounts.rank** / **winpercentage** / **predictcount** / **profitpoint**：僅由排名計算邏輯 (`UpgradeRank`) 更新；不可由外部 API 或管理後台任意修改
- **activities_record.restday**：由活動排程或結算邏輯計算更新；不可直接 INSERT 或 UPDATE 錯誤值
- **activities_record.winbets**：由活動邏輯新增獲勝投注 ID；不可手動亂改
- **calculatelog.done**：由週報計算邏輯 (`WeeklyReportProvider`) 設為 `1` 標記完成；不可手動修改
- **calculatelog.addtime** / **weekdate**：由週報計算邏輯在開始計算時寫入，結算完成後不可再變更
- **killeraccounts_BK.avgodd**：由殺手帳號分析邏輯計算平均賠率後寫入；不可手動修改
- **killeraccounts_BK.addtime**：記錄產生時自動寫入，不可事後修改

### 讀取規則

- **待結算比賽**：查詢 `betpool_games` 時，必須過濾 `status > 1 AND payout = false`（已結束但尚未派獎）；避免重複結算
- **用戶投注查詢**：從 `betpool_bets` 取得某場遊戲的所有投注時，必須以 `gid` 為分割鍵，並可搭配 `account` 或 `id` 條件；嚴禁僅靠時間等非主鍵條件進行全表掃描
- **活動週期過濾**：查詢 `activities_cycles` 須提供完整主鍵 `site`、`activityevent`、`cid`；不允許只依賴 clustering key 範圍或部分條件查詢
- **活動參與記錄**：查詢 `activities_record` 同樣須以 `site`、`eventname`、`account` 為完整條件；不可僅以 `winbets` 或 `restday` 條件查詢
- **機器人排除**：結算或統計時，應先從 `member` keyspace 的 `gamerobots` 過濾出已啟用的機器人；本服務在查詢 `predictbets` 或 `betpool_bets` 時，若涉及帳號列表，須排除 `enabled = 3` 的機器人帳號
- **計算日誌檢查**：執行週報計算前，必須檢查 `calculatelog.done = 1` 以跳過已完成的週期；只處理 `done = 0` 的週
- **殺手帳號查詢**：查詢 `killeraccounts_BK` 時，需以 `lid`（聯賽）和 `cid`（週期）作為分割鍵條件；不可全表掃描

### 不可回傳欄位

- **betpool_bets.betzcoin**：投注金額為敏感財務數據，對外 API 不得回傳；僅可回傳獲利點數 (`profitzcoin`) 或輸贏結果
- **authkey**：若任一表（如 `predictbets_%s`）中存在關聯驗證金鑰，對外 API 必須脫敏或排除，不得明文輸出

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter keyspace — `accounts_*` 系列 | reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |
| Cassandra pricecenter keyspace — `actionlog` | writer | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **accounts_\***（所有供應商帳號表）：本服務**僅有讀取權限**，不得進行 INSERT、UPDATE 或 DELETE。帳號建立、啟用停用、密碼修改等一律由 PriceCenterService 或其他授權服務處理。
- **actionlog**：僅供記錄與預測結果結算、排名更新、機器人操作等關鍵業務動作相關的審計日誌。寫入後即**不可變更亦不可刪除（Immutable）**，且每筆記錄必須包含：
  - `date`：分區鍵（日期），不得為空。
  - `addtime`：精確記錄時間（聚簇鍵）。
  - `user`：執行操作的使用者帳號（聚簇鍵，不得為空）。
  - `gametype`：遊戲類型（聚簇鍵，若無遊戲類型可填預設值但不得留空）。
  - `actionclass`、`action`：動作分類與動作名稱，均為必填。
  - `detail`：需為合法 JSON 字串，內容只允許存放結構化摘要，**嚴禁**放入明文密碼、完整手機號、授權金鑰等敏感個資。

### 讀取規則

- **帳號狀態驗證**：查詢特定供應商帳號時，必須以 `account` 為主鍵進行精確查詢，不得全表掃描。判斷帳號是否可用時，應檢查 `enabled = 1` 且 `closetime` 為空或大於當前時間（若定義為停用時間）。
- **處理器資訊解讀**：`handler` 欄位為 `map<text,text>`，讀取時須確認所需 key 存在；若某 key 缺失應採用預設行為，而非直接 panic。
- **操作日誌回溯**：查看歷史操作記錄時，必須指定 `date` 分區鍵，並搭配至少一個聚簇鍵條件（如 `addtime` 範圍或 `user`），嚴禁跨分區、無範圍的全表掃描。

### 不可回傳欄位

- **password**：任何 API 回應（包含內部傳遞的結構）都不得攜帶明文密碼；僅可傳遞帳號識別碼或脫敏 Token。
- **phone**：電話號碼屬個人敏感資訊，對外 API 須進行脫敏（例如隱藏中間四位）或直接略過不輸出。

---

## newlottery

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| newlottery | reader / writer | Schema：[db/newlottery.json](../../db/newlottery.json) · 語意：[db/newlottery-detail.md](../../db/newlottery-detail.md) |

### 寫入限制

- **ChampionshipWallet.Balance**：僅由預測結算邏輯（派獎、退款、調整）更新，不可直接 SET 或手動修改。
- **ChampionshipWallet.LastUpdateTime**：由系統在更新 Balance 時自動設為當前時間，不允許人工寫入。
- **ChampionShipWallet_Transactions.ID** / **AddTime**：由資料庫自動產生（自增 / 時間戳），不得由應用層手動賦值。
- **ChampionShipWallet_Transactions.Point**：僅由結算邏輯根據玩家預測結果與賽事規則計算後寫入（正為獎勵，負為扣款），必須與錢包 Balance 變動保持原子性；不可直接 UPDATE。
- **ChampionShipWallet_Transactions.T_Type**：必須為預定義的交易類型枚舉（例如 0: 投注扣點、1: 派獎、2: 退款、3: 人工調整），由結算流程指定；不可隨意賦值。
- **ChampionShipWallet_Transactions.T_Detail**：交易描述僅供記錄，不能作為業務邏輯的判斷依據；內容不得包含個人隱私資料。
- **CoinWallet.Balance**：僅由結算邏輯更新，禁止外部 API 直接寫入。
- **CoinWallet.LastUpdateTime**：自動維護，不可手動介入。
- **CoinWallet_Transactions.T_ID** / **AddTime**：自動生成，不可由應用程式設定。
- **CoinWallet_Transactions.Coin**：僅由結算邏輯計算後寫入（正為增加，負為消耗），須與 CoinWallet.Balance 變動同步，不得單獨修改。
- **CoinWallet_Transactions.T_Type**：必須使用定義好的交易類型碼（如預測投注、派彩、退款），由業務層設定。
- **CoinWallet_Transactions.T_UID**：關聯唯一業務單號（如預測單號、訂單號），僅在建立交易時寫入，不可事後篡改。

### 讀取規則

- **錦標賽餘額查詢**：查詢 `ChampionshipWallet` 必須以 `Account` + `CID` 為完整條件（若 Account 或 CID 為分區鍵，須提供兩者），不可只靠其中之一或全表掃描。
- **錦標賽交易記錄**：查詢 `ChampionShipWallet_Transactions` 須提供 `CID` 和 `Account`（分區鍵），並可搭配 `AddTime` 範圍過濾；嚴禁跨 CID 或跨帳號的無鍵掃描。
- **代幣餘額**：查詢 `CoinWallet` 須以 `Account` 精確查詢，禁止全表掃描。
- **代幣交易記錄**：查詢 `CoinWallet_Transactions` 必須以 `Account` 為分區鍵，並可加上 `AddTime` 或 `T_Date` 範圍；不得只靠 `T_Type` 或 `T_UID` 進行無分區鍵的查詢。
- **結算前檢查**：在進行派獎或退款前，須讀取對應的錢包餘額（`ChampionshipWallet.Balance` 或 `CoinWallet.Balance`）以確保餘額足夠或狀態正確，並在同一事務中完成交易記錄寫入。

### 不可回傳欄位

- **直接餘額**：對外 API 不得直接回傳 `Balance`（`ChampionshipWallet` / `CoinWallet`）或 `Point`、`Coin` 等金額欄位；若需在前端顯示，應透過專用的、脫敏的餘額接口，並確保最小化權限。
- **交易細節**：`T_Detail` 中若包含關聯用戶資訊（如對手帳號），應脫敏處理；不可在公開 API 中洩漏其他用戶的帳號。

---

## Redis

*本服務未直接使用 Redis；快取由上游服務（MemberService / GameService）管理。*

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 會員註冊/登入 | MemberService | member.gameusers 的 CRUD 由 MemberService 統一管理 |
| 錢包餘額查詢 | WalletService | 本服務僅寫入交易紀錄（WalletTransaction），不處理餘額計算 |
| 會員訂閱狀態驗證 | SubscriptionService | gamesublogs 查詢與訂閱有效性判斷由訂閱服務處理 |
| 比賽資料寫入（games_%s） | GameManager / DataFeed | predictresultservice 僅讀取比賽資料與結果，不負責寫入或更新比賽資訊 |

---

## 常見錯誤

- ❌ 直接 UPDATE betpool_bets.winlose 而未同步計算 profitpoint → ✅ 應透過 `PredictModeResult` 統一計算後一次寫入正確欄位
- ❌ 忽略 payout flag 重複派獎 → ✅ 派獎前必須檢查 `payout = false`，並在結算完成後設為 true
- ❌ 未過濾機器人導致統計失真 → ✅ 結算前須確認 `gamerobots.enabled != 3`；若從 `predictbets` 層面迴避，需另加 account 黑名單檢查
- ❌ 跨週期計算 `weeklyreport` 時未檢查 `calculatelog.done` → ✅ 應先查詢 `done = 1` 的週期後才執行彙總計算
- ❌ 以非主鍵條件查詢 `betpool_games`（例如只靠 starttime 範圍）→ ✅ 應以 `id` 為 partition key，避免 Cassandra 全表掃描
- ❌ 在操作日誌 `detail` 中直接放入原始使用者密碼或完整手機號 → ✅ `detail` 只能存放脫敏後的業務摘要；原始敏感資料不得以任何形式寫入 `actionlog`
- ❌ 對 `ChampionShipWallet_Transactions` 進行跨帳號或跨賽事的查詢 → ✅ 必須同時提供 `CID` 與 `Account`，確保查詢落在單一分區內
- ❌ 結算時直接加減 `ChampionshipWallet.Balance` 而不透過錢包交易記錄同步 → ✅ 每次變動都應先寫入對應交易表，並在更新餘額時確保兩者原子性