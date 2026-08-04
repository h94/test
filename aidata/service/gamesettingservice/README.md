# GameSettingService

## 概述
GameSettingService 是 ZB 遊戲平台的內部核心設定管理服務，負責商務號、帳號、登入會話、場中賽事、各層級玩法設定（系統 / 範本 / 聯盟 / 賽事）、站台配置、聯盟走地規則以及使用者與訂閱者管理。服務以 RESTful API 提供所有操作，並記錄完整操作日誌。

## 主要功能
- **商務號管理**：商務號 CRUD、帳號新增/狀態/密碼維護、登入與登入資訊查詢/移除、場中賽事設定。
- **設定管理**：站台配置、聯盟走地設定；支援球種、聯盟、範本、賽事四層玩法設定值的新增、修改、刪除及讀取；批次操作玩法與告警初始化。
- **系統設定**：公司層級系統設定值查詢、站台停用管理、全部設定層級的玩法批次操作（新增/修改/刪除玩法、增加支援站台、新增告警偏移量）。
- **訂閱者與使用者**：訂閱者團隊註冊/查詢/啟用狀態更新；使用者註冊、登入、登出、密碼重設及權限查驗。
- **日誌系統**：完整記錄使用者操作、商務號操作、各設定層級變更前後內容，提供多維度查詢。
- **系統維運**：自動建表、健康檢查、服務版本查詢、ZBA API 資料修復。

## 技術棧
- **執行環境**：.NET 6
- **框架**：ASP.NET Core (Web API)
- **容器化**：Docker，基於 `mcr.microsoft.com/dotnet/sdk:6.0`
- **部署平台**：Docker Swarm，由 Portainer 管理
- **通訊**：HTTP RESTful JSON，內部使用 Kafka 記錄日誌（引用 `IKafkaLogger`）
- **依賴注入**：廣泛使用 Interface 注入各 Domain Service

## 組態與部署注意
- **容器時區**：已固定為 `Asia/Taipei`。
- **服務端口**：容器內部暴露 `5000`，Swarm 部署時需透過 overlay 網路或 Portainer 配置端口映射。
- **必要環境變數**：
  - 需提供資料庫連線字串（由 `ECCore` 函式庫讀取，具體鍵值需人工確認）。
  - 需提供 Redis 連線字串（用於快取或 Session 管理，鍵值需人工確認）。
  - 需提供 Kafka 相關設定（如 `BootstrapServers`，用於日誌傳輸，鍵值需人工確認）。
  （以上可參考專案 `appsettings.json` 或 Portainer 環境變數區塊進行配置）
- **資料表初始化**：可透過 API `POST /api/v1/system/autocreatetable` 自動建立缺失的資料表結構。
- **版本與健康**：`/api/version` 與 `/api/heart` 提供版本與心跳，可作為負載均衡或監控告警檢查端點。
- **Portainer 管理**：服務對應 PortainerKey `PRD_Docker_Swarm|container|gamesettingservice`，確保在 Portainer 中服務名稱與實際部署一致。

## 相關連結
- GitLab 原始碼倉庫：[https://git.zbdigital.net/Biz/gamesettingservice.git](https://git.zbdigital.net/Biz/gamesettingservice.git)