# 產生驗證碼 (AuthToken Generation)

## 1. 場景目的
依外部傳入的 `authKey` 產生一組六位數驗證碼，存入 Redis 並設定有限存活時間 (TTL)，供後續驗證流程使用；同時回傳該 `authKey` 當前的建立次數與最後發送時間，協助前端控制發送頻率。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/token/auth/{authKey}` | 根據 `authKey` 要求生成驗證碼 |

---

## 3. 流程總覽

1. 接收 `authKey` 路徑參數
2. 檢查 `authKey` 合法性（可能從中解析公司代碼，或驗證其格式）
3. 產生六位數隨機驗證碼
4. 以 `authKey` 為索引將驗證碼與相關 metadata 寫入 Redis
5. 設定 Redis key TTL（過期時間，推測為固定值或可配置）
6. 取得或更新 `createCount`（建立次數）與 `lastSendTime`（最後發送時間）
7. 回傳 `AuthToken` 物件（含驗證碼、建立次數、最後發送時間）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `TokenController.PostAuthToken` (推測) | 接收 `authKey`，呼叫 Service |
| 2 | Service | `AuthTokenService.GenerateAsync` (推測) | 執行驗證碼產生、Redis 寫入、計數更新 |
| 3 | Provider | `RedisProvider (或多個)` | 原子操作 Redis Hash: 設定 token、更新 createCount、lastSendTime |
| 4 | Helper | `RandomGenerator` | 產生六位數驗證碼 |

> **注意**：由於程式碼未提供，以上 Class/Method 名稱為推測，實際名稱需人工確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Redis | Key（推測格式：`auth:token:{authKey}`） | Write / HSET | 儲存驗證碼 `token`、`createCount` 與 `lastSendTime` |
| Redis | 同上 Key | 設定 TTL | 驗證碼存活時間（過期自動清除） |
| Redis | 同上 Key | Read / HINCRBY (createCount) | 累計建立次數 |
| Kafka | - | Publish（可能） | 紀錄驗證碼產生事件（OpenAPI / README 未明述，需人工確認） |

> MySQL `tokens` 與 `logs` 表**未參與**此流程，此場景僅使用 Redis 與可能 Kafka。

---

## 6. 重要規則

- **權限限制**：需要合法的 `authKey`；具體驗證機制可能由 authservice 或自有的解密邏輯處理（需人工確認）
- **欄位限制**：`token` 欄位在回應中為 `nullable`，可能代表若產生失敗或非首次查詢則不回傳明文 (僅在首次建立時回傳)
- **不可暴露資料**：`AuthToken.token` 為六位數驗證碼，回傳時需確認傳輸安全（HTTPS），且不可寫入持久化 DB（僅存 Redis）
- **TTL 規則**：Redis key TTL 須設定，逾期驗證碼失效；建議值：300 秒 (5 分鐘)（需人工確認實際配置）
- **Transaction 規則**：Redis 操作（設定 token、更新計數、設定 TTL）應使用 `MULTI/EXEC` 或 Pipeline 保證原子性（若程式使用 StackExchange.Redis）
- **狀態值限制**：`createCount` 無上限，但前端可依此做頻率限制（服務本身無限制）
- **不可修改欄位**：`createCount` 與 `lastSendTime` 僅可由服務端原子遞增/更新，不得由客戶端傳入

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `authKey` 不存在或格式不符 | 回應 400 Bad Request 或 401 Unauthorized（取決於驗證邏輯） |
| Redis 連線失敗 | 回應 500 伺服器錯誤，可能記錄錯誤日誌 |
| Redis 寫入失敗（逾時等） | 回應 500 或重試機制（需人工確認） |
| 產生驗證碼時系統資源不足 | 回應 500 |
| `authKey` 有效但 TTL 操作失敗 | 可能導致 Redis key 永不過期（需人工確認異常處理有無 fallback） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| AT-001 | API Test | `POST /api/v1/token/auth/validKey` | 200，回傳包含 token, createCount≥1, lastSendTime |
| AT-002 | Flow Test | 相同 `authKey` 連續呼叫兩次 | 第二次 createCount 累加 (2)，lastSendTime 更新，token 可能為 null (需確認) |
| AT-003 | Redis Test | 寫入成功後，直接讀取 Redis key | Key 存在，Hash 欄位正確 |
| AT-004 | TTL Test | 寫入後等待 TTL 時間過期 | Redis key 自動消失 |
| AT-005 | Permission Test | 傳送無效或偽造的 `authKey` | 應回傳非 200（如 401/400） |
| AT-006 | Error Test | Redis 離線狀態下呼叫 | 500 回應，不洩漏內部資訊 |

---

## 9. 高風險區域

- **高風險資源**：Redis key `auth:token:{authKey}` 存有明碼驗證碼，若快取被未授權存取或未加密傳輸，可能造成安全漏洞。
- **高風險 API**：此端點無明顯速率限制，若未搭配前端或 API Gateway 的 rate limiting，易受暴力測試。
- **Cache consistency**：若因故 Redis 寫入成功但未設定 TTL，key 將永存佔用記憶體。
- **Idempotency**：重複請求會增加 `createCount`，非冪等，前端需注意不可重複發送以免誤計次數。

---

## 10. 常見錯誤

- **新人容易犯錯**：誤以為此端點會寫入 MySQL `tokens` 表 → 實際僅操作 Redis。
- **AI 容易誤解**：認為後續驗證碼驗證 (POST .../verify) 與此流程是同一個 token，實為一分離的驗證步驟（另需 Scenario）。
- **常見漏檢查項目**：未檢查 authKey 是否具備足夠權限（例如已過期的 authKey 仍可產碼），若有相關驗證邏輯應補強。
- **常見錯誤流程**：直接從 Redis 刪除 key 卻沒有檢查是否成功，可能遺留孤兒 key。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI：POST /api/v1/token/auth/{authKey} |
| 回應結構 | OpenAPI schemas/AuthToken |
| 功能描述 | README.md：「產生六位數驗證碼並快取至 Redis」 |
| Redis 使用 | tokenservice-detail.md：Redis 快取 AuthToken（需人工確認實際 key 命名規則） |
| 責任邊界 | tokenservice-detail.md：本服務不負責使用者認證，authKey 驗證由 authservice 或內部邏輯處理（需人工確認） |
| 無 DB 參與 | DB schema 無對應 auth token 儲存表，且 db-usage 未提及此場景用 MySQL |
| 程式碼 | 未提供實際程式碼，本文 Class/Method 名稱為推測；需人工比對 `TokenController.cs` 與相關 Service 檔案確認 |

---

### 建議新增文件/規則

- 新增 `authKey` 格式規範與驗證規則（目前僅推測）
- 明確定義 Redis 儲存結構與 Key 前綴（如 `auth:token:{authKey}`）
- 定義 TTL 預設值及可配置性
- 若 Kafka 發送日誌，應補上發送事件定義
- Rate limiting 機制文件化

> **備註**：部分細節（如 authKey 驗證邏輯、Redis pipeline 使用、Kafka 整合）在現有文件中未明述，需由資深工程師確認後補齊。