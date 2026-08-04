# livechatservice — DB 操作邊界

> 產出時間：2025-04-10 15:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## tokens

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| tokens (MySQL) | writer & reader | Schema：[db/tokens.md](../../db/tokens.md) · 語意：[db/tokens-detail.md](../../db/tokens-detail.md) |

### 寫入限制

- **tokens.tokens**：
    - `HashKey`：僅允許透過 `TokenProvider.CreateToken` 方法生成並寫入。生成邏輯應為不可逆雜湊或隨機字串，不可直接複製或手動指定。
    - `CompanyCode`：必須與請求上下文中的公司代碼一致，嚴防跨公司寫入。
    - `AddTime`、`ExpirationTime`：必須由 `TokenProvider.CreateToken` 根據傳入的 `expirationTime` 參數和當前時間自動設定，不允許從外部 API 直接指定。
    - `Enabled`：預設為 1。僅允許透過特定的管理功能進行啟用/停用，不應由一般業務流程直接修改。
- **tokens.logs**：
    - 此表為唯寫（Write-Only）記錄，僅供 `TokenProvider` 內部在執行 `CreateToken` 和 `CheckToken` 時新增（INSERT）。任何外部服務或 API 不應直接操作此表。

### 讀取規則

- **Token 驗證 (`tokens.tokens`)**：
    - 必須同時滿足 `HashKey` 完全匹配、`CompanyCode` 匹配請求上下文、`Enabled = 1` 且 `ExpirationTime > NOW()` 的條件，方可視為有效 Token。
    - 查詢時應使用 `HashKey` 作為主要過濾條件，以提高查詢效率。
- **操作記錄 (`tokens.logs`)**：
    - 僅供後台查詢或問題排查使用，不參與任何線上業務邏輯判斷。

### 不可回傳欄位

- `tokens.tokens.HashKey`：與密碼等價的敏感憑證。在對外的任何 GET 回應中，均不可回傳此欄位的完整或部分值。
- `tokens.logs.ID`、`tokens.tokens.ID`：內部主鍵，無業務意義，不應回傳給客戶端。

---

## Redis

本服務對 `tokens` 資料庫無使用 Redis 操作。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| Token 的跨服務驗證 | 各接入服務 (如 API Gateway) | livechatservice 負責生成與驗證自身發出的 Token，不負責統一認證中心職責。 |
| 公司代碼的有效性驗證 | 公司/租戶管理服務 | livechatservice 假定傳入的 `CompanyCode` 是有效且已存在的，不負責校驗其合法性。 |

---

## 常見錯誤

- ❌ 在驗證 Token 時，僅比對 `HashKey` 存在，而忽略了 `Enabled=0` 或 `ExpirationTime` 已過期。
  → ✅ 必須同時檢查 `Enabled = 1` 和 `ExpirationTime > NOW()`。
- ❌ 嘗試讀取 `tokens.logs` 來判斷 Token 是否有效。
  → ✅ `logs` 表僅為操作記錄，不具備狀態判斷能力，必須查詢 `tokens.tokens` 表。
- ❌ 在 API 回應中，因格式化或 Debug 需求而回傳了 `HashKey`。
  → ✅ 應設計專門的、安全的值物件（ViewModel）來排除敏感欄位。

---

## feedback

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra feedback | writer & reader | Schema：[db/feedback.md](../../db/feedback.md) · 語意：[db/feedback-detail.md](../../db/feedback-detail.md) |

### 寫入限制

- **businessmessages**：
  - `id`：由服務端生成唯一識別碼（UUID），禁止外部傳入。
  - `site`：必須從已驗證的業務上下文取得，不可直接接受前端請求參數。
  - `sendcontent`、`sendermail`：僅在發送業務訊息（如客服通知）時由本服務寫入；`sendermail` 須取自已驗證的管理員身份，不得由外部指定。
  - `respcontent`：僅當回覆訊息時由本服務填寫，禁止由外部請求直接賦值。
  - `status`：由服務根據內部狀態機更新（如 未處理→處理中→已處理），前端僅可觸發操作，不可直接指定目標值。
  - `updatetime`：每次寫入自動設為當前 Unix 時間戳，不允許外部傳入。
  - `datetime`：建立記錄時由服務填入 `yyyy-MM-dd HH:mm` 格式的當前時間字串，後續不可變更。

