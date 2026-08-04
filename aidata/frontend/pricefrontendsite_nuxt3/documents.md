# pricefrontendsite_nuxt3 — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 12:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---


## 業務規範類


### TCZB-4039 [球王 APP] - 活動更新

> Confluence 頁面 ID：79466167
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79466167)
> 摘要檔：[processed/79466167-summary.md](../../confluence/processed/79466167-summary.md)
> Confluence 最後更新：2025-11-05
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件是球王 APP 的功能更新清單，規範了多項前端顯示邏輯和後端行為變更。重點包括：賽事列表和內頁根據 otherInfo 特定欄位顯示運彩、緯來、愛爾達和 AI 圖示的條件；個人預測解鎖從檢查 VIP 改為直接調用 API 並統一處理每日免費解鎖限制；以及高手頁 AI 預測表格需移除「反下冥燈」功能。

**關鍵業務規則**：
- 賽事頁顯示「AI」圖示的條件為 otherInfo.AI == "true"（注意為字串比對，而非布林值）
- 賽事內頁需依據 otherInfo.AI == "true" 來判斷是否顯示「AI分析文章 賽事頻道」區塊
- 個人預測解鎖機制調整：前端不再先檢查使用者是否為 VIP，改為直接調用解鎖 API，由後端檢查並在達到每日免費解鎖三次限制時，統一返回 403 status code 和 "Today's free unlock limit has been reached" 訊息
- 高手頁的「AI預測表格」中需移除「反下冥燈」相關顯示
- 服務條款與隱私條款中，公司名稱由「正邦」統一修改為「曜木」

**注意事項**：
- ⚠️ 容易誤解：otherInfo.AI 的值為字串 "true"，而非布林值 true，開發時需進行字串比對


### TCZB-3917 [球王] - AI預測 / 頁面訊息修改 / 球王名人堂

> Confluence 頁面 ID：79464638
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464638)
> 摘要檔：[processed/79464638-summary.md](../../confluence/processed/79464638-summary.md)
> Confluence 最後更新：2025-09-17
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義球王網站多項業務變更：高手頁面以AI預測取代反下冥燈；全站公司名稱與版權資訊更新為曜木科技/YMTech；完賽賽事頁隱藏盤口賠率與操盤訊號；並提供AI預測的設計原型及名人堂新Layout。

**關鍵業務規則**：
- 高手頁面移除「反下冥燈」功能，改為「AI預測」模組
- 網站中所有「正邦數位」中文字樣改為「曜木科技」；「ZB Digital Co., Ltd.」改為「YMTech Co., Ltd.」
- 版權宣告文字由「Copy Right © 2021 zbdigital」更新為「Copy Right © 2025 YMTech Co., Ltd.」
- 完賽賽事頁面中，移除「盤口賠率」與「操盤訊號」兩個資訊區塊

**注意事項**：
- ⚠️ 公司名稱與版權修改範圍涵蓋全站，開發時需確保所有前端頁面統一替換，避免漏改


### TCZB-3838 [球王] - 賽事字卡調整/賽事頁面更新/UI調整

> Confluence 頁面 ID：79463213
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463213)
> 摘要檔：[processed/79463213-summary.md](../../confluence/processed/79463213-summary.md)
> Confluence 最後更新：2025-07-31
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義球王前端賽事字卡與賽事頁面的顯示邏輯調整。當賽事有台灣運彩場中資訊時，字卡與頁面顯示台彩圖示與「場中」文字；有AI分析文時，字卡顯示AI圖示，頁面切換為AI分析、盤口賠率、操盤訊號頁籤，否則維持舊有頁籤。

**關鍵業務規則**：
- 賽事字卡：若該賽事台灣運彩有開場中，顯示台彩小ICON圖示及文字「場中」；若有AI分析文，顯示AI icon圖示
- 賽事頁面頁籤：若賽事有AI分析文，頁籤依序顯示為「AI分析」、「盤口賠率」、「操盤訊號」
- 賽事頁面：移除聊天室區塊

