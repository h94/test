# 場景：驗證 Licence Token

## 1. 場景目的

驗證 Client 端傳入的 `originKey` 與 `token` 是否為有效的授權 Token。系統根據 `originKey` 計算 HashKey，再結合請求來源的 `CompanyCode` 查詢 MySQL `tokens` 表，確認 Token 存在、啟用且未過期，並比對傳入的 `token` 參數是否與系統紀錄一致。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/licence/check` | 驗證 Licence Token 有效性 |

**參數**：

| 名稱 | 位置 | 必要 | 說明 |
|------|------|------|------|
| originKey | query | 是 | 原始金鑰，用於計算比對的 Hash |
| token | query | 是 | Client 端持有的 Token 字串 |

**回應**：`boolean`（`true` 有效，`false` 無效）

---

## 3. 流程總覽

1.  接收 GET 請求，取得 `originKey` 與 `token` 查詢參數。
2.  從請求認證上下文（`authKey` 或對應的 `CompanyCode` 解析機制）取得呼叫方的 `CompanyCode`。
    - **需人工確認**：實際提取 CompanyCode 的具體方式（例如：從 JWT payload、API Key mapping 或 Header 解析）在提供的 code evidence 中未完全展露，需確認 `TokenController` 中 `_context.CompanyCode` 的賦值流程。
3.  使用與 `CreateTokenByOriginKey` 相同的雜湊演算法，將傳入的 `originKey` 計算為 `HashKey`（長度應為 10 字元）。
4.  查詢 MySQL `tokens` 表：
    - 條件：`CompanyCode` = 呼叫方代碼 **AND** `HashKey` = 計算出的 HashKey **AND** `Enabled` = 1 **AND** `ExpirationTime` > 當前時間 (UTC)。
5.  若查無相符記錄，回傳 `false`。
6.  若有相符記錄，比對請求中的 `token` 參數是否與資料庫中的 Token 值一致（具體比對邏輯須包含原始 Token 字串組合或解密，可能涉及 `originKey` 的關聯）。
    - **需人工確認**：需確認比對的是 `HashKey` 本身，還是利用 `HashKey` + `CompanyCode` 等資訊組合生成的完整 Token 字串。根據 OpenAPI 回應僅為 Boolean，推測為內部直接比對。
7.  比對成功則回傳 `true`，失敗則回傳 `false`。
8.  流程中**不操作 Redis**，直接讀取資料庫。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `TokenController.CheckLicence` | 接收 `originKey`, `token` 參數 |
| 2 | Service | `TokenService.CheckLicence` | 協調查詢邏輯，調用 Hash 計算與 DB 查詢 |
| 3 | Service | `TokenService` (私有方法) | 根據 `originKey` 計算 `HashKey`（10 字元） |
| 4 | Provider / ORM | `TokenDataProvider` / `DbContext` | 依 `CompanyCode`, `HashKey`, `Enabled=1`, `ExpirationTime > NOW()` 查詢 `tokens` 表 |
| 5 | Service | `TokenService.CheckLicence` | 比對查詢結果與傳入的 `token` 字串 |
| 6 | Service | `TokenService` (私有方法) | 呼叫 `setLog` 寫入操作紀錄 (`Action`: "Token Validation Request") |
| 7 | Controller | `TokenController.CheckLicence` | 回傳 Boolean 結果 |

- **需人工確認**：Controller 的實際命名可能非 `CheckLicence`（例如 `CheckLicenceToken`），需核實 `TokenController.cs` 的實際方法名稱。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `tokens` | Read (SELECT) | 依 `CompanyCode`, `HashKey`, `Enabled=1`, `ExpirationTime > NOW()` 查詢有效 Token |
| DB | `logs` | Write (INSERT) | 寫入本次驗證請求的操作紀錄 (`Action`: "Token Validation Request") |
| DB | `logs` | Write (INSERT) | 若驗證成功，可能需記錄成功事件（需視 Service 層完整邏輯確認） |
| Redis | none | - | **此場景不操作 Redis** |
| Kafka | - | - | **此場景不操作 Kafka**（日誌是透過 `setLog` 寫入 MySQL `logs` 表） |

---

## 6. 重要規則

- **權限限制**：`CompanyCode` 必須由系統從請求認證資訊中解析，不可由 Client 直接指定。
- **欄位限制**：查詢 `tokens` 表時，**務必**包含 `Enabled = 1` 與 `ExpirationTime > NOW()`。
- **HashKey 生成**：計算 HashKey 的雜湊演算法必須與 `CreateTokenByOriginKey` 完全一致。
- **狀態檢查**：僅檢查 `Enabled = 1` 的 Token；已停用 (`Enabled = 0`) 或過期的 Token 視為無效。
- **不可暴露資料**：任何情況下，API 回應都不得包含 `HashKey` 值。
- **操作日誌**：驗證請求（無論成功或失敗）通常應記錄至 `logs` 表。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 缺少 `originKey` 或 `token` 參數 | 回傳 `false` 或 HTTP 400 |
| `originKey` 計算出的 HashKey 在 `tokens` 表中不存在 | 回傳 `false` |
| Token 存在但 `Enabled` = 0 | 回傳 `false` |
| Token 存在但 `ExpirationTime` < NOW() | 回傳 `false` |
| Token 存在且有效，但傳入的 `token` 參數與系統內值不符 | 回傳 `false` |
| DB 查詢失敗 (timeout / connection lost) | 回傳 `false` 或 HTTP 500（取決於全域例外處理設定） |
| 請求來源無法解析出 `CompanyCode` | 回傳 `false` 或 HTTP 401 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| LIC-01 | API Test | 傳入有效的 `originKey` 與對應的 `token` | 回傳 `true` |
| LIC-02 | API Test | 傳入有效 `originKey` 但錯誤 `token` | 回傳 `false` |
| LIC-03 | API Test | 傳入的 `originKey` 從未被建立 Token | 回傳 `false` |
| LIC-04 | Flow Test | Token 存在且 Enabled=1，但已過期 | 回傳 `false` |
| LIC-05 | Flow Test | Token 存在且未過期，但 Enabled=0（被停用） | 回傳 `false` |
| LIC-06 | Permission Test | 嘗試指定不同的 `CompanyCode`（若 API 設計允許） | 回傳 `false`（因 Token 不屬於該公司） |
| LIC-07 | Integration Test | DB 無法連線時的處理 | 回傳 `false` 或記錄錯誤 log |
| LIC-08 | API Test | 缺少 `originKey` 或 `token` 參數 | 回傳 `false` |

---

## 9. 高風險區域

- **SQL Injection**：查詢 `tokens` 表時必須使用參數化查詢，不可拼接 SQL。
- **雜湊演算法一致性**：確保驗證時計算 `HashKey` 的演算法與產生時相同，否則有效 Token 會永遠驗證失敗。
- **時間同步**：`ExpirationTime` 的比較依賴於應用程式伺服器與 MySQL 伺服器的時間同步（基於 UTC）。
- **CompanyCode 注入**：若 Client 端可偽造 CompanyCode，則可繞過權限驗證。必須確保 CompanyCode 來自伺服器端的可靠來源。

---

## 10. 常見錯誤

- ❌ **直接查詢而不檢查 `Enabled` 和 `ExpirationTime`**：這是最常見且危險的錯誤，會導致已停用或過期的 Token 通過驗證。
- ❌ **誤將 `originKey` 直接當作 `HashKey` 查詢**：必須先經過雜湊運算。
- ❌ **忘記記錄 Log**：在驗證流程中，應正確呼叫 `setLog` 寫入操作軌跡，以便後續稽核。
- ❌ **比對 Token 時未考慮大小寫或編碼**：儘管 Token 通常為固定格式，但字串比對仍應注意潛在的誤判。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `TokenController` - `/api/v1/licence/check` 路由定義 (OpenAPI) |
| Parameters | `originKey`, `token` (OpenAPI path `/api/v1/licence/check`) |
| Response | `boolean` (OpenAPI path `/api/v1/licence/check`) |
| DB | `tokens` table (DB schema `tokens.md` / `tokens.md`) |
| DB 欄位 | `HashKey`, `CompanyCode`, `Enabled`, `ExpirationTime` (DB schema + `tokens-detail.md`) |
| 重要規則 | 查詢必須包含 `Enabled = 1` AND `ExpirationTime > NOW()` (`tokenservice-detail.md`) |
| 重要規則 | 不操作 Redis (`tokenservice-detail.md`：Redis 操作僅列於 CheckToken，未述及此場景) |
| Code | `TokenService.cs`：`generateHashKey()`, `setLog()` (Source code semantics batch-5) |
| Log 紀錄 | `logs` table, `Action` 欄位內容 (`'Token Validation Request: ' + hashKey`) (Source code semantics batch-5) |