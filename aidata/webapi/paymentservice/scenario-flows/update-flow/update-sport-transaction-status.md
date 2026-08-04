# 更新體育交易訂單狀態

## 1. 場景目的

提供金流回調（Payment Callback）或後台管理員透過 API 變更體育交易訂單狀態的標準流程。主要用於將訂單從「待付款」更新為「付款成功」、「付款失敗」或其它業務定義的狀態終態。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/sport/transactions/{year}/{dateTime}/{account}/{id}` | 更新指定體育交易訂單狀態 |

---

## 3. 流程總覽

1. 後台系統或第三方金流回調觸發 API 請求。
2. 驗證請求來源與 `authKey`。
3. 根據路徑參數（`year`, `dateTime`, `account`, `id`）查詢 `payment.sport_transactions` 確認訂單存在。
4. 驗證當前訂單狀態是否允許更新（需人工確認）。
5. 執行更新操作，寫入新的 `status`。
6. 依據新狀態觸發後續業務邏輯（如透過 `mq` 發送付款成功通知，需人工確認）。
7. 回傳操作成功結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `SportTransactionController.UpdateTransaction` | 接收 PUT 請求，解析路徑參數與 request body |
| 2 | Validator | `SportTransactionValidator` | 驗證 `year`, `dateTime`, `account`, `id` 格式與 `status` 有效性 |
| 3 | Service | `SportTransactionService.UpdateStatus` | 確認訂單存在，驗證狀態流轉規則，執行更新 |
| 4 | Provider | `SportTransactionDataProvider` | 與 Cassandra 交互，讀取與更新 `sport_transactions` |
| 5 | Message Queue | `MqService.Publish` | 根據新狀態，發送付款成功/失敗通知（需人工確認） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.sport_transactions` | Read | 查詢待更新的訂單明細 |
| DB | `payment.sport_transactions` | Update | 更新訂單狀態（`status`） |
| Cache | `SportCache:SportTransactions` | Delete | 若存在交易快取，需使其失效以確保資料一致性（需人工確認） |
| Queue | `mq` | Publish | 發送付款成功通知信給會員（需人工確認） |

---

## 6. 重要規則

- **權限限制**：此 API 需要內部驗證，不可對外公開。通常只允許透過 `ECFramework` 驗證的內部服務（如金流閘道或管理後台）呼叫。
- **欄位限制**：
  - `status`：更新時必須為有效狀態值（需人工確認）。
  - 訂單識別碼（`year`, `dateTime`, `account`, `id`）不可修改。
- **不可暴露資料**：API 回傳不應包含完整的付款細節（如卡號）。
- **Transaction 規則**：更新操作應為原子性，避免併發更新導致狀態不一致。
- **狀態值限制**：狀態流轉應遵循業務規則，不允許任意的狀態回退或跳躍（需人工確認）。
- **不可修改欄位**：`year`, `date_time`, `account`, `id`, `amount`。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 路徑參數格式錯誤（`year` 非數字） | 400 Bad Request |
| `account` 或 `id` 不存在 | 404 Not Found |
| 請求中未提供有效的 `status` | 400 Bad Request |
| 非法狀態流轉（如從