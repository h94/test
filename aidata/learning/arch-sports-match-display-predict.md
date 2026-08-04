# 架構學習地圖：運動賽事展示 / 預測業務鏈

> 產出日期：2026-05-24 | 學習者：（可填）

---

## 1. 系統概覽

這條業務鏈涵蓋「使用者在前台看到比賽資訊 → 下注預測 → 看到即時比分 → 等待結算」的完整生命週期。
賽事原始資料來自外部爬蟲，經多層 BackgroundService 清洗、計算後，分別寫入 Cassandra（持久化）與 Redis（即時快取），再透過 REST API 與 SignalR 推播呈現給前端。
預測投注則由 PredictService 獨立管理，結算由 PredictResultService 非同步執行，兩條線路在設計上刻意解耦。

---

## 2. 服務分層

（來源：`webapi/_index.md`、`service/_index.md`、`frontend/_index.md`）

```
前台站台
  └── pricefrontendsite_nuxt3（Nuxt 3）
        主力前台：賽事展示、即時比分、競猜預測、AI 分析、社群、商城

BFF / 前台主 API
  └── PriceCenterSite
        前台所有 REST 請求的入口，彙整 PriceCenterService、MemberService、
        PredictService、CommunityService、ProductService、PaymentService 等

核心業務服務
  ├── PriceCenterService   賽事/賠率/比分/聯賽/球隊對照表（核心資料源）
  ├── PredictService       競猜下注/Killer/獎池/報表/串關
  ├── PriceClientSystem    即時比分賠率推送（Kafka → SignalR，供 inplayz）
  ├── PriceSubscriptionSystem  多站台賠率訂閱彙整推送（SignalR）
  └── MemberService        會員認證、訂閱狀態（賽事預測需登入）

基礎設施
  ├── TokenService         Token 核發與驗證（所有需登入 API 的前置關卡）
  ├── GatewayManagerService  API 閘道設定與存取日誌
  └── TranslateService     聯賽/球隊名稱多語系翻譯

BackgroundService（賽事資料管線）
  ├── LeisuParserV2        解析足球/籃球 HTML → 發送 Kafka gamedata
  ├── ZBAParser            計算讓分/大小/賽果 → 發送 Kafka gamedata
  ├── CrawlerFlowService   消費 gamedata → 寫 Cassandra pricecenter → 發送 processedgamedata
  ├── CrawlerService       消費 gamedata → 批次寫入 Cassandra pricecenter
  ├── FlowControlService   消費 processedgamedata → 更新 Redis 站台賽事快取 + 寫賠率歷史
  ├── ClientFlowService    消費 processedgamedata → 整合賽事/預測資料 → 寫 Redis DB5~DB7（供前端）
  ├── GameCombineService   自動合併多站台賽事、隊伍映射、翻譯、取消偵測
  └── PredictResultService 每 3 分鐘結算競猜單 → 更新錢包/等級/週報
```

---

## 3. 賽事展示 / 預測 業務資料流

### 3-1. 賽事資料從外部爬蟲到前端的路徑

（來源：`service/_index.md` 資料管線章節）

```
外部爬蟲站台（leisu / ZBA 等）
  │
  ├─[足球/籃球 HTML]─→ LeisuParserV2
  │                         │ 解析賠率、比分、賽況
  │                         ↓
  │                    Kafka: gamedata
  │
  └─[ZBA 格式資料]──→ ZBAParser
                           │ 計算讓分/大小/賽果
                           ↓
                      Kafka: gamedata
                           │
              ┌────────────┴────────────┐
              ↓                         ↓
     CrawlerService              CrawlerFlowService
     批次寫 Cassandra pricecenter  驗證/轉換後存 Cassandra
                                  並發送 processedgamedata
                                         │
                           ┌─────────────┴──────────────┐
                           ↓                             ↓
                  FlowControlService           ClientFlowService
                  更新 Redis 站台賽事快取        整合賽事+預測資料
                  寫 Cassandra 賠率歷史          寫 Redis DB5~DB7
                                                （前端即時快取用）
```

### 3-2. 前端請求賽事資料（REST）

```
使用者打開賽事列表頁
  → pricefrontendsite_nuxt3（Nuxt 3）
  → PriceCenterSite /apiservice/api/...（BFF 主入口）
  → PriceCenterService（查 Cassandra pricecenter + Redis 快取）
  → 回傳賽事/賠率/比分資料給前端渲染
```

### 3-3. 即時比分推送（SignalR）

