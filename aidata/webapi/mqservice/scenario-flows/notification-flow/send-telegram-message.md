# 發送 Telegram 訊息

## 1. 場景目的

提供標準化 Telegram 訊息發送入口，支援告警、股票、銀行、InPlayZ 四種通知類型。呼叫者只需傳入目標 ChatID 與訊息內容，服務會透過 Telegram Bot API 發送，並記錄發送結果至 `messagelog` 日誌表。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/telegram/message` | 發送 Telegram 告警訊息 |
| POST | `/api/v1/telegram/message/stock` | 發送 Telegram 股票相關訊息 |
| POST | `/api/v1/telegram/message/bank` | 發送 Telegram 銀行相關訊息 |
| POST | `/api/v1/telegram/message/inplayz` | 發送 Telegram InPlayZ 訊息 |

所有端點均**需要驗證**（ECCore 3.0.2 內建機制）。

---

## 3. 流程總覽

1. 接收 POST 請求，由 ECCore 驗證身份。
2. 解析 request body 中的 `ChatID` 與 `Message`（需人工確認欄位名稱）。
3. 從設定檔（含 Zookeeper）讀取對應的 Telegram Bot Token。
4. 呼叫 Telegram Bot API 發送訊息至指定 ChatID。
5. 依發送結果寫入 `stock.messagelog` 表（INSERT 或先 INSERT 再 UPDATE）。
6. 回傳發送狀態給呼叫端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method（推測） | 動作 |
|------|-------|------------------------|------|
| 1 | Middleware | ECCore Auth | 驗證請求簽章或 Token |
| 2 | Controller | `TelegramController` | 接收並綁定請求參數 |
| 3 | Service | `TelegramService.SendAsync` | 讀取 Bot Token、呼叫 Telegram.Bot 發送 |
| 4 | Provider | `MessageLogProvider` | 寫入 `messagelog`（SendStatus 初始 0，後續依結果更新為 1 或 2） |
| 5 | Service | `TelegramService` | 根據發送結果組裝回應 |

> ⚠️ 實際類別與方法名稱需人工確認，本表基於常見命名慣例推導。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `stock.messagelog` | Write (INSERT) | 記錄發送任務，包含日期、帳號、發送方式、目標位址、訊息內容、初始狀態（0） |
| DB | `stock.messagelog` | Update (UPDATE) | 發送完成後更新 `SendStatus` 為 1（成功）或 2（失敗） |
| 外部 API | Telegram Bot API | HTTP POST (sendMessage) | 實際發送訊息 |

> mqservice 無 Redis 或 Kafka 暫存，直接同步發送。

---

## 6. 重要規則

- **權限限制**：所有 Telegram 發送 API 都必須通過 ECCore 驗證，未授權請求直接拒絕。
- **欄位限制**：`messagelog.Date` 格式為 `yyyy-MM-dd`；`Account` 不可為空，非使用者場景可能填入 `system` 或呼叫方服務名稱（需人工確認）。
- **不可暴露資料**：`messagelog.MsgContent` 不可回傳至前端（符合 db-usage 規範）。
- **TTL 規則**：無快取，訊息發送無 TTL。
- **Transaction 規則**：無跨表 Transaction，發送結果僅影響單一 `messagelog` 記錄。
- **Retry 規則**：目前未實作重試機制，發送失敗僅標記狀態並回傳錯誤（需人工確認是否預期加入重試）。
- **狀態值限制**：`messagelog.SendStatus` 只能為 0（未發送）、1（成功）、2（失敗），不可設為其他值。
- **不可修改欄位**：`messagelog` 的 `Date`、`Account`、`SendAction`、`TargetAddress`、`MsgContent` 建立後不可修改；`AddTime`、`LastUpdateTime` 由系統自動產生。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 驗證失敗（無效 Token 或簽章） | 回傳 401 Unauthorized，不執行任何業務邏輯 |
| ChatID 格式不合法或為空 | 回傳 400 Bad Request，不寫入 `messagelog` |
| Telegram Bot API 回傳失敗（如 ChatID 不存在、Bot 被移除） | 更新 `messagelog.SendStatus = 2`，回傳 502 Bad Gateway 或自定義錯誤碼 |
| DB 寫入 `messagelog` 失敗 | Telegram 可能已成功發送但記錄遺失，目前無補償機制（高風險，需人工確認） |
| 訊息內容超過 Telegram 限制（4096 字符） | Telegram API 回傳錯誤，處理同上，但建議前端驗證長度（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T01 | API Test | 使用有效憑證呼叫任一端點，提供正確 ChatID 與內容 | 收到 `200 OK`，目標聊天收到訊息，`messagelog` 中 `SendStatus=1` |
| T02 | Permission Test | 使用無效或過期憑證呼叫 | `401 Unauthorized`，無任何 DB 記錄 |
| T03 | Integration Test | 提供不存在的 ChatID | `4xx/5xx` 錯誤，`messagelog.SendStatus=2` |
| T04 | Flow Test | 模擬 DB 寫入失敗 | 服務應記錄錯誤 log，回傳 500，避免影響 Telegram 發送結果 |
| T05 | API Test | 缺少必填欄位（如 ChatID） | `400 Bad Request`，並說明缺少的欄位 |

---

## 9. 高風險區域

- **高風險 table**：`stock.messagelog`，若寫入失敗將導致發送證據遺失，且無法回溯。
- **高風險 API**：Telegram Bot API 因網路或對方限制容易暫態失敗，目前無重試（需人工確認）。
- **跨服務資料同步**：無。
- **Transaction**：無，需注意記錄與實際發送的非一致性。
- **Cache consistency**：無。
- **Queue retry**：無，建議未來評估導入輕量佇列進行非同步發送與重試。
- **Idempotency**：API 不支援冪等性，重複請求會造成多次 Telegram 發送與重複 `messagelog` 記錄。

---

## 10. 常見錯誤

- **新人容易犯錯**：忘記在 `messagelog` 初始化 `SendStatus=0` 再更新，或直接寫入最終狀態（導致無法區分未發送與失敗）。
- **AI 容易誤解**：以為 mqservice 無 DB 操作（README 寫「資料庫：無」），實際上它會讀寫 `stock` 資料庫的 `messagelog` 等表（需依賴 stock-detail 修正認知）。
- **常見漏檢查項目**：未驗證 `ChatID` 格式，可能傳入非數字字串導致 Telegram API 報錯。
- **常見錯誤流程**：發送成功但未更新 `messagelog`，或發送失敗卻誤標記為成功。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md / 訊息發送表格 |
| DB | `stock.md` > `messagelog` 結構 |
| DB 寫入規則 | `mqservice-detail.md` > `messagelog.SendStatus` 操作說明 |
| 驗證機制 | README.md > 技術棧 > 驗證：ECCore 3.0.2 內建機制 |
| Telegram 發送 | README.md > 技術棧 > Telegram.Bot 15.7.1 |
| 不可回傳欄位 | `db-usage` > 不可回傳欄位 > `MsgContent` |
| 服務相依 | README.md > 服務相依 > Telegram Bot |

> 部分細節如 `Account` 欄位值、請求欄位結構、Bot Token 來源需人工確認。