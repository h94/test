# 列出監控玩法設定

## 1. 場景目的

查詢賠率異常監控系統中已設定的監控玩法清單，支援取得全部球種設定，或依指定球種代碼 (`game_type`) 查詢單一設定。此 API 供後台管理人員查閱當前啓用的監控玩法，不涉及資料異動。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/monitored_play_modes` | 列出監控玩法設定，可選擇性提供 `game_type` 查詢參數。 |

OpenAPI 定義 (tags: monitored_play_modes, operationId: list_monitored_play_modes_api_monitored_play_modes_get)  
範例：`GET /alertbackendservice/api/monitored_play_modes?game_type=soccer`

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，可選附帶 `game_type` 查詢參數。
2. FastAPI 將請求路由至對應的 Resource 層 controller。
3. Controller 調用 Service 層取得資料。
4. Service 調用 Provider 層查詢資料庫 `monitored_play_modes` 表。
5. 若帶有 `game_type`，則查詢該球種單筆記錄；若無則查詢全部記錄。
6. 將查詢結果（含 `game_type`、`play_mode`、`operator_account`、`created_at`、`updated_at`）轉為 JSON 回傳。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `MonitoredPlayModesResource.get` (推測) | 接收 query param `game_type`，呼叫 Service |
| 2 | Service | `MonitoredPlayModesService.list_modes` (推測) | 呼叫 Provider 對應查詢方法 |
| 3 | Provider | `MonitoredPlayModesProvider.list_all(game_type=None)` | 對 `monitored_play_modes` 表執行 SELECT，依 `game_type` 篩選（若有） |

（層級命名基於專案結構：Resources/, Service/, Provider/；實際 method 名稱可能為 `list_all`，來源見下文 evidence）

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `monitored_play_modes` | Read (SELECT) | 取得監控玩法設定 |
| Redis | 無 | 不適用 | 本場景未使用快取 |
| Queue | 無 | 不適用 | 本場景僅查詢，無訊息生產或消費 |

---

## 6. 重要規則

- **權限限制**：需人工確認。OpenAPI 未顯示安全定義，可能需後台管理員權限，或為內部使用不限制。
- **欄位限制**：無。查詢不涉及過濾隱藏欄位，回傳所有欄位。
- **不可暴露資料**：`operator_account` 欄位會回傳，若帳號機敏需確認是否允許顯示。
- **TTL 規則**：不適用。
- **Transaction 規則**：查詢操作無須 transaction。
- **Retry 規則**：不適用。
- **狀態值限制**：無。
- **不可修改欄位**：此場景僅讀取，無法修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 無任何監控玩法設定 | 回傳空陣列 `[]`。（需人工確認） |
| 指定不存在的 `game_type` | 回傳空陣列或 `404 Not Found`。（需人工確認目前實作行為） |
| 缺少必要權限 | 回傳 `401` 或 `403`。 |
| DB 連線失敗 | 回傳 `500 Internal Server Error`，並記錄錯誤。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| FT-01 | API Test | 不帶參數呼叫 GET `/api/monitored_play_modes` | 回傳全部球種設定清單，status 200 |
| FT-02 | API Test | 帶有效 `game_type` (如 `soccer`) 呼叫 | 回傳該球種之設定，status 200 |
| FT-03 | API Test | 帶不存在的 `game_type` (如 `invalid`) | 回傳空陣列或 `404`，status 對應結果 |
| FT-04 | Schema Test | 驗證回傳 JSON 結構 | 包含 `game_type`, `play_mode`, `operator_account`, `created_at`, `updated_at` |
| FT-05 | Permission Test | 無有效身份驗證請求 | 回傳 `401` 或 `403` |

---

## 9. 高風險區域

（本場景為單純查詢，無高風險操作）

- 資料表 `monitored_play_modes` 變更頻率低，查詢負載輕微。
- 若未來新增快取，需注意快取一致性。

---

## 10. 常見錯誤

- 誤以 POST 方式呼叫（正確使用 GET）。
- 誤解 `game_type` 大小寫敏感度；應與資料庫儲存一致（通常為小寫，見 alerts 表 `game_type` 欄位說明）。
- 將 `play_mode` 欄位（JSONB）當成字串處理，前端需正確解析。
- 忽略空陣列回應，誤認為錯誤。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 定義 | OpenAPI (`/api/monitored_play_modes` GET) |
| DB 表格 | `monitored_play_modes` 定義於 `migrations/001_create_core_tables.sql` |
| DB 欄位語意 | `monitored_play_modes` 欄位說明來自 Semantics (phase1 batch-2) |
| Provider 查詢 | `monitored_play_modes.py:list_all` 方法語意 (Semantics batch-3) |
| 無 Cache/Queue 使用 | README 及相關 source semantics 未提及此場景使用 Redis/Kafka |