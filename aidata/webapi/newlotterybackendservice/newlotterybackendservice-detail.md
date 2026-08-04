# newlotterybackendservice — DB 操作邊界

> 產出時間：2025-04-08 10:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member keyspace | owner / writer / reader | Schema：[db/member.md](../../db/member.md) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **gameusers.authkey**：僅註冊 API 可寫入，一經建立不可修改（主鍵）。
- **gameusers.password**：須經 BCrypt 或等效演算法雜湊後寫入，禁止明文儲存。
- **gameusers.email**：註冊時須檢查 `forbidden_email_domains`，禁止使用黑名單網域；已註冊後不可修改。
- **gameusers.status**：僅管理端或封禁流程可變更；值為 0 時帳號不可登入。
- **gameusers.memberships**：僅訂閱成功後由支付模組追加訂閱方案 ID（`list<text>` 僅 APPEND，不可覆寫）。
- **gameusers.renamecount**：每次改名時 +1，改名功能需檢查上限（具體限制見業務規則）。
- **gameusers.focus_account / follow_account / black_account**：僅用戶自行維護（加入/移除），後端 API 不可直接覆蓋整個列表；應使用專用 ADD/REMOVE 操作。
- **gameusers.signindate / signindays / gamecount**：由簽到服務或遊戲服務更新，不應由一般業務 API 直接寫入。
- **gameusers.lastactiontime / lastchecktime**：由系統自動更新（最後活動/檢查時間），不可手動修改。
- **gameusers.username / account / authkey**：`authkey` 為內部主鍵不可變；`account` 一般不可修改；`username` 可改名（受 `renamecount` 限制）。
- **gameusers_banned.authkey**：封禁時新增記錄（分區鍵），`endtime` 為空表示永久封禁。
- **gameusers_banned.addtime、description、endtime、username**：`addtime` 由系統寫入（封禁時間戳毫秒）；`description` 由管理員填寫封禁原因；`endtime` 可更新（提前解封），更新時僅允許延長或設定為空；`username` 為被封禁用戶的顯示名稱（管理端可指定）。
- **gamesublogs**：僅支付成功或訂閱變更時寫入（複合主鍵：authkey + subtime + tradeno + addtime），不可修改或刪除；`paymethod`、`paytype` 由支付回調寫入，不可事後變更。
- **gamerobots.account**：僅管理端新增機器人時寫入，主鍵不可修改。
- **gamerobots.enabled**：僅管理端可修改（0=停用，1=啟用）。
- **forbidden_email_domains.name**：主鍵，僅管理端可新增，不可修改或刪除（若需移除黑名單域名應由管理端執行 DELETE，但建議保留歷史記錄）。
- **forbidden_email_domains.addtime**：新增時寫入 Unix 毫秒時間戳（bigint），不可修改。
- **appleinfos_game.id、email、name**：僅第三方（Apple）登入成功後由認證流程寫入，一經建立不可修改（主鍵不可變）。
- **gameuserviews、gameuserviewsv2、gameusers_recommend**：本服務 **不寫入** 這些表，由統計服務或推薦服務維護。

### 讀取規則

- **登入查詢**：WHERE `email = ?` AND `status = 1`，狀態非 1（啟用）或在 `gameusers_banned` 中有未過期記錄者不可登入。
- **封禁檢查**：查詢 `gameusers_banned` WHERE `authkey = ?`，若 `endtime` 為空或大於當前時間則視為封禁中。
- **訂閱歷史**：查詢 `gamesublogs` WHERE `authkey = ?` ORDER BY `subtime DESC, tradeno DESC`（Cassandra 聚類鍵排序）。
- **機器人過濾**：查詢 `gamerobots` WHERE `enabled = 1` 取得啟用機器人清單，排行榜等需排除。
- **Email 黑名單**：註冊前 SELECT `name` FROM `forbidden_email_domains` WHERE `name IN (...)`，匹配者拒絕註冊。
- **第三方登入輔助查詢**：查詢 `appleinfos_game` 時需指定 `id`（主鍵），避免全分區掃描。
- **瀏覽次數查詢**：`gameuserviews` 必須指定 `year`（分區鍵），並可帶 `datetime` 與 `account` 聚類鍵縮小範圍；`gameuserviewsv2` 查詢時需指定 `year`, `gtype`, `lid`，並可指定 `account`。
- **推薦關係查詢**：查詢 `gameusers_recommend` 需以 `authkey`（被推薦人分區鍵）為條件，可設定 `regdate` 或 `recommendaccount` 範圍。

