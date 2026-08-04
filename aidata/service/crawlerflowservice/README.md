# CrawlerFlowService 內部服務目錄

## 概述
CrawlerFlowService 是基於 .NET 6 的 Worker Service，負責即時訂閱 Kafka 中的爬蟲比賽數據（gamedata），進行資料驗證、格式轉換、快取比對後寫入 Cassandra 資料庫，並將處理結果發送回 Kafka（processedgamedata）。服務運行於 Docker Swarm 叢集，透過 Portainer 管理。

## 主要功能
- **即時數據消費**：從 Kafka Topic `gamedata` 訂閱比賽數據，支援多例（PRD/PRD2/PRD3）分流。
- **資料驗證與轉換**：驗證比賽來源、類型、時間合理性，並轉換為統一格式。
- **快取比對與去重**：使用 ConcurrentDictionary 快取比賽 ID，避免重複處理；定期清理過期快取。亦使用 Redis 進行跨實例狀態暫存。
- **Cassandra 寫入**：將比賽資料寫入 `pricecenter` Keyspace 下的對應表，支援寫入開關（`WriteDB`）。
- **狀態監控與日誌**：透過 Kafka 日誌 Topic `applogs` 輸出運行日誌，包含錯誤與效能資訊。
- **多環境支援**：透過不同 appsettings.{Environment}.json 配置開發、正式、備援環境。

## 技術棧
- **語言/框架**：C# / .NET 6 (Worker Service)
- **訊息佇列**：Apache Kafka (Confluent.Kafka 1.8.2)
- **資料庫**：Cassandra (DataStax CassandraCSharpDriver 3.17.1)
- **快取**：Redis
- **基礎框架**：ECCore、ECFramework.ECService（內部套件）
- **容器平台**：Docker (Swarm) / Portainer
- **版本控制**：GitLab
- **測試**：xUnit + Moq

## 組態與部署注意
1. **環境變數與組態**：透過 `appsettings.{Environment}.json` 管理，`ASPNETCORE_ENVIRONMENT` 控制啟用哪份配置。關鍵組態包含 Kafka 節點、Cassandra 連線、GameTypes/Site 白名單。
2. **內部 NuGet 來源**：建置時需指定內部 NuGet 伺服器 (`http://192.168.9.234:8079/repository/nuget-hosted/`)。
3. **Kafka 消費者群組**：不同環境使用不同的 GroupId（如 `MatchCFXSystemPRD`），避免偏移量衝突。
4. **Cassandra Keyspace**：正式環境使用 `pricecenter`，開發環境使用 `test`；連線點依環境不同。
5. **寫入開關**：`WriteDB` 設為 false 可僅處理不寫庫，適合測試或負載分流。
6. **部署方式**：以 Docker 容器搭建，透過 Portainer 管理；Dockerfile 基於 mcr.microsoft.com/dotnet/sdk:6.0，時區設定為 Asia/Taipei。
7. **多實例支援**：PRD/PRD2/PRD3 對應不同 Kafka Consumer 與 Producer Topic，可水平擴展。
8. **accounts 表結構差異**：部分站點帳戶表（如 HGA、KKK、KU、NK、TG、TG999）無 `username` 欄位，存取前必須檢查 schema，避免空指針錯誤。

## 資料庫操作邊界（pricecenter / Redis）

### pricecenter（Cassandra）
- **accounts_\* 系列**：本服務僅可 INSERT 新帳戶（密碼須雜湊後寫入），**不可對既有帳戶執行任何 UPDATE**（包含 enabled、closetime、handler、password、phone 等欄位）。讀取時必須過濾 `enabled = 1` 且 `closetime IS NULL`。
- **actionlog**：僅允許 INSERT 操作日誌，禁止 UPDATE 或 DELETE；`date`、`addtime` 由系統自動設定。
- **crawler_log**：`id` 僅在任務開始前 INSERT；`machine`、`site`、`starttime` 初始化後不可修改；`processcount`、`exectime` 僅在任務完成時一次性更新，不可增量累加。
- **讀取規範**：帳戶驗證（`IValidate.ValidateSource`）須以 `account` 為主鍵且 `enabled=1`；`sitegames_*` 查詢須包含 `sitegid` 與 `enabled=1`；日誌查詢必須帶分區鍵（`date`）或範圍條件，禁止全表掃描。
- **敏感欄位**：`password` 不得對外洩漏（API 或 Kafka 消息）；`phone` 非必要不回傳；`actionlog.detail` 若含敏感資訊須過濾。

### Redis 快取
| Key 模式 | 用途 | TTL |
|----------|------|-----|
| `CrawlerFlow:{GameType}:{SiteLid}:{SiteGid}` | 比分比對快取 | 7200 秒 |
| `MainSpread:{SiteLid}:{SiteGid}` | 主盤值暫存 | 3600 秒 |
| `KafkaCache:{GameType}:{Site}:{Sitegid}` | Kafka 發送前暫存 | 1800 秒 |

### 本服務不負責
- 帳戶註冊、密碼變更、enabled/handler 等帳戶屬性維護 → `accounts-manage-service`
- 賽事資料表（`sitegames_*`）DDL 建立 → db-admin / infra
- 最終賠率計算與封裝 → `odds-compute-service`

> ⚠️ 完整讀寫限制與常見錯誤請參閱內部 DB 操作邊界文件（生成日期 2025-04-12），本節僅列舉重點。

## 相關連結
- **GitLab 存放庫**：[https://git.zbdigital.net/Biz/crawlerflowservice.git](https://git.zbdigital.net/Biz/crawlerflowservice.git)
- **Portainer Key**：`SRV84|container|crawlerflowservice`（需人工確認完整標籤如 `:latest`）