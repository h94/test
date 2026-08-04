# 更新競猜及 Killer 設定

## 1. 場景目的

本場景描述後台管理員如何透過 pricebackendservice 代理，更新 predictservice 中的競猜遊戲設定（predict_settings）、Killer 周期設定（killer_cycle_settings）以及最終的派彩參數（pay_out）。此流程確保競猜玩法的啟動、Killer 機制的參數與派彩金額能被正確調整，同時避免在非適當狀態下修改導致邏輯錯誤。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/v1/settings/predict/{gameType}` | 更新競猜遊戲設定（如玩法、Killer 開關） |
| PUT | `/api/v1/settings/killer/cycles/{gameType}/{lid}/{cid}` | 更新整個 Killer 周期設定 |
| PUT | `/api/v1/settings/killer/cycles/{gameType}/{lid}/{cid}/payout` | 單獨更新 Killer 周期的派彩金額 |

**代理模式**：根據 README.md 職責說明，上述 API 由 `pricebackendservice` 代理後台操作呼叫。驗證由 ECFramework.ECService 內部框架處理（所有後台 API 皆需驗證）。

---

## 3. 流程總覽

1. **接收後台請求**：`pricebackendservice` 根據管理員操作，轉發對應的 PUT 請求至 `predictservice`。
2. **參數驗證**：透過 ECFramework 驗證器檢查請求格式、必填欄位，並進行業務規則校驗（例如 `gameType` 的合法性、Killer 狀態與 `pay_out` 的邏輯）。
3. **查詢現有設定**：從 `predict.predict_settings` 讀取當前遊戲設定，必要時從 `predict.killer_cycle_settings` 讀取 Killer 周期設定。
4. **業務邏輯檢查**：
   - 確認競猜遊戲是否存在。
   - 檢查是否允許在當前狀態下啟用/停用 Killer 機制。
   - 檢查更新 `pay_out` 時，Killer 周期是否已存在且為有效狀態（如已確認派彩則不可再修改）。
5. **執行更新寫入**：根據請求寫入 `predict_settings` 或 `killer_cycle_settings`。
6. **清除相關快取**（`需人工確認`：目前 predict-detail.md 未明確定義設定相關的 Redis Key，但高頻查詢可能緩存，需確認 settings 變更時是否需手動失效，否則前台依然讀取舊設定）。
7. **回傳成功結果**。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SettingsController.PutPredictSetting` | 接收 gameType 與 request body，轉發 Service |
| 2 | Controller | `SettingsController.PutKillerCycleSetting` | 接收 gameType, lid, cid 與 body，轉發 Service |
| 3 | Controller | `SettingsController.PutKillerCyclePayout` | 接收 gameType, lid, cid 與 pay_out，轉發 Service |
| 4 | Service | `SettingsService.UpdatePredictSetting` | 參數驗證、狀態檢查、呼叫 Provider 寫入 DB |
| 5 | Service | `SettingsService.UpdateKillerCycleSetting` | Killer 設定校驗、狀態檢查、呼叫 Provider |
| 6 | Service | `SettingsService.UpdateKillerCyclePayout` | 確認 Killer 結算狀態，寫入新的 pay_out |
| 7 | Provider | `PredictSettingsProvider.UpdateSettings` | 執行 Cassandra UPDATE (predict_settings) |
| 8 | Provider | `KillerCycleProvider.UpdateCycleSettings` | 執行 Cassandra UPDATE (killer_cycle_settings) |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.predict_settings` | Read, Update | 讀取現有設定，更新 `play_modes`, `killer_enabled` 等 |
| DB | `predict.killer_cycle_settings` | Read, Update | 讀取現有周期，更新 `pay_out` 等字段 |
| Redis | `predict:settings:{gameType}` | DEL | `需人工確認` 是否需要失效快取，避免讀取過期設定 |
| Kafka | `applogs` | Publish | 記錄 API 請求、參數錯誤、更新完成的 Log 資訊 |

---

## 6. 重要規則

- **權限限制**：僅允許具備管理員權限的後台帳號透過 `pricebackendservice` 呼叫。
- **不可修改欄位**：`predict_settings` 的 `game_type`（主鍵）不可變更。
- **Killer 啟用邏輯**：`killer_enabled` 設為 true 前，需確保該遊戲類型的 `killer_cycle_settings` 已正確建立。
- **派彩修改限制**：若 `killer_cycle_settings` 已進入結算或已派彩狀態（`pay_out` 確認後），應拒絕修改（`需人工確認`：目前未定義確切的 Killer 結算狀態碼，需依後續規則補充）。
- **狀態值限制**：
  - `play_modes`：需符合該 gameType 定義的合法模式。
  - `killer_enabled`：僅接受 Boolean 值。
- **Transaction 規則**：此次更新皆為單表操作，不涉及強制包裹 Transaction，但需注意寫入原子性。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `gameType` 不存在於 `predict_settings` | 回傳 404 Not Found 或特定錯誤碼 |
| 請求參數格式錯誤（如 `pay_out` 為負數） | 回傳 400 Bad Request，附帶驗證錯誤訊息 |
| 試圖修改已結算的 Killer 周期的 `pay_out` | 回傳 409 Conflict 或邏輯錯誤，提示不可修改 |
| Cassandra 寫入暫時失敗（超時） | 回傳 500 Internal Server Error，記錄 Kafka 錯誤日誌 |
| 未驗證或權限不足的使用者呼叫 API | 回傳 401 Unauthorized 或 403 Forbidden |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T-001 | API Test | 傳入合法 `play_modes` 陣列更新 | 200 OK，DB 內容對應更新 |
| T-002 | API Test | 啟用一個 gameType 的 Killer 機制 | 200 OK，`killer_enabled` 設為 true |
| T-003 | Permission Test | 使用一般使用者 Token 呼叫 | 403 Forbidden |
| T-004 | Flow Test | 更新一個不存在的 gameType 設定 | 404 Not Found |
| T-005 | Flow Test | 修改已確認派彩的 Killer `pay_out` | 409 Conflict，`pay_out` 未被修改 |
| T-006 | Validation Test | `pay_out` 傳入字串或負數 | 400 Bad Request |

---

## 9. 高風險區域

- **高風險 table**：`predict.killer_cycle_settings` — 若 `pay_out` 在派彩後被意外覆寫，將導致金流計算錯誤。
- **Cache consistency**：若存在 `predict:settings:{gameType}` 快取，更新 DB 後未清除會導致前台與後台設定不一致長達 TTL 時間。
- **跨服務同步**：`pricebackendservice` 僅為代理，若代理層增加了額外的快取或狀態，需確保與 `predictservice` 內部狀態一致。
- **Idempotency**：連續兩次相同的 PUT 請求應得到相同結果，不可重複觸發 side effects（如發送多次 Kafka 通知）。

---

## 10. 常見錯誤

- **AI 容易誤解**：忽視 `pricebackendservice` 的代理角色，直接在 predictservice 外部試圖繞過身份驗證模擬請求。
- **新人容易犯錯**：修改 `killer_enabled` 為 true 時，未事先建立對應的 Killer 條件設定（`POST /api/v1/settings/killer/conditions/...`），導致後續排程報錯。
- **常見漏檢查項目**：未驗證 `gameType` 是否屬於系統支援的合法競猜類型。
- **常見錯誤流程**：在未讀取舊設定的情況下直接 UPDATE，意外覆蓋了不打算修改的欄位（如只改 pay_out 卻誤將其他欄位設為預設值）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `SettingsController` (PutPredictSetting / PutKillerCycleSetting) |
| DB | `predict.predict_settings` / `predict.killer_cycle_settings` |
| Service | `SettingsService` (UpdatePredictSetting / UpdateKillerCycleSetting) |
| Provider | `PredictSettingsProvider` / `KillerCycleProvider` |
| README | `predictservice` README.md / predict-detail.md |