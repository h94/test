# 更新訂閱狀態 (Payment Callback)

## 1. 場景目的
支付金流服務（如 ECPay、PaymentService）在確認收到玩家款項後，透過內部 API 回調，更新玩家的訂閱記錄與會員資格。此流程包含新增 `gamesublogs` 記錄、更新 `gameusers.memberships`，以及最終更新 `users.SubEndTime`。

---

## 2. 入口 API
> 本次回調由 `PaymentService` 發起，透過 `MemberModels` 或 `PaymentModels` 定義的內部 Transfer/Service 執行，非前台 OpenAPI。

| Method | Path | 說明 |
|---|---|---|
| POST | 內部回調（由 PaymentService 觸發） | 支付成功後的回調端點，用於更新訂閱 |

---

## 3. 流程總覽
1. 接收支付成功回調請求（含 `authKey`, `SubID`, `SubRank`, ` TradeNo` 等）。
2. 驗證請求來源（Token 或內網 IP）。
3. 查詢 `member.gamesublogs` 過去訂閱記錄。
4. **計算 `subendtime`**：
   - 若為**新訂閱**：以當前時間 + 方案天數計算。
   - 若為**續訂**：以前一筆記錄的 `subendtime` 為起點計算新的到期日。
5. **寫入 `member.gamesublogs`**：插入新的訂閱記錄。
6. **更新 `member.gameusers`**：對 `memberships` 列表進行 `APPEND` 操作，加入新方案。
7. **更新 `stock.users.SubEndTime`**：更新當前最高權限方案的到期日。
8. 回傳成功。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Transfer / Service | `PaymentTransfer.InsertSubLog` | 接收付款資訊，作為流程起點 |
| 2 | Service | `PaymentService` (或 MemberService) | 驗證參數，查詢前次 `gamesublogs` 記錄 |
| 3 | Service | 時間計算邏輯 | 判斷新訂或續訂，計算 `subendtime` |
| 4 | Provider / Service | `GamesubLogProvider.Insert` | 將 `authKey`, `subtime`, `subendtime`, `tradeno` 等寫入 `gamesublogs` |
| 5 | Provider / Service | `GameUserProvider.UpdateMembership` | 對 `gameusers.memberships` 進行 `APPEND`，**不可直接覆寫整個 list** |
| 6 | Provider / Service | `UserProvider.UpdateSubEndTime` | 更新 `stock.users.SubEndTime` |
| 7 | Service | 回調結束 | 回傳 `Success` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `member.gamesublogs` | **Read** | 查詢前次訂閱記錄 (`authkey ORDER BY subtime DESC`) 以利續訂時間計算 |
| DB (Cassandra) | `member.gamesublogs` | **Write (Insert)** | 新增本次訂單記錄 (`authkey, subtime, tradeno, autosub, subendtime...`) |
| DB (Cassandra) | `member.gameusers` | **Update (Append)** | 更新 `memberships` list，加入新方案代號 |
| DB (MySQL) | `stock.users` | **Update** | 更新 `SubEndTime` 為最新的最高方案到期日 |
| Queue / Kafka | — | 無直接使用 | 後續可能觸發 `NotificationService` 發送訂閱成功通知 |

---

