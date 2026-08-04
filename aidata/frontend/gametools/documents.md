# gametools — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2025-01-15 10:30
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB-1568 [GameTools]-Log查詢工具

> Confluence 頁面 ID：32538980
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32538980)
> 摘要檔：[processed/32538980-summary.md](../../confluence/processed/32538980-summary.md)
> Confluence 最後更新：2022-03-09
> 摘要最後同步：2026-05-27

**摘要**：
文件定義一個嵌入 GameTools 的內部查詢工具，用於檢索 PriceCenter DB 中使用者對賽事資料的操作紀錄。搜尋條件包含 gametype、日期、action 等，其中日期和 gametype 由後端處理，其他由前端處理。限制僅公司 ZB 帳號可訪問。

**關鍵業務規則**：
- 日期為必填搜尋條件，由後端處理
- gametype 由後端處理，其餘搜尋條件由前端過濾
- 工具僅限 ZB 帳號（公司內部帳號）使用
- 此功能置於 GameTools 內，非獨立站點

**注意事項**：
- ⚠️ 「是否需要限制僅ZB帳號可以訪問」的結果欄為空白，此需求可能仍未確認，需人工查證
- ⚠️ 文件最後更新於 2022-03-09，距今已久，相關實作或 API 可能已變更

---

### TCZB-1392 [GameTools]-強制合併賽事功能

> Confluence 頁面 ID：24092519
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24092519)
> 摘要檔：[processed/24092519-summary.md](../../confluence/processed/24092519-summary.md)
> Confluence 最後更新：2022-02-08
> 摘要最後同步：2026-05-27

**摘要**：
本文件描述了 GameTools 中強制合併賽事、聯盟和隊伍的功能需求，旨在解決資料重複問題。定義了三種合併場景：聯盟強制合併、隊伍強制合併、賽事強制合併，並指定了對應的 API 列表。前端通過開關控制已合併賽事顯示，以啟用強制合併操作。

**關鍵業務規則**：
- 聯盟強制合併（時間搜索）：通過選擇時間範圍，篩選某球種 SiteGame 中已合併的 League 進行合併操作
- 聯盟強制合併（條件搜索）：可通過 URL 攜帶多個 LID（英文逗號分隔）實現多重搜索，支援中英文搜索
- 隊伍強制合併適用條件：相同賽事未合併，且在同一 LID 下出現隊伍相同但 TID 不同的情況
- 賽事強制合併適用條件：賽事未合併，但兩端聯盟和隊伍均已正確合併（即 LID 和 TID 相同，僅 GID 不同），且賽事已存在 GID
- 賽事強制合併操作限制：必須先將顯示模式 switch 切換為 enable（僅顯示已合併賽事），然後才能進行強制合併，只能勾選已有 GID 的賽事

**注意事項**：
- ⚠️ 文檔最後更新於 2022-02-08，屬於舊項目需求，可能已有變更或已廢棄，需人工確認當前系統是否仍使用此功能

---

### TCZB-1500 [GameTools] 提高使用者體驗

> Confluence 頁面 ID：32079875
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32079875)
> 摘要檔：[processed/32079875-summary.md](../../confluence/processed/32079875-summary.md)
> Confluence 最後更新：2022-02-22
> 摘要最後同步：2026-05-27

**摘要**：
這篇文件定義了 GameTools 使用者體驗改善的業務需求，包括全面中文化、合併操作自動化、聯盟隊伍預設邏輯、賽事資料時效過濾、錯誤訊息關鍵字變色及效能檢查。AI 開發時應根據這些規則實作前端提示轉換、自動呼叫 NameMap、篩選近期賽事，以及用正則表達式高亮錯誤訊息中的特定資訊。

**關鍵業務規則**：
- 所有介面提示及標題必須顯示為中文
- 使用者在 Merge 界面點擊多語系站台合併時，系統需自動呼叫 NameMap 功能（原為人工觸發）
- 強制合併聯盟隊伍時，需根據已合併賽事的聯盟隊伍資訊，自動將 Main 預設為對應值
- 撈取今日以後的賽事時，只能取最後更新時間在 12 小時內的資料
- 錯誤訊息中，括號內的關鍵資訊需要變色顯示，提取規則使用正則表達式：(?i)(?<=\[)(.*)(?=\])

