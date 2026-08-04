# Kafka 賽事數據消費與處理推送

## 1. 場景目的
描述 InplayzSubscriptionSystem 從 Kafka 消費即時賽事消息，依據系統狀態與連線狀況決定是否處理，將消息解析、比對並轉換為前端適用的 SiteGameDto，再按賽事狀態（PreGame、InProgress、Final）分流，最終透過 SignalR Hub 推送給已驗證的商務端連線用戶。

---

## 2. 入口點
本場景無 REST API，觸發點為 **Kafka Consumer**（需人工確認具體 topic 名稱）。

---

## 3. 流程總覽
1. Kafka Consumer 訂閱指定 topic（需人工確認）並接收消息。
2. 檢查當前系統模式與連線狀態：
   - 若 **無客戶端連線** 且 **非測試模式**，僅記錄來源站點（`site`）後結束，不進行處理。
   - 如有連線或處於測試模式，繼續後續步驟。
3. 解析 Kafka 消息為內部賽事資料模型。
4. 比對現有賽事快取（若存在），識別是否為新賽事或更新。
5. 轉換為 SiteGameDto，併根據賽事狀態分流（PreGame / InProgress / Final）。
6. 從快取或 DB 讀取已授權的商務端訂閱資訊與連線識別。
7. 透過 SignalR Hub 將資料推送至相應的客戶端群組（需已驗證連線）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Consumer | `KafkaConsumerService`（推測） | 從 Kafka 消費消息，送出給處理程序 |
| 2 | Service | `MatchProcessService`（推測） | 判斷有無連線/測試模式，決定繼續或直接記錄 |
| 3 | Service | `MatchParser`（推測） | 解析原始消息為標準賽事物件 |
| 4 | Service | `MatchCacheService`（推測） | 比對現有快取，決定新增或更新 |
| 5 | Service | `SiteGameDtoFactory`（推測） | 轉換為 SiteGameDto 並標記狀態 |
| 6 | Provider | `BusinessDataProvider`（已知） | 讀取商務訂閱與授權資訊 |
| 7 | Hub | `MatchHub`（推測） | 推送賽事數據至相關客戶端 |

> ※ 實際類別名稱以程式碼為準，此處為合理推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Queue | Kafka | Consume | 接收即時賽事消息（topic、GroupId 需人工確認） |
| Cache | Redis（推測） | Read | 讀取商務訂閱快取、賽事比對快取（需人工確認 key 結構） |
| Cache | Redis（推測） | Write / Delete | 定期刷新訂閱資訊、更新比賽狀態快取 |
| DB | Cassandra / MySQL（推測） | Read | 讀取商務端授權 Token、訂閱有效性（BusinessDataProvider） |
| DB | product tables（若用於兌換記錄） | Read / Write | 本場景可能不直接涉及，但系統為 product owner，可讀寫兌換記錄（若需要） |

> 因無快取細節，具體 Redis key 與 TTL 需人工確認。

---

## 6. 重要規則

- **連線狀態判斷**：若無任何客戶端連線（`ConnectedClientCount == 0`）且非測試模式，僅記錄來源站點後返回；不進行解析、轉換與推送。  
  *Evidence*：README「若無客戶端連線且非測試模式，則僅記錄來源站點而不處理消息。」
- **測試模式**：Kafka GroupId 會附加機器名稱，避免多實例消費衝突。  
  *Evidence*：README「支援按 `TestMode` 設定切換 Kafka GroupId 附加機器名稱以避免衝突。」
- **賽事狀態分流**：訊息需帶有狀態標記（PreGame / InProgress / Final），不同狀態可能走不同推送邏輯或頻率。  
  *Evidence*：README「並依據賽事狀態（PreGame、InProgress、Final）分流處理。」
- **客戶端驗證**：連線至 SignalR Hub 時須驗證商務代碼與授權 Token；推送前應確保該商務端仍有權限（訂閱未過期）。  
  *Evidence*：README「商務驗證與快取：驗證商務代碼與授權 Token」。
- **IP 速率限制**：同一 IP 在 3 分鐘內最多建立 20 次連線。此規則影響連線建立，但不直接作用於 Kafka 流程，惟推送時客戶端可能已因觸發限制而被斷開。  
  *Evidence*：README「IP 速率限制（每 IP 3 分鐘內最多 20 次連線）」。
- **不可暴露資料**：推送的 SiteGameDto 不應包含內部敏感欄位（如商務端內部 token），僅輸出前端所需欄位。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| Kafka 消息格式錯誤 | 記錄錯誤並跳過該消息，不影響後續消費 |
| 消息遺失賽事狀態欄位 | 無法分流，視為無效消息，記錄並跳過 |
| 解析成功但無對應的商務訂閱 | 不推送，或推送至空群組 |
| Redis/DB 暫時不可用 | 可能無法獲取最新訂閱資訊，記錄錯誤並嘗試重試或使用過期快取 |
| SignalR Hub 推送失敗（客戶端已斷線） | 忽略該客戶端，記錄發送失敗（如有的話） |
| 測試模式下群組 ID 衝突 | 應已被附加機器名稱機制避免 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T01 | Integration | 發送一份正常 PreGame 消息，並有已認證客戶端連線 | 消息被解析、推送至該客戶端，且狀態為 PreGame |
| T02 | Integration | 無客戶端連線 + 非測試模式 | 僅記錄站點，不處理消息 |
| T03 | Integration | 無客戶端連線但為測試模式 | 消息仍被處理（模擬有連線情境） |
| T04 | API / Hub | 推送 InProgress 更新至連線客戶端 | 客戶端收到更新 |
| T05 | Flow | Kafka 消息包含無效 JSON | 系統記錄 parse error，不 push |
| T06 | Flow | 商務訂閱過期 | 即使有連線，也不推送賽事資料 |

---

## 9. 高風險區域

- **高風險 API**：Kafka Consumer 的 offset 提交與消息處理失敗重試機制可能導致重複推送。
- **快取一致性**：商務訂閱快取若未及時更新，可能造成錯誤推送或遺漏推送。
- **跨服務同步**：賽事消息來源與內部模型的映射規則需與上游資料一致，否則前端顯示錯誤。
- **Queue Retry**：Kafka 訊息消費失敗時，重試可能導致順序錯亂或重複處理，需確保處理冪等。

---

## 10. 常見錯誤

- ❌ 忽略無連線判斷，直接處理所有 Kafka 消息，造成資源浪費。
- ❌ 測試模式未正確設定 GroupId，導致多個實例重複消費同一消息。
- ❌ 賽事狀態分流邏輯錯誤（例如將 Final 消息當作 InProgress 處理），前端顯示不正確。
- ❌ 未檢查商務訂閱有效性，對已過期商務端推送賽事數據。
- ❌ 對 SiteGameDto 暴露過多內部資料（如原始消息中的特定欄位）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| 無連線內處理 | README「若無客戶端連線且非測試模式，則僅記錄來源站點而不處理消息」 |
| 測試模式 | README「支援按 TestMode 設定切換 Kafka GroupId 附加機器名稱」 |
| 賽事狀態分流 | README「依據賽事狀態（PreGame、InProgress、Final）分流處理」 |
| 商務驗證 | README「商務驗證與快取：驗證商務代碼與授權 Token」 |
| IP 限制 | README「IP 速率限制（每 IP 3 分鐘內最多 20 次連線）」 |
| Kafka Topic / GroupId 設定 | **需人工確認**：appsettings.json 中 HubSettings 區段 |