### 不可回傳欄位

- **gameusers.password**：任何 GET API 均不可回傳（包括個人資料、列表、排行榜等）。
- **gameusers.authkey**：內部使用主鍵，對外 API 使用 `account` 或 `email` 作為識別。
- **gameusers.lastchecktime**：系統內部檢查時間戳，不對外暴露。
- **gameusers_banned.authkey**：內部關聯用主鍵，對外回傳時不應暴露。
- **forbidden_email_domains.name**：域名黑名單為內部管理資料，不對外 API 回傳（僅於註冊時內部比對使用）。

---

## payment

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra payment keyspace | owner / writer / reader | Schema：[db/payment.md](../../db/payment.md) · 語意：[db/payment-detail.md](../../db/payment-detail.md) |

### 寫入限制

- **commissions_betpool_newlottery**：所有欄位（betpool、id、addtime、coin、ctype、source_cid、source_game、source_uid）均為**唯寫**，一經寫入不可修改或刪除（主鍵不可變更）；coin 僅由 BetPoolService 按其佣金計算邏輯寫入，不得由其他 API 直接操作。
- **paymethods_sport.enabled**：僅管理端 API 可啟用（1）或禁用（0）；names 多語言映射僅由管理介面維護，不可由前端使用者更新。
- **products_activity.price、quantity、status**：價格與庫存僅活動建立或後台調整時寫入，status 切換（0→1→2）需符合活動生命週期；quantity 更新為原子減量（不可直接 SET）。
- **products_activity_redeem_logs**：狀態（status）可由轉換流程（待處理→成功/失敗）更新；其餘欄位（site、activityevent、account、id、pid、addtime）**只寫一次**，不可修改。
- **rechargeplans_newlottery.amount、coin**：金額與贈送幣值一經上架不可修改（若需調整應停用舊方案（`enabled=0`）後新增）；currency 一旦設定不可變更；enabled 僅由管理端切換；starttime / endtime 僅在方案建立時設定，不支援動態延長。
- **reports_sport、reports_sport_recommend**：本服務 **不寫入** 這些表，由報表結算服務負責維護。

### 讀取規則

- **佣金累計查詢**：依 `betpool` 分組，WHERE `betpool = ?` 並 GROUP BY（或在 application 層彙總）`coin` 值，用於顯示該彩池總佣金金額；不得在無 `betpool` 過濾條件下全表掃描。
- **支付方式列表**：查詢 `paymethods_sport` 時需附加 `enabled = 1` 條件，僅回傳啟用的支付類型及對應語言名稱。
- **活動商品查詢**：查詢 `products_activity` 時，`status = 1` 為可顯示/可兌換商品；`quantity > 0` 為有庫存；下單兌換前須 SELECT FOR UPDATE 或透過應用層原子操作確保庫存正確。
- **兌換記錄查詢**：支援依 `account` (使用者) 或 `activityevent` (活動) 查詢，WHERE 條件至少包含 site；後台查詢可忽略 status 條件，前端則預設顯示全部但允許依 status 過濾。
- **充值方案列表**：查詢 `rechargeplans_newlottery` 時須附加 `enabled = 1` AND `starttime <= now()` AND `endtime >= now()`，僅回傳目前有效方案。
- **報表查詢**：`reports_sport` 依 `year` + `month` 組合主鍵查詢，用於後台統計；不可接受動態範圍（如無 `year` 條件）。`reports_sport_recommend` 相同規則。

### 不可回傳欄位

