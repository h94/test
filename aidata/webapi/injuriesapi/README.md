# Injuries API 內部服務目錄

## 概述

此服務為一個基於 Flask 的 RESTful API，專門處理各大運動聯盟的傷兵名單資料。透過 Cassandra 資料庫儲存與查詢傷兵資訊，支援多來源、多聯盟、多球隊的傷兵資料整合。部署於 Docker Swarm 叢集，並以 Portainer 管理容器映像。

## 主要功能

- **傷兵資料查詢** (`GET /api/injuries/v1/injurylist`)  
  支援依 `gtype`（賽事類型）、`league`（聯盟）、`team`（球隊）篩選，回傳 JSON 格式的傷兵清單。
- **傷兵資料更新** (`POST /api/injuries/v1/update`)  
  接收批量傷兵資料，寫入 Cassandra，並自動清理過期資料（當日首次更新時刪除昨日資料）。
- **版本檢查** (`GET /api/version`)  
  回傳目前部署的版本號（基於檔案最後修改時間），用於健康檢查與版本驗證。
- **自動清除舊資料**  
  每次更新時，若日期變更則刪除 `update_date` 小於當日的記錄，避免歷史資料累積。

## 技術棧

| 類別 | 技術 |
|------|------|
| 語言與框架 | Python 3.9, Flask 3.1 |
| 資料庫 | Cassandra (透過 cassandra-driver) |
| 訊息佇列 / 日誌 | Kafka (自訂 Logger 設定，支援多 Broker) |
| 內部套件 | TCZB（自訂工具函式庫，由 GitLab 私有源安裝） |
| 容器化 | Docker, 基礎映像 `python:3.9-slim-buster` |
| 部署 | Docker Swarm (由 Portainer 管理) |
| 版本控制 | GitLab (https://git.zbdigital.net/CrawlerAgent/injuriesapi.git) |

## 組態與部署注意

### 環境變數與執行模式

應用程式透過命令列參數指定環境（`PRD`、`PRD2`、`PRD3` 或 `Local`），不同環境對應不同的 Kafka Logger 位址：

- **PRD 環境**：使用 `49.213.1.158:29096`
- **Local 開發**：使用內部三台主機 `192.168.9.231:9092` 等

### Cassandra 叢集設定

資料庫連線位址寫在 `project/AppSettings.py` 的 `settings["provider"]["cluster"]` 中。生產環境預設指向 `192.168.55.80`（Cassandra 叢集）；開發時可註解切換至本機測試用位址。

### 連接埠

- 容器內部監聽 `5000` 埠（Dockerfile 中 `EXPOSE 5000`）
- 生產環境以 `0.0.0.0` 繫結，由 Portainer 或 Swarm 服務對外映射連接埠

### 啟動方式

```bash
# 生產環境
python project/__main__.py PRD

# 本機測試
python project/__main__.py Local
```

### 注意事項

- 內部套件 `TCZB` 需從自訂 PyPI 源下載，Dockerfile 中已設定 `--trusted-host localhost:8070`
- 若有新增類別（Category），需在 `Categories/` 下建立新檔案，並在 `__main__.py` 中實例化與註冊 Blueprint
- 清理舊資料邏輯：每次 `POST /v1/update` 若日期變更，會刪除所有 `update_date < 當日` 的資料，請確認此行為符合業務需求

## 相關連結

- **原始碼**：[GitLab Repository](https://git.zbdigital.net/CrawlerAgent/injuriesapi.git)
- **Portainer 容器管理**：`PRD_Docker_Swarm` 環境下容器 `cc1554949a41`（映像標籤 `injuriesapi:latest`）
- **內部依賴套件源**：http://localhost:8070 (需內部網路存取)