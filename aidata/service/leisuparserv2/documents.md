# leisuparserv2 — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效  
> 最後更新：2026-05-27 14:00  
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

本類別尚無相關文件。

---

## 技術設計類

### TCZB-3526 [Crawler] - Leisu providerV2

> Confluence 頁面 ID：55581663  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3526+%5BCrawler%5D+-+Leisu+providerV2)  
> 摘要檔：[processed/55581663-summary.md](../../confluence/processed/55581663-summary.md)  
> Confluence 最後更新：2024-11-13 14:23  
> 摘要最後同步：2026-05-27 10:52  

**摘要**  
本文說明透過雷速 (Leisu) API V2 獲取籃球比賽資料的方式。主要調用 `match/list`（增量）與 `match/diary`（全量）兩個端點，並透過 FetchGame 組合場地、聯賽、球隊資訊，維護 inplay cache 以加速即時統計輸出。對開發 leisuparserv2 提供了明確的資料整合流程與呼叫頻率規範。

**關鍵業務規則**  
- `match/list` API 僅查詢前 30 天比賽資料，首次全量使用 `id` 參數，後續增量使用 `time` 參數，建議 1 分鐘查詢一次。  
- `match/diary` API 僅查詢前後 30 天賽程賽果，當天賽程建議 10 分鐘全量更新，未來賽程建議 30 分鐘全量更新。  
- 所有 API 請求 payload 必須包含 `user='dgc'` 與 `secret='d936105a4e78666150'`。  
- FetchGame 必須先呼叫 info API 取得 LocationInfo、LeagueInfo、TeamInfo 再組合比賽資料，並將進行中比賽加入 inplay cache。  
- GetInplayInfo 從即時統計 API 取得資料後，必須從 inplay cache 取出已組合的比賽資料一併送出。  

**關鍵設計決策**  
- 採用兩個 API 分離增量更新（`match/list`）與定時全量（`match/diary`），平衡即時性與負載。  
- 集中由 FetchGame 負責比賽資訊組合與 inplay cache 建立，避免重複調用 info API 並加速回應。  
- inplay cache 機制使即時統計資料能直接搭配已組合的比賽資料，減少延遲。  

**注意事項**  
- ⚠️ 文件中提供了 API key（user/secret）及數據服務登入帳密，生產環境需確保使用正式授權的憑證，避免資安風險。  
- ⚠️ 官方文檔連結為 `nami.com/docs?id=1001`，但 API 主機為 `open.sportnanoapi.com`，可能已變更，需人工確認當前正確文檔。  

---

### TCZB-3527 [Crawler] - Leisu parser V2

> Confluence 頁面 ID：55581666  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3527+%5BCrawler%5D+-+Leisu+parser+V2)  
> 摘要檔：[processed/55581666-summary.md](../../confluence/processed/55581666-summary.md)  
> Confluence 最後更新：2024-11-12 15:17  
> 摘要最後同步：2026-05-27 10:52  

**摘要**  
本文件定義 Leisu V2 parser 從 `leisu.com` 原始 JSON 提取比賽數據的規則，涵蓋基本資訊、分數（區分足球 SC 與籃球 BK）、賽中 play-by-play 與賽果統計，並因應球種不同設計不同的解析路徑與轉換邏輯。對 AI 開發人員可直接參考此文件實作或驗證 parser 的欄位對應與資料轉換。

