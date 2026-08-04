# 更新活動商品資訊 (PUT /api/v1/activity/products)

## 1. 場景目的

提供後台管理員整筆重建活動商品（products_activity）的功能。因應業務規則「price / quantity / names 僅在建立時一次性寫入，後續不允許單一欄位更新，須整筆重建」，本 API 作為整筆重建的入口，確保商品內容（名稱、價格、數量）可被安全地整體替換，同時嚴格控制狀態（status）的變更權限。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | /api/v1/activity/products | 整筆更新活動商品，body 為 ActivityProduct JSON |

---

## 3. 流程總覽

1. 接收 PUT 請求，body 包含 site、activityevent、id、price、quantity、names、status（可能）等。
2. 驗證 API 呼叫者的後台管理權限（Token 驗證，需確認：從哪個服務驗證？authservice？）。
3. 檢查 request body 的 site、activityevent、id 是否已存在於 `product.products_activity`（或 `payment.products_activity`，需人工確認 primary keyspace）。
4. 驗證 price、quantity 為正整數，names map 的 key 為有效語言代碼（zh-CN、en 等），且 map 不可為空。
5. 特別檢查：若 body 包含 status，僅允許後台且必須透過 `UpdateSiteActivityEventProductStatus` 方法寫入 → **此處可能拒絕直接由 PUT 修改 status**（需人工確認）。
6. 執行整筆覆蓋寫入（INSERT 或 UPDATE）：在 Cassandra 中，使用相同的 partition key（site, activityevent, id）進行 INSERT，覆蓋原有 row。
7. 更新 `updatetime` 欄位為當前 Unix 時間戳（秒）。
8. 清除相關 Redis 快取 key：`product:activity:{site}:{activityevent}` 或類似 pattern，確保後續查詢取得最新資料。
9. 回傳 200 OK。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Middleware | 驗證機制（ECCore） | 檢查 Bearer Token 有效性 |
| 2 | Controller | ActivityController.PutProduct(...) | 接收 body，轉遞給 Service |
| 3 | Service | ActivityService.UpdateProduct(...) | 業務邏輯：驗證參數、檢查商品存在性、決定是否允許更新 status、決定寫入方式 |
| 4 | Provider / DataProvider | IActivityDataProvider.ReplaceActivityProduct(...) | 對 Cassandra 執行 INSERT（整筆覆蓋） |
| 5 | Provider / CacheProvider | RedisCacheProvider.RemoveAsync(key) | 刪除活動商品快取 |

*（實際類別與方法名需對照原始碼，上述為合理推斷）*

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | product.products_activity（或 payment.products_activity） | INSERT（覆蓋） | 整筆更新活動商品資料 |
| DB | product.products_activity（或 payment.products_activity） | SELECT（WHERE site=.. AND activityevent=.. AND id=..） | 確認商品存在 |
| Cache | Redis：`product:activity:{site}:{activityevent}` | DELETE | 清除活動商品快取，強制下次查詢讀 DB |

---

## 6. 重要規則

- **權限限制**：僅限後台管理角色呼叫，需透過認證服務驗證 Token，且操作者須有管理活動商品的權限（後台 API 權限）。
- **欄位限制**：
  - `price`、`quantity`、`names` 不可單獨透過 partial update 修改，必須整筆重建（本 API 為整筆重建）。
  - `status` 欄位：依 `productservice-detail.md`，僅能透過 `UpdateSiteActivityEventProductStatus` 方法寫入，因此 **PUT 不應允許改變 status**。若允許，則違反規則，需人工確認。
  - `updatetime` 由系統自動設定，不可由 client 指定。
