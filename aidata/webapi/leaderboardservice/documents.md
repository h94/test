# leaderboardservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：{yyyy-MM-dd HH:mm}
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### [球王] - APP開發（會議記錄）

> Confluence 頁面 ID：55575644
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55575644)
> 摘要檔：[processed/55575644-summary.md](../../confluence/processed/55575644-summary.md)
> Confluence 最後更新：2023-12-01
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此為 Sprint 139 的開發進度同步記錄，涵蓋球王 App 共 17 個功能模組的完成狀態。文件中界定多項與「高手榜」（排行榜）相關的關鍵業務規則，包括 API 拆分策略、UI 顯示格式、排序邏輯與設定連動等，對 AI 開發排行榜相關功能模組尤為重要。

**關鍵業務規則**：
- 個人預測頁的今日推薦與歷史推薦需拆分成兩支獨立的 API
- 高手榜前三名下方需新增「看預測」按鈕
- 高手榜獲利點數需加上千位分隔符號
- 個人預測頁關注人數右側需新增莊殺圖示
- 個人預測頁（查看自己）需在今日推薦/歷史推薦按鈕左側新增本期莊殺標準顯示
- 賽事排序規則：聯盟排序為 已收藏賽事（聯盟名稱＞開賽時間）→ 熱門聯盟（聯盟名稱＞開賽時間）→ 普通聯盟（聯盟名稱＞開賽時間）
- 賽事排序規則：時間排序為 已收藏賽事（聯盟名稱＞開賽時間）→ 熱門聯盟（聯盟名稱＞開賽時間）→ 普通聯盟（開賽時間）
- 設定頁面需提供切換顯示賠率的功能

**注意事項**：
- ⚠️ 文件為 Sprint 進行中的進度記錄，非最終規格文件，部分功能可能後續有變更
- ⚠️ 文件日期為 2023-12-01，距今已有一段時間，需人工確認目前實際開發進度與此記錄是否一致

### TCZB-1903 [排行榜] 排行榜APIService

> Confluence 頁面 ID：36995487
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=36995487)
> 摘要檔：[processed/36995487-summary.md](../../confluence/processed/36995487-summary.md)
> Confluence 最後更新：2022-06-27
> 摘要最後同步：2026-05-27

**摘要**：
此文件定義了排行榜服務的核心業務規範，包括 REST API、資料模型與資料庫結構。它規範了排行榜的新增、設定、內容管理、自動刷新機制與使用者帳號管理等完整業務流程，是實現排行榜後端功能的基礎業務文件。

**關鍵業務規則**：
- 自動刷新排行榜 API 請求由 xxl-job 排程控制，每 10 分鐘執行一次
- 資料來源為 API 時，UrlPath 欄位必填
- 資料來源為 API 且 FlashTime 設為 0 時，不執行自動刷新
- ReloadTime 設為 0 時，前端不自動刷新畫面
- 排行榜使用者帳號密碼長度限制為 6~12 位英數字元及符號
- 排行榜內容格式為 JSON 陣列，每筆包含 Rank（目前排名）、BeforeRank（上次排名）、Name、Total 等欄位
- 使用者角色 Rank：1 為管理帳號，2 為公司帳號
- 更新排行榜內容時需提供 LastUpdater 欄位
- 排行榜 Token 為字串，長度最大 10 字元，作為唯一識別

**注意事項**：
- ⚠️ 文件最後更新於 2022-06-27，可能已有後續變更，需確認目前排行榜服務是否仍遵循相同 API 與模型
- ⚠️ 與《[球王] - APP開發》中的「高手榜獲利點數需加上千位分隔符號」規則需一併考慮顯示格式

### TCZB-1905 [排行榜]-前台Embeded JS

> Confluence 頁面 ID：36995500
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=36995500)
> 摘要檔：[processed/36995500-summary.md](../../confluence/processed/36995500-summary.md)
> Confluence 最後更新：2022-06-22
> 摘要最後同步：2026-05-27

**摘要**：
此文件說明排行榜前台嵌入 JS 的整合方案，規範了兩種渲染觸發模式（自動/手動），以及由 API 返回已組裝 HTML 與 CSS 的前端整合業務規則，簡化了第三方網站的排行榜嵌入流程。

