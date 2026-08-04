# PriceSubscriptionSystem

## 概述

PriceSubscriptionSystem 是基於 .NET 8 的內部 Web API 服務，負責從多個來源站點訂閱即時賠率資料，透過 Kafka 訊息佇列接收賽事數據，並經由 SignalR Hub 進行統整、過濾與分發。服務運行於 Docker Swarm 叢集，提供高併發的賠率推送能力，為前端與下游系統提供統一的賠率訂閱接口。

服務會讀取 pricecenter Cassandra 中的帳號狀態（如 `enabled`、`closetime`），並寫入操作日誌（`actionlog`）。本服務不負責帳號的啟用／停用管理、密碼設定，以及各站台玩法的設定同步；這些由上游 pricecenter 管理後台或其他專屬服務處理。關於本服務對 pricecenter Cassandra 的具體操作限制與讀寫邊界，請參閱下方〈資料庫操作邊界〉一節。

> ⚠️ 近期業務討論（如賽前／走地分開訂閱、站台自動支援所有玩法、商務號聯盟訂閱等）可能影響服務行為，實作前務必查閱 [`documents.md`](./documents.md) 並確認最終決策。

## 主要功能

- **多站台賠率彙整**：從各來源站點收集不同賽事類型的賠率，並透過各站對應的 `HubDataTransfer` 實作（如 `bet365.com`、`bwin.com`、`cloudbet.com`、`hga.com`、`jz.com`、`ku.com`、`m88.com`、`mb.com`、`oxb.com`、`pinnacle.com`、`sbo.com`、`tony.com`、`vbet.com`、`asc.com` 等）進行格式統一、主客隊轉換、無效賠率過濾等處理。支援的站點包含 asc.com、bet365.com、bwin.com、cloudbet.com、hga.com、jz.com、ku.com、m88.com、mb.com、oxb.com、pinnacle.com、sbo.com、tony.com、vbet.com 等。（需人工確認最新完整站台清單）
- **即時資料推送**：透過 SignalR Hub 與用戶端建立即時連線，推送標準化的 `SiteGameOutputDto` 資料。Hub 初始化時會依用戶授權輸出對應賽事或站台的初始賠率。
- **Kafka 訊息消費**：訂閱指定的 Kafka Topic（`processgamedata`），非同步消費並處理比賽數據，並追蹤各站台的最後更新時間。
- **Redis 快取**：對已處理的賠率輸出（`SiteGameOutputDto`）進行快取，減少重複計算與資料庫負擔。
- **連線管理與防護**：限制單一 IP 短時間內的連線次數（預設規則為 3 分鐘內超過 20 次則阻擋，並記錄 `Ben IP` 警告日誌；實際邏輯由 `IPriceCenterHubService` 控制，需人工確認現行閾值），避免惡意連線。免費試用帳號（`Company=Free`）僅能存取部分開放站台。
- **訂閱授權控制**：依據 `CompanyToken` 驗證用戶端身分，區分內部測試帳號（ZB）、管理 UI（PC）、訂閱客戶與免費試用者。連線時檢查請求的站台與球種是否為該站支援的玩法。
- **結果處理與監控**：記錄 Hub 發送統計、連線資訊，並提供 PriceCenterManager Dashboard 查詢介面，包含各站台最後更新時間。

## API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/version` | GET | 取得服務版本、建置時間與主機名稱 |
| `/api/heart` | GET | 心跳檢查，回傳伺服器目前時間 |
| `/api/v1/system/hubinfo` | GET | 取得 SignalR Hub 連線清單與各資料源站台最後更新時間（供 PriceCenterManager Dashboard 使用） |
| `/api/v1/schema` | GET | 取得系統支援的參數 Schema（含玩法模式對照表 Mapping） |

詳盡的請求與回應格式請參考服務內建的 OpenAPI 文件（若已啟用）。

## 技術棧

- **執行環境**：.NET 8 / ASP.NET Core
- **即時通訊**：SignalR (MessagePack 協定)
- **訊息佇列**：Confluent Kafka (Consumer)
- **資料快取**：Redis
- **容器化**：Docker (Dockerfile 基於 `mcr.microsoft.com/dotnet/sdk:8.0`)
- **部署平台**：Docker Swarm (Portainer 管理)
- **內部依賴**：ECCore、ECFramework.ECService、GameDataModels

