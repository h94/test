# 發送 Log 訊息

## 1. 場景目的

接收來自平台內其他服務的日誌訊息請求，經過身份驗證後，對請求內容進行處理。根據現有文件，具體處理方式（如寫入資料庫 `messagelog` 或輸出至系統日誌）尚需釐清，此文件將基於既有資訊進行推斷，並標明待確認部分。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/log/message` | 接收並處理 Log 訊息 |

---

## 3. 流程總覽

**需人工確認**：由於缺乏對應的 Controller/Service 原始碼，以下流程為根據 README、DB Schema 及服務定位的**邏輯推斷**，並非最終實現。

1. 接收 Log 訊息 POST request。
2. 驗證 API 呼叫方的身份（Auth）。
3. 解析請求內容（可能是 Log 等級、訊息、來源服務等）。
4. 將訊息寫入 `stock` 資料庫的 `messagelog` 表，或直接輸出到系統日誌（如 Console, File, Elasticsearch）。**需人工確認最終實作。**
5. 回傳處理結果。

---

## 4. 程式流程

**需人工確認**：因缺乏原始碼，以下為推斷的邏輯流程。

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `LogController.PostMessage` (推斷) | 接收請求，呼叫驗證 |
| 2 | Service / Validator | `AuthValidator` (推斷) | 驗證請求的 API Key 或 Token |
| 3 | Service | `LogService` (推斷) | 解析請求內容 |
| 4 | Provider / Transfer | `MessageLogProvider` (推斷) | 將處理後的資料寫入資料庫或輸出至日誌 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `stock.messagelog` | Write | 若流程包含持久化，則會新增一筆日誌記錄 |
| Redis | 無 | - | 根據 `mqservice` 職責，本服務未使用 Redis |
| Queue | 無 | - | README 未提及此端點使用 Queue |

**Evidence**: `mqservice` README 指出服務本身無資料庫，為純訊息轉發服務，但 `stock` DB 中存在 `messagelog` 表，且 `mqservice` 在其讀寫規則中有被提及。

---

## 6. 重要規則

- **權限限制**：此 API 需要驗證（`需要驗證 ✅`），呼叫方必須提供有效的驗證憑證。
- **必填欄位**：Request body 應包含標準的 Log 資訊（如 Level, Message, ServiceName），**欄位定義需人工確認**。
- **不可修改欄位**：若寫入 `messagelog`，`AddTime` 與 `LastUpdateTime` 應由資料庫自動維護，應用層不可寫入。
- **敏感資訊**：不可在 Log 訊息中記錄密碼（`Password`）或完整的手機（`Phone`）、信箱（`Email`）等個資。

**Evidence**: `mqservice` README (API 需要驗證), `stock-detail.md` (messagelog 寫入限制, 不可回傳欄位)

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未提供驗證 Header 或驗證失敗 | 回傳 `401 Unauthorized` |
| Request body 格式錯誤（如缺少必要欄位） | 回傳 `400 Bad Request` |
| 資料庫寫入失敗 | 回傳 `500 Internal Server Error`，並可能嘗試寫入本機 Log |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-01 | Unit Test | 傳入正確的 Log 資訊 | 成功寫入 `messagelog` 或系統日誌，回傳 `200 OK` |
| UT-02 | Permission Test | 未帶驗證 Token 發送請求 | 回傳 `401 Unauthorized` |
| UT-03 | API Test | 傳入缺少 `Message` 欄位的請求 | 回傳 `400 Bad Request` |
| UT-04 | Flow Test | 模擬 DB 連線失敗 | 服務擲出例外，回傳 `5xx` 錯誤碼 |

---

## 9. 高風險區域

- **高風險 Table**：`stock.messagelog`
  - **原因**：若此端點直接寫入，任何通過驗證的服務皆有權限新增記錄，需注意寫入頻率與內容大小，避免日誌表暴增。
- **高風險 API**：`POST /api/v1/log/message`
  - **原因**：作為全平台統一的 Log 入口，若發生效能問題或崩潰，將影響所有服務的 Log 記錄。
- **資料庫一致性**：此服務在 README 中被定義為「無持久化」，若其實作卻直接寫入資料庫，則存在文件與實作不一致的風險。**需人工確認。**

---

## 10. 常見錯誤

- 在 Log 訊息中記錄敏感個資（如完整的 `Email`, `Phone`）。
- 試圖手動寫入 `messagelog` 的 `AddTime` 或 `LastUpdateTime` 欄位。
- 認為此服務有使用 Redis 或 Kafka 來緩衝 Log 訊息（根據文件，它沒有）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 定義 | `mqservice/README.md` - 對外 API 重點 |
| DB Table | `db/stock/schema.sql` - `messagelog` |
| DB 規則 | `db/stock-detail.md` - `messagelog` 寫入限制 |
| 服務職責 | `mqservice/README.md` - 職責、技術棧 |
| 服務相依 | `mqservice/README.md` - 無 Redis 使用 |