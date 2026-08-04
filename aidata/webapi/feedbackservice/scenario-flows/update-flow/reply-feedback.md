# 管理員回覆反饋

## 1. 場景目的
管理員針對用戶提交的單則反饋進行回覆，可附加圖片，更新 `feedbacks_sport` 或 `feedbacks_stock` 的 `RespContent` 及 `Status`。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PATCH/PUT | `/api/admin/sport/feedback/{id}/reply` | 管理員回覆體育站點反饋 |
| PATCH/PUT | `/api/admin/stock/feedback/{id}/reply` | 管理員回覆股票站點反饋 |

> 備註：具體路徑由後端路由配置決定，`{id}` 為反饋的唯一識別碼 (Feedback ID)。Request Body 包含回覆內容及可選的圖片路徑。

---

## 3. 流程總覽

1. 管理員前端觸發回覆操作，發送包含 Feedback ID、回覆內容的 request。
2. Gateway 或中間件進行管理員身份驗證 (JWT/Session)。
3. Controller 接收並解析 request 參數 (ID, Content)。
4. Service 層驗證反饋是否存在，並檢查當前狀態是否允許回覆（例如「未回覆」或「已回覆」狀態）。
5. Service 層組合新的回覆記錄 (Append 至 `RespContent` JSON 陣列)。
6. 若包含圖片，執行圖片上傳邏輯，取得圖片 URL 或路徑，更新 `AdminImgPath` (僅體育站點)。
7. Service 層調用 Provider 更新對應的 ScyllaDB 表。
8. 更新 `Status` 為「已回覆」或「結束」。
9. 更新 `UpdateTime` 為當前 timestamp。
10. 返回更新後的完整反饋記錄或成功訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `AdminController.ReplySportFeedback` / `ReplyStockFeedback` | 接收 request，解析 feedbackId 及回覆內容 |
| 2 | Service | `AdminFeedbackService.ReplyToFeedback` | 驗證權限、反饋狀態，組合新的回覆內容 |
| 3 | Service | `AdminFeedbackService.UploadAdminImage` | 若請求包含圖片，執行上傳並取得路徑 |
| 4 | Provider | `SportFeedbackDataProvider` / `StockFeedbackDataProvider` | 執行對應 ScyllaDB 的更新操作 |
| 5 | Response | - | 回傳操作結果或更新後的反饋物件 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `feedbacks_sport` / `feedbacks_stock` | Update | 更新 RespContent, Status, UpdateTime |
| DB | `feedbacks_sport` | Update | 更新 AdminImgPath (僅體育站點) |
| File | 圖片儲存路徑 | Write | 儲存管理員上傳的圖片 |

> 此場景不涉及 Redis、Kafka 操作。根據現有程式碼語意，無 Cache 操作。

---

## 6. 重要規則

- **權限限制**：僅允許具備管理員角色 (Admin role) 的帳號操作。需透過 JWT 或 Session 驗證。
- **狀態值限制**：反饋狀態 (`Status`) 的可能值為：`0` (未回覆), `1` (已回覆), `2` (結束)。回覆時狀態通常從 `0` 變為 `1`，或從 `1` 保持為 `1`。
- **不可暴露資料**：系統內部處理的 Account 等敏感資訊不應洩露給前端。
- **欄位限制**：
    - `RespContent`: 由 `LIST<VARCHAR>` (ScyllaDB) 或 `text` (MySQL) 儲存 JSON 陣列。回覆時為追加 (append) 操作，不可覆蓋既有回覆。
    - `AdminImgPath`: 僅 `feedbacks_sport` 存在此欄位。為 JSON 陣列或字串。**需人工確認**該欄位確切的儲存格式與更新方式。
- **Transaction 規則**：ScyllaDB 不支援多行 ACID transaction。在此場景中，更新單一 partition key 的操作是原子性的。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| Feedback ID 不存在 | 返回 404 Not Found，訊息提示反饋不存在或 ID 錯誤。 |
| 權限不足 (非管理員) | 返回 403 Forbidden。 |
| 請求參數缺失 (Content 為空) | 返回 400 Bad Request，提示回覆內容不可為空。 |
| 反饋狀態不允許回覆 (例如已「結束」) | 返回 400 Bad Request 或 409 Conflict，提示當前狀態不可回覆。 |
| DB 更新失敗 / 連線 timeout | 返回 500 Internal Server Error，記錄錯誤日誌。 |
| 圖片上傳失敗 (格式錯誤、檔案過大等) | 返回 400 Bad Request 或 500 Internal Server Error。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| FT-ADMIN-REPLY-01 | API Test | 正常回覆，不含圖片 | 200 OK，DB 中 `RespContent` 正確追加，`Status` 更新為 1。 |
| FT-ADMIN-REPLY-02 | API Test | 正常回覆，附帶圖片 (體育站點) | 200 OK，圖片成功儲存，DB 中 `AdminImgPath` 正確寫入。 |
| FT-ADMIN-REPLY-03 | Permission Test | 無管理員權限的用戶呼叫 | 403 Forbidden。 |
| FT-ADMIN-REPLY-04 | Flow Test | 對已結束的 Feedback 回覆 | 4xx Error，`Status` 未變更。 |
| FT-ADMIN-REPLY-05 | API Test | 回覆內容為空 | 400 Bad Request。 |

---

## 9. 高風險區域

- **高風險 Table**：`feedbacks_sport`, `feedbacks_stock`。這些是核心的客戶互動記錄，錯誤的更新可能導致資料遺失或狀態異常。
- **高風險 API**：管理員回覆 API。權限控制不當可能導致未授權的資訊修改。
- **不可修改欄位**：Feedback 建立時的原始 `Problem` 內容、`Account` 等欄位不應在回覆流程中被異動。

---

## 10. 常見錯誤

- **新人**：可能在開發時直接覆蓋 `RespContent` 欄位，而未採用 Append 方式，導致歷史回覆記錄丟失。
- **AI**：可能誤認為此流程涉及 Cache 更新或非同步 Queue 處理。根據現有程式碼語意，此為同步的直接寫庫操作。
- **常見漏檢查項目**：忘記檢查 Feedback 當前的 `Status` 是否允許被回覆。
- **圖片處理**：在體育模組中遺漏圖片上傳或路徑格式錯誤。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | AdminController (透過語意分析推斷，需比對原始碼確認) |
| DB (體育) | `feedbacks_sport` (SportFeedbackDataProvider.cs) |
| DB (股票) | `feedbacks_stock` (MessageDataProvider.cs) |
| 狀態值 | Status 語意 (int: 0,1,2) 來自 `SportMessage.Status`, `StockFeedback.Status` |
| 碼源 | AdminFeedbackService (需人工確認具體檔名，語意來自 Admin 操作) |
| 規則 | 圖片欄位 `AdminImgPath` 僅存在於 `feedbacks_sport` (SportFeedbackDataProvider.cs) |