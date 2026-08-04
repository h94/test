# 語言規範套用原則

處理任何檔案前，先判斷語言類型，只讀取對應規範，不需要全部載入。

---

## Code 修改前 Branch Gate（硬規則）

修改任何 code 前，必須先確認目標檔案所屬 repo 的目前分支。

適用範圍：
- C# / Python / Frontend / scripts / tests / config 等會影響程式行為的檔案
- multi-root workspace 必須以實際要修改的檔案判定 repo root，不可只看 aidata repo

判斷流程：
1. 取得目前分支：`git rev-parse --abbrev-ref HEAD`
2. 若目前分支不是 `main` / `master`：
   - 視為已在工作分支，不需要檢查其他分支，可繼續修改 code。
3. 若目前分支是 `main` / `master`：
   - 先檢查本機分支：`git branch --format="%(refname:short)"` 與 `git branch -r --format="%(refname:short)"`
4. 若本機已看到其他分支：
   - **擋下，不得修改 code。**
   - 詢問 user 是否要切換到既有分支。
   - 不需要再查 GitLab / remote。
5. 若本機只看到 `main` / `master`：
   - 再查 GitLab / remote：`git ls-remote --heads origin`
6. 若 remote 也沒有其他分支：
   - **通過，可修改 code。**
   - 但需提醒 user：目前 local / remote 都只看到主線，將直接在主線修改。
7. 若 remote 有其他分支：
   - **擋下，不得修改 code。**
   - 詢問 user 是否要 fetch / checkout 既有分支。

其他分支判定：
- 不算其他分支：`main`、`master`、`origin/main`、`origin/master`、`origin/HEAD`
- 算其他分支：任何其他 local branch 或 remote branch，例如 `origin/dev`、`origin/feature/*`、`origin/release/*`

禁止事項：
- 禁止在 `main` / `master` 且 local 或 remote 存在其他分支時直接修改 code
- 禁止自行切換分支
- 禁止自行建立新分支
- 禁止只檢查 aidata repo，而忽略實際要修改 code 的 repo

---

## C#

### 1. 判定 Service Kind（C# 專案 — 最先執行）

在讀取 C# 規範或修改 Controller / appsettings 前，**先判定 kind**，再載入對應 `service-kind-*.mdc`。

| 優先序 | 判定方式 | kind | 載入規則 |
|--------|----------|------|----------|
| 1 | 查 `./aidata/webapi/_index.md` 或 `./aidata/service/_index.md` 的 **kind** 欄 | `atomic` / `integration` / `service` | 見下表 |
| 2 | Repo 列於 `service/_index.md`、且任務為 Worker / 背景排程（無 Controller 任務） | `service` | `service-kind-background.mdc` |
| 3 | 有 `*Controller.cs` 或 WebAPI 特徵 + `appsettings` 含 `MySQLSettings` / `CassandraSettings` / `PostgreSQLSettings` | `atomic` | `service-kind-atomic.mdc` |
| 4 | 有 Controller + `appsettings` 僅 `RestfulSettings.Gateway`（無上述 DB Settings） | `integration` | `service-kind-integration.mdc` |
| 5 | 無法判定 | — | **先詢問使用者**，不可假設 |

**kind → 規則檔**

| kind | 規則檔 |
|------|--------|
| `atomic` | `./aidata/csharp/rules/service-kind-atomic.mdc` |
| `integration` | `./aidata/csharp/rules/service-kind-integration.mdc` |
| `service` | `./aidata/csharp/rules/service-kind-background.mdc` |

**硬規則**：未判定 kind 前，不得新增 Controller Route 或 AppSettings 的 DB / Restful 區塊。

### 2. 載入共用 C# 規範

