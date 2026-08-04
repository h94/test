# 批次更新 Bet365 頁面排程

## 1. 場景目的

管理員針對特定頁面類型（`pagetype`）進行批次排程更新，以控制 Bet365 爬蟲對該類型下所有頁面的抓取行為（如排程時間、頻率）。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/bet365/pages/{pagetype}` | 批次更新指定類型下所有頁面的排程 |

---

## 3. 流程總覽

1. 管理員透過管理後台觸發批次更新操作。
2. 請求經由 `ECFramework.ECService` 驗證，確保操作者具備管理權限。
3. `Bet365Controller` 接收請求，取得路徑參數 `pagetype` 與請求主體 (Body) 的排程設定。
4. Controller 將 `pagetype` 和排程設定傳遞給對應的 Service 層。
5. Service 層依據 `pagetype` 查詢所有符合條件的目標頁面，此步驟可能涉及：
    - 讀取 Cassandra `pricecenter` keyspace 中的相關表格（如 `machines` 或特定設定表）以獲取爬蟲頁面列表。**（需人工確認讀取的具體 Table）**
    - 或從另一個組態服務／資料表獲取頁面列表。**（需人工確認）**
6. Service 層遍歷頁面列表，為每個頁面更新排程設定。
7. 更新操作寫入負責儲存 Bet365 排程設定的資料庫。**（需人工確認寫入的具體 Table，可能為 MySQL 或 Cassandra 中的特定組態表）**
8. 更新成功後，回傳操作結果給前端。
9. 相關的爬蟲機器 (Crawler) 应在下次心跳回報或重新載入組態時，讀取到最新的排程設定。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `Bet365Controller` | 接收 `POST` 請求與路徑參數 `pagetype`，驗證請求主體 |
| 2 | Controller | `Bet365Controller` | 呼叫 `IBet365Service` 進行批次更新 |
| 3 | Service | `Bet365Service` | 接收 `pagetype` 和排程設定，查詢所有符合該類型 (`pagetype`) 的頁面列表 |
| 4 | Service | `Bet365Service` | 迴圈處理每個頁面，可能透過 `IProvider` 更新單一頁面的排程，或直接操作資料存取層 |
| 5 | Provider | **需人工確認** | 實際對資料庫進行寫入，更新該頁面的排程資訊 |
| 6 | Provider | **需人工確認** | 寫入成功後回傳，Service 層匯總所有操作結果 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | **需人工確認** (MySQL / Cassandra) | Read / Write | 查詢指定類型的爬蟲頁面列表、更新特定頁面的排程設定。 |
| DB | `pricecenter.machines` 或 `accounts_*` | Read | **可能**用於驗證爬蟲機器或帳號狀態，以確保排程更新可被執行。**（需人工確認）** |

**注意**：
- 根據現有文件，`pricecentermanage` 在 `pricecenter` keyspace 中具備讀寫權限，但具體寫入哪張表來控制 Bet365 排程，在提供的資料中**不明確**，需人工確認。
- 未發現此流程使用 Redis 或 Kafka 的證據。Bet365 爬蟲的配置同步可能透過其心跳機制 (`POST /api/v1/system/machines/crawler`) 被動觸發讀取，或由管理後台主動推送指令。**（需人工確認）**

---

## 6. 重要規則

- **權限限制**：必須通過管理後台 (ECFramework.ECService) 的驗證，僅限授權管理員操作。
- **欄位限制**：請求主體中的排程設定（如時間、頻率）必須進行格式與合理性校驗。
- **不可暴露資料**：`pricecenter.accounts_*.password` 等敏感欄位絕不可在此流程中回傳。
- **狀態值限制**：進行更新時，應確保目標爬蟲頁面或帳號處於可被更新的狀態（例如 `enabled=1`）。**（需人工確認）**
- **不可修改欄位**：`pricecenter.accounts_*.account` 等主鍵不可修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `pagetype` 不存在或無效 | API 應回傳 400 Bad Request 或特定錯誤代碼，提示頁面類型無效。 |
| 請求主體的排程格式錯誤 | API 應回傳 400 Bad Request，提示格式錯誤。 |
| 權限不足 | API 應回傳 401 Unauthorized 或 403 Forbidden。 |
| 目標頁面列表為空 (該類型下無頁面) | API 應回傳成功 (200 OK)，但提示無需更新的頁面。 |
| 更新單一頁面時發生資料庫錯誤 | 記錄錯誤日誌，並回報給管理員；流程可設計為全部成功或全部失敗 (Transaction) 或部分成功。**（需人工確認）** |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-B365-01 | API Test | 以有效的 `pagetype` 和正確的排程設定呼叫 API | 回傳 200 OK，排程設定被正確更新 |
| UT-B365-02 | API Test | 以無效的 `pagetype` 呼叫 API | 回傳 400 Bad Request |
| UT-B365-03 | Permission Test | 以未授權的 token 呼叫 API | 回傳 401 或 403 |
| UT-B365-04 | Flow Test | 更新一個包含多個頁面的 `pagetype` | 驗證該類型下所有頁面排程皆被更新 |

---

## 9. 高風險區域

- **高風險 Table**：任何用來儲存爬蟲排程設定的資料表，錯誤的寫入可能導致爬蟲停止運作或頻率異常，影響數據時效性。
- **高風險 API**：`POST /api/v1/bet365/pages/{pagetype}` 和 `POST /api/v1/bet365/page/{pagename}`，錯誤操作將直接影響線上爬蟲系統。
- **跨服務資料同步**：管理後台更新排程後，爬蟲機器何時能感知到變更是一個關鍵點。依賴排程或心跳間隔可能導致延遲，需要確認同步機制。

---

## 10. 常見錯誤

- ❌ **在沒有充分驗證的情況下，直接對整個 `pagetype` 執行批次更新**，可能因參數錯誤導致大規模排程異常。
- ❌ **忘記 `pagetype` 的命名規則**，使用了錯誤的大小寫或格式。
- ❌ **忽略了爬蟲帳號的 `enabled` 狀態**，為已停用的帳號更新了排程，可能引發後續錯誤。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/bet365/pages/{pagetype}` (from README & OpenAPI) |
| DB | `pricecenter.machines`, `pricecenter.accounts_*` (from README & db-detail; used for crawler management context) |
| Code | `Bet365Controller` (as per README context, needs verification in actual codebase) |
| Code | `Bet365Service` (as per README context, needs verification in actual codebase) |