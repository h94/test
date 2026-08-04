# crawleragentbc — 爬蟲代理 BC 解析服務

## 概述
本服務為 **CrawlerAgent** 系統中的 BC（Business Context）解析模組，以輕量容器部署。主要負責接收外界爬蟲任務、擷取目標頁面、執行內容解析，並經由 Kafka 與下游服務交換資料。服務提供基於 Flask-SocketIO 的即時通訊介面，便於任務狀態推播與監控。

## 主要功能
- **任務接收與排程**：透過 HTTP / WebSocket 接收 BC 解析要求，並將任務推送至 Kafka 佇列。
- **頁面爬取與解析**：依任務設定之規則抓取目標網頁，提取結構化欄位資料。
- **狀態回報**：利用 Socket.IO 即時回報任務進度、成功／失敗訊息予調用方。
- **高可用協調**：整合 ZooKeeper (kazoo) 實現分布式鎖與領導者選舉，確保多執行個體協作不重複處理。
- **內部函式庫支援**：依賴 `TCZB` 套件，提供公司自訂的資料處理邏輯。

## 技術棧
- **Python 3.9** (Slim Buster 基礎映像)
- **Web 框架**：Flask + Flask-SocketIO
- **訊息佇列**：Apache Kafka (kafka-python)
- **協調服務**：Apache ZooKeeper (kazoo)
- **容器化**：Docker
- **其他關鍵套件**：requests、bidict、cachetools、pytest 等（詳見 `requirements.txt`）
- **內部依賴**：TCZB（安裝自內部套件倉庫）

## 組態與部署注意
- **容器建置**：使用專案根目錄下的 `Dockerfile` 建置映像，會自動複製原始碼並安裝相依套件。
- **環境變數**：
  - `TZ=Asia/Taipei` 已內建於映像中，確保時區正確。
  - Kafka 與 ZooKeeper 連線設定應透過環境變數或設定檔注入（如 `KAFKA_BOOTSTRAP_SERVERS`、`ZOOKEEPER_CONNECT`）。
- **內部套件庫**：建置時需確保能存取 `http://localhost:8070` 上的 Python 套件庫，否則 `TCZB` 安裝會失敗。正式部署前應調整為對應之內部索引位址或改為離線安裝。
- **執行入口**：容器啟動後直接執行 `python ./project/__main__.py`，請確保 `project` 模組結構完整。
- **對外通訊埠**：若使用 Flask 內建伺服器，預設埠為 5000（可依 `flask run` 參數調整）；Socket.IO 則依相同埠號運作。建議於容器執行時映射所需埠號。
- **日誌與監控**：可透過程式內部設定的日誌層級進行查錯；需注意 Kafka 消費者/生產者連線狀態。

## 相關連結
- **原始碼倉庫**：[GitLab - CrawlerAgent/crawleragentbc](https://git.zbdigital.net/CrawlerAgent/crawleragentbc.git)
- **Portainer 服務入口**：`SRV84` (container: crawleragentbc)
- **內部依賴庫**：TCZB (需聯繫基礎架構團隊取得安裝指引)