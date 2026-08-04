# 查詢預測結果

## 1. 場景目的
讓使用者查詢自己在特定比賽中的預測投注結果，包含該注單的最終輸贏狀態（WinLoss）與盈虧點數（ProfitPoint）。此流程是一個純查詢操作，不涉及下注或結算的業務邏輯變更。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/Predict` | 查詢使用者在指定比賽的預測注單結果 |

---

## 3. 流程總覽
1. 前端呼叫 `GET /api/Predict`，傳入使用者帳號（Account）與比賽識別參數。
2. `PredictController` 接收請求，調用 `PredictService` 進行查詢。
3. `PredictService` 組合查詢條件，透過 `PredictDataProvider` 從 `CommunityPredictBet` 與 `PredictBetResult` 兩張表撈取資料。
4. 服務層將取得的原始注單與結算結果進行組合，產出包含 `WinLoss` 與 `ProfitPoint` 的 `PredictResult` 物件。
5. 回傳最終的預測結果列表給前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `PredictController.GetPredicts` | 接收 HTTP GET 請求，呼叫 Service 層 |
| 2 | Service | `PredictService.GetPredictResult` | 組合查詢參數，呼叫 Provider 取得原始資料，並進行結果組合 |
| 3 | Provider | `PredictDataProvider.GetPredictsByIds` | 執行 SQL 查詢，從 `CommunityPredictBet` 與 `PredictBetResult` 關聯撈取資料 |
| 4 | Service | `PredictService.GetPredictResult` | 將取得的資料對應至 `List<PredictResult>`，過濾並排序後回傳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `CommunityPredictBet` | Read | 查詢使用者的投注記錄，取得注單ID、玩法、盤口、賠率等 |
| DB | `PredictBetResult` | Read | 查詢結算結果，取得輸贏狀態（WinLoss）與盈虧點數（ProfitPoint） |

- **無 Redis / Cache 使用**
- **無 Queue / Kafka 使用**

---

## 6. 重要規則
- **狀態過濾**：查詢結果僅包含 `Status` 為 `2`（已結算）的注單，才會展示 `WinLoss` 與 `ProfitPoint` 給前端。
- **使用者隔離**：查詢時強制帶入 `Account`，使用者只能查詢自己的預測結果。
- **不可暴露資料**：`PredictBetResult` 中的內部結算邏輯欄位（如 `SettleTime`、`SettleOperator`）不應直接回傳給前端。
- **結果不可修改**：此流程為純查詢，不允許對 `CommunityPredictBet` 或 `PredictBetResult` 進行任何寫入或更新。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 傳入不存在的比賽ID（GID） | 回傳空列表，不報錯 |
| 使用者在該比賽無任何投注記錄 | 回傳空列表，不報錯 |
| `PredictBetResult` 中無對應的結算資料（尚未結算） | 該筆注單的 `WinLoss` 與 `ProfitPoint` 為預設值或不出現 |
| 資料庫查詢逾時 | 回傳 HTTP 500 內部伺服器錯誤 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | API Test | 傳入有效的 Account 與 GID，存在已結算注單 | 回傳 200，列表包含 WinLoss 與 ProfitPoint |
| T2 | API Test | 傳入無投注紀錄的 Account | 回傳 200，列表為空 |
| T3 | API Test | 查詢尚未結算的比賽 | 回傳 200，列表為空或結果欄位為空值 |
| T4 | Permission Test | 嘗試查詢其他使用者的結果（若 API 設計為強制帶入 Account） | 需人工確認：目前 API 直接使用傳入的 Account，無強制比對 AuthKey，此為高風險 |

---

## 9. 高風險區域
- **權限驗證缺失**：目前 `GetPredicts` 方法直接使用請求中的 `Account` 進行查詢，未與驗證後的 AuthKey 綁定。理論上使用者可以傳入他人帳號查詢結果。
- **資料一致性**：`CommunityPredictBet` 與 `PredictBetResult` 分屬不同表，若結算程序非原子性，可能出現注單存在但無結算結果的狀況。

---

## 10. 常見錯誤
- **誤解 Status 意義**：新人或 AI 可能認為查詢會返回所有狀態的注單，但實際上只有 `Status=2` 的注單才會包含有意義的 WinLoss 與 ProfitPoint。
- **混淆表格用途**：容易將 `CommunityPredictBet` 當作純記錄表，忽略 `PredictBetResult` 才是結算結果的主要來源。
- **忽略權限問題**：輕易相信前端傳入的 `Account` 參數，未在服務端進行身份比對。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `PredictController.GetPredicts` |
| Service | `PredictService.GetPredictResult` |
| Provider | `PredictDataProvider.GetPredictsByIds` |
| DB Table | `CommunityPredictBet`, `PredictBetResult` |
| Model | `PredictResult` (包含 WinLoss, ProfitPoint) |
| 狀態判斷 | `PredictService` 中對 `Status=2` 的過濾邏輯 |

---

## 12. 建議新增事項
- **建議新增權限規則**：在 `PredictService` 中，應從 `GameUserInfo`（透過 AuthKey）取得實際登入的 `Account`，再與請求的 `Account` 進行比對，防止越權查詢。
- **建議新增測試**：建立一個 Integration Test，驗證當 `PredictBetResult` 中無對應 ID 時，回傳的 `WinLoss` 與 `ProfitPoint` 應為 `null` 或 `0`。