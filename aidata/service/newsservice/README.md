# NewsService

## 概述
NewsService 為運動新聞與 AI 內容管理後端服務，負責儲存、查詢與更新各類運動新聞（Sports News）、AI 生成新聞、AI 預測報告及運動站台文章，主要支援內部運動數據平台與多個前端站台（例如 inplayz、GS、LT Sports）。

## 主要功能
- **服務健康與版本** (`/api/heart`、`/api/version`)：提供心跳檢查與版本資訊。
- **運動新聞管理**
  - 新增 (`POST /api/v1/sports/{gameType}`)、查詢 (`GET /api/v1/sports`)、刪除 (`DELETE /api/v1/sports/{gameType}`) 運動新聞，支援多球種、多語系、時間區間與標籤篩選。
  - 自動建立資料表 (`POST /api/v1/system/autocreatetable`)。
- **AI 新聞管理**
  - 依日期取得 AI 新聞 (`/api/v1/sports/ai/{gtype}/{gdate}`)，並支援 inplayz/GS/LT 等不同站台路由。
  - 取得單筆 AI 新聞 (`/api/v1/sports/ai/{gtype}/{gdate}/{lid}/{gid}/{llmhashkey}/{status}`)。
  - 人工修訂 AI 新聞 (`PUT /api/v1/sports/ai/{gtype}/{gdate}/{lid}/{gid}/{llmhashkey}/{status}`)。
- **AI 預測與 Inplay**
  - 取得 AI 預測報告 (`/api/v1/sports/aireport/{gtype}/{lid}`)。
  - 取得即時 AI Inplay 預測 (`/api/v1/sports/aiinplay/{gtype}`)。
- **AI 熱門討論賽事** (`/api/v1/sports/ai/hotdiscussiongames`)：設定、查詢、刪除熱門討論賽事。
- **運動站台文章** (`/api/v1/sportarticles`)：文章的新增/更新、清單查詢、單篇查詢與刪除，可依文章分類（如 twsl）篩選。

## 技術棧
- **運行環境**：.NET 8 (ASP.NET Core Web API)
- **資料庫**：Cassandra（透過 ECCore 等自訂組件存取）
- **容器化**：Docker（基於 `mcr.microsoft.com/dotnet/sdk:8.0` 映像）
- **日誌與配置**：`ILogger`、`IConfiguration`、自訂 `IECConfig`
- **時區**：Asia/Taipei
- **部署平台**：PRD Docker Swarm（Portainer Key: `PRD_Docker_Swarm|container|newsservice`）

## 組態與部署注意
- **Docker 執行**：Dockerfile 直接使用 .NET SDK 映像執行編譯後的 DLL，非典型生產配置，必要時可考慮切換為 runtime 映像並加入多階段建置。
- **時區設定**：容器內已透過 `ENV TZ=Asia/Taipei` 與符號連結指定時區，確保時間相關邏輯一致。
- **配置項目**（`appsettings.json` 或環境變數）：
  - `Version` 與 `Environment`：用於 `/api/version` 回應。
  - Cassandra 連線參數（須確保可達性及 keyspace 權限）。
  - 各站台對應的資料表名稱（如 `ainews_gs`、`ainews_lt`）。
- **Portainer 部署**：服務已註冊於 Portainer（Key `PRD_Docker_Swarm|container|newsservice`），可透過 Portainer 進行啟停、查看日誌及滾動更新。
- **API 基底路徑**：預設對外端口 `5000`，路由前綴為 `/api`。

## 相關連結
- GitLab 倉庫：[https://git.zbdigital.net/Biz/newsservice.git](https://git.zbdigital.net/Biz/newsservice.git)