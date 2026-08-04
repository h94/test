# cryptocacheservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 07:30
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---


## 業務規範類


### Crypto 需求文件

> Confluence 頁面 ID：24087640
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24087640)
> 摘要檔：[processed/24087640-summary.md](../../confluence/processed/24087640-summary.md)
> Confluence 最後更新：2021-11-11
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件說明加密貨幣匯率抓取需求，包括法幣匯率來源（鉅亨、Yahoo）與 USDT 匯率來源（Yahoo、Pionex、Maicoin、Huobi、Binance、Coinbase）。最初決策以當地銀行現金賣出價為基準，後來變更為需將匯差納入計算，但具體計算方式未載明。對 AI 開發有助於確認匯率數據來源與匯差處理方向，但細節不足，需擴充實作規則。

**關鍵業務規則**：
- 法幣匯率應從鉅亨、Yahoo 抓取，USDT 匯率應從 Yahoo、Pionex、Maicoin、Huobi、Binance、Coinbase 抓取（具體抓取元素與格式見文件截圖，因截圖無法存取，需人工確認）
- 匯率計算必須考慮匯差，之前曾規劃統一使用銀行現金賣出價，但後續決議需將匯差納入，實際計算方法與參數未規範，需人工確認

**注意事項**：
- ⚠️ 文件內所有截圖均無法存取，無法得知實際抓取的 CSS 選取器或 API 端點
- ⚠️ 關於匯差的規則前後不一致：先劃掉「統一使用現金匯率賣出價」，後改為「需要將匯差考慮進去」，但未說明匯差定義或計算方式，容易誤解
- ⚠️ 文件最後更新日期為 2021-11-11，可能已與現行系統行為不同，需人工確認目前匯率計算規則是否仍以此為基礎


### Cryptocurrency 產品項目

> Confluence 頁面 ID：24088218
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088218)
> 摘要檔：[processed/24088218-summary.md](../../confluence/processed/24088218-summary.md)
> Confluence 最後更新：2022-11-03
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件定義了 Cryptocurrency 產品的支援資料源，包括 Huobi、Binance 等交易所和 Yahoo、Investing 等資訊平台，提供穩定幣兌換、USDT/USD、法幣兌換等匯率數據。對 AI 開發而言，這份文件界定了可合法使用的數據來源範圍，有助於設計匯率查詢、價格預測等功能的數據接入邏輯。免責聲明提醒資料僅供參考且可能隨時變更，開發時需考慮容錯與非強依賴的設計。

**關鍵業務規則**：
- 支援的穩定幣兌換資料源包括 Huobi、Binance、MaiCoin Max、Pionex；USDT/USD 匯率來源包括 Coinbase Pro、Yahoo；USD/其他法定貨幣匯率來源包括 Yahoo、Investing；台幣兌換匯率來自台灣銀行 (BOT)；日幣兌換匯率來自三井住友銀行 (SMBC)
- 所有資料僅供參考分析之用，本網站可能隨時更改資料且不另行通知，不對準確性或使用後果承擔責任；用戶若意圖進行不當行為需自行承擔後果

**注意事項**：
- ⚠️ 最後更新於 2022-11-03，資料源列表可能已過時（例如 Coinbase Pro 已重組為 Coinbase Advanced Trade），需人工確認當前實際支援的數據源
- ⚠️ 免責聲明強調資料可能隨時變更並不另行通知，因此開發時不可將此清單視為固定合約，應設計動態配置或定期審查機制

---

## 技術設計類


### Currency Redis Schema

> Confluence 頁面 ID：24087418
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Currency+Redis+Schema)
> 摘要檔：[processed/24087418-summary.md](../../confluence/processed/24087418-summary.md)
> Confluence 最後更新：2021-11-15
> 摘要最後同步：2026-05-26

**摘要**：
這份文件定義了 Redis db8 中加密貨幣匯率的 HASH 結構，以交易所及貨幣對作為 key（例：houbi_USDT_USD），包含 Basic、OrderBook、MarketTrades 三個欄位。Basic 欄位存放價格、高低、漲跌、成交量等 JSON 資料。對 AI 開發來說，這提供了讀取快取時所需的欄位名稱與格式，避免猜測鍵值或取值錯誤。

**關鍵設計決策**：
- 採用 Redis HASH 儲存每個貨幣對的快取，而非多個獨立的 String key，方便一次獲取 Basic、OrderBook、MarketTrades 相關資料
- HASH 內的 field 值（如 Basic）直接存放 JSON 字串，而不將每個價格欄位拆成獨立 field，保留資料結構的彈性
- Key 命名規則為 '{交易所}_{貨幣對}'，例如 'houbi_USDT_USD'，便於程式動態組合並查詢不同來源的匯率

