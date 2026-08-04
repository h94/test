# 場景：建立商城庫存異動紀錄

## 1. 場景目的

為特定商城商品 (`pclass`+`pid`) 建立一筆庫存異動紀錄 (`product_store_stock_logs`)。此動作用於記錄補庫 (正數) 或扣庫 (負數) 的數量，是庫存管理的核心流程。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/store/productstocklogs` | 新增商品庫存紀錄 |
> **Evidence**: README.md

---

## 3. 流程總覽

1. 客戶端以 `POST` 請求呼叫此 API。
2. Controller 接收請求，驗證呼叫者是否具有有效驗證 (需登入)。
3. 檢查請求內 `pclass`, `pid`, `quantity` 等必要欄位是否提供且有效。
4. 呼叫 Service 層處理業務邏輯，決定庫存異動類型 (補庫/扣庫)。
5. Service 呼叫 Data Provider (`ProductStoreDataProvider`)，執行對 `product.product_store_stock_logs` 表的 INSERT 操作。
6. Cassandra 寫入成功後，回傳成功響應。
7. 若 Cassandra 寫入失敗，回傳伺服器錯誤。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `StoreController.AddProductStockLog` | 接收 `ProductStoreStockLog` 請求體，轉發至 Service。 |
| 2 | Service | `ProductStoreService.AddStockLog` | 驗證資料，建立 `ProductStoreStockLog` 物件，設定 `Addtime` 與 `Updatetime`。 |
| 3 | Provider | `ProductStoreDataProvider.AddStockLog` | 對 Cassandra `product.product_store_stock_logs` 執行 INSERT 操作。 |
> **Evidence**: 從 `productservice-detail.md` 歸納 Controller/Service/Provider 責任。`ProductStoreDataProvider` 由 `product-detail.md` 的語意分析推得。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `product.product_store_stock_logs` | Write (INSERT) | 新增一條庫存異動記錄。 |
> **Evidence**: `product-detail.md`, `README.md`, `db/product.md`

---

## 6. 重要規則

- **權限限制**：呼叫此 API 必須通過驗證。
  > **Evidence**: README.md 中 API 列表標記 `需要驗證`。
- **欄位限制**：
  - `quantity` 為整數，可為正 (補庫) 或負 (扣庫)。
  - `pclass` 和 `pid` 為組合分區鍵，必須與 `products_store` 中的既有商品對應，寫入後不可變更。
  > **Evidence**: `product-detail.md` 寫入限制章節。
- **不可後續修改**：庫存異動記錄一經寫入，即為不可變更的歷史數據。
  > **Evidence**: Schema 顯示 `PRIMARY KEY (pclass, pid, addtime, id)`，無 UPDATE 語意，且 `product-detail.md` 提到庫存量由 sum(log) 計算得出。
- **TTL 規則**：無 TTL，庫存記錄持久保存。
- **Retry 規則**：`product-detail.md` 未定義 Retry，需人工確認。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求缺少必要欄位 (`pclass`, `pid`, `quantity`) | 400 Bad Request |
| 請求未經驗證或 Token 無效 | 401 Unauthorized |
| Cassandra 寫入失敗 | 500 伺服器錯誤 |
> **Evidence**: ASP.NET Core 標準驗證流程及一般 API 設計慣例。

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| STOCK-API-01 | API Test | 以合法參數呼叫 API | 200 OK，`product_store_stock_logs` 新增一筆記錄。 |
| STOCK-API-02 | API Test | 缺少必填欄位 (`pclass`) 呼叫 API | 400 Bad Request (若於 Controller 端驗證)。 |
| STOCK-API-03 | Permission Test | 未帶有效 Token 呼叫 API | 401 Unauthorized。 |
| STOCK-FLOW-01 | Flow Test | 連續寫入扣庫紀錄後，檢查對應商品的計算庫存 | 計算庫存量應等於 `products_store.quantity` (若存在) 加上所有 `stock_logs.quantity` 之總和。 |
> **Evidence**: `product-detail.md` 寫入限制章節提到「庫存異動應寫入 `product_store_stock_logs` 並透過 sum(log) 計算當前庫存」。

---

## 9. 高風險區域

- **高風險 API**：若此 API 無嚴格的內部調用限制，可能被外部隨意呼叫導致庫存記錄混亂。
- **異動順序**：Cassandra 的 `addtime` 作為 Clustering Key 的一部分，需確保時間戳的準確性與順序性，以免影響庫存計算的歷史紀錄準確性。
- **Idempotency (冪等性)**：此 API 本身不具冪等性，重複呼叫會產生多筆記錄。需由上游調用方控管。
- **需人工確認**：扣庫行為發生時，服務端是否有對 `products_store` 的現有庫存進行檢查並阻止使計算庫存變為負數的扣庫？`product-detail.md` 中提到「由服務端程式檢查，DB 無 CHECK」，但具體在哪個 Layer 實現需從 Controller/Service 代碼確認，此處暫無相關 evidence。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 誤認為此 API 會直接修改 `products_store` 表的 `quantity` 欄位。實際上本服務僅寫入 log，庫存量是透過彙總 log 計算的。
    > **Evidence**: `product-detail.md` 常見錯誤章節。
  - 沒有以 `pclass` 和 `pid` 作為查詢條件 (`WHERE`)，試圖全表掃描庫存記錄。
    > **Evidence**: `product-detail.md` 讀取規則章節。
- **AI 容易誤解**：
  - 認為可以對此記錄進行 UPDATE 或 DELETE，實際上應為 append-only。
  - 忽略 `pid` 和 `pclass` 是 `products_store` 的外鍵關係，誤允許寫入不存在的商品 ID。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | 由 `README.md` 及 Scenarios 描述推得。 |
| DB | `db/product.md` 中 `product_store_stock_logs` 的定義。 |
| DB Rules | `product-detail.md` 中對 `product_store_stock_logs` 的寫入限制與讀取規則。 |
| Code Semantics | Phase1 的 `product_store_stock_logs` 語意分析，確認 `ProductStoreDataProvider` 責任。 |