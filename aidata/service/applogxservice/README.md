# AppLogXService 內部服務目錄

## 概述
AppLogXService 是一個以 .NET 8.0 為基礎的後台工作者服務，負責從 **Kafka** 訂閱應用程式日誌主題（Topic `applogs`），將訊息解析後寫入 **Cassandra** 資料庫，同時也將日誌推送至 **Loki** 以便即時查詢與監控。服務會依照日期自動建立與刪除 Cassandra 表格，並具備重複日誌去重、批次寫入等優化機制。

## 主要功能
- 消費 Kafka 主題 `applogs`，即時接收來自各應用的結構化日誌。
- 將日誌寫入 Cassandra（Keyspace: `applogs`），每日自動建立 `logsYYYYMMdd` 表格，並在 7 天後自動刪除舊表。
- 支援 Cassandra 索引（預設對 `requestid`、`uri` 建立索引）。
- 同步將日誌推送至 Loki，便於 Grafana 可視化。
- 批量寫入（40KB 門檻）與短時間重複日誌去重（checksum 比對）。
- 自動記錄活躍應用列表（`applist` 表），定期更新最後活動時間。

## 技術棧
| 類別       | 技術                                     |
| ---------- | ---------------------------------------- |
| 語言與執行環境 | .NET 8.0 (Worker Service)                |
| 訊息佇列   | Apache Kafka（透過 Confluent.Kafka 1.8.2）|
| 資料庫     | Apache Cassandra（CassandraCSharpDriver 3.17.1）|
| 日誌彙整   | Loki (HTTP Push)                         |
| 容器化     | Docker (基於 mcr.microsoft.com/dotnet/sdk:8.0) |
| 建置工具   | Visual Studio 2022 / .NET CLI            |

## 組態與部署注意
- **主要設定檔**：`appsettings.json`（正式環境）及 `appsettings.Development.json`（開發環境）。
  - `KafkaSetting.BootstrapServers`：Kafka 叢集位址。
  - `KafkaSetting.GroupId`：Consumer Group ID（正式：`AppLogXSystem`，開發：`AppLogXSystem_Test`）。
  - `CassandraSetting.ContactPoints`：Cassandra 節點位址。
  - `CassandraSetting.Keyspace`：固定為 `applogs`。
  - `CassandraSetting.TableSql`：用於每日建立表格的 CQL 樣板。
  - `IsLocal`：是否為本機開發環境（影響 Loki 的 `env` 標籤）。
- **Dockerfile** 採用多階段建置，最終映像基於 `mcr.microsoft.com/dotnet/sdk:8.0`（注意：使用 SDK 而非 Runtime 映像，生產環境建議改為 Runtime 以縮小體積）。
- **時區設定**：容器內已設定 `TZ=Asia/Taipei`，確保日誌時間正確。
- **環境變數**：可透過環境變數覆蓋 `DOTNET_ENVIRONMENT` 切換設定檔（預設 `Development`）。
- **部署至 Portainer**：服務以容器方式運行，PortainerKey 為 `SRV60`，容器 ID `0d96b6882fe8`。
- **連線埠**：無對外暴露埠（純背景工作者）。
- **記憶體與執行緒**：Worker 使用 `ThreadPool.QueueUserWorkItem` 處理日誌，需注意並行量與記憶體使用。

## 相關連結
- **GitLab 原始碼**：https://git.zbdigital.net/Architecture/applogxservice.git
- **Portainer 管理介面**：請洽 IT 團隊取得內部網址（服務名稱：AppLogXService）