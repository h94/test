# ForexFlowService 內部服務目錄

## 概述
ForexFlowService 是一個基於 **.NET 6** 的後台工作者（Worker）服務，負責從 Kafka 訂閱外匯數據（forexdata），進行格式轉換與處理，最終寫入 Cassandra 資料庫，並更新儀表板狀態。服務部署於 Docker Swarm 環境。

## 主要功能
- 從 Kafka 即時消費外匯資料訊息
- 利用 `IForexDataTransfer` 將原始資料轉換為 `FxRateData` 清單
- 批次寫入多張 Cassandra 資料表（依據類型/站點/幣別分表）
- 更新 `CurrencyFlowService` 的儀表板狀態（`machines` 表）
- 非同步佇列處理：內部使用 `ConcurrentQueue` 與獨立寫入執行緒，每分鐘批次寫入一次
- 支援多環境組態（Local / BAK / PRD）

## 技術棧
- **語言/框架**：C# .NET 6
- **訊息佇列**：Apache Kafka（使用 Confluent.Kafka 用戶端）
- **資料庫**：Cassandra（透過內部 `ECCore` 封裝）
- **依賴注入**：內建 `Microsoft.Extensions.Hosting` 與 `ECFramework.ECService`
- **組態管理**：`appsettings.{Environment}.json` + 環境變數
- **容器化**：Docker（Base image: `mcr.microsoft.com/dotnet/sdk:6.0`）
- **部署平台**：Docker Swarm（Portainer Key 標示 PRD_Docker_Swarm）

## 組態與部署注意
- **環境變數**：透過 `DOTNET_ENVIRONMENT` 切換環境（預設 Local）
- **必要組態**（`appsettings.{env}.json`）：
  - `KafkaLoggerSettings`：日誌寫入的 Kafka 叢集
  - `AppSettings.KafkaSetting`：消費外匯數據的 Kafka 叢集、GroupId、訂閱主題
  - `AppSettings.CassandraSettings`：Cassandra 節點與 Keyspace
  - `AppSettings.WriteCryptoData`：是否寫入加密貨幣資料（布林值）
- **NuGet 來源**：需要內部私有 NuGet 伺服器（`http://192.168.9.234:8079/repository/nuget-hosted/`）
- **時區**：`Dockerfile` 已設定 `TZ=Asia/Taipei`
- **部署路徑**：請確認 Docker Swarm 服務名稱與 Portainer Key 一致（`forexflowservice`）

## 相關連結
- **GitLab 原始碼**：`https://git.zbdigital.net/Currency/forexflowservice.git`
- **Portainer 標籤**：PRD_Docker_Swarm / swarm / forexflowservice
- **NuGet 來源**：`http://192.168.9.234:8079/repository/nuget-hosted/`
- **相依套件**：`ECCore`, `ECFramework.ECService`, `ForexModel`, `Confluent.Kafka`, `CassandraCSharpDriver` (透過 ECCore)