- **不可暴露資料**：對外 API 不應回傳內部主鍵或其他敏感資訊，但本 API 為後台操作，回傳內容可適當包含完整資料。
- **多語言規則**：`names` 為 `map<text, text>`，key 必須為有效語言代碼（如 `zh-CN`、`en`），map 不可為空；寫入時不可覆蓋既有語系，但整筆重建時必須提供完整 map，應確保至少包含一個語言條目。
- **Cassandra 覆蓋特性**：由於 Cassandra 的 INSERT 本質是 upsert，整筆重建實際上是以相同主鍵寫入，會完全覆蓋舊 row。因此不存在 transaction 問題，但需注意不可並發寫入導致資料競爭（需人工確認是否有樂觀鎖或 compare-and-set 機制）。
- **快取一致性**：更新後必須立即清除活動商品相關快取（`product:activity:{site}:{activityevent}`），不可只靠 TTL 自然過期。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|-----------|
| 未提供認證 Token 或 Token 無效 | 401 Unauthorized |
| 操作者無後台管理權限 | 403 Forbidden |
| 請求 body 中 site、activityevent、id 任一為空 | 400 Bad Request（驗證失敗） |
| 指定的 site+activityevent+id 對應的商品不存在 | 404 Not Found 或 422 Unprocessable Entity |
| `price` 或 `quantity` 為負值或非整數 | 400 Bad Request |
| `names` map 為空或 key 非合法語言代碼 | 400 Bad Request |
| body 中包含 status 且值非預期枚舉（0,1,2）或試圖變更 status | **需人工確認**：可能拒絕並回 422，或由 Service 無視 status 寫入其他欄位 |
| 資料庫寫入失敗（Cassandra 不可用） | 500 Internal Server Error |
| Redis 清除快取失敗 | 仍應回傳成功（因主要資料已更新），可記錄錯誤並觸發告警 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC01 | API Test | 正常整筆更新價格、數量、名稱，所有欄位合法 | 200，資料庫查詢回傳更新後的值 |
| TC02 | Permission Test | 無 Token 或使用一般使用者 Token 請求 | 401 或 403 |
| TC03 | Flow Test | 更新已售完的活動商品（status=2），僅修改 names | 200，status 維持 2 |
| TC04 | Flow Test | 嘗試在 body 中將 status 從 1 改為 0 | **需人工確認**：預期拒絕或忽略 status 變更；根據規則應不允許 |
| TC05 | API Test | names map 為空 | 400 Bad Request |
| TC06 | API Test | 指定不存在的 site+activityevent+id | 404 Not Found |
| TC07 | Cache Test | 更新後立即 GET 該活動商品列表 | 回傳最新資料（快取已清除） |
| TC08 | Idempotency | 連續兩次發送相同 PUT 請求 | 第二次仍成功，資料無變化 |

---

## 9. 高風險區域

- **活動商品狀態誤改**：若 PUT 不慎允許修改 `status`，可能導致未審核或未上架商品被強制上架，或販售中商品被誤停，造成業務混亂。
- **多語言資料覆蓋**：整筆重建時若 client 未提供完整 `names` map，可能丟失其他語系內容。需確保 client 傳入完整的多語言字典。
- **快取未清除**：若清除 Redis 失敗，可能導致前端仍顯示舊資料，造成不一致；需有重試或監控告警機制。
- **並發更新**：多個管理員同時對同一活動商品進行整筆重建，由於 Cassandra 無行級鎖，後寫入者會覆蓋先寫入者的變更。需考慮前端提示或引入樂觀鎖（例如 based on `updatetime` 版本檢查）。
- **未檢查商品存在性**：直接 INSERT 覆蓋可能意外創建新商品（若主鍵誤填）。應先 SELECT 確認存在，或由 Cassandra 輕量級事務（IF EXISTS）控制，但目前產品未使用此機制。**需人工確認**目前實作是否有檢查存在性。

---

## 10. 常見錯誤

- ❌ 誤將 PUT 用於部分更新（如只修改價格）而不整筆重建 → 違反 price/quantity 欄位更新規則，可能導致遺失其他欄位資料（因為 Cassandra 覆蓋）。
- ❌ 忘記清除 Redis 快取 → 前端顯示舊資料。
- ❌ 未對 `names` map 做語言代碼驗證 → 可能寫入無效語系，導致多語言顯示異常。
- ❌ 前端擅自將 `status` 傳入並嘗試變更 → 若後端未強制阻擋，可能破壞狀態機的流程。
- ❌ 未檢查 id、site、activityevent 對應的活動商品是否存在，直接 INSERT 造成幽靈資料。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI: PUT /api/v1/activity/products |
| DB | table: product.products_activity (keyspace 待確認) |
| 規則 | productservice-detail.md: products_activity.price/quantity/names 僅在 CreateActivityProduct 時一次寫入，後續不允許單一欄位更新；若要修改需整筆重建 |
| 規則 | productservice-detail.md: products_activity.status 僅透過 UpdateSiteActivityEventProductStatus 寫入 |
| 快取 | product-detail.md: Redis key `product:activity:{site}:{activityevent}`，更新時需 DEL |
| 權限 | README: 所有活動商品 API 均需要驗證 |

---

*本文件依現有規格推斷產生，部分流程細節（如 status 能否透過 PUT 修改、是否檢查商品存在性、實際 Service 方法簽名）**需人工確認**實際程式碼與團隊開發規範。*