# crawlerservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 12:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB-476 [bet365htmlprovider] 自爆機制

> Confluence 頁面 ID：11436143
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=11436143)
> 摘要檔：[processed/11436143-summary.md](../../confluence/processed/11436143-summary.md)
> Confluence 最後更新：2020-11-23
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義 bet365htmlprovider 生命週期規則，VPN 重啟時必須自動關閉 provider。

**關鍵業務規則**：
- 當偵測到 VPN 重啟事件時，必須自動關閉 bet365htmlprovider 程序或服務。

**注意事項**：
- ⚠️ 文件未說明「VPN 重啟」的具體定義，實作時需人工確認
- ⚠️ 文件最後更新於 2020 年，可能已過時

---

### TCZB-1380 - [CrawlerAgent] - stock 每日監控

> Confluence 頁面 ID：24091672
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24091672)
> 摘要檔：[processed/24091672-summary.md](../../confluence/processed/24091672-summary.md)
> Confluence 最後更新：2022-02-09
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義 CrawlerAgent 每日監控股票資料的檢查機制與欄位處理規則。

**關鍵業務規則**：
- closemarket、company、etf、stockprice 等模組需每日比對 DB 並補值
- stockprice 無開盤價時用昨天收盤價（暫停交易除外）；異常值給 -99999 時由檢查機制回補

**注意事項**：
- ⚠️ 提及金管會研議週六補班股市不開的規則可能影響假日判斷，需確認現行是否仍適用

---

## 技術設計類

### .NET 爬蟲 (pageId=40502228)

> Confluence 頁面 ID：40502228
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40502228)
> 摘要檔：[processed/40502228-summary.md](../../confluence/processed/40502228-summary.md)
> Confluence 最後更新：2022-12-09
> 摘要最後同步：2026-05-27

**摘要**：
彙整運動博弈爬蟲清單、Provider 技術類型及未來計畫。

**關鍵設計決策**：
- ascbet provider 未來改用 WinApp 部署
- bet365 因瀏覽器模擬遭阻擋暫停抓取
- betfair 因頻寬問題暫停抓取

**影響範圍**：
- 影響 crawlerservice、crawlerflowservice 等多個服務的 Provider 部署與遷移策略

---

### PriceCenterService時序圖 (pageId=5341511)

> Confluence 頁面 ID：5341511
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=5341511)
> 摘要檔：[processed/5341511-summary.md](../../confluence/processed/5341511-summary.md)
> Confluence 最後更新：2022-01-11
> 摘要最後同步：2026-05-27

**摘要**：
說明 MLB Parser 從 ZooKeeper 取得設定、DataProvider 呼叫 API、Parser 處理到 MLBService 推送 nginx 的流程。

**關鍵設計決策**：
- 資料獲取分兩階段：先 Get All Game Data，再 Get Match Data for each match
- 採用 ZooKeeper 進行組態推送

**影響範圍**：
- 影響 crawlerservice、pricecenterservice 的資料獲取與分發管線

---

### 韓股 (pageId=44663901)

> Confluence 頁面 ID：44663901
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44663901)
> 摘要檔：[processed/44663901-summary.md](../../confluence/processed/44663901-summary.md)
> Confluence 最後更新：2022-12-28
> 摘要最後同步：2026-05-27

**摘要**：
記錄 Daum Finance 韓股的兩個外部 API 端點規格與必要 Header。

**關鍵設計決策**：
- 使用 `market` 參數區分 KOSPI/KOSDAQ
- 歷史資料使用 pagination 參數分頁

**影響範圍**：
- 影響 crawlerservice 串接韓股資料的爬取模組

---

### 日系銀行爬蟲清單 (pageId=55574955)

> Confluence 頁面 ID：55574955
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55574955)
> 摘要檔：[processed/55574955-summary.md](../../confluence/processed/55574955-summary.md)
> Confluence 最後更新：2024-03-19
> 摘要最後同步：2026-05-27

**摘要**：
列出日系銀行爬蟲部署方式、Cassandra 停啟用設定及僵屍處理流程。

**關鍵設計決策**：
- 每個爬蟲獨立 VM 部署
- 停啟用需操作 paypalpages 表

**影響範圍**：
- 影響 crawlerservice、pricecenterservice 的日系銀行爬蟲維運

