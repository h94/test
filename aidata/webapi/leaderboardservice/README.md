# LeaderboardService

## 概述

LeaderboardService 為一個內部排行榜與圖表管理 Web API 服務。負責處理圖表（Charts）的建立、更新、刪除、內容自動刷新，以及動畫、樣板、系統管理等核心業務邏輯。部署於 Docker Swarm 環境，使用 .NET 6.0 開發。

## 主要功能

- **圖表 CRUD**：建立、讀取、更新、刪除圖表設定與內容。
- **自動刷新內容**：透過 SysManagerService 定時監控，當設定的 FlashTime 到達時自動擷取外部資料源並更新圖表內容。
- **動畫與樣板管理**：支援動畫列表與樣板取得的服務。
- **資料驗證**：針對圖表標題、內容、資料源等參數進行有效性檢查。
- **系統測試資料**：提供測試用的圖表內容產生方法（GetTestChartsContent）。

## 技術棧

- **語言/框架**：C# .NET 6.0（WebApi）
- **內部套件**：ECCore、ECFramework.ECService、LeaderboardModels
- **資料庫**：MySQL（透過 ECCore 連接）
- **日誌**：Kafka（IKafkaLogger）
- **設定管理**：Zookeeper（非強制遠端設定）
- **容器化**：Docker（Linux，port 5000）
- **排程**：內建定時任務（AutoFlashChartsContent）

## 組態與部署注意

- **環境設定檔**：`appsettings.{Environment}.json`（如 Local、PRD）包含資料庫連線、Kafka、Zookeeper 等組態。
- **Dockerfile**：使用 `mcr.microsoft.com/dotnet/sdk:6.0` 作為基礎映像，暴露 5000 埠，並設定時區為 `Asia/Taipei`。
- **部署平台**：PRD 環境運行於 Docker Swarm（PortainerKey 標示 `PRD_Docker_Swarm`）。
- **資料庫**：需先建立 Leaderboard 資料庫，並確保 LeaderboardUser 具備對應權限。
- **外部依賴**：需確保 MySQL、Kafka、Zookeeper 服務可連通（位置依環境而異，請參考對應 appsettings）。

## 相關連結

- **GitLab 倉庫**：[https://git.zbdigital.net/biz/leaderboardservice.git](https://git.zbdigital.net/biz/leaderboardservice.git)