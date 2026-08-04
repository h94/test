# 建立商家登入資訊

## 1. 場景目的
為指定商家帳號建立登入資訊記錄，用於後端登入驗證、狀態追蹤與稽核。記錄通常包含帳號、登入時間、Token 或 IP 等。建立成功後可供查詢或後續登入狀態檢查。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/businesses/{businessCode}/logininfos` | 建立登入資訊 |

**需要驗證權限**，僅後台管理／授權用戶可操作。

---

## 3. 流程總覽

1. Controller 接收 request，路徑參數含 `businessCode`，body 為 `BusinessAccountLogin`（可能含 `account`、`password` 或其他登入必要欄位）。
2. 驗證 `businessCode` 對應的商家存在且未過期（`subenddate` 檢查）。
3. 驗證該商家下的帳號存在（透過 `business_accounts` 查詢），且帳號狀態 `status = 1`。
4. 密碼驗證：比對 request 密碼（hash 後）與 DB 中的 `password`（bcrypt 比對）。
5. 若驗證通過，生成登入資訊（可能包含 session token、登入時間、IP 等），寫入儲存層（可能為 Cassandra 某表或 Redis，**需人工確認**）。
6. 回傳 `BusinessAccountLoginInfo` 物件（排除敏感欄位）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `BusinessController.PostLoginInfos` | 接收參數，呼叫 Service |
| 2 | Service | `IBusinessService.CreateLoginInfo` | 組合業務邏輯 |
| 3 | Provider（Storage） | Cassandra `business_accounts` | 讀取帳號與密碼 hash |
| 4 | Provider（Storage） | Cassandra `businesses` | 讀取商家訂閱狀態 |
| 5 | Provider（Cache/Log） | **需人工確認** | 寫入登入資訊記錄 |
| 6 | Service | - | 建立回傳物件（DTO） |
| 7 | Controller | - | 回傳 HTTP 200 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `gamesettings.businesses` | Read | 驗證商家存在與 `subenddate` 是否有效 |
| DB | `gamesettings.business_accounts` | Read | 查詢帳號、密碼（hash）、`status` |
| Cache/DB | **需人工確認** | Write | 寫入登入資訊（可能用 Redis `LoginCache` 或 Cassandra 特定表） |

**備註**：儲存層未在提供的 schema 或 detail 中明確記載用於 logininfos 的表，已知 Redis `LoginCache` 主要用於訂閱者登入，此處是否復用需人工確認。

---

## 6. 重要規則

- **權限限制**：API 需通過驗證（由 ECFramework 統一驗證），僅限後台操作員或具有對應商家管理權限者。
- **帳號狀態**：僅 `business_accounts.status = 1` 的帳號可登入，停用（0）則拒絕。
- **商家過期檢查**：必須讀取 `businesses.subenddate`，若 `subenddate < 今日日期`，則視為訂閱過期，**拒絕建立登入資訊**。
- **密碼安全**：密碼比對**僅使用 bcrypt 雜湊值**，傳輸與儲存均不得包含明文。任何 API 回傳不可包含 `password` 欄位。
- **不可回傳欄位**：`BusinessAccountLoginInfo` 回傳時排除 `password`、`authtoken`（若從商家表取得）。
- **Account 不可變更**：`business_accounts.account` 為主鍵的一部分，建立後不可修改。
- **登入資訊記錄**：建立後可能需記錄操作者（`updater` 或類似機制），**需人工確認**。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `businessCode` 不存在 | 回傳 404，提示「商家不存在」 |
| `businesses.subenddate` 小於今日 | 回傳 403，提示「訂閱已過期」 |
| `account` 不存在於該商家下 | 回傳 401，提示「帳號或密碼錯誤」 |
| `business_accounts.status` = 0 | 回傳 403，提示「帳號已停用」 |
| 密碼比對失敗 | 回傳 401，提示「帳號或密碼錯誤」 |
| DB 寫入失敗（登入資訊儲存層） | 回傳 500，記錄錯誤日誌 |
| 未通過驗證（無權限） | 回傳 401，提示「未授權」 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| LI-01 | Integration | 正常登入資訊建立（合法 account + 正確密碼） | 200，回傳 LoginInfo 且不含敏感欄位 |
| LI-02 | Permission | 無效 token 呼叫 API | 401 |
| LI-03 | Flow | 商家過期（subenddate 已過） | 403 |
| LI-04 | Flow | 帳號狀態為凍結（status=0） | 403 |
| LI-05 | Flow | 密碼錯誤 | 401 |
| LI-06 | Security | API 回傳內容檢查 | 確保不包含 `password`、`authtoken` |
| LI-07 | API | 帳號不存在（但商家存在） | 401 |

---

## 9. 高風險區域

- **密碼處理**：若誤用明文比對，將造成安全漏洞；必須嚴格使用 bcrypt 比對。
- **商家過期邏輯**：若未檢查 `subenddate`，已過期商家仍可登入，屬高風險。
- **帳號凍結狀態遺漏**：讀取帳號時若未過濾 `status = 1`，可能導致凍結帳號被登入。
- **登入資訊記錄儲存層不明**：因未確認儲存目標，若儲存層故障可能影響登入記錄完整性（不影響主流程但影響稽核）。

---

## 10. 常見錯誤

- ❌ **登入時直接明文比對密碼** → 應使用 `bcrypt.verify()`。
- ❌ **回傳物件忘記排除 `password`** → DTO 轉換時明確定義排除。
- ❌ **未檢查 `subenddate`** → 必須比對當前日期。
- ❌ **跨商家查詢** → 查詢 `business_accounts` 時必須限定 `businessCode`。
- ❌ **未將登入資訊寫入日誌或 Cache** → 導致後續狀態查詢失敗或稽核缺失（**需人工確認**預期行為）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/v1/businesses/{businessCode}/logininfos`（OpenAPI） |
| DB | `gamesettings.businesses`、`gamesettings.business_accounts` |
| Code | `IBusinessService.CreateLoginInfo`（基於服務介面推測） |
| Rules | `business_accounts.status` 唯 0/1；`password` 為 bcrypt hash；`subenddate` 格式檢查 |
| Detail | gamesettingservice-detail.md：`password` 僅內部比對，不可回傳；帳號查詢需帶 `status=1`；商家過期規則 |
| Schema | `gamesettings` keyspace 結構（business_accounts, businesses） |
| Redis | **未明確使用**（需人工確認 logininfos 是否快取於 Redis） |