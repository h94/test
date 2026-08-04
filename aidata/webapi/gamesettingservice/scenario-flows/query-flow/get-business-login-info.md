# 查詢登入資訊

## 1. 場景目的
查詢某個商家（businessCode）下，特定帳號（uid）的登入資訊記錄，供後台管理者追蹤帳號登入狀況。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/businesses/{businessCode}/logininfos/{uid}` | 查詢特定商家帳號的登入資訊 |

---

## 3. 流程總覽

1. 接收請求，解析路徑參數 `businessCode` 與 `uid`。
2. 驗證呼叫者身份與權限（需管理員權限）。
3. 依據 `businessCode` 確認商家存在（`businesses` 表）。
4. 查詢該商家下 `uid` 對應的帳號是否存在且狀態為啟用（`business_accounts` 表，`status = 1`）。
5. 讀取登入資訊資料（儲存層待定，僅推測可能為 MySQL GM 或 Cassandra log）。
6. 排除敏感欄位（如 `password`、`authtoken`）。
7. 回傳 `BusinessAccountLoginInfo` DTO。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `BusinessController.GetLoginInfo` | 接收參數，調用 Service |
| 2 | Service | `IBusinessService.GetLoginInfo` | 驗證商家與帳號，取得登入資訊 |
| 3 | Provider | `IBusinessRepository` | 查詢 Cassandra `business_accounts` |
| 4 | Provider | *(待確認)* | 查詢登入資訊實體（可能為MySQL或Redis） |
| 5 | Transfer | `BusinessAccountLoginInfo` | 組裝回應，排除敏感欄位 |

- 實際 Provider 調用需人工確認，目前僅推測儲存於 MySQL GM DB 或 Cassandra 中的特定 log 表。
- 也可能查詢 `pricecenter.accounts_{brand}` 的 `handler` 或 `enabled` 欄位，但與「登入資訊」語意不符。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `gamesettings.businesses` | Read | 確認 `businessCode` 存在 |
| DB | Cassandra `gamesettings.business_accounts` | Read | 確認帳號存在且狀態啟用 |
| DB | (待確認) MySQL GM 或 Cassandra | Read | 取得登入資訊記錄 |
| Cache | Redis `LoginCache` | 可能 Read | 若查詢即時登入狀態（非歷史） |

- **需人工確認**：登入資訊確切儲存表（可能是 GM DB 的 `logininfo` 或 Cassandra `action_logs` 等）。

---

## 6. 重要規則

- **權限限制**：僅具備管理員角色可查詢，呼叫者必須通過 ECFramework 驗證。
- **不可暴露欄位**：回傳 DTO 不得包含 `password`（business_accounts）或 `authtoken`（businesses）。
- **商家隔離**：查詢必須限定 `businessCode`，不可跨商家讀取帳號。
- **狀態限制**：若該帳號 `status = 0`（凍結），仍可回傳登入資訊（營運需要），但需在回應中標示帳號狀態。
- **TTL 規則**：若資料來自快取，應有 TTL 值，但快取未命中時需 fallback 至持久層。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 無效的 `businessCode`（不存在於 `businesses`） | 回傳 404，錯誤碼含「商家不存在」 |
| `uid` 指定的帳號不存在於該商家 | 回傳 404，錯誤碼含「帳號不存在」 |
| 呼叫者權限不足 | 回傳 403 |
| 登入資訊記錄不存在 | 可能回傳空資料或特定狀態碼 (404 或 200 空內容) |
| DB 查詢逾時 | 回傳 500，記錄錯誤日誌 |

- **需人工確認**：未登入過或無記錄時的回傳行為。

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| LI-01 | API Test | 存在的商家與帳號 | 200，回傳登入資訊 |
| LI-02 | API Test | 不存在的 `businessCode` | 404 |
| LI-03 | API Test | 帳號存在但屬其他商家 | 404 |
| LI-04 | Permission Test | 無效 Token 或非管理員 | 401/403 |
| LI-05 | Integration Test | 帳號凍結但仍查詢 | 200，可顯示狀態 |
| LI-06 | Flow Test | 確認 `password` 未出現在回應 | 回應中無此欄位 |

---

## 9. 高風險區域

- **敏感資料洩漏**：若錯誤回傳 `business_accounts.password` 或 `businesses.authtoken`，將造成資安事件。
- **跨商家資料存取**：若未嚴格過濾 `businessCode`，可能導致其他商家登入記錄外洩。
- **快取一致性**：若登入資訊來自快取，狀態變更時需確保清除快取，否則回傳過期資料。
- **需人工確認**：確切儲存層與快取策略。

---

## 10. 常見錯誤

- ❌ 查詢時未指定 `businessCode`，直接以 `uid` 全表掃描 `business_accounts`。
- ❌ 回傳 DTO 包含 `password` 或 `authtoken` 欄位。
- ❌ 忘記檢查 `status` 狀態，將凍結帳號當作無效帳號而拒絕查詢。
- ❌ 未對空結果做防禦處理，導致 NPE。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | README - `GET /api/v1/businesses/{businessCode}/logininfos/{uid}` |
| 回應模型 | OpenAPI - `BusinessAccountLoginInfo` |
| DB 權限規則 | gamesettings-service-detail.md - `business_accounts` 讀取限制 |
| 不可回傳欄位 | gamesettings-service-detail.md - password / authtoken 不可回傳 |
| Redis 使用 | README - Redis LoginCache 用於訂閱者登入狀態；本流程是否使用待確認 |
| 儲存層待確認 | 目前 DB schema 無明確 `logininfos` 表，**需人工確認**實際儲存位置 |

---

**⚠️ 聲明**：此場景中「登入資訊」的具體儲存與結構需由團隊確認，文件僅基於既有 API 規格與服務邊界推論，實際實作可能不同。