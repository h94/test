# oddnotificationservice — I/O 與操作邊界

> 產出時間：2026-07-07
> **README**：[./README.md](./README.md) — 職責、技術棧、API、SignalR、服務相依（**本文件不重複**）
> **業務規則**：[./documents.md](./documents.md)
> ⚠️ AI 產出，需資深工程師審核後生效

---

## 資料庫

**本服務不連線任何 DB**（PostgreSQL / Cassandra / Redis 等均不使用）。

| 資料 | 儲存位置 | 說明 |
|------|----------|------|
| 合批佇列 | 記憶體 `AlertBroadcastQueueProvider` | `MaxQueueSize` 超限丟棄最舊 + Warning |
| Kafka `id` 去重 | 記憶體 `AlertDedupProvider` | TTL 預設 5 分鐘 |
| `game_info` 精簡 | 記憶體 `GameInfoSlimmingProvider` | `(source, game_id)` TTL 預設 60 分鐘 |

---

## Kafka（Consumer）

### 設定（`AppSettings.KafkaConsumerSettings`）

| 欄位 | 說明 |
|------|------|
| Topic | `alert_events`（與 OddAlertService 對齊） |
| GroupId | `OddAlert{Environment}`（TestMode 加 `_Test`） |
| BootstrapServers | 依環境（Local / PRD 見 Plan §14.3） |

### 讀取規則

- `AutoOffsetReset = Latest`：新 consumer 不追歷史
- 訊息年齡超過 `MaxMessageAgeMs`（若設定）→ skip + log
- 無效 JSON、缺 `game_type` / `id` 等 → log，**不 crash host**
- 重複 `id`（去重窗口內）→ 不 enqueue

### 寫入限制

- **禁止** 本服務 produce 至任何 Kafka topic（Phase 1 僅 Consumer）

---

## SignalR（OddHub）

### Client → Server（invoke）

| Method | 參數 | 行為 |
|--------|------|------|
| `AddGroup` | `gameType`, `companyToken` | 驗證 token → 加入 `game_ALL` 或 `game_{gameType}` |
| `RemoveGroup` | `gameType` | 離開 group；連線保持 |

### Server → Client（push）

| Method | payload | 訂閱條件 |
|--------|---------|----------|
| `alert_created` | `AlertBroadcastEnvelope` | 已加入對應 `game_*` group |
| `alert_status_updated` | `AlertBroadcastEnvelope` | 同上 |
| `SubscribeError` | string | token / gameType 無效時僅送 Caller |

### 驗證規則

- `companyToken` 須存在於 `HubSettings.CompanyToken` 且 `enabled = "1"`
- `gameType` 須**全大寫**（`ALL` / `SC` / `BK`…）
- **不**依 company 切分 Kafka 廣播內容

---

## 內部 HTTP

| Path | 驗證 | 行為 |
|------|------|------|
| `POST /api/system/broadcast/alertstatus` | 內網隔離（無 API Key） | 驗證 body → enqueue → 200 無 body |

### Request 驗證（`SystemService.BroadcastAlertStatus`）

| 欄位（wire） | 必填 | 失敗 |
|--------------|:----:|------|
| `alert_id` | ✅ | 400 |
| `game_type` | ✅ | 400 |
| `status` | ✅ | 400 |
| `handled_action` / `handled_by` / `handled_at` | — | — |

---

## MVC 開發端點（非 Swagger）

| Path | 說明 |
|------|------|
| `GET /Home/AlertTest` | 瀏覽器測試頁 |
| `POST /Home/SimulateAlertCreated` | 直接 ingest `alert_created` JSON（M7） |

---

## 本服務不負責

| 事項 | 負責服務 |
|------|----------|
| 異常規則與閾值 | OddAlertService |
| 警示持久化、歷史 API | AlertBackendService |
| 前端 UI、GameSettingSite auth | 前端 / 整合層 |
| 依 company 過濾警示內容 | 前端本地過濾 |
| 斷線補發 / resync | Phase 1 不實作 |

---

## 常見錯誤

- ❌ 未 `AddGroup` 就期待收到 WS 推播 → 須先訂閱對應 `gameType`
- ❌ HTTP 200 當作已推送 → 僅表示入佇列；須等 ~200ms 並監聽 `on("alert_status_updated")`
- ❌ 訂閱 `BK` 卻廣播 `game_type: sc` → 收不到球種 group（`game_ALL` 除外）
- ❌ 重連後未重新 `AddGroup` → 連線正常但無推播
- ❌ 在 Test 環境未載入 `appsettings.Local.json` → `companyToken` 驗證失敗
- ❌ 假設 `/api/heart` 包含 Kafka 健康 → 僅伺服器時間
