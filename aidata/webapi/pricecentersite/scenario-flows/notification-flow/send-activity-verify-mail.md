# 發送活動驗證碼郵件

## 1. 場景目的

此流程用於處理使用者請求發送「活動驗證碼」郵件的業務。系統必須在指定時間內（60秒）對同一組 Email 實施嚴格頻率控制，防止重複發送。驗證碼產生後，會將發送任務寫入 `stock.messagelog`（初始 `SendStatus=0`，即待發送狀態），最後委派給外部 `MailService` 完成實際的郵件派送。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/activity/verify/{site}/{activityEvent}/{authKey}` | 送出活動驗證碼發送請求 |

---

## 3. 流程總覽

1.  Controller 接收包含 `site`、`activityEvent` 與 `authKey` 的路徑參數。
2.  透過 `authKey` 驗證使用者身份（需人工確認是否調用 `member.gameusers` 進行查核）。
3.  進行 Redis 頻率控制檢查，確認同一個郵件地址在 **60 秒內** 未重複請求。
4.  產生一組新的活動驗證碼。
5.  組合郵件內容，並將發送任務寫入 `stock.messagelog` 資料表：
    *   此時 `SendStatus` 固定為 `0`（待發送）。
6.  呼叫 `MailService` 發送郵件。
    *   若呼叫失敗，`messagelog` 記錄的狀態將由 `MailService` 後續更新為 `2`（失敗）；呼叫成功則更新為 `1`（成功）。
7.  將含有驗證碼與時間戳的記錄寫入 Redis（以 `AuthToken:{email}` 為 Key），並設置 TTL，以便後續請求進行頻率校驗。
8.  回傳成功響應給客戶端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `ActivityController.Verify` | 接收請求，提取路徑參數。 |
| 2 | Validator | （未明確指定，推測由 Controller 觸發） | 驗證 `authKey` 有效性。 |
| 3 | Service | `ActivityService` 或 `VerifyService` （具體名稱待確認） | 組合驗證邏輯：解析使用者 Email、調用 Redis Provider 進行頻率檢查。 |
| 4 | Provider | `RedisProvider` / `RedisService` | 讀取 Key `AuthToken:{email}`，執行 `CreateCount` 與 `LastSendTime` 的檢查。若超出限制則拋出錯誤。 |
| 5 | Service | （同上述 Service） | 生成驗證碼，構建郵件內容。 |
| 6 | Provider | `MessageLogProvider` / `MessageLogService` | 對 `stock.messagelog` 執行 INSERT，寫入帳號、日期、動作、內容、初始 `SendStatus=0`。 |
| 7 | Service | `MailService` | 調用外部服務進行郵件發送。 |
| 8 | Provider | `RedisProvider` / `RedisService` | 寫入 Redis 記錄，使用 `AuthToken:{email}` 作為 Key，內容包含當次發送的時間戳與計數，並設定 TTL。 |
| 9 | Controller | `ActivityController.Verify` | 回傳 200 OK。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (MySQL) | `stock.messagelog` | Write | 記錄每一筆驗證碼發送任務，初始 `SendStatus` 為 `0`。 |
| DB (MySQL) | `stock.users` | Read （推測） | 根據 `authKey` 查詢使用者 `Email` 與啟用狀態。 |
| Redis | `AuthToken:{email}` | Write | 記錄本次發送的時間戳，並設定 TTL，用於後續的頻率檢查。 |
| Redis | `AuthToken:{email}` | Read | 檢查 `CreateCount` 與 `LastSendTime`，確保同一 Email **60 秒內** 不會重複觸發郵件發送。 |
| Queue | （無） | - | 現有資訊未提及使用 Kafka 或 Queue，實際發送為同步/非同步直接呼叫 `MailService`。 |

---

## 6. 重要規則

*   **頻率控制規則（Redis）**：
    *   Key：`AuthToken:{email}`
    *   檢查邏輯：當同一 Email 在 **60 秒內** 再次請求時，必須拒絕並拋出「重複發送」的錯誤。
    *   **TTL 規則**：此 Redis Key 的 TTL 設定為 **300 秒**。即使 60 秒過後，此 Key 仍會存在一段時間以利後續驗證。
*   **Messagelog 寫入規則**：
    *   `SendStatus` 的初始值固定為 **`0`**（未發送/待發送）。
    *   `SendStatus` 僅能由後續的 `MailService` 回呼或系統排程變更為 `1`（成功）或 `2`（失敗），**本服務不可直接寫入其他值**。
    *   該表為 Append-Only 模式，一旦寫入，**不可 UPDATE 或 DELETE** 記錄。
*   **不可暴露欄位**：
    *   `messagelog.MsgContent` 可能包含完整郵件內容與驗證碼，對外的任何 API 回傳皆**必須排除或進行脫敏**。
*   **不可修改欄位**：
    *   `messagelog.AddTime` 與 `LastUpdateTime` 由資料庫自動產生，應用程式端**不可手動指定或異動**。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 60 秒內對同一 Email 重複請求 | 觸發 Redis 檢查，API 返回業務錯誤（例如錯誤代碼：TOO_FREQUENT），拒絕發送。 |
| `authKey` 無效或查無此使用者 | 返回 UNAUTHORIZED 或 USER_NOT_FOUND 錯誤。 |
| `stock.messagelog` 寫入失敗 | 觸發資料庫例外，必須記錄錯誤日誌，並返回 SERVER_ERROR，**不可繼續呼叫 MailService**。 |
| `MailService` 調用失敗 | 記錄失敗日誌；`messagelog` 中的任務記錄其 `SendStatus` 最終將被更新為 `2`。API 可視設計選擇回傳成功（非同步）或回傳錯誤（同步需人工確認）。 |
| Redis 讀取或寫入失敗 | 為避免因快取問題造成阻擋，**需人工確認** 策略。預期是返回服務不可用，或降級允許通過併發送警報？ |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T-01 | Integration Test | 對一個全新的 Email 請求發送驗證碼。 | 成功寫入 `messagelog`，成功呼叫 `MailService`，成功寫入 Redis。 |
| T-02 | API Test (Rate Limit) | 同一 Email 在 15 秒內連續請求兩次。 | 第二次請求返回頻率限制錯誤（TOO_FREQUENT）。 |
| T-03 | Flow Test | `messagelog` 寫入失敗，`MailService` 未被調用。 | 觸發 Exception Handler，`MailService` 呼叫次數為 0，Redis 內不會有新的頻率控制記錄。 |
| T-04 | Permission Test | 使用一個已被停用（`Enabled=0`）的使用者 `authKey` 請求發送。 | 返回 UNAUTHORIZED 錯誤。 |

---

## 9. 高風險區域

*   **高風險 Table**：`stock.messagelog`。
    *   風險：該表為 Append-Only，若邏輯誤用 `Update`，會破壞審計與重試機制。
*   **Cache Consistency**：
    *   風險：若 `MailService` 尚未實際發送，但 Redis 寫入成功，可能導致使用者因頻率限制而無法立即重試。
*   **外部服務依賴**：`MailService`。
    *   風險：呼叫外部服務不受本服務控制，需明確處理 Timeout、Retry 策略與最終一致性（透過 `messagelog` 狀態）。
*   **Idempotency**：
    *   風險：需確認在極端情況下（如 Request 已成功但 Response 因網路問題遺失），客戶端重試時是否會生成全新的驗證碼，導致舊碼失效，新碼可能觸發頻率限制。**需人工確認**去重策略是透過前端 `Idempotency-Key` 還是後端 Redis 驗證碼校驗。

---

## 10. 常見錯誤

*   **新人常見錯誤**：
    *   誤以為 `messagelog` 可以透過 `Update` 重送訊息，實際上該表只能 INSERT 新記錄。
    *   在操作 Redis 時，使用簡單的 `StringSet` 而沒有設置 TTL，導致頻率控制永久生效。
*   **AI 易誤解點**：
    *   混淆 `AuthToken:{email}` 的 TTL (300s) 與實際的頻率限制時間 (60s)。TTL 是給 Key 的生命週期，而 60s 是程式內邏輯判斷 `LastSendTime` 的閾值。
*   **常見漏檢查項目**：
    *   忘記在寫入 `messagelog` 後，且呼叫 `MailService` 前，如果有中斷，任務狀態會停留為 `0`。
    *   未對 `messagelog.MsgContent` 進行過濾就直接存進 Log 系統。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `ActivityController.Verify` |
| DB | `stock.messagelog` |
| DB | `stock.users` （查詢 Email 與狀態） |
| Redis | `AuthToken:{email}` （Key） |
| Redis | `pricecentersite-detail.md: Redis 操作` （頻率控制規則與 TTL） |
| Code | `pricecentersite-detail.md: stock 寫入限制` （Messagelog 行為） |