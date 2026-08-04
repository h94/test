# 設定賽事為最終結果

## 1. 場景目的
將特定賽事標記為最終結果（Final），寫入 Redis（DB5 即時資料）與 Cassandra（`pricecenter.games` 歷史資料），並通知 `predictservice` 觸發競猜結算。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/games/{gameType}/setfinal` | 將一筆或多筆賽事標記為 Final，需驗證 |

**Evidence**: README.md 賽事結算流程、OpenAPI paths

---

## 3. 流程總覽

1. 接收 `PUT /api/v1/games/{gameType}/setfinal` request，body 包含賽事識別資訊（`gid`、`gdate`、`lid`、`id` 等）
2. 透過 ECFramework.ECService 驗證呼叫方身份與權限（後台或內部服務）
3. 解析 request body，取得目標賽事清單
4. 查詢 Redis DB5 (`{gameType}:{lid}:{gDate}`) 確認賽事存在，並檢查目前狀態（是否已為 Final）
5. 更新 Redis DB5 內該賽事的狀態為 Final
6. 非同步寫入 Cassandra `pricecenter.games` 表，記錄結果（比分、狀態、時間）
7. 呼叫 `predictservice` API，通知該賽事已進入 Final 狀態，觸發競猜結算
8. 寫入操作日誌（`pricecenter.datum_logs` 或透過 Kafka）
9. 回傳 HTTP 200 OK

**Evidence**: README 常見使用場景第 3 點、技術棧提及 SignalR/Kafka、服務相依 predictservice

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GameController.SetFinal(gameType, request)` | 接收 PUT request，呼叫 Service |
| 2 | Service | `GameService.SetFinalAsync(gameType, request)` | 協調流程：驗證、更新 Redis、寫 Cassandra、呼叫 predictservice |
| 3 | Provider | `RedisGameProvider.UpdateGameStatus(key, status)` | 更新 Redis DB5 賽事狀態為 Final；需處理 CAS 或 Lock |
| 4 | Provider | `CassandraGameProvider.LogGameResult(game)` | 非同步寫入 Cassandra `games` 表 |
| 5 | Transfer/Client | `PredictServiceClient.NotifyFinal(gameInfo)` | 以 HTTP/gRPC 呼叫 predictservice，傳遞賽事結果 |
| 6 | Provider | `KafkaLogProvider.Publish(logEntry)`（若有） | 發佈操作日誌至 Kafka（供 Cassandra 日誌寫入） |

**Evidence**: README 技術棧（Redis DB5、Cassandra pricecenter）、服務相依（predictservice）

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis (DB5) | `{gameType}:{lid}:{gDate}` | Read, Update | 讀取賽事目前資料，更新狀態為 Final |
| Cassandra | `pricecenter.games` | Write | 寫入賽事最終結果歷史記錄 |
| Cassandra | `pricecenter.datum_logs` | Write | 記錄資料來源異動日誌（若流程包含） |
| Kafka | 操作日誌 topic | Publish | 發佈日誌訊息，供取用者寫入 Cassandra |
| External API | `predictservice` | HTTP/gRPC Call | 通知觸發競猜結算 |

**Evidence**: README 資料庫重要 Table、README 服務相依、技術棧（Kafka + Cassandra）

---

## 6. 重要規則

- **權限限制**：需通過 ECFramework.ECService 驗證，僅允許後台管理員或內部服務呼叫；不可對外暴露。
- **狀態檢查**：寫入 Final 前，需檢查賽事是否已為 Final，避免重複結算。
- **Transaction 規則**：Redis 更新與 Cassandra 寫入不強制 strong consistency，但應確保最終一致性（Cassandra write 可 retry）。
- **冪等性**：同一賽事重複設定 Final 應回傳成功（或明確拒絕），不可重複觸發 predictservice 結算。
- **不可修改欄位**：標記 Final 後，賽事比分、狀態等核心欄位不應再被一般分數更新 API 修改（需 Service 內部防呆）。
- **資料一致性**：Redis DB5 更新成功但 predictservice 呼叫失敗時，需有 retry 或補償機制（如排程重新通知）。
- **TTL 規則**：Redis DB5 賽事資料可能設有 TTL，Final 後不應因 TTL 過期而遺失（預期 Cassandra 為主要歷史儲存）。

