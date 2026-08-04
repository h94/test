# 異常告警推送

## 1. 場景目的

當 tradegameservice 在處理交易、查詢或結算等業務流程中發生非預期的內部錯誤（如 Cassandra 寫入失敗、外部服務呼叫逾時或回傳異常）時，透過 MQService 推送告警訊息至相關的監控或維運系統，以便即時偵錯與介入處理。

---

## 2. 入口 API

此流程並非由單一對外 API 直接觸發，而是作為內部橫切關注點（cross-cutting concern），嵌入於各主要業務 API 的錯誤處理路徑中。

| API 類別 | Method | Path 範例 | 說明 |
|---|---|---|---|
| 交易操作 | POST | `/api/trade/{game_type}` | 當寫入 `stock_holdings_*` 或呼叫 zcoin_api 失敗時觸發告警。 |
| 查詢操作 | GET | `/api/trade/{game_type}`, `/api/tradegames/{game_type}/{lid}` | 當讀取 Cassandra 或 Redis 發生嚴重錯誤時觸發告警（此情境較少見，通常為記錄錯誤）。 |
| 重算操作 | POST | `/api/recalculate/{game_type}` | 結算流程中若發生資料讀寫失敗的嚴重錯誤，觸發告警。 |

**❓ 需人工確認**：OpenAPI 未暴露 MQService 的直接控制端點，告警的觸發邏輯與閾值（例如：錯誤次數、錯誤類型過濾）是在 tradegameservice 的 Service 層實作。

---

## 3. 流程總覽

1.  **內部錯誤發生**：業務邏輯（如 TradeService）在執行過程中捕獲到一個無法自行恢復的嚴重例外（Exception）。
2.  **建構告警訊息**：錯誤處理模組將例外資訊（如錯誤碼、錯誤訊息、發生時間、堆疊追蹤）包裝成結構化格式。
3.  **發送告警請求**：呼叫 `MQService` 提供的方法或 API，將告警訊息推送至指定的佇列（Queue）或主題（Topic）。
4.  **紀錄發送結果**：不論 MQService 呼叫成功或失敗，此告警嘗試本身及其結果應被記錄到服務日誌中。
5.  **回傳業務錯誤**：向原始請求的客戶端回傳一個通用、安全的錯誤訊息（例如 HTTP 500），不暴露內部細節。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | TradeController.post | 接收 HTTP 請求，呼叫 Service 層。 |
| 2 | Service | TradeService.execute | 執行核心交易邏輯，嘗試寫入 `stock_holdings_*`。 |
| 3 | Service | TradeService.execute (catch block) | 捕獲來自 Provider 的例外（如 `CassandraWriteException`）。 |
| 4 | Service | `AlertService.send_alert(error_payload)` | **需人工確認**：此為推測的服務與方法名稱。負責建構告警訊息。 |
| 5 | Provider | `MQServiceProvider.publish(message)` | **需人工確認**：將告警訊息發送至 MQ。實作細節（HTTP/RPC/Queue）未知。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Queue | MQService | Publish | 推送異常告警訊息，將其導向監控系統或維運群組的管道。 |

---

## 6. 重要規則

-   **訊息內容限制**：
    *   **禁止**將使用者密碼 (`accounts_*.password`)、手機號碼 (`accounts_*.phone`) 或內部配置 (`accounts_*.handler`) 的完整或部分內容放入告警訊息中。
    *   **可以**包含請求追蹤 ID (`TraceId`)、錯誤發生的 API 路徑、Cassandra 查詢語句的摘要、關鍵業務參數（如 `game_type`, `gid`）以及不敏感的帳號資訊（如 `account` 名稱）。
-   **不影響主要流程**：告警發送應非同步進行，發送過程中的任何例外都不應影響原始業務請求的錯誤處理流程（即告警失敗不能導致業務錯誤處理中斷）。
-   **冪等性考量**：告警機制本身應考慮短時間內相同錯誤大量重複發送的情況，`MQService` 或接收端應有去重或聚合的邏輯。
    *   **❓ 需人工確認**：此邏輯是在 `tradegameservice` 的 Service 層處理還是由 `MQService` 端處理。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `stock_holdings_BK` 發生寫入逾時 | 捕獲例外，發送告警至 MQ，向客戶端回傳 HTTP 500。 |
| `zcoin_api` 點數服務無回應 | 捕獲例外，發送告警至 MQ，向客戶端回傳 HTTP 500。 |
| 呼叫 `MQService` 本身失敗 | 將此次發送失敗記錄到本地日誌，並回傳原始業務錯誤給客戶端。不可因為發送告警失敗而拋出另一個未處理的例外。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| ALERT-01 | Flow Test | 模擬 Cassandra 寫入失敗，觸發交易流程。 | 1. 客戶端收到 HTTP 500。 2. 系統呼叫了 MQService 發送一則包含正確錯誤訊息的告警。 |
| ALERT-02 | Flow Test | 模擬 `MQService` 呼叫失敗，觸發交易流程。 | 1. 客戶端仍收到 HTTP 500（原始錯誤）。 2. 系統在日誌中記錄了告警發送失敗的事件。 3. 沒有任何例外從告警邏輯中洩漏。 |
| ALERT-03 | Security Test | 檢查觸發時實際發送到 MQ 的訊息內容。 | 訊息中不可包含 `password` 或 `phone` 欄位。 |

---

## 9. 高風險區域

-   **誤發敏感資料**：告警訊息中不小心包含了使用者密碼、個資等高風險資料，這是極嚴重的安全漏洞。
-   **告警風暴**：在系統大規模故障時，告警訊息可能如洪水般湧入 `MQService`，壓垮監控系統或 MQ 本身。
-   **非同步失效**：如果告警發送失敗，維運人員無法察覺系統異常，延長 MTTR（平均修復時間）。

---

## 10. 常見錯誤

-   **AI 容易誤解**：可能會將 `tradegameservice` 構想為直接包含 MQ 連線的複雜邏輯。
-   **新人容易犯錯**：在告警訊息或日誌中輸出了帳號密碼，只為方便除錯。
-   **常見漏檢查項目**：Code review 時未檢查錯誤處理區塊中送往 MQService 的酬載（payload）內容，導致敏感資訊外洩。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 服務相依 | README.md - 服務相依章節，列出 `MQService | 異常告警推送`。 |
| DB 寫入限制 | tradegameservice-detail.md `stock_holdings` 寫入限制章節。 |
| 不可回傳欄位 | pricecenter-detail.md 不可回傳欄位章節。 |
| MQ 操作 | **(需人工確認)** 無 OpenAPI 定義或程式碼可供驗證。 |
| 程式碼 | **(需人工確認)** 無對應的程式碼證據。 |