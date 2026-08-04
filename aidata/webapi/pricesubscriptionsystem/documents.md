# pricesubscriptionsystem — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 07:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### 訂閱機制測試

> Confluence 頁面 ID：44663729  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44663729)  
> 摘要檔：[processed/44663729-summary.md](../../confluence/processed/44663729-summary.md)  
> Confluence 最後更新：2023-02-23  
> 摘要最後同步：2026-05-26  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：  
文件記錄了會員訂閱機制的功能測試，包含一般會員首次訂閱、高級會員續訂、高級升級 VIP 等場景，驗證了層級變更、到期日計算與差額付費方案的預期行為。測試結果可作為開發或自動化驗證的預期規則參考。

**關鍵業務規則**：
- 無現有訂閱的會員（一般會員）訂閱高級/VIP 方案時，層級立即變更為訂閱方案對應的層級，到期日為訂閱日期加 1 個月（例：2022-12-23 訂閱，到期日 2023-01-23）。
- 已有高級資格的會員續訂高級方案，到期日從原有最近到期日延長 1 個月（例：原到期日 2023-01-23，續訂後變為 2023-02-23）。
- 高級會員升級 VIP 時，若剩餘有效期 ≤ 5 天，適用「5 日以下差額方案」計費，升級後層級變為 VIP，到期日為訂閱日期加 1 個月（例：2023-02-23 訂閱，到期日 2023-03-23）。需人工確認差額方案的具體計算方式。
- VIP 訂閱高級會員方案（降級）的行為未在測試中給出預期結果，需人工確認該情境的規則。

**注意事項**：
- ⚠️ 文件最後一行（VIP 訂閱高級）完全空白，可能尚未定義或未測試，需人工確認。
- ⚠️ 所有預期結果與實際結果均附帶圖片，但圖片內容無法提取，可能遺漏精確欄位或 UI 細節。
- ⚠️ 文件最後更新於 2023-02-23，距今已有一段時間，需確認相關規則是否仍適用。

---

### 2025-08-22 會議記錄

> Confluence 頁面 ID：79464189  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464189)  
> 摘要檔：[processed/79464189-summary.md](../../confluence/processed/79464189-summary.md)  
> Confluence 最後更新：2025-08-26  
> 摘要最後同步：2026-05-26  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：  
會議討論了訂閱系統中及時賠率查閱限制、商務帳號層級與數量規範，以及球種玩法基礎版與加值版的分層需求。多項決策直接影響權限控制與商務設定，有助於開發時明確設計邊界。

**關鍵業務規則**：
- 及時賠率僅供訂閱者查詢自己賽事的賠率；其他資訊源賠率須透過賽事賠率資訊新功能查看。
- 商務帳號分層級：admin 帳號由系統方開通，trader 帳號由該訂閱戶 admin 開通；每個訂閱戶 admin 最多 1 個，trader 最多 3 個。
- 新增商務帳號時，需同時新增 admin 帳號。
- LS、BC 資訊源不排除。
- 球種玩法需提供基礎版與加值版，商務設定時應增加對應設定。

**注意事項**：
- ⚠️ 基礎版與加值版玩法的具體內容尚未定義，需後續確認。
- 第一階段開發結束後才進行測試與 DEMO，具體時程未定。

---

### 2025-09-19 會議記錄

> Confluence 頁面 ID：79465022  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465022)  
> 摘要檔：[processed/79465022-summary.md](../../confluence/processed/79465022-summary.md)  
> Confluence 最後更新：2025-09-22  
> 摘要最後同步：2026-05-26  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：  
會議討論訂閱機制變更：資訊源也須訂閱且賽前/走地分開；訂閱站台即支援所有玩法；新增可透過商務號聯盟訂閱全部賽事走地；額外玩法訂閱暫停；產品名稱暫用INPLAYZ。對開發的影響：需調整訂閱模型，實作分開訂閱、全玩法自動支援及聯盟訂閱功能。

**關鍵業務規則**：
- 資訊源必須一併訂閱，且賽前和走地需分別訂閱。
- 只要訂閱某站台，就自動支援該站台所有玩法，無需單獨訂閱玩法。
- 提供透過商務號聯盟直接訂閱其下所有賽事走地的功能。
- 額外玩法訂閱功能暫時停用。

