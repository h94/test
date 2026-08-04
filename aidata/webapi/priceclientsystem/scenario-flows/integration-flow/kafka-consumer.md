# Kafka 資料消費與處理

## 1. 場景目的

從 Apache Kafka 訂閱 `processedgamedata` 主題，消費上游服務產出的即時賽事資料，執行比分畸變修正、賠率映射與玩法過濾，並透過 SignalR Hub 推播給前端客戶端（InplayZ），同時存入 Redis 快取以供快速查詢。

---

## 2. 入口 API

此流程無對外 HTTP API；入口為 Kafka Consumer。  

| Method | Path | 說明 |
|---|---|---|
| Kafka Subscribe | Topic: `processedgamedata` | 持續消費 ProcessedGameData 訊息 |

---

## 3. 流程總覽

1. 服務啟動，註冊 Kafka Consumer（GroupId 依據環境變數，如 `PC_`、`UI_`），訂閱 `processedgamedata` 主題。  
2. Consumer 接收到訊息後，反序列化為 `ProcessedGameData` 物件。  
3. 根據 `ProcessedGameData.Source` 與 `GameType`，載入對應站台與球種的處理規則。  
4. 執行比分畸變修正（如單局/單節比分錯誤修正）。  
5. 過濾非必要玩法，僅保留「讓分」與「大小」兩種 PlayMode。  
6. 將外部平台 PlayMode 代碼映射為內部系統代碼（HA、OU、RBHA、RBOU）。  
7. 將處理後的資料壓縮寫入 Redis 快取（Key 含站台與賽事 ID，TTL 30 秒）。  
8. 透過 SignalR Hub 發布 `ReceiveGameData` 訊息給所有已連線且匹配的客戶端。  
9. 若訊息處理失敗，記錄錯誤日誌，Consumer offset 不提交，等待重試。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Consumer | `KafkaConsumerService.StartAsync` | 訂閱 `processedgamedata`，開始消費迴圈 |
| 2 | Consumer | `KafkaConsumerService.Consume` | 接收 `ConsumeResult`，反序列化 `ProcessedGameData` |
| 3 | Service | `GameDataProcessService.Process` | 依據 Source/GameType 選擇處理策略 |
| 4 | Service | `ScoreCorrectionService.Correct` | 執行比分畸變修正邏輯 |
| 5 | Service | `PlayModeFilterService.Filter` | 過濾非讓分/大小玩法 |
| 6 | Service | `PlayModeMappingService.Map` | 將外部代碼轉為內部代碼（HA/OU/RBHA/RBOU） |
| 7 | Provider | `RedisCacheProvider.SetAsync` | 寫入 Redis 快取，TTL 30 秒 |
| 8 | Hub | `GameDataHub.SendGameData` | 透過 SignalR 推播 `ReceiveGameData` 給連線客戶端 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Queue | Kafka `processedgamedata` | Consume | 接收上游即時賽事資料 |
| Cache | Redis DB 6 | Write | 快取處理後的賽事資料（30 秒 TTL） |
| Cache | Redis DB 6 | Read | 30 秒內重複請求直接回傳快取，減少重複處理 |

---

## 6. 重要規則

