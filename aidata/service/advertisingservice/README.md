# AdvertisingService

## 概述
AdvertisingService 為 ZB 數位廣告管理核心後端服務，負責一般廣告（多語系、多類型）與運動站台專屬廣告、公告欄的 CRUD、圖片上傳及系統維護功能。  
服務以容器形式部署於 **PRD Docker Swarm** 叢集，透過 Portainer 管理，提供 RESTful API 供前、後台系統調用。

## 主要功能

### 一般廣告管理 (AdvertisingServiceController)
- 建立、更新廣告（含標題、圖片連結、語系、類型、顯示區間、排序、啟用狀態）
- 依語系與類型查詢廣告（前台用）
- 後台取得全部廣告清單
- 上傳廣告圖檔

### 運動站台廣告管理 (SportAdvertisementController)
- 新增運動站台廣告（依區域區分，如 banner、sidebar）
- 取得全部廣告或依區域篩選
- 更新指定區域內的單一廣告

### 運動公告欄管理 (SportBulletinBoardController)
- 新增、修改、刪除公告
- 以 ID 或全部查詢公告，支援快取控制

### 系統功能 (SystemController)
- 心跳檢測 (`/api/heart`)：回傳伺服器當前時間
- 服務版本查詢 (`/api/version`)：回傳組建版本、環境與建置時間
- 自動建表 (`/api/v1/system/autocreatetable`)：依 Model 自動初始化資料庫表單
- 站台圖片上傳 (`/api/v1/system/upload/imgfile/{site}`)：依站台儲存圖片

## 技術棧
- **語言與框架**：C# / .NET 8, ASP.NET Core Web API
- **部署環境**：Linux Docker (mcr.microsoft.com/dotnet/sdk:8.0)
- **容器管理**：Docker Swarm + Portainer
- **時區設定**：Asia/Taipei（UTC+8）
- **日誌／配置**：ECCore (IECConfig), Microsoft.Extensions.Logging
- **資料庫**：由服務層透過 ORM 存取（支援自動建表）
- **API 通訊**：RESTful JSON，支援 multipart/form-data 檔案上傳

## 組態與部署注意
- Docker 映像檔建置時會複製 `AdvertisingService/bin/Debug/net8.0/` 及 `wwwroot/` 至工作目錄。
- 容器暴露埠號 **5000**，部署時需對應 Swarm 服務埠。
- 環境變數 `TZ=Asia/Taipei` 已於 Dockerfile 設定，確保時間一致。
- 資料庫連線字串等敏感組態應透過環境變數或外部配置注入（如 appsettings.json 掛載）。
- `AutoCreateTable` 端點可用於初始化環境，首次部署後可呼叫以建立必要表格。
- 上傳的圖片與檔案儲存位置需確保容器內路徑具寫入權限，或掛載持久化磁碟區。

## 相關連結
- **原始碼存放庫**： [https://git.zbdigital.net/Biz/advertisingservice.git](https://git.zbdigital.net/Biz/advertisingservice.git)
- **容器管理平台**： Portainer (PRD Docker Swarm)
  - Stack / Service 名稱： `advertisingservice`