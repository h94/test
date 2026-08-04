# priceclientsystem — DB 操作邊界

> 產出時間：2025-04-08 10:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## product

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Product (Cassandra) | owner | Schema：[db/product.md](../../db/product.md) · 語意：[db/product-detail.md](../../db/product-detail.md) |

### 寫入限制

- **系統時間戳欄位（`lastup_time`, `updatetime`, `addtime` 等）**：僅由服務端內部邏輯或資料庫觸發器自動設定，**禁止應用程式直接寫入或修改**，避免時間戳不一致。
- **主鍵欄位（分區鍵／集群鍵）**：如 `products_activity.activityevent`、`products_activity.site`、`products_activity.id`、各 log 表的 `site`、`account`、`pid`、`pclass`、`id` 等，一經建立**即不可修改**，變更將導致資料分佈錯亂與關聯中斷。
- **products_store.price / originalprice**：僅管理後台或價格同步批次可寫入；前端兌換流程不可改動。
- **products_store.pnames / description / image_path**（map 欄位）：僅管理後台可整體更新 map；前端 API **不允許直接操作 map 單鍵**，以免遺失多語言資料。
- **products_store.status**：僅允許 `'1'`（啟用）或 `'0'`（下架），由管理後台控制；前端不可介入。
- **products_store.pclass**：商品分類代碼，僅管理後台設定，前端不可建立或變更。
- **products_activity.quantity**：活動庫存僅由活動建立或庫存調整批次寫入；兌換成功時必須透過原子操作扣減（建議使用 Cassandra LWT 或樂觀鎖），防止超賣。
- **products_activity.names / price / status**：僅管理後台可設定或調整；前端兌換流程不可修改。
- **product_store_redeem_logs.status**：僅內部兌換流程可更新，且狀態機必須強制校驗（例如 `pending → shipping → delivered`，或 `pending → cancelled`），不允許跳轉。
- **product_store_stock_logs.quantity**：為不可變日誌，僅庫存變動時插入正／負值記錄，**禁止 UPDATE 既有記錄**。
- **withdrawlogs_activity.status**：僅提現審核流程可更新（如已處理、已撥款），前端 API 不得直接變更。
- **withdrawlogs_activity.contactnumber**：由用戶提交時寫入，後續**不可透過前端 API 修改**；管理後台如需修改應記錄 audit log。

### 讀取規則

- **產品列表查詢**：僅回傳 `products_store.status = '1'` 的商品；`'0'` 或其他值視為下架／未激活，不對外展示。
- **兌換紀錄查詢**：依 `account` 篩選時，僅允許用戶透過 token 查詢自身的紀錄；後端強制校驗請求帳號與 token 身分一致。
- **活動商品查詢**：僅回傳 `products_activity.status = 1` 且 `quantity > 0` 的活動商品；已停用或已售罄的活動不可參與兌換。
- **庫存判斷**：兌換前須比較 `products_store.status` 並以 `product_store_stock_logs` 加總計算實際庫存，**不可僅依 `products_store.price` 存在即放行**。
- **提現記錄查詢**：依 `account` 篩選，只允許用戶查詢自身的提現申請；管理後台查詢亦需限制站點或權限範圍。

### 不可回傳欄位

- **product_store_redeem_logs.phonenumber**：對外列表或管理 API 預設不回傳完整電話號碼；僅用戶本人查詢訂單明細時可顯示，必要時脫敏為 `0912***456`。
- **product_store_redeem_logs.address**：除用戶本人查詢訂單明細外，其餘 API 皆不可回傳完整地址。
- **product_store_redeem_logs.account**：用戶查詢自身兌換紀錄時，不回傳此欄位（避免 payload 冗餘與身分混淆）；管理後台可依需求顯示。
- **products_activity_redeem_logs.account**：同上，一般用戶查詢時隱藏，管理後台可查但須權限控制。
- **withdrawlogs_activity.contactnumber**：任何對外 API 皆應脫敏，僅保留末四位或直接隱藏；管理後台可脫敏顯示。
- **withdrawlogs_activity.account**：前端用戶查詢時不回傳，管理後台可依權限提供。

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Pricecenter (Cassandra) | owner | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **password**：僅帳戶註冊或密碼修改 API 可寫入；須先經雜湊（bcrypt）再寫入，**不允許直接明文 UPDATE**。
- **enabled**：僅系統內部停用/啟用流程可寫入，前端 API 不可直接修改。
- **closetime**：僅帳戶關閉時由後端自動填入時間戳（格式 yyyy-MM-dd HH:mm:ss），不支援手動修改。
- **handler**：僅特定內部批次服務可寫入或更新整個 map，前端不可操作。
- **actionlog**：僅供內部稽核元件以 **INSERT** 寫入，**嚴禁 UPDATE 或 DELETE**；所有欄位（`date`, `addtime`, `user`, `gametype`, `action`, `actionclass`, `detail`）均由後端邏輯自動填入，前端 API 無任何直接寫入權限；`date` 為合法日期分區鍵（yyyy-MM-dd），`addtime` 為時間戳字串。

