# 即時比分推送

## 1. 場景目的

從 Apache Kafka 消費 `processedgamedata` 主題中的賽事更新資料，經過比分修正與玩法過濾後，透過 SignalR Hub 即時推送給已完成訂閱的客戶端，為前端 (InplayZ) 提供低延遲的即時比分與賠率服務。

---

## 2. 入口 API

本場景以 Kafka Consumer 後臺服務為主要入口，無 REST API 觸發。相關管理 API 僅供查詢連線狀態。

| Method | Path | 說明 |
|---|---|---|
| GET | `/hub` | SignalR Hub 端點，用於建立 WebSocket 連線與協商 |
| GET | `/api/v1/system/hubinfo` | 查詢當前 SignalR Hub 連線資訊（管理用途） |

---

## 3. 流程總覽

1.  服務啟動時，`KafkaConsumer` 作為一個 Background Service 開始訂閱 `processedgamedata` 主題。
2.  從 Kafka 收到一筆 `ProcessedGameData` 訊息。
3.  將原始訊息體經由 GZip 壓縮，並以 `{MatchId}_{Timestamp}` 為快取鍵存入 Redis，TTL 設為 30 秒。
4.  檢查 Redis 是否存在此快取鍵，作為重複資料篩選機制。
5.  **若快取命中**：直接從 Redis 取出上次壓縮後的完整推送資料，並跳至步驟 9。
6.  **若快取未命中**：進入完整處理流程。
    *   根據配置的修正規則，修正可能出現單局或單節分數錯誤的比分。
    *   過濾非必要玩法（保留指定玩法，如全場讓分/大小）。
    *   將外部平臺代碼 (PlayMode) 轉換為內部系統代碼 (HA, OU)。
    *   加總計算全場分數。
7.  將處理後的資料進行 GZip 壓縮。
8.  將壓縮後的推送資料以 `{MatchId}_{Timestamp}` 為鍵寫入 Redis，TTL 設為 30 秒。
9.  透過 SignalR Hub 的 `SendDataToClient` 方法，將資料廣播給所有已連線且訂閱該球種的客戶端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Background Service | `KafkaConsumer.StartAsync` | 初始化並啟動 Kafka Consumer，開始輪詢訊息 |
| 2 | Provider | `KafkaConsumer.ProcessMessageAsync` | 收到訊息後進行 GZip 壓縮並檢查 Redis 快取 |
| 3.1 | Provider | `KafkaConsumer.ProcessMessageAsync` | **(快取命中)** 從 Redis 讀取上次推送的位元組資料，直接推送 |
| 3.2.1 | Provider | `KafkaConsumer.HandleMessageAsync` | **(快取未命中)** 開始處理原始資料：比分修正 |
| 3.2.2 | Provider | `KafkaConsumer.HandleMessageAsync` | 過濾非必要玩法 (PlayMode) |
| 3.2.3 | Provider | `KafkaConsumer.HandleMessageAsync` | 轉換 PlayMode 代碼並加總比分 |
| 3.2.4 | Provider | `KafkaConsumer.HandleMessageAsync` | GZip 壓縮處理後的資料，寫入 Redis 快取 |
| 4 | Hub | `PriceHub.SendDataToClient` | 接收處理後的位元組陣列，廣播給符合 GameType 的連線 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Cache | Redis `{MatchId}_{Timestamp}` | Read, Write | 儲存 30 秒內的 GZip 壓縮推送資料，實現重複訊息去重與快速響應 |
| Queue | Kafka `processedgamedata` | Consume | 訂閱上游服務發佈的原始賽事更新訊息 |

---

## 6. 重要規則

