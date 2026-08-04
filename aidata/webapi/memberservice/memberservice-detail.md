# memberservice — DB 操作邊界

> 產出時間：2025-08-24 10:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member keyspace | owner | Schema：[db/member.json](../../db/member.json) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **authkey**：由 `Hash.HashAuthString(account)` 產生，註冊時寫入，不可變更
- **account**：註冊時寫入，格式為平台前綴 + 原始帳號（如 `E`+email hash、`A`/`G`/`D`/`L`/`X`/`P` + 平台 ID、`3rd_` + 合作夥伴帳號），不可變更
- **password**：註冊時須經 `Hash.HashPasswordString` 雜湊後寫入；變更密碼需舊密碼驗證或合作夥伴升級流程
- **email**：註冊時須驗證格式與黑名單網域（`forbidden_email_domains`）；合作夥伴用戶升級時可補填
- **status**：
  - 註冊時預設值依來源不同：一般為 `0`（未啟用），`uwin` 等特定來源自動設為 `1`（已啟用）
  - 僅管理 API / 驗證流程可修改（0=未啟用, 1=已啟用, 2=凍結）
  - 登入時須 `status=1`，未啟用或凍結帳號不可登入
- **rank**：註冊時預設 `1`；訂閱升級時可改為 `2`/`3`
- **memberships**（list）：訂閱 / 活動 / 至尊競賽獲獎時新增項目（格式如 `supreme_{gametype}_{lid}_{cid}`），不可手動直接寫入
- **focus_account** / **black_account** / **follow_account**（list）：僅使用者本人可透過對應 API 增刪；黑名單與關注清單互斥
- **lastactiontime** / **lastchecktime**：系統自動更新，不可手動寫入
- **showcode**：註冊時可選填推薦人代碼，寫入後不可變更
- **headshotpath**：僅透過上傳 API（`UploadType.HeadShot`）更新
- **appleinfos_game（Apple 登入相關）**：
  - `id`、`email`、`name` 僅由 Apple 登入流程寫入，不可手動修改
- **forbidden_email_domains**：僅管理 API 可新增、刪除禁止註冊的郵件網域；`name` 為唯一鍵
- **gamerobots**：僅管理 API 可設定機器人交易參數（`stoploss`、`takeprofit`、`enabled` 等）
- **gamesublogs**：由訂閱流程（含付款回呼）自動寫入，應用程式不應直接 INSERT
- **gameusers_banned**：僅管理封禁 API 可寫入，記錄封禁原因、罰金、結束時間
- **gameusers_recommend**：註冊時若攜帶推薦碼，由系統寫入推薦關係，不可手動新增或修改
- **gameuserviews**：唯讀資料，由其他服務（如統計分析）寫入，本服務不具備寫入權限

### 讀取規則

- **登入驗證**：
  - 須 `status=1`（已啟用），`status=0`（未啟用）或 `status=2`（凍結）拒絕登入
  - 驗證密碼需比對 `Hash.HashPasswordString` 雜湊值
- **推薦關係查詢**：
  - 關聯表 `gameusers_recommend`，以 `authkey`（推薦人）+ `regdate`（年月）+ `recommendaccount`（被推薦人）為複合鍵
  - 僅計算 `status=1` 的有效推薦
- **訂閱記錄查詢**：關聯表 `gamesublogs`，以 `authkey` + `subtime` + `tradeno` + `addtime` 為複合鍵
- **封禁記錄查詢**：關聯表 `gameusers_banned`，以 `authkey` + `addtime` 為複合鍵
- **機器人排除**：統計 / 報表查詢需排除 `gamerobots.account` 與 `memberships` 含 `admin` 的帳號
- **郵件網域黑名單**：註冊時需檢查 `forbidden_email_domains.name`，禁止匹配網域註冊
- **Apple 登入關聯**：查詢 `appleinfos_game` 以關聯 Apple ID，僅供內部使用

### 不可回傳欄位