- **paymethods_sport.names**：內部多語言映射可回傳，但禁止單獨回傳原始 map（應依請求語言回傳對應值或全 map 但需過濾語言金鑰）。
- **commissions_betpool_newlottery.source_uid / source_cid**：對外佣金排行查詢時不可暴露來源使用者或客戶 ID，僅回傳彙總後的 coin 總和。

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra predict keyspace | owner / writer / reader | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **activities_cycles.site + activityevent + cid**：複合主鍵，一經建立不可修改（主鍵不可變更）。
- **activities_cycles.startdate / starttime / enddate / endtime**：週期時間僅在建立時設定，不支援事後延長或提前。
- **activities_record.site + eventname + account**：複合主鍵，一經建立不可修改；**winbets**（`list<text>`）僅可 APPEND 追加中獎注單 ID，不可覆寫整個列表。
- **activities_record.restday**：僅由系統每日排程（Cron Job）更新，使用者端不可寫入；值為 0 時該帳號即被視為活動資格已用盡。
- **activities_winneraccounts.site + activityevent + cid + account**：複合主鍵，寫入後不可刪除或修改；**rank、profitpoint、predictcount、winpercentage** 僅在排名結算時由系統寫入，管理端不可手動調整。
- **betpool_bets.gid + account + id**：複合主鍵，一經建立不可修改或刪除（Cassandra immutable 設計）；**betzcoin、profitzcoin** 不可事後修改，金額錯誤應透過新增沖正記錄處理。
- **betpool_games.id**：主鍵，不可修改；**payout** 僅能在結算成功時從 `false` 變更為 `true`，不可反向回退；**starttime / endtime** 僅在遊戲建立時設定，不支援動態延長。
- **betpool_games.winresult**：僅在遊戲結束且 `payout = true` 之前可設定；一旦 `payout = true`，winresult 不可再修改。
- **betpool_games.zcoinprice / feedrate / basicprofitzcoin / bonusprofitzcoin**：這些財務相關欄位僅在遊戲建立時設定，不可事後調整；若需修改應建立新遊戲並停用舊遊戲。
- **championships.GameType + ID**：C* 複合主鍵（GameType 為分區鍵，ID 為聚類鍵），一經建立不可修改；**CloseTime** 為計算值（推測為結束前兩天），由系統自動運算，不可手動寫入。
- **championships.Names、Leagues、Sell_Commission_Options**：collection 欄位（map/list），修改時應使用 ADD / REMOVE 操作避免全量覆寫。
- **killeraccounts_BK、calculatelog**：本服務 **不寫入** 這些表，由其他服務負責。

### 讀取規則

- **活動週期查詢**：查詢 `activities_cycles` 時至少指定 `site` + `activityevent`，避免全表掃描；若需依時間過濾，應以 `startdate >= ?` 搭配 `enddate <= ?` 作為應用層過濾（Cassandra 不支援非主鍵欄位的全域範圍查詢）。
- **遊戲列表查詢**：查詢 `betpool_games` 時，前端遊戲大廳 API 應附加 `status = 1`（進行中）條件；`viponly = true` 的遊戲須在用戶為 VIP 時才可回傳；`hot = true` 為熱門篩選標記，可獨立使用。
- **下注記錄查詢**：查詢 `betpool_bets` 時必須指定 `gid`（遊戲 ID），不可無條件查詢；依 `account` 查詢個人注單時須同時指定 `gid`；`winlose` 可作為過濾條件（如查已贏注單），但不可為空條件。
- **活動贏家排行查詢**：查詢 `activities_winneraccounts` 時須指定 `site` + `activityevent` + `cid`；前端顯示可依 `rank` 排序（聚類鍵排序）或依 `profitpoint DESC` 排序（應用層）。
- **賽事查詢**：查詢 `championships` 時須指定 `GameType`（分區鍵）；前端開放查詢應附加 `Status = 1`（進行中）條件；`StartTime >= ?` 與 `EndTime <= ?` 可作為應用層過濾，但不可單獨作為全域條件。
- **歷史資料範圍**：`betpool_bets` 與 `activities_record` 可能隨時間累積大量資料，查詢時應加入 `addtime >= ?` 或 `updatedate >= ?` 時間範圍，避免全分區掃描。
- **殺手帳號查詢**：查詢 `killeraccounts_BK` 必須指定 `lid`（分區鍵），可選 `cid`、`account` 過濾。
- **計算週期狀態**：查詢 `calculatelog` 使用主鍵 `weekid`，用於檢查指定週是否已完成計算（`done = 1`）。

