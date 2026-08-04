# flowcontrolservice — DB 操作邊界

> 產出時間：2025-04-10 12:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| pricecenter Cassandra | writer | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

#### 帳號相關表（`accounts_*`，例如 `accounts_AU8`、`accounts_Fortuna888`、`accounts_HGA`…）

- `account`：主鍵，僅在帳戶建立時指定，後續禁止任何直接寫入。
- `password`：僅內部帳務或初始化 API 可寫入；須以不可逆雜湊儲存，禁止明文持久化。
- `enabled`：僅後台帳戶管理或有效啟用流程可修改；關閉帳戶（`enabled=0`）後，不得單獨重設為 `1`，須搭配 `closetime` 評估。
- `closetime`：僅於帳戶關閉時寫入一次，寫入後該帳戶應視為永久關閉，不再允許登入或操作。
- `handler`：系統內部擴展邏輯專用，禁止客戶端或外部 API 直接傳入完整 `map` 覆蓋。
- `phone`：個資欄位，僅帳務服務或後台授權流程可更新；一般請求禁止直接寫入。
- `username`：僅在帳戶創建時設定，後續禁止任何 UPDATE。

#### 日誌與操作記錄

- `actionlog`：僅 flowcontrol 內部流程在執行關鍵操作後 **INSERT**；所有欄位（`date`、`addtime`、`user`、`gametype`、`action`、`actionclass`、`detail`）一次性寫入，**禁止任何後續 UPDATE 或 DELETE**。
- `alertlog`：由 `AlertLogDataProvider.WriteLog` 負責 INSERT；所有欄位（`site`、`gtype`、`sitegid`、`addtime`、`content`、`gid`、`league`、`team1`、`team2`、`gdate`、`gtime`）寫入後不可修改或刪除。
- `fixdatalog`：僅 `FixDataProvider` 可對 `fixed`（`0`→`1`）及 `addtime` 執行 **UPDATE**；其餘欄位禁止直接寫入。
- `matches_his_{gameType}_{date}`：`matches`、`playbyplay` 以及（若存在）`simpleplay` 欄位僅允許 **追加寫入**（`SET list = list + ?`），不可覆蓋、不可刪除。
- `odds_his_{gameType}_{date}`：`logs` 欄位僅允許 **追加**（`SET logs = logs + ?`）。
- `inplaysrepadlogs`：`logs` 欄位僅允許 **追加**（`SET logs = logs + ?`）。

#### 遊戲相關

- `sitegames_{gameType}`：`fixed` 欄位僅由 `FixDataProvider.SetGameFixed` 更新（`0`→`1`），已修正的記錄不可回復；`swap` 由內部配對邏輯設定，禁止 API 層直接傳入；其他欄位（例如 `sitegid`、`teamid_a`、`teamid_h`）僅在初次導入時寫入，禁止後續直接 UPDATE。
- `games_{gameType}`：`status`、`match_a`、`match_h`、`match_detail` 等賽果相關欄位僅可由 `GameDataProvider.UpdateGames` 更新，禁止手動 SQL 修改。
- `odds_{gameType}` 與 `odds_{gameType}_view`：賠率資料完全由 pipeline 寫入，**不允許人工或 API 直接 INSERT / UPDATE**；`gid` 建立後不可變更。
- `leagues_{gameType}`、`teams_{gameType}`、`siteteams_{gameType}`：僅對應的 DataProvider 可進行插入與更新，外部服務不得直接寫入。
- `predictbets_{gtype}`：`enabled` 僅由預測流程控制，不允許外部服務隨意切換。
- `settings_league`：預測相關設定，僅內部排程可更新。

### 讀取規則

- **帳號驗證**：讀取 `accounts_*` 時強制過濾 `enabled = 1`；禁用帳號不應參與任何後續業務。
- **告警查詢**：`alertlog` 必須以 `addtime` 範圍為條件（`WHERE addtime >= ?`），防止全表掃描。
- **站點映射查詢**：`sitegames_{gameType}` 必須以 `site` + `sitelid` + `sitegid` 為查詢前綴；通常僅讀取 `fixed = 0` 的記錄。
- **賠率讀取**：`odds_{gameType}` 及 `odds_{gameType}_view` 查詢必須附帶 `gid` 條件，嚴禁無 `gid` 的跨分割區掃描。
- **操作記錄**：`actionlog` 必須以分區鍵 `date` 為前綴，並依序使用聚簇鍵 `addtime`、`user` 範圍查詢；禁止跨日期全表掃描。
- **歷史賽事／賠率**：讀取 `matches_his_*`、`odds_his_*` 時須限定日期分區，禁止無範圍掃描。
- **預測資料**：查詢 `predictbets_*` 時須標明 `gdate` 分區條件，且通常僅讀取 `enabled = 1` 的記錄。
- **聯賽／隊伍**：`leagues_*`、`teams_*` 盡量以 `id` 列表 IN 查詢，避免無 ID 條件全表掃描。

