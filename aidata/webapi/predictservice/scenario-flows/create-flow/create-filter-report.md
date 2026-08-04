# 建立筛选报表演算

## 1. 場景目的

每日由排程觸發，針對指定遊戲類型、聯賽及日期範圍，計算各帳號的勝率、盈利等統計指標，並產生篩選報表（`predict_filter_reports`、`predictfilterreports_mainbet`）及週報表，供前台排行榜與管理後台查詢。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/reports/predictfilterreports` | 觸發排程計算（內部或後台呼叫） |

- 此 API 需驗證（由後台管理員或內部排程模組發起，非前台用戶）。
- 推測 Request Body 包含 `date`、`gameType`、`lid`、`filterType` 等參數（需人工確認）。

---

## 3. 流程總覽

1. 接收請求，驗證呼叫方權限（後台角色或內部憑證）。
2. 依據參數從 `predict.predict_bets` 讀取符合條件（日期、遊戲類型、聯賽）的下注記錄。
3. 依照 `account` 分組計算：
   - 勝率：獲勝注數 / 總注數。
   - 盈利點數 / ZCoin 盈虧。
   - 其他篩選指標（依 `filterType` 決定）。
4. 將計算結果寫入 `predict.predict_filter_reports`（與 `predictfilterreports_mainbet`）。
5. 若為週結算，同步更新 `predict.weekly_reports`。
6. 寫入 `predict.calculate_logs` 記錄計算結果（成功 / 失敗），供稽核與除錯。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ReportController.PostPredictFilterReports` | 接收 HTTP 請求，驗證 Token 與權限，呼叫 Service（需人工確認） |
| 2 | Service | `ReportService.GenerateFilterReport` | 實際計算邏輯：讀取注單、分組、計算勝率、寫入報表（需人工確認） |
| 3 | Provider | `PredictBetProvider.GetBetsByFilter` | 從 Cassandra 讀取 `predict_bets`，使用分頁避免全表掃描（需人工確認） |
| 4 | Provider | `ReportProvider.UpsertFilterReport` | 將計算結果批次寫入 `predict_filter_reports` 及相關表（需人工確認） |
| 5 | Provider | `ReportProvider.InsertCalculateLog` | 寫入 `calculate_logs` 記錄（需人工確認） |

> **注意**：上述層級與名稱若未提供程式碼，需人工確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `predict.predict_bets` | Read | 讀取待計算的下注記錄 |
| DB (Cassandra) | `predict.predict_filter_reports` | Write / Update | 寫入各帳號勝率等篩選指標 |
| DB (Cassandra) | `predict.predictfilterreports_mainbet` | Write / Update | 寫入主玩法篩選報表（需人工確認） |
| DB (Cassandra) | `predict.weekly_reports` | Write / Update | 週報表（若計算週期符合） |
| DB (Cassandra) | `predict.calculate_logs` | Write | 記錄排程執行結果與時間 |
| Redis | 未觀察到 | — | 此流程未使用 Redis 快取（需人工確認） |
| Kafka | `applogs` | Produce | 記錄執行日誌（依系統慣例） |

---

## 6. 重要規則

