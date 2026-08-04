# 查詢球種交易資料

## 1. 場景目的

本場景描述管理後台使用者查詢特定球種 (`game_type`) 下所有交易持倉記錄的完整流程。透過此 API，管理者可依 `lid`（聯盟）、`startdate` / `enddate` 等條件過濾，取得大量交易數據，用於報表、對帳與風控。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/tradedata/{game_type}` | 查詢指定球種的交易持倉資料 |

**參數**：
- **Path**：`game_type`（必填，如 `BK`, `SC`，對應 Cassandra 表 `stock_holdings_{game_type}`）
- **Query**：`lid`、`startdate`、`enddate`（均為選填，用於過濾）

**Evidence**：OpenAPI 定義 `get_trade_data_api_tradedata__game_type__get`

---

## 3. 流程總覽

1. 接收請求，取得 path parameter `game_type` 與 query parameters `lid`、`startdate`、`enddate`
2. 驗證 API Key / 內部服務授權，確保為管理後台呼叫
3. 驗證 `game_type` 是否為合法球種（對應 Cassandra 的 `stock_holdings_*` 表存在）
4. 查詢 Cassandra `stock_holdings_{game_type}` 表：
   - 根據 `gdate` 分區鍵與查詢參數動態構建 CQL
   - 若未提供 `startdate` / `enddate`，則默認查詢近期全部資料
5. 取得所有符合條件的交易持倉記錄
6. 回傳交易列表

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Route | `app.py` | 路由 `/api/tradedata/<game_type>` → `trade_data_list` |
| 2 | Controller | `TradeController` | 接收 `game_type`、`lid`、`startdate`、`enddate` 參數 |
| 3 | Service | `TradeService` | 驗證 `game_type` 合法性，動態定位 Cassandra 表 |
| 4 | Provider | `StockHoldingsProvider` | 構建 CQL 查詢 `SELECT * FROM stock_holdings_{game_type} WHERE ...` |
| 5 | Provider | `StockHoldingsProvider` | 執行查詢，讀取 `stock_holdings` 記錄 |
| 6 | Transfer | `StockHoldingsRowResponse` | 序列化結果，回傳交易列表（含持倉、盈虧等） |

**Evidence**：OpenAPI Operation ID `get_trade_data`；README API 路由表

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `tradegame.stock_holdings_{game_type}` | Read | 讀取指定球種的交易持倉與盈虧記錄 |
| Redis | （此場景未使用） | - | 此場景為管理後台批次查詢，無 Cache |

**Evidence**：tradegame-detail.md `stock_holdings_*` 讀取規則；dbSchema `tradegame.keyspace`

---

## 6. 重要規則

- **權限限制**：僅管理後台可呼叫，驗證 API Key
- **欄位限制**：
  - `trade_history`：非本人查詢時必須遮蔽或僅統計化，不回傳原始交易明細
  - `winloss`：對外回傳（供管理者查看），但不可修改
  - `account`：非本人查詢時需遮蔽或僅供統計使用
- **分區鍵限制**：查詢時應盡量提供 `gdate` 範圍（`startdate` / `enddate`），避免跨分區全表掃描
- **不可寫入欄位**：此 API 僅供查詢，不可更新任何 `stock_holdings` 欄位（如 `winloss`、`trade_history`、`stock_num`、`account` 等）
- **動態表名**：表名 `stock_holdings_{game_type}` 由 URL path 決定，需校驗合法性，避免 CQL Injection
- **不可暴露資料**：`password`、`phone`、`handler` 不應出現在回傳

**Evidence**：tradegame-detail.md 讀取規則與不可回傳欄位；DB detail 寫入限制

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `game_type` 不存在或非法 | 回傳 422 或 404，拒絕查詢 |
| 缺少必填參數 `game_type` | 回傳 422 Validation Error |
| API Key 缺失或無效 | 回傳 401 Unauthorized |
| Cassandra 查詢逾時 | 回傳 500 Internal Server Error |
| 查詢時間範圍過大導致全表掃描 | 可能因 Cassandra 效能限制而逾時，需前端限制範圍 |
| 查詢結果為空 | 回傳空陣列 `[]`，不回傳錯誤 |

**Evidence**：OpenAPI 定義 `422` / `500` 回應；Cassandra 查詢限制

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC-001 | API Test | 正確 `game_type` 與合法 `lid` 查詢 | 回傳 200，交易列表 |
| TC-002 | API Test | 僅提供 `game_type`，無過濾條件 | 回傳 200，所有近期交易 |
| TC-003 | API Test | `game_type` 不合法（如 `INVALID`） | 回傳 422 或 404 |
| TC-004 | Permission Test | 無效 API Key | 回傳 401 |
| TC-005 | Flow Test | 查詢範圍內無交易資料 | 回傳 200，空陣列 `[]` |
| TC-006 | API Test | 查詢結果包含 `trade_history` 欄位但已遮蔽 | 回傳資料中 `trade_history` 為空或統計值 |
| TC-007 | Flow Test | 提供 `startdate` / `enddate` 過濾 | 回傳資料僅在日期範圍內 |

**Evidence**：OpenAPI 定義；tradegame-detail.md 讀取規則

---

## 9. 高風險區域

- **高風險 Table**：`tradegame.stock_holdings_*`，存放所有交易與盈虧數據
- **高風險 API**：`GET /api/tradedata/{game_type}`，若無權限控制可導出大量機敏交易資料
- **跨服務資料同步**：無（僅讀取此服務的 Cassandra）
- **Transaction**：無（僅 SELECT 操作）
- **Cache consistency**：此場景無 Cache 使用，無一致性風險
- **Queue retry**：無
- **Idempotency**：查詢操作本身冪等，無副作用

**Evidence**：tradegame-detail.md 寫入限制；README 服務相依說明

---

## 10. 常見錯誤

- ❌ **未驗證 `game_type` 參數，直接拼接 CQL 造成 Injection**  
  ✅ 必須校驗 `game_type` 是否在合法列表中，並使用參數化查詢。
- ❌ **回傳 `trade_history` 原始資料（含使用者的每一筆買賣）**  
  ✅ 應遮蔽或只回傳統計值（如總交易次數）。
- ❌ **未提供 `gdate` 範圍條件，導致 Cassandra 全表掃描與逾時**  
  ✅ 後端應要求前端傳入時間範圍或限制最大查詢跨度。
- ❌ **將此 API 開放給一般使用者（應為管理後台專用）**  
  ✅ 需驗證 API caller 身份為管理後台服務。
- ❌ **回傳 `account` 欄位原始值**  
  ✅ 應做脫敏（如只顯示前兩碼與最後兩碼）。

**Evidence**：tradegame-detail.md 常見錯誤；DB detail 不可回傳欄位

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI `get_trade_data_api_tradedata__game_type__get` |
| DB | `tradegame.stock_holdings_{game_type}` 系列表 |
| DB 操作限制 | `tradegame-detail.md` 讀取規則與不可回傳欄位 |
| DB Schema | `tradegame.md` |
| 驗證規則 | README 「需要驗證」欄位 |
| 服務相依 | README 「服務相依」：Cassandra（tradegame keyspace） |