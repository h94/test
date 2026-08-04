# currencyservice — DB 操作邊界

> 產出時間：2025-04-02 19:00  
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）  
> ⚠️ AI 產出，需資深工程師審核後生效

---

## product

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra product | owner | Schema：[db/product.md](../../db/product.md) · 語意：[db/product-detail.md](../../db/product-detail.md) |

### 寫入限制

- **products_activity**  
  `id`：系統或活動後台生成，不可由外部寫入；`site`、`activityevent`、`id` 組成複合主鍵，建立後不可修改。  
  `price`、`quantity`、`status`：僅活動管理後台 API 可變更。  
  `names`（多語言名稱）：僅管理介面提供。  
  `updatetime`：系統自動維護，不可手動設定。

- **products_activity_redeem_logs**  
  `id`：系統生成。  
  `status`：僅兌換確認 API（完成/取消）可更新。  
  `pid`、`account`：寫入後永久不可變更。  
  `activityevent`、`site`：依活動上下文賦值，寫入後不可改。  
  `addtime`、`updatetime`：系統時間。

- **products_store**  
  `pclass` + `pid` 複合主鍵不可異動。  
  `price`、`originalprice`、`popular`、`sequence`、`status`、`pnames`、`description`、`image_path`：僅商品管理後台 API 可寫入。  
  `psource`：可選欄位，由後台填寫。  
  `lastup_time`：系統自動記錄。

- **product_store_redeem_logs**  
  `id`：系統自動產生。  
  `status`：僅兌換流程 API 控制狀態流轉（pending → shipped → completed / cancelled）。  
  `account`、`recipient`、`phonenumber`、`address`、`cname`、`cheadshot`、`cmemo`：建立時由用戶提供，一經寫入即不可修改（如需變更應新增記錄）。  
  `pclass`、`pid`：建立後不可變更。  
  `addtime`、`updatetime`、`deliverytime`：系統管理。

- **product_store_stock_logs**  
  `id`：系統生成。  
  `quantity`：僅能經由庫存增減 API 以正/負值寫入（記錄變動量），不允許直接覆蓋絕對值。  
  `pclass`、`pid`：建立後不可變更。  
  `addtime`、`updatetime`：系統維護。

- **withdrawlogs_activity**  
  `cid`：提現記錄 ID，系統自動分配，不可外部指定。  
  `status`：僅提現流程 API 可更新（審核中、完成、拒絕等）。  
  `account`、`site`、`activityevent`：建立後不可修改。  
  `contactnumber`：建立時由用戶提供，寫入後即為固定（敏感資料保護）。  
  `updatetime`：系統時間。

### 讀取規則

- **商品列表查詢** (`products_store`)：僅回傳 `status = '1'`（上架）的商品；可依 `pclass` 過濾，並以 `sequence` 正序排序；熱門推薦須附加 `popular = true`。
- **商品詳情查詢** (`products_store`)：以 `pclass` + `pid` 精確查詢，且務必確認 `status` 為上架。
- **活動商品查詢** (`products_activity`)：回傳 `status = 1` 且 `quantity > 0` 的記錄；可透過 `activityevent` 或 `id` 過濾。
- **活動兌換記錄查詢** (`products_activity_redeem_logs`)：必須同時過濾 `site = :site` 與 `account = :account`；可附加 `status` 條件。
- **實體商品兌換記錄查詢** (`product_store_redeem_logs`)：需過濾 `account = :account`，按 `addtime` 降序取得近期記錄；可依 `status` 篩選。
- **庫存異動查詢** (`product_store_stock_logs`)：依據 `pclass` + `pid` 過濾，以 `addtime` 降序查看歷史變動。
- **提現記錄查詢** (`withdrawlogs_activity`)：需過濾 `site = :site` 與 `account = :account`，可依 `status` 篩選，並以 `updatetime` 降序排列。

### 不可回傳欄位

- `account`（所有表）：使用者帳號，對外 API 不應直接回傳，宜改用 token 或遮罩。
- `product_store_redeem_logs`：`address`、`phonenumber`、`recipient`、`cheadshot`、`cmemo` — 個人資料與聯絡資訊，僅內部出貨流程使用，不得對外揭露。
- `withdrawlogs_activity`：`contactnumber` — 電話號碼隱私，必須排除。

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