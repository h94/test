# 查詢使用者單日交易資料

## 1. 場景目的
提供使用者或後台管理員查詢特定帳戶在指定日期的所有交易持倉紀錄，用於日結對帳、歷史交易檢視或異常排查。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/usertradedailydata/{account}/{game_type}/{addtime}` | 查詢特定帳號在指定球種與日期的交易資料 |

---

## 3. 流程總覽

1. 接收查詢請求，路徑參數包含 `account`、`game_type`、`addtime`。
2. 驗證 API 授權（內部服務驗證）。
3. 驗證參數格式（特別是 `addtime` 日期格式 YYYY-MM-DD）。
4. 根據 `game_type` 動態決定 Cassandra 表名。
5. 對 `tradegame.stock_holdings_{game_type}` 執行查詢，條件為 `account = ?` 與 `gdate = ?`。
6. 若查無資料，回傳空陣列 `[]`。
7. 處理敏感欄位（如 `trade_history` 需遮蔽非本人查詢）。
8. 回傳符合格式的交易資料列表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | TradeController / TradeDailyView | 接收 GET 請求，解析路徑參數 |
| 2 | Validator | Marshmallow Schema | 校驗參數格式（字串非空、addtime 格式） |
| 3 | Service | TradeService.DailyUserTrade | 組合查詢條件，呼叫 Provider 層 |
| 4 | Provider | TradeProvider.QueryByAccount | 動態組裝 CQL `SELECT * FROM stock_holdings_{game_type}` |
| 5 | Provider | TradeProvider.QueryByAccount | 添加 `WHERE account = ? AND gdate = ?` 條件 |
| 6 | Service | TradeService.DailyUserTrade | 過濾不可回傳欄位、脫敏處理 |
| 7 | Controller | TradeController / TradeDailyView | 序列化為 JSON 回傳 |

*註：實際呼叫層次需人工確認 Controller / Service 具體名稱。*

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `tradegame.stock_holdings_{game_type}` | Read | 查詢指定帳戶在指定日期的持倉紀錄 |
| Redis | *未使用* | 無 | 此流程無快取讀取需求 |
| Kafka | *未使用* | 無 | 此為純查詢流程，無消息發布 |

---

## 6. 重要規則

- **權限限制**：使用者僅能查詢自己的紀錄（`account` 必須與登入身份一致）；管理後台可查詢任意帳戶。
- **欄位限制**：
  - `trade_history`：非本人查詢時必須遮蔽（不回傳或統計化處理）。
  - `password`、`phone` 等帳戶隱私欄位**不可**在此回傳（即使來源表有其他欄位也不可洩漏）。
  - `account`：管理後台查詢時需脫敏處理後才可回傳。
- **動態表名**：`game_type` 必須與 Cassandra 中的表名後綴一致（例：`BK`、`BS`、`SC`），不可任意傳入。
- **不可修改欄位**：此為讀取操作，不可對 `stock_holdings` 表進行任何 UPDATE、DELETE。
- **查詢效能**：必須同時指定 `account` 與 `gdate`，避免跨分區掃描或觸發 Cassandra `ALLOW FILTERING`。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `game_type` 參數不存在對應的 Cassandra 表 | 回傳 400 Bad Request 或對應錯誤碼 |
| `addtime` 格式不符（非 YYYY-MM-DD） | 回傳 422 Validation Error |
| 指定 `account` + `gdate` 無任何紀錄 | 回傳空陣列 `[]`，HTTP 200 |
| Cassandra 查詢 timeout | 回傳 500 Internal Server Error |
| 未授權呼叫（API Key 無效或無內部權限） | 回傳 401 或 403 |
| 一般使用者查詢他人的 `account` | 回傳 403 Forbidden |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|--------|------|------|----------|
| QT-01 | API Test | 正確參數，有交易紀錄的日期 | 回傳 200，資料筆數大於 0，欄位完整 |
| QT-02 | API Test | 正確參數，無交易紀錄的日期 | 回傳 200，空陣列 `[]` |
| QT-03 | API Test | `game_type` 不存在（如 `XX`） | 回傳 400 或 500 |
| QT-04 | API Test | `addtime` 格式錯誤（如 `2026/05/01`） | 回傳 422 Validation Error |
| QT-05 | Permission Test | 使用一般使用者 token 查詢他人帳戶 | 回傳 403 |
| QT-06 | Permission Test | 使用管理員 token 查詢任意帳戶 | 回傳 200，帳號已被脫敏 |
| QT-07 | Flow Test | 故意刪除對應表模擬 DB 異常 | 回傳 500 |

---

## 9. 高風險區域

- **全表掃描風險：** Cassandra `stock_holdings_{game_type}` 的分區鍵為 `gdate`，若查詢僅指定 `account` 而未指定 `gdate`，會被迫使用不建議的 `ALLOW FILTERING` 或產生跨分區掃描，導致效能問題。須強制帶入 `gdate`。
- **敏感資料外洩：** `trade_history` 與 `winloss` 對非本人查詢不可直接回傳原始值。若在此 API 用於管理後台時未遮蔽，將造成個資外洩。
- **動態表名注入：** `game_type` 由 API 路徑傳入並直接拼接成 SQL，若未嚴格校驗，可能導致 Cassandra 查詢異常或錯誤的表訪問。

---

## 10. 常見錯誤

- ❌ **未過濾 `gdate` 導致掃描全表**：Cassandra 設計上 `gdate` 為分區鍵，只指定 `account` 時查詢效率極差且可能觸發 `ALLOW FILTERING` 限制，應在 Service 層校驗是否有 `gdate` 條件。
- ❌ **直接將 `trade_history` 回傳給非本人**：管理後台或非本人查詢場景下，未遮蔽此欄位即回傳整筆記錄，違反隱私規則。
- ❌ **誤將此 API 用於結算**：`winloss` 欄位在查詢時可能為空值（`NULL`），若程式直接依賴此值判斷輸贏，將出現邏輯錯誤。
- ❌ **未處理 `stock_holdings` 的動態表名不存在的情況**：當傳入不支援的 `game_type` 時，程式直接崩潰或回傳不清晰的錯誤碼，應捕獲此異常並給出清晰錯誤訊息。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 定義 | OpenAPI: `/api/usertradedailydata/{account}/{game_type}/{addtime}` |
| DB Table | `tradegame.stock_holdings_BK`, `tradegame.stock_holdings_BS`, `tradegame.stock_holdings_SC` |
| DB 分區鍵規則 | `tradegame-detail.md` (分區鍵為 `gdate`) |
| 讀取限制 | `tradegame-detail.md` (trade_history 對非本人不可回傳) |
| 寫入限制 | `tradegame-detail.md` (stock_num, winloss 僅由交易/結算流程更新，查詢不可修改) |
| 代碼推測 | 需人工確認確切 Service / Provider 檔名與方法 |

### 建議新增文件
- **API 權限對照表**：明確列出每個 API 的角色權限（一般使用者 vs 管理員 vs 內部服務），避免跨場景權限誤判。
- **tradegameservice 管理者 API 串接指南**：針對後台管理需求，提供 `trade_history`、`winloss` 等敏感欄位的脫敏或顯示規則。
- **Cassandra 查詢規範**：統一規定各服務查詢 `tradegame` keyspace 必須帶入分區鍵與必要 Clustering Key，禁止 `ALLOW FILTERING`。

### 建議新增規則
- **規則：查詢使用者單日交易資料的回傳欄位限制**：非本人查詢時，`trade_history` 一律回傳 `"***"` 或統計化後的摘要；`winloss` 僅在非為 `NULL` 時可回傳，`NULL` 時回傳 `"pending"`。

### 建議新增測試情境
- **管理員查詢帶有 `trade_history` 的紀錄**：驗證回傳的 `trade_history` 已被遮蔽或統計化處理，而非原始陣列。