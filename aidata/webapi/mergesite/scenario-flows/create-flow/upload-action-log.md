# 上傳使用者操作紀錄

## 1. 場景目的

管理後台將使用者的重要操作（如強制合併、資料編輯）寫入操作日誌，供後續查詢與稽核，確保關鍵業務行為可追溯。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/system/logs/action` | 上傳使用者操作紀錄 |

---

## 3. 流程總覽

1. 接收 HTTP POST 請求，攜帶操作紀錄內容
2. 驗證請求者是否具備管理後台權限（需人工確認具體權限邏輯）
3. 檢查 request body 格式是否符合規範（需人工確認欄位定義）
4. 將操作紀錄透過 PriceCenterService REST API 寫入（需人工確認目標資源與 API）
5. 寫入成功後回傳 200 OK
6. 若寫入失敗，回傳對應錯誤碼

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SystemController.PostActionLog` | 接收 request body，呼叫 Service |
| 2 | Service | `ActionLogService.CreateLog` | 組裝 log model，呼叫 PriceCenterService client（需人工確認） |
| 3 | Provider | `PriceCenterServiceClient.WriteLog` | 呼叫外部 REST API 寫入 log（需人工確認） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| 外部 API | PriceCenterService REST API | Write | 寫入操作紀錄（需人工確認端點） |
| Message Queue | Kafka（192.168.55.60） | Publish（不確定） | 應用程式 log 寫入（非操作紀錄，需人工確認是否用於此場景） |

**注意**：MergeSite 本身無直接 DB 操作，操作紀錄的實際儲存由 PriceCenterService 負責。Kafka 用途依 README 為「應用程式 Log 寫入」，與操作紀錄可能為不同目的，需人工確認。

**需人工確認**：
- 操作紀錄的儲存媒體（DB table / 檔案 / 外部服務）
- 是否需要透過 Kafka 發送操作事件觸發其他服務

---

## 6. 重要規則

- **權限限制**：需驗證（依 README 該 API 標記為需要驗證）
- **Request Body 欄位限制**：需人工確認必填欄位、長度限制、格式限制
- **不可暴露資料**：若 request body 包含敏感資訊（如密碼、token），不可寫入 log
- **Transaction 規則**：無（單一外部 API 呼叫）
- **Retry 規則**：需人工確認是否實作 retry 機制
- **不可修改欄位**：操作紀錄一經寫入應為不可變，不可提供 UPDATE / DELETE API（需人工確認 PriceCenterService 側實作）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未通過驗證 | 回傳 401 Unauthorized |
| Request body 格式錯誤或缺少必填欄位 | 回傳 400 Bad Request（需人工確認錯誤訊息格式） |
| PriceCenterService 連線失敗或 timeout | 回傳 502 Bad Gateway 或 504 Gateway Timeout（需人工確認） |
| PriceCenterService 回傳寫入失敗 | 回傳對應錯誤碼（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | API Test | 傳送合法 request body，驗證寫入成功 | 回傳 200 OK |
| T02 | Permission Test | 未攜帶有效 token 或權限不足 | 回傳 401 或 403 |
| T03 | API Test | Request body 缺少必要欄位 | 回傳 400 Bad Request |
| T04 | API Test | Request body 欄位值超長 | 回傳 400 Bad Request（需人工確認長度限制） |
| T05 | Flow Test | PriceCenterService 無法連線 | 回傳 502 或 504 |
| T06 | API Test | 操作紀錄寫入後，透過 GET API 查詢一致性（GET `/api/system/logs/action/{date}`） | 查詢結果包含剛寫入的紀錄 |

---

## 9. 高風險區域

- **跨服務資料同步**：操作紀錄依賴 PriceCenterService 寫入，若外部服務異常，操作紀錄可能遺失，影響稽核完整性
- **無本地資料庫**：此服務無獨立資料庫，所有資料讀寫依賴外部服務，需確保連線穩定性與監控告警
- **Idempotency**：需人工確認是否需實作 idempotency key，避免重複請求導致重複寫入相同的操作紀錄

---

## 10. 常見錯誤

- ❌ **未驗證 request body 長度**：若未在 API 層檢查欄位長度，可能導致 PriceCenterService 端寫入失敗或資料截斷
- ❌ **未區分操作紀錄與應用程式 log**：Kafka 寫入的是應用程式 log（如 debug、info、error），非業務操作紀錄，不可混用
- ❌ **假設 PriceCenterService 一定可用**：未實作 retry 或 fallback 機制，導致操作紀錄遺失
- ❌ **在 GET 查詢時未限制日期格式**：可能導致查詢失敗或回傳過多資料（需人工確認）
- ❌ **操作人資訊未正確傳遞**：需確保操作人帳號由驗證資訊中取得，不可由 request body 直接指定（防偽造）

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | SystemController.PostActionLog（需人工確認 controller 名稱） |
| Service | ActionLogService（需人工確認 class 名稱） |
| 外部 API | PriceCenterService REST API（需人工確認 endpoint） |
| README | MergeSite WebAPI 系統 API 路由表 |
| 服務相依 | PriceCenterService（Gateway: 192.168.55.60） |
| Kafka | 192.168.55.60（應用程式 Log 寫入，用途需人工確認） |

---

## 建議新增文件

- 需人工確認：`/api/system/logs/action` 的完整 request body schema（欄位定義、型別、長度限制、必填欄位）
- 需人工確認：PriceCenterService 中操作紀錄的儲存位置（DB table / collection 名稱）與對應 API endpoint
- 需人工確認：操作紀錄的 TTL 或保留策略

## 建議新增規則

- 需人工確認：POST `/api/system/logs/action` 的 retry 策略（是否支援、次數限制）
- 需人工確認：操作紀錄的不可變更原則（是否允許後續修改或刪除）
- 需人工確認：request body 中「操作人」欄位是否由後端自動填入，禁止前端傳入

## 建議新增測試情境

- 需人工確認：大量操作紀錄寫入的效能測試（若需）
- 需人工確認：PriceCenterService 短暫中斷後的 retry 行為測試