*   **權限限制**：SignalR 連線時需驗證 `CompanyToken`，此流程不負責驗證，而是在 `OnConnectedAsync` 階段完成。
*   **訊息大小限制**：SignalR 最大接收訊息大小設定為 `3276800` 位元組 (約 3.1 MB)。
*   **TTL 規則**：Redis 快取 `{MatchId}_{Timestamp}` 的 TTL 為 **30 秒**。
*   **玩法過濾規則**：僅保留特定核心玩法（如全場讓分、全場大小），過濾掉非必要玩法。
*   **比分修正規則**：根據預先配置的規則，自動修正特定聯賽可能出現的單局/單節比分錯誤。
*   **不可修改欄位**：`CompanyToken` 應從 `appsettings.json` 的 `AppSettings:HubSettings:CompanyToken` 讀取，不可在程式碼中硬編碼或由客戶端傳入。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 消費到的訊息格式錯誤或無法反序列化 | 記錄錯誤日誌，跳過該筆訊息並繼續消費下一筆。 |
| Redis 快取服務無法連線或寫入失敗 | 記錄錯誤，但流程應繼續進行，直接推送即時資料，不因快取異常而中斷服務。 |
| Kafka 消費者與 Broker 連線中斷 | 服務會嘗試重連，依賴 Kafka Client 的自動重連機制，直到連線恢復。 |
| SignalR 推送時部分用戶端已斷線 | SignalR 框架會自動處理，移除無效連線，不影響向其他連線的廣播。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| FT-01 | Flow Test | 消費一筆新賽事資料 | 完整執行比分修正、玩法過濾、寫入快取、透過 SignalR 成功推播。 |
| FT-02 | Flow Test | 30 秒內重複消費完全相同的一筆資料 | 第二次消費時命中 Redis 快取，直接推送上次壓縮後的資料，不再重複處理。 |
| FT-03 | API Test | 使用有效的 `CompanyToken` 建立 SignalR 連線並訂閱球種 | 連線成功，且能收到對應球種的廣播。 |
| FT-04 | API Test | 模擬 Redis 服務崩潰 | 服務應能持續從 Kafka 消費與處理，並透過 SignalR 推送，不應崩潰。 |
| ET-01 | Integration Test | 推送的比分資料與來源平臺原始資料不一致 | 觸發比分修正規則，推送修正後的比分。 |

---

## 9. 高風險區域

*   **Cache Consistency**：修改快取策略或資料結構時，需確保 `ProcessMessageAsync` 中的「存 Redis」與「讀 Redis」的鍵生成規則嚴格一致，否則會導致快取永久性穿透。
*   **Queue Retry**：`KafkaConsumer` 的異常處理需注意，若在 `try-catch` 區塊外拋出未處理的例外，可能導致 Consumer 進程崩潰。
*   **資源管理**：頻繁的 GZip 壓縮與 Redis 寫入操作可能造成 CPU 與網路的高負載，需監控服務資源。

---

## 10. 常見錯誤

*   ❌ **新人誤解**：`processedgamedata` 的資料已經是處理過的，不需再次修正。**事實**：`priceclientsystem` 內部仍需對特定聯賽執行比分修正與玩法過濾。
*   ❌ **AI 誤解**：SignalR 的廣播是針對所有連線。**事實**：廣播是針對訂閱了特定 `GameType` 的連線群組。
*   ❌ **常見漏檢查**：程式碼中 Redis 的 TTL 是否正確設定為 30 秒；快取鍵 `{MatchId}_{Timestamp}` 的組合邏輯，時間戳精確度是否足以區分同一秒內的多筆訊息。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 系統職責 | `README.md`：即時比分推送、比分與賠率修正、快取機制 |
| Kafka 主題 | `README.md`：`KafkaTopic` 預設 `processedgamedata` |
| Redis 快取 | `README.md`：30 秒內重複請求直接回傳壓縮後的快取資料 |
| SignalR Hub | `README.md`：SignalR `/hub` 端點 |
| 管理 API | `OpenAPI`：`/api/v1/system/hubinfo` |
| 驗證方式 | `README.md`：`CompanyToken` 定義每個客戶端公司的驗證 Token |
| 服務技術棧 | `README.md`：C# (.NET 6), SignalR Core, Kafka, Redis |