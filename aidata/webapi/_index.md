# WebAPI 服務目錄

此目錄包含各服務的 OpenAPI 3.0 規格檔與服務說明，供開發時查閱端點定義與服務職責。

## kind 欄位說明

| kind | 意義 | 判斷依據（README / detail） |
|------|------|---------------------------|
| `atomic` | 原子 WebAPI | 直連 DB（Cassandra / MySQL / PostgreSQL 等）或自有資料域（Redis / 檔案為主資料來源）；Controller Route **固定含 `v1` 版號**（除非開發人員明確指定其他版號） |
| `integration` | 整合 WebAPI | 不直連業務 DB；資料來源為 Gateway 呼叫下游原子服務（＋ Redis / 檔案）；Controller Route **不含** `v1` 版號 |

> Background Worker 見 [service/_index.md](../service/_index.md)（kind 一律為 `service`）。

---

## Confluence 業務文件（documents.md）

由 Confluence 整理、經人工審核的業務規範／技術設計摘要。引導師（`@task-helper`、`@service-teacher`、`@plan-maker` 等）**優先讀此檔**，再讀 `*-detail.md`；與 detail 衝突時以 `documents.md` 為準。

> 全域目錄（僅在該服務無 `documents.md` 或需查未整合頁時）：[confluence/_index.md](../confluence/_index.md) — **禁止整檔讀取**，僅 grep `### webapi/{service}` 或關鍵字後讀 `confluence/processed/{pageId}-summary.md`。

| 服務 | kind | Confluence 摘要 |
|------|------|----------------|
| AdvertisingService | atomic | [documents.md](./advertisingservice/documents.md) |
| AireviewAgentService | atomic | [documents.md](./aireviewagentservice/documents.md) |
| CommunityService | atomic | [documents.md](./communityservice/documents.md) |
| CurrencyManageService | atomic | [documents.md](./currencymanageservice/documents.md) |
| CurrencyService | atomic | [documents.md](./currencyservice/documents.md) |
| FeedbackService | atomic | [documents.md](./feedbackservice/documents.md) |
| GameLiveService | atomic | [documents.md](./gameliveservice/documents.md) |
| GameSettingService | atomic | [documents.md](./gamesettingservice/documents.md) |
| GameSettingSite | atomic | [documents.md](./gamesettingsite/documents.md) |
| GatewayManagerService | atomic | [documents.md](./gatewaymanagerservice/documents.md) |
| GeoIPService | atomic | [documents.md](./geoipservice/documents.md) |
| InjuriesAPI | atomic | [documents.md](./injuriesapi/documents.md) |
| InplayzSubscriptionSystem | atomic | [documents.md](./inplayzsubscriptionsystem/documents.md) |
| LeaderboardService | atomic | [documents.md](./leaderboardservice/documents.md) |
| LiveChatService | atomic | [documents.md](./livechatservice/documents.md) |
| MemberService | atomic | [documents.md](./memberservice/documents.md) |
| MergeSite | integration | [documents.md](./mergesite/documents.md) |
| NewLotteryBackEndService | integration | [documents.md](./newlotterybackendservice/documents.md) |
| NewLotterySite | integration | [documents.md](./newlotterysite/documents.md) |
| NewsService | atomic | [documents.md](./newsservice/documents.md) |
| OpenclawService | atomic | [documents.md](./openclawservice/documents.md) |
| PaymentService | atomic | [documents.md](./paymentservice/documents.md) |
| PredictService | atomic | [documents.md](./predictservice/documents.md) |
| PriceBackendService | integration | [documents.md](./pricebackendservice/documents.md) |
| PriceCenterManage | atomic | [documents.md](./pricecentermanage/documents.md) |
| PriceCenterService | atomic | [documents.md](./pricecenterservice/documents.md) |
| PriceCenterSite | integration | [documents.md](./pricecentersite/documents.md) |
| PriceSubscriptionSystem | atomic | [documents.md](./pricesubscriptionsystem/documents.md) |
| OddNotificationService | atomic | [documents.md](./oddnotificationservice/documents.md) |
| ProductService | atomic | [documents.md](./productservice/documents.md) |
| SiteGameOddService | atomic | [documents.md](./sitegameoddservice/documents.md) |
| TokenService | atomic | [documents.md](./tokenservice/documents.md) |
| TradeGameService | atomic | [documents.md](./tradegameservice/documents.md) |
| TranslateService | atomic | [documents.md](./translateservice/documents.md) |

