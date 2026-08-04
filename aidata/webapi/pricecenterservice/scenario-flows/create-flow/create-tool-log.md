# 寫入工具操作日誌

## 1. 場景目的

記錄後台管理工具（如 Blazor 內部工具介面）的任何變更性操作，將操作行為以非同步方式寫入日誌系統，供後續稽核、查詢與統計分析使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/log/game` | 寫入一筆工具操作日誌（需驗證） |

---

## 3. 流程總覽

1. 後台工具（Blazor 內部工具）發起操作（如更新賠率、刪除賽事）。
2. 前端呼叫 POST `/api/v1/log/game` 傳遞操作日誌內容。
3. Controller 接收 Request，透過 ECFramework.ECService 驗證呼叫者身份。
4. Service 層進行業務驗證（參數格式、必填欄位）。
5. Service 將日誌訊息序列化後，發布到 Kafka 的特定 Topic。
6. 獨立的 Kafka Consumer（如 LogConsumer）監聽該 Topic，將訊息寫入 Cassandra。
7. 回傳成功或失敗結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | LogController.PostGameLog | 接收 Request，驗證 token，呼叫 Service |
| 2 | Service | LogService.WriteGameLog | 驗證 Request 參數，包裝成 LogMessage |
| 3 | Service | LogService.WriteGameLog | 呼叫 LogProvider.PublishAsync 發布到 Kafka |
| 4 | Provider | LogProvider.PublishAsync | 序列化訊息，使用 Kafka Producer 發送 |
| 5 | (外部) | Kafka Broker | 接收並儲存訊息到指定 Partition |
| 6 | Consumer | CassandraLogConsumer | 監聽 Topic，批次寫入 Cassandra |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Kafka | Topic: `log.game` | Publish | 接收操作日誌訊息（非同步，解耦寫入與儲存） |
| Cassandra | `pricecenter.datum_logs` | Write（Consumer 執行） | 儲存日誌紀錄（最終一致性） |
| Cassandra | `pricecenter.games` | Write（Consumer 執行） | 與 `datum_logs` 關聯的賽事歷史資料（若日誌涉及賽事變更） |

---

## 6. 重要規則

- **權限限制**：所有 API 皆需驗證；需具有後台管理權限（如 Admin 角色或多站台管理員權限）。
- **不可回傳欄位**：對外 API 不可回傳任何敏感欄位（如 Kafka 內部 offset、Partition key、Consumer 內部狀態）。
- **Transaction 規則**：
  - Kafka 發布為「盡力而為」模式；Producer 使用 `acks=all` 確保至少寫入 Broker。
  - 若 Kafka 發布失敗，API 需回傳錯誤（HTTP 500），不進行重試或寫入備援。
- **Retry 規則**：
  - API 端不進行重試；失敗由呼叫端（Blazor 前端）決定是否重新提交。
  - 若 Kafka Producer 配置 `retries`，則由 Kafka 內部重試，但不可超過 `delivery.timeout.ms`。
- **Idempotency**：不保證冪等性；相同操作可能因重試而產生多筆相同日誌。呼叫端需自行控管重複提交風險。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未經驗證或 token 失效 | 回傳 HTTP 401 / 403 |
| 缺少必填參數（如 ActionType） | 回傳 HTTP 400，描述欄位缺失 |
| Kafka Broker 無法連線 | 回傳 HTTP 503（Service Unavailable），告知日誌服務暫時不可用 |
| 訊息序列化失敗（如型別不符） | 回傳 HTTP 400，描述參數格式錯誤 |
| Consumer 寫入 Cassandra 失敗 | Consumer 內部重試；最終無法寫入時記錄錯誤日誌，但不影響 API 回傳 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | API Test | 發送合法日誌內容（含所有必填欄位） | HTTP 200，需人工確認日誌已寫入 Cassandra |
| T02 | API Test | 發送缺少必填欄位的日誌 | HTTP 400 |
| T03 | Permission Test | 使用無後台權限的 token 呼叫 | HTTP 403 |
| T04 | API Test | Kafka 服務中斷（模擬連線失敗） | HTTP 503 |
| T05 | Flow Test | 連續發送 100 筆日誌（壓力測試） | 無遺失，Kafka 訊息無重複或錯序 |
| T06 | Integration Test | Consumer 寫入 Cassandra 後執行 GET `/api/v1/log/game/{date}` | 回傳的日誌列表包含剛才寫入的操作 |

---

## 9. 高風險區域

- **高風險 API**：`POST /api/v1/log/game` 若被濫用（發送大量無效日誌），可能打爆 Kafka 或填滿 Cassandra 儲存空間。
- **Kafka 可用性**：
  - Kafka 集群若完全中斷，所有日誌寫入將全部失敗（因不保證重試），導致審計斷層。
  - 需監控 Kafka Broker 健康狀態與 Producer 錯誤率。
- **Cassandra Consumer 失敗**：
  - 若 Consumer 停止運作，日誌將堆積在 Kafka 中；Kafka 保留時間過後將永久遺失。
  - 需監控 Consumer Lag，以及 Cassandra 寫入錯誤率。
- **Idempotency 缺失**：
  - 相同操作的日誌重複寫入將導致統計偏差（如操作次數被高估）；後續查詢需依賴時間戳或序號去重。

---

## 10. 常見錯誤

- ❌ **誤解日誌寫入為同步**：API 回傳 200 僅代表 Kafka 接收成功，日誌尚未寫入 Cassandra。直接查詢 Cassandra 可能遺漏最新日誌。
- ❌ **忽略 Kafka 失敗情境**：未實作 API 端的錯誤處理，導向前端收到成功回應但日誌實際上未記錄。
- ❌ **權限配置不當**：API 未正確驗證權限，使無權限使用者可寫入日誌，汙染審計資料。
- ❌ **訊息 Key 設計不當**：若 Kafka 訊息 Key 設計錯誤，可能導致相同 Partition 內訊息排隊，影響效能。
- ❌ **未處理日誌大小限制**：單筆日誌訊息過大（超過 `max.request.size`），導致 Kafka 拒絕寫入。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/log/game`（README） |
| 架構 | 日誌系統：Kafka + Cassandra（README 技術棧） |
| DB | `pricecenter.datum_logs`（README 資料庫重要 Table） |
| 權限 | 需要驗證（README API 列表） |
| 非同步設計 | API 回傳不應阻塞等待 Cassandra 寫入（系統職責描述：日誌為 Kafka + Cassandra） |