# 建立遊戲層級賠率閥值

## 1. 場景目的

針對特定賽事（`sitegid`）新增或更新賠率閥值的遊戲層級監控玩法與參數。此設定僅影響指定賽事，優先級高於聯盟層級與球種層級設定。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/oddthreshold/game/{game_type}/{sitegid}` | 新增或更新指定賽事的賠率閥值設定 |

- **需人工確認**：OpenAPI Schema `GamePlaymodeBody` 的完整欄位定義未提供，需查閱 `Resources/` 下的 Pydantic model 或轉接層（Transfer）以取得完整 request body 欄位。

---

## 3. 流程總覽

1. 接收 HTTP POST request，路徑攜帶 `game_type`（球種）與 `sitegid`（賽事 ID）。
2. 由 Resource / Controller 層解析 request body，取得 `source`、`gdate`、`sitelid`、`playmode` 與 `operator_account`。
3. 調用 Service 層執行建立或更新邏輯（Upsert）。
4. Service 調用 Provider 層，以 `sitegid + source` 為複合鍵對 `oddthreshold_game_setting` 資料表執行 `INSERT ... ON CONFLICT ... DO UPDATE`（Upsert）。
5. 同一資料庫 Transaction 內，將此次異動寫入 `threshold_changelog` 資料表。
6. 同一 Transaction 內，將同步任務寫入 `threshold_sync_pending` 資料表，供下游消費者同步閥值變更。
7. Transaction 成功提交後回傳成功回應。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller（Resource） | `oddthreshold.py`（推測） | 解析路徑參數 `game_type`、`sitegid` 與 request body |
| 2 | Service | `OddThresholdService`（推測） | 協調 Upsert、寫入 Changelog、排入同步佇列 |
| 3 | Provider | `OddThresholdGameSettingProvider` | 對 `oddthreshold_game_setting` 執行 `INSERT ... ON CONFLICT (sitegid, source) DO UPDATE` |
| 4 | Provider | `ThresholdChangelogProvider` | 對 `threshold_changelog` 執行 `INSERT`，記錄變更前後值 |
| 5 | Provider | `ThresholdSyncPendingProvider` | 對 `threshold_sync_pending` 執行 `INSERT`，status 為 `pending` |

- **Evidence**：
  - API: `POST /api/oddthreshold/game/{game_type}/{sitegid}`（OpenAPI）
  - DB: `oddthreshold_game_setting`（db-usage / phase1 table list）
  - Code: `oddthreshold_setting.py:upsert`（phase1 semantics）
  - Code: `threshold_changelog.py:insert`（phase1 semantics）
  - Code: `threshold_sync_pending.py:enqueue`（phase1 semantics）

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `oddthreshold_game_setting` | Write（Upsert） | 寫入或更新遊戲層級賠率閥值 |
| DB | `threshold_changelog` | Write（Insert） | 記錄閥值變更軌跡 |
| DB | `threshold_sync_pending` | Write（Insert） | 排入同步佇列，供下游系統（如 OddAlertService）同步閥值變更 |
| Redis | - | 無直接操作 | 此場景未使用 Redis |
| Kafka | - | 無直接操作 | 同步機制使用 DB 佇列（`threshold_sync_pending`），非 Kafka |

---

## 6. 重要規則

- **權限限制**：需人工確認，OpenAPI 未定義此 API 的權限守衛（Guard）機制。
- **欄位限制**：
  - `playmode` 欄位為 JSONB，由前端傳入完整的遊戲層級監控玩法設定，**直接覆蓋**原有設定。
  - `operator_account` 為必填，寫入 `oddthreshold_game_setting` 與 `threshold_changelog`。
- **不可暴露資料**：無。
- **TTL 規則**：`threshold_sync_pending` 中 status 為 `done` 的記錄會由每日排程清理（README）。
- **Transaction 規則**：對 `oddthreshold_game_setting`、`threshold_changelog`、`threshold_sync_pending` 的操作必須在同一個 DB Transaction 內完成。
- **Retry 規則**：此 API 為同步寫入，無自動重試；下游同步由 `threshold_sync_pending` 的消費者負責重試。
- **狀態值限制**：`threshold_sync_pending.status` 初始值固定為 `pending`。
- **不可修改欄位**：`created_at` 由資料庫自動產生，不可由 API 傳入。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| request body 格式錯誤（缺少必填欄位） | HTTP 422 Unprocessable Entity，由 FastAPI 自動驗證 |
| `game_type` 不存在於 `monitored_play_modes` | 不影響寫入，但需人工確認 Service 層是否有驗證邏輯 |
| `source` 為空或無效 | 需人工確認是否有 source 驗證規則 |
| DB 寫入失敗（`oddthreshold_game_setting`） | Transaction 回滾，HTTP 500 Internal Server Error |
| `threshold_sync_pending` 寫入失敗 | Transaction 回滾，HTTP 500 Internal Server Error |
| 同步消費者未啟動或延遲 | 閥值變更無法即時生效，`threshold_sync_pending` 堆積 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 正常新增遊戲層級閥值設定，傳入完整 `playmode` | HTTP 200，DB 寫入正確，changelog 與 sync_pending 各新增一筆記錄 |
| TC02 | API Test | 對同一 `sitegid + source` 再次呼叫，更新 `playmode` | HTTP 200，DB 更新，changelog 記錄新舊值，sync_pending 新增一筆 |
| TC03 | API Test | 傳入不完整的 `playmode`（如缺少特定玩法） | 需人工確認 Service 層是否有驗證，若無則直接寫入 |
| TC04 | Flow Test | 驗證 Transaction 完整性（模擬 DB 異常） | `oddthreshold_game_setting` 未變更，changelog 與 sync_pending 無新記錄 |
| TC05 | Integration Test | 排程執行 `purge_done_older_than` | status 為 `done` 且超過保留期限的記錄被刪除 |

---

## 9. 高風險區域

- **高風險 table**：`oddthreshold_game_setting`，遊戲層級閥值設定直接影響監控準確性，錯誤的 `playmode` 可能導致漏報或誤報警示。
- **高風險 API**：`POST /api/oddthreshold/game/{game_type}/{sitegid}`，無明確的輸入驗證規則，需確認 Service 層是否有對 `playmode` JSON 結構的 schema 校驗。
- **跨服務資料同步**：依賴 `threshold_sync_pending` DB 佇列，若消費者延遲或故障，閥值變更不會生效。
- **Transaction**：涵蓋三張表的寫入，Transaction 失敗需確保全部回滾。
- **Cache consistency**：此場景未使用 Redis，無快取一致性風險。
- **Queue retry**：`threshold_sync_pending` 的消費者實作需支援重試，否則可能遺失同步。
- **Idempotency**：API 本身為 Upsert，具備冪等性；但 `threshold_sync_pending` 每次呼叫皆新增一筆，消費者需能處理重複的同步任務。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 誤解 `playmode` 為 Partial Update，實際上是**完整覆蓋**（整包取代）。
  - 忘記 `operator_account` 為必填，導致寫入失敗（需人工確認 Service 層驗證）。
- **AI 容易誤解**：
  - 將此 API 理解為 RESTful 的 PUT（replace），但實際上是 POST + Upsert。
  - 誤以為有使用 Redis 快取閥值設定，實際上閥值設定直接讀取 DB。
- **常見漏檢查項目**：
  - 未檢查 `source` 是否存在於 `source_type` 資料表。
  - 未檢查 `sitelid` 是否存在於對應的聯盟設定。
  - 未驗證 `playmode` 內的每個玩法是否屬於 `monitored_play_modes` 定義的合法玩法。
- **常見錯誤流程**：
  - 在 Transaction 外寫入 `threshold_changelog` 或 `threshold_sync_pending`，導致資料不一致。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI: `POST /api/oddthreshold/game/{game_type}/{sitegid}` |
| DB | `oddthreshold_game_setting` table schema（migrations/001_create_core_tables.sql） |
| DB | `threshold_changelog` table schema（migrations/002_create_supplement_tables.sql） |
| DB | `threshold_sync_pending` table schema（migrations/003_create_sync_tables.sql） |
| Code | `oddthreshold_setting.py:upsert`（phase1 source semantics） |
| Code | `threshold_changelog.py:insert`（phase1 source semantics） |
| Code | `threshold_sync_pending.py:enqueue`（phase1 source semantics） |
| README | 閥值異動皆寫入 changelog，並將變更排入同步佇列供下游消費 |