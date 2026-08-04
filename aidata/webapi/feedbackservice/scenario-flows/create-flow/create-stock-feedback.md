# 用戶提交股票反饋

## 1. 場景目的
用戶在股票站點（stock）提交問題或建議，系統寫入 `feedbacks_stock` 表建立一筆反饋記錄，初始狀態為「未回覆」，供管理員後續處理。

---

## 2. 入口 API
*需人工確認*（未提供 OpenAPI 文件，推測路徑可能為 `POST /api/stock/feedback` 或 `POST /Feedback/Stock`）

---

## 3. 流程總覽
1. 接收用戶請求，解析認證資訊取得 `Account`
2. 驗證請求參數（ `TID` 必填、 `Problem` 非空）
3. 查詢 `stock_topics` 表驗證主題有效且啟用（ `Enabled=1` ）
4. 查詢 `stock.users` 表驗證帳號存在且啟用（ `Enabled=1` ），同時獲取 `Email`
5. 產生反饋唯一 `ID`
6. 組合資料( `Status=0` 、 `DateTime` 等)並寫入 `feedbacks_stock` 表
7. 回傳新建立的反饋 `ID`

---

## 4. 程式流程

| 順序 | Layer      | Class / Method                     | 動作                                             |
|------|------------|------------------------------------|--------------------------------------------------|
| 1    | Controller | *需人工確認*（推測 `StockFeedbackController`） | 接收 HTTP POST，解析參數與認證令牌               |
| 2    | Validator  | *需人工確認*                         | 驗證 `TID` 必填、`Problem` 非空                   |
| 3    | Service    | *需人工確認*                         | 協調驗證與寫入流程                                |
| 4    | Provider   | `TopicDataProvider`                | 查詢 `topics_stock` 表，驗證 `TID` 是否啟用         |
| 5    | Provider   | *需人工確認*（可讀 `stock.users`）       | 查詢 `users` 表，取得 `Email` 並確認帳號狀態        |
| 6    | Service    | *需人工確認*                         | 產生唯一 `ID`（如 GUID）                           |
| 7    | Provider   | `MessageDataProvider`              | 執行 `INSERT INTO feedbacks_stock`                 |
| 8    | Controller | -                                  | 回傳成功回應（含 `ID`）                            |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源                | 操作   | 用途                         |
|------|---------------------|--------|------------------------------|
| DB   | `topics_stock`      | Read   | 驗證主題有效性               |
| DB   | `users`（stock 庫）   | Read   | 驗證用戶狀態與取得 `Email`     |
| DB   | `feedbacks_stock`   | Insert | 寫入新的反饋記錄             |

> 未發現 Redis / Kafka 等使用證據。

---

## 6. 重要規則
- **權限限制**：必須通過認證（有合法 `Account`），不可匿名提交。
- **主題驗證**：`TID` 必須存在於 `topics_stock` 且 `Enabled=1`。
- **用戶驗證**：`Account` 須存在於 `stock.users` 且 `Enabled=1`。
- **狀態值**：新建反饋 `Status` 一律設為 `0`（未回覆），不可由客戶端設定。
- **不可修改欄位**：`ID` 產生後不可變更；`DateTime` 由伺服器產生，不允許前端傳入。
- **欄位限制**：`Problem` 型別為 `LIST<VARCHAR>`，寫入時應包裝為單一元素列表（前端僅傳一個問題字串）。
- **資料庫**：`feedbacks_stock` 為 ScyllaDB 表（支援 `LIST` 集合），`users` 為 MySQL 表，兩者跨庫操作需處理連線。

---

## 7. 錯誤情境

| 情境                          | 預期結果                                 |
|-------------------------------|------------------------------------------|
| 未提供有效認證令牌            | 回傳 401 未授權                          |
| `TID` 缺失或為空              | 回傳 400 驗證錯誤                        |
| `Problem` 缺失或為空          | 回傳 400 驗證錯誤                        |
| `TID` 不存在或已停用          | 回傳 400 或 404，訊息「主題無效」        |
| `Account` 不存在或已停用      | 回傳 400 或 404，訊息「帳號無效」        |
| ScyllaDB 寫入失敗（逾時）     | 回傳 500，不可部分寫入                   |

---

## 8. 測試重點

| Test ID | 類型             | 情境                           | 預期結果                     |
|---------|------------------|--------------------------------|------------------------------|
| FT-01   | API Test         | 有效認證 + 有效 TID + 問題內容 | 200，回傳新 ID，資料寫入 DB  |
| FT-02   | Permission Test  | 無認證                         | 401                          |
| FT-03   | Validation Test  | TID 為空                       | 400 驗證錯誤                 |
| FT-04   | Flow Test        | 停用主題                       | 400/404，主題無效            |
| FT-05   | Flow Test        | 停用帳號                       | 400/404，帳號無效            |
| FT-06   | DB Integrity     | 寫入後檢查 `feedbacks_stock`   | `Status=0`，`Problem` 為列表 |

---

## 9. 高風險區域
- **跨資料庫依賴**：`users` (MySQL) 與 `feedbacks_stock` (ScyllaDB) 不在同一實體，任一庫連線異常將導致流程中斷。
- **並發寫入**：`feedbacks_stock` 以自產 `ID` 寫入，理論上無衝突，但若未來需要依序編號則需注意。
- **缺少補償機制**：若 `feedbacks_stock` 寫入成功但回應失敗，可能遺留孤立記錄。
- **未使用交易**：跨庫操作無法保證 ACID，需評估矛盾可能性（如主題查詢後立即被停用，但影響微小）。

---

## 10. 常見錯誤
- 忽略主題或帳號的啟用狀態檢查，導致寫入無效反饋。
- 誤將 `Problem` 以字串型態寫入，造成 ScyllaDB 型別錯誤（應為 `LIST`）。
- 未從 `users` 表取得 `Email`，導致反饋記錄缺失聯絡資訊。
- 前端直接傳入 `DateTime` 或 `Status`，被惡意篡改；伺服器應完全覆蓋這些欄位。

---

## 11. Evidence

| 類型        | 來源                                        |
|-------------|---------------------------------------------|
| DB 表結構   | Phase1 語義分析：`feedbacks_stock` 欄位定義   |
| DB 角色     | `stock-detail.md`：feedbackservice 讀取 users |
| 主題驗證    | Phase1 `TopicDataProvider` 語義              |
| 程式元件    | Phase1 `MessageDataProvider` 操作 `feedbacks_stock` |
| 欄位語意    | Phase0/1 合併分析：`Problem` 為 `LIST<VARCHAR>` |
| 使用者表    | `stock` schema 中 `users` 表定義             |

*需人工確認 API 路由、Controller 名稱、具體 Service 與 Provider 類名，以及認證機制實作細節。*