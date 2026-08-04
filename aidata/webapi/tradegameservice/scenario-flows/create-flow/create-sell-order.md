# 場景：建立賣出交易 (Sell Order)

## 1. 場景目的
使用者針對已持有的倉位進行平倉。系統需驗證庫存充足後，更新 `stock_holdings_{game_type}` 表中的 `stock_num` 與 `trade_history`，並呼叫外部點數服務（zcoin_api）回收對應的資金（profitpoint）。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/trade/{game_type}` | 交易操作的主要端點。Request body 中 `trade_type` 需設為 `sell`。 |

---

## 3. 流程總覽

1. 接收前端 `trade_type=sell` 的請求。
2. 驗證 API 內部授權（TCZB Globals）。
3. 從 Redis 快取驗證帳戶是否存在且啟用（`enabled=1`）；若無快取則查詢 Cassandra `pricecenter.accounts_*`。
4. 根據請求的 `gdate`, `lid`, `gid`, `account`, `mode_spread_type` 查詢庫存，確認 `stock_num` 足夠賣出。
5. 執行庫存更新：減少 `stock_num`，並將此筆交易資訊附加至 `trade_history`。
6. 呼叫點數服務 `zcoin_api` 回收點數（profitpoint）。
7. 回傳交易結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `TradeController.add_trade` | 接收並解析 `AddTradeBodyArgs`。 |
| 2 | Validator | `TradeSchema` | 驗證 `trade_type`, `stock_num`, `game_type` 等欄位格式。 |
| 3 | Service | `TradeService.execute_sell` | 協調驗證、庫存更新、點數回收的主流程。 |
| 4 | Provider | `AccountProvider` | 查詢 Redis `price:acc:verify:{account}` 或 Cassandra 以確認帳戶狀態。 |
| 5 | Provider | `StockProvider` | 讀取當前庫存，執行 `stock_num` 與 `trade_history` 的原子化更新。 |
| 6 | Provider | `ZCoinProvider` | 建構點數回收的 request body，呼叫 `zcoin_api`。 |
| 7 | Service | `LogService` | 非同步寫入 `trade_log`（append-only）供稽核。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | `price:acc:verify:{account}` | Read | 驗證帳號狀態（`enabled=1`），TTL 3600秒。 |
| Cache Miss | `pricecenter.accounts_*` | Read | 查詢帳戶的 `enabled` 與 `closetime`。 |
| DB | `tradegame.stock_holdings_{game_type}` | Read | 查詢當前 `stock_num` 以確認可賣出數量。 |
| DB | `tradegame.stock_holdings_{game_type}` | Write | 更新 `stock_num`（扣除）與 `trade_history`（追加）。 |
| Queue | MQService | Publish | 交易失敗或點數回收異常時，發送告警訊息。 |

---

## 6. 重要規則

- **權限限制**：交易僅能由請求中 `account` 欄位的擁有者發起。需透過 Token 確認身份。
- **不可變更欄位**：`stock_holdings` 表中的 `gdate`, `lid`, `gid`, `account`, `mode_spread_type` 一旦建立即固定，本次流程絕不更新。
- **庫存驗證**：賣出數量不可大於當前 `stock_num`。若庫存不足，應直接拒絕，返回明確錯誤代碼。
- **交易歷史**：`trade_history` 僅允許 `APPEND` 操作，不可覆蓋或刪除舊記錄。
- **帳戶狀態**：`closetime` 非空或 `enabled=0` 的帳戶不得進行交易。所有查詢都必須檢查 `enabled=1`。
- **外部點數服務**：呼叫 `zcoin_api` 為同步關鍵路徑。若回收失敗，必須中斷流程並發送 MQ 告警，不應在 DB 留下成功的交易記錄（需人工確認是否實施本地補償或回滾）。
- **不可回傳欄位**：API 回傳嚴禁包含 `accounts_*.password`, `accounts_*.phone`, `handler` 等敏感欄位。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求的 `account` 在快取與資料庫中皆不存在 | 返回 4xx 錯誤，提示帳號不存在。 |
| 帳號 `enabled=0` 或 `closetime` 非空 | 返回 4xx 錯誤，提示帳號已停用或關閉，拒絕交易。 |
| 庫存 `stock_num` 小於賣出的 `stock_num` | 返回 4xx 錯誤，提示庫存不足。 |
| 對同一筆資料進行併發賣出時庫存衝突 | 由於 Cassandra 的最終寫入特性，可能導致 `stock_num` 變為負數。需在更新時使用 `IF stock_num >= ?` 的輕量級交易（LWT）條件。若條件不符，更新失敗，交易中止。（*需人工確認是否實作 LWT*）。 |
| 呼叫 `zcoin_api` 因網路超時或服務內部錯誤失敗 | 返回 5xx 錯誤。停止流程，確保 DB 內的 `stock_num` 未被扣除，並向 MQService 推送告警。 |
| Cassandra 執行庫存寫入時發生 timeout | 返回 5xx 錯誤，提示系統忙碌，請稍後重試。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC-SELL-01 | Flow Test | 正常賣出部分庫存 | `stock_num` 正確減少，`trade_history` 長度增加，API 返回成功。 |
| TC-SELL-02 | Flow Test | 賣出全部庫存（平倉） | `stock_num` 歸零，`trade_history` 記錄完整，`zcoin_api` 被呼叫。 |
| TC-SELL-03 | API Test | `trade_type` 非 `sell` | 應由驗證層拒絕，返回 422 錯誤。 |
| TC-SELL-04 | API Test | 賣出數量超過 `stock_num` | 應返回 4xx「庫存不足」錯誤，DB 資料無變化。 |
| TC-SELL-05 | API Test | 不帶 Token 或 Token 與 account 不符 | 應返回 401/403 認證授權錯誤。 |
| TC-SELL-06 | Integration Test | 模擬 `zcoin_api` 回傳失敗 | 應返回 5xx 錯誤，且不應更動 `stock_num`。 |
| TC-SELL-07 | Permission Test | 查詢已停用帳戶 (`enabled=0`) | 應直接拒絕交易。 |

---

## 9. 高風險區域

- **庫存一致性**：因 Cassandra 分散式特性，併發的賣出請求可能導致超賣。必須依賴於服務層的漏桶或鎖機制，或底層的 LWT（輕量級交易）來確保 `stock_num >= 0`。
- **分散式交易**：DB（`stock_holdings`）與外部服務（`zcoin_api`）之間的寫入無法在原生 Cassandra 驅動下保持強一致性。若 `zcoin_api` 呼叫失敗，需確保 DB 變更已成功回滾，或擁有可靠的補償機制。
- **帳戶狀態快取**：若帳戶被封鎖或停用（`enabled=0`），但 Redis 快取（`price:acc:verify:{account}`）未被主動刪除（DEL），可能導致用戶在 TTL 過期前仍可通過驗證。
- **API 濫用**：賣出端點需實作速率限制（Rate Limiting），防止有心人士透過大量平倉請求探查系統，或嘗試對系統進行重放攻擊（應檢查 idempotency key）。

---

## 10. 常見錯誤

- **新人或 AI 容易直接使用 `UPDATE ... SET stock_num = ?` 而沒有帶 `WHERE stock_num >= ?` 的條件檢查**，導致超賣。
- **誤解 `zcoin_api` 的資金流向**：賣出應該是呼叫回收/增加點數的 API（通常為正數請求），而非扣除點數的 API。文件中「回收點數」的語意需釐清。
- **忘記非同步的 MQ 告警**：直接回傳錯誤給前端而沒有記錄，導致排錯困難。
- **忽略庫存查詢的 PK**：查詢庫存時未使用完整的 `gdate = ? AND lid = ? AND gid = ? AND account = ? AND mode_spread_type = ?`，試圖使用 `ALLOW FILTERING`，造成效能瓶頸。
- **更新 `trade_history` 時覆蓋舊資料**：應該使用 Cassandra 的 `list` 或 `map` 操作，或應用層讀取後合併再寫回（需配合 LWT），單純的 `SET` 指令會導致歷史記錄丟失。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 端點 | `README.md` / OpenAPI 路徑 `/api/trade/{game_type}` |
| Request Schema | OpenAPI `AddTradeBodyArgs` 組件 |
| DB 表結構 | `tradegame.md` 中 `stock_holdings_*` 表的定義 |
| DB 寫入限制 | `tradegameservice-detail.md` 中“寫入限制”一節 |
| 帳戶驗證 Redis Key | `tradegameservice-detail.md` 中 “Redis” 一節的 `price:acc:verify:{account}` |
| 帳戶狀態查詢 | `pricecenter-detail.md` 中 `accounts_*` 表的 `enabled` 欄位操作規則 |
| 外部服務 | `README.md` 中 “服務相依” 的 `zcoin_api` |