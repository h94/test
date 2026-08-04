# 查詢單一商家

## 1. 場景目的
根據 `businessCode` 獲取特定商家的詳細資料。此流程為查詢類場景，必須嚴格遵循「以 businessCode 為主鍵查詢」的規則，禁止以 email 或 authtoken 作為查詢條件。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/businesses/{businessCode}` | 依據商家代碼查詢單一商家 |

---

## 3. 流程總覽

1.  API 閘道驗證請求之 AuthToken（需人工確認驗證機制詳細邏輯，現有文件僅記錄 `[Auth]`）。
2.  `BusinessController` 接收 `businessCode` 路徑參數。
3.  呼叫 `BusinessService`，執行查詢邏輯。
4.  `BusinessService` 以 `businessCode` 為主鍵，查詢 Cassandra `gamesettings.businesses` 表。
5.  若查無資料，返回 404 Not Found。
6.  DTO 組裝時，必須明確排除 `authtoken` 欄位。
7.  將去除敏感資料的商家詳細資訊回傳給客戶端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `BusinessController.GetBusiness` | 接收 `businessCode` 參數並轉送 Service 層 |
| 2 | Service | `IBusinessService.GetBusiness(businessCode)` | 呼叫 Provider 取得資料，執行 DTO 轉換與欄位排除 |
| 3 | Provider | Cassandra Provider | 對 `gamesettings.businesses` 執行主鍵查詢：`WHERE businesscode = ?` |
| 4 | Transfer | (Internal DTO Mapper) | 將 `Business` 實體映射為 Response DTO，過程中強制排除 `authtoken` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `gamesettings.businesses` (Cassandra) | Read | 取得商家詳細資料，以 `businesscode` 為主鍵查詢 |

---

## 6. 重要規則

-   **權限限制**：需要通過 API 驗證，僅允許已授權的服務或管理員呼叫。
-   **不可暴露資料**：API Response 中**絕對禁止**包含 `authtoken` 欄位。此 Token 僅供後端服務之間溝通使用，任何對外 API 回傳皆不應包含。
-   **查詢限制**：必須以 `businesscode` 為主鍵進行查詢。Cassandra `businesses` 表上，`email` 和 `authtoken` 沒有索引，以此為條件會導致全表掃描，效能極差且應嚴格避免。
-   **狀態檢查**（需人工確認）：查詢到的 `businesses` 資料中，若 `subenddate` 小於當前日期，理論上該商家已過期，但需確認此查詢 API 是否會過濾或僅回傳資料由客戶端判斷。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 請求未附帶有效的 AuthToken | 返回 401 Unauthorized |
| `businessCode` 不存在於 `gamesettings.businesses` 表中 | 返回 404 Not Found 或相應的錯誤訊息 |
| Cassandra 查詢逾時 | 返回 500 Internal Server Error 或 503 Service Unavailable |
| 以 `email` 或 `authtoken` 作為查詢條件（錯誤用法） | 查詢被強制轉向或拒絕，因不符查詢規則與無索引支援。開發階段應被強烈禁止。 |
| DTO 轉換時意外包含 `authtoken` | 資料洩漏，這是一個嚴重的安全漏洞，應透過代碼審查和自動化測試防止 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | API Test | 使用有效的 businessCode 請求 | 200 OK，回傳的 Response Body 不包含 `authtoken` |
| T2 | API Test | 使用不存在的 businessCode 請求 | 404 Not Found |
| T3 | Flow Test | 驗證 DTO 轉換邏輯 | `authtoken` 欄位嚴格為空或不存在 |
| T4 | Permission Test | 不帶 AuthToken 或使用過期 Token 請求 | 401 Unauthorized |
| T5 | API Test | Cassandra 發生異常 | 返回 5xx 錯誤，不暴露內部 SQL 或資料庫結構 |

---

## 9. 高風險區域

-   **高風險 Table**：`gamesettings.businesses`，其 `authtoken` 為高度敏感資料，一旦洩漏將導致整個商家的 API 被非法調用。
-   **高風險 API**：`GET /api/v1/businesses/{businessCode}`，需確保權限驗證與 DTO 轉換不出錯。
-   **Data Masking**：`authtoken` 的排除發生在 Service 或轉換層，若未來重構程式碼，必須確保這個規則不會被略過。

---

## 10. 常見錯誤

-   ❌ 新人或 AI 在實作時，可能會實現「以 email 查詢商家」的輔助功能，但這違反了 DB Schema 的限制（無索引），會導致效能問題，不應被實現。
-   ❌ 在 API 回傳的 DTO 模型定義中，直接包含了來自 `Business` 實體的所有欄位，導致 `authtoken` 被序列化並洩漏給前端。
-   ❌ 將此 API 誤認為不需要驗證即可呼叫，導致商家資料外洩。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由定義 | `README.md` - `GET /api/v1/businesses/{businessCode}` |
| DB 操作規則 | `gamesettings-detail.md` - 「查詢單一商家」說明，必須以 `businesscode` 主鍵查詢，禁止 `email` 或 `authtoken` 查詢 |
| 敏感欄位規則 | `gamesettings-detail.md` - `authtoken` 不可回傳規則 |
| DB Schema | `gamesettings.businesses` - `businesscode` 為主鍵，`authtoken` 不存在二級索引 |
| 查詢規則 | `service_detail.md` / Code semantics - DTO 轉換時需排除 `authtoken`；`subenddate` 檢查規則需人工確認 |