跨服務主題（架構、博彩業務、股票業務等）見 [others/_index.md](../others/_index.md)、[game/_index.md](../game/_index.md)、[stock/_index.md](../stock/_index.md)。

---

## 服務一覽（含 OpenAPI 規格）

| 服務 | kind | OpenAPI 規格 | 說明 |
|------|------|-------------|------|
| AdvertisingService | atomic | [advertisingservice/advertisingservice.json](./advertisingservice/advertisingservice.json) | 廣告投放與公告佈告欄（Cassandra + Redis）[詳](./advertisingservice/advertisingservice-detail.md) |
| AireviewAgentService | atomic | [aireviewagentservice/aireviewagentservice.json](./aireviewagentservice/aireviewagentservice.json) | 接收 GitLab Webhook（Push/MR）觸發 AI 程式碼／Plan 審查，結果寫入 PostgreSQL（aireviews），支援補 MR 註解與 Rocket.Chat 通知；同時提供審查事件、Run、Issue、Portainer mapping 的查詢與維運 API |
| CommunityService | atomic | [communityservice/communityservice.json](./communityservice/communityservice.json) | 社群文章、留言、按讚、HashTag、新彩票論壇（Python Flask + MeiliSearch）[詳](./communityservice/communityservice-detail.md) |
| CurrencyManageService | atomic | [currencymanageservice/currencymanageservice.json](./currencymanageservice/currencymanageservice.json) | 貨幣爬取任務分發與機器健康監控 |
| CurrencyService | atomic | [currencyservice/currencyservice.json](./currencyservice/currencyservice.json) | 加密貨幣、穩定幣、外匯匯率查詢（Redis + Cassandra）[詳](./currencyservice/currencyservice-detail.md) |
| FeedbackService | atomic | [feedbackservice/feedbackservice.json](./feedbackservice/feedbackservice.json) | 使用者反饋（運動/股票）與商業合作訊息 [詳](./feedbackservice/feedbackservice-detail.md) |
| GameLiveService | atomic | [gameliveservice/gameliveservice.json](./gameliveservice/gameliveservice.json) | 直播社群群組、聊天室、頻道開關（SignalR）[詳](./gameliveservice/gameliveservice-detail.md) |
| GameSettingService | atomic | [gamesettingservice/gamesettingservice.json](./gamesettingservice/gamesettingservice.json) | 遊戲設定、玩法模式、商家帳號、訂閱者管理 [詳](./gamesettingservice/gamesettingservice-detail.md) |
| GameSettingSite | atomic | [gamesettingsite/gamesettingsite.json](./gamesettingsite/gamesettingsite.json) | 遊戲設定後台站台（AI 新聞、賽事查詢）[詳](./gamesettingsite/gamesettingsite-detail.md) |
| InplayzSubscriptionSystem | atomic | [inplayzsubscriptionsystem/inplayzsubscriptionsystem.json](./inplayzsubscriptionsystem/inplayzsubscriptionsystem.json) | 即時賽事訂閱推送給商務端（SignalR + Kafka）[詳](./inplayzsubscriptionsystem/inplayzsubscriptionsystem-detail.md) |
| LeaderboardService | atomic | [leaderboardservice/leaderboardservice.json](./leaderboardservice/leaderboardservice.json) | 排行榜圖表建立、自動刷新、樣板管理 |
| LeaderboardSite | integration | [leaderboardsite/leaderboardsite.json](./leaderboardsite/leaderboardsite.json) | 排行榜前台站台（CRUD、嵌入 JS）[詳](./leaderboardsite/leaderboardsite-detail.md) |
| LiveChatService | atomic | [livechatservice/livechatservice.json](./livechatservice/livechatservice.json) | 即時客服聊天（SignalR + Redis + MySQL）[詳](./livechatservice/livechatservice-detail.md) |
| MemberService | atomic | [memberservice/memberservice.json](./memberservice/memberservice.json) | 會員管理：遊戲/股票/新彩票/排行榜，含錢包、冠軍賽 [詳](./memberservice/memberservice-detail.md) |
| MergeSite | integration | [mergesite/mergesite.json](./mergesite/mergesite.json) | 賽事合併管理後台（聯盟、SiteGame、OpenClaw）[詳](./mergesite/mergesite-detail.md) |
| NewLotteryBackEndService | integration | [newlotterybackendservice/newlotterybackendservice.json](./newlotterybackendservice/newlotterybackendservice.json) | 新彩票後端：投注池、錦標賽、會員錢包、支付訂單 [詳](./newlotterybackendservice/newlotterybackendservice-detail.md) |
| NewLotterySite | integration | [newlotterysite/newlotterysite.json](./newlotterysite/newlotterysite.json) | 新彩票站台：會員註冊/登入/簡訊驗證 [詳](./newlotterysite/newlotterysite-detail.md) |
| NewsService | atomic | [newsservice/newsservice.json](./newsservice/newsservice.json) | 運動新聞、站台文章、AI 生成新聞（ainews）[詳](./newsservice/newsservice-detail.md) |
| PaymentService | atomic | [paymentservice/paymentservice.json](./paymentservice/paymentservice.json) | 金流：訂閱方案、交易訂單、報表、提現、活動兌換 [詳](./paymentservice/paymentservice-detail.md) |
| PredictService | atomic | [predictservice/predictservice.json](./predictservice/predictservice.json) | 競猜預測：下注、Killer、獎池、報表、串關 [詳](./predictservice/predictservice-detail.md) |
| PriceBackendService | integration | [pricebackendservice/pricebackendservice.json](./pricebackendservice/pricebackendservice.json) | 管理後台 BFF：聚合所有微服務，提供後台管理介面 [詳](./pricebackendservice/pricebackendservice-detail.md) |
| PriceCenterManage | atomic | [pricecentermanage/pricecentermanage.json](./pricecentermanage/pricecentermanage.json) | 價格中心管理後台：通知、站內信、App 版本、爬蟲監控 [詳](./pricecentermanage/pricecentermanage-detail.md) |
| PriceCenterService | atomic | [pricecenterservice/pricecenterservice.json](./pricecenterservice/pricecenterservice.json) | 價格中心核心：賽事、賠率、比分、聯賽/球隊對照表 [詳](./pricecenterservice/pricecenterservice-detail.md) |
| PriceCenterSite | integration | [pricecentersite/pricecentersite.json](./pricecentersite/pricecentersite.json) | 前台站台主 API：賽事、會員、社群、商城、支付、廣告、賽事交易所 [詳](./pricecentersite/pricecentersite-detail.md) |
| PriceClientSystem | atomic | [priceclientsystem/priceclientsystem.json](./priceclientsystem/priceclientsystem.json) | 即時比分賠率推送（Kafka → SignalR，供 InplayZ）[詳](./priceclientsystem/priceclientsystem-detail.md) |
| PriceSubscriptionSystem | atomic | [pricesubscriptionsystem/pricesubscriptionsystem.json](./pricesubscriptionsystem/pricesubscriptionsystem.json) | 多站台賠率訂閱彙整與推送（SignalR） |
| OddNotificationService | atomic | [oddnotificationservice/oddnotificationservice.json](./oddnotificationservice/oddnotificationservice.json) | 賠率異常警示即時推送（Kafka `alert_events` + SignalR）[詳](./oddnotificationservice/oddnotificationservice-detail.md) |
| ProductService | atomic | [productservice/productservice.json](./productservice/productservice.json) | 商城商品、活動商品、兌換紀錄、庫存記錄 [詳](./productservice/productservice-detail.md) |
| TokenService | atomic | [tokenservice/tokenservice.json](./tokenservice/tokenservice.json) | Token 核發、驗證與操作日誌 |
| TradeGameService | atomic | [tradegameservice/tradegameservice.json](./tradegameservice/tradegameservice.json) | 賽事交易遊戲：倉位買賣、盤口快照（Python Flask）[詳](./tradegameservice/tradegameservice-detail.md) |

