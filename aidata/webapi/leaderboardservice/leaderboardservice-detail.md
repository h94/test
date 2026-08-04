# leaderboardservice — DB 操作邊界

> 產出時間：2025-04-15 10:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## leaderboard

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| leaderboard MySQL | owner | Schema：尚未收錄於 `aidata/db` · 語意：尚未收錄於 `aidata/db` |

### 寫入限制

- **charts.Token**：僅由程式於新增時自動產生 Hash Key，不允許外部寫入或修改。
- **charts.Account**：新增時必須存在於 `users` 表（FK），且僅允許對應帳號擁有者或管理員操作。
- **charts.Template**：僅可寫入存在於 `templates` 表的 ID，不可直接寫入不存在的值。
- **charts.Title**：長度不可超過 `varchar(20)`，且須通過服務層 Title 驗證器（禁止特殊字元、空白字串）。
- **charts.DataSource**：僅允許預先定義的值（如 `'API'`），新增時須通過 DataSource 驗證器。
- **charts.UrlPath**：當 `DataSource = 'API'` 時為必填，且長度不可超過 `char(250)`；非 API 來源時此欄位須為空。
- **charts.ReloadTime**：僅允許正整數（單位：秒），用於排程自動更新。
- **charts.FlashTime**：僅允許正整數（單位：小時），服務層會自動根據此值更新 `PreFlashTime`，不允許直接修改 `PreFlashTime`。
- **charts.LastUpdater / LastUpdateTime**：由系統自動設定，不允許手動寫入。
- **charts.AddTime**：由資料庫自動填入，不可寫入。
- **chartscontents.ID**：自動遞增主鍵，不可指定。
- **chartscontents.Token**：須為已存在於 `charts` 表的 Token，新增時必須檢查 FK 存在。
- **chartscontents.Content**：僅可由排行榜更新排程或管理 API 寫入，外部客戶端不應直接 INSERT / UPDATE 此欄位。
- **chartscontents.AddTime**：由資料庫自動填入，不可寫入。
- **chartscontents.Updater**：由系統自動填入操作者帳號。
- **animations.ID**：自動遞增主鍵，不可寫入。
- **animations.Name / Style**：僅可由管理後台維護，本服務不提供 API 寫入。
- **templates.ID**：自動遞增主鍵，不可寫入。
- **templates.Name / Layout / Style**：同 animations，僅管理途徑修改。
- **users.Password**：須以雜湊儲存，禁止明文寫入；`users` 表整體由其他服務（如 auth service）管理，本服務僅讀取 `Account` 與 `Rank`。

### 讀取規則

- **charts 查詢**：一般 GET 時須過濾 `Account` 等於當前請求者帳號（除非管理員），防止跨帳號查閱。
- **chartscontents 查詢**：常以 `Token = ?` 搭配 `AddTime` 排序取得最新內容；查詢時應以 Token 為條件，避免一次回傳全部排行榜內容。
- **users 查詢**：僅用於驗證帳號存在及權限等級（`Rank`），不應回傳密碼或敏感欄位。
- **templates / animations 查詢**：全部公開（無 WHERE 條件），但須注意快取策略避免每次回傳大量資料。

### 不可回傳欄位

- **users.Password**：密碼欄位，任何對外 API 皆不可回傳。
- **users.LastLoginTime**：個人隱私，對外 GET 不應暴露。
- **chartscontents.Content**：內容可能包含敏感排名資料，僅限授權使用者或查閱自己排行榜時回傳；若 Content 為 JSON 格式，不應回傳原始字串以外的內部結構。
- **charts.LastUpdater / LastUpdateTime**：審計欄位，一般 GET 不應包含。

---

## product

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| product MySQL | reader | Schema：[db/product.json](../../db/product.json) · 語意：[db/product-detail.md](../../db/product-detail.md) |

### 寫入限制

本服務對 product 資料庫的所有表均為唯讀，不執行任何 INSERT、UPDATE 或 DELETE。所有寫入操作應由 productservice 或相關後台系統負責。

### 讀取規則

- **可兌換商品查詢**（`products_activity`、`products_store`）：查詢時必須過濾狀態（`products_activity.status` 為整數，應取 1；`products_store.status` 為文字型，應取 `'1'`），僅回傳上架商品；對於活動商品（`products_activity`），應額外檢查 `quantity > 0`，確保尚有庫存。
- **兌換紀錄查詢**（`products_activity_redeem_logs`、`product_store_redeem_logs`）：查詢特定帳號的兌換紀錄時，必須以 `account = :currentUser` 為必要條件，防止跨帳號查閱；若需管理端全覽，需搭配權限驗證。
- **庫存日誌查詢**（`product_store_stock_logs`）：僅供內部稽核或管理用途，不對外直接暴露；查詢時須搭配 `pid` 及時間範圍，避免全表掃描。
- **提領記錄查詢**（`withdrawlogs_activity`）：必須以 `account` 過濾，且僅回傳請求者相關記錄；管理端查詢需額外權限驗證。
- **多語系欄位處理**：對於 `map<text, text>` 型別的欄位（如 `names`、`pnames`、`description`、`image_path`），查詢時應根據請求的 `Accept-Language` 頭選擇對應語系的值回傳，不得直接輸出整個 Map。

