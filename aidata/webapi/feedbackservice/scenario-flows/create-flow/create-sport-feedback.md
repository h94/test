# 用戶提交運動反饋

## 1. 場景目的
用戶在體育站點（Sport）對特定主題提出問題或建議，支援文字描述與圖片附件，系統將反饋記錄至 ScyllaDB `feedbacks_sport` 表，狀態初始為「未回覆」，供管理員後續處理。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| （需人工確認） | （需人工確認） | 接收提交內容，可能為 `POST /api/sport/feedback` 或類似端點。因未提供 API 文件，需對照 `README` 與控制器程式碼確認。 |

---

## 3. 流程總覽

1. 客戶端帶入登入 Token、主題 ID（TID）、問題內容（可能含圖片）發起請求。
2. 驗證請求格式與必要欄位（TID、Problem 不可為空）。
3. 從 Token 解析用戶 Account（需人工確認驗證機制，可能由閘道傳入或呼叫 memberservice）。
4. 查詢 `topics_sport` 表，確認該 TID 存在且 `enabled = 1`。
5. 生成反饋 ID 與建立時間（DateTime 字串）。
6. 若含有圖片，處理檔案上傳並產生 `ImgPath`（儲存至掛載目錄，避免容器重啟遺失）。
7. 組裝 `feedbacks_sport` 記錄，設定 Status = 0（未回覆），`Problem` 為 LIST<VARCHAR>，`RespContent` 空。
8. 寫入 ScyllaDB `feedbacks_sport` 表。
9. 回傳成功狀態與反饋 ID。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | （需人工確認） | 接收請求、參數繫結、呼叫 Service |
| 2 | Service | （需人工確認） | 組合邏輯：驗證主題、處理圖片、產生資料物件 |
| 3 | Provider | `SportFeedbackDataProvider.Insert`（推斷） | 實際對 `feedbacks_sport` 執行 INSERT |
| 4 | Validator | （需人工確認） | 檢查 TID 存在且啟用、欄位長度、圖片格式 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (ScyllaDB) | `topics_sport` | Read | 驗證主題是否存在且啟用 |
| DB (ScyllaDB) | `feedbacks_sport` | Write (INSERT) | 儲存用戶反饋記錄 |
| Cache | 無 | – | 當前流程未使用 Redis |
| Queue | 無 | – | 未發現 Kafka/Queue 參與 |
| 外部 API | （需人工確認） | – | 可能呼叫 `memberservice` 驗證帳號狀態，若 Token 未自帶資訊 |

---

## 6. 重要規則

- **權限限制**：需登入，僅允許本人提交；不可冒用他人 Account（需人工確認 Token 驗證來源）。
- **欄位限制**：
  - `Problem` 為 `LIST<VARCHAR>`，API 輸入需轉為列表格式。
  - `ImgPath` 應為合法檔案路徑，禁止目錄遍歷攻擊。
  - `Account` 與 `Email` 不可為空，Email 格式需驗證。
- **不可暴露資料**：`AdminImgPath`、`RespContent` 在新建時不應由用戶輸入。
- **狀態值限制**：新建時 Status 固定為 0（未回覆），不可由客戶端指定。
- **不可修改欄位**：`ID`、`DateTime`、`Account`、`TID` 寫入後不提供更新。
- **Transaction 規則**：ScyllaDB 不支援多表事務，需自行實作補償或重試（若有跨表需求）。
- **圖片儲存**：檔案路徑需限制於掛載目錄，防範任意目錄寫入。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未登入或 Token 無效 | 回傳 401，拒絕提交 |
| TID 不存在或 `topics_sport.enabled = 0` | 回傳 400，提示主題不可用 |
| 問題內容（Problem）為空 | 回傳 400，參數檢驗失敗 |
| 圖片格式不支援或超出大小 | 回傳 400，拒絕上傳，清理暫存 |
| ScyllaDB 寫入失敗（逾時/不可用） | 回傳 500，記錄 Log，提示稍後再試 |
| 圖片上傳成功但資料庫寫入失敗 | 需人工確認：是否保留孤兒圖片、是否觸發補償刪除？ |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SPT-FB-01 | Flow Test | 正常提交含文字與圖片 | 回傳 200，`feedbacks_sport` 新增一筆 Status=0 |
| SPT-FB-02 | Permission Test | 未帶 Token | 回傳 401 |
| SPT-FB-03 | API Test | TID 不存在 | 回傳 400，主題無效 |
| SPT-FB-04 | API Test | TID 已停用 | 回傳 400，主題停用 |
| SPT-FB-05 | Integration Test | 圖片上傳非法副檔名 | 回傳 400，未寫入 DB |
| SPT-FB-06 | Flow Test | 不含圖片 | 正常寫入，ImgPath 為 NULL 或空 |

---

## 9. 高風險區域

- **高風險 Table**：`feedbacks_sport`  
  直接由用戶觸發寫入，需嚴防注入與資料污染（如 `Problem` LIST 結構破壞）。
- **高風險 API**：圖片上傳端點  
  路徑注入、惡意檔案類型、磁碟空間耗盡。
- **跨服務資料同步**：若 `Account` 由 `memberservice` 驗證，網路抖動可能導致呼叫失敗。
- **Cache consistency**：無快取，不適用。
- **Queue retry**：無佇列，若寫入失敗由客戶端重試可能導致重複提交；需人工確認是否實作 idempotency（利用 ID 作為 primary key 可防重複？）。
- **Idempotency**：當前 `feedbacks_sport` 主鍵組成未知，若含用戶端傳入的 ID，需確保唯一性；若由伺服器產生，重試可能建立多筆。需人工確認重試策略。

---

## 10. 常見錯誤

- 新人容易忘記檢查 `topics_sport.enabled`，導致停用主題仍可提交。
- AI 容易誤解 `Problem` 為普通字串而非 `LIST<VARCHAR>`，生成錯誤的 INSERT 語法。
- 未驗證圖片格式即嘗試寫入磁碟，可能觸發異常。
- 直接將前端傳來的 `Status` 寫入 DB，導致狀態被竄改。
- 未處理 ScyllaDB 連線失敗，讓 API 崩潰。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 表結構 | code semantics: `SportFeedbackDataProvider.cs` / `feedbacks_sport` |
| 主題啟用規則 | code semantics: `topics_sport.enabled` 欄位 |
| 狀態初始值 | README: 反饋狀態預設「未回覆」 |
| 圖片路徑設計 | README: 體育站點支援 `ImgPath` 與持久化掛載 |
| 寫入操作 | code semantics: `SportFeedbackDataProvider.cs` 負責 INSERT |
| 無外部佇列/Cache | README 未提及，code semantics 未出現相關元件 |