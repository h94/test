# 產生會員每日報表

## 1. 場景目的
本流程由排程服務每日觸發，將前一日會員相關統計數據（註冊、活躍、聊天、交易、編輯聊天筆數）寫入 `sport.memberdailyreport`，供管理後台查詢與數據分析使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/sport/report/member` | 建立會員每日報表 |

**⚠️ 需人工確認**  
OpenAPI 文檔未包含 Report API 的 Request Body Schema。目前無 evidence 可確定具體參數。推測 Request Body 結構應包含 `Reportdate`、`Registers`、`Actives`、`Chats`、`Trades`、`Editorchats` 等欄位，但需確認實際 API 程式碼。

---

## 3. 流程總覽
1. 排程（如 cron job 或 Hangfire）在每日固定時間觸發。
2. 排程呼叫 `POST /api/v1/sport/report/member`。
3. Controller 接收請求，驗證 API 權限。
4. 呼叫 Service 層處理寫入邏輯。
5. Service 將統計數據寫入 MySQL `sport.memberdailyreport` 表格。

**⚠️ 需人工確認**  
- 排程是否直接呼叫此 API，或是由內部 Provider 直接寫入，尚無 evidence。
- 實務上此 API 可能僅存在於後台操作（手動補寫報表），由排程直接透過 Provider 層寫入 DB 較為常見。但此流文依據 README 描述「排程自動執行 → POST ... → 寫入」，故仍以 API 為入口。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `ReportController.CreateMemberReport`（需人工確認方法名） | 接收 POST 請求，驗證權限 |
| 2 | Service | `IReportService` / `ReportService`（需人工確認） | 驗證輸入日期格式、數值範圍 |
| 3 | Provider | `ISportDbProvider` / `SportDbProvider`（需人工確認） | 將資料寫入 `sport.memberdailyreport` |
| 4 | Provider | （同上） | 使用 INSERT INTO 或 REPLACE INTO 語法（需人工確認） |

**⚠️ 需人工確認**  
- 實際 Controller / Service / Provider 名稱及方法簽名，因 source code analysis 未包含完整 Report 實作細節。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | MySQL `sport.memberdailyreport` | Write（INSERT） | 寫入每日統計數據 |
| DB | MySQL `sport.memberdailyreport` | Read（SELECT） | 供 `GET /api/v1/sport/report/member` 查詢使用 |
| Cache | Redis | 未使用 | 依據現有資料，此場景未使用 Redis 快取 |
| Queue | Kafka / MQ | 未使用 | 依據現有資料，此場景未使用佇列 |

**⚠️ 需人工確認**  
- 若實際寫入邏輯在排程內為內部呼叫（非 API），可能直接使用 `REPLACE INTO` 或 `INSERT INTO ... ON DUPLICATE KEY UPDATE`，以處理同一天重複產生的情況。需確認 Provider 實作。

---

## 6. 重要規則

- **權限限制**
  - API 需要驗證（依據 README：`POST /api/v1/sport/report/member` 標記為需要驗證）。
  - 需後台管理員權限才可呼叫（需人工確認確切角色）。

- **欄位限制**
  - `Reportdate` 格式為 `YYYY-MM-DD`（char(10)），為表格主鍵，寫入後不可修改。
  - 所有數值欄位（Registers / Actives / Chats / Trades / Editorchats）為 int，不可為負數。

- **不可回傳欄位**
  - 此場景為寫入操作，無回傳欄位限制。查詢時（GET），僅回傳日期與數值，不含用戶個資。

- **Transaction 規則**
  - 無跨表 Transaction（單一 Table INSERT），無需處理分散式交易。

- **Retry 規則**
  - 需人工確認：若寫入失敗（如 DB timeout），是否由排程自動重試，或需人工手動補寫。

- **不可修改欄位**
  - `Reportdate` 為主鍵，不可修改。若需更正數據，需由管理後台手動 DELETE 後重新 INSERT。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| Request Body 缺少 `Reportdate` | HTTP 400 Bad Request |
| 權限不足（未帶有效 token 或角色不符） | HTTP 401 Unauthorized / 403 Forbidden |
| `Reportdate` 格式錯誤（非 `YYYY-MM-DD`） | HTTP 400 Bad Request |
| 數值欄位為負數 | HTTP 400 Bad Request |
| 同一 `Reportdate` 寫入第二次（INSERT 重複主鍵） | 若使用 INSERT，應回傳 409 Conflict 或主鍵衝突錯誤；若使用 REPLACE INTO，則會覆蓋。需人工確認預期行為 |
| MySQL 連線 timeout | HTTP 500 Internal Server Error，排程應記錄錯誤並可觸發 retry |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| T1 | API Test | 成功寫入一筆今日報表 | HTTP 200，DB 內出現該筆記錄 |
| T2 | API Test | 未帶 token 呼叫 | HTTP 401 |
| T3 | API Test | 帶錯誤格式 Reportdate (`202511-01`) | HTTP 400 |
| T4 | API Test | Registers = -5 | HTTP 400 |
| T5 | API Test | 重複寫入同一 Reportdate | 依設計：HTTP 409 或成功覆蓋（需確認） |
| T6 | Flow Test | 排程自動呼叫 → 驗證 DB 資料 | DB 資料正確，數值與原始數據相符 |
| T7 | Permission Test | 非管理員角色呼叫 | HTTP 403 |

---

## 9. 高風險區域

- **高風險 table**：`sport.memberdailyreport` — 寫入後預設不可修改，若數據錯誤，需透過後台手動刪除並補寫。
- **高風險 API**：`POST /api/v1/sport/report/member` — 若排程重複觸發造成重複寫入，需確認 Idempotency 機制是否存在。
- **跨服務資料同步**：此流程依賴其他服務（如 pricecenterservice 或 memberservice）所計算的統計數據，若上游數據錯誤，報表會連帶錯誤。
- **Idempotency**：需人工確認是否支援重複寫入的冪等性（例如使用 REPLACE INTO），以避免排程重試時主鍵衝突。

---

## 10. 常見錯誤

- ❌ **直接修改已寫入的報表數據** → ✅ 應透過後台刪除後補寫，不可直接 UPDATE 數值欄位（除非流程明確定義）。
- ❌ **查詢報表時未指定日期區間** → ✅ GET API 需加上 `WHERE Reportdate >= ? AND Reportdate <= ?`，避免撈取所有歷史資料導致效能問題。
- ❌ **排程寫入時間設為 00:00:00，但數據尚未完全彙整** → ✅ 排程時間應設在確保所有來源數據皆已產出之後（需依賴上游服務完成）。
- ❌ **對外 API 回傳此表時包含內部稽核欄位** → ✅ 此表皆為聚合數據，無敏感個資，但仍應避免在未經授權下暴露。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README: `POST /api/v1/sport/report/member` |
| DB Schema | `sport.memberdailyreport` CREATE TABLE statement |
| DB 使用脈絡 | sport-detail.md: pricecentermanage 為 writer / reader |
| 場景描述 | README: 常見使用場景 — 每日統計報表產生 |
| Controller | 需人工確認（ReportController） |
| Service | 需人工確認（ReportService） |
| Provider | 需人工確認（SportDbProvider） |