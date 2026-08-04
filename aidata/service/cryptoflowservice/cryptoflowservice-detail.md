# cryptoflowservice — DB 操作邊界

> 產出時間：2025-05-05 15:30  
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）  
> ⚠️ AI 產出，需資深工程師審核後生效

---

## product

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra product | owner | Schema：[db/product.md](../../db/product.md) · 語意：[db/product-detail.md](../../db/product-detail.md) |

### 寫入限制

- **product_store_redeem_logs.account / phonenumber / address / recipient**：僅兌換 API 可寫入；不可由其他業務直接 INSERT 或 UPDATE。
- **product_store_redeem_logs.status**：僅系統流程（兌換建立、出貨、完成）可變更；不可由管理後台直接覆寫。
- **products_store.price / originalprice**：價格欄位（分單位）僅商品管理 API 可寫入；不允許直接透過唯讀查詢後回寫。
- **products_store.quantity（透過 product_store_stock_logs）**：庫存增減僅能透過寫入 stock_logs 觸發；不可直接 UPDATE products_store 庫存欄位。
- **products_activity.quantity / price / status**：僅活動管理 API 可寫入；一般兌換流程不可修改活動庫存。

### 讀取規則

- **商店商品列表查詢**：WHERE status = 'active' AND popular = true（僅顯示上架且熱門商品）。
- **活動查詢**：WHERE status = 1（僅顯示啟用的活動）。
- **兌換記錄查詢**：需依 account 篩選，返回該使用者自己的兌換記錄。
- **庫存變更查詢**：需過濾 addtime 時間範圍，避免全表掃描。
- **商品詳細查詢**：依 pclass + pid 組合作為主鍵條件。

### 不可回傳欄位

- **product_store_redeem_logs.account**：使用者帳號，資安敏感，不對外 API 回傳。
- **product_store_redeem_logs.phonenumber**：電話號碼，資安敏感。
- **product_store_redeem_logs.address**：完整地址，資安敏感。
- **product_store_redeem_logs.cname / cname**：客戶姓名，資安敏感。
- **product_store_redeem_logs.cheadshot**：客戶頭像 URL，可能含個人資訊。
- **product_store_redeem_logs.cmemo**：客戶備註，內部資訊。
- **products_activity.names**：活動多語言名稱 map，內部管理用途。

---

## Redis

本服務目前無使用 Redis。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 支付處理 | payment-service | 兌換流程不處理金流，僅記錄兌換請求與結果。 |
| 使用者帳戶餘額/點數管理 | account-service | 兌換扣款非本服務職責，改由 account-service 處理。 |
| 商品圖片儲存與 CDN | storage-service | 僅記錄 image_path 路徑，不處理檔案上傳與儲存。 |

---

## 常見錯誤

- ❌ 查詢兌換記錄時未依 account 過濾，導致回傳跨使用者敏感資料。  
  ✅ 所有兌換記錄 API 必須加入 WHERE account = :account 條件。
- ❌ 直接 UPDATE products_store.quantity 欄位造成庫存不一致。  
  ✅ 庫存異動應寫入 product_store_stock_logs 並透過 sum(log) 計算。
- ❌ 兌換請求未驗證 products_activity.status = 1 即建立兌換記錄。  
  ✅ 兌換前必須確認活動狀態為啟用（status = 1）且庫存足夠。