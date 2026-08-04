# 查詢站內信列表

## 1. 場景目的

後台管理員或客服人員依時間區間查詢站內信發送記錄，以便追蹤近期發送給會員的站內信清單。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sport/notifications/sitemails` | 查詢站內信列表，依時間區間過濾 |

---

## 3. 流程總覽

1. 接收查詢請求，讀取 Query 參數 `startTime` 與 `endTime`
2. 由 Controller 轉發至 Service 層
3. Service 層直接透過 Provider 查詢 MySQL `sport.notification_sitemails` 表
4. 依 `SendTime` 欄位進行區間過濾
5. 不符合時間區間（startTime 或 endTime 未提供或為 0）時，可能回傳空集合或全表掃描（須注意 DB 效能）
6. 將查詢結果轉換為 `SportSiteMailDTO` 列表回傳

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `NotificationController.GetSiteMails` | 接收 GET 請求，取出 startTime / endTime 查詢參數 |
| 2 | Service | `ISportNotificationService.GetSiteMails` | 呼叫 Provider 查詢 DB（推測） |
| 3 | Provider | `ISportNotificationProvider.GetSiteMails` | 執行 MySQL 查詢 `notification_sitemails`（推測） |
| 4 | Controller | `NotificationController.GetSiteMails` | 將結果序列化為 JSON 回傳 |

> **註**：目前分析基於 OpenAPI 與 README，Controller / Service / Provider 詳細實作路徑需人工確認實際 code。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `sport.notification_sitemails` | Read | 依 `SendTime` 欄位過濾時間區間，撈取站內信記錄 |
| Redis | `SiteMails_{account}` | 未使用 | 列表查詢通常不讀取 Redis 站內信主旨快取；快取僅用於個人站內信主旨查詢 |

---

## 6. 重要規則

- **查詢參數**：`startTime` 與 `endTime` 型別為 `int64`（bigint 時間戳），預設值 0（OpenAPI 證據）
- **禁止全表掃描**：Service 層應檢查時間區間不得為空（兩個參數皆不可為 0），避免查詢 `notification_sitemails` 全表
- **不可暴露完整內容**：列表查詢回傳資料僅能包含摘要資訊（如 `Account`、`ID`、`Subject`、`SendTime`、`ReadStatus`），**不可**回傳 `Content` 欄位完整內文
- **權限制限**：本 API 需要後台管理驗證，僅 `pricecentermanage` 服務有寫入權限，但查詢時僅讀取 DB
- **StatusCode 限制**：不可回傳已刪除或隱藏的站內信；此表無 `Enabled` 標記，`ReadStatus` 僅表示讀取狀態

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未提供 startTime 或 endTime（值為 0） | 若未實作假設驗證則可能全表掃描，建議應回傳 400 Bad Request |
| 時間區間過大（如跨度超過 90 天） | DB 查詢時間過長，可能 timeout（需人工確認是否有區間上限規則） |
| 資料庫連線失敗或 timeout | 回傳 500 Internal Server Error |
| 管理員權限不足 | 若未通過 ECFramework 驗證則直接拒絕，回傳 401/403 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SITEMAILLIST-01 | API Test | 提供合法 startTime 與 endTime | 回傳 200，Body 為 SportSiteMailDTO 陣列 |
| SITEMAILLIST-02 | API Test | 未提供 startTime（0）與合法 endTime | 需確認是否回傳錯誤或全表；理想應為 400（需人工確認）|
| SITEMAILLIST-03 | API Test | endTime 早於 startTime | 回傳空陣列或 400 |
| SITEMAILLIST-04 | Permission Test | 使用無效或不具管理權限的 token | 回傳 401/403 |
| SITEMAILLIST-05 | Flow Test | 時間區間跨越多日，確認回傳筆數正確 | 回傳筆數與手動查詢 DB 筆數一致 |

---

## 9. 高風險區域

- **高風險 table**：`sport.notification_sitemails` — 此表可能資料量龐大，時間查詢必須使用索引（`SendTime` 是否存在索引需人工確認）
- **高風險 API**：`GET /api/v1/sport/notifications/sitemails` — 若未強制要求 `startTime`、`endTime`，可能觸發全表掃描導致 DB 異常
- **Cache consistency**：列表查詢不涉及 Redis 快取，無一致性風險；但需注意 `SiteMails_{account}` 快取不應影響此 API
- **Transaction**：唯讀查詢，無 Transaction 需求

---

## 10. 常見錯誤

- ❌ **未強制檢查時間參數**：startTime / endTime 未提供時仍查詢 DB，可能造成 performance 問題
- ❌ **回傳完整 Content**：列表查詢錯誤地將站內信內文（`Content`）回傳給前端，導致封包過大且個資洩漏
- ❌ **誤用 Redis 快取**：將個人 `SiteMails_{account}` 快取用於列表查詢，導致資料錯誤
- ❌ **時間格式錯誤**：傳入的 bigint 時間戳為秒而非毫秒，或時區處理錯誤，導致查詢區間偏移

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI：`/api/v1/sport/notifications/sitemails` GET |
| DB | `sport.notification_sitemails` |
| Query Params | OpenAPI：`startTime` (int64, default 0), `endTime` (int64, default 0) |
| 權限 | README：所有 `/api/v1/sport/*` 路徑皆需驗證 ✅ |
| 不可回傳內容 | `sport-detail.md`：列表查詢不可回傳 `Content` 欄位 |