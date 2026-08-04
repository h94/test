# currencyservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### Currency Name Define

> Confluence 頁面 ID：24087837
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Currency+Name+Define)
> 摘要檔：[processed/24087837-summary.md](../../confluence/processed/24087837-summary.md)
> Confluence 最後更新：2021-11-15
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本篇定義了系統支援的虛擬幣（USDT、USDC、BUSD、HUSD、TUSD）、虛擬幣交易站台（如 binance、huobi 等）、法幣（USD、TWD、JPY、KRW、VND）及法幣報價站台（bot 代表台灣銀行、yahoo）。對 AI 開發而言，提供了一個標準的貨幣與站台代碼表，確保跨服務的引用一致，特別是在價格獲取、轉換與顯示功能上。

**關鍵業務規則**：
- 虛擬幣支援 USDT（泰達幣）、USDC（Circle美元穩定幣）、BUSD（幣安美元穩定幣）、HUSD（火幣美元穩定幣）、TUSD（TrustToken美元穩定幣）
- 虛擬幣站台支援 huobi（火幣網）、binance（幣安）、coinbasepro（比特幣基地）、maicoinmax（MaiCoin Max）、pionex（派網）、yahoo（Yahoo）、coinmarketcap（CoinMarketCap）
- 法幣支援 USD（美元）、TWD（台幣）、JPY（日圓）、KRW（韓元）、VND（越南盾）
- 法幣站台支援 bot（台灣銀行）、yahoo（Yahoo）
- 代碼大小寫需依文件定義（如 USDT 不可寫成 usdt）以確保匹配
- 站台代碼與服務實作的對應需保持一致，如「bot」必須指向台灣銀行

**注意事項**：
- ⚠️ 文件最後更新於 2021-11-15，部分貨幣或站台可能已新增或移除，需人工確認是否仍為現行定義
- ⚠️ 法幣站台表格出現兩個空白行，可能表示過去支援的站台已被移除或待補充，應確認目前有效的站台清單
- ⚠️ 容易誤解：法幣站台的「bot」並非機器人，而是代表台灣銀行的站台代碼，容易與其他服務混淆

---

### TCZB-1503 [CurrencyService]-Dashboard顯示各站台幣種資料,資料有錯誤時需發警報

> Confluence 頁面 ID：32079945
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32079945)
> 摘要檔：[processed/32079945-summary.md](../../confluence/processed/32079945-summary.md)
> Confluence 最後更新：2022-02-22
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義幣種資料監控的核心規則：ForexFlowService 與 CryptoFlowService 必須每分鐘為每個站台的每種幣種發送一次 Heartbeat，CurrencyManageService 負責顯示這些 Heartbeat 資訊。透過 Dashboard 監測更新時間，若超過 3 分鐘未更新，應自動發送警報至 Telegram。這些規範明確了服務交互與異常偵測機制，對開發相關微服務的定時任務與告警邏輯具有直接指導意義。

**關鍵業務規則**：
- ForexFlowService 需為每個站台的每種外幣，每 1 分鐘發送一次 Heartbeat 更新
- CryptoFlowService 需為每個站台的每種加密貨幣，每 1 分鐘發送一次 Heartbeat 更新
- CurrencyManageService 必須能夠獲取並顯示各站台各幣種的 Heartbeat 狀態
- Dashboard 監測到某站台某幣種的上次更新時間超過 3 分鐘時，應自動觸發 Telegram 警報

**注意事項**：
- ⚠️ 文件置於「舊的Projects 1-200」路徑下，可能為歷史需求，需人工確認該規則當前是否仍有效
- ⚠️ 警報規則是從目標敘述中提取，需求表格僅列舉發送 Heartbeat 的項目，未具體描述警報實作細節

---

## 技術設計類

### TCZB-1216 [CryptoService]-Get Crypto Data API

> Confluence 頁面 ID：24087841
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-1216+%5BCryptoService%5D-Get+Crypto+Data+API)
> 摘要檔：[processed/24087841-summary.md](../../confluence/processed/24087841-summary.md)
> Confluence 最後更新：2021-11-12
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了取得虛擬貨幣兌換法定貨幣匯率的 API，包含兩個端點：取得單一幣種對指定法幣匯率，以及該幣種對所有支援法幣匯率。核心設計為穩定幣兌換一律先轉美金，再依情境轉為其他法幣，並詳列四種計算情境的公式與參數意義。對 AI 開發而言，可直接參照此份文件實作呼叫與解析加密貨幣匯率資料，理解各欄位（如 Bid、Ask、FXRate 中的 Crypto/Stable/UsdBid 等）的計算來源與預設值。

**關鍵設計決策**：
- 強制所有穩定幣兌換先經過美元中轉，確保匯率計算一致性並降低複雜度
- 區分四種計算情境，以處理不同外匯站台基底（USD 或非 USD）及與目標法幣相同與否的組合
- 銀行站台基底設定：yahoo 提供 USD 匯率，bot（台灣銀行）提供 TWD 匯率，作為基礎數據來源
- API 採用路徑參數與 query string 組合，提供預設值以簡化呼叫，同時保留自訂站台的彈性

