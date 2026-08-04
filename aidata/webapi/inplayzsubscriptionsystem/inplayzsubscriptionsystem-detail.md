# inplayzsubscriptionsystem — DB 操作邊界

> 產出時間：2025-03-27 14:00  
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）  
> ⚠️ AI 產出，需資深工程師審核後生效

---

## product

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Product Cassandra | owner | Schema：[db/product.md](../../db/product.md) · 語意：[db/product-detail.md](../../db/product-detail.md) |

### 寫入限制

- **`account`**（`product.product_store_redeem_logs`, `product.products_activity_redeem_logs`, `product.withdrawlogs_activity`）：僅由兌換/提現請求寫入，不可由管理後台直接修改；寫入時需與當前登入 token 綁定。
- **`phonenumber`、`address`、`recipient`**（`product_store_redeem_logs`）：兌換瞬間由使用者填入，兌換完成後不可修改；管理後台不可直接 UPDATE。
- **`contactnumber`**（`withdrawlogs_activity`）：僅在提現請求時由用戶填寫，寫入後不可修改；管理後台不可直接 UPDATE。
- **`status`**（兌換記錄表）：`product_store_redeem_logs.status` 僅能由內部發貨流程（ship）或退款流程更新，不可由外部 API 改寫。  
  `products_activity_redeem_logs.status` 僅能由活動結算或取消流程更新。  
  `withdrawlogs_activity.status` 僅能由活動提現結算流程更新，不可由外部 API 直接改寫。
- **`price`、`originalprice`**（`products_store`）：僅在商品建立時設定，後續不可透過兌換 API 變更。
- **`quantity`**（`product_store_stock_logs`）：僅能透過庫存增減操作（扣庫、補庫）寫入，且須與事務鎖確保原子性；不可直接 DELETE。
- **`addtime`**（所有表，`withdrawlogs_activity` 除外）：寫入後不可修改，由服務端時間戳自動填入。
- **`updatetime`**（所有記錄表）：由服務端自動維護，不允許外部手動寫入。

### 讀取規則

- **商品列表查詢**（`products_store`）：須過濾 `status = '上架'`，僅顯示熱門或按 `sequence` 排序；不顯示下架商品。
- **活動查詢**（`products_activity`）：僅回傳 `status = 1`（啟用）的活動；若活動庫存 `quantity <= 0` 應主動隱藏。
- **兌換記錄查詢**（`product_store_redeem_logs`、`products_activity_redeem_logs`）：非管理端 API 僅能查詢當前登入使用者的記錄（以 `account` 過濾），不可跨帳號查詢。
- **提現記錄查詢**（`withdrawlogs_activity`）：非管理端 API 僅能查詢當前登入使用者的記錄（以 `account` 過濾），不可跨帳號查詢。
- **庫存查詢**（`product_store_stock_logs`）：需按 `pclass` + `pid` 聚合計算總量，不可直接回傳明細。
- **多語言欄位**（`pnames`、`description`、`image_path`、`names`）：對外輸出時需根據 Accept-Language 或 tenant 配置只回傳對應語系的 value，不可直接回傳整個 map。

### 不可回傳欄位

- **`phonenumber`、`address`、`recipient`**（`product_store_redeem_logs`）：任何 GET API 不可回傳；僅供內部訂單處理或管理後台受權限控制查詢。
- **`contactnumber`**（`withdrawlogs_activity`）：任何 GET API 不可回傳；僅供內部處理或管理後台受權限控制查詢。
- **`account`**（兌換記錄表、提現記錄表）：一般商品列表、庫存等查詢不可回傳；僅在「我的兌換記錄/提現記錄」或管理端可回傳。
- **`cheadshot`**（客戶頭像 URL）：資安敏感，預設不回傳；僅管理介面可選。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `product:store:{pclass}:{pid}` | 商品查詢時快取單一商品資訊 | 30 秒，或當商品狀態/庫存變更時主動 DEL |
| SET / GET | `product:activity:{site}:{activityevent}` | 活動列表或單一活動查詢 | 10 秒，活動開始前/結束後可加大 TTL |
| INCR / DECR (Lua) | `product:stock:{pclass}:{pid}` | 兌換扣庫時原子增減 | 無 TTL（庫存常駐），配合資料庫鎖使用 |

> 說明：本服務基於產品代碼推測使用 Redis 做商品快取與庫存水位控制；實際 Key 前綴及使用方法請以 source code 為準。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 使用者身份驗證 / Token 發放 | member / auth service | 兌換請求中 `account` 與 token 的綁定校驗由上游服務完成 |
| 付款處理 / 點數扣減 | payment / wallet service | 商品兌換需先確認 wallet 餘額後才寫入兌換記錄 |
| 商品圖片與多語言內容管理 | admin / CMS service | `image_path`、`pnames` 等內容由後台管理系統維護，本服務僅讀取 |
| 活動排程 / 時效控制 | activity scheduler | 活動啟用/停用時機由排程服務觸發，本服務只依 `status` 判斷 |

---

## 常見錯誤

- ❌ 兌換時直接 INSERT `product_store_redeem_logs` 而未檢查庫存（`quantity` 是否足夠）  
  → ✅ 應使用 Lua 腳本或資料庫事務鎖先檢查庫存，庫存不足時拒絕寫入並回傳錯誤。
- ❌ 管理後台直接 UPDATE `status` 為「已發貨」而未記錄 `deliverytime`  
  → ✅ 應由專門的發貨流程同時更新 `status` 與 `deliverytime`，並寫入操作日誌。
- ❌ 對外 API 回傳 `products_store` 時未過濾 `status`，導致下架商品仍被展示  
  → ✅ 查詢語句務必加上 `WHERE status = '上架'`，並可用 Redis 快取生效中的商品清單。
- ❌ 活動商品兌換時僅檢查活動 `quantity`，忽略實際 `products_store` 庫存  
  → ✅ 活動庫存與商品庫存需分開檢查：活動庫存不足時不允許建立兌換記錄，後續再由排程同步減扣商品庫存。
- ❌ 「我的兌換記錄」或「我的提現記錄」未以 `account` 過濾，回傳了全站記錄  
  → ✅ 任何非管理端 API 必須加上 `WHERE account = :currentUser` 條件，防止資料洩露。