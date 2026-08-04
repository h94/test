# 概述

PredictRobot 是內部用於運動賽事自動投注的預測機器人服務。它從多個資料來源（Cassandra、Kafka、外部 API）取得賽事賠率與歷史數據，並透過多種策略模型產生下注決策，模擬真人下注行為。服務部署於 Docker Swarm 叢集，針對不同帳號類型（`enabled=1` 與 `enabled=3`）提供兩組獨立的排程邏輯。

# 主要功能

- **賠率獲取**：從 inplayz.com API 即時拉取各球種（籃球、棒球、冰球、美式足球、足球、電競、網球等）的讓分、大小、獨贏等賠率。
- **排行榜分析**：擷取各聯盟的預測排行榜，篩選出高勝率的「莊殺」帳號，優先分配給這些帳號下注（**注意**：自 2025-11-27 起已取消策略優先帳號機制）。
- **歷史下注比對**：查詢 Cassandra 中 `predictbets_*` 表過去下注紀錄，避免同一帳號重複下注已投注的場次，並控制每日下注次數。
- **多策略引擎**：內建多種下注策略（隨機、1X2 強隊、球頭變化、上次對戰結果、機器學習 OU 比對等），可根據環境設定動態啟用。策略數量已由 17 種縮減為 12 種（取消策略 38, 39, 40, 41, 42）。
- **帳號分級**：支援 `enabled=1`（每日可大量下注）與 `enabled=3`（每天限 200 注）兩種機器人帳號群組，各自獨立排程。`Service.py` 固定使用 `enabled=1` 機器人，`Service2.py` 固定使用 `enabled=3` 機器人。
- **假下注機制**（2025-11-27 起）：每個帳號每筆下注有 20% 機率觸發假下注（僅記錄不下注），使下注分佈更均勻。
- **錯誤回傳**：透過 Kafka 日誌系統（Logger）將執行訊息、錯誤、下注摘要傳送至監控中心。

# 業務規則與關鍵調整

> 部分決策來自 Confluence 頁面 TCZB-4061、TCZB-3862 等，完整文件請參考內部知識庫。

- **帳號下注上限**（依球種與聯盟）：
  - 棒球、籃球：該聯盟可下注比賽數的 70%
  - 足球：20% ~ 30%
  - 冰球：50% ~ 70%
  - 網球、電競：30% ~ 40%（⚠️ 網球先前描述為 3~4 成，最終與電競合併為 30% 需人工確認）
- **下注間隔**：每輪下注之間需間隔 2.5 小時，完成一輪後容器會關閉重啟。
- **帳號選擇順序**：高手榜帳號 → 通用帳號（策略優先帳號已取消）。每次需檢查下注歷史，若場次已下注則跳過。（⚠️ 現有實作順序需人工確認）
- **分組邏輯**：目前仍依帳號前兩碼分為五組（BK、BS、SC、FL、HL），各組固定對應球種。此限制可能導致跨球種莊殺帳號無法充分發揮，改進方案尚未確定（需人工確認最終方案）。
- **策略變更**：自 2025-11-27 起取消策略 38~42 共 5 種，現行策略數量 12 種；棄注機制已棄用。
- **假下注**：20% 機率觸發，僅寫入下注記錄而不實際下注，使下注行為更分散。
- **每日帳號過濾**：從 `gamerobots` 表中選取 `enabled=3` 的帳號進行上限過濾，使每日可下注帳號總數降至約 320 個。

# 技術棧

- **語言**：Python 3.9.13
- **執行環境**：Docker (slim-buster)，部署於 Docker Swarm
- **資料庫**：Cassandra（連線至 `192.168.55.80`，操作 `predict`、`games` 與 `member` keyspace）
- **訊息佇列**：Kafka（多組 Broker，用於日誌、爬蟲資料傳遞）
- **外部 API**：`https://inplayz.com/apiservice` 系列端點（賠率、排行榜、賽事資料）
- **第三方套件**：`cassandra-driver`, `kafka-python`, `requests`, `websockets`, `ddt`（單元測試）

# 資料庫操作邊界

## member keyspace（唯讀）

- `gamerobots`：根據 `enabled` 篩選機器人帳號，`Service.py` 取 `enabled=1`，`Service2.py` 取 `enabled=3`。
- `gameusers`：不直接執行 WHERE 查詢，而是從排行榜 API 取得帳號後解析。
- 不可回傳欄位：`password`, `authkey`, `email`, `black_account`, `focus_account`, `follow_account`, `memberships`。

## predict keyspace（唯讀）

