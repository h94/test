# pricecentermanage — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 10:40
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類


### TCZB-608 [PriceCenter] - b365,bwin,betfair page editor

> Confluence 頁面 ID：15401086
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-608+%5BPriceCenter%5D+-+b365%2Cbwin%2Cbetfair+page+editor)
> 摘要檔：[processed/15401086-summary.md](../../confluence/processed/15401086-summary.md)
> Confluence 最後更新：2021-02-25 16:31
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件定義了 PriceCenter 管理後台中針對 bet365、betfair、bwin、pinnacle 等平台的頁面編輯 API。提供了依頁面名稱或頁面類型進行更新，以及查詢頁面清單的功能。每個平台有獨立的 REST 端點，更新時需傳入多項參數（如 enabled、interval、maxworks 等），這些 API 供管理員動態調整各平台頁面的顯示設定與擷取排程。

**關鍵業務規則**：
- 支援四個平台：bet365、betfair、bwin、pinnacle，各有獨立 API 端點
- 更新特定頁面名稱：POST /{platform}/page/{pagename}，平台為 bet365、betfair、bwin 或 pinnacle
- 批量更新頁面類型：POST /{platform}/pages/{pagetype}（pinnacle 使用 gametype 而非 pagetype）
- 查詢頁面清單：GET /{platform}/pages，可帶 pagetype 和 enabled 參數進行過濾
- 更新時必須提供的共用參數包括：enabled、get_data_interval、interval、maxworks、minworks、popular
- pinnacle 平台在更新時僅需 enabled 參數

**注意事項**：
- ⚠️ 文件中有拼寫錯誤：'be365' 應為 'bet365'，'pinnacl' 應為 'pinnacle'，在實際開發時需校正
- ⚠️ pinnacle 的更新參數僅列出 'enabled'，但可能遺漏其他共用參數，需人工確認


### TCZB-650 [PriceCenterManage]-KU Account API

> Confluence 頁面 ID：15401415
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-650+%5BPriceCenterManage%5D-KU+Account+API)
> 摘要檔：[processed/15401415-summary.md](../../confluence/processed/15401415-summary.md)
> Confluence 最後更新：2021-03-12 11:48
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了一個用於關閉 KU 帳號的 API 端點。對 AI 開發來說，需要知道當系統需要封鎖或關閉特定 KU 帳號時，應透過 POST 請求呼叫此 API。此為需求規範文件，僅定義了 API 路徑格式與 HTTP 方法，缺少請求參數、回應格式、認證方式等技術細節，實作時需參考其他技術文件或程式碼。

**關鍵業務規則**：
- KU 帳號可透過 API 被關閉（BAN），關閉後該帳號應無法繼續使用
- 關閉 KU 帳號的 API 端點為 POST /system/accounts/closeaccound/ku/{account}，其中 {account} 為帳號識別碼

**注意事項**：
- ⚠️ API 路徑中的 closeaccound 可能是拼寫錯誤（應為 closeaccount），實作時需人工確認正確路徑
- ⚠️ 文件僅定義了 API 路徑，缺少請求參數、回應格式、錯誤處理等規格，無法直接實作
- ⚠️ 此需求來自 Sprint18，距今已久，API 可能已有變更或被其他功能取代


### TCZB-654 [PriceCenterManage]-Bwin Dashboard

> Confluence 頁面 ID：15401423
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-654+%5BPriceCenterManage%5D-Bwin+Dashboard)
> 摘要檔：[processed/15401423-summary.md](../../confluence/processed/15401423-summary.md)
> Confluence 最後更新：2021-03-08 10:08
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件記載於 PriceCenter 管理模組中新增 Bwin Controller 狀態功能的兩項需求：一為提供新增狀態的 API，二為在 Dashboard 上顯示 Bwin Controller Status。內容極簡，僅有使用者故事而無具體業務邏輯或技術細節，主要作為開發任務追蹤之用。

**關鍵業務規則**：
- 提供用於新增 Bwin Controller 狀態的 API
- 在 Dashboard 上顯示 Bwin Controller Status

