# TradeGameResultService

## 概述

負責將交易資料進行結算：讀取比賽結果與使用者持倉，計算輸贏並更新持倉狀態，同時將獲利透過 API 通知 ZCoin 錢包系統。服務以多個獨立背景執行緒執行：一個負責掃描未結算的持倉並進行結算，另一個負責處理重結算，還有排程負責定期清除超過保留期限的歷史交易資料以及檢查未結算賽事。

## 主要功能

- **比賽資料讀取**：從 **`games`** 資料庫的 `games_{game_type}` 表（如 `games_bk`、`games_bs`、`games_bm` 等）取得已完賽或取消的比賽。
  ⚠️ 需人工確認：根據最新的 DB 邊界文件，`games` 表 `status` 欄位定義為文字型態（值為 `'Final'`、`'Cancelled'` 等）。但現有實作 (`process_trade.py`, `check_result.py`) 仍以數值狀態 (`1, 3, 4`) 進行過濾，可能為舊版對應或內部映射，應由資深工程師確認應使用哪一套過濾條件（建議統一為 `status IN ('Final', 'Cancelled')`）。

- **持倉資料讀取**：從 Cassandra `tradegame` keyspace 的 `stock_holdings_{game_type}` 表取得對應賽事的所有持倉記錄，並過濾尚未結算的項目（`winloss` 為空值或 NULL）。

- **結算邏輯**：支援多種遊戲類型（BS、BK、SC 等）及盤口模式（HA、OU、1X2），依據主客隊比分（`match_h`、`match_a`）、讓分（`spread`）與下注方向（H/A/T/O/U）計算贏/輸/平手/取消（W/L/N/C），並在比賽取消或平手時退回原價。

- **持倉更新與結算記錄**：
  - 根據結算結果更新 `winloss` 欄位（值 W/L/N/C），該欄位寫入後不可再修改。
  - 結算過程中會同時在 `trade_history` 附加一筆系統結算交易（sell / resell / refund），並將 `stock_num` 設為 0，寫回資料庫。
    ⚠️ 需人工確認：DB 邊界文件 (`tradegame-detail.md`) 要求 `trade_history` 和 `stock_num` 僅由交易服務維護，本服務不可直接寫入，但實際實作會整筆更新持倉記錄，需確認此行為是否符合最終規範。
  - 結算時會依序更新 `resultlogs` 表的 `status`：`0`（待結算）→ `1`（結算中）→ `2`（已結算），`2` 為最終狀態，寫入後不可再變更。
    ⚠️ 需人工確認：目前程式碼中僅觀察到 `0` 與 `1` 兩個狀態，並未使用到 `2`，實際狀態流轉以資深工程師確認為準。
  - 對於已結算比賽的重結算，會透過退款（recalculate）流程退回系統交易後再重新結算。

- **ZCoin 獲利發送**：將結算後的獲利點數與相關交易資訊組合成請求，透過 REST API 傳送至 ZCoin 錢包服務進行派彩。

- **過期資料清理**：獨立排程定期清除：
  - 所有 `gdate` 超過 30 天的 `stock_holdings_{game_type}` 記錄（⚠️ 需人工確認：此處未區分結算狀態，直接依日期刪除整個分區，符合現有實作 `clear_data.py`，但可能需確認是否有業務要求僅刪除已結算資料，以及本服務是否具備刪除 `stock_holdings` 的權限）。
  - `resultlogs` 中 `gdate` 超過 3 天的結算紀錄（⚠️ 已由原 7 天修正為程式碼實際的 3 天）。

- **未結算告警**：每 10 分鐘掃描過去兩天的比賽，若發現有持倉但超過開賽時間 8 小時仍未結算（或因狀態異常），則透過 Telegram 發送告警訊息。

- **心跳監控**：每 60 秒向 Logger 發送服務運行訊息。

- **多環境支援**：透過啟動參數區分 Local（開發測試）與 PRD（正式環境）。

## 技術棧

- **語言**：Python 3.9（slim-buster）
- **資料庫**：
  - **`games`**：唯讀，讀取比賽資料表 `games_bk, games_bm, games_bs, games_ck` 等（使用內部封裝的資料庫驅動，由 `TCZB` 套件提供，非直接依賴 `psycopg2`）。
  - **Cassandra `pricecenter`**：讀取 `accounts_*`（帳號驗證），寫入 `actionlog`（操作日誌）。使用 `cassandra-driver`，一致性級別 ONE。
  - **Cassandra `tradegame`**：讀寫 `stock_holdings_BK, stock_holdings_BS, stock_holdings_SC` 等持倉表，以及讀寫 `resultlogs`。
- **訊息佇列／日誌**：Kafka（透過內部 `TCZB.Logger` 模組）
- **依賴管理**：`requirements.txt`，並依賴內部 pip 源 `localhost:8070` 安裝私有套件 `TCZB`
- **其他函式庫**：Flask（僅作為相依）、Flask-SocketIO、redis、requests、kazoo（ZooKeeper）等
  ⚠️ redis 是否實際於本服務中使用需人工確認，依 DB 邊界文件標示為無 Redis 使用；`requirements.txt` 包含 `redis==7.0.1`，可能為其他服務共用之殘留依賴。
