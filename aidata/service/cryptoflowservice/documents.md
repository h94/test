# cryptoflowservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 12:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類


### Cryptocurrency SupportList

> Confluence 頁面 ID：24088231
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Cryptocurrency+SupportList)
> 摘要檔：[processed/24088231-summary.md](../../confluence/processed/24088231-summary.md)
> Confluence 最後更新：2023-12-18 08:59
> 摘要最後同步：2026-05-26 12:00
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件列出系統從各匯率資訊源（如Huobi、Binance、MaiCoin Max、Pionex、Coinbase Pro、BOT、Yahoo、Investing、SMBC）所支援的貨幣兌換對清單，包含加密貨幣對加密貨幣（如BTC/USDT）及加密貨幣對法幣（如USDT/USD）的組合。部分項目（如BUSD/USDT）已被刪除線標記，可能表示已停止支援。對AI開發而言，此清單可作為匯率查詢服務允許的邊界，用於限制資料擷取範圍、前端顯示選項或校驗輸入參數。

**關鍵業務規則**：
- Huobi 資訊源支援以下貨幣對：TUSD/USDT, USDC/USDT, BTC/USDT, ETH/USDT。
- Binance 資訊源支援以下貨幣對：ETH/USDT, BTC/USDT（原BUSD/USDT已刪除線，可能不再支援）。
- MaiCoin Max 資訊源支援以下貨幣對：BTC/USDT, ETH/USDT, USDC/USDT。
- Pionex 資訊源支援以下貨幣對：ETH/USDT, USDC/USDT, BTC/USDT（原BUSD/USDT已刪除線，可能不再支援）。
- Coinbase Pro 資訊源僅支援 USDT/USD。
- BOT（台灣銀行）資訊源支援多組 TWD/X 與 USD/X 的兌換對，涵蓋 USD, KRW, VND, SEK, CNY, MYR, EUR, IDR, PHP, THB, NZD, CHF, CAD, AUD, GBP, HKD, SGD, JPY；以及 TWD/USD, TWD/KRW 等。
- Yahoo 資訊源支援 USD/X 與 USDT/USD 在內的多組貨幣對，包含 TWD, VND, JPY, KRW, PHP, MYR, EUR, CNY, IDR, HKD, GBP, SGD, THB, CHF, SEK, CAD, AUD, NZD, MXN。
- Investing 資訊源支援 USD/X 在內的多組貨幣對，包含 TWD, HKD, GBP, AUD, CAD, SGD, CHF, JPY, SEK, NZD, THB, PHP, IDR, EUR, KRW, VND, MYR, CNY。
- SMBC（三井住友銀行）資訊源僅支援 JPY/USD。
- 所有支援的貨幣對表示系統可從對應的資訊源獲取該匯率資料，未列出的組合不得查詢或使用。
- BUSD/USDT 在 Binance 與 Pionex 皆以刪除線標示，可能已停止支援，實作時應排除或警示。

**注意事項**：
- ⚠️ Binance 和 Pionex 中的 BUSD/USDT 已畫刪除線，需人工確認此貨幣對是否仍在服務中，或已移除支援。
- ⚠️ 文件中 Coinbase Pro 僅列出 USDT/USD，其他潛在貨幣對是否支援需人工確認。
- ⚠️ 表格中的資料說明指出「TUSD/USDT為資訊源提供TUSD轉USDT的匯率」，類似定義可能適用於所有貨幣對，但未明確說明其他貨幣對的方向性。

### TCZB-1256 [CryptoFlowService]-Crypto data寫入DB

> Confluence 頁面 ID：24088430
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088430)
> 摘要檔：[processed/24088430-summary.md](../../confluence/processed/24088430-summary.md)
> Confluence 最後更新：2021-11-15 14:44
> 摘要最後同步：2026-05-27 07:03
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義 CryptoFlowService 將虛擬幣資料存入 Cassandra 的寫入規則。核心行為是每正 5 秒觸發一次批量寫入，且必須去除 5 秒內的重複資料（distinct）。資料來源為 Kafka，表結構定義在另份文件中。對 AI 開發而言，明確了定時寫入頻率和去重需求，有助於實現冪等性和定時任務排程。