---

## 服務一覽（僅 README，無 OpenAPI 規格）

| 服務 | kind | README | 說明 |
|------|------|--------|------|
| GatewayManagerService | atomic | [gatewaymanagerservice/README.md](./gatewaymanagerservice/README.md) | API 閘道設定、Access Log 查詢、Jira 週報整合 |
| GeoIPService | atomic | [geoipservice/README.md](./geoipservice/README.md) | IP 地理位置查詢（MaxMind GeoIP2 + Redis） |
| ImageService | atomic | [imageservice/README.md](./imageservice/README.md) | 驗證碼辨識：數字驗證碼（ddddocr）、滑塊缺口定位（Python Flask） |
| InjuriesAPI | atomic | [injuriesapi/README.md](./injuriesapi/README.md) | 運動傷兵名單管理（Cassandra，Python Flask） |
| MQService | atomic | [mqservice/README.md](./mqservice/README.md) | 訊息通知中介：Email、SMS、Telegram、RocketChat、Kafka |
| OpenclawService | atomic | [openclawservice/README.md](./openclawservice/README.md) | 賽事/聯盟合併（龍蝦系統，Python FastAPI）[詳](./openclawservice/openclawservice-detail.md) |
| SiteGameOddService | atomic | [sitegameoddservice/README.md](./sitegameoddservice/README.md) | 賽事賠率查詢、歷史賠率、賠率走勢（Python Flask + Loki）[詳](./sitegameoddservice/sitegameoddservice-detail.md) |
| TranslateService | atomic | [translateservice/README.md](./translateservice/README.md) | 多語系關鍵字翻譯管理（MySQL + Redis + Google Translate） |

