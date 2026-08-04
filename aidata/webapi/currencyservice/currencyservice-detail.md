# currencyservice — DB 操作邊界

> 產出時間：2025-04-02 11:00  
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）  
> ⚠️ AI 產出，需資深工程師審核後生效

---

## product

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra product | owner | Schema：[db/product.md](../../db/product.md) · 語意：[db/product-detail.md](../../db/product-detail.md) |

### 寫入限制

- **product_store_redeem_logs**：`id`（記錄 ID）僅系統自動生成，不可由外部寫入；`status` 僅允許透過兌換流程 API 更新（初期 `pending` → `shipped` → `completed` / `cancelled`）；`account`、`recipient`、`phonenumber`、`address` 一經建立不可修改，需變更時應新增一筆記錄。
- **product_store_stock_logs**：`quantity`（庫存變動量）僅能經由庫存增減 API 寫入（增加時正值、扣減時負值），不允許直接覆蓋；`id` 由系統內部產生。
- **products_activity**：`price`、`quantity`、`status` 僅活動管理後台 API 可修改；`names`（多語言名稱）僅後台維護介面可寫入。
- **products_activity_redeem_logs**：`status` 僅兌換確認（完成/取消）API 可更新；`pid`、`account` 寫入後不可變更。
- **products_store**：`price`、`originalprice`、`popular`、`sequence`、`status`、`pnames`、`description`、`image_path` 僅商品管理後台 API 可寫入；`pclass` + `pid` 為複合主鍵，寫入後不可修改。

### 讀取規則

- **商品列表查詢**：僅回傳 `status = 'active'` 且 `popular = true` 的商品（前台熱門推薦），或指定 `pclass` 後依 `sequence` 正序排序。
- **商品詳情查詢**：透過 `pclass` + `pid` 精確查詢，且 `status` 必須為 `active`（下架/隱藏商品不應顯示）。
- **兌換記錄查詢（單一帳號）**：需過濾 `account = :account`（防止跨帳號查詢），通常以 `addtime` 降序取得最近記錄；若狀態過濾，需加上 `status = 'completed'` 或 `'pending'` 等。
- **活動商品查詢**：回傳 `status = 1`（啟用）且 `quantity > 0` 的活動記錄；以 `id` 或 `activityevent` 為過濾條件。
- **活動兌換記錄查詢**：需同時過濾 `site = :site` 與 `account = :account`；必要時加 `status` 條件。

### 不可回傳欄位

- `product_store_redeem_logs`：`account`（帳號敏感）、`address`（地址隱私）、`phonenumber`（電話隱私）、`recipient`（收件人姓名隱私）、`cheadshot`（頭像可能視為個人資訊）、`cmemo`（備註可能含敏感內容）  
  **原因**：高敏感性個人資料，僅內部管理或發貨流程使用，對外 API 不應出現。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| 未使用 | — | — | — |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 商品上下架與活動創建 | productservice（假設） | 新增/啟用/停用商品、活動設定由商品後台服務管理，currencyservice 僅讀取已啟用資料並處理兌換。 |
| 庫存總量管理 | productservice（假設） | 商品總庫存（`products_store` 無明顯庫存欄位）應由獨立庫存服務管理，currencyservice 僅記錄庫存變動日誌。 |

---

## 常見錯誤

- ❌ 在兌換記錄中直接更新 `address`、`phonenumber` 等收件資訊 → 應維持不可變設計，若收件資訊變更應新增一筆兌換記錄，而非修改既有記錄。
- ❌ 讀取商品列表時未過濾 `status = 'active'` → 可能將已下架或隱藏商品回傳給前端。
- ❌ 兌換庫存時直接更新 `product_store_stock_logs` 的 `quantity` 為剩餘值 → 應使用增減值（正/負）而非絕對值，以保留完整庫存軌跡。
- ❌ 未檢查 `products_activity.quantity` 即寫入兌換記錄 → 應在兌換前先確保活動庫存充足，否則應拒絕並回寫錯誤日誌。