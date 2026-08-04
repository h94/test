# 更新賽事結果資訊

## 1. 場景目的

由後台管理員或比分擷取機器人調用，更新指定賽事的詳細結果資訊（如各節比分、最終勝負隊、比賽時長等）。此操作為賽後結算的前置步驟，提供 `predictservice` 進行競猜結算時所需的完整賽果資料。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/games/{gameType}/{lid}/{gDate}/{id}/resultinfos` | 更新指定賽事的結果資訊 |

此 API 需要驗證 (✅)。

---

## 3. 流程總覽

1. 接收 PUT request，包含 `gameType`、`lid`、`gDate`、`id` 路徑參數及更新的結果資訊 request body。
2. 驗證 request body 結構合法性。
3. 根據 `gameType`、`lid`、`gDate` 組合，從 **Redis DB5** 查找對應的 `key` 以取得賽事即時資料。
4. 在 Redis 中找到對應 `id` 的單場賽事資料。
5. 更新該場賽事的結果資訊欄位（例如各節得分、最終結果、比賽狀態）。
6. 將更新後的完整賽事資料寫回 **Redis DB5**。
7. 非同步將此更新操作寫入 **Cassandra `pricecenter.games`** 進行歷史留存。
8. 透過 **SignalR** 即時推播更新後的賽事結果給所有已連接的前台客戶端。
9. 回傳成功響應。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `GameController.UpdateResultInfos` | 接收並驗證 request，調用 Service。 |
| 2 | Service | 需人工確認 (例: `GameService.UpdateGameResultInfo`) | 協調 Redis 讀寫與 Cassandra 寫入。 |
| 3 | Provider | `RedisGameProvider` (需人工確認) | 負責對 Redis DB5 進行 `HGET` / `HSET` 操作。 |
| 4 | Provider | `CassandraGameHistoryProvider` (需人工確認) | 負責非同步對 Cassandra 進行 `INSERT` 或 `UPDATE` 操作。 |
| 5 | Hub | `GameHub` (需人工確認) | 負責將更新後的賽事資訊透過 SignalR 推送至特定群組或全體客戶端。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Redis | DB5: `{gameType}:{lid}:{gDate}` | Read (HGET) / Write (HSET) | 讀取並更新指定賽事的即時結果資訊。 |
| Cassandra | `pricecenter.games` | Write (INSERT/UPDATE) | 將賽事結果變更記錄寫入歷史資料庫，供日誌查詢與資料分析。 |
| Kafka | 推測用於操作日誌 | Publish | 推測此更新操作可能會產生一筆操作日誌記錄 (用於 `datum_logs` 或 `action log`)。需人工確認。 |

---

## 6. 重要規則

- **權限限制**：此 API 需要通過 `ECFramework.ECService` 的內部驗證，僅允許管理後台或具相應權限的服務（如比分機器人）呼叫。從 README 確認所有寫入相關的 API 都需要驗證。
- **Redis 為主要操作對象**：賽事的即時結果更新首先反映在 Redis DB5 中，以確保前台查詢效能。
- **Cassandra 非同步寫入**：對 Cassandra 的寫入為最終一致性，不應阻塞對 Redis 的更新即時回應。
- **不可修改欄位**：`gameType`, `lid`, `gDate`, `id` 為賽事唯一標識，不可更新。僅能更新請求主體中包含的結果相關欄位。
- **結果資訊一致性**：更新結果時需確保資料結構符合 `GameDataModels` 中定義的合約，避免因資料格式錯誤導致後續結算服務 (`predictservice`) 處理失敗。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 路徑中的 `{gameType}:{lid}:{gDate}` 在 Redis 中不存在 | 回傳 404 Not Found 錯誤。 |
| 指定的 `{id}` 在 Redis 對應的賽事集合中找不到 | 回傳 404 Not Found 錯誤。 |
| Request body 格式不符或缺少必要欄位 | 回傳 400 Bad Request 錯誤，並指明驗證失敗的欄位。 |
| 無效的驗證憑證或權限不足 | 回傳 401 Unauthorized 或 403 Forbidden 錯誤。 |
| Redis 寫入失敗 | 回傳 500 Internal Server Error，並記錄錯誤日誌。操作應為原子性，不可部分寫入。 |
| Cassandra 寫入失敗 | 不影響 API 回應 (回傳 200 OK)，但需記錄嚴重錯誤日誌並觸發警報，以進行後續資料修復。 |
| 嘗試更新一個已結束 (Final) 且標記為不可修改的賽事 | 回傳 409 Conflict 或 422 Unprocessable Entity 錯誤。需人工確認是否有此業務規則。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| UT-RI-01 | API Test | 對有效路徑發送合法的結果資訊更新請求 | API 回應 200 OK，且 Redis 中賽事資料已更新。 |
| UT-RI-02 | API Test | 更新不存在的 `gameType` 或 `gDate` 組合下的賽事 | API 回應 404 Not Found。 |
| UT-RI-03 | API Test | 更新不存在的 `id` 賽事 | API 回應 404 Not Found。 |
| UT-RI-04 | Flow Test | 成功更新後，驗證 Cassandra 資料 | 在短時間內 (e.g., 5秒) Cassandra `games` 表中應存在更新後的資料。 |
| UT-RI-05 | Flow Test | 成功更新後，驗證 SignalR 推播 | 已連接的 SignalR 客戶端收到訊息，內容為更新後的完整 Game 物件。 |
| UT-RI-06 | Permission Test | 以無效的或過期的 token 請求 API | API 回應 401 Unauthorized。 |
| UT-RI-07 | Integration Test | 更新賽事結果後，呼叫 `predictservice` 結算 | 結算服務能夠基於新的結果資訊正確計算。 |

---

## 9. 高風險區域

- **Cache Consistency**：Redis 為主要資料來源，Cassandra 為歷史備份。若更新 Redis 成功但 Cassandra 寫入失敗，將產生資料不一致。需有強健的日誌記錄與補償機制。
- **跨服務相依**：此流程是賽事結算的前置步驟。如果 `predictservice` 在結果資訊尚未完全寫入 Redis 時就觸發結算，可能導致錯誤。需要確保有狀態機控制，例如賽事狀態需變更為 `Final` 才能觸發結算 (由 `setfinal` API 負責)。
- **併發更新**：多個來源（例如多個比分機器人）可能同時對同一場賽事進行更新，可能導致資料覆蓋。必須確保 Redis 的更新操作具有足夠的隔離性（例如使用 Redis 的 WATCH 或 Lua script）。
- **SignalR 推播可靠性**：若推播失敗，前台將不會即時顯示最新結果，影響使用者體驗。

---

## 10. 常見錯誤

- **錯誤流程**：開發人員誤將 Cassandra 設為主要更新對象，再同步回 Redis。正確流程應為 Redis 優先，Cassandra 非同步。
- **漏檢查項目**：未在 Service 層檢查返回的 Redis 讀取結果是否為 null，直接進行更新導致 NullReferenceException。
- **新人容易犯錯**：未理解 `{gameType}:{lid}:{gDate}` 這個 Redis key 代表一個聯賽在某天的所有賽事集合（通常是 Hash 結構），而誤用為單一賽事的 key。
- **AI 容易誤解**：模型可能自行想像 Cassandra `games` 表的 Schema 而不參考 `pricecenter-detail.md` 或對應的資料 models (`GameDataModels`)。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `PUT /api/v1/games/{gameType}/{lid}/{gDate}/{id}/resultinfos`，來自 `README.md` |
| DB (即時) | Redis DB5: `{gameType}:{lid}:{gDate}`，用途為「賽事即時資料（賠率、比分、狀態）」，來自 `README.md` |
| DB (歷史) | Cassandra `pricecenter.games`，用途為「賽事歷史資料（結果、比分）」，來自 `README.md` |
| 權限 | `README.md` API 表格中，該路由標記為需要驗證 ( ✅ ) |
| 相依服務 | `predictservice` 為結算相依方，其用途為「結算時提供賽事結果」，來自 `README.md` |