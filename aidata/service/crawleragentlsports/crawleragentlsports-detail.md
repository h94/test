# crawleragentlsports — DB 操作邊界

> 產出時間：2025-04-04 10:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## sport

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport MySQL (192.168.9.232) | writer / reader | Schema：[db/sport.json](../../db/sport.json) · 語意：[db/sport-detail.md](../../db/sport-detail.md) |

### 寫入限制

- `BK_SitePlayers`：
  - `Site`, `SiteID`, `Year`, `League`, `Name`, `TeamID`, `Team`, `Record`, `LastUpdateTime`：僅爬蟲代理 `crawleragentlsports` 可寫入；寫入時須以 `Site + SiteID + Year` 作為業務唯一鍵執行 upsert，禁止覆蓋其他服務管理的欄位。
  - `Record`（mediumtext）欄位**只能**寫入原始 JSON，不可進行結構轉換、篩選或解析後再儲存。
  - **嚴禁**直接 DELETE 記錄；更新時僅允許修改 `Record` 與 `LastUpdateTime`，其餘欄位（如 `Name`, `Team`）一經建立即不可異動。
- `ChatRoomHistories_Backup`, `Community_Groups`, `GameUsers_Wallet`, `GameUsers_Wallet_Transactions`, `Notification_Messages`：
  - 爬蟲代理服務**不得**對這些表執行 INSERT / UPDATE / DELETE，僅供必要時讀取。

### 讀取規則

- 查詢 `BK_SitePlayers` 時，必須搭配 `Site`, `SiteID`, `Year` 做等值過濾，以精確定位既有記錄，避免全表掃描與誤更新。
- 若因業務需要讀取 `GameUsers_Wallet` 或其他表，應明確指定所需欄位（例如 `AuthKey`, `Balance`），並以最短查閱範圍操作，不得撈取整個資料列。
- 任何讀取都應參考 `LastUpdateTime` 做資料新鮮度判斷，但不可單靠該欄位決定爬取排程，需結合外部源頭狀態。

### 不可回傳欄位

- `BK_SitePlayers.Record`：原始比賽統計 JSON，不得透過 API 直接回傳給客戶端；應由專門的統計服務解析後提供結構化資料。
- `GameUsers_Wallet.Balance`、`GameUsers_Wallet_Transactions.Amount`：涉及用戶餘額與交易金額，對外回傳時須脫敏或以特定授權機制保護，避免金額洩漏。

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter | reader / writer | Schema：[db/pricecenter.json](../../db/pricecenter.json) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- `accounts_*` 表（如 `accounts_AU8`, `accounts_Fortuna888`, …）：
  - `enabled`、`closetime`：僅限管理後台或帳號維護流程寫入，爬蟲代理服務**不得自行修改**啟用狀態或關閉時間。
  - `password`、`handler`：由帳號管理服務寫入，爬蟲代理僅讀取。
  - `account`（主鍵）：不可異動。
- `actionlog` 表：僅供 `crawleragentlsports` 以 append 方式寫入操作日誌，禁止 UPDATE 或 DELETE。

### 讀取規則

- 爬蟲代理啟動或更換帳號時，讀取 `accounts_*` 表需滿足：
  ```sql
  WHERE enabled = 1
    AND (closetime IS NULL OR closetime > toTimestamp(now()))
  ```
  理由：僅使用「啟用中」且「未到期關閉」的帳號登入外部來源。
- 讀取帳號時，**不應**依賴 `handler` 內容做業務決策，僅用於傳遞給登入模組。

### 不可回傳欄位

- `password`（所有 `accounts_*` 表）：任何 API、日誌或對外輸出皆不得包含密碼明文或雜湊，僅供內部認證使用。
- `phone`：視為個人資料，不對外揭露。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
|（無）   |     |      |            |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 爬蟲帳號的啟用/停用管理 | 後台帳號管理服務 | `crawleragentlsports` 不修改 `enabled` 或 `closetime` |
| 帳號密碼的產生與輪換 | 帳號生命周期服務 | 本服務僅消費既存密碼，不負責建立或變更 |

---

## 常見錯誤

- ❌ 直接將 `accounts_*` 查詢結果（含 `password`）記錄到 log 或回應給前端 → ✅ 應在 log 層遮罩敏感欄位，且 API 回應結構中永不包含 `password`。
- ❌ 爬蟲自行根據內部邏輯將 `enabled` 設為 0 以停用帳號 → ✅ 應僅由帳號管理服務進行狀態變更，爬蟲需透過通知機制觸發管理流程。