# 建立活動商品

## 1. 場景目的

管理後台批次建立活動兌換商品，將商品資料寫入 `payment.products_activity` 表。商品初始狀態為「暫停」(status=0)，庫存量由請求參數指定，建立完成後商品方能於後續流程上架供會員兌換。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/activity/products` | 建立活動商品 (開放請求體為陣列，支援批次建立) |

---

## 3. 流程總覽

1. 接收批次商品建立請求
2. 驗證請求參數 (site、activityEvent、id、price、quantity、names)
3. 寫入 `payment.products_activity` 表，狀態預設為 `status=0` (暫停)
4. 系統自動填入 `updatetime` (當下 Unix timestamp)
5. 寫入成功後回傳 `200`

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ActivityController.CreateProducts` | 接收 `ActivityProduct[]` 陣列 request body |
| 2 | Service | `ActivityService` | 呼叫 `IActivityDataProvider` 逐筆或批次寫入資料 |
| 3 | Provider | `ActivityDataProvider (實作 IActivityDataProvider)` | 組裝 CQL INSERT 語句，寫入 Cassandra `payment.products_activity` 表，自動填入 `updatetime` 時間戳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.products_activity` | Write | 批次寫入或更新活動商品基本資料 (site, activityevent, id, price, quantity, status, names, updatetime) |

> **需人工確認**：Redis 快取 `SportCache:Activity_{site}_{activityEvent}_Products` 在此流程中是否需要主動失效，或由後續商品上架流程 (`status` 變更為 `1`) 才觸發清除。

---

## 6. 重要規則

- **權限限制**：本 API 需要驗證，僅限管理後台角色呼叫
- **欄位限制**：`id`、`site`、`activityevent` 為主鍵的一部分，寫入後不可修改。`price` 與 `quantity` 亦受保護 (詳見寫入限制)
- **狀態值限制**：`status` 初始寫入固定為 `0` (暫停)。`1` (販售中) 與 `2` (售完) 狀態變更需經由 `UpdateSiteActivityEventProductStatus` 方法處理，不可在本 API 直接設定
- **不可暴露資料**：對外 API 應僅回傳對應請求語言的 `names` 值，不可回傳完整 map
- **TTL 規則**：無
- **Transaction 規則**：無，Cassandra 寫入為原子性，但批次多筆寫入需在程式端處理部分失敗的記錄或重試
- **不可修改欄位**：`site`、`activityevent`、`id`

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 缺少必要參數 (如 site, activityevent, id) | 400 Bad Request |
| Request body 為空陣列 | API 正常執行，無資料寫入 |
| Cassandra 寫入失敗 | 500 Internal Server Error，需人工確認是否有部分寫入成功 |
| 重複的 site + activityevent + id (主鍵衝突) | 需人工確認：覆蓋 / 忽略 / 回傳錯誤 (依據處理邏輯) |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| AP-01 | API Test | 傳送合法 ActivityProduct 物件陣列 | 200，DB 查詢可見寫入資料 |
| AP-02 | API Test | 傳送空陣列 `[]` | 200，DB 無任何寫入 |
| AP-03 | Flow Test | 寫入後檢查 status | 所有新增商品的 status 均為 `0` (暫停) |
| AP-04 | API Test | 缺少 activityevent 參數 | 400 回傳 |
| AP-05 | Permission Test | 無驗證 token 或不具權限呼叫 | 401 或 403 |

---

## 9. 高風險區域

- **高風險 table**：`payment.products_activity`，因其為活動兌換庫存數據核心，寫入後 `site`、`activityevent`、`id` 無法修改
- **高風險 API**：無。本 API 為單一寫入操作，不涉及交易或橫跨多服務同步

---

## 10. 常見錯誤

- 誤解 `status` 欄位語意，將 `0` 視為「啟用」、「有效」狀態，實則為「暫停」。應依循 `AppDefine.ActivityProductStatus` 與文件定義
- 嘗試在一次建立請求中設定 `status=1` (販售中)，此應通過獨立的商品狀態更新流程進行
- 未採用批次建立，而逐筆多次呼叫相同 API，缺乏效率

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `ActivityController` (根據 OpenAPI 路由 `/api/v1/activity/products` POST) |
| DB | `payment.products_activity` (db/payment-detail.md, db/payment.md) |
| Code | `IActivityDataProvider`, `ActivityService` (Phase0/1 source semantics) |
| Status 規則 | `db/payment-detail.md` - status 欄位值定義 (`0` 暫停) |