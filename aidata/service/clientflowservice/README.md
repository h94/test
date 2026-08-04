# ClientFlowService 內部服務目錄

## 概述
ClientFlowService 是負責處理賽事賠率與賽程資料的 .NET Worker Service。主要從 Kafka 訂閱 `processedgamedata` 主題，解析即時賠率並寫入 Redis（DB5），供前端 inplayz 使用，並根據比賽狀態動態設定 TTL（進行中賽事賠率約 20 秒有效，未開始賽事賠率約 3 分鐘有效，以避免前端顯示過時資料）。

同時，服務也從資料庫獲取賽事資料（InPlay、PreGame、Final），結合聯盟/隊伍資訊與預測投注統計，整理後寫入 Redis DB6（站台賽事資料）與 DB7（賽事映射資料），供前端 inplayz 查詢。

此外，服務負責處理使用者預測提交與投注，寫入 Predict keyspace 的 `activities_record`、`betpool_bets` 等表，並讀取預測相關資料（如 `predictbets_*`）以彙整預測數據；必要時可直接操作 PriceCenter keyspace 的 `accounts_*` 等資料表（詳細 DB 操作邊界與限制請參閱內部文件）。

服務部署於 Docker Swarm（PRD）環境，服務名稱：`clientflowservice`。

## 主要功能
- **Kafka 即時賠率處理**：訂閱 `processedgamedata` 主題，解析 ProcessedMatch 訊息，並只處理限定的賠率站台。將有效賠率（過濾 `-1` 值）寫入 Redis DB5，並根據 `Game_Status`（0=進行中, 2=未開始）設定不同的 TTL，確保賠率資訊的即時性。
- **賽事資料彙整與快取**：定期從資料庫獲取 InPlay、PreGame、Final 賽事資訊，整合聯盟/隊伍名稱、預測投注數據及主客交換（swap）資訊後，寫入 Redis DB6 與 DB7。服務會比對新舊資料，僅在賽事列表有變更時才更新 Final 與 PreGame 快取，以減少不必要的寫入。
- **預測投注資料整合與寫入**：從 Predict Cassandra 獲取 `predictbets_*` 預測單，依 `Gid` 與玩法分組後快取，供賽事流程使用。同時提供使用者預測與投注 API，負責寫入 `activities_record`、`betpool_bets` 等表，並管理帳號驗證與部分 `accounts_*` 更新（詳細 DB 操作邊界請參閱內部文件）。
- **自動重啟機制**：每天下午 1 點或偵測到處理速度過慢時會主動拋出例外，觸發容器重新啟動。
- **多環境支援**：支援 BAK、Local、PRD、Test 等環境，透過 `appsettings.{Environment}.json` 切換連線設定。

## 服務邊界
為避免職責重疊，下列事項明確**不屬於** ClientFlowService 的負責範圍：

- 活動週期（`activities_cycles`）的建立與更新：由 Admin Service / 管理後台處理。
- 遊戲派彩（`betpool_games.payout`）與用戶餘額變更：由 Payout Service、Wallet Service 處理。
- 賽程資料（`games_{gameType}`、`leagues_{gtype}`、`teams_{gtype}`）的初始寫入與同步：由 Data Sync Service 負責。
- 帳號註冊與密碼雜湊驗證：由 Registration Service、Authentication Service 負責。
- 操作日誌（`actionlog`）的歸檔與清理：由定時歸檔服務處理。
- `sitegames_{gameType}`、`siteteams_{gameType}`、`siteleagues_{gameType}` 的初始建立及大部分欄位維護：除 `swap` 欄位外，均由站台設定管理後台或同步服務負責。
- `games_{gameType}` 的 `status`、`match_h`、`match_a`、`match_detail`、`resultinfo` 寫入：這些欄位由 GameLiveService 或 PredictService 管理，本服務僅讀取。

以上邊界與跨服務約定，有助於避免寫入衝突與資料不一致。關於本服務對各資料庫表格的具體讀/寫限制，請參閱 [`clientflowservice-detail.md`](./clientflowservice-detail.md)。

## 技術棧
| 類別       | 技術                                   |
|------------|----------------------------------------|
| 語言/框架  | .NET 8 (Worker Service)                |
| 訊息佇列   | Apache Kafka (Confluent.Kafka)         |
| 快取/資料庫| Redis (StackExchange.Redis)、Cassandra、PostgreSQL |
| 依賴注入   | ECFramework.ECService、ECCore          |
| 序列化     | Newtonsoft.Json、System.Text.Json      |
| 工具庫     | AutoMapper、GameDataModels             |
| 容器化     | Docker (基於 `mcr.microsoft.com/dotnet/sdk:8.0`) |

## 組態與部署注意
### 組態說明
- **appsettings.json**：預設環境為 Test，連線至 BAK 的 Redis/Kafka 節點。
- **appsettings.PRD.json**：生產環境設定，Redis 主機均為 `192.168.55.80`，Kafka GroupId 為 `ClientOddsPRD`。
- **重要的設定區段**：
  - `KafkaSetting`：Broker 列表 (`BootstrapServers`)、訂閱主題 (`Subscribe`)、消費者群組 (`GroupId`)。 
  - `RedisSettings`：三個連線 (GameData, SiteGameData, GameMapping) 分別對應 DB5、DB6、DB7。
  - `CassandraSettings`：連線至 pricecenter 與 predict keyspace。
  - `AppSettings`：賽事類型 (`GameTypes`)、主要賠率站台清單 (`GameMainOddSites`)、語言修正站台等。
- **環境變數**：可透過 `DOTNET_ENVIRONMENT` 或 `ASPNETCORE_ENVIRONMENT` 切換環境（例如 `PRD`）。

### 部署注意
- **容器映像**：目前使用 `mcr.microsoft.com/dotnet/sdk:8.0` 作為基底映像。此為 SDK 映像，體積較大，建議在正式環境改用 `mcr.microsoft.com/dotnet/aspnet:8.0` 或自訂 runtime 映像。
- **Docker Swarm**：透過 Portainer 管理，服務名稱為 `clientflowservice`。
- **啟動指令**：`ENTRYPOINT ["dotnet", "ClientFlowService.dll"]`
- **時區**：已設定 `TZ=Asia/Taipei`，並建立時區符號連結。
- **重啟行為**：服務本身內建定時重啟機制（每日 13:00 或偵測到延遲時），應確保容器配置了自動重啟策略（例如 `--restart always`）。
- **資源建議**：此服務高度依賴穩定的 Kafka、Redis 與 Cassandra 連線。網路延遲可能導致賠率更新不及時或賽事資料寫入失敗。建議根據實際負載設定 CPU/Memory 限制，並監控訊息處理的延遲時間。

## 相關連結
- **GitLab 倉庫**：`https://git.zbdigital.net/biz/clientflowservice.git`
- **Portainer 服務**：`PRD_Docker_Swarm` 環境下的 `clientflowservice`
- **相依服務**：Redis (192.168.55.80:6379)、Kafka (192.168.55.85~87)、Cassandra (192.168.55.80)
- **外部依賴 NuGet**：`ECCore`、`ECFramework.ECService`、`GameDataModels`、`AutoMapper` 等（請參考 `.csproj` 檔案）
- **DB 操作邊界文件**：[`clientflowservice-detail.md`](./clientflowservice-detail.md)