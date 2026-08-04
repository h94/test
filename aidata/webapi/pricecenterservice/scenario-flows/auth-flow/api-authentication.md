# API 驗證

## 1. 場景目的
描述 `pricecenterservice` 如何對每個 API 請求進行身份驗證與授權。根據現有資訊，此服務依賴 `ECFramework.ECService` 統一驗證框架。由於程式碼中未直接暴露自訂的驗證邏輯，本文件基於框架規範、README 及 DB 操作邊界進行推導與歸納，**但具體實作流程與細節需人工確認**。

---

## 2. 入口 API
根據 README，除了 `/api/heart` 與 `/api/version`，其餘所有對外 API 皆需要驗證。

| Method | Path | 說明 |
|---|---|---|
| (所有) | `/api/v1/*` | 所有業務 API，皆需要驗證 (✅) |
| GET | `/api/heart` | Health Check，不需要驗證 |
| GET | `/api/version` | 版本查詢，不需要驗證 |

---

## 3. 流程總覽 (需人工確認)
由於未提供 `ECFramework.ECService` 的詳細架構，以下為基於現有 DB 操作邊界與框架慣例推導的**假設性流程**。

1. 請求進入 `pricecenterservice` API。
2. `ECFramework.ECService` 驗證中介層攔截請求 (推測為 Middleware 或 ActionFilter)。
3. 從請求中提取身份驗證資訊 (可能是 `AuthKey`、JWT、或自訂 Header)。
4. 查詢 Cassandra `pricecenter.accounts_{brand}` 表驗證帳號狀態。
    *   需確認 `brand` 是如何決定的。
5. 驗證帳號是否 `enabled = 1` 且 `closetime` 為空。
6. 驗證密碼或其他憑證。
7. (可選) 檢查帳號 `handler` 或其他來源的額外權限。
8. 驗證通過，請求進入 Controller；失敗則回傳 401/403。

---

## 4. 程式流程 (需人工確認)
因無直接 `AuthController` 或自訂 `AuthService` 的 source code，無法提供確切的程式流程。若依照一般 ASP.NET Core 與內部框架整合的架構，其流程可能如下：

| 順序 | Layer | Class / Method (推測) | 動作 |
|---|---|---|---|
| 1 | Middleware / Filter | `ECServiceAuthMiddleware` / `ECAuthorizeFilter` | 攔截請求，提取憑證 |
| 2 | Service | `ECAuthService` / `AccountService` | 負責呼叫 Provider 查詢帳號 |
| 3 | Provider | `PriceCenterAccountProvider` | 查詢 Cassandra `accounts_{brand}` |
| 4 | Provider | `PriceCenterAccountProvider` | 驗證 `enabled` 狀態 |
| 5 | Provider | `PriceCenterAccountProvider` | 驗證 `closetime` 狀態 |
| 6 | Service | `ECAuthService` | 驗證密碼/憑證 |

**⚠️ 重要**：以上為推測流程，資深工程師需根據 `ECFramework.ECService` 套件的實作提供確切程式流程。

---

## 5. DB / Cache / Queue 使用 (需人工確認)
根據現有 DB 操作邊界，驗證流程可能涉及的資源如下。

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `pricecenter.accounts_{brand}` | Read | 驗證帳號是否存在、是否啟用、是否關閉 |
| DB (Cassandra) | `pricecenter.accounts_{brand}` | Read | 取得雜湊後的密碼進行比對 |
| Redis | 未明確使用於驗證流程 | Read/Write | 除非 `webpservice` 的快取 `price:cache:{brand}:{account}` 被用於驗證，否則無直接使用。 |
| Queue/Kafka | 無 | - | 驗證流程本身不應使用 Queue。 |

---

## 6. 重要規則
根據 DB 操作邊界文件，無論驗證框架如何實作，以下規則**必須**遵守。

- **權限限制**：所有業務 API (`/api/v1/*`) 都必須經過驗證。
- **帳號啟用規則**：驗證時必須過濾 `enabled = 1`。任何 `enabled != 1` 的帳號都不可通過驗證。
- **帳號關閉規則**：驗證時必須檢查 `closetime` 為空 (`NULL` 或 `''`)。任何 `closetime` 非空的帳號都視為已關閉，不可通過驗證。
- **不可暴露資料**：任何 API 回應或日誌中，**嚴禁**回傳 `password` 欄位（包含雜湊值）。`AuthKey`、`phone` 等敏感個資也須依規則處理。
- **帳號存在性**：需人工確認登入失敗時，應回傳通用的「帳號或密碼錯誤」訊息，避免洩露帳號是否存在。

---

## 7. 錯誤情境 (推測)
| 情境 | 預期結果 |
|---|---|
| 缺少驗證 Header/憑證 | HTTP 401 Unauthorized |
| 帳號不存在 | HTTP 401 (推測) |
| 帳號存在但 `enabled = 0` | HTTP 403 Forbidden 或 401 (推測) |
| 帳號存在但 `closetime` 非空 | HTTP 403 Forbidden 或 401 (推測) |
| 憑證錯誤 (密碼不符) | HTTP 401 Unauthorized |
| Cassandra 查詢逾時 | HTTP 500 Internal Server Error |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| `AUTH-01` | Permission Test | 不帶任何憑證呼叫 `/api/v1/games/{gameType}` | 401 Unauthorized |
| `AUTH-02` | Permission Test | 不帶任何憑證呼叫 `/api/heart` | 200 OK |
| `AUTH-03` | Flow Test | 使用有效的帳號呼叫 API | 200 OK |
| `AUTH-04` | Flow Test | 使用 `enabled=0` 的帳號呼叫 API | 403 Forbidden / 401 Unauthorized |
| `AUTH-05` | Flow Test | 使用 `closetime` 不為空的帳號呼叫 API | 403 Forbidden / 401 Unauthorized |
| `AUTH-06` | Integration Test | Cassandra 無法使用時呼叫 API | 500 Internal Server Error |

---

## 9. 高風險區域
- **高風險 Table**：`pricecenter.accounts_*`，因為包含密碼與帳號狀態。
- **Cache consistency**：若 `webpservice` 管理的 `price:cache` 被用於驗證，狀態變更時的快取一致性是風險點。

---

## 10. 常見錯誤
- **❌ 未過濾帳號狀態**：查詢帳號進行驗證時，未同時檢查 `enabled = 1` 和 `closetime IS NULL`。
- **❌ 洩露敏感資訊**：
    *   在驗證失敗的錯誤訊息中，詳細指出是「帳號不存在」還是「密碼錯誤」。
    *   在日誌中記錄了明文密碼或密碼雜湊值。

---

## 11. Evidence
| 類型 | 來源 |
|---|---|
| API 需驗證 | `README.md` - 對外 API 重點表格中的「需要驗證」欄位 |
| 不需驗證的 API | `README.md` - 系統工具表格：`/api/heart` (❌), `/api/version` (❌) |
| DB 帳號狀態規則 | `pricecenterservice-detail.md` - pricecenter 讀取規則 |
| 驗證框架 | `README.md` - 技術棧：驗證：`ECFramework.ECService` |

## 建議後續行動
1.  **人工確認**：請資深工程師提供 `ECFramework.ECService` 的文件或說明其整合方式（Middleware/Filter）。
2.  **Source Code Review**：確認是否存在自訂的 `AuthController`, `AuthService`, 或任何實作 `IAuthorizationFilter` 的類別。
3.  **Redis 用途確認**：確認 `webpservice` 管理的 `price:cache:{brand}:{account}` 快取是否參與到 `pricecenterservice` 的API驗證流程。