**關鍵業務規則**：
- 引入腳本時可傳 idToToken 參數觸發預渲染，否則需手動調用函數渲染
- API 返回已組裝的 HTML 與 CSS，前端無需自行拼裝

**注意事項**：
- ⚠️ 文件中測試地址為內部環境，可能已失效
- ⚠️ 樣式示例僅以 GIF 展示，缺乏具體的 CSS 或 DOM 結構說明

---

## 技術設計類

### TCZB-1903 [排行榜] 排行榜APIService

> Confluence 頁面 ID：36995487
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=36995487)
> 摘要檔：[processed/36995487-summary.md](../../confluence/processed/36995487-summary.md)
> Confluence 最後更新：2022-06-27
> 摘要最後同步：2026-05-27

**摘要**：
此為排行榜服務的核心技術設計文件，定義了完整的 REST API、資料模型、資料庫結構與自動刷新機制。包含透過 MemberService 管理使用者帳號、支援檔案上傳與 API 兩種資料來源、xxl-job 排程控制的自動刷新邏輯等技術實現方案。

**關鍵設計決策**：
- 自動刷新採用 xxl-job 排程，週期設定為 10 分鐘，解耦前端與資料更新邏輯
- 排行榜資料來源設計為可切換（檔案上傳/API），透過 DataSource 欄位區分，並以 UrlPath 輔助 API 模式
- 獨立 NuGet 套件 LeaderboardModels 及擴充 MemberModels，將資料模型與服務分離，便於跨服務共用
- FlashTime 欄位控制自動刷新時間，並記錄 PreFlashTime 上次刷新時間，以比對是否需要更新內容
- 模板系統透過 EditClass 與 DefaultClass 提供可客製化樣式，支援 CSS 動畫清單獨立管理

**影響範圍**：
- 涉及 leaderboardservice 與 memberservice 的跨服務整合
- 依賴 xxl-job 排程系統的正確配置

### TCZB-1905 [排行榜]-前台Embeded JS

> Confluence 頁面 ID：36995500
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=36995500)
> 摘要檔：[processed/36995500-summary.md](../../confluence/processed/36995500-summary.md)
> Confluence 最後更新：2022-06-22
> 摘要最後同步：2026-05-27

**摘要**：
說明排行榜前台嵌入 JS 的技術實現方案，包含自動渲染與手動渲染兩種模式，以及由 API 返回已組裝 HTML 與 CSS 的前端整合技術設計。

**關鍵設計決策**：
- 采用两种渲染模式：通过 script 标签中 idToToken 参数触发预先渲染；未传参数时通过函数调用按需渲染
- 由 API 返回已组装好的 HTML 和 CSS，避免前端自行拼装，降低集成复杂度
- idToToken 为非必填参数，用于决定是否需要对指定元素自动渲染

**影響範圍**：
- 影響排行榜服務與前端站台（leaderboardfrontendsite）的整合方式
- API 需負責 HTML 與 CSS 的組裝邏輯

### [球王] - APP開發（技術相關）

> Confluence 頁面 ID：55575644
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55575644)
> 摘要檔：[processed/55575644-summary.md](../../confluence/processed/55575644-summary.md)
> Confluence 最後更新：2023-12-01
> 摘要最後同步：2026-05-27

**摘要**：
此會議記錄中包含多項技術設計決策，特別是高手榜相關的 API 拆分策略與設定頁排序連動邏輯。

**關鍵設計決策**：
- 個人預測的今日推薦與歷史推薦拆分為兩支 API，而非單一 API 用參數區分，推測是為了效能或前端獨立渲染考量
- 設定頁的賽事排序與首頁賽事排序連動，排序邏輯依賴設定頁的選項

**影響範圍**：
- 影響 leaderboardservice 的 API 設計與 gamesettingservice 的整合

---

## 注意事項

- ⚠️ 部分文件時效性需確認：《TCZB-1903》最後更新於 2022-06-27、《TCZB-1905》更新於 2022-06-22，可能已有後續變更
- ⚠️ 《[球王] - APP開發》為會議記錄性質，非最終規格，其中提到的功能實現狀態需人工確認
- ⚠️ 文件之間的業務規則可能存在演進關係，例如排行榜顯示格式從基礎 JSON 結構（36995487）到歷次會議中新增的千位分隔符號等 UI 需求（55575644）