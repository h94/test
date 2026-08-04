# cryptoflowservice — DB 操作邊界

> 產出時間：2025-05-05 16:00  
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）  
> ⚠️ AI 產出，需資深工程師審核後生效

---

## product

<!-- 本次觸發 db 為 product，增量更新本節內容，其餘章節沿用既有 -->

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra product | owner | Schema：[db/product.json](../../db/product.json) · 語意：[db/product-detail.md](../../db/product-detail.md) |

### 寫入限制

- **products_activity.quantity / price / status**：僅活動管理 API 可寫入；兌換流程不可直接修改庫存或價格。
- **products_activity_redeem_logs.account / pid**：由兌換 API 自動填入，不可人工修改或由其他服務寫入。
- **products_store.price / originalprice**：僅商品管理 API 可寫入；不允許透過唯讀查詢後直接回寫。
- **商品庫存（透過 product_store_stock_logs）**：庫存變動僅能透過寫入 stock_logs 觸發，不可直接 UPDATE 商品表庫存欄位或以其他方式直接增減數量。
- **product_store_redeem_logs.account / phonenumber / address / recipient / cname / cheadshot / cmemo**：僅兌換 API 建立記錄時可寫入，後續不可修改，且不可由其他業務直接 INSERT 或 UPDATE。
- **product_store_redeem_logs.status**：僅系統流程（兌換建立、出貨、完成）可變更；不可由管理後台直接覆寫。
- **withdrawlogs_activity.account / contactnumber**：僅活動提領 API 寫入對應欄位；不可由其他服務修改。
- **withdrawlogs_activity.status**：僅提領流程系統可變更。
- **所有表的分區鍵 / 聚類鍵 (如 site, activityevent, pclass, pid)**：為資料寫入的強制索引組成，寫入時不可遺漏或任意變更，否則將導致資料落入錯誤分區。

### 讀取規則

- **商店商品列表**：WHERE status = '1' AND popular = true，按 sequence 排序，僅回傳上架且熱門商品。
- **活動商品列表**：WHERE site = :site AND activityevent = :event AND status = 1，僅啟用的活動商品可被查詢。
- **活動兌換記錄**：WHERE site = :site AND activityevent = :event AND account = :account，需嚴格依帳號過濾。
- **商店兌換記錄**：WHERE pclass = :pclass AND pid = :pid AND account = :account，並可依 addtime 範圍擷取，必須以 account 限制當前用戶。
- **庫存異動日誌**：WHERE pclass = :pclass AND pid = :pid AND addtime >= :start AND addtime <= :end，必須指定時間區間，避免全表掃描。
- **商品詳細查詢**：以 (pclass, pid) 組合主鍵精確查詢。
- **活動領獎記錄 (withdrawlogs_activity)**：WHERE site = :site AND activityevent = :event AND account = :account，僅查詢自身記錄。

### 不可回傳欄位

- **products_activity_redeem_logs.account**：用戶帳號，資安敏感。
- **product_store_redeem_logs.account**：同上。
- **withdrawlogs_activity.account**：同上。
- **product_store_redeem_logs.phonenumber**：電話號碼，個人資料。
- **product_store_redeem_logs.address**：完整配送地址。
- **product_store_redeem_logs.cname**：客戶／公司名稱。
- **product_store_redeem_logs.cheadshot**：客戶頭像 URL（可能內含個人資訊）。
- **product_store_redeem_logs.cmemo**：內部備註。
- **product_store_redeem_logs.recipient**：收件人姓名。
- **withdrawlogs_activity.contactnumber**：聯繫電話。
- **products_activity.names**：多語言名稱 map，內部管理用途，不對外暴露。

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