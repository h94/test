# 建立商城商品

## 1. 場景目的

管理後台人員透過 API 新增一筆商城商品資料，寫入 `products_store` 表，預設為下架狀態，供後續上架與兌換使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/store/products` | 新增商城商品，需後台驗證 |

---

## 3. 流程總覽

1. 呼叫端攜帶有效管理員 Token 請求 `POST /api/v1/store/products`。
2. Controller 驗證 Token 權限（後台角色）。
3. Service 層執行領域邏輯驗證：
   - 檢查必要欄位（pclass、pnames、price、originalprice 等）。
   - 檢查多語言 Map 不可為空，且 key 為有效語言代碼。
4. Provider 層產生商品 ID（`pid`）並設定預設狀態為下架（`"0"`）。
5. 寫入 `products_store` 至 Cassandra（無 Transaction）。
6. 回傳新建立商品資料（或成功訊息）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `StoreController.CreateProduct` | 接收請求，委派 Service |
| 2 | Service | `StoreProductService.CreateProduct` | 驗證輸入，組裝 ProductStore 物件 |
| 3 | Provider | `ProductStoreDataProvider.InsertProductStore` | 產生 `pid`，設定 `status="0"`，寫入 Cassandra |
| 4 | - | - | 回傳建立結果 |

> **需人工確認**：實際類別名稱依據程式碼，以上為推斷。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | product.products_store | INSERT | 寫入商品基本資料，預設 status="0" |
| Redis | - | 無 | 本次建立不涉及快取；Redis 僅供查詢服務使用 |
| Kafka/Queue | - | 無 | 不透過佇列 |

---

## 6. 重要規則

- **權限限制**：僅含管理員角色（如 `Admin`）之 Token 可呼叫。
- **欄位限制**：
  - `pclass` 必須是系統允許的商品分類之一（需人工確認來源，可能來自 `AppDefine` 或 `options` 表）。
  - `pnames`、`description`、`image_path` 為 `map<text, text>`，不可為空，key 須為有效語言代碼（如 `zh-CN`, `en`）。
  - `price`、`originalprice` 建立後不可單獨 UPDATE，若要修改需整筆重建。
- **預設值**：`status` 寫入 `"0"`（下架），不可由前端指定。
- **不可修改欄位**：`pid`（自動產生）、`pclass`（寫入後不可變更）、`psource`（若有）、`lastup_time`（系統時間）。
- **Transaction**：無跨表交易，僅單一 INSERT。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未帶合法管理員 Token | 401 Unauthorized |
| pclass 為空或不在允許清單 | 400 BadRequest，提示分類無效 |
| pnames 為空 map | 400 BadRequest，提示多語言名稱必填 |
| price / originalprice 為負數或未填 | 400 BadRequest |
| Cassandra 寫入失敗 | 500 Internal Server Error |
| 重複 pid（理論上不應發生） | 可能覆蓋？系統應保證 pid 唯一性 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| TC01 | Permission | 以無管理權限 Token 呼叫 | 401 Unauthorized |
| TC02 | API | 缺少 pnames | 400 BadRequest |
| TC03 | API | 多語言 Map 中包含無效語言代碼 | 400 BadRequest 或忽略？需人工確認 |
| TC04 | API | 提供完整合法資料 | 200 OK，商品建立且 status="0" |
| TC05 | Flow | 建立後查詢商品 | 可透過 GET /api/v1/store/products/{pclass}/{pid} 取得，但前台因 status="0" 不顯示 |
| TC06 | DB | 驗證 products_store 寫入內容 | 各欄位正確，lastup_time 為當前時間戳 |

---

## 9. 高風險區域

- **高風險 table**：`products_store` — 為商城核心商品表，錯誤價格或狀態會直接影響使用者兌換。
- **價格欄位保護**：`price` / `originalprice` 建立後不可單一欄位更新，後續若需調整須重建商品，需有妥善設計避免資料不一致。
- **多語言寫入**：Map 型態容易因 key 重複或覆蓋造成既有語言內容遺失，需確保新增語言條目時不覆蓋其他語系（此處為全新建立，無此風險）。
- **無庫存概念**：建立商品時不涉及庫存（庫存透過 `product_store_stock_logs` 管理），但 `status` 預設下架，確保不會意外曝光。

---

## 10. 常見錯誤

- ❌ 前端嘗試在 Request Body 中傳入 `status` 欄位 → 後端應忽略或拒絕，強制設為 `"0"`。
- ❌ 誤把 `pnames` 當成字串傳送，而非 `map<text, text>` → 應使用物件格式（如 `{"zh-CN":"商品名","en":"Product Name"}`）。
- ❌ 將 `price` 設為 0 而未檢查業務規則 → 建議後端校驗 `originalprice > 0` 及 `price > 0`。
- ❌ 建立後直接透過其他 API 更新 `price` 欄位 → 應拒絕，引導使用重建流程。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | productservice README：`POST /api/v1/store/products` |
| DB schema | `product.products_store` (db/product.md) |
| DB write rule | product-detail.md：`status` 預設 `"0"`，僅 `UpdateStoreProductStatus` 可寫入；`price/originalprice` 一次寫入不可單獨更新 |
| Code semantics | ProductStoreDataProvider (from phase1 batch-3) 寫入 products_store |
| Status enum | AppDefine.StoreProductStatus："0"下架，"1"上架 |
| Auth rule | README 標示需驗證；ECCore 內建機制（需後台權限） |

---

**需人工確認事項**：
- `pclass` 允許值清單來源（可能為 `AppDefine` 或 `options` 表）。
- 建立時若傳入 `popular`、`sequence` 等欄位是否接受。
- 若 `pnames` 中語言代碼不合法，系統是拒絕還是忽略。
- Redis 快取 `product:store:{pclass}:{pid}` 是否需要在建立後主動 SET 或 DELETE（目前由 inplayzsubscriptionsystem 負責，productservice 建立時可能不需動作，但可能導致快取不一致，建議主動發送訊息使其失效）。