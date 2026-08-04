# GameSettingSite — 相關文件摘要

>  此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
>  最後更新：2026-05-27 00:00
>  完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類


### GameSettingSite API列表

> Confluence 頁面 ID：24089148
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24089148)
> 摘要檔：[processed/24089148-summary.md](../../confluence/processed/24089148-summary.md)
> Confluence 最後更新：2022-01-10
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件提供 GameSettingSite 服務的完整 API 列表，包含認證、設定查詢、聯盟/賽事/模板的 CRUD、站台設定與查詢等功能。每個端點標記路由、方法、參數與回應模型，並附有「賽事設定值維護」的業務規則，說明賽事、聯盟、系統三級設定的覆蓋邏輯，對 AI 開發理解 API 結構與關鍵邏輯有直接幫助。

**關鍵業務規則**：
- 查詢賽事設定值時，若無專屬賽事設定值（UseGameSetting=0）或賽事設定值已停用（UseGameSetting=1 且 Enabled=0），則回退至聯盟設定值；若仍無則回退至系統設定值。僅當賽事設定值存在且為啟用狀態（UseGameSetting=1, Enabled=1）時，才回傳賽事設定值。

**注意事項**：
- ⚠️ 文件內有「-------- 代表未完成」標記，表示部分 API 可能尚未實作，需確認目前完成狀態
- ⚠️ 部分路由參數拼寫錯誤（如 `gaemType` 應為 `gameType`），開發時須注意修正
- ⚠️ 部分 API 已標示合併（如 GetLeagueID 合併至 GetSiteLeague），實作時應檢查服務端實際路由
- ⚠️ 最後更新時間為 2022-01-10，可能已有後續變更，需對照當前服務版本確認過時資訊

---


### TCZB-3890 [GS站台vue3版本] - 及時賠率/其它/操作說明

> Confluence 頁面 ID：79464369
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464369)
> 摘要檔：[processed/79464369-summary.md](../../confluence/processed/79464369-summary.md)
> Confluence 最後更新：2025-09-05
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件描述 GS 站台（遊戲設定站台）由舊版改為 Vue3 的重構規劃，比較了及時賠率資料、登入記錄查詢、站台狀態查詢、站台警報查詢、操作說明等頁面的新舊介面。其中及時賠率頁面將搜尋欄改為篩選功能，並新增 JSON 按鈕顯示從 Hub 收到的原始賽事資料，同時在瀏覽器 console 輸出相同內容，但此功能僅限特定帳號可見。

**關鍵業務規則**：
- 及時賠率頁面的 JSON 按鈕與 console 輸出內容僅限帳號 zb666、zb999、zbadmin 可見，其他帳號無法看到這些調試資料。

**注意事項**：
- ⚠️ 本文件為 Sprint 規劃，實際實作細節可能已有變更，截圖無法查看，需人工確認最終實作結果
- ⚠️ 指定的三個帳號可能非長期有效，需確認目前環境中是否仍然使用這些帳號

---

## 技術設計類


### GameSettingSite 時序圖

> Confluence 頁面 ID：24088987
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088987)
> 摘要檔：[processed/24088987-summary.md](../../confluence/processed/24088987-summary.md)
> Confluence 最後更新：2021-12-27
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件提供了 GameSettingSite 各項 API 的時序圖，涵蓋登入、取得/更新/新增/刪除設定、移動聯盟、查詢站台設定列表等功能。前端請求皆經過 GameSettingSite 統一驗證使用者，再依任務需求呼叫 MemberService、PriceCenterService 或 GameSettingService。對於 AI 開發，能快速掌握該站台的服務依賴關係、API 呼叫鏈與主要流程設計。

**關鍵設計決策**：
- GameSettingSite 作為前端與後端服務的仲介層，統一進行使用者驗證（Validation User）後才轉發請求
- 查詢聯盟/賽事設定時，先透過 PriceCenterService 取得基礎遊戲資料（如 Search LeagueID、Games），再向 GameSettingService 請求業務設定，實現資料來源解耦

**影響範圍**：
- MoveLeague 操作依序為：取得設定、從舊設定移除聯盟、將聯盟加入新設定，分三步完成移動，非原子操作可能在中斷時產生不一致，需人工確認是否已引入交易機制

