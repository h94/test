# 更新遊戲層級賠率閥值

## 1. 場景目的
讓維運人員針對特定賽事（sitegid）設定或異動其賠率監控閥值（playmode），異動會記錄至 changelog 並排入同步佇列，供下游監控服務即時生效。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | /api/oddthreshold/game/{sitegid} | 修改遊戲層級賠率閥值設定 |

Request body (JSON)：

| 欄位 | 型態 | 說明 |
|---|---|---|
| source | string | 資料來源代碼 |
| gdate | string | 賽事日期 |
| sitelid | string | 聯盟識別碼 |
| game_type | string | 球種 |
| playmode | JSON object | 玩法閥值設定（如 handicap 上限、下限） |
| operator_account | string | 操作者帳號 |

---

## 3. 流程總覽

1. 接收 PUT 請求與 body 參數
2. 驗證必填欄位（operator_account、playmode …）
3. 呼叫 Service 層 upsert `oddthreshold_game_setting` 記錄
4. 比對新舊值，將變更寫入 `threshold_changelog`
5. 將同步記錄寫入 `threshold_sync_pending` 佇列
6. 回傳成功

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `OddthresholdGameSettingResource` | 解析路徑參數 sitegid 與 body，呼叫 service |
| 2 | Service | `OddthresholdSettingService.upsert_game(sitegid, ...)` | 組裝資料，呼叫 provider 進行 upsert |
| 3 | Provider | `OddthresholdGameSettingProvider.upsert(record)` | 執行 INSERT … ON CONFLICT (sitegid, source) DO UPDATE |
| 4 | Service | 同上 | 取得 upsert 前舊值（若有），計算變化 |
| 5 | Provider | `ThresholdChangelogProvider.insert(...)` | 寫入 changelog（old_value / new_value） |
| 6 | Provider | `ThresholdSyncPendingProvider.enqueue(table_name, record_key)` | 插入一筆 status=‘pending’ 的同步任務 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `oddthreshold_game_setting` | Upsert (Write/Update) | 儲存遊戲層級賠率閥值設定 |
| DB | `threshold_changelog` | Insert (Write) | 記錄每次閥值異動的詳細內容 |
| DB | `threshold_sync_pending` | Insert (Write) | 將異動排入同步佇列供下游消費 |

（本場景未使用 Redis / Kafka）

---

## 6. 重要規則

- **不可暴露的資料**：無，所有欄位屬設定值，非機敏。
- **唯一鍵限制**：`oddthreshold_game_setting` 的 primary key 為 `(sitegid, source)` 組合，同一賽事同一來源只能有一筆設定。
- **異動記錄強制**：每次 upsert 必須寫入 `threshold_changelog`，包含 `old_value` 與 `new_value`。
- **同步保證**：每次異動都必須在 `threshold_sync_pending` 中產生一筆 pending 記錄，供後續 worker 或下游服務同步使用。
- **operator_account 必填**：異動者的帳號不可為空，會寫入設定表與 changelog。
- **playmode JSON 結構**：由前端定義，後端直接儲存，不進行內容驗證（需人工確認）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 缺少必填欄位（如 operator_account） | HTTP 422 Validation Error |
| DB 連線失敗 | 回傳 500 內部錯誤 |
| 寫入 changelog 失敗 | 整個交易應 rollback（若在同一個 DB session） |
| 寫入 sync_pending 失敗 | 同上，需確保一致性 |
| 同一 sitegid + source 同時多次請求 | 關鍵為最後寫入的資料，並各自產生 changelog |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| OT-001 | API Test | 帶合法 body 修改既有遊戲閥值 | 回應 200，DB 中 playmode 更新 |
| OT-002 | API Test | 使用新的 sitegid+source，建立新設定 | 成功新增一筆，changelog 記錄為空舊值 |
| OT-003 | Integration Test | 寫入後檢查 changelog 與 sync_pending | changelog 筆數增加，sync_pending 一筆 pending |
| OT-004 | Validation Test | 忽略 operator_account | 回傳 422 |
| OT-005 | Flow Test | 重複使用相同 body 呼叫兩次 | 第二次 changelog 紀錄若無變化則可能跳過 insert（需人工確認邏輯） |

---

## 9. 高風險區域

- **高風險 Table**：`oddthreshold_game_setting`（直接影響告警判斷）、`threshold_sync_pending`（耽誤同步可能導致告警遺漏）
- **同步延遲**：若 sync_pending 未被及時消化，後續監控將使用舊閥值，可能漏報或誤報
- **Transaction 邊界**：upsert、changelog、sync 三者應同生命週期，需確保使用同一 DB 交易（若 provider 各別寫入則需注意）
- **並行更新**：多個操作員對同一場次同時異動，可能造成 changelog 與最終狀態對應混亂，但本質上取最後寫入值

---

## 10. 常見錯誤

- **忘記寫 changelog**：只在 Service 層處理，新人可能遺漏
- **operator_account 未傳遞**：前端或 API 中未強制檢查，導致 DB 欄位為空
- **認為 old_value 來自 request**：正確做法是從 DB 撈取目前值再比較，若直接取 request 則失去實際變化紀錄
- **AI 容易誤導**：可能會以為有 Redis 快取閥值，但目前無證據，請勿添加

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI path: `/api/oddthreshold/game/{sitegid}` (PUT) |
| DB | `oddthreshold_game_setting` 表定義於 migrations/001_create_core_tables.sql |
| DB | `threshold_changelog`、`threshold_sync_pending` 定義於 migrations/002/003 |
| Code | Service: `oddthreshold_setting.py:upsert`（推論自 batch-3 語意）|
| Code | Provider: `ThresholdChangelogProvider.insert`（來自 provider 語意） |
| Code | Provider: `ThresholdSyncPendingProvider.enqueue`（來自 provider 語意） |
| 規則 | README 說明「閥值異動皆寫入 changelog，並將變更排入同步佇列」 |