---

### CoinMarketCap 介面 (pageId=24088137)

> Confluence 頁面 ID：24088137
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088137)
> 摘要檔：[processed/24088137-summary.md](../../confluence/processed/24088137-summary.md)
> Confluence 最後更新：2021-11-09
> 摘要最後同步：2026-05-27

**摘要**：
記錄呼叫 CoinMarketCap 需加入 homepage_table_customize cookie 以客製化欄位。

**關鍵設計決策**：
- 透過 cookie 指定首頁表格顯示欄位

**影響範圍**：
- 影響 crawlerservice CoinMarketCapAgent 的 header 設定

---

### 90vs provider review (pageId=55585347)

> Confluence 頁面 ID：55585347
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/90vs+provider+review)
> 摘要檔：[processed/55585347-summary.md](../../confluence/processed/55585347-summary.md)
> Confluence 最後更新：2025-04-09
> 摘要最後同步：2026-05-27

**摘要**：
列出 90vs provider 程式碼審查修正事項與 coding style 要求。

**關鍵設計決策**：
- Selenium 物件統一在 GetDriver 實例化
- 變數命名必須語意清晰

**影響範圍**：
- 影響 crawlerservice 的實作規範與可讀性

---

### TCZP-3691[Crawler]-90vs provider (pageId=55585294)

> Confluence 頁面 ID：55585294
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZP-3691%5BCrawler%5D-90vs+provider)
> 摘要檔：[processed/55585294-summary.md](../../confluence/processed/55585294-summary.md)
> Confluence 最後更新：2025-04-07
> 摘要最後同步：2026-05-27

**摘要**：
說明使用 Selenium 從 90vs.com 抓取籃球賽程及依比賽狀態調整抓取頻率。

**關鍵設計決策**：
- 賽中每 5 秒、賽前賽後每 8 分鐘抓取

**影響範圍**：
- 影響 crawlerservice 籃球賽程爬取策略

---

### [CloudProviderV2] review (pageId=76546649)

> Confluence 頁面 ID：76546649
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/%5BCloudProviderV2%5D+review)
> 摘要檔：[processed/76546649-summary.md](../../confluence/processed/76546649-summary.md)
> Confluence 最後更新：2025-05-19
> 摘要最後同步：2026-05-27

**摘要**：
列出 CloudProviderV2 程式碼審查改進要點（JSON 解析、空值判斷、thread 延遲等）。

**關鍵設計決策**：
- 使用框架 format='json()' 解析
- 大量 thread 啟動前加入 0.1 秒延遲

**影響範圍**：
- 影響 crawlerservice Provider 穩定性與 coding style

---

### TCZB-3776 [CrawlerAgentBetCity] - crawleragentbetcity (pageId=76547076)

> Confluence 頁面 ID：76547076
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3776+%5BCrawlerAgentBetCity%5D+-+crawleragentbetcity)
> 摘要檔：[processed/76547076-summary.md](../../confluence/processed/76547076-summary.md)
> Confluence 最後更新：2025-06-16
> 摘要最後同步：2026-05-27

**摘要**：
定義 BetCity 網站的爬蟲資料映射規則與盤口配置。

**關鍵設計決策**：
- 採用多層巢狀結構組織盤口配置
- 使用 date_ev 作為比賽時間

**影響範圍**：
- 影響 crawlerservice CrawlerAgentBetCity 資料標準化邏輯

---

### TCZB-3798 [crawleragenttonybet] - 資料格式改版修復 (pageId=79462466)

> Confluence 頁面 ID：79462466
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79462466)
> 摘要檔：[processed/79462466-summary.md](../../confluence/processed/79462466-summary.md)
> Confluence 最後更新：2026-04-16
> 摘要最後同步：2026-05-27

**摘要**：
記錄 Tonybet Provider/Parser 改版修復與效能調校細節。

**關鍵設計決策**：
- 延長 pregames/inplay 請求間隔
- 改為以球種為單位開執行緒

**影響範圍**：
- 影響 crawlerservice Tonybet 爬蟲效能與解析規則

---

### TCZB-3812 [crawleragentnpbyahoo] - 單場賽事對戰資訊 (pageId=79462896)

