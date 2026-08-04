# 管理員建立預設問題

## 1. 場景目的

管理員於指定主題下，新增預設的問答配對（FAQ），以利前臺使用者快速取得常見疑問之解答。依據站點（Sport／Stock）寫入對應資料表，體育站點支援多語言內容。

---

## 2. 入口 API

需人工確認：具體 API Path 未於原始碼摘要中提供。以下為推估路徑。

| Method | Path | 說明 |
|---|---|---|
| POST | /api/admin/sport/question | 管理員於體育站點新增預設問答 |
| POST | /api/admin/stock/question | 管理員於股票站點新增預設問答 |

---

## 3. 流程總覽

1. 管理員透過管理後端（如 `SportAdminController`、`StockAdminController`）發送 POST 請求。
2. 請求中攜帶所屬主題 `TID`、問題內容 `Question` 與答案內容 `Answer`。
3. 系統驗證管理員身分與權限（需具備管理員角色）。
4. 驗證 `TID` 對應的主題確實存在且為啟用狀態。
5. 生成唯一 `ID` 作為問題主鍵。
6. 對應站點寫入對應 DB 表：
   - 體育：寫入 ScyllaDB `sport.questions_sport`，`Question` 與 `Answer` 儲存為多語言 MAP 結構。
   - 股票：寫入 MySQL `stock.questions_stock`（或 ScyllaDB 轉接表），`Question` 與 `Answer` 為純文字。
7. 回傳成功（含新建立之 `ID`）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | SportAdminController.CreateQuestion | 接收請求，呼叫驗證與服務層 |
| 2 | Validator | （需人工確認） | 驗證必填欄位（`TID`、`Question`、`Answer`），驗證多語系格式 |
| 3 | Service | SportFeedbackService.AddQuestion | 檢查 `TID` 對應主題存在，生成唯一 `ID` |
| 4 | Provider | SportFeedbackDataProvider.InsertQuestion | 組裝 CQL INSERT 語句，寫入 ScyllaDB `questions_sport` 表 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (ScyllaDB) | `sport.questions_sport` | Write (INSERT) | 寫入體育站點預設問答，包含多語言內容 MAP |
| DB (MySQL) | `stock.questions_stock` | Write (INSERT) | 寫入股票站點預設問題與答案（純文字） |

**需人工確認**：`feedbackservice` 對 `stock` 庫是否直連 MySQL 或經由 ScyllaDB 統一接口；`stock.questions_stock` 表實際存在於 ScyllaDB 的 `stock` keyspace 中。

本場景不涉及 Redis、Kafka 或其他 Queue 操作。

---

## 6. 重要規則

- **權限限制**：
  - 必須為管理員角色（`Admin`），一般使用者不可呼叫此 API。
- **欄位限制**：
  - `ID` 為唯一主鍵，由系統生成（如 GUID），不可由客戶端指定。
  - 體育站點 `Question` 與 `Answer` 儲存為 `MAP<varchar, varchar>` 格式，key 為語系代碼（如 `zh-TW`, `en`）。
  - `Enabled` 欄位預設為 `1`（啟用）。
- **不可暴露資料**：
  - 管理員建立問答不應涉及任何用戶個資（Account、Email 等）。
- **狀態值限制**：
  - 雖 `Enabled` 由服務端預設為 `1`，但已存在之問題狀態變更（啟用/停用）不屬於本場景範圍。
- **不可修改欄位**：
  - `ID` 寫入後不可變更。
  - ScyllaDB 的 `MAP` 欄位（`Question`、`Answer`）通常為 replace 操作。
- **跨站點隔離**：
  - 體育站點 (`sport`) 與股票站點 (`stock`) 的問題儲存完全隔離，不可跨站點寫入。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未攜帶有效管理員 Token | HTTP 401 Unauthorized |
| Token 權限不足（一般使用者） | HTTP 403 Forbidden |
| 請求 `TID` 不存在 | HTTP 400 Bad Request，錯誤訊息指示無效的主題 |
| 請求 `TID` 之主題已停用 | HTTP 400 Bad Request，錯誤訊息指示主題已停用 |
| 必填欄位缺失（如 `Question` 為空） | HTTP 400 Bad Request，驗證錯誤 |
| 體育站點 `Question` MAP 缺少必要語系 key | HTTP 400 Bad Request，提示語系不足 |
| 資料庫寫入失敗（ScyllaDB 節點無回應） | HTTP 500 Internal Server Error |
| 重複的 `ID` 碰撞（極低機率） | HTTP 500 Internal Server Error，服務端應實施重試機制 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| FT-ADMIN-QC-01 | Permission Test | 使用一般用戶 Token 呼叫 API | 403 Forbidden |
| FT-ADMIN-QC-02 | API Test | 傳入不存在的 `TID` | 400 Bad Request，含明確錯誤訊息 |
| FT-ADMIN-QC-03 | API Test | 傳入合法體育問答資料 | 201 Created，DB 中 `questions_sport` 表出現該 ID |
| FT-ADMIN-QC-04 | Integration Test | 體育站點寫入後，查詢前臺 API （需人工確認） | 前臺問答列表應回傳新建立的啟用問題 |
| FT-ADMIN-QC-05 | Data Integrity Test | 寫入 `MAP` 結構後再次讀取 | `Question` MAP 內容與輸入一致（key/value 準確） |

---

## 9. 高風險區域

- **高風險 table**：
  - `questions_sport`：體育站點核心問答表，使用 `MAP` 結構。寫入錯誤的 MAP key 可能導致前臺顯示空白或錯誤語系。
- **跨儲存結構管理**：
  - 體育站點使用 ScyllaDB `MAP`，股票站點使用純文字。開發或合併時容易誤用格式，需人工審查寫入路徑。
- **ID 產生機制**：
  - 若 `ID` 產生途徑依賴 `GUID`，在高併發建立場景下雖碰撞機率極低，仍需確保 Provider 層有例外捕捉。
- **ScyllaDB 的 data type 約束**：
  - Schema 定義與 Provider 中的 CQL 務必一致，尤其 `MAP` 的鍵值型別宣告。

---

## 10. 常見錯誤

- **新人容易**：
  - 誤將股票站點的問答寫入 `MAP` 結構，或將體育站點問答寫為純文字。
  - 於請求中擅自指定 `ID`，而不是讓服務端生成。
- **AI 容易**：
  - 假設所有寫入操作均經歷相同的欄位校驗器，而忽略了體育與股票站點可能使用不同 Validator 或 Service。
  - 推測 `questions_stock` 表位於 MySQL，但實際系統可能已將 stock keyspace 遷移至 ScyllaDB，應以 service 內 `DataProvider` 指向為準。
- **常見漏檢查項目**：
  - 未驗證 `TID` 對應主題的 `Enabled` 狀態。
  - 未處理 ScyllaDB `MAP` 欄位在資料庫層為空時的行為（null vs empty map）。
- **常見錯誤流程**：
  - 管理員誤操作，對同一主題重複建立相同問題，未實作去重檢查。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB Table | `sport.questions_sport` |
| DB Table | `stock.questions_stock` |
| Schema | `Question` 欄位類型：體育為 `MAP<VARCHAR,VARCHAR>`, 股票為 `VARCHAR` |
| Code | `SportFeedbackDataProvider.cs` (Write path for Sport Questions) |
| Code | `QuestionDataProvider.cs` (Write path for Stock Questions) |
| Controller | `SportAdminController`、`StockAdminController`（需人工確認具體方法名） |
| Service | `SportFeedbackService`（推估邏輯） |
|---|