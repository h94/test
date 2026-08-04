# 賽事結算通知預測服務

## 1. 場景目的

當管理員或自動化作業將賽事設定為最終結果（Final）時，pricecenterservice 必須通知 predictservice 進行競猜結算。由於通訊機制（直接 gRPC/HTTP 呼叫、Kafka 訊息佇列）在現有文件中未明確指定，本文件標記為「需人工確認」。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/v1/games/{gameType}/setfinal` | 設定賽事為最終結果，觸發結算通知 |

---

## 3. 流程總覽

1. 接收 PUT `/api/v1/games/{gameType}/setfinal` 請求
2. 驗證請求方權限（通過 ECFramework.ECService 驗證）
3. 從 Redis DB5 讀取賽事即時資料，檢查賽事狀態
4. 更新 Cassandra `pricecenter.games` 表的賽事狀態為 Final
5. 更新 Redis DB5 中的賽事狀態快取
6. 透過 SignalR 推播賽事狀態變更給前台
7. 通知 predictservice 進行競猜結算（通訊機制待確認）
8. 回傳操作成功

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | GameController.SetFinal | 接收請求，驗證權限 |
| 2 | Service | GameService.SetFinal | 讀取 Redis 賽事資料，檢查賽事是否存在 |
| 3 | Provider | GameProvider.UpdateGameStatus | 更新 Cassandra 賽事狀態 |
| 4 | Provider | RedisProvider.UpdateGameCache | 更新 Redis DB5 快取 |
| 5 | Service | SignalRProvider.NotifyStatusChange | 推播狀態變更至前台 |
| 6 | Service | PredictServiceNotifier.NotifySettlement | 通知 predictservice 進行結算（需人工確認具體實作） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | DB5 Key: `{gameType}:{lid}:{gDate}` | Read | 讀取賽事即時資料，確認賽事存在 |
| Redis | DB5 Key: `{gameType}:{lid}:{gDate}` | Update | 更新賽事狀態為 Final |
| Cassandra | pricecenter.games | Update | 寫入賽事最終結果狀態 |
| Queue | Kafka / Direct Call | Publish / Call | 通知 predictservice 結算（需人工確認） |

---

## 6. 重要規則

- **權限限制**：需通過 ECFramework.ECService 內部統一驗證框架，僅允許後台管理員或系統服務呼叫。
- **狀態檢查**：賽事必須存在於 Redis DB5 中，且當前狀態必須允許設定為 Final（需人工確認具體狀態機）。
- **冪等性**：重複呼叫 setfinal 不應重複通知 predictservice 結算。需確認是否有 `IsSettled` 標記防止重新處理。
- **資料一致性**：Redis 快取與 Cassandra 永久儲存必須同步更新，避免快取與資料庫不一致。
- **不可修改欄位**：賽事 ID（gid）、聯賽 ID（lid）、比賽日期（gDate）為不可變更識別碼。
- **結算通知保證**：需確保 predictservice 確實收到結算通知，若通訊失敗應有重試機制（需人工確認）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 賽事不存在（Redis 中無對應 Key） | 回傳 404 Not Found，不進行任何後續操作 |
| 賽事狀態不允許設定為 Final | 回傳 400 Bad Request，說明狀態不符 |
| Cassandra 寫入失敗 | 回傳 500 Internal Server Error，記錄錯誤日誌 |
| Redis 快取更新失敗 | 回傳 500 Internal Server Error，但需確保 Cassandra 已寫入（需人工確認交易策略） |
| predictservice 呼叫失敗 | 記錄錯誤日誌，觸發重試或人工介入（需人工確認） |
| 重複 setfinal 請求（冪等性） | 回傳 200 OK 或 409 Conflict，不重複結算（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| IT-SF-01 | Integration Test | 成功設定賽事為 Final | 狀態更新，predictservice 收到通知 |
| IT-SF-02 | API Test | 賽事不存在時呼叫 setfinal | 回傳 404 |
| IT-SF-03 | Permission Test | 未授權請求呼叫 setfinal | 回傳 401 或 403 |
| IT-SF-04 | Flow Test | Redis 更新成功但 Cassandra 失敗 | 系統回報錯誤，無髒資料殘留（需人工確認） |
| IT-SF-05 | Flow Test | predictservice 呼叫失敗 | 系統記錄錯誤，有重試機制（需人工確認） |
| IT-SF-06 | Idempotency Test | 重複呼叫 setfinal | 不重複通知 predictservice（需人工確認） |

---

## 9. 高風險區域

- **高風險 table**：Cassandra `pricecenter.games`，包含賽事最終結果，錯誤寫入將直接影響結算、派彩與對帳。
- **高風險 API**：`PUT /api/v1/games/{gameType}/setfinal`，具有結算觸發能力，必須嚴格控制呼叫來源與權限。
- **跨服務資料同步**：pricecenterservice 必須確保 predictservice 收到結算通知，避免賽事結算遺漏。
- **Cache consistency**：Redis DB5 與 Cassandra games 表的賽事狀態必須一致。
- **Queue retry**：若使用 Kafka，需確認 Topic 配置與 Consumer Group 的 retry 策略。
- **Idempotency**：setfinal 操作必須具備冪等性，避免重複結算與重複派彩。

---

## 10. 常見錯誤

- **新人容易犯錯**：直接更新 Redis 而未同步更新 Cassandra，導致快取與持久層不一致。
- **AI 容易誤解**：誤認為 pricecenterservice 直接處理結算邏輯，但實際上 pricecenterservice 僅負責通知 predictservice 進行結算。
- **常見漏檢查項目**：未檢查賽事當前狀態是否允許設為 Final，導致狀態機異常。
- **常見錯誤流程**：predictservice 呼叫失敗後無重試機制，導致賽事已結束但競猜未結算。

---

## 11. Evidence

所有重要結論必須附 evidence：

| 類型 | 來源 |
|---|---|
| API | GameController.SetFinal (需人工確認實際 Controller 名稱) |
| DB | Cassandra pricecenter.games |
| Cache | Redis DB5 `{gameType}:{lid}:{gDate}` |
| 服務相依 | README 服務相依章節：predictservice |
| 場景描述 | README 常見使用場景：賽事結算流程 |
| 權限驗證 | README 技術棧：ECFramework.ECService |

## 12. 待確認事項（需人工確認）

1. **通訊機制**：pricecenterservice 如何通知 predictservice？是直接 HTTP/gRPC 呼叫，還是透過 Kafka 訊息佇列？Topic 名稱為何？
2. **重試策略**：若通知 predictservice 失敗，是否有自動重試？重試次數與間隔？
3. **冪等性實作**：如何確保重複呼叫 setfinal 不會導致重複結算？是否有 `SettlementStatus` 或 `IsSettled` 欄位？
4. **狀態機**：賽事從哪些狀態可以轉換為 Final？是否允許從 InPlay 直接設定為 Final？
5. **交易一致性**：若 Redis 與 Cassandra 其中一個寫入失敗，系統如何處理？是全部回溯還是部分成功？
6. **實際 Controller/Service 名稱**：負責此流程的具體類別與方法名稱，需從原始碼確認。