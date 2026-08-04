# LeaderboardSite 排行榜服務

## 概述

LeaderboardSite 是一個基於 .NET 6 的 WebAPI 內部服務，提供排行榜（Leaderboard）的建立、管理、動態嵌入及前端渲染功能。服務部署於 Docker Swarm 叢集（PRD 環境），對外暴露 Port 5000，可與會員系統（MemberService）及排行引擎（LeaderboardService）協作，支援多種動畫效果與模板自訂。

## 主要功能

- 排行榜 CRUD：建立、讀取、更新、刪除排行榜。
- 用戶認證：登入、修改密碼、新增用戶（依權限管控）。
- 排行榜內容管理：支援動態排名更新、排名升降動畫。
- 嵌入 JS 輸出：產生可直接嵌入第三方網站的 HTML/CSS 片段。
- 模板與動畫：提供多種版面模板與動畫樣式（updown、fade、scale）。
- 模擬資料展示：內建 FakeData 作為預覽用。

## 技術棧

- **語言與框架**：C# .NET 6、ASP.NET Core WebAPI
- **依賴注入**：ECCore、ECFramework.ECService
- **資料存取**：RestSharp、自定義 RestfulClient（透過 Gateway 呼叫其他微服務）
- **訊息紀錄**：Kafka（AppLogXSystem）
- **設定管理**：Zookeeper（可選遠端設定）、appsettings.json 環境設定
- **容器化**：Docker（mcr.microsoft.com/dotnet/sdk:6.0），時區 Asia/Taipei
- **部署平台**：Docker Swarm（PortainerKey 指示 PRD 環境）

## 組態與部署注意

- **環境變數**：時區需設定為 `Asia/Taipei`（Dockerfile 已處理）。
- **連接埠**：容器內部監聽 5000。
- **相依服務**：需依賴 MemberService（會員管理）與 LeaderboardService（排行榜引擎），透過 Gateway 位址（PRD: `http://192.168.55.60`）呼叫 RESTful API。
- **組態檔**：使用 `appsettings.PRD.json` 覆蓋預設值，包含 Kafka、Zookeeper、Gateway 端點與動畫設定。
- **日誌**：Kafka Topic 為 `applogs`，Consumer Group `AppLogXSystem`。

## 相關連結

- **GitLab 儲存庫**：`https://git.zbdigital.net/biz/leaderboardsite.git`
- **部署環境**：PRD Docker Swarm（服務名：`leaderboardsite`）