# 建立一般廣告

## 1. 場景目的
後台管理人員建立一筆一般廣告（對應 `advertising` table）。目標是提供廣告所需的所有資訊（如類型、語言、順序、有效時間、圖片與連結），並確保寫入資料庫的廣告符合業務規則，以利前台或各服務後續查詢與展示。

---

## 2. 入口 API

> **需人工確認**：OpenAPI 定義為 `POST /api/v1/ad`，但 README 僅列出 `POST /api/v1/sport/ads`（後者對應 `advertising_sport`）。一般廣告建立可能有獨立 API，或因歷史因素存在兩套路由。

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/ad` | 建立一般廣告 (OpenAPI) |

---

## 3. 流程總覽

1. 後台人員調用 `POST /api/v1/ad`，傳入廣告資訊。
2. ECFramework.ECService 進行統一驗證。
3. Controller 接收請求，轉交 Service 層處理。
4. Service 層執行業務規則驗證：
   - `type` 不可為空。
   - `lang` 必須為系統定義的有效語言代碼（如 `zh`, `en`）。
   - `starttime` 與 `closetime` 為 Unix 秒級時間戳，且 `starttime < closetime`。
   - `closetime` 若小於當前時間，拒絕建立請求。
   - `seq` 在同一 `type` 下不可重複。
5. 系統自動生成廣告 `id`。
6. `createdby` 自動由系統寫入當前操作者資訊。
7. `enabled` 預設寫入 `1`（啟用）。
8. 其餘欄位（`title`, `path`, `url`, `action`）依請求內容寫入。
9. 將資料寫入 `ads.advertising` table。
10. 回傳成功訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `AdvertisingController.Create` (推測) | 接收 HTTP POST 請求，透過 ECFramework 驗證身分 |
| 2 | Service | `AdvertisingService.CreateAd` (推測) | 執行業務規則驗證：時間、語言、順序、必要欄位 |
| 3 | Service | `AdvertisingService.CreateAd` (推測) | 檢查 `seq` 於相同 `type` 下的唯一性（查詢現有最大 `seq`） |
| 4 | Service | `AdvertisingService.CreateAd` (推測) | 產生廣告 `id`，取得當前使用者作為 `createdby` |
| 5 | Provider | `AdvertisingRepository.Insert` (推測) | 寫入 Cassandra `ads.advertising` table |
| 6 | Controller | `AdvertisingController.Create` (推測) | 回傳成功代碼 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | ads.advertising | Write | 新增廣告記錄 |
| DB | ads.advertising | Read | 檢查相同 `type` 下 `seq` 是否重複 |
| Cache | (未使用) | - | 文件與程式碼分析未顯示對一般廣告的 Redis 快取操作 |
| Queue | (未使用) | - | 無相關 Kafka 或 Queue 操作 |

---

## 6. 重要規則

- **權限限制**：此 API 需要驗證（ECFramework），僅後台管理人員可調用。
- **欄位限制**：
  - `id`：系統自動生成，請求不可傳入。
  - `createdby`：系統自動寫入，請求不可傳入，後續不可修改。
  - `enabled`：建立時預設為 `1`，不可由建立請求指定。
  - `starttime` / `closetime`：必須為 Unix 時間戳（秒級）。
- **不可暴露資料**：`createdby` 不可回傳給一般客戶端。
- **時間規則**：
  - `starttime < closetime` 為強制規則。
  - 若 `closetime` 早於當前時間，拒絕請求。
- **語言規則**：`lang` 僅可為系統定義代碼（如 `zh`、`en`），不支援空值或任意字串。
- **排序規則**：`seq` 於同一 `type` 下不可重複，寫入前需檢查唯一性。
- **不可修改欄位**：廣告建立後，`createdby` 禁止修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未提供 type | 回傳驗證錯誤（必要欄位缺失） |
| lang 為未定義代碼 | 回傳驗證錯誤（無效語言代碼） |
| starttime >= closetime | 回傳時間範圍無效錯誤 |
| closetime 早於當前時間 | 回傳時間範圍無效錯誤（已過期） |
| seq 與相同 type 下既有記錄重複 | 回傳排序衝突錯誤 |
| request body 缺失 path 或 url | 回傳驗證錯誤（必要欄位缺失） |
| 未經授權調用 API | 回傳 401 未授權 |
| 資料庫寫入失敗 | 回傳伺服器錯誤 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 傳入完整有效廣告資料 | 成功建立，回傳 200 |
| TC02 | Permission Test | 無效 token 調用 API | 回傳 401 |
| TC03 | Flow Test | starttime 大於 closetime | 回傳錯誤，未寫入 DB |
| TC04 | Flow Test | closetime 為過去時間 | 回傳錯誤，未寫入 DB |
| TC05 | Flow Test | lang 為 “fr” (未定義) | 回傳驗證錯誤 |
| TC06 | Flow Test | seq 在相同 type 下已存在 | 回傳排序衝突錯誤 |
| TC07 | Integration Test | 建立成功後，查詢 `ads.advertising` | 記錄存在，`enabled=1` |
| TC08 | Integration Test | 建立成功後，`createdby` 欄位非空 | 可確認寫入來源 |

---

## 9. 高風險區域

- **高風險 table**：`ads.advertising`（直接寫入，影響所有服務查詢結果）
- **高風險 API**：`POST /api/v1/ad`（未授權可能導致垃圾廣告或資安風險）
- **跨服務資料同步**：
  - 其他服務（如 `communityservice`、`livechatservice`）查詢廣告時依賴 `enabled=1` 與時間範圍，錯誤寫入可能造成廣告顯示異常。
- **Transaction**：
  - Cassandra 不支援跨分割區交易，需確保單一寫入的原子性（單筆插入為原子操作）。
- **Cache consistency**：
  - 若未來增加 Redis 快取，需注意寫入時的快取同步問題。目前雖未使用，但 README 提及 `SportAdCache`，需留意避免混淆。
- **Idempotency**：
  - 若 `id` 由客戶端傳入，重複請求可能造成覆蓋。現行設計由系統產生 `id`，重複請求將建立多筆記錄，需根據業務是否需要冪等性。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 直接使用 OpenAPI 中的 `POST /api/v1/ad` 建立廣告，但未比對 README 中的 `/api/v1/sport/ads` 屬於不同 table，可能搞錯目標。
  - `starttime` / `closetime` 傳入毫秒級時間戳，導致時間範圍比對失效。
  - 建立時嘗試傳入 `enabled=0` 或 `createdby`，被系統忽略或造成錯誤。
- **AI 容易誤解**：
  - 將 `advertising` 與 `advertising_sport` 欄位混淆（如時間格式用 `startdate` 而非 `starttime`）。
  - 誤以為此流程使用 Redis 快取（實際上只有體育廣告版本使用 `SportAdCache`）。
- **常見漏檢查項目**：
  - 未於寫入前驗證 `starttime < closetime`，寫入不合邏輯的時間區間。
  - 未檢查 `seq` 重複性，導致前端排序錯亂。
- **常見錯誤流程**：
  - 跳過語言代碼驗證，寫入非法 `lang` 值，導致查詢過濾失效。
  - 未處理 `closetime` 已過期的情況，建立無效廣告。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI `POST /api/v1/ad` |
| DB | `ads.advertising` table schema (Cassandra) |
| 規則：createdby 禁止修改 | db-usage `advertisingservice-detail.md` - advertising 寫入限制 |
| 規則：starttime / closetime 驗證 | db-usage `advertisingservice-detail.md` - 常見錯誤 |
| 規則：enabled 預設 1 | db-usage `ads-detail.md` - Table advertising enabled 欄位 |
| 規則：createdby 不可回傳 | db-usage `advertisingservice-detail.md` - 不可回傳欄位 |
| Code evidence | 未提供具體 Controller / Service 程式碼，流程推導自 OpenAPI 與 DB 細節 |