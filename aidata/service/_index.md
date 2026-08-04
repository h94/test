# BackgroundService 服務目錄

此目錄包含各後台背景服務的說明，涵蓋爬蟲資料管線、結算、預測機器人、日誌監控、AI 內容生成、貨幣外匯等功能。
所有服務均為無 HTTP 對外端點的 Worker / BackgroundService（少數例外已標註）。

## kind 欄位說明

| kind | 意義 |
|------|------|
| `service` | Background Worker：無（或極少）Controller / 對外 URL；非 WebAPI 原子或整合層 |

> WebAPI 的 `atomic` / `integration` 見 [webapi/_index.md](../webapi/_index.md)。

---

## Confluence 業務文件（documents.md）

由 Confluence 整理、經人工審核的業務規範／技術設計摘要。引導師**優先讀此檔**，再讀 README / `*-detail.md`；與 detail 衝突時以 `documents.md` 為準。

> 全域目錄（僅在該服務無 `documents.md` 或需查未整合頁時）：[confluence/_index.md](../confluence/_index.md) — **禁止整檔讀取**，僅 grep `### service/{service}` 或關鍵字。

| 服務 | kind | Confluence 摘要 |
|------|------|----------------|
| CrawlerAgentStandings | service | [documents.md](./crawleragentstandings/documents.md) |
| CrawlerFlowService | service | [documents.md](./crawlerflowservice/documents.md) |
| CrawlerOddTrend | service | [documents.md](./crawleroddtrend/documents.md) |
| CrawlerService | service | [documents.md](./crawlerservice/documents.md) |
| CryptoCacheService | service | [documents.md](./cryptocacheservice/documents.md) |
| CryptoFlowService | service | [documents.md](./cryptoflowservice/documents.md) |
| FlowControlService | service | [documents.md](./flowcontrolservice/documents.md) |
| ForexCacheService | service | [documents.md](./forexcacheservice/documents.md) |
| ForexFlowService | service | [documents.md](./forexflowservice/documents.md) |
| GameCombineService | service | [documents.md](./gamecombineservice/documents.md) |
| LeisuParserV2 | service | [documents.md](./leisuparserv2/documents.md) |
| PredictResultService | service | [documents.md](./predictresultservice/documents.md) |
| PredictRobot | service | [documents.md](./predictrobot/documents.md) |
| SyncService | service | [documents.md](./syncservice/documents.md) |
| TradeGameResultService | service | [documents.md](./tradegameresultservice/documents.md) |
| ZAIService | service | [documents.md](./zaiservice/documents.md) |
| ZBAParser | service | [documents.md](./zbaparser/documents.md) |

博彩／股票爬蟲專題見 [game/_index.md](../game/_index.md)、[stock/_index.md](../stock/_index.md)；跨服務架構見 [others/_index.md](../others/_index.md)。

---

## 1. 賽事資料管線

負責從外部爬蟲站台接收原始資料，經處理後寫入 Cassandra / Redis / Kafka 供下游使用。

| 服務 | kind | README | 技術 | 說明 |
|------|------|--------|------|------|
| CrawlerService | service | [crawlerservice/README.md](./crawlerservice/README.md) | .NET 6 | 消費 Kafka `gamedata`，驗證/清洗原始賠率後批次寫入 Cassandra（pricecenter）[詳](./crawlerservice/crawlerservice-detail.md) |
| CrawlerFlowService | service | [crawlerflowservice/README.md](./crawlerflowservice/README.md) | .NET 6 | 消費 Kafka `gamedata`，驗證/轉換後存 Cassandra，並發送 `processedgamedata` [詳](./crawlerflowservice/crawlerflowservice-detail.md) |
| ZBAParser | service | [zbaparser/README.md](./zbaparser/README.md) | .NET 8 | 消費 `processedgamedata`，計算讓分/大小/賽果，發送至 `gamedata`；維護 Redis 賽事快取 [詳](./zbaparser/zbaparser-detail.md) |
| LeisuParserV2 | service | [leisuparserv2/README.md](./leisuparserv2/README.md) | Python 3.9 | 消費 Kafka `leisuhtml`，解析足球/籃球賠率、比分、比賽狀態，發送 `gamedata` |
| FlowControlService | service | [flowcontrolservice/README.md](./flowcontrolservice/README.md) | .NET 8 | 消費 `processedgamedata`，更新 Redis 站台賽事快取、寫 Cassandra 賠率歷史，並執行資料修復 [詳](./flowcontrolservice/flowcontrolservice-detail.md) |
| ClientFlowService | service | [clientflowservice/README.md](./clientflowservice/README.md) | .NET 8 | 消費 `processedgamedata`，整合賽事/預測資料後寫 Redis DB5~DB7（供 inplayz 前端使用）[詳](./clientflowservice/clientflowservice-detail.md) |
| GameCombineService | service | [gamecombineservice/README.md](./gamecombineservice/README.md) | .NET 6 | 呼叫 PriceCenterService API 進行多站台賽事自動合併、隊伍映射、翻譯、取消偵測 [詳](./gamecombineservice/gamecombineservice-detail.md) |
| CrawlerAgentStandings | service | [crawleragentstandings/README.md](./crawleragentstandings/README.md) | Python 3.8 | 爬取 MLB/NBA/KBO 等聯盟戰績，轉換後 POST 至 PriceCenter Gateway [詳](./crawleragentstandings/crawleragentstandings-detail.md) |
| CrawlerOddTrend | service | [crawleroddtrend/README.md](./crawleroddtrend/README.md) | Python Flask | ⚠️ 有 HTTP 端點。查詢 Cassandra 賠率歷史，回傳趨勢圖格式資料 [詳](./crawleroddtrend/crawleroddtrend-detail.md) |