- **feedbacks_sport / feedbacks_stock**：
  - `respcontent`：唯本服務可附加回覆內容（append）。每個新增元素必須為包含 `DateTime` 與 `Message` 的 JSON 字串，禁止覆蓋整份清單或刪除歷史記錄。
  - `adminimgpath`：管理員上傳圖片後由本服務寫入，路徑須先經檔案服務驗證其合法性。
  - `status`：本服務可依規則推進狀態（0 未處理 → 1 處理中 → 2 已回覆），需遵守有限狀態機；不允許跨狀態跳躍或逆轉。
  - `updatetime`：任何對該筆記錄的更新均自動設為當前 Unix 時間戳。
  - **本服務不可寫入**：`problem`、`imgpath`、`email`、`account`、`tid`、`datetime`（這些欄位由反饋提交服務在建立時設定，livechatservice 僅可讀取）。

- **topics_sport / topics_stock / questions_sport / questions_stock**：
  - 所有欄位均為**唯讀**，本服務不具備任何寫入權限。

### 讀取規則

- **businessmessages**：
  - 列表查詢：**必須**提供分區鍵 `site`，可搭配 `datetime` 範圍、`status` 進行過濾，確保查詢落在單一分區。
  - 單一訊息查詢：需同時提供 `site` 及 `id`（聚簇鍵）。

- **feedbacks_sport**：
  - 依主題查詢：**必須**提供分區鍵 `tid`，可再傳入 `account` 或 `datetime` 起始條件進行範圍掃描。
  - 查詢單筆：須提供完整主鍵 `(tid, account, datetime, id)`。

- **feedbacks_stock**：
  - 主鍵為 `id`，可直接以 `id` 查詢單筆記錄；為利用索引，建議搭配 `tid` 一同過濾。

- **topics / questions（sport、stock）**：
  - 所有對外查詢必須帶有 `enabled = 1` 條件，只回傳已啟用的主題與問題。
  - 顯示順序應依照 `sort` 升冪排列。

### 不可回傳欄位

- `feedbacks_sport.email`、`feedbacks_stock.email`：使用者私人郵件，嚴禁在任何 API 回應中出現。
- `feedbacks_sport.account`、`feedbacks_stock.account`：使用者帳號識別，屬於隱私欄位，不可回傳。
- `businessmessages.sendermail`：管理員信箱，禁止暴露給前端使用者。
- 所有表中的 `updatetime` 原始 Unix 時間戳，應在回傳前轉換為可讀格式（如 ISO 8601），避免直接暴露內部儲存值。

---

## Redis

本服務對 `feedback` 資料庫無使用 Redis 操作。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 使用者提交反饋（建立 `feedbacks` 記錄） | 反饋提交服務 | livechatservice 僅處理回覆與狀態流轉，不負責 `problem`、`imgpath` 等初始欄位的建立。 |
| 主題與常見問題的管理（增刪改） | 客服管理後台服務 | 本服務僅讀取已啟用的主題與問題，所有配置變更由專門後台進行。 |
| 圖片上傳與儲存 | 檔案服務 | `adminimgpath` 僅由本服務傳遞路徑，實際檔案上傳與託管由獨立檔案服務負責。 |
| 站點（site）可用性與權限校驗 | 站點配置服務 | 本服務假定傳入的 `site` 為合法且授權的站點，不進行站點存在性檢查。 |

---

## 常見錯誤

- ❌ 直接將使用者端傳入的 `respcontent` 整筆覆蓋 `feedbacks` 的 `respcontent` 欄位。
  → ✅ 必須以附加（append）方式將新回覆連同時間戳轉為 JSON 字串後加入列表尾端。
- ❌ 查詢 `businessmessages` 時未指定 `site` 分區鍵，導致全表掃描。
  → ✅ 所有對 `businessmessages` 的查詢都必須提供 `site`。
- ❌ 在回覆 `feedbacks_sport` 時忘記更新 `updatetime` 與適當推進 `status`。
  → ✅ 每次寫入回覆，系統應自動將 `updatetime` 設為當前時間，並依規則將 `status` 從待處理改為處理中或已回覆。
- ❌ 對外 API 回傳了 `email` 或 `account` 欄位，造成個資洩漏。
  → ✅ 應使用 DTO（資料傳輸物件）明確排除敏感欄位再序列化回應。
- ❌ 試圖在 livechatservice 中修改主題或問答的 `question`、`answer` 等設定資料。
  → ✅ 這些表僅供讀取，寫入操作必須委由專門的後台管理服務執行。