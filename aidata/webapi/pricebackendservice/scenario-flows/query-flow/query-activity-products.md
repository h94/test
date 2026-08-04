# 查詢活動商品

## 1. 場景目的

後台管理員查詢指定網站（`site`）與活動（`activityEvent`）下的商品列表，以進行後續編輯或管理。此為 **唯讀查詢**，用於後台「活動商品管理」介面。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/activity/{site}/{activityEvent}/products` | 查詢活動商品列表 |

- **權限**：需要驗證（✅）
- **參數**：
  - `site`：網站代碼（路徑參數，必填）
  - `activityEvent`：活動事件名稱（路徑參數，必填）

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，解析路徑參數 `site`、`activityEvent`
2. 透過 `ECFramework.ECService` 驗證使用者身份與後台管理權限
3. 呼叫下游微服務 `productservice` 的 REST API，查詢活動商品資料
4. 將下游回傳的原始商品資料進行過濾、欄位轉換（僅保留必要欄位、遮蔽敏感欄位）
5. 回傳 `List<ActivityProduct>` JSON 陣列

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ActivityController.GetProducts` | 接收請求，呼叫 Service |
| 2 | Service | `IActivityService.GetProductsBySiteAndEvent` | 組合查詢條件，呼叫 Provider |
| 3 | Provider | `IProductServiceProvider.GetActivityProducts` | 發起 HTTP GET 至 `productservice` |
| 4 | Provider | *(下游 productservice)* | 查詢 `payment.products_activity` 表並回傳 |
| 5 | Service | `IActivityService` | 轉換 DTO、過濾 status=1（上架）、過濾 quantity>0 |
| 6 | Controller | `ActivityController` | 回傳 `ActivityProduct[]` JSON |

> ⚠️ Layer 細節依賴實際程式碼，此處為基於架構慣例推估，若與實做不符請人工確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| 下游 REST | `productservice`（內部 API） | Read | 查詢活動商品原始資料 |
| — | — | — | 本服務 **無直接 DB 存取**，無 Redis / Queue 參與 |

- 下游客戶端實際查詢的 Cassandra 表為 `payment.products_activity`，以 `site`、`activityevent` 為分區鍵，過濾 `status = 1`（上架）。

---

## 6. 重要規則

- **權限限制**：僅後台管理員可呼叫，需通過 `ECService` 驗證
- **不可暴露欄位**：`remail`（供應商信箱）不可回傳（來源：`product DB detail`）
- **過濾規則**：
  - 必須過濾 `status = 1`（上架商品），排除下架或暫停的商品
  - 建議同時過濾 `quantity > 0`，避免顯示無庫存商品
- **欄位限制**：
  - `id` 建立後不可更改
  - `price`、`quantity` 不可透過此查詢 API 修改
- **時間戳**：`updatetime` 為系統自動維護，不對外寫入

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未登入或 Token 過期 | 回傳 `401 Unauthorized` |
| 權限不足（非管理員） | 回傳 `403 Forbidden` |
| `site` 或 `activityEvent` 為空或不合法 | 回傳 `400 Bad Request`，提示缺少必要參數 |
| 下游 `productservice` 不可用（網路斷線或 5xx） | 回傳 `502 Bad Gateway` 或 `503 Service Unavailable` |
| 指定的 `site`、`activityEvent` 不存在 | 回傳 `200` 但空陣列（不拋錯） |
| Redis / Kafka 故障 | 不影響此查詢（未使用） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| ACT-QUERY-01 | Permission | 沒有 Bearer Token 呼叫 API | 401 |
| ACT-QUERY-02 | Permission | 非管理員角色呼叫 | 403 |
| ACT-QUERY-03 | Flow | 傳入合法 `site` 與 `activityEvent`，存在上架商品 | 回傳陣列，僅 `status=1` 商品 |
| ACT-QUERY-04 | Flow | 傳入合法參數，但該活動無上架商品 | 回傳空陣列 `[]` |
| ACT-QUERY-05 | Filter | 活動中存在下架商品（`status=0`） | 下架商品不出現在回傳中 |
| ACT-QUERY-06 | Field | 檢查回傳 JSON 不應包含 `remail` 欄位 | `remail` 不存在 |

---

## 9. 高風險區域

- **無**：此查詢為唯讀，無跨服務寫入、無交易、無快取一致性問題。
- 下游 `productservice` 故障屬於常規依賴風險，可透過重試或熔斷處理。

---

## 10. 常見錯誤

- 未過濾 `status` 欄位，直接回傳「下架」或「暫停」商品，導致前台誤顯示。
- 回傳不應暴露的欄位（如 `remail`），違反營運規範。
- 未處理下游服務回傳的 null 或例外狀況（例如未用 try-catch 包覆，導致 500）。
- 忘記在 Service 層將 `names` 多語言 map 轉換為前端相容格式（例如只提供預設語言或請求語言）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `GET /api/v1/activity/{site}/{activityEvent}/products`（OpenAPI/README） |
| 權限 | README 中標記 `✅` 需要驗證 |
| DB 讀取規則 | `payment-detail.md`：查詢 `products_activity` 時過濾 `status = 1`，依 `site`、`activityevent` 過濾 |
| 不可回傳欄位 | `product-detail.md`：`remail` 不可公開 |
| 下游服務 | `README.md` 提及 `productservice` 負責活動商品、商城商品等 |
| 代碼證據 | （無直接程式碼，依架構慣例推斷 Controller → Service → Provider → 下游 REST） |
| 過濾建議 | `payment-detail.md`：查詢時通常過濾 `status = 1`；`price`、`quantity` 不可透過查詢 API 修改 |