**影響範圍**：
- 穩定幣兌換法定貨幣一律先轉美金再轉其他法定貨幣，不得直接兌換
- 四種計算情境的買賣價皆取四捨五入後小數第四位
- 法定貨幣與虛擬幣名稱皆須參照 Currency Name Define 文件定義
- 預設參數：stableName=USDT, cryptoSite=huobi, stableSite=yahoo, forexSite=bot

---

### CurrencyService API

> Confluence 頁面 ID：24088874
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/CurrencyService+API)
> 摘要檔：[processed/24088874-summary.md](../../confluence/processed/24088874-summary.md)
> Confluence 最後更新：2021-11-22
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義了 CurrencyService 的三個 REST API 端點：取得特定虛擬幣兌換法定貨幣資料（支援指定多個外部數據來源）、取得該虛擬幣對所有支援法定貨幣的報價清單、自動創建資料表（用途不明）。請求參數可動態指定 crypto/stable/forex 站台來源，並提供預設值如 USDT、huobi、yahoo。回應 Quotation Model 包含買賣價、各層匯率（穩定幣轉美金、法幣兌美金等），部分數值為 -1 表示無可用報價。對 AI 開發而言，可直接調用此服務取得標準化虛擬幣匯率，需注意處理 -1 值及多站台切換邏輯。

**關鍵設計決策**：
- 採用路徑參數指定 cryptoName 與 fiatMoneyName，查詢參數支援動態切換數據來源（cryptoSite、stableSite、forexSite）以實現多源報價彈性
- 提供預設值 (stableName=USDT, cryptoSite=huobi, stableSite=yahoo, forexSite=bot) 以簡化常用呼叫
- 設計兩個端點分別處理單一法幣及全部法幣查詢，滿足不同場景（如即時報價與列表展示）
- 報價模型中以 -1 標記不可用的匯率（如 FiatMoneyBid/FiatMoneyAsk），使調用方需判斷並處理缺失數據
- 自動創建 Table 端點以 GET 方法實作，推測為維運用途，但缺少詳細說明

**影響範圍**：
- 回應值 -1 代表無可用報價，不可當作有效匯率使用
- 端點路徑及參數名稱可能因版本演進而異動，需與當前實作比對

---

### TCZB-2225 [CurrencyService] - 法幣兌換API和SMBC Crawler Heartbet

> Confluence 頁面 ID：40503961
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40503961)
> 摘要檔：[processed/40503961-summary.md](../../confluence/processed/40503961-summary.md)
> Confluence 最後更新：2022-11-03
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件記錄了為支援 SMBC 銀行日圓兌美元匯率查詢，在 currencyservice 新增一個 GET /forex 端點，接收銀行名稱與目標法幣，回傳買賣價。同時說明使用現有 currencymanageservice 的 POST /machines 心跳端點，並以 program=smbcfagentstatus 監控 SMBC 爬蟲狀態。對於後續開發，可直接參考此 API 規格實作匯率查詢與爬蟲健康檢查。

**關鍵設計決策**：
- SMBC 匯率查詢獨立為 GET /currencyservice/api/forex/{forexSite}/{fiatMoneyName}，回傳固定 JSON 結構（ForexSite, ForexFiat, TransFiat, Bid, Ask）
- SMBC 爬蟲心跳沿用現有 currencymanageservice 的 POST /currencymanageservice/api/machines/{machinename}/{program}，並以 program=smbcfagentstatus 區別
- 匯率回應中的 ForexFiat 為銀行基底幣別（JPY），TransFiat 為欲兌換的目標幣別（如 USD）

**影響範圍**：
- 此端點專為 SMBC 銀行設計，與虛擬幣查詢端點邏輯不同，不可混用

---

## 注意事項（跨文件彙總）

- ⚠️ 本服務多份文件的最後更新時間皆在 2021-2022 年，部分貨幣站台（如 huobi、yahoo、binance）可能已異動或停用，**需人工確認當前適用的貨幣與站台清單**
- ⚠️ `Currency Name Define` 為所有貨幣與站台代碼的基礎定義，任何跨服務引用都必須以此為準，不可自定義名稱
- ⚠️ TCZB-1216 與 CurrencyService API 兩份文件均涉及虛擬幣匯率查詢 API，前者著重計算公式，後者著重端點定義，合併閱讀可完整理解實作邏輯，**若發現不一致處需人工確認**
- ⚠️ TCZB-1503 定義的心跳機制與 TCZB-2225 中的 SMBC 心跳端點為不同用途，前者為一般監控，後者為特定銀行爬蟲監控，不可混用
- ⚠️ 法幣站台代碼「bot」指台灣銀行，非機器人，極易與一般聊天機器人混淆