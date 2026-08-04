# 查詢商家操作日誌

## 1. 場景目的

讓後台管理者或擁有權限的訂閱者，查詢指定商家（businessCode）的歷史操作記錄，用於稽核、問題追蹤或設定變更回顧。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/businesses/{businessCode}/logs/{actionType}` | 取得指定商家、指定操作類型的日誌清單 |

---

## 3. 流程總覽

1. 前端呼叫 API 並夾帶有效的 JWT 或 Session Token。
2. API Gateway / Middleware 驗證 Token 有效性及服務存取權限。
3. Controller 接收 `businessCode` 與 `actionType` 參數，執行參數校驗。
4. Controller 呼叫 Service 層，Service 層先檢查當前操作者是否具備該商家的查詢權限（通常透過 `business_accounts` 或 `businesses` 的關聯確認）。
5. 通過權限後，Service 透過 Provider 向 Cassandra 的 `logs` 或 `logs_business` 表下達查詢。
6. 查詢條件為 `businesscode = {businessCode} AND action = {actionType}`，並可能附加時間範圍（若 API 支援）。
7. 取得結果後，Service 層組裝 DTO，**屏蔽／排除敏感欄位**（例如 before/after 內容若包含密碼雜湊或 token，需過濾），再回傳。
8. 若查無資料，回傳空集合。

---

## 4. 程式流程

| 順序 | Layer | Class / Method（推測） | 動作 |
|------|-------|------------------------|------|
| 1 | Middleware | `ECAuthHandler` | 檢驗 JWT / Auth Header，解析使用者身份 |
| 2 | Controller | `BusinessController.GetBusinessLog` | 接收 businessCode、actionType，呼叫 Service |
| 3 | Service | `BusinessService.GetBusinessLogs` | 檢查業務權限（確認操作者隸屬於該 businessCode） |
| 4 | Provider | `BusinessLogProvider.GetByBusinessCodeAndAction` | 對 Cassandra `gamesettings.logs_business` 執行 CQL SELECT |
| 5 | Service | `BusinessService` | 將查詢結果轉換為 API 回傳格式，過濾敏感資料 |
| 6 | Controller | `BusinessController` | 回傳 `200 OK` 與 Log 列表 |

> **需人工確認**：上述類別名稱僅為依慣例推測，實際名稱請對照原始碼。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `gamesettings.logs_business` 或 `gamesettings.logs` | Read | 儲存商家操作日誌，以 `businesscode` 作為分區鍵、`action` 作為條件 |
| Redis | 未使用 | — | — |
| Kafka | 未使用 | — | — |

---

## 6. 重要規則

- **權限限制**：請求者必須屬於該 `businessCode` 的帳戶（`business_accounts`），且 `status = 1`（啟用）。跨商家查詢會被拒絕。
- **欄位限制**：回傳的日誌不可包含任何帳號的密碼雜湊或 `authtoken`；若 `before`/`after` JSON 中存有此類資訊，需在序列化前移除。
- **不可暴露資料**：日誌中的 `handler`、`password` 等敏感欄位不可回傳。
- **actionType 驗證**：僅接受預定義的操作類型（如 `create`、`update`、`delete`、`status_change`）；未定義的值應回傳 `400 Bad Request`。
- **狀態值限制**：此 API 僅提供讀取，無任何狀態變更。
- **查詢條件**：不允許未指定 `businessCode` 的全表掃描；Cassandra 查詢必須包含分區鍵。
- **TTL**：無。
- **Transaction**：無寫入，不涉及交易。
- **Retry**：當 Cassandra 查詢發生瞬時錯誤時，可由 Provider 層自動重試 1~2 次（視配置而定）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未提供驗證 Token | `401 Unauthorized` |
| Token 無效或過期 | `401 Unauthorized` |
| 使用者不屬於該 businessCode | `403 Forbidden` |
| businessCode 不存在於 `businesses` 表 | `404 Not Found`（或 `400` 視實作） |
| actionType 參數為非法值（如 `attack`） | `400 Bad Request` |
| Cassandra 連線逾時或查詢失敗 | `500 Internal Server Error`，後端應記錄錯誤並回傳通用訊息 |
| 查無符合條件的日誌 | `200 OK` 並回傳空陣列 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| T1 | Integration | 以有效管理者 Token 查詢既有商家的 `update` 日誌 | 200，回傳該商家的更新日誌列表 |
| T2 | Permission | 以無關帳號（不同 businessCode）查詢 | 403 或 404（取決於實作） |
| T3 | API Test | 傳入不合法的 actionType（如 `invalid`） | 400，錯誤訊息提示合法值 |
| T4 | Flow Test | 查詢完全不存在的 businessCode | 404 或適當錯誤 |
| T5 | Data Security | 檢查回傳的 JSON 中不應出現 `password` 或 `authtoken` | 所有日誌物件的欄位皆無此二鍵 |
| T6 | API Test | 日誌資料為空時 | 200，回傳空陣列 `[]` |

---

## 9. 高風險區域

- **高風險 table**：`gamesettings.logs_business`（因儲存完整設定變更內容，可能包含敏感 token 或商業邏輯細節）
- **高風險 API**：此 API 本身為查詢，但若未正確屏蔽敏感欄位，將造成資訊洩漏（如洩漏 `authtoken`）。
- **Cache consistency**：無快取，不涉及。
- **Queue retry**：未使用隊列。
- **Idempotency**：讀取操作具冪等性。
- **權限繞過**：若未嚴格驗證 businessCode 與操作者的關聯，可能導致跨商家資料洩漏。

---

## 10. 常見錯誤

- ❌ **忘記過濾 before/after JSON 中的密碼或 authtoken**：應在 DTO 組裝時遞迴掃描並移除敏感鍵。
- ❌ **未驗證 actionType**：可能導致 CQL 注入或效能問題（若直接拼接查詢）。
- ❌ **全表掃描**：當 businessCode 參數為空時不應執行 `SELECT * FROM logs`，應直接回絕請求。
- ❌ **權限驗證不足**：僅依賴 path 中的 businessCode，而未確認 Token 內的使用者是否真的擁有該商家的存取權。
- ❌ **回傳超出需求的欄位**：如將 `addtime` 或內部標記直接拋出，應只回傳前端需要的欄位（時間、操作者、動作、摘要）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `GET /api/v1/businesses/{businessCode}/logs/{actionType}`（README） |
| DB Table | `gamesettings.logs_business`（gamesettings-detail.md 中的描述） |
| 權限規則 | `gamesettings.business_accounts.status = 1` 且隸屬於該商家的帳戶方可讀取（gamesettings-detail.md） |
| 操作類型 | `action` 欄位可能值：create, update, delete, status_change（gamesettings-detail.md） |
| 敏感欄位過濾 | `password` 及 `authtoken` 不得回傳（gamesettings-detail.md） |

---

> **建議新增文件**：
> - 補充 `logs_business` 的完整 schema 與欄位說明。
> - 明確定義每個 `actionType` 對應的操作場景。