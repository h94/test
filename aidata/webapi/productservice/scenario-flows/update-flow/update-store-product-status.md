# 更新商城商品上下架狀態

## 1. 場景目的

管理員透過後台變更商城商品（`products_store`）的上架或下架狀態，控制商品在前端商城的可見性。流程必須透過專用方法 `UpdateStoreProductStatus` 寫入狀態值，禁止直接對資料庫執行 UPDATE 操作。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| **需人工確認** | **需人工確認** | **對外 API 端點尚未明確，可能隸屬於現有 Store 管理路由或獨立後台端點，須從實際 Controller 程式碼或 API 閘道設定補全。** |

---

## 3. 流程總覽

1. 管理後台發送請求，攜帶商品分類 (`pclass`)、商品 ID (`pid`) 及目標狀態 (`"1"` 上架 / `"0"` 下架)。
2. API 層進行身份驗證，確認呼叫者為後台管理員。
3. 呼叫 `UpdateStoreProductStatus` 方法，禁止直接操作 `products_store` 資料表。
4. 方法內部讀取 `products_store` 確認商品存在。
5. 若目標為上架 (`"1"`)，計算當前商品庫存（透過彙總 `product_store_stock_logs` 的 `quantity` 欄位），驗證庫存大於 0。
6. 更新 `products_store.status` 為目標值，並更新 `lastup_time`。
7. 刪除對應的 Redis 快取 `product:store:{pclass}:{pid}`，確保前台讀取到最新狀態。
8. 回傳操作成功。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | **需人工確認** | 接收請求，進行 JWT 驗證與角色檢查 |
| 2 | Service | **需人工確認** | 呼叫 `UpdateStoreProductStatus` 方法 |
| 3 | Provider | `ProductStoreDataProvider` | 讀取商品紀錄、計算庫存、執行 Cassandra 狀態更新（透過對應的 Cassandra 操作） |
| 4 | Cache Helper | `CacheManager` 或類似元件 | 刪除 Redis key `product:store:{pclass}:{pid}` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `product.products_store` | Read | 確認商品存在、取得當前狀態 |
| DB (Cassandra) | `product.products_store` | Update (方法內) | 寫入 `status` 與 `lastup_time` |
| DB (Cassandra) | `product.product_store_stock_logs` | Read（聚合） | 計算 `SUM(quantity)` 以驗證上架條件（庫存 > 0） |
| Redis | `product:store:{pclass}:{pid}` | Delete | 清除商品快取，確保前台即時反應狀態變更 |

> 無使用 Kafka / Queue。

---

## 6. 重要規則

- **寫入限制**：`products_store.status` 僅能透過 `UpdateStoreProductStatus` 寫入，值限定 `"1"`（上架）或 `"0"`（下架），不可透過一般 SQL 或 Cassandra Driver 直接 UPDATE。  
  _Evidence: `productservice-detail.md` 寫入限制章節。_
- **上架條件**：從下架重新上架時，必須確認 `quantity`（庫存）大於 0。庫存係由 `product_store_stock_logs` 彙總計算，`products_store` 資料表本身無此欄位。  
  _Evidence: `productservice-detail.md` 寫入限制。_
- **權限限制**：僅限後台管理員操作。所有商城商品 API 皆需要驗證，此操作更應限定後台角色。  
  _Evidence: `README.md` 明確指示所有商城 API 需要驗證；後台管理行為應由管理介面觸發。_
- **快取一致性**：狀態更新後必須立即刪除 `product:store:{pclass}:{pid}` 快取，不可只依賴 TTL。  
  _Evidence: `product-detail.md` Redis 段落。_
