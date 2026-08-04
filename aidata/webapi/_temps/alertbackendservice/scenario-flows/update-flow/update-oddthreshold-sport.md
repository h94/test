# 更新運動層級賠率閥值

## 1. 場景目的
管理者設定或調整特定球種（game_type）在運動層級的賠率監控閥值，使系統能依據新閥值對該球種的所有賽事賠率進行異常偵測。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/oddthreshold/sport/{game_type}` | 更新指定球種的運動層級賠率閥值設定（整包覆蓋）。|

> 需人工確認：OpenAPI 片段未包含此端點定義，但符合 `oddthreshold_setting` 模組的路由慣例（參考 `oddthreshold_setting.py:upsert`）。

---

## 3. 流程總覽

1. 接收含 `game_type` 路徑參數與 `playmode` 設定的請求。
2. 驗證操作者帳號（`operator_account`）是否具備管理權限。
3. 讀取 `oddthreshold_sport_setting` 表的現有記錄（若有）。
4. 執行 UPSERT 將新的 `playmode` 設定寫入 `oddthreshold_sport_setting`。
5. 將變更新舊值寫入 `threshold_changelog` 稽核表。
6. 將異動紀錄加入 `threshold_sync_pending` 同步佇列。
7. 回傳更新後的設定內容。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `OddThresholdSportResource.update` | 解析路徑參數 `game_type` 與 request body，呼叫 Service。|
| 2 | Service | `OddThresholdService.update_sport` | 驗證 `playmode` 結構，呼叫 Provider 進行 DB 操作。|
| 3 | Provider | `OddThresholdSportProvider.upsert` | 執行 UPSERT SQL（`INSERT ... ON CONFLICT DO UPDATE`），並將異動寫入 changelog 與 sync。|
| 4 | Provider | `ThresholdChangelogProvider.insert` | 寫入 `threshold_changelog`，記錄舊值（若更新）或 null（若新建）。|
| 5 | Provider | `ThresholdSyncPendingProvider.enqueue` | 寫入 `threshold_sync_pending`，狀態 `pending`，供下游同步服務消費。|

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `oddthreshold_sport_setting` | Upsert (INSERT/UPDATE) | 儲存運動層級閥值設定。以 `game_type` 為主鍵。 |
| DB | `threshold_changelog` | Insert | 稽核記錄，存新舊值供追蹤。 |
| DB | `threshold_sync_pending` | Insert | 將異動排入同步佇列，等待下游處理。 |
| Redis | 無 | – | 目前無直接使用 Redis 快取。 |
| Kafka | 無 | – | 同步機制使用 DB 佇列，未實作 Kafka 發佈，需人工確認跨服務同步方式。|

---

## 6. 重要規則

- **權限限制**：必須提供 `operator_account`，由後端或上游 Gateway 驗證登入狀態及管理權限（需人工確認具體驗證方式）。
- **欄位限制**：`playmode` 為 JSONB，需符合預先定義的玩法鍵值結構（如 `{"1x2": 0.03}`），不可為空物件。
- **不可修改欄位**：`game_type` 為路徑參數與主鍵，不可於 request body 中變更；`created_at`、`updated_at` 由資料庫自動管理。
- **Transaction 規則**：同一請求內的 `oddthreshold_sport_setting` 更新、changelog 寫入、sync 寫入應在同一 DB transaction 中完成，確保原子性。
- **狀態值限制**：無特定狀態欄位。
- **TTL 規則**：`threshold_sync_pending` 中已完成的同步記錄會由排程定期清理（每日清理過期資料，見 README）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未提供 `operator_account` | 回傳 400 或 401（需人工確認）。 |
| `playmode` 格式錯誤（非合法 JSON 或結構不符） | 回傳 422 Validation Error。 |
| DB 寫入失敗（如連線超時） | 回傳 500，並記錄錯誤日誌。 |
| changelog 或 sync pending 寫入失敗 | 根據 transaction 規則，應一併回滾 `oddthreshold_sport_setting` 的異動，回傳 500。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| IT-01 | Integration | 更新已存在的 `game_type` 閥值，提供合法 `playmode` 與 `operator_account` | 回傳 200，DB 記錄更新，changelog 新增一筆 old_value 非 null 的記錄，sync pending 新增一筆 pending 記錄。 |
| IT-02 | Integration | 對不存在的 `game_type` 呼叫（相當於新建） | 回傳 200，DB 新增一筆記錄，changelog old_value 為 null，sync pending 新增 pending 記錄。 |
| IT-03 | Validation | 傳送空 `playmode` 或不合法 JSON | 回傳 422。 |
| PT-01 | Permission | 不帶 `operator_account` 或無效 token 呼叫 | 回傳 401/403（依實作而定）。 |
| FT-01 | Flow | 確認異動後下游同步服務能正確讀取並處理 `threshold_sync_pending` | 下游服務狀態更新為 `done`，閥值同步至其他系統（需人工確認下游整合測試）。 |

---

## 9. 高風險區域

- **高風險 table**：`oddthreshold_sport_setting`（直接影響監控規則）、`threshold_sync_pending`（遺失記錄會導致跨系統閥值不一致）。
- **Transaction 遺漏**：若未將更新、changelog、sync 納入同一個 transaction，可能造成部分成功，需確保 Provider 層有明確的交易邊界。
- **Cache consistency**：目前無快取，但若有其他服務快取閥值，需依賴 sync pending 通知刷新（需人工確認）。
- **Idempotency**：相同內容重複請求應可重複執行（UPSERT 具 idempotent），但 changelog 與 sync 會重複產生記錄，需注意對下游的影響（必要時可在 sync pending 加入去重鍵）。

---

## 10. 常見錯誤

- 新人誤以為 `playmode` 是 partial update，實際為整包覆蓋（需確認 Resource 層是否有 merge 邏輯，原始設計多為直接替換）。
- 忽略同步佇列的寫入，導致下游服務無法獲知閥值變更。
- 直接操作 DB 變更閥值而不透過 API，將缺乏 changelog 與 sync pending，造成稽核與同步斷裂。
- 未檢查 `playmode` 中的玩法鍵是否與 `monitored_play_modes` 設定一致，可能導致閥值設定對應不到實際監控玩法。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `OddThresholdSportResource.update`（推測，需人工確認） |
| DB | `oddthreshold_sport_setting` 表定義於 `migrations/001_create_core_tables.sql` |
| Code | `oddthreshold_setting.py:upsert` 方法語意 |
| SQL | `INSERT ... ON CONFLICT (game_type) DO UPDATE`（見 `oddthreshold_setting.py`） |
| Changelog | `threshold_changelog.py:insert` |
| Sync | `threshold_sync_pending.py:enqueue` |
| README | 閥值異動皆寫入 changelog，並將變更排入同步佇列供下游消費。 |