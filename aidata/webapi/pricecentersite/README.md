# PriceCenterSite WebAPI

- **Git Repository**：https://git.zbdigital.net/biz/pricecentersite.git
- **PortainerKey**：PRD_Docker_Swarm|container|pricecentersite

## 職責

作為主要前端站台的 API 服務，負責整合全平台大部分業務邏輯，包含賽事資料、會員、預測、社群文章、商城商品、活動、支付訂閱、新聞、廣告、反饋、合作夥伴及第三方站台等功能。此服務是前端應用程式與網站的主要對接接口，同時也負責處理跨越多個資料庫的讀寫操作。

## 技術棧

- **框架**：ASP.NET Core 8（.NET 8.0）
- **資料庫**：
  - Cassandra：`member`、`payment`、`predict`、`community`、`product`、`pricecenter`、`feedback`、`news`（唯讀）、`logs`（由 ECFramework 管理）
  - Redis（快取）
  - MySQL：`stock`
- **本地快取**：System.Runtime.Caching（MemoryCache）
- **驗證**：ECCore 3.0.2 內建機制（authKey）
- **其他重要 NuGet 套件**：
  - `MeiliSearch` 0.18.0（搜尋引擎）
  - `AdvertisingModels` 0.0.6
  - `MemberModels` 1.1.9
  - `PaymentModels` 2.0.8
  - `GameDataModels` 2.0.198

## 本服務對各 Keyspace 的操作權限

- **member**：reader / writer（讀寫）
- **payment**：reader / writer（讀寫特定後台管理表，如 `rechargeplans_newlottery`、`subplans_sport`；對其他表唯讀）
- **predict**：writer / reader（讀寫；但遊戲結算與活動排名由 `predictresultservice` 等負責）
- **community**：reader / writer（前台唯讀；後台管理 API 可寫入）
- **product**：writer（讀取商品資訊，寫入活動商品相關表）
- **pricecenter**：reader（唯讀）
- **feedback**：reader（唯讀，查詢主題與常見問題）
- **news**：reader（唯讀）
- **stock（MySQL）**：owner（此服務直接管理 `stock` 資料庫）
- **Redis**：reader / writer（讀寫，用於驗證碼頻率控制、會員活動時間、回應快取、反饋主題快取等）

## 資料庫重要 Table

### Cassandra

| Table 名稱 | 用途 | 重要欄位 |
|-----------|------|---------|
| member.gameusers | 會員主要資料 | authkey (PK), email, password, status, memberships，社交清單 (focus/black/follow_account) |
| member.gamesublogs | 訂閱交易紀錄 | authkey, subtime, subendtime, autosub, tradeno |
| member.gameusers_banned | 會員封禁記錄 | authkey, endtime, description |
| member.appleinfos_game | Apple 第三方登入資訊 | id (PK), email, name |
| member.forbidden_email_domains | 禁止註冊的 Email 域名 | name (PK) |
| member.gameusers_recommend | 會員推薦關係 | authkey, recommendaccount, regdate |
| member.gamerobots | 機器人設定 | account (PK), enabled, stoploss, takeprofit |
| payment.products_activity | 活動商品 | site, activityevent, id, price, quantity, status, names |
| payment.products_activity_redeem_logs | 活動商品兌換記錄 | site, activityevent, account, pid, status |
| payment.rechargeplans_newlottery | 充值方案 | id, amount, coin, currency, enabled, starttime, endtime |
| payment.subplans_sport | 訂閱方案 | id, amount, currency, effectivelength, startdate, enddate, enabled, names |
| payment.paymethods_sport | 支付方式 | paytype, mode, enabled, names |
| payment.reports_sport(share) | 分潤與推薦報表 | year, month, finishing, shareamount 等 |
| predict.betpool_games | 彩池遊戲 | id, hot, payout, status, viponly, betoptions, winresult |
| predict.betpool_bets | 彩池投注 | gid, account, betoption, betzcoin, profitzcoin, winlose |
| predict.activities_cycles | 活動週期設定 | site, activityevent, cid, startdate/enddate |
| predict.activities_winneraccounts | 活動贏家排行榜 | site, activityevent, cid, account, rank, profitpoint |
| predict.activities_record | 會員活動記錄 | site, eventname, account, restday, winbets |
| community.newlottery_forums | 社群論壇 | id, country_code, icon, names, status |
| product.products_store | 商城商品 | pclass, pid, pnames, price, status, quantity |
| product.product_store_redeem_logs | 商城兌換記錄 | pclass, account, address, phonenumber, status |
| pricecenter.accounts_{site} | 各品牌站台帳號 | account (PK), password, enabled, closetime, phone, username |
| feedback.feedbacks_sport / feedbacks_stock | 使用者反饋 | id, account, email, problem, respcontent, status |
| feedback.businessmessages | 商業合作訊息 | site, id, sendermail, sendcontent, respcontent, status |
| feedback.questions_sport / questions_stock | 常見問題 FAQ | id, tid, question, answer, enabled, sort |
| feedback.topics_sport / topics_stock | 反饋主題 | id, name, enabled, sort |

