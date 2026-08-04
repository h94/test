# 查詢兌換記錄

## 1. 場景目的

此場景讓使用者查詢自己的商品兌換記錄。系統會驗證查詢者身份是否與請求中的 `account` 參數一致，確保使用者僅能查看自己的兌換記錄。回應內容會對敏感個人資料（如電話、地址）進行脫敏處理，確保隱私不外洩。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/store/redeemlogs` | 依 `account` 查詢該使用者的商品兌換記錄（需人工確認確切路由與參數，OpenAPI 未揭露此端點，此處依場景描述推斷） |

---

## 3. 流程總覽

1. 前端發送 GET 請求，並附帶 JWT token 與欲查詢的 `account`。
2. 認證中介軟體解析 token，獲得請求者身份。
3. 控制器 (Controller) 收到 request，將參數傳遞給服務層 (Service)。
4. 服務層 (Service) 進行身份比對：比對 token 中的帳號與參數 `account` 是否一致。
5. 服務層 (Service) 呼叫資料存取層 (Provider/DAO)，查詢 Cassandra `product` keyspace 中的兩張表：
   - `product_store_redeem_logs` (一般商品兌換記錄)
   - `products_activity_redeem_logs` (活動商品兌換記錄)
6. 查詢條件中需包含 `account` 作為過濾條件。
7. 成功取得記錄後，在服務層進行脫敏處理：遮罩 `phonenumber`、`address` 等敏感欄位。
8. 將處理後的兌換記錄列表回傳給前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `StoreController` 或類似命名 | 接收 GET 請求，提取 query string 中的 `account` 參數（需人工確認） |
| 2 | Service | `RedeemLogService` (推測命名) | 呼叫驗證方法，確認 token 帳號與查詢帳號一致 |
| 3 | Provider/DAO | `ProductDAO` (推測) | 組裝 CQL 查詢語句，對 `product.product_store_redeem_logs` 執行 `WHERE account = ?` |
| 4 | Provider/DAO | `ProductDAO` (推測) | 組裝 CQL 查詢語句，對 `product.products_activity_redeem_logs` 執行 `WHERE account = ?` |
| 5 | Service | `RedeemLogService` | 合併兩張表的查詢結果，並進行敏感資料脫敏 |
| 6 | Controller | `StoreController` | 將脫敏後的結果轉換為 DTO 並回傳 HTTP 200 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `product.product_store_redeem_logs` | Read (SELECT) | 查詢一般商品兌換記錄，以 `account` 為過濾條件 |
| DB | `product.products_activity_redeem_logs` | Read (SELECT) | 查詢活動商品兌換記錄，以 `account` 為過濾條件 |
| Redis | — | 無操作 | 本服務目前未對兌換記錄使用 Redis 快取 (依據 `priceclientsystem-detail.md`) |

---

## 6. 重要規則

- **身份強制比對**：前端傳入的 `account` 參數必須與請求 token 中解析出來的帳號完全一致。否則應回傳權限不足錯誤 (HTTP 403 Forbidden)。
- **不可暴露資料**：回應內容中，`phonenumber` 必須脫敏（如 `0912***456`），`address` 在列表查詢中不可完整回傳（或需脫敏）。`account` 欄位不應在回傳的 payload 中重複暴露。
- **權限限制**：此 API 僅限一般用戶查詢自己的記錄。管理後台可能使用不同端點，擁有更全面的查詢權限。
- **跨表查詢**：查詢必須同時涵蓋 `product_store_redeem_logs` 和 `products_activity_redeem_logs` 兩張表，以提供完整的兌換歷史。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| token 無效或未附帶 | 認證中介層回傳 HTTP 401 Unauthorized |
| token 中的帳號與 request 參數 `account` 不符 | 服務層回傳 HTTP 403 Forbidden |
| 查詢的 `account` 在 DB 中沒有任何記錄 | API 回傳 HTTP 200 OK，並附帶空的記錄列表 |
| Cassandra 查詢時發生逾時或連線錯誤 | 服務層回傳 HTTP 500 Internal Server Error（需人工確認此服務的全局錯誤處理策略） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| Test-R1 | Permission Test | 使用者 A 的 token 請求查詢使用者 B 的記錄 (`?account=B`) | HTTP 403 Forbidden |
| Test-R2 | API Test | 使用者 A 的 token 請求查詢自己的記錄 (`?account=A`) | HTTP 200 OK，且回應內容僅包含使用者 A 的記錄 |
| Test-R3 | API Test | 無任何兌換記錄的使用者查詢 | HTTP 200 OK，回應列表為空 |
| Test-R4 | Unit Test | 查詢結果中的 `phonenumber` 欄位 | 驗證 `phonenumber` 已正確脫敏為 `****` 格式 |
| Test-R5 | Unit Test | 查詢結果中的 `address` 欄位 | 驗證 `address` 欄位為空或被置換為脫敏字串 |
| Test-R6 | Flow Test | 使用者完成一筆兌換後立即查詢 | 驗證新記錄會出現在 `product_store_redeem_logs` 的查詢結果中 |
| Test-R7 | Flow Test | 使用者完成一個活動兌換後立即查詢 | 驗證新記錄會出現在 `products_activity_redeem_logs` 的查詢結果中 |

---

## 9. 高風險區域

- **高風險 API**：查詢兌換記錄 API (GET)-> 若身份驗證邏輯有缺陷，可能導致大量用戶兌換記錄與個資外洩。
- **資料一致性**：需注意同時從兩張表查詢時的資料合併邏輯，確保排序正確（例如依時間戳倒序），避免前後端對記錄順序的認知不一致。

---

## 10. 常見錯誤

- ❌ 查詢時未驗證 identity，直接以 request 參數 `account` 查詢，導致使用者可查看他人記錄。
  - → ✅ 必須從 token 中提取使用者身份，強制比對。
- ❌ 在列表中回傳了完整的 `phonenumber`、`address` 或重複回傳 `account` 欄位。
  - → ✅ 服務層回傳前，必須對這些欄位執行脫敏或清除。
- ❌ 只查詢 `product_store_redeem_logs`，遺漏了活動兌換記錄 `products_activity_redeem_logs`。
  - → ✅ 查詢邏輯必須涵蓋這兩張主要的兌換記錄表。
- ❌ `SELECT * FROM product_store_redeem_logs` 未帶 `account` 過濾條件，或在程式中才進行過濾，對 Cassandra 造成巨大效能壓力。
  - → ✅ 必須在 CQL 查詢時就將 `account` 作為過濾條件（因 `account` 是 clustering key 的一部分，查詢是高效的）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `store/RedeemLogController` 或 `RedeemLogService`（確切命名需人工確認） |
| DB | `product.product_store_redeem_logs`、`product.products_activity_redeem_logs` |
| Rule | `priceclientsystem-detail.md` - 兌換紀錄查詢規則、不可回傳欄位 |
| DB Detail | `product-detail.md` - 對 `product_store_redeem_logs` 與 `products_activity_redeem_logs` 的 SELECT 規則需依 `account` 過濾 |
| Note | 此份 OpenAPI 文件未包含兌換相關端點，API 路由 / 參數為推斷。**需人工確認實際 Controller 名稱與 Request/Response Schema。** |