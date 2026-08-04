# oddnotificationservice — 業務與技術文件摘要

> 來源：**TCZB-4446** 專案 Plan（`oddnotificationservice/_plans/TCZB-4446.md`）；尚無獨立 Confluence 頁，本檔為引導師優先閱讀之業務規範摘要。
> 最後更新：2026-07-07
> 與 Plan / 程式衝突時以 **`documents.md`（本檔）** 與已上線程式為準；細節 I/O 見 Plan §8。

---

## 系統定位

OddNotificationService 是賠率異常監控架構中的**即時推送層**：

```
OddAlertService → Kafka alert_events → OddNotificationService → SignalR → 後台即時警示頁
AlertBackendService → HTTP broadcast/alertstatus → OddNotificationService → SignalR alert_status_updated
```

| 職責 | 負責方 |
|------|--------|
| 異常判斷、寫入 PG `alerts` | OddAlertService |
| 即時 WebSocket 推送 | **OddNotificationService** |
| 歷史查詢、PATCH 狀態 | AlertBackendService |

---

## 關鍵業務規則

### 推送事件

| SignalR method | 觸發來源 | 用途 |
|----------------|----------|------|
| `alert_created` | Kafka `alert_events` 或開發模擬 | 新警示出現 |
| `alert_status_updated` | HTTP `broadcast/alertstatus` | 他人處理/忽略後畫面同步 |

### 合批與延遲

- 預設 **200ms** 合批窗口（`BatchIntervalMs`）；Client 應在觸發後 **≤250ms** 內收到 batch
- envelope 格式：`{ event_type, items[], batch_time }`；`items` 內容型別依 method 不同

### 訂閱（比照 PriceSubscriptionSystem）

1. 連線 `/hubs/OddHub`（**不在** query string 帶球種）
2. `invoke("AddGroup", gameType, companyToken)` — `gameType` **全大寫**（`ALL` / `SC` / `BK`…）
3. 收到 `game_ALL` 或 `game_{GAME_TYPE}` 的推播
4. **重連後須重新 `AddGroup`**（`withAutomaticReconnect` 不恢復 group）

### 前端過濾

- `companyToken` 僅作**連線存取控制**；payload **不含** company 欄位
- 站台（`source`）、等級、規則等由**前端本地過濾**（非本服務職責）

### 狀態廣播 HTTP

- Path：`POST /api/system/broadcast/alertstatus`
- Body：**snake_case**（對齊 AlertBackendService FastAPI）
- **`game_type` 必填**；缺欄位回 **400**，不做 `alert_id → game_type` fallback
- 成功 **200 無 body**；SignalR 推播為**非同步**（入佇列後由 Batcher 送出）

### Kafka `alert_created` 欄位

- 以 **TCZB-4443 §8.4.3** 為準：`id`、`game_type`、`source`、`game_id` 等
- **不使用** 草稿舊名 `event_id` / `sport_type` / `source_id`

---

## 已知限制（Phase 1）

| 項目 | 說明 |
|------|------|
| 斷線不補發 | 佇列僅記憶體；斷線期間錯過的訊息不補；歷史用 `GET /alerts` |
| `/api/heart` | 不反映 Kafka Consumer / lag 狀態 |
| Token 輪替 | `HubSettings.CompanyToken` 變更需**重啟**服務 |
| 單 instance | 無 Redis SignalR backplane |
| Graceful shutdown | 依框架預設，極少量佇列資料可能未送出 |

---

## 開發與驗收

| 項目 | 路徑 |
|------|------|
| 手動測試頁 | `GET /Home/AlertTest` |
| 模擬 Kafka（M7） | `POST /Home/SimulateAlertCreated` |
| 情境說明 | [`scenario-flows/alert-push-flow.md`](./scenario-flows/alert-push-flow.md) |
| 自動測試 | `dotnet test`（19 項） |

---

## 注意事項

- ⚠️ 正式前端 Vue 頁在**另 repo**；本服務僅提供 Hub 與內部 HTTP
- ⚠️ `POST /Home/SimulateAlertCreated` 為開發用，**不在** Swagger OpenAPI 內
- ⚠️ AlertBackendService 需保證 `broadcast/alertstatus` 帶出 `game_type`（F1）
