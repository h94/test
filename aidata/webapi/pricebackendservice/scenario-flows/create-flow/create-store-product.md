# 建立商城商品

## 1. 場景目的

後台管理員建立一個可供會員於商城兌換的商品，設定商品名稱、價格、庫存等資訊。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/store/products` | 建立商城商品 |

---

## 3. 流程總覽

1. 後台管理員呼叫 API，傳入商品資訊
2. 驗證管理員權限
3. 驗證請求參數（pclass、pid、價格、庫存等）
4. 轉換請求資料為 DTO
5. 呼叫下游 `productservice` REST API 建立商品
6. `productservice` 寫入 `payment.products_store` 表
7. 回傳建立結果

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `StoreController.CreateProduct` | 接收 request，驗證 ModelState，呼叫 Service |
| 2 | Service | `IStoreService.CreateProduct` | 轉換參數為 DTO，呼叫 Provider |
| 3 | Provider | `IProductDataProvider.CreateStoreProduct` | 呼叫下游 `productservice` REST API |
| 4 | Service (下游) | `productservice` | 驗證資料，寫入 `payment.products_store` |
| 5 | DB | Cassandra `payment.products_store` | 寫入商品記錄，`id` 由系統自動生成 |

> **需人工確認**：Validator 層具體實作是否存在，以及參數驗證細節（如 `pclass` 合法值、價格範圍）。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.products_store` | Write | 寫入新商品記錄 |
| Queue | — | 無 | 此流程未使用 Queue |
| Redis | — | 無 | 此流程未使用 Redis Cache |

---

## 6. 重要規則

- **權限限制**：此 API 需要管理員驗證，不可匿名呼叫。若權限不足，應回傳 `401 Unauthorized` 或 `403 Forbidden`。
- **欄位限制**：
  - `id`：由系統自動生成（UUID），不允許 API 直接傳入或後續修改。
  - `systemtime`：由系統自動設定為當前時間，不允許 API 寫入。
- **不可暴露資料**：`remail`（供應商聯絡資訊）不可對外回傳，僅供內部使用。
- **狀態值限制**：商品建立後初始狀態應為未上架（`status = 0`），需由後台另行操作上架。
  > **需人工確認**：`status` 初始值的具體行為，文件描述為「商品上架狀態僅能透過後台管理服務設定」，暗示初始值可能為 0。
- **不可修改欄位**：`id`、`systemtime` 建立後不可修改。
- **價格單位**：根據 `product-detail.md`，`price`、`originalprice` 單位為「分」。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未通過管理員驗證 | 回傳 `401` 或 `403` |
| 必要參數缺失（如 pclass, pid） | 回傳 `400 Bad Request` |
| `payment.products_store` 寫入失敗 | 回傳 `500 Internal Server Error` |
| 下游 `productservice` 無回應 | 回傳 `502 Bad Gateway` 或 `504 Gateway Timeout` |
| 請求參數格式錯誤 | 回傳 `400 Bad Request` |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T01 | Permission Test | 無 token 呼叫 API | `401` |
| T02 | API Test | 正常參數建立商品 | `201 Created` 或 `200 OK` |
| T03 | Flow Test | 建立後查詢商品 | 查詢結果包含新商品 |
| T04 | API Test | 傳入超大值 `price` | `400` (若後端有驗證) |
| T05 | API Test | 缺失 `pid` 參數 | `400 Bad Request` |
| T06 | Integration Test | 模擬 `productservice` 掛點 | `502` 或 `504` |

---

## 9. 高風險區域

- **高風險 Table**：`payment.products_store` —— 唯一寫入商品資料的位置，寫入失敗會直接導致商品遺失。
- **高風險 API**：下游 `productservice` CreateProduct API —— 若此 API 異常，整個流程失敗。
- **Transaction**：此流程無跨服務 Transaction。若後續有「建立商品 + 寫入庫存記錄」等多步操作，需考慮補償機制。
- **Cache consistency**：此流程不涉及 Cache，無風險。
- **Idempotency**：API 重複呼叫將建立多個獨立商品（不同 `id`），需由前端避免重複提交。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 誤以為 `id` 可以由前端指定，實則由系統生成。
  - 忘記 `price` 單位為「分」，直接傳入元造成價格放大百倍。
  - 忽略權限驗證，直接測試 API 導致 `401`。
- **AI 容易誤解**：
  - 誤將 `payment.products_store` 當作 `product` keyspace 的表，應注意為 `payment` keyspace。
  - 可能誤判 `status` 初始值為 1（上架），實則可能為 0（下架）。
- **常見漏檢查項目**：
  - 未確認 `pclass` (商品分類) 是否存在或合法。
  - 未確認 `pid` (商品自訂識別碼) 是否與既有商品重複。
- **常見錯誤流程**：
  - 在 `pricebackendservice` 端進行參數驗證後直接寫入 DB（應交由 `productservice` 處理）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `README.md`：`POST /api/v1/store/products` |
| DB 表 | `payment.products_store` schema definition |
| DB 寫入規則 | `pricebackendservice-detail.md` — product 章節 |
| 服務相依 | `README.md` 服務相依：`productservice` 負責商品商城 |
| 流程 | 基於 BFF 模式推導，`pricebackendservice` 為聚合層，呼叫下游 `productservice` |
| DB 欄位語意 | `db/payment-detail.md`：`products_store` 欄位定義 |