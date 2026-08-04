# InplayzSubscriptionSystem

## 概述
InplayzSubscriptionSystem 為內部即時賽事訂閱系統，負責接收 Kafka 賽事數據，經處理後透過 SignalR Hub 推送給各商務端。採用 .NET 8 Web API 實作，部署於 Production Docker Swarm 叢集。

## 主要功能
- **商務驗證與快取**：驗證商務代碼與授權 Token，並快取商務訂閱資訊，定期檢查訂閱時效。
- **即時賽事數據處理**：從 Kafka 消費賽事消息，解析、比對、轉換為前端適用的 SiteGameDto，並依據賽事狀態（PreGame、InProgress、Final）分流處理。
- **SignalR Hub 推送**：透過 Hub 將賽事數據即時推送至已連線客戶端，支援走地賽事與比賽結果獨立執行緒處理。
- **連線管理與安全**：記錄連線資訊、IP 速率限制（每 IP 3 分鐘內最多 20 次連線）、自動斷線清除。
- **自動維護**：定期清理過期快取及逾時連線，並於每週五下午自動重啟服務以維持穩定性。

## 技術棧
- **.NET 8** (SDK 8.0)
- **ASP.NET Core SignalR** (含 MessagePack 通訊協定)
- **Kafka** (透過 ECFramework 封裝之消費者)
- **ECCore / ECFramework.ECService** (內部基礎框架)
- **GameDataModels** (賽事資料模型)
- **Docker** (容器化部署，暴露 Port 5000)
- **Docker Swarm** (Production 叢集，由 Portainer 管理)

## 組態與部署注意
- **Dockerfile**：
  - 基於 `mcr.microsoft.com/dotnet/sdk:8.0` 建置，最後以 `dotnet InplayzSubscriptionSystem.dll` 啟動。
  - 時區設定為 `Asia/Taipei`。
  - 僅暴露單一 Port 5000（對應 ASP.NET Core 預設服務埠）。
- **組態**：
  - 需正確設定 Kafka GroupId 與 Broker（`appsettings.json` 之 HubSettings 區段）。
  - 資料庫連線（BusinessDataProvider）需可存取商務與訂閱資訊表。
- **部署注意**：
  - 服務啟動後約 3 分鐘開始初始化商務快取。
  - 若無客戶端連線且非測試模式，則僅記錄來源站點而不處理消息。
  - 支援按 `TestMode` 設定切換 Kafka GroupId 附加機器名稱以避免衝突。

## 相關連結
- **GitLab 倉庫**：[https://git.zbdigital.net/biz/inplayzsubscriptionsystem.git](https://git.zbdigital.net/biz/inplayzsubscriptionsystem.git)
- **Portainer 標籤**：`PRD_Docker_Swarm|container|4827eff4b721|inplayzsubscriptionsystem:latest`