> **注意**：`products_activity` 和 `products_activity_redeem_logs` 在 `payment` 和 `product` keyspace 中皆存在，PriceCenterSite 主要讀取 `payment` keyspace 中的對應表格（需人工確認：是否存在跨 keyspace 讀寫情況）。

### MySQL

| Table 名稱 | 用途 | 重要欄位 |
|-----------|------|---------|
| stock.users | 股票站台帳號 | Account (PK), Password, Enabled, SubEndTime |
| stock.sublogs | 股票站台訂閱記錄 | Account, TradeNo, SubID, SubEndTime |
| stock.favoriterule | 使用者最愛規則 | User, Country, NeedSend, FirstMatch |
| stock.favoritestock | 使用者收藏股票 | User, Country, StockID |
| stock.messagelog | 訊息發送記錄 | Account, Date, SendStatus, MsgContent |
| stock.rules / stock.options | 系統規則與選項設定 | Enabled（前台查詢需過濾 Enabled=1） |

## 其他重要 Table
- **Cassandra logs keyspace**：應用程式操作日誌（由 ECFramework 管理）
- **Redis（快取）**：
  - `AuthToken:{email}`：活動驗證碼頻率控制（TTL 300s；60 秒內不可重複發送）
  - `GameUserLastActionTime:{authKey}`：會員最後活動時間（TTL 300s；減少直接寫入 Cassandra 的頻率）
  - `GameUser:{authKey}`：會員資料快取（會員資格、訂閱狀態變更時，必須主動 DEL，不可只靠 TTL 過期）
  - `ResponseCacheInfo:{cacheKey}`：API 回應快取（如廣告、公告，TTL 300~600s）
  - `feedback_topics:{site}`：反饋主題清單快取（TTL 600s）
  - `feedback_faq:{site}:{tid}`：常見問題快取（TTL 300s）
  - `feedback_user_last_submit:{account}`：防重複提交回饋（TTL 60s）
  - `paymethods:enabled:{site}`：啟用中的支付方式快取（TTL 10 分鐘；`enabled` 狀態變更時，管理服務必須執行 `DEL` 使其失效）
  - **後端請求使用 `System.Runtime.Caching`（MemoryCache）進行本地快取**，前台回應快取使用 Redis `ResponseCacheInfo:{cacheKey}`

## 其他參考文件
- **服務 DB 操作邊界**：`pricecentersite-detail.md` — 各 keyspace 的操作權限、讀寫規則、不可回傳欄位
- **業務需求文件**：Confluence documents (`documents.md`) — 特定 API 業務規則
- **場景流程文件**：`scenario-flows/` 目錄 — 關鍵業務場景（登入、註冊、預測、兌換等）的詳細流程與規則
- **DB 結構文件**：`db/` 目錄 — Cassandra 及 MySQL 各 keyspace/DB 的 schema 與使用細節

