# 場景名稱：查詢活動提現記錄

## 1. 場景目的
本場景描述會員或後台管理員查詢特定站點、特定活動中，某一帳號的所有提現申請記錄。主要用於提供用戶檢視自己的提現狀態與歷史，或供管理後台審核與對帳。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/activity/withdrawlogs/{site}/{activityEvent}/{account}` | 查詢指定站點、活動與會員的活動提現記錄清單。 |

---

## 3. 流程總覽

1.  Client 發起 GET 請求，路徑帶有 `site`、`activityEvent` 及 `account`。
2.  API Gateway / Authentication 中介層驗證請求方身份與權限。
3.  `ActivityWithdrawController` 接收請求，將參數傳遞至 Service 層。
4.  `ActivityWithdrawService` 呼叫 `IActivityWithdrawDataProvider` 查詢資料庫。
5.  Provider 對 Cassandra 的 `payment.withdrawlogs_activity` 表執行查詢（條件：`site`、`activityevent`、`account`）。
6.  取得結果集後回傳至 Service。
7.  Service 過濾或轉換敏感欄位（例如電話、姓名），組裝 DTO 回傳 Controller。
8.  回傳 JSON 格式的提現記錄清單。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `ActivityWithdrawController.GetWithdrawLogs` | 接收 HTTP GET 請求，取得路徑參數 `site`、`activityEvent`、`account` 並傳遞給 Service |
| 2 | Service | `ActivityWithdrawService.GetWithdrawLogsByAccount` | 組合查詢條件，呼叫 Provider 進行 DB 查詢 |
| 3 | Provider | `ActivityWithdrawDataProvider.GetWithdrawLogs` | 使用 Cassandra Driver 執行 SELECT 查詢，指定 Partition Key (`site`) 與 Clustering Key (`activityevent`, `account`) |
| 4 | Service | `ActivityWithdrawService.GetWithdrawLogsByAccount` | 映射回傳資料至 DTO，過濾或遮罩敏感個資 |
| 5 | Controller | `ActivityWithdrawController.GetWithdrawLogs` | 包裝成 HTTP 200 並回傳 JSON 陣列 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `payment.withdrawlogs_activity` | Read | 查詢特定會員於特定站點與活動的所有提現記錄 |

**需人工確認**：目前無明確證據顯示此查詢流程有使用 Redis 快取或訊息佇列 (Kafka)。純查詢操作，不應涉及寫入。

---

## 6. 重要規則

- **權限限制**：  
  一般會員僅能查詢自身 (`account`) 的提現記錄。管理後台可查詢任何帳號，但需具備對應的管理角色。  
  **需人工確認**：確認是否透過 `[Authorize]` 屬性並在 Service 層驗證 `account` 與 Token 的關聯。

- **欄位限制**：  
  `accountname` (提領人姓名) 及 `contactnumber` (聯絡電話) 屬個人隱私資料。對外 API (會員端) 回傳時應進行遮罩處理（例如 `王**`、`09******12`）。管理後台則可視權限回傳完整欄位。  
  **Evidence**: `paymentservice-detail.md` 將 `withdrawlogs_activity.accountname/contactnumber` 標記為隱私欄位。

- **不可暴露資料**：  
  禁止回傳任何系統內部識別碼（如 DB raw ID 等），僅能使用業務主鍵 (`site`, `activityevent`, `account`, `cid`)。

- **狀態值限制**：  
  `status` 欄位型別為 `int`，具體值映射（例如 0=審核中，1=成功，2=失敗）由 `AppDefine.WithdrawStatus` 定義。  
  **需人工確認**：目前無法從既有文件中找到 `WithdrawStatus` 的完整列舉值定義。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未通過身份驗證 (無效 Token) | 回傳 HTTP 401 Unauthorized。 |
| Token 對應的會員與請求路徑中的 `account` 不符（且非管理員） | 回傳 HTTP 403 Forbidden。 |
| 會員沒有任何提現記錄 | 回傳 HTTP 200，內容為空陣列 `[]`。 |
| Cassandra 查詢逾時或連線失敗 | 回傳 HTTP 500 Internal Server Error。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| WT-01 | API Test | 使用已存在提現記錄的會員查詢 | 回傳 HTTP 200，包含多筆提現記錄，欄位符合定義 |
| WT-02 | API Test | 使用從未提現的會員查詢 | 回傳 HTTP 200，內容為 `[]` |
| WT-03 | Permission Test | 會員 A 查詢會員 B 的提現記錄 | 回傳 HTTP 403 |
| WT-04 | Permission Test | 管理員查詢任意會員的提現記錄 | 回傳 HTTP 200，內容為該會員的記錄 |
| WT-05 | Flow Test | 同時查詢不同 `activityEvent` | 確認回傳資料只包含指定活動，不會互相汙染 |
| WT-06 | API Test | 查詢會員隱私欄位遮蔽狀況 | 確認 `accountname`, `contactnumber` 依角色被遮蔽 |

---

## 9. 高風險區域

- **高風險 Table**：`payment.withdrawlogs_activity` — 包含大量會員提現記錄與個資。
- **Cache consistency**：此查詢為純讀取且要求即時性，不應使用過期快取。若有快取機制（文件未明確提及），需有強力失效機制以避免呈現錯誤的審核狀態。

---

## 10. 常見錯誤

- **新人容易犯錯**：  
  在 Service 層組裝 DTO 時，忘記對 `accountname`, `contactnumber` 等欄位進行角色權限判斷（遮罩 vs. 完整回傳）。

- **AI 容易誤解**：  
  易於混淆 `payment.withdrawlogs_activity` 與 `sport.withdraw_logs`，它們是不同的資料表。這個場景僅處理後者。

- **常見漏檢查項目**：  
  查詢時沒有驗證請求者是否有權限存取指定的 `account`。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI: `GET /api/v1/activity/withdrawlogs/{site}/{activityEvent}/{account}` |
| DB | `payment.withdrawlogs_activity` (根據 Source code semantics) |
| Code | `ActivityWithdrawController` 接收查詢請求 |
| Rule | `paymentservice-detail.md` - 隱私欄位不可暴露規則 |