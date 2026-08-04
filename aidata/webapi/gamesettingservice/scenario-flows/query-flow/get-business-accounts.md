# 查詢商家帳號

## 1. 場景目的

查詢指定商家下所有子帳號的列表，供管理後台檢視帳號狀態、角色與最後更新時間，回傳內容**不可**包含 `password` 欄位。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/businesses/{businessCode}/accounts` | 查詢指定商家的所有子帳號 |

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，路由參數包含 `businessCode`
2. 驗證請求方是否具備有效授權（AuthToken）
3. 以 `businessCode` 為 partition key，向 Cassandra 查詢 `gamesettings.business_accounts` 表
4. 取得該分區內所有帳號記錄（含 `account`、`role`、`status`、`updatetime` 等）
5. 將結果轉換為 DTO，**顯式排除 `password` 欄位**
6. 回傳帳號陣列至客戶端

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `BusinessController.GetAccounts` | 接收 `businessCode` 路徑參數，調用 Service 層 |
| 2 | Service | `BusinessService.GetAccounts` (推估) | 調用 Provider 層進行資料查詢 |
| 3 | Provider | `BusinessDataProvider` (推估) | 執行 Cassandra 查詢 `SELECT * FROM business_accounts WHERE businesscode = ?` |
| 4 | Service | `BusinessService.GetAccounts` (推估) | 將查詢結果轉換為 DTO，排除 `password` |
| 5 | Controller | `BusinessController.GetAccounts` | 回傳 `IEnumerable<BusinessAccount>` JSON 陣列 |

> 註：Service / Provider 層類名與方法名基於 OpenAPI 路由與既有 Controller 命名慣例推估，**需人工確認**實際 Controller 內注入的 Service 介面名稱。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `gamesettings.business_accounts` (Cassandra) | Read | 以 `businesscode` 查詢所有子帳號 |

> 本場景未使用 Redis Cache 或 Kafka Queue。此服務為直接存取資料庫，無中介快取層。

---

## 6. 重要規則

- **權限限制**：此 API 需要驗證（AuthToken），僅授權用戶可存取。
- **隔離規則**：必須指定 `businesscode` 作為查詢條件，不允許全表掃描。
- **不可回傳欄位**：`password` 欄位**絕對不可**出現在 Response Body 中。DTO 轉換時須明確排除。
- **狀態值限制**：`status` 欄位值為 `0`（凍結）或 `1`（啟用），查詢時不過濾狀態，回傳所有帳號。
- **主鍵規則**：`businesscode` + `account` 為複合主鍵；`account` 建立後不可更新。
- **無 Transaction 需求**：此為單純讀取操作，無需跨表事務。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 請求方未提供有效 AuthToken | 回傳 HTTP 401 Unauthorized |
| `businessCode` 不存在於 `businesses` 表中 | 回傳空陣列 `[]`，不回傳 404（查詢帳號不驗證商家存在性） |
| Cassandra 查詢逾時或連線失敗 | 回傳 HTTP 500 Internal Server Error |
| DTO 序列化時誤含 `password` | 資安事件，Response Body 外洩敏感資料 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| T1 | API Test | 以有效 `businessCode` 查詢，該商家有多筆帳號 | 回傳完整帳號陣列，無 `password` 欄位 |
| T2 | API Test | 以有效 `businessCode` 查詢，該商家無任何帳號 | 回傳空陣列 `[]` |
| T3 | Permission Test | 無 AuthToken 呼叫 API | 回傳 401 Unauthorized |
| T4 | API Test | 回應 JSON 中不應存在 `password` key | 對所有 Response 進行 key 斷言 |
| T5 | Flow Test | `businessCode` 參數為不存在值 | 回傳空陣列（不拋出 404） |

---

## 9. 高風險區域

- **高風險 Table**：`gamesettings.business_accounts` — 若 `password` 欄位洩漏至 Response，將直接導致該商家所有子帳號密碼（雜湊）曝光，違反不可回傳規則。
- **無快取一致性風險**：本場景為直接查詢資料庫，無過期快取問題。
- **無跨服務同步**：此為單一服務內部讀取，不涉及跨服務寫入。

---

## 10. 常見錯誤

- ❌ 回傳帳號列表時，DTO 包含 `password` 欄位 → DTO 映射時必須排除此欄位。
- ❌ 查詢時忘記指定 `businesscode` 條件，進行全表掃描 → Cassandra 不支援高效全表掃描，可能導致效能問題並回傳不該查詢的商家資料。
- ❌ 回傳前未判斷查詢結果是否為空，拋出 404 例外 → 指定 `businessCode` 無帳號時，應回傳空陣列而非錯誤。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `GET /api/v1/businesses/{businessCode}/accounts` (OpenAPI / README) |
| DB | `gamesettings.business_accounts` (Cassandra Schema) |
| 不可回傳規則 | `gamesettings-detail.md`：「password（business_accounts）：任何 API 回傳皆不可包含此欄位」 |
| 隔離規則 | `gamesettings-detail.md`：「查詢 business_accounts 時必須指定 businesscode，不允許全表掃描」 |
| Code | `BusinessController` (推估，基於 API 路由命名慣例) |