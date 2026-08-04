# 更新計算日誌結果

## 1. 場景目的

此場景描述當系統或後台管理員在完成一輪週度計算（例如週報表結算、活動排行計算）後，調用此 API 將執行結果寫入計算日誌，供後續查詢與稽核使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/v1/reports/calculalogs/{weekID}/result` | 更新指定週期的計算日誌結果。需要驗證。 |

---

## 3. 流程總覽

1. 接收請求，從路徑參數取得 `weekID`，從請求主體取得 `result`（推測為 JSON 格式的字串或物件，需人工確認）。
2. 通過 ECFramework.ECService 驗證請求身分與權限。
3. 調用 Service 層，根據 `weekID` 組裝寫入邏輯。
4. 透過 Provider 層將 `result` 資料寫入 Cassandra 的 `predict.calculate_logs` 表。
5. 日誌寫入 Kafka 的 `applogs` Topic。
6. 回傳操作成功結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `ReportsController`（推測） | 接收 `PUT` 請求，解析 `weekID` 與 request body。 |
| 2 | Controller / Validator | ECFramework 驗證機制 | 驗證請求的 JWT 或內部 token 是否合法。 |
| 3 | Service | `CalculateLogService.UpdateResult`（推測） | 執行業務邏輯，可能包含格式校驗，再調用 Provider 寫入。 |
| 4 | Provider | `CalculateLogProvider`（推測） | 組裝 Cassandra 的 INSERT 或 UPDATE 語句，執行 DB 操作。 |
| 5 | Service / Provider | Kafka logging | 操作完成後，將執行記錄發送至 Kafka 的 `applogs` Topic。 |

> **需人工確認**：實際的 class 名稱與方法簽名，需對照原始碼才可確定。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `predict.calculate_logs` | Write | 將此次計算的 `result` 寫入對應的 `week_id` 記錄。 |
| Queue (Kafka) | `applogs` | Publish | 記錄此次 API 操作的行為日誌。 |

> **需人工確認**：此流程中是否使用 Redis 快取或更新其他資料表。依現有資訊推測，它為單純的更新操作，無快取互動。

---

## 6. 重要規則

- **權限限制**：所有報表相關 API (包含此 API) 皆需要驗證，推測僅允許後台管理員角色調用。
- **DB 寫入規則**：此操作可能為 **Upsert** 行為。若 `week_id` 已存在，則更新其 `result` 欄位；若不存在，則新增一筆記錄。
- **不可暴露資料**：回傳結果不應包含寫入的完整 `result` 細節，僅需回傳成功與否的狀態。
- **Status 值限制**：計算日誌的寫入應是冪等的，重複提交相同的 `weekID` 和 `result` 不應導致錯誤或產生重複記錄。
- **欄位校驗**：`result` 內容需為有效格式，以確保儲存的一致性。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求未包含合法驗證資訊 | 回傳 `401 Unauthorized`。 |
| 請求包含驗證資訊但權限不足 | 回傳 `403 Forbidden`。 |
| 路徑參數 `weekID` 格式不符預期 | 回傳 `400 Bad Request`，提示參數錯誤。 |
| Request body 中的 `result` 為空 | 回傳 `400 Bad Request`，提示內容不可為空。 |
| Cassandra 寫入失敗或 timeout | 回傳 `500 Internal Server Error`，並記錄錯誤日誌。 |
| Kafka 發佈失敗 | 不影響主要寫入流程，但需記錄錯誤以供後續排查。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-01 | API Test | 使用有效 token 調用 API，提供正確的 `weekID` 與 `result`。 | 回傳 `200 OK`，且 `predict.calculate_logs` 中該 `weekID` 的記錄更新成功。 |
| PT-01 | Permission Test | 使用權限不足的帳號調用 API。 | 回傳 `403 Forbidden`。 |
| FT-01 | Flow Test | 對一個不存在的 `weekID` 進行更新。 | 成功在 `predict.calculate_logs` 中新增一筆記錄。 |
| FT-02 | Flow Test | 對一個已存在的 `weekID` 進行更新。 | 該筆記錄的 `result` 欄位被更新為最新值。 |

---

## 9. 高風險區域

- **高風險 Table**：
  - `predict.calculate_logs`：此為計算結果的正式記錄，錯誤的寫入可能導致前台顯示或後續分析失準。
- **Cache consistency**：
  - 無直接快取風險，但若後續查詢 (`GET /api/v1/reports/calculalogs`) 有使用快取，需考慮在此 API 寫入時是否應使快取失效。 **(需人工確認是否有快取機制)**
- **Idempotency**：
  - API 具備冪等性。對相同 `weekID` 重複執行更新，其最終結果皆為最後一次寫入的 `result`，不會產生多筆重複記錄。

---

## 10. 常見錯誤

- ❌ **誤解操作為 INSERT**：此 API 路徑為 `PUT`，語意上應為新增或更新（Upsert），而非單純新增。開發者若以為僅能新增，當 `weekID` 已存在時實作錯誤處理，會導致流程失敗。
- ❌ **遺漏 `result` 欄位校驗**：未對 request body 進行格式和長度校驗，直接寫入 Cassandra，可能寫入無效或損毀的資料。
- ❌ **對外洩漏內部結果**：將寫入的 `result` 原封不動地回傳給客戶端，可能暴露不必要的內部運算資訊。API response 應重新包裝。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `PUT /api/v1/reports/calculalogs/{weekID}/result` |
| DB | `predict.calculate_logs` |
| Code | ReportsController（推測） |
| Code | CalculateLogService.UpdateResult（推測） |
| Queue | Kafka Topic `applogs` |
| 驗證規則 | predictservice-detail.md - 篩選報表 APIs 皆需要驗證 |
| 不可回傳欄位 | predictservice-detail.md - 策略內部紀錄不應暴露 |