- **password**：任何對外 API 皆不可回傳，僅用於內部驗證
- **authkey**：僅內部使用，對外以 account 或 token 識別
- **siteid**：第三方平台使用者 ID，僅內部關聯使用
- **appleinfos_game.id / email**：Apple 之隱私資訊，禁止直接暴露給前端

---

## stock

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| MySQL stock 資料庫 | owner / writer / reader | Schema：[db/stock.json](../../db/stock.json) · 語意：[db/stock-detail.md](../../db/stock-detail.md) |

### 寫入限制

- **Users.Account** / **Users.Password**：註冊時由 `Transfer` 服務寫入（`TransferStockRegisterValidate`），Password 須雜湊後儲存；變更密碼須驗證舊密碼
- **Users.Enabled**：註冊時預設 `0`，透過驗證流程（`RegisterValidate`）改為 `1`；管理員可凍結帳號（設為 `0` 或 `2`）
- **Users.Rank**：註冊時預設 `1`，訂閱升級（`UpdateUserRank`）時修改為對應等級（`2`/`3`），同時更新 `SubEndTime`
- **Users.SendAction / Phone / Email / ChatID**：使用者可透過訊息設定 API（`UpdateUserMessageInfo`）更新，Email 須符合格式且不與他人重複
- **Users.SubEndTime**：由訂閱系統自動寫入，不可手動修改
- **FavoriteStock / FavoriteBroker**：
  - 僅使用者本人可新增、刪除、修改分組（`Name`）與內容（`Value`，JSON 陣列）
  - 新增時自動生成 `ID`（自增），跨使用者不可存取
  - `Country` 預設 `tw`，可依市場需求設定
  - `Value` 必須為合法 JSON 陣列，例如股票代碼或券商代號列表
- **FavoriteRule**：
  - 僅使用者本人可新增、刪除、修改（`Name`, `Strategy`, `Value`, `NeedSend`, `FirstMatch`, `Industry`, `FilterMarket`, `Country`）
  - `Strategy` 對應系統規則表，不可超出已啟用的規則範圍
  - `Value` 為 JSON 陣列字串，需符合對應策略的參數格式（如 `'["投信","買超","5","1000"]'`）
- **MessageLog**：由通知發送模組自動寫入，禁止應用層直接 INSERT
- **SubLogs**：訂閱系統處理付款後寫入（`InsertUserSubLog`），記錄交易單號、方案、時間等，不可手動新增或修改
- **Options**：僅管理員可變更，用於系統開關或設定（`Value` JSON，`Enabled` 1/0）
- **Rules**：僅管理員可新增／修改，定義篩選規則（`Type`, `Indicator`, `Parameter` 等），使用者僅能引用已啟用的規則

### 讀取規則

- **登入驗證**：查詢 `Users` 時須 `Enabled=1`，比對 `Password` 雜湊值
- **用戶設定查詢**：一律以 `Account` 為條件，只能讀取本人資料（`FavoriteStock`, `FavoriteRule`, `FavoriteBroker` 等）
- **通知發送**：系統讀取 `Users` 的傳送方式（`SendAction`）與目標（`Phone`, `Email`, `ChatID`）決定推送渠道
- **訊息日誌查詢**：按 `Date`（日期）與 `Account` 檢索，區分不同發送活動
- **訂閱日誌**：按 `Account` 查詢，可依 `AddTime` 排序，供會員查閱歷史
- **系統規則／選項**：全域讀取，`Options` 與 `Rules` 僅參考 `Enabled=1` 的項目
- **自選股／券商列表**：前端依 `Country` 過濾相關市場資料

### 不可回傳欄位

- **Users.Password**：任何對外介面皆不可輸出
- **Users.Phone / Email**：回傳時須脫敏處理（部分遮罩）
- **FavoriteStock.Value / FavoriteRule.Value**：內部使用完整 JSON，對外可回傳，但應避免洩漏不相關用戶資料
- **MessageLog.TargetAddress**：可能含有完整信箱或電話，應限制於本人查詢

