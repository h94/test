# 建立聯盟層級賠率閥值

## 1. 場景目的
管理人員針對特定聯盟（由 `sitelid` 與 `source` 定義）新增或更新賠率閥值設定（`playmode` JSON），並自動產生變更記錄與觸發同步佇列，確保下游監控服務能即時套用新規則。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/alertbackendservice/api/oddthreshold/league` | **需人工確認**，推測路由為 `/api/oddthreshold/league`，OpenAPI 截斷未完整提供。 |

此 API 預期接受 `sitelid`、`source`、`game_type` 以及 `playmode`（JSON）等參數，實際規格依 `Resources/` 目錄下的路由定義為準。

---

## 3. 流程總覽

1. 接收建立／更新請求，包含 `sitelid`、`source`、`game_type`、`playmode` 與 `operator_account`。
2. 驗證 `game_type` 與 `source` 是否合法（可能查詢 `source_type` 表）。
3. 調用 Service 層，執行 DB upsert 至 `oddthreshold_league_setting`。
4. 比較新舊 `playmode` 內容，寫入 `threshold_changelog` 記錄差異。
5. 寫入一筆 `pending` 狀態記錄至 `threshold_sync_pending`，供排程 Worker 或下游服務消費。
6. 回傳成功訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `OddThresholdController` (推測) | 接收請求並轉交 Service |
| 2 | Service | `OddThresholdService.upsert_league()` | 組合驗證、呼叫 Provider、寫 changelog 與 sync 佇列 |
| 3 | Provider | `OddThresholdProvider.upsert()` | 執行 `INSERT ... ON CONFLICT (sitelid,source,game_type) DO UPDATE` |
| 4 | Provider | `ThresholdChangelogProvider.insert()` | 寫入變更記錄 |
| 5 | Provider | `ThresholdSyncPendingProvider.enqueue()` | 寫入同步待處理記錄 |
| 6 | (背景) | Worker 或排程器 | 定時掃描 `threshold_sync_pending` 並推送至 Kafka 或其他同步機制 | **需人工確認** 確切同步實作方式 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `oddthreshold_league_setting` | Write (upsert) | 儲存或更新聯盟層級的賠率閥值設定 |
| DB | `threshold_changelog` | Write | 記錄此次異動的舊值、新值與操作者，供稽核 |
| DB | `threshold_sync_pending` | Write | 記錄待同步任務，狀態為 `pending`，供下游消費 |
| Kafka (可能) | `topic-threshold-sync`? | Publish | **需人工確認**：背景 Worker 可能將同步記錄發佈至 Kafka，觸發相關服務更新快取 |

---

## 6. 重要規則

- **唯一性約束**：`oddthreshold_league_setting` 的 primary key 為 (`sitelid`, `source`, `game_type`)，重複寫入時會更新既有記錄。
- **playmode 格式**：`playmode` 必須為合法的 JSON 物件，結構須符合系統定義（如各玩法對應的閥值參數）。**需人工確認** 實際 Schema。
- **操作者記錄**：`operator_account` 為必填，會寫入 `oddthreshold_league_setting.operator_account`、`threshold_changelog.operator_account`。
- **changelog 規則**：若為新建則 `old_value` 為 `null`；若更新則比對新舊並寫入差異。
- **同步規則**：每次 upsert 後必定寫入一筆 `threshold_sync_pending`，狀態 `pending`，`record_key` 可能為 `sitelid:source:game_type` 的字串組合。
- **權限限制**：無額外權限檢查，信任 API 層級已驗證 operator_account。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求缺少必填欄位 (`sitelid`、`source`、`game_type`、`playmode`) | 回傳 422 Validation Error |
| game_type 不在允許清單中 | 回傳 400 Bad Request (可能查詢 `source_type` 或其他設定) |
| source 不存在於 `source_type` 表中 | 回傳 400 Bad Request |
| playmode JSON 格式錯誤或不符合規範 | 回傳 422 / 400 |
| DB upsert 失敗 (連線超時或約束衝突以外的錯誤) | 回傳 500 Internal Server Error，不從重試（由客戶端決定是否重試） |
| changelog 寫入失敗 | 回傳 500，並 rollback 整個交易，避免主資料與 log 不一致（需確認是否使用 DB transaction） |
| threshold_sync_pending 寫入失敗 | 同上，應 rollback 全部操作 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | API Test | 使用合法參數首次建立 | 200，記錄寫入 `oddthreshold_league_setting`，changelog 及 sync_pending 各新增一筆 |
| T02 | API Test | 相同 key 再次呼叫但 `playmode` 有變動 | 200，`oddthreshold_league_setting` 更新，changelog 記錄新舊值差異 |
| T03 | Integration Test | 確認 `threshold_sync_pending` 狀態 | 新增記錄 `status = 'pending'`，`table_name = 'oddthreshold_league_setting'` |
| T04 | Permission Test | 使用無效或空的 operator_account | 視規格，可能 422，或仍允許但需確保不影響下游 |
| T05 | API Test | 使用不存在的 `source` | 400 Bad Request |
| T06 | Error Test | 模擬 DB 連線失敗 | 500，且無任何髒資料殘留（transaction 回滾） |
| T07 | Flow Test | 背景 Worker 是否成功將 sync_pending 標記為 `done` 並推送 Kafka | **需人工確認** 完整同步流程 |

---

## 9. 高風險區域

- **高風險 table**：`oddthreshold_league_setting`（核心設定）、`threshold_changelog`、`threshold_sync_pending`
- **跨服務資料同步**：同步佇列的消費機制若失效，監控服務將使用舊閥值，造成警示誤判
- **Transaction**：寫入主要設定、changelog 與 sync_pending 必須包在同一個 DB transaction 內，否則可能產生孤立的 sync 記錄
- **Cache consistency**：下游服務可能快取閥值設定，同步延遲會導致快取過期，需確認同步後的快取刷新策略
- **Queue retry**：若背景 Worker 推送 Kafka 失敗，sync_pending 記錄應有重試或告警機制，否則記錄永久 `pending`

---

## 10. 常見錯誤

- **新人容易犯錯**：忽略 `source` 的正確性，直接使用任意字串，導致與 `source_type` 表對不上。
- **AI 容易誤解**：可能僅生成直接寫 `oddthreshold_league_setting` 的程式碼，忘了寫入 changelog 和 sync_pending。
- **常見漏檢查項目**：未確認 `playmode` 的 JSON 結構是否完全符合預定義的 Key 與 Value 型別。
- **常見錯誤流程**：沒有包在 transaction 內，若 changelog 寫入失敗，主設定仍被更新，造成記錄缺失。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | 推測來自 `oddthreshold_setting.py` 的 router 與 `GamePlaymodeBody` schema （OpenAPI 未完整提供） |
| DB | `oddthreshold_league_setting` (migrations/001_create_core_tables.sql) |
| Code | `oddthreshold_setting.py:upsert` (phase1 code semantics) |
| SQL | `INSERT ... ON CONFLICT (sitelid, source, game_type) DO UPDATE` (由 upsert 推測) |
| Changelog | `threshold_changelog` table (migrations/002_create_supplement_tables.sql) |
| Sync | `threshold_sync_pending` table (migrations/003_create_sync_tables.sql) |