### 不可回傳欄位

- `password`：任何對外 API 均不可回傳明文或雜湊後的密碼。
- `handler`：可能包含內部配置，禁止直接洩漏至前端。
- `phone`：個資欄位，除使用者本人或後台授權外不回傳完整號碼（可考慮遮罩）。
- `actionlog.detail`：操作細節 JSON 可能包含後端敏感資訊，對外輸出前須脫敏或完全排除。
- `games_{gameType}` 的 `siteidmaps`、`otherinfo`、`teams`（內部 JSON 可能含供應商識別碼）：對外時應遮罩或僅輸出必要欄位。
- `odds_*` 的 `Others` 欄位：可能含未審核特殊玩法，對外時須篩選。

---

## Redis

（pricecenter 操作中，本服務不直接使用 Redis；若有獨立快取層由 Infrastructure/Caching 統一管理，Key／TTL 細節見原始碼註解。）

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 帳戶建立／修改 | `accountservice` | `accounts_*` 的啟用／關閉由帳務服務統籌；本服務僅讀取驗證。 |
| 賠率計算與生成 | `oddsservice` | `odds_*` 由賠率管線寫入；本服務僅讀取用於流速控制。 |
| 比賽資料初始匯入 | `dataimportservice` / `crawlerservice` | `games_*`、`sitegames_*` 的 INSERT 由其他管線負責；本服務僅讀取與更新特定欄位。 |
| 比分即時更新 | `scoreservice` / `livescore-ingestion` | `match_h`、`match_a`、`match_detail` 由比分管線更新；本服務僅在被動通知後進行流速評估。 |
| 聯賽／隊伍資料管理 | `sportsdataservice` | `leagues_*`、`teams_*` 的 CRUD 由體育資料管理服務負責。 |
| 預測配置維護 | `predictservice` | `predictbets_*` 的啟用狀態與設定由預測服務維護。 |

---

## 常見錯誤

- ❌ 在遊戲映射流程中直接 UPDATE `sitegames_{gameType}` 的 `fixed` 欄位  
  ✅ 應由 `FixDataProvider` 寫入 `fixdatalog`，再透過告警或排程補償同步更新遊戲映射狀態。
- ❌ 未對 `password` 欄位進行存取遮罩，於 API 回應中直接回傳  
  ✅ 應在序列化前將該欄位設為 null，或使用 DTO 排除。
- ❌ 檢查帳戶時僅按 `account` 查詢，未過濾 `enabled = 1`  
  ✅ 查詢必須加上 `enabled = 1`，避免已停用帳戶參與業務。
- ❌ 在無 `gid` 條件下直接掃描 `odds_{gameType}` 或 `odds_{gameType}_view`  
  ✅ 所有賠率讀取應以 `gid` 為主要篩選條件，避免跨分割讀取放大。
- ❌ 試圖 UPDATE 或 DELETE `actionlog` / `alertlog` 中的歷史記錄  
  ✅ 這些表為僅附加（append-only）日誌；任何修正應寫入新的記錄，不應刪改既有資料。
- ❌ 直接 INSERT 或手動更新 `matches_his_*`、`odds_his_*` 的整個欄位內容  
  ✅ 必須使用追加語法（如 `SET logs = logs + ?`），保留完整歷史軌跡。
- ❌ 未透過 `sitegames_*` 映射，直接以外部 `sitegid` 查詢 `games_*`  
  ✅ 必須先從 `sitegames_*` 取得內部 `gid`，再查詢 `games_*`；外部識別碼不可直接作為 `games_*` 的查詢條件。
- ❌ 對外 API 直接輸出 `odds_*` 的原始 `Others` 欄位  
  ✅ 應過濾未授權或未審核的玩法，僅輸出前端支援的玩法賠率。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Games PostgreSQL（`games_bk`、`games_bm`、`games_bs`、`games_ck` 等） | reader / conditional writer | Schema：[db/games.json](../../db/games.json) · 語意：[db/games-detail.md](../../db/games-detail.md) |
| Games Cassandra（`sitegames_*`、`matches_his_*`、`odds_his_*`、`odds_*`） | reader / writer | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |
| Games Cassandra（`leagues_*`、`teams_*`、`predictbets_*`） | reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

