# 建立 Token

## 1. 場景目的

建立一個新的 Token，設定有效期限（預設 60 秒，最大 432000 秒）。系統自動生成 10 字元 Token 字串並寫入 `tokens` 表（`Enabled=1`），同時透過 Kafka 發送建立日誌。`CompanyCode` 由請求端的 `authKey` 自動決定，Caller 不可手動指定。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/token/get` | 接收 `expirationtime`（秒，預設 60，上限 432000），返回 10 字元 Token 字串 |

---

## 3. 流程總覽

1. 接收請求與 `expirationtime` 參數
2. 驗證 `authKey`（從請求上下文取得），解出 `CompanyCode`
3. 驗證 `expirationtime` 範圍：0 秒至 432000 秒（5 天）
4. 系統自動生成 10 字元 Token 字串（即為 `HashKey`）
5. 計算 `ExpirationTime = 當前時間 + expirationtime`（UTC）
6. 寫入 `tokens` 表（`HashKey`, `CompanyCode`, `ExpirationTime`, `Enabled=1`）
7. 透過 Kafka 發送建立日誌（`Action = 'Token Generation Request: ' + token`）
8. 回傳 Token 字串

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | TokenController.GetToken | 接收 `expirationtime` 參數，調用 `_tokenService.CreateToken` |
| 2 | Service | TokenService.CreateToken | 取得 `_context.CompanyCode`，驗證有效期，調用 `generateHashKey()` 生成 Token，計算過期時間，調用 `setToken` 與 `setLog` |
| 3 | Service | TokenService.generateHashKey | 生成 10 字元隨機字串作為 HashKey |
| 4 | Provider | TokenService.setToken | 將 Token 資訊寫入 MySQL `tokens` 表 |
| 5 | Provider | TokenService.setLog | 記錄操作至 Kafka，內容為 `'Token Generation Request: ' + token` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `tokens` | INSERT | 建立 Token 記錄（`Enabled=1`） |
| Queue | Kafka | Publish | 發送 `Token Generation Request` 日誌 |
| Redis | `xxx_token_{HashKey}` | 無操作 | 建立 Token 時不寫入 Redis；Redis 僅在後續 `CheckToken` 驗證通過後才 SET |

---

## 6. 重要規則

- **權限限制**：`CompanyCode` 由 `authKey` 決定，Caller 不可自行指定（Evidence: tokenservice-detail.md 寫入限制）
- **欄位限制**：
  - `HashKey` 為 10 字元，系統自動生成，不可手動指定
  - `ExpirationTime` 建立後不可再 UPDATE
- **不可暴露資料**：對外回應的 Token 字串（即 `HashKey`）可返回；但任何 GET API 查詢 Token 記錄時不可返回 `HashKey`
- **TTL 規則**：`expirationtime` 參數預設 60 秒，最大 432000 秒（5 天），超出範圍應返回錯誤（Evidence: README 組態注意）
- **Transaction 規則**：需人工確認是否使用資料庫交易保證寫入一致性
- **Retry 規則**：需人工確認 Kafka 發送失敗時的重試策略
- **不可修改欄位**：`ExpirationTime` 建立後不可更新，需延長時應停用舊 Token 並重新建立

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `expirationtime` 超過 432000 秒 | 返回錯誤，拒絕建立 Token |
| `expirationtime` 小於 0 秒 | 返回錯誤，拒絕建立 Token |
| 未傳遞有效的 `authKey` | 無法取得 `CompanyCode`，請求失敗（需人工確認具體錯誤回應） |
| MySQL `tokens` 寫入失敗 | 返回 500 錯誤，Token 未建立 |
| Kafka 發送失敗 | 需人工確認是否影響 Token 建立結果（推測僅寫日誌，不應阻擋主流程） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 正常建立 Token，不指定有效期 | 返回 10 字元 Token，`tokens` 有 `Enabled=1` 記錄，有效期為 60 秒後 |
| TC02 | API Test | 正常建立 Token，指定有效期 3600 秒 | 返回 Token，過期時間為當前時間 +3600 秒 |
| TC03 | Flow Test | `expirationtime=432000`（上限） | 正常建立，過期時間為上限值 |
| TC04 | Flow Test | `expirationtime=432001`（超過上限） | 返回錯誤，Token 未建立 |
| TC05 | Flow Test | `expirationtime=0`（下限） | 正常建立，過期時間等於建立時間 |
| TC06 | Flow Test | 無效的 `authKey` | 返回錯誤，Token 未建立 |
| TC07 | Integration Test | MySQL 暫時無法連線 | 返回 500 錯誤，Token 未建立 |
| TC08 | Flow Test | 重複建立 Token | 正常建立多筆，不會檢查 `HashKey` 重複（與 `CreateTokenByOriginKey` 不同，本場景每次均生成全新 HashKey） |

---

## 9. 高風險區域

- **高風險 Table**：`tokens`（寫入操作，`Enabled` 與 `ExpirationTime` 欄位不允許後續手動修改）
- **高風險 API**：無（本場景為單純 INSERT，風險較低）
- **跨服務資料同步**：`authservice` 後續查詢 Token 時依賴 `Enabled=1` 與 `ExpirationTime > NOW()`，本場景建立的 Token 將影響授權服務行為
- **Cache Consistency**：建立 Token 時不寫 Redis，若後續立刻進行 `CheckToken` 且 Redis Miss，將 fallback 到 DB 查詢，一致性無問題
- **Queue Retry**：Kafka 發送日誌失敗時的行為需人工確認（是否阻塞主流程或丟棄）
- **Idempotency**：本場景無冪等性設計（每次請求生成全新 Token）

---

## 10. 常見錯誤

- ❌ 新人可能誤以為 Token 字串（`HashKey`）需手動傳入 → ✅ Token 由系統自動生成，API 不接受 Token 參數
- ❌ 忽略 `expirationtime` 上限驗證 → ✅ 必須驗證 0～432000 秒，超過範圍返回錯誤
- ❌ 手動指定 `CompanyCode` 試圖繞過權限 → ✅ `CompanyCode` 必須由 `authKey` 解析，不可由 Caller 傳入
- ❌ 以為本場景需檢查 `HashKey` 是否重複 → ✅ `CreateToken` 不同於 `CreateTokenByOriginKey`，每次生成全新 HashKey，不需查重或停用舊 Token
- ❌ 建立 Token 後立刻更新 `ExpirationTime` 以延長期限 → ✅ 應重新建立 Token，舊 Token 標記 `Enabled=0`

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `GET /api/v1/token/get` (OpenAPI paths) |
| DB | `tokens` table (DB schema `tokens.md`) |
| DB 寫入 | `setToken` method (code semantics: writes HashKey, CompanyCode, ExpirationTime, Enabled=1) |
| Token 生成 | `generateHashKey()` method (code semantics: generates 10-char string) |
| CompanyCode 來源 | `_context.CompanyCode` (code semantics: obtained from authKey) |
| 有效期限制 | `AppSettings` 驗證 (README 組態注意: 0～432,000 秒) |
| Kafka 日誌 | `setLog` method (code semantics: publishes `'Token Generation Request: ' + token`) |
| Redis 操作 | tokenservice-detail.md (建立 Token 時不寫入 Redis) |
| 不可手動指定 HashKey | tokenservice-detail.md 寫入限制 |
| 不可返回 HashKey | tokenservice-detail.md 不可回傳欄位 |