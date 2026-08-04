# 查詢活動商品清單

## 1. 場景目的

提供已驗證使用者查詢指定站台（site）與活動事件（activityEvent）下所有販售中（status=1）的活動商品，支援是否使用快取的參數，以加速前端展示。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/activity/products/{site}/{activityEvent}` | 取得活動商品清單，需要驗證，支援 cache 查詢參數（boolean，預設 true） |

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，解析路徑參數 `site`、`activityEvent` 及查詢參數 `cache`。
2. 執行 ECCore 內建驗證（須帶有效 Token），確認使用者已登入。
3. 若 `cache=true`，優先從記憶體快取（或 Redis？）讀取鍵為 `product:activity:{site}:{activityEvent}` 的資料；若有資料則直接回傳。
4. 若無快取或 `cache=false`，調用 Service 層向 Cassandra 的 `products_activity` 表進行查詢。
5. 查詢條件：`WHERE site = {site} AND activityevent = {activityEvent}`，並過濾 `status = 1`（販售中）。
6. 將查詢結果中的多語言欄位 `names` 依請求的 `Accept-Language` 進行取值；若無對應語系則 fallback 預設語系（如 `en`）。
7. 可將結果寫入快取（若 cache 啟用），依設定 TTL（可能 10 秒）儲存。
8. 回傳商品陣列，包含 `id`、`names`、`price`、`quantity`、`status`（固定為 1）、`updatetime` 等（依 OpenAPI schema `ActivityProduct`）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method（推測） | 動作 |
|------|-------|------------------------|------|
| 1 | Controller | `ActivityController.GetProducts` | 接收參數，轉呼叫 Service |
| 2 | Service | `IActivityService.GetActivityProducts` | 檢查快取，若無則呼叫 Provider |
| 3 | Provider | `IActivityDataProvider.QueryProducts` | 執行 Cassandra 查詢：`SELECT * FROM products_activity WHERE site=? AND activityevent=?` |
| 4 | Transfer | `ActivityProductDTO` / `Map` | 將結果依語言處理 `names`，移除內部不必要欄位 |
| 5 | Cache | `IMemoryCache`（如 MemoryCache） 或 Redis（需確認） | 根據 `cache` 參數讀寫，key 可能為 `activity:products:{site}:{activityEvent}` |

> **需人工確認**：實際 Class 名稱與快取機制（Redis vs MemoryCache），目前以一般架構推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `products_activity`（keyspace 待確認：`product` 或 `payment`） | Read（SELECT） | 取得指定活動、狀態為 1 的商品 |
| Cache | 記憶體快取（可能為 `IMemoryCache`），或 Redis（若有的話） | Read / Write | 減輕 DB 讀取壓力，加速回應 |
| Queue | 無使用 | - | - |

> **需人工確認**：實際使用的 keyspace（product / payment）與快取儲存後端。

---

## 6. 重要規則

- **權限限制**：此 API 需要驗證（ECCore Token），一般使用者皆可呼叫；無特定角色限制。
- **欄位限制**：只回傳 `status = 1` 的商品；`status = 0`（暫停）或 `2`（售完）不可回傳。
- **不可暴露資料**：無直接敏感欄位，但 `names` 應僅回傳對應語系的值，不可回傳整個 map。
- **TTL 規則**：若使用快取，TTL 通常為 10 秒（依其他服務的活動快取慣例），活動結束後可適度延長；快取需在商品狀態變更時主動清除。
- **Transaction 規則**：本查詢為唯讀，無需 transaction。
- **Retry 規則**：無。
- **狀態值限制**：status 欄位僅可為 0,1,2，查詢時固定 `status=1`。
- **不可修改欄位**：此 API 為 GET，不涉及寫入。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未帶有效 Token 或 Token 過期 | HTTP 401 Unauthorized |
| site 或 activityEvent 不存在 | 回傳空陣列 `[]` |
| DB 查詢逾時或拋出例外 | HTTP 500 Internal Server Error（或依全域例外處理） |
| 快取服務（如 Redis）無法連線 | 應降級為直接查詢 DB，不影響回應（但不更新快取） |
| 語言代碼無對應的 `names` 內容 | 回傳預設語言（如 `en`）的名稱 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | API Test | 帶有效 Token，site=zh-tw, activityevent=event1 | 回傳 200，body 為商品陣列，所有商品 status=1 |
| T2 | API Test | 不帶 Token | 回傳 401 |
| T3 | Flow Test | 第一次查詢無快取，第二次查詢（cache=true） | 第二次應從快取回應，Cassandra 無查詢記錄 |
| T4 | Flow Test | 商品狀態為 0 或 2 | 不回傳在列表中 |
| T5 | API Test | 帶 `cache=false` | 每次皆查詢 DB，不使用快取 |
| T6 | Permission Test | 使用已停用帳號的 Token（Enabled=0） | 回傳 401（由驗證機制攔截） |
| T7 | API Test | 指定 Accept-Language: zh-CN，商品 names 只有 en | 回傳的名稱應為 en 的內容 |

---

## 9. 高風險區域

- **高風險 table**：`products_activity`（尤其是 `payment.products_activity` 與 `product.products_activity` 雙重存在的潛在一致性问题），需確認讀寫哪一個 keyspace。
- **高風險 API**：本 API 因讀取量大，若無有效快取可能造成 Cassandra 壓力。
- **跨服務資料同步**：活動商品狀態可能由其他服務（如 paymentservice）變更，快取不一致可能導致回傳已下架商品。
- **Cache consistency**：若使用記憶體快取，多執行緒或多 Pod 環境下快取可能不一致；需仰賴短 TTL 或分散式快取。
- **Idempotency**：本 API 為 GET，無需處理。

---

## 10. 常見錯誤

- **新人容易犯錯**：忽略 `status=1` 過濾，直接將所有狀態商品回傳給前端；未處理多語言名稱，直接回傳整個 `names` map。
- **AI 容易誤解**：可能誤認為 productservice 直接使用 Redis（實際文件顯示 Redis 段落為空）；可能誤判使用 `payment.products_activity` 或 `product.products_activity`，但沒有明確規則。
- **常見漏檢查項目**：未驗證快取參數 `cache` 的實際作用，可能直接忽略造成效能問題；未處理 `quantity` 欄位（雖然此處僅查詢不需判斷庫存 >0，但前台常需展示剩餘數量，需確認是否過濾 quantity>0）。
- **常見錯誤流程**：在未加 `site` 與 `activityevent` WHERE 條件下全表掃描，Cassandra 會非常耗時。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI: `GET /api/v1/activity/products/{site}/{activityEvent}` |
| DB 讀取規則 | productservice-detail.md: payment - 讀取規則（products_activity）；product - 讀取規則（products_activity） |
| 快取推測 | product-detail.md: Redis - `product:activity:{site}:{activityevent}`（由 inplayzsubscriptionsystem 執行，但 productservice 可能複用相同 pattern） |
| 驗證需求 | README.md: API 路由表中該 API 標示「需要驗證 ✅」 |
| 狀態定義 | AppDefine.cs / semantics: status 值 0=暫停、1=販售中、2=售完 |
| 多語言處理 | productservice-detail.md: 不可回傳整個 map，須依語言取值 |
| 快取可能性 | OpenAPI query 參數 `cache` 預設 true，暗示內部有快取邏輯 |

> 部分資訊（如 keyspace 實際使用、快取後端實作、服務層具體類別）需人工補充確認。