**關鍵業務規則**：
- 每整 5 秒（如 00:00:00, 00:00:05）執行一次寫入作業，將虛擬幣資料寫入 Cassandra。
- 寫入前須對 5 秒內的重複資料做 distinct 處理，確保同一時間窗口內重複的資料只寫入一次。

**注意事項**：
- ⚠️ 文件未明確定義「重複」的判定條件（如使用哪些欄位作為去重 key），需人工確認實作細節。
- ⚠️ 文件位於「舊的 Projects 1-200」路徑，可能已過時或已被後續設計取代，使用前須與現行實作比對。

---

## 技術設計類


### CoinBaseAgent 介面

> Confluence 頁面 ID：24088314
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088314)
> 摘要檔：[processed/24088314-summary.md](../../confluence/processed/24088314-summary.md)
> Confluence 最後更新：2021-11-17 13:28
> 摘要最後同步：2026-05-26 13:10
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件提供 Coinbase WebSocket 的訂閱請求格式與連線位址，定義如何訂閱 level2、heartbeat、ticker 等頻道以獲取即時市場數據。響應部分缺失，僅保留請求範例，可作為 Coinbase Agent 實作的技術參考。

**關鍵業務規則**：
—

**注意事項**：
- ⚠️ 響應格式段落空白，文件不完整，實際回應結構需從 Coinbase API 文件或程式碼補充。
- ⚠️ 文件最後更新於 2021-11-17，需確認 Coinbase WebSocket 端點與訂閱格式是否仍符合現行 API 版本。

### MaiCoinAgent API

> Confluence 頁面 ID：24088326
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/MaiCoinAgent+API)
> 摘要檔：[processed/24088326-summary.md](../../confluence/processed/24088326-summary.md)
> Confluence 最後更新：2021-11-15 13:54
> 摘要最後同步：2026-05-26 13:19
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件記錄了 MaiCoin 交易所的 Websocket 訂閱格式（可訂閱多市場 ticker）及 REST API 端點（/api/v2/tickers），用於即時或批次取得加密貨幣報價。對 AI 開發而言，這是外部數據來源的參考，有助於理解 MaiCoinAgent 如何獲取原始行情。但文件極簡略，缺少錯誤處理、資料模型或業務邏輯說明。

**關鍵業務規則**：
—

**注意事項**：
- ⚠️ 文件最後更新於 2021-11-15，API 端點可能已變更或過時，需人工確認是否仍在使用。
- ⚠️ 文件內容過於簡略，未說明斷線重連、認證或具體回應欄位，實際整合時需查閱 MaiCoin 官方文件。

### CryptoFlowService 時序圖

> Confluence 頁面 ID：24088366
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088366)
> 摘要檔：[processed/24088366-summary.md](../../confluence/processed/24088366-summary.md)
> Confluence 最後更新：2021-11-15 14:33
> 摘要最後同步：2026-05-26 13:30
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件以時序圖方式呈現 CryptoFlowService 的核心資料處理流程：從 Kafka 取得訊息後，呼叫 Nuget 進行基礎驗證，最後將驗證通過的資料寫入資料庫。對 AI 開發的幫助為：可快速掌握服務的輸入來源（Kafka）、處理步驟（驗證後入庫）及外部依賴（Nuget、DB），有助於模擬互動行為或建立自動化測試假設。

**關鍵業務規則**：
—

**注意事項**：
- ⚠️ 最後更新於 2021-11-15，距今已過長時間，流程可能已有變更，建議與最新程式碼比對。
- 文件中僅有流程圖，未描述驗證規則、DB Schema 或錯誤處理細節，實作時須參照其他規範。
- Nuget 在此處的確切角色（類別庫、內部服務或第三方元件）不明，需人工確認。

---

## 歷史決策類

暫無相關文件。

---

## 操作手冊類

暫無相關文件。