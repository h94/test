# 建立商家帳號 (Create Business Account)

## 1. 場景目的
為指定商家建立子帳號，提供 account、role 等欄位，密碼必須以 bcrypt 進行雜湊儲存，status 預設為 1（啟用）。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/businesses/{businessCode}/accounts` | 建立商家帳號 |

---

## 3. 流程總覽

1. 接收到帶有 `businessCode` 與 account 資訊的請求
2. 驗證請求權限（需驗證通過）
3. 檢查 `{businessCode}` 對應的商家是否存在於 `gamesettings.businesses` 表中
4. 檢查帳號 `account` 在該 `businessCode` 下是否已存在（複合主鍵唯一性，`businesscode` + `account`）
5. 將傳入的明文 password 使用 bcrypt 進行雜湊
6. 寫入 `gamesettings.business_accounts` 表（status 預設為 1, role 為傳入值）
7. 記錄 `updatetime` 為當前時間戳
8. 回傳成功

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `BusinessController` | 接收 `POST /api/v1/businesses/{businessCode}/accounts` 請求，參數綁定 |
| 2 | Service | `IBusinessService.CreateBusinessAccount` | 協調業務邏輯：驗證商家、檢查帳戶是否存在、雜湊密碼、寫入 DB |
| 3 | Provider | `IGameSettingProvider` (或具體 Cassandra Provider) | 讀取 `businesses` 表確認商家存在、執行 `business_accounts` 的插入操作 |
| 4 | Helper | `BCrypt.HashPassword(plainPassword)` | 密碼強雜湊 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | gamesettings.businesses | Read (`SELECT WHERE businesscode=…`) | 驗證商家是否存在 |
| DB | gamesettings.business_accounts | Write (`INSERT`) | 寫入新帳號資訊 |
| DB | gamesettings.business_accounts | Read (`SELECT WHERE businesscode=… AND account=…`) | 檢查帳號是否重複（OCC 檢查） |
| Cache | Redis (BusinessCache) | 不需操作 | 此流程未明確操作快取。若存在 account 列表快取，需人工確認是否需要清除或更新快取 |
| Queue | N/A | 不需操作 | 此流程未發送 Queue 訊息 |

---

## 6. 重要規則

| 規則類別 | 規則描述 |
|---|---|
| 權限限制 | 需通過 ECFramework 驗證。僅有管理該商家帳號權限的角色可執行。 |
| 欄位限制 | `account` 為複合主鍵的一部分，建立後不可更新、不可刪除（主鍵語意）。 |
| 狀態值限制 | `status` 欄位預設為 `1`（啟用）。值限 `0`（凍結）或 `1`（啟用），由專用 API 變更。 |
| 密碼安全 | `password` 必須以 bcrypt 強雜湊儲存，禁止明文寫入 DB。 |
| 不可暴露資料 | `password` 欄位嚴禁在任何對外 API 回傳。 |
| 不可修改欄位 | `businesscode` + `account` 在 INSERT 後不可更新。 |
| 跨服務約束 | 不可直接對 `pricecenter` 資料庫進行寫入（除非另有明確流程）。 |
| 業務約束 | 建立帳號的 `businessCode` 必須對應至一個已存在的商家記錄。 |

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未通過驗證或權限不足 | 返回 401 或 403 錯誤 |
| `businessCode` 不存在 | 返回失敗，提示商家不存在 |
| 帳號 `account` 在該商家下已存在 | 返回衝突錯誤，提示帳號已存在 |
| password 為空或未提供 | 返回驗證錯誤 |
| 密碼雜湊過程失敗 | 返回伺服器錯誤（HTTP 500） |
| DB 寫入逾時或失敗 | 返回伺服器錯誤，不殘留不一致狀態（需人工確認是否有 Transaction 補償機制） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 正常建立帳號（提供合法 businessCode, account, password, role） | 返回成功，`status=1`，DB 中 password 為 bcrypt hash |
| TC02 | API Test | 建立帳號缺少必填欄位（如 password） | 返回 400 驗證錯誤 |
| TC03 | Permission Test | 未帶認證 token 或角色權限不足 | 返回 401/403 錯誤 |
| TC04 | Flow Test | 商家不存在 | 返回失敗提示，狀態碼需人工確認 |
| TC05 | API Test | 重複建立相同 account | 返回衝突錯誤提示 |
| TC06 | DB Verification | 驗證 DB 中的 password 非明文 | 透過查詢確認儲存值為 bcrypt 格式 (`$2a$…`) |
| TC07 | API Test | 查詢帳號列表 API (`GET /api/v1/businesses/{businessCode}/accounts`) | 回傳列表不包含 `password` 欄位 |

---

## 9. 高風險區域

| 風險類型 | 項目 | 說明 |
|---|---|---|
| 高風險 Table | `gamesettings.business_accounts` | 密碼寫入安全與不可暴露欄位 |
| Transaction | Cassandra 不支援傳統 RDBMS 的 Transaction，需注意寫入過程中無部分成功遺留 |
| Cache consistency | 若管理者透過列表 API 查詢帳號時有快取，建立後可能需清除相關 cache key（需人工確認實際實作） |
| Idempotency | 重複請求會因主鍵唯一性而失敗，屬於被動冪等，但需確保客戶端可處理衝突錯誤 |

---

## 10. 常見錯誤

| 錯誤行為 | 正確處理方式 |
|---|---|
| 直接將明文 password 寫入 DB | 必須總是使用 `BCrypt.HashPassword(password)` 進行雜湊 |
| API 回傳包含 `password` 欄位 | DTO 模型應明確排除此欄位 (`[JsonIgnore]` 或 DTO 不含此屬性) |
| 未檢查商家是否存在 | 必須先查詢 `businesses` 表確保外鍵關係存在 |
| 未處理 `account` 重複衝突 | Cassandra INSERT 若主鍵重複為 upsert 行為，需在應用層先檢查或透過 Lightweight Transaction（IF NOT EXISTS）防止覆蓋（需人工確認實作方式） |
| 無資料庫隔離查詢 | 建立時僅能基於指定的 `businessCode` 操作，不可跨商家查詢 |

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/businesses/{businessCode}/accounts`（BusinessController） |
| DB | `gamesettings.business_accounts`（Schema: businesscode, account, password, role, status, updatetime） |
| Code | `IBusinessService.CreateBusinessAccount` (Service Layer) |
| Rules | `password` 須 bcrypt 雜湊（來源：gamesettings-detail.md Section "password 欄位"） |
| Rules | `status` 預設值為 1，不可由客戶端直接傳入（來源：gamesettings-detail.md Section "status 欄位"） |
| Rules | `businesscode` 建立後不可更新，需依賴 `businesses` 主表（來源：gamesettings-detail.md Section "businesscode 欄位"） |
| Test Scenario | 帳號建立、密碼雜湊驗證（來源：來自 gamesettingservice 測試腳本，需人工確認路徑） |