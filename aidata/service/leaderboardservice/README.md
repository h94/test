# LeaderboardService

## 概述
LeaderboardService 是一個基於 .NET 6.0 的內部排行榜微服務，提供排行榜設定與內容的 CRUD 操作、模板與動畫資源查詢，以及自動化排程刷新外部 API 排行榜資料。服務部署於 PRD Docker Swarm 叢集（Portainer 容器名 `leaderboardservice`），監聽 5000 port。

## 主要功能
*   **排行榜管理**：支援建立、查詢、更新、刪除排行榜設定與內容，並保留內容歷史紀錄。
*   **資源查詢**：提供排行榜模板樣式列表與動畫效果列表 API，供前端或其他服務選用。
*   **自動刷新**：系統排程可呼叫 `/api/v1/system/flashcharts`，針對 DataSource 為 API 且有 FlashTime 設定的排行榜自動拉取外部資料並更新內容。
*   **健康與版本**：`/api/heart` 回傳伺服器時間，`/api/version` 回傳服務版本、環境與建置時間。
*   **測試輔助**：提供 `/api/v1/system/testdata` 產生 10 筆模擬排行榜明細，方便開發與 API 資料來源測試。
*   **Swagger 文件**：內建 Swagger UI，詳細描述每個端點與模型。

## 技術棧
*   **執行環境** .NET 6.0（ASP.NET Core）
*   **容器** Docker（基礎映像 `mcr.microsoft.com/dotnet/sdk:6.0`）
*   **文件** Swashbuckle / Swagger
*   **時區** Asia/Taipei
*   **相依模組** `ECCore`（組態）、`LeaderboardModels`（資料模型）

## 組態與部署注意
*   **服務埠**：`5000`（容器）
*   **環境變數**（透過 `appsettings.json` 或 `IECConfig`）：
    *   `Version`：服務版本號
    *   `Environment`：環境標記（例如 Local、Staging、Production）
*   **資料庫連線**：由 `ECCore` 管理連線字串，部署時需確保組態正確。
*   **建置與發佈**：Dockerfile 直接複製已編譯的 `LeaderboardService.dll`，因此部署前需先建置專案並將 `bin/Debug/net6.0/`（或 Release）內容放入映象。
*   **部署指令**（範例）：
    ```bash
    docker build -t leaderboardservice .
    docker stack deploy -c docker-compose.yml leaderboard
    ```
    在 Portainer PRD_Docker_Swarm 環境中對應服務名稱 `leaderboardservice`。

## 相關連結
*   GitLab Repository：[https://git.zbdigital.net/Biz/leaderboardservice.git](https://git.zbdigital.net/Biz/leaderboardservice.git)
*   Swagger UI：`http://<host>:5000/swagger`