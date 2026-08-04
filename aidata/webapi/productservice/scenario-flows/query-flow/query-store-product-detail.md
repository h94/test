# 查詢單一商城商品詳情

## 1. 場景目的
讓已驗證的使用者取得特定商城商品的所有可公開資訊，包含多語言名稱、價格、圖片與描述，用於商品展示頁。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/store/products/{pclass}/{pid}` | 查詢單一商城商品，需登入 |

---

## 3. 流程總覽

1. 從請求 Header 取得驗證 Token，由 ECCore 驗證身分
2. 解析路由參數 `pclass`（商品分類）與 `pid`（商品編號）
3. 嘗試從 Redis 讀取快取 `product:store:{pclass}:{pid}`
4. 若快取命中且商品狀態為上架（`status="1"`），直接回傳
5. 若快取未命中或商品已下架，向 Cassandra `products_store` 以 `pclass` 為分區鍵查詢特定 `pid`
6. 檢查商品 `status` 是否為 `"1"`（上架）；若為 `"0"` 則視同不存在，回傳 404
7. 根據請求的 `Accept-Language` 從 `pnames`、`description`、`image_path` 等 Map 欄位中取出對應語系的內容
8. 組裝回應模型，排除任何內部 ID（若有）並回傳
9. 將有效結果寫入 Redis 快取，TTL 建議 30 秒（若系統有啟用快取）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Middleware | ECCore 驗證模組 | 檢查 Token，無效則回應 401 |
| 2 | Controller | `StoreController.GetStoreProduct` (推測) | 接收 pclass, pid，呼叫 Service |
| 3 | Service | `ProductService.GetStoreProductAsync` (推測) | 查詢快取或 DB，過濾狀態，處理多語言 |
| 4 | Provider | `ProductStoreDataProvider` (推測) | 呼叫 Cassandra Driver 以 `WHERE pclass=:pclass AND pid=:pid` 查詢 |
| 5 | Helper | 語系解析函數 | 根據 `Accept-Language` 從 Map 取出對應值，若無則 fallback 預設語系 (如 `en`) |
| 6 | （若有） | `HashCacheHelper` | 讀取或寫入 Redis 快取 `product:store:{pclass}:{pid}` |

> **需人工確認**：實際 Controller / Service 類別與方法名稱需比對原始碼。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `product.products_store` | Read | 查詢商品主檔 (by pclass + pid) |
| Cache | `Redis` key: `product:store:{pclass}:{pid}` | Read / Write | 儲存單一商品快取，TTL 30 秒（推測） |
| Queue | 無 | - | - |

> **需人工確認**：productservice 是否自行管理此 Redis 快取，或依賴其他服務（如 inplayzsubscriptionsystem）寫入。

---

## 6. 重要規則

- **權限限制**：必須攜帶有效 JWT，由 ECCore 驗證；未登入回傳 401。
- **狀態過濾**：`status` 欄位為 text，值 `"1"` 才對外公開；`"0"`（下架）視同不存在，回傳 404。
- **分區鍵強制**：Cassandra 查詢必須用 `pclass` 當作分區鍵，不可全表掃描。
- **多語言處理**：`pnames`、`description`、`image_path` 均為 `map<text, text>`，回傳時必須依據 `Accept-Language` 取值，若無對應則 fallback 至預設語系（如 `en`）。
- **不可暴露欄位**：無內部 ID 問題（`products_store` 以 pid 為公開主鍵）；但需注意未來若有內部主鍵不得暴露。
- **價格不可修改**：此 API 僅供查詢；價格欄位 (price, originalprice) 依規定不允許直接 UPDATE，故此處僅讀取無安全顧慮。
- **Sequence / Popular**：可一併回傳供前端排序或標記熱門。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 缺少或無效的 Authorization Header | 401 Unauthorized |
| pclass 或 pid 格式非預期（例如含特殊符號） | 400 Bad Request |
| 商品不存在 (pclass/pid 組合無資料) | 404 Not Found |
| 商品存在但 status != "1" | 404 Not Found (對前端等價於不存在) |
| Cassandra 查詢 timeout 或連線失敗 | 500 Internal Server Error，寫入 log |
| Redis 無法讀取（若依賴快取） | 應降級查詢 Cassandra，不影響功能 |
| Accept-Language 無匹配語系 | 回傳預設語系內容，不報錯 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| ST-01 | API Test | 使用有效 Token 查詢存在且上架的商品 | 200，回傳完整商品資訊 |
| ST-02 | API Test | 查詢存在但已下架的商品 (status="0") | 404 |
| ST-03 | API Test | 查詢不存在的 pclass | 404 |
| ST-04 | Permission Test | 不帶 Token 請求 | 401 |
| ST-05 | Flow Test | 指定 Accept-Language: zh-CN，商品有此語系 | 回傳中文名稱與描述 |
| ST-06 | Flow Test | 指定 Accept-Language: jp，商品無此語系 | 回傳 fallback 語系 (如 en) |
| ST-07 | Integration Test | Redis 快取命中 | 回應時間顯著低於直接查 DB，且資料正確 |
| ST-08 | Integration Test | Cassandra 回應延遲 | 前端收到 500 或觸發重試機制 |

---

## 9. 高風險區域

- **快取一致性**：若商品狀態被後台修改（上架→下架），必須主動清除 `product:store:{pclass}:{pid}` 快取，否則舊資料可能被錯誤回傳。依目前規範，狀態變更只能透過 `UpdateStoreProductStatus`，該方法需負責清除快取。
- **分區鍵缺失**：若 Controller 未正確傳遞 pclass 或 Service 層省略分區鍵條件，可能觸發 Cassandra 全表掃描，導致效能問題。
- **多語言 map 解析**：若 map 中有空值或非法語言代碼，可能拋出例外，需防禦性取用。

---

## 10. 常見錯誤

- ❌ 查詢時未以 `pclass` 為 WHERE 條件，導致全表掃描。
- ❌ 直接回傳 `status="0"` 的下架商品給前端。
- ❌ 忽略 `Accept-Language`，直接回傳整個多語言 Map 或固定語言內容。
- ❌ 在 Service 層未處理 Cassandra 讀取例外，導致 Unhandled Exception。
- ❌ 快取命中後未再確認 `status`，可能回傳過期或已下架的商品。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | `README.md`：`GET /api/v1/store/products/{pclass}/{pid}`，需要驗證 |
| DB 查詢表 | `product.products_store`，schema: `product.md` |
| 讀取規則 | `product-detail.md`：必須以 `pclass` 為分區鍵，前端只回傳 status="1" |
| 狀態值 | `AppDefine.cs` (推測)，`product-detail.md`：`"0"` = 下架，`"1"` = 上架 |
| 多語言處理 | `product-detail.md`：pnames/description/image_path 為 map，依語系取值 |
| Redis 快取 | `product-detail.md`：key `product:store:{pclass}:{pid}`，TTL 30 秒，由 inplayzsubscriptionsystem 管理；productservice 可能使用 |
| 權限驗證 | `README.md` 需要驗證 ✅，框架 ECCore 3.0.2 內建機制 |