> Confluence 頁面 ID：79462896
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79462896)
> 摘要檔：[processed/79462896-summary.md](../../confluence/processed/79462896-summary.md)
> Confluence 最後更新：2025-07-16
> 摘要最後同步：2026-05-27

**摘要**：
定義 NPB Yahoo 單場賽事頁面抓取範圍與 yahoo_info JSON 結構。

**關鍵設計決策**：
- 賽前資訊存入 yahoo_info 物件

**影響範圍**：
- 影響 crawlerservice other_info 欄位輸出格式

---

### TCZB-3813 [NaverSportProvider] - Naver賽事資訊爬取 (pageId=79462884)

> Confluence 頁面 ID：79462884
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79462884)
> 摘要檔：[processed/79462884-summary.md](../../confluence/processed/79462884-summary.md)
> Confluence 最後更新：2025-07-11
> 摘要最後同步：2026-05-27

**摘要**：
說明 Naver Sports API 清單與單場詳情端點及依比賽狀態的請求策略。

**關鍵設計決策**：
- 依比賽狀態區分請求策略（賽中獨立 thread）

**影響範圍**：
- 影響 crawlerservice Naver 賽事資訊爬取邏輯

---

### TCZB-3886 [CrawlerAgent1xbet] - 賽車賽事 (pageId=79464345)

> Confluence 頁面 ID：79464345
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464345)
> 摘要檔：[processed/79464345-summary.md](../../confluence/processed/79464345-summary.md)
> Confluence 最後更新：2025-08-29
> 摘要最後同步：2026-05-27

**摘要**：
定義 1xbet 賽車（RC）賽事資料映射與 PlayMode 對應。

**關鍵設計決策**：
- 無主客隊時使用固定字串填充
- result_info 存放優勝者資訊

**影響範圍**：
- 影響 crawlerservice 賽車賽事資料處理

---

### TCZB-4084 [AStockParserV2] - Python重構 (pageId=79466791)

> Confluence 頁面 ID：79466791
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79466791)
> 摘要檔：[processed/79466791-summary.md](../../confluence/processed/79466791-summary.md)
> Confluence 最後更新：2025-12-09
> 摘要最後同步：2026-05-27

**摘要**：
記錄 AStockParserV2 從 cn.investing.com 抓取 A 股的技術設計與正則解析規則。

**關鍵設計決策**：
- 使用 tls_client 模擬 Chrome TLS 指紋
- Queue 生產者-消費者模式

**影響範圍**：
- 影響 crawlerservice A 股爬取排程與資料寫入

---

### TCZB-4108 [CrawlerAgentFortuna888] - fortuna888 Parser (pageId=79467251)

> Confluence 頁面 ID：79467251
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-4108+%5BCrawlerAgentFortuna888%5D+-+fortuna888+Parser)
> 摘要檔：[processed/79467251-summary.md](../../confluence/processed/79467251-summary.md)
> Confluence 最後更新：2025-12-15
> 摘要最後同步：2026-05-27

**摘要**：
說明 Fortuna888 足球賠率解析器設計與正則萃取 JSON 流程。

**關鍵設計決策**：
- 以 game_id 為鍵值建立 store 字典關聯資料

**影響範圍**：
- 影響 crawlerservice Fortuna888 解析邏輯

---

### TCZB-4114 [PTT爬蟲] - 籃球、NBA、棒球版 (pageId=79467395)

> Confluence 頁面 ID：79467395
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467395)
> 摘要檔：[processed/79467395-summary.md](../../confluence/processed/79467395-summary.md)
> Confluence 最後更新：2026-01-09
> 摘要最後同步：2026-05-27

**摘要**：
定義 PTT 爬蟲的資料篩選邏輯與輸出檔案格式。

**關鍵設計決策**：
- 只爬取 2 天內且回覆數 ≥20 的指定類別文章

**影響範圍**：
- 影響 crawlerservice PTT 新聞爬取與檔案命名

---

### TCZB-4138 [新聞爬蟲] - 美國yahoo、日本yahoo (足、籃、棒) (pageId=79467593)

> Confluence 頁面 ID：79467593
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467593)
> 摘要檔：[processed/79467593-summary.md](../../confluence/processed/79467593-summary.md)
> Confluence 最後更新：2026-01-13
> 摘要最後同步：2026-05-27