**注意事項**：
- ⚠️ 此為會議記錄，非最終決策，需確認是否已轉為正式規格文件。
- ⚠️ 產品名稱暫用 INPLAYZ，最終名稱待上層決定。

---

### 整合系統收費標準

> Confluence 頁面 ID：24091193  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24091193)  
> 摘要檔：[processed/24091193-summary.md](../../confluence/processed/24091193-summary.md)  
> Confluence 最後更新：2022-01-11  
> 摘要最後同步：2026-05-26  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：  
本文件定義整合系統的收費模型：基礎整合系統月費為 4,000 USD，選配國際盤口需額外加價，並列出各盤口的體育覆蓋範圍與單價，同時標明 Bet365、1xBet、KU Casino、NK 為標配無需外加費用。AI 開發時可據此建立訂閱計費與盤口組合規則。

**關鍵業務規則**：
- 整合資訊源總費用 = ZB整合系統月費（4,000 USD）＋ 所有選配國際盤口的月費總和，範例：ZB+PS3838+HGA＝4,000+800+800=5,600 USD/月。
- Bet365、1xBet、KU Casino、NK（36588 系統）為標準配備，訂閱整合系統時自動包含，不另行收費。
- 每個選配盤口有各自的體育項目支援表（例如 PS3838 不支援足球，HGA 僅支援足球），訂閱時應根據表單限制可用體育項目。
- 各選配盤口月費：PS3838 800 USD、Marathonbet 500 USD、SportPesa 800 USD、Fun88(UK) 800 USD、Betfair 500 USD、BWin 500 USD、HGA 800 USD、188Bet 800 USD、ASC 500 USD、利記(SBO) 500 USD、KKK 500 USD。
- 全套國際盤口方案無標準定價，需另洽客服，系統應支援人工報價或引導聯絡客服。
- 價格可能未包含所有情境，文件中免責聲明表示本公司可隨時更改資料，實際收費以業務最新公告為準。

**注意事項**：
- ⚠️ 最後更新日期為 2022-01-11，所列價格與產品組合可能已過時，需人工確認現行收費標準。
- ⚠️ 免責聲明載明「隨時更改資料，並不作另行通知」，此文件不宜直接作為系統自動計費的硬編碼來源。
- ⚠️ 表格中部分盤口的體育支援有例外（如 PS3838 足球未勾選），需在訂閱邏輯中精確對應，避免誤開放賽種。

---

### TCZB-752[PriceSubscriptionSystem] - 新增KU其他玩法

> Confluence 頁面 ID：24086357  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24086357)  
> 摘要檔：[processed/24086357-summary.md](../../confluence/processed/24086357-summary.md)  
> Confluence 最後更新：2021-09-22  
> 摘要最後同步：2026-05-27  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：  
本文件定義了在 KU 數據源中新增 7 種球種（網球、冰球、排球、乒乓、橄欖球、撞球、電競）的賠率資訊支援。實作上需修改 PriceCenterService 與 PriceSubscriptionSystem 的 appsettings 配置，並在 SignalR Tools 增加對應玩法選項。開發時需參考另一份 data define 頁面取得球種參數對照，以確保解析與傳遞正確。

**關鍵業務規則**：
- KU 數據源須支援以下額外球種：網球(TN)、冰球(HL)、排球(VB)、乒乓(桌球,TB)、橄欖球(FL)、撞球(SN)、電競(ES)。
- 球種參數對照需查閱 Confluence 上的「data define」頁面（/display/TCZB/data+define）。
- PriceCenterService 的 appsettings 需新增對應配置項目（具體配置內容需人工確認）。
- PriceSubscriptionSystem 的 appsettings 需新增對應配置項目（具體配置內容需人工確認）。
- SignalR Tools（可能對應 pricefrontendtools）需增加這些新玩法的選項。

**注意事項**：
- ⚠️ 文件最後更新於 2021-09-22，可能已與目前系統行為不一致，實施前需人工確認。
- ⚠️ 文件中未提供具體 appsettings 配置方式，僅提及「增加配置」，需進一步查閱相關技術文件或代碼。
- ⚠️ 提到的「data define」頁面可能已變更或失效，需確認連結有效性及最新參數定義。

---

### 板球 玩法支援站台配置