---

## 服務名稱對照備註

| 相依服務名稱（appsettings） | 實際資料夾 / 服務 | 說明 |
|--------------------------|-----------------|------|
| `pricecenter` | `pricecenterservice` | 同一服務，appsettings 中路由前綴為 `pricecenter`，資料夾名稱為 `pricecenterservice` |
| `pricecentermanage` | `pricecentermanage` | 與 pricecenterservice 不同，負責通知/站內信/App 裝置/爬蟲心跳管理 |
| `mq` | `mqservice` | 訊息中介服務，appsettings 中通常以 `mq` 簡稱 |

---

## Scenario Flows（使用場景描述）

部分服務在 `scenario-flows/` 目錄下提供各操作場景的流程說明與注意事項，
供 AI 進行**跨服務流程分析**、**整合測試規劃**及**任務理解**時參考。

> 目錄結構慣例：`{service}/scenario-flows/{動詞}-flow/{場景}.md`
> 例：`advertisingservice/scenario-flows/create-flow/create-advertisement.md`

| 服務 | Scenario Flows 路徑 |
|------|-------------------|
| AdvertisingService | [advertisingservice/scenario-flows/](./advertisingservice/scenario-flows/) |
| CommunityService | [communityservice/scenario-flows/](./communityservice/scenario-flows/) |
| FeedbackService | [feedbackservice/scenario-flows/](./feedbackservice/scenario-flows/) |
| GameLiveService | [gameliveservice/scenario-flows/](./gameliveservice/scenario-flows/) |
| GameSettingService | [gamesettingservice/scenario-flows/](./gamesettingservice/scenario-flows/) |
| GameSettingSite | [gamesettingsite/scenario-flows/](./gamesettingsite/scenario-flows/) |
| InplayzSubscriptionSystem | [inplayzsubscriptionsystem/scenario-flows/](./inplayzsubscriptionsystem/scenario-flows/) |
| LiveChatService | [livechatservice/scenario-flows/](./livechatservice/scenario-flows/) |
| MemberService | [memberservice/scenario-flows/](./memberservice/scenario-flows/) |
| MergeSite | [mergesite/scenario-flows/](./mergesite/scenario-flows/) |
| MQService | [mqservice/scenario-flows/](./mqservice/scenario-flows/) |
| NewsService | [newsservice/scenario-flows/](./newsservice/scenario-flows/) |
| OpenclawService | [openclawservice/scenario-flows/](./openclawservice/scenario-flows/) |
| PaymentService | [paymentservice/scenario-flows/](./paymentservice/scenario-flows/) |
| PredictService | [predictservice/scenario-flows/](./predictservice/scenario-flows/) |
| PriceBackendService | [pricebackendservice/scenario-flows/](./pricebackendservice/scenario-flows/) |
| PriceCenterManage | [pricecentermanage/scenario-flows/](./pricecentermanage/scenario-flows/) |
| PriceCenterService | [pricecenterservice/scenario-flows/](./pricecenterservice/scenario-flows/) |
| PriceCenterSite | [pricecentersite/scenario-flows/](./pricecentersite/scenario-flows/) |
| PriceClientSystem | [priceclientsystem/scenario-flows/](./priceclientsystem/scenario-flows/) |
| OddNotificationService | [oddnotificationservice/scenario-flows/](./oddnotificationservice/scenario-flows/) |
| ProductService | [productservice/scenario-flows/](./productservice/scenario-flows/) |
| SiteGameOddService | [sitegameoddservice/scenario-flows/](./sitegameoddservice/scenario-flows/) |
| TokenService | [tokenservice/scenario-flows/](./tokenservice/scenario-flows/) |
| TradeGameService | [tradegameservice/scenario-flows/](./tradegameservice/scenario-flows/) |

