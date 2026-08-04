# 建立新彩票佣金

## 1. 場景目的

由上游佣金計算服務（NewLotteryCommissionService）透過呼叫 Payment Service，將計算後的新彩票佣金記錄寫入 `payment.commissions_betpool_newlottery` 表。記錄依 `ctype` 區分為「票券佣金 (ticket)」與「銷售佣金 (sell)」，供後續對帳與報表使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/newlottery/commissions/betpool` | 建立獎池佣金 |

---

## 3. 流程總覽

1. 佣金計算服務（調用方）完成佣金結算。
2. 調用方發送 POST 請求至 `/api/v1/newlottery/commissions/betpool`。
3. Payment Service 接收請求並驗證身份與參數。
4. 寫入一筆記錄至 `payment.commissions_betpool_newlottery`。
5. 回傳成功回應。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `NewLotteryCommissionController` | 接收 POST 請求 |
| 2 | Controller | `NewLotteryCommissionController` | 驗證請求參數及權限 |
| 3 | Service | `NewLotteryCommissionService` | 處理佣金邏輯、組裝資料 |
| 4 | Provider | `NewLotteryCommissionDataProvider` | 寫入 Cassandra `commissions_betpool_newlottery` |
| 5 | Controller | `NewLotteryCommissionController` | 回傳成功 |

> **需人工確認**：請驗證 Controller 與 Service 的具體名稱（`NewLotteryCommissionController` / `NewLotteryCommissionService`）及方法名稱，上述為基於命名的推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `payment.commissions_betpool_newlottery` | Write | 寫入佣金記錄 |
| DB | `payment.commissions_betpool_newlottery` | Read | 佣金查詢（查詢 API） |
| Cache | — | — | 本場景無 Redis 操作 |
| Queue | — | — | 本場景無 Kafka 操作 |

---

## 6. 重要規則

- **寫入權限**：`payment.commissions_betpool_newlottery` 僅供 `NewLotteryCommissionService` 寫入，禁止任何形式的人工 INSERT 或 UPDATE。
- **ctype 限制**：`ctype` 值必須為 `'ticket'` 或 `'sell'`，由佣金計算邏輯自動決定，API 不可任意傳入。
- **coin 限制**：`coin` 欄位（佣金金額）必須由佣金計算邏輯產生，API 不可直接設定。
- **不可變更**：記錄一經寫入，`id`、`betpool`、`source_uid`、`source_cid` 等核心關聯欄位不可變更，且記錄不可刪除。

- **不可回傳欄位**：對外（非管理後台）查詢佣金時，不可回傳 `source_uid` 與 `source_cid`。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求未經驗證 | 回傳 401 Unauthorized |
| 調用方權限不足 | 回傳 403 Forbidden |
| 漏傳必填參數 (如 `betpool` 或 `coin`) | 回傳 400 Bad Request |
| `ctype` 傳入無效值（非 `ticket` 或 `sell`） | 回傳 400 Bad Request 或被強制覆寫為正確值（依實作決定） |
| Cassandra 寫入失敗（Timeout / Unavailable） | 回傳 500 Internal Server Error |
| 寫入時 Primary Key 衝突 (`betpool` + `id` 重複) | 回傳 409 Conflict 或直接複寫（依 Cassandra upsert 行為） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 正確參數呼叫，ctype 為 `ticket` | 200 OK，DB 可查詢到記錄 |
| TC02 | API Test | 正確參數呼叫，ctype 為 `sell` | 200 OK，DB 可查詢到記錄 |
| TC03 | Permission Test | 不帶驗證 Token 呼叫 API | 401 Unauthorized |
| TC04 | Flow Test | 模擬 Cassandra 連線失敗 | 500 Internal Server Error |
| TC05 | API Test | 傳入空的 `betpool` | 400 Bad Request |

---

## 9. 高風險區域

- **高風險 Table**：`payment.commissions_betpool_newlottery` — 若被未授權服務直接寫入，將導致佣金數據錯亂，影響財務對帳。
- **禁止人工操作**：任何透過 DB 工具直接 INSERT / UPDATE / DELETE 此表的行為皆為高風險，必須嚴禁。
- **跨服務寫入**：需確保只有受信任的佣金計算服務能夠存取此 API，避免偽造佣金記錄。

---

## 10. 常見錯誤

- **新人容易犯錯**：手動在 DB 插入佣金記錄。應完全透過 `NewLotteryCommissionService` 調用 API 寫入。
- **AI 容易誤解**：
  - 認為此 API 可供前端或用戶觸發。此為內部服務間 API。
  - 認為 `ctype` 可以由請求方任意指定。應由佣金計算邏輯決定。
- **常見漏檢查**：對外查詢佣金 API 時，未過濾掉 `source_uid` 與 `source_cid`，導致隱私外洩。
- **錯誤流程**：佣金計算有誤時，試圖直接 UPDATE 此記錄。正確做法應是修正源頭數據並重新產生記錄（或執行沖正流程，視系統設計而定）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/newlottery/commissions/betpool` |
| DB | `payment.commissions_betpool_newlottery` |
| Table 寫入限制 | `paymentservice-detail.md` · 章節：payment > 寫入限制 |
| ctype 枚舉定義 | `payment-detail.md` · 章節：Table：commissions_betpool_newlottery > ctype 欄位 |
| 不可回傳欄位 | `paymentservice-detail.md` · 章節：payment > 不可回傳欄位 |

## 建議新增文件

- **`db-usage/commissions_betpool_newlottery.md`**：應補充此表的 Cassandra 寫入與讀取模式，及 `id` (UUID) 的生成規則。
- **API 文件**：應補充確切的 Request Body Schema 與範例。
- **規則文件**：應補充 `ctype` 的完整定義清單（目前已知 `ticket` 和 `sell`）。