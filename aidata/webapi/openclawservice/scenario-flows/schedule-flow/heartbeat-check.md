# 背景心跳偵測

## 1. 場景目的

監控 OpenclawService 的活躍狀態。透過每分鐘定時偵測，若發現服務連續 70 分鐘未收到任何 API 請求，則觸發錯誤層級日誌，作為服務健康狀態的被動監控與告警機制。

---

## 2. 入口 API

此為背景排程任務，無對外 API 入口，由服務內部排程器觸發。

---

## 3. 流程總覽

1. 服務啟動時，初始化一個背景排程任務（每 60 秒執行一次）。
2. 排程觸發時，從 Redis 讀取最後一次 API 請求的時間戳。
3. 計算當前時間與最後請求時間的差值（分鐘）。
4. 若差值大於等於 70 分鐘，則透過 Logger 寫入一條 Error 層級日誌。
5. 若差值小於 70 分鐘，則不執行任何動作，等待下一次排程。
6. 任何 API 請求到達時，Controller 層會更新 Redis 中的最後請求時間戳。
7. 此流程不涉及任何 Cassandra DB 操作。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Scheduler | `HeartbeatScheduler.start()` | 啟動排程器，每 60 秒執行一次 `check_heartbeat` 任務（需人工確認類別與方法名稱）。 |
| 2 | Service/Provider | `HeartbeatService.check()` | 從 Redis 讀取 Key `service:heartbeat:last_request`（需人工確認確切 Key 名稱）。 |
| 3 | Service/Provider | `HeartbeatService.check()` | 計算 `current_time - last_request_time`，單位為分鐘。 |
| 4 | Service/Provider | `HeartbeatService.check()` | 判斷差值是否 >= 70。若為真，調用 Logger.error 寫入日誌。 |
| 5 | Controller | `Middleware / BaseController` | 每次 API 請求進入時，更新 Redis Key 為當前 timestamp。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | `service:heartbeat:last_request`（名稱需人工確認） | Read | 讀取最後一次 API 請求的時間戳，用於計算閒置時間。 |
| Redis | `service:heartbeat:last_request`（名稱需人工確認） | Write | 每次收到 API 請求時，更新為伺服器當前時間戳。 |
| Kafka | 生產環境 `49.213.1.158:29096` | Publish | 透過非同步日誌隊列發送 Error 日誌，用於監控告警。 |

---

## 6. 重要規則

- **時間計算精度**：需以分鐘為單位進行比較。浮點數或秒數差異應無條件捨去或直接比較絕對分鐘數。
- **閾值設定**：閒置閾值為 70 分鐘，此為硬編碼值（High Risk）。
- **Redis 連線失敗**：若讀取 Redis 失敗，需有 Fallback 機制（需人工確認是視為「無請求」而發送警報，或是跳過本次偵測）。
- **時區問題**：Redis 儲存的時間戳與伺服器當前時間必須使用相同的時區標準（建議 UTC）。
- **日誌級別**：僅在超過 70 分鐘時使用 Error，正常心跳不應輸出任何日誌，以免造成日誌洪水。
- **排程阻塞**：心跳檢查邏輯必須是非同步且輕量，不可阻塞 FastAPI 的 Event Loop。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 服務啟動後，Redis 中無此 Key（首次運行） | 應視為無歷史請求，可能觸發誤報。需確認是否應先初始化 Key 或容錯。 |
| Redis 連線中斷或 Timeout | 需人工確認：是否直接發送警報，或跳過本次偵測。 |
| Kafka 發送日誌失敗 | Logger 內部通常有本地緩衝，但若累積過多可能遺失日誌。需確認 Kafka 發送的重試與錯誤處理機制。 |
| 時鐘不同步（NTP 問題）導致時間倒退 | Redis 寫入的 Timestamp 可能比當前時間更新，導致計算出負數，永遠不觸發告警。 |
| 服務處於高負載，排程延遲執行 | 可能導致誤判服務長時間閒置。需確保排程器使用絕對時間而非相對執行次數。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| HB-01 | Integration Test | 服務啟動後 70 分鐘內無任何 API 請求 | 第 70 分鐘時觸發 Error 日誌，內容包含明確的告警訊息。 |
| HB-02 | Integration Test | 服務持續有 API 請求（每 10 秒一次） | 永不觸發 Error 日誌。 |
| HB-03 | Integration Test | 中斷 API 請求 69 分鐘後恢復 | 應不觸發告警，計時器被重置。 |
| HB-04 | Unit Test | Redis 連線失敗 | 根據已定義的 Fallback 機制，確認是否拋出異常或正常忽略。 |
| HB-05 | Flow Test | 驗證日誌發送至 Kafka 的正確性 | Kafka Consumer 應能收到對應的 Error 層級日誌訊息。 |

---

## 9. 高風險區域

- **閾值硬編碼**：70 分鐘的閾值直接寫在程式碼中，若需調整必須重新部署服務。
- **Redis 單點依賴**：心跳機制仰賴 Redis 記錄時間。若 Redis 因故清空資料（如重啟），會遺失最後請求時間，可能導致重啟後立即誤觸告警。
- **時間同步依賴**：高度依賴伺服器時鐘的正確性。NTP 服務異常可能導致心跳機制失效。
- **閒置判定失真**：若只有 Middleware 層計數，但健康檢查端點（如 Kubernetes Liveness Probe）也會觸發 Middleware，可能導致永遠不會觸發告警。需確認健康檢查路徑是否被排除在外。

---

## 10. 常見錯誤

- ❌ **誤將排程間隔當作閒置時間**：排程本身不重設計時器。計時器是由「API 請求」重置，而非排程任務。
- ❌ **健康檢查干擾**：未將 K8s Probes 或 Load Balancer 健康檢查請求排除在計數之外，導致服務永遠不會被判定為閒置。
- ❌ **日誌級別濫用**：正常心跳記錄使用 Info/Debug，只應在異常時印出 Error。避免產生大量無用日誌。
- ❌ **同步阻塞**：在非同步函式中使用 `time.sleep()` 或同步 I/O 操作，導致整個服務事件循環卡死。
- ❌ **時區不一致**：伺服器使用本地時間，但 Redis 儲存 UTC 時間，或反之，導致計算錯誤。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 需求描述 | README.md - 背景任務章節：「每分鐘心跳偵測，若連續 70 分鐘無請求則觸發錯誤日誌。」 |
| Redis 使用 | README.md - 技術棧：「Redis（db=3）... 用於服務狀態儲存。」 |
| Kafka 日誌 | README.md - 技術棧：「日誌：使用 TCZB 套件經 Kafka 傳送...」 |
| 非同步機制 | README.md - 技術棧：「非同步隊列（Queue）避免阻塞事件循環。」 |
| DB 邊界 | openclawservice-detail.md - Redis 章節：「無使用 Redis」→ 此與 README 衝突，需人工確認。openclawservice-detail.md 聲明此服務不操作 Redis，但 README 與心跳需求明確需要 Redis。**此為嚴重文件不一致，需立即人工確認。** |