- **部署形式**：Docker 容器，基於 `python:3.9-slim-buster` 映像

## 資料庫操作邊界

| 資料庫 | 角色 | 說明 |
|------|------|------|
| games | reader | 唯讀。讀取比賽資料與最終比分。 |
| pricecenter | reader / writer | 唯讀 accounts_* 表進行帳號驗證；可對 actionlog 表執行 INSERT 記錄結算操作。 |
| tradegame | reader / writer | 讀取 stock_holdings_* 與 resultlogs；更新 winloss、trade_history、stock_num（透過整筆記錄覆寫）；寫入並更新 resultlogs.status。 |

### games

- 權限：**唯讀**。
- 讀取規則：
  - 僅讀取 `status = 'Final'` 或 `status = 'Cancelled'` 的比賽（⚠️ 需人工確認「取消」的精確值，現有實作仍使用數值 1,3,4，見上方注意事項）。
  - 必須以 `gdate` 為主要篩選條件，可搭配 `lid`、`id` 過濾，嚴禁全表掃描。
  - 比分來源以 `match_h`、`match_a` 為準，不應依賴 `resultinfo` 等原始資料。
  - `source` 欄位標記資料供應商，結算邏輯中**不應**用於判斷比分可信度。
- 不可回傳欄位：`siteidmaps`、`teams` 詳細 JSON、`resultinfo`、`otherinfo`（任何對外 API 皆須屏蔽）。

### pricecenter（Cassandra）

- `accounts_*` 表：唯讀，僅用於帳號啟用狀態驗證（`enabled=1`）及關閉狀態檢查（`closetime` 為空）。不可跨表掃描，查詢需以 `account` 精確匹配。`handler` 欄位僅供內部使用，對外不得暴露。
- `actionlog`：僅允許 `INSERT`，記錄結算相關操作（成功、失敗、重結算）；必須包含分區鍵 `date`（格式 `yyyy-MM-dd`）且格式正確；禁止 `UPDATE` / `DELETE`。`detail` 欄位建議使用 JSON 結構，但不得含密碼、Token 等敏感資訊。
- 不可回傳欄位：`password`、`phone`、`closetime`（對外 API 皆須排除）；`detail` 欄位僅供內部稽核，對外須脫敏。

### tradegame（Cassandra）

- `stock_holdings_{game_type}`：
  - `winloss`：僅結算流程可寫入一次（W/L/N/C），寫入後不可再修改。tradegameresultservice 為唯一寫入者。
  - `trade_history`：結算時可附加結算交易記錄（sell / resell / recalculate），其餘時間僅讀取；不可對外暴露完整內容。
  - `stock_num`：結算時不可直接單獨更新（結算後會設為 0 是透過更新整個記錄，非直接修改此欄位），正常交易增減由 `tradeservice` 處理，tradegameresultservice 僅在更新持倉記錄時一併寫入。
  - 查詢時必須包含分區鍵 `gdate`，並過濾 `winloss IS NULL` 以選取未結算記錄。
  - `mode_spread_type`、`lid`、`gid`、`account` 等構成 primary key 的欄位寫入後不可更新。
- `resultlogs`：
  - 用於記錄比賽結算進度（`status` 0→1→2），寫入後 `status=2` 不可再變更。tradegameresultservice 可更新 `status`。
  - 讀取時需包含分區鍵 `gdate`。
  - `gdate`、`gtype`、`gid`、`lid` 一經建立不可修改。
- 不可回傳欄位：`trade_history`、`account`（對外需脫敏）、`addtime`。

### stock（MySQL，⚠️ 需人工確認）

根據 DB 邊界文件 `tradegameresultservice-detail.md`，本服務可能具備對 `stock` 資料庫的讀寫權限（例如 `FavoriteRule`、`MessageLog`、`Users` 等表的讀取與部分寫入），但目前釋出的核心程式碼中未發現對 `stock` 的操作，此功能是否存在或已廢棄，須由資深工程師確認。若確認無此功能，本章節可移除。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 股票持倉寫入與庫存變動 | `tradeservice` | `stock_holdings` 表的插入與 `stock_num` 更新（非結算場景）均由交易服務處理，本服務僅讀取及在結算時更新整筆記錄（包含 `winloss`, `stock_num`, `trade_history`）。 |
| 遊戲比分來源及結果判定 | `gameservice` 或上游遊戲供應商 | 本服務從遊戲服務取得已確認的最終結果，不負責比分驗證。 |
| 玩家帳號管理與權限驗證 | `authservice` / `memberservice` | `account` 取自外部系統，本服務不負責帳號建立或停用。 |
| 外部遊戲平台帳號連動 | `pricecenter` 相關服務 | `tradegame` 庫不儲存平台帳密，結算時不處理第三方金流。 |
| `games` 系列表的任何寫入操作 | `gameservice` | 比賽建立、比分更新、狀態異動皆由賽事服務負責，本服務僅讀取。 |