### 不可回傳欄位

- **betpool_bets.id**（注單內部 ID）：前端使用者無需知道系統內部注單唯一識別碼，回傳時應使用業務層產生的訂單號。
- **betpool_bets.profitzcoin**（盈利金額）：下注清單回傳時僅回傳總金額（betzcoin）與輸贏結果（winlose），盈利計算由前端依結果自行推算或透過專門的獲利 API 查詢。
- **activities_winneraccounts.account**（中獎帳號）：排行榜公佈時僅回傳暱稱（使用者顯示名稱），不可直接暴露 account 主鍵值；管理後台可回傳但須左側 ACL 審核。
- **championships.CloseTime**（計算欄位）：為內部系統運算用（推測用途：截止時間減兩天），不對外公開。

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter keyspace (accounts_AU8, accounts_Fortuna888, accounts_HGA, accounts_HGA2, accounts_KKK, accounts_KU, accounts_NK, accounts_Panda, accounts_TG, accounts_TG999, actionlog) | reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- 本服務**不直接寫入** pricecenter 的任何表；所有寫入（包含帳戶資料、操作日誌）由上游服務（如 IMemberProvider、PaymentService、後台管理、pricecenter 自身排程）處理。
- **password**：若未來本服務因業務擴展需寫入，則須強制使用 BCrypt 或等效演算法雜湊，禁止明文儲存。
- **account**：所有 accounts_* 表的主鍵，一經建立不可修改；新增時應由上游服務保證唯一性。
- **enabled**：僅可透過停用／啟用帳號流程寫入（0／1），不可隨意切換；本服務查詢時必須強制過濾 `enabled = 1`。
- **closetime**：僅在帳號關閉時由系統設定為時間戳，不可手動填入或修改；若值非空且小於當前時間即視為已關閉帳號。
- **phone、handler**：若需寫入，phone 須遵循個資保護規範，handler 僅允許管理端或帳號服務維護，不可由終端用戶修改。
- **actionlog 寫入控制**：本服務目前不寫入 actionlog；若未來需記錄操作軌跡，則寫入時 `date`（分區鍵）、`addtime`、`user`、`gametype` 必須齊全，`detail` 須為 JSON 並避免儲存密碼、手機號等明文敏感資料；且記錄操作必須與業務動作在同一請求內完成，不支援事後修改。

### 讀取規則

- **帳號有效性檢查**：所有 accounts_* 表的查詢必須附加 `enabled = 1` 條件，確保僅啟用帳號可用於業務操作（如下注、登入）。同時應過濾 `closetime`（若值為非空且小於現在，則視為已關閉，需排除）。
- **主鍵強制**：任何 accounts_* 讀取都必須以 `account`（主鍵）為條件，禁止全表或非主鍵掃描。
- **跨廠商查詢**：若需一次查詢多個廠商帳號狀態（如 AU8 與 HGA），應分別以 `account` 分別查詢各自的表，並在應用層彙整，禁止跨分區 JOIN 或 UNION。
- **actionlog 查詢限制**：查詢 actionlog 時必須指定 `date` 分區鍵，可附加 `user`、`gametype` 等聚類鍵縮小範圍；禁止無 `date` 條件的全表掃描。後台審計用 API 方可讀取，前端用戶介面不應直接暴露操作日誌。
- **敏感操作追蹤**：讀取 actionlog.detail 時，應在應用層過濾或遮蔽如密碼、電話等敏感欄位後再回傳給具權限的後台管理員。

### 不可回傳欄位

- **password**：任何對外 API 一律不可回傳（含個人資料、列表、日誌）。
- **phone**：涉及個人隱私，前端 API 不回傳（後台管理介面可依角色權限決定是否遮蔽）。
- **handler**：內部處理器配置映射（map<text, text>），可能包含內部標記或路由資訊；對外回傳時應移除，或僅回傳業務允許的 key（若無明確需求則不應回傳）。
- **actionlog.detail**：操作詳情 JSON 可能蒐集敏感欄位（如帳號、金額變動），對前端一律屏蔽；後台審計存取時需以權限控制並脫敏處理。

