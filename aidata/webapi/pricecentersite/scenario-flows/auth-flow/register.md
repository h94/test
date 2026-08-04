# 用戶註冊

## 1. 場景目的
描述新用戶透過 Email／密碼方式完成註冊的完整流程，確保資料正確寫入 `member.gameusers`，帳號狀態預設為「未啟用（status=0）」，並產生唯一 `authkey` 供後續驗證使用。此流程是會員系統的入口，須嚴格執行禁用域名檢查與密碼雜湊，以符合安全規範。

---

## 2. 入口 API
| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/auth/register`（需人工確認實際路徑） | 接收註冊請求，回傳基本成功資訊（不含 authkey） |

---

## 3. 流程總覽
1. 接收註冊請求，包含 `email`、`password`、`account` 及選填的 `showcode`（推薦碼）。  
2. 驗證 `email` 格式（正則表達式）。  
3. 查詢 `member.forbidden_email_domains`，檢查 email 域名是否被禁止。  
4. 透過 `member.gameusers` 的 `email` 索引確認該 email 尚未被使用。  
5. 對 `password` 進行不可逆雜湊（如 bcrypt/PBKDF2）。  
6. 系統產生 `authkey`（`Hash.HashAuthString(account)`）作為主鍵。  
7. 設定預設值：`status=0`（未啟用）、`rank=1`、`site/siteid` 依當前站點。  
8. 將資料寫入 `member.gameusers`（含 `authkey`、`email`、`password`、`status` 等）。  
9. 寫入成功後，若有 `showcode` 則建立推薦關係（`gameusers_recommend`）。  
10. 回傳成功訊息，用戶需透過 Email 驗證後才能啟用帳號。

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `AuthController.Register`（需人工確認） | 接收請求，呼叫 Service |
| 2 | Service | `AuthService.Register` | 協調驗證與寫入 |
| 3 | Validator | `EmailValidator` | 格式與禁止域名檢查 |
| 4 | Provider | `MemberProvider.GetForbiddenDomains` | 讀取 `forbidden_email_domains` |
| 5 | Provider | `MemberProvider.GetUserByEmail` | 查詢 email 是否存在 |
| 6 | Service | `HashUtil.HashPassword` | 密碼雜湊 |
| 7 | Service | `HashUtil.HashAuthString` | 產生 authkey |
| 8 | Provider | `MemberProvider.InsertGameUser` | 寫入 `member.gameusers` |
| 9 | Provider | （選用）`RecommendProvider.InsertRecommend` | 建立推薦關係 |

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB（Cassandra） | `member.forbidden_email_domains` | Read | 檢查 email 域名是否在黑名單 |
| DB（Cassandra） | `member.gameusers`（透過 email 索引） | Read | 確認 email 未被註冊 |
| DB（Cassandra） | `member.gameusers` | Write | 寫入新用戶資料（含 authkey、password、status=0） |
| DB（Cassandra） | `member.gameusers_recommend`（選用） | Write | 記錄推薦關係 |
| Redis | 無直接使用 | – | 此流程未使用 Redis 快取（驗證郵件發送階段可能使用 `AuthToken:{email}`，但非本文件範圍） |

---

## 6. 重要規則
- **權限限制**：任何第三方不可直接指定 `authkey`，必須由系統產生。  
- **欄位限制**：  
  - `email` 必須經過標準格式驗證，且域名不得出現在 `forbidden_email_domains` 中。  
  - `password` 不得明文儲存，所有雜湊操作須在服務端完成。  
  - `status` 預設為 `0`（未啟用），僅 email 驗證後才可改為 `1`。  
  - `site` / `siteid` 寫入後不可變更。  
  - `authkey` 為 `member.gameusers` 主鍵，不可更新。  
- **不可暴露資料**：所有對外 API 不得回傳 `password` 或 `authkey`（僅登入成功時可回傳一次 `authkey` 作為 token）。  
- **Transaction 規則**：此流程未使用跨表交易（Cassandra 不支援）；若推薦寫入失敗不影響主流程。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|------|----------|
| email 格式無效 | 回傳 400 Bad Request，錯誤訊息提示格式錯誤 |
| email 域名在禁止清單內 | 回傳 400，提示不允許的郵箱提供商 |
| email 已被註冊 | 回傳 409 Conflict，提示帳號已存在 |
| 密碼長度不足（規則需人工確認） | 回傳 400，提示密碼不符合安全規則 |
| `member.gameusers` 寫入失敗 | 回傳 500 Internal Server Error，前端提示稍後再試 |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| REG-01 | Integration Test | 使用合法 email 與密碼註冊 | 成功寫入 DB，status=0 |
| REG-02 | Permission Test | 嘗試在請求中傳入自訂 authkey | 忽略或拒絕，系統使用自產 authkey |
| REG-03 | API Test | email 包含禁止域名（如 `@temp.com`） | 回 400，不可註冊 |
| REG-04 | Flow Test | 註冊後立即嘗試登入（status=0） | 登入失敗（需 status=1） |
| REG-05 | Error Test | 重複註冊相同 email | 回 409 |

---

## 9. 高風險區域
- **密碼雜湊**：若使用弱雜湊或明文儲存，將導致資安問題。  
- **`authkey` 生成演算法**：若可被預測，可能導致帳號劫持。  
- **email 唯一性約束**：Cassandra `email` 索引為次級索引，大量併發可能導致效能瓶頸，需注意註冊 QPS。  
- **`status=0` 的資料清理**：長期未驗證的帳號應有排程處理，避免垃圾資料堆積。

---

## 10. 常見錯誤
- **未檢查 `forbidden_email_domains`**：直接寫入，導致違規郵箱漏入。  
- **前端傳入的 `authkey` 被直接採用**：應強制使用服務端生成的值。  
- **在回傳給前端的 JSON 中意外包含 `password` 欄位**：DTO 映射時須明確排除。  
- **忘記設定 `status=0`**：導致用戶無需驗證即可登入。

---

## 11. Evidence
| 類型 | 來源 |
|------|------|
| API | OpenAPI 未明確收錄，推測為 `POST /api/auth/register`；需人工確認 |
| DB | `member.gameusers`（authkey、email、password、status 等） |
| DB | `member.forbidden_email_domains`（域名黑名單） |
| Code | `Hash.HashAuthString(account)` 用於產生 authkey（from db-usage） |
| Code | `Hash.HashPasswordString` 用於密碼雜湊（from db-usage） |
| Rules | service-detail：`password` 須經雜湊，`authkey` 不可由外部指定，`status` 預設為 0，email 需驗證禁用域名 |