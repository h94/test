# 删除策略结果

## 1. 场景目的

清除策略分析所产生的历史数据，包含策略执行记录、下注日志与相关快取。由后台管理端触发，属于高风险资料清理操作。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| DELETE | `/api/v1/strategies` | 刪除策略結果，需要驗證 |

---

## 3. 流程總覽

1. 後台管理員或排程觸發 DELETE 請求。
2. 驗證呼叫方是否具備管理權限（確切權限角色需人工確認）。
3. 依據請求參數（需人工確認具體過濾條件，如策略 ID、日期範圍）清理 Cassandra 中的策略相關紀錄。
4. 若存在對應的 Redis 快取，需同步失效（需人工確認快取 key 規則）。
5. 回傳操作結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `StrategyController` (推測) | 接收 DELETE 請求並轉交 Service |
| 2 | Service | `StrategyService` (推測) | 組合刪除條件，呼叫 Provider 執行資料清理 |
| 3 | Provider | `StrategyDataProvider` (推測) | 對 Cassandra 執行 DELETE 操作 |
| 4 | Service | `StrategyService` (推測) | 若有必要，清除相關 Redis 快取 |
| 5 | Controller | `StrategyController` (推測) | 回傳操作結果 |

> 由於缺少 source code，Service 與 Provider 的具體名稱與方法為推測。需人工確認實際 Class 與 Method 名稱。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.strategy_bet_log` | Delete | 刪除策略下注執行記錄 |
| DB | 其他策略相關表（需人工確認） | Delete | 可能包含策略設定、結果彙總等資料 |
| Redis | 策略相關快取（需人工確認 key，如 `strategy:{id}`） | Delete | 刪除策略結果快取，避免幽靈資料 |

---

## 6. 重要規則

- **權限限制**：僅後台管理員可執行此操作，需通過驗證框架（ECFramework.ECService）。
- **欄位限制**：`strategy_bet_log.result` 在 detail 文件中被規範僅由策略執行模組透過 UPDATE 寫入，且不可暴露給外部 API。本次刪除為整筆記錄移除，符合規範。
- **不可暴露資料**：刪除操作的回傳值（Response）不應包含任何被刪除的策略明細資料（如投注內容、帳號）。
- **Transaction 規則**：Cassandra 不支援傳統 RDBMS 的 Transaction，若需跨表原子性刪除，需在應用層實現補償邏輯（Compensating Transaction）或接受最終一致性。
- **狀態值限制**：無特定狀態流轉限制，此為資料清除而非狀態更新。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 操作者權限不足 | 回傳 401 Unauthorized 或 403 Forbidden |
| 請求參數缺失或格式錯誤 | 回傳 400 Bad Request |
| Cassandra 連線逾時或查詢失敗 | 回傳 500 Internal Server Error，並記錄錯誤日誌 |
| 欲刪除的資料不存在 | 回傳 200 OK（冪等操作，重複刪除視為成功）或 404 Not Found（需人工確認） |
| Redis 快取清除失敗 | 記錄錯誤日誌，不影響主流程回應（可接受快取殘留，依賴 TTL 最終清除） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| FT-DEL-STRATEGY-01 | Permission Test | 一般使用者呼叫刪除 API | 回傳 403 |
| FT-DEL-STRATEGY-02 | API Test | 管理員不帶任何參數呼叫 | 根據設計，可能回傳 400 或刪除所有資料（需人工確認） |
| FT-DEL-STRATEGY-03 | Integration Test | 管理員指定存在的策略 ID 進行刪除 | 回傳 200，DB 中對應紀錄被移除 |
| FT-DEL-STRATEGY-04 | Flow Test | 刪除成功後，檢查相關 Redis 快取 | 相關策略快取應不存在或已被標記失效 |
| FT-DEL-STRATEGY-05 | API Test | 刪除不存在的策略 ID | 回傳 200 (冪等) 或 404 (需人工確認) |

---

## 9. 高風險區域

- **高風險 Table**：`predict.strategy_bet_log`。誤刪可能導致策略分析報表數據失真。
- **高風險 API**：`DELETE /api/v1/strategies`。若權限控管不當，可能被惡意清空資料。
- **Cache consistency**：若刪除 DB 後未清除 Redis 快取，前端可能在快取有效期內讀取到已被刪除的舊資料（幽靈讀取）。
- **Idempotency**：刪除操作應設計為冪等，重複刪除不會導致錯誤。需確保 DELETE 操作的實現方式滿足此特性。

---

## 10. 常見錯誤

- ❌ 未檢查 `DELETE` 請求的 `body` 或 `query` 參數，導致誤解刪除範圍。
- ❌ 忘記在刪除後清除對應的 Redis 快取。
- ❌ 在回傳的 Response 中洩漏了被刪除的資料（如為了 Debug 而回顯）。
- ❌ 假設 Cassandra 的 DELETE 操作是同步且立即生效的（Cassandra 的刪除是寫入 tombstone，最終一致）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README.md |
| DB | `predict.strategy_bet_log` 存在於 predict keyspace，語意來自 Source code semantics |
| Detail Rule | `predictservice-detail.md` 規範 `strategy_bet_log.result` 不可由外部寫入與不可暴露 |
| Validation | README.md 標示需要驗證，ECFramework.ECService 為統一驗證框架 |