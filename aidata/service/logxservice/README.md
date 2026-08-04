# LogXService – 內部服務目錄

## 概述
LogXService 是一個 .NET 6 背景工作服務，負責從 Kafka 訂閱 `nginxlogs` 日誌訊息，解析後寫入 Cassandra 資料庫，同時也支援應用程式日誌（`applogs` 主題）的記錄。服務會按日自動建立與刪除 Cassandra 表，並為常用欄位建立索引。

## 主要功能
- **Kafka 日誌消費**：訂閱 Kafka 主題 `nginxlogs`，持續消費並解析 NGINX 存取日誌。
- **Cassandra 寫入**：將日誌資料寫入 `accesslogs` keyspace 下的每日資料表（`logsYYYYMMDD`）及原始資料表（`rawlogsYYYYMMDD`），並自動建立索引（依 `traceid`、`routing`）。
- **自動表管理**：每日自動建立未來兩天的資料表，並刪除 7 天前的舊表。
- **站點過濾**：透過 `SiteLogSettings` 設定可依站點名稱決定是否記錄日誌，並可設定忽略低回應時間的記錄。
- **應用程式日誌**：支援透過 `KafkaLoggerSettings` 設定另一個消費者，記錄應用程式自訂日誌。

## 技術棧
- **語言與框架**：C# / .NET 6 (Worker Service)
- **訊息佇列**：Apache Kafka (使用 Confluent.Kafka 用戶端)
- **資料庫**：Apache Cassandra (使用 DataStax Cassandra .NET Driver)
- **自訂元件**：ECCore（內部共用函式庫，包含 IKafkaLogger 等）
- **容器化部署**：Docker (base image: mcr.microsoft.com/dotnet/sdk:6.0)

## 組態與部署注意

### 設定檔結構
- `appsettings.json` – 正式環境設定（單節點 Kafka/Cassandra）
- `appsettings.Development.json` – 開發環境多節點設定
- `appsettings.Local.json` – 本機測試設定

### 關鍵設定項目
| 區段 | 說明 |
|------|------|
| `KafkaSetting` | 消費者 GroupId、BootstrapServers、訂閱主題 |
| `CassandraSetting` | 連線點、Keyspace、表格建立 SQL、索引設定 |
| `KafkaLoggerSettings` | 應用程式日誌消費者設定 |
| `SiteLogSettings` | 站點過濾規則 |

### 部署注意事項
- 服務監聽埠 **5000**（Dockerfile EXPOSE）。
- 時區固定為 **Asia/Taipei**。
- Cassandra 表會按日動態創建，請確保 `gc_grace_seconds=60` 適合你的叢集壓縮策略。
- 消費者 GroupId 預設為 `LogXSystem`，請確認與其他消費者不衝突。

## 相關連結
- **GitLab 倉庫**：https://git.zbdigital.net/Architecture/logxservice.git