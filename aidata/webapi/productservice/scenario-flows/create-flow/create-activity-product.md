# 建立活動商品

## 1. 場景目的
管理員透過後台建立活動商品，將商品資訊寫入活動商品表，供前台活動兌換使用。此流程包含價格、庫存、多語系名稱與初始狀態的設定。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/activity/products` | 新增活動商品，需驗證 |

---

## 3. 流程總覽

1. 接收帶有 `ActivityProduct` 物件的請求
2. 驗證呼叫者身分（後台管理員權限）
3. 參數校驗（必填、數值範圍、多語系格式）
4. 產生商品 ID（若未提供）
5. 設定系統欄位（`updatetime`）
6. 寫入 `products_activity` 表（**keyspace 待人工確認：product 或 payment**）
7. 回傳成功回應

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ActivityController.Post` | 接收請求，呼叫 Service |
| 2 | Service | `ActivityService.CreateActivityProduct` | 商業邏輯處理 |
| 3 | Provider | `IActivityDataProvider.CreateActivityProduct` | 組裝 INSERT 語句，寫入 Cassandra |
| 4 | Transfer | `ActivityProduct` | Request/Response DTO 對映 |

> **注意**：實際類別與方法名稱因無原始碼證據，為推測命名。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `products_activity` (Cassandra) | Write (INSERT) | 新增一筆活動商品記錄 |
| Cache | 無直接操作 | — | 本服務不操作活動商品快取（由 `inplayzsubscriptionsystem` 管理） |

---

## 6. 重要規則

- **權限限制**：僅後台管理員可呼叫，需通過 ECCore 驗證（具體角色需人工確認）
- **欄位限制**：
  - `site`、`activityevent`：必填，為 Partition Key 的一部分，不可後續修改
  - `price`、`quantity`：建立時必填，後續不允許單一欄位更新（若需修改應整筆重建）
  - `names`：必填，型態 `map<text, text>`，key 須為有效語言代碼（如 `zh-CN`、`en`），不可為空 map
  - `status`：傳入值需符合定義（0-暫停、1-販售中、2-售完），但**寫入規則衝突**（見下方）
- **狀態寫入規則衝突**：
  - `product-detail.md`：INSERT 預設 `status=1`（販售中）
  - `payment-detail.md`：INSERT 預設 `status=0`（暫停）
  - 兩者皆宣稱 `productservice` 為 owner
  - **需人工確認**實際預設值及 API 是否允許直接傳入 `status`
- **不可修改欄位**：`site`、`activityevent`、`id`（寫入後不可變更）
- **ID 規則**：若請求未提供 `id`，由系統自動產生（UUID）；若提供則需確保唯一性
- **Transaction 規則**：Cassandra 無跨表交易，僅單表原子寫入

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未驗證或權限不足 | 回傳 401 / 403 |
| 缺少必填欄位（site/activityevent/price/quantity） | 回傳 400 並提示欄位缺失 |
| `price` 或 `quantity` 為負數 | 回傳 400 並提示數值無效 |
| `names` 為空 map 或 key 非有效語言代碼 | 回傳 400 並提示格式錯誤 |
| `status` 超出 0/1/2 範圍 | 回傳 400 並提示狀態值無效 |
| `id` 重複（若前端傳入） | INSERT 失敗，回傳 409 或 500 |
| Cassandra 寫入失敗 | 回傳 500，記錄錯誤日誌 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| AC-01 | API Test | 正確參數建立活動商品 | 201 Created，可透過 GET 查詢到該商品 |
| AC-02 | Permission Test | 無 token 呼叫 | 401 Unauthorized |
| AC-03 | Validation Test | 缺少 site | 400 Bad Request |
| AC-04 | Validation Test | names 為空 map | 400 Bad Request |
| AC-05 | Flow Test | 寫入後查詢（GET）確認快取更新 | 前端查詢可取得新商品（若快取由外部服務管理，則需確認快取失效機制） |

---

## 9. 高風險區域

- **高風險 table**：`products_activity` — 直接寫入可能繞過狀態變更控制，若 API 允許任意設定 `status`，可能跳過審核流程
- **快取一致性**：本服務不管理活動商品快取，但外部服務（`inplayzsubscriptionsystem`）依賴快取。新增商品後若未清除快取，前端可能無法立即看到
- **權限控制**：必須確保只有後台管理員能操作，避免一般使用者建立活動商品

---

## 10. 常見錯誤

- ❌ 直接在前端傳入 `status` 為任意值，而未遵循後台標準流程（應由 `CreateActivityProduct` 方法統一設定初始狀態）
- ❌ 建立後試圖用 PUT 單獨修改 `price` 或 `quantity` → 應整筆重建
- ❌ 忘記驗證 `names` 的語言代碼，寫入無效 key → 應嚴格檢查
- ❌ 誤以為本服務會操作 Redis 快取 → 實際上快取由其他服務負責，若有依賴需排程清除

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI: `/api/v1/activity/products` POST |
| DB | `products_activity` (keyspace 待人工確認：`product` or `payment`) |
| Schema | `product/products_activity` 或 `payment/products_activity` |
| 寫入限制 | `product-detail.md` / `payment-detail.md` |
| 權限 | README: 需要驗證；實際角色需人工確認 |

---

## 12. 待人工確認事項

1. 活動商品實際存放的 keyspace 為 `product` 還是 `payment`？目前兩處皆有同名表，需釐清唯一資料源
2. `status` 的預設值：建立時是 0（暫停）還是 1（販售中）？API 是否允許傳入 `status` 參數？
3. 管理員權限細節：需要何種角色或 Claim？
4. 新增商品後，是否需要主動通知其他服務清除快取？