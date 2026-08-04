# aireviewagentservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 06:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---


## 業務規範類


### AI Review Agent Sever 整合開發流程工作清單

> Confluence 頁面 ID：79471368
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471368)
> 摘要檔：[processed/79471368-summary.md](../../confluence/processed/79471368-summary.md)
> Confluence 最後更新：2026-05-25
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了一套以 AI Review Agent Server 為核心的自動化開發流程，強制在 Merge Request 時必須附帶 Plan 文件，並透過 AI 自動檢查 Plan 規範與測試涵蓋率。此外，它還規劃了如何將 Confluence 文件轉換為 aidata 知識庫的管線設計，用於協助 AI 和新人工程師更準確地理解任務。

**關鍵業務規則**：
- Merge Request 時，即使是小功能修改，也必須帶有 Plan 文件才能執行。
- Plan 文件中必須強制要求包含對應的單元測試及整合測試程式碼。
- Plan 提交後，系統需自動檢查其內容是否符合 PLAN_SPEC.md 規範。
- 當計劃提交時，應將過去犯過的錯誤結構化地儲存為 lessons-learned，供 AI 在編寫後續計劃時自動對照，避免重犯。
- 需將 DB 與 Redis 等資料源的隱性知識顯性化。當 DB schema 或 repo 更新時，自動分析並產出 db-detail.md 文件，標記各欄位語意。此文件需由資深工程師審核後才能正式採用。
- 新人工程師在訂定 Plan 之前，必須透過 AI 產出「任務理解文件」，並由資深人員審核，確保對任務有正確理解（此項功能需等待 DB 隱性知識顯性化完成後才能實施）。

**注意事項**：
- ⚠️ 多數任務狀態為「進行中」或「完成待驗證」，可能尚未全面實作或穩定，需人工確認當前進度。
- ⚠️ 「任務理解文件」的實施存在相依性，需等待 DB 顯性化功能完成。
- ⚠️ 部分流程提及需人工搬運或審核，非全自動化。


### AI Review Server 完整開發計畫

> Confluence 頁面 ID：79471262
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471262)
> 摘要檔：[processed/79471262-summary.md](../../confluence/processed/79471262-summary.md)
> Confluence 最後更新：2026-05-05
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件為 AI Review Server 的完整技術開發計畫，定義了服務如何接收 GitLab 的 Push 和 Merge Request Webhook，並自動化地對程式碼和 Plan 文件進行 AI 審查。審查結果會寫入 PostgreSQL，並在發現嚴重問題時通知 Rocket.Chat 及回寫評論到 GitLab MR。文件明確將 AI 審查定位為顧問性質，絕不阻擋或延遲既有的 CI/CD 流程。

**關鍵業務規則**：
- AI Review 的結果僅為顧問性質，不阻擋、不延遲、不控制 Jenkins 的打包或部署流程。即使 AI 驗證失敗或服務不可用，發版是否繼續完全由人工判斷。
- Push Webhook 會觸發所有分支的審查。
- Merge Request Webhook 僅處理 `open`、`update`、`reopen` 這三種 action，其餘如 `merge`、`close` 僅記錄日誌。
- 同一 `project_key + commit_sha + event_type` 的重複 Webhook 由 PostgreSQL 的唯一約束防止重複處理。
- Push 審查為輕量檢查，僅檢查 `_plans/` 目錄的變更。即使該目錄無變更，仍需建立審查事件。
- MR 審查為完整檢查，會建立 code 與 plan 兩筆審查運行紀錄。
- 通知規則：僅當審查結果為 fail（且包含 `critical` / `high` 等級問題）時，才透過 Rocket.Chat 通知。同一目標 24 小時內不重複通知。
- AI 回應的 JSON Schema 必須通過驗證，其中 `review_type`、`summary`、`issues` 為必填欄位，issue 的 `severity` 僅允許 `low/medium/high/critical`。
- 當程式碼差異過大時，系統會分批呼叫 AI 審查再合併結果，合併時會根據特定維度去重，若衝突則取最高嚴重等級。

**注意事項**：
- ⚠️ 所有 API Key / Token / 密碼以明文直接寫入各環境的 appsettings 設定檔中，此風險雖在內部情境可接受，但仍需注意。


### AI Review Server Upgrade1 計畫

> Confluence 頁面 ID：79471548
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471548)
> 摘要檔：[processed/79471548-summary.md](../../confluence/processed/79471548-summary.md)
> Confluence 最後更新：2026-05-15
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件為 AI Review Server 的升級計畫，核心是擴展 Plan Review 功能，並引入語言感知的規則載入機制，讓 C# 和 Python 專案能使用各自專屬的審查規則。同時，它也加入了 Git 帳號追溯與多供應商 AI 備援機制，以提升系統的強健性與可追溯性。

