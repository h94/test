# FlowControlService — 內部服務目錄

## 概述

FlowControlService 為基於 .NET 8 的 Background Worker 服務，部署於 Docker Swarm 叢集（PRD 環境）。主要負責處理經由 Kafka 傳遞的比賽與賠率訊息，進行資料轉換、快取更新、歷史紀錄儲存及資料修復，確保站點遊戲資料即時且一致。  
本服務直接寫入 `pricecenter` 與 `predict` keyspace（Cassandra），並操作 Redis 快取層；不負責帳戶建立／修改、賠率計算，詳見下方責任邊界。

### 服務責任邊界

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 帳戶建立／修改 | `accountservice` | `pricecenter.accounts_*` 的啟用／關閉由帳務服務統籌；本服務僅讀取驗證。 |
| 賠率計算 | `oddsservice` | 賠率資料僅供本服務讀取用於流速控制；賠率生成與變更不屬本服務職責。 |
| 活動週期與預測結算 | `predictresultservice` 等 | `predict` keyspace 中的活動、排行榜等僅由對應結算服務寫入，本服務僅在派彩流程中更新特定欄位（`betpool_games.status/winresult/payout`、`predictbets_*.winloss/profitpoint/status`）。 |

⚠️ 更多 DB 操作邊界與權限細節請參閱 `db/pricecenter-detail.md` 及 `db/predict-detail.md`。

## 主要功能

- **Kafka 即時消費與處理**  
  透過消費者群組訂閱 `processedgamedata`、`processedgamedata2`、`processedgamedata3` 主題，接收 ProcessedMatch 訊息（包含比分、賠率、狀態變更等），並過濾延遲超過 10 秒的訊息。

- **站點遊戲 Redis 快取更新**  
  將處理後的比賽基本資訊、比分、賠率（含一般與滾球）寫入 Redis，支援批次寫入與日期索引，同時處理 Swap 賽事（主客互換）的情況。

- **賠率歷史紀錄（OddsHis）**  
  針對主要玩法（HA、OU、RBHA、RBOU）與其他次要玩法，將賠率變更序列化後寫入 `pricecenter.odds_his_{gameType}_{date}` 資料表，並壓縮歷史資料以節省儲存空間。

- **比賽歷史紀錄（MatchesHis）**  
  將比分、比賽進程（PlayByPlay）等資料以追加方式寫入 `pricecenter.matches_his_{gameType}_{date}`，確保完整保留比賽軌跡。

- **比賽與賠率變更去重檢查**  
  透過記憶體快取（PreMatch / PreOdd）判斷比賽比分或特定賠率是否有實際變動，避免無謂的資料庫寫入與下游更新。

- **自動修復與資料一致性維護**  
  執行定期的背景工作，包括：
  - `FixHisData`：清理、壓縮過期歷史資料（odds_his / matches_his）並刪除非必要站台的記錄。
  - `FixMergeData`：修正合併過程中可能產生錯誤的映射資料（League、Team、Game）。
  - `FixLeagues` / `FixTeams`：確保聯盟、隊伍與站台映射一致。
  - `FixTeamLogoInfo`：補遺缺少 Logo 的隊伍資訊。
  - 清除異常比賽（status=9 且無對應 sitegame）等，維護 `pricecenter` 與 `predict` 資料的正確性。

- **即時比賽 Log 與 InplaySiteLog**  
  每 15 秒收集指定站台（如 sa8888.net、1xbet.com）的滾球比分與讓球盤、大小盤資料，寫入 Cassandra `inplay_logs` 表，並定期清理（保留 14 天）。

- **ChangeLog 更新（選擇性啟用）**  
  記錄每場比賽的變更紀錄，目前預設關閉。

## 技術棧

| 類別 | 技術 |
|------|------|
| 語言與框架 | .NET 8, C# |
| 執行環境 | Docker, Docker Swarm |
| 訊息佇列 | Kafka (Confluent.Kafka) |
| 快取 | Redis (StackExchange.Redis) |
| 資料庫 | Cassandra (DataStax C# Driver)，連線 `pricecenter`、`predict` keyspace |
| 輔助套件 | AutoMapper、ECCore、ECFramework.ECService、GameDataModels |
| 日誌 | Kafka Logger (自訂寫入 Loki) |

## 組態與部署注意

- **組態管理**  
  支援多環境設定（`appsettings.json` + 環境特定檔案如 `appsettings.PRD.json`、`appsettings.Development.json`），透過 `DOTNET_ENVIRONMENT` 環境變數切換。主要設定項目包含：
  - Kafka 叢集位址、Consumer Group ID、訂閱主題
  - Redis 連線（GameDataDB、SiteGameDataDB、GameMappingDB）
  - Cassandra 連線（pricecenter、predict keyspace）
  - 站台清單、球種清單、資料庫寫入開關（`WriteDB`）、測試模式（`TestMode`）

- **部署注意**  
  - Dockerfile 基於 `mcr.microsoft.com/dotnet/sdk:8.0`，以 `dotnet FlowControlService.dll` 啟動，並設定時區為 `Asia/Taipei`。
  - 服務會定期（每 3 天）自動重啟以釋放資源與重新整理快取；資料庫連續錯誤超過 100 次時亦會強制重啟。
  - 生產環境建議佈署至少 3 個實例（對應 PRD1/PRD2/PRD3 三個獨立 Kafka Consumer Group），分散負載。
  - 注意 `NoDBDay` 陣列配置：PRD 環境為空（每日寫入），開發環境排除週末（0,6）。

## 資料操作要點

- 寫入 `pricecenter` 的 `actionlog`、`alertlog` 僅允許 **INSERT**，禁止 UPDATE / DELETE。
- 歷史表（`matches_his_*`、`odds_his_*`、`inplay_logs`）的資料變更必須使用 **追加（append）語法**（如 `SET logs = logs + ?`），不可覆蓋整個欄位。
- 讀取 `accounts_*` 時必須一併過濾 `enabled = 1`，且不得在對外 API 回應中回傳 `password`（含雜湊值）或 `handler`。
- 操作 `predict` keyspace 時，`betpool_games.status` 僅能由掌有結算權限的服務更新為 2（結算），不可直接寫入 3（取消）；寫入後應主動清除對應的 Redis 快取。
- 所有對 Cassandra 的查詢都必須搭配完整分區鍵（partition key），嚴禁跨日期或跨分割區的全表掃描。

> 詳細的寫入限制與常見錯誤請參閱 `flowcontrolservice-detail.md`。

## 相關文件

- 業務規範與設計文件摘要：詳見 `service/flowcontrolservice/documents.md`。
  - Confluence 頁面 [TCZB-312](https://confluence.zbdigital.net/pages/viewpage.action?pageId=9797885)（最後更新 2020-10-26）、[TCZB-509](https://confluence.zbdigital.net/display/TCZB/TCZB-509)（最後更新 2020-12-22）及 [TCZB-1993](https://confluence.zbdigital.net/pages/viewpage.action?pageId=38011930)（最後更新 2022-07-29）的摘要，可能與現行實作有落差，實作時應以原始碼為準。
- DB 操作邊界：`service/flowcontrolservice/flowcontrolservice-detail.md`

## 相關連結

- **GitLab 儲存庫**：https://git.zbdigital.net/biz/flowcontrolservice.git