## 目錄結構與命名規範
- `PriceCenterSite/Controllers/`：包含所有 API Controller（Activity, Adv, Community, Game, GameLive, Member, News, Notification, Partner, Payment, Predict, Store, System, ThirdPartySite, TradeExchange, VLSport, Feedback 等）
- `PriceCenterSite.Interface/`：領域服務介面（IActivityService, IPaymentService 等）
- `PriceCenterSite.Model/`：DTO 與請求/回應模型
- `PriceCenterSite.DomainService/`：領域服務實作（需人工確認是否獨立專案或位於主專案內）
- 服務層命名慣例：`{Domain}Service` 或 `{Domain}Provider`；文檔中若無確切證據，會標記「需人工確認」

## 驗證與授權
- 所有需要授權的 API 皆使用 `ECCore 3.0.2` 的 `authKey` 機制
- 部分 API（如活動商品列表、廣告、賽事查詢）可讓未登入使用者訪問
- VIP 權限透過 `gameusers.memberships` 與 `gamesublogs.subendtime` 組合判斷，而非單一角色。**必須同時檢查 `memberships` 清單非空及對應的訂閱 (`gamesublogs.subendtime`) 是否過期。**
- 任何 API 回應都不得包含 `password`、`authkey`（登入成功時可回傳一次）、`tradeno`、會員完整地址/電話等敏感個資。

## 資料庫與快取策略
- **Cassandra**：提供會員、預測、支付、社群、產品、反饋、新聞等業務所需的資料儲存。本服務對 `payment` keyspace 主要是唯讀，僅可寫入特定的後台管理表（如 `rechargeplans_newlottery` 和 `subplans_sport`）。對 `news` keyspace 為唯讀。
- **MySQL（stock）**：主要用於股票相關功能（`stock` DB），如使用者、訂閱記錄、訊息日誌、規則設定等。此 DB 由 PriceCenterSite 直接管理。
- **Redis**：用於短期快取，包含頻率控制 (`AuthToken:{email}`)、會員最後活動時間 (`GameUserLastActionTime:{authKey}`)、會員資料 (`GameUser:{authKey}`)、API 回應快取 (`ResponseCacheInfo:{cacheKey}`)、支付方式 (`paymethods:enabled:{site}`)、反饋主題 (`feedback_topics:{site}`) 及 FAQ (`feedback_faq:{site}:{tid}`) 等。
- **System.Runtime.Caching**：用於 API 層本地快取，由 `RequestCacheAttribute` 管理，快取時間依 API 設定（10-900 秒不等）。

## 關鍵場景與高風險區域
- **兌換流程（活動/商城）**：活動商品兌換必須使用 Cassandra LWT (`IF quantity >= ?`) 原子扣減庫存，禁止先讀後寫。所有對一般用戶的查詢都必須加上 `status=1` 和 `quantity>0` 條件。商城商品兌換的收件人地址、電話等個資，**僅限本人或後台查看，對外 API 必須遮蔽**。
- **登入與註冊**：多管道（Email、第三方），嚴格過濾密碼/授權金鑰不可外洩；封禁檢查不分管道。註冊時必須檢查 `forbidden_email_domains`；密碼必須經雜湊處理（bcrypt/PBKDF2）。
- **社交操作**：`focus_account`、`black_account` 等 list 欄位僅能透過「新增/移除」原子操作，**嚴禁直接覆蓋**。`black_account` 與 `focus_account` 互斥。
- **支付回調**：需驗證來源，計算續訂時間、更新會員等級與到期日時不可遺漏 Redis 快取清除。`memberships` 欄位僅可 APPEND，不可直接 SET。
- **預測投注**：查詢熱門預測遊戲時需嚴格過濾 `hot`、`payout`、`status`、`endtime`，並根據使用者 VIP 身份過濾 `viponly` 遊戲；VIP 判斷須同時檢查 `memberships` 與 `gamesublogs.subendtime`。投注寫入 `betpool_bets` 時**不可預先寫入 `profitzcoin` 或 `winlose`**，這些欄位僅由結算服務回填。
- **商品價格不可部分更新**：修改 `products_store` 的 `price` 或 `products_activity` 的 `price` 時，需整筆重建商品記錄，不可直接 UPDATE，以避免歷史訂單金額不一致。

