# Plan 規格書規範 (PLAN_SPEC)

---

## ⚡ 關鍵規則速查（AI 必讀）

| 規則 | 說明 |
|------|------|
| Phase 順序鎖定 | WebAPI: P1→P2→⛔→P3→P4；BackgroundService: P1→P2→⛔→P3→P4 |
| I/O 禁止模糊 | 禁止「Member 資料」、「回傳 DTO」等描述，必須逐欄展開 |
| POST/PUT Body | 每個欄位列出：欄位名、類型、✅必填/—選填、說明、範例值 |
| Response 欄位 | 每個端點列出：欄位名、類型、說明，並附 JSON 範例 |
| BackgroundService I/O | Input 來源＋讀取欄位＋Output 目標＋寫入欄位，全部展開 |
| 單元測試涵蓋 | Phase 3 必須列出：Happy Path、Edge Case（空值/邊界）、Error Path（例外處理） |
| 整合測試情境 | Phase 4/6 必須列出情境步驟表（呼叫/操作→預期結果），不得只寫 checkbox |
| E2E 禁止模糊 | 前端 Plan 的 E2E 規格禁止「Toast 成功」「列表刷新」等描述；須寫明按鈕文案、Toast title/message、Dialog 文案、斷言欄位 |
| E2E 與 scenario-flows 分工 | `webapi/*/scenario-flows/` 供 API/業務流程；前端 E2E 規格寫在 Plan **E2E 小節**（模板 §9.5，或 UI Spec 下同級如 §7.6）與 Phase 6，不寫入 webapi scenario-flows |
| 待確認問題 | 永遠最後一節，commit 前必須清空 ⬜/🔄 |
| Plan Gate 先於實作比對 | PR Review 時必須先檢查 Plan 本身符合本規範；Plan Gate 未通過不得用該 Plan 放行實作 |
| DB / 外部相依 | 涉及 DB 或第三方 / 內部 API 必須逐項列出；若無也要以表格明確標示「不適用」 |
| Scope Guard | 實作不得超出 In Scope 與 File List；新增未列功能需另開 Plan |
| Spec 參考文件 | §11 必填（涉及 aidata 服務時）：逐檔列出 OpenAPI `.json`、`documents.md`、跨服務 Spec；供 `@plan-executor` 讀取 |
| Step 進度檔 | `@plan-executor` 首次拆步寫入 `{repo}/_plans/logs/{PlanBasename}_steps.md`；Resume 依此檔接續 |

---

## 規範說明

### 適用 Plan 類型

| 類型 | 說明 | 典型觸發情境 |
|------|------|------------|
| `feature` | 新功能開發 | 全新頁面、API、元件 |
| `refactor` | 重構 | 解耦、改架構、命名整理 |
| `bugfix` | 問題修復 | 有明確 Bug 需要根治 |
| `tech-debt` | 技術債清理 | 測試補齊、相依升級 |

---

### 實作順序規則（強制）

AI 產出「實作步驟」時，必須依照以下各類型的強制順序排列 Phase，不得自行調整。

#### 🔵 WebAPI / Controller 類型

```
Phase 1 — Provider 層實作
  └── 實作所有外部資料存取方法（呼叫下游 API、DB 查詢等）
  └── 產出物：可獨立呼叫的 Provider 方法 + 對應 Interface

Phase 2 — Controller I/O 定義（含 Route / Request / Response）
  └── 定義所有端點的 URI、HTTP Method、Input DTO、Output DTO
  └── 此階段不實作 Service 邏輯，Service 方法僅定義簽章（throw NotImplementedException）
  └── 產出物：可編譯、可看到 Swagger 端點的 Controller 骨架

⛔ 中止點：交由開發者 / PM Review I/O 設計，確認後才繼續

Phase 3 — Service 邏輯實作
  └── 依已確認的 I/O 實作業務邏輯
  └── 串接 Phase 1 的 Provider

Phase 4 — 整合測試 / Checklist 驗收
  └── 查閱本次涉及服務的 scenario-flows/，確認現有場景是否受影響，補充必要情境或調整測試流程
```

> ⛔ 中止點規則：Phase 2 完成後必須標註「等待 I/O 設計確認後，才能進行 Phase 3」。AI 不得在同一輪對話中直接產出 Service 實作。

---

#### 🟣 BackgroundService 類型

```
Phase 1 — Provider 層實作
  └── 實作所有外部資料存取 / 外部 API 呼叫

Phase 2 — Worker / Job 定義（執行頻率、觸發條件、I/O 邊界）
  └── 定義 BackgroundService 的執行週期（Cron / Interval）
  └── 定義每次執行的 Input 來源（DB query / API call）與 Output（寫入目標）
  └── Service 邏輯僅定義骨架，不實作

⛔ 中止點：確認執行頻率、Input/Output 邊界設計後才繼續

Phase 3 — Service 邏輯實作（含錯誤處理 / Retry 策略）

Phase 4 — 整合測試 / Checklist 驗收
  └── 查閱本次涉及服務的 scenario-flows/，確認現有場景是否受影響，補充必要情境或調整測試流程
```

---

#### 🟢 前端 Vue / Nuxt 類型

```
Phase 1 — API 串接層建立
  └── 定義所有 API 呼叫函式與對應 TypeScript Interface / DTO
  └── 產出物：可呼叫後端（畫面尚未完成）的 API 函式

Phase 2 — GET / Select（查詢展示）
  └── 實作所有資料讀取頁面與元件（列表、詳情、分頁、篩選、頭像 fallback 等）

Phase 3 — Insert / Create（新增）
  └── 實作新增表單、Modal、送出邏輯

Phase 4 — Update / Edit（修改）
  └── 實作編輯 Modal 或 inline 編輯、預填資料、送出邏輯

Phase 5 — Delete（刪除）
  └── 實作刪除確認、送出邏輯、成功後 UI 更新

Phase 6 — 整合測試 / Checklist 驗收
  └── 查閱本次串接後端服務的 scenario-flows/，確認現有場景是否受影響，補充必要情境或調整測試流程
  └── 含互動 CRUD 時須填 **E2E 小節**（§9.5 或同級如 §7.6）；Phase 6 情境表須含 Test ID 並與 E2E 小節對齊
```

> GET → Insert → Update → Delete 的順序不得顛倒。若某類操作不存在，跳過對應 Phase，其餘順序維持不變。