## 常見錯誤

- ❌ 結算掃描時未過濾 `winloss`，導致已結算資料被重新處理而重複扣除庫存 → ✅ 每次結算批次必須先讀取 `winloss IS NULL` 的記錄，處理後立即寫入 `winloss` 避免二次處理。
- ❌ 跨日期查詢時忽略 `gdate` 條件，僅以 `gid` 搜尋引發全表掃描或逾時 → ✅ 查詢前必須帶入 `gdate` 作為 partition key 限制，必要時使用 `IN` 搭配多日期。
- ❌ 結算完成後允許透過一般 API 直接 `UPDATE winloss` 改變結果 → ✅ `winloss` 應僅由結算內部流程寫入，且寫入後鎖定，變更需走管理後台人工覆核。
- ❌ 將 `trade_history` 回傳給前端，暴露用戶交易明細 → ✅ 前端如需查詢歷史交易應透過 `tradeservice` 提供的專用 API，本服務不予暴露。
- ❌ 讀取 `accounts_*` 時未檢查 `enabled` 或 `closetime`，導致已停用/關閉的帳號繼續進行交易 → ✅ 每次驗證帳號必須同時確認 `enabled = 1` 且 `closetime` 為空。
- ❌ 寫入 `actionlog` 時未提供 `date` 分區鍵或寫入錯誤格式，導致寫入失敗或落入錯誤分區 → ✅ 必須以操作當日正確填入 `date`，並確保其他聚簇鍵一致。
- ❌ 將 `password` 或 `actionlog.detail` 透過 API 暴露給客戶端 → ✅ 嚴格過濾所有對外輸出，僅在內部使用。
- ❌ 結算時讀取 `games_*` 表未過濾 `status = 'Final'`，誤用未完成比賽的即時比分 → ✅ 在讀取 `match_h`/`match_a` 前，務必確認 `status` 為 `'Final'`，避免使用 `Live` 或 `PreGame` 狀態的比賽。
- ❌ 直接信任 `resultinfo` 或 `match_detail` JSON 中的數值而未與 `match_h`/`match_a` 欄位比對，導致取錯結算用比分 → ✅ 以 `match_h`、`match_a` 為最終比分來源；`match_detail` 僅供特殊規則（如局分）使用，且須標準化解析。
- ❌ 在 `stock_holdings` 中直接以 UPDATE 語句變更 `stock_num` → ✅ `stock_num` 的變更應透過完整的持倉記錄更新（含 `winloss`、`trade_history`），不可單獨修改。
- ❌ 結算重試時未先退回系統發放的利潤（recalculate），導致帳務重複 → ✅ 重結算時必須先利用 `recalculate_trade` 流程退回既有系統交易，再重新結算。
- ❌ 批次結算前未檢查 `resultlogs`，導致同一日期的同一遊戲類型被重複結算 → ✅ 每次執行結算批次前，必須查詢 `resultlogs` 確認該 `gdate` 與 `gtype` 組合的 `status` 尚未為 `2`（已結算）。
- ❌ 更新 `resultlogs.status` 時跳過中間狀態或未按順序流轉（例如由 0 直接跳 2） → ✅ 必須嚴格按照 0→1→2 順序更新，並記錄操作日誌。

## 組態與部署注意

- **啟動方式**：`python ./project/__main__.py <environment>`  
  環境參數 `environment` 需為 `Local` 或 `PRD`，對應 `AppSettings.environment_path` 中的設定。
- **Games 資料庫連線**：需設定資料庫連線資訊（⚠️ 需人工確認環境變數或設定檔位置）。本服務僅讀取。
- **Cassandra 連線**：
  - `pricecenter`：用於讀取帳號、寫入 `actionlog`。
  - `tradegame`：用於讀寫持倉與結算記錄。
- **Logger 設定**：Kafka 位址可依環境不同而切換（Local 使用內網 `192.168.9.231~233`，PRD 使用外網 `49.213.1.158:29096`）。
- **內部 pip 源**：Dockerfile 中使用 `pip install TCZB -i http://localhost:8070`，建立 Image 時需確保此私源可連線，或修改為正確位址。
- **時區**：已設定 `TZ=Asia/Taipei`。
- **Portainer Key**：`PRD_Docker_Swarm`，表示正式環境部署於 Docker Swarm 叢集。

## 相關連結

- **GitLab 倉庫**：<https://git.zbdigital.net/CrawlerAgent/tradegameresultservice.git>
- **Confluence 業務規範 (TCZB-4263)**：[交易結算流程](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469182) (最後更新 2026-04-08)
- **Confluence 結果格式規範**：[Result information](https://confluence.zbdigital.net/display/TCZB/Result+information) (最後更新 2022-09-01，⚠️ 可能過時需確認)