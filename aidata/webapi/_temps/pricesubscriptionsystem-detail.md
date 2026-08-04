# pricesubscriptionsystem — DB 操作邊界

> 產出時間：2025-04-10 17:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| pricecenter Cassandra | reader / writer | Schema：[db/pricecenter.json](../../db/pricecenter.json) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

**由本服務寫入的表**
- `alertlog`：由 `AlertLogDataProvider` 寫入，所有欄位（`site`、`gtype`、`sitegid`、`gid`、`content`、`addtime`、`league`、`team1`、`team2`、`gdate`、`gtime`）均為必填，不得缺漏或為空；`addtime` 為 Unix 秒，不可重複插入相同組合。
- `actionlog`：由內部排程或 Hub 寫入，強制寫入 `date` 分區鍵（格式 `yyyy-MM-dd`），且必須同時提供 `action`、`actionclass`、`user`、`gametype`；寫入時 `addtime` 應精確到毫秒級（如 `yyyy-MM-dd HH:mm:ss.SSS`），`detail` 為有效 JSON。
- `kupages`：僅允許透過 `ManagerDataProvider` 以 `pagename` 為主鍵 UPDATE `adddate`；不支援 INSERT 或 DELETE。

**唯讀表（本服務嚴禁寫入）**
- `accounts_*` 系列（如 `accounts_AU8`、`accounts_Fortuna888` 等）：僅供讀取，帳號狀態（`enabled`、`closetime`、`password`、`handler`）一律由 pricecenter 管理後台異動。不同表結構略有差異（例如部分表無 `username` 欄位），查詢時須明確列舉所需欄位，避免 `SELECT *`。
- `sitegames_{gameType}` / `odds_{gameType}` 系列：數據由外部爬蟲或同步服務維護，本服務不得寫入。

### 讀取規則

- `accounts_*`：必須以 `account` 主鍵精確查詢（`WHERE account = ?`）；應用層須強制校驗 `enabled = 1` 且 `closetime` 為空（或 NULL），任一條件不符即視為無效帳號，終止後續流程。查詢時應明確指定所需欄位（如 `account`, `enabled`, `closetime`, `handler`, `phone` 等），避免 `SELECT *` 誤取敏感欄位。
- `actionlog`：查詢必須包含 `date` 分區鍵；建議同時過濾 `gametype` 與 `user`（聚簇鍵），避免全分區掃描。
- `sitegames_{gameType}` / `odds_{gameType}`：查詢時須指定 `site` 並使用與表名相符的 `gameType`；常用條件為 `sitegid = ?`，或組合 `sitelid` + `gdate`，若未命中分區鍵將觸發 `ALLOW FILTERING`，應禁止。
- `alertlog`：主要用於寫入，若需查詢應優先使用 `site` 與 `gdate` 範圍條件，並搭配 `gid`、`team1`、`team2` 等過濾，嚴防全表掃描。
- `kupages`：可透過 `pagename` 主鍵點查，用於確認頁面最後更新時間。

### 不可回傳欄位

- `password`（所有 `accounts_*` 表）：任何對外 API 均不得回傳密碼內容（包含雜湊值），僅可回應「是否已設定」的狀態。
- `handler`（所有 `accounts_*` 表）：若包含第三方金鑰（如 `api_key`、`secret`），回傳前必須移除；僅允許暴露無敏感資訊的配置鍵。
- `phone`（所有 `accounts_*` 表）：視為個人資料，前端展示時須脫敏處理（如中間四碼隱碼），後端應避免直接完整回傳；查詢時若非必要，不應選取此欄位。
- `sitegames_*` / `odds_*` 的賠率原始字串（`ha`、`rbha` 等）：不建議直接暴露給終端使用者，應透過領域 API 轉換為結構化資料。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| — | — | — | pricecenter 操作未使用 Redis 快取 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 帳號啟用／停用 | pricecenter 管理後台 | 本服務僅查詢 enabled 狀態 |
| 密碼設定與管理 | pricecenter 管理後台 | 本服務不處理密碼 CRUD |
| 各站台玩法設定同步 | 上游 pricecenter 同步服務 | 價格訂閱服務僅消費已同步的賠率與玩法，不負責觸發同步流程 |
| 警報記錄（alertlog）的長期分析與歸檔 | 專屬數據分析服務 | 本服務僅負責寫入原生日誌，不實作聚合或統計 |

---

## 常見錯誤

- ❌ 直接讀取 `password` 欄位比對明碼 → 應透過後台 API 進行驗證，不對外洩露密碼欄位
- ❌ 未檢查 `closetime` 是否為空，僅依 `enabled=1` 判斷帳號可用 → 已關閉帳號（closetime 有值）亦不可使用
- ❌ 跨全表掃描 actionlog 查詢 → 須包含 `date` 分區條件，避免影響叢集效能
- ❌ 查詢 `accounts_*` 時使用 `SELECT *` 導致無意間回傳 `password` 或完整 `phone` → 應明確列舉所需欄位，排除敏感資料
- ❌ 對 `actionlog` 進行範圍或不精確的 `date` 過濾導致跨多分區掃描 → 應盡量使用精確 `date = ?` 條件，必要時搭配 `gametype` 與 `user` 以命中聚簇鍵
- ❌ 寫入 `alertlog` 時省略 `league`、`team1`、`team2` 等可選欄位 → 所有欄位均為必填，缺漏將導致寫入失敗或數據不完整