# CrawlerAgentStandings 爬蟲服務目錄

## 概述

CrawlerAgentStandings 是一個專門負責爬取各大運動聯盟戰績（Standings）資料的內部爬蟲服務。服務透過排程或即時觸發，從 MLB、NBA、KBO、CPBL、NPB、NFL、NHL 及 SofaScore 等資料源取得球隊排名與統計，並經由 Transformer 轉換為統一格式後，推送至 PriceCenter 系統，供後續盤口與數據使用。

## 主要功能

- **多聯盟支援**：內建 MLB、NBA、KBO、CPBL、NPB、NFL、NHL、SOFANBA 共 8 個爬取任務。
- **智慧排程**：每個聯盟可獨立設定有效日期區間（rundateRange）與每日執行時間窗口（runtimeRange），僅在指定時間內執行爬取。
- **資料轉換**：針對不同來源格式（JSON、HTML），內建專屬轉換器（Transformer），將原始資料標準化為統一結構。
- **資料推送**：爬取並轉換完成後，透過 HTTP POST 將整理後的戰績資料送至 PriceCenter Gateway。
- **記錄與監控**：使用 Kafka 日誌系統輸出執行狀態，並可透過 Zookeeper 進行服務協調與路徑管理。

## 技術棧

| 項目 | 技術 |
|------|------|
| 執行環境 | Python 3.8.5（Docker 容器） |
| 容器管理 | Docker / Docker Swarm（Portainer 可視化管理） |
| 資料爬取 | requests、lxml（解析 HTML/XML） |
| 資料結構 | json（處理 API 回應） |
| 日誌系統 | Kafka（透過 TCZB Logger 模組） |
| 協調服務 | Zookeeper（透過 TCZB ZooKeeper 模組） |
| 內部套件 | TCZB（自訂框架，含 Logger、Setting、Globals、Datetime、Versioning 等） |
| 排程機制 | 透過時間條件檢查（程式內迴圈 + sleep） |

## 組態與部署注意

### 執行方式

```bash
python project/__main__.py <Environment> <IntervalSeconds>
```

範例（Local 測試，每 3600 秒執行一次）：
```bash
python project/__main__.py Local 3600
```

### 支援環境

- `Local`（開發測試）
- `PRE`（預發環境）
- `PRD`、`PRD2`（正式環境）

### 組態重點

- **Kafka 位址**：依環境不同（PRD: `192.168.55.60:9092`，PRD2/PRE: `192.168.10.231:9092` 等）。
- **Zookeeper 位址**：所有環境皆使用 `34.96.165.76:2181`，路徑為 `/crawlerservice/standings`。
- **PriceCenter Gateway**：正式環境為 `http://192.168.55.60/pricecenter/api/overview/{gameType}`。
- **內部 PyPI**：Dockerfile 中指定從 `http://localhost:8070` 安裝 `TCZB` 套件，部署時需確保該內部儲存庫可存取。

### 依賴套件

請參考 `requirements.txt`，除標準庫外包含 `requests`、`lxml`、`kafka-python`、`kazoo`、`GitPython` 等。

### 部署提醒

- 容器使用 `python:3.8.5-slim-buster` 基礎映像。
- 時區設定為 `Asia/Taipei`。
- 需掛載對應的網路與環境變數，確保可連線至 Kafka、Zookeeper 及 PriceCenter。
- 每個聯盟的爬取時間窗口應與賽季同步，請留意日期設定（rundateRange 與 runtimeRange）。

## 相關連結

- **GitLab 儲存庫**：[https://git.zbdigital.net/CrawlerAgent/crawleragentstandings.git](https://git.zbdigital.net/CrawlerAgent/crawleragentstandings.git)
- **Portainer 管理介面**：PRD 環境容器 ID `3785c636e968`（Docker Swarm 服務: `crawleragentstandings`）