**注意事項**：
- ⚠️ 文件僅有簡略需求，無完整業務規則、欄位定義或狀態生命週期說明
- ⚠️ 最後更新於 2021 年，需確認該功能是否已實作或後續已有變更


### TCZB-786 [PriceCenterManger] - 球種開關策略

> Confluence 頁面 ID：18645924
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=18645924)
> 摘要檔：[processed/18645924-summary.md](../../confluence/processed/18645924-summary.md)
> Confluence 最後更新：2021-05-18 11:08
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義了 PriceCenterManger 提供的球種玩法開關控制 API。外部 Python 程式可透過 POST /api/system/controllerpages/{site} 傳送包含 PageName 與 Enabled（0 關閉/1 開啟）的 JSON 陣列，由後端驗證 site 與 pagename 是否存在後更新 DB enabled 欄位。成功回傳 "success"，失敗回傳 "site not found" 或 "pagename not found"。可作為 AI 整合此服務時的操作介面參考。

**關鍵業務規則**：
- Enabled 欄位僅接受 0（關閉）或 1（開啟）
- site 路徑參數必須對應已存在的站點，否則回傳 "site not found"
- 每個 PageName 必須在該 site 下存在，否則回傳 "pagename not found"
- 請求主體須為 Bet365Page Model 的 JSON 陣列，每個物件包含 PageName 與 Enabled 欄位

**注意事項**：
- ⚠️ 文件最後更新於 2021-05-18，且位於「舊的Projects 1-200」路徑，API 端點與內網 IP 可能已變更，需人工確認目前是否仍在使用此 API


### TCZB-2931 [PriceCenterManage] - 運動站台通知訊息管理

> Confluence 頁面 ID：47223303
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47223303)
> 摘要檔：[processed/47223303-summary.md](../../confluence/processed/47223303-summary.md)
> Confluence 最後更新：2023-09-13 13:34
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了一組用於管理運動站台通知訊息的 RESTful API，涵蓋通知主題（Topic）和通知訊息（Message）的新增、查詢、修改功能。資料儲存於 MySQL sport 資料庫並使用 Redis DB 7 進行快取，支援繁體中文（TW_Content）、簡體中文（CN_Content）及英文（EN_Content）三種語言。此文件對 AI 開發的幫助在於提供了精確的 API 規格、資料庫結構與快取策略，是實作此通知管理功能的直接技術依據。

**關鍵業務規則**：
- 通知訊息內容需支援繁體中文（TW_Content）、簡體中文（CN_Content）及英文（EN_Content）三種語言
- 通知主題名稱（NameMap）與訊息標題（Title）需以物件格式提供多語系內容，key 值為 'zh-TW', 'zh-CN', 'en-US'
- 取得全部公告項目的 API 預設會使用快取資料（cacheData=true），若需取得最新資料需傳入 cacheData=false
- 通知主題和訊息都具備啟用/停用狀態（Enabled=1/0），可用於控制前端是否顯示

**注意事項**：
- ⚠️ Redis DB 編號指定為 7，若未來統整 Redis 資源配置，需要特別注意此設定，可能造成連線錯誤
- ⚠️ API 參數範例與 Response 範例中的欄位命名大小寫不一致，實作時需人工確認統一的 naming convention


### TCZB-3435 [PriceCenterManage] - 球王站內信系統

> Confluence 頁面 ID：55581227
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55581227)
> 摘要檔：[processed/55581227-summary.md](../../confluence/processed/55581227-summary.md)
> Confluence 最後更新：2024-09-05 14:30
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義球王站台站內信系統 API，包含信件新增、查詢、閱讀狀態更新等功能。使用 MySQL 作為持久存儲，Redis 作為信件列表快取，寫入時先寫 Redis 再寫 DB。API 路由均在 /pricecentermanage/api/sport/notifications/ 下。