> Confluence 頁面 ID：79465279  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465279)  
> 摘要檔：[processed/79465279-summary.md](../../confluence/processed/79465279-summary.md)  
> Confluence 最後更新：2025-10-29  
> 摘要最後同步：2026-05-26  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：  
本文件定義板球（Cricket）賽前與賽中兩種場景下，各玩法（HA、OU、T1 Score、T2 Score、RBHA、RBOU）所支援的資料源站台清單。對 AI 開發而言，這是一份訂閱設定的配置來源，當系統需要決定板球特定玩法的賠率資料應從哪些站台拉取時，應以此文件為準。部分玩法標注「不使用」，表示雖有定義但現行不啟用。

**關鍵業務規則**：
- 板球賽前 HA 玩法支援 16 個站台：188bet, 1xbet.com, asc.com, au8tw.com, betcity, betsapi.com, cloudbet.com, konibet.com, ladbrokes.com, m88keren.com, marathonbet.com, napoleon, panda, ps3838.com, tonybet, twsl, unibet.com。
- 板球賽前 OU 玩法支援 6 個站台（但標注不使用）：1xbet.com, asc.com, au8tw.com, betsapi.com, ladbrokes.com, ps3838.com。
- 板球賽前 T1 Score 玩法支援 1 個站台（但標注不使用）：cloudbet.com。
- 板球賽前 T2 Score 玩法支援 2 個站台（但標注不使用）：cloudbet.com, panda。
- 板球賽中 RBHA 玩法支援 15 個站台：1xbet.com, asc.com, au8tw.com, betcity, betsapi.com, cloudbet.com, konibet.com, ladbrokes.com, m88keren.com, marathonbet.com, napoleon, panda, ps3838.com, twsl, unibet.com。
- 板球賽中 RBOU 玩法支援 6 個站台（但標注不使用）：1xbet.com, asc.com, au8tw.com, betsapi.com, ladbrokes.com, ps3838.com。
- 賽前 HA 比 RBHA 多支援 188bet 和 tonybet 兩個站台；賽前 OU 與賽中 RBOU 支援站台完全相同。

**注意事項**：
- ⚠️ 文件僅列出支援站台清單，未說明各站台的優先順序或權重，需確認訂閱系統如何從多站台中選擇資料源。
- ⚠️ 文件未說明賽前 OU、T1 Score、T2 Score 及賽中 RBOU 標注「不使用」的原因，需確認是永久停用或是暫停使用。
- ⚠️ 部分站台名稱格式不一致（如有的含 .com 後綴、有的沒有），在實作站台對應時需注意標準化問題。

---

### 格鬥 玩法支援站台配置

> Confluence 頁面 ID：79465297  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465297)  
> 摘要檔：[processed/79465297-summary.md](../../confluence/processed/79465297-summary.md)  
> Confluence 最後更新：2025-10-29  
> 摘要最後同步：2026-05-26  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：  
文件定義格鬥（MMA）賽前與賽中的玩法在各個資料站台的支援狀況。賽前玩法 HA 與 OU 及賽中玩法 RBHA 與 RBOU 各有指定的站台清單，其中 OU 與 RBOU 備註為「不使用」，代表這些配置目前無效。這份配置可直接用於判斷特定玩法應從哪些站台取價或過濾。

**關鍵業務規則**：
- 賽前玩法 HA 僅支援以下站台：1xbet.com, asc.com, au8tw.com, betcity, betsapi.com, cloudbet.com, konibet.com, ladbrokes.com, lsports.com, m88keren.com, marathonbet.com, napoleon, ps3838.com, sbo.com, tonybet, twsl, unibet.com。
- 賽前玩法 OU 的站台列表（1xbet.com, asc.com, au8tw.com, bc.com, betcity, betsapi.com, cloudbet.com, konibet.com, lsports.com, ps3838.com, sbo.com, tonybet, unibet.com）備註為「不使用」，即當前環境中該玩法不採用這些站台。
- 賽中玩法 RBHA 僅支援以下站台：1xbet.com, asc.com, au8tw.com, betcity, betsapi.com, cloudbet.com, konibet.com, ladbrokes.com, lsports.com, m88keren.com, marathonbet.com, napoleon, ps3838.com, sbo.com, twsl, unibet.com。
- 賽中玩法 RBOU 的站台列表（1xbet.com, asc.com, au8tw.com, bc.com, betcity, betsapi.com, cloudbet.com, konibet.com, lsports.com, ps3838.com, sbo.com, unibet.com）備註為「不使用」，即當前環境中該玩法不採用這些站台。

