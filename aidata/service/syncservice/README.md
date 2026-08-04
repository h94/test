# SyncService 內部服務目錄

## 概述
SyncService 是一個基於 .NET Core 3.1 的後台 Worker 服務，負責將來源 Cassandra 資料庫中的賽事、隊伍、聯賽及遊戲設定等資料，即時同步至備援 Cassandra 資料庫。服務同時提供定時清理過期數據與增量同步機制，確保兩端資料的一致性。

## 主要功能
- **賽事同步**：定期從來源庫讀取 games、sitegames 等賽事資料，並寫入目標庫。
- **聯賽與隊伍同步**：比對來源與目標庫的 leagues、teams 資料，僅同步有變更的記錄。
- **遊戲設定同步**：同步 GameTypeSettings、LeagueSettings、TemplateSettings、GameSettings、Users、SiteSettings 等設定資料。
- **定時清理**：每日 11:00 自動清理兩天前的賽事及相關 sitegames 資料。
- **增量同步控制**：透過快取時間戳記，僅拉取自上次同步後有更新的資料。
- **日誌輸出**：使用 Kafka 將服務日誌傳送至集中式日誌系統。

## 技術棧
- **執行環境**：.NET Core 3.1 Worker Service
- **資料庫**：Apache Cassandra（來源：PRD Keyspace；備援：BAK Keyspace；遊戲設定來源：GameSetting-PRD；備援：GameSetting-BAK）
- **日誌**：Kafka（BootstrapServers: 192.168.55.60, Topic: applogs）
- **容器化**：Docker（基礎映像 mcr.microsoft.com/dotnet/core/aspnet:3.1-buster-slim）
- **內部套件**：ECCore、ECFramework.ECService（透過內部 NuGet 伺服器還原）

## 組態與部署注意
- 主要設定檔為 `appsettings.json`，包含 Cassandra 多節點連線、Kafka 日誌參數及支援的遊戲類型列表（BS、BK、HL、SC…等 27 種）。
- 開發環境設定檔為 `appsettings.Development.json`，生產環境請使用 `appsettings.PRD.json`。
- 部署時需確認.NET Core 3.1 執行環境，Docker 映像已設定時區為 `Asia/Taipei`。
- 依賴內部 NuGet 來源：`http://192.168.9.234:8079/repository/nuget-hosted/` 及 `nuget.org-proxy`。
- 服務啟動入口為 `SyncService.dll`，容器內以 `dotnet SyncService.dll` 執行。

## 相關連結
- **原始碼倉庫**：[GitLab - biz/syncservice](https://git.zbdigital.net/biz/syncservice.git)