#### PostgreSQL `games_{gameType}`（games_bk、games_bm、games_bs、games_ck）
- `status`：僅 `GameDataProvider.UpdateGames` 流程可寫入；值須控制為合法枚舉（`PreGame`、`InProgress`、`Final` 等）。
- `match_h`、`match_a`：僅由比分結果同步流程寫入；不可手動 UPDATE。
- `match_detail`：僅由賽事詳情同步流程寫入；更新時須為完整局/節分數陣列，不可部分覆蓋。
- `resultinfo`、`otherinfo`：由 `SiteGameRedisService` 合併邏輯寫入；外部服務不得直接 INSERT / UPDATE。
- `siteidmaps`：各站點 GID 映射，僅在初始匯入或站點補償時寫入；後續不允許直接覆蓋整個欄位，須合併更新。
- `teams`、`team_h`、`team_a`、`teamid_h`、`teamid_a`：僅於賽事建立時一次性寫入；後續不得修改（如需修正須透過專用補償流程）。
- `source`、`lid`、`gdate`、`gtime`：建立後不可更改。
- `create_at`：僅 INSERT 時由系統自動寫入，不允許任何後續 UPDATE。

#### Cassandra `sitegames_{gameType}`
- `fixed`：僅 `FixDataProvider.SetGameFixed` 流程可修改（`0`→`1`）；已修正的記錄不可復原為未修正。
- `swap`：僅內部主客互換配對邏輯可設定；不得由 API 層直接傳入。
- `site`、`sitelid`、`sitegid`：建立後不可變更。
- 所有欄位均不允許 DELETE 操作；若需停用應透過 `fixed` 標記。

#### Cassandra 歷史與賠率相關
- `matches_his_*`：`matches`、`playbyplay`、`simpleplay` 僅允許 **追加寫入**（`SET x = x + ?`），不可覆蓋或刪除。
- `odds_his_*`：`logs` 欄位僅允許 **追加**（`SET logs = logs + ?`）。
- `odds_*`：賠率資料由 pipeline 寫入，**不允許人工或 API 直接 INSERT / UPDATE**；`gid` 建立後不可變更。

#### Cassandra 聯賽 / 隊伍
- `leagues_{gameType}`、`teams_{gameType}`：僅對應的 `GameDataProvider` 可進行插入與更新；外部服務不得直接寫入。

#### 預測與設定
- `predictbets_{gtype}`：`enabled` 僅由預測排程控制；不允許外部服務隨意切換。
- `settings_league`：僅內部排程可讀寫。

### 讀取規則

#### 遊戲資料查詢（`games_{gameType}`）
- 須以 `gdate` 為日期分區條件，搭配 `lid` 或 `status` 進行過濾，避免全表掃描。
- 查詢特定來源遊戲時，須以 `source` + `siteidmaps` 中對應 `SiteGID` 為條件（透過 `sitegames_*` 映射後再查 `games_*`）。
- 流速控制讀取時僅需 `status IN ('PreGame', 'InProgress')` 的記錄；`Final` 狀態若為歷史補償才讀取。

#### 站點映射查詢（`sitegames_{gameType}`）
- 必須以 `site` + `sitelid` + `sitegid` 為查詢前綴。
- 通常僅查詢 `fixed = 0` 的記錄（未修正的活躍映射）。
- 禁止跨 `site` 或無 `site` 條件的全表掃描。

#### 賠率查詢（`odds_{gameType}`）
- 必須以 `gid` 為查詢條件，不得使用無 `gid` 的跨分區掃描。
- 滾球賠率（`rbha`、`rbou`、`rbothers`）與賽前賠率（`ha`、`OU`、`Others`）須明確區分讀取。

#### 歷史記錄查詢（`matches_his_*`、`odds_his_*`）
- 必須以日期分區為前綴（表名後綴日期或 `date` 欄位），禁止跨日期全表掃描。

#### 聯賽 / 隊伍查詢
- `leagues_*`、`teams_*`：通常以 `id` 列表 IN 查詢；避免無 ID 條件的全表掃描。
- 查詢 `teams_*` 時應搭配 `lid` 限定聯賽範圍。

#### 預測查詢（`predictbets_*`）
- 必須以 `gdate` 為前綴，且通常僅讀取 `enabled = 1` 的記錄。

### 不可回傳欄位