---

### 區塊排列順序（強制）

Plan 的區塊必須依以下順序排列，不得任意調換。
**「待確認問題」永遠是最後一個區塊。**

```
1.  目錄（Table of Contents）
2.  目標（Goal）
3.  背景與策略適合（Context & Strategy Fit）
4.  假設（Assumptions）
5.  範圍（Scope）
6.  需求（Requirements）              ← 僅 feature / bugfix 類型
7.  現有結構分析（Current Structure）  ← 有舊程式碼需分析時
8.  架構差異對照（Architecture Gap）  ← 跨技術棧或框架遷移時
9.  I/O 設計（API / Controller）      ← 後端 feature 必填
10. 元件與頁面規格（UI Spec）         ← 前端 feature 必填（含 E2E 小節 §9.5 或同級，若需 Playwright）
10a. E2E / Playwright 規格            ← 前端 feature 且需 E2E 時必填；純展示頁可省略並於 §4 註明
11. 需新增或修改的檔案（File List）
12. Spec 參考文件（Spec References）     ← 涉及 aidata 服務時必填；供 @plan-executor
13. 實作步驟（Implementation Plan）
14. 驗收標準（Acceptance Criteria）
15. Checklist
16. 附錄（Appendix）                  ← Model 定義、Multipart 欄位表等
17. 待確認問題（Open Questions）      ← 🔒 永遠最後，不得移動
```

> 若某區塊不適用可省略，但區塊順序不得顛倒，「待確認問題」必須是最後一項。

---

## Plan 完整模板