---

## newlottery

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| MySQL NewLottery 資料庫 | reader / writer | Schema：[db/newlottery.json](../../db/newlottery.json) · 語意：[db/newlottery-detail.md](../../db/newlottery-detail.md) |

### 寫入限制

#### 使用者與封禁

- **NewLotteryUsers**：
  - `Account`：註冊時由系統生成或使用者指定（須唯一），不可變更
  - `Password`：註冊時須雜湊後儲存；變更密碼需舊密碼驗證
  - `Email` / `Phone`：註冊時需格式驗證；`Phone` 可選填，但不可重複
  - `UserName`：可由使用者修改，不可為空
  - `Status`：註冊時預設 `0`（未驗證），經驗證流程改為 `1`（已啟用）；管理員可凍結為 `2`
  - `AddTime`：系統自動寫入，不可手動修改
  - `ID`：系統生成之唯一內部識別碼，不可變更
  - `HeadShotPath`：透過上傳 API 更新
  - `Contact_Info`（JSON，含 line/wechat/whatsapp）：使用者在個人資料設定中修改，須為合法 JSON
- **NewLotteryBanned**：
  - 僅管理 API 可停權使用者，寫入 `Account`、`UserName`、`EndTime`（yyyy-MM-dd HH:mm:ss）、`Description`
  - `AddTime` 由系統自動填入 Unix 秒

#### 錢包

- **CoinWallet.Balance**：
  - 僅可透過交易 API 進行點數增減，禁止直接 UPDATE 數值。
  - 餘額更新必須與 `CoinWallet_Transactions` 寫入在同一交易範圍內，確保事務一致性。
- **ChampionshipWallet.Balance**：
  - 須透過 `ChampionShipWallet_Transactions` 記錄後更新，不可直接修改。
  - 必須同時指定 `Account` 與 `CID`，不可跨 `CID` 合併或扣抵。
- **ChampionshipWallet.Account + CID**：
  - 組合必須唯一，同一使用者同一錦標賽只能存在一個錢包，重複建立應返回錯誤。
- **ChampionshipWallet.CID**：
  - 不可為空，寫入時必須提供有效的錦標賽標識（通常對應最高層級賽事週期）。
- **CoinWallet_Transactions** / **ChampionShipWallet_Transactions**：
  - 每一筆交易必須記錄 `Account`、`T_Type`、變動量（`Coin` / `Point`）、`T_Detail`，並確保與對應錢包餘額的事務一致性。
  - `T_UID`（僅 `CoinWallet_Transactions`）用於關聯外部業務單號（如兌換碼、轉帳對象），可為空；但若 `T_Type` 指示為轉帳或特定操作，則必須填入接收者帳號或唯一單號。
  - `Point`（或 `Coin`）可為正（充值）或負（消費），但不可為 `0`（無效交易）。
  - `T_Detail` 應包含人類可讀的交易描述，不可為空。
- **LastUpdateTime**：
  - 由系統自動更新，不可手動設定。

#### 通知與主題

- **NewLotteryNotificationTopics**：
  - 僅管理 API 可新增、修改主題（`ID`, `Names`, `Icon`, `Enabled`）
  - `Names`：多語系主題名稱，須至少包含 `zh-TW`
  - `UpdateTime` 系統自動維護
- **NewLotteryNotificationMessages**：
  - 由系統或管理 API 新增訊息，關聯 `TID`（主題 ID）
  - `Contents`、`Titles` 為多語系 JSON，寫入時需確保格式正確
- **NewLotteryBetPoolCommissions**：
  - 系統計算並自動寫入佣金記錄，不可手動新增或修改

#### 訂閱方案

- **NewLotterySubPlans**：
  - 僅管理 API 可建立或修改方案（`ID`, `UpdateTime` 等），詳細欄位依訂閱模組規範

### 讀取規則

#### 使用者與封禁

