# CryptoFlowService 內部服務目錄

## 概述
CryptoFlowService 是一個基於 .NET 6 的常駐背景服務，部署於 Docker Swarm 叢集。主要負責從 Kafka 主題 `cryptodata` 消費即時加密貨幣資料，進行資料轉換與合併（K線處理），並將結果寫入 Cassandra 資料庫，同時更新系統儀表板（Dashboard）的運作狀態。該服務作為加密貨幣資料管線的核心環節，確保資料流通與儲存的一致性。

## 主要功能
- **Kafka 消費**：透過 Confluent Kafka 用戶端訂閱 `cryptodata` 主題，即時接收原始加密貨幣資料。
- **資料轉換與 K線彙總**：利用 `ICryptoDataTransfer` 將原始資料解析為統一的 `CryptoData` 格式，並依時間戳（每分鐘）彙整出 K 線資料（開高低收、成交量）。
- **Cassandra 寫入**：將彙總後的 K 線資料以 `UPDATE` 批次寫入對應的 Cassandra 表格；同時更新 `machines` 表中的儀表板狀態資訊。
- **儀表板狀態更新**：追蹤每個交易對（Type + Site + Code）的最新資料時間，並寫入 Cassandra 供前端儀表板查詢。
- **內部記錄**：透過 Kafka Logger 將服務運作日誌傳送至 `applogs` 主題，並定期輸出運行狀態。

## 技術棧
| 技術 | 用途 |
|------|------|
| .NET 6 (Worker Service) | 應用程式框架 |
| Confluent.Kafka | Kafka 消費端 |
| Apache Cassandra | 資料持久化儲存 |
| ECFramework.ECService | 內部框架（依賴注入、設定管理） |
| CryptoModel | 加密貨幣資料模型 |
| ECCore | 基礎元件（Kafka/Cassandra Provider 抽象） |
| Newtonsoft.Json | JSON 序列化 |
| Docker | 容器化部署（目標 .NET 6 SDK 映像） |

## 組態與部署注意
### 設定檔結構
- `appsettings.json`：基底設定（空白）
- `appsettings.{Environment}.json`：各環境專屬設定（目前支援 `Local`、`BAK`、`PRD`）
- 程式啟動時會依 `DOTNET_ENVIRONMENT` 環境變數載入對應設定檔
- 設定檔包含：
  - `Version` / `Environment` 識別
  - `KafkaLoggerSettings`：日誌 Kafka 叢集資訊
  - `AppSettings`：業務邏輯相關（Kafka 消費設定、Cassandra 連線、`WriteCryptoData` 開關）

### 部署注意
- **Docker Swarm**：Portainer 標籤表明部署於 Swarm，建議使用 `docker stack deploy` 或 Portainer UI 管理。
- **Dockerfile** 基於 `mcr.microsoft.com/dotnet/sdk:6.0`，執行階段使用相同 SDK 映像（無 runtime-only 層，便於內部除錯）。
- **時區設定**：固定為 `Asia/Taipei`，需確保宿主機時間正確。
- **NuGet 來源**：建置時使用內部 NuGet 伺服器（`http://192.168.9.234:8079/repository/nuget-hosted/`），若無法連線可能需調整 Dockerfile 中的來源。
- **環境變數**：必須設定 `DOTNET_ENVIRONMENT` 為對應環境名稱（如 `PRD`），否則預設為 `Production` 且可能找不到設定檔。
- **資源需求**：此服務為長時間執行的背景工作，建議配置適當 CPU/記憶體限制，避免單點故障。

## 相關連結
- GitLab 原始碼：[https://git.zbdigital.net/Currency/cryptoflowservice.git](https://git.zbdigital.net/Currency/cryptoflowservice.git)