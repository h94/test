# 查詢體育報表

## 1. 場景目的

供後台管理系統或排程服務查詢已結算的體育收益報表、分潤報表、推薦報表及推薦分潤報表，用於財務對帳或數據分析。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sport/reports/{year}` | 查詢指定年度所有月度收益報表 |
| GET | `/api/v1/sport/reports/{year}/{month}` | 查詢指定月度收益報表 |
| GET | `/api/v1/sport/reportlist/{year}/{month}` | 查詢指定月份所有帳號的分潤報表 |
| GET | `/api/v1/sport/sharereports/{account}` | 查詢指定帳號的所有分潤報表 |
| GET | `/api/v1/sport/recommendreports/{year}` | 查詢指定年度的推薦報表 |

---

## 3. 流程總覽

1. 客戶端（後台/排程服務）發起查詢請求。
2. 驗證請求來源權限。
3. 根據請求參數，從對應的 `payment` keyspace Table 讀取報表資料。
4. 回傳查詢結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SportReportController` | 接收請求，根據路由參數呼叫對應的 Service |
| 2 | Service | `SportReportService` | 呼叫 Data Provider 執行查詢，處理業務邏輯 |
| 3 | Provider | `SportReportDataProvider` | 執行 Cassandra 查詢語句，從對應 Table 取得資料並回傳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `payment.reports_sport` | Read | 查詢年度/月度收益報表。僅查詢 `finishing=true` 的已結算報表。 |
| DB | `payment.sharereports_sport` | Read | 依帳號或月份查詢分潤報表。 |
| DB | `payment.reports_sport_recommend` | Read | 查詢年度推薦報表。 |
| DB | `payment.sharereports_sport_recommend` | Read | 查詢推薦分潤報表。 |

---

## 6. 重要規則

- **權限限制**：所有報表查詢 API 皆需驗證。
- **資料範圍**：`reports_sport` 僅查詢 `finishing=true` 的已結算報表。查詢時 `year`, `month` 為必要的 WHERE 條件。
- **不可暴露資料**：`reports_sport.leaguesunlock` 為內部 JSON 結構，不對前端公開。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求參數不完整（如缺少年份、月份） | 回傳 400 Bad Request |
| 查詢無結果（如查詢尚未結算的報表） | 回傳空陣列或 404 Not Found |
| Cassandra 查詢超時或失敗 | 回傳 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| RPT-01 | API Test | 查詢特定年度報表（存在已結算數據） | 成功回傳該年度所有月份的報表清單 |
| RPT-02 | API Test | 查詢特定月度報表（狀態為未結算） | 回傳空值或 404 |
| RPT-03 | Flow Test | 查詢不存在帳號的分潤報表 | 成功回傳空陣列 |
| RPT-04 | API Test | 查詢報表時未帶入 Token | 回傳 401 Unauthorized |

---

## 9. 高風險區域

- **資料一致性**：排程服務（`reportservice`）寫入報表資料後，`paymentservice` 必須能立即讀取到最新結果。
- **跨服務依賴**：此場景為典型的唯讀流程，風險較低，但需確保 `reportservice` 正確標記 `finishing=true`。
- **不可修改欄位**：`reports_sport` 的 `finishing=true` 一旦寫入，禁止人工修改，因此查詢端無需擔心狀態回流。

---

## 10. 常見錯誤

- ❌ **查詢報表時未過濾 `finishing=true`**：可能讀取到未完成結算的報表，導致數據不正確。
- ❌ **將 `reports_sport.leaguesunlock` 直接回傳給前端**：應在 API 層過濾掉此內部欄位。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README `### 體育報表` |
| DB | payment-detail.md `Table：reports_sport` |
| DB Rule | paymentservice-detail.md `月份財報：僅查詢finishing=true` |
| DB Rule | paymentservice-detail.md `reports_sport.leaguesunlock：內部 JSON 結構，不對前端公開` |