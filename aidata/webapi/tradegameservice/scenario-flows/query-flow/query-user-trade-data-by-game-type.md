# 查詢使用者球種交易資料

## 1. 場景目的

讓使用者查詢自身在特定球種（game_type）的交易持倉資料，支援以聯賽（lid）、日期區間進行篩選。管理後台亦可透過此 API 查詢指定帳戶的交易資料。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/usertradedata/{account}/{game_type}` | 查詢指定會員在特定球種的交易持倉。可帶 query 參數過濾 lid、startdate、enddate。 |

---

## 3. 流程總覽

1. 接收查詢 request，包含路徑參數 `account`、`game_type`，以及可選查詢參數 `lid`、`startdate`、`enddate`。
2. 驗證基本參數格式（非空、球種代碼與 Cassandra 表前綴一致）。
3. 進行身份驗證（API Key / 內部服務授權）。
4. 驗證請求者權限（僅允許查詢自身帳戶，或請求來自管理後台）。
5. 驗證目標帳戶狀態（從 `pricecenter` 的 accounts_* 表或 Redis 快取驗證 `enabled=1`）。
6. 依 `game_type` 動態決定查詢的 Cassandra 表，如 `stock_holdings_{game_type}`。
7. 組合 CQL 查詢，包含 partition key `gdate` 以及 clustering key `lid`, `gid`, `account`, `mode_spread_type`，並套用查詢過濾條件。
8. 執行查詢，取得用戶的持倉清單。
9. 處理回傳結果，依規則遮蔽或過濾敏感欄位（如非本人查詢時，`winloss`、`trade_history` 需遮蔽）。
10. 回傳持倉資料陣列。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `trade.UserTradeDataResource` / `get_user_trade_data` | 接收路徑參數 `account`, `game_type`，查詢參數 `lid`, `startdate`, `enddate`；進行基本型態校驗後呼叫 Service。 |
| 2 | Service | `trade.TradeService` / `get_user_trade_data` | 執行身份驗證與授權檢查，確認查詢者為帳號本人或管理員。呼叫 Provider 進行資料查詢。 |
| 3 | Provider | `provider.TradeProvider` / `get_user_stock_holdings` | - 驗證帳戶狀態（查詢 `pricecenter` 的 `accounts_*` 表或 Redis key `price:acc:verify:{account}`，必須 `enabled=1` 且未關閉）。<br>- 組合 CQL，查詢 `tradegame.stock_holdings_{game_type}`。<br>- 處理查詢結果並回傳。 |
| 4 | Transfer | `schema.TradeSchema` / `StockHoldingsRowResponse` | 定義回傳 Schema，確保不回傳敏感欄位或進行脫敏處理。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `tradegame.stock_holdings_{game_type}` | Read | 查詢使用者在指定球種的持倉記錄。 |
| DB (Cassandra) | `pricecenter.accounts_*` | Read | 查詢帳戶是否存在且 `enabled=1`（若 Redis 快取未命中）。 |
| Redis | `price:acc:verify:{account}` | Read | 快取帳戶驗證結果，避免頻繁查詢 Cassandra。TTL 3600 秒。 |

---

## 6. 重要規則

- **權限限制**：
  - 使用者僅能查詢自己的庫存（路徑參數 `account` 必須與驗證通過的帳號相符）。
  - 管理後台可查詢任意帳戶。
- **Cassandra 查詢限制**：
  - 所有查詢需明確指定 partition key。因 `account` 非 partition key，查詢時仍須提供日期範圍（`gdate`）或 `lid`，避免全表掃描（ALLOW FILTERING 禁止）。
  - 若僅指定 `lid`，需依日期區間 `startdate`、`enddate` 遍歷多個 partition。
- **不可暴露資料**：
  - 非本人查詢時，`trade_history`、`winloss` 須遮蔽或僅回傳統計量。
  - `account` 欄位在非管理後台的一般查詢中應遮蔽。
- **帳戶狀態驗證**：查詢前必須確認帳戶 `enabled=1` 且 `closetime` 為空（或 `NULL`）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 路徑參數 `game_type` 為非法球種代碼 | 回傳 422 Validation Error。 |
| 未提供有效身份驗證（如 API Key 缺失或錯誤） | 回傳 401 Unauthorized。 |
| 一般使用者查詢他人的 `account` (路徑參數) | 回傳 403 Forbidden。 |
| 查詢的目標帳戶在 `pricecenter` 中不存在或 `enabled=0` | 回傳 404 Not Found 或 403 Forbidden，並提示帳戶無效。 |
| Cassandra 連線逾時或查詢失敗 | 回傳 500 Internal Server Error，並記錄錯誤日誌。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-01 | API Test | 使用正確的 account 和 game_type 查詢自身交易資料 | 200 OK，回傳該帳戶的持倉列表。 |
| PT-02 | Permission Test | 使用者A的 token 查詢使用者B的路徑參數 | 403 Forbidden。 |
| PT-03 | Permission Test | 使用管理後台 token 查詢任意 account | 200 OK，且回傳資料中 `winloss`, `trade_history` 可見。 |
| FT-04 | Flow Test | 目標帳戶已停用 (`enabled=0`) | 403 或 404，提示帳戶不可用。 |
| IT-05 | Integration Test | 模擬 Cassandra 查詢失敗 | 500 Internal Server Error。 |

---

## 9. 高風險區域

- **高風險 Table**：`tradegame.stock_holdings_{*}`。持倉數據為核心交易資料，任何不當的查詢或暴露都可能導致使用者隱私外洩或商業機密洩漏。
- **高風險 API**：`GET /api/usertradedata/{account}/{game_type}`。權限驗證不嚴謹可能導致越權存取（IDOR）。
- **Cache consistency**：Redis key `price:acc:verify:{account}` 的快取失效需及時。若帳戶被停用但快取未清除，可能短暫允許查詢已停用的帳戶。

---

## 10. 常見錯誤

- ❌ **未驗證 `account` 路徑參數與 token 的關聯性**：導致一般使用者可以查詢其他使用者的持倉。
- ❌ **在 Cassandra 查詢中使用 `ALLOW FILTERING`**：因為 `account` 非 partition key，若為方便直接加 `ALLOW FILTERING` 會造成嚴重效能問題。
- ❌ **查詢時未過濾 `enabled=1` 與 `closetime`**：可能對已停用帳戶執行查詢並回傳資料。
- ❌ **對非本人的查詢回傳了 `trade_history` 或未遮蔽的 `winloss`**：違反資料隱私規則。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI `/api/usertradedata/{account}/{game_type}` GET |
| DB | `tradegame.stock_holdings_BK`, `tradegame.stock_holdings_BS`, `tradegame.stock_holdings_SC` |
| DB Detail | `tradegame-detail.md` (stock_holdings_* tables) |
| DB Detail | `pricecenter-detail.md` (accounts_* tables, enabled/closetime rules) |
| Redis | `tradegameservice-detail.md` (`price:acc:verify:{account}`) |
| Code | `trade.UserTradeDataResource.get_user_trade_data` |
| Code | `trade.TradeService.get_user_trade_data` |