# 更新策略結果

## 1. 場景目的
策略分析模組完成一輪分析後，將執行結果回寫至預測服務，更新策略投注日誌的最終狀態。此流程由 `pricebackendservice` 代理後台操作，為內部服務間的非同步回調。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/strategies/result` | 策略分析模組回寫執行結果 |

---

## 3. 流程總覽

1. 策略分析模組完成計算，準備更新策略日誌結果。
2. 調用 `PUT /api/v1/strategies/result`，傳入 `strategy_bet_log` 的 ID 與結果。
3. `predictservice` 驗證請求合法性（內部服務授權）。
4. 根據 ID 寫入 `predict.strategy_bet_log` 的 `result` 欄位。
5. 回傳操作成功確認。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `StrategyController` | 接收 `PUT /api/v1/strategies/result` 請求 |
| 2 | Provider | `StrategyProvider` | 驗證內部服務授權，解析請求參數 |
| 3 | Service | `StrategyService` | 調用資料層更新策略結果 |
| 4 | Data | `PredictDataService` | 執行 Cassandra UPDATE `strategy_bet_log.result` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `predict.strategy_bet_log` | Update | 寫回策略執行結果至 `result` 欄位 |

---

## 6. 重要規則

- **權限限制**：僅內部服務（如 `pricebackendservice`）可呼叫，不對外開放。
- **欄位限制**：`strategy_bet_log.result` 僅可由策略執行模組寫入，外部 API 不可直接修改。
- **不可暴露資料**：`strategy_bet_log.result` 為內部策略紀錄，對外 API 不回傳。
- **不可修改欄位**：除了 `result` 之外，其他欄位（如 bet 內容、時間）均不可透過此請求修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 請求未經授權（無效的內部服務憑證） | 回傳 `401 Unauthorized` |
| 指定的 `strategy_bet_log` ID 不存在 | 回傳 `404 Not Found` |
| Cassandra 寫入失敗（Timeout/Unavailable） | 回傳 `500 Internal Server Error`，建議觸發重試機制 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| STG-001 | API Test | 合法請求更新策略結果 | `200 OK`，DB 中 `result` 已更新 |
| STG-002 | Permission Test | 無效的內部服務 Token | `401 Unauthorized` |
| STG-003 | Flow Test | 模擬 Cassandra 寫入失敗 | `500 Internal Server Error` |

---

## 9. 高風險區域

- **高風險 Table**：`predict.strategy_bet_log`，result 欄位直接影響策略分析的後續決策，不可被非法篡改。
- **高風險 API**：`PUT /api/v1/strategies/result`，需嚴格驗證呼叫來源與授權。
- **Idempotency**：重複請求可能導致結果被覆寫，需確認業務上是否允許最終一致性。

---

## 10. 常見錯誤

- ❌ 允許外部使用者或前台 API 呼叫此端點，跳過內部授權檢查。
- ❌ 誤將 `strategy_bet_log` 中其他欄位（如 bet 金額）一併更新，違反業務規則。
- ❌ 未處理 Cassandra 的冪等性，導致離線重試時重複寫入。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `PUT /api/v1/strategies/result` (README.md) |
| DB | `predict.strategy_bet_log` (predict-detail.md) |
| Rule | `result` 欄位僅由策略執行模組寫入 (predict-detail.md) |
| Rule | 內部服務可呼叫，需驗證 (README.md 服務相依) |

---

## 建議補充

- **需人工確認**：此 API 的具體 Request/Response Schema 及冪等性設計尚未在現有文件中揭露。
- **建議新增測試**：高併發情境下的寫入衝突測試。