**注意事項**：
- ⚠️ 賽前 OU 與賽中 RBOU 的站台清單雖有列舉，但實務上標記為「不使用」，AI 開發時應直接排除這些玩法的站台配置，避免誤用。
- ⚠️ 文件僅提供站台名稱清單，未說明「不使用」的原因，如需啟用需人工確認業務決策。

---

### 桌球 玩法支援站台配置

> Confluence 頁面 ID：79465303  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465303)  
> 摘要檔：[processed/79465303-summary.md](../../confluence/processed/79465303-summary.md)  
> Confluence 最後更新：2025-11-05  
> 摘要最後同步：2026-05-26  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：  
本文件定義桌球賽事中，賽前和賽中的各個玩法所支援的站台清單，並標記某些玩法目前不使用。這有助於 AI 開發人員在處理賠率或賽事資料時，依據站台和玩法進行過濾與路由，確保僅處理有效配置的玩法。

**關鍵業務規則**：
- 桌球賽前HA玩法支援以下站台：1xbet.com, asc.com, bc.com, betcity, betsapi.com, cloudbet.com, konibet.com, ladbrokes.com, lsports.com, m88keren.com, marathonbet.com, napoleon, panda, sbo.com, tonybet, twsl, unibet.com。
- 桌球賽前OU玩法雖定義了站台（1xbet.com, asc.com, bc.com, betcity, betsapi.com, lsports.com, sbo.com, unibet.com），但標記為「不使用」，系統應忽略此玩法。
- 桌球賽前PointHA、PointOU、2nd PointHA、2nd PointOU玩法皆標記為「不使用」，儘管有站台配置。
- 桌球賽前1st PointHA和1st PointOU玩法為啟用狀態，各自有多個站台支援（見文件清單）。
- 桌球賽中RBHA玩法支援所有列出的18個站台，為啟用狀態。
- 桌球賽中RBOU、PointRBHA、PointRBOU、2nd PointRBHA、2nd PointRBOU玩法標記為「不使用」。
- 桌球賽中1st PointRBHA和1st PointRBOU為啟用玩法，各有10-11個站台支援。

**注意事項**：
- ⚠️ 部分玩法（PointHA, PointOU, 2nd PointHA等）雖有站台清單但標記「不使用」，需確認這些玩法是否已廢棄或未來可能啟用，避免誤認為有效。
- ⚠️ 支援站台的清單位於表格中，格式為逗號分隔的字串，需在代碼中正確分割和比較。
- ⚠️ 此配置可能隨時間變化，需定期確認，目前最後更新為2025-11-05。

---

### 棒球 玩法支援站台配置

> Confluence 頁面 ID：79465276  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465276)  
> 摘要檔：[processed/79465276-summary.md](../../confluence/processed/79465276-summary.md)  
> Confluence 最後更新：2025-11-04  
> 摘要最後同步：2026-05-26  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：  
本文件定義棒球彩種在「賽前」與「賽中」兩階段，所有可投注玩法（如讓分、大小、半場、單局等）各自適用的站台清單。部分玩法標示「不使用」，代表該玩法在目前系統中已停用。此配置可直接作為訂閱過濾與數據派送的依據，確保 AI 在處理賠率訂閱時只向相關站台發送對應玩法的資料。

**關鍵業務規則**：
- 每個玩法的可用站台均以逗號分隔的站台代碼字串明確定義，系統應嚴格依此清單派送訂閱資料。
- 玩法分為「賽前」與「賽中」兩組；賽中玩法的代碼以「RB」前綴區別，如 RBHA、RBOU 等。
- 標注「不使用」的玩法（賽前 RunsHitsErrorsOU、Home Runs）應在全系統中禁用，不對任何站台產生數據或顯示。
- 站台代碼可能存在重複（如 1InnHA 的 'm88keren.com' 出現兩次），實作時應去重處理，避免重複訂閱。
- 部分玩法（如 FirstScore、LastScore、Odd/Even）僅在賽前使用，賽中無對應配置。

