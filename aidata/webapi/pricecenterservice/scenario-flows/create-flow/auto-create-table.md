# 場景：自動建立資料表

## 1. 場景目的

提供系統管理工具，根據內部配置自動在 Cassandra 與 MySQL 中建立服務運行所需的資料庫表格結構，用於服務初始化、新品牌上線或資料表異常修復。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/system/autocreatetable` | 自動建立 DB Table |

- 需要驗證：✅
- 驗證框架：ECFramework.ECService（內部統一驗證框架）
- 請求格式：無 request body（系統內部觸發）

---

## 3. 流程總覽

1. 接收 POST request，攜帶內部 JWT Token
2. ECFramework.ECService 驗證 Token 權限（管理員或系統層級權限）  
3. Controller 呼叫 AutoCreateTable Service
4. Service 根據配置，為每個品牌（brand）建立或確保 Cassandra Table 存在
5. Service 為 Sport DB 建立或確保必要的 MySQL Table 存在
6. 完成後回傳成功狀態

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | SystemController.AutoCreateTable | 接收 request，轉發至 Service |
| 2 | Service | AutoCreateTableService | 根據配置列表，逐一調用 Cassandra 與 MySQL 初始化 |
| 3 | Provider | CassandraProvider.CreateTableIfNotExists | 對每個品牌執行 `CREATE TABLE IF NOT EXISTS pricecenter."accounts_{brand}" (...)` |
| 4 | Provider | MySqlProvider.CreateTableIfNotExists | 對 Sport DB 執行 `CREATE TABLE IF NOT EXISTS sport.League (...)` / `sport.Team (...)` |

> ⚠️ 由於缺乏對應 Controller/Service 程式碼分析覆蓋，上述流程為架構推測，細節需人工確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra pricecenter keyspace | DDL (CREATE TABLE IF NOT EXISTS) | 建立或確保 `accounts_{brand}` 系列表格存在 |
| DB | MySQL Sport DB | DDL (CREATE TABLE IF NOT EXISTS) | 建立或確保 `League`、`Team` 表格存在 |
| Redis | N/A | N/A | 本場景未使用 |
| Queue | N/A | N/A | 本場景未使用 |

---

## 6. 重要規則

- **權限限制**：
  - 僅內部管理服務（具備系統層級 JWT Token）可呼叫（README 標記「需要驗證」）
  - 需人工確認具體 Token scope / role 要求

- **不可修改欄位**：
  - 表格結構由 Schema 定義決定，API 不提供動態變更結構的參數
  - 不允許變更現有表格的欄位定義（僅 `CREATE TABLE IF NOT EXISTS`）

- **冪等性規則**：
  - 使用 `IF NOT EXISTS` 語法，重複呼叫不會造成錯誤或資料遺失
  - 需人工確認程式碼中是否正確使用此語法

- **錯誤處理規則**：
  - 若任一 Table 建立失敗，需記錄錯誤日誌但需人工確認是否影響其他表格建立（全部成功或部分成功）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 驗證失敗（無效 Token） | 回傳 401 Unauthorized |
| 權限不足（非管理員 Token） | 回傳 403 Forbidden |
| Cassandra 連線失敗 | 需人工確認：回傳 500 錯誤或部分成功 |
| MySQL 連線失敗 | 需人工確認：回傳 500 錯誤或部分成功 |
| 表格已存在 | 無動作，回傳成功（冪等操作） |
| Schema 定義錯誤 | 需人工確認：回傳 500 或記錄錯誤 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| ACT-01 | API Test | 使用合法管理員 Token 呼叫 | 回傳 200，表格建立成功 |
| ACT-02 | Permission Test | 使用一般使用者 Token 呼叫 | 回傳 403 Forbidden |
| ACT-03 | Permission Test | 不帶 Token 呼叫 | 回傳 401 Unauthorized |
| ACT-04 | Flow Test | 重複呼叫（表格已存在） | 回傳 200，無錯誤（冪等性） |
| ACT-05 | Flow Test | 新品牌加入配置後呼叫 | 自動建立對應 `accounts_{新品牌}` Table |
| ACT-06 | Error Test | Cassandra 無法連線 | 需人工確認：回傳 500 或部分成功 |
| ACT-07 | Error Test | MySQL 無法連線 | 需人工確認：回傳 500 或部分成功 |

---

## 9. 高風險區域

- **高風險 API**：
  - `POST /api/v1/system/autocreatetable` 直接操作 DDL，若權限控管不當可能被濫用刪除表格（需確認程式碼中無 DROP 語句）
  - 需人工確認：API 是否透過對外 API Gateway 暴露，或僅限內部網路調用

- **跨服務資料同步**：
  - 無，本場景為一次性初始化操作

- **Idempotency**：
  - 必須保證冪等，重複呼叫不應造成錯誤或重複建立（依賴 `IF NOT EXISTS`）
  - 需人工確認：程式碼中是否有其他非冪等邏輯（如建立 Index 或 Materialized View）

---

## 10. 常見錯誤

- ❌ 新人容易誤解為此 API 會自動修復資料表結構變更 → 實際上僅執行 `CREATE TABLE IF NOT EXISTS`，不處理結構遷移（migration）
- ❌ AI 容易誤解為此 API 可接受 request body 指定表格結構 → 表格結構由內部 Schema 定義或程式碼硬編碼，非由 API 參數決定
- ❌ 常見漏檢查項目：未驗證 Cassandra / MySQL 連線狀態就直接執行 DDL，導致部分表格建立失敗卻未回報錯誤
- ❌ 常見錯誤流程：在生產環境手動呼叫此 API 後未驗證表格結構是否正確，導致後續業務流程讀寫失敗

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/system/autocreatetable` |
| README | 系統工具 API 列表、技術棧（Cassandra / MySQL） |
| DB | Cassandra pricecenter keyspace（`accounts_*` 系列） |
| DB | MySQL Sport（`League`、`Team`） |
| 驗證 | ECFramework.ECService（內部統一驗證框架） |
| Code | ❌ 缺乏 Controller/Service 程式碼分析覆蓋，需人工確認 |
| Code | ❌ 缺乏具體 DDL 語句實作證據，需人工確認 |

## 建議新增

- **建議新增文件**：
  - `autocreatetable` 的具體 DDL 語句定義文件（說明各表格欄位結構與 Index 設定）
  - 內部管理 API 的權限模型文件（說明哪些角色/service 可呼叫此 API）

- **建議新增規則**：
  - 本 API 僅限內部服務網路調用，不可透過對外 API Gateway 暴露
  - 必須記錄每次呼叫的審計日誌（誰、何時、建立了哪些表格）

- **建議新增測試**：
  - Cassandra/MySQL 部分連線失敗的異常測試（驗證錯誤處理與日誌記錄）
  - Cassandra/MySQL 表格結構與 Schema 定義的一致性驗證 Test（確保 DDL 語句正確）