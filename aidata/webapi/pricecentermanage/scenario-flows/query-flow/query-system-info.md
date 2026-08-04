# 查詢系統資訊

## 1. 場景目的
提供管理後台查詢 `pricecentermanage` 服務本身的系統資訊，包含服務版本、組態、運行環境等。用於監控與診斷。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/system/info` | 查詢 pricecentermanage 服務的系統資訊，需要驗證。 |

---

## 3. 流程總覽

1. 接收後台管理員的 GET 請求。
2. 透過 ECFramework.ECService 中介軟體進行權限驗證。
3. 驗證通過後，`SystemController` 接收請求。
4. 系統收集自身運行資訊，包含：
   - 服務版本
   - 組態狀態 (來源: Zookeeper 連線狀態)
   - 系統資源使用狀況 (推測: CPU, Memory)
   - 依賴服務狀態 (推測: DB, Redis, Kafka 連線狀態)
5. 組裝 `SystemInfo` 物件並回傳 200 OK。
6. 若驗證失敗，回傳 401 Unauthorized。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Middleware | `ECFramework.ECService` | 驗證請求的 Auth Token。 |
| 2 | Controller | `SystemController.GetSystemInfo` (推測) | 接收請求，呼叫 Service 層。 |
| 3 | Service | `SystemService.GetSystemInfo` (推測) | 收集服務資訊，組合回傳物件。 |
| 需人工確認 | Provider | 無特定 Provider | 此流程為查詢內部狀態，推測不直接存取 DB。 |
| 需人工確認 | Validator | 無 | 無需特定輸入驗證。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| 需人工確認 | Cassandra `pricecenter` | Read | 可能讀取 `extension_version` 或 `machines` 表來確認服務與機器的最新狀態。（此為推測，實際可能僅從記憶體或配置檔讀取） |
| 需人工確認 | Redis `SportCache` | Read | 無直接用途，除非系統資訊中包含快取命中率等統計。 |

---

## 6. 重要規則

- **權限限制**：此 API 在 README 中標記為 `需要驗證`，應僅限管理員角色存取。
- **不可暴露資料**：回傳的資訊中，絕對不可包含任何資料庫的連線字串、密碼、IP 或內部拓樸等敏感資訊。
- **狀態值限制**：無。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 請求未附帶有效的 Auth Token | 回傳 `401 Unauthorized`。 |
| Auth Token 權限不足 | 回傳 `403 Forbidden`。 |
| 服務內部錯誤（如收集資訊時例外） | 回傳 `500 Internal Server Error`，並記錄錯誤日誌至 Kafka。 |
| 請求方法錯誤（如使用 POST） | 回傳 `405 Method Not Allowed`。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| SYS-INFO-01 | Permission Test | 使用無效 Token 呼叫 API | 回傳 `401`。 |
| SYS-INFO-02 | Permission Test | 使用一般使用者 Token 呼叫 API | 回傳 `403`。 |
| SYS-INFO-03 | API Test | 使用有效管理員 Token 呼叫 API | 回傳 `200`，且包含版本及時間戳資訊。 |
| SYS-INFO-04 | API Test | 驗證回傳內容 | 確保不包含 IP、DB 密碼等敏感字串。 |

---

## 9. 高風險區域

- **高風險 API**：`/api/v1/system/info` 若權限控管不當，可能洩漏服務內部資訊，成為攻擊者的資訊收集來源。
- **需人工確認**：Transaction, Queue retry 等機制在此唯讀場景中不適用。

---

## 10. 常見錯誤

- **新人容易犯錯**：在 `SystemInfo` 的回傳物件中，不小心包含了資料庫連線字串或內部配置，導致敏感資訊外洩。
- **AI 容易誤解**：可能誤認為此 API 需要查詢所有站台的資訊，但根據名稱 `System Info`，其目的應為回傳服務本身的狀態，而非外部資料。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md - `GET /api/v1/system/info` |
| 權限 | README.md - 該路由標記為 `需要驗證` |
| 驗證框架 | README.md - 技術棧 `ECFramework.ECService 2.0.0` |
| Code | 需人工確認 `Controller` 實際名稱 (推測 `SystemController`) |
| DB | 需人工確認 'DB / Cache / Queue 使用' 章節的推測 |