**關鍵業務規則**：
- Plan Review 僅檢查 `_plans/` 目錄下第一層的 `*.md` 檔案，明確排除所有子目錄（如 `_plans/_reference/`）及非 `.md` 檔案。
- Plan Review 的審查規則輸入，必須是通用規範（`general.mdc`）與 `PLAN_SPEC.md` 中「Commit 前檢查規範」區塊的合併結果，而非整份文件。
- 程式碼審查（Code Review）的規則輸入，必須以 `general.mdc` 為基底，然後再拼接語言專屬規則（如 C# 的 `csharp/.cursor_rules`）。
- 若一次 Push/MR 事件中變更的檔案同時包含 `.cs` 和 `.py`，此事件不觸發 AI 審查，僅記錄 Kafka 日誌。
- 分流後若既無程式碼也無 Plan 變更，該審查事件的狀態需結案為 `completed`，但不產生審查運行紀錄，也不發送任何通知。
- 每次 AI 審查完成後，資料庫、Kafka 和通知中必須能追溯到本次所使用的規範來源清單。
- 觸發審查的 Git 帳號必須被記錄，Push 事件取 `user_username`，MR 事件取 `user.username`。
- 多供應商 AI 備援機制：依設定檔陣列順序嘗試，單一端點內失敗後會重試最多 `MaxRetries` 次，才切換至下一個端點。
- AI 回應必須包含 `status`（pass/fail）和 `unresolved_count` 欄位，並通過 Schema 驗證。

**注意事項**：
- ⚠️ `generalrules/.cursor/rules/general.mdc` 必須是相對於 aidata git 倉庫根目錄的完整路徑，而非 `templates/` 下的舊路徑，此處容易搞錯。
- ⚠️ 多供應商備援中的語言改寫重試（zh-TW rewrite），其使用的 AI 供應商/模型必須對齊主審查任務首次成功回應所使用的端點，而非獨立於備援邏輯之外。


### AI Review Server Upgrade2 計畫

> Confluence 頁面 ID：79471550
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471550)
> 摘要檔：[processed/79471550-summary.md](../../confluence/processed/79471550-summary.md)
> Confluence 最後更新：2026-05-15
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件規劃為 AI Review Server 新增兩個背景服務：`ReadmeCatalogSync` 和 `AidataSwaggerSync`。它們會透過獨立的 Portainer 實例發現運行中的服務，並依據 PostgreSQL mapping 表自動從 GitLab 克隆倉庫、產生 README 文件，或取得 OpenAPI 快照，最後將結果提交到 aidata 規則庫。

**關鍵業務規則**：
- Mapping 表中的兩個時間戳 `ReadmeCatalogSyncLastCheckUtc` 和 `AidataSwaggerSyncLastCheckUtc` 分別由各自的 Worker 獨立更新。
- 當 GitLab 預設分支沒有新的 commit 時，不執行 AI 產生 README，但仍視為同步成功並更新時間戳。
- Swagger 同步時，即使取得的 JSON 內容與 aidata 中現有檔案相同，仍視為成功並更新時間戳；但若 HTTP 請求失敗，則不更新時間戳。
- 兩個 Worker 寫入 aidata 的路徑需嚴格分開，`ReadmeCatalogSync` 僅寫入 `*/*.md`，`AidataSwaggerSync` 僅寫入 `webapi/**/*.json`，且必須分兩次獨立的 commit 和 push。
- 每個邏輯服務鍵獨立進行 git add/commit/push，單個服務失敗不影響其他服務。只有在 push 成功且資料庫更新成功後，才更新對應的時間戳。

**注意事項**：
- ⚠️ 兩個 Worker 並行寫入 mapping 表時，明確不做 lost update 防護，極低機率下可能出現時間戳覆寫。
- ⚠️ Mapping 表中的主列若被刪除，關聯的 GitLab 同步會中斷且無自動恢復機制，需人工介入。

---


## 技術設計類


### AI Review Server 完整開發計畫

> Confluence 頁面 ID：79471262
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471262)
> 摘要檔：[processed/79471262-summary.md](../../confluence/processed/79471262-summary.md)
> Confluence 最後更新：2026-05-05
> 摘要最後同步：2026-05-27

