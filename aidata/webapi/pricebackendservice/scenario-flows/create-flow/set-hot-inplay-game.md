# 設定熱門進行中賽事

## 1. 場景目的
後台管理員將特定進行中的賽事標記為熱門，使該賽事在用戶端（如遊戲直播、社群、賽事列表）優先曝光。

---

## 2. 入口 API

| Method | Path                                                              | 說明                     |
|--------|-------------------------------------------------------------------|--------------------------|
| POST   | `/api/v1/pricecenter/games/inplay/hot/{gameType}/{lid}/{gDate}/{gid}` | 設定熱門進行中賽事，需後台驗證 |

- 預期 Request Body 包含 `hot` (boolean) 欄位。
- `gameType`：遊戲類型代碼，如 basketball、football。
- `lid`：聯賽 ID。
- `gDate`：賽事日期，格式 yyyy-MM-dd。
- `gid`：賽事 ID。

---

## 3. 流程總覽

1. 管理員通過後台發起 HTTP POST 請求，攜帶路徑參數及 body。
2. 經 `ECFramework` 統一驗證框架檢查身份與後台權限。
3. Controller 接收並解析參數，調用對應 Service。
4. Service 組裝請求，透過 HTTP Client 轉發至下游 **pricecenter** 微服務。
5. pricecenter 服務驗證賽事存在且為進行中狀態，更新其 `hot` 屬性，並可能使相關 Redis 快取失效。
6. 回傳成功結果至前端。

---

## 4. 程式流程

> 因缺乏原始碼，以下為基於慣例推測，**需人工確認**。

| 順序 | Layer      | Class / Method (推測)                          | 動作                                                   |
|------|------------|------------------------------------------------|--------------------------------------------------------|
| 1    | Controller | `PriceCenterController.SetInPlayGameHot()`    | 接收路徑參數與 body，呼叫 Service                     |
| 2    | Service    | `PriceCenterService.SetInPlayGameHotAsync()`   | 組裝下游請求 DTO，呼叫 Provider                       |
| 3    | Provider   | `PriceCenterApiClient` (HttpClient)           | 發送 HTTP 請求至 pricecenter 微服務                   |
| 4    | 下游 API   | (pricecenter 服務內部)                         | 驗證並更新 DB，回傳結果                               |

---

## 5. DB / Cache / Queue 使用

- **本服務無直接 DB 存取**，所有操作由下游 pricecenter 服務完成。
- 下游可能的資源操作（**需人工確認**）：

| 類型  | 資源                          | 操作        | 用途                            |
|-------|-------------------------------|-------------|---------------------------------|
| DB    | (pricecenter 內部 MySQL/Cassandra) | UPDATE      | 設定賽事 `hot` 標記            |
| Redis | 熱門賽事相關快取 key          | DELETE / SET | 確保前端讀取到最新熱門狀態     |

---

## 6. 重要規則

- **權限限制**：必須登入後台，且具備體育賽事管理權限。
- **參數規則**：
  - `gameType` 須為系統預定義的有效類型。
  - `lid`、`gid` 必須對應存在且狀態為「進行中」的賽事。
  - `gDate` 格式須符合 `yyyy-MM-dd`，並與賽事日期吻合。
  - `hot` 必須為 boolean。
- **不可暴露資料**：無敏感資料。
- **Transaction**：單一操作，無跨資源交易需求（由下游保證一致性）。
- **Retry 規則**：操作為冪等（可重複設定相同狀態），呼叫下游失敗時可重試。
- **狀態值限制**：僅允許修改 `hot` 屬性，不可變更賽事比分、狀態等欄位。

---

## 7. 錯誤情境

| 情境                                      | 預期結果                     |
|-------------------------------------------|------------------------------|
| 缺少必要路徑參數                          | 400 Bad Request              |
| `gameType` 不合法                         | 400 Bad Request              |
| `gid` 對應賽事不存在                      | 404 Not Found（或業務錯誤碼）|
| 賽事非進行中（已結束、未開始）            | 422 Unprocessable Entity     |
| 未攜帶有效認證 token                      | 401 Unauthorized             |
| 權限不足（非管理員）                      | 403 Forbidden                |
| 下游 pricecenter 服務回應 5xx             | 500 Internal Server Error    |
| 呼叫下游超時                              | 504 Gateway Timeout          |
| Body 格式錯誤（`hot` 非 boolean）         | 400 Bad Request              |

---

## 8. 測試重點

| Test ID | 類型            | 情境                                | 預期結果               |
|---------|-----------------|-------------------------------------|------------------------|
| TC1     | API Test        | 正常設定 `hot=true`                 | 200 OK                 |
| TC2     | API Test        | 正常設定 `hot=false`（取消熱門）    | 200 OK                 |
| TC3     | API Test        | 無效 `gameType`                     | 400                    |
| TC4     | API Test        | 不存在賽事                          | 404 或業務錯誤         |
| TC5     | API Test        | 賽事狀態為未開始或已結束            | 422                    |
| TC6     | Permission Test | 未帶 token                          | 401                    |
| TC7     | Permission Test | 一般會員 token                      | 403                    |
| TC8     | Flow Test       | 設定後查詢賽事列表確認 `hot` 屬性   | `hot` 為 true          |
| TC9     | Flow Test       | 模擬下游服務 500 錯誤               | 500，並記錄錯誤日誌    |

---

## 9. 高風險區域

- **跨服務依賴**：強依賴 pricecenter 服務可用性，需有熔斷與超時控制。
- **快取一致性**：若下游未即時清除熱門賽事快取，前端可能顯示過期狀態。
- **並發操作**：多管理員同時標記同一賽事無衝突，但須確保狀態正確覆蓋。
- **賽事狀態驗證**：必須在 pricecenter 服務端驗證賽事確實為 inplay，否則可能出現邏輯錯誤。

---

## 10. 常見錯誤

- 未檢查賽事是否為進行中，導致已結束賽事仍可被標為熱門。
- 前端未正確處理 `hot=false`，仍停留在舊的熱門狀態。
- 呼叫下游 API 未設置超時，造成請求阻塞。
- 未記錄操作日誌，排查困難。
- 忽略下游服務回傳的業務錯誤碼，僅以 HTTP 200 判斷成功。

---

## 11. Evidence

| 類型       | 來源                                                                                  |
|------------|---------------------------------------------------------------------------------------|
| API        | README.md - `POST /api/v1/pricecenter/games/inplay/hot/{gameType}/{lid}/{gDate}/{gid}` |
| 驗證       | README.md - 需要驗證 ✅                                                               |
| 服務相依   | README.md - 「服務相依」表格中對 `pricecenter` 的描述                                 |
| DB 邊界    | service-detail.md - 「本服務不直接存取資料庫」                                        |
| Controller | **需人工確認**，推測存在 `PriceCenterController`                                      |
| Service    | **需人工確認**，推測存在 `PriceCenterService`                                         |

---

> **需人工確認事項**
> - 實際 Controller / Service 類別與方法名稱
> - 下游 pricecenter 微服務的具體內部 API 路徑與 Request Body 格式
> - pricecenter 內部 DB 表結構（是否為 sport MySQL 的 `games` 表或其它）
> - Redis 快取 key 的具體前綴與清除機制