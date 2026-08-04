# CurrencyManageService — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-28 00:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### Cryptocurrency Parameter

> Confluence 頁面 ID：24088221
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Cryptocurrency+Parameter)
> 摘要檔：[processed/24088221-summary.md](../../confluence/processed/24088221-summary.md)
> Confluence 最後更新：2023-12-18 08:59
> 摘要最後同步：2026-05-26 11:59
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件為 FX 系統匯率 API 的參數對照表，說明呼叫匯率 API 時如何指定資訊源站台和幣別。對於 AI 開發，這份文件提供了呼叫匯率相關 API 時所需的正確參數枚舉值，特別是預設值的設定。

**關鍵業務規則**：
- 呼叫 FX 匯率 API 時，虛擬幣站台參數 cryptoSite 預設值為 huobi（火幣網）
- 呼叫 FX 匯率 API 時，穩定幣轉美金站台參數 stableSite 預設值為 yahoo
- 呼叫 FX 匯率 API 時，穩定幣名稱參數 stableName 預設值為 USDT
- 外匯站台 forexSite 的法定貨幣基底依站台而異：yahoo 和 Investing 以 USD 為基底，bot 以 TWD 為基底，smbc 以 JPY 為基底

**注意事項**：
- ⚠️ BUSD（幣安美元穩定幣）已標注刪除線，表示此幣別已不再支援，AI 開發時應排除此參數值
- ⚠️ 文件最後更新於 2023-12-18，需人工確認目前支援的站台和幣別是否有增減

---

### TCZB-1214 [CryptoManageService]-Get Page

> Confluence 頁面 ID：24087571
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-1214+%5BCryptoManageService%5D-Get+Page)
> 摘要檔：[processed/24087571-summary.md](../../confluence/processed/24087571-summary.md)
> Confluence 最後更新：2021-11-08 16:51
> 摘要最後同步：2026-05-27 06:58
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義 CurrencyManageService 中針對火幣網與幣安網的爬蟲頁面取得策略，提供 GET /api/{site}/page/{type}/{provider} 隨機回傳待爬頁面、工作心跳（PATCH）與停止工作（PATCH）三個 API。對 AI 開發而言，此文件闡明了與爬蟲分配子系統的互動介面與逾時機制。

**關鍵業務規則**：
- 工作心跳超過 2 分鐘沒更新則會清除 handler（文件問答確認不會太快）
- 取得 page 時由亂數篩選回傳（隨機分配頁面）

**注意事項**：
- ⚠️ 文件最後更新於 2021-11-08，屬於 Sprint 35 期間的設計，可能已不完全反映當前實作，路徑或超時參數須人工確認
- ⚠️ Confluence 路徑包含「舊的Projects 1-200」，表示此需求來自早期 sprint，部分決策可能已被後續需求取代

---

### TCZB-1523 [CurrencyAgent]-Agent需定時關閉程式

> Confluence 頁面 ID：32079905
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32079905)
> 摘要檔：[processed/32079905-summary.md](../../confluence/processed/32079905-summary.md)
> Confluence 最後更新：2022-02-21 16:51
> 摘要最後同步：2026-05-27 07:30
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件記錄一項需求：要求虛擬貨幣 Agent 必須具備定時關閉程式的功能。對 AI 開發來說，需注意 CurrencyAgent 應加入排程關閉機制，但詳細規則需人工進一步確認。

**關鍵業務規則**：
- 虛擬貨幣 Agent 需具備定時關閉程式的能力。

**注意事項**：
- ⚠️ 文件內容極度簡化，未定義關閉的時間間隔、觸發條件、是否需要優雅關閉等，開發前需釐清實際需求
- ⚠️ 此需求可能已過時或與現行架構不符，需人工確認在當前服務中是否仍適用

---

## 技術設計類

### CurrencyManageService API

> Confluence 頁面 ID：24087341
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/CurrencyManageService+API)
> 摘要檔：[processed/24087341-summary.md](../../confluence/processed/24087341-summary.md)
> Confluence 最後更新：2021-11-22 09:49
> 摘要最後同步：2026-05-26 13:31
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了 CurrencyManageService 的 REST API 端點，包括取得頁面 (GET)、工作心跳 (PATCH)、停止工作 (PATCH) 以及自動建立資料表 (POST)。對於 AI 開發此服務，可以理解如何與該服務通訊以管理爬蟲任務或獲取頁面配置。

**關鍵業務規則**：
- site 參數必須是文件列表中的站台代碼之一：houbi, binance, bot, yahoo, maicoinmax, coinbasepro, pionex, investing
- 取得 page 時，需提供有效的 site 與 provider，返回值為 PageMsg 模型（含 PageName 和 Url）
- 工作心跳和停止工作要求提供 site、provider、pagename，否則請求無效

**注意事項**：
- ⚠️ 文件最後更新於 2021-11-22，可能已過期，API 路由或行為可能已變更
- ⚠️ 表格格式有誤（建立資料表 route 欄位出現多餘的 '|'），需人工確認正確路由