**關鍵業務規則**  
- 比賽狀態 `game_status` 需根據 `status_id` 搭配設定檔判斷為賽前、賽中或賽果。  
- `game_date` 與 `game_time` 由 `match_time` 時間戳轉換，需拆分為日期與時間。  
- SC 總分取自 `home_scores[0]` 與 `away_scores[0]`；BK 總分為 `home_scores` 陣列加總與 `away_scores` 陣列加總。  
- SC 各節分數 `scores` 由 `home_scores` 與 `away_scores` 直接組合為配對陣列；BK 亦然，但 `home_scores` 與 `away_scores` 本身為多節分數陣列。  
- 賽中時間顯示：SC 以當前半節的開始時間戳計算進行時間；BK 以剩餘秒數轉為分鐘與秒，並依 `section_code` 對應節次（Q1~Q4）。  
- 賽果紅黃牌與角球（SC）從 `Home_scores/Away_scores` 的固定索引（2,3,4）取得 `[主,客]` 陣列。  
- 賽果技術統計（BK）從 `Stats` 陣列依 `stats_info[0]` 值 (1,2,3) 區分三分、二分、罰球，取得對應 `[主,客]` 陣列。  
- 天氣 `weather` 為數字代碼，需由設定檔轉換為天氣狀態文字。  
- 直播、視訊直播等覆蓋資訊依 `data['Coverage']` 中的 `MliveUrl`、`Mlive`、`Vlive`、`VliveUrl` 取得。  

**關鍵設計決策**  
- 針對 SC 與 BK 採用不同的解析分支，因為原始數據結構在得分、時間表示上差異顯著。  
- 將狀態碼、天氣碼等透過外部設定檔對應，而非在程式內硬編碼，提高可維護性。  
- 賽中數據與賽果數據使用不同來源 (InplayInfo vs `Home_scores/Away_scores` 或 `Stats`)，以適應不同比賽階段的數據可用性。  

**注意事項**  
- ⚠️ 文件中多處以截圖示意資料結構，若圖片不可用則部分欄位路徑需實測確認。  
- ⚠️ `game_status` 與 `weather` code 的具體對照表未提供，需查閱對應設定檔。  
- ⚠️ SC 的 `home_scores` 結構（總分/各節分數排列方式）未完全明確，文字與圖片可能存在歧義，需人工確認原始數據。  
- ⚠️ SC 賽中時間以「現在時間減去開始時間戳」計算，可能受時區或網路延遲影響，需評估準確性。  

---

### TCZB-3787 [leisuAnalysis] leisu 賽事情報爬取

> Confluence 頁面 ID：76547295  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76547295)  
> 摘要檔：[processed/76547295-summary.md](../../confluence/processed/76547295-summary.md)  
> Confluence 最後更新：2025-06-16 13:52  
> 摘要最後同步：2026-05-27 03:46  

**摘要**  
這份文件定義了 Leisu 賽事情報的爬取流程與資料輸出規格。爬蟲每約 1 小時從 Leisu 的足球與籃球情報列表頁，透過正則表達式提取包含「swot」的詳情頁連結，再用 BeautifulSoup 解析主客隊的有利/不利情報及中立情報，整理成特定文字格式後，以 SFTP 上傳到內部伺服器的 info 資料夾。對 AI 開發而言，這是爬蟲實作的完整技術規格，包含資料來源、解析邏輯與最後的輸出格式。

**關鍵業務規則**  
（本文件未列出具體業務規則，以下為設計決策與操作要求）  

**關鍵設計決策**  
- 使用正則 `findall` 匹配所有含有「swot」的網址，以過濾出情報詳情頁，而非透過 DOM 解析列表。  
- 採用 BeautifulSoup 解析情報詳情頁 HTML，並只提取主客隊有利/不利情報及中立情報，忽略其他內容。  
- 輸出格式固定為「## 主隊 ### 有利情報 - (情報1) ...」，即使某個區塊無情報仍保留標題但不列出項目。  
- 最終透過 SFTP 將文字檔寫入固定 IP 192.168.55.20 的 info 目錄，而非透過 API 或其他傳輸方式。  

**注意事項**  
- ⚠️ 情報列表頁不會列出中立情報，必須進入詳情頁才能擷取，需確保爬蟲流程涵蓋此邏輯。  
- ⚠️ 中立情報為可選出現，輸出格式仍需保留「中立情報」標題，即使內容為空。  

---

## 歷史決策類

本類別尚無相關文件。

---

## 操作手冊類

本類別尚無相關文件。