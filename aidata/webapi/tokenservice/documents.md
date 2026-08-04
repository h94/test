# tokenservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-26 06:55
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---


## 技術設計類


### Auth(Login/Manager)Service

> Confluence 頁面 ID：5341294
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=5341294)
> 摘要檔：[processed/5341294-summary.md](../../confluence/processed/5341294-summary.md)
> Confluence 最後更新：2020-08-19
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了 Auth(Login/Manager)Service 的 API 規格與技術設計，包含 Login Service 和 Manager Service 兩部分。說明了登入、註冊、令牌刷新、帳號管理的 API 端點、請求/回應格式。對 AI 開發而言，這份文件提供了實現身份驗證與授權流程的技術細節，方便了解如何與認證服務互動，例如取得令牌、驗證令牌、管理用戶會話等。

**關鍵設計決策**：
- 採用 JWT (JSON Web Token) 作為身份驗證的令牌格式。
- 令牌透過 HTTP Header `Authorization: Bearer {token}` 傳遞。
- 設計了 RefreshToken 機制來更新過期的 AccessToken，而不是讓使用者重新登入。
- Login Service 和 Manager Service 被設計為獨立的 API 端點（例如 /api/login, /api/manager）。
- API 設計遵循 RESTful 風格。
- 文件提到了 `TokenInfo` 的格式改造（v1 到 v2），這是一項重要的技術演進，涉及 `AccessToken` 結構的變更，可能影響所有依賴此令牌的服務。（⚠️ 需要確認此改造是否已完成及實施範圍）

**影響範圍**：
- `TokenInfo` 格式改造會影響所有依賴此令牌的服務。
- 文件整體技術架構基於 ASP .Net Core 3.1。

**注意事項**：
- ⚠️ 文件最後更新於 2020-08-19，其中的技術設計與 API 端點可能已過時，需人工確認是否為現行標準。
- ⚠️ 文件提到了 `TokenInfo` 格式從 v1 到 v2 的改造，但未提供詳細的變更內容或遷移指南，這是一項潛在的破壞性變更，需要特別關注。
- ⚠️ 文中提及的具體 API 路徑（如 /api/login, /api/manager）需要在當前代碼庫中確認是否存在及功能是否一致。
- ⚠️ 本文為技術設計文件，但未見具體的業務規則、錯誤處理細節或完整的請求/回應範例，開發時需參考更詳細的 API 文件。
- ⚠️ 文件整體技術架構基於 ASP .Net Core 3.1，若現行服務已升級，則本文件僅供參考。

---