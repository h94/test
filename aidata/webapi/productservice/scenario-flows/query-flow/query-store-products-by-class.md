# 依分類查詢上架商城商品

## 1. 場景目的

供前台使用者依據商品分類查詢所有已上架的商品，以便瀏覽與選擇兌換。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/store/products/{pclass}` | 依分類取得上架商品列表 |

> **需人工確認**：OpenAPI 文件中未直接提供此 API 定義。API 資訊來自 README.md ，但 README 標記此 API 需要驗證，與「前台查詢」的描述（前台 GET）可能不一致，需確認實際的權限設定。

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，包含路徑參數 `pclass`（商品分類代碼）。
2. 系統驗證請求方的身分（若需要驗證，此處由 ECCore 3.0.2 機制處理）。
3. Controller 層將請求轉交給 Service 層處理。
4. Service 層呼叫 DataProvider 查詢資料庫：
   - 查詢對象：`product.products_store` 表。
   - 查詢條件：`WHERE pclass = {pclass}`，且過濾 `status = '1'` 的記錄。
   - 僅查詢必要的欄位。
5. Service 層將查詢結果映射為回傳模型，並進行語系處理（如 `pnames`, `description` 等）。
6. Controller 回傳 HTTP 200 與商品列表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `StoreController.GetProducts(string pclass)` | 接收 `pclass` 參數，呼叫 `IStoreService`。 |
| 2 | Service | `StoreService.GetProducts(string pclass)` | 接收 `pclass`，呼叫 `IStoreDataProvider` 查詢已上架商品。 |
| 3 | Provider | `StoreDataProvider.GetStoreProducts(string pclass, string status)` | 對 `product.products_store` 執行 Cassandra 查詢，WHERE `pclass` = 傳入值 且 `status` = `"1"`。 |
| 4 | Service | `StoreService.GetProducts(...)` | 將 `ProductStore` 實體列表映射為對外的 DTO (`StoreProduct`)，並依 `Accept-Language` 處理多語系欄位。 |
| 5 | Controller | `StoreController` | 回傳 `IEnumerable<StoreProduct>` 與 HTTP 200。 |

> **需人工確認**：上述 Controller, Service, Provider 的具體名稱是根據架構慣例推斷，應以實際代碼（如 `StoreController.cs`, `IStoreService.cs`, `IStoreDataProvider.cs`）為準。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `product.products_store` | Read | 根據 `pclass` 分區鍵查詢商品資料。 |
| Cache | 未使用 | - | 此流程未涉及 Redis 快取。 |

---

## 6. 重要規則

- **權限限制**：無特定業務權限，但需通過系統的 ECCore 驗證機制。
- **狀態過濾**：強制過濾 `status = '1'`（上架）的商品。`status = '0'`（下架）的商品僅供後台查詢。
- **資料庫查詢限制**：查詢必須以 `pclass` 為分區鍵 (Partition Key) 進行 `WHERE` 查詢，不可全表掃描。
- **不可回傳欄位**：無。
- **多語系處理**：對於 `pnames`, `description`, `image_path` 等 map 類型欄位，應根據請求的 `Accept-Language` 頭返回對應的語系值。若找不到對應語系，需有默認回退機制。
- **排序規則**：支援依 `popular` 或 `sequence` 排序，但不可跨 `pclass` 排序。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 請求未通過驗證 | 返回 HTTP 401 Unauthorized。 |
| `pclass` 參數為空 | 返回 HTTP 400 Bad Request。 |
| `pclass` 對應的分類下沒有任何商品 | 返回 HTTP 200 且商品列表為空 `[]`。 |
| 指定的 `pclass` 下所有商品皆為下架（`status='0'`） | 返回 HTTP 200 且商品列表為空 `[]`。 |
| Cassandra 查詢逾時或連線失敗 | 返回 HTTP 500 Internal Server Error。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| UT-001 | Unit Test | 提供有效的 `pclass`，該分類下有多筆上架商品 | 回傳的商品列表長度正確，且全部為 `status='1'`。 |
| UT-002 | Unit Test | 提供有效的 `pclass`，該分類下有上架與下架商品 | 回傳的列表僅包含上架商品。 |
| UT-003 | Unit Test | 提供一個不存在的 `pclass` | 回傳空的商品列表。 |
| IT-001 | Integration Test | 驗證 Cassandra 查詢語句的正確性 | 確認 CQL 包含 `WHERE pclass=? AND status='1'`。 |
| IT-002 | Integration Test | 模擬 Cassandra 查詢拋出例外 | Service 層應正確捕獲並轉拋或記錄，Controller 回傳 HTTP 500。 |
| API-001 | API Test | 發送帶有 `Accept-Language: en` 的請求 | 回傳的 `pnames` 應為對應的英文名稱。 |

---

## 9. 高風險區域

- **全表掃描風險**：Cassandra 查詢必須強制帶入 `pclass` 分區鍵。若因程式錯誤導致全表掃描，在資料量大時將嚴重影響效能。
- **無快取機制**：本場景未使用 Redis，所有讀取壓力直接作用於 Cassandra。若為高頻率存取端點，需考慮引入快取以保護後端資料庫。
- **狀態一致性**：保證回傳的永遠是 `status = '1'`，避免對外暴露不該顯示的商品。

---

## 10. 常見錯誤

- ❌ 查詢時僅使用 `pclass` 條件，卻遺漏 `status='1'` 的過濾，導致前端顯示下架商品。
- ❌ 沒有處理 `pnames` 等 Map 型態的語系回退，導致部分語系使用者看到空白。
- ❌ Cassandra 查詢沒有使用參數化，而是拼接字串，可能導致查詢效能低落或注入風險。
- ❌ 誤將 README 中標記「需要驗證」視為需要特定角色權限，而阻擋了一般使用者的請求。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md：`GET /api/v1/store/products/{pclass}` |
| DB | Schema: `product.md`, Table: `products_store` |
| 規則 | productservice-detail.md：product 讀取規則 - 查詢商店商品列表 |
| 規則 | product-detail.md：products_store table 說明 |
| 驗證 | README.md：技術棧 - ECCore 3.0.2 內建機制 |
| 語意 | Phase0/1 AI 分析：products_store 各欄位語意 |