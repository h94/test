# TokenService

## 概述

TokenService 是一個基於 .NET 8 的輕量級微服務，專責提供各類一次性驗證碼（AuthToken）、通用 Hash Token 的產生、驗證與授權檢查，以及操作紀錄的查詢。服務已容器化並部署於 Docker Swarm（PRD 環境），主要作為內部系統身分驗證與短期授權的核心元件。

## 主要功能

- **一次性身分驗證碼**
  - 依 `authKey` 產生六位數驗證碼 (`POST /api/v1/token/auth/{authKey}`)
  - 驗證碼驗證，成功後自動清除快取 (`POST /api/v1/token/auth/{authKey}/verify`)
- **通用 Hash Token**
  - 產生有時效的 Token 並寫入資料庫 (`GET /api/v1/token/get?expirationtime=60`)
  - 檢查 Token 有效性 (`GET /api/v1/token/check?token=...`)
- **Licence 授權 Token**
  - 依原始金鑰 (`originKey`) 產生固定 Token (`GET /api/v1/licence?originKey=...`)
  - 驗證 Licence Token 是否有效 (`GET /api/v1/licence/check`)
- **操作紀錄查詢**
  - 依日期區間取得 Token 使用紀錄 (`GET /api/v1/log/{date}?enddate=...`)
- **服務監控端點**
  - 心跳檢查 (`GET /api/heart`)
  - 版本資訊 (`GET /api/version`)，回傳版號、環境與組建時間

## 技術棧

- **執行環境**: .NET 8, ASP.NET Core Web API
- **容器化**: Docker, 基於 `mcr.microsoft.com/dotnet/sdk:8.0`
- **依賴注入**: `ITokenService`, `IECConfig`, `IKafkaLogger`, `IHttpContextAccessor`
- **資料持久化**: 後端資料庫（儲存 Hash Token、Log 等）
- **訊息記錄**: Kafka（透過 `IKafkaLogger`）
- **時區**: Asia/Taipei

## 組態與部署注意

- **服務 Port**: 容器內部使用 `5000`，Swarm 層可透過 overlay 網路或 Portainer 對外暴露。
- **環境變數**（建議使用 Docker secrets 或 config 注入）：
  - 資料庫連線字串
  - Kafka 相關設定（Broker 位址、Topic）
  - `Version` 與 `Environment` 組態（用於版本端點）
- **Dockerfile 要點**：採用多階段構建，最終映像直接複製 `bin/Debug/net8.0/` 產物（正式環境應改用 `Release` 並最佳化映像大小）。
- **Swarm 部署**：服務定義中應設定 restart policy，並掛載必要的 secrets。
- **健康檢查**：可利用 `GET /api/heart` 進行容器健康狀態監控。

## 相關連結

- **GitLab 儲存庫**: [https://git.zbdigital.net/Biz/tokenservice.git](https://git.zbdigital.net/Biz/tokenservice.git)
- **Portainer 服務**: `PRD_Docker_Swarm` → 搜尋容器 `tokenservice`