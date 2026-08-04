# 測試計畫規格 (TEST_PLAN_SPEC)

由 `@test-maker` 觸發時載入。定義 `testplan.md`、xlsx 用例表、腳本產出的格式與 Gate 規則。

---

## ⚡ 關鍵規則速查

| 規則 | 說明 |
|------|------|
| Phase 順序 | 訪談 → testplan.md → ⛔ 確認 → xlsx → ⛔ 確認 → 腳本 |
| ticketId | **必須向使用者詢問**；禁止自行編造或從檔名推斷 |
| 輸入來源 | 使用者訪談、aidata、testscripts 既有資產、可選 `./_plans/{ticketId}.md` |
| 禁止來源 | **不使用 Jira、Confluence** 作為需求輸入 |
| 待確認問題 | **永遠列在 testplan.md 最後一節**；有 ⬜ 且未接受風險 → Gate fail |
| E2E 禁止模糊 | Toast / Dialog 須寫明完整文案，禁止「顯示成功」 |
| 腳本格式 | Bruno / Playwright 依 `testing-rules.md` |

---

## 適用類型

| 類型 | 說明 | 典型產物 |
|------|------|----------|
| API | WebAPI / BFF 端點驗證 | Bruno `.yml` |
| E2E | 前端頁面操作 | Playwright `.spec.ts` |
| 資料驗證 | DB / 爬蟲比對 | 僅 xlsx（預設不產腳本） |
| 混合 | 跨服務 | xlsx 多 Sheet + 多 folder 腳本 |

---

## 目錄慣例

```
{project}/_testcases/{ticketId}/testplan.md
{project}/_testcases/{ticketId}/{ticketId}-testcases.xlsx
{service}/_tempscripts/{ticketId}/*.yml
{service}/_tempscripts/{ticketId}/Version.yml
{frontend}/_tempe2e/{ticketId}/*.spec.ts
```

`{project}` 為主要功能歸屬（如 `newlottery`）；腳本 folder 第一段為服務名（如 `memberserviceTest`）。

---

## Test ID 命名

| 前綴 | 用途 | 範例 |
|------|------|------|
| `R-{模組}{序號}` | API / 整合 | `R-B1`、`R-N4` |
| `E2E-{模組}-{TYPE}-{序號}` | 前端 E2E | `E2E-NOTIF-01`、`E2E-FORUM-ERR-01` |
| `DATA-{來源}-{序號}` | 資料驗證 | `DATA-NAP-01` |

**TYPE**：`01` Happy、`ERR` Error、`VAL` Validation、`EDGE` Edge。

xlsx「測試項目」前綴：`[正確場景]`、`[邊界場景]`、`[錯誤場景]`。

---

## testplan.md 模板

章節順序固定；**§12 待確認問題永遠在最後**。

```markdown
# {ticketId} 測試計畫

## 1. 基本資訊

| 欄位 | 內容 |
|------|------|
| ticketId | {使用者提供} |
| 功能摘要 | |
| 測試環境 | SIT / UAT / 本機 |
| 日期 | |

## 2. 測試目標與範圍

### In Scope

-

### Out of Scope

-

## 3. 測試策略

| 層級 | 類型 | 工具 | folder | 用例數（預估） |
|------|------|------|--------|:------------:|
| | API | Bruno | | |
| | E2E | Playwright | | |
| | 資料 | 人工/SQL | | |

## 4. 參考文件

- aidata：`aidata/{kind}/{service}/documents.md`
- 可選 Plan：`./_plans/{ticketId}.md`
- 參考 testcase / 腳本：{路徑}

## 5. 測試環境與 Fixture

| Fixture ID | 說明 | 建立方式 | 用於案例 |
|------------|------|----------|----------|
| FIX-01 | | | |

## 6. 用例清單（Master List）

| Test ID | 類型 | 模組 | 摘要 | 優先級 | 腳本類型 |
|---------|------|------|------|:------:|----------|
| | Happy | | | P0 | Bruno / Playwright / manual |

**腳本類型**：`Bruno` | `Playwright` | `manual` | `db-check`

## 7. API 測試設計（若適用）

| 端點 | Method | Happy | Error | Edge |
|------|--------|:-----:|:-----:|:----:|
| | | | | |

## 8. E2E 測試設計（若適用）

### 8.1 頁面與路由

| 頁面 | 路由 |
|------|------|
| | |

### 8.2 Locator 策略

優先：`data-testid` > `id` > `getByRole` + 文案。

### 8.3 Toast / Dialog 文案

| 情境 ID | 觸發 | title | message | type |
|---------|------|-------|---------|------|
| TOAST-01 | | | | error / success |

## 9. 資料驗證設計（若適用）

| 檢查點 | 資料來源 | 驗證方式 |
|--------|----------|----------|
| | SQL / 比對 | |

## 10. 腳本產出計畫

| 類型 | 輸出路徑 | 命名規則 |
|------|----------|----------|
| Bruno | `{service}/_tempscripts/{ticketId}/` | `R-{n} {Endpoint} {Scenario}.yml` |
| Playwright | `{frontend}/_tempe2e/{ticketId}/` | `E2E-{nn} {feature}.spec.ts` |

## 11. Test Plan Gate 自檢

（JSON，見下方 Gate 規範）

## 12. 待確認問題

> ⚠️ **本節為計畫書最後一節。** 所有未決事項集中於此。
> 有 ⬜ 且使用者未明示接受風險前，Gate 不得 pass。

| # | 問題 | 影響範圍 | 狀態 | 備註 |
|---|------|----------|------|------|
| 1 | | | ⬜ 待確認 | |

**狀態**：⬜ 待確認 / 🔄 討論中 / ✅ 已確認
```