## 組態與部署注意

- **Docker 映像**：基於 `mcr.microsoft.com/dotnet/sdk:8.0`，暴露埠 `5000`（內部 Hub 端點使用 `http://127.0.0.1:5000/hub`）。
- **時區設定**：映像內設定 `TZ=Asia/Taipei`，確保時間處理正確。
- **Kafka 設定**：需於 `appsettings.json` 或環境變數中指定 `HubSettings.KafkaBootstrapServers`、`KafkaGroupId`、`KafkaTopic`。
- **Redis 連線**：需提供 `IRedisCacheService` 實作，建議使用環境變數注入連線字串。
- **來源站台與授權**：需設定 `HubSettings.SourceSites`（含各站支援的 `GameTypes`）與 `HubSettings.CompanyToken`（客戶端授權金鑰）。
- **資源限制**：由於連線管理與記憶體快取，建議容器記憶體不小於 2GB。
- **健康檢查**：可透過 `/api/heart` 端點進行 HTTP 健康檢查；SignalR `/hub` 端點可進行連線測試。

## 資料庫操作邊界

本服務對 pricecenter Cassandra 的讀寫需嚴格遵守以下規則（完整細節請參考 [`pricesubscriptionsystem-detail.md`](./pricesubscriptionsystem-detail.md)）：

- **帳號有效性檢查**：必須同時滿足 `enabled = 1` **且** `closetime` 為空（NULL 或空字串），才視為有效可用帳號。任一條件不符（例如 `enabled = 0` 或 `closetime` 已有值）均不可執行訂閱相關操作。
- **寫入限制**：
  - `accounts_*` 系列表僅供讀取，本服務嚴禁 INSERT、UPDATE 或 DELETE；`enabled`、`closetime`、`password`、`handler` 等欄位均由 pricecenter 管理後台或其他專屬服務維護。
  - `actionlog`：由 `PriceCenterHub` 或內部排程寫入，必須以日期分區鍵 `date`（格式 `yyyy-MM-dd`）進行操作；寫入時需提供 `action`、`actionclass`、`user`、`gametype`，`addtime` 精確到毫秒級，`detail` 為有效 JSON。查詢必須包含 `date` 範圍條件，禁止全表掃描。
  - `alertlog`：由 `AlertLogDataProvider` 寫入，所有欄位（`site`、`gtype`、`sitegid`、`gid`、`content` 等）為必填，`addtime` 為 Unix 秒，不可重複插入相同組合。
  - `kupages`：僅允許透過 `ManagerDataProvider` 以 `pagename` 為主鍵 UPDATE `adddate`，不支援 INSERT 或 DELETE。
  - `sitegames_{gameType}` / `odds_{gameType}` 系列表僅供讀取，本服務不得寫入。
- **資料保護**：
  - `password`：任何對外 API **不得回傳**（包含管理端查詢），僅能回傳是否已設定密碼的狀態。
  - `handler`：若存放第三方金鑰或連線資訊，回傳前必須過濾敏感鍵值，不得完整暴露。
  - `phone`：視為個人資料，API 回傳時應避免完整號碼，前端須脫敏處理。
  - `sitegames_*` / `odds_*` 的賠率原始字串（`ha`、`rbha` 等）不建議直接暴露給終端，應透過領域 API 轉換為結構化資料。
- **常見錯誤**：
  - ❌ 直接讀取 `password` 比對明碼 → 應透過後台 API 驗證。
  - ❌ 只檢查 `enabled=1` 忽略 `closetime` → 已關閉帳號不可使用。
  - ❌ actionlog 查詢未含 `date` 分區鍵 → 必須包含分區條件。

## 相關連結

- GitLab 儲存庫：[https://git.zbdigital.net/biz/pricesubscriptionsystem.git](https://git.zbdigital.net/biz/pricesubscriptionsystem.git)
- Portainer Key：`SRV84|container|pricesubscriptionsystem`
- 業務規則文件：[`documents.md`](./documents.md)（Confluence 摘要，包含訂閱機制、收費標準、會議記錄等，實施前請確認時效性）