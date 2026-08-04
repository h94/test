# 查詢商城商品

## 1. 場景目的
讀取已上架的商城商品列表，並依排序權重（sequence）由小到大排列，回傳時根據用戶語系回傳對應的多語言名稱、描述與圖片，供前端商城頁面展示。

---

## 2. 入口 API
| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/store/products` | 查詢指定類別（pclass）的上架商品，可選語系參數決定回傳內容語言 |

- 實際 API 路徑與參數待由程式碼確認（需人工確認）。

---

## 3. 流程總覽
1. 接收請求，含 `pclass`（商品類別）與可選的 `lang`（語系）參數。
2. 透過 ECCore 驗證 `authKey`，確認身份有效性。
3. 讀取 Cassandra `product.products_store` 表：
   - 條件：`pclass = ?` 且 `status = '1'`（上架）。
4. 將查詢結果在應用層依 `sequence` 遞增排序（Cassandra 無法直接按此欄位排序）。
5. 根據請求語系（或使用者偏好語系）從 `pnames`、`description`、`image_path` 三個 map 中提取對應值；若無對應語言則 fallback 至預設語系（如 `en`）。
6. 過濾不可回傳欄位（如 `originalprice`、`psource`），組裝回傳 DTO。
7. 寫入本地快取（`System.Runtime.Caching`）或 Redis（快取 Key 可能為 `ResponseCacheInfo:{cacheKey}`），TTL 依配置（通常 300～600 秒）。
8. 回傳商品列表。

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `StoreController.GetProducts` | 接收 HTTP GET 請求，解析 pclass、lang 參數，調用 Service |
| 2 | Service | `StoreService.GetStoreProducts` | 組裝查詢條件，呼叫 Provider 讀取 DB，處理排序與語言映射 |
| 3 | Provider | `ProductDataProvider.GetStoreProducts` | 執行 Cassandra 查詢：`SELECT * FROM product.products_store WHERE pclass=?`，並於應用層過濾 status='1' |
| 4 | Transfer | `StoreProductDto` | 將資料庫實體轉換為前端 DTO，提取對應語系的名稱、描述、圖片，排除敏感欄位 |
| 5 | Cache | `ResponseCacheService` | 若快取命中則直接回傳；miss 時寫入快取（Redis `ResponseCacheInfo:{cacheKey}` 或 `System.Runtime.Caching`） |

- 以上流程為推估，實際類別名稱需人工確認（需人工確認）。

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `product.products_store` | Read | 查詢指定 pclass 的商品清單 |
| Cache | Redis `ResponseCacheInfo:{cacheKey}` | Read / Write | 快取 API 回應，降低 DB 查詢頻率；TTL 通常 300–600 秒 |
| Cache | `System.Runtime.Caching`（本地） | - | 可能用於二級快取（需人工確認） |

- 本場景只讀不寫，不涉及 Kafka 或 Queue。

---

## 6. 重要規則
- **狀態過濾**：僅回傳 `status = '1'` 的商品；`'0'`（下架）不應出現。
- **排序**：`sequence` 為整數，數值越小排序越前；若無指定，預設以 `sequence` ASC 排序。
- **多語言回傳**：`pnames`、`description`、`image_path` 均為 `map<text, text>`，回傳時僅提取請求語系對應的 value，不可暴露整個 map。若缺少該語系，應 fallback 至預設語言（如 `en`）。
- **不可回傳欄位**：
  - `originalprice`：前台一般不需要，應排除。
  - `psource`：內部來源，不可暴露。
  - `lastup_time`：內部時間戳，不應回傳。
  - `popular`：可依業務決定是否回傳（本場景為商城列表，可能回傳用於標記熱門）。
- **分區鍵使用**：查詢時必須指定 `pclass`，嚴禁全表掃描。
- **快取一致性**：後台更新商品狀態或內容後，應透過某種機制（如 pub/sub）失效相關快取。目前責任歸屬不在此場景內，但屬於潛在風險。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|------|----------|
| 缺少或無效的 `authKey` | HTTP 401，拒絕存取 |
| 未傳入 `pclass` 參數 | HTTP 400，提示缺少必要參數 |
| 指定的 `pclass` 無任何上架商品 | 回傳空陣列（HTTP 200） |
| Cassandra 查詢逾時 | HTTP 500，記錄錯誤日誌，避免回傳 DB 細節 |
| Redis 連線失敗 | 跳過快取，直接查詢 DB（降級處理） |
| 使用者請求不支援的語系 | 使用預設語系（`en`）進行回傳，不回傳錯誤 |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| STORE-01 | Integration Test | 正常查詢：pclass 有效且有上架商品 | 回傳 status='1' 的商品，依 sequence ASC |
| STORE-02 | Integration Test | 過濾狀態：資料庫中含有 status='0' 的商品 | 回應中不包含下架商品 |
| STORE-03 | API Test | 多語言：lang=zh-TW 請求 | 回傳商品名稱、描述為繁體中文 |
| STORE-04 | API Test | 缺語系 fallback：lang=ja 但 pnames 無日文 | 回傳預設 en 名稱 |
| STORE-05 | Permission Test | 無 authKey 或錯 token | 401 Unauthorized |
| STORE-06 | Flow Test | pclass 無商品 | 回傳空陣列 []，status 200 |
| STORE-07 | Cache Test | 連續兩次相同請求，第二次命中快取 | 第二次不查 DB，回應與第一次一致 |

---

## 9. 高風險區域
- **高風險 Table**：`product.products_store`（前台核心展示，錯誤的 status 過濾將導致下架商品外洩）。
- **快取一致性**：商品上/下架或內容變更後若未清除快取，用戶端將看到舊資料；需確保管理後台更新時能觸發快取失效（目前機制需人工確認）。
- **全表掃描**：若實作中未強制帶入 `pclass` 條件，將對 Cassandra 造成效能衝擊。
- **多語言洩漏**：若 DTO 映射錯誤，可能將整個 `pnames` map 回傳，暴露未公開語系內容。

---

## 10. 常見錯誤
- ❌ 未過濾 `status='1'`，回傳下架商品。  
  ✅ 所有查詢必須加上此條件。
- ❌ 直接回傳 `pnames` 整個 map。  
  ✅ 前端只需指定語系的一個值。
- ❌ 未依 `sequence` 排序，導致前端顯示混亂。  
  ✅ 應用層必須執行 `OrderBy(sequence)`。
- ❌ 忘記排除 `originalprice` 或 `psource`，可能造成資安或商業機密洩漏。  
  ✅ DTO 組裝時明確指定回傳欄位白名單。
- ❌ Cassandra 查詢未指定 `pclass`，試圖查詢所有商品。  
  ✅ 必須以 `pclass` 作為 partition key 進行查詢。

---

## 11. Evidence
| 類型 | 來源 |
|------|------|
| DB 結構 | `product.products_store` schema：pclass + pid 為 primary key，包含 status、sequence、pnames |
| DB 規則 | [product-detail.md](#) ：「前台查詢商品列表須過濾 status='1'」「originalprice 對外 API 通常不須回傳」 |
| 服務角色 | [pricecentersite-detail.md](#) ：pricecentersite 對 product keyspace 為 reader，僅可讀取 |
| 快取 | [pricecentersite-detail.md](#) Redis 段落：`ResponseCacheInfo:{cacheKey}` 用於 API 回應快取 |
| 驗證機制 | [README.md](#) ：驗證採用 ECCore 3.0.2 內建機制（authKey） |

- 實際 Controller、Service 類別名稱需從程式碼確認（目前為推測，需人工確認）。