# 取得足球聯盟ID清單

## 1. 場景目的

提供足球（SC）所有聯盟的 ID 與名稱清單，供前端 `/api/check-team/teams/SC?lid= ` 進行聯盟篩選時使用。此 API 僅負責讀取並回傳聯盟基礎資料，不涉及任何帳號驗證或寫入操作。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | /api/check-team/sc-league-ids | 回傳足球所有聯盟 ID 與名稱 |

---

## 3. 流程總覽

1. 接收 GET 請求，無需任何 request body 或 query parameter
2. 查詢 Cassandra `pricecenter` keyspace 的 `leagues_SC` 表，擷取所有聯盟的 `id` 與 `lname`
3. 若查詢成功，將結果組裝為 JSON 陣列回傳；若查詢失敗，回傳錯誤

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | CheckTeamController.sc_league_ids | 接收 GET 請求，無參數驗證 |
| 2 | Service | CheckTeamService.get_sc_leagues | 調用 Provider 層查詢 Cassandra |
| 3 | Provider | GamesProvider.get_all_leagues | 執行 CQL：`SELECT id, lname FROM pricecenter.leagues_SC` |
| 4 | Provider | GamesProvider.get_all_leagues | 將 Cassandra Row 物件轉換為 DTO list |
| 5 | Controller | CheckTeamController.sc_league_ids | 組裝 JSON 陣列 `[{id, name}, ...]` 回傳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | pricecenter.leagues_SC | Read | 查詢所有聯盟的 id 與 lname 欄位 |

> 此場景無 Redis / Kafka / Queue 操作。

---

## 6. 重要規則

- **無權限限制**：此為公開查詢 API，不需任何驗證（無 auth token、無 session 檢查）
- **不可回傳欄位**：僅回傳 `id` 與 `lname`，不應回傳 `name_map` 或其他內部欄位
- **讀取限制**：限定查詢 `leagues_SC` 表，不可跨球種查詢其他 `leagues_*` 表
- **無 TTL 規則**：此場景無暫存或過期機制
- **無 Transaction 規則**：單一讀取操作，不涉及多表事務
- **無 Retry 規則**：由 Cassandra driver 內建重試機制處理，應用層無額外 retry 邏輯

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| Cassandra 連線失敗 | 回傳 HTTP 500 或 503，回應內部錯誤訊息 |
| `leagues_SC` 表不存在 | Cassandra driver 拋出 InvalidQueryException，回傳 HTTP 500 |
| 查詢 timeout | Cassandra driver 拋出 OperationTimedOutException，回傳 HTTP 500 |
| `leagues_SC` 為空表 | 回傳 HTTP 200 與空陣列 `[]` |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| CT-001 | API Test | 正常呼叫，資料庫含多筆聯盟 | HTTP 200，回傳非空陣列，每筆含 `id` 與 `name` |
| CT-002 | API Test | 正常呼叫，資料庫無聯盟資料 | HTTP 200，回傳空陣列 `[]` |
| CT-003 | API Test | Cassandra 不可用 | HTTP 500，錯誤訊息不含敏感資料 |
| CT-004 | Flow Test | 確認回傳格式符合前端使用 `teams/SC?lid=` | 回傳的 `id` 可作為 `lid` query param 的值 |
| CT-005 | Permission Test | 無 auth header 呼叫 | HTTP 200（無需驗證） |

---

## 9. 高風險區域

- **無高風險 table**：`leagues_SC` 為只讀查詢，無寫入或狀態變更風險
- **無高風險 API**：此端點為純查詢，無副作用
- **無跨服務資料同步**：此場景僅查詢 Cassandra 單表，不涉及跨服務同步
- **無 Transaction**：單一讀取操作，不需分散式事務
- **無 Cache consistency 問題**：未使用快取，每次查詢均為即時資料
- **無 Queue / Idempotency 問題**：無訊息隊列操作

---

## 10. 常見錯誤

- ❌ 誤以為需要 auth token → ✅ 此端點為公開 API，不需身份驗證
- ❌ 誤回傳 `name_map` 或其他內部欄位 → ✅ 僅回傳 `id` 與 `lname` 兩個欄位
- ❌ 誤將 `leagues_BK` 或其他球種的聯盟資料混入回傳 → ✅ 僅查詢 `leagues_SC` 表，不可跨表查詢
- ❌ 預期有 Redis 快取機制 → ✅ 此場景無快取，每次呼叫皆直接查詢 Cassandra（可接受，因聯盟清單變動頻率低且資料量小）
- ❌ 認為空表會回傳錯誤 → ✅ 空表應正常回傳空陣列 `[]`，非錯誤回應

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `openclawservice/README.md` — 路由表：`GET /api/check-team/sc-league-ids` |
| DB | 原始碼語意分析 Phase0/1 — `leagues_SC` 表，欄位：`id`, `lname`, `name_map` |
| DB Keyspace | 原始碼語意分析 — `pricecenter` keyspace |
| Provider | 原始碼語意分析 — `project/Provider/games.py` 定義 `leagues_SC` 表結構 |
| 無 Redis | `openclawservice-detail.md` — 本服務未在 code 中發現 Redis 操作（與此查詢場景相關） |
| 無權驗 | `README.md` — 該 API 目的為「供 teams/SC?lid= 使用」，無提及驗證需求 |