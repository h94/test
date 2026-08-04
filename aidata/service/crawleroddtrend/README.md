# crawleroddtrend 內部服務目錄

## 概述
crawleroddtrend 是一個基於 Python Flask 的 Web API 服務，負責從 Cassandra 資料庫中讀取特定站台的賠率歷史資料，並將其整理為前端易於使用的趨勢圖表格式。服務透過 Kafka 發送日誌與錯誤訊息，支援多環境部署（Local / PRD / PRD2 / PRD3）。

## 主要功能
- **查詢賠率趨勢資料**  
  `POST /api/v1/oddtrend/getdata`  
  接收站台、賽事類型、日期、聯盟 ID、賽事 ID、玩法模式等參數，查詢 Cassandra 並回傳格式化後的賠率波動資料。
- **檢查服務版本**  
  `GET /api/v1/oddtrend/version`  
  回傳目前版本、主機名稱、環境及請求端 IP。
- **自動化單元測試**  
  內建 `Unittest.py`，使用 ddt 框架對資料轉換邏輯進行測試。

## 技術棧
- **語言與框架**：Python 3.8.5、Flask 2.2.2
- **資料庫**：Apache Cassandra（cassandra-driver 3.25.0）
- **訊息佇列**：Apache Kafka（kafka-python 2.0.2）、ZooKeeper（kazoo 2.8.0）
- **依賴管理**：基於 `requirements.txt`，並透過內部 pip 源（`http://localhost:8070`）安裝自訂套件 `TCZB`
- **容器化**：Docker（基底映像 `python:3.8.5-slim-buster`），使用 Portainer 管理

## 組態與部署注意
- **環境參數**：啟動時需傳入環境名稱（`Local`、`PRD`、`PRD2`、`PRD3`），例如：  
  `python ./project/__main__.py PRD`
- **資料庫設定**：  
  - Cassandra 叢集 IP：`192.168.55.80`  
  - Keyspace：`pricecenter`  
  - 查詢語句可依 `game_type`、`game_date` 等動態組成（詳見 `AppSettings.py` 中的 `SQL` 範本）
- **日誌與錯誤回報**：  
  - PRD 環境日誌發送至 `49.213.1.158:29096`  
  - Local 環境則輸出至本機 Kafka（`192.168.9.231:9092`、`192.168.9.232:9092`、`192.168.9.233:9092`）
- **容器執行**：  
  - 使用 Dockerfile 建置後，容器預設監聽 5000 埠  
  - 注意內部 pip 源需可存取，否則 `TCZB` 套件無法安裝
- **版本識別**：版本號碼由 `__main__.py` 自動依據檔案最後修改時間產生
- **單元測試**：執行 `python project/Unittest.py` 即可驗證資料轉換邏輯

## 相關連結
- **GitLab 原始碼**：https://git.zbdigital.net/CrawlerAgent/crawleroddtrend.git
- **Portainer 容器管理**：依據 PortainerKey `PRD_Docker_Swarm|container|4a14b8aa1381|crawleroddtrend:latest` 對應環境中的容器