```
FlowControlService 更新 Redis 賽事快取
  → PriceClientSystem 消費 Kafka processedgamedata
  → 透過 SignalR Hub（/hubservice/hub）推播給 pricefrontendsite_nuxt3
  → 前端直接更新畫面，不需重新 HTTP 請求
```

### 3-4. 使用者下注預測

```
使用者點選預測下注
  → pricefrontendsite_nuxt3
  → PriceCenterSite（驗 Token → MemberService / TokenService）
  → PredictService /api/...（寫 Cassandra predict keyspace）
       ├── bets（注單）
       ├── betpools（獎池）
       └── championships（冠軍賽）
  → 回傳下注成功 or 失敗
```

### 3-5. 賽事結算（非同步後台）

```
賽事結束後
  → PredictResultService（每 3 分鐘輪詢）
  → 查 pricecenter 確認賽果
  → 查 predict.bets 計算輸贏
  → 更新錢包（WalletService）
  → 更新週報/等級
  → 同步競猜結果回社群系統（CommunityService）
```

---

## 4. 關鍵服務說明

（來源：`webapi/_index.md`、`service/_index.md`、`db/_index.md`）

| 服務 | 職責 | 技術棧 | 相依 DB |
|------|------|--------|---------|
| pricefrontendsite_nuxt3 | 主力前台，渲染賽事/預測/即時比分 | Nuxt 3 / TypeScript | — |
| PriceCenterSite | 前台所有 REST API 的統一入口（BFF） | C# | — |
| PriceCenterService | 賽事/賠率/比分/聯賽/球隊核心資料 | C# | Cassandra pricecenter（692 表） |
| PredictService | 競猜下注、Killer、獎池、串關、報表 | C# | Cassandra predict（77 表） |
| PriceClientSystem | 即時比分賠率推送 Kafka → SignalR | C# | Redis |
| CrawlerFlowService | 消費原始賠率 → 寫 Cassandra + 發 processedgamedata | .NET 6 | Cassandra pricecenter |
| ClientFlowService | 整合賽事+預測 → 寫前端用 Redis DB5~DB7 | .NET 8 | Redis DB5~DB7 |
| FlowControlService | 更新 Redis 站台快取、寫賠率歷史、資料修復 | .NET 8 | Redis + Cassandra |
| PredictResultService | 每 3 分鐘結算競猜單 | .NET 8 | Cassandra predict + pricecenter |
| GameCombineService | 多站台賽事自動合併、隊伍映射、翻譯 | .NET 6 | PriceCenterService API |

---

## 5. 新人常見疑問

**Q：前端的即時比分是怎麼更新的？不是每秒 polling 嗎？**
A：不是。系統用 SignalR 長連線（WebSocket）推播。`PriceClientSystem` 消費 Kafka 的 `processedgamedata`，有新資料就主動推給已連線的前端，前端不需要輪詢。

**Q：賽事資料有這麼多 BackgroundService，哪一個才是「真正的資料源」？**
A：LeisuParserV2 / ZBAParser 是第一層入口（爬蟲解析），它們發送到 Kafka `gamedata`，之後的 CrawlerService / CrawlerFlowService 才是寫進 Cassandra 的主力。FlowControlService 和 ClientFlowService 是再加工層（快取/整合），不改動原始資料的主表。

**Q：PredictService 和 PriceCenterService 有什麼差別？**
A：PriceCenterService 管的是「賽事本身」（比賽/賠率/比分/聯賽），是只讀性質居多。PredictService 管的是「玩家對這場比賽的預測行為」（注單/獎池/結算），是獨立的業務域，寫入 predict keyspace。

**Q：下注後，錢包是誰在扣？**
A：PredictService 下注時呼叫 WalletService 扣款，PredictResultService 結算後再透過 WalletService 發放獎勵。MemberService 本身不處理金錢。

**Q：Cassandra pricecenter 有 692 張表，怎麼查？**
A：表名規律是 `{table}_{sport}_{YYYYMM}`（如 `matches_his_BK_202506`），按運動種類代碼（BK=籃球、SC=足球等）和月份動態建立，查詢時要帶對應後綴。

---

## 6. 建議下一步

- 想深入了解賽事核心資料服務 → `@service-teacher PriceCenterService`
- 想深入了解競猜預測服務 → `@service-teacher PredictService`
- 想了解即時推播機制 → `@service-teacher PriceClientSystem`
- 想了解資料管線入口 → `@service-teacher CrawlerFlowService`
- 要開始做任務 → `@task-helper {任務描述}`
