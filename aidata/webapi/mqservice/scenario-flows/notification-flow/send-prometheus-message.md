# 發送 Prometheus 告警訊息

## 1. 場景目的

接收 Prometheus 系統發送的格式化告警訊息，經過身份驗證後，將告警內容轉送至特定渠道（如 Telegram 群組），並將發送記錄寫入 `stock.messagelog` 表。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/prometheus/message` | 接收 Prometheus 告警訊息 |

---

## 3. 流程總覽

1. 外部 Prometheus 系統經由 Webhook 呼叫 `/api/v1/prometheus/message`。
2. 系統驗證請求的 `authKey`。
3. 解析 Request Body，取得告警內容。
4. 調用對應的渠道服務（Telegram Bot）發送格式化後的告警訊息。
5. 取得發送結果。
6. 將發送記錄（日期、帳號、動作、目標、狀態、內容）寫入 `stock.messagelog` 表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `PrometheusController.SendMessage` | 接收 HTTP POST 請求。 |
| 2 | Validator | ECCore 內建驗證機制 | 驗證請求來源的 `authKey` 是否合法。 |
| 3 | Service | `PrometheusService` (推測) | 解析 Prometheus Alert Payload，格式化訊息文本。 |
| 4 | Provider | `TelegramProvider` (推測) | 調用 Telegram Bot API 將格式化訊息發送至指定 Chat ID 或群組。 |
| 5 | Service | `PrometheusService` (推測) | 取得 Telegram 發送的回傳結果。 |
| 6 | Repository | (直接操作 Stock MySQL) | 將發送記錄寫入 `stock.messagelog` 表。 |

> **需人工確認**：具體的 Service 與 Provider 命名與調用流程，需參考實際代碼。此流程基於服務職責推導。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `stock.messagelog` | Write（INSERT） | 記錄每一次告警發送的詳細日誌，初始狀態為 `SendStatus=0`。 |
| 外部 API | Telegram Bot | 發送 | 轉發格式化後的告警內容至特定群組。 |

> 根據 `README` 及 `mqservice-detail.md`，此服務本身不使用 Redis 或 Kafka 進行內部處理。

---

## 6. 重要規則

- **權限限制**：
  - 此端點需要驗證，驗證失敗將拒絕請求。根據 `README`，端點標記為需要驗證。
- **訊息日誌記錄原則**：
  - `messagelog` 為 append-only 表，記錄一經寫入，僅 `SendStatus` 可被後續（非此場景）更新為 1（成功）或 2（失敗），不可刪除。
  - `messagelog.AddTime`, `messagelog.LastUpdateTime` 由系統產生，應用層不可指定。
- **不可暴露資料**：
  - `messagelog.MsgContent` 可能包含原始告警資訊，對外查詢時需謹慎，且根據 `stock-detail.md`，此欄位不可回傳至前端。
  - `messagelog.TargetAddress` 對外查詢時應遮蔽。
- **無外部呼叫快取**：
  - 此流程無 Redis 或 Queue 參與，為同步處理流程。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 缺少 `authKey` 或 `authKey` 無效 | 返回 401 或 403 Unauthorized，請求中斷。 |
| Request Body 格式錯誤或為空 | 返回 400 Bad Request，請求中斷。 |
| 呼叫外部 Telegram Bot API 失敗（如網路不通、Token 失效） | 捕捉例外，寫入 `messagelog` 並將 `SendStatus` 設為 2（失敗）。 |
| 寫入 `stock.messagelog` 失敗 | 引發例外，需人工確認是否重試或僅記錄 Server Log。 |
| 內部處理時發生未預期例外 | 返回 500 Internal Server Error。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| IT-PROM-01 | Integration Test | 發送一個格式正確的 Prometheus Alert Body | HTTP 200，`stock.messagelog` 新增一筆 `SendStatus=1` 的記錄。 |
| IT-PROM-02 | Permission Test | 不帶 `authKey` 或帶錯的 `authKey` 發送請求 | HTTP 401 或 403，無任何日誌寫入。 |
| IT-PROM-03 | API Test | 發送格式錯誤的 JSON Body | HTTP 400，無任何日誌寫入。 |
| IT-PROM-04 | Flow Test | 模擬 Telegram API 回覆失敗 | 請求仍返回成功（或依設計返回錯誤），但 `messagelog` 中該筆記錄的 `SendStatus` 為 2（失敗）。 |

---

## 9. 高風險區域

- **外部依賴 Telegram API**：
  - 任何 Telegram Bot API 的異常（超時、停機、Token 過期）都會直接導致發送失敗。系統需有超時處理和重試機制。
    > **需人工確認**：目前是否有重試機制？
- **`messagelog` 寫入一致性**：
  - 若 Telegram 發送成功，但寫入 `messagelog` 失敗，會導致日誌缺失。需確認此事務邊界如何處理。
    > **需人工確認**：是否應先寫入初始日誌，發送後再更新狀態，以確保記錄不丟失？

---

## 10. 常見錯誤

- ❌ 忘記驗證 Prometheus 請求來源的 `authKey`，導致偽造告警。
- ❌ 在 `messagelog.MsgContent` 中明文儲存了完整的告警資訊，違反回傳限制。
- ❌ 未處理 Telegram API 呼叫的例外，導致整個請求崩潰，連日誌都未寫入。
- ❌ 誤將此 API 視為內部呼叫而不記錄日誌，導致無法追蹤告警發送歷史。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README.md: `POST /api/v1/prometheus/message` |
| 權限 | README.md: 路由表中標記 `需要驗證` |
| DB | `stock-detail.md`: `messagelog` append-only 特性、欄位限制 |
| 服務限制 | README.md: `資料庫：無（純訊息轉發，無持久化）` （此處指的應是服務本身無業務庫，但會操作業務庫 `stock`） |
| 相依服務 | README.md: 相依 Telegram Bot |