# 查詢支付方式

## 1. 場景目的

提供前端可用的支付管道清單，從 Cassandra `payment.paymethods_sport` 讀取所有 `enabled=1` 的紀錄，並依使用者語系回傳對應的支付方式名稱。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/Payment/Methods` (推測) | 讀取所有啟用的支付方式 |

> **需人工確認**：OpenAPI 文件中未直接揭露查詢支付方式的完整端點路徑與參數，此路徑為基於常見命名慣例推測，需以實際程式碼確認為準。

---

## 3. 流程總覽

1. 前端發送 GET 請求，可選帶入語系參數（例如 `Accept-Language`）
2. Service 層查詢 Cassandra `payment.paymethods_sport`
3. SQL 條件：`WHERE enabled = 1`
4. 從 `names` map 中提取對應語系的名稱（若無則 fallback 至預設語言）
5. 若系統有啟用 Redis 快取 `paymethods:enabled:{site}`，優先讀取快取
6. 回傳可用支付方式清單，包含 `paytype`、`mode`、顯示名稱

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `PaymentController` (推測) | 接收 HTTP GET 請求，解析語系標頭 |
| 2 | Service | `PaymentService` (推測) | 調用 Data Provider 查詢 DB 或快取 |
| 3 | Provider | `IPaymentDataProvider` (推測) | 執行 Cassandra SELECT；若快取命中則直接返回 |
| 4 | Transfer | `PaymentMethodDTO` (推測) | 組裝回應，篩選 `names` map 中對應語系的名稱 |
| 5 | Controller | `PaymentController` | 回傳 `200 OK` 與支付方式清單 |

> **需人工確認**：實際類別名稱與方法簽名應以程式碼為準，此處為基於既有 `pricecentersite` 架構慣例推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.paymethods_sport` | Read (`SELECT WHERE enabled=1`) | 讀取所有啟用的支付管道設定 |
| Redis | `paymethods:enabled:{site}` | Read (`GET`) | 若存在快取，直接回傳，減少 Cassandra 查詢壓力 |
| Redis | `paymethods:enabled:{site}` | Write (`SET`) | 支付方式列表更新後，由 `newlotterysite` 或其他管理服務更新快取 |

---

## 6. 重要規則

- **權限限制**：無特殊權限要求；此為公開 API，任何已授權的客戶端皆可呼叫。
- **欄位限制**：
  - 查詢必須過濾 `enabled = 1`，禁止回傳 `enabled = 0`（停用）的支付方式。
  - `names` map 不應直接回傳整個物件，需依語系提取對應值後回傳。
- **不可暴露資料**：無額外敏感欄位；`paytype`、`mode` 均為業務識別碼，可安全回傳。
- **TTL 規則**：
  - Redis 快取 `paymethods:enabled:{site}` TTL 建議為 10 分鐘（基於 `payment-detail.md` 的 PayMethodsCache 說明）。
  - `enabled` 狀態變更時，管理服務必須執行 `DEL` 使快取失效，不可僅依賴 TTL 自然過期。
- **Transaction 規則**：不適用（僅讀取操作）。
- **Retry 規則**：Cassandra 查詢失敗時，依 ECFramework 內建重試機制處理（不超過 3 次）。
- **狀態值限制**：
  - `enabled` 僅允許 `0`（停用）或 `1`（啟用）。
  - 查詢時必須排除 `enabled = 0`。
- **不可修改欄位**：`paytype`、`mode` 為 Partition Key 與 Clustering Key，建立後不可更新。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| Cassandra 連線失敗 | 回傳 `503 Service Unavailable`，內容為「支付服務暫時無法使用」 |
| 所有支付方式皆為停用 (`enabled=0`) | 回傳空陣列 `[]`，HTTP 200 |
| Redis 快取無法讀取 | 直接查詢 Cassandra，不中斷服務 |
| 請求的語系在 `names` map 中無對應值 | fallback 至預設語言（如 `en`），仍回傳 200 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| P001 | API Test | 查詢啟用中的支付方式 | 回傳所有 `enabled=1` 的紀錄，HTTP 200 |
| P002 | API Test | 所有支付方式皆停用（模擬 DB 狀態） | 回傳空陣列 `[]`，HTTP 200 |
| P003 | Permission Test | 無 Token 情況下請求 | 應成功回傳（此 API 為公開） |
| P004 | Flow Test | 模擬 Redis 快取命中 | 應直接返回快取內容，不查詢 Cassandra |
| P005 | Flow Test | 模擬 Cassandra 查詢失敗 | 回傳錯誤，HTTP 503 |
| P006 | Integration Test | 驗證語系 fallback | 當請求語系不存在時，回傳預設語言 (`en`) 的名稱 |

---

## 9. 高風險區域

- **高風險 Table**：`payment.paymethods_sport` — 若誤將 `enabled=0` 的支付方式回傳給前端，可能導致使用者嘗試使用已停用的金流渠道。
- **高風險 API**：任何對 `paymethods_sport` 執行 `UPDATE enabled` 的管理 API — 僅 `paymentservice` 或 `productservice` 可變更；若其他服務誤寫入將造成狀態不一致。
- **跨服務資料同步**：`rechargeplans_newlottery` 與 `paymethods_sport` 的 `enabled` 狀態由不同服務管理，需確保 `pricecentersite` 僅讀取，不寫入。
- **Transaction**：不適用（純讀取場景）。
- **Cache consistency**：
  - 當 `enabled` 狀態變更時，必須主動清除 `paymethods:enabled:{site}` 快取。
  - 若管理後台直接更新 Cassandra 而未通知 `pricecentersite`，快取可能陳舊。
- **Queue retry**：此場景不涉及 Queue。
- **Idempotency**：此場景為冪等 GET，無需額外處理。

---

## 10. 常見錯誤

- ❌ **查詢時未過濾 `enabled = 1`**  
  → 直接 `SELECT * FROM paymethods_sport` 會將已停用的支付方式一併回傳給前端。

- ❌ **直接回傳 `names` map 全欄位**  
  → 應根據前端請求的語系（如 `zh-TW`）提取對應值；不應暴露所有語系的完整名稱映射。

- ❌ **誤將 `pricecentersite` 用於寫入 `paymethods_sport.enabled`**  
  → `pricecentersite` 對 `payment` keyspace 的角色為 reader，僅能讀取；寫入權限僅限 `paymentservice` 或 `productservice`。

- ❌ **`enabled` 狀態變更後未清除 Redis 快取**  
  → 前台可能繼續顯示已停用的支付方式，必須由管理服務主動 `DEL` 快取。

- ❌ **Redis 快取失敗時直接報錯，未 fallback 查詢 Cassandra**  
  → 快取層應作為加速機制，不可影響服務可用性；miss 時須回源查 DB。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | PaymentController (推測) |
| DB | `payment.paymethods_sport` |
| DB Rule | `db/payment-detail.md` — 「支付方式列表：paymethods_sport 須 WHERE enabled=1 回傳」 |
| Cache | `db/payment-detail.md` — Redis PayMethodsCache: `paymethods:enabled:{site}` |
| Code | PaymentService (推測，實際類別待確認) |
| SQL | `SELECT paytype, mode, names FROM payment.paymethods_sport WHERE enabled = 1` |