# 建立商家

## 1. 場景目的

後台管理人員透過此流程建立一筆全新的商家（Business）記錄，包含商家代碼（businessCode）、認證令牌（authtoken）、聯絡信箱（email）等必要資訊。authtoken 必須以加密形式儲存，禁止明文寫入資料庫。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/businesses` | 建立商家，需驗證（✅） |

---

## 3. 流程總覽

1. 接收 HTTP POST 請求，Body 包含 Business 物件（businessCode, authtoken, email 等）。
2. 驗證請求參數：businessCode 非空、格式合規；email 格式；authtoken 必填。
3. 檢查 businesses 表，確認 businessCode 不存在（避免主鍵衝突）。
4. 對 authtoken 進行加密（使用系統內部的加密演算法，非雜湊）。
5. 組裝 INSERT 語句寫入 `gamesettings.businesses` 表。
6. 回傳 HTTP 200 成功（Response 不包含 authtoken）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `BusinessController.Post` | 接收請求、觸發驗證、呼叫 Service |
| 2 | Service | `IBusinessService.CreateBusiness` | 商業邏輯：檢查唯一性、加密 authtoken、組裝物件 |
| 3 | Provider / Repository | Cassandra driver (直接操作) | 執行 `INSERT INTO gamesettings.businesses` |
| 4 | Service | `IBusinessService.CreateBusiness` | 返回成功，不包含 authtoken 於 response |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `gamesettings.businesses` | Write (INSERT) | 建立商家記錄 |
| DB | `gamesettings.businesses` | Read (SELECT) | 檢查 businessCode 是否已存在 |
| Redis | N/A (本服務不直接操作) | — | 建立後可能由 syncservice 異步更新 BusinessCache（需人工確認） |

---

## 6. 重要規則

- **權限限制**：需通過 ECFramework 驗證（team token 或管理員身份）。
- **欄位限制**：
  - `businesscode`：主鍵，建立後不可修改。
  - `authtoken`：必須以加密方式儲存（如 AES），禁止明文。
  - `email`：必填，格式需合規，可作為管理者聯絡信箱。
- **不可暴露資料**：任何 GET 或 response 中皆不得回傳 `authtoken`。
- **TTL 規則**：無。
- **Transaction 規則**：Cassandra 不支援跨 partition 交易，此處僅單表 INSERT，依 Cassandra 一致性級別保證寫入。
- **Retry 規則**：若因競態條件導致 businessCode 重複，應返回衝突錯誤，客戶端可重新嘗試。
- **狀態值限制**：無。
- **不可修改欄位**：`businesscode`（主鍵建立後不可變更）；`inplaycount` 僅能由 `SetBusinessInplayGame` 操作。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| businessCode 已存在 | HTTP 409 Conflict 或自定義錯誤訊息，阻止重複建立 |
| authtoken 缺失或空白 | HTTP 400 Bad Request，驗證失敗 |
| email 格式無效 | HTTP 400 Bad Request |
| 未提供有效的驗證資訊（team token 失效） | HTTP 401 Unauthorized |
| Cassandra 寫入失敗（timeout） | HTTP 500 Internal Server Error，可重試 |
| 加密模組異常 | HTTP 500 Internal Server Error（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC-CB-01 | Integration Test | 正常流程，提供有效 businessCode、authtoken、email | HTTP 200，DB 中出現該筆記錄且 authtoken 非明文 |
| TC-CB-02 | API Test | 重複 businessCode | HTTP 409，DB 不增加記錄 |
| TC-CB-03 | API Test | 缺少 email | HTTP 400，不回寫 DB |
| TC-CB-04 | API Test | 缺少 authtoken | HTTP 400 |
| TC-CB-05 | Permission Test | 無 token 或過期 token 呼叫 | HTTP 401 |
| TC-CB-06 | Flow Test | 檢查 response body 是否包含 authtoken | 回應中絕對不可有 authtoken 欄位 |
| TC-CB-07 | Data Integrity | 確認 DB 中 authtoken 為加密後密文，非傳入的原始值 | 解密後可得原始 token |

---

## 9. 高風險區域

- **高風險 table**：`gamesettings.businesses`，authtoken 若洩露將導致整個商家的 API 存取權被濫用。
- **高風險 API**：`POST /api/v1/businesses`，需嚴格控管調用權限，避免任意建立商家。
- **跨服務資料同步**：建立後可能需觸發 syncservice 更新 Redis BusinessCache，否則其他服務可能抓到過期或不存在的商家；目前需人工確認此同步機制。
- **Transaction**：Cassandra 無事務，但唯一性檢查可最大限度避免重複插入；需注意極端情況下仍可能插入重複（若兩請求同時檢查後均插入），建議使用 `IF NOT EXISTS` 語法達成輕量級交易。
- **Cache consistency**：若 Redis 快取未及時更新，可能導致前台讀取不到新商家（責任歸屬 syncservice）。
- **Queue retry**：無。
- **Idempotency**：未實作，重複請求將回傳 409。

---

## 10. 常見錯誤

- ❌ **新人容易犯錯**：直接將客戶端傳入的 authtoken 明文存入資料庫。
- ❌ **AI 容易誤解**：誤認為 authtoken 採用雜湊（如 bcrypt），實際上它需要可解密還原（用於後續 API 呼叫），故應採用可逆加密。
- ❌ **常見漏檢查項目**：忘記在 response 中排除 authtoken，或忘記先查詢 businessCode 是否已存在。
- ❌ **常見錯誤流程**：未進行加密即寫入，或加密後忘記更新 `updatetime` 欄位。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由及方法 | `README` — BusinessController POST `/api/v1/businesses` |
| DB 寫入規則 | `gamesettings-detail.md` — businesses 表寫入限制：authtoken 須加密，businesscode 主鍵不可變更 |
| Service 方法 | Phase1 語意分析 — `IBusinessService.CreateBusiness` |
| authtoken 加密儲存政策 | `gamesettings-detail.md` — 「應以加密方式儲存，禁止明文」 |
| 不可回傳 authtoken | `gamesettings-detail.md` — 任何對外 API 回傳不可包含 authtoken |
| Redis 非本服務直接操作 | `gamesettings-detail.md` — 「本服務未直接使用 Redis」 |