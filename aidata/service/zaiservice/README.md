# ZAIService 內部服務目錄

## 概述

ZAIService 是以 .NET 8 為基礎的後台 Worker 服務，專注於運動賽事數據分析、AI 預測生成、自動化新聞撰稿與多語言翻譯。服務透過 Cassandra、Redis 與 Kafka 進行資料儲存與日誌通訊，並整合多個外部賽事資訊站台（如 leisu、covers.com、nba.com 等）與 LLM 引擎，實現賽前分析、即時賽況報導與機器人文章發布。

## 主要功能

- **AI 預測與比分分析**  
  結合站台分析、玩家預測與賠率走勢，產出勝負、讓分與大小的綜合 AI 預測投票結果。

- **自動化賽事文章生成**  
  透過 LLM（多種 Workspace）根據賽事資料、分析數據與預測內容，產出賽前分析、即時賽況與賽後回顧文章。

- **機器人發布系統**  
  模擬多個 Bot 帳號，自動在論壇發布預測文章與回覆，並支援罐頭訊息與時間隨機調度。

- **多語言翻譯與檔案輸出**  
  調用 LLM 翻譯工作區，將文章翻譯成各國語言並寫入磁碟檔案供前端使用。

- **場中（Inplay）動態更新**  
  即時擷取 Play-by-Play 資料，根據比賽進度（節次、時間）更新文章內容，並支援 CSV 輸出歷史統計。

- **賠率日誌與清理**  
  紀錄賠率變化、修正過期文章狀態、清理過期磁碟檔案。

## 技術棧

| 分類       | 技術                                       |
| ---------- | ------------------------------------------ |
| 語言與框架 | C# 12, .NET 8, Worker Service              |
| 資料庫     | Cassandra（多 Keyspace）、Redis（GameData） |
| 訊息佇列   | Kafka（應用日誌）                          |
| 容器化     | Docker（base image: dotnet/sdk:8.0）       |
| 外部服務   | LLM API（多 Workspace）、多家賽事資訊站台  |
| 套件管理   | NuGet（ECCore, ECFramework, HtmlAgilityPack, MathNet.Numerics 等） |

## 組態與部署注意

- **組態檔**  
  主要設定位於 `ZAIService/appsettings.json`（與 Development、PRD 環境覆蓋），包含：
  - `KafkaLoggerSettings`：Kafka Broker、GroupId、Topic
  - `AppSettings`：Cassandra 連線資訊、Redis 連線、ToDoLeagueSettings、AIPredictRules、ToDoSiteList 等

- **資料庫依賴**  
  需確保 Cassandra 中 `pricecenter`、`news`、`predict`、`member` 四個 Keyspace 可用，以及 Redis DB 5 正常連線。

- **部署方式**  
  使用 Docker 容器化，環境變數 `TZ=Asia/Taipei` 設定時區，ENTRYPOINT 為 `dotnet ZAIService.dll`。

- **網路連線**  
  服務需對外存取：
  - Kafka Broker（範例 IP: `49.213.1.158:29096`）
  - Cassandra（範例 IP: `192.168.55.80`）
  - Redis（範例 IP: `192.168.55.80:6379`）
  - 外部賽事 API 與 LLM API

- **資源提醒**  
  服務內有多個 Thread 迴圈（如 `threadToRunInplay`、`threadToPostArticles`），需注意 CPU 與記憶體使用量，建議搭配健康檢查與日誌監控。

## 相關連結

- 原始碼：<https://git.zbdigital.net/biz/zaiservice.git>
- Portainer 容器標籤：`PortainerKey=SRV60|container|zaiservice`

## 外部依賴與資料流

- **CrawlerAgent 資料整合**  
  依據 TCZB-531 規範，bet365api 需將其抓取到的聯盟玩法資訊（玩法網址、聯盟名稱、gameType）透過呼叫 API 傳遞至後端服務。此文件狀態為草稿（最後更新於 2020 年 12 月），**需人工確認**最終實作狀態與目標服務端點。