- **登入驗證**：以 `Account` 查詢 `NewLotteryUsers`，須 `Status=1`，並比對 `Password` 雜湊值
- **基本資料**：僅限本人查詢，回傳時應脫敏 `Phone` 及 `Email`
- **封禁檢查**：依 `Account` 查詢 `NewLotteryBanned`，判斷當前是否在封禁期間（`AddTime` ≤ 現在 ≤ `EndTime`）

#### 錢包

- **錢包餘額查詢**：
  - `CoinWallet`：以 `Account` 為主鍵，查詢時必須提供帳號。
  - `ChampionshipWallet`：必須同時提供 `Account` 和 `CID`，禁止僅用 `Account` 查詢並彙總跨 `CID` 餘額。
- **交易記錄查詢**：
  - `CoinWallet_Transactions`：預設依 `Account`、`AddTime` 降冪排列；可依 `T_Type` 過濾（類型代碼由 NewLotteryService 維護，如 1=門票,2=轉帳,3=買牌,4=賣牌,5=彩池獲利,7=儲值,8=VIP購買,77=其他）。
  - `ChampionShipWallet_Transactions`：預設依 `Account`、`CID`、`AddTime` 降冪排列，必須帶入 `CID` 條件；`T_Type` 過濾同前。
  - `T_Date`（`CoinWallet_Transactions`）為業務日期（通常等同 `AddTime` 的日期部分），可作為輔助篩選條件，但不能取代 `AddTime` 排序。
- **分頁**：所有交易查詢必須支援基於 `AddTime` 或 `ID` 的分頁，避免全表掃描。
- **資料權限**：僅限查詢本人錢包，禁止跨帳戶訪問。

#### 通知

- **通知主題與訊息**：依 `Enabled=1` 的主題關聯最新訊息，回傳給客戶端；訊息依 `AddTime` 降序

### 不可回傳欄位

- **NewLotteryUsers.Password**：禁止輸出
- **NewLotteryUsers.Contact_Info**：對外回傳時需脫敏（如隱去部分 ID）
- **NewLotteryUsers.Phone / Email**：回傳時應部分遮罩
- **NewLotteryBanned.Description**：可能包含敏感封禁原因，僅管理端可見完整內容
- **CoinWallet_Transactions.T_UID**：
  - 可能包含其他用戶帳號、轉帳接收者或內部單號，對外回傳時必須脫敏（如隱去部分字符），或僅限本人查看完整資訊
- **T_Detail**：
  - 交易明細可能包含內部操作參數或業務敏感信息，對外輸出時應過濾或簡化，避免洩漏系統邏輯
- **所有 `ID` 型主鍵**（非帳號欄位）：對外可用作排序游標，但無需暴露實際數值含義

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| 資料庫 games（多租戶分表：games_bk, games_bm, games_bs, games_ck） | reader | Schema：[db/games.json](../../db/games.json) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- 無。本服務僅讀取比賽資料，不具備任何寫入 games 表的權限，也不應實例化 UPDATE/INSERT/DELETE 操作。

### 讀取規則

- **比賽列表查詢**：必須依照 `gdate`（比賽日期）進行篩選，僅回傳今日或未來日期，歷史比賽僅供報表模組使用。
- **狀態過濾**：僅顯示 `status` 為 `PreGame`（未開始）或 `Live`（進行中）的比賽，`Final`（已結束）由歷史查詢 API 單獨提供。
- **聯賽隔離**：必須配合 `lid`（聯賽 ID）進行過濾，禁止跨聯賽混合查詢。
- **排序**：預設依 `gdate` 升序、`gtime` 升序。

### 不可回傳欄位