- `siteidmaps`：內部站點 GID 映射可能包含供應商敏感資訊；對外 API 應遮罩或僅輸出必要站點。
- `teams`：內部 JSON 可能包含供應商專屬識別碼；對外應僅輸出名稱與內部 ID。
- `otherinfo`：可能包含內部標記或未清理的原始資料；需經脫敏處理再輸出。
- `odds_*` 中 `Others` 欄位：可能包含未審核的特殊玩法賠率；對外輸出時須經篩選。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| GET / SET | `sitegame:{site}:{siteLID}:{siteGID}` | 查詢站點遊戲映射時，優先讀取 Redis 快取 | TTL 依 `SiteGameRedisService` 配置；寫入後由排程或事件主動失效 |
| GET / SET | `game:{gid}` 或 `game:{source}:{gid}` | 取得比賽基本資訊時 | 與資料庫 `games_*` 同步；主動更新時刷新快取 |
| DEL | `sitegame:{site}:{siteLID}:{siteGID}` | 當 `sitegames_*` 的 `fixed` 變更或遊戲結束時 | 由 `FixDataProvider` 或補償排程觸發 |
| HSET / HGET | `odds:{gid}:{mod}` | 取得特定玩法的賠率快取 | TTL 與賠率更新頻率相關；通常短 TTL（≤60s）或事件驅動失效 |
| HSET / HGET | `rbodds:{gid}:{mod}` | 滾球賠率快取 | TTL 較短（≤30s）；滾球階段頻繁更新 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 比賽資料初始匯入 | `dataimportservice` 或 `crawlerservice` | `games_*`、`sitegames_*` 的 INSERT 由資料匯入 pipeline 負責；本服務僅讀取與更新特定欄位。 |
| 賠率生成與推送 | `oddsservice` | `odds_*` 表由賠率服務寫入；本服務僅讀取用於流速控制判斷。 |
| 比分即時更新 | `scoreservice` 或 `livescore-ingestion` | `match_h`、`match_a`、`match_detail` 由比分 pipeline 更新；本服務僅在被動通知後進行流速評估。 |
| 聯賽 / 隊伍資料管理 | `sportsdataservice` | `leagues_*`、`teams_*` 的 CRUD 由體育資料管理服務負責。 |

---

## 常見錯誤

- ❌ 在流速控制流程中直接 UPDATE `games_*` 的 `status` 欄位  
  ✅ `status` 變更應由比分或賽事狀態 pipeline 驅動；本服務僅讀取狀態進行決策，不主動變更。

- ❌ 未透過 `sitegames_*` 映射，直接以外部 `sitegid` 查詢 `games_*`  
  ✅ 必須先從 `sitegames_*` 取得內部 `gid`，再查詢 `games_*`；外部識別碼不可直接作為 `games_*` 的查詢條件。

- ❌ 嘗試 `SET siteidmaps = ?` 覆蓋整個 JSON，遺失其他站點映射  
  ✅ 必須使用 JSON 合併操作（如 `jsonb_set` 或應用層合併後寫回），確保不遺失已存在的站點資料。

- ❌ 在無 `gdate` 條件下查詢 `games_*` 或 `predictbets_*`  
  ✅ 必須帶上 `gdate` 範圍過濾，避免跨分區全表掃描造成效能問題。

- ❌ 直接覆蓋 `matches_his_*` 的 `matches` 或 `playbyplay` 欄位  
  ✅ 必須使用追加語法（`SET matches = matches + ?`），保留完整歷史紀錄。

- ❌ 從 Redis 取得 `sitegame` 後未檢查 `fixed` 狀態即使用  
  ✅ Redis 快取可能滯後；若映射結果涉及寫入或關鍵決策，應同時驗證資料庫中的 `fixed` 欄位。

- ❌ 對外 API 直接輸出 `odds_*` 的原始 `Others` 欄位  
  ✅ 應過濾未授權或未審核的玩法，僅輸出前端支援的玩法賠率。

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Predict Cassandra（`betpool_games`, `betpool_bets`） | reader | Schema：[db/predict.json](../../db/predict.json) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |
| Predict Cassandra（`activities_cycles`, `activities_record`, `activities_winneraccounts`） | reader | Schema：[db/predict.json](../../db/predict.json) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |
| Predict Cassandra（`calculatelog`, `killeraccounts_BK`） | writer | Schema：[db/predict.json](../../db/predict.json) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **`calculatelog`**  
  - `done`：僅在計算流程成功完成後由本服務寫入為 `1`；寫入前必須先確保對應 `weekid` + `weekdate` 的記錄已存在（由排程預先 INSERT）；嚴禁將 `done` 從 `1` 改回 `0`。  
  - `weekid`、`weekdate`、`addtime`：建立時寫入，後續不允許任何 UPDATE 操作。