- **權限限制**：此 API 需後台管理權限，不允許一般用戶呼叫（即使驗證過 Token，也需檢查角色或來源 IP）。
- **計算範圍**：必須依據請求的 `reportdate`、`gametype`、`lid`、`filtertype` 精確篩選，禁止全表掃描。
- **分區鍵查詢**：讀取 `predict_bets` 時需搭配 partition key 條件（如 `game_type`），以符合 Cassandra 高效能要求。
- **不可修改欄位**：`predict_bets` 的 `amount`、`result` 等原始資料僅讀取，不得修改；報表寫入後亦不可由外部 API 直接篡改（僅透過排程更新）。
- **資料隱私**：寫入報表的 `account` 欄位在後續查詢 API 時須依情境決定是否脫敏（排行榜 API 不可暴露帳號）。
- **冪等性**：同一日期、`gameType`、`filterType` 可重複執行但應覆蓋舊結果；不可因重複執行導致數據累加（需用 UPSERT）。
- **時間格式**：所有時間比對應使用 UTC，避免時區錯誤。
- **CQL 批次**：若同時寫入多張表，需注意 Cassandra batch 的限制（不分區批次可能造成效能問題）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 無符合條件的下注記錄 | 寫入空的報表記錄（或回傳成功，報表內無資料） |
| 帳號被停用或凍結（`status ≠ 1`） | 該帳號不應計入統計，需在讀取會員時過濾 |
| Cassandra 讀取逾時 | 重試機制（若無則記錄失敗到 `calculate_logs`） |
| Cassandra 寫入失敗 | 記錄錯誤日誌，報表中斷，不可部分寫入導致不一致 |
| 參數缺漏（如未傳 `gameType`） | 回傳 400 Bad Request，提示必要欄位 |
| 未認證或無權限呼叫 | 回傳 401 / 403 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| FR-IT-01 | Integration Test | 模擬排程觸發，有正常下注資料 | 報表正確產出，勝率計算無誤 |
| FR-API-01 | API Test | 無權限 Token 呼叫 POST | 回傳 401 或 403 |
| FR-API-02 | API Test | 傳入不存在的 `gameType` | 無資料，回傳成功但報表為空 |
| FR-FLOW-01 | Flow Test | 連續兩次觸發同日期同條件 | 第二次執行後報表仍是正確值，無重複累加 |
| FR-PERM-01 | Permission Test | 使用一般會員 Token 呼叫 | 拒絶訪問 |
| FR-EDGE-01 | Edge Test | 大量下注記錄（例如百萬筆） | 計算在可接受時間內完成，無 OOM |

---

## 9. 高風險區域

- **高風險 Table**：`predict_filter_reports`、`predictfilterreports_mainbet` —— 若計算邏輯錯誤，會直接影響排行榜正確性與用戶獎金（若報表用於派獎）。
- **跨服務資料同步**：本服務僅計算，不直接派彩；但若後續服務依賴此報表發放獎勵，則數據錯誤會造成金流損失。
- **Transaction**：Cassandra 無跨表事務，寫入多個報表時需依賴應用層補償或重試，可能導致部分表更新失敗。
- **Cache consistency**：本流程目前未使用 Redis；若後續加入報表快取，則排程完成後需主動清除相關快取 key。
- **Queue retry**：若使用背景工作或 Queue，需確保重試不會重複計算（靠冪等寫入）。
- **Idempotency**：強烈依賴 primary key 設定（如 `date + game_type + lid + filtertype + account`），若 key 設計不唯覆蓋則可能殘留舊資料。

---

## 10. 常見錯誤

- ❌ 新人認為此 API 是給一般用戶「手動產生報表」→ 實際上僅由排程或管理員呼叫。
- ❌ AI 直接對 `predict_bets` 全表掃描計算 → 應嚴格限制 `game_type` 與日期範圍。
- ❌ 計算時未過濾機器人帳號（`gamerobots.enabled=1`）→ 會造成報表失真。
- ❌ 勝率分母為 0 時未處理 → 導致除以零例外。
- ❌ 寫入報表時未使用 UPSERT 語法 → 重複執行時可能插入重複記錄。
- ❌ 忘記記錄 `calculate_logs` 的失敗原因 → 造成監控困難。
- ❌ 後續 API 回傳報表時直接暴露 `account` → 應檢查是否為公開排行榜，必要時脫敏。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/v1/reports/predictfilterreports` (README.md - 篩選報表區塊) |
| Table 結構 | `predict.predict_filter_reports` (README Table 清單) |
| Table 結構 | `predict.weekly_reports` (README Table 清單) |
| Table 結構 | `predict.calculate_logs` (README Table 清單) |
| 讀取規則 | `predictfilterreports` 查詢須依 `reportdate, gametype, lid, filtertype` 過濾 (predict-detail.md - "predictfilterreports 與 predictfilterreports_mainbet") |
| 服務角色 | predictservice 為 predict keyspace owner (predict-detail.md - 服務角色總覽) |
| 不可回傳規則 | 排行榜不可回傳 account (predict-detail.md - 不可回傳欄位) |
| 權限限制 | 無全部 code evidence，需人工確認 |

> **建議新增文件 / 規則**：  
> - 明確 `filterType` 的列舉值與對應計算公式。  
> - 補充 `predictfilterreports_mainbet` 與 `predict_filter_reports` 的差異說明。  
> - 排程觸發的定時設定（Cron）與失敗通知機制。  
> - 若報表用於獎勵派發，需建立跨服務資料校驗流程。