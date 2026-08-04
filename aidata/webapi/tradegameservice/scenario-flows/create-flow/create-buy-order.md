# 場景：建立買入交易

## 1. 場景目的
使用者在前端選定賽事盤口並下注（trade_type=buy），系統驗證帳戶啟用狀態後，寫入股票持倉表並呼叫外部點數服務扣款，最後回傳利潤點數。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/trade/{game_type}` | 新增交易。game_type 對應 Cassandra 表名後綴（如 SC、BK、BS） |

---

## 3. 流程總覽
1. 接收 POST 請求，包含 account、lid、gdate、gid、mode、oddtype、spread、stock_num、trade_price 等參數
2. 驗證帳戶啟用狀態：優先查 Redis，miss 則查 pricecenter 並回寫快取
3. 驗證盤口資料有效性
4. 計算 profitpoint
5. 寫入 `stock_holdings_{game_type}` 表（買入交易）
6. 呼叫外部 zcoin_api 扣除點數
7. 回傳 profitpoint

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | trade.TradeAPI.post | 解析路徑參數 game_type，呼叫 Service |
| 2 | Service | TradeService.add_trade | 協調驗證、計算、寫入、外部扣點 |
| 3 | Provider | AccountProvider.verify_account | 檢查 Redis `price:acc:verify:{account}`，miss 則查 Cassandra pricecenter.accounts_* |
| 4 | Provider | TradeProvider.insert_stock_holdings | INSERT INTO tradegame.stock_holdings_{game_type} |
| 5 | External | zcoin_api | 扣點 HTTP 請求（:22306） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Redis | `price:acc:verify:{account}` | GET → SET | 驗證帳戶是否存在且 enabled=1。TTL 3600 秒 |
| DB | pricecenter.accounts_AU8 / accounts_Fortuna888 / ... | Read | 查詢帳戶狀態（SELECT WHERE account=? AND enabled=1） |
| DB | tradegame.stock_holdings_{game_type} | Write (INSERT) | 買入交易寫入新持倉記錄 |
| DB | tradegame.stock_holdings_{game_type} | Read | 檢查是否已存在相同持倉（需人工確認） |
| External | zcoin_api (HTTP /:22306) | 扣點請求 | 扣除用戶下注點數 |

---

## 6. 重要規則

- **權限限制**：僅啟用帳戶（enabled=1 且 closetime 為空）可交易；使用者不可交易他人帳戶
- **帳戶驗證**：必須過濾 `enabled=1 AND (closetime IS NULL OR closetime = '')`，否則拒絕交易
- **欄位不可變更**：stock_holdings 的 gdate、lid、gid、account、mode_spread_type 一旦寫入，不可修改
- **敏感欄位不可暴露**：password、handler 不可回傳；phone 需脫敏
- **僅允許 append**：trade_history 只能追加，不可覆蓋
- **快取規則**：帳戶驗證快取 TTL 3600 秒；帳戶狀態變更時需主動 DEL
- **跨服務寫入限制**：winloss 僅 tradegameresultservice 可寫入；stock_num 僅 tradegameservice 可變更
- **本服務不負責**：會員登入認證（member-service）、錢包資金實際轉帳（wallet-service）、第三方遊戲商帳號管理

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 帳號不存在 | 回傳錯誤（帳號無效） |
| enabled=0 或 closetime 非空 | 回傳錯誤（帳號已停用/關閉） |
| 缺少必要參數（lid, gid, account 等） | 422 Validation Error |
| Redis 不可用 | 降級查 Cassandra，不阻斷交易 |
| Cassandra 寫入 timeout | 回傳 500，交易失敗 |
| zcoin_api 扣點失敗 | 回傳錯誤，stock_holdings 不應寫入成功（需人工確認當前是否使用交易補償機制） |
| 同一持倉重複買入 | 需人工確認（當前邏輯為 INSERT 新記錄或更新 stock_num） |
| 盤口資料不存在 | 拒絕交易，回傳錯誤 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | API Test | 正常買入請求 | 200，回傳 profitpoint |
| T02 | API Test | 缺少 account | 422 |
| T03 | Permission Test | account 停用 (enabled=0) | 拒絕交易 |
| T04 | Permission Test | account 關閉 (closetime 非空) | 拒絕交易 |
| T05 | Flow Test | Redis 快取命中 | 不查 Cassandra，交易成功 |
| T06 | Flow Test | Redis miss，查 Cassandra 成功 | 寫入快取，交易成功 |
| T07 | Integration Test | Cassandra 寫入成功，zcoin_api 正常 | stock_holdings 新增記錄，點數扣除 |
| T08 | Integration Test | zcoin_api 呼叫失敗 | 回傳錯誤，確認 stock_holdings 狀態 |

---

## 9. 高風險區域

- **高風險 table**：stock_holdings_{game_type}（直接影響庫存和盈虧計算）
- **高風險 API**：POST /api/trade/{game_type}（涉及金流）
- **外部服務依賴**：zcoin_api（扣點失敗可能導致庫存與點數不一致）
- **快取一致性**：`price:acc:verify:{account}` 若未在帳戶停用時清除，已停用帳戶可能繼續交易
- **Idempotency**：需確認前端重複提交相同交易是否會建立重複持倉
- **跨服務寫入衝突**：tradegameservice 若誤寫 winloss，會與 tradegameresultservice 結算邏輯衝突

---

## 10. 常見錯誤

- ❌ 交易前未過濾 `enabled=1` 和 `closetime`，導致已停用/關閉帳戶仍可下注
- ❌ 直接回傳 password、handler、完整 phone 給前端
- ❌ 交易 API 試圖直接 UPDATE stock_holdings 的 winloss
- ❌ 帳戶停用後未主動 DEL Redis 快取，導致舊狀態殘留
- ❌ Cassandra 查詢未提供 gdate（分區鍵），觸發全表掃描
- ❌ 將 `mode_spread_type` 寫入後再嘗試拆分修改

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI POST `/api/trade/{game_type}` |
| API Description | README "交易操作" |
| DB Table | tradegame.stock_holdings_BK / BS / SC |
| DB Rules | tradegame-detail "stock_num 欄位"、"winloss 欄位" |
| Account Verification | tradegameservice-detail Redis `price:acc:verify:{account}` |
| Account Verification | tradegameservice-detail "交易時查詢使用者帳戶需過濾 enabled=1" |
| Unchangeable Fields | tradegame-detail mode_spread_type、gdate、lid、gid、account |
| External Dependency | README "點數服務 zcoin_api（:22306）" |
| Auth Responsibility | tradegameservice-detail "本服務不負責" |