**資料流概覽：**
```
外部爬蟲站台
  → [leisu/其他 HTML] → LeisuParserV2 → Kafka gamedata
  → [ZBA 資料]        → ZBAParser     → Kafka gamedata
  → CrawlerService / CrawlerFlowService 消費 gamedata → Cassandra pricecenter
  → FlowControlService / ClientFlowService 消費 processedgamedata → Redis / Cassandra
```

---

## 2. 結算與資料同步

負責賽事結算、資料備援同步及交易遊戲結算。

| 服務 | kind | README | 技術 | 說明 |
|------|------|--------|------|------|
| PredictResultService | service | [predictresultservice/README.md](./predictresultservice/README.md) | .NET 8 | 每 3 分鐘結算已完成賽事的競猜單，更新錢包/等級/週報，並同步回社群系統 [詳](./predictresultservice/predictresultservice-detail.md) |
| TradeGameResultService | service | [tradegameresultservice/README.md](./tradegameresultservice/README.md) | Python 3.9 | 讀取 Cassandra 賽事結果與持倉，計算交易遊戲輸贏，更新持倉並發放 ZCoin 獎勵 [詳](./tradegameresultservice/tradegameresultservice-detail.md) |
| SyncService | service | [syncservice/README.md](./syncservice/README.md) | .NET Core 3.1 | 將 PRD Cassandra（pricecenter / gamesetting）資料即時同步至 BAK 備援庫 [詳](./syncservice/syncservice-detail.md) |

---

## 3. 競猜分析與預測機器人

負責高手排名計算、自動下注機器人及預測排行榜。

| 服務 | kind | README | 技術 | 說明 |
|------|------|--------|------|------|
| MasterService | service | [masterservice/README.md](./masterservice/README.md) | Python 3.8 | 從 Cassandra 計算玩家預測勝率/連勝/獲利，產出高手排行榜，寫 Cassandra + Google Sheets [詳](./masterservice/masterservice-detail.md) |
| MainMasterService | service | [mainmasterservice/README.md](./mainmasterservice/README.md) | Python 3.8 | 專注主推（mainbet）玩家連勝計算，每 30 分鐘執行，結果 POST 至 PredictService [詳](./mainmasterservice/mainmasterservice-detail.md) |
| PredictRobot | service | [predictrobot/README.md](./predictrobot/README.md) | Python 3.9 | 模擬真人下注的自動投注機器人，從 inplayz API 取得賠率，依策略（20+ 種）自動下注 [詳](./predictrobot/predictrobot-detail.md) |
| PredictRobotByConnect | service | [predictrobotbyconnect/README.md](./predictrobotbyconnect/README.md) | Python 3.9 | 透過 WebSocket / Kafka 接收即時賠率串流，依策略即時下注，支援 20+ 種策略 [詳](./predictrobotbyconnect/predictrobotbyconnect-detail.md) |

---

## 4. 日誌與監控

負責集中收集 Kafka 日誌並持久化至 Cassandra / Loki。