- **玩法過濾規則**：僅保留 PlayMode 為「讓分」與「大小」的賠率，其餘玩法一律丟棄。  
- **賠率映射規則**：外部代碼必須精確映射至 `HA`、`OU`、`RBHA`、`RBOU`，不可回傳未映射代碼。  
- **比分修正**：單局/單節比分異常時（如負數、超大值），依鄰近合法值或官方源修正。  
- **快取 TTL**：30 秒，超時後由下一次訊息驅動更新，不可人工延長。  
- **Consumer Group**：依部署環境區分（`PC_` 或 `UI_`），避免不同環境互相搶佔 partition。  
- **不可暴露的 Token**：`CompanyToken` 僅用於 Hub 連線驗證，不可透過 API 回傳。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| Kafka 訊息反序列化失敗 | 記錄錯誤日誌，跳過該訊息，提交 offset |
| 比分修正無法找到合法參考值 | 保留原始比分，記錄 Warning 日誌 |
| PlayMode 映射無對應內部代碼 | 忽略該筆玩法，不推播 |
| Redis 寫入失敗（超時或連線中斷） | 記錄 Error 日誌，仍繼續推播 SignalR 訊息 |
| SignalR Hub 推播失敗 | 記錄 Error 日誌，不影響後續訊息處理 |
| Kafka Consumer 連線中斷 | 依 `auto.offset.reset` 設定恢復，預設 `latest` |
| 同筆訊息重複消費（At-least-once） | 下游服務需具備冪等性（SignalR 推播本身冪等） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| FT-01 | Flow Test | 正常訊息消費與推播 | SignalR 客戶端收到正確格式的 GameData |
| FT-02 | Flow Test | 玩法過濾 | 僅讓分/大小玩法出現在推播資料中 |
| FT-03 | Flow Test | 比分畸變修正 | 異常比分被修正為合理值 |
| FT-04 | API Test | 快取命中 | 30 秒內重複請求回傳快取資料 |
| FT-05 | Permission Test | Token 驗證 | 錯誤 Token 的 Hub 連線被拒絕 |
| FT-06 | Flow Test | PlayMode 映射失敗 | 無法映射的玩法被忽略，不影響其他資料 |

---

## 9. 高風險區域

- **Kafka offset 提交**：若處理失敗仍提交 offset，會導致資料遺失。須確保僅在成功處理後提交。  
- **Redis 快取一致性**：賽事資料更新頻繁（毫秒級），快取 TTL 必須短於資料變更頻率。  
- **SignalR 訊息放大**：若客戶端數量龐大，Hub 推播會造成大量並行連線壓力。  
- **比分畸變修正邏輯**：錯誤的修正規則可能導致錯誤比分被推播，影響前端顯示。  
- **自動重啟機制**：每日 UTC 13:00 拋出 Exception 重啟服務，可能導致短暫服務中斷。建議由容器編排工具管理。

---

## 10. 常見錯誤

- ❌ 誤以為此服務直接讀寫 Cassandra：本場景不直接操作 DB，僅消費 Kafka 並推播。  
- ❌ 忘記過濾非必要玩法：若未正確過濾，前端可能收到不預期的 PlayMode。  
- ❌ Redis TTL 設定過長：導致賽事資料過時，前端顯示舊比分。  
- ❌ Consumer Group 設定錯誤：多環境使用相同 GroupId，導致 partition 被搶佔。  
- ❌ 未處理 PlayMode 映射失敗：應忽略而非拋出例外，避免中斷整個處理流程。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| Kafka Topic | README.md: `KafkaTopic` 預設 `processedgamedata` |
| GroupId | README.md: `KafkaGroupId` 依環境（`PC_`、`UI_`） |
| 比分修正 | README.md: 主要功能「比分與賠率修正」 |
| 玩法過濾 | README.md: 「過濾非必要玩法（僅保留讓分/大小）」 |
| 賠率映射 | README.md: 「多語系 / 賠率映射」支援將外部代碼轉換為 HA/OU/RBHA/RBOU |
| Redis 快取 | README.md: 「快取機制：30 秒內重複請求直接回傳壓縮後的快取資料」 |
| SignalR 推播 | README.md: 「透過 SignalR `/hub` 端點廣播給訂閱用戶」 |
| Token 驗證 | README.md: `CompanyToken` 定義每個客戶端公司的驗證 Token |
| 自動重啟 | README.md: 「每日 UTC 13:00 自動重啟服務」 |

> ⚠️ 程式碼層級證據（如 `KafkaConsumerService`、`ScoreCorrectionService` 實作）需人工從原始碼補充。