**注意事項**：
- ⚠️ 文件內站台代碼清單為手動維護，可能存在筆誤或重複（例如 1InnHA 的 'm88keren.com' 重複），實作時應做去重防禦。
- ⚠️ 「不使用」的標示僅在 Memo 欄位出現，建議將此類規則正規化存入資料庫，避免僅依賴文字註解。
- ⚠️ 站台代碼的格式（如是否區分大小寫、有無隱含前綴）需人工確認，此處未說明。

---

### 美式足球/橄欖球 玩法支援站台配置

> Confluence 頁面 ID：79465285  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465285)  
> 摘要檔：[processed/79465285-summary.md](../../confluence/processed/79465285-summary.md)  
> Confluence 最後更新：2025-11-04  
> 摘要最後同步：2026-05-26  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：  
本文件定義美式足球/橄欖球在賽前與賽中的所有玩法（讓分、大小、各節等）對應的第三方站台支援清單。文中以表格列出每個玩法可接收資料的站台，並特別標注哪些玩法「不使用」（雖然站台有提供資料，但系統內不採用）。對 AI 開發而言，此配置可直接作為訂閱過濾或賠率派送的規則依據，確保只向合規站台發送相應玩法數據，同時排除被標記為不使用的玩法。

**關鍵業務規則**：
- 賽前 HA、OU 玩法支援的站台為：1xbet.com, asc.com, au8tw.com, bc.com, betcity, betsapi.com, cloudbet.com, espnbet.com, kkk.net, konibet.com, ladbrokes.com, m88keren.com, marathonbet.com, napoleon, nk.net, panda, ps3838.com, sbo.com, tonybet, twsl, unibet.com，共21個站台。
- 賽前 HalfHA、HalfOU、2nd HalfHA、2nd HalfOU、T1HalfScore、T2HalfScore 雖有支援站台但標注「不使用」，系統在處理這些玩法時應忽略對應站台的數據，不進行訂閱或推送。
- 賽中 RBHA、RBOU 玩法的支援站台與賽前 HA、OU 完全相同。
- 賽中 HalfRBHA、HalfRBOU、T1HalfScoreRBOU、T2HalfScoreRBOU 標注「不使用」，處理規則與賽前同類玩法一致。
- 各節（Quarter）玩法支援站台不同，例如 1st QuarterHA/OU 包含 1xbet.com, au8tw.com, cloudbet.com, konibet.com, m88keren.com, ps3838.com, sbo.com, tonybet, unibet.com，而 2nd-4th Quarter 則逐步減少站台（如4th QuarterHA 僅支援 1xbet.com, cloudbet.com, konibet.com, tonybet, unibet.com），必須嚴格按清單執行。
- 任何未列在此配置中的站台，皆不被允許接收對應玩法的資料。

**注意事項**：
- ⚠️ 文件最後更新時間為 2025-11-04，若後續有站台增減或玩法調整，本配置可能已過期，需人工確認是否為最新版本。
- ⚠️ 文件僅列出站台名稱，未定義站台標識碼對照，實作時需將站台名稱轉為內部站台ID，映射關係需另行確認。
- ⚠️ 標注「不使用」的玩法，其支援站台仍被列出，可能是為了記錄原始資料來源，開發時不可誤將這些站台視為有效支援。

---

## 技術設計類

### PriceSubscriptionSystem的InplayAlertHandler機制

> Confluence 頁面 ID：47221224  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47221224)  
> 摘要檔：[processed/47221224-summary.md](../../confluence/processed/47221224-summary.md)  
> Confluence 最後更新：2023-05-31  
> 摘要最後同步：2026-05-26  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：  
本文說明 InplayAlertHandler 的設計與運作機制：從 Kafka 取得即時比賽資料後，比較合併站台的賠率與比分差距以檢測爬蟲資料異常（殭屍或延遲）。依球種（BK/SC/BS）定義不同閾值與邏輯，並討論誤報風險與緩解方案（如間歇性重複通知、合併資訊重取）。透過 SignalR WSS 發送 Alert 訊息並附帶 heartbeat 檢測連線。對 AI 開發而言，本文提供異常檢測規則、訊息格式與訂閱方式，有助於實現或維護告警系統。