| 服務 | kind | README | 技術 | 說明 |
|------|------|--------|------|------|
| AppLogXService | service | [applogxservice/README.md](./applogxservice/README.md) | .NET 8 | 消費 Kafka `applogs`，批次寫入 Cassandra（每日建表），同步推送至 Loki 供 Grafana 監控 |
| LogXService | service | [logxservice/README.md](./logxservice/README.md) | .NET 6 | 消費 Kafka `nginxlogs`，解析 NGINX 存取日誌後寫入 Cassandra `accesslogs`（每日建表） |

---

## 5. AI 內容生成

負責 AI 賽事分析、新聞自動產出與機器人發文。

| 服務 | kind | README | 技術 | 說明 |
|------|------|--------|------|------|
| ZAIService | service | [zaiservice/README.md](./zaiservice/README.md) | .NET 8 | 結合 LLM 產出賽事分析/即時賽況/賽後文章，模擬 Bot 在論壇發文，支援多語系翻譯與文件輸出 [詳](./zaiservice/zaiservice-detail.md) |

---

## 6. 加密貨幣與外匯

負責加密貨幣/外匯資料的 Kafka 消費、快取寫入與歷史儲存。

| 服務 | kind | README | 技術 | 說明 |
|------|------|--------|------|------|
| CryptoCacheService | service | [cryptocacheservice/README.md](./cryptocacheservice/README.md) | .NET 6 | 消費 Kafka `cryptodata`，驗證轉換後批量寫入 Redis Hash（多節點），供即時查詢 |
| CryptoFlowService | service | [cryptoflowservice/README.md](./cryptoflowservice/README.md) | .NET 6 | 消費 Kafka `cryptodata`，彙整 K 線資料（每分鐘）後批次寫入 Cassandra，更新儀表板狀態 [詳](./cryptoflowservice/cryptoflowservice-detail.md) |
| ForexCacheService | service | [forexcacheservice/README.md](./forexcacheservice/README.md) | .NET 6 | 消費 Kafka `forexdata`，轉換後批量寫入 Redis（DB 8），提供外匯即時快取 |
| ForexFlowService | service | [forexflowservice/README.md](./forexflowservice/README.md) | .NET 6 | 消費 Kafka `forexdata`，轉換為 FxRateData，批次寫入 Cassandra（依類型/站點/幣別分表） |

**資料流概覽：**
```
外部交易所 / 外匯來源
  → 爬蟲發送至 Kafka cryptodata / forexdata
  → CryptoCacheService / ForexCacheService → Redis（即時快取）
  → CryptoFlowService / ForexFlowService   → Cassandra（歷史 K 線）
```

---

## 7. 工具服務

| 服務 | kind | README | 技術 | 說明 |
|------|------|--------|------|------|
| WebpService | service | [webpservice/README.md](./webpservice/README.md) | .NET 6 | 每 30 分鐘掃描指定目錄，將 PNG/JPG/BMP 圖片自動轉換為 WebP 格式 [詳](./webpservice/webpservice-detail.md) |

---

## 套用原則

處理 BackgroundService 任務時，**kind 一律為 `service`**；依功能類型查閱對應說明：

> 若說明欄附有 **[詳]** 連結，應在閱讀 README 後優先查閱，其中包含更完整的 Input/Output 欄位規格、資料流邊界與常見錯誤說明。

| 任務類型 | 查閱服務 |
|---------|---------|
| 賠率/賽事資料流 | CrawlerService、CrawlerFlowService、ZBAParser、LeisuParserV2 |
| 賠率快取/歷史更新 | FlowControlService、ClientFlowService |
| 賽事合併/翻譯 | GameCombineService |
| 競猜結算/錢包 | PredictResultService |
| 交易遊戲結算 | TradeGameResultService |
| 高手排名/報表 | MasterService、MainMasterService |
| 自動投注機器人 | PredictRobot、PredictRobotByConnect |
| 應用程式日誌 | AppLogXService |
| Nginx 存取日誌 | LogXService |
| AI 新聞/文章 | ZAIService |
| 加密貨幣快取/歷史 | CryptoCacheService、CryptoFlowService |
| 外匯快取/歷史 | ForexCacheService、ForexFlowService |
| 圖片格式轉換 | WebpService |
| 資料備援同步 | SyncService |
| 戰績爬蟲 | CrawlerAgentStandings |
| 賠率趨勢查詢 | CrawlerOddTrend |
