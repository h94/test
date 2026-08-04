# PriceCenterResult - 賽果寫入服務

## 概述
此服務負責將賽果（price center result）訊息消費後寫入 Cassandra 資料庫中的新表格，以降低後續預測分析系統直接查詢原始資料的壓力，改善整體查詢效能與可用性。

## 主要功能
- 從 Kafka 主題消費即時賽果訊息
- 進行資料解析與格式轉換
- 將結構化賽果寫入 Cassandra 專用表格
- 提供穩定、低延遲的資料供應，減緩預測分析模組的讀取負載

## 技術棧
- **語言** Python 3.8
- **訊息佇列** Apache Kafka（kafka-python）
- **儲存** Apache Cassandra（cassandra-driver）
- **協調服務** Apache ZooKeeper（kazoo）
- **監控** Watchdog
- **容器化** Docker（python:3.8.5-slim-buster）
- **內部函式庫** TCZB

## 組態與部署注意
- 服務透過 `project/__main__.py` 啟動，所有邏輯封裝於 project 套件中
- 容器內時區設定為 Asia/Taipei
- 部署前需確保以下環境或連線資訊正確設定（通常以環境變數注入）：
  - Kafka bootstrap servers
  - Cassandra 集群連線點與 keyspace
  - ZooKeeper 連線位址（若使用）
- 相依於內部 PyPI 伺服器上的 TCZB 套件，Dockerfile 已指定從 `localhost:8070` 安裝，實際部署時需調整該位址或確保內部網路可達
- 可使用標準 Docker 命令建置與執行：
  ```bash
  docker build -t pricecenterresult .
  docker run -d pricecenterresult
  ```

## 相關連結
- [GitLab 原始碼倉庫](https://git.zbdigital.net/CrawlerAgent/pricecenterresult.git)
- [Confluence 設計文件](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47221445)