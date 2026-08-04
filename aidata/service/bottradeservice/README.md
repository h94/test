## 概述

`bottradeservice` 是運行於 Docker Swarm（生產環境）的自動化機器人交易服務，負責模擬真實玩家行為，週期性對體育賽事市場進行掃描、隨機買入、並依據停損停利規則自動賣出。服務透過內部 TCZB 框架與 Cassandra 資料庫溝通，完全獨立於其他交易流程，用於提高市場流動性與仿真度。

## 主要功能

- **週期性交易排程**  
  每個週期執行完整的 Step1~Step5 流程：
  1. 掃描可交易賽事（SC、BK、BS 球種，今日與明日賽事）
  2. 根據賠率快照、剩餘庫存比例等條件篩選適合買入的賽事
  3. 隨機選取機器人帳號進行買入操作，具備單輪與單機器人買入次數上限
  4. 搜尋近期活躍機器人持倉，進行停損、停利賣出評估
  5. 自動執行賣出單（避開系統不收賣單的零庫存玩法）

- **冷卻與上限機制**  
  買入後對相同帳號、賽事、玩法設立冷卻時間，避免短期重複買入；支援單輪總買入上限與單機器人買入上限動態計算。

- **買入偏好與動態門檻**  
  可設定優先買入賽事條件（如剩餘庫存比例、賠率分佈），並根據穩定雜湊為每場賽事隨機化門檻。

- **交易歷史解析**  
  解析 Cassandra 中的 `trade_history` 欄位，以 FIFO 方式還原未平倉買入批次，確保賣出價量決策正確。

- **執行摘要通知**  
  每週期結束後輸出詳細摘要並發送通知（包含掃描場次、買賣機器人數、交易次數等）。

## 技術棧

- **執行環境**：Python 3.9（`python:3.9-slim-buster` 容器）
- **分散式儲存**：Cassandra（透過 `cassandra-driver`）
- **HTTP 客戶端**：`httpx`（用於內部 API 呼叫）
- **內部框架**：`TCZB`（包含訊息推送、交易遊戲客戶端等基礎設施）
- **容器化**：Docker（`Dockerfile` 已提供）
- **部署平台**：Docker Swarm（Portainer 管理，`PRD_Docker_Swarm` 叢集）
- **排程**：服務自身內部迴圈（非外部排程），可依需求設定執行週期

## 組態與部署注意

- **訂製套件源**  
  Docker 建置時需確保可存取 `http://localhost:8070` 的內部 PyPI 源來安裝 `TCZB`；實際部署時應調整為叢集內可達位址或使用私有 registry。

- **環境變數與設定**  
  服務依賴 `service_config`（透過框架注入）控制以下關鍵參數：
  - `buy_success_limit_ratio_per_cycle`：單輪買入總數上限比例
  - `buy_success_limit_per_robot`：單一機器人買入次數上限
  - `robots_per_cycle`：每輪啟動機器人數
  - `snapshot_fetch_concurrency`：賠率快照並行查詢數量
  - `buy_game_preference`：買入偏好及門檻設定

- **Cassandra 連線**  
  需確保容器可連線 Cassandra 叢集，連線資訊由框架（`TCZB`）統一管理，無需額外設定。

- **時間區域**  
  容器強制設定 `TZ=Asia/Taipei`，確保所有時間計算使用台北時間。

- **日誌與監控**  
  服務透過 `send_msg` 推送重要事件與週期摘要，可用於整合日誌或警示系統。

## 相關連結

- **GitLab 倉庫**：[https://git.zbdigital.net/CrawlerAgent/bottradeservice.git](https://git.zbdigital.net/CrawlerAgent/bottradeservice.git)
- **Portainer 服務**：`PRD_Docker_Swarm` 叢集內 `bottradeservice` 容器
- **相依服務**：`trade-game` 系列 API（提供可交易賽事與賠率快照）