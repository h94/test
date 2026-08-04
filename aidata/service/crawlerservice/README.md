# CrawlerService 內部服務目錄

## 概述
CrawlerService 是負責管理爬蟲帳號憑證、啟用狀態與相關配置的後臺服務。它主要維護 `pricecenter` 中的 `accounts_*` 系列資料表（如 `accounts_AU8`、`accounts_Fortuna888`、`accounts_Panda` 等），確保爬蟲帳號的合法性與可用性。本服務**不直接處理賠率資料的消費、解析、持久化，亦不負責實際爬蟲任務的排程與執行**（詳見服務邊界）。  
需人工確認：服務是否仍從 Kafka 消費帳號操作訊息，若否，相關配置及相依可移除。

## 主要功能
- **爬蟲帳號生命週期管理**：提供帳號建立、密碼雜湊保存、啟用/停用、關閉（closetime）等完整狀態控制。所有密碼必須經服務端雜湊後寫入，嚴禁明文儲存。
- **帳號資料讀取與驗證**：依 `account` 主鍵精準查詢，強制過濾 `enabled = 1` 且 `closetime` 為空（NULL 或空字串）之有效帳號；查詢時不回傳敏感欄位（`password`、`phone`、`handler`）。
- **處理器（handler）配置**：維護 `map<text, text>` 型態的內部策略配置，僅供爬蟲啟動時內部讀取，不對外暴露。
- **Cassandra 批次寫入**：使用背景執行緒批次更新 `accounts_*` 資料，並定期監控寫入延遲，超時觸發告警。
- **多環境支援**：透過 `appsettings.*.json` 區分 `PRD`、`PRD2`、`Local` 等環境，各環境可擁有獨立的 Cassandra Keyspace 與 Kafka 群組設定（如有）。
- **本服務未使用 Redis**：所有快取與狀態管理由其他服務負責，本服務不直接依賴 Redis。

## 技術棧
- **語言與框架**：.NET 6、C#、Worker Service
- **訊息佇列**：Apache Kafka（用戶端函式庫 `Confluent.Kafka` 1.8.2） —— 需人工確認目前是否仍使用 Kafka
- **資料庫**：Apache Cassandra（驅動 `CassandraCSharpDriver` 3.17.1），主要操作 `pricecenter` keyspace 下的 `accounts_*` 表
- **基礎設施**：Docker、Docker Swarm、Portainer
- **測試**：xUnit + Moq 單元測試
- **內部套件**：`ECCore`、`ECFramework.ECService`

## 服務邊界
| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 爬蟲排程觸發與執行 | scheduler-service | CrawlerService 僅管理帳號憑證與啟用狀態，不負責實際爬蟲任務排程及執行。 |
| 爬蟲結果持久化（賠率資料） | price-result-service | 爬蟲取得的價格資料由獨立服務處理，CrawlerService 不負責寫入相關價格資料表。 |
| 爬蟲執行日誌記錄（`actionlog`） | logservice | 爬蟲執行過程中的任務日誌主要由 logservice 寫入；CrawlerService 雖會寫入 `actionlog`，但僅限於帳號管理操作（如啟用/停用），**不負責**寫入爬蟲任務執行記錄。 |
| 快取機制 | 其他服務 | 本服務未直接使用 Redis 進行快取。 |

## 資料庫操作要點（pricecenter.accounts_*）
- **寫入限制**  
  - `account`：主鍵，建立後不可更新。  
  - `password`：僅內部註冊/更新 API 可寫入，必須經雜湊處理。  
  - `enabled`：僅專用啟用/停用 API 可修改。  
  - `closetime`：僅排程終止任務寫入，不可手動修改。  
  - `handler`：僅管理端或策略更新 API 可寫入，其內容可能包含 session cookies/tokens，須確保最小權限。  
  - `phone`：僅管理 API 可修改，需記錄操作日誌。  
  - `username`：管理端可透過專用 API 修改（僅限有該欄位的表）。  

- **讀取規則**  
  - 有效帳號查詢必須包含 `enabled = 1` 且 `closetime IS NULL OR closetime = ''`。  
  - `handler` 僅內部讀取，不回傳至前端。  
  - 任何對外 API 回應**禁止包含** `password`、`phone`、`handler`。

## 常見錯誤
- ❌ 在 API 回應中回傳 `password`、`phone` 或 `handler` 欄位 → ✅ 應過濾後只回傳非敏感欄位（`account`、`username`、`enabled`、`closetime` 等）。
- ❌ 允許前端直接傳遞 `enabled` 值更新狀態（例如 PUT 整份 Account 資料） → ✅ 應透過專用的 enable/disable API，確保業務規則一致性。
- ❌ 未對 `password` 進行雜湊即寫入 Cassandra → ✅ 寫入前必須使用服務端雜湊函數處理，避免明文儲存。
- ❌ 直接 UPDATE `account` 欄位以變更帳號標識 → ✅ 帳號標識不可變更；若需修改，必須刪除原帳號並透過註冊 API 重新建立。

## 組態與部署注意
1. **連線設定**：需依環境調整 `appsettings.{ENV}.json` 中的 `CassandraSetting`（ContactPoints、Keyspace）與 `KafkaSetting`（BootstrapServers，如有使用 Kafka）。  
2. **NuGet 來源**：Dockerfile 中指定了內部 NuGet 來源 `http://192.168.9.234:8079/repository/nuget-hosted/` 及 Proxy，建置時需確保內部網路連通。  
3. **容器時區**：Dockerfile 已設定 `TZ=Asia/Taipei`，確保時間戳正確。  
4. **多環境部署**：各環境建議部署獨立副本，若使用 Kafka 則需配置獨立的 Consumer Group（如 `PRD` 使用 `MatchXSystemPRD`，`PRD2` 使用 `MatchXSystemPRD2`）。  
5. **資源監控**：服務內建監控機制，定期檢查資料庫寫入延遲與執行緒池狀態，超時將記錄 Critical 日誌。  
6. **重要開關**（需人工確認目前是否仍有效）：  
   - `WriteDB`：控制是否實際寫入 Cassandra。  
   - `SendProcessGameData`：控制是否將處理後的資料重新發送回 Kafka。  
   - `NoDBDay` / `NoDBHours`：可設定停寫時間（主要用於開發/測試環境）。

## 相關連結
- **GitLab 儲存庫**：[https://git.zbdigital.net/biz/crawlerservice.git](https://git.zbdigital.net/biz/crawlerservice.git)
- **Portainer 對應**：`PRD_Docker_Swarm` 叢集，容器名稱 `crawlerservice:latest`（ID: `22150754e3c1`）