# Alert DB — 完整使用脈絡

> 產出時間：2026-07-28 08:55
> 欄位結構定義：[Alert.json](./Alert.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

<!-- ⚠️ 衝突待人工：現有內容以 `oddalertservice` 為 owner，本次 triggerSource 為 `alertbackendservice`。
     經分析新服務摘要，`oddalertservice` 可能已拆分為 `alertengine`（規則觸發寫入）與 `alertbackendservice`（API 查詢與狀態變更）。
     以下以新服務摘要為準，並保留舊有配置寫入服務，請人工確認後移除本提示。 -->

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| alertbackendservice | owner | 讀、寫（警報狀態變更、操作者記錄、變更日誌）、刪（歸檔） |
| alertengine | writer | 僅可 INSERT alerts 表（內部規則引擎觸發時寫入不可變業務欄位） |
| odd_data_sync_service | writer | 僅可寫入 `config_direct_sync`、`effective_thresholds`、`oddthreshold_*_setting`、`scorethreshold_setting` 等配置相關表 |
| admin_backend_service | writer | 讀取配置表；寫入 `monitored_play_modes`、`source_type`、`sport_alert_sources` 等設定 |
| webhook-dispatcher | writer | 僅可寫入 `webhook_pending`、`webhook_logs`（webhook 佇列與日誌） |

---

## Table：alerts

### status 欄位

**型別**：character varying

**值定義與狀態流轉**：

```
     alertengine          alertbackendservice   alertbackendservice
      INSERT               UPDATE               UPDATE
     value=pending ──────→ value=ignored ──────→ (結束)
         │
         │
         └──────────────→  value=confirmed ──→ value=resolved
              alertbackendservice（管理員標記）  alertbackendservice（管理員確認解決）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| pending | 待處理 | alertengine | INSERT 時預設值，告警規則觸發時自動產生 |
| ignored | 已忽略 | alertbackendservice | 管理員透過 update_alert API 手動標記為忽略，毋需處理 |
| confirmed | 已確認 | alertbackendservice | 管理員透過 update_alert API 確認告警，準備處理 |
| resolved | 已解決 | alertbackendservice | 管理員確認問題已解決後設定 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| alertengine | INSERT status=pending | 告警規則檢測觸發 | 自動建立告警，初始狀態為 pending |
| alertbackendservice | UPDATE status=ignored | 管理員 API 操作 | 忽略不重要的告警，不再追蹤 |
| alertbackendservice | UPDATE status=confirmed | 管理員 API 操作 | 確認告警需要處理 |
| alertbackendservice | UPDATE status=resolved | 管理員 API 操作 | 問題已解決，告警關閉 |

**⚠️ 跨服務限制**：

- status 欄位僅能由 alertbackendservice 的 `update_alert` API 進行變更（pending 由 alertengine INSERT 時設定除外），任何其他服務或直接 SQL 操作皆不被允許
- 狀態流轉必須嚴格遵循 `pending → ignored` 或 `pending → confirmed → resolved`，不允許跳躍或逆轉（如 resolved 不可退回 confirmed）
- 每次 status 變更時，alertbackendservice 必須在**同一交易內**自動寫入一筆記錄至 `alert_change_log`，記錄新舊值與操作者帳號
- 其他服務（如 admin_backend_service）僅允許 SELECT 讀取此表，不可直接對 status 欄位進行任何寫入操作
- alertengine 僅在 INSERT 時寫入初始值 `pending`，不可在後續流程中再次修改此欄位

---

### operator_account 欄位

**型別**：text

**值定義與狀態流轉**：

此欄位用於記錄最後操作此告警的管理員帳號。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| null | 無操作者 | — | 告警 INSERT 時預設值，表示僅由系統自動觸發，尚未有人處理 |
| {username} | 操作者帳號 | alertbackendservice | 每次透過 `update_alert` API 變更 status 時，從認證資訊（JWT / req.user）自動注入，且為必填 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| alertengine | INSERT operator_account=null | 告警觸發 | 初始無操作者，設為 null |
| alertbackendservice | UPDATE operator_account={user} | status 變更時 | 自動從認證資訊注入，`operator_account` 為必填參數，記錄處理人員 |

**⚠️ 跨服務限制**：

- 不允許請求參數自行指定 `operator_account`，必須由 API 後端從已驗證的 Session/Token 中提取並強制寫入，防止身份偽造
- 其他服務不可修改此欄位
- `operator_account` 在 status 變更時為必填，不可為空或 null

---

### level 欄位

**型別**：character varying

**值定義與狀態流轉**：

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| yellow | 黃燈警告 | alertengine | 告警規則檢測值超過黃燈閾值但未達紅燈時，INSERT 時設定 |
| red | 紅燈警報 | alertengine | 告警規則檢測值超過紅燈閾值時，INSERT 時設定 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| alertengine | INSERT level=yellow 或 red | 依規則閾值判斷 | 對比 `threshold_snapshot` 決定，插入後不可變更 |
| alertbackendservice | SELECT WHERE level='red' | 優先處理 | 紅燈告警應優先檢視與處理 |

**⚠️ 跨服務限制**：

- level 與 `rule_code`、`source`、`game_id` 等欄位同為**不可變動的業務鍵**，INSERT 後任何服務皆不可修改，alertbackendservice 的 update_alert API 也不可變更此欄位
- 其他服務查詢時可利用此欄位區分告警嚴重程度（如：儀表板優先顯示 `level=red` 的 pending 告警）

---

### rule_code 欄位

**型別**：character varying

**值定義與狀態流轉**：

此欄位為固定規則代碼，對應後端檢測器類型。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| odds_implied_probability_divergence | 隱含機率分歧 | alertengine | 檢測到不同資料源間的隱含機率差異過大時 |
| odds_spike | 賠率驟升 | alertengine | 賠率在短時間內異常飆升時 |
| odds_flutter | 賠率劇烈波動 | alertengine | 賠率在短時間內頻繁變動時 |
| odds_stale | 賠率凍結 | alertengine | 賠率長時間未更新時 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| alertengine | INSERT rule_code | 依觸發規則類型 | 插入後不可變更 |
| alertbackendservice | SELECT WHERE rule_code | 分類查詢與統計 | 用於依規則類型篩選告警 |

**⚠️ 跨服務限制**：

- rule_code 為**不可變動的業務鍵**，INSERT 後任何服務皆不可修改，alertbackendservice 的 update_alert API 也不可變更此欄位
- 規則代碼由系統定義，不允許動態新增或變更，若需擴充需透過版本發布流程

---

### detail 欄位

**型別**：jsonb

**值定義與狀態流轉**：

儲存觸發告警時的詳細上下文資訊（JSON 物件），為觸發瞬間的**證據快照**。由 alertengine 在檢測到異常時填入原始數據（如各資料源價格、計算過程）。

| 服務 | 操作 | 說明 |
|------|------|------|
| alertengine | INSERT 寫入 | 由檢測模組在 INSERT 時寫入，包含觸發的原始數據 |
| alertbackendservice | SELECT（明細查詢） | 僅在查看單筆告警明細時載入，列表查詢不應選取此欄位以提升效能 |

**⚠️ 注意**：

- detail 為**不可變更**的 evidence 欄位，不對外提供任何 UPDATE 或覆寫介面，alertbackendservice 的 API 不可修改此欄位
- 此欄位可能非常大，嚴禁在列表查詢或批次操作中使用 `SELECT *` 將其載入，需使用欄位篩選

---

### threshold_snapshot 欄位

**型別**：jsonb

**值定義與狀態流轉**：

儲存觸發告警時所套用**閾值設定的快照**（含 red/yellow 數值、維度等），用於事後稽核。由 alertengine 在 INSERT 時寫入。

| 服務 | 操作 | 說明 |
|------|------|------|
| alertengine | INSERT 寫入 | 由檢測模組在 INSERT 時寫入，記錄觸發當下的閾值參數 |
| alertbackendservice | SELECT（明細查詢） | 僅在查看單筆告警明細時載入 |

**⚠️ 注意**：

- threshold_snapshot 為**不可變更**的 evidence 欄位，不對外提供任何 UPDATE 或覆寫介面，alertbackendservice 的 API 不可修改此欄位
- 與 `effective_thresholds` 表不同，此欄位反映的是「告警當下」的配置（事後配置可能已變更），兩者應可互相對照以進行稽核

---

### game_info 欄位

**型別**：jsonb

**值定義與狀態流轉**：

儲存觸發告警時的**比賽基本資訊快照**（隊伍名稱、比分、狀態等），用於前台展示時無需再查詢賽事 DB。由 alertengine 在 INSERT 時寫入。

| 服務 | 操作 | 說明 |
|------|------|------|
| alertengine | INSERT 寫入 | 由檢測模組在 INSERT 時寫入 |
| alertbackendservice | SELECT（列表與明細） | 可安全用於列表展示（相較 detail 輕量），提供比賽摘要資訊 |

**⚠️ 注意**：

- game_info 為**不可變更**的 evidence 欄位，不對外提供任何 UPDATE 或覆寫介面，alertbackendservice 的 API 不可修改此欄位
- 內部結構為非結構化 JSON，若需搜尋特定欄位（如 `team_away`），需使用 PostgreSQL JSONB 查詢語法，注意 GIN 索引的設計

---

### 查詢注意事項（alertbackendservice）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| alertbackendservice | SELECT | 一般查詢 | 建議強制指定 `game_type`（路徑參數）或 `created_at` 範圍（`start`/`end`），防止全表掃描 |
| alertbackendservice | SELECT | 狀態過濾 | 常用過濾：`status = 'pending'` 或 `status != 'ignored'` |
| alertbackendservice | SELECT | 歷史查詢 | 歷史查詢應使用 `alerts_archive` 表，不應直接查詢主表 |
| alertbackendservice | UPDATE | `updated_at` | 此欄位由資料庫自動維護（`now()`），禁止手動賦值 |

---

## Table：alerts_archive

### 用途與限制

此表為 `alerts` 的**歷史歸檔表**，結構與 `alerts` 完全相同。用於儲存已結案或過期的告警資料，以維持主表效能。

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| alertbackendservice | INSERT / DELETE | 定時歸檔作業 | 將主表已處理完畢的告警移至 archive，或依留存政策清除過期資料 |
| alertbackendservice | SELECT | 歷史查詢 | 用於稽核或查閱歷史告警，不可用於常規業務查詢 |

**⚠️ 跨服務限制**：

- 對外不允許任何 INSERT / UPDATE / DELETE 操作，僅由 alertbackendservice 內部排程或存檔程式寫入
- 此表不對一般業務 API 開放寫入，僅供後台歷史查詢功能唯讀

---

## Table：alert_change_log

### 用途與限制

此表為告警狀態變更的**審計日誌（Audit Log）**，確保每一次人為操作皆有跡可循。

| 欄位 | 型態 | 說明 |
|------|------|------|
| id | bigint | 自增主鍵 |
| alert_id | character varying | 關聯 alerts.id |
| field_name | text | 變更的欄位名稱（如 `status`） |
| old_value | text | 變更前的值（可為 null） |
| new_value | text | 變更後的值（可為 null） |
| operator_account | text | 操作者帳號（必填） |
| changed_at | timestamp with time zone | 變更時間（預設 now()） |

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| alertbackendservice | INSERT | `alerts.status` 變更時，同一交易內自動觸發 | 記錄 alert_id、變更欄位（field_name）、新舊值及操作者 |

**⚠️ 跨服務限制**：

- 無任何外部寫入介面，嚴禁任何服務或人工透過 SQL 直接 INSERT / UPDATE / DELETE
- 此表由 alertbackendservice 在 status 變更交易中自動維護，不可手動寫入
- admin_backend_service 可對 `alert_change_log` 進行 SELECT 查詢，例如依 `alert_id` 查閱該告警的完整操作歷程，用於管理後台顯示或合規稽核報表

---

## Table：export_tasks

### 用途與限制

此表用於管理告警資料的**匯出任務**，記錄匯出請求的狀態、檔案資訊及錯誤訊息。

| 欄位 | 型態 | 說明 |
|------|------|------|
| id | character varying | 任務 ID |
| status | character varying | 任務狀態（預設 pending） |
| query_params | jsonb | 查詢參數 |
| file_path | text | 匯出檔案路徑 |
| file_size_bytes | bigint | 檔案大小 |
| row_count | integer | 資料筆數 |
| error_message | text | 錯誤訊息 |
| created_at | timestamp with time zone | 建立時間 |
| started_at | timestamp with time zone | 開始時間 |
| completed_at | timestamp with time zone | 完成時間 |
| operator_account | text | 請求匯出的操作者帳號 |

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| alertbackendservice | INSERT | 使用者請求匯出 | 建立匯出任務，初始狀態為 pending，`operator_account` 必填 |
| alertbackendservice | UPDATE file_path, file_size_bytes, row_count | 匯出排程完成時 | 由內部匯出排程寫入，外部僅能讀取 |
| alertbackendservice | UPDATE status, started_at, completed_at | 任務生命週期 | 由內部排程管理任務狀態流轉 |
| alertbackendservice | SELECT | 查詢任務狀態 | 僅回傳當前操作人（`operator_account`）的任務，不可查詢他人任務 |

**⚠️ 跨服務限制**：

- `file_path`、`file_size_bytes`、`row_count` 由匯出排程寫入，外部 API 不可修改
- 查詢 `export_tasks` 時，alertbackendservice 必須強制過濾 `operator_account`，僅回傳當前操作人的任務，防止資訊洩漏
- `started_at` 和 `completed_at` 由系統自動維護，不可手動賦值

---

## Redis — DebounceCache

### `debounce:{source_id}:{source_game_id}:{play_mode}:{spread}:{selection}`

用於賠率變動事件的**防抖（debounce）窗口聚合**，記錄特定比賽/玩法/讓分/選項的最近事件時間戳，避免同一窗口內重複觸發告警。

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET | alertengine | 收到賠率變動事件時 | 記錄最新事件時間戳，TTL 等於 debounce 窗口長度（例如 60 秒） |
| GET | alertengine | 判斷是否在防抖窗口內 | 若 Key 存在且未過期，表示仍在窗口內，聚合而非重複觸發 |
| DEL | —（自動過期） | TTL 到期後自動清除 | 不須主動刪除，Redis 自動清理過期 Key |

**⚠️ 注意**：

- TTL 由 debounce 窗口長度決定（例如 60 秒），過期後自動清除，不需任何服務人工介入
- alertengine 讀不到此 Key 時，表示該事件為新窗口的首次事件，應正常觸發告警檢測
- 此快取僅用於 alertengine 內部防抖邏輯，不應由 alertbackendservice 或其他服務讀取或修改

---

## 常見錯誤（跨服務）

- ❌ 任何服務直接對 `alerts.status` 執行 SQL UPDATE → 必須透過 alertbackendservice 的 `update_alert` API 進行，且需在同一交易內記錄 `alert_change_log`
- ❌ alertbackendservice 的 API 允許請求參數自行指定 `operator_account` → 應強制從認證資訊注入，防止偽造操作者身份
- ❌ alertbackendservice 嘗試變更 `rule_code`、`level`、`detail`、`threshold_snapshot`、`game_info` 等不可變欄位 → 這些為 alertengine 寫入的業務鍵或 evidence 欄位，INSERT 後任何修改皆應被拒絕
- ❌ 前端或後台列表查詢時使用 `SELECT *` 包含 `detail` 欄位 → 導致傳輸量過大與效能問題，應區分明細查詢與列表查詢
- ❌ alertbackendservice 歷史查詢直接掃描 `alerts` 主表 → 應使用 `alerts_archive` 表進行歷史查詢
- ❌ alertbackendservice 查詢 `export_tasks` 時未過濾 `operator_account` → 可能導致操作者看到他人的匯出任務，造成資訊洩漏
- ❌ 狀態流轉不遵循 `pending → ignored` 或 `pending → confirmed → resolved` → 可能導致資料不一致或前端顯示錯誤
- ❌ alertbackendservice 嘗試手動賦值 `alerts.updated_at` → 此欄位由資料庫自動維護（`now()`），不可手動設定