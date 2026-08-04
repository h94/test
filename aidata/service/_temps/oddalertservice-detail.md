# oddalertservice — DB 操作邊界

> 產出時間：2025-04-10 14:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## Alert

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Alert PostgreSQL | writer / reader | Schema：[db/Alert.json](../../db/Alert.json) · 語意：[db/Alert-detail.md](../../db/Alert-detail.md) |

### 寫入限制

#### `alerts` 表

- **`id`**：僅由告警發佈模組生成（shortuuid），**不允許任何外部寫入或覆蓋**。
- **`created_at`、`updated_at`**：資料庫自動維護（`DEFAULT now()`），**禁止手動修改**。
- **`status`**：
  - 修改必須通過服務端 API，**嚴禁直接 SQL UPDATE**。
  - 狀態變更必須一併寫入 `alert_change_log`，記錄操作者與新舊值。
  - 允許的狀態流轉為：`pending` → `ignored` 或 `pending` → `resolved`，不允許跳躍或逆轉（具體邏輯由 API 控制）。
- **`operator_account`**：由 API 端從認證資訊注入（`req.user` 或 JWT），**不允許請求參數自行指定**。
- **`detail`、`threshold_snapshot`、`game_info`**：僅供檢測模組在 `INSERT` 時寫入，**不對外提供修改/覆寫介面**，以保留觸發時的證據原貌。
- **`rule_code`、`level`、`source`、`game_id`、`game_type`、`play_mode`、`spread`、`selection`、`league_id`**：插入後**不可變更**，為不可變動的業務鍵。

#### `alerts_archive` 表

- 僅由定時歸檔程式或內部存檔作業寫入，**對外不允許任何 INSERT / UPDATE / DELETE**。

#### `alert_change_log` 表

- **無外部寫入介面**，僅在 `alerts` 狀態變更時由同一交易內自動產生新行。
- 任何試圖手動插入或修改日誌的行為都應被拒絕（可通過權限限制）。

#### 配置相關表（`monitored_play_modes`、`scorethreshold_setting`、`source_type`、`sport_alert_sources`）

- oddalertservice **僅具有讀取權限，不得直接寫入或刪除**這些表。所有配置變更必須透過獨立的後台管理服務進行。
- 若有寫入需求，應呼叫管理服務的 API，並等待配置重載機制同步。

### 讀取規則

- **查詢警報列表**（`alerts`）：
  - 必須支援依 `status`（如 `pending`、`ignored`）篩選以區分待處理與已處理。
  - 常用業務過濾維度：`rule_code`（規則類型）、`level`（`yellow` / `red`）、`game_type`、`source`、`game_id`、`play_mode`、`league_id`。
  - 預設排序：`created_at DESC`，支援分頁。
  - 清單型查詢應避免一次載入所有 JSON 大欄位（`detail`、`threshold_snapshot`、`game_info`），建議明細查看時再個別載入。
- **讀取配置**（`monitored_play_modes`、`scorethreshold_setting`、`source_type`、`sport_alert_sources`）：
  - 用於檢測模組載入規則參數，**不得對外直接暴露這些查詢介面**。
  - 以 `game_type` 為主鍵讀取，若無對應設定則使用服務預設值。
- **查詢存檔**（`alerts_archive`）：通常依 `created_at` 範圍刪除或檢索歷史記錄，不應支援一般業務查詢。

### 不可回傳欄位

- **無特殊隱私欄位**，但建議：
  - 清單 API 勿直接返回完整的 `detail` 和 `threshold_snapshot`，僅在明細 API 中提供。
  - `operator_account` 雖然非高度機敏，但若系統對操作者隱私有要求，可進行部分遮蔽或更嚴格的權限控管。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 告警規則與監控配置的管理（`monitored_play_modes`, `scorethreshold_setting`, …） | AlertBackend 或 ConfigAdmin | oddalertservice 僅讀取配置進行檢測，增刪改由專屬管理後台負責。 |
| 前端操作界面與警報處置流程（忽略、解決等） | AlertBackend / Frontend | oddalertservice 提供變更狀態的 API，但 UI 互動與流程控制歸屬於對應的前端應用。 |
| 原始數據採集與賠率轉換（GameEvent） | oddsservice / pricecenter | 本服務僅消費 Kafka 中的結構化賽事資料，不負責資料來源的連線與轉換。 |
| 過期警報的歸檔與清理排程 | 獨立排程服務或 DBA | 將舊警報移入 `alerts_archive` 由排程任務執行，本服務不實作歸檔邏輯。 |

---

## 常見錯誤

- ❌ 直接於資料庫修改 `alerts.status` 且忘記寫入 `alert_change_log`，導致審查軌跡斷層。  
  ✅ 必須透過 API 統一變更，並在交易中同時寫 log。
- ❌ 誤將 `game_id` 視為內部 `PriceCenter.game.id`，而在關聯時使用錯誤的鍵值。  
  ✅ 應使用 Kafka `GameEvent.game_id`（即 source game ID），此欄位代表來源站台賽事標示。
- ❌ 外部請求攜帶自訂的 `id` 或 `created_at`，導致插入重複或時間錯亂。  
  ✅ `id` 由 shortuuid 生成，時間採預設值，禁止請求攜帶。
- ❌ 管理員試圖直接修改 `detail` 或 `threshold_snapshot` 以調整證據。  
  ✅ 應保留原始快照，若有誤判透過狀態 + comment 欄位記錄，不可竄改來源資料。
- ❌ 忽略配置快取過期，使用舊閾值進行判斷，導致告警漏報或誤報。  
  ✅ 實作配置重載機制或監聽設定變更再啟動重新評估。