**摘要**：
定義日本/美國 Yahoo 運動新聞爬取流程與 PTT 格式輸出。

**關鍵設計決策**：
- 日本雅虎優先使用 contents_list API

**影響範圍**：
- 影響 crawlerservice Yahoo 新聞爬取

---

### TCZB-4140 [Fortuna888] - 改抓CR Sport (pageId=79467589)

> Confluence 頁面 ID：79467589
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467589)
> 摘要檔：[processed/79467589-summary.md](../../confluence/processed/79467589-summary.md)
> Confluence 最後更新：2026-01-12
> 摘要最後同步：2026-05-27

**摘要**：
定義 Fortuna888 CR Sport 站台的抓取範圍、玩法過濾與 game_id 生成規則。

**關鍵設計決策**：
- game_id 使用聯盟+隊名雜湊+日期生成

**影響範圍**：
- 影響 crawlerservice Fortuna888 CR Sport 爬取

---

### TCZB-4303 [Python] - 爬蟲Chrome開啟異常處理 (pageId=79470448)

> Confluence 頁面 ID：79470448
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79470448)
> 摘要檔：[processed/79470448-summary.md](../../confluence/processed/79470448-summary.md)
> Confluence 最後更新：2026-04-20
> 摘要最後同步：2026-05-27

**摘要**：
記錄清理重複標題網頁與記憶體過量網頁的 Provider 實作。

**關鍵設計決策**：
- 單一網頁記憶體超過總記憶體 12.5% 即關閉

**影響範圍**：
- 影響 crawlerservice Chrome 環境穩定性

---

### TCZB-4335 [NewTeam] - TPHubService、TPCrawlerService 鄒型框架建構 (pageId=79471141)

> Confluence 頁面 ID：79471141
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471141)
> 摘要檔：[processed/79471141-summary.md](../../confluence/processed/79471141-summary.md)
> Confluence 最後更新：2026-05-14
> 摘要最後同步：2026-05-27

**摘要**：
定義 TPHubService 與 TPCrawlerService 的非同步 Kafka 與 PostgreSQL 批次寫入設計。

**關鍵設計決策**：
- 採用 aiokafka + asyncpg 全非同步技術棧
- 寫入順序：聯盟 → 隊伍 → 賽事 → 賠率

**影響範圍**：
- 影響 crawlerservice 新一代 TPCrawlerService 架構

---

### CrawlerService 重構計畫 (pageId=79471040)

> Confluence 頁面 ID：79471040
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471040)
> 摘要檔：[processed/79471040-summary.md](../../confluence/processed/79471040-summary.md)
> Confluence 最後更新：2026-05-03
> 摘要最後同步：2026-05-27

**摘要**：
完整 CrawlerService 重構技術設計，導入 BoundedChannel 與 WriteBuffer 批次寫入。

**關鍵設計決策**：
- DomainService / Infrastructure / Interface / Model 四層架構
- BoundedChannel 15s + WriteBuffer 5s 批次寫入

**影響範圍**：
- 影響 crawlerservice 整體重構與可維護性

---

### TCZB-2023 [CrawlerService] - Write OtherInfo & ResultInfo to DB & send to hub&api (pageId=38012381)

> Confluence 頁面 ID：38012381
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=38012381)
> 摘要檔：[processed/38012381-summary.md](../../confluence/processed/38012381-summary.md)
> Confluence 最後更新：2022-08-18
> 摘要最後同步：2026-05-27

**摘要**：
定義 resultinfo/otherinfo 欄位新增與各服務的資料流處理策略。

**關鍵設計決策**：
- resultinfo/otherinfo 採用 map<text,text> 結構

**影響範圍**：
- 影響 crawlerservice、pricecenterservice 的賽事資訊輸出

---

### TCZB-2060 [nowscore]-抓取nowscore站台(全部球種)比分資訊 (pageId=40502466)

> Confluence 頁面 ID：40502466
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40502466)
> 摘要檔：[processed/40502466-summary.md](../../confluence/processed/40502466-summary.md)
> Confluence 最後更新：2022-09-29
> 摘要最後同步：2026-05-27

**摘要**：
定義 nowscore 各球種 API 端點與足球完賽時抓取 detail 的規則。

