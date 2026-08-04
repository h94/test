# 更新聯盟層級賠率閥值

## 1. 場景目的
提供管理後台「修改指定聯盟（以 `sitelid` 識別）的賠率監控閥值設定」。操作員可對特定資料源（`source`）與球種（`game_type`）的聯盟更新其玩法（`playmode`）閾值。異動會完整記錄至 changelog，並排入同步佇列供下游服務消費。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/oddthreshold/league/{sitelid}` | 整包覆蓋更新指定 `sitelid` 的聯盟層級賠率閥值 |

---

## 3. 流程總覽

1. 接收含 `sitelid`、`source`、`game_type` 與 `playmode` 設定的 PUT request
2. 解析 request body，驗證必要欄位與 JSON 結構
3. 判斷目標聯盟閥值設定是否已存在
4. 若不存在，回傳 404 Not Found
5. 讀取現行 `oddthreshold_league_setting` 紀錄作為變更前快照
6. 以 UPSERT 邏輯寫入新的 `playmode` 設定（覆蓋整個 JSON 欄位）
7. 將異動寫入 `threshold_changelog`（記錄 table、key、新舊值、操作者）
8. 向 `threshold_sync_pending` 寫入一筆 pending 同步任務
9. 必要時，發布 Kafka 訊息通知下游服務（需人工確認）
10. 回傳成功訊息，包含更新後的完整紀錄

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `Resources/OddThreshold.py` → `update_league` | 接收 PUT request，解構路徑參數 `sitelid` 與 body |
| 2 | Validator | `Schemas/OddThreshold.py` → `LeaguePlaymodePutBody` | 校驗 `source`、`game_type`、`playmode`、`operator_account` 型態與必填 |
| 3 | Service | `Service/OddThresholdService.py` → `update_league_setting` | 協調查詢、比對、寫入、changelog、同步任務 |
| 4 | Provider | `Provider/OddThresholdProvider.py` → `get_league_setting` | 依 `sitelid`、`source`、`game_type` 查詢現行設定；若無回傳 None |
| 5 | Provider | `Provider/OddThresholdProvider.py` → `upsert_league_setting` | 執行 PostgreSQL `INSERT ... ON CONFLICT ... DO UPDATE`，完整取代 `playmode` 欄位 |
| 6 | Provider | `Provider/ThresholdChangelogProvider.py` → `insert` | 寫入 `threshold_changelog`（`table_name`, `record_key`, `old_value`, `new_value`, `operator_account`） |
| 7 | Provider | `Provider/ThresholdSyncPendingProvider.py` → `enqueue` | 寫入 `threshold_sync_pending`（`table_name='oddthreshold_league_setting'`, `record_key`, `status='pending'`） |
| 8 | Controller | `Resources/OddThreshold.py` | 組裝並回傳 200 OK 與更新後的完整紀錄 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `oddthreshold_league_setting` | Read + UPSERT | 查詢現行設定並整包覆蓋 `playmode` |
| DB | `threshold_changelog` | Write | 記錄變更軌跡 |
| DB | `threshold_sync_pending` | Write | 排入同步佇列供下游消費 |
| Queue | Kafka topic（需人工確認） | Publish | 即時廣播閥值異動至 OddAlertService 等監控服務（需人工確認） |

---

## 6. 重要規則

- **權限限制**：無內建 RBAC 檢查；需由上游 Gateway 攔截（需人工確認）
- **欄位限制**：
  - `sitelid`、`source`、`game_type` 三者組合為複合主鍵，不可變更
  - `playmode` 為 JSONB，僅允許特定結構（詳見 `LeaguePlaymodePutBody` schema）
- **不可暴露資料**：不應在錯誤回應中洩漏 DB schema 或完整 stack trace
- **不可修改欄位**：`sitelid`、`source`、`game_type` 不可透過本 API 修改；`created_at` 僅在 INSERT 時設定
- **Transaction 規則**：未觀察到跨表 transaction；變更與 changelog 寫入未包在同一個 DB transaction 中（需人工確認）
- **Idempotency**：整包覆蓋，重複相同 request body 會得到相同結果，具備冪等性

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 目標聯盟閥值設定不存在 | 404 Not Found |
| request body 缺少必要欄位或型態錯誤 | 422 Validation Error |
| `playmode` JSON 結構不符合 schema | 422 Validation Error |
| DB 寫入失敗（連線逾時、死結） | 500 Internal Server Error，changelog 未寫入 |
| `threshold_sync_pending` 寫入失敗 | 500 Internal Server Error（需人工確認是否 rollback 閥值寫入） |
| Kafka publish 失敗 | 可能不回滾 DB 變更，導致資料不一致（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-01 | Unit Test | Provider `upsert_league_setting` 正常寫入 | 回傳 updated row |
| UT-02 | Unit Test | 不存在設定時呼叫 Service 層 | Service 拋出自訂 NotFound 例外 |
| IT-01 | Integration Test | 正常流程：PUT 合法 body | 200 OK，`oddthreshold_league_setting` 更新，changelog 新增 1 筆，sync_pending 新增 1 筆 |
| IT-02 | Integration Test | `playmode` 格式錯誤 | 422，DB 未變更 |
| PERM-01 | Permission Test | 無有效 JWT 或 API Key | 上游 Gateway 阻擋，本服務需確認 header 存在 |
| FLOW-01 | Flow Test | 連續兩次相同 PUT | 皆 200 OK，第二次 changelog 記錄相同新舊值或偵測無異動不寫入（需人工確認） |

---

## 9. 高風險區域

- **高風險 table**：`oddthreshold_league_setting`（直接影響監控邏輯）、`threshold_sync_pending`（資料同步中樞）
- **高風險 API**：`PUT /api/oddthreshold/league/{sitelid}`（無版本控制，直接覆蓋線上閥值）
- **跨服務資料同步**：依賴 `threshold_sync_pending` 與可能存在的 Kafka 機制觸發 OddAlertService 更新
- **Transaction**：閥值寫入、changelog 寫入、sync 任務寫入未觀察到 ACID 保護，可能產生部分失敗
- **Cache consistency**：若監控服務有自帶 cache，需確保 Kafka 或 sync 機制可靠送達
- **Queue retry**：`threshold_sync_pending` 需由排程或 worker 拉取重試
- **Idempotency**：整包覆蓋保證 API 層冪等，但 changelog 可能重複記錄相同內容（需人工確認）

---

## 10. 常見錯誤

- **新人容易犯錯**：誤以為可部分更新 `playmode` 內單一玩法，實為整包覆蓋
- **AI 容易誤解**：誤將 `sitelid` 當作可變更欄位，或試圖用 PATCH 語意實作
- **常見漏檢查項目**：
  - 未確認 `operator_account` 是否來自已驗證的 request context
  - 忘記檢查回傳的 `playmode` 是否為當初寫入的值（JSONB key order 可能不同）
- **常見錯誤流程**：
  - 直接在 DB 手動修改 `oddthreshold_league_setting`，導致 changelog 與 sync_pending 未產生，下游服務不同步

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `Resources/OddThreshold.py` → `PUT /api/oddthreshold/league/{sitelid}` |
| DB | `oddthreshold_league_setting` (migrations/001_create_core_tables.sql) |
| DB changelog | `threshold_changelog` (migrations/002_create_supplement_tables.sql) |
| DB sync | `threshold_sync_pending` (migrations/003_create_sync_tables.sql) |
| Code (Provider) | `Provider/OddThresholdProvider.py` → `get_league_setting`, `upsert_league_setting` |
| Code (Service) | `Service/OddThresholdService.py` → `update_league_setting` |
| Code (ChangeLog) | `Provider/ThresholdChangelogProvider.py` → `insert` |
| Code (Sync) | `Provider/ThresholdSyncPendingProvider.py` → `enqueue` |
| Schema | `Schemas/OddThreshold.py` → `LeaguePlaymodePutBody` |
| SQL | `INSERT ... ON CONFLICT (sitelid, source, game_type) DO UPDATE SET playmode = ...` |