# 查詢活動商品

## 1. 場景目的

提供前台（用戶端）一個不需要登入（不需 authKey）的 GET API，以指定的 `site` 與 `activityEvent` 查出目前可參與兌換的活動商品清單，只顯示已上架且有庫存的商品。此流程確保前端只取得有意義的活動商品，避免暴露下架、售完或未啟用的資料。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/activity/products/{site}/{activityEvent}` | 依指定站點與活動事件名稱查詢活動商品，無需登入 |

---

## 3. 流程總覽

1. 接收 GET request，從路徑參數取得 `site` 與 `activityEvent`
2. Controller 呼叫 `ActivityService.GetActivityProducts(site, activityEvent)`
3. Service 呼叫 `IActivityDataProvider` 查詢 DB
4. 查詢 `payment.products_activity` 或 `product.products_activity`（由 Provider 實作決定）
5. 查詢條件：`WHERE site=? AND activityevent=? AND status=1 AND quantity>0`
6. 讀取結果，若無資料則回傳空陣列 `[]`
7. Service 將結果轉換為 `ActivityProductDTO` 回傳（對外不回傳 `status` 數值）
8. 回傳 JSON array 至前端

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `ActivityController.GetProducts` | 接收 GET 請求，帶入 site, activityEvent |
| 2 | Service | `ActivityService.GetActivityProducts` | 組裝查詢條件，呼叫 Provider |
| 3 | Provider | `ActivityDataProvider.GetSiteActivityEventProducts` | 讀取 DB，過濾 status=1, quantity>0 |
| 4 | Transfer | `ActivityService.GetActivityProducts` | 將讀取結果對應成 `ActivityProductDTO` 列表 |
| 5 | Controller | `ActivityController.GetProducts` | 回傳 `ActionResult<IEnumerable<ActivityProductDTO>>` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.products_activity` 或 `product.products_activity` | Read | 查詢 site + activityevent 下的有效商品 |
| Cache | 無 | — | 此 API 目前無使用 Redis 快取（需人工確認是否需加入） |
| Queue | 無 | — | — |

---

## 6. 重要規則

- **權限限制**：此 API 為公開接口，不需要 `authKey` Token，任何未登入使用者皆可呼叫。
- **過濾規則（關鍵）**：查詢時必須滿足以下所有條件才能回傳：
  - `status=1`（販售中 / 上架）
  - `quantity > 0`（庫存大於 0）
  - 不得回傳 `status=0`（暫停）、`status=2`（售完）的商品。
- **不可暴露 `status` 原始值**：對外回傳的 DTO 不應包含內部狀態代碼（如 0/1/2），只應透過商品是否存在於列表中來隱含其販售中狀態。
- **不可回傳內部管理欄位**：`updatetime` 等維護時間戳不可回傳給前台。
- **分區查詢限制**：由於 `products_activity` 的 Partition Key 是 `site`，所有查詢必須帶入 `site`，不可跨站點查詢。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 該 site / activityEvent 下沒有任何活動商品 | 回傳 HTTP 200，body 為空陣列 `[]` |
| 該 site / activityEvent 下商品皆已下架（status=0）或售完（status=2，quantity=0） | 回傳 HTTP 200，body 為空陣列 `[]` |
| `site` 或 `activityEvent` 未提供或為空 | 依 ASP.NET Core routing 回傳 404 Not Found（路徑不匹配） |
| 資料庫查詢 timeout | 回傳 HTTP 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| IT-PROD-01 | API Test | 傳入有販售中且有庫存商品的 site + activityEvent | 回傳非空陣列，且所有商品 status=1, quantity>0 |
| IT-PROD-02 | API Test | 傳入只有下架或售完商品的 site + activityEvent | 回傳空陣列 `[]` |
| IT-PROD-03 | API Test | 傳入不存在的 activityEvent | 回傳空陣列 `[]` |
| IT-PROD-04 | Permission Test | 未帶 authKey token 發送請求 | 可成功取得資料（公開 API） |
| IT-PROD-05 | Flow Test | 後台將商品 quantity 改為 0（售完）後，前台查詢 | 該商品不再出現於回傳列表中 |

---

## 9. 高風險區域

- **跨服務 table 重複**：`products_activity` 同時存在於 Cassandra 的 `payment` 與 `product` keyspace。若 Provider 實作時連接錯誤的 keyspace 或資料未同步，將導致前台顯示不一致。**需人工確認 `pricecentersite` 實際讀取哪一個 keyspace**。
- **庫存即時性**：若後台修改 `quantity` 或 `status` 後前台查詢結果未即時更新，可能是 Cassandra 一致性設定（如 `read_repair = 'BLOCKING'`）或未有快取失效機制導致。此 API 目前無 Redis cache，風險較低，但仍需留意。
- **無分頁機制**：若單一活動商品數量極多（如超過 1000 個），可能導致 API response 過大。**需人工確認是否有分頁需求或既有上限。**

---

## 10. 常見錯誤

- ❌ 查詢商品時未過濾 `quantity > 0`，前端顯示已售完商品。
- ❌ 查詢商品時使用 `status=0` 或未過濾 `status`，回傳下架商品。
- ❌ 回傳時直接揭露 `products_activity.status`（int）給前端，而非僅依賴列表存在與否。
- ❌ Provider 實作誤從 `payment.products_activity` 與 `product.products_activity` 混用未區分，導致兩個 keyspace 資料不一致時出現幽靈商品或商品遺失。（**需人工確認提供者實作**）

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `ActivityController.GetProducts` （推測） |
| DB | `payment.products_activity` 或 `product.products_activity` |
| Code | `ActivityService.GetActivityProducts` （推測） |
| DB Rule | `products_activity` 須 WHERE `status=1` 且 `quantity > 0` |
| DB Detail | `db/payment-detail.md` 或 `db/product-detail.md` |
| OpenAPI | `GET /api/activity/products/{site}/{activityEvent}` |