**關鍵設計決策**：
- 足球必須抓取 detail 頁面取得進球時間點

**影響範圍**：
- 影響 crawlerservice nowscore 比分爬取

---

### Pinnacle json內容 (pageId=11436168)

> Confluence 頁面 ID：11436168
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=11436168)
> 摘要檔：[processed/11436168-summary.md](../../confluence/processed/11436168-summary.md)
> Confluence 最後更新：2020-11-23
> 摘要最後同步：2026-05-27

**摘要**：
展示 Pinnacle API 的 Match Data 與 Odds Data JSON 結構範例。

**關鍵設計決策**：
- Period 0 為全場、1 為上半場

**影響範圍**：
- 影響 crawlerservice Pinnacle 資料解析

---

### a股下市爬取 (pageId=47219651)

> Confluence 頁面 ID：47219651
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47219651)
> 摘要檔：[processed/47219651-summary.md](../../confluence/processed/47219651-summary.md)
> Confluence 最後更新：2023-03-13
> 摘要最後同步：2026-05-27

**摘要**：
提供深圳/上海交易所下市股票 Excel 下載端點與 xlrd 相容處理方式。

**關鍵設計決策**：
- showtype 必須改為 xls 才能用 xlrd 讀取

**影響範圍**：
- 影響 crawlerservice A 股下市資料爬取

---

## 歷史決策類

### DataBase Information (pageId=8716756)

> Confluence 頁面 ID：8716756
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/DataBase+Information)
> 摘要檔：[processed/8716756-summary.md](../../confluence/processed/8716756-summary.md)
> Confluence 最後更新：2021-04-06
> 摘要最後同步：2026-05-27

**決策背景**：
記錄多個爬蟲遇到的欄位異常及處理決策。

**決策結論**：
- 壘包狀態統一採用布林值
- 主客隊位置反轉問題延後至賽事合併階段處理

**影響**：
- 影響 crawlerservice 資料清洗邏輯與 gamecombineservice 轉換處理

---

### InvestingFAgent  介面 (pageId=24088566)

> Confluence 頁面 ID：24088566
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088566)
> 摘要檔：[processed/24088566-summary.md](../../confluence/processed/24088566-summary.md)
> Confluence 最後更新：2025-08-13
> 摘要最後同步：2026-05-27

**決策背景**：
Investing.com 匯率頁面改版，買賣價格區塊移除。

**決策結論**：
- 改抓取 forward-rates 頁面

**影響**：
- 影響 crawlerservice InvestingFAgent 的目標 URL

---

### 使用AI對CrawlerService進行重構 (pageId=79471031)

> Confluence 頁面 ID：79471031
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471031)
> 摘要檔：[processed/79471031-summary.md](../../confluence/processed/79471031-summary.md)
> Confluence 最後更新：2026-05-02
> 摘要最後同步：2026-05-27

**決策背景**：
使用 Claude AI 輔助規劃 CrawlerService 重構。

**決策結論**：
- 採用 PLAN_SPEC 範本生成結構化計畫
- 移除 needUpdateDB 等廢棄功能

**影響**：
- 影響 crawlerservice 重構方向與 AI 輔助開發流程

---

### 使用Cline掛載Deepseek檢查Plan (pageId=79471062)

> Confluence 頁面 ID：79471062
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471062)
> 摘要檔：[processed/79471062-summary.md](../../confluence/processed/79471062-summary.md)
> Confluence 最後更新：2026-05-04
> 摘要最後同步：2026-05-27

**決策背景**：
使用 Cline + Deepseek 審查 CrawlerService 重構計畫。

**決策結論**：
- 計畫升級至 .NET 8
- BAK 環境 WriteDB 設定回歸一般流程

**影響**：
- 影響 crawlerservice 重構計畫最終版本

---

### TCZB-1605 [DB]-Local Service更改DB IP (pageId=32538952)

> Confluence 頁面 ID：32538952
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32538952)
> 摘要檔：[processed/32538952-summary.md](../../confluence/processed/32538952-summary.md)
> Confluence 最後更新：2022-03-08
> 摘要最後同步：2026-05-27

**決策背景**：
資料庫 keyspace 從舊 DB（231~233）遷移至新 DB（234）。

