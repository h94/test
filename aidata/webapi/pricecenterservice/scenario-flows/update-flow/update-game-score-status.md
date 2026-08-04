# 更新賽事比分與狀態

## 1. 場景目的

由比分機器人或管理員手動觸發，即時更新特定賽事的比分、比賽狀態及相關資訊。系統將變更寫入 Redis（即時資料）與 Cassandra（歷史紀錄），並透過 SignalR 推播即時變動給前端連線客戶端，以維持競猜首頁與直播頁的資料即時性。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/games/{gameType}/score-status` | 更新指定賽事比分與狀態（主要入口） |
| PUT | `/api/v1/games/{gameType}/{lid}/{gDate}/{id}/time-score-status` | 更新賽事時間、比分、狀態 |

上述 API 皆須通過 ECFramework.ECService 驗證（`✅`）。

---

## 3. 流程總覽

1. 接收 PUT 請求，驗證身分與權限。
2. 驗證輸入的必填欄位（`gameType`, score-status request body 等）。
3. 根據 `gameType`、`lid`、`gDate` 計算 Redis DB5 的 Key：`{gameType}:{lid}:{gDate}`。
4. 更新 Redis 中該場賽事的比分、狀態欄位（部分更新，非直接覆蓋整筆物件）。
5. 異步寫入 Cassandra `pricecenter.games` 表，記錄比分、狀態變更歷史（包含時間戳）。
6. 透過 SignalR Hub 推播訊息給訂閱該賽事的連線群組（群組名稱可能為 `{gameType}_{lid}_{gDate}` 或 `{gid}`）。
7. 回傳 HTTP 200 或適當的執行結果。

---

## 4. 程式流程

（因未提供實際 source code，以下為基於 .NET 慣例與 README 推測，標記 `需人工確認`）

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `GamesController.PutScoreStatus(gameType, [FromBody] model)` | 取得 gameType 與 request body，呼叫 Service |
| 2 | Validator | 需人工確認 | 驗證 model（score、status 格式、gameType 可接受值） |
| 3 | Service | `GameService.UpdateScoreStatusAsync(gameType, model)` | 組合 Redis key，進行 Redis 局部更新 (Hash Set 或 JSON patch) |
| 4 | Provider/Repo | `RedisProvider.UpdateGameFieldsAsync(key, fieldValues)` | 對 DB5 的 `{gameType}:{lid}:{gDate}` 下 Hash 指令 `HSET` 或 Lua Script 進行原子更新 |
| 5 | Service | `GameService.LogGameStatusChangeAsync(...)` | 呼叫 Cassandra 寫入非同步任務 |
| 6 | Provider/Repo | `CassandraGameRepo.InsertAsync(gameRecord)` | 寫入 `pricecenter.games` 表（INSERT 或 UPDATE 比分、狀態、最後更新時間） |
| 7 | Service | `GameService.NotifyScoreUpdate(gameType, lid, gDate, gid, scoreData)` | 蒐集需要推播的資料，呼叫 SignalR Hub |
| 8 | Hub | `GameHub.SendAsync("ScoreUpdated", groupName, payload)` | 推播給對應的 SignalR group，前端收到後更新畫面 |

**備註**：若 API 為 `time-score-status`，則額外更新賽事開始時間等欄位，流程類似。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Cache | Redis DB5 | Write (`HSET` 或 `JSON.SET`) | 更新即時賽事資料（比分、狀態），不影響賠率等其他欄位 |
| DB | Cassandra `pricecenter.games` | Write (INSERT/UPDATE) | 寫入比分變更歷史紀錄，供後續查詢或結算使用 |
| DB | Cassandra `pricecenter.datum_logs` | Write (INSERT) | 記錄資料來源日誌（若比分更新由特定來源觸發） |
| Queue/SignalR | SignalR Hub | Publish | 推播即時比分變動給已連線的前端客戶端 |

**注意**：此場景不涉及 Kafka 寫入，但服務日誌可能透過 Kafka 傳送（由基礎架構層處理，非業務邏輯直接操作）。

---

## 6. 重要規則

- **權限限制**：必須通過 ECFramework 驗證，通常只有比分機器人帳號或後台管理員才有此 API 的寫入權限。
- **Redis 操作**：
  - 不可直接覆蓋整個 `{gameType}:{lid}:{gDate}` Key，以免遺失其他賽事資料（如賠率）。
  - 應使用 Hash 的 `HSET` 僅更新指定欄位，或使用 Lua Script 確保原子性。
  - 若使用 JSON 儲存，需要進行部分 patch。
- **Cassandra 寫入**：
  - `game` 表分區鍵為 `gid` 或 `(lid, gDate, id)`，需使用合適的 partition key 避免熱點（需人工確認具體 schema）。
  - 寫入時應更新 `LastUpdateTime` 或 `UpdatedAt` 欄位（證據：同 `datum_logs` 慣例）。
- **SignalR 推播**：
  - 必須正確建立 group，通常依 `gameType`、`lid`、`gDate` 或 `gid` 分組，避免過度推播所有連線。
  - 訊息格式需與前端約定（可能為 JSON：`{ gid, score, status, ... }`）。
- **不可暴露資料**：
  - 此 API 為內部寫入，回傳結果中不應包含敏感欄位（如 `password`）。
- **TTL 規則**：
  - Redis DB5 的賽事資料可能設有 TTL（如 7 天），但需人工確認。更新時不應變更 TTL，除非有明確需求。
- **Transaction 規則**：
  - Redis 與 Cassandra 為兩段式提交？系統無分散式交易，通常先寫 Redis，再非同步寫 Cassandra。若 Cassandra 寫入失敗，需有重試機制，但不應影響 Redis 的正確性（最終一致性）。
- **冪等性**：
  - 比分更新 API 可能會被重複呼叫（網路重試），需確保相同資料的多次寫入不導致錯誤（例如使用 `UPSERT` 語義）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 請求缺少必要參數（gameType 空白、model 為 null） | 回傳 400 Bad Request，附帶驗證錯誤訊息 |
| 未經驗證或權限不足 | 回傳 401/403，拒絕請求 |
| Redis 寫入失敗（連線逾時或 DB5 不可用） | 回傳 5xx 錯誤，記錄 Log，不進行後續 Cassandra 寫入與推播 |
| Cassandra 寫入失敗 | 非同步任務失敗，記錄錯誤 Log，但 HTTP 仍回傳成功（Redis 已寫入）。需人工確認設計是否需要同步寫入確保一致性。 |
| SignalR 發送失敗（Hub 未連線或群組無訂閱者） | 不影響 API 回應，僅記錄 Warning Log |
| 比分格式不合法（例如分數為字串而非數字） | 回傳 400 Bad Request，提供明確格式說明 |
| 更新不存在的賽事（Redis key 不存在） | 視策略：可能回傳 404 或自動建立賽事（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| S1 | API Test | 正常更新比分與狀態 | HTTP 200，Redis 與 Cassandra 資料正確，SignalR 推播被觸發 |
| S2 | API Test | 缺少必填欄位 | HTTP 400 |
| S3 | Permission Test | 無 token 或 token 無效 | HTTP 401 |
| S4 | Flow Test | Redis 寫入失敗 | HTTP 5xx，不呼叫 Cassandra |
| S5 | Flow Test | Cassandra 寫入失敗（模擬） | HTTP 仍回傳成功，後台有錯誤日誌 |
| S6 | Integration Test | 連續兩次相同比分更新 | 資料維持正確，無重複推播或錯誤（冪等性） |
| S7 | Feature Test | SignalR 客戶端驗證推播訊息格式與內容 | 收到符合合約的 JSON，欄位正確 |

---

## 9. 高風險區域

- **Redis 與 Cassandra 一致性**：非原子操作，需明確定義資料最終以哪個為準。若 Redis 成功但 Cassandra 失敗，賽事歷史可能遺漏；可考慮使用 Outbox 模式或補償 job。
- **高寫入量賽事**：熱門賽事短時間內大量比分更新（如籃球、排球），可能對 Redis 和 Cassandra 產生壓力。需確保連接池足夠、避免 Redis lock contention。
- **SignalR 推播放大**：多台 server 實例需透過背板 (如 Redis Pub/Sub) 同步推播，否則客戶只連到其中一台可能收不到消息。
- **Cache stampede**：若更新同時大量讀取，Redis 可能短暫回應舊資料，視業務容忍度。

---

## 10. 常見錯誤

- ❌ **Redis 直接 `SET` 整筆 Key**，導致其他賽事欄位（賠率、盤口）遺失。
- ❌ **忘記驗證**：API 過濾不確實，讓一般用戶呼叫寫入比分。
- ❌ **未處理比賽狀態流轉**：例如已結束（Final）的賽事仍接受比分更新，可能導致結算問題。應檢查狀態機，禁止從 `Final` 返回 `InPlay`。
- ❌ **SignalR 推播群組名稱設計不當**：導致所有客戶端收到非必要推播，造成前端效能瓶頸。
- ❌ **Cassandra insert 使用 `INSERT` 而非 `UPDATE`**：若主鍵已存在會拋錯，應一律使用 `INSERT ... IF NOT EXISTS` 或 `UPDATE` 語法（視業務邏輯）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README: PUT `/api/v1/games/{gameType}/score-status` 更新賽事比分與狀態 |
| DB | README: Redis DB5 賽事即時資料，Key 格式 `{gameType}:{lid}:{gDate}` |
| DB | README: Cassandra pricecenter.games 賽事歷史資料 |
| SignalR | README: 技術棧包含 SignalR 即時推播，常見場景 2 描述「更新 Redis + Cassandra → SignalR 推播前台」 |
| Auth | README: API 需要驗證 ✅ |
| Service Detail | pricecenterservice 為 owner 角色，可對 pricecenter keyspace 進行讀寫 |
| Flow | README: 後台更新賽事比分場景觸發 → PUT `/api/v1/games/{gameType}/score-status` → 更新 Redis + Cassandra → SignalR 推播前排 |