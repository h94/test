# 查詢月份進行中賽事

## 1. 場景目的
查詢指定商家（Business）在特定月份範圍內，已被設定為「進行中」的賽事 ID 列表。此流程僅讀取已由管理員透過 `POST /api/v1/businesses/{businessCode}/inplaygames` 預先設定的賽事資訊，不包含即時動態賽事。

---

## 2. 入口 API

| Method | Path                                          | 說明                     |
|--------|-----------------------------------------------|--------------------------|
| GET    | `/api/v1/businesses/{businessCode}/inplaygames/{month}` | 查詢指定商家月份進行中賽事 |

---

## 3. 流程總覽

1. 接收請求，解析 `businessCode` 與 `month`
2. 透過內部驗證框架檢查呼叫方權限（Team Auth）
3. 查詢 `gamesettings.businesses` 驗證 `businessCode` 存在且有效（訂閱未過期）
4. （需人工確認）依 `businessCode` 與 `month` 從對應儲存後端取得賽事 ID 列表
5. 回傳賽事 ID 陣列（`application/json`）

---

## 4. 程式流程

| 順序 | Layer      | Class / Method                          | 動作                                               |
|------|------------|-----------------------------------------|----------------------------------------------------|
| 1    | Middleware | ECFramework.ECService Auth              | 驗證呼叫方 Token 與權限                            |
| 2    | Controller | BusinessController.GetInplayGames       | 接收參數，轉交 Service                             |
| 3    | Service    | IBusinessService                        | 呼叫 `GetMonthInplayGames(businessCode, month)`    |
| 4    | Repository | (需人工確認)                             | 從儲存層讀取賽事列表                                |

---

## 5. DB / Cache / Queue 使用

| 類型  | 資源                         | 操作 | 用途                               |
|-------|------------------------------|------|------------------------------------|
| DB    | `gamesettings.businesses`    | Read | 驗證商家存在、讀取訂閱狀態         |
| DB    | (需人工確認)                  | Read | 取得指定月份的賽事 ID 列表         |
| Redis | 無                           | –    | –                                  |
| Queue | 無                           | –    | –                                  |

---

## 6. 重要規則

- **權限限制**：所有對 `/api/v1/businesses` 的請求皆需通過驗證，驗證方式依 `ECFramework.ECService` 團隊憑證機制。
- **訂閱有效性**：查詢商家時必須檢查 `subenddate`，若 `subenddate` 早於當前日期，則該商家不應回傳任何賽事（需人工確認實際實作是否包含此檢查）。
- **資料範圍**：查詢範圍僅限已由管理員設定之賽事，非即時滾球列表。
- **回傳格式**：回傳值為 `string` 陣列（賽事 ID）。
- **不可回傳欄位**：商家資訊（如 `authtoken`、`password`）不可外洩。

---

## 7. 錯誤情境

| 情境                             | 預期結果                         |
|----------------------------------|----------------------------------|
| 未提供合法驗證 Token              | HTTP 401 / 403                   |
| `businessCode` 不存在            | HTTP 404 或空列表（需人工確認）   |
| `businessCode` 對應商家已過期     | HTTP 400 或空列表（需人工確認）   |
| `month` 格式錯誤（非預期格式）    | HTTP 400 或空列表                 |
| 資料庫查詢無結果                  | HTTP 200，回傳空陣列 `[]`         |

---

## 8. 測試重點

| Test ID | 類型               | 情境                                       | 預期結果               |
|---------|-------------------|--------------------------------------------|------------------------|
| T01     | Permission Test    | 無 Token 請求                               | 401                    |
| T02     | Permission Test    | 使用過期或不合法 Token                      | 401 / 403              |
| T03     | API Test           | 存在且有效的 `businessCode` + 合法 `month`  | 200，回傳賽事 ID 陣列   |
| T04     | API Test           | 不存在的 `businessCode`                     | 404 或 `[]`            |
| T05     | API Test           | 已過期商家                                 | 400 或 `[]`            |
| T06     | Flow Test          | 先 `POST` 設定賽事，再 `GET` 確認          | 返回剛設定的賽事 ID    |
| T07     | Data Integrity Test| 檢查回傳的 ID 是否為實際已設定之賽事        | 資料一致               |

---

## 9. 高風險區域

- **業務資料範圍隔離**：必須確保查詢僅限於指定 `businessCode`，不可跨商家洩漏賽事資料。
- **訂閱過期控制**：若未檢查 `subenddate` 可能導致已過期商家持續使用服務。
- **資料來源一致性**：若賽事儲存與商家設定分屬不同服務/DB，需確保讀取路徑的一致性與延遲問題。

---

## 10. 常見錯誤

- 忘記在查詢前校驗 `businessCode` 是否存在，導致空指針或誤判。
- 直接回傳未過濾的內部資料結構，可能暴露不該回傳的商家欄位（如 `authtoken`）。
- 月份格式與資料庫儲存格式不一致，導致查詢永遠回傳空陣列。
- 認為此 API 會回傳即時滾球賽事，但實際僅為管理員手動設定的資料。

---

## 11. Evidence

| 類型    | 來源                                                                                     |
|---------|------------------------------------------------------------------------------------------|
| API     | OpenAPI: `GET /api/v1/businesses/{businessCode}/inplaygames/{month}`                     |
| 權限    | README 標記 ✅ (需要驗證)                                                                 |
| DB      | `gamesettings.businesses` table（儲存商家資訊、訂閱日期）                                 |
| 資料來源| 需人工確認：賽事列表儲存於何處（可能為 Cassandra 其他表或外部服務）                       |
| 規則    | gamesettings-detail.md: `subenddate` 過期應拒絕查詢                                      |
| 相依    | 可能依賴 `pricecenterservice` 提供賽事資訊，但實際調用方式未明確                           |