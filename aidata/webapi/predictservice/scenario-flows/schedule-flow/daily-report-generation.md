# 每日篩選報表生成

## 1. 場景目的

每日定時任務調用 `predictservice` 內部 API，根據指定日期、遊戲類型、聯賽與篩選條件，計算各帳號的預測勝率與主要玩法命中率，並將結果寫入 `predict.predict_filter_reports` 與 `predict.predictfilterreports_mainbet` 表，以供排行榜或後台查詢使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/reports/predictfilterreports` | 觸發每日篩選報表生成（後台排程專用，需驗證） |

---

## 3. 流程總覽

1. 定時排程觸發 POST 請求至 predictservice
2. 驗證請求者權限（內部服務或後台管理員）
3. 解析 request body：指定 `reportdate`、`gametype`、`lid`、`filtertype`
4. 查詢 `predict.predict_bets` 等注單記錄，彙整指定日期區間內各帳號的所有下注
5. 根據對應的賽事結果（來自 `pricecenter` 之賽果資料），計算每個帳號的勝率與主要玩法命中數據
6. 寫入計算結果至 `predict.predict_filter_reports`（一般篩選）與 `predict.predictfilterreports_mainbet`（主要玩法篩選）
7. 可選：計算並寫入對應的排行榜或活動資料（需人工確認是否為此場景一部份）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ReportsController` / `CreatePredictFilterReports` | 接收 request 並驗證 |
| 2 | Service | `ReportService` / `GenerateFilterReports` | 組合篩選條件、排程計算邏輯 |
| 3 | Provider | `PredictReportProvider` / `AggregateBets` | 從 `predict_bets` 表中讀取指定範圍的注單並彙整 |
| 4 | Provider | `PredictReportProvider` / `CalculateWinRate` | 根據賽事結果計算勝率 |
| 5 | Provider | `PredictReportProvider` / `SaveFilterReports` | 將計算結果寫入 `predict_filter_reports` 與 `predictfilterreports_mainbet` |

> **需人工確認**：以上 Class/Method 名稱基於常見命名慣例推測，未取得實際 class code evidence。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `predict.predict_bets` | Read | 讀取指定日期、遊戲類型、聯賽的所有下注記錄，作為計算來源 |
| DB | `predict.predict_filter_reports` | Write | 寫入篩選報表結果（date, game_type, lid, account, win_rate 等） |
| DB | `predict.predictfilterreports_mainbet` | Write | 寫入主要玩法篩選報表 |
| DB | `pricecenter` (賽果相關表) | Read | 讀取賽事結果以判斷輸贏（實際表名需人工確認） |
| Redis | 無直接使用證據 | - | 此場景為排程一次性大量寫入，推測無快取；若查詢端有快取，需後續手動清除 |
| Kafka/Queue | 未使用 | - | 此流程為同步 API 觸發，無佇列邏輯 |

---

## 6. 重要規則

- **權限限制**：僅內部排程或具有後台管理權限的帳號可呼叫此 API。
- **不可回傳欄位**：
  - `predict_filter_reports` 中的 `account` 欄位對外（如公開排行榜）查詢時不可回傳，需脫敏處理。
  - 計算過程中的內部注單明細（`predict_bets.*`）不可直接回傳給前端。
- **查詢條件限制**（參考 predict-detail.md 中對 `predictfilterreports` 的規定）：
  - 必須依 `reportdate`、`gametype`、`lid`、`filtertype` 過濾，不可全表掃描。
- **寫入限制**：
  - `predict_filter_reports` 表為每日批次寫入，相同 `date + game_type + lid + filter_type + account` 組合原則上應為覆寫（UPSERT），避免重複記錄。
- **TTL 規則**：無直接證據，推測報表資料不設 TTL（永久保存）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------| 
| 未提供必要參數（`reportdate`, `gametype`, `lid`, `filtertype`） | 回傳 400 Bad Request 並附帶錯誤訊息 |
| 指定的 `gametype` 不存在或未啟用 | 回傳 400 或 404，不進行計算 |
| 查無任何下注記錄（`predict_bets` 無符合條件的資料） | 仍回傳 200，寫入的報表為空（無勝率資料） |
| DB timeout 或 Cassandra 連線失敗 | 回傳 500 Internal Server Error，排程應有 retry 機制（需人工確認） |
| 計算過程中發生部分寫入失敗 | 需人工確認：目前無 Transaction 機制，可能造成部分資料缺失 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| IT-01 | Integration Test | 提供完整參數，模擬已存在注單與賽果 | 成功回傳 200，`predict_filter_reports` 寫入正確勝率 |
| IT-02 | Integration Test | 指定日期無任何注單 | 成功回傳 200，報表內無數據 |
| PT-01 | Permission Test | 使用一般前台用戶身份呼叫 | 回傳 403 Forbidden |
| FT-01 | Flow Test | 模擬 Cassandra 短暫中斷後恢復 | 排程應能 retry 並最終成功寫入（若實作 retry） |
| FT-02 | API Test | 缺少 `reportdate` 參數 | 回傳 400 Bad Request |

---

## 9. 高風險區域

- **高風險 Table**：`predict.predict_bets`（讀取量大）、`predict.predict_filter_reports`（每日全量覆寫）。
- **高風險 API**：`POST /api/v1/reports/predictfilterreports`，若被頻繁調用可能造成 DB 壓力。
- **跨服務資料同步**：依賴 `pricecenter` 的賽果資料，若賽果延遲寫入，可能造成報表數據不完整。
- **Cache consistency**：若排行榜或查詢端對報表有快取，每日報表生成後需主動清除，否則顯示舊資料。

---

## 10. 常見錯誤

- ❌ 新人直接在 “predict_bets” 表中用 `account` 做全表掃描查詢 → 應遵循 Cassandra 主鍵設計，依 `game_type`、`lid`、`g_date` 等條件過濾。
- ❌ 對外回傳 `predict_filter_reports` 時包含完整 `account` → 公開排行榜應遮蔽帳號。
- ❌ 假設 `predictfilterreports_mainbet` 的欄位與 `predict_filter_reports` 完全相同 → 它們是不同的表，需注意 `filtertype` 與特定欄位的差異。
- ❌ 忘記處理賽果未產生的注單（尚未開獎）→ 應只計算已有結果的注單，未開獎的跳過。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/v1/reports/predictfilterreports` (from README) |
| DB | `predict.predict_filter_reports` (from README) |
| DB | `predict.predictfilterreports_mainbet` (from predict-detail.md 讀取規則) |
| Rule | 報表查詢需指定 partition key 過濾，不可全表掃描 (from predict-detail.md) |
| Rule | 對外回傳不可包含 account 原始值 (from predict-detail.md 不可回傳欄位) |