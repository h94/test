# crawleragentlsports

## 概述
`crawleragentlsports` 為內部運動數據爬蟲代理服務（服務代號 SRV84），負責從 LSports 數據源擷取即時比賽資訊、賠率與賽程更新，並將處理後的結構化資料透過 Kafka 與 WebSocket 推送給下游系統。服務以 Docker 容器形式部署，確保環境一致性與易於水平擴展。

## 主要功能
- **數據擷取**  
  透過 SFTP 或 API 定時取得 LSports 提供的原始數據檔案（如 XML/JSON 格式）。
- **資料解析與清洗**  
  將原始資料轉換為標準化結構，過濾無效、重複或未授權的內容，並依據業務規則補齊必要欄位。
- **即時訊息發布**  
  處理後的數據即時送入 Kafka（可指定多個 topic），並經由 Socket.IO 向已連線之內部前端應用廣播更新。
- **API 端點**  
  提供 RESTful API 供內部系統查詢最新數據、觸發全量重新拉取或檢視服務狀態。
- **高可用性支援**  
  整合 ZooKeeper 進行服務註冊與 leader election，確保多實例運行時的任務分配與故障轉移。

## 技術棧
- **執行環境**：Python 3.9（容器化，基於 `python:3.9-slim-buster`）
- **Web 框架**：Flask + Flask‑SocketIO
- **訊息佇列**：Apache Kafka（`kafka‑python`）
- **協調服務**：Apache ZooKeeper（`kazoo`）
- **遠端存取**：Paramiko / pysftp（SFTP，用於讀取 LSports 檔案伺服器）
- **安全與加密**：bcrypt、cryptography、PyNaCl
- **內部依賴**：TCZB（公司內部通用工具庫，需從內部 PyPI 安裝）
- **容器管理**：Docker、Portainer（SRV84）

## 組態與部署注意

### 必要環境變數
服務依賴環境變數進行設定，常見項目如下（實際名稱請以程式碼版本為準）：

| 變數名稱              | 說明                         | 範例值                        |
|-----------------------|------------------------------|-------------------------------|
| `KAFKA_BROKERS`       | Kafka 叢集位址（逗號分隔）   | `broker1:9092,broker2:9092`   |
| `KAFKA_TOPIC`         | 資料發佈目標 topic           | `lsports.live`                |
| `ZK_HOSTS`            | ZooKeeper 節點列表           | `zk1:2181,zk2:2181`           |
| `SFTP_HOST`           | LSports SFTP 伺服器位址      | `sftp.lsports.com`            |
| `SFTP_USER`           | SFTP 登入帳號                | `user`                        |
| `SFTP_PASSWD`         | SFTP 密碼（建議使用 Secret） | `********`                    |
| `FETCH_INTERVAL`      | 數據擷取間隔（秒）           | `300`                         |
| `LOG_LEVEL`           | 日誌層級                     | `INFO`                        |

### 部署步驟
1. **建置映像**  
   於專案根目錄執行：
   ```bash
   docker build -t crawleragentlsports:latest .
   ```
   建置過程會安裝 TCZB（需能訪問內部 PyPI 或預先準備）。

2. **推送至內部 Registry**  
   將映像標籤後推送至集團容器倉庫，以利目標主機拉取。

3. **啟動容器**  
   可透過 Portainer 或直接執行：
   ```bash
   docker run -d --name crawleragentlsports \
     -e KAFKA_BROKERS=... \
     -e ZK_HOSTS=... \
     -e SFTP_HOST=... \
     -e SFTP_USER=... \
     -e SFTP_PASSWD=... \
     -e FETCH_INTERVAL=300 \
     crawleragentlsports:latest
   ```

### 執行條件與注意
- **網路需求**：容器需能訪問目標 SFTP 伺服器、Kafka 叢集及 ZooKeeper 所在網路。
- **磁碟空間**：擷取的原始檔案會暫存於容器內 `/tmp` 或指定目錄，請確保足夠空間並定期清理。
- **Kafka 前置作業**：事先建立指定的 topic，並設定適當的 retention 與 partition 數量。
- **ZooKeeper 依賴**：服務利用 ZooKeeper 實作 leader election，若 ZK 集群不可用，部分排程任務可能無法執行或發生重複處理。
- **日誌管理**：建議將容器日誌導向集中式日誌平台（如 ELK），以便追蹤與告警。

## 相關連結
- **原始碼倉庫**：https://git.zbdigital.net/CrawlerAgent/crawleragentlsports.git
- **容器管理平台**：Portainer → SRV84 | container | crawleragentlsports
- **文件與維運手冊**：請參考內部 Confluence（CrawlerAgent 專區）或聯絡開發團隊