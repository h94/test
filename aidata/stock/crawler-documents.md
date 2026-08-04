# crawler — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-28 03:44
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類


### A股

> Confluence 頁面 ID：44663880
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44663880)
> 摘要檔：[processed/44663880-summary.md](../../confluence/processed/44663880-summary.md)
> Confluence 最後更新：2022-12-28
> 摘要最後同步：2026-05-26

**摘要**：
文件提供了从 Investing.com 获取中国 A 股数据的两个 API 规格：通过 POST 到 stock-screener 接口获取股票代码列表（支持分页，每页 50 条），以及通过 GET 历史数据接口获取某只股票日线数据。对开发数据抓取服务有直接参考价值，明确了请求头、参数格式和响应结构。

**關鍵業務規則**：
- 获取股票列表时，必须携带 x-requested-with: XMLHttpRequest 头
- 国家代码参数 country[] 固定为 '37' 代表中国
- 分页参数 pn 从 1 开始，需根据返回的总笔数循环调用直到获取全部代码
- 获取历史数据时，必须在请求头中加入 domain-id: cn
- 历史数据接口的 time-frame 固定为 Daily，add-missing-rows 固定为 false
- start-date 和 end-date 格式为 YYYY-MM-DD，由调用方指定

**注意事項**：
- ⚠️ 文件最后更新于 2022-12-28，距今已较久，API 接口或响应字段可能已变更，需人工验证
- ⚠️ 股票代码格式（/api/financialdata/historical/{code} 中的 code）未明确说明是从搜索接口返回的哪个字段获取，可能导致解析错误

---

## 技術設計類


### CoinMarketCapAgent

> Confluence 頁面 ID：24088134
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/CoinMarketCapAgent)
> 摘要檔：[processed/24088134-summary.md](../../confluence/processed/24088134-summary.md)
> Confluence 最後更新：2021-11-09
> 摘要最後同步：2026-05-26

**摘要**：
本文件提供 CoinMarketCap 網站首頁表格的自定義 cookie，用於指定顯示 24 小時漲跌幅、成交量、最高價、最低價等數據。在 AI 開發加密貨幣爬蟲時，需要通過此 cookie 模擬用戶偏好，確保爬取到所需的結構化數據，避免網站返回默認視圖。

**關鍵設計決策**：
- 使用 homepage_table_customize cookie 指定表格列，以便爬蟲獲取 24h 漲跌幅、成交量、最高價、最低價等字段，而非依賴網頁默認顯示。

**注意事項**：
- ⚠️ 文檔最後更新於 2021 年，CoinMarketCap 網站可能已改版，cookie 格式或功能可能已失效，需人工確認。

### TCZB-3718 [BinanceCAgentV2] Binance Python重構

> Confluence 頁面 ID：76546158
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76546158)
> 摘要檔：[processed/76546158-summary.md](../../confluence/processed/76546158-summary.md)
> Confluence 最後更新：2025-04-30
> 摘要最後同步：2026-05-27

**摘要**：
本文件說明 BinanceCAgentV2 如何透過 WebSocket 從 Binance 即時獲取 BTC、ETH 的成交價與 24 小時成交量，並在價格變動時以固定 JSON 格式發送至 PRD Kafka 的 cryptodata topic。內容包含訂閱頻道、資料結構、價格比對去重邏輯，以及 Volume 計算方式（24h 成交量 / 當前價格）。

**關鍵設計決策**：
- 採用 WebSocket 串流以取得即時資料，避免高頻輪詢。
- 以價格是否變動作為 Kafka 發送條件，減少重複訊息，降低下游處理開銷。
- 價格與成交量來自不同串流，故需用快取暫存成交量，供後續計算 Volume 使用。

**注意事項**：
- ⚠️ 文中圖片標示的訂閱內容未直接以文字呈現，需人工確認是否有遺漏的頻道或幣種。
- ⚠️ 緩存儲存方式（記憶體／Redis）與失效機制未明文規定，可能影響 Volume 計算準確性，需人工確認。
- ⚠️ 文件標題雖提及「Python 重構」，但實際內容多為當前實作描述，未區分新舊差異。

---

## 歷史決策類


### TCZB-3761[HuoBiCAgentV2] - 火幣 Python重構

> Confluence 頁面 ID：76546923
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76546923)
> 摘要檔：[processed/76546923-summary.md](../../confluence/processed/76546923-summary.md)
> Confluence 最後更新：2025-05-29
> 摘要最後同步：2026-05-27

**決策背景**：
本文件說明火幣（HTX）交易所 4 個幣對（ETH/USDT, TUSD/USDT, USDC/USDT, BTC/USDT）的即時價格與成交量透過 WebSocket 抓取，binary 訊息需 gzip 解壓後轉為 JSON，提取 close（價格）與 amount（成交量），組裝成包含 Site, Name, Datum, CryptoBasic 等欄位的訊息，發送到 PRD Kafka 的 cryptodata topic。

**決策結論**：
- 採用 WebSocket 而非輪詢以獲取即時行情，訂閱 market.<幣種>usdt.detail 頻道

**影響**：
- 需確認 PRD 環境 Kafka topic 名稱是否仍為 cryptodata
- 火幣交易所已更名為 HTX，域名為 htx.com，文件使用 htx.com 為正確，但仍需確認舊版 huobi 域名是否已全面棄用

---

## 操作手冊類


### TCZB-2376 [AStockHistoryParser] - A股歷史修復

> Confluence 頁面 ID：44663948
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44663948)
> 摘要檔：[processed/44663948-summary.md](../../confluence/processed/44663948-summary.md)
> Confluence 最後更新：2023-01-03
> 摘要最後同步：2026-05-27

**摘要**：
文件定義了一個從 investing.com 抓取 A 股歷史日線數據並存入 DB 的修復程序。程序通過文件記錄待處理股票代碼並在成功寫入後刪除記錄，支持斷點續傳；使用兩個 API 獲取代碼列表（分頁，每頁 50 筆）和歷史數據（指定日期範圍），遇到 403 錯誤時停止所有請求並等待後重啟。

**AI 開發需要注意的部分**：
- API 返回 403 狀態碼時，必須停止所有動作並等待數秒後重啟。
- 股票代碼處理成功並寫入 DB 後，必須從記錄檔案中刪除該代碼，避免重複處理。
- 獲取代碼列表的分頁請求需根據首次響應的 totalCount 計算總頁數，每頁固定返回 50 筆。