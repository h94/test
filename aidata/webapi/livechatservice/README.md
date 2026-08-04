# LiveChatService 內部服務目錄

## 概述

`LiveChatService` 為即時客服聊天核心 API 服務，部署於 **PRD Docker Swarm** 叢集。提供客服人員與使用者之間的即時訊息傳遞、線上狀態管理、問題類型設定及圖片上傳等功能。本服務採用 .NET Core 3.1 建置，以 Web API 形式運作，並整合多項中介軟體以支援高併發與分散式場景。

## 主要功能

- **即時訊息傳遞**：透過 Redis 儲存聊天內容，支援訊息的寫入、讀取與最新訊息快取。
- **線上用戶管理**：記錄每位使用者所屬的房間、連線 ID、服務類型，並提供線上用戶列表刷新。
- **問題類型（Issue Type）管理**：支援新增、修改、刪除問題類型，資料同步寫入 MySQL 與 Redis。
- **圖片上傳**：接受上傳圖片檔案，存放於 `wwwroot/downloads/{日期}/livechat` 目錄，並驗證副檔名（僅允許 JPG、PNG、GIF、BMP）。
- **Token 服務**：提供建立與驗證 Token 的功能，用於第三方服務整合。
- **SignalR 整合**：透過 Hub 實現即時推送，並透過設定檔管理 SignalR 相關 URL 與逾時設定。
- **多國語系與地區資訊**：整合 GeoIP 與翻譯 Provider，提供 IP 定位與內容翻譯能力。
- **Kafka 日誌**：使用 IKafkaLogger 記錄服務運作日誌。

## 技術棧

| 類別       | 技術                                       |
|------------|--------------------------------------------|
| 語言/框架  | .NET Core 3.1 (C#)                         |
| 容器化     | Docker (aspnet:3.1-buster-slim)             |
| 排程部署   | Docker Swarm (透過 Portainer 管理)          |
| 資料庫     | MySQL (MySQL Provider)、Redis (Redis Provider) |
| 訊息佇列   | Kafka (KafkaLogger)                         |
| 即時通訊   | SignalR                                    |
| 外部服務   | GeoIP Provider、Translate Provider、Gateway Provider |
| 其他函式庫 | ECCore、ECFramework.ECService、BouncyCastle、Cassandra 驅動 (部分功能) |

## 組態與部署注意

- **Portainer Stack 名稱**：`livechatservice_LiveChatService`，部署於 Swarm 叢集。
- **對外埠號**：容器內暴露 **5000** 埠，對應主機埠須於 Stack 定義中設定。
- **時區設定**：Dockerfile 已設定 `TZ=Asia/Taipei`，確保時間日誌正確。
- **機敏資訊**：`appsettings.json` 應包含 MySQL 連線字串、Redis 連線、Kafka Broker 清單、SignalR 各端點 URL 等設定，請勿寫入版本控制。
- **上傳檔案目錄**：圖片上傳路徑為 `wwwroot/downloads/`，需確保容器內該目錄可寫入；若需持久化，建議掛載外部 Volume。
- **相依服務**：本服務依賴 MySQL、Redis、Kafka、GeoIP 服務及 Telegram Helper（用於異常通知），部署時請確認這些服務可達。

## 相關連結

- **GitLab 原始碼**：<https://git.zbdigital.net/biz/livechatservice.git>
- **Portainer Stack**：`livechatservice_LiveChatService` (Swarm)
- **API 文件**：目前無公開 Swagger，可參考 `LiveChatService.DomainService/LiveChatService.cs` 中的公開方法簽章。
- **內部 Wiki**（若存在）：請參閱團隊知識庫中「LiveChatService 維運手冊」。