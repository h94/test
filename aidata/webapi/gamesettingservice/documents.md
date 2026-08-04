# gamesettingservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 12:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### 高爾夫球 玩法站台配置

> Confluence 頁面 ID：79465287
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465287)
> 摘要檔：[processed/79465287-summary.md](../../confluence/processed/79465287-summary.md)
> Confluence 最後更新：2025-11-04
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了高爾夫球賽前階段的兩種玩法（HA 與 Winner）所適用的站台。HA 玩法僅在 bc.com 站台提供；Winner 玩法雖配置在 bc.com 及 napoleon 站台，但目前標註為不使用。此資訊可供開發 gamesettingservice 時確認站台對玩法的支援邏輯，避免錯誤開放未啟用的玩法。

**關鍵業務規則**：
- 高爾夫球賽前 HA 玩法僅支援 bc.com 站台。
- 高爾夫球賽前 Winner 玩法的配置涵蓋 bc.com 與 napoleon 站台，但狀態為「不使用」（實際應視為未啟用，開發時需排除或隱藏）。

**注意事項**：
- ⚠️ Winner 玩法雖然列出了支援站台，但 Memo 欄位註記「不使用」，實際行為需人工確認（可能是已廢棄或尚未開放的玩法）。
- ⚠️ 文件僅列出「賽前」階段的玩法，未涵蓋賽中或其他階段的配置，可能有缺失。

### TCZB-3867 [GS營運版] - 設定值設定/賽事查詢

> Confluence 頁面 ID：79463894
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463894)
> 摘要檔：[processed/79463894-summary.md](../../confluence/processed/79463894-summary.md)
> Confluence 最後更新：2025-08-22
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這是一份前端重構的業務需求文件，定義了 GS 營運版中「設定值設定/賽事查詢」相關頁面的名稱變更與側邊欄排序調整。

**關鍵業務規則**：
- 頁面名稱變更：'範本設定值維護' 更名為 '賽事設定值維護-設定值'。
- 側邊欄排序調整：'聯盟設定值維護-設定值' 排序高於 '聯盟設定值維護-聯盟'（即設定值在前，聯盟在後）。

**注意事項**：
- ⚠️ 文件中缺少文字說明，主要內容依賴截圖對比，若截圖無法載入將遺失大量資訊。

### TCZB-3918[GS營運版] - 會員系統 / 賽事查詢系統

> Confluence 頁面 ID：79464656
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464656)
> 摘要檔：[processed/79464656-summary.md](../../confluence/processed/79464656-summary.md)
> Confluence 最後更新：2025-09-17
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這是一份 GS 營運版專案（InplayZ）的啟動需求文件，說明了從既有 GameSettingFrontEndTools 繼承後的變更範圍。

**關鍵業務規則**：
- 會員登入頁需新增「公司代號」欄位，作為登入必要資訊。
- 會員需新增「公司代號」與「角色」屬性，角色固定分為 admin 與 trader。
- 當任何 API 返回 Error: Login information does not exist 時，系統必須清除登入資料並強制登出使用者。
- 球種與玩法選項必須根據當前帳號的訂閱內容動態過濾顯示。

**注意事項**：
- ⚠️ 文件為需求規格，非最終實作細節。

### TCZB-4006 [GS營運版] - 商務賽事及時賠率對比

> Confluence 頁面 ID：79465556
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465556)
> 摘要檔：[processed/79465556-summary.md](../../confluence/processed/79465556-summary.md)
> Confluence 最後更新：2025-10-21
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義在 GS 營運版及時賠率頁面新增各站台賠率對比彈窗的功能需求。

**關鍵業務規則**：
- 彈窗從畫面右邊緣滑出，大小為頁面內容全高全寬。
- PreGame 狀態下，賠率資料每 30 秒刷新一次；Inplay 狀態下，每 5 秒刷新一次。

**注意事項**：
- ⚠️ 文件中「使用者互動設計」表格的 Method、Route、Parameter、Response 欄位皆為空白。

---

## 技術設計類

### GameSettingService DB Table

