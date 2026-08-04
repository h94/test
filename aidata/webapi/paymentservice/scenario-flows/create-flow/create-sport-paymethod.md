# 建立體育支付方式

## 1. 場景目的
提供管理後臺建立一筆新的體育支付方式。寫入 `payment.paymethods_sport` 表，預設 `enabled=1`（啟用狀態）。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/sport/paymethods` | 建立一筆或多筆體育支付方式 |

---

## 3. 流程總覽

1. 接收管理後臺 POST 請求，包含支付方式資料（payType、mode、enabled、names）
2. 透過 ECFramework 進行驗證與授權檢查
3. Validator 驗證請求參數（必填欄位、格式）
4. Service 層處理業務邏輯，將支付方式資料寫入 `payment.paymethods_sport`
5. 寫入成功後回傳 200 OK；若失敗則回傳錯誤資訊

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `SportController.PostPayMethods` | 接收 HTTP POST 請求，呼叫 Service |
| 2 | Validator | 參數驗證 | 驗證 `payType`、`mode` 必填且格式正確；`enabled` 預設值為 1 |
| 3 | Service | `SportPayMethodService.Create` | 處理業務邏輯，呼叫 DataProvider 寫入 |
| 4 | Provider | `SportPayMethodDataProvider.Insert` | 將支付方式寫入 Cassandra `payment.paymethods_sport` |
| 5 | Controller | `SportController.PostPayMethods` | 回傳 200 OK 或錯誤回應 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.paymethods_sport` | Write | 寫入體育支付方式設定 |
| Redis | `SportPayMethods:{site}` | Write | 依 paymentservice-detail.md Redis 使用慣例，建立後需主動失效相關快取（若存在），確保下次查詢取得最新資料 |

---

## 6. 重要規則

- **權限限制**：僅管理後臺可呼叫此 API（需 ECFramework 驗證通過）  
- **欄位限制**：`payType` 與 `mode` 為 Partition Key 與 Clustering Key，一經寫入不可更新  
- **不可暴露資料**：`names` map 對外 API 應僅回傳對應語言的值，不可回傳完整 map  
- **不可修改欄位**：`payType`、`mode` 不可修改（若需變更，必須刪除後重建）  
- **狀態值限制**：`enabled` 由管理後臺 API 控制，預設值為 1（啟用）；`enabled` 值僅可為 0（停用）或 1（啟用）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未通過驗證 | 回傳 401 Unauthorized |
| 權限不足（非管理後臺角色） | 回傳 403 Forbidden |
| 必填欄位缺失（`payType` 或 `mode` 為空） | 回傳 400 Bad Request，提示欄位必填 |
| `enabled` 傳入非 0 或 1 的值 | 回傳 400 Bad Request，提示數值無效 |
| Cassandra 寫入失敗（Timeout/Exception） | 回傳 500 Internal Server Error |
| 已存在相同 `payType`+`mode` 的記錄 | 回傳 409 Conflict（需人工確認：目前 Cassandra INSERT 為 upsert 行為，應由程式先檢查是否存在） |
| Redis 快取清除失敗 | 不影響主流程，寫入仍回傳成功；需人工確認是否需記錄 Warning Log |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| TC-01 | Integration Test | 正常建立支付方式，enabled=1，names 填寫多語系 | 回傳 200，DB 可查詢到 enabled=1 的記錄 |
| TC-02 | Permission Test | 一般使用者呼叫 API | 回傳 403 Forbidden |
| TC-03 | API Test | 缺少 payType 參數 | 回傳 400 Bad Request |
| TC-04 | API Test | enabled 不填寫（使用預設值） | 回傳 200，DB 記錄 enabled=1 |
| TC-05 | Flow Test | 建立後立即查詢支付方式列表 | 查詢結果包含新建立的支付方式 |

---

## 9. 高風險區域

- **高風險 Table**：`payment.paymethods_sport` — 為主檔，包含啟用設定與多語系名稱  
- **高風險 API**：`POST /api/v1/sport/paymethods` — 直接影響前端支付選項顯示  
- **Cache Consistency**：建立後未主動失效快取可能導致前端無法顯示新支付方式  

---

## 10. 常見錯誤

- ❌ 未設定 `enabled` 預設值，導致寫入後前端無法顯示（`enabled=0`）  
- ❌ 直接在前端 API 回傳 `names` 的完整 map（應依語言回傳對應值）  
- ❌ 建立後未清除 Redis 快取，前端查詢不到新支付方式  

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `SportController.PostPayMethods` (README#體育支付方式) |
| DB | `payment.paymethods_sport` (README#資料庫重要Table, db-usage#payment) |
| Cache | `SportPayMethods:{site}` (paymentservice-detail.md#Redis) |
| 權限 | ECFramework.ECService (README#技術棧) |
| 寫入限制 | paymethods_sport 僅管理後臺 API 可修改 enabled (db-usage#payment) |
| 不可更新欄位 | payType、mode 為 Partition Key / Clustering Key 不可更新 (db-usage#payment) |

---

## 12. 需人工確認

- **建立前是否檢查 `payType`+`mode` 是否已存在**：Cassandra INSERT 為 upsert 行為，若未檢查可能覆蓋現有記錄。需人工確認實作邏輯。
- **Redis 快取清除邏輯**：paymentservice-detail.md 提及寫入後需失效相關快取，但此情境的具體 Redis Key 格式需人工確認。