- **不可修改欄位**：`price`、`originalprice` 不可透過此流程變更，僅能在建立商品時設定。  
- **稽核軌跡**：應記錄更新時間 (`lastup_time`)，方便後續追查。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 指定的 `pclass` + `pid` 不存在 | 回傳 404，錯誤訊息指明商品不存在 |
| 請求來自非管理員或未通過驗證 | 回傳 401 或 403 |
| 目標狀態為 `"1"` 但當前庫存 ≤ 0 | 回傳 422 或 400，明確指出庫存不足無法上架 |
| 傳入非法狀態值（非 `"0"` 或 `"1"`） | 回傳 400，狀態格式錯誤 |
| Cassandra 寫入失敗（timeout / unavailable） | 回傳 500，可提示稍後重試 |
| Redis 刪除失敗 | 不影響主流程回應 200，但需記錄 error log，並可排程異步重試 DEL |
| 同時大量請求上架同商品（race condition） | 僅一個請求成功，其餘應收到樂觀鎖失敗或狀態已變更的提示 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|-----------|
| UPT-01 | Flow Test | 管理員將下架商品（庫存 = 5）上架 | status 變為 "1"，Redis 快取消失，前台可查到商品 |
| UPT-02 | Flow Test | 管理員將上架商品下架 | status 變為 "0"，前台不可見 |
| UPT-03 | Permission Test | 使用一般使用者 Token 呼叫 API | 403 |
| UPT-04 | Validation Test | 嘗試上架庫存為 0 的商品 | 失敗，回傳庫存不足錯誤 |
| UPT-05 | Validation Test | 傳入非法狀態 "2" | 400 |
| UPT-06 | Consistency Test | 更新狀態後直接查詢 Redis key | key 不存在 |

---

## 9. 高風險區域

- **直接 UPDATE**：任何人若繞過 `UpdateStoreProductStatus` 直接修改 Cassandra `status` 欄位，將破壞庫存檢查與快取一致性，屬於高風險違規。須透過資料層封裝與權限控制防範。
- **庫存計算競爭**：上架檢查庫存後到實際寫入 `status` 之間，可能有其他請求扣減庫存，導致最終上架商品實際無庫存。  
  建議採用樂觀鎖（例如比對 `lastup_time` 或增加庫存版本號）或先執行庫存扣減（如同兌換流程），再允許上架。
- **Redis 刪除失敗**：若快取未被清除，使用者將持續看到舊狀態（已下架商品仍顯示上架）。需監控刪除失敗率並實作補償機制（例如在商品查詢時比對狀態）。
- **錯誤的 API 端點設計**：若端點設計不當（例如以 `POST` 代替 `PATCH/PUT`）可能引發誤解或重複執行等冪性問題。

---

## 10. 常見錯誤

- ❌ 直接在程式碼中執行 `UPDATE products_store SET status = ?` 而不透過 `UpdateStoreProductStatus`。  
  ✅ 必須強制使用專用方法，並在 code review 中檢查。
- ❌ 上架前忘記確認庫存，或誤以為 `products_store` 有 `quantity` 欄位。  
  ✅ 庫存由 `product_store_stock_logs` 彙總計算。
- ❌ 狀態更新後未清除 Redis 快取，導致前台顯示不一致。  
  ✅ 更新後立即執行 `DEL`，或使用 publish/subscribe 通知其他服務清除。
- ❌ 未驗證呼叫者角色，導致一般使用者可操作。  
  ✅ 須於 Controller 層級加上 `[Authorize(Roles = "Admin")]` 或同等驗證。
- ❌ 忘記更新 `lastup_time`，影響後續稽核與同步。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | **需人工確認**（OpenAPI 中未直接列出此端點） |
| DB（主表） | `product.products_store` (Schema: product.md, Code: ProductStoreDataProvider) |
| DB（庫存計算） | `product.product_store_stock_logs` (Schema: product.md) |
| 寫入限制 | `productservice-detail.md` – 「products_store.status：僅可透過 UpdateStoreProductStatus 方法寫入」 |
| 業務規則 | `productservice-detail.md` – 「下架後若要重新上架，需確認 quantity 大於 0」 |
| 快取 | `product-detail.md` Redis 段落 – `product:store:{pclass}:{pid}` 狀態變更須主動 DEL |
| 常見錯誤 | `product-detail.md` 常見錯誤 – 「直接 UPDATE products_store.status」為錯誤示範 |