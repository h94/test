# crawlerflowservice — DB 操作邊界

> 產出時間：2025-04-12 09:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| pricecenter (Cassandra) | writer / reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **accounts_\* 系列（AU8 / Fortuna888 / HGA / HGA2 / KKK / KU / NK / Panda / TG / TG999）**
  - `password`：僅 crawlerflowservice 新增帳戶時可寫入；須以雜湊儲存；不可在價格處理流程中 UPDATE。
  - `enabled`：僅透過帳戶管理流程修改（0/1）；不可在 `ITransfer.ProcessPrice` 或 `IValidate.ValidateSource` 執行中直接 UPDATE。
  - `closetime`：僅在帳戶關閉或停用操作時設定；不得在一般爬蟲資料比對中覆寫。
  - `handler`：僅帳戶初始化或配置更新時由管理 API 寫入；爬蟲／驗證流程只讀不寫。
  - 注意：`username` 欄位並非所有站點表皆存在（例如 HGA、KKK、KU、NK、TG、TG999 無此欄位），存取前應檢查 schema。

- **actionlog**
  - 所有欄位（`action`、`actionclass`、`detail`、`addtime`、`date`、`user`、`gametype`）僅在爬蟲執行動作後 INSERT；不允許 UPDATE 或 DELETE（日誌不可篡改）。
  - `addtime` 與 `date` 由系統自動設定，不可手動修改。

- **crawler_log**
  - `id`：僅於爬蟲流程開始前 INSERT 產生；不可後續 UPDATE。
  - `machine` / `site`：僅在爬蟲任務初始化時寫入；不得在中途覆寫。
  - `starttime` / `addtime`：僅在任務開始時寫入，不可事後修改。
  - `processcount` / `exectime`：僅在爬蟲完成後一次更新；不可增量累加。

### 讀取規則

- **使用者驗證流程** (`IValidate.ValidateSource`)
  - 需以 `account` 為 WHERE 條件，且 `enabled = 1`（僅啟用帳戶可登入爬蟲）。
  - 若有 `closetime` 非空值，視為已關閉帳戶，不可用於爬蟲任務。

- **爬蟲任務分配** (`ICassandraProvider.GetSiteGames`)
  - 查詢 `sitegames_<gameType>` 或動態 `<site>` 表時，需以 `sitegid` 為條件，且 `enabled = 1`（僅啟用頁面類型可使用）。

- **日誌查詢**
  - `crawler_log`：查詢時常以 `machine` / `site` / `addtime` 範圍作為過濾條件；不支援無條件的全表掃描。
  - `actionlog`：查詢須指定 `date` 分區鍵，可搭配 `user`、`gametype`、`actionclass` 等進行過濾；避免跨分區全掃。

### 不可回傳欄位

- `password`：任何對外 API 或 Kafka 消息中不可帶出；僅內部處理流程在必要時可使用。
- `phone`：原則上不對外回傳；若日誌需記錄應先脫敏。
- `actionlog.detail`：若包含密碼、帳號資訊等敏感內容，必須過濾後方可對外提供。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `CrawlerFlow:{GameType}:{SiteLid}:{SiteGid}` | 爬蟲資料比對時（`CompareData` 寫入前與讀取） | 7200 秒（2小時）；或用於緩存比分狀態，主動失效於比對完成。 |
| SET / GET | `MainSpread:{SiteLid}:{SiteGid}` | 主盤比對時 (`MainSpreadCache`) | 3600 秒；用於暫存主盤值，避免重複比對。 |
| SET / DEL | `KafkaCache:{GameType}:{Site}:{Sitegid}` | Kafka 消息寫入前 (`KafkaCacheData`) | 1800 秒（30分鐘）；Kafka 發送成功後 DEL。 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 帳戶註冊與密碼變更 | accounts-manage-service | 密碼、enabled、handler 等帳戶屬性的寫入維護不由 crawlerflowservice 處理。 |
| 遊戲賽事資料庫的 DDL 建立 | db-admin / infra | `sitegames_<gameType>` 及動態 `<site>` 表的建立與欄位維護不屬本服務。 |
| 最終賠率的計算與推送 | odds-compute-service | crawlerflowservice 僅產出原始賠率，不進行算術轉換或最終格式封裝。 |

---

## 常見錯誤

- ❌ `password` 以明文儲存或傳遞至出口消息 → ✅ 須在 `IValidate.ValidateSource` 內部以雜湊比對；不得寫入 Redis 或 Kafka 日誌。
- ❌ 未檢查 `closetime` 即允許帳戶用於爬蟲 → ✅ 查 `accounts_*` 時必須加入 `WHERE closetime IS NULL` 過濾條件。
- ❌ 對 `crawler_log` 以 `id` 為條件查詢未建立索引 → ✅ 應以 `machine` + `addtime` 組合條件存取，避免全表掃描。
- ❌ 多站點帳戶共用同一 `handler` map 的鍵值擴展錯誤 → ✅ 各 `accounts_*` 表結構一致但 handler 內容可能不同，應按 `account` 區分讀取。
- ❌ 對 `actionlog` 直接執行跨分區查詢 → ✅ 必須包含 `date` 條件；避免全叢集掃描。
- ❌ 對新增站點帳戶表（如 `accounts_TG`、`accounts_TG999`）未檢查 `username` 欄位是否存在即取值 → ✅ 存取前應讀取 schema 或使用安全取值方式，避免空指針。