---

## newlottery

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra newlottery keyspace | owner / writer / reader | Schema：[db/newlottery.md](../../db/newlottery.md) · 語意：[db/newlottery-detail.md](../../db/newlottery-detail.md) |

### 寫入限制

- ChampionshipWallet.Balance：僅由錦標賽結算流程（如 BetPoolWinner 計算 ProfitPoint 後）進行加減，不可透過 API 直接設定；需以原子操作（如 UPDATE SET Balance = Balance + ?）確保並發安全。
- ChampionshipWallet.CID 與 Account：建表時組合寫入，一經建立不可修改（作為錢包唯一標識）。
- ChampionShipWallet_Transactions：所有欄位僅允許新增，不可修改或刪除（immutable 設計）。
  - Point：正數為錦標賽積分增加，負數為支出；交易時必須與實際變動一致。
  - T_Type：由業務邏輯定義（例如 1:獎勵, 2:消費 ...），不可接受未定義值。
  - T_Detail：存放交易細節，對於特殊類型（如彩池獲利）可為 JSON 格式，寫入前須序列化並確保不包含明文密碼或個人隱私。
  - AddTime：由系統在 INSERT 時寫入當前時間戳。
- CoinWallet.Balance：僅由代幣相關業務（如彩池獲利轉換為 Coin，對應 ProfitCoin）更新，需使用 UPDATE ... SET Balance = Balance + ? 並在應用層驗證餘額非負；禁止直接覆寫。
- CoinWallet.Account：主鍵，建立錢包時設定，不可修改。
- CoinWallet_Transactions：僅可新增，不可修改或刪除。
  - Coin：為代幣變動量，正加負減，數值須與業務動作相符。
  - T_Date：寫入業務日期（可能不同於 AddTime）。
  - T_Detail：記錄交易詳情，可能為 JSON，依 T_Type 對應不同結構（如 ticket info, bet business info）。
  - T_Type：交易類型代碼，需正確定義（例如 1:門票, 3:買賣牌, 7:儲值, 77:其他）。
  - T_UID：關聯的唯一標識（如訂單號），可用於防重或稽核。

### 讀取規則

- ChampionshipWallet 查詢：必須指定 Account 與 CID（若 Application 設計為組合主鍵），避免全表掃描；查詢單一帳號所有錦標賽錢包時需限定 Account，返回該會員參與的各錦標賽餘額。
- ChampionShipWallet_Transactions 查詢：必須過濾 Account 或 CID，並可搭配 AddTime 範圍查詢；依時間排序可使用 AddTime DESC。
- CoinWallet 查詢：依 Account 主鍵直接取得單一錢包資訊；若需批量查詢（如排行榜），應使用 IN 或分批查詢，不可無條件全表掃描。
- CoinWallet_Transactions 查詢：建議指定 Account 和時間範圍（AddTime 或 T_Date）；查詢特定交易類型可加上 T_Type；不可無 Account 過濾的跨用戶查詢（除非管理後台且限制分頁大小）。
- 對外 API 回傳錦標賽錢包時，需確保僅當前授權用戶可查詢自己的餘額，不可暴露他人紀錄。

### 不可回傳欄位