- `betpool_games`：僅讀取 `status=0` 且 `payout=false` 的未開賽遊戲；依 `id` 單筆查詢。
- `betpool_bets`：主鍵查詢 `gid, account, id` 用於歷史比對；不支援全表掃描。
- `activities_cycles`：過濾 `startdate <= 今日 <= enddate` 取得進行中活動週期。
- `activities_winneraccounts`：依 `site, activityevent, cid` 查詢排行榜。
- `activities_record`：查詢用戶活動狀態與剩餘天數。
- `calculatelog`：查詢 `weekid`，過濾 `done=1` 確認週次計算已完成。
- 不可回傳欄位：`account`, `betzcoin`, `profitzcoin`, `winlose`, `betoption`, `winbets`, `predictcount`, `profitpoint`, `winpercentage`, `restday`, `resultcount` 等所有涉及財務、個人識別、輸贏隱私的欄位。

## games keyspace（唯讀）

- `games_{sport_code}` 系列表（如 `games_bk`, `games_bs`, `games_fl`…）：用於策略分析及歷史賽果查詢。
- 讀取規則：
  - 僅對 `status='PreGame'` 且 `(gdate + gtime) > 當前時間` 的比賽進行預測。
  - 歷史賽果分析需過濾 `status='Final'` 並搭配日期範圍。
  - 查詢時應包含 `gdate` 區間及 `lid` 等條件，避免全表掃描。
  - 可依 `source` 過濾站台。
- 不可回傳欄位：`siteidmaps`（站台對應商業資訊）、`create_at`（內部時間戳）。

## Redis

目前無 Redis 操作。

# 組態與部署注意

1. **環境變數**：啟動時須以命令列參數指定環境名稱（如 `PRD`、`Local`），對應 `AppSettings.py` 中的 Kafka 與 Cassandra 連線配置。
2. **Kafka 連線**：`AppSettings.py` 中定義了多組 Kafka Broker，正式環境使用 `192.168.55.60:9092`（內網）或 `49.213.1.158:29096`（外網），請確保網路可通。
3. **Cassandra**：目前固定連接 `192.168.55.80`，若更換節點或需調整超時設定，請修改 `DataProvider.py` 中的 `Cluster` 參數。
4. **版本管理**：使用 GitLab CI/CD，Image 標籤為 `predictrobot:latest`，容器名稱可透過 PortainerKey 識別。
5. **資源限制**：服務為長駐程式，主執行緒保持 sleep 以避免 Cassandra 連線被回收。**每輪下注週期約 2.5 小時，完成後容器自動關閉重啟**（⚠️ 先前的 2 小時週期已變更）。
6. **策略擴充**：新的策略檔案需置於 `project/Strategies/` 目錄，並在 `Service.py` 的 `strategy_setting` 中註冊對應的 ID 與適用球種。目前可用策略數量已降至 12 種，擴充前應評估是否違反分佈控制策略。

# 常見錯誤與注意事項

- ❌ 混用 `enabled=1` 與 `enabled=3` 的機器人在同一策略中。
- ❌ 對 `betpool_games` 讀取未過濾 `status=0` 或 `payout=true`，導致使用過期比賽。
- ❌ 對 `games_*` 表查詢未過濾比賽狀態（應檢查 `status='PreGame'` 且 `(gdate + gtime) > 當前時間`），或未加日期範圍／聯賽條件導致全表掃描。
- ❌ 直接 JOIN `gameusers` 取帳號，而應從排行榜 API 取得後解析。
- ❌ 快取機器人清單未設失效機制，應每次查詢前重新讀取 DB 或設定 TTL。
- ❌ 誤用 `predictbets_*` 表，應依 `game_type` 動態選擇正確的分表。
- ❌ 回傳敏感欄位（如 `password`, `account`, `siteidmaps` 等）給前端或日誌。
- ⚠️ 棄注機制已棄用，不應再出現在程式碼中。
- ⚠️ 策略棄用後相關程式碼應徹底移除，避免誤用。
- ⚠️ 電競與網球下注上限的合併方式需人工確認最終數值。
- ⚠️ 機器人分組邏輯改進方案尚未確定，現階段仍使用帳號前兩碼分組，新增球種時需注意遷移策略。
- ⚠️ `enabled=3` 篩選邏輯是否已正式採用為永久機制，需人工確認。

# 相關連結

- **GitLab 倉庫**：`https://git.zbdigital.net/CrawlerAgent/predictrobot.git`
- **Docker Swarm**：PRD 環境容器 ID `06a5b53df205`，Image `predictrobot:latest`
- **外部 API 入口**：`https://inplayz.com/apiservice/api/predict/topics`（動態取得聯盟清單）