**摘要**：
本文件是 AI Review Server 的技術藍圖，詳細定義了服務的架構。它採用「DB-first + Channel<T> 佇列」模式，Controller 收到 Webhook 後會先將事件寫入 PostgreSQL（狀態為 pending），再放入記憶體中的 Channel。背景的 ReviewWorker 則從 Channel 取出事件進行處理，這樣的設計確保了服務重啟後可以從資料庫中恢復未完成的工作。

**關鍵設計決策**：
-   **分層架構與框架整合**：採用 Controller / DomainService / Infrastructure 的分層架構，並與既有的 ECCore 框架整合。其中 `Infrastructure` 層的 GitLab 和 AI 提供者使用原生的 `HttpClient` 呼叫 API，而 `ReviewRepository` 則使用 ECCore 的 `IPostgreSQLManager` 操作資料庫，保持與框架的一致性。
-   **非同步佇列與並行控制**：使用 `System.Threading.Channels` 的 `BoundedChannel`（預設容量 100）作為內部佇列，並搭配 `SemaphoreSlim` 控制並行的 AI 請求數量，提供背壓機制。
-   **規則來源管理**：AI 審查規則庫採用獨立的 git clone（透過 HTTPS + Token），在每次審查前執行 `git pull` 檢查更新，其存放路徑設在 Docker Volume 中常駐。
-   **補償機制**：`ReviewCompensationWorker` 在啟動時會立即掃描 `pending`/`processing`/`failed` 狀態的事件並重新放入佇列，之後每 5 分鐘定時掃描一次。
-   **Webhook 冪等性**：依賴 PostgreSQL 的唯一索引來保證，當寫入遇到重複鍵時直接回傳 HTTP 202，不重複建立審查事件。

**影響範圍**：
-   此架構定義了服務的核心運作方式，從 Webhook 接收、任務排程、規則載入到結果回寫的整個流程都與此設計緊密相關，是開發此服務不可輕易變更的基礎。


### AI Review Server Upgrade1 計畫

> Confluence 頁面 ID：79471548
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471548)
> 摘要檔：[processed/79471548-summary.md](../../confluence/processed/79471548-summary.md)
> Confluence 最後更新：2026-05-15
> 摘要最後同步：2026-05-27

**摘要**：
此文件定義了 AI Review Server 的升級藍圖，核心是在既有的 Code Review 上增加 Plan Review 功能，並引入更複雜的規則載入邏輯。升級後，系統能根據程式碼的語言（C# 或 Python）載入對應的審查規則，並實現了多供應商備援，提升系統的可用性。

**關鍵設計決策**：
-   **語言感知規則載入**：全面棄用舊的 `LoadConsolidatedRulesAsync` 方法，改用新的 `LoadMultiLanguageRulesAsync` 方法，以支援為不同語言載入不同規則。
-   **用戶端判定 Python 框架**：Server 端不判定 Python 的框架類型（如 FastAPI 或 Flask），而是將完整的規則內容提供給 AI，由 AI 自行判斷，讓 Server 端邏輯能與框架細節解耦。
-   **通用規範基底**：引入 `generalrules/.cursor/rules/general.mdc` 作為所有審查（Code/Plan）的通用規範基底，確保所有審查線遵循一致的基礎標準。
-   **規範來源追蹤**：`review_runs.rules_version` 欄位會記錄 aidata repo 當下的 commit SHA，用於精確追溯審查時使用的規則版本，提高問題排查的複現性。
-   **語言檢核調整**：將繁體中文檢核（zh-TW）改為欄位門檻制，並取消對簡體字的嚴格禁止，避免技術術語中混用字元導致不合規誤判。

**影響範圍**：
-   這個設計直接影響了 `AIDomainService` 中規則載入的核心邏輯，以及對 AI 審查結果的 Schema 驗證。開發與維護此服務時，必須理解「規範來源全量提供 + AI 自報 + 白名單驗證」的追蹤策略。


### AI Review Server Upgrade2 計畫

> Confluence 頁面 ID：79471550
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471550)
> 摘要檔：[processed/79471550-summary.md](../../confluence/processed/79471550-summary.md)
> Confluence 最後更新：2026-05-15
> 摘要最後同步：2026-05-27

**摘要**：
這份文件規劃了為 AI Review Server 新增兩個背景服務，用於自動維護 aidata 規則庫中的服務中繼資料（README 和 OpenAPI spec）。它定義了如何以 Portainer 為權威來源發現服務，並通過 PostgreSQL mapping 表連結到 GitLab 倉庫進行操作。