**注意事項**：
- ⚠️ 無AI分析文時的「照舊」頁籤內容未載明，需人工確認原始預設頁籤為何


### TCZB-3978 [球王] - 足球、籃球走地AI預測推薦/球王名人堂

> Confluence 頁面 ID：79465416
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465416)
> 摘要檔：[processed/79465416-summary.md](../../confluence/processed/79465416-summary.md)
> Confluence 最後更新：2025-10-20
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義兩項功能：足球、籃球賽事字卡下半部新增「走地AI預測」區塊，包含時間切換、預測結果顏色標示（綠/紅）、按玩法顯示資料、小i圖示顯示權重說明等互動細節；修改球王名人堂的數據展示方式。

**關鍵業務規則**：
- 走地AI預測區塊上方提供時間切換按鈕，點擊後切換表格內資料，被選取的時間顯示為紅色
- 有資料的欄位背景為米黃色，若預測結果正確則該欄位背景轉為綠色，錯誤則轉為紅色
- 某玩法若無預測資料，則完全隱藏該玩法欄位

**注意事項**：
- ⚠️ API格式需參照另一頁面「足球Inplay AI預測畫面」(pageId=79464933)


### TCZB-4200 [球王] - 彩池場中競猜

> Confluence 頁面 ID：79468285
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79468285)
> 摘要檔：[processed/79468285-summary.md](../../confluence/processed/79468285-summary.md)
> Confluence 最後更新：2026-02-04
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義「球王」產品的多項功能需求，包含：場中競猜的輪詢與更新策略、熱門彩池每注獲利計算公式、訂閱方案新增即時洞察（場中AI推薦）權益、常見問題內容調整，以及社群文章留言數超過20顯示「爆」的規則。

**關鍵業務規則**：
- 場中競猜頁面進入時，需調用一次「場中競猜賽事」及「會員競猜注數」資料
- 場中賽事若非進行中，每隔60秒重新調用；若為進行中，則每隔10秒重新調用
- 熱門彩池中，每個選項的「預期每注獲利」計算公式為：(總獎金 × (1 - 手續費比率)) ÷ 該選項注數
- 社群文章若留言總數超過20則，需在文章列表/詳情處顯示「爆」字樣

**注意事項**：
- ⚠️ 輪詢間隔與WebSocket更新方式為需求描述，實際實作技術細節未定義


### TCZB-4085 [球王] - AI預測報表更新

> Confluence 頁面 ID：79466850
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79466850)
> 摘要檔：[processed/79466850-summary.md](../../confluence/processed/79466850-summary.md)
> Confluence 最後更新：2025-12-11
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義球王預測服務首頁文章與 Inplayz News 整合的 UI 行為規則。包含：非本人文章隱藏右上角按鈕、底部新增分享按鈕、屏蔽功能移至追蹤按鈕右側、未登入點擊屏蔽強制跳轉登入視窗；Inplayz News 文章列表中圖片缺失時顯示填充圖、標題取文章第一句、內文取第二或第三句。

**關鍵業務規則**：
- 首頁文章底部新增分享按鈕，取代原有的複製連結功能
- 屏蔽功能按鈕移動至追蹤按鈕的右側
- 未登入用戶點擊屏蔽按鈕時，需彈出登入視窗強制登入
- 文章清單中的標題擷取文章內文的第一句
- 文章內頁標題使用文章第一句作為最終顯示標題



## 技術設計類


### PriceFrontEndSite(Nuxt3) Architecture

> Confluence 頁面 ID：47222701
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/PriceFrontEndSite%28Nuxt3%29+Architecture)
> 摘要檔：[processed/47222701-summary.md](../../confluence/processed/47222701-summary.md)
> Confluence 最後更新：2023-11-30
> 摘要最後同步：2026-05-26

