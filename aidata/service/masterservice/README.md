# MasterService 內部服務目錄

## 概述
MasterService 是一個用於運動賽事預測數據分析與高手排名的後端服務。它從 Google Sheets 讀取配置，透過 Kafka 接收/傳送賽事數據，儲存於 Cassandra 資料庫，並定時計算玩家預測績效，產出排行榜報表。服務支援多種運動類型（棒球、籃球、足球、冰球、網球、電競等），並區分主推與一般預測模式。

## 主要功能
- **資料收集與處理**：從指定的 Kafka 集群接收 HTML / game_data，經解析後轉存至 Cassandra。
- **高手排名計算**：依據玩家預測紀錄（勝率、平均賠率、獲利點數、連勝天數等）計算排名分數，篩選出高手與殺手。
- **報表產出**：將計算結果寫入 Google Sheets（透過 Sheets API）及 Cassandra（`predictfilterreports` 表）。
- **自動化排程**：依當日時間自動執行不同球種的排行計算，並支援人工調整賽事。
- **黑名單與機器人過濾**：可設定帳號黑名單（鎖定至特定日期），並過濾機器人帳號。
- **心跳監控**：每分鐘回報服務版本，便於監控。

## 技術棧
| 元件         | 技術                                                   |
| ------------ | ------------------------------------------------------ |
| 語言         | Python 3.8.5                                           |
| 容器化       | Docker（基礎映像 `python:3.8.5-slim-buster`）          |
| 資料庫       | Apache Cassandra（集群 `192.168.55.80`）               |
| 訊息佇列     | Apache Kafka（多個集群，依環境切換）                   |
| 外部 API     | Google Sheets API v4（OAuth 2.0 憑證）                 |
| 內部套件     | `TCZB`（內部 pip 套件，從 `localhost:8070` 安裝）      |
| 部署平台     | Portainer（Docker Swarm，服務名稱 `PRD_Docker_Swarm`） |

## 組態與部署注意
- **環境變數**：服務啟動時需傳入環境名稱（`Local`, `PRD`, `PRD2`, `PRD3`, `PROD`），對應不同的 Kafka 集群與路由設定（定義於 `project/AppSettings.py`）。
- **憑證檔案**：需提供 `cred.json`，內含 Google Sheets API 的 OAuth 2.0 憑證（token、refresh_token、client_id、client_secret 等）。此檔案應妥善保管，勿提交至版本控制。
- **Cassandra 連線**：寫死於 `DataProvider.py` 中的 `192.168.55.80`，若需變更請修改程式碼或透過環境變數注入。
- **Docker 建置**：
  - 使用 `Dockerfile` 建置，先安裝內部套件 `TCZB`（需可存取 `localhost:8070`），再安裝 `requirements.txt` 所列依賴。
  - 容器啟動後會執行 `project/__main__.py`。
- **Portainer 服務標籤**：`PortainerKey=PRD_Docker_Swarm|container|d483da8545c4|masterservice:latest`，表示該服務屬於 PRD 環境的 Docker Swarm，容器 ID `d483da8545c4`，映像標籤 `masterservice:latest`。

## 相關連結
- [GitLab 原始碼倉庫](https://git.zbdigital.net/biz/masterservice.git)
- Portainer 服務頁面（透過 `PortainerKey` 定位）
- Google Sheets 試算表 ID：`1UkfOja2_wWXG-YyZG-vPFGTflXuEr7WI7fBXeia_csY`