---

## 套用原則

處理 WebAPI / Controller 任務時，**先查本頁 kind 欄**確認 `atomic` 或 `integration`，再依服務類型查閱對應 OpenAPI 規格了解端點定義：

> 若說明欄附有 **[詳]** 連結，應在查閱 OpenAPI / README 後優先閱讀，其中包含更完整的業務邏輯、欄位限制、讀寫規則與常見錯誤說明。

> **流程分析 / 整合測試時**：若任務涉及跨 API 操作順序、前後端串接驗證、或端到端場景，
> 應先查閱對應服務的 `scenario-flows/`（見上方速查表），確認正確的操作流程與前置條件後再進行分析或測試規劃。

**核心賽事與競猜**
- **賽事/賠率/比分** → `./pricecenterservice/pricecenterservice.json`
- **競猜下注/Killer/獎池** → `./predictservice/predictservice.json`
- **交易遊戲（買賣倉位）** → `./tradegameservice/tradegameservice.json`
- **賽事合併（聯盟/SiteGame）** → `./mergesite/mergesite.json`
- **即時比分推送（InplayZ）** → `./priceclientsystem/priceclientsystem.json`
- **多站台賠率訂閱** → `./pricesubscriptionsystem/pricesubscriptionsystem.json`
- **賠率異常警示即時推送** → `./oddnotificationservice/oddnotificationservice.json`
- **商務端即時訂閱** → `./inplayzsubscriptionsystem/inplayzsubscriptionsystem.json`

**會員與認證**
- **會員（遊戲/股票/新彩票/排行榜）** → `./memberservice/memberservice.json`
- **Token 核發/驗證** → `./tokenservice/tokenservice.json`

**金流與商品**
- **支付訂閱/交易訂單/報表** → `./paymentservice/paymentservice.json`
- **商城/活動商品/兌換** → `./productservice/productservice.json`

**前台站台**
- **前台主站（賽事/社群/商城/支付）** → `./pricecentersite/pricecentersite.json`
- **新彩票前台** → `./newlotterysite/newlotterysite.json`
- **排行榜站台** → `./leaderboardsite/leaderboardsite.json`

**後台管理**
- **管理後台 BFF（彙整所有功能）** → `./pricebackendservice/pricebackendservice.json`
- **價格中心後台（通知/爬蟲/App）** → `./pricecentermanage/pricecentermanage.json`
- **遊戲設定/玩法/商家** → `./gamesettingservice/gamesettingservice.json`
- **廣告/公告** → `./advertisingservice/advertisingservice.json`
- **運動新聞/AI 新聞** → `./newsservice/newsservice.json`
- **賽事合併後台** → `./mergesite/mergesite.json`

**社群與互動**
- **社群文章/留言/按讚/新彩票論壇** → `./communityservice/communityservice.json`
- **直播社群群組/聊天室/頻道** → `./gameliveservice/gameliveservice.json`
- **即時客服聊天** → `./livechatservice/livechatservice.json`

**彩票**
- **新彩票後端（投注池/錦標賽）** → `./newlotterybackendservice/newlotterybackendservice.json`
- **新彩票前台** → `./newlotterysite/newlotterysite.json`

**基礎設施**
- **訊息通知（Email/SMS/Telegram）** → `./mqservice/README.md`
- **翻譯管理** → `./translateservice/README.md`
- **貨幣/匯率** → `./currencyservice/currencyservice.json`
- **排行榜引擎** → `./leaderboardservice/leaderboardservice.json`
- **客服反饋** → `./feedbackservice/feedbackservice.json`
- **IP 地理位置** → `./geoipservice/README.md`
- **驗證碼辨識** → `./imageservice/README.md`
- **傷兵名單** → `./injuriesapi/README.md`
- **賠率查詢/歷史** → `./sitegameoddservice/README.md`
- **龍蝦合併（OpenClaw）** → `./openclawservice/README.md`