## 開發與維運注意事項
- **禁止回傳敏感欄位**：任何 API 不可回傳 `password`、`authkey`（登入時除外）、交易單號（`tradeno`）、完整地址（`address`、`phonenumber`、`recipient`）等
- **操作 list 欄位**：必須使用 Cassandra 原生的 append / remove 語法，不可全讀後整組寫回（例：`SET focus_account = focus_account + ['target']`）
- **VIP 權限**：相關查詢需結合 `memberships` 及 `gamesublogs.subendtime > NOW()`，不可僅依賴 `memberships` 非空
- **VIP 遊戲過濾**：查詢預測遊戲時應使用 `hot=true AND payout=false AND status=1 AND endtime > now`，並根據使用者 VIP 狀態過濾 `viponly` 遊戲
- **商城商品兌換狀態值限制**：初始狀態固定為 `"pending"`，後續由後台審核流程更新為 `"ReviewSuccesful"`、`"InTransit"`、`"Delivered"`、`"Received"`、`"UnReceived"` 或 `"Failure"`。**不可直接設為 `"1"`。**
- **時區統一**：所有時間戳以 UTC 為準，DB 欄位為 bigint（毫秒）或特定格式 text
- **跨服務寫入限制**：本服務對 `payment` keyspace 僅有讀取權限，**不可直接寫入**支付方式、方案等管理欄位，但可寫入 `rechargeplans_newlottery` 和 `subplans_sport` 的後台管理操作。
- **新聞 keyspace 唯讀**：本服務對 `news` keyspace 僅有 SELECT 權限，不可寫入

## 常見錯誤
- ❌ 實作社交清單操作時，使用 `SET focus_account = ['target']` 直接覆蓋 list → 應使用 `focus_account = focus_account + ['target']`
- ❌ 查詢兌換記錄未提供完整 Partition Key（如 `site`, `activityevent`, `account`），導致跨分區掃描
- ❌ 忘記在查詢 `gameusers` 或 `paymethods_sport` 時過濾 `status=1` 或 `enabled=1`，導致已停用資料外洩
- ❌ 支付回調或登入成功時，未清除對應會員的 Redis 快取（如 `GameUser:{authkey}`），導致前台資料過期
- ❌ 查詢反饋或常見問題時未過濾 `enabled=1`，顯示已停用內容
- ❌ 查詢活動商品或商城商品時未過濾 `status=1`，導致已下架商品外洩
- ❌ 建立預測投注時未過濾 `betpool_games` 的 `hot`、`payout`、`status` 與 `endtime`，導致對非熱門、已結算或已結束遊戲投注
- ❌ 未檢查 `viponly` 與會員 VIP 有效性（需同時驗證 `memberships` 與 `gamesublogs.subendtime`），導致非 VIP 會員可對 viponly 遊戲投注
- ❌ 投注寫入 `betpool_bets` 時包含了 `profitzcoin` 或 `winlose`，這些欄位應僅由結算服務回填
- ❌ 未驗證 `betoption` 是否存在於 `betpool_games.betoptions` 中，導致寫入無效選項
- ❌ 註冊時未檢查 `forbidden_email_domains`，允許違規域名註冊
- ❌ 密碼重設或變更時，未先雜湊就直接寫入 DB
- ❌ 更新 `memberships` 時使用 `SET` 覆蓋整個 list，而非 `APPEND`