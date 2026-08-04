# tokenservice — DB 操作邊界

> 產出時間：2025-04-13 08:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| pricecenter (Cassandra) | reader (accounts_* 表群) + writer (actionlog) | Schema：[db/pricecenter.json](../../db/pricecenter.json) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **accounts_* 表群**（如 accounts_AU8, accounts_Fortuna888 等）：tokenservice 無任何寫入權限，所有帳號欄位（account, closetime, enabled, handler, password, phone, username）均由 pricecenter 維護。
- **actionlog**：tokenservice 僅可寫入，不可更新或刪除既有記錄。寫入時必須填入：
  - `date`：當前日期（分區鍵，格式依 pricecenter 定義）
  - `addtime`：當前時間戳（文字格式）
  - `user`：操作歸屬的使用者識別
  - `gametype`：對應的遊戲類型
  - `action`、`actionclass`、`detail`：由 tokenservice 依其作業定義，例如 token 建立、驗證、停用等；不可記錄非 token 相關內容，`detail` 不可包含原始 token 或密碼。

### 讀取規則

- 依請求中的平台代碼（如 `AU8`, `Fortuna888`）決定查詢哪個 `accounts_{platform}` 表。
- 必須使用主鍵 `account = ?` 進行查詢。
- 僅選取必要欄位，至少讀取 `enabled`, `handler`；不得讀取 `password`、`phone` 等敏感欄位（除非內部流程明確需要，且須保證不外洩）。
- 業務條件：查詢帳號時必須同時過濾 `enabled = 1` 且 `closetime` 為空（或視為未關閉），避免使用已停用或已關閉帳號進行 token 操作。

### 不可回傳欄位

- **accounts_* 表**：`password`、`phone` 絕對不可透過任何對外 API（含內部間接暴露）回傳。
- **actionlog**：`detail` 欄位若包含敏感參數（如 token 原文、密碼雜湊）亦不可回傳給前端或其他非必要服務。

---

## Redis

無。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 帳號的建立、啟用、停用、關閉、密碼管理 | pricecenter | tokenservice 僅讀取帳號狀態與 handler 配置，不維護帳號生命週期 |
| actionlog 記錄的清理、歸檔或稽核匯出 | pricecenter / 稽核服務 | tokenservice 只負責寫入 token 相關操作日誌，不管理日誌留存 |
| 多帳號表的資料一致性或跨平台帳號映射 | pricecenter | tokenservice 只依傳入的 platform 查詢對應表，不負責跨表關係 |

---

## 常見錯誤

- ❌ 未根據 platform 選擇對應的 `accounts_{platform}` 表，導致查錯表或取到錯誤的帳號配置
- ❌ token 建立/驗證時僅檢查 `account` 存在，未過濾 `enabled = 1` 及 `closetime` 狀態，允許已停用或關閉帳號繼續操作
- ❌ 對外 API 回應中帶出 `password`、`phone` 欄位
- ❌ 試圖直接 UPDATE `accounts_*` 表以記錄 token 狀態或更新 handler → 一律由 pricecenter 負責
- ❌ 寫入 actionlog 時使用了非 token 相關的 actionclass 或寫入過於細碎的資訊，造成日誌膨脹與敏感資訊外洩風險

---

## tokens

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| tokens (MySQL) | owner | Schema：[db/tokens.md](../../db/tokens.md) · 語意：[db/tokens-detail.md](../../db/tokens-detail.md) |

### 寫入限制

- **HashKey**：僅 `CreateTokenByOriginKey` API（當使用原始金鑰生成 token）或內部生成邏輯可寫入；由原始輸入經雜湊演算法轉換為長度 10 的字串後存入，禁止 API 呼叫方直接指定雜湊值。
- **AddTime**：僅在 token 首次建立時由服務端自動設定為當前時間戳；建立後不可再 UPDATE。
- **ExpirationTime**：僅在 token 建立時，由服務端根據 `AddTime` 加上設定的有效期秒數計算後寫入；token 一經建立，不得透過 UPDATE 延長或修改此欄位。
- **CompanyCode**：由認證請求中的 `authKey` 或平台配置決定，並寫入 token 記錄用於多租戶隔離；不允許 API 呼叫方自由指定或修改。
- **Enabled**：預設值為 `1`（啟用）；停用 token 時應透過標記為 `0` 進行邏輯刪除，不允許實體刪除記錄。

