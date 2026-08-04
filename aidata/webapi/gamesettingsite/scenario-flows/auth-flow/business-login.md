# 商家後台登入

## 1. 場景目的

提供商家帳號透過 `businesscode` + `account` 雙憑證登入系統後台。系統接收登入請求後，從 `gamesettings.business_accounts` 查詢帳號記錄，核對雜湊密碼，驗證帳號狀態，並驗證所屬商家訂閱有效性。登入成功後回傳身分驗證 token (需人工確認 token 格式與時效機制)。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/auth/login` (需人工確認) | 商家後台登入端點 |

需人工確認：API 路徑可能因 Controller 命名而異，實際請以 `AuthController` 或對應 Controller 標註的路由為主。

---

## 3. 流程總覽

1. 前端傳入 `businesscode`、`account`、`password`
2. 必填欄位檢查
3. 依 `businesscode` + `account` 查詢 `gamesettings.business_accounts`
4. 檢查帳號是否 `status = 1` (啟用)
5. 以 bcrypt 或對應雜湊演算法比對密碼
6. 依 `businesscode` 查詢 `gamesettings.businesses`，驗證商家存在且 `subenddate` 未逾期 (若逾期則拒絕登入)
7. 產生 session token 或 JWT (需人工確認)
8. 回傳 token 與基本資訊，不回傳 password、authtoken 等敏感欄位

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `AuthController.Login` (推測) | 接收 login request，提取 `businesscode`、`account`、`password` |
| 2 | Validator | Request Model Validation | 驗證 request body 必填欄位 `businesscode`、`account`、`password` 均不為空 |
| 3 | Service | `AuthService` / `BusinessAccountService` | 協調驗證流程、呼叫 Provider 查詢 DB、密碼比對、token 產生 |
| 4 | Provider | `BusinessAccountProvider` / `CassandraProvider` | 執行 `SELECT * FROM business_accounts WHERE businesscode = ? AND account = ?` |
| 5 | Service | `PasswordHasher` / `BCrypt` | 將 request password 進行雜湊後與 DB 內 `password` 比對 |
| 6 | Provider | `BusinessProvider` | 執行 `SELECT * FROM businesses WHERE businesscode = ?` |
| 7 | Service | Subscription Validation | 比對 `subenddate` 是否小於今日，逾期則拒絕登入 |
| 8 | Service | Token Generator (需人工確認) | 產生 token (JWT or session-based)，若需寫入 DB 則更新 `businesses.authtoken` 或用 Redis (需人工確認) |
| 9 | Controller | Return DTO | 組裝回傳物件 (排除 `password`、`authtoken`) |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `gamesettings.business_accounts` | Read (SELECT) | 以完整主鍵 `businesscode + account` 查詢帳號記錄 |
| DB | `gamesettings.businesses` | Read (SELECT) | 以 `businesscode` 查詢商家設定，驗證訂閱狀態 |
| Cache | Redis | (未使用，待擴充) | 目前服務未使用 Redis，token 管理方式需人工確認 |
| Queue | Kafka | (未使用) | 本流程未使用 Kafka |

---

## 6. 重要規則

- **完整主鍵查詢 (Cassandra 必要)**：查詢 `business_accounts` 必須同時提供 `businesscode` (分區鍵) 與 `account` (集群鍵)，不可省略 `businesscode` 做全範圍掃描。
- **密碼不可回傳**：`business_accounts.password` 在任何 GET 路由 (含管理後台) 都不可回傳。
- **密碼雜湊儲存**：密碼必須以強雜湊演算法 (如 bcrypt) 儲存，禁止儲存明文。
- **帳號啟用狀態**：登入時必須過濾 `status = 1` (啟用)；`status = 0` (凍結) 的帳號應拒絕登入。
- **商家訂閱有效性**：必須比對 `subenddate` 與當前日期，`subenddate < today` 時該商家視為過期，拒絕登入 (不可回傳遊戲設定資料給該業務)。
- **不可暴露欄位**：回傳結果不得包含 `authtoken`（認證令牌視為內部機密）、`password`。
- **updater 欄位**：應由服務端自動填入目前登入操作者帳號，不可由請求端自行指定（若本流程含登入記錄寫入則適用）。
- **business_accounts.businesscode + account**：複合主鍵寫入後不可更改，新增僅能用 `INSERT ... IF NOT EXISTS`。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `businesscode` 或 `account` 或 `password` 為空 | 回傳 400 Bad Request，提示必填欄位缺失 |
| 以 `businesscode + account` 查無資料 | 回傳 401 Unauthorized，提示「帳號或密碼錯誤」(不可區分是否帳號存在) |
| 帳號 `status = 0` (凍結) | 回傳 403 Forbidden，提示「帳號已停用」 |
| 密碼比對失敗 | 回傳 401 Unauthorized，提示「帳號或密碼錯誤」 |
| 商家 `businesscode` 不存在 | 回傳 401 Unauthorized，提示「商家不存在」 |
| 商家訂閱已過期 (`subenddate < today`) | 回傳 403 Forbidden，提示「訂閱已過期，請聯繫管理員」 |
| Cassandra 連線失敗 / timeout | 回傳 503 Service Unavailable，提示「系統忙碌中，請稍後再試」 |
| 密碼 hash 與 DB 中儲存格式不一致 (如演算法變更) | 回傳 500 Internal Server Error，需人工確認處理流程 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| AUTH-LOGIN-001 | Integration Test | 使用正確的 businesscode、account、password 登入 | 回傳 200 OK，取得 token |
| AUTH-LOGIN-002 | API Test | 缺少 `businesscode` 欄位 | 回傳 400 Bad Request |
| AUTH-LOGIN-003 | API Test | 使用不存在的 account 登入 | 回傳 401 Unauthorized |
| AUTH-LOGIN-004 | Flow Test | 使用 `status=0` 的已凍結帳號登入 | 回傳 403 Forbidden |
| AUTH-LOGIN-005 | Flow Test | 使用錯誤密碼登入 | 回傳 401 Unauthorized |
| AUTH-LOGIN-006 | Flow Test | 商家訂閱已過期 (`subenddate` 小於今日) | 回傳 403 Forbidden |
| AUTH-LOGIN-007 | Permission Test | 驗證回傳 token 是否可存取受保護資源 | token 有效，可存取對應權限資源 |
| AUTH-LOGIN-008 | API Test | 驗證登入成功後回傳內容不包含 `password` | 回傳物件中無 `password` 欄位 |
| AUTH-LOGIN-009 | API Test | 驗證登入成功後回傳內容不包含 `authtoken` (若 DB 有值) | 回傳物件中無 `authtoken` 欄位 |

---

## 9. 高風險區域

- **高風險 table**：`gamesettings.business_accounts` (密碼欄位)，`gamesettings.businesses` (authtoken 欄位)
- **高風險 API**：登入 API (POST)，若有密碼重置相關 API 也須關注
- **跨服務資料同步**：`business_accounts` 亦由 syncservice、zbaparser 寫入，需確保密碼 hash 規則一致 (如需人工確認)
- **Cache consistency**：目前無 Redis，若後續引入 token cache，需注意主動失效機制
- **Idempotency**：登入本身為非冪等操作，重複發送會產生多個 token (需人工確認 token 管理策略)

---

## 10. 常見錯誤

- ❌ **新人容易犯錯**：查詢 `business_accounts` 時忘記帶 `businesscode`，僅用 `account` 查詢 (Cassandra 會因缺少分區鍵而效能低落或被框架拒絕)。
- ❌ **新人容易犯錯**：忘記檢查 `status = 1`，導致凍結帳號能成功登入。
- ❌ **AI 容易誤解**：誤以為查詢時可以只以 `account` 搜尋，未理解 Cassandra 複合主鍵的查詢限制。
- ❌ **常見漏檢查項目**：未驗證商家 `businesses` 表，導致不存在的商家也能登入；未驗證 `subenddate` 訂閱效期。
- ❌ **常見錯誤流程**：回傳 response 時帶出 `password` 欄位 (即使為 hash 值)，或帶出 `authtoken`。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | AuthController.Login (需人工確認實際 Controller 名稱) |
| DB | `gamesettings.business_accounts` |
| DB | `gamesettings.businesses` |
| Code | `GameSettingSite.Model.User.Account`, `GameSettingSite.Model.User.Password` (來源：Source code semantics) |
| Code | `gamesettings.business_accounts.status` (來源：gamesettings-detail.md `status` 欄位說明) |
| Code | `gamesettings.businesses.subenddate` (來源：gamesettings-detail.md `subenddate` 欄位說明) |
| Rule | 完整主鍵查詢必要，不可省略 businesscode (來源：gamesettings-detail.md 讀取規則) |
| Rule | 密碼不可回傳，任何 GET 路由都不可 (來源：gamesettings-detail.md 寫入限制) |
| Rule | 需過濾 `status=1` 啟用帳號 (來源：gamesettings-detail.md `status` 欄位說明) |
| Rule | `subenddate` 逾期視為過期 (來源：gamesettings-detail.md `subenddate` 欄位說明) |
| Rule | 本服務目前未使用 Redis (來源：gamesettingsite-detail.md Redis 章節) |
| Test | AUTH-LOGIN-001 ~ AUTH-LOGIN-009 測試重點（基於上述規則與錯誤情境設計） |

---

## 建議新增規則 / 文件

- **需人工確認**：token 格式 (JWT vs session-based)、TTL、刷新機制、儲存位置 (是否使用 businesses.authtoken、Redis key pattern)。
- **需人工確認**：登入是否使用統一 Auth Service 或由 GameSettingSite 自行管理，權限模型是否需要與其他服務一致。
- **建議新增文件**：`auth-flow.md` 描述完整認證流程。
- **建議新增測試**：token 過期刷新測試、多裝置登入行為測試。