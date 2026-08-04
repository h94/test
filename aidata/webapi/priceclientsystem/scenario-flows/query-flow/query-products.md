# 查詢商品列表

## 1. 場景目的

為用戶（前端 InplayZ）提供可兌換的商品清單。系統從 Cassandra `product.products_store` 查詢所有狀態為「上架（active）」的商品，並根據請求的語言偏好（Accept-Language）回傳對應的多語系名稱與描述。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/product/store` | 查詢所有上架商品列表（推測，OpenAPI 未列出，需從源碼確認） |

> **需人工確認**：OpenAPI 文件中未定義商品相關端點，此 API 路徑是根據 DB 操作邊界與服務職責的合理推測。實際路徑與參數需由 `ProductStoreController` 源碼確認。

---

## 3. 流程總覽

1. 前端請求商品列表，攜帶語言偏好（e.g., `Accept-Language: zh-CN`）。
2. Controller 接收請求，調用對應的 Service。
3. Service 層通過 Provider 向 Cassandra 的 `product.products_store` 表查詢。
4. 查詢條件為 `status = 'active'`，可能按 `sequence` 排序。
5. 從查詢結果中，根據請求語言解析 `pnames`、`description`、`image_path` 等 map 欄位，提取對應語言的文字。
6. 組裝 DTO 並回傳給前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `ProductStoreController.GetProducts` | 接收 HTTP GET 請求，取得語言偏好，調用 Service 層。 |
| 2 | Service | `ProductStoreService.GetActiveProducts` | 負責業務邏輯組裝，過濾與多語系解析。 |
| 3 | Provider | `ProductStoreProvider.GetAllActive` | 執行 Cassandra 查詢，語法類似 `SELECT * FROM products_store WHERE status='active'`。 |
| 4 | Transfer | DTO 映射 | 將 Cassandra 回傳的 Entity 轉換為對外 DTO，僅包含必要且非敏感欄位。 |

> **需人工確認**：具體的 Class 與 Method 名稱需從 `batch-1` 至 `batch-5` 的 source code 中確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `product.products_store` | Read | 查詢所有 `status='active'` 的商品資訊。 |

此場景不涉及寫入、佇列或快取。

> **Evidence**: `priceclientsystem-detail.md` 明確指出「Redis（無）」，且價格/商品管理細節文件指出 `products_store` 的讀取操作由 `priceclientsystem` 發起。

---

## 6. 重要規則

- **狀態過濾**：查詢時必須帶有條件 `status = 'active'`。任何其他狀態（如 `'inactive'`, `'deleted'`）的商品不可對一般用戶展示。
- **多語系解析**：
    - `pnames`、`description`、`image_path` 均為 `map<text, text>` 型別。
    - 應根據請求的語言代碼（e.g., `zh-CN`, `en`）從 map 中提取對應的值。若無對應語言，應有預設回退機制（如回退至英文或第一個可用語言）。
- **不可回傳欄位**：此場景為公開商品列表，不涉及兌換紀錄中的敏感欄位（如 `phonenumber`, `address`, `account`）。
- **排序規則**：商品應依照 `sequence` 欄位排序，熱門商品 (`popular = true`) 可能優先顯示。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| Cassandra 連線失敗或逾時 | 回傳 HTTP 500 Internal Server Error，前端應顯示「服務暫時不可用」。 |
| 查無任何上架商品 | 回傳 HTTP 200 OK，但 body 為空列表 `[]`。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC-01 | API Test | 無任何過濾條件，直接呼叫 API | 只回傳 `status='active'` 的商品。 |
| TC-02 | Function Test | 請求 Header `Accept-Language: en` | `pnames` 和 `description` 應為英文內容。 |
| TC-03 | Function Test | 請求 Header `Accept-Language: zh-CN` | `pnames` 和 `description` 應為簡體中文內容。 |
| TC-04 | Function Test | 資料庫中存在 `status='inactive'` 的商品 | 回傳列表中不應包含該商品。 |
| TC-05 | Function Test | 資料庫中無任何商品 | 回傳 HTTP 200，body 為空陣列。 |

---

## 9. 高風險區域

- **資料庫查詢效率**：若 `products_store` 表資料量極大，且 `status` 欄位不具有索引或非分區鍵，全表掃描可能造成效能瓶頸。需確保查詢設計符合 Cassandra 數據模型最佳實踐。
- **多語系資料完整性**：若 `pnames` map 中缺少特定語言鍵值，應用程式需有穩健的 fallback 機制，避免回傳 null 導致前端顯示異常。

---

## 10. 常見錯誤

- ❌ **未過濾商品狀態**：直接 `SELECT *` 後透過應用層過濾或根本未過濾，導致下架或已刪除商品洩漏給前端。
    - ✅ 必須在 CQL 查詢層級加上 `WHERE status = 'active'`。
- ❌ **多語系處理失誤**：直接將整個 `pnames` map 回傳給前端，讓前端自行解析，增加了前端複雜度且有暴露多餘數據的風險。
    - ✅ 後端應根據請求的 `Accept-Language` 頭解析並只回傳對應的單一語言字串。
- ❌ **誤解 `status` 值**：DB 文件顯示 `status` 為 text，值為 `"0"` 或 `"1"`，但場景描述與 `priceclientsystem` 讀取規則中均使用 `'active'`，可能是其他服務的定義。
    - ✅ **需人工確認** `products_store.status` 的實際枚舉值為 `"active"`, `"inactive"` 還是 `"1"`, `"0"`。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | 推測自 `priceclientsystem` 服務職責，需源碼確認 |
| DB | `product.products_store` (Schema: `db/product.md`) |
| 讀取規則 | `webapi/priceclientsystem/priceclientsystem-detail.md` - 產品列表查詢規則 |
| 無快取 | `webapi/priceclientsystem/priceclientsystem-detail.md` - Redis章節 |
| 多語系欄位 | `db/product.md` - `pnames map<text, text>`, `description map<text, text>` |