# WebpService - 圖片轉 WebP 背景服務

## 概述

WebpService 為內部圖片轉換服務，基於 .NET 6 Worker 實作，定期掃描指定目錄下的圖片檔案（PNG、JPG、JPEG、BMP），並自動轉換為 WebP 格式，以提升網頁載入效能。服務運作於容器環境，具備錯誤重試與強制更新機制。

## 主要功能

- **定期轉換**：每 30 分鐘掃描 `/app/wwwroot/downloads/` 下的 `logo`、`sport/advertising`、`sport/jersey` 資料夾（含子資料夾），將非 WebP 圖片轉換為 `.webp`
- **強制更新**：對早於 2024-04-26 15:00 的舊 WebP 檔案進行強制重新轉換
- **會員照片修復**：啟動時自動檢查 `sport/img/upload` 下單一 JPEG 檔案，若轉換失敗則補回預設 Basic.webp
- **批次處理**：每轉換 1000 張暫停 5 秒，避免資源耗盡
- **心跳日誌**：每分鐘輸出 heartbeat 至 Kafka

## 技術棧

| 項目 | 技術 |
|------|------|
| 執行環境 | .NET 6 (Worker Service) |
| 圖片處理 | Magick.NET-Q16-AnyCPU (ImageMagick) |
| 日誌系統 | KafkaLogger (Kafka) |
| 組態儲存 | Cassandra (pricecenter / predict / member) |
| 依賴注入 | ECFramework.ECService + ECCore |
| 容器化 | Docker (mcr.microsoft.com/dotnet/sdk:6.0) |

## 組態與部署注意

- **映像建置**：使用自訂 NuGet 來源 `http://192.168.9.234:8079/repository/nuget-hosted/` 與 `nuget.org-proxy/`
- **必要掛載**：容器內 `/app/wwwroot/downloads/` 需掛載主機圖片資料夾，否則服務無法執行
- **時區設定**：Dockerfile 已設定 `TZ=Asia/Taipei`
- **Kafka 連線**：透過 `appsettings.json` 設定 `BootstrapServers: 49.213.1.158:29096`、Topic: `applogs`
- **Cassandra 連線**：設定於三個 Keyspace（pricecenter、predict、member），主機 `192.168.55.80`
- **啟動方式**：容器入口點 `dotnet WebpService.dll`，需設定環境變數 `DOTNET_ENVIRONMENT`（Development/Production）

## 相關連結

- GitLab 原始碼：[https://git.zbdigital.net/Architecture/webpservice.git](https://git.zbdigital.net/Architecture/webpservice.git)
- Portainer 容器 ID：`2a419f9821cd`（服務標籤 `webpservice:latest`）