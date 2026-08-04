# 自動結算預測

## 1. 場景目的
根據賽事結果自動結算預測投注，更新注單的輸贏結果（WinLoss）及獲利點數（ProfitPoint），並將狀態轉為已結算。

---

## 2. 入口 API
此為背景排程流程，無對外 API 入口。  
觸發方式推測為定時任務或訊息佇列（需人工確認）。

---

## 3. 流程總覽
1. 排程服務觸發結算作業（需人工確認觸發機制，如 cron、Kafka / RabbitMQ 事件）。
2. 查詢 `PredictBetResult` 表中狀態為「待結算」的注單（需確認狀態值定義）。
3. 根據注單中的比賽識別碼（GameType、LID、GDate、GID）讀取對應比賽結果，資料來源為 `games_{gameType}` 或外部 API（需確認結果欄位與取得方式）。
4. 依注單的玩法（Mode）、盤口（Spread）、賠率（Odd）及比賽結果計算 WinLoss（Win/Loss/Draw）與 ProfitPoint。
5. 以交易更新對應注單的 Status、WinLoss、ProfitPoint。
6. 可能透過 SignalR 或訊息佇列推送結算結果至前端（需人工確認）。

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Scheduler | (定時器／訊息監聽器) | 啟動結算工作單元 |
| 2 | Service | SettlePredictService (推測) | 查詢待結算注單、調用結算邏輯 |
| 3 | Provider | PredictResultProvider (推測) | 讀取 `PredictBetResult`、更新結算結果 |
| 4 | Provider | GameDataProvider | 讀取 `games_{gameType}` 取得比賽結果 |
| 5 | Hub (選用) | ChatHub (推測) | 推送結算通知至用戶所屬群組 |

> 註：實際類別與方法名稱需人工確認原始碼。

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | PredictBetResult | Read / Update | 讀取待結算注單，更新 WinLoss、ProfitPoint、Status |
| DB | games_{gameType} | Read | 讀取比賽結果，作為結算基準 |
| Queue (推測) | 結算結果 Topic | Publish | 將已完成結算的事件通知其他服務（需確認） |
| Cache (推測) | 用戶盈虧快取 | Write | 更新用戶即時盈虧統計（需確認） |

---

## 6. 重要規則
- **冪等性**：已結算注單不得重複結算，更新時需檢查原狀態，僅限「待結算」→「已結算」。
- **狀態定義**：`Status` 值需明確定義（如 0:未結算、1:已結算、-1:無效），目前無 precise mapping（需人工確認）。
- **WinLoss 判定**：依據比賽結果與盤口（Spread）比對，僅限於有結果的比賽才進行結算。
- **ProfitPoint 計算**：須採用 (賠率 Odd - 1) × 投注點數 或其他規則，依據 `Mode` 不同可能變化（需確認業務公式）。
- **交易一致性**：同一注單的 Status、WinLoss、ProfitPoint 必須在同個交易中更新。
- **不可修改欄位**：注單 ID、Account、Mode、Spread、Odd 等原始投注內容結算後禁止修改。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|------|----------|
| 比賽結果尚未產生 | 略過該注單，保留待結算狀態，等待下次執行 |
| 注單已被其他行程結算 | 檢查狀態後跳過，不重複更新 |
| 更新 `PredictBetResult` 失敗 | 交易回滾，記錄錯誤，可透過重試機制再處理（需確認重試實作） |
| 無法取得比賽結果（資料源異常） | 記錄錯誤，留待下次重試，避免誤判輸贏 |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC01 | Integration | 比賽結果正確，多筆待結算注單同時結算 | 每筆注單正確更新 WinLoss 與 ProfitPoint |
| TC02 | Integration | 同一注單觸發兩次結算 | 第二次結算不更新，資料與首次相同 |
| TC03 | Flow | 比賽結果不存在 | 注單維持原狀態，不進行任何變更 |
| TC04 | DB | 更新過程中發生連線中斷 | 交易回滾，注單狀態不變 |
| TC05 | Permission | 非結算服務直接呼叫更新 API | 應拒絕存取（需確認是否有此保護） |

---

## 9. 高風險區域
- **PredictBetResult 表**：多筆並行結算可能產生死結或 race condition，需要適當的鎖定機制（如 SELECT ... FOR UPDATE 或樂觀鎖）。
- **比賽結果同步**：若結果來自外部系統且存在延遲，可能導致多次無效嘗試，需設定合理的重試策略與告警。
- **狀態一致性**：更新 WinLoss/ProfitPoint 後若未成功寫入 Status，可能導致資料不一致。
- **Queue 消費**：若透過 Queue 驅動結算，需確保訊息不遺失、不重複消費。

---

## 10. 常見錯誤
- 誤以為結算流程是同步 API，實作時設計成 HTTP 接口，忽略背景任務特性。  
- 未實作冪等邏輯，導致重複結算並篡改盈虧紀錄。  
- 未考慮不同 `Mode`（如讓分、大小分）對 ProfitPoint 的影響，產生錯誤的公式。  
- AI 可能憑空產生不存在的 Controller 與 API path，應堅持以排程或事件驅動的架構為基礎。

---

## 11. Evidence
| 類型 | 來源 |
|------|------|
| DB 表結構 | Phase2 分析產出之 `PredictBetResult` 表 (含 Status, WinLoss, ProfitPoint, Account, ID 等欄位) |
| 業務描述 | README 明列「系統自動結算輸贏（WinLoss）及獲利點數（ProfitPoint）」 |
| 比賽資料存取 | `games_{gameType}` 表存在於 DB schema 分析中，由 `GameDataProvider` 操作 |
| 不確定部分 | 結算服務程式碼位置、確切觸發機制、賠率計算公式、狀態列舉值，均需人工確認原始碼後補齊 |

---
**需人工確認項目：**
- 結算服務的實際類別名稱與觸發方式（定時器、訊息事件）。
- `Status` 欄位的明確列舉值與狀態機轉換規則。
- 不同 `Mode` 下的 ProfitPoint 公式。
- 佇列（Kafka / RabbitMQ）使用情況與訊息結構。
- 是否透過 SignalR 推送結算通知。