# 批次查詢盤口快照

## 1. 場景目的

提供客戶端（如大廳、首頁）在一次請求中，查詢多筆不同球種、聯盟、日期的賽事盤口快照。此流程專為加速前端多筆盤口同時顯示而設計，避免客戶端發起多次單筆查詢。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/tradegames` | 傳入多筆 {gtype, lid, gdate, gid}，一次取得多球種盤口資料 |

**驗證需求**: ✅ API Key / 內部服務授權 (TCZB Globals)

**Request Body (OpenAPI)**:
```json
[
  {
    "gtype": "SC",
    "lid": "123",
    "gdate": "2026-05-22",
    "gid": "456"
  }
]
```

---

## 3. 流程總覽

1. 接收 POST body 為 Array，包含至少一筆 `{gtype, lid, gdate, gid}` 物件
2. 驗證 body 格式（Flask-marshmallow Schema 驗證）
3. 遍歷陣列中的每一筆查詢條件
4. 針對每一筆條件，組合 Redis key pattern（從 Redis DB5 讀取）
5. 從 Redis 讀取對應賽事盤口快照 (odds, use_spread, first_data 等)
6. 過濾並組裝回傳欄位（不可回傳內部敏感欄位，如 handler map）
7. 回傳盤口快照陣列
8. 若 Redis 無資料：回傳空陣列或略過該筆（需人工確認行為）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `tradegameservice.webapi.trade_games` | 接收 POST 請求，解析 body 為 Array |
| 2 | Validator | `Schema` (marshmallow) | 驗證 body 為 Array，每個元素包含 gtype, lid, gdate, gid |
| 3 | Service | `tradegameservice.service.trade_games_service` | 遍歷查詢條件，呼叫 Redis Provider |
| 4 | Provider | `tradegameservice.provider.redis_provider` | 組合 Redis key 格式（如 `odd:snapshot:{gtype}:{lid}:{gdate}:{gid}`），執行 GET 命令 |
| 5 | Transfer | `transfer/response_transfer` | 將 Redis 原始資料轉換為 `TradeGameSnapshotResponse` DTO，過濾內部欄位 |

> **需人工確認**: 具體的 Redis key pattern 格式未在 README 中明確，需查閱 `redis_provider.py` 實作以確認格式。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Cache | Redis DB5 | Read (GET) | 讀取即時盤口快照（odds, use_spread, first_data 等） |
| DB | Cassandra | ❌ 無 | 此 API 僅讀取 Redis，不讀取 Cassandra |
| Queue | Kafka | ❌ 無 | 無 Queue 操作 |

**重要說明**: 此 API 為純快取讀取流程，不涉及任何 DB 寫入或持久化存儲操作。

---

## 6. 重要規則

- **權限限制**: 必須通過 API Key 或內部服務授權驗證
- **不可回傳欄位**: 
  - Redis 快照中若有 `source` 內部標記，應確認是否需過濾（需人工確認）
  - 不可回傳內部 `handler` map 結構（參考 pricecenter-detail.md）
  - `password` 或敏感 phone 等欄位不可出現（參考 db-usage）
- **資料來源限制**: 僅從 Redis DB5 讀取，不應 fallback 到 Cassandra
- **批次大小限制**: Request body array 有隱性長度上限，需人工確認前端傳入筆數限制
- **TTL 規則**: Redis 快照的 TTL 由資料寫入端（crawleragent）控制，本服務不負責 TTL 設定

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| Request body 為空陣列 | 回傳 422 Validation Error |
| Request body 缺少必填欄位（如 gtype） | 回傳 422 Validation Error |
| 驗證失敗（無效 API Key） | 回傳 401 Unauthorized |
| Redis 無法連線（timeout） | 回傳 500 Internal Server Error，並由 MQService 推送告警 |
| Redis 中無對應 key 的快取 | 回傳空陣列（[]）或略過該筆（需人工確認） |
| 部分查詢成功、部分 Redis miss | 回傳僅包含查到的快照陣列（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| T01 | API Test | 傳入一筆有效 SC 球種的查詢條件 | 回傳 200，包含該場賽事盤口資料（odds, use_spread） |
| T02 | API Test | 傳入多筆不同球種（SC, BK）的查詢條件 | 回傳 200，全部都有對應盤口快照 |
| T03 | Flow Test | 傳入 Redis 中不存在的 gid/lid 組合 | 回傳空陣列（或略過該筆），不應 500 錯誤 |
| T04 | Permission Test | 無 API Key 的請求 | 回傳 401 Unauthorized |
| T05 | Error Test | Redis 模擬斷線，發送 POST 請求 | 回傳 500，MQService 收到告警 |
| T06 | Validation Test | 傳入缺少 gtype 的 body | 回傳 422 Validation Error |

---

## 9. 高風險區域

- **高風險依賴**: Redis DB5 是此 API 的唯一資料來源，若 Redis 故障，API 直接不可用
- **快取一致性**: 此 API 完全依賴 Redis 中的即時盤口快照，若上游 crawleragent 寫入延遲，客戶端將顯示過期資料
- **無 Fallback**: 此 API 不支援 Redis miss 時查詢 Cassandra（根據 README 場景定義）
- **批次查詢效能**: 高併發請求可能造成 Redis 連線壓力，需確認連線池設定

---

## 10. 常見錯誤

- ❌ **誤以為此 API 會查詢 Cassandra**: 此 API 僅從 Redis 讀取，不應在任何情境下退查 Cassandra
- ❌ **回傳了不該暴露的內部欄位**: 如 `source`、`handler` 等內部標記，應在 Response DTO 中明確過濾
- ❌ **批次傳入過大 Array**: 需考量 Redis pipeline 或連線池限制，避免一次大量查詢拖垮連線
- ❌ **誤解 gtype 參數**: gtype 需與 Redis key 片段一致（如 SC、BK），並非任意傳入
- ❌ **假設 Redis 保證有資料**: 需總是處理 Redis miss，不應擲出例外導致 500

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | POST /api/tradegames (OpenAPI) |
| Redis 使用 | README.md: 「即時盤口快照查詢（從 Redis 讀取）」|
| Redis DB | README.md: 「Redis DB5（即時盤口快照）」|
| 場景描述 | README.md: 場景 4「批次盤口查詢」|
| 驗證方式 | README.md: 「API Key / 內部服務授權（TCZB Globals）」|
| MQService | README.md: 「MQService: 異常告警推送」|
| 不可回傳欄位 | tradegameservice-detail.md: 「accounts_*.handler 不可回傳」|
| Redis key format | 需人工確認: `redis_provider.py` |