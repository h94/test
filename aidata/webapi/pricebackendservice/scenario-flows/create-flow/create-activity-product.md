# 建立活動商品

## 1. 場景目的

後台管理員為指定網站 (`site`) 與活動 (`activityEvent`) 建立可兌換的商品，包含設定商品名稱、點數價格與庫存數量。此為活動商品生命週期的起點，建立後商品預設狀態為「暫停（未發布）」，需後續透過更新 API 發布上架。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/activity/{site}/{activityEvent}/products` | 建立活動商品 |

**來源**：OpenAPI `Activity` 標籤

---

## 3. 流程總覽

1. 接收後台管理員的 HTTP POST Request
2. Controller 層綁定路徑參數 `site`、`activityEvent` 與 Request Body
3. 傳遞請求至 `IActivityProductService`
4. Service 層生成商品唯一識別碼 (`id`)
5. Service 層調用 `IActivityDataProvider.CreateActivityProduct`
6. Provider 層呼叫下游 `productservice` REST API，寫入 `payment.products_activity` 表
7. 回傳成功結果 (HTTP 200)

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ProductController.CreateActivityProduct` | 接收 Request，綁定參數 `site`、`activityEvent` 及 `ActivityProduct` Body |
| 2 | Service | `ActivityProductService.Create` | 生成商品 UUID `id`；將 DTO 轉換為 `ActivityProduct` Model |
| 3 | Provider | `ActivityDataProvider.CreateActivityProduct` | 呼叫下游 `productservice` REST API |
| 4 | External | `productservice` | 接收請求，將商品資料寫入 `payment.products_activity` |

**來源**：Semantics `controller-product-createactivityproduct`、`service-iactivityproductservice-create`、`provider-iactivitydataprovider-createactivityproduct`、DB 使用限制 `products_activity.id` 由系統生成。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.products_activity` | Write (INSERT) | 寫入新建立的活動商品記錄 |

**來源**：DB Detail payment `products_activity` 寫入規則。

---

## 6. 重要規則

- **id 生成規則**：商品 `id` 由系統自動生成（UUID v4 格式），不應由管理員手動指定。任何 API 請求若包含 `id` 欄位，應忽略或拒絕。
  - **來源**：DB Detail payment 寫入限制 `products_activity.id` 僅在建立產品時由系統自動生成，不允許後續更新。
- **不可修改欄位**：`site`、`activityevent`、`id` 為複合主鍵 (Partition Key + Clustering Columns)，建立後不可修改。`updatetime` 由系統自動寫入，API 不可直接設定。
  - **來源**：DB Detail payment 寫入限制 `products_activity.updatetime` 由系統自動更新。
- **初始狀態**：新建立的活動商品預設狀態 (`status`) 應為 `0`（暫停），而非 `1`（販售中）。後續需管理員於後台「發布」才會變更為 `1`。
  - **來源**：DB Detail payment `products_activity.status` 值定義：0=暫停（INSERT 預設值）。
- **欄位驗證**：`price` 與 `quantity` 為必填正整數，不可為負值。
- **多語言支援**：`names` 為 `map<text, text>` 結構，用於儲存多語言商品名稱。寫入時不應直接覆蓋整個 map，可透過逐鍵更新。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 請求缺少必填欄位 `price` 或 `quantity` | 回傳 HTTP 400 Bad Request，提示缺少必要參數 |
| `site` 或 `activityEvent` 為空或格式錯誤 | 回傳 HTTP 400 Bad Request |
| 下游 `productservice` 無法連線或超時 | 回傳 HTTP 502 Bad Gateway 或 504 Gateway Timeout |
| `productservice` 回傳寫入失敗 (如 keyspace 不存在) | 回傳 HTTP 500 Internal Server Error |
| 請求中包含不應由用戶指定的欄位 (如 `id`、`updatetime`) | 應由 Service 層忽略或拒絕，不影響寫入結果 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| ACT-001 | API Test | 提交有效 `site`、`activityEvent`、`price`、`quantity`、`names` | 回傳 HTTP 200，`payment.products_activity` 中存在對應記錄且 `status=0` |
| ACT-002 | API Test | 提交時缺少 `price` 欄位 | 回傳 HTTP 400 |
| ACT-003 | API Test | 提交時 `quantity` 為負數 | 回傳 HTTP 400 |
| ACT-004 | Integration Test | 模擬 `productservice` 回傳錯誤 | Controller 正確處理並回傳 5xx 錯誤碼 |
| ACT-005 | Flow Test | 建立商品後，再以 GET API 查詢該活動商品列表 | GET 回應中顯示新建立商品，且 `status` 為 0 |
| ACT-006 | Permission Test | 使用未驗證的 Request 或無效 Token | 回傳 HTTP 401 Unauthorized |

---

## 9. 高風險區域

- **下游服務相依**：此流程依賴 `productservice` 的正常運作。若 `productservice` 發生故障，整個商品建立功能將無法使用。需配置 Retry 機制或 Circuit Breaker。
- **資料一致性**：`price` 與 `quantity` 僅在建立時一次寫入，後續不允許透過一般更新 API 直接變更。但需確保建立時的值正確無誤，否則需刪除後重建商品。
  - **來源**：DB Detail payment 寫入限制 `price`、`quantity` 僅在建立時寫入，後續不允許單一欄位更新。
- **多語言 Map 覆蓋**：若 Service 層對 `names` 處理不當，直接覆蓋整個 map，可能導致資料遺失。應確保建立時提供的 map 為完整初始值。
  - **來源**：廣告 DB 多語言 map 更新規範。

---

## 10. 常見錯誤

- **新人誤解**：誤以為活動商品建立後會自動上架 (`status=1`)。事實上，商品建立後預設為「暫停」狀態 (`status=0`)，需管理員手動發布。這是為了讓後台人員先填寫完整資訊後再對外公開。
- **AI 常見誤解**：直接將 `products_activity.status` 設為 `1` 或忽略初始狀態。必須理解狀態流轉 `0 → 1 → 2`，建立時為 `0`。
- **常見漏檢查**：未檢查下游 `productservice` 的回傳值是否成功，忽略異常處理導致前端無回應。
- **常見錯誤流程**：在建立請求中傳入自訂 `id`，或意圖修改 `updatetime`。應由 Service 層完全控制這些系統欄位。
- **DB 操作混淆**：誤以為可以透過直接對 `payment.products_activity` 進行 CQL INSERT 來建立商品。實際上 `pricebackendservice` 不直接存取 DB，所有操作必須透過 `productservice` API。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI `POST /api/v1/activity/{site}/{activityEvent}/products` |
| DB Table | payment.products_activity |
| DB 寫入限制 | DB Detail payment `products_activity.id`、`products_activity.updatetime`、`products_activity.price` |
| 狀態流轉 | DB Detail payment `products_activity.status`：0=暫停 (INSERT 預設) |
| Service | Semantics `service-iactivityproductservice-create` |
| Provider | Semantics `provider-iactivitydataprovider-createactivityproduct` |
| Controller | Semantics `controller-product-createactivityproduct` |