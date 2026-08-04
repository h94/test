# tradegameservice — DB 操作邊界

> 產出時間：2025-08-07 15:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## tradegame

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| tradegame (Cassandra) | owner | Schema：[db/tradegame.md](../../db/tradegame.md) · 語意：[db/tradegame-detail.md](../../db/tradegame-detail.md) |

### 寫入限制

- **resultlogs.status**：僅可由結算流程（`recalculate.py`）更新（0=待結算/重算中，1=已結算）。其他任何服務或 API 不得直接寫入此欄位。
- **resultlogs.addtime / gdate / gtype / gid / lid**：由比賽結果資料寫入服務（非本服務）負責插入，本服務僅讀取並更新 status 欄位。
- **stock_holdings_\*.stock_num**：僅可由交易下單流程（`trade.py: write_trade_log`）執行增減（對應 buy/sell），及結算流程（`recalculate.py`）批量更新（如歸零或調整）。禁止直接手動 UPDATE。
- **stock_holdings_\*.winloss**：僅可由結算流程（`recalculate.py`）寫入，值為 `'W'`（贏）、`'L'`（輸）或空字串（未結算）。不允許交易流程或其他 API 直接設定。
- **stock_holdings_\*.trade_history**：僅可由交易下單流程（`trade.py`）以序列化 JSON 字串寫入（記錄每次買賣詳情，含 stock_price、trade_type、num、profitpoint、trade_time 等），不允許外部直接拼接或修改。
- **stock_holdings_\*.addtime / mode / oddtype / ratio / spread**：由交易模組（`trade.py`）在建立或更新持股時一次性寫入，後續不可更改（玩法及賠率等參數一經建立即鎖定）。
- **stock_holdings_\*.account / mode_spread_type / gdate / lid / gid**：集群鍵，在持股記錄建立時設定後不可修改。
- **mode_spread_type** 為模式、讓分、賠率類型的組合鍵（格式 `{mode}_{spread}_{oddtype}`，例：`'HA_1.5_H'`），由服務端根據 get_spread_and_ratio 自動生成，不允許外部傳入或手動修改。
- **spread** 與 **ratio** 由 `trade.py` 解析球頭字串後寫入，spread 為讓分量化整數（如 -2 對應讓 -1.5 球），ratio 為賠率比例整數（通常乘 100），兩者皆不可由外部直接設定。
- **settings_gametype.gametype**：作為主鍵，僅可由管理 API（`/settings/gametype`）進行新增；後續不可更改。`enabled` 欄位僅可由管理後台進行切換，不允許交易流程直接修改。`lids` 欄位為關聯聯賽 ID 列表，須使用逗號分隔字串格式，由管理後台設定，更新時需確保引用現有聯賽 ID。
- **settings_score.gtype, layer, lid**：作為組合主鍵，一經建立不可變更。`rules` 欄位為 JSON 格式，必須符合預定義的評分規則 schema（包含 1X2、HA、OU 的差值閾值），僅可透過 `/settings/score` API 寫入，結算流程只讀取。
- **settings_stock.gtype, layer, lid, gid**：作為組合主鍵。`initial_stock_num` 為股票發行數量，僅可透過 `/settings/stock` API 設定。`rules` 為 JSON 格式的買賣時間規則，需通過服務端驗證。`gdate` 可選，用於特定場次設定。這些欄位僅可由管理後台設定，交易流程讀取。
- **settings 相關表的 addtime**：在設定建立或更新時由系統自動寫入時間戳，外部不可直接指定。

### 讀取規則

- **resultlogs** 查詢必須提供完整主鍵條件 `gdate`、`gtype`、`gid`（可搭配 `lid` 精確定位），**嚴禁全表掃描或使用 ALLOW FILTERING**。通常用於判斷結算狀態以驅動重算或交易開關。
- **stock_holdings_\*** 查詢：
  - 一般使用者查詢必須強制帶入 `account`（當前登入者）及分區鍵 `gdate`（格式 YYYY-MM-DD），僅可查自身單日持股。
  - 管理後台查詢可省略帳戶限制，但必須指定 `gdate` 及至少一個集群鍵（如 `lid`、`gid`），不可無分區鍵掃描。
  - 查詢單筆持股需提供完整主鍵：`gdate`, `lid`, `gid`, `account`, `mode_spread_type`。
  - 查詢交易歷史時，`trade_history` 須透過程式解析（`json.loads`），並按 `mode_spread_type` 過濾比對。