**關鍵業務規則**：
- 信件無固定存活時間，由會員自行刪除
- 查詢郵件列表時 startTime 預設前 2 天時間，endTime 預設現在時間
- 讀取信件時，若快取列表狀態為 0（未讀），同時更新 DB 和 Redis 的閱讀狀態為已讀；第二次讀取後不做任何動作

**注意事項**：
- ⚠️ 注意 startTime 預設前 2 天，若無信件可能返回空列表，前端應避免誤導
- ⚠️ 閱讀狀態更新基於快取列表狀態為 0 時才執行，須確保快取中狀態與 DB 一致，否則可能漏更新或重複更新

---

## 技術設計類


### TCZB-4364 [PriceCenterManage] - TG999站台配置

> Confluence 頁面 ID：79471587
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471587)
> 摘要檔：[processed/79471587-summary.md](../../confluence/processed/79471587-summary.md)
> Confluence 最後更新：2026-05-19 17:21
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件記錄在 PriceCenterManager 服務中為 TG999 爬蟲新增站台以及對應的 API 端點。設計上參考了現有 hga 站台的爬蟲策略與 kkk 站台的帳號取得 API，新增三個 API：取得可用的頁面與帳號、通知系統重啟以清除先前控制的頁面與帳號、通知某頁面與帳號已停止處理。對 AI 開發的幫助在於提供了具體 API 的路由、參數與回應規格。

**關鍵設計決策**：
- 為 TG999 爬蟲新增專屬的 API 入口，路由前綴使用 /pricecentermanage/api/tg999，與其他站台的 API 區分
- 爬蟲策略與現有的 hga 站台相同，直接複用相同邏輯，降低開發成本與不一致風險
- 取得帳號的 API 參考了 kkk 站台的設計，確保回傳的帳號欄位一致（包含 PageName, PageType, Account, Password, Phone, UserName）

**注意事項**：
- ⚠️ 文件提到「參考 kkk 站台取得帳號的API後，新增TG999」，但同時又註明「與 hga 相同的爬蟲策略」，需人工確認最終實現是否屬於 hga 的變體，還是與 kkk 完全一致
- ⚠️ 未說明 API 的回應狀態碼及錯誤處理機制，實作時需參考其他類似站台的實作補充


### TCZB-642[PriceCenterManage]- KU GetPage API

> Confluence 頁面 ID：15401416
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-642%5BPriceCenterManage%5D-+KU+GetPage+API)
> 摘要檔：[processed/15401416-summary.md](../../confluence/processed/15401416-summary.md)
> Confluence 最後更新：2021-03-16 09:34
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件為 PriceCenterManage 服務新增 KU provider 的 Page API 設計，定義了三個端點：GET ku/getpage/{provider} 取得網頁與帳號資訊，POST ku/workfor/{pageNames}/{account}/{provider} 進行心跳偵測，POST ku/sendstop/{pageName}/{account}/{provider} 刪除 handler。這份設計文件可作為 AI 開發時串接 KU 相關功能的 API 規格參考。

**關鍵設計決策**：
- 將 KU 的 Page 相關功能獨立為三個 RESTful API 端點，使用路徑參數傳遞 provider、pageNames、account 等
- getpage 回傳固定結構 {pageName, pageType, account, password}

**注意事項**：
- ⚠️ 文件最後更新於 2021-03-16，需人工確認這些 API 是否仍在使用，實作邏輯或參數是否已變更
- ⚠️ workfor 與 sendstop 的回傳參數未定義，需人工確認


### TCZB-702 [PriceCenterManage] - display KUPages information on dashboard

> Confluence 頁面 ID：15402291
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-702+%5BPriceCenterManage%5D+-+display+KUPages+information+on+dashboard)
> 摘要檔：[processed/15402291-summary.md](../../confluence/processed/15402291-summary.md)
> Confluence 最後更新：2021-04-06 15:43
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文檔定義了在 PriceCenterManage 服務中增加 Ku Controller 狀態管理的 API 與 Dashboard 展示功能。API 透過 GET 請求將狀態字串（多組 key:value 以逗號分隔）寫入資料庫，並在 Dashboard 顯示這些狀態資訊。對 AI 開發而言，可藉此了解 Ku 控制器狀態的匯報機制與資料格式。

