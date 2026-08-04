# 設定 AI 熱門討論賽事

## 1. 場景目的

後台管理員透過此 API 指定特定賽事為「AI 熱門討論」項目，供前端或推薦系統標記使用，以提升特定賽事的曝光。此功能為管理後台操作，需驗證身份。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/news/ai/hotdiscussiongames` | 設定 AI 熱門討論賽事 |

---

## 3. 流程總覽

1. 後台管理員提交賽事標記資訊（如 `gtype`, `lid`, `gdate`, `gid` 等）
2. `PriceBackendService` 驗證請求者權限（需登入且具管理員權限）
3. 將請求轉發至 `newsservice`（或合併呼叫 `pricecenter`），執行熱門賽事設定
4. 設定成功後回傳 200；若失敗則回傳對應錯誤碼

> **需人工確認**：實際寫入的儲存體（DB table、Redis）與下游服務確切呼叫細節，需由擁有程式碼存取權的工程師補充。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `NewsController.SetAIHotDiscussionGames` | 接收請求，呼叫 Service |
| 2 | Service | `NewsService.SetHotDiscussionGamesAsync` | 驗證參數，組裝 DTO，呼叫下游 Provider |
| 3 | Provider | `NewsProvider.SetHotDiscussionGamesAsync` | 透過 HTTP 呼叫 `newsservice` API（可能為 `POST /api/v1/internal/news/hotdiscussiongames`） |
| 4 | (下游) | `newsservice` | 寫入資料庫或快取（例如 `news` keyspace 或 `Redis`） |
| 5 | Controller | 同上 | 回傳結果給前端 |

> **需人工確認**：Service / Provider 實際類別名稱與下游 API 路由，需核對程式碼。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| HTTP API | `newsservice` | POST | 執行標記作業 |
| HTTP API | `pricecenter` | (可能) | 可能讀取賽事資訊以驗證賽事存在 |
| DB | `news` keyspace（未知表） | Write | 儲存熱門討論賽事列表 |
| Cache | Redis（未知 key） | Write | 可能用於快速查詢熱門賽事 |

> **需人工確認**：最終儲存位置（如 `news` 中的某個表，或 Redis 的特定 key），以及是否與 `pricecenter` 直接互動。

---

## 6. 重要規則

- **權限限制**：僅允許具備管理後台「AI 新聞管理」權限的角色操作。
- **欄位限制**：傳入的 `gtype`, `lid`, `gdate`, `gid` 必須對應到 `pricecenter` 中已存在的賽事，否則應拒絕。
- **不可暴露資料**：回應中不應包含敏感個資（即使不涉及）。
- **Transaction 規則**：若涉及跨服務寫入，需確保冪等性或使用補償機制（目前推測為單一服務寫入，無分散式事務）。
- **狀態值限制**：熱門設定可能為 toggle 操作（設定/取消），具體行為需確認。

> **需人工確認**：是否支援取消設定、是否可重複設定、最大可設定賽事數量等業務規則。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未經授權的請求（無 token） | 回傳 401 Unauthorized |
| token 合法但不具備管理權限 | 回傳 403 Forbidden |
| 請求 body 格式錯誤（缺少必要欄位） | 回傳 400 Bad Request，附帶錯誤訊息 |
| 指定的賽事不存在（`pricecenter` 查無對應資料） | 回傳 422 Unprocessable Entity 或自定義錯誤碼，提示賽事無效 |
| 下游 `newsservice` 呼叫失敗（網路錯誤或 500） | 回傳 502 Bad Gateway 或 503 Service Unavailable，並記錄日誌 |
| `newsservice` 回傳業務錯誤（如重複設定） | 將下游錯誤碼/訊息轉發給前端 |
| 請求重複（相同賽事再次設定） | 視業務規則：可能成功（更新）或回傳 409 Conflict |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| HOT-01 | API Test | 使用合法管理員 token 設定一筆有效賽事 | 200 OK，後續查詢該賽事顯示為「熱門討論」 |
| HOT-02 | Permission Test | 使用一般使用者 token 呼叫 | 403 Forbidden |
| HOT-03 | Validation Test | 缺少 `gid` 參數 | 400 Bad Request |
| HOT-04 | Integration Test | 模擬 `newsservice` 回傳 500 | 502 Bad Gateway，且後台收到錯誤 alert |
| HOT-05 | Flow Test | 設定成功後，使用前台 API 查詢熱門賽事列表，確認包含該賽事 | 前台列表包含該賽事 |
| HOT-06 | Idempotency Test | 對同一賽事連續發送兩次相同請求 | 視業務規則，應返回成功且不產生重複記錄或錯誤 |

---

## 9. 高風險區域

- **高風險 table**：若寫入 Cassandra `news` 表，需注意 partition key 設計，避免 hotspot。  
- **跨服務資料同步**：`pricebackendservice` → `newsservice` 的呼叫可能失敗，前端無法得知實際寫入狀態，需有重試機制或確保 newsservice 有冪等設計。  
- **Cache consistency**：如果熱門賽事資料有 Redis 快取，必須在寫入後主動失效或更新快取；依賴 TTL 可能延遲生效。  
- **Queue retry**：本 API 為同步 HTTP 呼叫，若下游無回應可能導致前端 timeout；可考慮改為非同步任務，但產品需求可能要求即時反應。

---

## 10. 常見錯誤

- ❌ **未驗證下游服務回應即回傳成功**：直接假定 `newsservice` 成功，忽略其返回的錯誤碼。
- ❌ **未記錄日誌**：後台重要操作（設定熱門賽事）應記錄操作者、時間與內容，方便稽核。
- ❌ **參數未校驗**：沒有檢查 `gtype` 是否為系統支援的遊戲類型，可能傳送無效數據至下游。
- ❌ **前端重複提交**：未阻擋重複點擊，可能造成多次相同請求，若下游無冪等設計會導致髒數據。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/v1/news/ai/hotdiscussiongames` (README) |
| 相依服務 | `newsservice`, `pricecenter` (README 服務相依列表) |
| 權限 | 所有 News API 均標記「需要驗證」 (README) |
| DB | 推測可能寫入 `news` keyspace（需人工確認具體表） |
| Code | 無直接 code evidence，情境基於 README 與服務架構推斷 |

> **需人工確認**：實際儲存結構、下游 API 合約、Redis 快取策略、錯誤處理細節，需由擁有原始碼存取權的團隊核實並補充。