**關鍵設計決策**：
-   **雙 Worker 設計**：將 README 生成（`ReadmeCatalogSync`）和 Swagger 快照（`AidataSwaggerSync`）拆分為兩個獨立的 `BackgroundService`，並透過相位偏移錯開執行時間，避免彼此爭搶資源。
-   **權威來源**：採用獨立的 Portainer 實例而非 GitLab 作為服務運行狀態的唯一權威來源，以解除與 AI Review 部署環境的耦合。
-   **資料儲存**：使用 PostgreSQL 的 `catalog.portainer_gitlab_mapping` 表儲存 Portainer 服務與 GitLab 倉庫的映射關係，並由兩個 Worker 直接更新表中不同欄位，取代舊有的 CSV 文件。
-   **寫入隔離與鎖定**：兩個 Worker 寫入 aidata 的路徑嚴格分開，確保檔案不會互相覆蓋。同時，它們會複用 `RuleProvider` 的內部鎖定機制來進行 pull/commit/push，保證與規則載入的互斥。

**影響範圍**：
-   這項設計將在 `aireviewagentservice` 中引入兩個新的 `BackgroundService`，它們依賴新的 `portainer_gitlab_mapping` 資料表。服務的穩定運行將依賴 Portainer 和該 Mapping 表的正確設定。


### 建立 AIReviewAgentService

> Confluence 頁面 ID：79471221
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471221)
> 摘要檔：[processed/79471221-summary.md](../../confluence/processed/79471221-summary.md)
> Confluence 最後更新：2026-05-06
> 摘要最後同步：2026-05-26

**摘要**：
此文件記錄了 AIReviewAgentService 的創建過程與初期經驗。專案的目標是用 .NET 建立 Web API，透過 AI 進行 Code Review，並將結果存入 PostgreSQL 和發送到 Rocket.Chat。

**關鍵設計決策**：
-   在開發過程中，採用多個 AI 模型（Claude、Deepseek、Cursor）互動地提交和審查 Plan，直到所有模型都認為沒有關鍵問題，以此方式提高 AI Code Review 流程的可靠性。
-   這份文件也總結了一個重要的經驗教訓：在全新、無現有程式碼可參考的專案中，AI 極度依賴 `.cursor_rules` 的指引。因此，必須制定比既有專案更精細、更明確的規則，才能防止 AI 的產出偏離預期。

**影響範圍**：
-   這是關於此服務最早的決策和經驗記錄，其「多模型互動」的開發方法以及「新專案需更詳細規則」的經驗，對後續所有開發計畫都有指導意義。

---


## 歷史決策類


### 建立 AIReviewAgentService

> Confluence 頁面 ID：79471221
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471221)
> 摘要檔：[processed/79471221-summary.md](../../confluence/processed/79471221-summary.md)
> Confluence 最後更新：2026-05-06
> 摘要最後同步：2026-05-26

**決策背景**：
當時的目標是創建一個全新的 .NET Web API 服務，用於整合 GitLab，實現自動化的 AI Code Review。這是一個從零開始的專案，沒有任何既有的程式碼或架構可以參考。

**決策結論**：
決定採用多 AI 模型（Claude, Deepseek, Cursor）互動的方式來制定開發計畫，直到所有模型達成共識。這個決策是為了在全新領域中，最大限度地降低由單一 AI 模型可能導致的設計錯誤或偏差。

**影響**：
這個初期決策及其總結的經驗（新專案需要更精細的 `.cursor_rules` 來引導 AI）直接影響了後續整個專案的開發模式和規則建立策略。這是一項重要的歷史記錄，解釋了為何此專案對規則的依賴性極高。

---


## 操作手冊類


### 使用 AI 同時修改前後端程式

> Confluence 頁面 ID：79471746
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471746)
> 摘要檔：[processed/79471746-summary.md](../../confluence/processed/79471746-summary.md)
> Confluence 最後更新：2026-05-19
> 摘要最後同步：2026-05-26

**摘要**：
這份文件提供了一個操作指引，說明如何使用 Cursor 同時開啟 `aireviewagentservice` 後端與 `reviewfrontendtools` 前端專案，進行 API 與前端的同步開發。

**AI 開發需要注意的部分**：
-   當同時開發前後端時，Plan 文件需要自行決定要放置在前端還是後端的專案中。如果沒有事先規劃好，可能會因為 AI 或開發者只關注其中一個專案，而遺漏了對新增 API 接口的記錄或發現。
-   Specstory 記錄只會保存在主要的工作區專案中，同時開發會導致前後端的操作歷程被混合記錄在同一個檔案裡，這可能會讓未來的回顧和追蹤變得混亂。在設計自動化流程時，需要考量到此限制。