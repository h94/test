# TokenService — 內部服務目錄

## 概述

TokenService 為一內部 Web API 服務，提供 Token 核發、驗證與管理功能，支援驗證碼（AuthToken）與一般 Token 兩種機制。服務採用 .NET 8 開發，部署於 Docker Swarm 叢集（PRD 環境），並整合 MySQL、Redis、Kafka 等基礎設施。

## 主要功能

- **驗證碼（AuthToken）管理**
  - 產生六位數驗證碼並快取至 Redis
  - 驗證碼正確性驗證，驗證成功後清除快取
- **Token 生成**
  - 依呼叫端公司代碼產生雜湊 Token（預設有效期限可設定）
  - 支援透過原始金鑰（originKey）產生 Token
- **Token 驗證**
  - 依 HashKey 與公司代碼檢查 Token 有效性並更新使用紀錄
  - 支援原始金鑰比對與校驗
- **操作日誌查詢**
  - 查詢指定日期範圍內 Token 生成與驗證的歷史紀錄（依公司代碼篩選）
- **日誌記錄**
  - 所有 Token 操作（生成 / 驗證）均透過 Kafka 寫入集中式紀錄

## 技術棧

- **語言 / 框架**：C#、.NET 8、ASP.NET Core
- **相依套件**：ECCore 3.0.1、ECFramework.ECService 3.0.0
- **資料儲存**：MySQL (Token、Log)、Redis (AuthToken 快取)
- **訊息佇列**：Kafka (日誌傳送)
- **容器化**：Docker，部署於 Swarm 叢集
- **CI / CD**：GitLab (原始碼管理)

## 組態與部署注意

- **環境設定檔**：`appsettings.Local.json`（開發）、`appsettings.PRD.json`（正式）
- **必要外部資源**：
  - MySQL 資料庫（需預先建立 `Tokens` 資料庫及相關資料表）
  - Redis 實體（用於 AuthToken 暫存）
  - Kafka Broker（用於日誌推送）
- **連接字串**：請依據實際部署環境調整 `AppSettings.MySQLSettings` 與 `AppSettings.RedisSettings` 中的 Server、Port、User、Password
- **Docker 映像**：Dockerfile 以 `mcr.microsoft.com/dotnet/sdk:8.0` 為基底，暴露埠 5000
- **排程與環境變數**：可透過 Docker Swarm secrets 或環境變數覆寫設定值（尤其密碼）
- **注意**：Token 有效期限限制為 0～432,000 秒（5 天），超過將回傳錯誤

## 相關連結

- GitLab 儲存庫：<https://git.zbdigital.net/biz/tokenservice.git>