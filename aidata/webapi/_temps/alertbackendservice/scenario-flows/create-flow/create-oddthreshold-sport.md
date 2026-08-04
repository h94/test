# 建立運動層級賠率閥值

## 1. 場景目的
此流程描述管理員針對特定球種（運動層級），新增或建立預設的賠率監控閥值設定。設定內容主要包含各玩法（play mode）的賠率變動絕對值與百分比上限，供後續賠率異常監控系統比對使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/oddthreshold/sport/{game_type}` | 新增指定球種的賠率閥值設定 |

---

## 3. 流程總覽

1. 管理員透過前端呼叫 `POST /api/oddthreshold/sport/{game_type}` API。
2. Resource 層接收請求，將 `game_type` 路徑參數與 Request Body 傳遞至 Service 層。
3. Service 層呼叫 Provider 層，將請求資料寫入 `oddthreshold_sport_setting` 資料表。
4. Provider 層使用 `INSERT ... ON CONFLICT DO UPDATE` (upsert) 語法執行寫入，確保單一球種只會有一筆設定。
5. 寫入成功後，Service 層記錄此次異動至 `threshold_changelog`。
6. 同時將同步任務排入 `threshold_sync_pending` 佇列，供下游系統（如監控服務）同步最新的閥值設定。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Resource | `OddThresholdSportResource.create` | 接收 `game_type` 與 `PlaymodePostBody`，呼叫 Service。 |
| 2 | Service | `OddThresholdService.create_sport_setting` | 處理業務邏輯，準備資料物件。 |
| 3 | Provider | `OddThresholdSettingProvider.upsert` | 執行 `oddthreshold_sport_setting` 的 upsert 操作。 |
| 4 | Provider | `ThresholdChangelogProvider.insert` | 寫入一筆異動紀錄至 `threshold_changelog`。 |
| 5 | Provider | `ThresholdSyncPendingProvider.enqueue` | 寫入一筆 pending 狀態的同步任務。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `oddthreshold_sport_setting` | Write (Upsert) | 儲存或更新球種層級的賠率閥值 JSON 設定。 |
| DB | `threshold_changelog` | Write (Insert) | 記錄每一次閥值設定的異動軌跡。 |
| DB | `threshold_sync_pending` | Write (Insert) | 排入待同步任務，由背景排程或外部消費者處理同步。 |

---

## 6. 重要規則

- **權限限制**：API 需驗證操作者身份，並記錄 `operator_account`。（需人工確認：此服務的 Auth 機制實作細節，目前 code 中未見 Middleware）
- **欄位限制**：
  - `game_type`：必填，需為系統支援的球種代碼。
  - `playmode`：必填，為一個 JSON 物件，其鍵為玩法代碼，值為包含 `absolute` 與 `percentage` 閥值的數字物件。
- **不可暴露資料**：Request / Response 中不應包含內部流水號或時間戳記。
- **Transaction 規則**：`oddthreshold_sport_setting` 的 upsert、`threshold_changelog` 寫入、`threshold_sync_pending` 寫入應在同一個 DB Transaction 中完成，以確保資料一致性。（需人工確認：目前 code 未顯示明確的 Transaction 管理方式）
- **不可修改欄位**：`game_type` 在建立後即為該設定的唯一鍵，不可變更。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求未帶入必要的 `playmode` 資訊 | 回傳 HTTP 422 Validation Error。 |
| 請求的 `game_type` 格式不合規 | 回傳 HTTP 422 Validation Error。 |
| `oddthreshold_sport_setting` 寫入失敗（如 DB 連線中斷） | 回傳 HTTP 500 Internal Server Error。 |
| `threshold_changelog` 寫入失敗 | 整個請求失敗，`oddthreshold_sport_setting` 的變更應一併回滾，回傳 HTTP 500。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-01 | API Test | 針對一個不存在的 `game_type` 發送建立請求。 | HTTP 200，DB 中成功新增一筆紀錄。 |
| UT-02 | API Test | 針對已存在設定的 `game_type` 再次發送建立請求。 | HTTP 200，該筆紀錄的 `playmode` 被更新為新值，其餘欄位未受影響。 |
| UT-03 | Flow Test | 驗證建立成功後，`threshold_changelog` 表格。 | 應新增一筆紀錄，內容包含新舊值的比較。 |
| UT-04 | Flow Test | 驗證建立成功後，`threshold_sync_pending` 表格。 | 應新增一筆 `status` 為 `pending` 的同步任務。 |

---

## 9. 高風險區域

- **高風險 API**：此 API 直接影響賠率監控規則，錯誤的設定可能導致大量誤報或漏報。
- **Transaction**：若 `threshold_changelog` 或 `threshold_sync_pending` 寫入失敗，但主設定已寫入，將導致資料不一致與下游同步遺漏。務必確保 Transaction 完整性。
- **Cache consistency**：（本場景未使用 Redis，此項不適用）
- **Queue retry**：需確認 `threshold_sync_pending` 的消費者是否有完善的重試機制，避免同步失敗後永久遺失。

---

## 10. 常見錯誤

- **新人容易犯錯**：誤以為此 API 會驗證 `playmode` 內部結構的合法性。目前 API 僅做基本的型別檢查，具體玩法代碼是否有效，需由前端或另一設定檔控管。
- **AI 容易誤解**：將此 API 與遊戲層級（game-level）或聯盟層級（league-level）的閥值設定混淆。它們是獨立的 API 與資料表。
- **常見漏檢查項目**：忘記檢查 `operator_account` 是否正確傳遞並記錄於所有異動相關表格中，影響後續稽核。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `Resources/OddThreshold.py` -> `SportResource` |
| Service | `Service/OddThresholdService.py` -> `create_sport_setting` |
| Provider | `Provider/OddThresholdSettingProvider.py` -> `upsert` |
| DB (設定) | Schema `oddthreshold_sport_setting` 定義於 `migrations/001_create_core_tables.sql` |
| DB (異動) | Schema `threshold_changelog` 定義於 `migrations/002_create_supplement_tables.sql` |
| DB (同步) | Schema `threshold_sync_pending` 定義於 `migrations/003_create_sync_tables.sql` |