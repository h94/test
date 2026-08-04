crawlerflowservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 10:56
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### 各站台Team 1,2位置說明

> Confluence 頁面 ID：11437219
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=11437219)
> 摘要檔：[processed/11437219-summary.md](../../confluence/processed/11437219-summary.md)
> Confluence 最後更新：2021-06-02
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了將不同外部資料源(如bet365, betfair)的隊伍與盤口資訊正規化為統一內部標準的規則。關鍵決策是將上下或左右顯示的兩隊分別定義為Team1與Team2，並明確規定Handicap(讓分)盤口的Spread一律代表Team1的讓分值，Over/Under(大小)盤口的Spread一律代表Over的分數。這些規則是為了確保AI開發時，能正確解析和轉換來自不同格式的原始賠率數據，避免主客隊或大小分數據錯置。

**關鍵業務規則**：
- 資料源畫面採上下排列時，上方隊伍定義為Team1，下方為Team2。
- 資料源畫面採左右排列時，左方隊伍定義為Team1，右方為Team2。
- 所有Handicap(讓分)盤的Spread值，一律代表Team1的讓分(Handicap)。
- 所有Over/Under(大小)盤的Spread值，一律代表Over(大)的分數。
- Handicap的Spread輸出格式應轉換為台灣顯示格式，且當Team1為強隊(讓隊)時數值為正(例如: 1+50)，Team1為弱隊(被讓隊)時數值為負(例如: -1-50)。
- Over/Under的Spread輸出格式應轉換為台灣顯示格式，且數值均為正數(例如: 143.5)。

**注意事項**：
- ⚠️ 過期資訊：文件最後更新於2021年6月，表格中引用了一些當時的資料源站台，部分可能已合作終止或新增其他站台，需人工確認當前適用的資料源清單。
- ⚠️ 容易誤解：Handicap格式中的'+'和'-'在台灣格式中有特定涵義(如1+50代表讓1.5球)，開發時需嚴格遵守文件中舉例的格式進行轉換，不可直接進行數學上的正負號運算。

---

## 技術設計類

### TCZB-3975 [AI預測] - 籃球AI預測

> Confluence 頁面 ID：79465313
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465313)
> 摘要檔：[processed/79465313-summary.md](../../confluence/processed/79465313-summary.md)
> Confluence 最後更新：2026-01-21
> 摘要最後同步：2026-05-27

**摘要**：
本文件記錄了在AI預測爬蟲中新增對籃球（NBA、歐洲籃球聯賽、日本B1、韓國KBL、中國CBA等）及多個冰球聯賽的數據來源擴充。主要涉及從 Forebet、Sportspunter、Scores24 三個站點補抓，並提供各聯盟對應的站點 ID（sitelid）與資料發送格式。特別說明了 Sportspunter 單場預測連結因站點改版需修改路由，以及 Scores24 因需 VPN 被獨立為 Scores24Provider 部署。對 AI 開發者而言，可快速掌握新爬取聯盟與站點的對應關係，以及資料結構與儲存規則。

**關鍵設計決策**：
- 因 Scores24 阻擋非 VPN 請求，將其爬取邏輯獨立為 Scores24Provider，並部署至 VM11、VM31、VM91
- 資料格式沿用先前 Sprint 的 Match 結構，不同站點僅 OtherInfo 內容有差異

**影響範圍**：
- ⚠️ 文件中「Sportspunter 單場點擊預測連結消失」為站點改版所致，需確認當前版本是否仍有此路由
- ⚠️ game_status 的狀態碼定義未完整列出，僅示例中出現 '2'，需參照先前 Sprint 文件或程式碼確認

---

## 歷史決策類

### Binance 畫面

> Confluence 頁面 ID：24087712
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24087712)
> 摘要檔：[processed/24087712-summary.md](../../confluence/processed/24087712-summary.md)
> Confluence 最後更新：2024-06-04
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**決策背景**：
文件記錄了 Binance 交易頁面上幣種選項（白色框）和成交價資訊（紅色框）的 HTML 區域變化。2024/05/21 有前端變動，2024/06/04 則 class 屬性從 css-160yc13 改為 css-uzzewv，但區塊結構不變。對 AI 開發而言，這提醒爬蟲或自動化代理需持續追蹤 Binance 前端 class 名稱變更，以維持正確的資料提取邏輯。

**決策結論**：
2024/05/21 發生前端變動，需調整解析邏輯；2024/06/04 僅變更 class 屬性但區塊結構相同，表示結構穩定但樣式名稱會改動，應採用更靈活的解析策略或定期更新 class 對照表。

**影響**：
- ⚠️ 文件僅包含文字描述與截圖連結，實際截圖未能查閱，需人工確認畫面細節
- ⚠️ 最後更新為 2024/06/04，後續可能有新的 class 變動，需確認目前線上版本是否仍適用

---

## 操作手冊類

### TCZB-3999 [7M] - 足籃走地即時資訊

> Confluence 頁面 ID：79465543
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465543)
> 摘要檔：[processed/79465543-summary.md](../../confluence/processed/79465543-summary.md)
> Confluence 最後更新：2025-10-21
> 摘要最後同步：2026-05-27

**摘要**：
此文件定義了從 7M 網站爬取足球和籃球即時比賽數據的技術規格。足球需在比賽開始後第15、30、45、60、75、90分鐘時抓取並寫檔；籃球則在每節結束前及比賽剩餘第5、6分鐘時觸發寫檔。提供了對應的 API 端點和參數格式，並指定籃球僅需提取主客隊統計數據（h_stat_t、a_stat_t）。內容有助於實現定時爬蟲流程與資料儲存邏輯。

**AI 開發需要注意的部分**：
- ⚠️ 足球的數據分析欄位「不是每場比賽都有 多數都沒有」，需在程式中有對應的缺失處理邏輯。
- ⚠️ 籃球寫檔時間點「每一節結束前」和「剩餘第5、6分時」具體時間定義模糊（例如Q1 00:38 僅為範例），需與需求方確認確切的觸發條件。
- ⚠️ 足球比賽開始後的時間點是否包含傷停補時或僅為常規時間，文件未說明。
- ⚠️ 足球 game_id 前四碼作為路徑，但 game_id 長度和規則需在實作時驗證。