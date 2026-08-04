# Alert DB — 完整使用脈絡

> 產出時間：2026-07-14 10:30
> 欄位結構定義：[Alert.json](./Alert.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| oddalertservice | owner | 讀、寫、刪 |
| odd_data_sync_service | writer | 僅可寫入 `config_direct_sync`、`effective_thresholds`、`oddthreshold_game_setting`、`scorethreshold_setting` 等配置相關表 |
| admin_backend_service | writer | 讀取配置表；寫入 `monitored_play_modes`、`source_type`、`sport_alert_sources` 等配置與設定 |

---

## Table：alerts

### status 欄位

**型別**：character varying

**值定義與狀態流轉**：

```
     oddalertservice     oddalertservice      oddalertservice
      INSERT               UPDATE               UPDATE
     value=pending ──────→ value=ignored ──────→ (結束)
         │
         │
         └──────────────→  value=confirmed ──→ value=resolved
              oddalertservice（管理員標記）    oddalertservice（管理員確認解決）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| pending | 待處理 | oddalertservice | INSERT 時預設值，告警規則觸發時自動產生 |
| ignored | 已忽略 | oddalertservice | 管理員透過 API 手動標記為忽略，勿需處理 |
| confirmed | 已確認 | oddalertservice | 管理員透過 API 確認告警，準備處理 |
| resolved | 已解決 | oddalertservice | 管理員確認問題已解決後設定 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| oddalertservice | INSERT status=pending | 告警規則檢測觸發 | 自動建立告警，初始狀態為 pending |
| oddalertservice | UPDATE status=ignored | 管理員 API 操作 | 忽略不重要的告警，不再追蹤 |
| oddalertservice | UPDATE status=confirmed | 管理員 API 操作 | 確認告警需要處理 |
| oddalertservice | UPDATE status=resolved | 管理員 API 操作 | 問題已解決，告警關閉 |

**⚠️ 跨服務限制**：

- status 欄位僅能由 oddalertservice 的 API 進行變更，任何其他服務或直接 SQL 操作皆不被允許
- 狀態流轉必須嚴格遵循 `pending → ignored` 或 `pending → confirmed → resolved`，不允許跳躍或逆轉
- 每次 status 變更時，oddalertservice 必須在**同一交易內**自動寫入一筆記錄至 `alert_change_log`，記錄新舊值與操作者帳號
- 其他服務（如 admin_backend_service）僅允許 SELECT 讀取此表，不可直接對 status 欄位進行任何寫入操作

---

### operator_account 欄位

**型別**：text

**值定義與狀態流轉**：

此欄位用於記錄最後操作此告警的管理員帳號。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| null | 無操作者 | — | 告警 INSERT 時預設值，表示僅由系統自動觸發，尚未有人處理 |
| {username} | 操作者帳號 | oddalertservice | 每次透過 API 變更 status 時，從認證資訊（JWT / req.user）自動注入 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| oddalertservice | INSERT operator_account=null | 告警觸發 | 初始無操作者 |
| oddalertservice | UPDATE operator_account={user} | status 變更時 | 自動從認證資訊注入，記錄處理人員 |

**⚠️ 跨服務限制**：

- 不允許請求參數自行指定 `operator_account`，必須由 API 後端從已驗證的 Session/Token 中提取並強制寫入，防止身份偽造
- 其他服務不可修改此欄位

---

### level 欄位

**型別**：character varying

**值定義與狀態流轉**：

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| yellow | 黃燈警告 | oddalertservice | 告警規則檢測值超過黃燈閾值但未達紅燈時，INSERT 時設定 |
| red | 紅燈警報 | oddalertservice | 告警規則檢測值超過紅燈閾值時，INSERT 時設定 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| oddalertservice | INSERT level=yellow 或 red | 依規則閾值判斷 | 對比 `threshold_snapshot` 決定，插入後不可變更 |
| oddalertservice | SELECT WHERE level='red' | 優先處理 | 紅燈告警應優先檢視與處理 |

**⚠️ 跨服務限制**：

- level 與 `rule_code`、`source`、`game_id` 等欄位同為**不可變動的業務鍵**，INSERT 後任何服務皆不可修改
- 其他服務查詢時可利用此欄位區分告警嚴重程度（如：儀表板優先顯示 `level=red` 的 pending 告警）

---

### rule_code 欄位

**型別**：character varying

**值定義與狀態流轉**：

此欄位為固定規則代碼，對應後端檢測器類型。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| odds_implied_probability_divergence | 隱含機率分歧 | oddalertservice | 檢測到不同資料源間的隱含機率差異過大時 |
| odds_spike | 賠率驟升 | oddalertservice | 賠率在短時間內異常飆升時 |
| odds_flutter | 賠率劇烈波動 | oddalertservice | 賠率在短時間內頻繁變動時 |
| odds_stale | 賠率凍結 | oddalertservice | 賠率長時間未更新時 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| oddalertservice | INSERT rule_code | 依觸發規則類型 | 插入後不可變更 |
| oddalertservice | SELECT WHERE rule_code | 分類查詢與統計 | 用於依規則類型篩選告警 |

**⚠️ 跨服務限制**：

- rule_code 為**不可變動的業務鍵**，INSERT 後任何服務皆不可修改
- 規則代碼由系統定義，不允許動態新增或變更，若需擴充需透過版本發布流程

---

### detail 欄位

**型別**：jsonb

**值定義與狀態流轉**：

儲存觸發告警時的詳細上下文資訊（JSON 物件），為觸發瞬間的**證據快照**。

| 服務 | 操作 | 說明 |
|------|------|------|
| oddalertservice | INSERT 寫入 | 由檢測模組在 INSERT 時寫入，包含觸發的原始數據（如各資料源價格、計算過程） |
| oddalertservice | SELECT（明細查詢） | 僅在查看單筆告警明細時載入，列表查詢不應選取此欄位以提升效能 |

**⚠️ 注意**：

- detail 為**不可變更**的 evidence 欄位，不對外提供任何 UPDATE 或覆寫介面
- 此欄位可能非常大，嚴禁在列表查詢或批次操作中使用 `SELECT *` 將其載入

---

### threshold_snapshot 欄位

**型別**：jsonb

**值定義與狀態流轉**：

儲存觸發告警時所套用**閾值設定的快照**（含 red/yellow 數值、維度等），用於事後稽核。

| 服務 | 操作 | 說明 |
|------|------|------|
| oddalertservice | INSERT 寫入 | 由檢測模組在 INSERT 時寫入，記錄觸發當下的閾值參數 |
| oddalertservice | SELECT（明細查詢） | 僅在查看單筆告警明細時載入 |

**⚠️ 注意**：

- threshold_snapshot 為**不可變更**的 evidence 欄位，不對外提供任何 UPDATE 或覆寫介面
- 與 `effective_thresholds` 表不同，此欄位反映的是「告警當下」的配置（事後配置可能已變更），兩者應可互相對照以進行稽核

---

### game_info 欄位

**型別**：jsonb

**值定義與狀態流轉**：

儲存觸發告警時的**比賽基本資訊快照**（隊伍名稱、比分、狀態等），用於前台展示時無需再查詢賽事 DB。

| 服務 | 操作 | 說明 |
|------|------|------|
| oddalertservice | INSERT 寫入 | 由檢測模組在 INSERT 時寫入 |
| oddalertservice | SELECT（列表與明細） | 可安全用於列表展示（相較 detail 輕量），提供比賽摘要資訊 |

**⚠️ 注意**：

- game_info 為**不可變更**的 evidence 欄位，不對外提供任何 UPDATE 或覆寫介面
- 內部結構為非結構化 JSON，若未來需搜尋特定欄位（如 `team_away`），需使用 PostgreSQL JSONB 查詢語法，注意 GIN 索引的設計

---

## Table：alerts_archive

### 用途與限制

此表為 `alerts` 的**歷史歸檔表**，結構與 `alerts` 完全相同。用於儲存已結案或過期的告警資料，以維持主表效能。

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| oddalertservice | INSERT / DELETE | 定時歸檔作業 | 將主表已處理完畢的告警移至 archive，或依留存政策清除過期資料 |
| oddalertservice | SELECT | 歷史查詢 | 用於稽核或查閱歷史告警，不可用於常規業務查詢 |

**⚠️ 跨服務限制**：

- 對外不允許任何 INSERT / UPDATE / DELETE 操作，僅由內部排程或存檔程式寫入
- 此表不對一般業務 API 開放寫入，僅供後台歷史查詢功能唯讀

---

## Table：alert_change_log

### 用途與限制

此表為告警狀態變更的**審計日誌（Audit Log）**，確保每一次人為操作皆有跡可循。

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| oddalertservice | INSERT | `alerts.status` 變更時，同一交易內自動觸發 | 記錄 alert_id、變更欄位（field_name）、新舊值及操作者 |

**⚠️ 跨服務限制**：

- 無任何外部寫入介面，嚴禁任何服務或人工透過 SQL 直接 INSERT / UPDATE / DELETE
- admin_backend_service 可對 `alert_change_log` 進行 SELECT 查詢，例如依 `alert_id` 查閱該告警的完整操作歷程，用於管理後台顯示或合規稽核報表

---

## 常見錯誤（跨服務）

- ❌ 任何服務直接對 `alerts.status` 執行 SQL UPDATE → 必須透過 oddalertservice API 進行，且需記錄 `alert_change_log`
- ❌ oddalertservice 的 API 允許請求參數自行指定 `operator_account` → 應強制從認證資訊注入，防止偽造操作者身份
- ❌ 前端或後台列表查詢時使用 `SELECT *` 包含 `detail` 欄位 → 導致傳輸量過大與效能問題，應區分明細查詢與列表查詢
- ❌ 其他服務嘗試寫入 `monitored_play_modes` 等配置表 → 僅管理服務可修改，oddalertservice 僅具讀取權限以載入規則
- ❌ `alerts` INSERT 後還嘗試 UPDATE `rule_code` 或 `level` → 這些為不可變業務鍵，任何修改皆應被拒絕
- ❌ 狀態流轉不遵循 `pending → ignored` 或 `pending → confirmed → resolved` → 可能導致資料不一致或前端顯示錯誤