**關鍵設計決策**：
- 採用單一查詢參數 status 傳送多個鍵值對（格式如 A:tts1122,P:BK,V:04/04 09:09,H:），推測是為了減少 API 端點數量，以簡化客戶端整合

**注意事項**：
- ⚠️ 文件來自 TCZB Sprint20（2021-04-06），可能已過時，需人工確認該 API 是否仍在使用
- ⚠️ 狀態字串範例中部分鍵值為空（例如 H:），未說明是否允許空值或預設行為


### TCZB-1066 [PriceCenterManager]-Nova / kkk Getpage 策略

> Confluence 頁面 ID：24085809
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24085809)
> 摘要檔：[processed/24085809-summary.md](../../confluence/processed/24085809-summary.md)
> Confluence 最後更新：2021-09-10 09:40
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義 Nova 與 KKK 兩種爬蟲代理的 Get Page API，用於 PriceCenter 分配爬蟲任務並接收心跳與停止通知。Nova 可一次索取多個頁面，KKK 則返回單一頁面並附帶帳密。文件提供 Nova page 的分類維度（彩種、Today/Early、玩法）與 VM 對應表。

**關鍵業務規則**：
- Nova getpage API 支援指定 provider 與 pageCount，返回最多 pageCount 個頁面名稱
- KKK getpage API 固定返回一個頁面名稱及對應帳密，且策略與 ku 相同
- 工作心跳 API 用於通知伺服器正在處理的頁面，Nova 傳入頁面名稱列表，KKK 則需傳入 pageNames、provider、account
- 停止工作 API 用於通知停止特定頁面任務，Nova 僅需 provider 和 pageName，KKK 需 pageName、provider、account
- Nova page 資料表以 GameType、Today/Early、PlayMode 組合定義任務類型，每個類型有 MaxWork 上限

**關鍵設計決策**：
- KKK 策略直接沿用 ku 策略，可能為了快速複製既有邏輯
- Nova page 設計了多種 Today/Early 及 PlayMode 分類，推測是為了支援不同投注市場的爬取需求

**注意事項**：
- ⚠️ 文件最後更新於 2021-09-10，且位於「舊的Projects 1-200」路徑，極可能已廢棄或大幅度變更
- ⚠️ 文件中提到的「策略」僅標題描述，未提供詳細邏輯或判斷條件


### [Chrome Extension] call price center manage auto update規劃

> Confluence 頁面 ID：24086194
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24086194)
> 摘要檔：[processed/24086194-summary.md](../../confluence/processed/24086194-summary.md)
> Confluence 最後更新：2021-09-13 09:46
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件為 Chrome Extension 自動更新機制的早期規劃，定義了兩個後端 API 需求（取得最新版本、強制重啟），並設計 extension_version 表以儲存各站點對應的擴充功能版本。對於 AI 開發，這意味著 pricecentermanage 服務需要提供對應端點，並依 site 參數查詢/管理 extension_version 資料。

**關鍵業務規則**：
- 需實現 get version 功能：依據 site 參數查詢 extension_version 表，回傳該站點最新版號
- 需實現 reload 功能：強制客戶端 Chrome Extension 進行重啟（具體機制未定義）

**關鍵設計決策**：
- 採用 pricecenter keyspace 下的 extension_version 表，以 site 為 primary key 儲存版本字串，簡化查詢結構

**注意事項**：
- ⚠️ 文件最後更新於 2021-09-13，屬於過期規劃，可能已被取代或未實作
- ⚠️ 文件內容不完整，缺乏 reload 的實際觸發機制與版號比較邏輯


### TCZB-1098[PriceCenterManager]-sa8888 get page