- 完整 C# 規範見 `./aidata/csharp/.cursor_rules`；編輯 `.cs` / `.csproj` 時由 `./aidata/generalrules/.cursor/rules/csharp.mdc` glob 自動觸發載入
- **命名**（method / field / route）以 `./aidata/csharp/rules/naming.mdc` 為準；新寫 code 不得沿用同檔案 legacy PascalCase private method（詳見 `.cursor_rules` Priority Order）
- 使用 **ECCore**、**ECFramework**（`EDASFramework`、`ECServiceStartup`、`[DependencyInjection]`、managers、`IKafkaLogger` 等）或大倉 **`demo/DemoService`** 範式時，**必讀** `./aidata/csharp/ECGuide.md`
- 若出現 ASP.NET Core WebAPI 特徵（`Controller`、`[HttpGet]`、`[FromBody]`、`*Request.cs`、`*Response.cs`），**必須**一併套用 `./aidata/csharp/rules/swagger.mdc`，產出 Swagger 文件（Input/Output `<summary>`、nullable 語意標記；Model 禁止 Data Annotation）

> 📌 效能規範：涉及 DB 查詢、外部 HTTP 呼叫或大量迴圈處理時，另參考 `./aidata/performance-rules.md`。

---

## Python WebAPI（先判斷框架）

- 出現 FastAPI 特徵（`from fastapi import FastAPI`、`APIRouter`、`Depends`）→ 讀 `./aidata/python/webapi/.cursor/rules/fastapi-webapi-rule.mdc`
- 出現 Flask 特徵（`from flask import Flask`、`Blueprint`、`flask_restful`）→ 讀 `./aidata/python/webapi/.cursor/rules/flask-webapi-rule.mdc`
- 同時存在兩種特徵 → 以目前正在修改的檔案所屬模組為準
- 無法判斷 → 先詢問使用者，不可自行假設

> 📌 效能規範：涉及 DB 查詢、外部 HTTP 呼叫時，另參考 `./aidata/performance-rules.md`。

---

## Python 爬蟲（WebAPI 不適用時，優先於 Service）

### 專案類型（依專案或 Repo 名稱）

| 類型 | 命名模式 | 範例 |
|---|---|---|
| **Provider** | 以 `Provider` 或 `ProviderV2` 結尾 | `SBOProvider`、`MCProviderV2` |
| **Parser** | 以 `CrawlerAgent` 開頭 | `CrawlerAgentMc`、`CrawlerAgentMcV2` |

- 名稱不符合且無法判斷 → 先詢問使用者，不可自行假設

### 規則載入（`./aidata/python/crawler/.cursor/rules/`）

掃描目錄內所有 `.mdc`，依規則檔標示篩選後載入：

| 規則標示 | 載入對象 |
|---|---|
| 標示 **Provider**（於 `description`、frontmatter 或「適用範圍」） | 僅 Provider 專案 |
| 標示 **Parser** | 僅 Parser（CrawlerAgent）專案 |
| 兩者皆未標示 | Provider 與 Parser 皆載入 |

- 不可載入與當前專案類型不符的爬蟲規則

---

## Python Service（WebAPI、爬蟲皆不適用時）

- 出現非同步特徵（`asyncio`、`async def run(...)`、`await`、`asyncio.create_task(...)`）→ 優先讀 `./aidata/python/service/.cursor/rules/async-service-rule.mdc`
- 未出現非同步特徵，且出現同步特徵（`project/Tasks.py`、`threading.Thread(...)`、`def run(self)`、`time.sleep(...)`）→ 讀 `./aidata/python/service/.cursor/rules/service-rule.mdc`
- `import threading` 單獨出現不視為同步判定依據
- 無法判斷 → 先詢問使用者，不可自行假設

> 📌 效能規範：涉及非同步 I/O、外部呼叫、Retry 機制時，另參考 `./aidata/performance-rules.md`。

---

## 外部參考查閱

| 任務類型 | 查閱對象 |
|---|---|
| WebAPI / Controller | `./aidata/webapi/_index.md`（**含 kind 欄**） |
| BackgroundService / Worker | `./aidata/service/_index.md`（**kind 一律 service**） |
| 前端 | `./aidata/frontend/_index.md` |
| DB 操作 | `./aidata/db/_index.md` |
