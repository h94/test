# 更新 AI 新聞

## 1. 場景目的

內容編輯人員在管理後台，針對特定賽事的 AI 生成新聞，上傳封面圖片或更新文本內容後，提交至系統。系統將圖片上傳至儲存服務，並將更新後的內容發送至下游新聞服務，以完成 AI 新聞的最終修正與發布。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/news/ainews` | 更新 AI 新聞，支援上傳圖片與內容更新 |

---

## 3. 流程總覽

1. 後台管理員發起請求，包含圖片檔案與新聞內容。
2. 系統驗證管理員身分與權限。
3. 系統將上傳的圖片檔案轉送至內部圖片上傳服務。
4. 取得圖片儲存路徑後，將新聞內容與圖片路徑組裝為 DTO。
5. 呼叫新聞服務 (`newsservice`) 更新 AI 新聞資料。
6. 回傳處理結果給後台前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `NewsController.UpdateAINews` | 接收 multipart/form-data 請求，含圖片與內容 |
| 2 | Service | `NewsService.UpdateAINews` | 協調圖片上傳與新聞資料更新的流程 |
| 3 | Provider | `SystemProvider.UploadImage` | 轉發圖片至 `/api/v1/system/upload/img` |
| 4 | Provider | `NewsProvider.UpdateAINews` | 呼叫新聞服務 `POST /api/v1/news/ainews` |
| 5 | Service | `NewsService.UpdateAINews` | 將下游服務回應轉換為 API 回傳格式 |
| 6 | Controller | `NewsController.UpdateAINews` | 回傳 `200 OK` |

---

## 5. DB / Cache / Queue 使用

> **注意**：`pricebackendservice` 為 BFF 層，不直接操作 DB。

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `news.ainews` | Write | 由 `newsservice` 負責寫入，更新 `status`, `anwser`, `others` 等欄位 |
| DB | `news.ainews_gs` | Write | 由 `newsservice` 負責寫入，依遊戲類型寫入對應分表 |
| DB | `news.ainews_lt` | Write | 由 `newsservice` 負責寫入，依遊戲類型寫入對應分表 |
| Internal API | `/api/v1/system/upload/img` | Write | 上傳圖片檔案並取得圖片路徑 |
| Internal API | `newsservice` | Write | 傳送 DTO 以更新 AI 新聞內容與圖片路徑 |

---

## 6. 重要規則

- **權限限制**：此 API 需要後台管理員驗證，僅內容編輯與管理員可操作。
- **欄位限制**：上傳的圖片格式與大小需符合系統規定（需人工確認具體限制）。
- **不可暴露資料**：
    - `news.ainews` 中的 `anwser`, `reanwser`, `llmsettings`, `bets` 等欄位不可直接對外暴露。
    - `pricebackendservice` 應確保傳遞給 `newsservice` 的資料不包含前端不應提交的欄位。
- **狀態值限制**：根據 `news-detail.md`，AI 新聞的 `status` 只能依序流轉 (0→1→2)。此次更新操作應將 `status` 設置為 `2` (已修正)。
- **不可修改欄位**：`news.ainews` 的複合主鍵 (`gdate`, `gtype`, `lid`, `gid`, `llmhashkey`, `status`) 在建立後不可修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未登入或權限不足 | 回傳 `401 Unauthorized` 或 `403 Forbidden` |
| 請求中未包含圖片檔案 | 回傳 `400 Bad Request` 並提示缺少圖片 |
| 圖片上傳服務 (`/api/v1/system/upload/img`) 無回應或失敗 | 回傳 `500 Internal Server Error` 並記錄錯誤日誌 |
| `newsservice` 回應錯誤 (如找不到對應的 AI 新聞) | 轉發 `newsservice` 的錯誤狀態碼與訊息給後台 |
| `newsservice` 無回應 | 回傳 `502 Bad Gateway` 並記錄錯誤日誌 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-UpdateAINews-01 | API Test | 使用管理員權限，上傳有效圖片與內容 | 回傳 200 OK，新聞服務成功更新 |
| UT-UpdateAINews-02 | Permission Test | 使用一般使用者權限呼叫 API | 回傳 401 或 403 |
| UT-UpdateAINews-03 | Flow Test | 模擬圖片上傳服務失敗 | BFF 回傳 500，不繼續呼叫新聞服務 |
| UT-UpdateAINews-04 | Flow Test | 模擬 `newsservice` 回應找不到對應新聞 | BFF 回傳 404，錯誤訊息正確轉發 |
| UT-UpdateAINews-05 | Integration Test | 完整執行成功流程後，查詢該新聞 | 圖片路徑與內容已更新為提交的最新版本 |

---

## 9. 高風險區域

- **跨服務資料一致性**：BFF 層協調了圖片上傳和新聞更新兩個下游服務，若新聞更新成功但後續 BFF 發生錯誤，可能導致圖片已上傳但新聞未關聯。可考慮最終一致性或重試機制。
- **高風險 Table**：`news.ainews` 為核心業務表，其 `status` 的流轉為不可逆操作，需確保業務邏輯正確。
- **Transaction**：BFF 層無資料庫交易，需關注跨服務呼叫的補償與冪等性。
- **冪等性**：對相同的新聞多次發送更新請求，可能重複寫入圖片紀錄或觸發多次 LLM 修正。API 需設計具備冪等性，或由 `newsservice` 妥善處理。

---

## 10. 常見錯誤

- **新人容易犯錯**：在 BFF 層嘗試直接組合 `newsservice` 的資料模型並寫入 DB，忽略了 BFF 層不直接存取資料庫的原則。
- **AI 容易誤解**：誤會此 API 是「創建」新的 AI 新聞，而非「更新」既有的新聞。
- **常見漏檢查項目**：忽略對圖片檔案大小和格式的伺服器端驗證，完全依賴前端限制，可能導致上傳攻擊。
- **常見錯誤流程**：在圖片上傳成功後，未正確取得圖片路徑即呼叫新聞服務更新，導致新聞中圖片路徑為空。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `README.md` · 新聞與 AI 資訊管理 · POST `/api/v1/news/ainews` |
| DB | `news.ainews` · Schema |
| DB | `news-detail.md` · status 欄位定義 |
| Rules | `pricebackendservice-detail.md` · 無直接 DB 存取 |
| Rules | `news-detail.md` · 跨服務寫入限制與狀態流轉 |
| Internal API | `README.md` · 系統工具 · POST `/api/v1/system/upload/img` |