**注意事項**：
- ⚠️ 文件來自舊的 Sprint（TCZB Sprint 48），部分需求可能已實作或變更，需人工確認當前系統行為
- ⚠️ 「人工合併...自動呼叫NameMap」敘述存在矛盾，推測為「原本人工操作，現改為自動呼叫」，需與 PO 確認正確流程

---

### TCZB-2165 [GameTools] 聯盟合併

> Confluence 頁面 ID：44663479
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44663479)
> 摘要檔：[processed/44663479-summary.md](../../confluence/processed/44663479-summary.md)
> Confluence 最後更新：2022-12-23
> 摘要最後同步：2026-05-27

**摘要**：
文件定義 GameTools 中聯盟合併的功能需求，提供兩種合併模式：可將一個或多個站台聯盟合併至一個既存聯盟，或將多個站台聯盟合併為一個全新聯盟。操作需先依球種與日期搜尋，再透過篩選欄過濾結果後進行合併。

**關鍵業務規則**：
- 可選擇一個或多個站台聯盟，加上一個目標聯盟，將站台聯盟合併至該目標聯盟
- 可選擇兩個或以上的站台聯盟，直接合併成一個全新的聯盟（無需指定目標聯盟）
- 操作前必須在最上方搜尋欄選擇球種與日期進行搜尋，結果顯示於下方表格；可再使用表格上方的篩選欄進一步篩選資料後進行合併

**注意事項**：
- ⚠️ 文件最後更新為 2022-12-23，距今較久，可能已有變更或補充規則，建議對照最新實作確認
- ⚠️ Figma 原型連結可能已失效或更新，需人工驗證

---

### TCZB-2369 [GameTools] - 強制合併聯盟、編輯聯盟隊伍、編輯原始聯盟隊伍

> Confluence 頁面 ID：44664098
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44664098)
> 摘要檔：[processed/44664098-summary.md](../../confluence/processed/44664098-summary.md)
> Confluence 最後更新：2023-01-03
> 摘要最後同步：2026-05-27

**摘要**：
本文件為 AI SCORE 模組的功能需求規格，定義體育賽事即時看盤系統的完整功能，包括全部賽事瀏覽、即時動畫與實況、賠率呈現、線上聊天室與即時翻譯、預測方案排行與付費規則、收藏功能、球隊與球員數據查詢，以及個人中心。

**關鍵業務規則**：
- 方案功能僅適用於足球與籃球賽事
- 方案排行可依盈利率、勝率、連紅（3天/7天/30天/90天）排序
- 方案中推薦理由為付費內容，一般用戶需付費解鎖，VIP 會員解鎖費用降低
- 已完賽的預測方案，推薦理由改為所有使用者皆可觀看
- 聊天室支援即時翻譯，可選語言包含：無需翻譯、印尼文、英文、西班牙文、土耳其文、泰文、繁體中文、越文
- VIP 會員進入聊天室時會有彈窗提示
- 收藏功能可收藏比賽、球隊、賽事、球員
- 進行中頁面預設顯示當前進行中的比賽，另可切換查看過去 24 小時已結束的比賽，以及未來 24 小時內即將開賽的比賽
- 賠率資訊提供獲勝、讓分、總分選項，並可選擇顯示來源為 bet365、188BET、1XBET、CrownBet
- 比賽詳細資訊的各項目顯示與否取決於資訊來源是否齊全
- 球隊詳細資訊中的項目亦需視資訊齊全程度決定是否顯示

**注意事項**：
- ⚠️ Live 按鈕的具體功能在文件中未明確定義（僅標示「不知道功用」），需人工確認
- ⚠️ 文件標題為「強制合併聯盟、編輯聯盟隊伍…」但內文主要為 AI SCORE 概述，可能為同一 Confluence 頁面中合併了不同主題，需人工確認範圍

---

### TCZB-2385 [GameTools] - 人工合併、操作紀錄

> Confluence 頁面 ID：44664013
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44664013)
> 摘要檔：[processed/44664013-summary.md](../../confluence/processed/44664013-summary.md)
> Confluence 最後更新：2022-12-29
> 摘要最後同步：2026-05-27

**摘要**：
這是一份 GameTools（合併站台）的功能需求文件，說明要在現有的合併站台功能中新增兩個核心功能：人工合併與操作紀錄。人工合併讓管理者可以手動執行站台合併；操作紀錄則用來追蹤合併的歷史操作。

