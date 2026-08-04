# 查詢新彩票交易訂單

## 1. 場景目的

提供後台管理員或前台會員查詢新彩票儲值或佣金相關的交易記錄。支援以帳號、日期範圍等條件篩選，回傳符合條件的訂單列表。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/newlottery/transactions` | 查詢新彩票交易訂單（支援多條件） |

**需驗證**：✅

---

## 3. 流程總覽

1. 接收查詢請求，驗證呼叫者身份與權限（後台或會員本人）。
2. 解析查詢參數（`account`、日期範圍等）。
3. 根據參數組合 Cassandra 查詢條件。
4. 查詢 `payment.newlottery_transactions`。
5. 回傳符合條件的交易記錄，過濾敏感欄位。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `NewLotteryController.GetTransactions` | 接收請求，呼叫 Service |
| 2 | Service | `NewLotteryTransactionService.GetTransactions` | 驗證參數，組合查詢條件 |
| 3 | Provider | `NewLotteryTransactionDataProvider` | 執行 Cassandra 查詢 |
| 4 | Cassandra | `payment.newlottery_transactions` | 查詢交易記錄 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `payment.newlottery_transactions` | Read | 查詢新彩票交易記錄 |

---

## 6. 重要規則

- **權限限制**：
  - 後台管理員可查詢所有帳號交易。
  - 前台會員僅能查詢本人交易（`account` 須與驗證身份一致）。
- **查詢條件**：
  - `account` 為必填或需人工確認。
  - 必須提供時間範圍限制，避免全表掃描。
- **不可暴露資料**：
  - `commissions_betpool_newlottery` 相關的 `source_uid`、`source_cid` 不可回傳。
  - 交易細節 `T_Detail`、`T_UID` 需脫敏或僅後台可見。
- **狀態值限制**：
  - 需人工確認是否有 `status` 欄位過濾規則。
- **Transaction 規則**：查詢操作為唯讀。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未提供 account 參數（若為必填） | 回傳 400 錯誤 |
| account 與驗證身份不符（前台） | 回傳 403 權限不足 |
| 查詢時間範圍過大 | 需人工確認是否限制或拒絕 |
| Cassandra 查詢超時 | 回傳 500 錯誤 |
| 無符合條件的交易 | 回傳空陣列 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | Permission Test | 前台查詢他人 account | 403 或 400 |
| T02 | Flow Test | 後台查詢所有交易 | 200 回傳列表 |
| T03 | API Test | 未帶 account 查詢 | 需人工確認預期結果 |
| T04 | API Test | 指定有效的 account 及日期範圍 | 200 回傳該帳號交易 |
| T05 | API Test | 查詢無記錄的 account | 200 空陣列 |

---

## 9. 高風險區域

- **高風險 table**：
  - `payment.newlottery_transactions`：主交易記錄，需嚴控跨帳號查詢權限。
- **高風險 API**：
  - 前台查詢若未限制 `account` 可能洩漏全站交易。
- **Query 效能**：
  - 未限制時間範圍可能導致 Cassandra 節點壓力過大。

---

## 10. 常見錯誤

- ❌ **前台查詢未強制綁定登入 account**：
  ✅ 必須比對 token 身份與 `account` 參數，或由後端自動注入。
- ❌ **後台查詢未限制時間範圍**：
  ✅ 應強制要求或預設近 30 天。
- ❌ **回傳了不應暴露的佣金來源 UID**：
  ✅ 須在回傳前過濾或脫敏。
- ❌ **直接拼接 SQL 導致注入**：
  ✅ 使用 Cassandra 參數化查詢。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `GET /api/v1/newlottery/transactions` |
| DB | `payment.newlottery_transactions` |
| Code | `NewLotteryController`, `NewLotteryTransactionService`, `NewLotteryTransactionDataProvider` |
| SQL | `SELECT * FROM payment.newlottery_transactions WHERE ...` |