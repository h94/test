# 場景：驗證驗證碼

## 1. 場景目的

提供一個內部端點，供客戶端驗證使用者輸入的六位數驗證碼是否正確。此流程為一次性驗證，驗證成功後，對應的快取記錄將被清除，防止重複使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/token/auth/{authKey}/verify` | 接收 `authKey` 與 `token` (驗證碼) 進行比對 |

| 參數 | 位置 | 類型 | 必要 | 說明 |
|---|---|---|---|---|
| authKey | path | string | 是 | 唯一識別鍵，用於定位 Redis 中的驗證碼 |
| token | query | string | 是 | 使用者輸入的六位數驗證碼 |

---

## 3. 流程總覽

1. 接收包含 `authKey` 與 `token` 的 POST 請求。
2. 根據 `authKey` 查詢 Redis，取得預存的驗證碼。
3. 比對 Redis 中的驗證碼與使用者輸入的 `token`。
4. **成功**：刪除 Redis 中的該筆驗證碼，回傳成功。
5. **失敗**：不刪除任何資料，回傳驗證失敗錯誤。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | AuthController.Verify | 接收 `authKey`(path) 與 `token`(query)，呼叫 Service |
| 2 | Service | AuthService.VerifyToken | 利用 Provider 查詢 Redis，進行比對，根據結果決定是否刪除快取 |
| 3 | Provider | **需人工確認** (RedisProvider) | 執行 Redis GET，讀取 `authKey` 對應的值；若成功則執行 DEL |
| 4 | Provider | **需人工確認** (LogProvider) | 無論成功或失敗，透過 Kafka 發送操作日誌 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | `auth_{authKey}` | Read (GET) | 取得預存的六位數驗證碼以供比對 |
| Redis | `auth_{authKey}` | Delete (DEL) | 驗證成功後清除快取，確保一次性使用 |
| Kafka | Topic: **需人工確認** | Publish | 發送此次驗證的操作日誌 |

---

## 6. 重要規則

- **一次性驗證**：Redis 中的驗證碼僅能使用一次。比對成功後必須立即刪除。
- **比對邏輯**：應為精確字串比對，不應包含模糊或部分匹配。
- **逾時處理**：Redis Key 本身設有 TTL（產生時設定），若驗證碼過期，GET 操作將返回 null，視為驗證失敗。
- **不可回傳敏感資訊**：API 回傳值應僅為成功或失敗，絕不可在回應中附帶正確的驗證碼。
- **日誌記錄**：無論驗證成功與否，均需透過 Kafka 發送日誌，包含 `authKey`、比對結果、時間戳。
- **權限**：此為內部服務 API，無使用者層級權限控管，但應由 API Gateway 或網路層保護。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 輸入的 `token` 與 Redis 中的值不符 | 回傳驗證失敗，Redis 記錄**不被刪除** |
| `authKey` 對應的 Redis Key 不存在或已過期 | 回傳驗證失敗（或 Key 不存在錯誤） |
| Redis 連線失敗 (GET 時) | 回傳伺服器錯誤 (HTTP 500)，不應視為驗證成功 |
| Redis 連線失敗 (DEL 時) | 需人工確認：驗證已成功，但 DEL 失敗會導致重複使用風險。應記錄嚴重錯誤並觸發告警。 |
| Kafka 發送失敗 | 記錄錯誤，但**不應影響** API 回傳（視為非關鍵路徑）。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| VF-01 | API Test | 提供正確的 `authKey` 與 `token` | HTTP 200，Redis 記錄被刪除 |
| VF-02 | API Test | 提供正確的 `authKey` 但錯誤的 `token` | HTTP 400/401，Redis 記錄仍存在 |
| VF-03 | API Test | 對同一個 `authKey` 再次發送 VF-01 的請求 | 應失敗，因為快取已被刪除 |
| VF-04 | API Test | 提供不存在的 `authKey` | 應失敗，回傳 HTTP 400/404 |
| VF-05 | Integration | 模擬 Redis 在 GET 時拋出異常 | API 應回傳 HTTP 500，不可回傳成功 |
| VF-06 | Integration | 驗證成功後，模擬 Redis 在 DEL 時拋出異常 | 記錄錯誤，但 API 仍應回傳成功給客戶端？**需人工確認** |
| VF-07 | Flow Test | 多次連續輸入錯誤驗證碼 | 每次均應回傳失敗，且不能刪除 Redis 記錄 |

---

## 9. 高風險區域

- **快取一致性**：若驗證成功但 `DEL` 失敗，會導致驗證碼可被重複使用。此為高風險，必須有重試機制或最終一致性的補償方案。
- **暴力破解**：若無失敗次數限制，攻擊者可嘗試猜測六位數驗證碼。風險極高。
  - **需人工確認**：是否在產生驗證碼時於 Redis 中實作失敗計數器，或由 API Gateway 進行速率限制。
- **Race Condition**：極短時間內對同一 `authKey` 發送多次請求，可能在 `GET` 和 `DEL` 之間的時間差內全部驗證成功。
  - **需人工確認**：是否使用 Redis 的原子性操作（如 Lua script 或 `GETDEL`）來確保一次性驗證。
- **Kafka 依賴性**：Kafka Publish 是 fire-and-forget，若日誌遺失將無法追溯。

---

## 10. 常見錯誤

- **新人**：在驗證失敗時也刪除了 Redis Key，導致流程中斷。
- **新人**：直接將從 Redis 讀取到的驗證碼回傳給客戶端，造成資安漏洞。
- **AI 誤解**：認為驗證碼驗證是比對 `tokens` 資料表。此場景**僅使用 Redis**，與 MySQL 完全無關。
- **常見漏檢查**：未檢查 Redis `GET` 返回的值是否為 null，導致空指標異常。
- **流程錯誤**：先回傳成功才刪除 Redis Key，應在確認刪除成功後才回傳（或使用原子操作）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/token/auth/{authKey}/verify` |
| API 參數資訊 | OpenAPI `paths./api/v1/token/auth/{authKey}/verify.post.parameters` |
| 程式分層 | 專案結構 `Controller/`, `Service/`, `Provider/` (推斷) |
| Redis 使用 | `tokenservice-detail.md` Redis 章節；README 提及「驗證碼快取至 Redis」、「驗證成功後清除快取」 |
| Kafka 使用 | README 提及「所有 Token 操作均透過 Kafka 寫入集中式紀錄」 |
| MySQL 無關性 | `tokenservice-detail.md` `tokens` 表操作皆為 Token 生命週期，與 AuthToken 驗證無關 |
| 一次性設計 | `tokenservice-detail.md` 驗證碼管理描述：「驗證成功後清除快取」 |