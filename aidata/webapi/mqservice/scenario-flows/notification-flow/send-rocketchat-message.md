# 發送 RocketChat 訊息

## 1. 場景目的

接收其他服務的訊息請求，經過驗證後，透過 RocketChat API 將訊息發送至指定目標頻道（一般頻道或 InPlayZ 專用頻道），並將發送結果記錄至 `messagelog` 表中。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/rocket/message` | 發送 RocketChat 訊息至一般頻道 |
| POST | `/api/v1/rocket/message/inplayz` | 發送 RocketChat 訊息至 InPlayZ 專用頻道 |

---

## 3. 流程總覽

1. Controller 接收 POST 請求，進行身份驗證（ECCore 3.0.2）。
2. 通過驗證後，呼叫對應 Service 處理訊息發送邏輯。
3. Service 調用 RocketChat（192.168.9.231）的 Webhook 或 API 發送訊息。
4. 根據發送結果（成功／失敗），調用 Provider 將發送記錄寫入 `stock.messagelog` 表。
5. 回傳發送結果給呼叫方。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `RocketController` | 接收 POST 請求，驗證 authKey |
| 2 | Service | `RocketService.SendMessage()` / `SendInplayzMessage()` | 處理訊息內容，調用 RocketChat Client |
| 3 | Provider | `MessageLogProvider.InsertLog()` | 寫入發送記錄至 `messagelog` 表 |
| 4 | Service | `RocketService` | 根據 RocketChat 回傳結果更新 `messagelog.SendStatus` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `stock.messagelog` | INSERT | 建立發送記錄，初始 `SendStatus = 0`（未發送） |
| DB | `stock.messagelog` | UPDATE | 根據 RocketChat API 回傳結果更新 `SendStatus` 為 `1`（成功）或 `2`（失敗） |
| External API | RocketChat（192.168.9.231） | POST | 實際發送訊息，依照頻道設定，一般或 InPlayZ 使用不同 Webhook URL 或 Payload |

> **注意事項**：根據 README，該服務描述為「純訊息轉發，無持久化」，但在 `db/stock-detail.md` 和程式碼語義中，確實存在 `messagelog` 表的寫入操作。此處保留日誌記錄，但需人工確認系統設計文檔與實作的一致性。

---

## 6. 重要規則

- **權限限制**：所有 API 需要通過 ECCore 驗證。
- **不可修改欄位**：
    - `messagelog.AddTime`：僅在建立記錄時寫入，應用層不可直接設定。
    - `messagelog.LastUpdateTime`：由 DB 自動更新，應用層不可直接寫入。
- **SendStatus 狀態流轉規則**：`SendStatus` 僅允許從 `0`（未發送）更新為 `1`（成功）或 `2`（失敗），不可設定其他值。
- **Append-Only 日誌**：`messagelog` 表採用 append-only 模式，寫入後不允許刪除，僅 `SendStatus` 可更新。
- **不可暴露資料**：對外查詢時，`messagelog.MsgContent` 不可回傳至前端。
- **RocketChat 服務相依**：本服務直接依賴內部 RocketChat 服務（192.168.9.231）進行訊息發送，若其不可用，發送將失敗。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 驗證失敗（無效或過期的 authKey） | 回傳 401 Unauthorized 錯誤 |
| RocketChat 服務無法連線（Timeout 或拒絕連線） | 記錄 `messagelog.SendStatus = 2`（失敗），回傳發送失敗的結果給呼叫方 |
| RocketChat API 回傳非 200 狀態碼 | 記錄 `messagelog.SendStatus = 2`，回傳發送失敗並附帶 RocketChat 的錯誤訊息 |
| 寫入 `messagelog` 表失敗（例如 DB 連線中斷、主鍵衝突） | 需人工確認 rollback 或重試機制，可能導致訊息已發送但無記錄（高風險） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| IT-RC-01 | Integration Test | 發送一則有效訊息到一般 RocketChat 頻道 | 訊息成功在頻道顯示，`messagelog` 記錄 `SendStatus = 1` |
| IT-RC-02 | Integration Test | 發送一則有效訊息到 InPlayZ 頻道 | 訊息成功在 InPlayZ 頻道顯示，`messagelog` 記錄 `SendStatus = 1` |
| PT-RC-01 | Permission Test | 使用無效 authKey 請求 API | 回傳 401 Unauthorized，訊息未發送，無 `messagelog` 記錄 |
| FT-RC-01 | Flow Test | 模擬 RocketChat 服務中斷 | API 回傳失敗，`messagelog` 記錄 `SendStatus = 2` |
| FT-RC-02 | Flow Test | 模擬 DB 寫入失敗 | 需人工確認系統行為（成功／失敗回傳與一致性） |

---

## 9. 高風險區域

- **外部 API 相依**：流程高度依賴 RocketChat 服務的可用性。若其服務中斷，所有請求都將直接失敗。
- **寫入一致性**：訊息發送成功，但寫入 `messagelog` 失敗，或反過來，都可能造成狀態不一致。此處缺少 Transaction 或 Compensating Transaction 機制。
- **RocketChat Webhook URL 硬編碼**：RocketChat 的連線資訊（IP：192.168.9.231）或 Webhook URL 可能以硬編碼或設定檔形式存在，變更時需要修改程式碼或設定，容易出錯。

---

## 10. 常見錯誤

- ❌ **誤解服務持久化能力**：根據 README，mqservice 被描述為「無持久化」，但實作上卻寫入 `messagelog`。新人或 AI 容易因此忽略 `messagelog` 表的存在和操作規則。
- ❌ **直接設定 `AddTime` / `LastUpdateTime`**：應用層程式碼直接指定這些時間欄位的值，違反了 DB 操作邊界的約定。
- ❌ **忽略 `SendStatus` 的狀態流轉**：錯誤地將 `SendStatus` 更新為 `0` 或其他未定義的值，或在成功後將其改為失敗狀態。
- ❌ **未處理外部 API 異常**：未對 RocketChat API 的 Timeout、網路錯誤等異常進行完整的 try-catch 處理，導致系統行為不穩定。
- ❌ **對外暴露 `MsgContent`**：在查詢或回傳 API Response 時，未遮蔽 `messagelog` 表中的 `MsgContent` 欄位。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README.md（POST /api/v1/rocket/message, POST /api/v1/rocket/message/inplayz） |
| DB | `messagelog` 表定義（`db/stock.md`, `db/stock-detail.md`） |
| Code | 程式碼語義（Controller: `RocketController`, Service: `RocketService`, Provider: `MessageLogProvider`） |
| Rules | `db/stock-detail.md`（`messagelog` 的寫入限制與 `SendStatus` 狀態流轉） |
| Service Dependency | README.md（RocketChat 192.168.9.231） |