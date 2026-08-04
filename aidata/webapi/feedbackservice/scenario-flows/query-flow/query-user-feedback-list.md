# 用戶查詢自身反饋列表

## 1. 場景目的

使用者登入後，根據指定的站點（sport / stock）與自身帳號，查詢過往提交的所有反饋歷史記錄。此流程為唯讀操作，回傳反饋摘要列表，不包含詳細回覆內容。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | /api/feedback/list | 查詢當前登入用戶的反饋列表。Request 包含站點識別參數（如 `site=sport` 或 `site=stock`）。 |

> 需人工確認：API 實際路由與參數名稱，建議參考 Controller（如 `FeedbackController`）的 Route Attribute。

---

## 3. 流程總覽

1. 接收用戶 HTTP Request，從 Token / Session 中取得當前使用者帳號（`Account`）。
2. 從 Request 取得站點參數（`site`），判斷查詢 `feedbacks_sport` 或 `feedbacks_stock` 表。
3. 調用對應 Provider 執行查詢，條件為 `Account = ?`。
4. Provider 對 ScyllaDB 執行 `SELECT`，取得當前使用者的所有反饋紀錄。
5. 回傳反饋列表（包含 ID、主題、狀態、建立時間等摘要資訊）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `FeedbackController.GetMyFeedbacks`（推測） | 接收 Request，驗證登入狀態，取得 `Account`。解析 `site` 參數。 |
| 2 | Service | `FeedbackService.GetUserFeedbacks`（推測） | 根據 `site` 決定調用 `SportFeedbackDataProvider` 或 `StockFeedbackDataProvider`。 |
| 3 | Provider | `SportFeedbackDataProvider.GetFeedbacksByAccount(account)` | 實體化後，執行對 `feedbacks_sport` 表的查詢。 |
| 4 | Provider | `StockFeedbackDataProvider.GetFeedbacksByAccount(account)` | 實體化後，執行對 `feedbacks_stock` 表的查詢。 |
| 5 | Provider → DB | ScyllaDB CQL `SELECT` | `SELECT id, tid, datetime, status, updatetime FROM feedbacks_{site} WHERE account = ?` |
| 6 | Service | `FeedbackService` | 組裝 DTO，確保過濾不應回傳的欄位（如詳細內容）。 |
| 7 | Controller | `FeedbackController` | 回傳 JSON 列表。 |

> 需人工確認：Controller 與 Service 的具體命名。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `feedbacks_sport` | Read (`SELECT`) | 查詢體育站點的用戶反饋。查詢條件必為 `account`。 |
| DB | `feedbacks_stock` | Read (`SELECT`) | 查詢股票站點的用戶反饋。查詢條件必為 `account`。 |
| Cache | 無 | - | 本次查詢流程中未發現使用 Redis 或本地快取。 |
| Queue | 無 | - | 本次查詢流程中未發現使用 Kafka 或其他 Queue。 |

---

## 6. 重要規則

- **權限限制**：用戶僅能查詢自身反饋。 `Account` 必須從登入 Session/Token 獲取，不可從 Request 傳入，嚴防越權查詢（IDOR）。
- **欄位限制**：列表查詢不可回傳詳細內容欄位（如 `Problem`, `RespContent`, `ImgPath` 的完整內容），僅回傳摘要資訊（ID, 主題ID, 狀態, 時間）。
- **不可暴露資料**：`ImgPath` 屬於使用者隱私數據，若列表需要顯示，應僅回傳「有無圖片」的布林值，而非路徑本身。
- **不可修改欄位**：`ID` 為提交後產生的唯一識別碼，API 不可嘗試修改。
- **狀態值限制**：`Status` 為數值型態，邏輯層應轉換為有意義的字串或枚舉（如：1:未回覆，2:已回覆，3:已結束）後再回傳。
- **跨服務限制**：feedbackservice 對此資料表有完整讀寫權限，但本場景為唯讀。服務本身無跨服務呼叫。

> 需人工確認：`Status` 的具體枚舉值定義（0/1/2 或其他），以及 `TID` 是否需要 join `topics_sport` / `topics_stock` 以回傳主題名稱。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未登入或 Token 失效 | 返回 HTTP 401 Unauthorized。 |
| `site` 參數缺失或為非法值（非 `sport` 或 `stock`） | 返回 HTTP 400 Bad Request，並附帶錯誤訊息（如「Invalid site parameter」）。 |
| 查詢的 `Account` 不存在任何反饋 | 返回 HTTP 200 OK，並帶有空列表（`[]`）。 |
| ScyllaDB 連線超時或查詢錯誤 | 返回 HTTP 500 Internal Server Error。不應將 DB 錯誤細節直接返回給客戶端。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| FT-01 | Flow Test | 正常查詢：登入用戶 A，查詢 `site=sport`。A 在 `feedbacks_sport` 有 3 筆紀錄。 | 返回包含 3 筆紀錄的列表，內容為摘要資訊。 |
| FT-02 | Flow Test | 空列表查詢：登入用戶 B，查詢 `site=stock`。B 在 `feedbacks_stock` 無紀錄。 | 返回空列表 `[]`。 |
| PT-01 | Permission Test | 越權查詢：嘗試通過竄改 Request 查詢其他用戶的帳號。 | 系統應忽略傳入的帳號，強制以登入帳號查詢，或返回 403 Forbidden。 |
| API-01 | API Test | 站點參數錯誤：傳入 `site=invalid`。 | 返回 HTTP 400 錯誤。 |
| API-02 | API Test | 遺漏站點參數：不傳 `site`。 | 返回 HTTP 400 錯誤。 |

---

## 9. 高風險區域

- **高風險 API**：若查詢 API 允許從 Request 傳入 `Account`，則存在嚴重的越權查詢（IDOR）風險。必須確保 `Account` 強制來自服務端 Session。
- **敏感資料洩漏**：`Problem`, `RespContent`, `ImgPath` 欄位為隱私資訊。若列表 API 直接序列化整個資料物件回傳，將造成資訊過度暴露。

---

## 10. 常見錯誤

- **新人容易犯錯**：直接將 Provider 回傳的 Data Model 序列化回傳給前端，忘記進行 DTO 轉換，導致 `Problem` 或 `RespContent` 等詳細內容在列表中全部露出。
- **AI 容易誤解**：誤認為 `feedbacks_sport` 和 `feedbacks_stock` 是同一張表，或認為它們在同一個 MySQL Server 上。實際上它們是 ScyllaDB 中兩個完全獨立的表。
- **常見漏檢查項目**：遺漏對 `site` 參數的合法性檢查，導致程式試圖查詢不存在的表而拋出例外。
- **常見錯誤流程**：在程式內部進行跨服務呼叫來驗證使用者或獲取主題名稱，應直接由 feedbackservice 本身或透過應用層快取解決。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 入口推測 | 基於 C# (.NET) Controller 慣例與 RESTful 設計。 |
| DB 表結構 | `feedbacks_sport`、`feedbacks_stock` 語義分析（Phase 0/1 產出）。 |
| 程式流程 | `SportFeedbackDataProvider`、`StockFeedbackDataProvider` 語義分析（Phase 0/1 產出）。兩者均包含 `Account` 欄位與 `SELECT` 操作。 |
| 服務角色 | `db/stock-detail.md`: `feedbackservice` 角色標記為 `reader`。 |
| ScyllaDB 使用 | README.md 技術棧說明。 |