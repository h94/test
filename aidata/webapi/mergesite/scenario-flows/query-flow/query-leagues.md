# 場景：取得聯盟列表

## 1. 場景目的

提供管理後台一個依球種代碼、可選的時間範圍、名稱或聯盟 ID 查詢聯盟清單的介面。此列表用於審視、比對與管理各球種下的聯盟資訊，不支援分頁，需人工確認

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/leagues/{gameType}` | 取得特定球種的聯盟列表。支援時間、名稱、ID 等可選篩選條件 |

來源：README.md API 路由表

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，路徑包含必填的 `gameType`，查詢參數可包含 `startDate`、`endDate`、`startTime`、`endTime`、`lName`、`lid`
2. 通過 ECCore 驗證機制，確認請求者具備後台管理權限
3. Controller 接收請求並轉交 Service 層處理
4. Service 透過 Provider 層，以 Gateway 模式對外呼叫 PriceCenterService 提供的 REST API
5. mergesite 收到 PriceCenterService 回傳的聯盟資料
6. 將結果反序列化為 `LeagueDTO` 列表後回傳

資料流：Client → Controller → Service → Provider → (Gateway) → PriceCenterService

來源：README.md 服務相依、mergesite-detail.md 服務不負責事項

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | LeaguesController.GetLeagues(gameType, queryParams) | 接收請求，委派 Service |
| 2 | Service | LeagueService.QueryLeagues(gameType, queryParams) | 組合查詢條件並呼叫 Provider |
| 3 | Provider | PriceCenterProvider.FetchLeagues(gameType, queryParams) | 透過 Gateway 向 PriceCenterService 發送 HTTP GET 請求 |
| 4 | Transfer | LeagueDTO | 將來自 PriceCenterService 的回應反序列化為 DTO 物件 |
| 5 | Controller | LeaguesController.GetLeagues() | 回傳 `List<LeagueDTO>` 給前端 |

需人工確認：Controller 與 Service 的具體類別名稱與方法簽名，及 Provider 使用的實際 Gateway Client 類別

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| 需人工確認 | – | – | mergesite 此查詢不直接操作任何資料庫。所有資料由 PriceCenterService 負責查詢與回傳。是否使用內部快取或 Queue 取決於該服務的實作 |

來源：README.md（資料庫：無）、pricecenter-detail.md mergesite 角色為 writer

---

## 6. 重要規則

- **權限限制**：此 API 需要驗證。只有通過 ECCore 認證的管理後台使用者才能存取
- **欄位限制**：
  - `gameType` 為必填路徑參數，不可為空
  - 日期與時間參數為可選的字串格式，須符合 PriceCenterService 接受的格式（規格未定義）
  - `lid` 與 `lName` 為可選的篩選條件
- **不可暴露資料**：回傳的 `LeagueDTO` 不應包含任何內部管理的敏感資訊（例如 PriceCenter 的內部鍵值），僅限業務所需的聯盟資訊
- **無 Transaction**：此為唯讀查詢，不涉及跨服務的交易或寫入操作
- **無 Retry 規則**：此查詢依賴 PriceCenterService 即時回應。若呼叫失敗，應由前端處理錯誤提示，或由 Gateway 層面實作重試（需人工確認）

來源：OpenAPI 規格、README.md 關聯服務

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 缺少路徑參數 `{gameType}` | 由 ASP.NET Core 路由機制回傳 404 Not Found |
| 驗證失敗（未登入或 Token 無效） | ECCore 中介軟體攔截，回傳 401 Unauthorized |
| PriceCenterService 無回應或逾時 | Gateway 或 Provider 拋出例外，最終回傳 500 Internal Server Error 或 504 Gateway Timeout |
| 傳入不合法格式的日期參數 | PriceCenterService 回傳錯誤，mergesite 依其定義回傳對應的錯誤碼與訊息（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SL001 | API Test | 不帶任何可選參數，僅提供有效的 `gameType` | 200 OK，回傳該球種所有聯盟列表 |
| SL002 | Integration Test | 帶入 `startDate` 與 `endDate` 查詢區間內的聯盟 | 200 OK，僅回傳符合時間條件的聯盟 |
| SL003 | Integration Test | 帶入 `lid` 查詢特定 ID | 200 OK，回傳一筆或零筆符合該 ID 的聯盟 |
| SL004 | Permission Test | 未攜帶有效的認證 Token 請求 API | 401 Unauthorized |
| SL005 | Flow Test | `PriceCenterService` 服務中斷時請求 | 500 或 504 錯誤，前端應顯示友善提示訊息 |

---

## 9. 高風險區域

- **跨服務資料同步**：此流程完全依賴 PriceCenterService 提供正確且即時的聯盟資料。若該服務資料有延遲或不一致，本列表將無法反映真實狀態
- **外部 API 相依性**：mergesite 對外的 Gateway 呼叫為單點依賴。若 PriceCenterService 不可用，整個聯盟查詢功能將全面癱瘓
- **無資料庫**：由於 mergesite 本身無狀態，無法進行任何查詢結果的快取或降級處理，風險集中於下游服務

來源：README.md 服務相依

---

## 10. 常見錯誤

- 新人容易誤認為 mergesite 有自己的資料庫，試圖在 `sport` 或 `pricecenter` 資料庫中直接搜尋邏輯
- AI 可能誤解此流程會寫入 Kafka（mergesite 的 Log 寫入僅限於特定操作，此唯讀查詢可能不寫入，需人工確認）
- 常見漏檢查項目：未驗證 `gameType` 是否為有效的球種代碼（應由 PriceCenterService 驗證，但前端亦可先檢查）
- 錯誤流程：在 mergesite 內實作快取而導致資料不一致，因資料的寫入權在 PriceCenterService

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI: GET /api/leagues/{gameType} |
| 服務相依 | README.md: 服務相依 PriceCenterService |
| DB | README.md: 此服務無直接資料庫 |
| 權限 | README.md: API 需要驗證 ✅ |
| 回傳結構 | OpenAPI: responses 200 的 content 引用 `LeagueDTO` |