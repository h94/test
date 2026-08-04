# crawleragentstandings — DB 操作邊界

> 產出時間：2025-04-12 14:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| pricecenter (Cassandra) | writer / reader | Schema：[db/pricecenter.json](../../db/pricecenter.json) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **`standings` 表**（對應 CPBL 棒球）  
  寫入複合鍵為 `(Site, Date, Partition, SiteTID)`，以 `Site='cpbl.com'`, `SiteLID='CPBL'` 寫入。  
  `Partition` 保留空字串 `''`。寫入前應先刪除同日同分區資料，再以 **upsert** 寫入當日整合結果。

- **`npb_standings` 表**（對應 NPB 棒球）  
  寫入複合鍵為 `(Site, Date, Partition, SiteTID)`，`Partition` 為實質分區（如中央聯盟／太平洋聯盟）。  
  `SiteTID` 為隊伍名稱。其餘欄位 Win/Lose/Draw/PCT/RS/RA 均為整數或文字型態。

- **`NBAStandings` 表**（對應 NBA 籃球，來源 SOFA）  
  寫入複合鍵以 `(Site, Date, Sitetid)` 為主；`Sitelid='NBA'`。  
  `LastWinLose` 為最近 5 場勝負的 JSON 陣列字串；`Partition`/`Conf`/`Div`/`Home`/`Road` 目前多為佔位符 `'0'`。  
  僅 `crawleragentstandings` 可寫入此表。

- **所有 standings 表通用**  
  僅 `crawleragentstandings` 可寫入。寫入前應確保當日同日資料不殘留，可先 `DELETE … WHERE Site=? AND Date=? [AND Partition=?]` 再寫入新資料。  
  **不允許其他服務直接寫入這些表。**

- **`accounts_*` 系列表**（如 `accounts_AU8`、`accounts_Fortuna888`、`accounts_HGA`、`accounts_HGA2`、`accounts_KKK`、`accounts_KU`、`accounts_NK`、`accounts_Panda`、`accounts_TG`、`accounts_TG999`）  
  本服務**僅讀取**這些表，**絕對不可**執行任何 INSERT、UPDATE 或 DELETE。帳號的 CRUD 生命週期由上層平臺服務管理。

- **`actionlog` 表**  
  僅 `crawleragentstandings` 寫入，記錄爬取操作日誌。  
  每次寫入必須提供當日分區鍵 `date`（格式 `YYYY-MM-DD`），**禁止跨日寫入**。  
  `detail` 欄位通常儲存爬取結果的完整 JSON（含 standings 資料），不可包含帳號密碼或金鑰。

### 讀取規則

- **讀取 standings 表**  
  查詢必須搭配 `Site`, `Date`（及 `Partition`，若該表使用），以利用分區與聚簇鍵，避免全表掃描。  
  若該 standings 表內有 `enabled` 控制欄位，前端展示時應過濾 `enabled = 1`。

- **讀取 `accounts_*`**  
  本服務以 `account` 主鍵查詢特定站點代理帳號。**必須過濾 `enabled = 1` 且 `closetime IS NULL`（或等價條件）**，防止使用到已關閉或停用的帳號。  
  注意不同站點為獨立表（例如 `accounts_AU8`、`accounts_Fortuna888`），查詢時必須動態指定對應的表名。

- **讀取 `actionlog`**  
  **任何查詢都必須附帶 `date=?` 條件**（分區鍵），否則會導致全表掃描。  
  典型用法：按 `user` 或 `gametype` 過濾當日某一類操作記錄。

### 不可回傳欄位

- **所有 `accounts_*` 表中的 `password`**：無論對外或內部 API，**嚴禁**以任何形式回傳原始密碼（僅允許內部驗證比對）。
- **所有 `accounts_*` 表中的 `handler`**：若內容包含 session token、內部端點或金鑰，視為敏感欄位，不得直接暴露於外部。
- **所有 `accounts_*` 表中的 `phone`**：屬個人資訊，除必要內部流程外，對外展示時應脫敏處理（如僅顯示末四碼）。

### Redis

本服務程式碼中**未使用** Redis 快取。若未來加入，需在此補充 Key/TTL 說明。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 體育資料源爬取排程與重試 | 外部排程器 / Airflow | `crawleragentstandings` 僅接收觸發並執行資料轉換寫入，不管理排程。 |
| `accounts` 表的帳號建立/啟用/停用 | 後臺管理服務 | 本服務僅讀取 accounts 表，不負責帳號生命週期。 |
| 歷史戰績保留與歸檔 | 數據清洗服務 / DBA 排程 | standings 表預設每日覆蓋當日資料，歷史資料需由其他流程備份。 |

### 常見錯誤

- ❌ 寫入 standings 時未使用複合鍵 `(Site, Date, Partition, SiteTID)` 導致重複寫入多筆  
  → ✅ 應使用 upsert，或先 `DELETE … WHERE Site=? AND Date=? AND Partition=?` 再寫入。
- ❌ 讀取 `accounts_*` 時未檢查 `enabled=1` 與 `closetime`，誤取到已停用帳號  
  → ✅ 查詢條件應加上 `WHERE enabled = 1 AND closetime IS NULL`（依實際型態調整）。
- ❌ 將 `password` 明文回傳至前端或記錄到日誌  
  → ✅ 密碼欄位僅在內部驗證使用，對外 API 須明確排除，且 actionlog 的 `detail` 不得包含密碼。
- ❌ 寫入 `actionlog` 時未使用當日分區鍵，或使用未來日期  
  → ✅ `date` 必須為當日 `YYYY-MM-DD`，否則寫入失敗或造成分區碎片。
- ❌ 查詢 `accounts_*` 時忽略了不同站點使用不同表（如 `accounts_AU8` vs `accounts_TG`）  
  → ✅ 動態組合表名，不可假設所有代理帳號都在同一張表。