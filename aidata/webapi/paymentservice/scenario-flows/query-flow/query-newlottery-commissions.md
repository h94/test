# 查詢新彩票佣金

## 1. 場景目的

提供後台管理人員或具權限之服務，查詢指定獎池 (`betpool`) 下的所有佣金記錄，用於對帳、報表統計或問題排查。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/newlottery/commissions/betpool/{betpool}` | 查詢指定獎池佣金 |

---

## 3. 流程總覽

1. 接收請求，從路由參數取得 `betpool`。
2. 透過內部驗證框架 (`ECFramework.ECService`) 驗證呼叫方權限。
3. 調用 `NewLotteryCommissionDataProvider` 查詢 Cassandra `payment.commissions_betpool_newlottery`。
4. 根據 `betpool` 分區鍵讀取所有佣金記錄。
5. 過濾不可回傳的敏感欄位 (`source_uid`, `source_cid`)。
6. 回傳佣金列表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `NewLotteryController.GetCommissionsByBetpool` | 接收 `betpool` 參數，調用 Service。 |
| 2 | Service | `NewLotteryCommissionService.GetCommissionByBetpool` | 調用 DataProvider。 |
| 3 | Provider | `NewLotteryCommissionDataProvider.GetByBetpool` | 組裝 CQL `SELECT * FROM payment.commissions_betpool_newlottery WHERE betpool = ?`，執行查詢。 |
| 4 | Transfer | `NewLotteryCommissionTransfer` | 將 Entity 轉換為 DTO，排除 `source_uid`、`source_cid`。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `payment.commissions_betpool_newlottery` | Read | 唯一資料來源，依 `betpool` 分區鍵查詢。 |
| Redis / Cache | 無 | 無 | 在此場景中，佣金查詢未使用快取。 |
| Kafka / Queue | 無 | 無 | 無。 |

---

## 6. 重要規則

- **權限限制**：此 API 需要驗證，僅允許後台管理或具相應權限之服務帳號調用。
- **查詢規則**：必須指定 `betpool`，不允許全表掃描。
- **不可暴露資料**：
    - `commissions_betpool_newlottery.source_uid`：來源用戶 ID。
    - `commissions_betpool_newlottery.source_cid`：來源客戶 ID。
- **欄位限制**：所有 `commissions_betpool_newlottery` 欄位均由 `NewLotteryCommissionService` 管理，此場景僅唯讀。
- **狀態值限制**：`ctype` 為固定枚舉值（如 `ticket`、`sell`），由寫入時決定。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未提供或提供無效的驗證 Token | 返回 HTTP 401 Unauthorized。 |
| 呼叫方權限不足 | 返回 HTTP 403 Forbidden。 |
| 請求路徑缺少 `betpool` 參數 | 返回 HTTP 400 Bad Request。 |
| 查詢的 `betpool` 無任何佣金記錄 | 返回 HTTP 200 OK，Body 為空陣列 `[]`。 |
| Cassandra 查詢超時或失敗 | 返回 HTTP 500 Internal Server Error。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| `TC-COMM-001` | API Test | 以有效 `betpool` 請求，DB 中有 3 筆記錄。 | 200 OK，回傳 3 筆佣金資料，且不包含 `source_uid`、`source_cid`。 |
| `TC-COMM-002` | API Test | 以不存在的 `betpool` 請求。 | 200 OK，回傳空陣列 `[]`。 |
| `TC-COMM-003` | Permission Test | 未攜帶 Token 或以一般使用者 Token 請求。 | 401 Unauthorized 或 403 Forbidden。 |
| `TC-COMM-004` | API Test | 驗證回傳的 `ctype` 欄位值是否為 `ticket` 或 `sell`。 | 200 OK，回傳資料的 `ctype` 符合預期。 |

---

## 9. 高風險區域

- **高風險 table**：`payment.commissions_betpool_newlottery`。此表包含敏感的用戶與客戶識別資訊 (`source_uid`, `source_cid`)，誤暴露將違反隱私協定。
- **跨服務資料同步**：需人工確認。根據 `db/payment-detail.md`，`newlotterybackendservice`, `pricecenterservice`, `pricebackendservice` 等服務均有權限寫入此表，可能潛在資料一致性風險。查詢端無風險。
- **效能風險**：若某 `betpool` 下佣金記錄數量巨大，查詢可能變慢。需注意 `betpool` 設計是否能均勻分佈資料，避免 hotspot。

---

## 10. 常見錯誤

- ❌ **新人直接在 DB 管理工具執行 `SELECT * FROM payment.commissions_betpool_newlottery` 進行排查。**
- ✅ 正規作法是透過此 API 或具備權限控制的內部工具查詢。
- ❌ **AI 或開發者將 `source_uid`、`source_cid` 包含在回傳結果中給前端。**
- ✅ 必須在 Transfer 層或 API 返回前將這兩個欄位排除。對外 API 絕不可回傳。
- ❌ **開發者想透過其他非 `betpool` 的條件（如 `source_uid`）進行查詢。**
- ✅ 查詢必須以分區鍵 `betpool` 為主要條件，若需靈活查詢，需與 DBA 討論建立物化視圖或次要索引的可能性與風險。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `NewLotteryController` (OpenAPI: GET `/api/v1/newlottery/commissions/betpool/{betpool}`) |
| DB | `payment.commissions_betpool_newlottery` (Schema: `betpool` as partition key) |
| Code | `NewLotteryCommissionService`, `NewLotteryCommissionDataProvider` (來自 Phase0/1 語義分析) |
| Rule | `db/payment-detail.md`: "不可回傳欄位: source_uid, source_cid" |
| Rule | `paymentservice-detail.md`: "佣金查詢：依 betpool 分區查詢特定彩池佣金" |