**影響範圍**：
- 所有讀取加密貨幣快取資料的服務或程式碼，都依賴此 Redis Schema 設計


### CryptoCacheService Redis Schema

> Confluence 頁面 ID：24087662
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/CryptoCacheService+Redis+Schema)
> 摘要檔：[processed/24087662-summary.md](../../confluence/processed/24087662-summary.md)
> Confluence 最後更新：2021-11-01
> 摘要最後同步：2026-05-26

**摘要**：
這份文件的實質內容為參考連結，指向 Currency Redis Schema 文件。對 AI 開發來說，這表示 CryptoCacheService 的 Redis 資料結構設計可能與 Currency 模組高度相似或共用同一套 Schema 定義，開發時應以 Currency Redis Schema 為基礎來理解 CryptoCacheService 的資料模型。

**關鍵設計決策**：
- CryptoCacheService 的 Redis Schema 設計決策為直接沿用或參考 Currency 模組的 Redis Schema 設計，而非獨立定義

**影響範圍**：
- 此設計決策影響任何直接操作或依賴 CryptoCacheService Redis 資料的程式碼，需確保與 Currency Redis Schema 保持一致


### CryptoCacheService 時序圖

> Confluence 頁面 ID：24087688
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24087688)
> 摘要檔：[processed/24087688-summary.md](../../confluence/processed/24087688-summary.md)
> Confluence 最後更新：2021-11-15
> 摘要最後同步：2026-05-26

**摘要**：
這是一個 CryptoCacheService 的簡易時序圖，描述服務從 Kafka 消費資料，透過 Nuget 進行基礎驗證，再寫入 Redis 的流程。對 AI 開發的幫助在於釐清此服務的資料輸入來源（Kafka）、驗證層（Nuget）與儲存層（Redis），可作為實作或除錯時的參考。

**關鍵設計決策**：
- 採用 Nuget 進行基礎驗證（文件未說明為何選擇 Nuget 而非其他驗證機制，需人工確認）
- 驗證後資料直接寫入 Redis，推測為快取或暫存用途

**影響範圍**：
- 此流程定義了 cryptocacheservice 的核心資料處理路徑，任何對該服務的修改或呼叫都應遵守此基本流程


### TCZB-1213 [CryptoCacheService]-CryptoData 寫入 Redis

> Confluence 頁面 ID：24087845
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24087845)
> 摘要檔：[processed/24087845-summary.md](../../confluence/processed/24087845-summary.md)
> Confluence 最後更新：2021-11-02
> 摘要最後同步：2026-05-27

**摘要**：
本文件描述 CryptoCacheService 的核心功能：接收來自爬蟲的加密貨幣資料（透過 Kafka 傳遞，格式遵循 Currency Kafka Data Define），進行驗證後寫入 Redis（格式遵循 Currency Redis Schema）。文件提供了時序圖與流程圖的連結，作為開發此服務的設計參考。對 AI 開發而言，這份文件揭示了 cryptocacheservice 的資料流方向（Kafka → 驗證 → Redis）及其依賴的資料合約。

**關鍵設計決策**：
- 選用 Redis 作為加密貨幣資料的快取儲存，以提供快速讀取（推斷，文件未明確說明原因）
- 採用 Kafka 接收爬蟲資料，實現非同步處理與解耦（推斷，文件未明確說明原因）

**影響範圍**：
- 此設計影響 cryptocacheservice 的讀寫效能與資料一致性，任何變更都需考慮對 Redis 和 Kafka 的依賴

---

## 操作手冊類


### TCZB Sprint 35 - Cryptocurrency

> Confluence 頁面 ID：24087507
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB+Sprint+35+-+Cryptocurrency)
> 摘要檔：[processed/24087507-summary.md](../../confluence/processed/24087507-summary.md)
> Confluence 最後更新：2021-11-01
> 摘要最後同步：2026-05-26

**摘要**：
這是一份 Scrum Sprint 管理操作手冊，定義了從需求評估、開發、測試到上線的完整流程與檢查清單。內容涵蓋每日站會、JIRA 工作記錄、測試進度追蹤、Git 分支建立、Swagger 更新等標準作業。對 AI 開發而言，可作為理解團隊 DevOps 流程、交付規範與質量把關機制的參考。

**AI 開發需要注意的部分**：
- 文件中定義的開發流程（如 Git 分支策略、Swagger 更新要求）可能仍影響目前的 CI/CD 管線，但建議確認現行做法
- 標題雖為 Cryptocurrency，但內文未涉及加密貨幣業務細節，此文件更偏向通用管理流程，而非服務特定資訊