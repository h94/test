# 即時賽事推播

## 1. 場景目的
當賽事資料（比分、狀態、賠率等）因外部資料源或後台管理員操作而更新時，系統透過 SignalR 將變動即時推送給所有已連線的前端客戶端，以確保前端顯示的賽事資訊為最新狀態。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/v1/games/{gameType}/score-status` | 更新賽事比分與狀態（批量） |
| PUT | `/api/v1/games/{gameType}/{lid}/{gDate}/{id}/time-score-status` | 更新單場賽事的時間/比分/狀態 |
| PUT | `/api/v1/games/{gameType}/{lid}/{gDate}/{id}/resultinfos` | 更新賽事結果資訊 |
| PUT | `/api/v1/games/{gameType}/setfinal` | 設定賽事為最終結果 |

---

## 3. 流程總覽

1. 接收後端服務（如比分機器人）或管理員的賽事更新請求。
2. 驗證請求方的權限（ECFramework 統一驗證）。
3. 更新 Redis DB5 中的即時賽事資料（`{gameType}:{lid}:{gDate}`）。
4. 將更新後的賽事資料同步寫入 Cassandra `pricecenter.games` 表（作為歷史記錄）。
5. 取得該賽事的 `Hub` 群組資訊（通常依 `gameType` 或 `lid` 區分）。
6. 透過 SignalR Hub 將變動的賽事資料推送給群組內所有已連線的客戶端。
7. 回傳 API 成功回應。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GameController` | 接收 PUT 請求，解析 `gameType` 與 request body 中的賽事資料。 |
| 2 | Validator | `ECFramework` | 驗證請求者的 Token 與 API 權限。 |
| 3 | Service | `GameService` | 協調資料更新與推播流程。呼叫 Provider 寫入儲存層，再呼叫 Hub 進行推送。 |
| 4 | Provider | `GameDataProvider` | 將賽事資料寫入 Redis DB5 暫存，並寫入 Cassandra 永久儲存。 |
| 5 | Hub | `GameHub` | 接收 Service 傳入的賽事更新資料，對指定群組廣播訊息。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Cache | Redis DB5 (`{gameType}:{lid}:{gDate}`) | Write | 更新即時賽事資料，供所有前端查詢 API 讀取。 |
| DB | Cassandra `pricecenter.games` | Write | 記錄賽事歷史資料，供後續對帳或查詢使用。 |
| Queue | 無 | - | 本場景未使用 Kafka 或 Queue 進行非同步推播，採用 SignalR 直接推送。 |

---

## 6. 重要規則

- **權限限制**：所有更新 API 皆需通過 `ECFramework` 驗證，僅允許具有 `pricecenter` 寫入權限的後端服務或管理員呼叫。
- **資料一致性**：必須先成功寫入 Redis，再寫入 Cassandra。若 Cassandra 寫入失敗，需觸發重試機制或記錄錯誤日誌，以確保資料最終一致。
- **推播範圍**：SignalR 推送應只針對關注該賽事或所屬 `gameType` 的連線群組，避免全局廣播造成不必要的效能損耗。
- **不可修改欄位**：`id`（賽事 ID）與 `gid`（全域賽事 ID）在建立後不可透過此類更新 API 修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求方權限不足 (401/403) | API 直接拒絕，不執行任何資料變更與推播。 |
| Redis 寫入失敗（連線逾時或記憶體不足） | API 回傳 500 錯誤。Service 層應攔截例外，不繼續寫入 Cassandra，也不推播。 |
| Cassandra 寫入失敗 | API 可能回傳成功，但須有補償機制（如 Retry Policy 或寫入失敗日誌），SignalR 推播仍會執行以維持前端即時性。 |
| SignalR 推送失敗（客戶端離線或網路中斷） | Hub 發送訊息為單向通知，不影響 API 回傳結果。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| NT-001 | API Test | 使用有效 Token 更新特定賽事比分 | API 回傳 200，Redis 與 Cassandra 資料更新，且已連線的 SignalR 客戶端收到推播。 |
| NT-002 | Permission Test | 使用無效或過期 Token 呼叫 | API 回傳 401，資料無任何變更。 |
| NT-003 | Flow Test | Redis 連線失敗時進行賽事更新 | API 回傳 500，略過後續的 Cassandra 寫入與 SignalR 推播。 |
| NT-004 | Flow Test | 模擬多個客戶端連線至 SignalR Hub | 確認所有在同 `gameType` 群組的客戶端都收到推播，其他群組不受影響。 |

---

## 9. 高風險區域

- **高風險 API**：`PUT /api/v1/games/{gameType}/score-status`（批量更新）。此 API 若參數錯誤或濫用，可能導致大量賽事資料錯誤，且會觸發大規模的 SignalR 推播。
- **Cache 一致性**：Redis 更新成功後，若有並發的 GET 請求到來，可能在 Cassandra 最終寫入完成前，查到短暫不一致的資料（需人工確認是否有分散式鎖或交易機制）。
- **無 Idempotency**：API 未提供 Idempotency Key 機制。相同請求重複發送會導致重複寫入與推播（需人工確認）。

---

## 10. 常見錯誤

- ❌ 新人誤以為 SignalR 推播是透過 Kafka 或 Queue 非同步處理。實際上，根據現有資訊，價格中心服務是直接呼叫 SignalR Hub，屬同步流程。
- ❌ 開發時在 Service 層直接呼叫 `GameDataProvider` 更新 Redis 後忘記寫入 Cassandra，導致資料在服務重啟後遺失。
- ❌ AI 或新人可能混淆不可跨服務寫入的限制，但此場景中 Redis 與 Cassandra 皆為 `pricecenterservice` 負責寫入的儲存層，無此問題。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | PriceCenterService WebAPI - `PUT /api/v1/games/{gameType}/score-status` |
| README 場景 | README.md - 常見使用場景：後台更新賽事比分 |
| 技術棧 | README.md - SignalR（即時推播） |
| Redis 結構 | README.md - `Redis DB5`：`{gameType}:{lid}:{gDate}` 賽事即時資料 |
| DB 角色 | pricecenterservice-detail.md - Cassandra `games` 為歷史資料，`buyercenter` Keyspace 由其負責寫入。 |
| 驗證框架 | README.md - ECFramework.ECService（內部統一驗證框架） |