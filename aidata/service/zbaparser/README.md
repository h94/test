# zbaparser - ZBA 賽事解析器

## 概述

zbaparser 為 ZBA（ZB Analysis）賽事解析服務，負責從 Kafka 消費 `processedgamedata` 主題的原始賽事資料，進行賠率運算、分數修正、賽果判斷，並將最終的 `gamedata` 結果寫回 Kafka。服務也包含聯盟/隊伍名稱快取、Redis 賽事快取管理、Cassandra 價格中心存取等功能，支援多球種（足球、籃球、棒球、網球等）的即時與賽後處理。

## 主要功能

- **Kafka 消費與發送**：從 `processedgamedata` 主題接收爬蟲原始資料，解析後將計算完成的賽事賠率、即時資訊發送至 `gamedata` 主題。
- **賽事賠率運算**：包含讓分盤（HA）、大小盤（OU）、正確比分、滾球盤（RBHA/RBOU）等，並進行賠率保護（檢查範圍、Spread 變動合理性）。
- **賽果判斷**：根據多個來源站台（如 hga.com, bwin.com, 1xbet.com 等）的結果進行比對與合併，產生最終賽果（Final）或取消（Cancel）。
- **即時比分修正**：針對不同站台的 PlayByPlay 格式進行統一，並修正分數倒退、時間格式異常等問題。
- **Redis 快取管理**：維護賽事快取（GameCache）、站台賽事映射（SiteGameMapping），每日清理過期資料。
- **設定與開關**：透過 `gamesettingservice` API 取得玩法設定（PlayModeConfig）與站台開關，支援動態更新。
- **聯盟/隊伍名稱修正**：從外部 API 取得聯盟與隊伍中文名稱，並定時修正 ZBA 站台的命名差異。

## 技術棧

| 元件 | 技術 |
|------|------|
| 執行環境 | .NET 8 (Worker Service) |
| 部署平台 | Docker Swarm (PRD) |
| 訊息佇列 | Apache Kafka (BootstrapServers: 192.168.55.85/86/87) |
| 快取資料庫 | Redis (192.168.55.80:6379, DB 4~7) |
| 持久化儲存 | Cassandra (192.168.55.80, Keyspace: pricecenter) |
| 設定 API | HTTP REST (gamesettingservice) |
| 記錄 | Kafka Logger (topic: applogs) |

## 組態與部署注意

- **環境設定檔**：使用 `appsettings.{環境}.json`（Development, Local, PRD, PRE 等），需依環境準備正確的 Kafka、Redis、Cassandra 連線字串。
- **啟動順序**：服務啟動時會先初始化聯盟/隊伍快取 → 取得賽事資料 → 載入玩法設定，最後才開始消費 Kafka 訊息。若快取未就緒會持續等待。
- **容器部署**：Dockerfile 基於 `mcr.microsoft.com/dotnet/sdk:8.0`，時區設定為 Asia/Taipei。EntryPoint 為 `dotnet ZBAParser.dll`。
- **自動重啟**：服務內建定時重啟機制（每日 14:00 左右），避免長期運行的快取問題。
- **測試模式**：可透過 `TestMode` 開關啟用，並從本機檔案讀取測試資料進行驗證。

## 相關連結

- GitLab 原始碼：[https://git.zbdigital.net/CrawlerAgent/zbaparser.git](https://git.zbdigital.net/CrawlerAgent/zbaparser.git)
- Portainer 容器管理：`PRD_Docker_Swarm` 環境下的 `zbaparser` (Image: `zbaparser:latest`)
- 相依服務：GameSettingService (API), Kafka 叢集, Redis 叢集, Cassandra