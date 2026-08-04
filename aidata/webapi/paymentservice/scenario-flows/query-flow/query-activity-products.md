# 查詢活動商品

## 1. 場景目的

前台會員瀏覽活動頁面時，取得指定活動、站台下所有「可兌換」的商品（販售中且有庫存），供前端呈現商品列表、價格與庫存。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/activity/products/{site}/{activityEvent}` | 查詢活動商品，支援快取控制 |

**Query Parameter**：
- `cache` (boolean, default true)：是否優先讀取 Redis 快取。

---

## 3. 流程總覽

1. API Gateway/ECFramework 驗證會話，確認登入狀態。
2. Controller 解析路徑參數 `site`、`activityEvent` 及 query `cache`。
3. 若 `cache=true`：嘗試從 Redis key `SportCache:Activity_{site}_{activityEvent}_Products` 取得序列化商品列表。
4. 若快取命中且未過期，直接回傳結果；否則進入 DB 查詢。
5. 查詢 `payment.products_activity`，條件：`site = :site AND activityevent = :activityEvent`。
6. 僅回傳 `status = 1`（販售中）且 `quantity > 0` 的紀錄。
7. `names` 欄位僅依請求語言（Accept-Language 或站台預設）回傳單一字串，不回傳完整 map。
8. 將結果序列化寫入 Redis 快取（TTL 為活動剩餘時間或固定值，需人工確認）。
9. 回傳商品列表（JSON）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ActivityController.GetActivityProducts(site, activityEvent, cache)` | 接收請求，呼叫 Service |
| 2 | Service | `IActivityService.GetProducts(...)` | 判斷快取開關，執行查詢邏輯 |
| 3 | Service | 若 `cache=true`，呼叫 `CacheProvider.GetAsync(key)` | 讀取 Redis 快取 |
| 4 | Service | 若沒命中，呼叫 `IActivityDataProvider.GetSiteActivityEventProducts(site, activityEvent)` | 查詢 Cassandra |
| 5 | Provider | 執行 CQL `SELECT * FROM payment.products_activity WHERE site=? AND activityevent=?` | 取得所有活動商品 |
| 6 | Service | 過濾：`status == 1 && quantity > 0` | 只保留可兌換商品 |
| 7 | Service | 處理 `names` map，提取對應語言名稱 | 避免回傳全部語系 |
| 8 | Service | 若有寫入 Redis 條件，`CacheProvider.SetAsync(key, data, ttl)` | 更新快取 |
| 9 | Controller | 回傳 `ActionResult<IEnumerable<ActivityProduct>>` | — |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Cassandra | `payment.products_activity` | Read | 查詢活動下所有商品 |
| Redis | `SportCache:Activity_{site}_{activityEvent}_Products` | Read / Write | 快取可兌換商品列表，降低 DB 負載 |

---

## 6. 重要規則

- **權限限制**：API 需要會員登入（驗證 token），但所有已登入會員皆可查詢。
- **狀態過濾**：僅回傳 `status = 1`（販售中）且 `quantity > 0` 的商品；後台暫停、售完商品不可見。
- **多國語系**：`names` map 不可直接暴露，依請求語言（或站台預設）回傳單一 value。
- **不可暴露欄位**：不可回傳 `updatetime`（內部用途）；`names` 只回傳對應語言。
- **快取 TTL**：應設為活動剩餘時間，但目前實作可能依賴手動清除，需人工確認。
- **不可修改欄位**：此 API 為唯讀查詢，商品價格、庫存、狀態皆由管理後台或兌換流程維護。
- **一致性**：商品狀態變更（下架、售完）或庫存歸零時，必須主動 `DEL` 對應 Redis 快取，不可僅依靠 TTL。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 會員未登入 | 回傳 401 未授權 |
| `site` 或 `activityEvent` 不存在 | 回傳空陣列 `[]` |
| Cassandra 讀取逾時 | 回傳 500，並記錄錯誤；若 Redis 有過期快取則可考慮降級回傳舊資料（需人工確認） |
| Redis 連線失敗且 `cache=true` | 應降級為直接查詢 DB（不影響可用性），並忽略快取寫入 |
| 所有商品皆為 `status≠1` 或 `quantity=0` | 回傳空陣列 |
| 快取中資料不符合過濾條件（如仍包含下架商品） | 表示快取未正確失效；應在流程中雙重驗證，最終依 DB 結果回傳，並自動更新快取 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| AT-01 | API Test | 提供有效的 `site` 與 `activityEvent`，且有商品庫存 | 回傳 200，陣列包含符合條件商品 |
| AT-02 | API Test | 提供無效的活動代碼 | 回傳 200，空陣列 |
| AT-03 | Permission Test | 未帶 Token 請求 | 回傳 401 |
| AT-04 | Flow Test | 第一次請求 (`cache=true`) 後，手動刪除 Redis key 再次請求 | 第二次請求應重新查詢 DB 並重新寫入快取 |
| AT-05 | Flow Test | 管理後台將商品狀態改為暫停後，前台呼叫 API | Redis 應先被清除，回傳結果不含該商品 |
| AT-06 | Cache Test | Redis 服務停止，`cache=true` 請求 | 應正常降級查 DB，不報錯 |
| AT-07 | Data Validation | 驗證回傳的 `name` 是否為請求語系（如 zh-TW） | 不可包含完整 map |

---

## 9. 高風險區域

- **快取一致性**：商品下架或庫存歸零時，若未立即清除 Redis，前台會持續顯示已售完商品。需確保管理後台寫入 DB 後觸發 cache invalidation。
- **Redis 降級策略**：Redis 失效時應自動降級查 DB，但需注意 DB 壓力（可考慮短期快取 fallback）。
- **語言映射錯誤**：若請求語系在 `names` map 中不存在，需定義 fallback 語系 (如 en 或 tw)；不可回傳 null。
- **參數驗證**：`site` 與 `activityEvent` 應防止 SQL/NoSQL injection（利用參數化查詢）。

---

## 10. 常見錯誤

- ❌ 回傳所有 `payment.products_activity` 資料，未過濾 `status` 和 `quantity`。
- ❌ 在快取中直接儲存 DB 原始 `names` map，前端取得後再自行選取語言（應由後端處理）。
- ❌ 未考慮 Redis 當機的 fallback，導致整個查詢失敗。
- ❌ 忘記在商品狀態變更 API 中清除對應 Redis 快取。
- ❌ 直接使用 `SELECT *` 並回傳所有欄位（包含 `updatetime`、內部管理欄位）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI `GET /api/v1/activity/products/{site}/{activityEvent}` |
| DB 查詢條件 | `payment-detail.md`：活動商品讀取規則 `status=啟用(1) AND quantity>0` |
| Redis 快取 | `paymentservice-detail.md`：Redis 章節 `SportCache:Activity_{site}_{activityEvent}_Products` |
| 過濾規則 | DB schema `products_activity.status` 定義 (0:暫停,1:販售中,2:售完) |
| 多語系處理 | `paymentservice-detail.md`：不可回傳欄位 `products_activity.names` 對外 API 應僅回傳對應語言值 |
| 權限 | README 中 API 清單該路由標示需要驗證 ✅ |