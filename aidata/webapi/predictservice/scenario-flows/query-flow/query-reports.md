# 查询筛选报表演算及週报

## 1. 场景目的
提供後台或排程查詢計算日誌、查詢特定日期或帳號的篩選報表、查詢帳號週報表，以及更新計算結果的業務流程。此場景為唯讀查詢輔以少量寫入，主要涉及 Cassandra 上的 `predict` keyspace。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/reports/calculalogs` | 查詢計算日誌 |
| GET | `/api/v1/reports/predictfilterreports/{date}` | 查詢特定日期的篩選報表 |
| GET | `/api/v1/reports/predictfilterreports/accounts/{account}` | 查詢特定帳號的篩選報表 |
| GET | `/api/v1/reports/weeklyreports/{account}` | 查詢特定帳號的週報表 |
| PUT | `/api/v1/reports/calculalogs/{weekID}/result` | 更新特定週期計算結果 |

---

## 3. 流程總覽

1. **接收請求**：Controller 層接收帶有路徑參數（如 `date`、`account`、`weekID`）的 GET/PUT 請求。
2. **權限驗證**：ECFramework 驗證請求的 auth token，確認操作者身份。
3. **資料查詢**：Service 層依據請求參數，構建 Cassandra 查詢語句。
4. **DB 交互**：Provider 層執行對 `predict` keyspace 的讀寫操作。
5. **結果處理**：Service 層將查詢結果轉換為 DTO，確保不回傳敏感欄位。
6. **回傳**：Controller 層將結果封裝為 HTTP 200 回傳；寫入操作則回傳成功狀態。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `ReportController.GetCalculateLogs` | 接收 GET 請求，無參數。 |
| 2 | Service | `ReportService.GetCalculateLogs` | 呼叫 Provider 查詢計算日誌列表。 |
| 3 | Provider | `PredictDataProvider` | 執行 Cassandra `SELECT * FROM predict.calculate_logs`。 |
| 4 | Controller | `ReportController.GetFilterReportsByDate` | 接收 GET 請求，路徑參數 `date`。 |
| 5 | Service | `ReportService.GetFilterReports` | 呼叫 Provider，依 `reportdate` 查詢。 |
| 6 | Provider | `PredictDataProvider` | 執行 `SELECT * FROM predict.predictfilterreports WHERE reportdate = ?`。 |
| 7 | Controller | `ReportController.GetFilterReportsByAccount` | 接收 GET 請求，路徑參數 `account`。 |
| 8 | Service | `ReportService.GetFilterReportsByAccount` | 呼叫 Provider，依 `account` 查詢。（需人工確認索引支持） |
| 9 | Controller | `ReportController.GetWeeklyReports` | 接收 GET 請求，路徑參數 `account`。 |
| 10 | Service | `ReportService.GetWeeklyReports` | 呼叫 Provider，查詢 `predict.weekly_reports`。 |
| 11 | Controller | `ReportController.UpdateCalculateResult` | 接收 PUT 請求，路徑參數 `weekID`。 |
| 12 | Service | `ReportService.UpdateResult` | 驗證 `weekID`，呼叫 Provider 更新。 |
| 13 | Provider | `PredictDataProvider` | 執行 `UPDATE predict.calculate_logs SET result = ? WHERE week_id = ?`。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.calculate_logs` | Read, Update | 查詢計算日誌；更新特定週期的計算結果。 |
| DB | `predict.predictfilterreports` | Read | 依日期或帳號查詢篩選報表。 |
| DB | `predict.weekly_reports` | Read | 查詢特定帳號的週報表。 |
| DB | `member.gameusers` | Read（可能） | 查詢用戶基本信息，需注意不可回傳 `password`, `authkey` 等敏感欄位。 |

**注意**：此查詢流程未使用 Redis 快取或 Kafka 訊息佇列。

---

## 6. 重要規則

- **權限限制**：所有 API 均需通過 ECFramework 身份驗證。
- **不可暴露資料**：
  - 任何關聯到 `member.gameusers` 的查詢，確保不回傳 `password`, `email`（公開 API）, `authkey` 欄位。
  - 報表資料不應包含足以識別個人用戶的敏感財務細節於非對應帳號的查詢中。
- **狀態值限制**：`predict.calculate_logs` 的 `result` 欄位僅可由內部結算排程或管理員透過 API 更新。
- **不可修改欄位**：報表資料為聚合數據，對報表的 GET API 無寫入能力。
- **查詢限制**：對於 `predictfilterreports`，`reportdate` 為分區鍵 (Partition Key)，所有查詢必須攜帶此參數以避免全表掃描。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 查詢不存在的日期或帳號報表 | 返回 HTTP 200，但回傳的資料列表為空。 |
| 權限不足（未攜帶有效 token） | 返回 HTTP 401 Unauthorized。 |
| Cassandra 連線超時或查詢失敗 | 返回 HTTP 500 Internal Server Error，前端應顯示通用錯誤訊息。 |
| PUT 更新結果時，提供的 `weekID` 不存在 | 操作執行，但影響行數為 0，服務應回報成功或有明確的業務錯誤碼。 |
| 以帳號查詢報表時未提供日期分區鍵（若有的話） | 查詢失敗或效能極差，高風險。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| RPT-01 | Flow Test | 查詢某一日期的篩選報表 | 成功回傳該日期的所有報表資料。 |
| RPT-02 | Flow Test | 查詢一個有大量下注歷史帳號的週報 | 成功回傳該帳號的週報資訊。 |
| RPT-03 | API Test | 查詢一個不存在帳號的週報 | 回傳空列表，非報錯。 |
| RPT-04 | Permission Test | 未登入狀態下調用 API | 回傳 401 Unauthorized。 |
| RPT-05 | Integration Test | 後台排程更新某 `weekID` 的計算結果 | 成功寫入，且之後的查詢會反映新結果。 |

---

## 9. 高風險區域

- **高風險 Table**：`predict.predictfilterreports`。若查詢條件不帶 `reportdate` 分區鍵，會導致全表掃描，影響 Cassandra 叢集效能。
- **高風險 API**：`PUT /api/v1/reports/calculalogs/{weekID}/result`。不當的更新可能覆蓋正確的結算結果，需嚴格的權限控制與操作日誌。
- **跨服務資料同步**：無。此流程完全在 `predictservice` 內部及 `predict` keyspace 內完成。

---

## 10. 常見錯誤

- ❌ **新人容易犯錯**：手動拼接 CQL 查詢 `predictfilterreports` 時，忘記在 `WHERE` 子句加上 `reportdate`，導致 Cassandra 拒絕查詢或性能問題。
- ❌ **AI 容易誤解**：錯誤地認為 `predictfilterreports` 和 `weekly_reports` 可以由使用者直接寫入，或與下注流程有實時耦合。這些表由排程任務產生。
- ❌ **常見漏檢查項目**：未確認 `GameUser` 快取是否存在與否，直接查詢 `member` keyspace，可能導致不必要的跨服務依賴。
- ❌ **常見錯誤流程**：更新 `calculate_logs` 的 `result` 欄位時，未經 `weekID` 所有權或狀態校驗，直接執行 UPDATE。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `ReportController` (推測) |
| DB | README: `predict.predict_filter_reports`, `predict.weekly_reports`, `predict.calculate_logs` |
| DB Schema | `predict.weekly_reports` (未在截斷JSON中，但README提及), `predict.calculate_logs` |
| Code | 需人工確認具體 Controller/Service 檔案名稱 (如 `ReportController.cs`, `ReportService.cs`) |
| Rules | predictservice-detail.md: `predictfilterreports` 查詢須依 `reportdate` 過濾 |