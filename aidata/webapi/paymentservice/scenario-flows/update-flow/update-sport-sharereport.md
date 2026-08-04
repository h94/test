# 更新體育分潤報表

## 1. 場景目的

後台管理系統或排程服務更新指定帳號的體育分潤明細，主要用於標記分潤金額已實際發放，或更正分潤資料。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/v1/sport/sharereports/{account}/{year}/{month}/{gameType}/{league}` | 更新特定帳號、年度、月份、遊戲類型及聯賽的分潤報表 |

---

## 3. 流程總覽

1. 接收外部 PUT 請求，包含路徑參數 `account`, `year`, `month`, `gameType`, `league` 及請求主體 (Request Body)。
2. 驗證請求方的管理權限 (需人工確認具體驗證機制)。
3. 根據路徑參數組合出 `sharereports_sport` 的完整主鍵。
4. 查詢 Cassandra `payment.sport_share_reports` 確認該筆分潤記錄是否存在。
5. 驗證請求主體中的更新內容，特別是 `payout` 狀態的變更是否合規。
6. 將更新寫入 `payment.sport_share_reports`。
7. 回傳操作成功與否的結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SportController` (推測) | 接收 HTTP PUT 請求，解析路徑與請求主體。 |
| 2 | Transfer | `UpdateSportShareReportIn` (推測) | 將請求參數轉換為內部傳輸物件。 |
| 3 | Service | `SportReportService` (推測) | 組合主鍵，呼叫 Provider 查詢現有資料。 |
| 4 | Provider | `SportShareReportDataProvider` (推測) | 執行 `SELECT` 查詢 `sharereports_sport`。 |
| 5 | Service | `SportReportService` (推測) | 驗證請求資料與現有資料，檢查 `payout` 狀態變更邏輯。 |
| 6 | Provider | `SportShareReportDataProvider` (推測) | 執行 `UPDATE` 寫入 `sharereports_sport`。 |
| 7 | Controller | `SportController` (推測) | 回傳 HTTP 200 OK。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `payment.sport_share_reports` | Read | 根據主鍵查詢現有分潤記錄 |
| DB | `payment.sport_share_reports` | Write | 更新分潤明細或 payout 狀態 |

---

## 6. 重要規則

- **權限限制**：此 API 需要驗證，僅限於管理後台或特定排程服務呼叫。
- **狀態值限制**：`payout` 欄位為 boolean，`false` 代表未發放，`true` 代表已發放。狀態一旦標記為 `true` 後，不應再被改回 `false`。
- **不可修改欄位**：分潤報表的主鍵（`account`, `year`, `month`, `game_type`, `league`）不可更新。
- **寫入限制**：只有 `paymentservice` 可以變更 `payout` 狀態。
- **高風險操作**：將 `payout` 從 `false` 變更為 `true` 可能觸發實際的財務發放流程或通知，需確認 (需人工確認)。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求路徑的主鍵組合無效 (如 year 非正整數) | 400 Bad Request |
| 無效的驗證或權限不足 | 401 Unauthorized / 403 Forbidden |
| 欲更新的分潤報表記錄不存在 | 404 Not Found |
| 請求將已發放 (`payout=true`) 的報表改為未發放 | 422 Unprocessable Entity 或拒絕更新 |
| Cassandra 寫入失敗或逾時 | 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-01 | API Test | 以合法參數更新已存在的分潤報表 | 200 OK，資料庫記錄已更新 |
| UT-02 | API Test | 更新不存在的分潤報表 | 404 Not Found |
| UT-03 | Flow Test | 嘗試將 `payout=true` 的記錄改回 `false` | 更新失敗 |
| UT-04 | Permission Test | 未攜帶有效 token 呼叫 API | 401 Unauthorized |
| UT-05 | Permission Test | 使用無管理權限的 token 呼叫 API | 403 Forbidden |

---

## 9. 高風險區域

- **高風險 table**：`payment.sport_share_reports`。此表直接關聯到對用戶的實際分潤發放，錯誤的寫入可能導致財務損失。
- **高風險 API**：`PUT /api/v1/sport/sharereports/{account}/{year}/{month}/{gameType}/{league}`。
- **狀態流轉**：`payout` 從 `false` 變更為 `true` 是不可逆的關鍵操作，需確保業務邏輯正確無誤。

---

## 10. 常見錯誤

- ❌ **重複標記已發放**：未檢查當前 `payout` 狀態就直接更新為 `true`，可能導致重複發放分潤。
- ❌ **越權操作**：未正確配置 API 的權限驗證，使得一般使用者也能呼叫此後台 API。
- ❌ **更新不存在的報表**：直接執行 `UPDATE` 而不先 `SELECT` 確認記錄存在，可能導致非預期的錯誤或無回應。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `PUT /api/v1/sport/sharereports/{account}/{year}/{month}/{gameType}/{league}` |
| DB | `payment.sharereports_sport` |
| 規則 | `paymentservice-detail.md` Table：sharereports_sport 的 `payout` 欄位說明 |
| 規則 | `payment-detail.md` 寫入限制 `只有 paymentservice 可以變更 payout` |
| 流程 | OpenAPI 3.0 定義的路徑與方法 (推測 Controller 層) |
| Code | 需要進一步分析 `SportController` 和 `SportReportService` 以確認確切的 Service / Provider 名稱。 |