---

### CurrencyManageService DB Tables

> Confluence 頁面 ID：24088088
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/CurrencyManageService+DB+Tables)
> 摘要檔：[processed/24088088-summary.md](../../confluence/processed/24088088-summary.md)
> Confluence 最後更新：2021-11-22 09:51
> 摘要最後同步：2026-05-26 13:32
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
描述 CurrencyManageService 使用的 currency 資料庫結構，包含 {SiteName}pages（多站台頁面配置：啟用狀態、URL、最大工作數、工作機器心跳）與 machines（機器清單、心跳、controller 狀態，並依站台動態增加狀態欄位）。對 AI 開發此服務可了解其底層資料模型。

**關鍵設計決策**：
- 採用 {SiteName}pages 表集中管理不同站台的頁面設定，以 pagename 為主鍵
- handler 欄位使用 map<text,text> 類型儲存機器名稱與心跳時間的對應，用於記錄當前正在處理該頁面工作的機器實例
- machines 表透過動態增加 {siteName}status 欄位來適應未來新增站台，避免頻繁修改 schema

**注意事項**：
- ⚠️ 文件最後更新於 2021-11-22，可能已過時，實際資料庫結構或有變更，需人工確認
- ⚠️ 範例中 handler 心跳時間格式需確認是否仍為字串型態，以及是否與系統其他部分一致

---

### CurrencyManageService 時序圖

> Confluence 頁面 ID：24087339
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24087339)
> 摘要檔：[processed/24087339-summary.md](../../confluence/processed/24087339-summary.md)
> Confluence 最後更新：2021-11-22 09:52
> 摘要最後同步：2026-05-26 13:34
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件以時序圖描述 CurrencyManageService 的五個核心 API 操作流程。對 AI 開發的幫助在於：它明確定義了此服務與 CrawlerAgent、CrawlerService、Controller 等外部調用者的互動契約，包含請求與回應的資料流。特別說明了 Get page API 具有亂數篩選、分配 handler 及淘汰過期 page 的內部邏輯。

**關鍵業務規則**：
- Get page 請求：從 DB 取得所有 pages 後，服務內部需先「取出需要工作的 page」，再進行「亂數篩選」決定最終回傳的 page
- Get page 請求：亂數篩選出 page 後，需更新 DB 中的 page handler（指派或鎖定該 page 給請求者），並清理「太久沒工作」的 page handler
- SendStop 請求：收到停止工作請求時，服務需從 DB 移除對應的 handler（釋放任務鎖定）
- 更新機器狀態請求：由 Controller 調用，服務需 Mapping 機器名稱、確認現在時間後，更新 DB 中的 status 時間
- 更新 CrawlerService 狀態請求：由 CrawlerService 調用，服務必須先「驗證 status 參數」才能更新 CrawlerService 狀態到 DB

**關鍵設計決策**：
- 任務分配策略（Get page）：採用亂數篩選而非順序分配，可能是為了避免多個 CrawlerAgent 同時搶佔同一批 page，或為了實現負載分散
- 過期清理機制（Get page）：在同一次請求中混合了「分配新任務」和「清理過期任務」兩個動作，這是一種原子化的維護策略
- 心跳分離：Heartbeat 和更新 CrawlerService 狀態是兩個獨立的 API，顯示代理層與服務層的狀態管理是分離的

**注意事項**：
- ⚠️ 此文件最後更新於 2021-11-22，已超過兩年未更新，需人工確認目前 Get page 的篩選與分配邏輯是否仍為亂數機制
- ⚠️ 時序圖中出現兩個名為「1.Get page」的章節（內容重複），可能為文件編輯錯誤，需人工確認原始 Confluence 頁面狀態
- ⚠️ 時序圖文字描述中，CryptoManageService 與標題 CurrencyManageService 名稱不一致，可能暗示此服務的前身或別名，需人工確認對應關係

---

## 歷史決策類

### TCZB-1523 [CurrencyAgent]-Agent需定時關閉程式

> Confluence 頁面 ID：32079905
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32079905)
> 摘要檔：[processed/32079905-summary.md](../../confluence/processed/32079905-summary.md)
> Confluence 最後更新：2022-02-21 16:51
> 摘要最後同步：2026-05-27 07:30
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**決策背景**：
Sprint 48 期間提出需求，要求虛擬貨幣 Agent 必須具備定時關閉程式的功能。文件未提供具體關閉週期、觸發條件或實現細節。

**決策結論**：
已決定加入定時關閉功能，但詳細規則（關閉時間間隔、觸發條件、優雅關閉機制）未在文件中記錄。

**影響**：
此決策影響 CurrencyAgent 的生命週期管理，若仍有此需求，需在程式中加入排程關閉機制。但由於文件資訊極度簡化，需人工確認當前是否仍適用。