---

## xlsx 用例表 Schema

檔名：`{ticketId}-testcases.xlsx`

依測試類型使用 **一個或多個 Sheet**：

### Sheet：`E2E`（前端）

| 列 | 欄 A | 欄 B | 欄 C | 欄 D | 欄 E | 欄 F |
|----|------|------|------|------|------|------|
| 1 | 專案的測試名稱 | {ticketId} {功能名} | | | | |
| 2 | 功能敘述 | {完整描述} | | | | |
| 3 | NO. | 測試項目 | 設置條件 | 測試步驟 | 預期結果 | 實際結果 |
| 4+ | 1 | `[正確場景] E2E-xxx-01 …` | FIX-… | 步驟（可換行） | 具體斷言 | （執行時填） |

### Sheet：`API`（整合 / API）

| 列 | 欄 A | 欄 B | 欄 C | 欄 D | 欄 E | 欄 F | 欄 G |
|----|------|------|------|------|------|------|------|
| 1 | 測試名稱 | | {ticketId} {功能} | | | | |
| 2 | 功能 | | {描述} | | | | |
| 3 | NO. | 檢查點 | | | 設置條件 | 預期結果 | 實際結果 |
| 4+ | 1.0 | 取得賽事 | show_detail=False | | 資料存在 | 回傳基本欄位正確 | |

- 同一「檢查點」下多列共用 NO. 大項（1.0、2.0…），子項填在 C/D 欄。

### Sheet：`DataValidation`（資料 / 爬蟲）

| 列 | 欄 A | 欄 B | 欄 C | 欄 D | 欄 E | 欄 F | 欄 G |
|----|------|------|------|------|------|------|------|
| 1 | 測試名稱 | | | {描述} | | | |
| 2 | 功能 | | | {描述} | | | |
| 3 | NO. | 檢查點 | | | 設置條件 | 預期結果 | 實際結果 |
| 4+ | 1.0 | 足球SC | pregame | 驗證項目 | SQL / 條件 | 多行預期 | |

---

## 腳本產出對照

| xlsx 腳本類型 | 產出 | 不產出 |
|---------------|------|--------|
| Bruno | `.yml` + `Version.yml` | — |
| Playwright | `.spec.ts` | — |
| manual / db-check | — | 僅 xlsx |

Bruno 要點（詳見 `testing-rules.md`）：

- `info.name` 對齊 Test ID 與情境
- `info.seq`：login / 前置資料優先
- URL / body 用 `{{var}}`
- assertion 對齊 xlsx「預期結果」

Playwright 要點：

- `test('…')` 標題含 Test ID
- 步驟對齊 xlsx「測試步驟」
- Toast 文案對齊 testplan §8.3

---

## Test Plan Gate

Phase 3 產出 testplan.md 後必做自檢：

```json
{
  "status": "pass",
  "unresolved_count": 0,
  "issues": []
}
```

**fail 條件（任一即 fail）：**

- §12 有 ⬜ 且使用者未明示接受風險
- In Scope 功能無 Happy Path
- API 缺 Error Path（404、驗證失敗、業務錯誤）
- E2E Toast / Dialog 文案模糊
- Test ID 重複
- 腳本輸出路徑不符合目錄慣例

**issues 格式：**

```json
{
  "status": "fail",
  "unresolved_count": 1,
  "issues": [
    {
      "section": "12. 待確認問題",
      "reason": "仍有 ⬜ 未確認",
      "evidence": "第 1 項：SIT baseUrl 未提供"
    }
  ]
}
```

---

## 與 @ai-tester 分工

| 階段 | 引導師 | 產物 |
|------|--------|------|
| 設計 | `@test-maker` | testplan.md → xlsx → 腳本 |
| 執行 | `@ai-tester` | 測試報告、ingest-json |

xlsx 由 `@test-maker` 產出；`@ai-tester` 以腳本 folder 為主執行，xlsx 僅作對照參考。
