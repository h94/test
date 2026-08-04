# OddNotificationService

## 概述

OddNotificationService 是賠率異常監控系統的**即時通知閘道**（.NET 10 / ECFramework），負責：

1. 消費 Kafka Topic **`alert_events`**（上游 OddAlertService），合批後以 SignalR 推送 **`alert_created`**
2. 接收 AlertBackendService 內部 HTTP **`POST /api/system/broadcast/alertstatus`**，合批後推送 **`alert_status_updated`**

本服務**不讀寫 DB**、不做異常判斷；歷史查詢由 AlertBackendService REST 負責。Hub 訂閱慣例比照 [PriceSubscriptionSystem](../pricesubscriptionsystem/README.md)（`AddGroup(gameType, companyToken)`）。

> 業務規則與 I/O 契約以 [`documents.md`](./documents.md) 為準；實作 Plan 見專案 repo `_plans/TCZB-4446.md`。

## 主要功能

- **Kafka 消費**：訂閱 `alert_events`，`AutoOffsetReset=Latest`；at-least-once 下以 `AlertDedupProvider` 對 `id` 短 TTL 去重
- **200ms 合批推送**：`AlertBroadcastBatcherWork` 定時取出佇列，分事件類型組 envelope 後送 SignalR
- **SignalR Hub（OddHub）**：`/hubs/OddHub`；Client `invoke AddGroup` / `RemoveGroup`；Server push `alert_created`、`alert_status_updated`
- **Group 路由**：每筆推送至 `game_ALL` 與 `game_{GAME_TYPE}`（大寫，如 `game_SC`）
- **game_info 精簡**：同一 `(source, game_id)` 第二次起可省略 `game_info`
- **狀態合批去重（M6）**：同一 200ms 窗口內同 `alert_id` 只保留最後一筆 `alert_status_updated`
- **開發測試頁**：`GET /Home/AlertTest`（MVC）；WS / API log 分欄；可模擬 ingest 與 status broadcast

## API 端點（REST）

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/version` | GET | 服務版本、建置時間、主機名稱 |
| `/api/heart` | GET | 心跳（**不含** Kafka Consumer 狀態） |
| `/api/system/broadcast/alertstatus` | POST | AlertBackendService 觸發狀態廣播（snake_case body；成功 200 無 body） |

詳盡 OpenAPI 見 [`oddnotificationservice.json`](./oddnotificationservice.json)；執行時 Swagger UI：`/swagger/index.html`。

## SignalR（非 OpenAPI）

| 項目 | 說明 |
|------|------|
| Hub URL | `/hubs/OddHub` |
| Client → Server | `AddGroup(gameType, companyToken)`、`RemoveGroup(gameType)` |
| Server → Client | `alert_created`、`alert_status_updated`（payload 為合批 envelope） |
| 訂閱驗證 | `HubSettings.CompanyToken`（`company` / `authToken` / `enabled`） |
| Group | `game_ALL`（`gameType=ALL`）或 `game_{GAME_TYPE}`（全大寫） |

## 技術棧

- **執行環境**：.NET 10 / ASP.NET Core（`ECFramework.ECService`）
- **即時通訊**：SignalR（JSON 協定）
- **訊息佇列**：Confluent.Kafka Consumer（`alert_events`）
- **分層**：Host / DomainService / Infrastructure / Interface / Model
- **日誌**：`IKafkaLogger`（`applogs` topic）
- **測試**：xUnit + Moq（19 項，含 1 整合測試）

## 組態與部署注意

- **環境設定**：`appsettings.json` + `appsettings.{Environment}.json`（Local 含 Kafka / Hub / 合批完整設定）
- **Kafka Consumer**：`AppSettings.KafkaConsumerSettings`（Topic、GroupId、BootstrapServers）；`TestMode` 時 GroupId 加 `_Test` 後綴
- **合批**：`AlertBroadcastSettings.BatchIntervalMs`（預設 200）、`MaxQueueSize`、`MaxBatchSize`、`DedupeWindowMinutes`
- **Hub 授權**：`HubSettings.CompanyToken[]`；Token 變更需重啟（Phase 1 無熱載入）
- **內部 HTTP**：僅內網隔離，無額外 API Key
- **安全**：部署須強制 **HTTPS / WSS**（`companyToken` 經 invoke 傳送）
- **健康檢查**：`/api/heart` 不反映 Kafka lag；lag 僅 log
- **資源**：Plan 建議 4 GB RAM；Phase 1 單 instance

## 資料庫

**本服務不使用任何 DB。** 合批佇列、去重集合、game_info 精簡快取均為**程序內記憶體**；重啟或 OOM 保護丟棄時，斷線期間訊息不補發。

邊界與限制見 [`oddnotificationservice-detail.md`](./oddnotificationservice-detail.md)。

## 服務相依

| 方向 | 服務 | 說明 |
|------|------|------|
| 上游 | OddAlertService | 產出 `alert_events`（見 TCZB-4443） |
| 下游呼叫方 | AlertBackendService | PATCH 成功後 POST `broadcast/alertstatus` |
| 下游訂閱方 | 後台 Vue（另 repo） | 連線 OddHub、本地過濾站台/等級 |
| 慣例參考 | PriceSubscriptionSystem | Hub `AddGroup` + `companyToken` |

## Scenario Flows

手動整合驗收情境：[`scenario-flows/alert-push-flow.md`](./scenario-flows/alert-push-flow.md)

## 相關連結

- 實作 Plan：專案 `_plans/TCZB-4446.md`
- 上游契約：[TCZB-4443 OddAlertService](../../_plans/_reference/TCZB-4443.md)（repo 內 `_plans/_reference`）
- Hub 慣例參考：[PriceSubscriptionSystem](../pricesubscriptionsystem/README.md)