**關鍵業務規則**：
- 合併站台必須提供「人工合併」功能，允許管理者手動觸發站台合併操作
- 合併站台必須提供「操作紀錄」功能，用於記錄和查詢合併操作的歷史

**注意事項**：
- ⚠️ 文件內容極簡，具體的業務規則（如：人工合併的觸發條件、操作紀錄的保留時間）和技術限制均未描述
- ⚠️ 需人工確認：Figma 原型中是否包含更多未在此文件文字中提及的業務規則

---

## 技術設計類

### TCZB-1575 [GameTools]-使用者體驗調整

> Confluence 頁面 ID：32538827
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32538827)
> 摘要檔：[processed/32538827-summary.md](../../confluence/processed/32538827-summary.md)
> Confluence 最後更新：2022-03-08
> 摘要最後同步：2026-05-27

**摘要**：
這份文件記錄了 GameTools 的一系列使用者體驗改善項目，全部已在開發環境修復完成。內容涵蓋錯誤訊息顯示強化、強制合併視窗新增排序功能、瀏覽器頁籤標題跟隨頁面路由動態更新、前端攔截無效請求，以及無賠率站台顯示 Spread 時自動從已合併站台提取正確資訊。

**關鍵設計決策**：
- 錯誤訊息詳細資訊採用 hover 浮層方式展示，減少畫面雜亂
- 錯誤訊息欄文字直接替換為 ErrorList 最後一筆，確保用戶看到最新錯誤
- 排序功能直接加入強制合併比對視窗，不另開新頁面
- 頁籤標題變更透過前端 JavaScript 根據路由動態修改 document.title
- 無賠率站台的 Spread 處理邏輯：優先使用已合併站台的 Spread 資訊

**影響範圍**：
- 影響錯誤訊息顯示、強制合併、編輯聯盟隊伍等前端頁面的互動行為

---

### TCZB-1341 [GameTools]-合併賽事分割功能

> Confluence 頁面 ID：24091310
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24091310)
> 摘要檔：[processed/24091310-summary.md](../../confluence/processed/24091310-summary.md)
> Confluence 最後更新：2022-01-10
> 摘要最後同步：2026-05-27

**摘要**：
本文件描述 GameTools 前端如何透過 PriceCenterService 的 API 實現賽事分割功能。GameTools 先呼叫 GetSiteGame 取得站點賽事、在本地端過濾後，再呼叫 SplitSiteGame 執行分割。文中定義了 API 端點 /pricecenter/api/split/sitegame/{gameType} 及其必要參數。

**關鍵設計決策**：
- 採用兩階段操作：先從 PriceCenterService 取得賽事清單，前端過濾後再呼叫同一服務的分割 API，維持 PriceCenterService 的職責單一與前端控制過濾邏輯

**影響範圍**：
- 影響 pricecenterservice 的 API 設計和 gametools 的賽事分割流程

**注意事項**：
- ⚠️ API 參數拼寫有疑慮（如 sitelid、sitegid），可能正確應為 siteId 或 siteGroupId，需原始碼確認
- ⚠️ 標題提到「合併賽事分割」，但內容僅有分割，合併部分可能在其他文件或未描述

---

### TCZB-2386 [GameTools] - 編輯賽事、編輯原始賽事

> Confluence 頁面 ID：44663929
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44663929)
> 摘要檔：[processed/44663929-summary.md](../../confluence/processed/44663929-summary.md)
> Confluence 最後更新：2022-12-30
> 摘要最後同步：2026-05-27

**摘要**：
本文件記錄了將舊站台的「編輯賽事」與「編輯原始賽事」功能遷移至新站台 (GameTools) 的 API 規格。編輯賽事用於管理已合併的賽事資料，包含取得列表、解除合併、編輯賽事內容與查看合併來源資訊；編輯原始賽事則處理合併前的原始第三方賽事資料。

**關鍵設計決策**：
- 將舊站台功能遷移至新站台 GameTools，統一管理編輯賽事與編輯原始賽事
- 編輯賽事 API 使用 /backend/games/{gameType} 路徑，以 gameType 區分不同球種
- 編輯原始賽事 API 使用 /backend/sitegames/{gameType} 路徑，用 sitegames 區分第三方來源賽事
- 解除合併操作在編輯賽事使用 DELETE 方法，在編輯原始賽事使用 PUT 方法，兩者行為不同需注意

