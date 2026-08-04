# PredictRobotByConnect 內部服務目錄

## 概述
此服務為預測機器人下注引擎，負責接收即時賽事資料與賠率，依據多種策略自動產生投注決策，並將下注結果回傳至 Cassandra 與 Kafka。部署於 Docker Swarm 生產環境（PRD）。目前容器映像標籤為 `latest`，基於 `python:3.9.13-slim-buster`。

## 主要功能
- **資料蒐集**：從 Cassandra（`predict`、`member` keyspace）讀取帳號、機器人設定、下注歷史；從 HTTP API 取得賽事資訊及隊伍勝率（如 NBA PCT）。
- **即時賠率串流**：透過 websockets 或 Kafka 接收多個網站（au8tw.com、ku888 等）的即時賠率變化。
- **多策略下注**：內建 20 種以上策略（Strategy1~20），包含：
  - 隨機下注（HA / OU / 1X2）
  - 賠率差異判斷（大小盤 / 讓分盤）
  - 隊伍近況與勝率分析（HL、BK 類型賽事）
  - 跨平台球頭對比（au8 vs ku888）
  - 歷史賠率變化觸發
- **資料寫入與錯誤回報**：將下注紀錄寫入 Cassandra 表（`predict.predictbets_BK/BS/SC/HL/FL`），並透過 Kafka Logger 輸出錯誤與執行訊息。
- **單元測試框架**：使用 `unittest` + `ddt` 進行參數化測試。

## 技術棧
- **語言與執行環境**：Python 3.9.13（slim-buster）
- **資料庫**：Cassandra（cassandra-driver 3.26.0）
- **訊息佇列**：Kafka（kafka-python 2.0.2）
- **WebSocket**：websockets 11.0.2
- **HTTP 請求**：requests 2.24.0
- **分散式協調**：kazoo（ZooKeeper）、watchdog（檔案監控）
- **內部套件**：TCZB（自訂工具，包含 Logger、Globals、Versioning）
- **自動化測試**：ddt（資料驅動測試）
- **容器化**：Docker，部署於 Docker Swarm

## 組態與部署注意
- **環境變數**：支援 `Local`、`PRD`、`PRD2`、`PRD3`、`PROD` 五種環境，透過啟動參數傳入（如 `python project/__main__.py PRD`）。
- **Kafka 位址**：
  - 生產環境（PRD）：`49.213.1.158:29096`（外網），`192.168.55.60:9092`（內網）。
  - 開發環境：`192.168.9.231:9092` 等。
- **Cassandra 叢集**：連線至 `192.168.55.80`，keyspace `predict` 與 `member`。
- **策略設定**：於 `project/AppSettings.py` 中的 `settings["Service"]["strategy"]` 定義各策略對應的遊戲類型與 LID。
- **容器運作**：Dockerfile 基於 `python:3.9.13-slim-buster`，ENTRYPOINT 為 `python ./project/__main__.py`，需啟動時提供環境參數。
- **依賴安裝**：需先透過內部 PyPI（`http://localhost:8070`）安裝 `TCZB` 套件，再安裝 `requirements.txt`。

## 相關連結
- **GitLab 儲存庫**：https://git.zbdigital.net/CrawlerAgent/predictrobotbyconnect.git
- **Portainer 服務標籤**：`PRD_Docker_Swarm | predictrobotbyconnect:latest`（容器 ID: `6f76899dd49c`）
- **內部 API 參考**：LID 查詢 https://inplayz.com/apiservice/api/predict/topics