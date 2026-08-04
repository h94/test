# 預測結果服務 (PredictResultService)

## 概述
PredictResultService 是內部系統的 **背景工作者服務**，負責處理賽事預測的結果結算、玩家等級更新、每週輸贏報表計算及歷史資料清理。該服務以 .NET 8 實作，部署於 Docker Swarm 叢集，並與 Cassandra、Kafka 及內部 RESTful API 整合。

## 主要功能
- **預測結果結算**  
  定時從 Cassandra 取得已完成賽事，比對預測單並計算輸贏結果，更新預測單狀態與玩家錢包。
- **每週報表計算**  
  統計每週各玩家的預測次數、勝負數、損益點數，產出週報。
- **玩家等級升級**  
  根據近一日預測活躍度（比賽場次）自動調整玩家等級（Rank）。
- **新彩券結果處理**  
  支援「新彩券」模式的賽事結果結算與錢包交易。
- **歷史資料清理**  
  定期清除過期預測記錄與結果日誌，保留近 8 週資料備用重新計算。
- **社群預測同步**  
  若預測單來自社群，結果更新後同步回社群系統。
- **異常監控與告警**  
  透過 Kafka 日誌與 AlertProvider 發送錯誤或完成通知。

## 技術棧
| 類別       | 技術                                     |
| ---------- | ---------------------------------------- |
| 語言       | C# (.NET 8)                              |
| 框架       | .NET Worker Service, ECFramework, ECCore |
| 資料庫     | Cassandra (keyspace: pricecenter, predict, member) |
| 訊息佇列   | Kafka (topic: applogs)                    |
| 內部 API   | RESTful (Gateway: member service)        |
| 測試       | xUnit, Moq                               |
| 部署       | Docker Swarm (container image: predictresultservice:latest) |

## 組態與部署注意
- **環境變數**  
  使用 `ASPNETCORE_ENVIRONMENT` 切換組態檔（`appsettings.json`、`appsettings.PRD.json`、`appsettings.Development.json`、`appsettings.Local.json`）。
- **Cassandra 連線**  
  需設定 `AppSettings:CassandraSettings` 中的 Server 與 Keyspace（PRD: 192.168.55.80，Local: 192.168.9.234）。
- **Kafka 設定**  
  BootstrapServers 指向 `49.213.1.158:29096`，GroupId 為 `AppLogXSystem`。
- **RESTful Gateway**  
  用於建立錢包交易與更新玩家等級，依環境不同 Gateway 位址不同（PRD: 192.168.55.87:22306，Local: 192.168.9.232）。
- **排程行為**  
  主要迴圈每 3 分鐘執行一次結果檢查；等級升級每日 12:00~18:00 執行；每週報表每 5 分鐘檢查。
- **部署**  
  使用 Portainer 管理 Docker Swarm 服務，映像標籤為 `predictresultservice:latest`。

## 相關連結
- **GitLab 原始碼**  
  [https://git.zbdigital.net/biz/predictresultservice.git](https://git.zbdigital.net/biz/predictresultservice.git)
- **Portainer**  
  PRD_Docker_Swarm 環境下的 `predictresultservice` 容器。