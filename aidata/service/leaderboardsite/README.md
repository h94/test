# LeaderboardSite

## 概述
LeaderboardSite 為內部排行榜管理服務，提供即時排行榜設定、內容更新、使用者認證與嵌入式內容產生 API，供前端網站、遊戲大廳或其他服務整合。服務以 ASP.NET Core Web API 形式部署於 Docker Swarm 叢集，並由 Portainer 管理。

## 主要功能
- **心跳與版本查詢**  
  - `/api/heart`：回傳當前伺服器時間。  
  - `/api/version`：顯示服務版本、環境及建置時間。
- **使用者認證**  
  - 登入 (`POST /api/v1/auth/login`)  
  - 查詢個人／全部用戶資料 (`GET /api/v1/auth/user`)  
  - 修改密碼 (`PUT /api/v1/auth/user`)  
  - 新增使用者 (`POST /api/v1/auth/user`)
- **排行榜管理**  
  - 取得使用者擁有排行榜清單 (`GET /api/v1/leaderboard/{account}`)  
  - 取得單一排行榜設定與內容 (`GET /api/v1/leaderboard/setting/{token}`、`content/{token}`)  
  - 建立排行榜 (`POST /api/v1/leaderboard`)  
  - 更新排行榜設定／內容 (`PUT /api/v1/leaderboard/setting/{token}`、`content/{token}`)  
  - 強制重新載入排行榜資料 (`PUT /api/v1/leaderboard/forcereload/{account}/{token}`)  
  - 刪除排行榜 (`DELETE /api/v1/leaderboard/{account}/{token}`)
- **輔助資源**  
  - 取得可用版面模板 (`GET /api/v1/leaderboard/templates`)  
  - 取得動畫效果清單 (`GET /api/v1/animations`)  
  - 產生嵌入式 HTML 內容 (`GET /api/v1/embeded/content/{token}`)
- **測試資料**  
  - `/api/fakedata`：回傳假資料方便前端開發。

## 技術棧
- **執行環境**：.NET 6（SDK 6.0）
- **框架**：ASP.NET Core Web API
- **依賴注入**：`IAuthService`、`ILeaderboardService`、`IECConfig`
- **封裝**：Docker (mcr.microsoft.com/dotnet/sdk:6.0)
- **部署平台**：Docker Swarm（PRD）
- **時區**：Asia/Taipei

## 組態與部署注意
- 服務容器監聽 **5000** 埠，請於反向代理或負載平衡器對應。
- 時區已於 Dockerfile 內設定為 `Asia/Taipei`，日誌時間以此為準。
- 組態檔 (appsettings.json) 透過 `IECConfig` 注入，需確保環境變數或掛載的組態檔包含正確的連線字串、外部服務端點及 `Version`、`Environment` 設定。
- 此服務相依於內部成員服務 (`MemberModels`) 及排行榜模型庫，部署前確認相關 NuGet 套件已還原或組件已複製至 `/app` 目錄。
- 透過 Portainer 管理，Stack 名稱為 `leaderboardsite`，可參考 `PRD_Docker_Swarm` 叢集設定進行更新或重啟。

## 相關連結
- GitLab 儲存庫：[https://git.zbdigital.net/Biz/leaderboardsite.git](https://git.zbdigital.net/Biz/leaderboardsite.git)