### 不可回傳欄位

- **phonenumber**（`product_store_redeem_logs`）、**contactnumber**（`withdrawlogs_activity`）：個人聯絡電話，回傳時須進行脫敏處理（僅顯示末三碼或完全遮蔽），不得輸出原始完整號碼。
- **address**（`product_store_redeem_logs`）：收件地址屬個人隱私，一般查詢應隱藏完整內容，僅顯示部分區域（如縣市），或完全遮蔽。
- **cheadshot**（`product_store_redeem_logs`）：若為證件照或頭像 URL，應僅限本人或授權管理人員檢視，不可在公開列表直接回傳。
- **多語系欄位原始內容**（`products_activity.names`、`products_store.pnames`、`products_store.description`、`products_store.image_path`）：這些 map 型欄位不可直接整包回傳；服務層應依據請求語系挑選對應文字後再輸出單一值，若無符合語系則使用預設 fallback。

---

## Redis

**本服務未使用 Redis**。排行榜內容快取由前端或 CDN 層處理，服務端無 Redis 相關操作。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 使用者帳號註冊、登入、密碼重設 | auth service | leaderboardservice 僅參考 `users` 表驗證帳號存在與權限，不管理認證流程 |
| 動畫（animations）與模板（templates）的 CRUD | admin service | 本服務僅讀取已定義的動畫與模板，新增/修改由管理後台處理 |
| 排行榜資料來源的外部 API 呼叫 | data-fetch service 或排程 | leaderboardservice 雖儲存 `UrlPath`，但實際呼叫與資料轉換由其他元件執行 |
| 商品的建立、修改、上下架與庫存管理 | productservice | 本服務僅讀取 product 資料庫，不執行任何商品狀態、價格或庫存的異動 |
| 兌換流程中的庫存扣減與點數扣除 | productservice / walletservice | leaderboardservice 不負責交易邏輯，兌換時僅提供驗證或展示所需資料 |
| 活動提領（withdraw）的審核與發放 | activityservice / productservice | `withdrawlogs_activity` 的狀態更新不應由本服務觸發 |

---

## 常見錯誤

- ❌ 直接修改 `charts.Token` 或試圖寫入重複的 Token → ✅ Token 由系統自動產生，不可變更；重複寫入應返回衝突錯誤。
- ❌ 插入 `charts.Title` 時未驗證長度或特殊字元，導致資料庫截斷或 Injection → ✅ 服務層應使用驗證器檢查長度（≤20）與合法字元。
- ❌ 設定 `DataSource = 'API'` 但未提供 `UrlPath`，或提供無效路徑 → ✅ 應在寫入前強制檢查 `UrlPath` 不為空且格式正確。
- ❌ 直接將外部使用者傳入的 Content 寫入 `chartscontents` 表，未經許可或防注入 → ✅ Content 僅由排程或內部 API 使用格式化的 JSON 寫入。
- ❌ 查詢 `chartscontents` 時未加上 `Token` 條件，導致回傳所有排行榜內容（效能與資安問題） → ✅ 查詢時必須以 Token 過濾。
- ❌ 誤以為本服務負責管理 `users` 表密碼或帳號啟用狀態 → ✅ 相關功能屬於 auth service，本服務僅讀取。
- ❌ 在讀取 product 資料庫時未過濾 `status` 或 `quantity`，導致回傳已下架或無庫存的商品 → ✅ 查詢上架商品時必須包含 `WHERE status = '1'`（或 `status = 1`）及 `quantity > 0`。
- ❌ 兌換紀錄查詢時未以 `account` 過濾，造成使用者可檢視他人兌換內容 → ✅ 一律加上 `account = :currentUser`，管理端則需額外權限檢查。
- ❌ 對外 API 直接回傳 `phonenumber`、`address` 等完整個資 → ✅ 必須進行脫敏（如隱藏中間數字、只顯示縣市），或完全遮蔽該欄位。
- ❌ 直接回傳多語系欄位（`names`、`pnames` 等）的 map 完整內容 → ✅ 應根據請求 `Accept-Language` 頭挑選對應語系文字，並有預設語系回退機制。
- ❌ 試圖在 leaderboardservice 中執行 product 表的 INSERT 或 UPDATE → ✅ product 的所有寫入應委派給 productservice，避免跨服務直接操作資料庫。