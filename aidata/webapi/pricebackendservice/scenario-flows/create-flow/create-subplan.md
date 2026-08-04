# 建立訂閱方案

## 1. 場景目的
提供後台管理員透過管理後台建立新的會員訂閱方案。此方案將作為前端用戶訂閱時的選項，定義了價格、週期與可用的支付方式。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/payment/sport/subplans` | 建立一個新的訂閱方案 |

---

## 3. 流程總覽

1. 管理員透過後台介面，填寫訂閱方案資訊（名稱、金額、幣別、啟用時間、適用支付方式等）並送出請求。
2. `PriceBackendService` 接收請求後，進行基本參數驗證（如必填欄位檢查）。
3. **重要**：`PriceBackendService` 本身為 BFF 層，不直接操作資料庫。它將請求資料轉換為 `paymentservice` API 要求的格式。
4. `PriceBackendService` 呼叫下游微服務 `paymentservice` 的對應端點來執行實際的資料寫入。
5. `paymentservice` 進行業務邏輯驗證（如方案名稱是否重複、支付方式是否有效等）。
6. 驗證通過後，`paymentservice` 將新的訂閱方案寫入 `payment` keyspace 的對應資料表（可能是 `rechargeplans_newlottery` 或相關表）。
7. `paymentservice` 返回操作成功結果給 `PriceBackendService`。
8. `PriceBackendService` 將成功回應傳遞給前端，完成建立流程。

---

## 4. 程式流程

> **需人工確認**：由於僅有 OpenAPI 定義，以下流程基於 `PriceBackendService` 作為 BFF 層的職責推斷。

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `PaymentController.CreateSubPlan` (推測) | 接收請求，調用 Service 層 |
| 2 | Service | `PaymentService.CreateSubPlan` (推測) | 執行主要邏輯：轉換 DTO、呼叫外部服務 |
| 3 | Provider | `PaymentProvider.CreateSubPlan` (推測) | 封裝對下游 `paymentservice` 的 HTTP 請求 |
| 4 | Service | `paymentservice` (外部) | 接收請求，執行業務驗證與資料庫寫入 |

---

## 5. DB / Cache / Queue 使用

> **重要**：`PriceBackendService` 在此場景中不直接操作 DB/Cache/Queue。以下為下游 `paymentservice` 的可能操作。

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `payment.rechargeplans_newlottery` | Write | 儲存新建立的訂閱方案。 |
| DB | `payment.paymethods_sport` | Read | 驗證請求中指定的支付方式 `paytype` 是否為 `enabled=1` 的有效狀態。 |
| Redis | `rechargeplans:all:{site}` | Delete | **潛在操作**：若存在快取，建立新方案後應失效相關快取，以確保前台能查詢到最新列表。 |

---

## 6. 重要規則

- **權限限制**：所有對 `/api/v1/payment/sport/*` 的請求都需要驗證，僅允許具有管理員權限的帳號存取。
- **欄位限制**：
    - `id`：由系統自動生成，不可於請求中指定。
    - `starttime` / `endtime`：`starttime` 不可晚於 `endtime`。`endtime` 不可早於當前時間（或依特定業務規則）。
    - `enabled`：建立時預設應為啟用狀態（1），或根據請求參數設定。
    - `currency`：必須是系統支援的有效幣別。
    - `status`：`PriceBackendService` 不直接處理此欄位，由下游服務管理。
- **不可回傳欄位**：API 回傳時，不應包含任何內部系統金鑰或未經處理的敏感資訊。
- **Transaction 規則**：跨服務調用涉及分布式交易，需考慮調用失敗時的補償或重試機制（由 `PriceBackendService` 統一處理或單純拋出錯誤）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未提供必填欄位（如方案名稱、金額） | 返回 400 Bad Request 及明確的錯誤訊息。 |
| 提供的支付方式 `paytype` 不存在或已停用 | `paymentservice` 返回錯誤，`PriceBackendService` 轉發錯誤，提示支付方式無效。 |
| 方案名稱或 ID 與現有方案重複（如果業務上不允許） | `paymentservice` 返回 409 Conflict 或其他業務錯誤。 |
| 呼叫下游 `paymentservice` 時網路超時或服務不可用 | 返回 502 Bad Gateway 或 503 Service Unavailable。 |
| 資料庫寫入失敗（如 Cassandra 寫入超時） | `paymentservice` 捕捉例外，返回 500 Internal Server Error。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| `SC-SUB-01` | API Test | 以合法的管理員權杖與完整的方案資訊呼叫 API | 返回 200 OK，並可於後續的查詢中看到新方案。 |
| `SC-SUB-02` | API Test | 使用不具管理員權限的權杖呼叫 API | 返回 401 Unauthorized 或 403 Forbidden。 |
| `SC-SUB-03` | API Test | 請求中缺少必要欄位（如 `amount`） | 返回 400 Bad Request。 |
| `SC-SUB-04` | Flow Test | 建立方案時指定一個已停用的支付方式 | API 返回錯誤，資料庫中未產生新方案記錄。 |
| `SC-SUB-05` | Integration Test | 模擬下游 `paymentservice` 呼叫失敗 | API 返回 5xx 錯誤，前端顯示錯誤提示。 |

---

## 9. 高風險區域

- **跨服務資料同步**：`PriceBackendService` 作為中介，真正的資料一致性由 `paymentservice` 保證。若 `paymentservice` 內部有其他依賴操作，需確保其分散式交易機制完善。
- **Cache consistency**：若前台查詢方案列表使用了 Redis 快取，新方案建立後若未即時更新或失效快取，將導致前台無法即時顯示新方案。

---

## 10. 常見錯誤

- **新人容易犯錯**：
    - 誤以為 `PriceBackendService` 直接寫入資料庫，而忽略了它作為 BFF 層的角色。
    - 在前端傳遞了應由後端生成的欄位（如 `id`、`updatetime`）。
- **AI 容易誤解**：
    - 在產生程式碼時，可能會在 `PriceBackendService` 的 Controller 或 Service 中直接編寫 SQL 或 Cassandra 驅動程式碼，而非透過 HTTP Client 呼叫下游服務。
- **常見漏檢查項目**：
    - 未檢查支付方式的啟用狀態 (`enabled`)。
    - 未驗證時間範圍的有效性 (`starttime` < `endtime`)。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/payment/sport/subplans` (OpenAPI / README) |
| DB (潛在) | `payment.rechargeplans_newlottery` (db-schema) |
| Code (架構) | `pricebackendservice` README 指出其為 BFF 層，不直接存取 DB。 |
| Rule | `db/payment-detail.md` 指出 `rechargeplans_newlottery` 的 `id` 由系統生成，不可修改。 `enabled` 需與時間範圍一同生效。 |
| Service | `pricebackendservice` README 相依服務章節說明其依賴 `paymentservice`。 |