> Confluence 頁面 ID：24086359
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-1098%5BPriceCenterManager%5D-sa8888+get+page)
> 摘要檔：[processed/24086359-summary.md](../../confluence/processed/24086359-summary.md)
> Confluence 最後更新：2021-09-22 15:07
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件為 PriceCenterManager 服務新增 sa8888 的 get page API、工作心跳與停止工作 API，並在 dashboard 增加對應訊息顯示。設計上直接沿用 nova 的頁面管理流程，每個球種玩法頁面的 maxwork 設定為 2。對 AI 開發的幫助在於清晰定義了 sa8888 頁面介面的路由、參數與回應格式。

**關鍵業務規則**：
- 每個球種玩法頁面的 maxwork 設定都為 2

**關鍵設計決策**：
- 流程與 nova 相同，以保持一致性並減少重複設計
- maxwork 設定為 2，可能為了限制同時處理的任務數量，避免資源壅塞

**注意事項**：
- ⚠️ 文件最後更新於 2021-09-22，且位於「舊的Projects 1-200」目錄，可能已過時或不再使用


### TCZB-1133 [PriceCenterManager]-nk.net get page

> Confluence 頁面 ID：24086633
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-1133+%5BPriceCenterManager%5D-nk.net+get+page)
> 摘要檔：[processed/24086633-summary.md](../../confluence/processed/24086633-summary.md)
> Confluence 最後更新：2021-10-04 14:18
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件設計了一組用於 nk.net 的 API，包含取得頁面、工作上報心跳、停止工作三個端點。取得頁面機制複用現有 kkk 服務的設計，回應中帶有頁面名稱、類型、帳號與密碼（明文）。這些 API 用於儀表板增加 nk.net 訊息顯示與工作狀態監控。

**關鍵設計決策**：
- 取得頁面的帳號機制與 kkk 相同，復用既有邏輯，避免重複開發
- 心跳與停止工作均採用 POST 方法，區分工作狀態的變更操作

**注意事項**：
- ⚠️ 回應中的 Password 為明文，不符合安全實務，需審核是否可接受或應改用密文
- ⚠️ 依賴的 kkk 機制未在文件中說明，若該機制已變更或移除，本設計可能失效
- ⚠️ 文件最後更新於 2021 年，設計可能已過時


### TCZB-1603 [PriceCenterManage]-永利(新HGA) Get Page API

> Confluence 頁面 ID：32538953
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32538953)
> 摘要檔：[processed/32538953-summary.md](../../confluence/processed/32538953-summary.md)
> Confluence 最後更新：2022-03-08 15:44
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了為永利新HGA站台新增取得Page策略的API設計。核心變更是基於既有HGA機制，新增一個名為hga2的provider路由，並在回傳帳號時多回傳一個UserName欄位。文件明確了三個REST API端點（取得page、工作心跳、停止工作）及其路由格式。

**關鍵設計決策**：
- 新永利站台機制與既有HGA相同，直接複用邏輯，僅在Response Model增加UserName欄位回傳
- 站台識別名稱為hga2.com（簡中站台），API路由使用hga2作為provider識別字
- Dashboard需配置VM群組，Program名稱定義為Hga2C

**注意事項**：
- ⚠️ 文件最後更新於2022-03-08，距今超過兩年，需人工確認此API是否仍在使用或已被後續版本取代
- ⚠️ 文件未說明參數provider的具體取值範圍或驗證規則，需人工確認


### TCZB-2419 [PriceCenterManage] - AIScore策略

> Confluence 頁面 ID：44664730
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44664730)
> 摘要檔：[processed/44664730-summary.md](../../confluence/processed/44664730-summary.md)
> Confluence 最後更新：2023-01-07 11:35
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義了 pricecentermanage 服務中 AIScore 工作控制的 API 端點：取得工作頁面設定 (GET /aiscore/page/{provider})、工作機器心跳 (POST /aiscore/workfor/{provider})、停止特定頁面工作 (POST /aiscore/sendstop/{provider}/{pageName})。這些 API 用於監控和管理 AI 分數相關的工作流程。

**關鍵設計決策**：
- 使用 provider 路徑參數區分不同工作提供者，支援多個 AI Score 來源
- 透過心跳 endpoint 實現工作機器健康檢查，確保節點正常運行
- 支援針對特定 pageName 發送停止指令，實現細粒度的作業控制