> Confluence 頁面 ID：24088937
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/GameSettingService+DB+Table)
> 摘要檔：[processed/24088937-summary.md](../../confluence/processed/24088937-summary.md)
> Confluence 最後更新：2022-01-17
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件描述了 gamesettings 資料庫中的主要資料表結構。

**關鍵設計決策**：
- 多數設定表採用 company + gametype 作為業務鍵，支援多租戶與多遊戲類型隔離。
- logs 表記錄每次設定變更的前後值 (before/after)，用於審計追溯。

**注意事項**：
- ⚠️ 文件最後更新於 2022-01-17，須確認目前資料庫結構是否有異動或新增欄位。
- ⚠️ settings 欄位型別為 text，實際內容應為結構化格式（如 JSON）。

### GameSettingService 時序圖

> Confluence 頁面 ID：24090243
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24090243)
> 摘要檔：[processed/24090243-summary.md](../../confluence/processed/24090243-summary.md)
> Confluence 最後更新：2021-12-24
> 摘要最後同步：2026-05-26

**摘要**：
本文件以兩張時序圖展示 GameSettingService 中「停止使用站台」的兩個流程。

**關鍵設計決策**：
- 採用分層架構：前端的 GameSettingFrontEndSite 不直接調用 GameSettingService，而是透過 GameSettingSite 作為中間層進行請求轉發與集中控制。

**注意事項**：
- ⚠️ 文件最後更新於 2021-12-24，距今較久，需確認流程或介接方式是否已變更。

### TCZB-3868 [GameSettingService] - 營運版商務號設定

> Confluence 頁面 ID：79463634
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463634)
> 摘要檔：[processed/79463634-summary.md](../../confluence/processed/79463634-summary.md)
> Confluence 最後更新：2025-09-01
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義 GameSettingService 中「營運版商務號」的完整功能設計。

**關鍵設計決策**：
- 營運版商務號與既有 GS 訂閱者分離，獨立命名為「商務號」。
- Redis Key 組合使用底線分隔的五段式結構，便於依維度查詢與清理。

**注意事項**：
- ⚠️ 更新商務號帳號密碼 API 的 Request Body 僅含新密碼，未見舊密碼驗證或雙重確認機制。

### TZCB-1291 [GameSettingService]-賽事設定站台功能API

> Confluence 頁面 ID：24089024
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24089024)
> 摘要檔：[processed/24089024-summary.md](../../confluence/processed/24089024-summary.md)
> Confluence 最後更新：2021-12-22
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義 GameSettingService 的完整 REST API 規格。

**關鍵設計決策**：
- 設定值分為 System / League / Template / Game 四個層級，形成繼承覆寫的階層結構。
- SystemSettings 的 Settings 欄位以 List<PlayModeSettings> 設計。

**注意事項**：
- ⚠️ 文件最後更新於 2021-12-22，距今已超過 2 年，API 路由或資料結構可能已有變更。

### TCZB-3952 [GameSettingSite] - 營運版設定值配置API

> Confluence 頁面 ID：79464938
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464938)
> 摘要檔：[processed/79464938-summary.md](../../confluence/processed/79464938-summary.md)
> Confluence 最後更新：2025-09-30
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了一組用於營運版後台管理商務號（business）設定值的 RESTful API，共 26 個端點。

**關鍵設計決策**：
- 新增獨立的營運版設定值 API，與舊有設定機制作區隔，避免互相干擾。

**注意事項**：
- ⚠️ 文件中部分 response body 標記「使用者互動設計 => 設定值輸出格式」。

---

## 歷史決策類

### Issue List

> Confluence 頁面 ID：24089965
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Issue+List)
> 摘要檔：[processed/24089965-summary.md](../../confluence/processed/24089965-summary.md)
> Confluence 最後更新：2022-01-10
> 摘要最後同步：2026-05-27

**決策背景**：
這份 Sprint 39 的 Issue 列表記錄了賽事設定相關功能的多項修正與調整。

**決策結論**：
- 踢人時間從原設定延長至3小時（Issue #2）。
- 聯盟、範本、賽事設定值的 Grid 改為前端排序（Issue #7）。

**影響**：
多數修正已內化為現有系統行為，需確認現行系統是否仍適用。

---

## 操作手冊類

（目前無 operation_guide 類文件摘要）