# 測試腳本規範

由 `@test-maker`（腳本產出）與 `@ai-tester`（腳本執行）觸發時載入。適用於 testscripts repo 內的 Bruno（`.yml`）與 Playwright（`.ts`）腳本。

測試計畫與 xlsx 用例表格式 → 見 `./TEST_PLAN_SPEC.md`（`@test-maker` 專用）。

---

## 引導師分工

| 引導師 | 職責 | 產物 |
|--------|------|------|
| `@test-maker` | 設計測試 | testplan.md → xlsx → 腳本 |
| `@ai-tester` | 執行測試 | 測試報告、ingest-json |

xlsx 由 `@test-maker` 產出；`@ai-tester` 以腳本 folder 為主，`xlsx` 僅作對照。

---

## 腳本產出守則（@test-maker）

- 命名對齊 testplan §6 Test ID 與 xlsx「測試項目」
- Bruno：`{service}/_tempscripts/{ticketId}/`，含 `Version.yml`（或 `folder.yml`）
- Playwright：`{frontend}/_tempe2e/{ticketId}/`
- `info.seq` / 檔名順序：login、前置資料優先
- assertion / expect 對齊 xlsx「預期結果」，禁止模糊斷言
- 環境變數用 `{{var}}`；不寫死 URL、token、密碼

---

## 修改範圍

| 允許 | 禁止 |
|------|------|
| 修改 testscripts repo 內的測試腳本 | 修改 `aidata/` 任何檔案 |
| 修語法錯誤、補缺區塊、修正 typo | 未告知即刪除整個 test case |
| 調整 selector（意圖不變） | 未告知即改變測試意圖或放寬斷言 |

---

## 修補守則

### 可自動修復

- YAML / TypeScript 語法錯誤（修到可解析）
- 缺少 `info`、`http`、`runtime.scripts`、`settings` 等結構區塊
- 明顯 typo、縮排錯誤
- selector 過時但測試意圖清楚（改用語意等效 selector）

### 須告知後修復

- 修改 API path 或 HTTP method（須對照 aidata `documents.md`）
- 修改斷言條件（可能改變測試意圖）
- 刪除或合併 test case

### 修補後必做

1. 在測試報告「腳本變更紀錄」列出：檔名、變更類型、說明
2. 修補完成後再執行，不可假設已通過

---

## Bruno（`.yml`）格式

Bruno v3.3+ 匯出格式，常見結構：

```yaml
info:
  name: ...
  type: http
  seq: N

http:
  method: GET | POST | PUT | DELETE | ...
  url: "{{baseUrl}}/path/{{var}}"
  headers: ...
  body: ...

runtime:
  scripts:
    - type: tests
      code: |-
        test('...', function () {
          expect(res.status).to.equal(200);
        });

settings:
  encodeUrl: true
  timeout: 0
  followRedirects: true
  maxRedirects: 5
```

要點：

- 變數使用 `{{varName}}` 語法
- `info.seq` 決定執行順序（數字小者先跑）
- `auth: inherit` 時需有前置 login 或環境變數提供 token
- assertion 使用 Bruno chai 語法：`expect(res.status).to.equal(200)`、`expect(res.body.xxx).to.exist`
- 修補時保持 `info.name` 與測試意圖一致

---

## Playwright（`.ts`）格式

常見結構：

```typescript
import { test, expect } from '@playwright/test';

test.describe('...', () => {
  test.beforeEach(async ({ page }) => { ... });

  test('...', async ({ page }) => {
    await page.goto('/path');
    await expect(page.locator('...')).toBeVisible();
  });
});
```

要點：

- 優先使用 `data-testid`，其次語意 selector（文字、role）
- 執行時以測試意圖為準，不死板依賴腳本中的 selector
- 整合測試預設打真實 API（不走 `page.route` mock），除非使用者明確要求 mock 模式
- 修補時不改 `test('...')` 標題所表達的測試意圖

---

## 執行環境與工具安裝

### 工具對照

| 類型 | 套件 | 安裝位置 | 用途 |
|------|------|----------|------|
| **Playwright MCP** | — | Cursor 設定（`user-playwright`） | `@ai-tester` 語意執行 E2E（`browser_navigate` 等） |
| **Playwright** | `@playwright/test` | repo 根目錄 `devDependencies` | 瀏覽器 binary、可選 CLI |
| **Bruno CLI** | `@usebruno/cli` | repo 根目錄 `devDependencies` | `npx bru run` 執行 API 測試 |

### 安裝位置（硬規則）

- Node.js 依賴（`package.json`、`node_modules`、`package-lock.json`）**僅允許**在 testscripts **repo 根目錄**
- **禁止**在使用者指定的測試腳本 folder 內執行 `npm init`、`npm install`、建立 `package.json`
- **禁止**未告知使用者即執行 `npm install -g`（全域安裝）
- 測試腳本 folder 僅放 `.yml`、`.ts`、`.xlsx` 等測試資產，不放工具鏈檔案

### 安裝步驟

1. 在 repo 根目錄執行 `install-deps.bat` 或 `npm ci`（同時安裝 `@playwright/test` 與 `@usebruno/cli`）
2. 若需瀏覽器 binary：在 repo 根目錄執行 `npx playwright install`
3. Playwright MCP 由 Cursor 設定啟用，不在腳本 folder 安裝

### Bruno CLI 檢查與使用

在 **repo 根目錄**執行：

```bash
npx bru --version
```

| 結果 | 處理 |
|------|------|
| 顯示版本號 | 可用 `npx bru run <folder>` |
| 失敗 | 執行 `install-deps.bat` 或 `npm ci` 後重試 |
| `bru run` 因缺少 collection 結構失敗 | fallback 至「解析 yml + HTTP」語意執行 |

執行範例（repo 根目錄）：

```bash
npx bru run communityservice/community-statistics-api-plan --env-file <env檔>
```

### 執行前檢查

- 確認 repo 根目錄存在 `package.json` 與 `node_modules`
- 若缺少依賴，**回根目錄安裝**，不可在腳本 folder 另建環境
- Playwright E2E 預設透過 MCP 語意執行；僅在使用者明確要求時才使用 `npx playwright test`（且必須在 repo 根目錄執行）
- Bruno API 優先 `npx bru run`；無法執行時 fallback HTTP 語意執行

---

## 與 aidata 的關係

- 業務語意（API 路徑、錯誤碼、欄位意義）→ 查 `aidata/{kind}/{service}/documents.md`
- 前端 E2E 頁面操作 → 查 `aidata/frontend/{project}/ui-context.md`（若存在）
- 腳本與文件衝突 → 以 `documents.md` 為準修腳本，但不得修改 aidata 本身

服務對應：依 folder 路徑中的服務名稱，grep `aidata/webapi/_index.md`、`aidata/frontend/_index.md`、`aidata/service/_index.md` 確認 kind 與路徑。
