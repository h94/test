# OpenclawService

PortainerKey=PRD_Docker_Swarm|container|openclawservice  
Kind=webapi  
GitLab=https://git.zbdigital.net/CrawlerAgent/openclawservice.git  

## 概述

OpenclawService 為「龍蝦」系統提供的後端 API 服務，負責處理跨站台賽事合併、隊伍比對與聯盟合併等核心邏輯，並內建 AI 輔助賽事合併模組（含自動比對、人工審核、參數調優、回測分析、調參包匯出）。支援多種球種（SC、BK、BS、FL、HL、ES、TN 等），並整合 Kafka 日誌、Cassandra 資料庫、PostgreSQL（AI Merge）與 Redis 快取。

## 主要功能

### 合併賽事 (Merge Games)
- `GET /api/merge/games`：依日期與時間區間查詢各球種的正式比賽，並補上聯盟與隊伍詳細資訊，用於龍蝦前端展示。
- `GET /api/merge/sitegames`：查詢各站台的原始比賽，補上站台層級聯盟與隊伍映射，協助龍蝦進行合併比對。
- `POST /api/merge/pending-result/{game_type}`：龍蝦寫入合併結果至 Cassandra（`{table_prefix}{game_type}`）。

### 隊伍檢查 (Check Team)
- `GET /api/check-team/teams/{game_type}`：取得指定球種所有聯盟的隊伍（僅顯示主站台映射），並補上對應聯盟與隊伍名稱。  
  > 足球（SC）聯盟數量過多，此端點在 game_type=SC 時**必須**附帶 query 參數 `lid` 指定聯盟，否則回傳 400；可先呼叫 `GET /api/check-team/sc-league-ids` 取得聯盟清單後再查詢。
- `GET /api/check-team/sc-league-ids`：回傳足球所有聯盟 ID 與名稱，供 `teams/SC?lid=` 使用。
- `POST /api/check-team/wrong-teams-merge/{game_type}`：將異常合併隊伍資料寫入 Redis（含 TTL）。

### 聯盟合併 (Merge League)
- `GET /api/merge_league/league/{game_type}`：根據時間區間產出「主聯盟」與「其他聯盟」清單，供龍蝦設定合併目標。主聯盟僅對應單一 site（驗證規則見 `MergeLeagueService.validate_payload`）。
- `POST /api/merge_league/pending-result/{game_type}`：寫入聯盟合併結果（含舊資料去重合併）。

### AI 賽事合併 (AI Merge)

此模組提供自動比對、人工審核、參數調優、回測分析與調參包匯出等功能，其資料儲存於 `Games` PostgreSQL 資料庫（Host: `192.168.9.231`）的 `aimerge_*` 表中，並以 Redis 記錄任務執行狀態。主要 API 如下：

- **設定管理**：  
  `GET/PUT /api/aimerge/config`、`GET /api/aimerge/config/history`、`POST /api/aimerge/config/rollback`、`GET /api/aimerge/config/all`
- **預測審核**：  
  `/api/aimerge/predictions`（查詢待審核/衝突預測）、人工確認/否定（單筆或批次）
- **回測與模擬**：  
  `POST /api/aimerge/backtest`、`POST /api/aimerge/backtest/simulate`
- **訓練標籤**：  
  `GET /api/aimerge/labels`、`POST /api/aimerge/labels/override`
- **調參包匯出**：  
  `/api/aimerge/tuning-packs/export`
- **每日報告**：`GET /api/aimerge/reports/daily`

#### 背景任務
- **Job1（自動比對）**：對主站（Site A）與其他站台（Site B）進行特徵比對（F1 聯盟、F2 隊伍、F3 時間、F4 賠率），產出預測分數並寫入 `aimerge_match_predictions`。支援排程與手動觸發，進度可於 API 查詢。
- **Job2（對答案與生成報告）**：合併完成後，依 `sitegames.gid` 驗證預測正確性，寫入 `training_labels` 並產生每日報告。
- **Job3（pending GID 解析）**：針對尚未有 `gid` 的待審核/衝突預測，補寫訓練標籤。
- **Job4（高分自動合併）**：分數高於門檻（`aimerge_auto_merge_min_score`）的 `auto_confirmed` 預測，自動呼叫 mergesite 寫入合併結果。

### 背景任務 (原有)
- 每分鐘心跳偵測：透過 Redis 記錄最後一次 API 請求時間，若連續 70 分鐘無請求則觸發錯誤日誌（透過 Kafka 發送）。

## 技術棧

- **語言**：Python 3.11
- **Web 框架**：FastAPI + uvicorn
- **資料庫**：
  - Cassandra（keyspace: `pricecenter`，用於比賽、隊伍、聯盟資料）
  - PostgreSQL（`Games` 資料庫，用於 AI Merge 相關功能）
- **快取**：Redis（db=3，`192.168.55.80:6379`；用於異常隊伍快取、服務狀態儲存及 AI 合併任務狀態暫存）
- **日誌傳輸**：Kafka（生產環境使用 `49.213.1.158:29096`）
- **部署**：Docker Swarm（透過 Portainer 管理）
- **其他依賴**：cassandra-driver、kafka-python、kazoo、pydantic、redis、jellyfish 等（見 `requirements.txt`）

## 組態與部署注意

- **環境切換**：啟動時透過命令行參數指定環境（`Local` / `PRD`），會載入 `AppSettings.py` 內對應的 Cassandra IP、日誌設定與資料表前綴。
  ```bash
  python ./project Local
  ```
  生產環境建議使用：
  ```bash
  python ./project PRD
  ```
- **Cassandra**：需先建立 Cassandra 連線（重試 10 次，間隔 5 秒）。keyspace 為 `pricecenter`。
- **Redis**：用於異常隊伍快取、服務狀態儲存，以及 AI 合併任務（Job1/Job2/Job3/Job4）的進度與狀態。心跳機制依賴 Redis 記錄最後 API 請求時間，若 Redis 不可用將影響閒置偵測（需人工確認 fallback 行為）。  
  > ⚠️ **文件衝突**：`openclawservice-detail.md` 聲明本服務無 Redis 操作，但 README 與多個場景流程（心跳偵測、異常隊伍寫入、AI 任務狀態管理）確認本服務使用 Redis。`openclawservice-detail.md` 相關段落為錯誤資訊，應予忽略。
- **AI Merge 設定持久化**：AI Merge 的執行期閾值設定（`aimerge_score_threshold_auto`、`aimerge_conflict_margin` 等）儲存於 PostgreSQL `aimerge_runtime_config` 表中，支援 API 動態調整、版本歷史與 rollback。`config_resolver` 會合併 `AppSettings` 預設值、 `_default` 全域設定與各球種覆寫，變更後快取將自動失效。
- **日誌**：使用 `TCZB` 套件經 Kafka 傳送，非同步隊列（`Queue`）避免阻塞事件循環。
- **Portainer**：PortainerKey 為 `PRD_Docker_Swarm|container|openclawservice`，表示該容器部署於生產 Swarm。
- **健康檢查**：服務本身無顯式健康檢查端點，但心跳機制會透過日誌發出異常警報。需注意 K8s 或 Load Balancer 的健康檢查請求應被排除在閒置計數之外，避免永遠無法觸發告警。

## 相關連結

- **GitLab 專案**：[https://git.zbdigital.net/CrawlerAgent/openclawservice.git](https://git.zbdigital.net/CrawlerAgent/openclawservice.git)