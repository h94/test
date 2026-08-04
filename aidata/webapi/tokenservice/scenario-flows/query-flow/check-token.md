# 驗證 Token

## 1. 場景目的

接收客戶端傳入的 Token 字串，透過多層快取與資料庫查詢驗證 Token 有效性，並回傳整數型態的驗證結果（推測為剩餘有效秒數或狀態碼）。本流程亦負責將驗證事件透過 Kafka 寫入集中式日誌，供稽核與監控告警使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/token/check` | 傳入 query 參數 `token`，回傳整數（可能為剩餘有效秒數，0 或負數代表無效） |

---

## 3. 流程總覽

1. 接收請求，取得 `token` 參數（即 HashKey）
2. 以 `xxx_token_{HashKey}` 為 key 查詢 Redis
3. 若 Redis 命中，直接回傳整數值（推測為預存的剩餘時間或狀態）
4. 若 Redis 未命中，查詢 MySQL `tokens` 表，條件：`HashKey = @HashKey AND Enabled = 1 AND ExpirationTime > UTC_NOW()`
5. 若資料庫無符合記錄，回傳失敗（推測回傳 0 或負數）
6. 若資料庫有符合記錄，計算剩餘有效秒數 = `ExpirationTime - NOW()`
7. 以 TTL = 剩餘秒數 將剩餘有效秒數寫入 Redis（`SET xxx_token_{HashKey} <value> EX <TTL>`）
8. 透過 Kafka 發送驗證日誌（Action: `CheckToken` + HashKey）
9. 回傳剩餘有效秒數至客戶端

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `TokenController.CheckToken` | 接收參數 `token` (HashKey)，呼叫服務層 |
| 2 | Service | `TokenService.CheckToken` | 組合 Redis key `xxx_token_{HashKey}`，查詢 Redis |
| 3 | Cache | Redis | 讀取快取，若命中則回傳數值 |
| 4 | Service | `TokenService.CheckToken` | 若 Redis miss，組合 SQL 查詢：`SELECT * FROM tokens WHERE HashKey=@HashKey AND Enabled=1 AND ExpirationTime > UTC_NOW()` |
| 5 | DB Provider | MySQL | 執行查詢並回傳 `tokens` 記錄 |
| 6 | Service | `TokenService.CheckToken` | 計算 `(ExpirationTime - DateTime.UtcNow).TotalSeconds`，呼叫 Redis SET with TTL，呼叫 Kafka producer 發送日誌 |
| 7 | Messaging | Kafka | 非同步推送驗證日誌 |
| 8 | Controller | `TokenController.CheckToken` | 回傳 `200 OK`，body 為整數（剩餘秒數） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Redis | `xxx_token_{HashKey}` | Read | 查詢 token 是否已有快取 |
| Redis | `xxx_token_{HashKey}` | Write (SET with TTL) | 將有效 token 結果寫入快取，TTL = 剩餘有效秒數 |
| MySQL | `tokens` | Read | Redis miss 時查詢 token 啟用狀態與過期時間 |
| Kafka | topic (需人工確認) | Publish | 記錄驗證事件（集中式日誌） |

---

## 6. 重要規則

- **權限限制**：本 API 未實作端點權限定義於 OpenAPI，可能仰賴上游 authservice 進行驗證，需人工確認。
- **欄位限制**：查詢 `tokens` 時必須同時滿足 `Enabled = 1` 與 `ExpirationTime > UTC_NOW()`，不可遺漏任何條件。
- **不可暴露資料**：回應主體僅為整數，不可回傳 `HashKey`、`CompanyCode`、`ID` 等敏感資料。
- **TTL 規則**：Redis 快取 TTL = `ExpirationTime - 當前 UTC 時間`（秒），避免快取比實際過期時間更晚失效。
- **Transaction 規則**：此流程為讀取操作，不涉及寫入交易，但寫入 Redis 時若失敗不應影響 API 回應（僅導致下次查詢重複查 DB）。
- **重試規則**：Redis 寫入失敗不重試；Kafka 發送失敗時應記錄錯誤 log 並讓請求成功回傳（日誌不應阻斷業務）。
- **狀態值限制**：`Enabled` 僅允許 0 或 1；查詢時固定加 `Enabled=1` 條件。
- **不可修改欄位**：`ExpirationTime` 建立後不可 UPDATE，本流程僅讀取。
- **時區**：所有時間比對皆使用 UTC。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| Token 不存在或已過期 (`Enabled=1 AND ExpirationTime <= NOW()`) | 回傳失敗（推測整數 0 或負數），不回傳敏感資訊 |
| Token 已停用 (`Enabled=0`) | 同 no record，回傳失敗 |
| Redis 連線失敗 | 跳過快取讀取，直接查 DB，流程可順利完成 |
| Redis 寫入失敗 | 記錄 log，仍回傳成功（不影響主流程） |
| DB 查詢 timeout | 回傳 HTTP 500，需人工確認 |
| Kafka publish 失敗 | 記錄 log，仍回傳成功（不中斷響應） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC01 | API Test | 傳入有效尚未快取的 token，DB 存在且未過期 | 回傳正整數（剩餘秒數），Redis 被寫入 |
| TC02 | API Test | 傳入有效且 Redis 已快取的 token | 回傳相同整數，不查 DB（可透過 DB log 確認無查詢） |
| TC03 | Flow Test | 傳入已過期的 token | 回傳失敗，無 Redis 寫入，無 Kafka 日誌（需人工確認） |
| TC04 | Flow Test | 傳入 Enabled=0 的 token | 回傳失敗 |
| TC05 | Fault Injection | Redis 不可用 | API 應回傳成功（因 DB 查詢仍可執行） |
| TC06 | Flow Test | 驗證日誌是否成功寫入 Kafka | 檢查 Kafka topic 有對應 Action: CheckToken |

---

## 9. 高風險區域

- **高風險 table**：`tokens`（儲存核心授權 token），任何不當讀取或權限旁路可能導致未授權存取。
- **高風險 API**：`/api/v1/token/check`，公開驗證入口，若缺少速率限制可能被暴力列舉。
- **跨服務資料同步**：Token 狀態變更（停用、重建）時，Redis 可能未及時刪除，需依靠 TTL 或事件驅動清除，本流程無主動刪除，需整體架構確認一致性。
- **Cache consistency**：Redis 快取與 DB 可能發生時間差，例如 token 被手動停用但 Redis 仍有效，可能短暫允許已停用 token 通過驗證。TTL 設計可減輕，但非即時同步。
- **Queue retry**：Kafka 發送若失敗無重試，可能遺失稽核日誌，需確認日誌重要性。
- **Idempotency**：本 API 為冪等，重複請求不改變系統狀態（除 Redis 可能刷新 TTL）。

---

## 10. 常見錯誤

- ❌ 新人可能忽略查詢 `Enabled = 1`，僅用 `HashKey` 查找，導致停用 token 仍通過驗證。
- ❌ 計算剩餘時間時使用本地時間而非 UTC，可能造成時區錯誤。
- ❌ 將 `HashKey` 欄位回傳至客戶端或記錄於 log 中明文輸出。
- ❌ AI 可能誤認為驗證失敗時也需寫入 Kafka 或 logs，但事實上只有驗證成功才記錄（此處需人工確認）。
- ❌ 在 Redis 寫入失敗時拋出例外，導致整個請求失敗，但正確應容錯繼續。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI `GET /api/v1/token/check` |
| DB | MySQL `tokens` 表結構 (db/tokens.md) |
| Redis Key | Service detail: `xxx_token_{HashKey}` |
| SQL 條件 | Service detail: `Enabled = 1 AND ExpirationTime > NOW()` |
| 快取邏輯 | Service detail: SET on check success, GET on check attempt |
| Kafka 日誌 | README: 「所有 Token 操作（生成 / 驗證）均透過 Kafka 寫入集中式紀錄」 |
| 回傳值 | OpenAPI: response `integer (int32)`；場景說明提及「剩餘時間或狀態」 |
| 程式入口 | Controller: `TokenController.CheckToken` (推測) |

---

**⚠️ 待人工確認事項**  
- 回傳整數的具體語意（剩餘秒數、狀態碼 -1/0/1 等）  
- Kafka topic 名稱與日誌格式（Action 內容）  
- 失敗（無效 token）時是否仍寫入 Kafka / logs  
- 是否實作速率限制或 authKey 前置驗證  
- Redis key 中的 `xxx_` 前綴具體值