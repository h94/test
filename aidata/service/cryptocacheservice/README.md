# CryptoCacheService 內部服務目錄

## 概述
CryptoCacheService 是一個基於 .NET 6 的後端背景服務，部署於 **Docker Swarm** 生產環境（PRD）。該服務負責從 Kafka 訂閱加密貨幣資料，經過驗證與轉換後，批量寫入 Redis 快取，以提供高效查詢。

## 主要功能
- **Kafka 消費**：訂閱 `cryptodata` 主題，即時接收原始加密貨幣資料。
- **資料處理**：轉換原始資料為標準 `CryptoData` 模型，並進行資料驗證。
- **Redis 快取**：以 Hash 結構將最新資料寫入多個 Redis 節點，支援分散式快取。
- **日誌記錄**：透過 Kafka Logger 將系統日誌發送至 `applogs` 主題，便於監控與除錯。

## 技術棧
- **語言與框架**：C# .NET 6（Worker Service）
- **訊息佇列**：Apache Kafka（使用 Confluent.Kafka 用戶端）
- **快取資料庫**：Redis（使用 StackExchange.Redis）
- **依賴注入框架**：ECFramework（內部封裝）
- **容器化**：Docker（多階段建置，基底映像 `mcr.microsoft.com/dotnet/sdk:6.0`）
- **部署平台**：Docker Swarm（PRD 環境）

## 組態與部署注意
- **環境設定**：不同環境使用對應的 `appsettings.{環境}.json`，目前支援 `Local`、`BAK`、`PRD`。
- **NuGet 來源**：Dockerfile 中指定了內部 NuGet 伺服器（`http://192.168.9.234:8079/repository/nuget-hosted/`）及 proxy，建置時需確保可存取。
- **Kafka / Redis 位址**：各環境位址不同，請參考對應設定檔（PRD 使用 `192.168.55.85~87` Kafka 叢集、`192.168.55.80:6379` Redis）。
- **時區**：映像中已設定 `TZ=Asia/Taipei`，確保時間正確。
- **啟動指令**：`dotnet CryptoCacheService.dll`，容器以 root 執行。

## 相關連結
- **原始碼倉庫**：[GitLab - Currency/cryptocache](https://git.zbdigital.net/Currency/cryptocache)（推測基於 PortainerKey 推斷，如路徑不同請確認）
- **Portainer 管理**：Docker Swarm 服務名稱 `cryptocacheservice`（標籤 `swarm`）
- **內部 NuGet 伺服器**：`http://192.168.9.234:8079/repository/nuget-hosted/`