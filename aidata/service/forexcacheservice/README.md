# ForexCacheService

## 概述

ForexCacheService 是一個背景服務（Worker），負責從 Kafka 訂閱外匯即時數據（Topic: `forexdata`），經資料轉換與驗證後，批量寫入 Redis 作為快取，提供高效的外匯資料查詢能力。服務部署於 Docker Swarm 集群，環境區分 PRD、Local、BAK 等。

## 主要功能

- **Kafka 消費**：使用 Confluent Kafka 客戶端，從指定 Topic 訂閱即時外匯資料。
- **資料處理**：將原始訊息轉換為 `ForexData` 物件，驗證資料完整性，並過濾保留最新資料。
- **Redis 寫入**：支援批量寫入 Redis String 與 Hash 型態，確保寫入效能；可同時寫入多個 Redis 節點（透過 ConnectId 區分）。
- **日誌記錄**：使用內部 `IKafkaLogger` 將執行日誌送往 Kafka（Topic: `applogs`），方便集中監控。

## 技術棧

- **語言與框架**：C# / .NET 6 (Worker 服務)
- **訊息佇列**：Apache Kafka (Confluent)
- **快取資料庫**：Redis (StackExchange.Redis)
- **內部套件**：ECCore、ECFramework.ECService、ForexModel
- **容器化**：Docker、Docker Compose / Swarm
- **組態管理**：appsettings.{Environment}.json + 環境變數

## 組態與部署注意

### 組態檔結構

服務依賴 `appsettings.json` 搭配環境變數 `DOTNET_ENVIRONMENT` 切換不同環境設定檔（如 `appsettings.Local.json`、`appsettings.PRD.json`）。

主要設定項目：

- **KafkaLoggerSettings**：服務日誌輸出的 Kafka 集群與 Topic。
- **AppSettings.KafkaSetting**：消費的外匯資料 Kafka 集群、GroupId、訂閱 Topic。
- **AppSettings.RedisSettings**：Redis 連線資訊（可配置多個 ConnectId，每個對應一組伺服器與 DB）。

範例（PRD）：
```json
{
  "Version": "1.0.0",
  "Environment": "PRD",
  "AppSettings": {
    "KafkaSetting": {
      "GroupId": "CurrencyCacheXSystem",
      "BootstrapServers": "192.168.55.85,192.168.55.86,192.168.55.87",
      "Subscribe": "forexdata"
    },
    "RedisSettings": [
      { "ConnectId": "ForexDataNode1", "Servers": "192.168.55.80:6379", "DB": 8 }
    ]
  }
}
```

### 部署注意

- **容器映像**：基於 `mcr.microsoft.com/dotnet/sdk:6.0` 建置，最終運行時使用 `dotnet ForexCacheService.dll`。
- **時區設定**：Dockerfile 已固定時區為 `Asia/Taipei`。
- **Swarm 服務**：Portainer 中 Key 為 `PRD_Docker_Swarm`，服務名稱 `forexcacheservice`，類型標示為 `webapi`（實際為背景 Worker，不開放 HTTP 埠）。
- **資源需求**：建議分配至少 512MB 記憶體，並確保網路可連線至 Kafka 與 Redis。

## 相關連結

- GitLab 原始碼：[https://git.zbdigital.net/Currency/forexcacheservice.git](https://git.zbdigital.net/Currency/forexcacheservice.git)
- Portainer 服務管理：內部 Portainer 節點，服務關鍵字 `forexcacheservice`