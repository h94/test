# 建立監控玩法設定

## 1. 場景目的
對指定球種新增監控玩法清單，若該球種已存在設定則回傳 409。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/monitored_play_modes/{game_type}` | 新增監控玩法設定（球種不區分大小寫） |

---

## 3. 流程總覽

1. 接收 POST request，路徑帶入 `game_type`（球種代碼）
2. 驗證 request body 包含 `play_mode` 與 `operator_account`
3. Provider 查詢 `monitored_play_modes` 檢查 `game_type` 是否已存在
4. 若已存在 → 回傳 HTTP 409 Conflict
5. 若不存在 → Provider 寫入 `monitored_play_modes`（INSERT）
6. 非同步寫入 `threshold_changelog`（無需等待、不阻斷主流程）
7. 回傳 200 OK 與新建記錄

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Resources | `MonitoredPlayModes.py` | 接收 POST request，解析 `game_type`、`play_mode`、`operator_account` |
| 2 | Resources | `MonitoredPlayModes.py` | 呼叫 Service 層 create 方法 |
| 3 | Service | `MonitoredPlayModesService.py` | 呼叫 Provider 檢查是否存在 |
| 4 | Provider | `MonitoredPlayModesProvider.py` | 查詢 `monitored_play_modes` 依照 `game_type` |
| 5 | Provider | `MonitoredPlayModesProvider.py` | 若存在則 raise 409 |
| 6 | Provider | `MonitoredPlayModesProvider.py` | 若不存在則 INSERT 新記錄 |
| 7 | Provider | `MonitoredPlayModesProvider.py` | 呼叫 `threshold_changelog.insert` 寫入 changelog |
| 8 | Resources | `MonitoredPlayModes.py` | 回傳 200 OK 與新建記錄 |

> **需人工確認**：`operator_account` 是否需驗證帳號存在性或權限

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `monitored_play_modes` | Read | 檢查 `game_type` 是否已存在 |
| DB | `monitored_play_modes` | Write (INSERT) | 新增球種之監控玩法設定 |
| DB | `threshold_changelog` | Write (INSERT) | 記錄本次新增稽核 |
| Redis | 無 | - | 本場景未使用 |
| Kafka | 無 | - | 本場景未使用 |

---

## 6. 重要規則

- **唯一性**：`game_type` 為 `monitored_play_modes` 的唯一鍵，不可重複插入（→ 409）
- **欄位格式**：`play_mode` 為 JSONB 儲存（DB 欄位型態）；request body 中可接受 `list[str]` 或 `dict[str,int]` 格式（OpenAPI `MonitoredPlayModePostBody.play_mode`）
- **不可暴露資料**：無特殊敏感性欄位
- **Transaction 規則**：`monitored_play_modes` INSERT 成功後才寫 `threshold_changelog`；changelog 寫入失敗不影響主流程回傳
- **狀態值限制**：無（本表無狀態欄位）
- **不可修改欄位**：`created_at` 僅於 INSERT 時自動設定

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 球種 `game_type` 已存在設定 | HTTP 409 Conflict |
| `play_mode` 格式無效（非 list/dict） | HTTP 422（由 FastAPI schema 自動驗證） |
| `operator_account` 缺失 | HTTP 422 |
| DB 寫入失敗 (`monitored_play_modes`) | HTTP 500，無部分寫入 |
| `threshold_changelog` 寫入失敗 | 不影響主流程，回傳 200；但 changelog 缺失（**風險**） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 對新球種建立監控玩法（合法 `play_mode`） | 200 OK，回傳記錄包含 `game_type`、`play_mode`、`operator_account` |
| TC02 | API Test | 對已存在球種建立監控玩法 | 409 Conflict |
| TC03 | API Test | `play_mode` 格式為非法型態 | 422 |
| TC04 | API Test | 缺少 `operator_account` | 422 |
| TC05 | DB Test | 建立成功後確認 `monitored_play_modes` 寫入 | 1 筆記錄，`play_mode` 為 JSONB |
| TC06 | DB Test | 建立成功後確認 `threshold_changelog` 寫入 | 1 筆記錄，`table_name='monitored_play_modes'` |
| TC07 | Flow Test | 模擬 changelog 寫入失敗 | 主請求回傳 200，changelog 無記錄 |

---

## 9. 高風險區域

- **高風險 table**：`monitored_play_modes`（唯一鍵約束衝突回傳 409）
- **高風險 API**：本 API 為寫入型 API，需確保 idempotent 行為（重複呼叫回 409）
- **跨服務資料同步**：changelog 寫入後，**尚無證據顯示有即時同步至其他服務**（如同步至 OddAlertService）
- **Cache consistency**：無 cache 使用
- **Idempotency**：同一 `game_type` 第二次呼叫必然 409（符合 idempotent）

---

## 10. 常見錯誤

- 誤以為 API 會自動處理 `play_mode` 格式轉換（實際需前端確保格式為 `list[str]` 或 `dict`）
- 忽略 409 衝突回應，前端未正確提示已存在設定
- 忘記 `operator_account` 為必填
- 誤以為 `play_mode` 可為空陣列（需人工確認是否允許空陣列）

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 定義 | OpenAPI `POST /api/monitored_play_modes/{game_type}` |
| Request schema | `MonitoredPlayModePostBody` (play_mode, operator_account) |
| DB table | `monitored_play_modes` (game_type, play_mode, operator_account, created_at, updated_at) |
| DB schema | `migrations/001_create_core_tables.sql` |
| Code - Provider exist check | `MonitoredPlayModesProvider.py` 查詢並判斷是否存在 |
| Code - 409 logic | 存在則 raise HTTP 409 |
| Changelog | `threshold_changelog` 寫入 (table_name, record_key, old_value=NULL, new_value) |

> **需人工確認**：
> 1. `operator_account` 是否需要驗證存在於人員系統
> 2. `play_mode` 是否允許空陣列
> 3. 是否有下游同步機制（如 Kafka sync 至 OddAlertService）