- **禁止對 stock_holdings 或 resultlogs 使用模糊查詢**（LIKE、正則等），所有 WHERE 條件必須為精確匹配或範圍查詢（僅限 `addtime` 等非鍵欄位的有限範圍）。
- **settings_gametype** 查詢必須提供 `gametype`（主鍵），嚴禁無條件全表掃描。交易流程讀取時需過濾 `enabled=1`，以確保只處理啟用的遊戲類型。
- **settings_score** 查詢需提供分區鍵 `gtype` 及 `layer`，可選擇性加入 `lid` 集群鍵精確定位，用於結算時取得指定遊戲類型與聯賽的評分規則。
- **settings_stock** 查詢需提供分區鍵 `gtype` 及 `layer`，並可加入 `lid`、`gid` 集群鍵，用於取得特定場次的股票交易規則與初始股票數。

### 不可回傳欄位

- **stock_holdings_\*.trade_history**：對一般使用者（前端）不回傳原始 JSON，或僅回傳交易摘要（如最後幾筆方向與數量），避免暴露完整歷史細節。管理後台可視需求回傳完整內容，但需注意資料量。
- **resultlogs** 無需遮蔽，status、日期、遊戲 ID 等皆可回傳。

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| pricecenter (Cassandra) | owner | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **accounts_\*.password**：僅可經由專屬註冊或密碼修改流程寫入（雜湊儲存），不可由一般交易或查詢 API 直接 UPDATE。
- **accounts_\*.phone**：僅可經由手機驗證或帳號綁定流程寫入，不可隨意改寫。
- **accounts_\*.enabled**：僅管理後台或系統排程可更改（1=啟用，0=停用），使用者不可自行設定。
- **accounts_\*.closetime**：僅當帳戶被停用或關閉時，由系統自動寫入（對應 enabled=0），不可由前端使用者觸發寫入。
- **accounts_\*.handler**：僅管理後台或配置流程可寫入（map<text, text> 型態的客製化設置），交易 API 不可修改此欄位。各平台（AU8、Fortuna888、HGA、HGA2、KKK、KU、NK、Panda、TG、TG999）的 handler 配置彼此獨立。
- **accounts_\*.username**：僅註冊流程可寫入，後續不可更改（部分平台無 username 欄位，如 HGA、KKK、KU、NK、TG、TG999）。
- **actionlog**：僅供系統記錄操作日誌時以 INSERT 方式寫入，不允許 UPDATE 或 DELETE 操作。各欄位（action、actionclass、detail、addtime 等）由內部日誌模組一次性寫入，不可事後修改。action 記錄具體操作名稱（如 `'Split'`），actionclass 記錄操作分類（如 `'SiteTeam'`），detail 為 JSON 字串記錄操作詳情。

### 讀取規則

- **accounts_\*** 查詢：
  - 交易時查詢使用者帳戶需過濾 `enabled=1`，僅啟用狀態的帳戶可進行下單、查詢庫存等操作。
  - 管理後台可查詢所有帳戶，不受 enabled 限制。
  - 查詢特定平台帳戶時，需指定對應的 accounts_ 表（如 accounts_AU8、accounts_TG 等），不可跨表查詢。
- **actionlog** 查詢：
  - 必須指定 `date`（分區鍵），並可加入 `addtime`、`user`、`gametype` 等集群鍵進行範圍查詢，嚴禁全表掃描。
  - 一般使用者僅可查詢自身操作記錄（WHERE user=? AND date=?）。

### 不可回傳欄位

- **accounts_\*.password**：任何對外 API 皆不可回傳（即便遮蔽，也不應出現）。
- **accounts_\*.phone**：對外 API 不可回傳完整手機號碼，查詢時應僅回傳遮蔽版本（如 09*****678）或不回傳。
- **accounts_\*.handler**：內部配置映射，對外不回傳（map 結構與內部 key 不應暴露）。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Games (PostgreSQL) | reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- **所有欄位**：本服務對 games_bk、games_bm、games_bs、games_ck 四張比賽表僅有讀取權限，**禁止任何 INSERT / UPDATE / DELETE 操作**。比賽資料的寫入、更新（如比分、狀態）由其他專職資料爬取服務負責。

