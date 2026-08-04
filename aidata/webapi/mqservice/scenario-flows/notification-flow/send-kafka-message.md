# Kafka 訊息發送流程

## 1. 場景目的
本場景描述 MQService 接收外部服務請求後，完成身份驗證、將訊息寫入指定 Kafka Topic，並於 `messagelog` 表留下非同步發送日誌的完整流程。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/kafka/message` | 發送 Kafka 訊息至指定 Topic |

---

## 3. 流程總覽

1. 接收包含 Topic、訊息內容的 POST 請求。
2. 透過 ECCore 驗證請求方身份 (API Token)。
3. 將訊息內容寫入指定 Kafka Topic（外部叢集 192.168.55.85~87）。
4. 根據 Kafka 寫入結果，寫入一筆記錄至 `stock.messagelog`（需要 Account 資訊，由驗證機制提供或由 request 指定）。
5. 回傳發送結果（成功或失敗）。

> **⚠️ 需人工確認**：本服務的 README 聲明「無資料庫，純訊息轉發」；然而 source code 與 `db-usage` 皆證據顯示 `POST /api/v1/kafka/message` 會寫入 `messagelog` 表，且 Controller 有 `MessagelogProvider` 依賴。以下以 source code 與 detail 文件為準。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `KafkaController.SendMessage` | 接收 `KafkaMessageRequest` (Topic, MsgContent 等)；透過 `[RQ.Authorized]` 驗證請求 |
| 2 | Controller | `KafkaController.SendMessage` | 調用 `KafkaProducer.SendMessageAsync` 寫入訊息 |
| 3 | Provider | `KafkaProducer` (推測服務) | 執行底層 Kafka producer 寫入操作 (BootstrapServers: 192.168.55.85~87) |
| 4 | Controller | `KafkaController.SendMessage` | 成功或失敗後調用 `MessagelogProvider.InsertLog` |
| 5 | Provider | `MessagelogProvider` | 寫入一筆資料至 `messagelog` 表 (SendStatus=0，隨後依發送結果更新為 1 或 2) |
| 6 | Controller | `KafkaController.SendMessage` | 回傳 `KafkaResponse` (成功或失敗資訊) |

> **⚠️ Code Evidence 限制**：`KafkaController` 調用 `IMessagelogProvider` 和 `IKafkaProducer` 的具體實作批次中無詳細 source；以下 DB 操作以 `mqservice-detail.md` 與 `stock-detail.md` 的約定為準。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Queue | Kafka (192.168.55.85~87) | Publish | 將訊息寫入指定 Topic 供下游消費 |
| DB | stock.messagelog | Write (INSERT) | 建立一筆發送日誌，初始 `SendStatus=0` |
| DB | stock.messagelog | Update (UPDATE) | 依發送結果更新 `SendStatus` 為 1 或 2 |
| DB | stock.users | Read | （若有相關檢查）可能需要確認使用者狀態，但本流程無直接寫入使用者狀態 |

本場景 **未使用 Redis**。

---

## 6. 重要規則

- **身份驗證**：所有呼叫 `POST /api/v1/kafka/message` 的請求必須通過 ECCore 的驗證。
- **messagelog 寫入限制**：
  - `messagelog.AddTime`、`LastUpdateTime` 由系統自動處理，應用層不可手動指定（`AddTime` 僅建立時寫入，`LastUpdateTime` 為 timestamp 自動更新）。
  - `SendStatus` 只允許三種值：0（未發送）、1（成功）、2（失敗）。
  - 本表為 append-only 日誌，**不可 DELETE**；只能 INSERT 後，更新 `SendStatus`。
- **不可回傳欄位**：`messagelog.MsgContent` 不可作為 API Response 回傳，僅限內部記錄。
- **Account 來源**：`messagelog.Account` 必須來自經過驗證的請求身份（ECCore 驗證後的用戶帳號），不可直接由 request 任意指定（需人工確認 Controller 是從 token 解析還是信任 request body 的 Account 欄位）。
- **Kafka 寫入保證**：需視業務需求決定是否要有 at-least-once 或強一致性。目前無證據顯示有 Kafka transaction 或 retry policy。
- **需人工確認**：Kafka 寫入失敗時，是否重試，或者直接記錄 `SendStatus=2` 後返回錯誤。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 請求未攜帶有效 API Token (ECCore 驗證失敗) | 回傳 401 Unauthorized，不寫入任何記錄（不寫 messagelog，不發送 Kafka） |
| Kafka 連線失敗 (broker unreachable) | 捕捉例外；仍寫入 `messagelog`，並將 `SendStatus` 設為 2（失敗）；回傳失敗原因給呼叫方 |
| Kafka 寫入超時 (timeout) | 同上，寫入 messagelog 的失敗記錄；回傳 `KafkaResponse` 失敗狀態 |
| messagelog 寫入失敗 (DB 連線異常) | 需人工確認：Kafka 已發送但 log 寫入失敗時如何補償（現無發現 Transaction 機制，兩者獨立執行） |
| request 未提供 Topic | 需人工確認：Controller 應有 model validation 阻擋或使用預設值 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| KFK-01 | API Test | 正常請求：提供有效 Topic 與訊息內容，驗證身份通過，Kafka 寫入正常 | 回傳 200 OK；messagelog 寫入一筆 SendStatus=1 |
| KFK-02 | Permission Test | 未帶 API Token 或 Token 無效 | 回傳 401 Unauthorized，messagelog 無記錄，Kafka 無訊息 |
| KFK-03 | Integration Test | Kafka Broker 斷線或寫入失敗 | 回傳失敗的 `KafkaResponse`；messagelog 寫入一筆 SendStatus=2 |
| KFK-04 | Flow Test | 提供空的 Topic string / 空的內容 | 需視 model validation 規則，可能回傳 400 Bad Request 或預設處理 |
| KFK-05 | DB Test | 驗證 messagelog 記錄的不可修改性 | 寫入一次後，嘗試手動 DELETE / UPDATE `MsgContent` 應被限制（於應用層禁止） |

---

## 9. 高風險區域

- **高風險 table**：`stock.messagelog` — 記錄所有通訊日誌，若未做好 `MsgContent` 遮蔽可能洩漏機敏資訊。
- **高風險 API**：`POST /api/v1/kafka/message` — 做為全局訊息中轉站，若因權限控管不當被濫寫，會影響所有訂閱該 Topic 的下游服務。
- **資料一致性風險**：Kafka 寫入與 messagelog INSERT 之間無 Transaction，`Kafka 寫入成功但 log 寫入失敗` 的情況未定義處理機制。這是典型的雙寫問題，會導致發送記錄丟失。
- **需人工確認**：Kafka Producer 是否有設定 retry / idempotence 機制以保證 at-least-once。
- **需人工確認**：帳號 `Account` 的來源是 Token 解析（安全），還是直接從 request body 取用（高風險）。

---

## 10. 常見錯誤

- **新人容易犯錯**：誤信 README 中「此服務無資料庫 Table」說法，實際在 Kafka 流程中會存取 `messagelog` 表。
- **AI 容易誤解**：將 MQService 視為純粹的 sidecar / proxy，忽略其內部也有「寫入業務日誌」的職責。
- **常見漏檢查項目**：未確認 `Account` 欄位是否由系統從驗證 Token 中安全提取，直接信任前端傳遞的帳號，導致跨帳號偽造發送記錄。
- **常見錯誤流程**：在 messagelog 寫入失敗時，未做任何重試或補償，導致外站已收到 Kafka 訊息但無發送記錄，喪失稽核軌跡。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `KafkaController.SendMessage` (含 `[RQ.Authorized]` 和 request model) |
| DB | `stock.messagelog` (schema) |
| DB Rules | `mqservice-detail.md` / `stock-detail.md` (messagelog 寫入限制) |
| Kafka | `README.md` (Kafka 192.168.55.85~87) |
| Code | `KafkaProducer`、`IMessagelogProvider` (Controller 依賴注入聲明) |