**摘要**：
這份文件描述 PriceFrontEndSite 以 Nuxt3 重構後的前端架構，包含目錄結構、啟動方式、核心技術（如 useFetch、Pinia、Composables）及開發約定。對於 AI 開發，可快速掌握此服務的框架慣例、自動導入規則、型別命名規範以及靜態資源部署路徑變更。

**關鍵設計決策**：
- 使用 Nuxt3 的檔案路由系統自動生成路由，以 pages 目錄結構對應 URL 路徑
- API 請求統一使用 useFetch（SSR 場景必須），不引入 axios
- 狀態管理採用 Pinia 而非 Vuex，並在 store/index 統一導出
- 組件利用 Nuxt 的自動導入功能，命名約定為 components/global/xxx => <GlobalXxx>
- 型別命名規範：interface 以 I 開頭、type 以 T 開頭、enum 以 E 開頭
- 靜態圖片資源從 assets 移至 Nginx 路徑 /usr/local/openresty/nginx/html/downloads/sport，打包時不再處理圖片路徑
- i18n 翻譯檔禁止直接修改 locales/*.json，需透過 i18n-sync 工具統一編輯

**影響範圍**：
- onMounted 中使用非同步操作時，需用 setTimeout 包裝以避免頁面刷新時被跳過（因 Nuxt 生命週期問題）


### TCZB-3819 [球王] - 首頁調整

> Confluence 頁面 ID：79462985
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79462985)
> 摘要檔：[processed/79462985-summary.md](../../confluence/processed/79462985-summary.md)
> Confluence 最後更新：2025-07-16
> 摘要最後同步：2026-05-27

**摘要**：
文件說明球王首頁的兩項調整：社群區塊新增「台灣運彩」分類（Tag: TWSL），並在彩池總獎金右側增加派彩說明圖標，點擊後彈窗顯示保底、加碼、手續費資訊，保底或加碼為 0 則隱藏該項目。

**關鍵設計決策**：
- 首頁社群區塊必須包含「台灣運彩」分類，其識別標籤（Tag）為 TWSL
- 若保底金額或加碼金額為 0，該項目不顯示於說明視窗中


### TCZB-4005 [球王] - 需求調整

> Confluence 頁面 ID：79465585
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465585)
> 摘要檔：[processed/79465585-summary.md](../../confluence/processed/79465585-summary.md)
> Confluence 最後更新：2025-10-30
> 摘要最後同步：2026-05-27

**摘要**：
本文件規範高手頁及至尊球王頁面導入「球王爭霸戰」相關功能，含廣告彈窗的新增與移除、常見問題與球王項目說明新增、訂閱方案頁面文案更新、至尊球王頁面選項變更為球王爭霸戰/球王榜/球王名人堂。

**關鍵設計決策**：
- 至尊球王頁面的選項變更為「球王爭霸戰」、「球王榜」、「球王名人堂」三個頁籤
- 訂閱方案頁面內容改為三點：解鎖無限、專屬賽道、完全沉浸
- 至尊球王頁面的比例數值需透過 API 動態提供，而非靜態設定


### TCZB-4115 [球王] - 頁面調整

> Confluence 頁面 ID：79467422
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467422)
> 摘要檔：[processed/79467422-summary.md](../../confluence/processed/79467422-summary.md)
> Confluence 最後更新：2025-12-26
> 摘要最後同步：2026-05-27

**摘要**：
這份需求文件描述「球王」專案的多項前端頁面調整，包括社群新增熱門/最新文章切換、讚按鈕旁加入Z幣動畫、手機版發文圖示改為筆插Z幣、彩池競猜頁籤置換圖示，以及Header在不同螢幕寬度下顯示Z幣餘額的規則。

**關鍵設計決策**：
- Header 在螢幕寬度 ≤375px 時隱藏使用者名稱與導覽選項；992px 時顯示導覽選項但隱藏使用者名稱；≥1200px 時全顯示
- Z幣餘額顯示規則：百萬以上數值簡寫為「m」，取小數點後兩位且無條件捨棄；每三分鐘自動刷新

**影響範圍**：
- 這些規則直接影響 Header 組件的 RWD 實作和 Z幣顯示邏輯


### TCZB-4141 [球王] - 首頁更新 / 任務頁面

> Confluence 頁面 ID：79467705
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467705)
> 摘要檔：[processed/79467705-summary.md](../../confluence/processed/79467705-summary.md)
> Confluence 最後更新：2026-01-06
> 摘要最後同步：2026-05-27

**摘要**：
文件定義球王活動首頁和任務頁面的更新需求。首頁手機版佈告欄改為跑馬燈，新增熱門彩池模組（點擊長條圖看投注記錄，投注按鈕開下注彈窗）；新增Z幣任務按鈕和任務頁面，其中簽到、競猜、社群、平台任務分別導向對應功能頁面。

**關鍵設計決策**：
- 首頁手機版佈告欄使用跑馬燈形式展示
- 熱門彩池僅顯示兩個選項
- 點擊熱門彩池的選項比例長條圖，打開該彩池的投注紀錄彈窗
- Z幣任務頁面中，簽到任務點擊「前往任務」打開每日簽到彈窗


### TCZB-3744 [球王] - 賽事頁效能優化

> Confluence 頁面 ID：76546888
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76546888)
> 摘要檔：[processed/76546888-summary.md](../../confluence/processed/76546888-summary.md)
> Confluence 最後更新：2025-05-27
> 摘要最後同步：2026-05-27

**摘要**：
文件說明賽事頁與賽事內頁的效能優化設計，將取得賽事 API 由撈取七天改為一天，調整刷新頻率與觸發時機，並將日期賽事數量計算轉移至賽事數量 API；賽事內頁透過 LocalStorage 記錄賽事狀態，對進行中賽事以 query temp=NOW 避開快取，並結合 WS 推送即時更新比分。

**關鍵設計決策**：
- 進行中賽事必須避開快取以取得最新比分，非進行中賽事可使用正常快取
- 賽事內頁每次調用賽事資料 API 後需將狀態與日期存入 LocalStorage
- 取得賽事 API 改為只撈取一天資料，單次傳輸量從 300kb~2mb 降至 60kb~500kb

**影響範圍**：
- 賽事資料 API 已有 2 分鐘快取，可透過 query temp=NOW 繞過快取取得最新資料
- ws 推送的賽事資料直接更新畫面上比分，不必等待定時輪詢


### TCZB-4201 [球王服務] - 場中競猜API

> Confluence 頁面 ID：79468304
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79468304)
> 摘要檔：[processed/79468304-summary.md](../../confluence/processed/79468304-summary.md)
> Confluence 最後更新：2026-02-04
> 摘要最後同步：2026-05-27

**摘要**：
定義場中競猜功能的 API 設計，包含 PriceCenterService（設定/取得熱門賽事）與 PriceCenterSite（會員投注、查詢注數、取得賽事與賠率）。玩法僅限讓分(RBHA)與大小(RBOU)，賠率快取10秒，投注點數固定100，一注200Z幣。

**關鍵設計決策**：
- 場中競猜僅提供讓分(RBHA)與大小(RBOU)兩種玩法
- 會員投注(point)固定為100，一注費用為200Z幣
- 走地賠率 API 快取時間為10秒

**影響範圍**：
- 將設定熱門賽事交由 PriceCenterService（後台），用戶查詢與投注交由 PriceCenterSite，維持服務邊界


### TCZB-4330 [球王] - 賽事交易所 / 會員賽事交易紀錄查詢

> Confluence 頁面 ID：79471631
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471631)
> 摘要檔：[processed/79471631-summary.md](../../confluence/processed/79471631-summary.md)
> Confluence 最後更新：2026-05-19
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了「賽事交易所」與「會員賽事交易紀錄查詢」兩個頁面的前端設計與API調用流程。賽事交易所需先取得球種聯盟列表，再依此獲取聯盟賽事股價，並透過Socket即時更新進行中比賽；我的倉位則結合會員持倉與批次股價API。

**關鍵設計決策**：
- 賽事交易所頁面先調用取得賽事交易所項目列表API，球種聯盟列表參照預測頁
- 以預設球種聯盟調用取得聯盟賽事股價API，進行中的比賽透過Socket即時更新比分
- 「我的倉位」區塊使用會員持倉API與批次取得賽事股價API組合
- 賽事交易紀錄頁以我的預測頁為基底，移除殺手資訊、今日/歷史切換及圖表

**注意事項**：
- ⚠️ 賽事交易紀錄功能標注「尚未確認，目前非必要完成」，可能存在變更或延後實作


### TCZB-4116 [球王服務] - 球王系統調整

> Confluence 頁面 ID：79467355
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467355)
> 摘要檔：[processed/79467355-summary.md](../../confluence/processed/79467355-summary.md)
> Confluence 最後更新：2025-12-23
> 摘要最後同步：2026-05-27

**摘要**：
本文档描述球王系统多项功能调整：实现注册验证后赠送1000 Z币（覆盖三种登录方式），新增按球种获取热门文章的 API（基于 MeiliSearch，返回权重前20篇），会员迷你搜索改用 MeiliSearch 索引，争霸战获利点数计算引入最低预测场次（PredictCount）机制。

**關鍵設計決策**：
- 采用 MeiliSearch 替代 Cassandra 缓存实现快速会员搜索与热门文章查询
- 热门文章以球种为维度，按权重排序固定返回20篇，支持分页索引
- 争霸战新增预测场次限制，并影响最终获利点数得分

**注意事項**：
- ⚠️ PredictCount 如何影响 PointProfit 的具体计算规则未在本文档中给出，需参考其他文档或人工确认


### TCZB-3864 [球王] - 賽事字卡和賽事頁面調整/至尊球王排行榜

> Confluence 頁面 ID：79463722
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463722)
> 摘要檔：[processed/79463722-summary.md](../../confluence/processed/79463722-summary.md)
> Confluence 最後更新：2025-08-18
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義兩項主要需求：賽事字卡與賽事頁面新增緯來、愛爾達轉播圖示（愛爾達商標需顏色反轉）；新增至尊球王排行榜頁面，列出前十名及本人排行資料。目前功能Demo僅開放Admin帳號存取。

**關鍵設計決策**：
- 賽事字卡需顯示緯來與愛爾達轉播圖示，其中愛爾達商標顏色需反轉
- 至尊球王排行榜需提供前十名資料，每筆包含：使用者名稱、名次、獲利點數、解鎖次數等
- 排行榜Demo階段僅限Admin帳號可閱覽，正式上線前需移除限制

**注意事項**：
- ⚠️ 愛爾達商標顏色反轉的具體條件（如背景明暗）未說明，需UI設計進一步釐清


### TCZB-3888 [球王] - AI預測報表/會員歷史預測頁面調整

> Confluence 頁面 ID：79464321
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464321)
> 摘要檔：[processed/79464321-summary.md](../../confluence/processed/79464321-summary.md)
> Confluence 最後更新：2025-09-02
> 摘要最後同步：2026-05-27

**摘要**：
這份文件描述了球王網站新增 AI 預測報表頁面及會員歷史預測頁面調整的功能需求。歷史預測頁面的聯盟篩選將只保留用戶有預測記錄的聯盟；另需建立 AI 預測報表頁，展示 1X2、讓分、大小等玩法。

**關鍵設計決策**：
- 會員歷史預測頁面的球種聯盟篩選下拉選單應根據該用戶實際有過預測記錄的聯盟動態生成
- AI 預測報表須支援 1X2、讓分、大小三種玩法類型的預測結果展示
- 連結文字在中文環境為「AI預測報表」，英文環境為「AI Report」