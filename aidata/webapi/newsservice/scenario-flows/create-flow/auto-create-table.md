# 自動建立資料表

## 1. 場景目的

本場景描述系統管理員觸發 `POST /api/v1/system/autocreatetable`，系統根據前置設定（通常是 `gameType` 或站台代碼）在 Cassandra `news` keyspace 中動態建立缺失的 `sports_{gameType}` 或 `ainews_{site}` 變體表，確保表結構存在以接收後續新聞資料。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/system/autocreatetable` | 觸發自動建立所有需要的動態表（在 API Gateway 端完成驗證） |

---

## 3. 流程總覽

1. 系統管理員（或具備管理權限之服務）透過 API Gateway 呼叫 `POST /api/v1/system/autocreatetable`
2. API Gateway 驗證 JWT 且必須包含系統管理角色（authService 預先授權）
3. 請求轉送至 `newsservice`，由 `SystemController` 接收
4. Service 層逐一檢查所有預先定義的動態表名（例如 `sports_{gameType}`、`ainews_gs`、`ainews_lt`）
5. 對每個表名執行 Cassandra `CREATE TABLE IF NOT EXISTS`（或等價的 Schema 同步邏輯）
6. 若表已存在則忽略；若不存在則依 Schema 定義建立（來自 `db/news.md` 或服務內部 Schema Registry）
7. 全部完成後回傳 `200 OK`

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SystemController.AutoCreateTable` | 接收 POST 請求，呼叫 Service |
| 2 | Service | `ITableManagementService.AutoCreateTablesAsync` | 負責迭代建表清單與排程建立 |
| 3 | Provider | `CassandraSchemaProvider`（或類似名稱） | 組裝 CQL `CREATE TABLE IF NOT EXISTS` 語句 |
| 4 | Data Access | ECService / Cassandra Driver | 對 Cassandra 執行 DDL |

> **需人工確認**：實際 Service/Provider 名稱以 codebase 為準。若無獨立 Service，可能直接在 Controller 內執行邏輯。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `news` keyspace | Exec DDL | 建立 `sports_{gameType}`、`ainews_gs`、`ainews_lt` 等動態表 |
| Cache | Redis | – | 本場景未使用 |
| Queue | Kafka / Queue | – | 本場景未使用 |

---

## 6. 重要規則

- **權限限制**：僅系統管理員可呼叫，須通過 API Gateway JWT 驗證
- **欄位限制**：建表時必須確保欄位順序、型別、PRIMARY KEY 與 Cassandra schema 定義一致
- **不可暴露資料**：此 API 僅回傳成功或失敗，不回傳任何欄位內容
- **TTL 規則**：不適用（無資料操作）
- **Transaction 規則**：無跨表 transaction；DDL 操作各自獨立
- **Retry 規則**：若 Cassandra 暫時不可用，API 會拋出異常；由呼叫方（管理員或排程）決定是否重試（**需人工確認**：無內建 Retry 邏輯）
- **狀態值限制**：不適用
- **不可修改欄位**：建表後不可透過此流程修改表結構；如需 ALTER 應另由 migration script 處理

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未攜帶有效 JWT | API Gateway 拒絕請求（401/403） |
| Cassandra 連線失敗或 timeout | API 回傳 500，錯誤訊息由全域例外處理器包裝 |
| 建表語法錯誤（如欄位型別不符） | Cassandra 驅動擲回例外，API 回傳 500 |
| 動態表名包含非法字元 | Service 層應先驗證表名格式，拒絕非法名稱 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| AT-01 | Permission Test | 未帶 JWT 呼叫 API | 被 API Gateway 阻擋，回傳 401 |
| AT-02 | Permission Test | 使用非管理員 JWT 呼叫 | 收到 403（由 Gateway 或 Controller 驗證） |
| AT-03 | Integration Test | Cassandra 正常，所有表不存在 | 成功建表，回傳 200；可再次查詢 Cassandra 確認 |
| AT-04 | Integration Test | 重複呼叫，所有表已存在 | Cassandra 因 `IF NOT EXISTS` 忽略建表，回傳 200 |
| AT-05 | Flow Test | Cassandra 異常中斷 | 回傳 500，記錄錯誤 log |

---

## 9. 高風險區域

- **高風險 table**：`sports_{*}`、`ainews_gs`、`ainews_lt`（DDL 操作若失敗可能影響後續寫入）
- **高風險 API**：`POST /api/v1/system/autocreatetable`（全域 Schema 變更，需嚴格權限控管）
- **跨服務資料同步**：無
- **Transaction**：無
- **Cache consistency**：無
- **Queue retry**：無
- **Idempotency**：具備（使用 `IF NOT EXISTS`），重複呼叫不產生錯誤

---

## 10. 常見錯誤

- ❌ 新人誤將「動態表名」當作 API 輸入參數 → ✅ `autocreatetable` 一般無需 request body，系統自行判斷應建立哪些表
- ❌ 手動在 Cassandra 建立表卻遺漏欄位或主鍵 → ✅ 一律透過本 API 觸發，確保全域一致
- ❌ AI 誤解 `gameType` 可由任意字串組合 → ✅ `gameType` 必須為預先定義的合法球種代碼（如 SC, BK, BS），否則後續 `sports_{gameType}` 寫入流程將失敗
- ❌ 認為建立失敗可手動補救 → ✅ 應查閱 log 確認 Cassandra 狀態後重新呼叫 API

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI — `/api/v1/system/autocreatetable`（需要驗證） |
| DB | `db/news.md` — Cassandra keyspace `news`（包含 `sports_*`） |
| Service Detail | `newsservice-detail.md` — 確認 `sports_{gameType}` 為動態表，`addtime` 由服務內部填入 |
| 權限 | `newsservice-detail.md` — 本服務不負責用戶認證與授權，由 API Gateway 預先鑑權 |
| Redis | `newsservice-detail.md` — 本服務未使用 Redis |
| Code | `news-detail.md` — 動態表名需由調用方明確指定 gameType，無默認值 |

> **需人工確認**：`autocreatetable` API 的實際實作細節（Controller/Service 名稱、建表表名清單來源、是否使用 `CREATE TABLE IF NOT EXISTS`）需透過原始碼確認。若 Info insufficient，建議直接檢視 `SystemController` 或 `TableManagementService`。