**影響範圍**：
- 影響 mergesite 服務的 API 設計和 GameTools 前端賽事管理頁面

---

### TCZB-3075 [GameTools] - 聯盟合併檢查功能/聯盟鎖定功能

> Confluence 頁面 ID：55575882
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55575882)
> 摘要檔：[processed/55575882-summary.md](../../confluence/processed/55575882-summary.md)
> Confluence 最後更新：2023-12-18
> 摘要最後同步：2026-05-27

**摘要**：
本文件說明了 GameTools 中合併站台新增的兩個功能：聯盟合併檢查及聯盟鎖定。提供了 4 個 API 的規格：查詢聯盟列表（含鎖定狀態）、鎖定聯盟、查詢合併檢查清單、人工標記檢查結果。

**關鍵設計決策**：
- 聯盟鎖定狀態 locked 為 0（未鎖定）或 1（已鎖定）
- 合併檢查結果 status 為 1（正確）或 2（錯誤）
- 聯盟鎖定 API：PUT backend/merge/league/locked/{gameType}/{lid}，無 Request Body
- 合併檢查標記 API：POST backend/automapteam/check/operator/{gameType}，Body 需傳 Site、SiteLid、Status

**影響範圍**：
- 影響 mergesite 的 API 設計和 GameTools 前端合併站台頁面

---

### TCZB-3222 [GameTools] - 賽事合併站台調整

> Confluence 頁面 ID：55578309
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55578309)
> 摘要檔：[processed/55578309-summary.md](../../confluence/processed/55578309-summary.md)
> Confluence 最後更新：2024-04-12
> 摘要最後同步：2026-05-27

**摘要**：
合併站台功能將原本調用 PriceCenterSite 與 GameSetting 的 API 改為透過 MergeSite 統一服務進行，以解決 CORS 報錯；人工合併賽事的顯示邏輯調整為只列出 swap=0 的站台，以便區分出 swap=1 的賽事。

**關鍵設計決策**：
- 合併站台相關 API 調用由 PriceCenterSite/GameSetting 轉移到 MergeSite，簡化跨域請求並降低 CORS 風險
- 人工合併賽事列表改為僅顯示 swap=0 的站台資訊，swap=1 的站台將被隱藏

**影響範圍**：
- 影響 mergesite、pricecentersite、gamesettingsite 等多個服務的 API 調用方式
- 影響 GameTools 前端賽事合併顯示邏輯

---

## 歷史決策類

### TCZB-1678 [GameTools] 使用者體驗調整

> Confluence 頁面 ID：32539699
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32539699)
> 摘要檔：[processed/32539699-summary.md](../../confluence/processed/32539699-summary.md)
> Confluence 最後更新：2022-03-24
> 摘要最後同步：2026-05-27

**決策背景**：
規劃 GameTools 賽事合併功能的多視窗作業（跨視窗資料同步）與聯盟篩選功能，以優化操作體驗。

**決策結論**：
- 多工處理採用「開新的瀏覽器畫面」模式，而非在單一視窗內切換
- 多工功能不需將中英文站台分開顯示
- 聯盟篩選功能優先實作，多工功能視使用結果再決定是否保留或調整
- 最終決定「沒有做」多視窗操作功能（原計劃的跨視窗同步功能取消或擱置）

**影響**：
- 多視窗操作功能未實作，後續開發不應假設此功能存在

---

### TCZB-2301 [GameTools] - 建置Vue3框架

> Confluence 頁面 ID：44662919
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44662919)
> 摘要檔：[processed/44662919-summary.md](../../confluence/processed/44662919-summary.md)
> Confluence 最後更新：2022-12-07
> 摘要最後同步：2026-05-27

**決策背景**：
gametools 需要技術棧升級，以改善開發體驗與效能。

**決策結論**：
- 採用 Vue3 重構 gametools，從原有框架遷移至 Vue3 生態
- 嘗試使用 Vite 取代原本的 webpack 作為建構工具
- 過水層（中間層）繼續使用 pricecentersite，不改變對接方式

**影響**：
- 定位了 gametools 的技術棧和與後端的對接方式，有助於理解模組邊界