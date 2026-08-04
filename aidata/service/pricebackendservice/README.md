# PriceBackendService

## 概述
PriceBackendService 為運動賽事後台管理核心服務，提供統一的 REST API 入口，涵蓋活動、廣告、社群、會員、預測、金流、新聞、商品商城、交易設定等近二十個業務領域。服務以 .NET 8.0 建置，部署於 Docker Swarm 生產環境，支撐前後台系統對資料的查詢與操作。

## 主要功能
- **活動管理** - 站台活動商品的新增、查詢、更新、刪除，以及會員兌換紀錄管理（儲存於 MongoDB）。
- **廣告與公告** - 廣告版位上傳與維護，公告新增、編輯、刪除（儲存於 MongoDB）。
- **社群討論** - 球種聯盟標籤創建、文章查詢與置頂、使用者及球種報表統計（文章、標籤等資料儲存於 MongoDB）。
- **反饋系統** - 運動站台反饋主題設定、會員/訪客反饋訊息查詢與回覆、商業訊息處理（反饋訊息儲存於 MongoDB）。
- **直播頻道** - 頻道啟用/停用、頻道資訊查詢，以及社群群組管理。
- **通知管理** - 通知主題、訊息、站內信的 CRUD，以及 App 裝置版本設定（儲存於 MongoDB）。
- **會員管理** - 賽事會員驗證、禁言、錢包交易紀錄、Email 網域禁用、至尊球王週期結算等完整會員生命周期管理（呼叫 MemberService API）。
- **新聞文章** - 運動文章設定、AI 熱門討論賽事寫入 MeiliSearch，支援 AI 新聞上傳圖片與修改。
- **金流支付** - 付費方式、訂閱方案、交易紀錄維護，每月報表與推薦分潤報表產出（金流資料透過 PaymentService 存取）。
- **預測與彩池** - 球種預測設定、莊家殺手週期與條件管理、預測合併、彩池遊戲與機器人下注、派彩結算（與 PredictService 互動）。
- **賽事中心 (PriceCenter)** - 聯賽名稱對照、日期賽事查詢、比分狀態更新、熱門場中賽事設定（透過 PriceCenter 服務存取賽事資料）。
- **商品商城** - 商品上架、庫存紀錄、兌換紀錄查詢與出貨狀態更新（儲存於 MongoDB）。
- **賽事設定** - 訂閱者、使用者、系統設定值的全域管理，支援 playmode 新增/編輯/刪除及站台開通（互動對象為 GameSettingService）。
- **交易所設定** - 球種聯盟設定、股票上限規則、分數防禦規則的新增、查詢、更新及刪除（經由 TradeGameService API 進行設定管理）。
- **交易報表** - 依會員或依賽事彙整的 tradegame 交易報表，以及單場賽事玩法交易紀錄、結算狀態查詢（經由 TradeGameService API 取得交易記錄與持倉資訊）。
- **系統工具** - 圖片上傳、服務心跳、版本查詢、球種清單（透過 `IAppSettingDataProvider` 取得支援球種）。

## 技術棧
- **執行環境**：.NET 8.0
- **容器化**：Docker (mcr.microsoft.com/dotnet/sdk:8.0)
- **排編部署**：Docker Swarm (PRD_Docker_Swarm)
- **資料儲存**：
  - **MongoDB**：主要業務資料（廣告、公告、通知、商品、社群文章、反饋訊息等）。
  - **Cassandra**：唯讀存取核心服務資料（PriceCenter 賽事、TradeGame 交易持倉），寫入由對應微服務負責。
  - **Redis**：快取與排行榜（如熱門場中賽事等）。
- **訊息佇列**：Kafka（用於結構化日誌與事件傳遞；具體 broker 設定與主題配置需人工確認）
- **搜尋引擎**：MeiliSearch（AI 文章索引）
- **內部依賴**：多個微服務（PredictService、PriceCenter、MemberService、TradeGameService、GameSettingService 等），透過 HTTP API 協作，提供賽事、會員、金流、交易等核心能力的聚合與管理。

> **注意**：根據資料庫權限分析，本服務對 `pricecenter` 與 `tradegame` 等核心資料庫僅有**唯讀 (reader)** 權限。所有資料的寫入、修改均由對應的微服務（如 PriceCenter、TradeGameService）負責，本服務不直接修改這些資料庫中的任何記錄。

## 組態與部署注意
- 容器時區已固定為 `Asia/Taipei`，透過環境變數 `TZ` 設定。
- 服務監聽端口 **5000**。
- 所有外部資源（MongoDB 連線字串、Kafka brokers、Redis 位址、MeiliSearch URL 等）均需透過環境變數或 `appsettings.json` 注入。
- 建議搭配 xxl-job 進行定時任務觸發（如報表生成、派彩、至尊球王結算、殺手週期派彩等）。此建議**需人工確認**，本次 Context 中未包含 xxl-job 的相關設定。
- 部署時應確保依賴的內部服務（PriceCenter、PredictService 等）在同一個 Swarm 網路中可達。
- 檔案上傳功能需設定對應的儲存路徑權限（如圖片上傳）。
- 本服務不直接以寫入權限存取 Cassandra，所有賽事、交易、會員等核心資料均由依賴的微服務管理，透過 API 取得所需數據。

## 相關連結
- **GitLab 原始碼**：https://git.zbdigital.net/Biz/pricebackendservice.git
- **Portainer 服務**：`PRD_Docker_Swarm` / `pricebackendservice`