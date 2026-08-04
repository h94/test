# 概述

livechatservice 為一套提供即時線上客服功能的核心服務，包含 RESTful API 與管理後台，支援多公司（租戶）隔離。部署於 Docker Swarm 環境（PRD_Docker_Swarm），對外透過埠 5000 提供服務。

# 主要功能

*   **即時通訊**  
    採用 SignalR 實現聊天室訊息傳遞、圖片上傳、在線用戶列表更新與逾時對話清理。
*   **客服管理後台**  
    HomeController 提供歡迎訊息、問題類型、快捷訊息（QuickMessage）、對話記錄（MessageLog）、滿意度回饋（Feedback）及第三方帳號（如 Telegram）的管理介面。
*   **RESTful API**  
    以 `/api` 為路由前置，提供完整的問題類型 CRUD、對話紀錄分頁查詢、Token 產製與驗證、第三方平台帳號維護等端點。
*   **多管道整合**  
    內建 Telegram 等第三方服務介接，可管理 API Token、Bot Token 與啟用狀態。
*   **健康檢查**  
    提供 `/api/heart` 與 `/api/version` 端點，供監控與版本追蹤。

# 技術棧

*   **執行環境**：.NET Core 3.1（ASP.NET Core MVC + Web API）
*   **即時通訊**：SignalR（後端推送、前端連線）
*   **資料儲存**：關聯式資料庫（透過 ECCore 存取）與 Redis 快取
*   **日誌**：Kafka（經由 IKafkaLogger 介面輸出）
*   **組態管理**：IECConfig 自訂組態服務，集中管理 SignalR、第三方連線等設定
*   **容器**：Docker（基於 `mcr.microsoft.com/dotnet/core/aspnet:3.1-buster-slim`），開放埠 5000

# 組態與部署注意

*   **時區**：容器啟動時將時區固定為 `Asia/Taipei`（TZ 環境變數）。
*   **必要組態**  
    IECConfig 中的 AppSettings 需正確設定 `SignalRSetting` 群組，包含 SignalR 連線 URL、上傳 URL、聊天紀錄查詢 URL 等。
*   **租戶識別**  
    多數 API 及後台頁面依賴 `X-Auth` header 或 `X-COMPANY` header 區分公司；後台亦可透過 Query `?XAuth=...` 傳遞。
*   **相依服務**  
    部署前請確保 Redis、Kafka 及目標資料庫可連線，並於組態中填入對應連線字串。
*   **容器化部署**  
    服務於 Docker Swarm 中命名為 `livechatservice`，監聽容器 5000 埠。

# 相關連結

*   GitLab 原始碼：<https://git.zbdigital.net/Biz/livechatservice.git>