- ChampionshipWallet.ID：內部自增主鍵，對外 API 改用 Account + CID 組合標識。
- ChampionShipWallet_Transactions.ID：內部交易 ID，不應暴露。
- CoinWallet_Transactions.T_ID：內部主鍵，不回傳。
- T_Detail 中若包含其他用戶的 Account 或敏感資訊（如金額細節），在非必要時應脫敏或移除。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `session:{authkey}` | 登入成功後建立 | 7200秒（2小時），每次 API 呼叫刷新 TTL |
| SET / GET | `user_cache:{authkey}` | 查詢 `gameusers` 後快取 | 300秒（5分鐘），更新個人資料時主動 DEL |
| SET / GET | `forbidden_domains` | 服務啟動時載入黑名單 | 3600秒（1小時），或管理端更新時主動刷新 |
| SET / GET | `robot_list` | 服務啟動時載入機器人清單 | 3600秒（1小時），或管理端更新時主動刷新 |
| DEL | `session:{authkey}` | 登出或 Token 失效時 | 主動刪除 |
| SET / GET | `paymethods:{lang}` | 查詢 `paymethods_sport` after `enabled = 1` | 600秒（10分鐘），管理端更新支付方式時主動 DEL |
| SET / GET | `recharge_plans` | 查詢有效充值方案後 | 300秒（5分鐘），管理端更新方案時主動 DEL |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 訂單建立與支付流程 | PaymentService / 第三方金流 | 本服務僅在支付成功後寫入 `gamesublogs` 與更新 `memberships` |
| 金幣錢包交易記錄 | WalletService / CoinWallet 模組 | `gameusers.account` 僅作為關聯鍵，金幣增減由專責服務處理 |
| 投注池抽成計算 | BetPoolService | `betpoolcommissions` 由投注結算服務寫入，本服務僅查詢累積金額 |
| 錦標賽門票驗證 | ChampionshipService | `gameusers` 中 `memberships` 清單僅記錄訂閱資格，門票核銷由錦標賽服務負責 |
| Apple / Google 第三方登入驗證 | 各平台 SDK / Gateway | 本服務僅儲存 `appleinfos_game`，Token 驗證由閘道器或前端完成 |
| 活動商品庫存跨服務事務 | 無（最終一致性） | `products_activity.quantity` 減量與 `products_activity_redeem_logs` 寫入不保證原子性，需由業務層處理補償 |
| 預測活動獎金派發 | CoinWallet / WalletService | `activities_winneraccounts` 僅記錄排名與積分，實際金幣增減由錢包服務處理 |
| 投注池結算與派彩 | BetPoolService | `betpool_games.payout` 與 `betpool_bets.winlose` 由投注池結算服務更新，本服務僅查詢結果 |
| 賽事門票購買與核銷 | ChampionshipService / TicketService | `championships.Ticket_Fee_Coin` 僅為費用定義，門票購買與使用由專責服務完成 |
| 活動資格天數（restday）扣減 | 每日排程 Cron Job | `activities_record.restday` 由獨立排程每天減少，非即時 API 觸發 |
| 佣金計算與幣值轉換 | PaymentService / Currency 模組 | `betpool_bets.betzcoin / profitzcoin` 以 zcoin 為單位，幣值轉換與手續費由外部服務處理 |
| **第三方遊戲廠商帳戶管理** | IMemberProvider / PaymentService / 後台管理 | pricecenter 中的 accounts_* 表由各廠商帳戶服務負責寫入與維護，本服務僅讀取帳號狀態與基本資訊 |

---

## 常見錯誤

- ❌ 直接 UPDATE `gameusers.status = 0` 封禁用戶 → ✅ 必須同時在 `gameusers_banned` 新增記錄並註明原因與結束時間
- ❌ 註冊時未檢查 `forbidden_email_domains` → ✅ 先查詢黑名單，匹配時拋出 `400 Invalid Email Domain`
- ❌ 登入查詢時僅檢查 `email` 與 `password` → ✅ 必須加上 `status = 1` 條件，避免封禁用戶登入
- ❌ 改名時直接 UPDATE `gameusers.username` → ✅ 需同時 +1 `renamecount` 並檢查是否超過上限（通常 3 次）
- ❌ `gamesublogs` 使用 DELETE 刪除歷史記錄 → ✅ Cassandra 複合主鍵不支援部分刪除，且訂閱日誌需永久保留供稽核
- ❌ 查詢 `gameusers_banned` 時未判斷 `endtime` → ✅ 空值或大於當前時間才為「封禁中」，否則為「已解封」
- ❌ `memberships` 使用 SET 覆寫整個列表 → ✅ 使用 `list APPEND` 操作僅追加新訂閱 ID，保留歷史
- ❌ Redis `session:{authkey}` 過期後仍嘗試查詢 Cassandra → ✅ 優先檢查 
...(truncated