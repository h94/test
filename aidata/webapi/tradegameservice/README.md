# TradeGameService WebAPI

- **Git Repository**：[https://git.zbdigital.net/crawleragent/tradegameservice.git](https://git.zbdigital.net/crawleragent/tradegameservice.git)

## 職責

負責運動賽事的交易遊戲功能，管理使用者對各球種賽事的買賣倉位（`stock_holdings_{game_type}`）、即時盤口快照查詢（從 Redis 讀取）、交易資料重算（重置比賽結算狀態，不直接修改盈虧或處理點數），以及交易取消與歷史查詢功能。本服務不負責實際點數的扣除或發放，點數相關操作已由錢包或其他服務接手。

## 技術棧

- 框架：Python / FastAPI（根據 `requirements.txt` 與 `__main__.py` 確認為 FastAPI + Uvicorn）
- 資料庫：
  - Cassandra：交易紀錄持久化（Keyspace: `tradegame`）；帳戶驗證資訊讀取（Keyspace: `pricecenter`）
  - Redis：即時盤口快照、庫存設定、帳戶驗證快取
- 驗證：API Key / 內部服務授權（TCZB Globals）
- 其他套件：marshmallow（Schema 驗證）、requests（外部 HTTP 呼叫）、kafka-python（與 MQService 通訊）、cassandra-driver、redis

## 資料庫重要 Table

| Table 名稱 | 用途 | 重要欄位 |
|-----------|------|---------|
| `stock_holdings_{game_type}` | 各球種使用者持倉與交易記錄（動態建表，依球種命名，例如 BK、BS、SC 等）。 | gdate (Partition Key), lid, gid, account, mode_spread_type（組成：`{mode}_{spread}_{oddtype}`, 例如 `HA_1.5_H`）, addtime, mode, oddtype, spread, ratio, winloss, stock_num, trade_history |
| `resultlogs` | 記錄各比賽結算狀態，用於重算排程選取未處理比賽。 | gdate (Partition Key), gtype, gid, lid, status, addtime |

- **`winloss` 狀態**：`W`（贏）、`L`（輸）、`N`（平局）、`C`（取消），空值代表尚未結算。此欄位僅可由結算流程（`tradegameresultservice`）寫入，寫入非空值後不可修改。
- **`resultlogs.status`**：`0` = 待結算，`1` = 結算中，`2` = 已結算。僅可由結算流程更新。
- **重算流程**：`recalculate` API 僅將 `resultlogs.status` 重置為 `0`，不直接修改 `stock_holdings` 的 `winloss`。
- **`trade_history`** 為 JSON 字串（陣列），記錄每筆交易的 `stock_price`、`trade_type`、`trade_operator`、`num`、`profitpoint`、`trade_time`。更新時採用應用層讀取後合併再寫回（等同於追加），不可覆蓋。`trade_type` 包含 `buy`、`sell`，以及可能的 `system`（如系統平倉）。
- **不可變更欄位**：`account`, `mode_spread_type`, `gdate`, `lid`, `gid` 等主鍵欄位一經建立即固定。

### Redis 鍵值

- 賠率快照：以 key 模式 `Tradegames_{game_type}_{lid}_{gdate}_{gid}` 儲存於 Redis，內容包含 odds（賠率）、use_spread、gdate、gid、gtype、lid、source、write_time、first_data 等欄位。本服務僅讀取，不寫入也不設定 TTL。
- 庫存設定：`Tradegames_Stock_{gdate}_{game_type}_{lid}_{gid}`（Hash），儲存該賽事可買賣總量設定（`amount`，包含 `amountbuy`、`amountsell`），用於交易限額檢查。
- 帳戶驗證快取：`price:acc:verify:{account}`（TTL 3600 秒），快取帳戶啟用狀態，交易前優先查詢；當帳戶狀態變更時須主動刪除（DEL）。

### 不可回傳欄位

- 對外 API 絕不可暴露 `password`、`phone`、`handler`、`authkey` 等敏感個資或內部配置。
- `trade_history` 對非本人查詢時應遮蔽或僅回傳統計量。

## 對外 API 重點

### 交易操作
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/trade/{game_type}` | 新增買入或賣出交易（lid, gdate, gid, account, mode, oddtype, spread, stock_num, trade_price, trade_type）。本服務不在此流程中直接扣除或發放點數。 | ✅ |
| GET | `/api/tradedata/{game_type}` | 管理後台專用，查詢球種交易資料（可依 lid、startdate、enddate 過濾）。 | ✅ |
| GET | `/api/usertradedata/{account}/{game_type}` | 查詢使用者球種交易資料（可依 lid、startdate、enddate 過濾）。 | ✅ |
| GET | `/api/usertradedailydata/{account}/{game_type}/{addtime}` | 查詢使用者單日交易資料（addtime 格式 YYYY-MM-DD）。 | ✅ |
| POST | `/api/tradehistory/{gtype}/cancel` | 取消指定交易記錄。從 `trade_history` 中移除指定交易，並相應調整 `stock_num`（若取消買入則減少持股數，若取消賣出則增加持股數）。 | ✅ |

### 盤口快照
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/tradegames/{game_type}/{lid}` | 取得球種聯盟盤口快照列表（可依 gdate、gid 過濾）。僅從 Redis 讀取。 | ✅ |
| POST | `/api/tradegames` | 批次查詢多球種盤口快照（body: [{gtype, lid, gdate, gid}]）。僅從 Redis 讀取。 | ✅ |
| GET | `/api/tradegames/stock/{gdate}/{gtype}` | 取得指定日期的賽事庫存設定（可選 lid、gid 過濾）。從 Redis Hash 讀取。 | ✅ |

### 重算
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/recalculate/{game_type}` | 重置指定球種的比賽結算狀態（將 `resultlogs.status` 設為 0，待 tradegameresultservice 重新結算）。不直接修改 `winloss` 或處理點數。 | ✅ |

## 服務相依

| 相依服務 | 用途 |
|---------|------|
| Cassandra（tradegame keyspace） | 儲存使用者持倉與交易歷史、比賽結算狀態。 |
| Cassandra（pricecenter keyspace） | 讀取帳戶驗證資訊（enabled、closetime 等）。 |
| Redis | 即時盤口快照讀取（odds、use_spread）、庫存設定讀取（買賣總量限制）、帳戶驗證快取（`price:acc:verify:{account}`）。 |
| MQService（Kafka） | 異常告警推送。 |

⚠️ **需人工確認**：README 與原始碼均未發現本服務呼叫點數服務（zcoin_api）的具體實作，點數處理推測已由 wallet-service 或其他機制負責。

## 常見使用場景

1.  **使用者買入倉位**
    - 觸發：使用者在前端選定賽事盤口並下注。
    - 流程：`POST /api/trade/{game_type}`（`trade_type=buy`）→ 驗證帳戶（Redis 快取優先，miss 則查 Cassandra pricecenter，過濾 `enabled=1` 且 `closetime` 為空）→ 檢查 Redis 庫存設定及個人限額 → 寫入 `stock_holdings_{game_type}` 與 `trade_history` → 回傳 `profitpoint`。
    - **重要限制**：買入時 `trade_price` 不可 ≥ 95；`profitpoint` 計算公式為 `-trade_price * stock_num`。

2.  **使用者賣出倉位**
    - 觸發：使用者選擇平倉。
    - 流程：`POST /api/trade/{game_type}`（`trade_type=sell`）→ 檢查 Redis 庫存設定限額 → 確認持有 `stock_num` 足夠 → 計算 `profitpoint`，追加賣出記錄至 `trade_history` → 回傳 `profitpoint`。
    - **重要限制**：賣出時 `trade_price` 不可 ≤ 5；`profitpoint` 公式為 `trade_price * stock_num - ceil(trade_price * stock_num * 0.05)`（扣 5% 手續費）。

3.  **前端載入賽事盤口**
    - 觸發：使用者進入交易遊戲賽事列表頁。
    - 流程：`GET /api/tradegames/{game_type}/{lid}` 從 Redis 讀取即時盤口快照（包含 odds 與 use_spread），支援以 gdate、gid 過濾。

4.  **批次盤口查詢**
    - 觸發：首頁或大廳需同時顯示多球種盤口。
    - 流程：`POST /api/tradegames` 傳入多筆 `{gtype, lid, gdate, gid}`，一次取得多球種盤口資料。

5.  **賽事結算後重算流程觸發**
    - 觸發：賽事結果需重新結算時由後台或排程觸發。
    - 流程：`POST /api/recalculate/{game_type}` → 檢查 `resultlogs` 確保比賽存在 → 將 `resultlogs.status` 重置為 0（待重算）。後續由 `tradegameresultservice` 掃描 status=0 的記錄進行持倉結算與點數處理。

6.  **取消交易**
    - 觸發：管理後台或內部流程需取消單筆交易。
    - 流程：`POST /api/tradehistory/{gtype}/cancel` → 從 `trade_history` 中移除指定交易（依 `trade_time` 與 `trade_type` 定位），並相應調整 `stock_num`。

## AI 判斷關鍵字

交易, 倉位, 持股, 盤口, 買入, 賣出, 球種, 賽事交易, trade, stock holdings, tradegame, 賠率, spread, 重算, recalculate, 帳戶驗證快取, 取消交易