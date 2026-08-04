# 密碼重設

## 1. 場景目的
使用者驗證身份後提交新密碼，系統進行雜湊處理並持久化至 `member.gameusers.password`，不回傳任何形式的舊密碼。

---

## 2. 入口 API
*由於 OpenAPI 中未揭露明確端點，以下為依據常見設計之推測，需人工確認實際路徑。*

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/member/reset-password` | 重設密碼（可能搭配發送驗證碼或一次性 token） |

---

## 3. 流程總覽
1. 接收請求：新密碼 `new_password` 與驗證因子（例如 `reset_token` 或直接透過登入後的 `authKey`）。
2. 解析使用者身分：
   - 若以 `reset_token` 操作，需先從暫存（推測 Redis）或解碼取得對應的 `authKey` 或 `email`。
   - 若使用者已登入，則由請求標頭或 token 中取得 `authKey`。
3. 查詢 `member.gameusers` 確認使用者存在且狀態有效（`status=1`）。
4. 檢查封禁狀態：查詢 `member.gameusers_banned` 確認該 `authKey` 未被永久或有效封禁。
5. 雜湊新密碼（使用 `Hash.HashPasswordString` 或同等 BCrypt 演算法）。
6. 寫入 `member.gameusers.password`（僅更新此欄位，不影響其他欄位）。
7. 回傳成功，回應**不包含**任何密碼欄位。

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `MemberController.ResetPassword` | 接收請求，轉交 Service |
| 2 | Service | `MemberService.ResetPassword` | 協調驗證、查詢、雜湊、寫入 |
| 3 | Provider | `MemberProvider.GetGameUserByAuthKey` 或 `GetGameUserByEmail` | 查詢 `gameusers` 並檢查 `status`、`banned` |
| 4 | Validator | `PasswordValidator` | 驗證新密碼強度（長度、複雜度等） |
| 5 | Transfer | `GameUserTransfer` | 對外回傳無密碼的 DTO（成功訊息） |

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `member.gameusers` | **Read** | 依 `authkey` 或 `email` 查詢使用者，驗證存在與 `status=1` |
| DB | `member.gameusers` | **Write** | 更新 `password` 欄位（僅此欄位） |
| DB | `member.gameusers_banned` | **Read** | 檢查 `authkey` 是否有有效封禁記錄 |
| Redis | 需人工確認 | 可能讀取 | 若使用 `reset_token`，可能從 Redis 取得暫存的驗證碼或對應的 authKey |

---

## 6. 重要規則
### 權限限制
- 僅已驗證身份的使用者（authKey 或合法 token）可執行。
- 重設密碼**不允許**透過「舊密碼」方式進行（這屬於變更密碼場景的範疇，為另一個端點）。

### 欄位限制
- **`member.gameusers.password`**：
  - 僅可由重設密碼（`ResetPassword`）、變更密碼（`ChangePassword`）或註冊流程寫入。
  - 必須經過雜湊處理，**嚴禁明文儲存**。
  - 任何對外 API 回應中**不可包含**此欄位（即使雜湊值亦不允許）。

### 不可暴露資料
- 舊密碼、雜湊值、authKey（除登入成功時外）皆不可外洩。
- 回應內容僅應包含成功或失敗的狀態資訊。

### 驗證規則
- 需檢查使用者狀態：`status=1`（已啟用）且未被封禁（`gameusers_banned` 無有效記錄）。
- 密碼複雜度需符合系統規範（例如長度、字元組合）。

### Transaction 規則
- 密碼更新為單一 Cassandra 寫入，不涉及跨表交易；無需 distributed transaction。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|------|----------|
| 提供的 `reset_token` 無效或過期 | 回傳 `401 Unauthorized` 或 `400 Bad Request`，禁止更新 |
| 使用者不存在（`email` 或 `authKey` 無對應記錄） | 回傳 `404 Not Found` |
| 使用者狀態為停用或凍結（`status != 1` 或有效封禁） | 回傳 `403 Forbidden`，訊息可回傳「帳號已停用」 |
| 新密碼格式不符（太短、缺特殊字元等） | 回傳 `400 Bad Request` 並附註規則說明 |
| Cassandra 寫入失敗（逾時、不可用） | 回傳 `500 Internal Server Error`，前端可提示稍後再試 |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC-01 | API Test | 以有效 token 提交合法新密碼 | 成功，`password` 更新為雜湊值，回應不含密碼 |
| TC-02 | API Test | 使用過期 token | 失敗，HTTP 40x，密碼不變 |
| TC-03 | Permission Test | 未經驗證直接呼叫端點 | 失敗，HTTP 401 |
| TC-04 | Flow Test | 重設成功後使用新密碼登入 | 可使用新密碼登入（舊密碼失效） |
| TC-05 | Integration Test | 查詢 `gameusers` 確認 `password` 欄位確認為雜湊值 | 非明文，符合雜湊演算法格式 |
| TC-06 | Security Test | 檢查回應內容是否包含密碼欄位 | 回應 JSON / 文字中無 `password` 字串 |

---

## 9. 高風險區域
- **高風險 table**：`member.gameusers`（直接儲存密碼雜湊，寫入正確性至關重要）。
- **高風險 API**：`POST /api/member/reset-password`（密碼變更的核心入口，需嚴格驗證身份與輸入）。
- **Cache consistency**：若使用 Redis 暫存重設 token，需確保 token 一次性使用或具備短 TTL，避免被濫用。
- **Idempotency**：重設成功後不可重複使用同一 token；若多次發送請求應返回錯誤或冪等無效。

---

## 10. 常見錯誤
- ❌ 更新密碼時未進行雜湊，直接寫入明文（**絕對禁止**）。
- ❌ 在回應中意外帶出 `password` 或 `authKey` 欄位（DTO 映射必須明確排除）。
- ❌ 未檢查 `status=1` 或封禁狀態，導致已停用帳號仍可重設密碼。
- ❌ 忘記驗證重設 token 的來源與時效，僅依賴前端傳入的 `email` 直接更新（可被偽造請求）。
- ❌ 使用 `change-password` 流程來實作「忘記密碼」，導致需要輸入舊密碼而無法完成。
- ❌ 在 `member.gameusers` 查詢時未利用 `email` 上的二級索引，導致全表掃描（應 `WHERE email=?`）。

---

## 11. Evidence
| 類型 | 來源 |
|------|------|
| DB | `member.gameusers` (schema 定義) |
| DB | `member.gameusers_banned` (封禁檢查依據) |
| 規則 | `db/member-detail.md` – 寫入限制與不可回傳欄位 |
| 規則 | `webapi/pricecentersite/pricecentersite-detail.md` – 密碼寫入限制與不可回傳規則 |
| 規則 | `Hash.HashPasswordString`（推測用於雜湊，需人工確認實際方法名稱） |