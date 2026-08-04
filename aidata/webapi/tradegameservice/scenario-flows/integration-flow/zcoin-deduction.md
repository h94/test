# 點數扣除/回收

## 1. 場景目的

本場景描述使用者在進行球種賽事交易（買入/賣出）時，tradegameservice 如何透過點數服務 zcoin_api（port 22306）即時扣除或回收對應的點數，並保證交易記錄在 Cassandra `stock_holdings_{game_type}` 表中的完整性與一致性。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/trade/{game_type}` | 新增買入或賣出交易；body 包含 `trade_type`（`buy` / `sell`）、`account`、`lid`、`gdate`、`gid`、`mode`、`oddtype`、`spread`、`stock_num`、`trade_price` 等欄位 |

---

## 3. 流程總覽

1. 接收交易請求，驗證內部服務授權 (TCZB Globals)
2. 透過 Redis 快取 `price:acc:verify:{account}` 驗證帳戶是否存在且啟用；若快取未命中，則查詢 `pricecenter.accounts_{brand}`，過濾 `enabled=1 AND closetime IS NULL`，並寫入快取（TTL 3600s）
3. 根據 `trade_type` 執行買入或賣出邏輯
4. 對 `stock_holdings_{game_type}` 表進行寫入：
   - **買入**：INSERT 新持倉記錄或累加 `stock_num`，將交易記錄 APPEND 至 `trade_history`
   - **賣出**：UPDATE 現有持倉記錄，減少 `stock_num`，並在 `trade_history` 中 APPEND 賣出記錄
5. 呼叫外部服務 `zcoin_api`（`http://zcoin_api:22306`）執行點數扣除（買入）或回收（賣出）
6. 若點數服務呼叫成功，更新 `stock_holdings` 中的交易狀態（必要欄位）；若失敗，進行補償或將交易標記為失敗（具體機制需人工確認）
7. 回傳結果給前端，包含 `profitpoint`（買入時）或回收點數資訊

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | TradeController.post_trade | 解析路徑參數 `game_type` 及 request body，呼叫對應交易服務 |
| 2 | Validator | TradeSchema | 驗證必要參數（`trade_type` 必須為 `buy` 或 `sell`、`stock_num > 0` 等） |
| 3 | Service | TradeService.process_trade | 根據 `trade_type` 分派至買入或賣出處理常式，負責整體流程協調 |
| 4 | Provider | AccountProvider | 查詢 Redis `price:acc:verify:{account}` 或回退查詢 Cassandra `pricecenter.accounts_{brand}`，驗證帳戶啟用狀態 |
| 5 | Provider | StockHoldingsProvider | 對 `tradegame.stock_holdings_{game_type}` 進行讀寫：買入時建立/累加持倉，賣出時查詢並扣減庫存 |
| 6 | Provider | ZcoinClient | 向 `zcoin_api` 發起 HTTP 請求，攜帶帳號、點數數量等進行扣除或回收 |
| 7 | Provider | TradeHistorySerializer | 將最新交易記錄序列化後 APPEND 至 `trade_history` 欄位（賣出時） |
| 8 | Service | TradeService | 根據 `zcoin_api` 回應決定最終交易結果，必要時觸發補償或告警（需人工確認） |
| 9 | Controller | TradeController | 封裝交易結果為 `TradePostResponse` 並回傳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `pricecenter.accounts_{brand}` | Read | 驗證帳戶是否存在、`enabled = 1` 且 `closetime` 為空 |
| DB (Cassandra) | `tradegame.stock_holdings_{game_type}` | Write / Update | 買入時寫入新記錄或累加庫存，賣出時更新 `stock_num` 並擴充 `trade_history` |
| Redis | `price:acc:verify:{account}` | Get / Set | 快取帳戶驗證結果，TTL 3600 秒；miss 時回查 DB 並寫入快取 |
| Redis | `price:acc:verify:{account}` | Delete | 當帳戶狀態變更（如 `enabled` 設為 0）時主動刪除，防止讀取舊狀態 |
| Queue (MQ) | MQService | Publish | 非必選；在點數服務異常或交易失敗時推送告警通知 |

---

## 6. 重要規則