## 6. 重要規則
- **權限限制**：僅支付回調服務有權限寫入 `gamesublogs` 和更新 `gameusers.memberships`。前台不可直接更新此欄位。
- **memberships 不可直接替換 (REPLACE)**：對 `gameusers.memberships` 必須使用 `APPEND` 語法。直接 `UPDATE SET memberships = [...]` 會清空其他服務寫入的資格。
- **續訂時間計算**：續訂時必須讀取前次 `subendtime`，**不能**直接拿當前時間計算，以免造成會員有效期損失。
- **SubEndTime 更新**：若使用者購買了較高層級的方案，`stock.users.SubEndTime` 需更新為該方案的結束時間；若為低層級續訂，則邏輯上通常保持原有較晚的到期日（需人工確認具體比對規則）。
- **不可暴露資料**：回傳或 log 中不可輸出原始的 `tradeno`。
- **autosub 標記**：定期定額扣款訂單 (`autosub=true`) 用於判斷自動續訂。一次性購買設為 `false`。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `authKey` 不存在於 `member.gameusers` | 回拋錯誤，回調失敗，需人工檢查或退費 |
| 查詢前次 `gamesublogs` 時發生 Timeout | 重試或記錄錯誤，不可擅自帶入當前時間算到期日 |
| 寫入 `gamesublogs` 失敗（Cassandra 不可用）| 調用方需重試，確保記錄不丟失 |
| 更新 `gameusers.memberships` 時因為 APPEND 衝突失敗 | 重試機制 |
| 支付回調重複發送（相同 `tradeno`） | `gamesublogs` 應有冪等性（主鍵包含 tradeno/addtime）；回傳成功，不可重複發放權益 |
| 欲寫入的 `membership` 格式不符合 `list<text>` | 嚴格驗證格式，阻止寫入 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SUB-01 | Flow Test | 新用戶首次訂閱 | `gamesublogs` 新增一筆，到期日為現在+方案天數；`memberships` 包含該方案；`SubEndTime` 正確 |
| SUB-02 | Flow Test | 老用戶續訂（前次未過期） | 到期日 = 前次到期日 + 方案天數；`memberships` 正確累加 |
| SUB-03 | Flow Test | 老用戶續訂（前次已過期） | 到期日 = 現在 + 方案天數 |
| SUB-04 | Permission Test | 前台 API 嘗試直接寫入 `memberships` | 無法寫入，回傳 403 或無此操作 |
| SUB-05 | Error Test | 帶入不存在的 `authKey` | 返回 User Not Found 錯誤 |
| SUB-06 | Idempotent Test | 重複發送相同 `TradeNo` 的回調 | 第二次回傳成功，但 `memberships` 不重複 Append，`SubEndTime` 不變 |

---

## 9. 高風險區域
- **續訂時間計算**：`subendtime = Max(前次subendtime, 現在) + 方案天數` 的邏輯若寫錯，會導致 VIP 用戶提前過期，引發大量客訴。
- **Cache Consistency**：`gameusers` 資料可能在 Redis 有快取（如 `GameUser:{authkey}`），更新 `memberships` 後必須確認快取已清除，否則前台會員狀態不會立即更新。
- **Transaction**：Cassandra 與 MySQL (stock.users) 不在同一個交易中。若 `gamesublogs` 寫入成功但 `stock.users.SubEndTime` 更新失敗，可能導致 stock 側功能（如選股通知）判斷錯誤。需人工確認補償機制。
- **Cassandra List Append**：Cassandra 的 list append 在 Concurrent 寫入時可能不如預期，雖然付費場景不太會同時發生，但仍需注意。

---

## 10. 常見錯誤
- ❌ 前端直接將 `memberships` 當作一般欄位進行 `REPLACE` 操作。
- ❌ 在計算續訂時間時，拿當前時間 (`NOW()`) 而非前次 `subendtime` 當作起始點。
- ❌ 忘記設定 `autosub` 的 `true/false`，導致定期定額扣款失敗。
- ❌ 回調日誌中輸出了完整的 `TradeNo` 或 `paymethod`。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB Schema | `member.gamesublogs`、`member.gameusers`、`stock.users` |
| Code Boundary | `pricecentersite-detail.md` - 寫入限制：`gameusers.memberships ... 不可直接修改`、`gamesublogs.subendtime ... 續訂時需比對前次記錄` |
| Code Boundary | `stock-detail.md` - 寫入限制：`users.SubEndTime ... 僅付款成功後由訂閱服務寫入` |
| Code Implementation | `MemberModels 1.1.9` (PaymentTransfer) |
| Process | 支付回調邏輯推導自 `PaymentService` 與 `MemberService` 邊界 |