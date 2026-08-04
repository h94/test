# 合併競猜

## 1. 場景目的

提供後台管理員將同一遊戲類型（gameType）下的多筆競猜下注記錄，合併至單一目標記錄的操作。主要為了修正因系統錯誤或用戶操作導致的重複、分散的下注數據，確保後續報表與結算的正確性。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/predict/mergepredicts/{gameType}` | 合併指定遊戲類型下的競猜記錄 |

---

## 3. 流程總覽

1. 後台管理員發起合併請求，指定 `gameType` 與 `MergePredictsTransfer` 物件。
2. `PriceBackendService` 驗證請求參數與權限。
3. `PriceBackendService` 呼叫下游 `predictservice` 的合併 API。
4. `predictservice` 根據請求中的來源注單 ID 與目標注單 ID，執行合併邏輯（需人工確認：具體為金額加總、記錄關聯或狀態更新）。
5. 操作完成後，`predictservice` 回傳結果給 `PriceBackendService`。
6. `PriceBackendService` 回傳成功結果給前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `MergePredictsController` (推測) | 接收 POST 請求，參數包含 `gameType`, `MergePredictsTransfer` |
| 2 | Transfer | `MergePredictsTransfer` | 定義合併請求的傳輸物件（如來源與目標注單 ID 列表） |
| 3 | Service | `PredictService` (推測) | 呼叫下游 `predictservice` 的合併 API |
| 4 | External Service | `predictservice` (下游微服務) | 接收合併請求，執行具體的數據庫操作 |
| 5 | DB | `predict` keyspace | 更新相關的 `betpool_bets` 或其他參與合併的表 |
| 6 | Service | `PredictService` | 接收下游回傳的結果 |
| 7 | Controller | `MergePredictsController` | 回傳操作結果給客戶端 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.betpool_bets` | Read | 讀取要被合併的來源下注記錄 |
| DB | `predict.betpool_bets` | Update | 更新目標下注記錄的金額、狀態等 |
| DB | 其他 predict 表 | Write / Update | 需人工確認：可能更新 `betpool_games`、`activities_record` 等相關表 |

> **注意**：`PriceBackendService` 本身不直接存取資料庫，所有 DB 操作均在 `predictservice` 內部執行。根據現有 `predict` keyspace 的定義，`betpool_bets` 的 `profitzcoin`, `winlose` 等欄位僅允許結算服務更新；但在合併場景中，`betzcoin`（下注金額）的加總是否需要更新，或是僅做邏輯關聯，**需人工確認**。

---

## 6. 重要規則

- **權限限制**：需通過 ECFramework 驗證，僅允許具備後台管理權限的用戶調用。
- **不可修改欄位**：合併後的記錄，其 `id`、`addtime` 等系統自動生成欄位不可變更。
- **Transaction 規則**：下游 `predictservice` 執行合併時，必須保證原子性，避免部分記錄更新失敗導致數據不一致。
- **狀態值限制**：只能合併尚未結算（`payout = false`）且狀態為有效（如 `status < 2`）的投注記錄（需人工確認）。
- **跨服務規則**：`pricebackendservice` 僅負責轉發請求，不可直接操作 `predict` keyspace。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 帳號無後台管理權限 | 回傳 401 Unauthorized 錯誤 |
| `gameType` 參數為空或無效 | 回傳 400 Bad Request，提示參數錯誤 |
| 指定的來源或目標注單 ID 不存在 | 下游 `predictservice` 回傳錯誤，`PriceBackendService` 回傳相應錯誤代碼 |
| 嘗試合併狀態不允許的記錄（如需人工確認） | 回傳業務錯誤，如 “該注單狀態不允許合併” |
| `predictservice` 服務不可用或超時 | 回傳 502 Bad Gateway 或 504 Gateway Timeout |
| `predictservice` 內部資料庫寫入失敗 | 回傳 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | Permission Test | 無認證資訊請求 API | 回傳 401 Unauthorized |
| T02 | API Test | 傳入無效的 `gameType` | 回傳 400 Bad Request |
| T03 | API Test | 傳入空的來源 ID 列表 | 回傳 400 Bad Request |
| T04 | Flow Test | 正常合併兩筆有效注單 | 回傳 200 OK，後續查詢顯示金額已合併至目標注單 |
| T05 | Integration Test | `predictservice` 回應失敗 | `PriceBackendService` 正確轉發錯誤訊息 |
| T06 | Integration Test | `predictservice` 無法連線 | 回傳 502/504，並記錄錯誤日誌 |

---

## 9. 高風險區域

- **跨服務資料同步**：合併邏輯完全依賴 `predictservice`，若 `predictservice` 的實作有誤或回應格式變更，將直接導致功能失敗。
- **數據一致性**：合併操作涉及金額的增減，若執行過程中發生異常，可能導致用戶資產計算錯誤。
- **Transaction**：合併必須是一個原子操作，尤其是在更新 `betpool_bets` 多條記錄時。
- **Idempotency**：同一合併請求不應被重複執行多次，若客戶端因網路問題重試，可能導致金額重複計算。需確認下游如何處理此場景。

---

## 10. 常見錯誤

- **新人容易犯錯**：
    - 誤以為 `pricebackendservice` 會直接操作數據庫，試圖在 BFF 層加入業務邏輯。
    - 未正確理解 `MergePredictsTransfer` 的結構，傳入不符合預期的數據。
- **AI 容易誤解**：
    - 自行想像合併的具體 SQL 操作（如 `SUM`， `DELETE`），但實際的實作邏輯在 `predictservice` 中，此處無法得知。
    - 誤以為 `predictservice` 回傳的模型與 `pricebackendservice` 的 DTO 完全相同。
- **常見漏檢查項目**：忘了檢查 `predictservice` 的回傳狀態碼，將下游錯誤誤當成成功回應。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `README.md` -> 競猜管理 -> `POST /api/v1/predict/mergepredicts/{gameType}` |
| Code | `webapi/pricebackendservice/semantic` -> Controller: `MergePredictsController` (推測) |
| Code | `webapi/pricebackendservice/semantic` -> Transfer: `MergePredictsTransfer` (推測) |
| DB | `db/predict.md`, `db/predict-detail.md` -> `betpool_bets` 表結構 |
| 服務相依 | `README.md` -> 服務相依 -> `predictservice` |
| 規則 | `db/predict-detail.md` -> `betpool_bets.profitzcoin` & `winlose` 僅由結算服務更新 |