# alertbackendservice — DB 操作邊界

> 產出時間：2025-03-28 12:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## Alert

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Alert PostgreSQL | owner/writer | Schema：[../../db/Alert.json](../../db/Alert.json) · 語意：[../../db/Alert-detail.md](../../db/Alert-detail.md) |

### 寫入限制

- `alerts.id`, `created_at`, `rule_code`, `level`, `game_type`, `source`, `game_id`, `league_id`, `play_mode`, `spread`, `selection`, `detail`, `threshold_snapshot`, `game_info`：僅由內部規則引擎在創建警報時寫入，不可由外部 API 直接修改。
- `alerts.status`、`operator_account`：僅通過 `update_alert` API 變更，且 `operator_account` 必填。
- `alerts.updated_at` 由資料庫自動維護，禁止手動賦值。
- `alert_change_log`：僅在 `alerts` 狀態變更時自動插入，不允許手動寫入。
- 所有設定表（`monitored_play_modes`, `source_type`, `sport_alert_sources`, `scorethreshold_setting`, `oddthreshold_*_setting`）的修改需記錄 `threshold_changelog`，不可繞過。
- `export_tasks` 的 `file_path`, `file_size_bytes`, `row_count` 由匯出排程寫入，外部僅能讀取。

### 讀取規則

- 查詢 `alerts` 時，建議強制指定 `game_type`（路徑參數）或 `created_at` 範圍（`start`/`end`），防止全表掃描。
- 查詢 `alerts` 常用狀態過濾：`status = 'pending'` 或 `status != 'ignored'`；歷史查詢應使用 `alerts_archive`。
- 查詢 `export_tasks` 時，僅回傳當前操作人（`operator_account`）的任務。
- 設定表（如 `monitored_play_modes`）按主鍵（`game_type`）精確讀取。

### 不可回傳欄位

- `webhook_pending.target_url`、`payload`：內含對外 webhook 配置，禁止經由任何 API 回傳至客戶端。
- `webhook_logs.target_url`：同上。
- 其餘欄位無特定機敏性，按既有 API 規範回傳。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET / DEL | `debounce:{source_id}:{source_game_id}:{play_mode}:{spread}:{selection}` | 收到賠率變動事件時記錄最近事件時間戳，用於防抖窗口聚合 | TTL 等於 debounce 窗口長度（例如 60 秒），自動過期，不需主動刪除 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 警報規則的定義與觸發邏輯 | alertengine | alertbackendservice 僅提供警報查詢、狀態變更，不執行規則評估。 |
| 賠率數據的即時採集與串流 | odds-collector | 本服務不直接訂閱上游賠率源，僅處理由上游傳遞的結構化訊息。 |
| Webhook 的實際發送與重試 | webhook-dispatcher | webhook_pending 記錄僅由 alertbackendservice 寫入佇列，實際發送由另一個排程服務處理。 |
| 匯出檔案的儲存與下載 | file-storage | export_tasks.file_path 指向 NAS 路徑，檔案上傳與下載由 file-storage 服務管理。 |
| 閾值設定同步到多節點 | threshold-sync | alertbackendservice 僅記錄同步需求至 threshold_sync_pending，執行同步由另外的 sync worker 負責。 |

---

## 常見錯誤

- ❌ 直接 UPDATE `alerts` 的 `status`/`operator_account` 而未同時寫入 `alert_change_log` → ✅ 必須通過 `update_alert` API，該 API 內部同時寫入變更記錄。
- ❌ 更新設定表（如 `scorethreshold_setting`）後未寫入 `threshold_changelog` → ✅ 任何設定異動都須同時 INSERT 一筆變更記錄。
- ❌ 在查詢 `alerts` 時未加入時間範圍導致全表掃描造成效能問題 → ✅ 務必在請求中加入 `start`/`end` 條件或優先使用 `game_type` 進行分區查詢。
- ❌ 操作歸檔表 `alerts_archive` 時誤認為可以更新狀態 → ✅ 歸檔表為唯讀記錄，不允許任何 UPDATE/DELETE。
- ❌ 在 debounce 窗口未完全結束前就觸發警示，導致重複警示 → ✅ 應確保通過 `debounce_stats` 檢查事件聚合後，再決定是否產出 `alerts`。