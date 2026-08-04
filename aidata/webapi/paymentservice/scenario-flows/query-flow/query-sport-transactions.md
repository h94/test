# 查詢體育交易訂單

## 1. 場景目的

提供後台管理員或一般會員查詢體育交易訂單記錄。支援兩種查詢模式：依日期範圍批次查詢，以及透過複合主鍵精準查詢單筆訂單。此功能用於訂單對帳、用戶交易歷史查詢及客戶服務。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sport/transactions` | 查詢交易訂單（依日期範圍） |
| GET | `/api/v1/sport/transactions/{year}/{dateTime}/{account}/{id}` | 查詢單筆訂單 |

> **需人工確認**：OpenAPI 文件未包含 `GET /api/v1/sport/transactions` 與 `GET /api/v1/sport/transactions/{year}/{dateTime}/{account}/{id}` 的詳細定義（Request/Response Schema），僅能從 README 路由清單確認端點存在。

---

## 3. 流程總覽

1. 接收查詢請求（日期範圍或複合主鍵）
2. 驗證 JWT Token（所有 API 皆需驗證）
3. 判斷請求者身份（後台管理員 或一般會員）
4. 若為一般會員：補入 `account` 過濾條件，限制僅能查詢自身訂單
5. 呼叫 Cassandra `payment.sport_transactions` 執行查詢
6. 對回傳結果進行資料脫敏（移除內部敏感欄位）
7. 回傳訂單列表或單筆訂單

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | SportTransactionController.cs - GetTransactions / GetTransactionById | 接收請求、呼叫 Service |
| 2 | Service | SportTransactionService.cs | 組合查詢條件、判斷權限、呼叫 DataProvider |
| 3 | DataProvider | SportTransactionDataProvider.cs | 執行 Cassandra Query、資料映射 |
| 4 | Database | payment.sport_transactions | Read（SELECT） |

> **需人工確認**：上述 Class/Method 名稱基於 .NET 常規命名慣例推測，需與實際代碼驗證。若專案採用 Minimal API 或不同架構模式，此流程可能不同。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | payment.sport_transactions | Read | 查詢交易訂單記錄 |

---

## 6. 重要規則

- **權限限制**：
  - 所有端點皆需 JWT 驗證（✅）
  - 一般會員僅可查詢自身帳號的訂單（`account` 過濾條件必須等於登入者帳號）
  - 後台管理員可查詢所有帳號訂單
- **欄位限制**：
  - 不可回傳 Cassandra Row Key 以外的內部識別碼（如 `authkey`）
  - 對外 API 應過濾付款細節中的敏感資訊（如完整卡號）
- **不可暴露資料**：
  - `payment.sport_transactions` 中的 `card4no` 或其他支付細節欄位需遮罩
- **Cassandra 查詢限制**：
  - 日期範圍查詢需指定 `year` 分區鍵，避免跨分區全表掃描
  - 單筆查詢必須提供完整複合主鍵：`year`、`date_time`、`account`、`id`

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未提供 JWT Token 或 Token 無效 | HTTP 401 Unauthorized |
| 一般會員查詢他人帳號訂單 | HTTP 403 Forbidden 或僅回傳自身訂單 |
| 查詢單筆訂單時主鍵不完整 | HTTP 400 Bad Request |
| 查詢日期範圍時 `year` 參數缺失 | HTTP 400 Bad Request |
| 指定主鍵的訂單不存在 | HTTP 200 空結果或 HTTP 404（需人工確認業務約定） |
| Cassandra 查詢逾時 | HTTP 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| QT-01 | API Test | 不帶 Token 請求 `GET /api/v1/sport/transactions` | 回傳 401 Unauthorized |
| QT-02 | Permission Test | 一般會員 `GET /api/v1/sport/transactions` 不指定 account | 僅回傳自身帳號的訂單 |
| QT-03 | Permission Test | 一般會員 `GET /api/v1/sport/transactions?account=他人` | 拒絕存取或忽略 `account` 參數 |
| QT-04 | API Test | 提供正確日期範圍（含 year）查詢 | 回傳符合條件的訂單列表 |
| QT-05 | API Test | 提供完整主鍵查詢單筆訂單 | 回傳正確的訂單詳細資料 |
| QT-06 | Flow Test | 查詢一筆不存在的訂單 ID | 回傳空或 404 |
| QT-07 | API Test | 查詢請求缺少必填參數 | 回傳 400 Bad Request |

---

## 9. 高風險區域

- **高風險 table**：`payment.sport_transactions` — 包含所有使用者的金融交易記錄，嚴禁越權查詢。
- **高風險 API**：`GET /api/v1/sport/transactions` — 若未強制綁定 `account` 過濾，可能導致大量資料外洩。

---

## 10. 常見錯誤

- ❌ **查詢時未使用 `year` 分區鍵** → 導致 Cassandra 全叢集掃描，效能極差且可能觸發超時。
- ❌ **API 層未區分管理者與一般會員權限** → 一般會員可能查詢到所有使用者的訂單，造成嚴重資料外洩。
- ❌ **直接回傳 DB 原始資料** → 可能暴露 `card4no`、內部 ID 等敏感欄位給前端。
- ❌ **日期範圍查詢未設上限** → 若無限制查詢跨度，可能因回傳資料量過大導致服務崩潰。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README.md - 體育交易訂單 API 表格 |
| DB Schema | db/payment.md - `sport_transactions` 表定義 |
| DB Role | paymentservice-detail.md - paymentservice 為 `payment` keyspace owner |
| 服務相依 | README.md - 相依 memberservice 驗證身份 |
| 程式語意 | Phase1 Code Semantics - `sport_transactions` 欄位定義（year, date_time, account, id） |