- **siteidmaps**：內部站點映射，包含第三方資料來源的原始識別碼與關聯細節，對外應轉換為統一比賽 ID，不可直接暴露。
- **create_at**：僅內部稽核使用，前端無需展示。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `editor_cache:{authkey}` | 編輯者登入時 | 序列化 `GameEditor`（含 `BlackAccounts`、`FocusAccounts`、`SubLogs`）；登出或 token 過期時 DEL |
| SET / GET | `login_track:{loginTrackId}` | 登入追蹤 | 記錄登入狀態與設備指紋；登入成功或失敗後寫入 Cassandra `logs.logintrack_{yyyyMM}` / `logs.loginfail_{yyyyMM}` |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 訂閱方案管理與付款處理 | SubscriptionService | 本服務僅記錄訂閱結果至 `gamesublogs` 或 `SubLogs`，不處理金流 |
| 錢包餘額與交易（遊戲／新樂透） | WalletService / NewLotteryService | 本服務不直接操作錢包扣款邏輯，僅在封禁等情境可能觸發 WalletService 扣款 |
| 至尊競賽週期與排名計算 | SupremeService | 本服務僅在獲獎時寫入 `memberships` |
| 排行榜使用者管理 | LeaderboardService | `Leaderboard.Users` 由 LeaderboardService 維護 |
| 股票行情、技術指標計算、通知發送排程 | StockService | 本服務僅儲存使用者收藏與規則，實際篩選與通知由 StockService 執行 |
| 新樂透會員管理 | NewLotteryService | 本服務不處理新樂透專屬欄位與邏輯 |
| 比賽資料（games 表）的建立、更新、狀態流轉 | GameService | 本服務僅限讀取，比賽新增、比分更新、狀態變更全由 GameService 負責 |

---

## 常見錯誤

- ❌ 直接 UPDATE `status=1` 啟用帳號 → ✅ 須透過驗證流程或管理 API，並記錄操作日誌
- ❌ 註冊時直接寫入明文密碼 → ✅ 須先經 `Hash.HashPasswordString` 雜湊
- ❌ 登入時僅檢查密碼正確 → ✅ 須同時驗證 `status=1`，否則凍結 / 未啟用帳號可繞過
- ❌ 使用 email 作為主鍵查詢 → ✅ 以 `authkey` 為主鍵，email 僅作索引輔助查詢
- ❌ 合作夥伴用戶升級時覆蓋 `site` / `siteid` → ✅ 升級時僅補填 `email` / `password`，保留原 `site` / `siteid` 關聯
- ❌ 在 `gameusers` 直接寫入 `memberships` 項目 → ✅ 由訂閱 / 活動 / 競賽服務觸發寫入
- ❌ 統計報表未排除機器人與管理員 → ✅ 須過濾 `gamerobots.account` 與 `memberships` 含 `admin` 的帳號
- ❌ 變更密碼未驗證舊密碼 → ✅ 一般用戶變更需舊密碼；合作夥伴升級例外
- ❌ 直接修改 `Stock.Users.Rank` 而不同時更新 `SubEndTime` → ✅ 須透過 `UpdateUserRank` 同步更新
- ❌ 在 `Stock.SubLogs` 手動新增記錄 → ✅ 應由訂閱付款流程自動寫入
- ❌ 未檢查 `Stock.Rules.Enabled` 或 `Options.Enabled` 就提供給使用者 → ✅ 前端與 API 僅顯示已啟用的規則與選項
- ❌ 直接 UPDATE `CoinWallet.Balance` 或 `ChampionshipWallet.Balance` → ✅ 一律透過交易 API 記錄 `_Transactions` 並更新餘額，確保帳務可追溯
- ❌ 跨 `CID` 合併錦標賽餘額 → ✅ `ChampionshipWallet` 以 `Account` + `CID` 為單位隔離，不可相互抵扣或加總
- ❌ 在 member 服務中嘗試寫入 games 表 → ✅ games 表為唯讀，任何新增、更新比賽狀態等操作應由 GameService 負責
- ❌ 新增 `NewLotteryUsers` 時忘記雜湊密碼 → ✅ 必須呼叫對應雜湊函式
- ❌ 回傳 `NewLotteryUsers.Contact_Info` 未脫敏 → ✅ 應隱去 line/wechat/whatsapp 等完整 ID 的一部分