**Evidence**: pricecenter-detail.md 操作邊界限制、README 賽事結算流程

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| request body 無法解析（格式錯誤、缺少必要欄位） | HTTP 400 Bad Request |
| 賽事不存在（Redis 查無資料） | 需人工確認：是否回傳 404 或記錄錯誤後忽略 |
| 賽事已為 Final 狀態（重複呼叫） | 不回傳錯誤，或回傳 409 Conflict，不可重複通知 predictservice |
| Redis 寫入失敗（連線中斷、key 鎖定） | HTTP 500 Internal Server Error，不可繼續通知 predictservice；可 retry |
| Cassandra 寫入失敗 | 記錄錯誤日誌，不影響 API 回傳（非同步處理）；需有補償機制 |
| predictservice 呼叫失敗（timeout、500） | 記錄錯誤，API 可視情況回傳 200（Cassandra 已寫）或 502；需 retry queue 或排程補償 |
| 權限不足（未通過驗證） | HTTP 401 Unauthorized 或 403 Forbidden |
| 賽事為 Final 後，又收到 score-status 更新請求 | Service 應拒絕更新（回傳 409），保護 Final 結果 |

**Evidence**: README 驗證框架 ECFramework.ECService、賽事狀態流程推導、db-usage 無直接規定但符合防呆原則

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC-SF-01 | API Test | 正常設定 Final（含完整 body） | 200 OK，Redis 狀態更新，predictservice 被呼叫 |
| TC-SF-02 | Permission Test | 未帶驗證 token 呼叫 | 401 Unauthorized |
| TC-SF-03 | Permission Test | 使用無權限 token 呼叫 | 403 Forbidden |
| TC-SF-04 | Flow Test | 設定 Final 後，查詢賽事（GET /games/{gameType}/final） | 應回傳該賽事 |
| TC-SF-05 | Flow Test | 設定 Final 後，用 score-status 更新比分 | 應回傳 409 或拒絕更新 |
| TC-SF-06 | Idempotency Test | 重複設定同一賽事 Final | 不回傳錯誤（200），predictservice 僅被呼叫一次或忽略 |
| TC-SF-07 | Error Test | 模擬 predictservice timeout | API 回傳 200（Cassandra 已寫）或 502，後續需有補償 |
| TC-SF-08 | Error Test | 模擬 Redis 寫入失敗 | API 回傳 500，不可呼叫 predictservice |
| TC-SF-09 | Data Test | 確認 Cassandra `games` 寫入內容 | 包含 final 狀態、比分、時間戳 |

**Evidence**: OpenAPI（setfinal）、README 驗證/賽事查詢 API、場景描述

---

## 9. 高風險區域

- **高風險 API**：`PUT /api/v1/games/{gameType}/setfinal` — 直接影響競猜結算與金流
- **跨服務資料同步**：predictservice 通知成敗非同步；若失敗，結算遺漏導致財務錯誤
- **Cache consistency**：Redis DB5 更新成功即視為 Final，但 Cassandra 寫入延遲；需確保 predictservice 以 Redis 或可靠訊息為準
- **Transaction**：Redis（快取）與 Cassandra（持久化）雙寫無 ACID 交易；需考量補償機制
- **Idempotency**：重複標記 Final 不可重複結算
- **Queue retry**：若 predictservice 呼叫失敗，需有 retry 機制（Kafka / 排程）

**Evidence**: README 服務相依（predictservice），db-usage 無明確定義交易規則（推導）

---

## 10. 常見錯誤

- ❌ 未檢查賽事是否已為 Final，重複呼叫 predictservice 結算 → ✅ 應先檢查狀態
- ❌ predictservice 呼叫失敗後直接回傳 500，但 Redis 已更新 → ✅ 需設計最終一致性補償，或先更新 Redis 再通知
- ❌ Final 後仍允許比分更新 → ✅ Service 層需攔截 Final 賽事的異動
- ❌ 忽略 request body 驗證（gid/gdate 格式錯誤） → ✅ Controller 層應有強型別 Binding + Validation
- ❌ 直接將 Cassandra 寫入設計為同步阻斷 API 回傳 → ✅ 應非同步寫入，避免 Cassandra 延遲影響 API 回應時間

**Evidence**: pricecenterservice-detail.md 寫入限制（enabled/closetime 類似狀態防護概念）、README 賽事狀態操作

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 入口 API | `PUT /api/v1/games/{gameType}/setfinal` (README, OpenAPI) |
| 驗證機制 | ECFramework.ECService (README 技術棧) |
| Redis (DB5) | `{gameType}:{lid}:{gDate}` (README 資料庫重要 Table) |
| Cassandra | `pricecenter.games`, `pricecenter.datum_logs` (README 資料庫重要 Table) |
| 服務依賴 | `predictservice` (README 服務相依) |
| 日誌 | Kafka + Cassandra (README 技術棧) |
| 流程 | README 常見使用場景 3. 賽事結算流程 |