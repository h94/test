# 產生競猜每日報表

## 1. 場景目的
由排程或後台觸發，將當日競猜相關統計數據（投注數、鎖定數、解鎖數等）寫入報表儲存，以供後續查詢與分析。此流程為每日自動化任務的核心環節之一。

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/sport/report/predict` | 建立當日競猜每日報表 |

## 3. 流程總覽
1. 排程服務定時觸發或管理後台手動請求，呼叫「建立競猜每日報表」API
2. Controller 進行身份驗證，確保為授權後台使用者
3. Service 層向競猜核心資料庫（predict keyspace）讀取當日競猜統計（例如：總投注數、鎖定數量、解鎖數量等）
4. 將彙總後的數據寫入 Cassandra pricecenter keyspace 的 `predict_daily_reports` 表
5. 回傳成功狀態

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | ReportController.CreatePredictReport | 接收 request，呼叫 Service |
| 2 | Service | ReportService.CreatePredictDailyReport | 負責統計彙總與寫入邏輯 |
| 3 | Provider | PredictStatProvider | 向 predict keyspace 讀取當日投注、遊戲狀態等數據（需人工確認具體類別） |
| 4 | Service | ReportService | 將數據轉換為報表物件 |
| 5 | Provider | CassandraProvider | 寫入 Cassandra pricecenter.predict_daily_reports |

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | predict.betpool_bets | Read | 讀取當日競猜投注總數、鎖定總數等 |
| DB (Cassandra) | predict.betpool_games | Read | 讀取遊戲狀態以過濾進行中/已結算的競猜 |
| DB (Cassandra) | pricecenter.predict_daily_reports | Write | 寫入每日報表 |
| Redis | 無 | - | 未使用 |
| Queue | 無 | - | 未使用 |

## 6. 重要規則
- **權限限制**：僅限後台管理員角色可呼叫此 API（需驗證 JWT 或 token）
- **日期唯一性**：寫入時報表日期（Reportdate）不可重複，若當日已存在報表記錄，應回報錯誤或進行更新（需人工確認行為）
- **遊戲類型維度**：報表可能依 Gametype 分組統計（如 NBA、MLB），寫入時需確保 Gametype 值合法
- **資料一致性**：讀取統計數據時建議加上日期過濾條件，不可全表掃描
- **不可回傳欄位**：API 僅處理數據寫入，不可回傳任何投注明細（如 betzcoin、profitzcoin）
- **寫入限制**：此服務為 pricecenter 的 writer，寫入操作僅限於 `predict_daily_reports` 表，不可寫入其他不屬於該服務的表

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未帶有效 token 或權限不足 | 回傳 401 / 403 |
| 當日報表已存在 | 回傳錯誤訊息，拒絕重複寫入（或執行更新，需確認） |
| Cassandra 寫入失敗（timeout 或異常） | 回傳 5xx 錯誤，並記錄日誌，排程重試 |
| 讀取 predict 統計數據時查詢超時 | 回傳 5xx 錯誤 |
| 傳入的 Gametype 為空或非法值 | 回傳 400 驗證錯誤 |

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| PREDICTREPORT-01 | API Test | 正常排程呼叫，寫入當日正確統計數據 | 200 OK，Cassandra 寫入一筆記錄，數值與統計相符 |
| PREDICTREPORT-02 | Permission Test | 未帶 token 或使用一般會員 token 呼叫 | 401 / 403 |
| PREDICTREPORT-03 | Flow Test | 重複呼叫建立同一日報表 | 根據設計回傳衝突或更新，數據不重複累加 |
| PREDICTREPORT-04 | Integration Test | 寫入 Cassandra 成功後，透過 GET 查詢 | 能正確回傳報表數據 |
| PREDICTREPORT-05 | Error Test | Cassandra 寫入失敗 | 收到錯誤碼，日誌有對應記錄 |
| PREDICTREPORT-06 | Error Test | 當日無任何競猜活動（統計為0） | 仍寫入報表，各數值為 0 |

## 9. 高風險區域
- **高風險 table**：`pricecenter.predict_daily_reports`（寫入次數多，且為報表核心數據）
- **高風險 API**：`POST /api/v1/sport/report/predict`（需嚴格驗證權限，避免非授權寫入破壞數據）
- **跨服務資料同步**：數據來源於 predict keyspace（可能由 predictservice 管理），需確保當日數據已結算完畢再寫入，避免資料不完整
- **Transaction**：Cassandra 不支援跨表事務，若寫入中間失敗，可能導致部分數據遺漏；建議加入重試機制或冪等性設計
- **Cache consistency**：本流程無 Redis 快取，但需注意其他服務查詢報表時的快取更新
- **Idempotency**：排程可能意外重複觸發，API 設計需支援冪等（例如以 Reportdate + Gametype 作為唯一鍵）

## 10. 常見錯誤
- **新人容易犯錯**：
  - 未過濾遊戲狀態（如僅統計 `status=1` 已結束的競猜）導致數據錯誤
  - 直接回傳 `betpool_bets` 的明細信息到 DTO
  - 在寫入報表時忘記指定分區鍵導致 Cassandra 寫入失敗
- **AI 容易誤解**：
  - 誤以為寫入到 MySQL sport.predictdailyeport，而非 Cassandra pricecenter.predict_daily_reports
  - 忽略 Gametype 過濾，進行全表掃描
- **常見漏檢查項目**：
  - 未檢查請求的日期是否為當日
  - 未檢查 API 使用者權限
  - 寫入後未驗證數據正確性
- **常見錯誤流程**：
  - 排程間隔設定過短，導致 Cassandra 寫入壓力過大
  - 彙總統計時使用不正確的時間範圍（例如未使用 UTC）

## 11. Evidence
| 類型 | 來源 |
|------|------|
| API | README.md：`POST /api/v1/sport/report/predict` |
| DB | README.md：Cassandra pricecenter.predict_daily_reports |
| 權限 | README.md：所有每日報表 API 需要驗證 |
| 讀取限制 | pricecenter-detail.md：`predictdailyeport 查詢` 須指定日期區間及 Gametype |
| 寫入服務 | pricecentermanage-detail.md：pricecentermanage 對 predict 有 writer/reader 角色 |
| 不可回傳欄位 | predict-detail.md：betpool_bets 金額欄位不可回傳 |