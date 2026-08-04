# GameSettingSite

## 概述
GameSettingSite 是一個以 ASP.NET Core 10 開發的內部 API 服務，負責提供遊戲設定站台的後端功能，包含使用者認證、商務號帳號管理、球種／聯盟／賽事資料查詢、商務配置（站台、玩法）、賽事對照、AI 新聞服務、Log 匯出、賠率異常警示管理、預測策略查詢（預計廢除）及系統日誌、儀表板、系統設定等模組。服務部署於 Docker Swarm 環境，搭配 Portainer 管理。

## 主要功能
- **認證與授權**：使用者登入、登出、密碼更新、工作階段檢查與訂閱者資訊查詢。
- **商務號管理**：商務帳號登入、建立、查詢、狀態管理、密碼更新，並記錄操作日誌。
- **賽事資料查詢**：依球種、站台、日期、聯盟查詢賽事、隊伍、聯盟的詳細資料與對照（含系統與站台層級）。
- **商務配置**：設定商務號下的站台啟用狀態、聯盟走地配置、玩法設定（球種預設／聯盟／範本／單場賽事），支援 CRUD 操作。
- **AI 新聞服務**：取得指定球種、日期的 AI 生成新聞，以及多語系版本和近期預測結果。
- **日誌查詢**：站台賽事警報紀錄、走地盤口變化紀錄、登入與設定操作紀錄。
- **Log 匯出**：提供 Loki 與 Kafka 資料的批次匯出（CSV），支援建立匯出工作、查詢／刪除工作、下載結果檔案。
- **賠率異常警示管理**：警示查詢（列表與單筆明細）、狀態更新、警示匯出任務（建立、查詢、下載）、設定管理（監控玩法、資料源類型、比分／賠率閾值、球種／資訊源層級配置）及 Webhook 管理。
- **儀表板**：提供即時監控摘要（透過 LS2Service）。
- **系統設定**：讀寫遊戲端系統參數、範本設定、聯盟與賽事層級的客製設定，支援設定移動與站台開關。
- **預測策略查詢（已排定廢除）**：查詢賽事預測結果與策略評分，此功能預計於後續版本移除。

## 技術棧
- **執行環境**：.NET 10, ASP.NET Core
- **API 文件**：Swagger / Swashbuckle
- **容器化**：Docker，基礎映像 `mcr.microsoft.com/dotnet/sdk:10.0`
- **編排**：Docker Swarm（由 Portainer 納管，服務標籤 `gamesettingsite`）
- **依賴服務**：Redis（用於工作階段、快取）、Cassandra（主要儲存層，keyspace `pricecenter`，含 `accounts_*`、`actionlog` 等表）、Loki（用於 Log 匯出查詢）、Kafka（用於 Log 匯出資料來源）、AlertBackendService（用於警示模組轉發），以及內部套件 GameDataModels 與 ECConfig

## 組態與部署注意
- 應用程式入口 DLL：`GameSettingSite.dll`，監聽埠 **5000**。
- 時區固定為 **Asia/Taipei**，已在 Dockerfile 中設定。
- 部署前確認 `appsettings.json` 或環境變數中的 Cassandra 連線資訊、Redis 連線、Loki 與 Kafka 連線（供 ExportLog 使用）及 AlertBackendService（供 Alert 模組使用）的相關金鑰已正確填入。
- 映像建置時需先執行 `dotnet publish`，將輸出放置於 `GameSettingSite/bin/Debug/net10.0/`（亦可調整為 Release 路徑），並確認 `wwwroot` 已包含。
- 本服務需存取內部的大量資料查詢服務（如 PriceCenter、Loki、Kafka、AlertBackendService），網路層需確保可達。
- 本服務以 `gamesettingsite` 角色對 `pricecenter` keyspace 具備 **writer / reader** 權限，主要操作 `accounts_{brand}` 與遊戲設定相關表，進行站台帳號建立、啟用/停用及密碼管理（密碼經雜湊處理，不可明文寫入或回傳）。
- 商務號 UID 來自登入後的工作階段，多數商務 API 需要攜帶 `uid` Query 參數進行身份驗證。
- Swagger UI 可透過 `/swagger` 或 HomeController 的 `APIDoc` 檢視。

## 相關連結
- 原始碼存放庫：[GitLab](https://git.zbdigital.net/Biz/gamesettingsite.git)
- 容器管理：Portainer（服務標籤 `gamesettingsite`）