- **權限限制**：僅限持有有效 API Key 的內部服務可呼叫交易 API (TCZB Globals)
- **帳戶狀態驗證**：交易前必須確認帳戶啟用 (`enabled=1`) 且未關閉 (`closetime IS NULL`)；任一不符合即拒絕請求
- **不可修改欄位**：`stock_holdings` 中的 `gdate`, `lid`, `gid`, `account`, `mode_spread_type` 一經 INSERT 即固定，任何服務不得更新
- **Trade History 寫入**：賣出時只能 **APPEND** 新記錄至 `trade_history`，不可覆蓋或刪除舊內容
- **點數服務相依**：扣除/回收點數為同步 HTTP 呼叫；若發生網路異常或逾時可能導致交易狀態不一致，需有補償設計（目前補償機制需人工確認）
- **Redis 快取一致性**：帳戶啟用狀態改變時，必須主動 DEL 對應的 `price:acc:verify:` key，不可只依賴 TTL 自然過期
- **隱私保護**：對外 API 不可回傳 `pricecenter` 的 `password`、`phone`、`handler` 欄位，查詢庫存時非本人需脫敏 `winloss`、`account`

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 帳號不存在或 `enabled=0` / `closetime` 非空 | 拒絕交易，回傳 403 或 422 並說明原因 |
| Redis 快取存在但帳戶已停用（因快取未 DEL） | 不一致狀況；必須確保變更時主動 DEL，否則可能放行交易（高風險） |
| `stock_holdings` 寫入失敗（Cassandra 寫入超時） | 交易立即失敗，不回傳成功，不呼叫 `zcoin_api` |
| `zcoin_api` 呼叫逾時或網路錯誤 | 需人工確認：通常應標記交易失敗，並可能觸發定時對帳與補償；當前無自動回滾 |
| `zcoin_api` 回傳點數不足 | 拒絕交易，回傳餘額不足錯誤 |
| 賣出時庫存數量不足 | 拒絕交易，回傳庫存不足 |
| `zcoin_api` 成功但後續更新 `stock_holdings` 狀態失敗 | 可能導致點數已扣但記錄未成對，需人工確認補償流程（如對帳後手動處理） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC-DEDUCT-01 | API Test | 買入交易，帳戶啟用，點數足夠 | 成功扣除點數，`stock_holdings` 新增記錄，回傳 `profitpoint` |
| TC-DEDUCT-02 | API Test | 賣出交易，庫存足夠 | 成功回收點數，`stock_num` 減少，`trade_history` 增長 |
| TC-DEDUCT-03 | Permission Test | 帳戶已停用 (`enabled=0`) | 拒絕交易，回傳明確錯誤 |
| TC-DEDUCT-04 | Integration Test | 帳戶啟用後因管理員停用，快取未 DEL | 驗證交易能否被攔截；預期最終應拒絕（依賴即時 DEL） |
| TC-DEDUCT-05 | Flow Test | `zcoin_api` 扣除點數逾時 | 交易回傳失敗，`stock_holdings` 未被修改，或標記為異常 |
| TC-DEDUCT-06 | Integration Test | `stock_holdings` 寫入成功，但 `zcoin_api` 失敗 | 確認庫存是否有回滾或補償機制；若無則需人工帳務處理 |
| TC-DEDUCT-07 | API Test | 必要參數缺失（如 `trade_type` 為空） | 回傳 422 錯誤 |
| TC-DEDUCT-08 | API Test | `stock_num` 為 0 或負數 | 回傳 422 錯誤 |

---

## 9. 高風險區域

- **高風險表**：  
  - `tradegame.stock_holdings_{game_type}`（交易庫存核心）  
  - `pricecenter.accounts_{brand}`（帳戶驗證來源）
- **高風險 API**：`POST /api/trade/{game_type}`（同時涉及 DB 寫入與外部點數扣款）
- **跨服務資料同步**：tradegameservice ↔ zcoin_api 的非事務性互動；無 ACID 保障，可能導致部分成功
- **Cache consistency**：Redis `price:acc:verify:{account}` 與實際 DB 狀態脫節風險；若未即時 DEL 會造成停用帳戶仍可交易
- **Idempotency**：交易請求目前是否支援 idempotency key 防止重複扣款？需人工確認實作狀況
- **Queue retry**：告警推送到 MQ 失敗不應阻斷交易，但應記錄日誌

---

## 10. 常見錯誤

- ❌ 驗證帳戶時未檢查 `closetime IS NULL`，導致已關閉帳戶被視為有效
- ❌ 帳戶狀態變更時忘記主動刪除 Redis 快取 `price:acc:verify:{account}`，造成不一致
- ❌ 修改 `stock_holdings` 時直接覆蓋 `stock_num` 或 `trade_history`，破壞併發安全或歷史紀錄
- ❌ 點數服務呼叫失敗後未將交易記錄置為最終失敗狀態，遺留懸空記錄
- ❌ 回傳 payload 中包含 `pricecenter` 的 `handler`、`password` 等敏感欄位
- ❌ 未對 `zcoin_api` 進行異常隔離（如 circuit breaker），導致其故障時拖垮整個交易服務

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 入口 | `POST /api/trade/{game_type}`（OpenAPI tags: trade） |
| DB 驗證規則 | `db/pricecenter-detail.md`（accounts_* 的 enabled、closetime 欄位限制） |
| DB 庫存表 | `db/tradegame-detail.md`（stock_holdings 寫入限制、winloss 權限） |
| Redis 快取 | `price:acc:verify:{account}`（tradegameservice-detail.md 的 Redis 段落） |
| 外部點數服務 | README 服務相依：點數服務 zcoin_api (:22306) |
| 交易流程 | README 常見使用場景 1、2 |

> 註：因未提供完整 source code，部分實作細節（如補償邏輯、idempotency 機制）標記為「需人工確認」。