### 讀取規則

- **帳戶登入驗證**：查詢 `SELECT * FROM accounts_{client} WHERE account = ?` 後，須檢查 `enabled != 0`（啟用） 且 `closetime IS NULL` 或 `closetime` 小於當前時間（表示未關閉）。已關閉或禁用帳戶不可登入。
- **帳戶資訊查詢**：前端 API 回傳時，若 `closetime` 非空並非預期顯示欄位，應忽略或返回 `null`；`handler` 僅在必要時提供（如管理後台），一般用戶查詢不回傳。
- **操作日誌查詢**：查詢 `actionlog` 時**必須**帶入分區鍵 `date`（或明確日期範圍），**禁止全表掃描**；僅允許授權管理角色存取，並需依服務情境限制查詢範圍（例如限定特定 `gametype` 或 `user`）；一般終端用戶不可查詢他人記錄。

### 不可回傳欄位

- **password**：任何 API 回傳（既使管理層級 API）**皆不可包含密碼欄位**。密碼僅用於內部驗證流程。
- **phone**：除非用戶授權或管理層級特定報表，預設不回傳完整手機號，可脫敏處理（如 138****1234）。
- **actionlog.detail**：包含 JSON 格式的操作細節，可能洩漏修改前後資料（如密文、個資），對外 API 須隱藏或僅輸出摘要；即使管理後台亦須控制顯示範圍，不得完整裸露。

---

## Redis

（無）

> **說明**：priceclientsystem 服務目前未使用 Redis 快取。所有產品及活動資料直接從 Cassandra 讀取。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 帳戶密碼驗證（比對雜湊） | `priceclientsystem` 本身（內部邏輯） | 但密碼管理（重設、安全規範）由 `account` 服務負責，priceclient 僅驗證登入時比對。 |
| 帳戶啟用/停用排程 | `account` 或 `scheduler` | 自動關閉逾時帳戶、批量停用作業不屬於 priceclient。 |
| 第三方客戶 `sitegames_{gameType}` 表操作 | 遊戲服務 (`game-service`) | priceclient 僅讀取 `sitegames_{gameType}` 中的即時賽事資料，寫入與結構管理由遊戲系統負責。 |
| 產品圖片儲存與 CDN 管理 | `storage` 或 `media` 服務 | priceclient 僅存取 `image_path` 欄位中的路徑字串，不處理圖片上傳、壓縮、CDN 分發。 |
| 多語言翻譯內容維護 | `i18n` 或 `cms` 服務 | `pnames`、`description`、`names` 等 map 內容由外部系統管理，priceclient 只讀取。 |
| 提現資金撥付與結算 | `payment` 或 `withdraw` 服務 | 負責記錄提現申請與狀態變更，實際資金出款、銀行對接由支付系統處理。 |

---

## 常見錯誤

- ❌ 兌換商品時未檢查 `products_store.status` 是否為 `'active'`，導致對已下架商品仍允許兌換。  
  → ✅ 兌換前必須讀取並驗證 `status`，以及 `pclass`/`pid` 存在性。且注意狀態值為文字 `'1'` 才是啟用，不可誤用 `'active'`。
- ❌ 庫存扣減時直接 `UPDATE products_store SET quantity = quantity - 1`（無此欄位），或未同時寫入 stock_logs 導致庫存對賬缺失。  
  → ✅ 應先讀取 `products_store` 確認無活動限制，再透過新增 `product_store_stock_logs`（負值）記錄變動，並依賴 stock_logs 加總計算剩餘庫存（Cassandra 不支援事務，需業務邏輯補償）。
- ❌ `product_store_redeem_logs` 中 `status` 更新時未校驗前置狀態（如直接從 `pending` 改為 `delivered` 跳過 `shipped`）。  
  → ✅ 狀態機必須嚴格校驗（`pending → shipping → delivered` 或 `pending → cancelled`），不可隨意跳轉。
- ❌ 活動商品兌換（`products_activity_redeem_logs`）未同時扣減 `products_activity.quantity`，導致超賣。  
  → ✅ 兌換成功後必須原子更新 `products_activity.quantity`（使用 Cassandra LWT 或樂觀鎖）。
- ❌ 前端 API 回傳 `phonenumber` 或 `address` 未脫敏，對用戶隱私造成風險。  
  → ✅ 除用戶本人查詢訂單詳情外，列表或管理 API 均應脫敏處理，或直接忽略敏感欄位。
- ❌ 提現記錄 API 回傳完整 `contactnumber`，未脫敏。  
  → ✅ 必須對聯絡電話進行脫敏處理，僅部分授權角色（如客服、審核）可查看完整號碼。
- ❌ 判斷 `products_store.status` 時使用字串 `'active'` 而非 `'1'`，導致產品顯示錯誤。  
  → ✅ 狀態欄位定義為 `text`，啟用值固定為 `'1'`，查詢與比較時須使用正確字面值。