**決策結論**：
- 列出受影響 keyspace 與各服務負責人

**影響**：
- 影響 crawlerservice 等多個服務的 DB 連線設定

---

### TCZB-2300 [Stock] - 美韓A股檢查機制 (pageId=44663098)

> Confluence 頁面 ID：44663098
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44663098)
> 摘要檔：[processed/44663098-summary.md](../../confluence/processed/44663098-summary.md)
> Confluence 最後更新：2022-12-13
> 摘要最後同步：2026-05-27

**決策背景**：
記錄 2022 年美、韓、A 股股票價格資料的異常檢查結果。

**決策結論**：
- 列出具體異常日期與問題現象

**影響**：
- 影響 crawlerservice 股票資料品質監控

---

### TCZB-2879 爬取歷史先發投手數據 (pageId=47223046)

> Confluence 頁面 ID：47223046
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47223046)
> 摘要檔：[processed/47223046-summary.md](../../confluence/processed/47223046-summary.md)
> Confluence 最後更新：2023-08-14
> 摘要最後同步：2026-05-27

**決策背景**：
MLB 官網提供歷史先發投手數據的速度有時較慢。

**決策結論**：
- 需留意延遲並設計備用來源或重試機制

**影響**：
- 影響 crawlerservice MLB 先發投手資料完整性

---

### TPCrawlerService review (pageId=79471429)

> Confluence 頁面 ID：79471429
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TPCrawlerService+review)
> 摘要檔：[processed/79471429-summary.md](../../confluence/processed/79471429-summary.md)
> Confluence 最後更新：2026-05-15
> 摘要最後同步：2026-05-27

**決策背景**：
對 TPCrawlerService 代碼進行審查，列出不符合規範事項。

**決策結論**：
- 禁止使用全域變數、底線開頭命名等
- 爬取資料先快取驗證再寫入 TAMP 表

**影響**：
- 影響 crawlerservice TPCrawlerService 編碼標準與資料寫入策略

---

## 操作手冊類

### 爬蟲VPN連線狀況 (pageId=24084654)

> Confluence 頁面 ID：24084654
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24084654)
> 摘要檔：[processed/24084654-summary.md](../../confluence/processed/24084654-summary.md)
> Confluence 最後更新：2021-07-28
> 摘要最後同步：2026-05-27

**摘要**：
記錄不同 VPN 伺服器對 TG、KU、HGA 等目標網站的連線狀態表格。

**AI 開發需要注意的部分**：
- 文件已過期兩年以上，VPN 狀態可能大幅變動，不建議直接作為配置依據

---

### 日系銀行爬蟲清單 (pageId=55574955)

> Confluence 頁面 ID：55574955
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55574955)
> 摘要檔：[processed/55574955-summary.md](../../confluence/processed/55574955-summary.md)
> Confluence 最後更新：2024-03-19
> 摘要最後同步：2026-05-27

**摘要**：
列出日系銀行爬蟲的 VM 部署、RDP 連線及 Cassandra 操作流程。

**AI 開發需要注意的部分**：
- 爬蟲僵屍化時需手動進入 VM 關閉程序
- 密碼以明文記錄於文件中，有資安疑慮

---

### TCZB Sprint21 - KUProvider 爬取棒球其他賠率 (pageId=18087938)

> Confluence 頁面 ID：18087938
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=18087938)
> 摘要檔：[processed/18087938-summary.md](../../confluence/processed/18087938-summary.md)
> Confluence 最後更新：2021-04-19
> 摘要最後同步：2026-05-27

**摘要**：
Sprint 執行與檢查清單，描述標準開發流程。

**AI 開發需要注意的部分**：
- 內容為通用模板，無具體爬取規則

---

### konibet provider v2 code review (pageId=55581360)

> Confluence 頁面 ID：55581360
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/konibet+provider+v2+code+review)
> 摘要檔：[processed/55581360-summary.md](../../confluence/processed/55581360-summary.md)
> Confluence 最後更新：2024-09-24
> 摘要最後同步：2026-05-27

**摘要**：
對 konibet provider v2 的效能審查建議。

**AI 開發需要注意的部分**：
- 建議將 datetime.now() 移出迴圈
- 部分 time.sleep() 可能多餘，需人工確認

---