# 訂閱者用戶註冊

## 1. 場景目的
為訂閱者（Subscriber）建立用戶登入帳號，支援後續登入管理後台工具。密碼必須以 bcrypt 強雜湊儲存，禁止明文。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/subscriber/users/register` | 訂閱者用戶註冊 |

---

## 3. 流程總覽

1. 接收註冊 request（含 `username`、`password` 及其他必要欄位）
2. 驗證請求參數格式與必填欄位
3. 使用 bcrypt 將原始密碼雜湊處理
4. 寫入訂閱者用戶資料至對應儲存層
5. 記錄操作日誌
6. 回傳註冊成功結果（不含 `password` 與任何敏感欄位）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `GameSettingServiceController.SubscriberUsersRegister` | 接收 HTTP POST request，呼叫 Service |
| 2 | Service | `ISubscriberService.CreateSubscriberUser` | 處理註冊邏輯、bcrypt 雜湊、呼叫 Provider |
| 3 | Provider | Cassandra Provider（需人工確認實際類別） | 執行對應儲存層 INSERT |
| 4 | Transfer | DTO / Response 物件 | 排除 `password` 後回傳結果 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `pricecenter.accounts_{brand}` | Write | 寫入訂閱者用戶帳號、已雜湊密碼、狀態等（需人工確認實際寫入 Table） |
| DB | Cassandra `action_logs` | Write | 寫入操作日誌（需人工確認） |
| Queue | Kafka | Publish | 非同步日誌發送（需人工確認） |

**需人工確認**：
- 現有文件未明確定義「訂閱者用戶」對應的 DB Table（可能為 `pricecenter.accounts_*` 或獨立 Table），需確認實際寫入目標。
- 是否使用 Redis 快取註冊狀態或暫存資料，需人工確認。

---

## 6. 重要規則

- **密碼規則**：僅註冊／密碼修改 API 可寫入 `password`，且必須以 bcrypt 強雜湊儲存，禁止明文或 MD5 直接寫入（source: `gamesettingservice-detail.md` / `pricecenter-detail.md` 寫入限制）。
- **不可回傳規則**：任何對外 API 回傳皆不得包含 `password` 欄位（source: `gamesettingservice-detail.md` 不可回傳欄位）。
- **帳號唯一性**：`account` 一旦建立即不可更新（主鍵語意）（source: `gamesettingservice-detail.md` 寫入限制）。
- **權限規則**：此 API 需要驗證（source: README `需要驗證` 欄位 ✅）。
- **操作日誌**：應記錄操作者、時間、動作類型（create）及變更內容（source: `gamesettings-detail.md` logs 用途說明）。
- **狀態初始值**：新建帳號預設啟用（`enabled=1` 或 `status=1`）（source: `gamesettingservice-detail.md` status 狀態流轉）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 缺少必填欄位（如 `username` 或 `password`） | 回傳 400 Bad Request，附錯誤訊息 |
| `password` 格式不符（如需最少長度） | 回傳 400 Bad Request，提示密碼規則 |
| 帳號已存在（違反唯一性） | 回傳 409 Conflict，提示帳號已存在 |
| 未通過驗證或權限不足 | 回傳 401 Unauthorized 或 403 Forbidden |
| bcrypt 雜湊處理失敗 | 回傳 500 Internal Server Error |
| DB 寫入失敗或 timeout | 回傳 500，記錄錯誤日誌 |
| Kafka publish 失敗（日誌發送） | 不影響主流程，但需記錄告警 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC-001 | API Test | 提供合法參數（含有效密碼） | 201 Created，回傳不含 `password` 的用戶資訊 |
| TC-002 | API Test | 缺少 `password` 欄位 | 400 Bad Request |
| TC-003 | API Test | 提供過短或無效密碼格式 | 400 Bad Request |
| TC-004 | API Test | 重複註冊相同帳號 | 409 Conflict |
| TC-005 | Flow Test | 驗證 DB 中的 `password` 為 bcrypt 雜湊值 | 無法透過明文比對成功，僅能使用 bcrypt.verify 驗證 |
| TC-006 | Permission Test | 未帶有效 Token 呼叫 API | 401 Unauthorized |
| TC-007 | Integration Test | Kafka 不可用時註冊 | 註冊成功，日誌記錄告警 |

---

## 9. 高風險區域

- **密碼處理**：任何明文密碼暫存或記錄至日誌都會導致資安風險。
- **DB 寫入對象不明確**：若誤寫入錯誤 Table（如 `gamesettings.business_accounts` 而非正確的訂閱者 Table），會導致資料錯亂（需人工確認）。
- **Transaction**：若註冊涉及多個儲存層寫入（如 DB + 日誌），需確認有 Transaction 或補償機制。
- **Idempotency**：若客戶端重試，需確保不會重複建立相同帳號。
- **Cache consistency**：若有使用 Redis 快取帳號狀態，註冊後應注意快取初始化或失效策略。

---

## 10. 常見錯誤

- ❌ 日誌中記錄原始密碼或完整 request body → ✅ 必須對 `password` 欄位脫敏。
- ❌ 使用快速雜湊（MD5/SHA1）或未使用鹽值的雜湊 → ✅ 必須使用 bcrypt（含鹽）。
- ❌ API response 回傳 `password`（即使已雜湊） → ✅ DTO 轉換時明確排除此欄位。
- ❌ 未檢查帳號是否已存在 → ✅ 必須先查詢確認唯一性。
- ❌ 註冊後未記錄 `updater` 或操作者資訊 → ✅ 應一併填入當前操作者帳號及時間。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | GameSettingServiceController - POST `/api/v1/subscriber/users/register` |
| DB | `pricecenter.accounts_{brand}`（寫入限制參考 `pricecenter-detail.md`） |
| Code | `ISubscriberService.CreateSubscriberUser`（Phase1 semantics） |
| Rules | `gamesettingservice-detail.md` - password 寫入限制與不可回傳欄位 |
| Rules | `gamesettings-detail.md` - 不可回傳欄位與寫入限制 |