**注意事項**：
- ⚠️ API 路由中 `/aiscor/workfor` 可能為 `/aiscore/workfor` 的筆誤，需人工確認
- ⚠️ 多數 API 的 Parameter 與 Response 欄位未提供具體內容，實作需補充細節
- ⚠️ 文件最後更新於 2023-01-07，距今較久，可能已有變更或棄用


### [PriceCenterManage] - Au8tw策略

> Confluence 頁面 ID：47218795
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47218795)
> 摘要檔：[processed/47218795-summary.md](../../confluence/processed/47218795-summary.md)
> Confluence 最後更新：2023-02-09 10:55
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了與 Au8tw 策略相關的 API，包括取得帳號、發送心跳、停止工作及更新機器狀態。這些 API 用於 PriceCenterManage 服務管理 Au8tw 帳號的運作狀態。對 AI 開發有助於了解如何與 Au8tw 帳號服務互動及控制其生命週期。

**關鍵設計決策**：
- 文件未詳細列出具體設計決策，需人工對照程式碼確認

**注意事項**：
- ⚠️ 文件最後更新於 2023-02-09，時隔較久，需人工確認 API 是否仍在運作


### [PriceCenterManage] - 球王APP管理功能

> Confluence 頁面 ID：55580260
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55580260)
> 摘要檔：[processed/55580260-summary.md](../../confluence/processed/55580260-summary.md)
> Confluence 最後更新：2024-07-10 15:02
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件定義了 pricecentermanage 服務中，用於管理球王運動站台 APP 裝置的三個 REST API 端點：設定裝置 (POST)、取得裝置列表 (GET) 與查詢單一裝置 (GET)。所有請求與回應均為 JSON 格式，回傳資料包含裝置類型、版本、描述與新增時間 (Unix timestamp)。

**關鍵業務規則**：
- 設定運動站台 APP 裝置時，必須傳入 Device（裝置類型，如 IOS/Android）、Version（版本號）和 Description（更新說明）三個必填欄位
- 取得裝置列表時，回應包含每個裝置的 device、version、description 及 addTime（Unix timestamp，單位秒）
- 查詢單一裝置時，路徑參數 {device} 為裝置類型，回應格式與列表中的單一物件一致

**注意事項**：
- ⚠️ POST /appmanage/sport/appdevices 的回應格式未於文件中定義，需人工確認實際實作

---

## 操作手冊類


### Log查詢操作

> Confluence 頁面 ID：24090967
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24090967)
> 摘要檔：[processed/24090967-summary.md](../../confluence/processed/24090967-summary.md)
> Confluence 最後更新：2022-10-11 14:53
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文說明賽事設定值系統的 Log 查詢操作介面，使用者可選擇玩法（讓分、大小、走地等）與小時級別的時間範圍，查詢賽事設定值的變更記錄。查詢結果會顯示賽事資訊（球種、站台、賽事ID 等）、更新時間及更新內容。對 AI 開發的幫助：需掌握後端查詢 API 的過濾邏輯，特別是時間區間採左閉右開規則（開始整點起，至結束整點前 59 分），並返還對應的欄位結構。

**關鍵業務規則**：
- 玩法選項包含：讓分、大小、其他玩法、走地讓分、走地大小、走地其他玩法、比分、賽事即時狀態
- 時間以 0-23 的小時為單位，開始時間與結束時間皆可留空（- 表示不限）
- 指定開始與結束時間時，查詢範圍為開始整點至結束整點前的所有資料（例：2 ~ 4 查詢 02:00 至 04:59）
- 開始時間為空、結束時間指定時，查詢該結束整點之前的所有資料（不包含該小時）
- 開始時間指定、結束時間為空時，查詢該開始整點之後的所有資料（包含該小時）

**注意事項**：
- ⚠️ 文件最後更新於 2022 年 10 月，可能對應已過時的系統或 UI，需人工確認目前系統是否仍沿用相同的查詢邏輯