**關鍵設計決策**：
- 對 BK 不採用比賽進行時間判斷，因為各站台比賽時間格式不統一、聯賽規則差異大，難以可靠運作。
- 對 SC 可考慮使用比賽進行時間 (>2 分鐘) 過濾，因足球比賽時間規格較一致。
- 採用間歇性重複通知 (每分鐘一次，3 次後暫停) 以避免短期內相同警告氾濫。
- 合併資訊錯誤場景下，要求 InplayAlertHandler 動態重取合併資料，而非依賴舊資料，以減少誤報持續時間。

**影響範圍**：
- InplayAlertHandler 依賴 Kafka 即時資料與合併站台資訊，不可自行變更警報邏輯而無視合併資訊。
- SignalR WSS 的 channel 為「Alert」，且每 2 分鐘須有心跳檢測。
- BK、SC、BS 三種球種的邏輯不可混淆；BS 規則仍待補充。

**注意事項**：
- ⚠️ 多項閾值參數標注「待確認」：BK RBOU 差距 >8、總分差距 >4；SC RBOU 差距 >1、總分差距 >1、比賽時間 >2分鐘；警報重發機制等均尚未定案。
- ⚠️ 文中提到多種誤判場景：站台關閉或無賠率時無法判斷、比分更新速度不一致導致誤報、比賽延遲開始造成初期誤判、合併錯誤導致不停誤報。
- ⚠️ 文件最後更新日期為 2023-05-31，部分設計與參數可能已變更，需與當前實作對照。
- ⚠️ 球種 BS 的判斷邏輯完全空白，需補充。
- ⚠️ 站台數量不足時是否需要通知，文中標注待確認。

---

### TCZB-641[PriceSubscriptionSystem]-拆分PriceCenterService 功能

> Confluence 頁面 ID：15402282  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=15402282)  
> 摘要檔：[processed/15402282-summary.md](../../confluence/processed/15402282-summary.md)  
> Confluence 最後更新：2021-04-13  
> 摘要最後同步：2026-05-27  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：  
本文規劃將 PriceCenterService 中的 Hub 相關功能獨立為新服務 PriceSubscriptionSystem。具體操作包括搬移 PriceCenterHub、PriceCenterHubService 等核心類別，將 siteGameRedisService 改由 PriceCenterService 的 API 提供，僅搬遷 siteGameDataProvider 的必要查詢函式。對 AI 開發而言，本文界定了服務拆分後的依賴邊界與接口規範，有助於理解新服務的職責和對外請求方式。

**關鍵設計決策**：
- Hub 功能從 PriceCenterService 拆分至獨立的 PriceSubscriptionSystem，以實現職責分離。
- 不屬於 Hub 但需使用的功能（siteGameRedisService）透過 PriceCenterService 的 GET /pricecenter/getredisdata API 調用，避免重複開發。
- DB 查詢僅搬遷 GetSiteGamesBySite 和 GetSiteSingleGameBySiteGID 兩個函式，以最小化耦合。

**影響範圍**：
- PriceSubscriptionSystem 對 PriceCenterService 有 API 依賴（/pricecenter/getredisdata），此介面不可隨意廢棄。
- DB 存取路徑受限於搬遷的兩個函式，新增 DB 查詢需求時需注意服務邊界。

---

## 歷史決策類

無相關文件。

---

## 操作手冊類

### 訂閱服務

> Confluence 頁面 ID：34767566  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=34767566)  
> 摘要檔：[processed/34767566-summary.md](../../confluence/processed/34767566-summary.md)  
> Confluence 最後更新：2022-05-25  
> 摘要最後同步：2026-05-26  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件展示訂閱服務的前端操作流程：登入後點選指定區域，進入訂閱方案頁面，選擇方案並點擊購買；系統檢查餘額，足夠則顯示成功畫面，不足則顯示失敗畫面。對 AI 開發的幫助在於知曉購買流程的 UI 狀態與互動步驟，可作為前端開發或測試的參考。

**AI 開發需要注意的部分**：
- 購買訂閱方案時，須檢查帳戶餘額（餘額不足時不可完成購買）。
- 前端需根據購買結果展示對應的成功/失敗畫面。
- 實際頁面操作可能與截圖不符（最後更新 2022-05-25），需人工確認現行流程是否變更。
- 文件僅為靜態截圖與簡短步驟，未說明後端邏輯或異常處理細節。