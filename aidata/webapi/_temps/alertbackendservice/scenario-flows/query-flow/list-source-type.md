# 列出資料源類型設定

## 1. 場景目的
查詢系統當前所有資料源（source）支援的遊戲類型對應設定，或依指定來源代碼取得單一來源的設定清單，供後端管理介面或外部系統取得可用的資料源類型映射。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | /api/source_type | 列出全部資料源類型設定，或透過 `?source=` 查詢單筆（OpenAPI List Source Type） |

query 參數：

| 參數 | 型別 | 必填 | 說明 |
|---|---|---|---|
| source | string | 否 | 資料源名稱，用於過濾單一來源的設定 |

回應內容：JSON 陣列，每筆包含 `source`, `support_type`, `operator_account`, `created_at`, `updated_at`。

---

## 3. 流程總覽

1. 接收 GET request（可選帶 `?source=` 篩選）
2. 驗證操作者權限（若有啟用驗證中間件，需人工確認）
3. Service 層呼叫 Provider 進行查詢
4. Provider 查詢 `source_type` 表：
   - 若未指定 `source`，回傳所有紀錄
   - 若指定 `source`，回傳該來源紀錄（不存在則回傳空陣列）
5. 回傳 JSON 陣列

無寫入、無快取、無佇列參與。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Router | `source_type_router` | 接收 GET `/api/source_type`，解析 `source` 參數（OpenAPI） |
| 2 | Service | `SourceTypeService.list_source_types` | 呼叫 Provider 查詢資料（推測，需人工確認） |
| 3 | Provider | `SourceTypeProvider.list_all` 或 `list_by_source` | 執行 SQL：`SELECT source, support_type, operator_account, created_at, updated_at FROM source_type`（若有 source 則加 `WHERE source = :source`）（依據 `source_type` 表結構） |
| 4 | Service | 同 2 | 將查詢結果轉為 DTO 回傳 |

**註：** Router 與 Service 的具體名稱、是否透過 Transfer 層轉換需人工確認實際 code。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `source_type` 表 | Read | 查詢資料源類型設定（OpenAPI 描述為列出設定） |

無 Redis / Cache / Kafka / Queue 參與。

---

## 6. 重要規則

- **查詢限制**：僅支援等值過濾 `source` 欄位，無模糊搜尋、排序或分頁（OpenAPI 僅提供一組 query 參數）
- **欄位暴露**：必須回傳 `support_type` (JSONB)、`operator_account`、時間戳記，無敏感資訊隱藏需求（依據 DB schema）
- **狀態值限制**：`source_type` 表無狀態欄位，所有記錄皆為有效設定
- **權限限制**：單純查詢，若未實施 API 級權限則任何可存取服務者皆可呼叫（需人工確認是否有 auth middleware）
- **不可修改欄位**：此 API 僅供讀取，不支援新增、修改、刪除

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未指定 source，正常查詢 | 回傳所有資料源設定（可能為空陣列） |
| 指定存在的 source | 回傳該筆記錄，陣列長度 1 |
| 指定不存在的 source | 回傳空陣列 `[]` |
| 資料庫連線失敗或語法錯誤 | HTTP 500，回應 error detail（需人工確認具體 error handling） |
| 操作者未通過驗證 | HTTP 401/403（需人工確認是否有驗證機制） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| ST-01 | API Test | GET /api/source_type 無參數，系統已有數筆設定 | 200，回傳全部設定，每筆含 source, support_type 等 |
| ST-02 | API Test | GET /api/source_type?source=existing_source | 200，回傳該筆設定 |
| ST-03 | API Test | GET /api/source_type?source=nonexistent | 200，回傳空陣列 |
| ST-04 | Flow Test | Provider 回拋例外（如連線中斷） | 500，記錄錯誤 log |
| ST-05 | Permission Test | 未帶 token 或無效 token（若實作 auth） | 401/403 |

---

## 9. 高風險區域

- **低風險**：純查詢，無資料異動，無跨服務相依。
- **潛在關注**：
  - 若 `source_type` 表資料量極大，無分頁可能造成回應過大或延遲，但實際資料源數量有限，風險低。
  - `support_type` 欄位為 JSONB，回傳時需確認格式一致，若下游解析依賴特定型態可能有相容性風險。

---

## 10. 常見錯誤

- **誤解 `support_type` 結構**：新人可能認為回傳是字串，實際為 JSON 陣列（如 `["game_type_1", "game_type_2"]`），需查閱 DB schema 或既有資料。
- **忽略權限檢查**：若服務已實作全域 API Auth，但新人直接從瀏覽器呼叫可能得到 401，需確認部署環境的驗證配置。
- **誤用 `source` 參數**：未注意 source 是完整匹配，可能想用部分字串搜尋但 API 不支援。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI: `GET /api/source_type`，tags: source_type，description: "列出全部資料源類型設定；可用 source 查詢單筆" |
| DB Table | `source_type`（欄位：source, support_type, operator_account, created_at, updated_at） |
| Migration | `migrations/001_create_core_tables.sql` 定義 `source_type` 表結構 |
| Provider (推測) | 可能實作於 `Provider/source_type.py` 的 `list_all` 方法，需人工確認實際 code |
| Service (推測) | Service 層可能由 `Service/source_type.py` 提供 `get_source_types` 或類似方法，需人工確認 |