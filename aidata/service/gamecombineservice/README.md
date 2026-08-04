# GameCombineService – 賽事合併服務

## 概述

GameCombineService 為 .NET 6 Worker Service，負責將各站點（如 1xbet、panda、betcity、napoleon、betsapi 等）的賽事資料自動合併至價格中心（PriceCenter），並執行翻譯、隊伍映射、賽事時間修正、取消異常賽事等維護工作。此服務為後端批次核心，確保前端顯示的賽事與賠率即時、正確。

## 主要功能

- **自動合併**：依球種與天數（+0 ~ +3 天）呼叫 PriceCenter API 進行賽事合併。
- **語系翻譯**：定期更新聯盟與隊伍的中文翻譯（支援強制更新）。
- **隊伍自動映射**：自動比對站點隊伍與本系統隊伍，處理映射錯誤。
- **賽事時間修正**：比對各站點賽事時間，自動更新異常比賽時間。
- **賽事取消偵測**：根據賠率更新時間判斷賽事是否延遲或取消，並自動關閉。
- **熱門排行榜**：觸發 PredictService 建立預測排行榜與熱門賽事資料。
- **異常偵測**：呼叫 Python API 檢查賽事是否有潛在錯誤。
- **告警發送**：透過 MQ (RocketMQ / Telegram) 發送錯誤或心跳訊息。
- **平台帳號管理**：負責建立或更新 `pricecenter.accounts_{brand}` 中的遊戲平台帳號，寫入時須將密碼雜湊處理，不可明文儲存。

## 技術棧

- **語言／框架**：C# .NET 6.0, BackgroundService
- **資料庫**：
  - Cassandra: `pricecenter`, `predict` (keyspace)，作為 writer。
  - MySQL `sport` (games 資料庫)，作為 reader，僅具讀取權限。
- **訊息佇列**：Kafka (作為 Logger), RocketMQ (告警)
- **外部 API**：PriceCenterService (內部 RESTful 服務), PredictService, 內部 RESTful 服務
- **容器化**：Docker, Portainer (PRD_Docker_Swarm)
- **版控**：GitLab (https://git.zbdigital.net/biz/gamecombineservice.git)
- **相依套件**：ECCore, ECFramework.ECService, GameDataModels, Microsoft.Extensions.Hosting

## 組態與部署注意

- **環境設定**：`appsettings.json` 搭配 `appsettings.Development.json`、`appsettings.PRD.json`、`appsettings.Local.json` 區分環境。PRD 環境的 Kafka BootstrapServers 指向 `192.168.55.60`，其他環境指向 `192.168.9.231,192.168.9.232,192.168.9.233`。
- **Cassandra**：需確保 `pricecenter` 與 `predict` 兩個 keyspace 存在且可連線（主機 `192.168.55.80`）。本服務對這兩個 keyspace 有寫入權限，負責合併、翻譯、帳號建立等寫入操作，具體責任邊界與不可回傳欄位請參考 [GameCombineService DB 操作邊界](./gamecombineservice-detail.md)。
- **服務分散**：透過 `Servers` 陣列（`["86","87"]`）隨機選擇 PriceCenter 實例，避免單點過載。
- **執行緒**：Worker 內使用 `ThreadPool.QueueUserWorkItem` 平行處理合併、翻譯、映射等多項工作，注意資源競爭與執行狀態管理（`ExecStaus`）。
- **Dockerfile**：基底使用 `mcr.microsoft.com/dotnet/sdk:6.0`，時區設為 `Asia/Taipei`，NuGet 來源包含內部託管站 (`http://192.168.9.234:8079/repository/nuget-hosted/` 與 `http://192.168.9.234:8079/repository/nuget.org-proxy/`)。
- **日誌**：透過 Kafka Logger 寫入，Topic `applogs`；PRD 生產環境需確認 Kafka 叢集正常。

## 相關連結

- [GitLab 儲存庫](https://git.zbdigital.net/biz/gamecombineservice.git)
- [Portainer 管理介面](http://portainer.zbdigital.net)（PRD_Docker_Swarm）
- [PriceCenterService 內部 API](http://192.168.55.60/pricecenter)（部分合併與翻譯端點）
- [PredictService API](http://192.168.55.60/predictservice)（排行榜與熱門賽事）
- [告警 MQ 端點](http://192.168.9.232/mq)（RocketMQ / Telegram）

## 相關文件

- [GameCombineService DB 操作邊界](./gamecombineservice-detail.md) — 寫入限制、讀取規則、不可回傳欄位與常見錯誤
- [相關文件摘要](./documents.md) — Confluence 技術設計與業務規範索引
- Confluence 設計文件：
  - [GameCombineService（自動合併流程）](https://confluence.zbdigital.net/display/TCZB/GameCombineService)
  - [TCZB-4359 AutoMergeService 技術設計](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471609)
  - [TCZB-4359 AutoMergeService 第一階段重構](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471725)
  - [合併 API 與其受影響之資料庫欄位](https://confluence.zbdigital.net/pages/viewpage.action?pageId=7111735)