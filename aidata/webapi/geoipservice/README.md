# GeoIPService 內部服務目錄

## 概述
GeoIPService 是一個基於 .NET 6 的 Web API 服務，提供 IP 地址的地理位置查詢與翻譯功能。整合 MaxMind GeoIP2 資料庫，支援以 Redis 快取查詢結果，並可將國家/城市名稱翻譯為指定語言。服務部署於 Docker Swarm 叢集，通過 Portainer 管理。

## 主要功能
- **IP 地理位置查詢**：根據輸入的 IP 位址，回傳國家、城市、經緯度等 GeoIP 資訊。
- **多語言翻譯**：可選參數 `countryCode`，將國家與城市名稱翻譯成對應語言（預設為英文）。
- **Redis 快取**：查詢結果會存入 Redis 以加速後續相同 IP 的請求。
- **日誌與監控**：透過 Kafka 輸出應用程式日誌，並整合內部 EC Framework 做健康檢查及錯誤處理。

## 技術棧
- **Runtime／框架**：.NET 6.0、ASP.NET Core WebAPI
- **內部框架**：ECCore、ECFramework.ECService
- **資料庫**：MaxMind.GeoIP2（離線 GeoLite2-City.mmdb 資料庫）
- **快取**：Redis（設定檔中定義 `GeoIP` 連線，DB=2）
- **日誌**：Kafka（applogs topic）
- **配置中心**：ZooKeeper（用於語言翻譯設定，路徑 `/language`）
- **容器與編排**：Docker、Docker Swarm（Portainer 管理）
- **其他**：BouncyCastle（部分封裝依賴）

## 組態與部署注意
- **Docker 映像**：使用 `mcr.microsoft.com/dotnet/sdk:6.0` 作為基底，開放埠 5000。
- **環境設定**：對應環境使用不同的 `appsettings.{Environment}.json`（Local、DEV、PRE、PRD）：
  - ZooKeeper 與 Kafka BootstrapServers 依環境變更。
  - Redis 連線位址：PRD 使用 `192.168.55.80:6379`；其他環境多為 `127.0.0.1:6379`。
  - Gateway（翻譯 API）位址亦會依環境調整。
- **資料庫檔案**：需將 `GeoLite2-City.mmdb` 放置於輸出目錄（已在 `.csproj` 中設定為 `CopyToOutputDirectory=Always`）。
- **網路設定**：`Startup.cs` 中設定 `ForwardedHeaders`，需允許內部 Docker 網路 IP 範圍（`::ffff:172.17.0.1/104`）通過代理。
- **健康檢查**：不需額外設定，EC Framework 會自動提供健康檢查端點（`/health`）。

## 相關連結
- **GitLab 原始碼**：[https://git.zbdigital.net/biz/geoipservice.git](https://git.zbdigital.net/biz/geoipservice.git)
- **Portainer 服務**：`PRD_Docker_Swarm` / container / `geoipservice`（請洽基礎架構團隊取得連線資訊）
- **API 文件**（Swagger UI）：依部署環境提供，預設路徑 `/swagger`。