# Alert Push Flow（OddNotificationService 整合測試）

> TCZB-4446 Phase 4 手動驗收情境；對應 Plan §11 Phase 4 Scenario Flows。
> aidata 副本；專案 repo 同步路徑：`scenario-flows/alert-push-flow.md`

## 前置條件

- 服務以 `Environment=Local` 啟動（`appsettings.Local.json`）
- `HubSettings.CompanyToken` 含 `local-dev-token`（DEV）
- 瀏覽器開啟 `/Home/AlertTest`

## 情境 1：SimulateAlertCreated → SignalR（無 Kafka）

| 步驟 | 動作 | 預期 |
|------|------|------|
| 1 | 輸入 gameType=`SC`、token=`local-dev-token`，按「連線並訂閱」 | 狀態「已連線」，group=`game_SC` |
| 2 | 按「送出模擬 alert_created」 | HTTP 200 `{ accepted: true }` |
| 3 | 等待 ≤250ms | **左欄 WS log** 收到 `alert_created` envelope |
| 4 | 再送一筆同 `(source, game_id)` | 第二筆 `game_info` 省略 |

## 情境 2：broadcast/alertstatus → SignalR

| 步驟 | 動作 | 預期 |
|------|------|------|
| 1 | 已訂閱 `SC` | group=`game_SC` |
| 2 | 按「送出狀態廣播」 | **右欄 API log** HTTP 200 無 body |
| 3 | 等待 ≤250ms | **左欄 WS log** 收到 `alert_status_updated` envelope |

## 情境 3：RemoveGroup（M3）

| 步驟 | 動作 | 預期 |
|------|------|------|
| 1 | 已訂閱 `SC` | — |
| 2 | 按 RemoveGroup | group 顯示 `—` |
| 3 | 再送 simulate / broadcast | 該連線不再收到 `game_SC` 推播（仍連線中） |

## 情境 4：Kafka alert_events（需 broker 存取）

| 步驟 | 動作 | 預期 |
|------|------|------|
| 1 | 已訂閱對應球種 | — |
| 2 | 向 `alert_events` 投遞合法 JSON | Consumer log 收到 |
| 3 | 等待 ≤250ms | **左欄 WS log** 收到 `alert_created` batch |

## 自動化

- 單元測試：`dotnet test`（19 項）
- Simulate 路徑整合：`SimulateAlertCreatedIntegrationTests`