```markdown
# [Plan 標題]
<!-- 格式：[類型] 描述，例：[feature] CommunityController 討論區後端實作 -->

> 版本：v1.0 | 日期：YYYY-MM-DD | 作者：
> Plan 類型：feature / bugfix / refactor / tech-debt
> 專案類型：webapi / frontend / backgroundservice / mixed
> 涉及服務：
> 是否涉及 DB：是 / 否
> 是否涉及 API：是 / 否
> 是否涉及 E2E：是 / 否

---

## 目錄

1. [目標](#1-目標)
2. [背景與策略適合](#2-背景與策略適合)
3. [假設](#3-假設)
4. [範圍](#4-範圍)
5. [需求](#5-需求)
6. [現有結構分析](#6-現有結構分析)
7. [架構差異對照](#7-架構差異對照)
8. [I/O 設計](#8-io-設計)
9. [元件與頁面規格](#9-元件與頁面規格)（含 9.5 E2E / Playwright 規格，若需 E2E）
10. [需新增或修改的檔案](#10-需新增或修改的檔案)
11. [Spec 參考文件](#11-spec-參考文件)
12. [實作步驟](#12-實作步驟)
13. [驗收標準](#13-驗收標準)
14. [Checklist](#14-checklist)
15. [附錄](#15-附錄)
16. [待確認問題](#16-待確認問題)

---

## 1. 目標

<!-- 1~3 句話。回答：「這個 Plan 完成後，我們獲得了什麼？」 -->


---

## 2. 背景與策略適合

<!-- 說明現況問題、業務需求，以及與整體產品策略的關聯。3~6 句。 -->


---

## 3. 假設

<!-- 列出前提假設。若假設不成立，Plan 需重新評估。 -->

- 使用者假設：
- 技術假設：
- 業務假設：

---

## 4. 範圍

**In Scope（包含）**
-

**Out of Scope（不包含）**
-

**Implementation Guard（實作邊界）**

| 類型 | 規則 |
|------|------|
| 允許變更 | 僅限 In Scope 與 File List 中列出的功能、檔案與必要衍生檔 |
| 禁止變更 | 不得新增 Plan 未列出的功能、UI 行為、API、DB table、背景 Job 或第三方整合 |
| 需求外變更 | 若開發中發現需新增功能，必須另開 Plan 或更新本 Plan 後重新 Review |

---

## 5. 需求

<!-- feature / bugfix 類型使用。以用戶故事格式撰寫，並標記優先級。 -->

| # | 標題 | 用戶故事（As... I want... So that...） | 優先級 | 備註 |
|---|------|--------------------------------------|--------|------|
| 1 | | | Must | |
| 2 | | | Should | |
| 3 | | | Nice | |

---

## 6. 現有結構分析

<!-- refactor / tech-debt，或有需要分析既有程式碼時使用 -->

### 6.1 專案分層結構

\```
ProjectName/
  └── LayerA/    ← 說明
  └── LayerB/    ← 說明
\```

### 6.2 可直接複用的既有檔案

| 檔案 | 用途 | 複用方式 |
|------|------|---------|
| | | 直接使用 / UI 參考 / 移植調整 |

### 6.3 關鍵機制說明

<!-- 認證機制、圖片上傳流程、快取策略等需特別說明的現有機制 -->


---

## 7. 架構差異對照

<!-- 跨技術棧、跨框架遷移時使用（例：Demo → 正式專案） -->

| 面向 | 來源（舊） | 目標（新） | 處理方式 |
|------|-----------|-----------|---------|
| 路由 | | | |
| 資料來源 | | | |
| 樣式 | | | |
| 狀態管理 | | | |
| 型別定義 | | | |

---

## 8. I/O 設計（API / Controller）

<!-- 後端 feature 必填 -->

> ⚠️ **Plan Gate 最低通過條件**
> - 每個端點都必須有獨立詳細規格，不得只列在端點總覽。
> - 禁止使用「同上」、「同 N1」、「同前述」、「回傳 DTO」、「回傳 Model」、「無特殊欄位」代替欄位表。
> - POST / PUT / PATCH 若有 body，必須逐欄列出所有 body 欄位；若沒有 body，必須明確寫「Request Body：無」。
> - 每個端點都必須列出 Response 欄位與至少一個具體 JSON 範例。
> - 若成功回應為 `204 No Content`，仍必須提供至少一個錯誤情境的 Response JSON 範例（例如 403 / 404 / 500）。
> - 每個端點總覽都必須填「需驗證」，值可為「否」、「是：登入」、「是：管理員」、「是：{權限名稱}」。

> Route 前綴：`/api`
> 需登入操作：`authKey` 放 route path（同既有慣例）

### 8.1 端點總覽

| # | Method | Path | 說明 | 需驗證 |
|---|--------|------|------|--------|
| a | GET | `/api/...` | | 否 |
| b | POST | `/api/{authKey}/...` | | 是 |

### 8.2 各端點詳細規格

> ⚠️ **禁止以 Model / DTO 名稱帶過**。輸入欄位必須逐欄列出必填標記，輸出欄位必須完整展開並附 JSON 範例。

#### 子模板 A：GET / DELETE（Query Params / Path Params 為主）

\```
GET /api/...
\```

**Request 參數：**

| 參數 | 位置 | 類型 | 必填 | 說明 | 範例值 |
|------|------|------|:----:|------|--------|
| keyword | query | string | — | 搜尋關鍵字，選填 | `"john"` |
| page | query | int | — | 頁碼，預設 1 | `1` |
| id | path | int | ✅ | 資源主鍵 | `42` |

**Response 欄位（必須逐欄列出，禁止以 Model 名稱帶過）：**

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | int | 主鍵 |
| name | string | 名稱 |
| createdAt | string (ISO8601) | 建立時間 |

**Response 範例：**
\```json
{
  "id": 1,
  "name": "John",
  "createdAt": "2026-01-01T00:00:00Z"
}
\```

---

#### 子模板 B：POST / PUT（Request Body 為主）

\```
POST /api/{authKey}/xxx
Content-Type: application/json
\```

**Request Body 欄位（POST/PUT 必須逐欄列出，禁止以「XX資料」Model 名稱帶過）：**

> 必填標記：✅ = 必填，— = 選填

| 欄位 | 類型 | 必填 | 說明 | 範例值 |
|------|------|:----:|------|--------|
| name | string | ✅ | 名稱 | `"John"` |
| age | int | — | 年齡，選填，預設 0 | `25` |
| avatarUrl | string | — | 頭像 URL | `"https://..."` |

**Response 欄位（必須逐欄列出，禁止以 Model 名稱帶過）：**

| 欄位 | 類型 | 說明 |
|------|------|------|
| id | int | 建立後的主鍵 |
| name | string | 名稱 |

**Response 範例：**
\```json
{
  "id": 42,
  "name": "John"
}
\```

#### 子模板 C：無 Request Body / 204 No Content 端點

\```
POST /api/{authKey}/xxx/{id}/like
Content-Type: application/json
\```

**Request 參數：**

| 參數 | 位置 | 類型 | 必填 | 說明 | 範例值 |
|------|------|------|:----:|------|--------|
| authKey | path | string | ✅ | 登入會員 AuthKey | `"abc123"` |
| id | path | string | ✅ | 目標資源 ID | `"subject-001"` |

**Request Body：** 無

**Response 欄位：** 成功時 `204 No Content`，無 body。

**Response 範例（錯誤情境仍必填）：**
\```json
{
  "status": 403,
  "detail": "user is banned"
}
\```

### 8.3 DB / 外部相依

> WebAPI / Controller 類型必填。若無 DB 或外部 API，也必須保留表格並填「不適用」。

**DB 使用**

| DB / Keyspace | Table / Collection | 操作 | 用途 | 欄位 / 條件 | 備註 |
|---------------|--------------------|:----:|------|-------------|------|
| 不適用 | 不適用 | — | 本 Plan 不直接讀寫 DB | — | — |

**內部 / 第三方 API**

| 服務 / 第三方 | Method | Path / 用途 | 呼叫時機 | 備註 |
|---------------|--------|-------------|----------|------|
| 不適用 | — | 本 Plan 不呼叫其他 API | — | — |

### 8.4 Job / Worker I/O 規格（BackgroundService 專案）

> ⚠️ **禁止以「讀取 XX 資料」或「寫入 XX 資料」帶過**。每個 Job 必須展開 Input 來源欄位與 Output 寫入欄位。

#### [Job 名稱]

**執行週期：** `0 */5 * * *`（每 5 分鐘）或 Interval 300s

**資料流向：**
\```
[來源 1：DB members (status=1)] ──┐
                                   ├── [Job 處理] → [目標 1：Redis key:cache:xxx]
[來源 2：Redis key:config:rate]  ──┘              → [目標 2：Kafka topic:evt-xxx]
\```

**Input 來源清單：**

| 來源類型 | 名稱 / Key / Table | 操作 | 過濾條件 | 說明 |
|----------|--------------------|:----:|----------|------|
| DB | members | SELECT | status = 1 | 讀取啟用中的會員 |
| Redis | config:exchange:rate | GET | — | 讀取匯率暫存 |

**Input 讀取欄位（必須逐欄列出，禁止以 Model 名稱帶過）：**

| 欄位 | 類型 | 來源 | 說明 |
|------|------|------|------|
| id | int | DB:members | 主鍵 |
| email | string | DB:members | Email |
| rate | decimal | Redis | 匯率值 |

**Output 目標清單：**

| 目標類型 | 名稱 / Key / Topic | 操作 | 說明 |
|----------|--------------------|:----:|------|
| DB | job_logs | INSERT | 寫入執行記錄 |
| Kafka | topic:member-sync | PRODUCE | 推送同步事件 |

**Output 寫入欄位（必須逐欄列出）：**

> 必填標記：✅ = 必填，— = 選填

| 欄位 | 類型 | 必填 | 目標 | 說明 |
|------|------|:----:|------|------|
| job_name | string | ✅ | DB:job_logs | Job 名稱 |
| executed_at | datetime | ✅ | DB:job_logs | 執行時間 |
| member_id | int | ✅ | Kafka | 會員 ID |
| event_type | string | ✅ | Kafka | 事件類型，固定值 `"member-sync"` |

---

## 9. 元件與頁面規格（UI Spec）

<!-- 前端 feature 必填 -->

### 9.1 頁面清單

| 頁面 | 路由 | 說明 |
|------|------|------|
| | | |

### 9.2 元件清單

| 元件 | 路徑 | 複用程度 | 說明 |
|------|------|---------|------|
| | | 直接移植 / UI 參考 | |

### 9.3 各頁面互動規格

#### [頁面名稱]（`/route`）

- 互動行為說明（條列）

**欄位 ↔ API 對應**

| 畫面欄位 | API 欄位 | 備註 |
|---------|---------|------|
| | | |

### 9.4 色彩系統（若有）

| 用途 | 色碼 |
|------|------|
| 背景 | |
| 強調色 | |

### 9.5 E2E / Playwright 規格

<!-- 前端 feature 且預期產出 Playwright / E2E 腳本時必填。
     純靜態展示、無互動寫入、明確 Out of Scope E2E 時可省略，並在 §4 範圍註明。 -->

> **與 scenario-flows 的分工**
> - 後端 `aidata/webapi/{service}/scenario-flows/`：API 呼叫序列、DB/Cache、業務規則；供 Bruno / API 測試與 **E2E 前置資料 setup**。
> - 本節：頁面互動、UI 斷言、Toast/Dialog 文案；供 Playwright 腳本生成。
> - 禁止將 UI 操作步驟寫入 `webapi/*/scenario-flows/`。

#### 9.5.1 測試環境

| 項目 | 值 | 備註 |
|------|-----|------|
| 專案 | `{repo 名稱}` | 例：`newlotterytools` |
| Base URL | `{環境 URL}` | 例：`http://localhost:3000` |
| 登入前置 | 是 / 否 | 否則寫明「無 auth，直接進入路由」 |
| 登入方式 | `{步驟或 storageState 路徑}` | 需登入時必填 |
| API 依賴 | `{BackEnd / Site 服務名}` | E2E 是否需 staging API 或 mock |

#### 9.5.2 測試資料 Fixture

> 固定測試用資料，避免 AI 腳本使用隨機值。可引用後端 scenario-flows 的 setup API。

| Fixture ID | 用途 | 關鍵欄位 | 建立方式 |
|------------|------|---------|---------|
| FIX-01 | 例：可搜尋玩家 | account=`rankballtest16` | 既有 DB 資料 |
| FIX-02 | 例：不存在玩家 | queryName=`not_exist_xxx` | 無需 setup |
| FIX-03 | 例：已禁言帳號 | account=`banned_user_01` | POST `{API}` 或手動 |

#### 9.5.3 Locator 策略

> 優先順序：`data-testid` > 穩定 `id` > `getByRole` + 可見文案 > placeholder / label。
> 禁止僅寫 CSS class（Vuetify 類名易變）。

| 優先 | 策略 | 範例 |
|:----:|------|------|
| 1 | `data-testid` | `[data-testid="banned-add-btn"]` |
| 2 | 元素 `id` | `#banned-table` |
| 3 | Role + name | `getByRole('button', { name: '新增' })` |
| 4 | Label / placeholder | `getByLabel('帳號或暱稱')` |

**本 Plan 建議新增的 test id（實作時加於元件）：**

| test id | 元素 | 頁面 |
|---------|------|------|
| `{page}-{action}-btn` | 例：新增按鈕 | `/member/banned` |

> 若實作階段未加 test id，Plan 必須在互動步驟表填寫 **Role + 按鈕/連結可見文案** 作為 fallback。

#### 9.5.4 Toast / Dialog 文案對照

> 對齊專案 Toast 實作（例：`SetToast(title, message, type)`）。title、message 分欄，禁止只寫「顯示成功」。

| 情境 ID | 觸發條件 | Toast title | Toast message | type |
|---------|---------|-------------|---------------|------|
| TOAST-01 | 搜尋無結果 | `{title}` | `找不到玩家` | error |
| TOAST-02 | 新增成功 | `{title}` | `{message}` | success |

| 情境 ID | Dialog 標題 | 確認按鈕 | 取消按鈕 | 觸發條件 |
|---------|------------|---------|---------|---------|
| DLG-01 | `{標題}` | `確認` | `取消` | 解除禁言 |

#### 9.5.5 各頁面互動步驟（Playwright-ready）

##### [頁面名稱]（`/route`）

| 步驟 | 操作 | Locator（testid / role+name） | 輸入 / 選取值 | 預期 UI 狀態 |
|:----:|------|------------------------------|--------------|-------------|
| 1 | 點側邊選單 | `getByRole('link', { name: '水桶管理' })` | — | URL=`/member/banned` |
| 2 | 開新增 Modal | `[data-testid="banned-add-btn"]` | — | dialog visible |
| 3 | 搜尋玩家 | placeholder=`帳號或暱稱` | `FIX-01.account` | 結果列含該 account |
| 4 | 選取結果 | `getByText('FIX-01.account')` | — | account/userName 欄位 disabled 且已帶入 |
| 5 | 填寫並送出 | — | endTime, description | TOAST-02；表格含新列 |

**Network 斷言（選填，有寫入操作時建議填）：**

| 步驟 | Method | Path | Request Body 要點 | 預期 Status |
|:----:|--------|------|-------------------|:-----------:|
| 5 | POST | `/api/banned` | `{ account, endTime, description }` | 200 |

#### 9.5.6 錯誤與邊界情境（E2E）

| Test ID | 類型 | 前置 | 操作摘要 | 預期結果 |
|---------|------|------|---------|---------|
| E2E-ERR-01 | Error | — | 搜尋 FIX-02 | TOAST-01 |
| E2E-EDGE-01 | Edge | 搜尋回傳多筆 | 未選取即按送出 | 按鈕 disabled 或 TOAST-{id} |
| E2E-VAL-01 | Validation | 開 Modal | 必填未填送出 | 欄位驗證提示 / 不可送出 |

---

## 10. 需新增或修改的檔案

### 新增

\```
path/to/file.ts    # 說明
\```

### 修改

\```
path/to/file.ts    # 說明變更內容
\```

---

## 11. Spec 參考文件

> **必填**（Plan 涉及 `aidata` 內既有 WebAPI / BackgroundService / 前端專案時）。
> 供 `@plan-executor` 與實作 agent 讀取；**禁止** 實作階段僅讀 `documents.md` 而略過本表列出的 OpenAPI `.json`。
> 路徑一律相對於 `aidata` repo 根目錄（或 workspace 內 `./aidata/...`）。

| 用途 | 路徑 | 讀取時機 / 備註 |
|------|------|----------------|
| 主服務 OpenAPI | `webapi/{service}/{service}.json` | I/O 定義；實作 Controller / Provider 前 |
| 主服務業務規範 | `webapi/{service}/documents.md` | 業務規則、限制；與 detail 衝突時以 documents 為準 |
| 主服務架構 | `webapi/{service}/{service}-detail.md` | 選填；分層、既有端點概覽 |
| 下游 / 串接服務 OpenAPI | `webapi/{other}/{other}.json` | §8.3 列出的每個內部 API 至少一列 |
| 整合流程 | `webapi/{service}/scenario-flows/.../*.md` | Phase 4/6 對照或 E2E setup 引用時 |
| DB Schema | `db/{db}-detail.md` | §8.3 有 DB 讀寫時 |
| 跨服務業務 | `others/*-documents.md` | 博彩 / 股票等跨域規則 |
| 前端業務 | `frontend/{project}/documents.md` | 前端 Plan |

**填寫規則**

- 主服務至少列出 **OpenAPI `.json` + `documents.md`**（若 aidata 存在該服務目錄）
- §8.3「內部 / 第三方 API」每一列下游服務，本表須有對應 `{service}.json`（或明確標「無 OpenAPI，理由：…」）
- 不適用時保留表格並填「不適用」列，**禁止** 整節省略

### 11.1 實作 Read Policy（refactor / 多檔修改建議填）

> Code 層讀取白名單；**§10 File List 為 Scope 上限**（不必每檔寫插入點 snippet）。
> `.rules.md` 由 **coding agent** 實作前端/UI 步驟前讀取，不列於 Spec 表。
> `@plan-executor` 缺結構時產 **Recon / 實作 Step** 授權有限 read，不要求 Plan 寫齊所有 namespace/DI。

**檔案類別**

| 類別 | 說明 | Plan 需嵌入 | 實作 read 預算 |
|------|------|-------------|---------------|
| **A 新建** | §10「新增」 | 完整 snippet / 簽章 | 通常 0 |
| **B 必改既有** | §10「修改」 | 僅「改什麼」一句 | 1 次 / ≤120 行 |
| **C 可能連帶** | §10「修改」、編譯失敗才可能動 | 不必 | Recon 1 次/≤80 行，或 Step 批准 |

**Read Policy 表（範例）**

| 檔案（目標 repo） | 類別 | 誰讀 | 允許 Step | read 上限 |
|-------------------|------|------|-----------|-----------|
| `_plans/本檔.md` | Spec | executor + coding agent | 全程 | 完整 |
| `Infrastructure/DriftChecker.cs` | A | coding agent | Step N | 0 |
| `Extensions/ServiceCollectionExtensions.cs` | B | coding agent | Step N 或 Recon | 1 次 / 120 行 |
| `Program.cs` | C | coding agent | Recon 或編譯失敗 Step | 1 次 / 80 行 |

### 11.2 Step 進度檔（`@plan-executor` 產出）

> 路徑：`{repo}/_plans/logs/{PlanBasename}_steps.md`（Plan 為 `_plans/Foo_Plan.md` → `_plans/logs/Foo_Plan_steps.md`）
>
> 含：`Spec 已讀`、`進度` checklist（`- [x] Step N`）、`Step 明細`表、`下一步` 欄位、已完成備註。
> **Resume 時 executor 優先讀此檔**，避免重拆 Step 目錄。完整模板見 `systemprompts/plan-executor-prompt.md`。

---

## 12. 實作步驟

<!-- 依 Plan 類型選擇下方對應的 Phase 結構，刪除不適用的類型區塊。順序為強制規定，不得調換。 -->

<!-- ===== WebAPI / Controller 類型 ===== -->
### Phase 1 — Provider 層實作
> 產出物：可獨立呼叫的 Provider 方法 + 對應 Interface

- [ ] 實作 Provider 方法（外部 API 呼叫 / DB 查詢）
- [ ] 定義 IProvider Interface

### Phase 2 — Controller I/O 定義
> 產出物：可編譯、可見 Swagger 端點的 Controller 骨架（Service 僅定義簽章）

- [ ] 定義所有端點 URI、HTTP Method
- [ ] 定義 Request / Response DTO
- [ ] Controller 呼叫 Service，Service 方法僅 throw NotImplementedException

> ⛔ **中止點**：交由開發者 / PM 確認 I/O 設計，**確認後才進行 Phase 3**。

### Phase 3 — Service 邏輯實作
> 產出物：完整業務邏輯 + 對應單元測試（與實作同步產出）

- [ ] 實作 Service 方法
- [ ] 串接 Phase 1 Provider

**單元測試涵蓋範圍（Service 層，以下為必填項目）：**

| 類型 | 測試對象 | 說明 |
|------|----------|------|
| Happy Path | 每個 Service 方法 | 正常輸入 → 回傳預期結果 |
| Edge Case | 每個 Service 方法 | 空集合、null 欄位、邊界數值等 |
| Error Path | Provider 呼叫失敗時 | Service 應正確回傳錯誤或往上拋出例外 |

> ⚠️ 禁止只寫 Happy Path 就收工；Edge Case 與 Error Path 為必填，非選填。

### Phase 4 — 整合測試 / Checklist 驗收

> 測試必須以**使用者操作情境**為單位，描述連貫的 API 呼叫序列，而非個別端點逐一驗證。
> 至少列出 1 個 Happy Path 情境，建議補 1 個 Error Path 情境。

- [ ] Build 無錯誤

#### Scenario Flows 影響分析

> 查閱本次涉及服務的 `scenario-flows/`（見 `webapi/_index.md` 速查表）。
> 若服務無 scenario-flows，填「不適用」即可。

| 服務 | 受影響場景檔案 | 影響說明 | 處置（補情境 / 調整流程 / 不影響） |
|------|--------------|---------|----------------------------------|
| 例：MemberService | auth-flow/login.md | 本次新增 OTP 驗證，影響既有登入流程前置步驟 | 補「含 OTP 的登入情境」 |

#### 情境 1：[Happy Path 名稱，例：完整下單流程]

| 步驟 | 呼叫（Method Path） | 說明 | 預期結果 |
|------|---------------------|------|----------|
| 1 | POST /api/auth/login | 有效帳密登入 | 回傳 authKey，HTTP 200 |
| 2 | POST /api/{authKey}/orders | 建立訂單 | 回傳 orderId，HTTP 201 |
| 3 | GET /api/{authKey}/orders/{orderId} | 確認訂單狀態 | status="pending"，HTTP 200 |

#### 情境 2：[Error Path 名稱，例：無效憑證]

| 步驟 | 呼叫（Method Path） | 說明 | 預期結果 |
|------|---------------------|------|----------|
| 1 | POST /api/auth/login | 錯誤密碼 | HTTP 401 |
| 2 | GET /api/{authKey}/orders | 過期 authKey | HTTP 401 |

<!-- ===== BackgroundService 類型 ===== -->
### Phase 1 — Provider 層實作
> 產出物：可獨立呼叫的 Provider 方法 + 對應 Interface

- [ ] 實作所有外部資料存取 / 外部 API 呼叫方法

### Phase 2 — Worker / Job 定義
> 產出物：明確的執行週期、Input/Output 邊界骨架（Service 邏輯僅骨架）

- [ ] 定義執行週期（Cron / Interval）：___
- [ ] 定義 Input 來源：___
- [ ] 定義 Output 目標：___
- [ ] Service 邏輯僅骨架，不實作

> ⛔ **中止點**：確認執行頻率、Input/Output 邊界設計後，**才進行 Phase 3**。

### Phase 3 — Service 邏輯實作（含錯誤處理 / Retry 策略）
> 產出物：完整業務邏輯 + 對應單元測試（與實作同步產出）

- [ ] 實作業務邏輯
- [ ] 實作錯誤處理與 Retry

**單元測試涵蓋範圍（Service / 處理邏輯層，以下為必填項目）：**

| 類型 | 測試對象 | 說明 |
|------|----------|------|
| Happy Path | 核心處理邏輯 | 正常輸入資料 → 產出正確的轉換 / 寫入結果 |
| Edge Case | 核心處理邏輯 | Input 為空、資料重複、欄位缺失等邊界條件 |
| Error Path | Retry 策略 | 拋出例外後重試次數、最終失敗時的處理行為 |

> ⚠️ 禁止只寫 Happy Path 就收工；Edge Case 與 Error Path 為必填，非選填。

### Phase 4 — 整合測試 / Checklist 驗收

> 測試必須以 **Before → Trigger → After** 為單位，驗證資料流端到端的狀態變化，
> 而非只確認 Job 不報錯。至少列出 1 個正常情境，建議補 1 個邊界情境（如 Input 為空）。

- [ ] Build 無錯誤

#### Scenario Flows 影響分析

> 查閱本次涉及服務的 `scenario-flows/`（見 `webapi/_index.md` 速查表）。
> 若服務無 scenario-flows，填「不適用」即可。

| 服務 | 受影響場景檔案 | 影響說明 | 處置（補情境 / 調整流程 / 不影響） |
|------|--------------|---------|----------------------------------|
| 例：PriceCenterService | query-flow/get-odds.md | Job 改寫賠率快取，影響此查詢場景的前置資料狀態 | 補「Job 執行後查詢賠率」情境 |

#### 情境 1：[正常情境名稱，例：有待處理資料時正常同步]

| 步驟 | 動作 | 說明 | 預期結果 |
|------|------|------|----------|
| Before | 準備 Input | DB members 插入 status=1 測試資料 3 筆 | DB 有 3 筆待處理資料 |
| Trigger | 手動觸發 Job | 呼叫端點 或 等待 Cron 執行 | Log 顯示開始處理 |
| After | 驗證 Output | 查詢 Redis key:cache:member:* | 3 筆快取已建立 |
| After | 驗證 Output | 查詢 DB job_logs | 1 筆記錄，status=success |

#### 情境 2：[邊界情境名稱，例：Input 為空時不報錯]

| 步驟 | 動作 | 說明 | 預期結果 |
|------|------|------|----------|
| Before | 確認 Input 為空 | DB members 無 status=1 資料 | 查詢結果 0 筆 |
| Trigger | 手動觸發 Job | — | Job 正常結束，不拋例外 |
| After | 驗證 Output | 查詢 DB job_logs | 1 筆記錄，processed_count=0，status=success |

<!-- ===== 前端 Vue / Nuxt 類型 ===== -->
### Phase 1 — API 串接層建立
> 產出物：可呼叫後端的 API 函式 + TypeScript Interface

- [ ] 在 apis/index.ts 定義所有 API 呼叫函式
- [ ] 定義對應的 TypeScript Interface / DTO

### Phase 2 — GET / Select（查詢展示）
> 產出物：所有查詢類頁面與元件可正常顯示資料

- [ ] 實作列表頁、詳情頁
- [ ] 實作分頁、篩選
- [ ] 頭像空值 fallback

### Phase 3 — Insert / Create（新增）
> 產出物：新增流程可完整執行

- [ ] 實作新增表單 / Modal
- [ ] 登入檢查、送出邏輯

### Phase 4 — Update / Edit（修改）
> 產出物：編輯流程可完整執行

- [ ] 實作編輯 Modal 或 inline 編輯
- [ ] 預填資料、送出邏輯

### Phase 5 — Delete（刪除）
> 產出物：刪除流程可完整執行

- [ ] 實作刪除確認
- [ ] 送出邏輯、成功後 UI 更新

### Phase 6 — 整合測試 / Checklist 驗收

> 測試必須以**使用者操作情境**為單位，描述連貫的頁面互動流程，
> 而非個別功能（CRUD）各自孤立測試。
>
> **最低要求：**
> - 至少 1 個 Happy Path 情境（含 Test ID）
> - 至少 1 個 Error Path 或 Validation 情境
> - 若 E2E 小節存在：Phase 6 情境的 Test ID 須與 E2E 小節內 9.5.5/9.5.6 或 7.6.x 對齊，不得矛盾
>
> **Playwright 生成對照：** MR 階段 AI 以 E2E 小節 + 本節情境表為腳本規格來源；缺 locator 或 Toast 文案視為 Plan 不完整。

- [ ] typecheck 無錯誤
- [ ] 若有 Composable 或 util 函式含業務邏輯，需補單元測試（Happy Path + Edge Case）
- [ ] E2E 小節已填（§9.5 或同級；或 §4 明確標示不適用 E2E）

#### Scenario Flows 影響分析

> 查閱本次**串接後端服務**的 `scenario-flows/`（見 `webapi/_index.md` 速查表）。
> 用途：評估 API 行為是否影響 UI；E2E **前置 setup / teardown** 可引用 scenario-flow 中的 API 步驟。
> 若服務無 scenario-flows，填「不適用」即可。
> **UI 互動步驟不寫入 scenario-flows**，應寫在 E2E 小節（§9.5 或同級）。

| 服務 | 受影響場景檔案 | 影響說明 | 處置（補情境 / 調整流程 / 不影響） |
|------|--------------|---------|----------------------------------|
| 例：MemberService | create-flow/create-order.md | E2E 需先 POST 建立訂單再測前台 | E2E Fixture FIX-03 引用該 API |

#### 情境 1：[Happy Path 名稱]（Test ID: `{E2E-xxx-01}`）

| 步驟 | 操作 | 頁面 / Locator | 輸入 / Fixture | 預期結果 |
|:----:|------|---------------|---------------|----------|
| Before | 準備資料 | — | FIX-01 已存在 | — |
| 1 | 點 `{按鈕文案}` | `{locator}` | — | `{可觀察 UI 狀態}` |
| 2 | 填 `{欄位 label}` | `{locator}` | `{值}` | — |
| 3 | 點 `{送出按鈕文案}` | `{locator}` | — | Toast: `{title}` / `{message}`；表格含 `{欄位}={值}` |
| After | 驗證 API（選填） | network | POST `{path}` | HTTP 200 |

#### 情境 2：[Error / Validation 名稱]（Test ID: `{E2E-xxx-ERR-01}`）

| 步驟 | 操作 | 頁面 / Locator | 輸入 / Fixture | 預期結果 |
|:----:|------|---------------|---------------|----------|
| 1 | `{操作}` | `{locator}` | FIX-02 | Toast: TOAST-01 或按鈕 disabled |

---

## 13. 驗收標準

<!-- 可量測、可被他人獨立驗證。禁止模糊描述如「功能正常運作」。 -->

- [ ] 驗收條件（測試方式：手動 / 自動化 / typecheck）

---

## 14. Checklist

**通用**
- [ ] Build / typecheck 無錯誤
- [ ] Logger 於所有錯誤路徑均有記錄

**後端（若適用）**
- [ ] authKey 驗證失敗回傳 401
- [ ] 擁有者驗證失敗回傳 403
- [ ] 圖片轉 WebP 後再送後端
- [ ] multipart 端點使用 `HttpClient`，其餘使用 `IRestfulClient`

**前端（若適用）**
- [ ] `useAsyncData` 用於 GET（SSR）
- [ ] 寫入操作限 client-side
- [ ] 頭像空值 fallback 至預設頭像
- [ ] 未登入操作導向登入提示
- [ ] E2E 小節已填（§9.5 或同級；或 §4 標示不適用）
- [ ] 關鍵互動元件已加 `data-testid` 或穩定 `id`（與 E2E 小節 Locator 表一致）
- [ ] Toast / Confirm Dialog 文案與 E2E 小節 Toast/Dialog 表一致

---

## 15. 附錄

### 14.1 Model / DTO 定義

\```csharp
// Model 定義（後端）
\```

\```typescript
// Interface 定義（前端）
\```

### 14.2 Multipart 欄位對應表（若有）

#### 操作名稱 — POST `/path`

| multipart 欄位 | 來源 | 必填 | 說明 |
|----------------|------|------|------|
| | | ✅ / — | |

### 14.3 參考資料

- [文件連結]()
- Issue / PR：#xxx

---

## 16. 待確認問題

> 🔒 此區塊永遠是 Plan 的最後一個區塊，不得移動。
> 所有無法確認的事項一律集中至此，不得穿插在其他區塊內。
> 確認後更新狀態與結論，保留紀錄供未來回溯。
> 禁止使用 `(無)`、`N/A`、空白段落或刪除表格來表示沒有問題。
> 若無待確認事項，只能使用下方固定表格列。

| # | 問題 | 狀態 | 結論 / 說明 |
|---|------|------|------------|
| Q1 | 目前無待確認問題 | ✅ 已確認 | 本 Plan 無阻塞實作的待確認事項 |

| 標記 | 意義 |
|------|------|
| ⬜ 待確認 | 尚未有答案，需確認 |
| ✅ 已確認 | 已獲明確答案，結論填入右欄 |
| 🚫 不適用 | 確認後不影響實作，原因填入右欄 |
| 🔄 討論中 | 正在討論，尚無定論 |
```

---

## Commit 前檢查規範（Validation Spec）

> 本章節僅供 **commit gate / AI 審查流程** 使用，不改變 Plan 的章節產生格式與內容模板。
> 若此章節與「Plan 完整模板」衝突，請以「Plan 完整模板」作為生成依據，並以本章節作為檢查依據。

### 一、通用檢查（所有 Plan 必須通過）

1. **生成一致性檢查（必須一致）**
   - Plan 章節順序、必填區塊、Phase 順序需符合本規範的生成要求。
   - 不得出現與規範衝突的自定義流程（例如調換強制 Phase 順序）。
   - 若類型不適用可省略區塊，但不得破壞既定順序規則。
   - Plan 開頭必須標示 Plan 類型、專案類型、涉及服務、是否涉及 DB / API / E2E，供後續套用類型專屬檢查。

2. **待確認問題檢查（必須為 0）**
   - 「待確認問題（Open Questions）」區塊必須存在且為最後一個區塊。
   - commit 檢查時，不得存在任何 `⬜ 待確認` 或 `🔄 討論中` 狀態。
   - 僅允許 `✅ 已確認` 或 `🚫 不適用`。
   - 若無待確認事項，需在表格中明確標示「目前無待確認問題」。
   - 禁止使用 `(無)`、`N/A`、空段落或刪除表格來表示無待確認事項。

3. **Scope Guard 檢查（不得超出 Plan）**
   - Implementation / PR 異動不得新增 Plan In Scope 與 File List 未列出的功能、UI 行為、API、DB table、背景 Job 或第三方整合。
   - 若出現 Plan 未列的新功能，預設視為不通過；應另開 Plan 或先更新本 Plan 並重新 Review。

4. **Spec 參考文件檢查（涉及 aidata 服務時）**
   - §11「Spec 參考文件」必須存在且為表格。
   - 主服務須列 `webapi/{service}/{service}.json` 與 `documents.md`（或 `service/`、`frontend/` 對應路徑）；aidata 無該服務目錄時須在表內說明。
   - §8.3 列出的每個內部 WebAPI 下游，§11 須有對應 OpenAPI 路徑或「無 OpenAPI」理由。
   - 禁止 Spec 表為空或僅寫服務名稱而無完整路徑。

5. **輸出結果（給檢查程式 / AI Agent Server）**
   - 需回傳結構化結果：
     - `status`: `pass` 或 `fail`
     - `unresolved_count`: 未解決待確認問題數量（整數）
     - `issues`: 未通過項目清單（可含 section、reason、evidence）
   - 判定原則：`status=pass` 且 `unresolved_count=0` 才可通過 commit gate。

### 二、類型專屬檢查（依 Plan 類型至少滿足對應條件）

#### A. 前端 Vue / Nuxt 專案

- 必須列出**調用哪些 API**（至少包含 Method、Path、用途）。
- 必須描述主要**操作流程**（至少涵蓋查詢與實際寫入操作流程；若有 CRUD，應呈現 GET → Insert → Update → Delete 流程或明確標示不適用項）。
- UI 規格需能對應到 API（例如欄位 ↔ API 欄位或互動 ↔ API 呼叫關係）。
- **整合測試情境**：Phase 6 必須包含至少 1 個以步驟表格呈現的 Happy Path 情境（含 Test ID；操作 → 頁面/Locator → 預期結果），不得只列 checkbox；並至少 1 個 Error Path 或 Validation 情境。
- **Scenario Flows 查閱**：Phase 6 必須包含「Scenario Flows 影響分析」表格；若串接服務有 scenario-flows，需逐一評估受影響場景並說明處置方式；若無則填「不適用」。UI 互動步驟寫在 **E2E 小節**（見下），不得僅寫入 scenario-flows。
- **E2E / Playwright 規格（E2E 小節）**：
  - **章節辨識**：模板為 `### 9.5 E2E / Playwright 規格`；實際 Plan 若 UI Spec 為第 7 章，可寫為 `### 7.6` 等**同級小節**，內容須含下列必填子節（等同 9.5.2 / 9.5.4 / 9.5.5）。
  - **觸發條件**：若 Plan 範圍含 CRUD、Modal、表單驗證、Toast、Confirm Dialog 等互動，**必須**包含 E2E 小節，或在 §4 Out of Scope 明確寫「不產 E2E」。
  - **必填子節**：**測試資料 Fixture**、**Toast/Dialog 文案對照**、**至少一頁互動步驟表**（對應模板 9.5.2、9.5.4、9.5.5）。
  - 禁止模糊斷言：「Toast 成功」「列表刷新」「功能正常」；須寫可 assert 的文案或 DOM 狀態。
  - Locator：每個關鍵步驟須有 testid、id、或 role+可見文案其一；不得全空白。
  - Phase 6 每個情境須含 **Test ID**，且與 E2E 小節內 **7.6.6 / 9.5.6** 的 Test ID 一致或可交叉引用。
- **單元測試**：若 Plan 包含 Composable 或 util 業務邏輯，必須明確列出需補單元測試的對象（Happy Path + Edge Case）。

#### B. 後端 WebAPI / Controller 專案

- 必須有完整 I/O 功能描述：
  - 端點清單（Method、Path、用途、驗證需求）
  - **Request 欄位**：POST / PUT 端點必須逐欄列出所有 body 欄位，並標記必填（✅）/ 選填（—）；
    禁止以「XX 資料」、「Member DTO」等 Model 名稱帶過。
  - **Response 欄位**：每個端點必須完整列出回傳物件的所有欄位（欄位名、類型、說明）；
    禁止以「回傳 Member」、「回傳 CreateResult」等 Model 名稱帶過。
  - 每個端點至少提供一個具體的 Response JSON 範例。
- 必須描述使用的資料庫（讀取/寫入目標、用途）。
- 必須描述整合調用的第三方 API 或其他內部 WebAPI（至少列出服務名稱或端點用途）。
- **Spec 參考文件**：§11 須列主服務 OpenAPI `.json` 與 `documents.md`；§8.3 下游服務須有對應 Spec 路徑。
- **整合測試情境**：Phase 4 必須包含至少 1 個以步驟表格呈現的 Happy Path 情境（API 呼叫序列 → 預期結果），不得只列 checkbox。
- **Scenario Flows 查閱**：Phase 4 必須包含「Scenario Flows 影響分析」表格；若涉及服務有 scenario-flows，需逐一評估受影響場景並說明處置方式；若無則填「不適用」。
- **單元測試**：Phase 3 必須明確列出單元測試涵蓋範圍，且需涵蓋 Happy Path、Edge Case（空值/邊界）、Error Path（Provider 例外處理）三類，不得只寫 Happy Path。

#### C. BackgroundService 專案

- 必須描述 Job/Worker 的執行週期與觸發條件（Cron 表達式或 Interval 秒數）。
- 必須描述完整資料流向（Input 來源 → Job 處理 → Output 目標），區分讀寫方向：
  - 資料庫（table / collection 名稱、查詢條件）
  - Redis（key pattern 或資料結構）
  - Kafka（topic 名稱、message schema）
  - 檔案（路徑、格式）
- **Input 欄位**：必須逐欄列出主要讀取欄位（欄位名、類型、來源、說明）；
  禁止以「讀取 XX 資料」等描述帶過。
- **Output 欄位**：必須逐欄列出寫入欄位（欄位名、類型、必填、目標、說明）；
  禁止以「寫入 XX 資料」等描述帶過。
- **整合測試情境**：Phase 4 必須包含至少 1 個以 Before → Trigger → After 步驟表格呈現的正常情境，不得只列 checkbox。
- **Scenario Flows 查閱**：Phase 4 必須包含「Scenario Flows 影響分析」表格；若 Job 的 Input/Output 涉及有 scenario-flows 的服務，需評估受影響場景並說明處置方式；若無則填「不適用」。
- **單元測試**：Phase 3 必須明確列出單元測試涵蓋範圍，且需涵蓋 Happy Path、Edge Case（Input 為空/重複）、Error Path（Retry 行為）三類，不得只寫 Happy Path。

### 三、檢查失敗處理

- 任一必填檢查未通過即 `fail`，不得自動放行。
- 允許緊急例外時，必須在檢查結果中附上「例外原因」與「責任人」；預設仍應視為不通過，由人工核准流程處理。

---

*版本：v1.4 | 最後更新：2026-06-01*