**注意事項**：
- ⚠️ 文件最後更新於 2021-12-27，可能與現行實作存在差異，建議人工比對當前程式碼
- ⚠️ 圖中缺少對異常處理（如驗證失敗、服務逾時）的描述，實際開發需額外確認

---


### GameSettingSite 流程圖

> Confluence 頁面 ID：24088995
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088995)
> 摘要檔：[processed/24088995-summary.md](../../confluence/processed/24088995-summary.md)
> Confluence 最後更新：2021-12-27
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件列出 GameSettingSite 後端 .NET 流程的主要操作步驟與相關 API 方法，如登入、取得球種/聯盟/設定值、更新設定值、停啟用站台等，可用於理解服務邊界與可能的端點定義，但未提供具體參數或設計細節，需搭配原始碼或 API 文件才完整。

**關鍵設計決策**：
- 流程採用 .NET 技術棧實作
- 將聯盟從 A 設定檔移動到 B 設定檔的操作獨立為一個步驟
- 站台操作流程包含 GetSiteLeague、GetSiteTeam、GetSiteGame 等跨站台資源查詢

**注意事項**：
- ⚠️ 文件內容僅有流程名稱與方法列表，無詳細邏輯或欄位說明，不易直接用於開發
- ⚠️ 最後更新時間為 2021-12-27，規則可能已變更
- ⚠️ 需人工確認所列 API 是否仍為最新實作

---

## 歷史決策類


### GameSettingSite API列表 (pageId=24089148)

> Confluence 頁面 ID：24089148
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24089148)
> 摘要檔：[processed/24089148-summary.md](../../confluence/processed/24089148-summary.md)
> Confluence 最後更新：2022-01-10
> 摘要最後同步：2026-05-26

**決策背景**：
GameSettingSite 需要提供統一的 API 接口來管理遊戲設定、聯盟設定、賽事設定和站台設定，支援 CRUD 操作以及進階查詢功能。

**決策結論**：
採用 RESTful API 架構，將賽事設定值維護設計為三級回退機制（賽事 → 聯盟 → 系統），確保設定值在未明確配置時能有合理的預設行為。

**影響**：
- 三級回退邏輯影響所有設定值查詢的實作方式
- API 路由可能已合併或調整（如 GetLeagueID 合併至 GetSiteLeague），需參考最新程式碼

---


### GameSettingSite 時序圖 (pageId=24088987)

> Confluence 頁面 ID：24088987
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088987)
> 摘要檔：[processed/24088987-summary.md](../../confluence/processed/24088987-summary.md)
> Confluence 最後更新：2021-12-27
> 摘要最後同步：2026-05-26

**決策背景**：
需要釐清 GameSettingSite 作為仲介層如何協調前端請求與後端多個微服務（MemberService、PriceCenterService、GameSettingService）之間的互動。

**決策結論**：
GameSettingSite 統一負責使用者驗證，並將業務邏輯分派給對應的後端服務，實現關注點分離與服務解耦。

**影響**：
- GameSettingSite 依賴三個後端服務，任何一個服務異常都會影響對應功能
- MoveLeague 的非原子操作設計可能在系統中斷時產生資料不一致風險

---


### GameSettingSite 流程圖 (pageId=24088995)

> Confluence 頁面 ID：24088995
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088995)
> 摘要檔：[processed/24088995-summary.md](../../confluence/processed/24088995-summary.md)
> Confluence 最後更新：2021-12-27
> 摘要最後同步：2026-05-26

**決策背景**：
定義 GameSettingSite 後端 .NET 流程的主要操作步驟，以標準化遊戲設定管理的操作流程。

**決策結論**：
採用步驟化的流程設計，每個操作（如登入、查詢設定、移動聯盟）都有明確的步驟序列和對應的 API 方法。

**影響**：
- 流程定義較為抽象，需搭配實際 API 文件和程式碼才能完整理解實作細節
- 文件最後更新於 2021-12-27，可能已與現行實作脫節

---


### TCZB-3890 [GS站台vue3版本] - 及時賠率/其它/操作說明 (pageId=79464369)

