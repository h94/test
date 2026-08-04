# PriceClientSystem 服務目錄

## 概述

PriceClientSystem 是一個基於 .NET 8 的 WebAPI 服務，主要負責即時比分與賠率推送。透過訂閱 Kafka 的 `processedgamedata` 主題，取得各平台（如 bet365、1xbet、ZBA 等）的賽事即時更新資料，並經由 SignalR Hub 推送給前端（InplayZ）。同時整合 Cassandra 作為持久化儲存以讀取商品資訊，並且支援多站點、多球種的比分修正與玩法過濾功能。

## 主要功能

- **即時比分推送**：從 Kafka 接收 ProcessedGameData，解析後透過 SignalR `/hub` 端點廣播給訂閱用戶。
- **比分與賠率修正**：自動修正單局單節比分錯誤，並過濾非必要玩法（僅保留讓分/大小）。
- **連線管理**：紀錄每個 Hub 連線的資訊（ConnectId、GameType、IP、Token 等），支援查詢即時連線狀態。
- **商品查詢**：直接從 Cassandra 的 `product.products_store` 讀取商品列表，以及查詢使用者的兌換記錄。
- **自動重啟**：每日 UTC 13:00 自動重啟服務，確保資料新鮮度（程式內建機制）。
- **多語系 / 賠率映射**：支援將外部平台代碼（PlayMode）轉換成內部系統代碼（如 HA、OU、RBHA、RBOU）。

## 技術棧

| 類別       | 技術                                            |
| ---------- | ----------------------------------------------- |
| 語言       | C# (.NET 8)                                     |
| 框架       | ASP.NET Core 8 (WebHost)                       |
| 即時通訊   | SignalR Core (MessagePack 協議)                 |
| 訊息佇列   | Apache Kafka (Confluent .NET Client)            |
| 持久化儲存 | Cassandra (用於查詢商品與兌換記錄)             |
| 快取       | Redis (用於賽事資料快取，TTL 30 秒)            |
| 容器       | Docker (基底鏡像 `mcr.microsoft.com/dotnet/sdk:8.0`) |
| 組態管理   | appsettings.{Environment}.json（依環境切換）     |

> **需人工確認**：根據 `priceclientsystem-detail.md`，此服務直接操作 Cassandra 的 `product` keyspace 來讀取商品列表與兌換記錄，並可能操作 `pricecenter` keyspace 進行帳號驗證。`priceclientsystem-detail.md` 中提到「目前未使用 Redis 快取」，但 `real-time-score-push.md` 場景中描述了使用 Redis 快取 30 秒的賽事資料。此矛盾需向開發團隊確認；此處技術棧已依場景文件新增 Redis 說明。

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 帳戶密碼驗證（比對雜湊） | `priceclientsystem` 本身（內部邏輯） | 但密碼管理（重設、安全規範）由 `account` 服務負責，priceclient 僅驗證登入時比對。 |
| 帳戶啟用/停用排程 | `account` 或 `scheduler` | 自動關閉逾時帳戶、批量停用作業不屬於 priceclient。 |
| 第三方客戶 `sitegames_{gameType}` 表操作 | 遊戲服務 (`game-service`) | priceclient 僅讀取 `sitegames_{gameType}` 中的即時賽事資料，寫入與結構管理由遊戲系統負責。 |
| 產品圖片儲存與 CDN 管理 | `storage` 或 `media` 服務 | priceclient 僅存取 `image_path` 欄位中的路徑字串，不處理圖片上傳、壓縮、CDN 分發。 |
| 多語言翻譯內容維護 | `i18n` 或 `cms` 服務 | `pnames`、`description`、`names` 等 map 內容由外部系統管理，priceclient 只讀取。 |
| 商品寫入與庫存管理 | `productservice` 或 `currencyservice` | priceclient 僅讀取商品和兌換記錄，不負責庫存扣減或狀態更新。 |

## API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/version` | 取得系統版本資訊 |
| GET | `/api/heart` | 心跳檢測端點 |
| GET | `/api/v1/system/hubinfo` | 查詢 SignalR Hub 連線狀態 |
| WebSocket | `/hub` | SignalR Hub，用於即時比分推送 |

> **需人工確認**：商品列表查詢 (`/api/v1/product/store`) 和兌換記錄查詢 (`/api/v1/store/redeemlogs`) 端點未在 OpenAPI 中列出，需從原始碼確認其實際路徑與是否真正存在。

## 組態與部署注意

### 必要環境變數與設定

- **Kafka**：`AppSettings:HubSettings:KafkaBootstrapServers`、`KafkaTopic`（預設 `processedgamedata`）、`KafkaGroupId`（依環境不同，如 `PC_`、`UI_`）。
- **Cassandra**：`AppSettings:CassandraSettings`，至少指定一台 Server 與對應 Keyspace（如 `pricecenter`、`product`）。
- **Restful Gateway**：`AppSettings:RestfulSettings:Gateway`，用於取得 SiteData 的 REST API 端點。
- **Hub 設定**：`AppSettings:HubSettings:GameTypes` 定義服務支援的球種；`SourceSites` 列出所有來源站點與對應球種（僅 PRD 環境省略了大部分 SourceSites，但保留 CompanyToken）。
- **Token 驗證**：`AppSettings:HubSettings:CompanyToken` 定義每個客戶端公司的驗證 Token（ZB、BB、PC）。部署時需確認 Token 與前端一致。

### 部署注意事項

1. **容器化**：Dockerfile 使用 `mcr.microsoft.com/dotnet/sdk:8.0` 基底，複製 `PriceClientSystem/bin/Debug/net8.0/` 輸出。建議修改為 Release 模式建置。
2. **時間與時區**：容器內已設定 `TZ=Asia/Taipei`，並同步時區檔案。
3. **暴露埠號**：Dockerfile 中 `EXPOSE 5000`，但服務實際監聽埠由 Kestrel 組態決定（通常為 80/5000）。若使用 Docker Swarm 請確認 service 的 port mapping。
4. **環境設定檔**：`appsettings.PRD.json` 已提供生產組態。部署時應將該檔案命名為 `appsettings.Production.json` 或透過環境變數 `ASPNETCORE_ENVIRONMENT=PRD` 載入。
5. **SignalR 訊息大小限制**：程式碼中設定 `MaximumReceiveMessageSize = 3276800`（約 3.1 MB），若前端需要更大量資料可調整。
6. **自動重啟機制**：程式內建每日 13:00（根據伺服器時間）自動拋出 `Exception` 觸發服務重啟。若使用容器編排（如 Docker Swarm 或 K8s），建議移除該邏輯，改由外部排程進行滾動更新。需人工確認是否仍以此機制運作。

## 相關連結

- **GitLab 儲存庫**：[https://git.zbdigital.net/biz/priceclientsystem.git](https://git.zbdigital.net/biz/priceclientsystem.git)
- **容器標籤**：需人工確認（無明確來源）
- **服務類型**：`webapi`