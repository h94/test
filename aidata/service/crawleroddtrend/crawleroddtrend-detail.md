# crawleroddtrend — DB 操作邊界

> 產出時間：2025-03-16 12:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| 爬蟲賠率歷史表 `odds_his_{game_type}_{game_date}` | **owner** | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |
| 站台帳號表 `accounts_{suffix}` | **reader**（僅查詢啟用站台配置） | 同上 |
| 操作記錄表 `actionlog` | **writer**（爬取過程紀錄） | 同上 |

### 寫入限制

- **`odds_his_*`**：僅 `crawleroddtrend` 爬蟲排程可寫入；寫入時 `game_type` 與 `game_date` 必須對應當前批次；禁止人工 INSERT / UPDATE。
- **`odds_his_*`** 之 `logs`：附加歷史記錄（append），不可覆蓋或刪除；每筆 log 內 `AddTime` 須遞增。
- **`actionlog`**：本服務僅能 INSERT 新的動作記錄（`action`、`actionclass`、`detail` 等），不可修改或刪除既有紀錄；`date`（分區鍵）由排程日期決定，`addtime` 為實際執行時間。
- **`accounts_*`**：本服務**不寫入**任何帳號表（`username`、`password`、`phone`、`handler` 等均為唯讀）；即使 handler 內含連線參數亦無權異動。

### 讀取規則

- **賠率趨勢查詢**（`GET /trend` 等 API）：WHERE `site = ?`、`sitelid = ?`、`sitegid = ?`、`mode = ?`，原因：僅回傳指定賽事與賠率模式的歷史曲線。
- **爬蟲任務觸發前**：查 `accounts_*` 表 `enabled=1` 且 `closetime IS NULL` 取得啟用站台清單；停用或已關閉的站台不應產生爬蟲任務。
- **擷取帳號配置**：讀取 `accounts_*` 的 `handler` 欄位（map<text, text>）以取得站台登入或爬取參數，但需確保該資訊僅用於內部排程，不可透過 API 外洩。

### 不可回傳欄位

- **`accounts_*` 表**：`password`、`phone`、`handler`（內含憑證或敏感參數） — 任何對外 API 都不可洩漏登入憑證與個資；即使內部回傳也應遮蔽。
- **`actionlog` 表**：`detail` 可能包含原始賠率 JSON 或系統內部資訊，前端／外部系統不得直接存取，僅供內部稽核使用。
- **`odds_his_*` 表**：無全域敏感欄位，但 `logs` 內部的原始 JSON 可能包含 `old`、`new` 等内部編碼，前端僅呈現計算後趨勢值。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET（排程鎖） | `crawler:lock:{site}:{game_type}` | 爬蟲任務開始時 | TTL 300 秒，防止同站台同類型重複爬取 |
| GET（最新賠率快照） | `trend:latest:{site}:{sitelid}:{sitegid}:{mode}` | 查詢最新一筆賠率時 | TTL 60 秒，減少 DB 讀取 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 帳號密碼管理（建立、啟用、停用） | `admin` 或 `account` 服務 | `accounts_*` 表僅供查詢啟用站台，密碼欄位本服務無權寫入 |
| 賠率即時推送（WebSocket） | `oddrealtime` | 本服務僅提供歷史趨勢資料，即時更新由另一服務處理 |
| DB 表格自動建立與遷移 | `schema-migration` | `odds_his_{game_type}_{game_date}` 動態表由排程任務確保建立時機 |

---

## 常見錯誤

- ❌ 在爬蟲排程中 delete 或 update `odds_his_*` 的 `logs` 記錄 → ✅ 僅允許 append，所有變更應寫入新 log。
- ❌ 查詢趨勢時未過濾 `enabled=1` 站台 → ✅ 應先依 `accounts_*` 啟用狀態決定是否抓取/顯示該站台資料。
- ❌ 直接回傳 `accounts_*` 中的 `password` 欄位給前端 → ✅ 任何 API 回傳都必須明確排除該欄位（或使用 DTO 過濾）。
- ❌ 將 `actionlog.detail` 直接提供給外部使用者 → ✅ 該欄位僅供內部記錄，應與面向使用者的趨勢數值嚴格分離。