### 讀取規則

- **交易可用比賽查詢**：提供前端可下注的比賽列表時，必須過濾 `status` 為可進行交易的有效狀態（例：`'PreGame'`、`'InPlay'`，視業務定義），並依 `source` 過濾站點（如 `'1xbet.com'` 或 `'panda'`），避免撈取已結束 (`'Final'`) 或無效的比賽。
- **特定比賽查詢**：透過 `id` 進行單筆查詢，確保迅速定位。
- **避免全表掃描**：所有查詢必須帶有至少一個有效的過濾條件（如 `WHERE id = ?` 或 `WHERE source = ? AND lid = ? AND gdate = ? AND status IN (...)`），不得執行無條件的全表掃描。

### 不可回傳欄位

無 — 所有比賽欄位（隊伍名稱、比分、狀態等）皆為公開資訊，無需遮蔽或隱藏。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `price:acc:verify:{account}` | 交易前驗證帳戶（account, enabled） | 3600 秒；避免頻繁查詢 Cassandra。 |
| DEL | `price:acc:verify:{account}` | 帳戶狀態變更（如 enabled → 0） | 主動失效，立即清除快取，防止讀取舊狀態。 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 使用者認證與登入 | member-service | 帳戶驗證、session 管理、凍結狀態等，不在此服務處理。 |
| 錢包扣款與資金轉帳 | wallet-service | 本服務僅記錄交易與庫存，實際 ZCoin 扣款、結算、提現等由 wallet-service 執行。 |
| 帳戶註冊與資訊維護 | member-service / admin | accounts_\* 表的建立、密碼重設、手機綁定等由專屬服務或管理後台負責。 |
| 與第三方遊戲商（AU8、Fortuna888 等）的即時通訊 | third-party-gateway | 本服務僅使用 pricecenter 帳戶資訊，不負責串接第三方遊戲商或管理其帳號。 |
| 比賽結果數據寫入 | score-service | result_log 表的比賽結果資訊（gdate、game_type、gid、lid 等）由專門的比分服務寫入，本服務只讀取並更新結算標記（status）。 |

---

## 常見錯誤

- ❌ 在 stock_holdings 或 trade_log 使用 `UPDATE ... WHERE account=?` 修改 `stock_num`、`winloss` 或 `trade_history`。  
  ✅ 這些欄位僅可經由交易下單（INSERT/UPDATE stock_holdings）或結算（全表更新 winloss）流程操作，不提供直接修改的 API。

- ❌ 查詢 accounts_* 時未過濾 `enabled=1`，導致停用帳戶仍可進行交易。  
  ✅ 交易前必須 WHERE `account=? AND enabled=1`，否則應拒絕請求。

- ❌ 在查詢 stock_holdings、actionlog 或 resultlogs 時未指定完整分區鍵（如 gdate），導致全表掃描（ALLOW FILTERING 禁止）。  
  ✅ 所有查詢必須提供 Cassandra 分區條件的精確值或範圍，避免大量過濾或掃描。

- ❌ 將 accounts_\*.password 或 phone 回傳至前端（即使為管理後台）。  
  ✅ password 完全不可回傳，phone 須脫敏處理或僅於必要時回傳遮蔽版本。

- ❌ 將 accounts_\*.handler map 整體回傳。  
  ✅ 對外不應暴露 map 結構與內部 key，僅回傳前端所需的處理器名稱即可。

- ❌ 直接手動 INSERT/UPDATE actionlog 或 resultlogs 的 status 以外的欄位。  
  ✅ actionlog 只能由系統內部記錄流程寫入，resultlogs 的 status 只能由結算流程更新，其他欄位由比分服務維護。

- ❌ 在交易流程中自行修改 stock_holdings 的 `mode`、`oddtype`、`ratio`、`spread` 等欄位。  
  ✅ 這些欄位由交易模組根據下單請求一次性寫入，後續僅可更新持股數與輸贏，不可更動玩法相關欄位。

- ❌ 跨平台混淆 accounts_* 表（如在 AU8 平台流程中查詢 accounts_TG）。  
  ✅ 每個平台對應獨立的 accounts_ 表，必須依當前交易平台選用正確的資料表。