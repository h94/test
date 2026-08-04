# 建立 Killer 周期設定

## 1. 場景目的

讓後台管理員為特定遊戲類型（gameType）的 Killer 競猜模式，建立一個新的活動週期。此流程接收週期的時間區間設定，透過下游 `predictservice` 將週期資料寫入 Cassandra `predict.activities_cycles` 表，供後續競猜結算與排名使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/predict/killer/cycles/{gameType}` | 建立 Killer 競猜週期設定 |

---

## 3. 流程總覽

1. 後台前端發送 POST request，包含 Killer 週期的 JSON 設定（`startdate`, `starttime`, `enddate`, `endtime` 等）。
2. `PriceBackendService` 的 `PredictController` 接收請求，進行基本驗證（身分認證、參數格式）。
3. 呼叫 `PredictService`（或對應的 Service 層邏輯），組裝下游 API 所需的模型。
4. 透過 `IPredictProvider` 呼叫下游 `predictservice` REST API。
5. 下游 `predictservice` 將資料寫入 Cassandra `predict.activities_cycles` 表。
6. 成功後回傳 HTTP 200；失敗則回傳對應的錯誤碼與訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `PredictController.CreateKillerCycle` | 接收 `gameType` 與 request body。 |
| 2 | Service | `PredictService.CreateKillerCycleAsync` | 轉換 request DTO 為下游模型，呼叫 Provider。 |
| 3 | Provider | `PredictProvider.CreateKillerCycle` | 呼叫下游 `predictservice` REST API。 |
| 4 | Transfer | `KillerCycleDTO` | 用於 API 之間資料傳遞的物件。 |

> **需人工確認**：具體的 Controller / Service / Provider 類別與方法名稱，需根據實際程式碼證據確認。目前為基於命名慣例的合理推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `predict.activities_cycles` | Write (INSERT) | 儲存新建立的 Killer 週期設定。 |

> 注意：`PriceBackendService` 本身不直接存取 DB，所有操作均透過下游 `predictservice` 完成。

---

## 6. 重要規則

- **權限限制**：此 API 需要驗證（`需要驗證: ✅`），僅後台管理員可操作。
- **不可修改欄位**：`predict.activities_cycles` 表中的 `site`, `activityevent`, `cid` 為複合主鍵，建立時設定後不可更新。
- **時間欄位限制**：`startdate`, `starttime`, `enddate`, `endtime` 由系統根據活動週期設定，不允許 API 直接修改（需人工確認：建立時是否由管理員輸入）。
- **無 Redis / Cache / Queue 使用**：此流程為單純的同步寫入，未使用快取或訊息佇列。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 請求缺少必填欄位（如 `startdate`） | HTTP 400 Bad Request，回傳驗證錯誤訊息。 |
| `gameType` 不在系統支援的範圍內 | 可能回傳 404 Not Found 或參數驗證錯誤，取決於實作方式。 |
| 下游 `predictservice` 呼叫失敗或逾時 | HTTP 502 Bad Gateway 或 500 Internal Server Error，前端應提示操作失敗。 |
| 下游 `predictservice` 回傳業務邏輯錯誤（例如週期時間衝突） | 應該透傳下游的錯誤碼與訊息給前端。 |
| 無效的日期格式 | HTTP 400 Bad Request。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| KILLER_CYCLE_01 | API Test | 以有效的 `gameType` 和正確的週期 JSON 呼叫 API。 | 回傳 200 OK，並可在管理介面查詢到新週期。 |
| KILLER_CYCLE_02 | API Test | 缺少 `startdate` 欄位。 | 回傳 400 Bad Request。 |
| KILLER_CYCLE_03 | API Test | 傳入無效的 `gameType`。 | 回傳 400 或 404。 |
| KILLER_CYCLE_04 | Integration Test | 模擬下游 `predictservice` 回傳 500 錯誤。 | BFF 層應回傳 502 或 500，不可 crash。 |
| KILLER_CYCLE_05 | Permission Test | 未帶任何認證資訊呼叫 API。 | 回傳 401 Unauthorized。 |

---

## 9. 高風險區域

- **跨服務資料同步**：此為同步寫入，若下游 `predictservice` 成功寫入 DB 後 BFF 回應超時，前端可能認為失敗而重試，導致重複建立。下游應考慮冪等性（Idempotency）。
- **無 Transaction**：跨服務的 REST 呼叫沒有分散式交易機制，需仰賴下游服務自身的資料一致性保證。
- **時間格式校驗**：需確保前後端與下游服務對日期時間字串格式的認知一致，避免因格式錯誤建立出無效的週期。

---

## 10. 常見錯誤

- **新人容易犯錯**：將後台 API 的參數驗證邏輯全部放在 Controller 層，導致 Service 層被略過直接呼叫 Provider。
- **AI 容易誤解**：誤以為此服務直接寫入 `predict.activities_cycles` 表，實際上它完全透過下游 `predictservice` 的 REST API 操作。
- **常見漏檢查項目**：未在 BFF 層對 request body 做基本的格式與必填欄位驗證，直接將錯誤資料轉發至下游服務。
- **常見錯誤流程**：僅以 BFF 層的 HTTP 狀態碼判斷成功與否，未正確映射與傳遞下游服務的業務錯誤碼。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README: `POST /api/v1/predict/killer/cycles/{gameType}` |
| DB | db/predict.md: `predict.activities_cycles` table schema |
| DB Rule | db/predict-detail.md: `site`, `activityevent`, `cid` 建立後不允許後續更新。 |
| Service Dependency | README: 相依於 `predictservice`。 |
| Auth | README: 此路由需要驗證 (`✅`)。 |