# 發送 SMS 簡訊 (TwSMS)

## 1. 場景目的
接收後端服務的簡訊發送請求，通過台灣簡訊（TwSMS）API 將簡訊發送至指定手機號碼，並將發送結果記錄至 `stock` 資料庫的 `messagelog` 表。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/sms/twsms/message` | 發送 SMS（台灣簡訊 TwSMS），需驗證 |

**Evidence**: [README.md](#對外-api-重點) 訊息發送表格。

---

## 3. 流程總覽

1. 接收 POST 請求，包含目標手機號碼 (Phone) 與訊息內容 (Content)。
2. 驗證請求方身份 (Auth / Permission)。
3. 驗證必要參數（手機號碼格式、訊息內容不可為空）。
4. 呼叫 TwSMS API 發送簡訊。
5. 根據 TwSMS API 回應寫入 `stock.messagelog`：
   - Date: 發送當日 (yyyy-MM-dd)
   - Account: 接收方帳號或系統帳號
   - SendAction: `SMS`
   - TargetAddress: 手機號碼
   - SendStatus: `1` (成功) 或 `2` (失敗)
   - MsgContent: 訊息全文
6. 回傳發送結果（成功或失敗）給呼叫方。

**注意**：原 README 指出 mqservice 為純訊息轉發服務，無持久化。但 stock DB 的 `messagelog` 表由 mqservice 寫入（詳見 db-usage 文件），此處為**必要更正**。

**Evidence**: [stock-detail.md](#tablemessagelog) 寫入權責，[db-usage](#寫入限制) 明確 mqservice 寫入 `messagelog`。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | SmsController | 接收 HTTP POST，驗證參數 |
| 2 | Service | SmsService | 驗證手機號碼格式、準備 TwSMS API 請求 |
| 3 | Provider | TwSmsProvider | 實際呼叫 TwSMS API |
| 4 | Service | SmsService | 根據 API 回應，調用 Repository 寫入 `messagelog` |
| 5 | Controller | SmsController | 回傳發送結果 |

需人工確認：Controller / Service / Provider 實際類別名。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `stock.messagelog` | INSERT | 記錄簡訊發送結果 |
| External | TwSMS API | HTTP Request | 發送簡訊 |

**Evidence**: [db-usage](#寫入限制) mqservice 負責寫入 messagelog，[README](#服務相依) TwSMS API 相依。

本流程未使用 **Redis** 與 **Queue/Kafka**。

---

## 6. 重要規則

- 權限限制：需通過 ECCore 驗證。 **Evidence**: README 技術棧。
- 欄位限制：
  - `TargetAddress` 為手機號碼，格式須驗證（如台灣手機 09xxxxxxxx）。
- 不可暴露資料：
  - `MsgContent` 不可回傳給前端或外部 API 查詢。 **Evidence**: [stock-detail.md](#tablemessagelog) 跨服務限制。
- 寫入規則：
  - `messagelog.SendStatus` 僅可為 0 (未發送)、1 (成功)、2 (失敗)。發送後寫入 1 或 2。
  - `messagelog.AddTime` 由應用程式寫入當下時間，不可用 DB 自動值。 **Evidence**: [stock-detail.md](#tablemessagelog) 時機。
- Transaction 規則：無跨表 Transaction。呼叫外部 API 前不宜做事務鎖定。
- Retry 規則：需人工確認 TwSMS API 呼叫失敗時是否實作 Retry，與 Retry 次數。
- `messagelog.Date` 格式應為 yyyy-MM-dd，基於發送日。
- 不可修改欄位：`messagelog` 寫入後僅 `SendStatus` 可更新，其餘欄位不可變動。 **Evidence**: `messagelog` append-only 規則。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求缺少手機號碼或內容 | 回傳 400 Bad Request，不寫入 messagelog。 |
| 手機號碼格式無效 | 回傳 400 Bad Request 並帶錯誤訊息，不發送。 |
| TwSMS API 連線逾時 | 寫入 `messagelog` 狀態為 2 (失敗)，回傳 502 Bad Gateway。 |
| TwSMS API 回傳錯誤 | 解析錯誤代碼，寫入 `messagelog` 狀態為 2，回傳對應的錯誤狀態碼或 502。 |
| DB 寫入 `messagelog` 失敗 | 簡訊可能已發送，但記錄失敗。需人工確認是否有補償或重試機制。此為高風險。 |

需人工確認：DB 寫入失敗時的具體處理策略。

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SMS-001 | API Test | 正常發送一個有效手機號碼與內容 | 返回 200 OK，messagelog 寫入 SendStatus=1。 |
| SMS-002 | API Test | 發送無效手機號碼（格式錯誤） | 返回 400 Bad Request。 |
| SMS-003 | API Test | 不帶驗證 Token 發送 | 返回 401 Unauthorized。 |
| SMS-004 | Integration | TwSMS API 模擬故障（500） | 返回 502，messagelog 寫入 SendStatus=2。 |
| SMS-005 | Flow Test | 寫入 messagelog 失敗 | 確認服務不會 Crash，並能正確記錄錯誤。 |
| SMS-006 | Permission | 使用無權限的 Token | 返回 403 Forbidden。 |

---

## 9. 高風險區域

- 高風險 API：`POST /api/v1/sms/twsms/message`。外部相依於 TwSMS API，穩定性仰賴第三方。
- Transaction：外部 API 呼叫與 DB 寫入為兩個獨立操作，存在不一致風險（簡訊已發送但 DB 寫入失敗）。
- 記錄缺失：TwSMS API 成功但 DB INSERT 失敗，導致無發送記錄。
- 資安：`MsgContent` 可能包含敏感資訊（如驗證碼），需確保其不被洩漏。API 請求應走 HTTPS。

---

## 10. 常見錯誤

- 新人容易犯錯：誤以為 mqservice 完全不操作 DB，而忽略 `messagelog` 寫入。 **Evidence**: README 與 db-usage 敘述矛盾。
- AI 容易誤解：錯誤推斷 `SendStatus=0` 存在滯留未發訊息，實際上 mqservice 是在發送後同步寫入狀態 1 或 2。
- 常見漏檢查項目：未驗證手機號碼格式就呼叫 TwSMS API。
- 常見錯誤流程：將 TwSMS API 呼叫放在 DB Transaction 內。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README.md - 對外 API 重點 |
| DB | stock.md / stock-detail.md - messagelog 表定義與權責 |
| Service | 需人工確認：SmsController / SmsService / TwSmsProvider |
| Dependency | README.md - 服務相依（TwSMS API） |
| Rule | stock-detail.md - messagelog 跨服務限制、SendStatus 規則 |