# SitegameOddService 內部服務目錄

## 概述
SitegameOddService 是一個提供賽事賠率查詢與歷史追蹤的 Web API 服務，主要用於即時賠率、歷史賠率、賠率走勢等資料的擷取與整理。服務支援多種球種與玩法，並整合 Cassandra、Redis、Loki 等資料來源，為內部系統提供統一的賠率資料介面。

## 主要功能
- **即時賠率查詢**：依球種、玩法、站台、賽事 ID 取得單場或多場次的主要賠率。
- **歷史賠率查詢**：從 Loki 日誌取得指定賽事的歷史主要賠率（最新球頭）。
- **賠率走勢查詢**：取得賠率隨時間的變動記錄，支援 HA、OU 等玩法的趨勢。
- **輔助工具 API**：
  - 版本檢查 (`/api/version`)
  - 透過 SFTP 寫入檔案至 NAS (`/api/write/file`)
  - 查詢 Cassandra 中 `gid` / `lid` 對應關係 (`/api/get/lid`、`/api/get/lids`)
  - 寫入下注日誌至 Cassandra (`/api/write/betlog`)

## 技術棧
- **語言與框架**：Python 3.8.5 (slim-buster), Flask 2.2.2
- **資料庫**：Apache Cassandra (cassandra-driver 3.25.0), Redis 4.5.4
- **日誌與監控**：Apache Kafka (kafka-python 2.0.2, Kakfa 叢集), Grafana Loki (HTTP API)
- **協調服務**：Kazoo (ZooKeeper 客戶端)
- **其他工具**：
  - pysftp (SFTP 上傳)
  - requests, paramiko, watchdog, ddt (測試)
  - **TCZB** (內部封裝庫，須自建 pip 源安裝)
- **部署環境**：Docker (基於 `python:3.8.5-slim-buster`)，運行於 Docker Swarm (PRD)

## 組態與部署注意
- **環境變數**：透過啟動參數指定環境（如 PRD、PRD2、Local），對應 `AppSettings.py` 中的 `environment_path` 取得 Logger、叢集、Redis、Loki 等設定。
- **Cassandra 連線**：需設定 `cluster` 區塊中的 IP 列表；支援不同環境（PRD、PRD2）對應不同叢集。
- **Redis 連線**：`redis_server` 設定各環境的 IP；資料庫號碼（db 5 即時、db 6 非即時）由請求參數決定。
- **Logger 配置**：透過 Kafka 傳送日誌，需提供 Broker 列表（PRD 使用 `49.213.1.158:29096`）。
- **Loki 查詢**：需提供 `loki` API 端點（內部 URL）。
- **內部套件 TCZB**：Dockerfile 中透過 `pip install TCZB -i http://localhost:8070 --trusted-host localhost:8070` 安裝，需確保 CI/CD 環境可存取該 Pip 源。
- **部屬方式**：基於 Docker Swarm，PortainerKey 標示 `PRD_Docker_Swarm`；映像名稱 `sitegameoddservice:latest`。
- **網路與埠號**：容器暴露 5000 埠，Flask 監聽 `0.0.0.0:5000`（PRD 環境使用指定埠）。

## 相關連結
- **GitLab Repository**：`https://git.zbdigital.net/CrawlerAgent/sitegameoddservice.git`