### 讀取規則

- **token 驗證**：任何 token 驗證（如 `CheckToken`、內部校驗）必須同時滿足以下條件，否則視為無效：`Enabled = 1` 且 `ExpirationTime > 當前時間`。絕不可僅比對 `HashKey`。
- **以原始金鑰驗證 (CheckTokenByOriginKey)**：應先將傳入的原始金鑰以相同雜湊演算法轉為 `HashKey`，再搭配 `CompanyCode` 進行查詢；查詢結果必須過濾 `Enabled = 1` 且未過期。
- **token 建立前衝突檢查**：在為同一 `CompanyCode` 建立新 token 時，若查得相同 `HashKey` 且 `Enabled = 1` 的既有 token，必須先將該舊 token 的 `Enabled` 標記為 `0`（停用），再新增新 token 記錄，確保同一公司代碼下，每個 `HashKey` 至多只有一筆啟用記錄。
- **批次查詢**：若業務存在批次驗證多個 token 的場景，WHERE 條件仍需對每一筆記錄套用 `Enabled = 1` 與 `ExpirationTime > NOW()`，不可因批次而省略。

### 不可回傳欄位

- **HashKey**：為 token 的雜湊識別值，屬於敏感資訊。任何對外（含前端、其他服務）的 GET 回應或日誌輸出，皆不可直接或間接暴露完整 `HashKey`。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET | `{prefix}:token:{HashKey}` | token 驗證（如 `CheckToken`）通過後，寫入快取 | TTL = `ExpirationTime - 當前時間`（秒）；若 Key 已存在則刷新 TTL。寫入值可為簡要狀態（如 `1`）或必要的 token 屬性，但不可包含 `HashKey` 原文。 |
| GET | `{prefix}:token:{HashKey}` | 執行 token 驗證前，優先查詢 Redis | 若命中快取，直接認定 token 有效（視同已通過 DB 層的 `Enabled` 與過期檢查），可略過查詢 DB；若未命中，才查詢 DB 並在驗證通過後回寫 Redis。 |
| DEL | `{prefix}:token:{HashKey}` | 手動停用 token（`Enabled` 設為 `0`）時；或背景作業偵測到 token 已過期 | 須與 DB 狀態保持最終一致；當 DB 中的 token 被停用或過期，必須同步清除對應的 Redis Key，防止快取殘留導致已失效 token 仍驗證通過。 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 使用者認證與授權 | authservice | tokenservice 僅管理 token 生命週期，不驗證使用者密碼或來源請求是否合法 |
| 前端 session 管理 | frontend-service / client | tokenservice 不維護使用者登入 session，僅產生/驗證 token |
| 密碼雜湊與驗證 | authservice | HashKey 雜湊只服務 token 識別，非使用者密碼 |

---

## 常見錯誤

- ❌ 驗證 token 時，SQL 僅用 `HashKey = ?` 作為條件，忽略 `Enabled` 與 `ExpirationTime` → ✅ 標準查詢必須為 `SELECT ... WHERE HashKey = ? AND CompanyCode = ? AND Enabled = 1 AND ExpirationTime > NOW()`。
- ❌ 手動執行 `UPDATE Tokens SET ExpirationTime = ...` 試圖延長 token 時效 → ✅ 欲延長使用期限應建立新 token，並將舊 token 停用（`Enabled = 0`）。
- ❌ 對外 API 回應或內部日誌中，直接印出或回傳 `HashKey` 的完整值 → ✅ 應遮蔽部分字元（如僅保留前後幾碼）或完全排除該欄位。
- ❌ `CreateTokenByOriginKey` 在新增 token 前未檢查是否已存在相同 `CompanyCode` + `HashKey` 且 `Enabled = 1` 的記錄 → ✅ 必須先將衝突的舊 token 設為 `Enabled = 0`，再新增，嚴格維持同一公司內單一有效 token 的唯一性。
- ❌ 停用 token（`Enabled` 設為 `0`）後，未同步執行 `DEL {prefix}:token:{HashKey}` 清除 Redis 快取 → ✅ 任何造成 token 失效的寫入操作，都應立即清除對應的 Redis Key，否則已失效 token 在 TTL 內仍可通過快取驗證。