# ThresholdService

## 概述
ThresholdService 負責運動賽事閾值（threshold）設定的展平與同步。服務以 Python 非同步架構實現，從多層設定（賽事、聯盟、球種 / 系統層）解析各玩法（play_mode）的有效閾值，輸出至 `effective_thresholds` 表，並觸發 config direct sync，供下游告警模組使用。

## 主要功能
- **全量展平（Flatten Cycle）**  
  依目前啟用的站台與球種任務，每日對今、明、後三天的 sitegames 進行一次性閾值展平。僅新增尚不存在的 sitegid，並寫入 pending 的 config_direct_sync。
- **增量同步（Sync Cycle）**  
  監聽 `threshold_sync_pending` 表的變更（來自資料庫 trigger），依變更的設定表（oddthreshold_game_setting / league_setting / sport_setting）刷新記憶體快取，並針對受影響的賽事重新計算有效閾值後寫入。
- **三層閾值快取與解析**  
  使用記憶體快取 (`ThresholdSettingCache`) 存放三層設定，並透過 `ThresholdResolver` 依照賽事 → 聯盟 → 球種 → 系統層的優先序解析最終 play_mode 閾值組合。

## 技術棧
- **語言**：Python 3.9
- **執行環境**：Docker（基礎映像 `python:3.9-slim-buster`）
- **核心依賴**  
  - `asyncpg` – PostgreSQL 非同步存取  
  - `httpx` – HTTP 客戶端  
  - `redis` – 快取 / 訊息佇列  
  - `kafka-python` / `kazoo` – Kafka 與 ZooKeeper 整合  
  - `watchdog` – 檔案監控（視需求使用）  
  - `TCZB` – 內部共用套件（自內部 PyPI 安裝）
- **時區**：`Asia/Taipei`（容器內已設定）

## 組態與部署注意
- **部署方式**：Docker Swarm 服務，定義於 Portainer（Key: `PRD_Docker_Swarm|container|thresholdservice`）。
- **設定注入**：服務啟動時接收 `setting` 字典，常用參數包含：
  - `game_date_window_days`：展平日期區間（預設 3 天）
  - `support_types`：允許的站台支援類型（如 `full`, `odds`）
  - `game_cache_retention_days`：賽事快取保留天數（預設 1 天）
- **外部依賴**：需確保 PostgreSQL、Redis、Kafka（若有使用）等服務正確連線；內部 PyPI 伺服器 (`localhost:8070`) 需可觸及以安裝 `TCZB`。
- **時區**：容器已設定 `TZ=Asia/Taipei`，日誌與日期處理均依台北時間。

## 相關連結
- GitLab 存放庫：https://git.zbdigital.net/Biz/thresholdservice.git