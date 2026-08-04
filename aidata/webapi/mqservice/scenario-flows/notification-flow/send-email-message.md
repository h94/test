# 發送 Email 訊息

## 1. 場景目的
當平台內部服務（如交易、會員）需要寄送 Email 通知給終端使用者時，呼叫 MQService 的 Email 發送 API。系統會根據品牌（一般 / InPlayZ）選擇對應的 SMTP 伺服器（Gmail 或 Zoho），組裝郵件內容後實際寄出，並將發送結果記錄至 `messagelog` 表。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/mail/message` | 一般品牌，使用 Gmail SMTP 發送 |
| POST | `/api/v1/mail/inplayz/message` | InPlayZ 品牌，使用 Zoho SMTP 發送 |

兩支 API 皆需要通過 ECCore 內建驗證（服務間驗證）才可呼叫。

---

## 3. 流程總覽

1. 接收 HTTP POST 請求（含收件人、主旨、內容等參數）
2. ECCore 驗證呼叫方身份（服務間認證）
3. 根據請求路徑決定 SMTP 配置（Gmail 或 Zoho）
4. 解析 request body 並組裝 MimeMessage（MailKit）
5. 建立 SmtpClient 連線至對應 SMTP 伺服器
6. 嘗試實際發送 Email
7. **無論成功或失敗**，將發送紀錄寫入 `stock.messagelog`（含發送狀態）
8. 回傳 HTTP 200（成功）或 500（失敗）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `MailController.SendMail` (推測) | 接收 request、呼叫 service |
| 2 | Service | `MailService` (推測) | 決定 SMTP 設定、組裝郵件 |
| 3 | Transfer | `MailKit` SmtpClient | 連線外部 SMTP 並發送 |
| 4 | Provider | `MessageLogRepository` (推測) | INSERT / UPDATE `messagelog` |

> ⚠️ **需人工確認**：Controller、Service、Provider 具體類別與方法名稱因無原始碼，以上為合理推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `stock.messagelog` | INSERT | 建立一筆發送記錄（初始 SendStatus = 0 或最終狀態） |
| DB | `stock.messagelog` | UPDATE | 發送完成後將 SendStatus 更新為 1（成功）或 2（失敗） |
| 外部服務 | Gmail SMTP (smtp.gmail.com:587) | 連線發送 | 一般品牌實際寄信 |
| 外部服務 | Zoho SMTP (smtp.zoho.com:587) | 連線發送 | InPlayZ 品牌實際寄信 |

> 本服務無 Redis、Kafka 參與此流程。

---

## 6. 重要規則

- **發送記錄不可刪除**：`messagelog` 為 append-only 日誌，INSERT 後僅 `SendStatus` 欄位可被更新為 1 或 2（來源：`stock-detail.md` 跨服務限制）。
- **SMTP 選定**：透過 API 路徑決定使用 Gmail 或 Zoho，不可由呼叫方任意指定其他 SMTP（來源：README 服務相依）。
- **郵件內容安全**：`messagelog.MsgContent` 可能包含郵件全文，對外查詢時應遮蔽或避免回傳（來源：`mqservice-detail.md` 常見錯誤）。
- **目標地址保護**：`TargetAddress` 在對外查詢時應遮蔽中間字元，不可明文完整暴露（來源：`mqservice-detail.md` 常見錯誤）。
- **發送狀態流轉**：`SendStatus` 僅允許 0 → 1（成功）或 0 → 2（失敗），不開放其他變更（來源：`stock-detail.md`）。
- **時間戳自動化**：`messagelog.AddTime` 與 `LastUpdateTime` 由應用層或 DB 自動設定，不可由呼叫方傳入。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 呼叫方未通過 ECCore 驗證 | HTTP 401 Unauthorized |
| 無法解析 request body（必要欄位缺失） | HTTP 400 Bad Request，不寫入 messagelog（需人工確認） |
| SMTP 連線失敗（如網路不通、認證失敗） | 補捉例外，寫入 messagelog (SendStatus=2)，回傳 HTTP 500 |
| 收件人 Email 格式不合法 | 可能由 SmtpClient 拋出例外，記錄失敗並回傳錯誤 |
| DB 寫入 messagelog 失敗 | 寄信可能已發出但無法記錄，此為高風險不一致（需確認是否有 retry 或補償機制） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T-01 | API Test | `POST /api/v1/mail/message` 帶有效參數 | 成功寄信，messagelog 寫入 SendStatus=1，HTTP 200 |
| T-02 | API Test | `POST /api/v1/mail/inplayz/message` 帶有效參數 | 成功寄信（Zoho），messagelog 寫入成功 |
| T-03 | Flow Test | SMTP 故意給錯密碼，觸發認證失敗 | messagelog 記錄 SendStatus=2，HTTP 500 |
| T-04 | Flow Test | DB 連線中斷，無法寫入 messagelog | 檢查錯誤處理邏輯，服務不應 crash（需人工確認） |
| T-05 | Permission Test | 無 ECCore token 呼叫 API | HTTP 401 |

---

## 9. 高風險區域

- **寄送與寫入非原子性**：郵件已寄出但 messagelog 寫入失敗，會導致記錄缺失，需考慮補償或 retry。
- **SMTP 連線外洩**：MailKit SmtpClient 若未正確釋放，可能造成連線洩漏。
- **郵件內容敏感資訊**：MsgContent 若未適當脫敏就存入 DB，可能違反資安規定。
- **跨服務依賴**：依賴外部 SMTP 伺服器，網路或認證問題將直接影響發送成功率。

---

## 10. 常見錯誤

- ❌ 開發時在程式中 hardcode Gmail/Zoho 帳密 → 應使用 Zookeeper 或 appsettings 管理設定（來源：README 使用 Zookeeper 配置中心）。
- ❌ 忘記在 messagelog 中記錄失敗狀態，只 log 到 console → 應在例外處理中明確 UPDATE SendStatus=2。
- ❌ 前端或呼叫方誤將 `POST /api/v1/mail/inplayz/message` 用於一般信件 → SMTP 發送會使用錯誤品牌信箱，可能被視為垃圾郵件。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | README.md 訊息發送表 |
| SMTP 相依 | README.md 服務相依 |
| messagelog 寫入權限 | stock-detail.md (mqservice 角色) |
| messagelog 狀態流轉 | stock-detail.md (SendStatus) |
| 發送記錄保護 | mqservice-detail.md 常見錯誤 |
| Zookeeper 配置 | README.md 服務相依 |