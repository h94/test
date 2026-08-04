# 重算交易盈虧

## 1. 場景目的

賽事結束後，由排程或外部服務（`tradegameresultservice`）觸發，重算指定球種（game_type）內所有「尚未結算」的庫存記錄（`stock_holdings_{game_type}`）的盈虧結果（`winloss`），並寫回資料庫。此流程確保使用者的持倉在賽事結果確認後，能正確反映贏（W）、輸（L）、平局（N）或取消（C）的最終狀態。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/recalculate/{game_type}` | 觸發指定球種的交易盈虧重算，由內部服務或排程呼叫，需要內部服務授權驗證。 |

- **Request Body**：需人工確認（目前 OpenAPI 未定義 request body，可能僅依賴路徑參數或內部實作有其他參數）。
- **Response**：需人工確認（目前 OpenAPI 未定義 response schema）。

---

## 3. 流程總覽

1. 接收 `POST /recalculate/{game_type}` 請求，通過內部服務授權驗證（API Key / TCZB Globals）。
2. 解析路徑參數 `game_type`（例如 `BK`、`BS`、`SC`），動態決定目標資料表 `stock_holdings_{game_type}`。
3. 查詢目標表中所有 `winloss` 為 `NULL` 或空字串的記錄（代表尚未結算）。
4. 針對每筆未結算記錄，根據其 `trade_history`（交易歷程）與賽事最終結果（可能從外部服務取得，需人工確認）計算盈虧結果（`W`、`L`、`N`、`C`）。
5. 將計算後的結果更新回記錄的 `winloss` 欄位。
6. 回傳處理結果（成功或失敗統計）。此流程不涉及點數服務（zcoin_api）的呼叫，盈虧結算後的點數處理應由 `tradegameresultservice` 負責（README 描述結算流程寫入 winloss，但未提及點數處理，因此 **點數處理不在本服務重算範圍內**）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `recalculate.py` 的 `recalculate_winloss` (推測) | 接收請求，驗證內部授權，解析 `game_type` 參數。 |
| 2 | Service / Provider | `RecalculateService` / `StockHoldingsProvider` (推測) | 根據 `game_type`，查詢 Cassandra `tradegame` keyspace 的 `stock_holdings_{game_type}` 表，取得所有 `winloss` 為 NULL 或空字串的記錄。 |
| 3 | Service | `RecalculateService` (推測) | 對每筆記錄，解析 `trade_history` 內的買賣記錄，結合賽事結果（來源需確認），計算出最終的 `winloss` 狀態（W, L, N, C）。 |
| 4 | Provider | `StockHoldingsProvider` (推測) | 將計算後的 `winloss` 更新回 Cassandra 的對應記錄。 |
| 5 | Controller | `recalculate.py` | 彙整處理結果並回傳。 |

- **注意**：以上方法名稱為推測，實際需根據程式碼 `webapi/tradegameservice/` 目錄下的檔案確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `tradegame.stock_holdings_{game_type}` | Read | 讀取所有 `winloss` 為空的記錄，取得計算盈虧所需的 `trade_history`、`ratio`、`spread` 等欄位。 |
| DB (Cassandra) | `tradegame.stock_holdings_{game_type}` | Update | 將計算完成的盈虧結果（W/L/N/C）寫入記錄的 `winloss` 欄位。 |
| DB (Cassandra) | `pricecenter.accounts_*` | Read (可選) | 需人工確認：重算流程**不應**涉及帳戶啟用狀態（`enabled`）的檢查，因結算不應因帳戶事後停用而終止。若程式有讀取，應予移除。 |
| Redis | `price:acc:verify:{account}` | 無 | 此快取用於交易前驗證，與結算重算流程**無關**。若帳戶狀態變更，應由帳戶管理服務主動失效。 |
| Queue / Kafka | 無 | - | 文件中未提及此流程使用 Message Queue。 |

- **關鍵限制**：`winloss` 欄位的寫入權限僅限於 `tradegameresultservice` 和此重算流程（`tradegameservice`），其他服務不可直接寫入。

---

## 6. 重要規則

- **權限限制**：API 僅供內部服務（如排程系統）呼叫，需通過 API Key 或內部服務授權驗證。外部使用者不可直接呼叫。
- **欄位限制**：
  - **不可修改欄位**：`account`、`mode_spread_type`、`gdate`、`lid`、`gid` 等主鍵欄位一旦寫入即固定，重算流程**絕不可修改**。
  - **不可暴露資料**：對外回傳時，不應暴露 `trade_history`（非本人查詢）、`account`（對非本人）等敏感或隱私欄位，但此 API 為內部使用，需確認 response 的設計。
- **不可逆規則**：`winloss` 欄位在寫入一個非空的最終值（W/L/N/C）後，**不可再次修改**。重算流程在更新前應檢查此規則，避免覆蓋已結算的記錄。
- **冪等性**：查詢待處理記錄時，必須篩選 `winloss IS NULL OR winloss = ''`，以確保不會重複計算已結算的記錄，保證流程的冪等性。
- **狀態值限制**：寫入的 `winloss` 值必須是預先定義的集合 `{ 'W', 'L', 'N', 'C' }` 之一。
- **Transaction 規則**：Cassandra 不支援跨分區交易。由於重算可能批次大量更新，應實現良好的錯誤處理與日誌，而非追求嚴格的 ACID 交易。單筆更新具有原子性。
- **TTL 規則**：無直接相關的 TTL 規則。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `game_type` 不存在（對應的 Cassandra 表不存在） | 回傳錯誤，例如 400 Bad Request 或 404 Not Found，並記錄錯誤 log。 |
| 內部授權失敗（API Key 無效） | 回傳 401 Unauthorized 或 403 Forbidden。 |
| Cassandra 查詢失敗（DB timeout，連線異常） | 回傳 500 Internal Server Error，記錄詳細錯誤 log，觸發告警。 |
| Cassandra 更新失敗（對已結算記錄嘗試更新） | 可透過輕量級交易（LWT）或更新前檢查來避免，若發生應記錄為邏輯錯誤，並繼續處理其他記錄。 |
| 計算盈虧時發生程式錯誤（如 `trade_history` 格式不符預期） | 記錄該筆記錄的錯誤 log，並繼續處理後續記錄，不應中斷整個批次。處理結果需統計失敗筆數。 |
| `trade_history` 為空或格式錯誤，無法計算盈虧 | 此為異常資料，應記錄為錯誤，並跳過該筆記錄，待人工介入處理。**不可**預設為 W 或 L。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| RT-01 | Flow Test | 對存在多筆未結算記錄（winloss 為 NULL）的球種觸發重算。 | 所有未結算記錄的 `winloss` 被正確更新為 W/L/N/C。 |
| RT-02 | Flow Test | 對所有記錄皆已結算的球種觸發重算。 | 沒有任何記錄被更新，API 回傳成功但更新筆數為 0。 |
| RT-03 | Idempotency Test | 對同一球種連續觸發兩次重算。 | 第二次重算沒有任何記錄被更新（因為都已結算），確保冪等性。 |
| RT-04 | Permission Test | 使用無效或不具備內部服務權限的 API Key 呼叫。 | 回傳 401 或 403 錯誤。 |
| RT-05 | Error Handling | 模擬 Cassandra 查詢失敗。 | API 回傳 500 錯誤。 |
| RT-06 | Error Handling | 模擬 `trade_history` 格式錯誤導致計算失敗。 | 該筆記錄被跳過，API 回傳成功但包含失敗計數，並記錄錯誤 log。 |

---

## 9. 高風險區域

- **高風險 Table**：`tradegame.stock_holdings_BK`, `tradegame.stock_holdings_BS`, `tradegame.stock_holdings_SC`。
  - **原因**：`winloss` 欄位直接影響使用者盈虧，必須確保計算結果100%正確。
- **高風險 API**：`POST /recalculate/{game_type}`
  - **原因**：此 API 將對大量資料進行不可逆的寫入操作。錯誤的呼叫或邏輯可能導致大規模的財務數據錯誤。
- **Cache consistency**：無直接風險，因不依賴快取。
- **Idempotency**：高風險。必須確保重算邏輯不會重複處理已結算的記錄，否則會將 `winloss` 從已確定的最終狀態覆寫為計算中的狀態（儘管規則禁止）。
- **跨服務資料同步**：`winloss` 的最終權威由 `tradegameresultservice` 和此 `tradegameservice` 的重算流程共同寫入。必須嚴格遵守 `winloss` 寫入規則，避免兩個服務同時寫入導致 race condition（Cassandra 的 Last-Write-Wins 特性可能導致問題）。

---

## 10. 常見錯誤

- ❌ 新人容易犯錯：
  - 在查詢未結算記錄時，未過濾 `winloss` 為 `NULL` 或空字串的條件，導致全表掃描。
  - 直接在應用程式碼中寫死表名，未根據 `game_type` 動態組合 `stock_holdings_{game_type}`。
  - 認為重算流程需要驗證使用者帳戶是否啟用（`enabled=1`），但結算應與帳戶當前狀態無關。
- ❌ AI 容易誤解：
  - 誤以為 `POST /recalculate/{game_type}` 的 request body 或 response 的結構，實際上需從程式碼確認。
  - 誤以為此 API 會呼叫點數服務（zcoin_api）來發放或回收點數。（應由 `tradegameresultservice` 負責）。
- ❌ 常見漏檢查項目：
  - 忘記檢查 `game_type` 的有效性，導致企圖查詢不存在的表。
  - 沒有為 Cassandra 查詢設定超時或合理的 fetch size，可能導致大結果集查詢逾時或 OOM。
  - 對 `winloss` 進行 UPDATE 操作時，未在 WHERE 子句中明確加入 `winloss = ''` 或 `winloss IS NULL` 的條件（若使用 Cassandra LWT），無法保證冪等性。
- ❌ 常見錯誤流程：
  - 因 `trade_history` 內容異常而中斷整個批次作業，導致部分記錄未結算。正確做法是捕獲異常、記錄 log，並繼續處理。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /recalculate/{game_type}` |
| API | OpenAPI 文件路徑 `/api/recalculate/{game_type}` (需確認) |
| DB | `tradegame.stock_holdings_BK`, `tradegame.stock_holdings_BS`, `tradegame.stock_holdings_SC` |
| DB detail | `db/tradegame-detail.md` - `winloss` 欄位定義與寫入限制 |
| Service detail | `webapi/tradegameservice/tradegameservice-detail.md` - stock_holdings 寫入限制 |
| README | `webapi/tradegameservice/README.md` - 場景5: 賽事結算後重算盈虧 |
| Code | `webapi/tradegameservice/recalculate.py` (推測) |
| Code | `webapi/tradegameservice/trade.py` (推測，用於了解 stock_holdings 的寫入方式) |