> Confluence 頁面 ID：79464369
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464369)
> 摘要檔：[processed/79464369-summary.md](../../confluence/processed/79464369-summary.md)
> Confluence 最後更新：2025-09-05
> 摘要最後同步：2026-05-27

**決策背景**：
GS 站台需要從舊版前端重構為 Vue3，以提升維護性和使用者體驗。

**決策結論**：
採用 Vue3 重構，同時在及時賠率頁面新增調試功能（JSON 顯示和 console 輸出），但限制僅特定高權限帳號可存取。

**影響**：
- 前端技術棧切換為 Vue3
- 權限控制邏輯需在 UI 層實作
- 指定的三個帳號（zb666、zb999、zbadmin）可能非長期有效

---

## 操作手冊類


### GameSettingSite API列表 (pageId=24089148)

> Confluence 頁面 ID：24089148
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24089148)
> 摘要檔：[processed/24089148-summary.md](../../confluence/processed/24089148-summary.md)
> Confluence 最後更新：2022-01-10
> 摘要最後同步：2026-05-26

**摘要**：
本文件提供 GameSettingSite 服務的完整 API 列表，包含認證、設定查詢、聯盟/賽事/模板的 CRUD、站台設定與查詢等功能，可用於理解服務邊界與端點定義。

**AI 開發需要注意的部分**：
- 部分路由參數拼寫錯誤（如 `gaemType` 應為 `gameType`），開發時須修正
- 部分 API 已標示合併或未完成（以「--------」表示），需對照服務端實際路由確認
- 三級設定回退邏輯（賽事 → 聯盟 → 系統）是核心業務規則，任何設定值查詢功能都必須正確實作

---


### GameSettingSite 時序圖 (pageId=24088987)

> Confluence 頁面 ID：24088987
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088987)
> 摘要檔：[processed/24088987-summary.md](../../confluence/processed/24088987-summary.md)
> Confluence 最後更新：2021-12-27
> 摘要最後同步：2026-05-26

**摘要**：
本文件提供 GameSettingSite 各項 API 的時序圖，展示前端請求如何透過 GameSettingSite 轉發到 MemberService、PriceCenterService 和 GameSettingService。

**AI 開發需要注意的部分**：
- GameSettingSite 是仲介層，所有請求必須先通過使用者驗證
- MoveLeague 操作分三步：取得設定 → 從舊設定移除 → 加入新設定，非原子操作需處理中斷恢復
- 異常處理（如驗證失敗、服務逾時）在時序圖中未描述，開發時需額外確認處理策略

---


### GameSettingSite 流程圖 (pageId=24088995)

> Confluence 頁面 ID：24088995
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088995)
> 摘要檔：[processed/24088995-summary.md](../../confluence/processed/24088995-summary.md)
> Confluence 最後更新：2021-12-27
> 摘要最後同步：2026-05-26

**摘要**：
文件列出 GameSettingSite 後端 .NET 流程的主要操作步驟與相關 API 方法，如登入、取得球種/聯盟/設定值、更新設定值、停啟用站台等。

**AI 開發需要注意的部分**：
- 文件僅有流程名稱和方法列表，缺乏詳細邏輯和欄位說明，需搭配實際程式碼和 API 文件
- 需人工確認所列 API 是否仍為最新實作，文件最後更新於 2021-12-27

---


### TCZB-3890 [GS站台vue3版本] - 及時賠率/其它/操作說明 (pageId=79464369)

> Confluence 頁面 ID：79464369
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464369)
> 摘要檔：[processed/79464369-summary.md](../../confluence/processed/79464369-summary.md)
> Confluence 最後更新：2025-09-05
> 摘要最後同步：2026-05-27

**摘要**：
本文件描述 GS 站台由舊版改為 Vue3 的重構規劃，涵蓋及時賠率資料、登入記錄查詢、站台狀態查詢、站台警報查詢、操作說明等頁面。

**AI 開發需要注意的部分**：
- 前端使用 Vue3 重構
- 及時賠率頁面新增 JSON 按鈕和 console 輸出功能，但僅限特定帳號（zb666、zb999、zbadmin）
- 本文件為 Sprint 規劃文件，實際實作可能已有變更，截圖無法查看
- 權限控制依賴使用者帳號比對

---