- **`killeraccounts_BK`**  
  - 整批數據由本服務於計算殺手帳戶後 **INSERT**；更新邏輯為先對同一 `lid` + `cid` 分區執行 **DELETE**，再批次 **INSERT** 最新排名資料。  
  - 禁止使用部分 UPDATE 或直接修改單一帳戶的 `avgodd` 或任何欄位；若需修正必須重新觸發完整計算流程。  
  - 不可跨分區刪除後未完整寫回，應保持交易一致性（或使用 Cassandra Batch 保證原子性）。

### 讀取規則

- **遊戲狀態查詢（`betpool_games`）**  
  必須以 `id` 為查詢條件（單一遊戲），或使用 `status = 1 AND endtime >= ? AND payout = false` 並嚴格限制結果集大小（如搭配 LIMIT 及 `ALLOW FILTERING` 僅在條件合理時使用）；禁止無條件全表掃描。

- **投注記錄查詢（`betpool_bets`）**  
  必須以 `gid` 為分區鍵，並搭配 `account` 或 `id` 聚簇鍵進行查詢；禁止跨 `gid` 或無 `gid` 的掃描。

- **活動周期查詢（`activities_cycles`）**  
  以 `site` 為分區鍵，並透過 `activityevent` 和 `cid` 定位當前周期；避免跨站點全表掃描。查詢當前有效周期時需附加 `startdate <= today AND enddate >= today`。

- **用戶參與記錄（`activities_record`）**  
  必須同時提供 `site`、`eventname` 與 `account`；禁止無 `account` 條件的查詢。

- **贏家排行榜（`activities_winneraccounts`）**  
  以 `site` + `activityevent` + `cid` 為查詢前綴；如需排序或分頁，應在查詢時加入 `rank` 範圍限制，避免大批量排序操作。

- **計算狀態（`calculatelog`）**  
  只能通過 `weekid` 查詢，禁止跨 `weekid` 掃描。

- **殺手帳戶讀取（`killeraccounts_BK`）**  
  必須指定 `lid` + `cid` 分區；若需全聯賽排行應在應用層處理，不得無條件全表掃描。

### 不可回傳欄位

- `betpool_games.winresult`：在 `payout = false`（未派獎）前，不得對外回傳最終勝出選項，包含透過內部 API 傳遞給非核心結算服務。
- `betpool_bets.profitzcoin`、`betpool_bets.betzcoin`：回傳投注明細時，須確保請求者為該筆投注的 `account` 所有者，或通過後台權限檢查。
- `activities_winneraccounts` 中的 `profitpoint`、`predictcount`：在對應週期尚未完成計算（`calculatelog.done = 0`）時，不可洩露給前端或非管理型 API。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| GET | `betpool:game:{id}` | 檢查遊戲可投注性時優先讀取快取 | TTL 至遊戲結束時間；當 `status` 或 `payout` 變更時主動 DEL |
| SET | `betpool:game:{id}` | 從 DB 載入後寫入 | 同上 |
| SETNX | `flowcontrol:calc_lock:{weekid}` | 開始計算週排名或殺手帳戶前獲取分散式鎖 | TTL 10~30s；計算完成後 DEL，確保不重複執行 |
| HSET / HGET | `betpool:active_gids` | 快取當前可投注遊戲集合 | 由排程定時整批刷新，TTL 可設 60s；遊戲下線時立即移除 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 預測遊戲資料管理 | `predict-admin` | `betpool_games` 的建立、狀態變更、派獎設定等由後台管理服務維護。 |
| 投注記錄即時查詢 | `betservice` | 使用者投注歷史、未結算投注等即時查詢由投注服務提供；本服務僅讀取用於流量計算。 |
| 活動週期管理與獎勵發放 | `activityservice` | `activities_cycles` 的建立／關閉、`activities_winneraccounts` 的獎勵發放由活動服務負責。 |

---

## 常見錯誤

- ❌ 在 `calculatelog.done = 0` 時直接回傳 `activities_winneraccounts` 的排名資料  
  ✅ 應先確認對應週期的計算已完成，否則回傳空列表或明確標示結果未完成。

- ❌ 跨 `gid` 全表掃描 `betpool_bets` 進行統計  
  ✅ 必須以 `gid` 為前綴，透過分頁或應用層聚合；若需跨遊戲統計，應由獨立的批處理服務執行，不可在線上請求中觸發。

- ❌ 在未鎖定的情況下同時更新 `killeraccounts_BK`  
  ✅ 使用 Redis 分散式鎖（`flowcontrol:calc_lock:{weekid}`）保護整個計算與寫入流程，避免重複寫入或競態條件。

- ❌ 將 `betpool_games.winresult` 在 `payout` 更新前推送至前端  
  ✅ 必須等到 `payout = true` 後才可對外揭露最終結果；若需即時顯示中獎狀態，應透過獨立的獎勵服務查詢。