# 建立新彩票交易訂單

## 1. 場景目的
會員在前台選擇新彩票儲值方案後，PaymentService 建立一筆交易訂單並記錄於 `payment.newlottery_transactions`，接著呼叫下游服務更新會員彩幣錢包餘額，完成儲值流程。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/newlottery/transactions` | 建立新彩票交易訂單 |

---

## 3. 流程總覽

1. 接收交易請求（攜帶 member auth token 與儲值方案 ID）。  
2. 驗證身份與請求參數。  
3. 查詢 `payment.rechargeplans_newlottery` 確認方案有效性（enabled=1，時間範圍內）。  
4. 產生交易主鍵（year、date_time、account、id），並組裝初始狀態（status=0）。  
5. 寫入 `payment.newlottery_transactions`。  
6. 呼叫 **newlotterysite**（或 memberservice，需人工確認）更新彩幣錢包（`newlottery.coinwallet`）與交易記錄。  
7. 收到錢包更新成功回應後，更新 `newlottery_transactions` 狀態為成功（status=1）。  
8. 發送 MQ 通知（如付款成功訊息）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|-----|-------|---------------|------|
| 1 | Controller | `NewLotteryTransactionController.Create` | 接收 request，驗證 token。 |
| 2 | Service | `NewLotteryTransactionService.CreateAsync` | 驗證方案、生成單號、呼叫 Provider 寫入 DB。 |
| 3 | Provider | `NewLotteryTransactionDataProvider.InsertAsync` | 執行 CQL INSERT 至 `payment.newlottery_transactions`。 |
| 4 | Service | `NewLotteryTransactionService` | 呼叫外部服務 API（如 `POST /api/wallet/deposit` on newlotterysite）更新彩幣。 |
| 5 | Provider | `NewLotteryTransactionDataProvider.UpdateStatusAsync` | 更新交易狀態為成功。 |
| 6 | Service | 發送 MQ | 推送 `payment.success` 訊息至 Kafka。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|-----|------|------|------|
| DB (Cassandra) | `payment.rechargeplans_newlottery` | Read | 驗證儲值方案有效性。 |
| DB (Cassandra) | `payment.newlottery_transactions` | Write | 寫入交易訂單初始狀態 (status=0)。 |
| DB (Cassandra) | `payment.newlottery_transactions` | Update | 更新交易狀態為成功 (status=1)。 |
| Redis | `rechargeplans:all:{site}` | GET（可能） | 快取啟用方案清單，若 miss 則查 DB。 |
| Queue (Kafka) | `payment.success` | Publish | 發送付款成功通知。 |
| External API | newlotterysite `POST /api/wallet/deposit` | Call | 更新 `newlottery.coinwallet.Balance` 與寫入 `coinwallet_transactions`。 |

---

## 6. 重要規則

- **權限限制**：必須攜帶有效 member token，且 member 帳號狀態為正常（`gameusers.status=1`），非機器人（`gamerobots.enabled=0`）。  
- **方案驗證**：`rechargeplans_newlottery.enabled=1` 且 `starttime <= now() < endtime`。  
- **交易唯一性**：一組 (year, date_time, account, id) 須唯一，不可重複插入相同主鍵。  
- **狀態流轉**：初始 `status=0`（待處理），僅在錢包成功後更新為 `status=1`（成功）。不可從其他服務直接寫為成功。  
- **不可修改欄位**：`year`、`date_time`、`account`、`id` 寫入後不可變更。  
- **冪等性**：重複相同 id 的請求應返回已存在的交易記錄，避免重複扣款或重複加值（需透過 id 檢查）。  
- **跨服務一致性**：寫入 `newlottery_transactions` 與呼叫錢包 API 不屬於同一事務，需設計補償機制（例如錢包失敗時將交易標記為 failure，或反覆重試）。  
- **敏感資料**：對外 API 不可回傳 `gameusers.password`、`authkey` 等欄位。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|-----|---------|
| 未提供 token 或 token 無效 | HTTP 401 Unauthorized |
| 會員狀態為停用／凍結 | HTTP 403 Forbidden，拒絕建立交易 |
| 方案 id 不存在或已停用 | HTTP 400 Bad Request，回傳方案無效 |
| 當前時間不在方案有效時間範圍內 | HTTP 400 Bad Request |
| 重複提交相同訂單 id | HTTP 409 Conflict，回傳已存在交易紀錄 |
| 寫入 `newlottery_transactions` 時 Cassandra 寫入失敗 | HTTP 500，記錄 log，觸發告警 |
| 呼叫 newlotterysite 更新錢包失敗（逾時或 refused） | 將交易狀態標為失敗（status=2），或進入重試佇列；不可回傳成功 |
| 錢包更新成功但後續狀態更新寫入失敗 | 需人工補單或排程重試，確保最終一致性 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|-----|------|---------|
| NL-TXN-01 | Integration Test | 合法方案、正常會員建立交易，錢包更新成功 | 交易狀態=1，錢包餘額增加對應 coin，交易記錄寫入 coinwallet_transactions |
| NL-TXN-02 | API Test | 缺少 token | 401 |
| NL-TXN-03 | Flow Test | 方案過期 | 400，提示方案不可用 |
| NL-TXN-04 | Permission Test | 使用停用會員 token | 403 |
| NL-TXN-05 | Flow Test | 重複提交相同 id | 409 且任何記錄不會重複，錢包不變 |
| NL-TXN-06 | Flow Test | 錢包更新 API 模擬失敗 | 交易狀態最終為失敗，錢包不變 |
| NL-TXN-07 | Flow Test | Cassandra 寫入失敗 | 500，無任何 side effect |

---

## 9. 高風險區域

- **高風險 Table**：`payment.newlottery_transactions`（交易主體）、`newlottery.coinwallet`（金融餘額）。  
- **高風險 API**：對 newlotterysite 的錢包加值 API，需確認 idempotency key 機制，避免重複加值。  
- **跨服務資料同步**：`newlottery_transactions` 與 `coinwallet_transactions` 須可對帳；任一環節失敗都可能造成帳務不平。  
- **Transaction**：Cassandra 不支援跨表/跨服務 ACID，需透過應用層 saga 或補償處理。  
- **Cache consistency**：若使用 `rechargeplans:all` 快取，方案變更時必須立即清除，避免使用過期方案。  
- **Queue retry**：Kafka 訊息發送失敗可能導致通知遺漏，需保留重試與死信佇列。  
- **Idempotency**：重複請求須辨識並拒絕，避免多次加值。

---

## 10. 常見錯誤

- ❌ 未檢查方案時間範圍即建立交易，導致已過期方案仍可儲值。  
- ❌ 未過濾 `gameusers.status` 與 `gamerobots`，使停用或機器人帳號執行儲值。  
- ❌ 先呼叫錢包再加 DB，錢包成功但 DB 寫入失敗，造成遺失交易記錄。  
- ❌ 錢包更新失敗時仍回傳前端成功，導致用戶金流錯亂。  
- ❌ 交易單號生成邏輯有衝突，使用自增 ID 可能造成跨年度重複，應確保包含時間分區。  
- ❌ 忘記將 `coinwallet` 的 Redis 快取 (`coin_wallet:{Account}`) 失效，導致餘額顯示錯誤。

---

## 11. Evidence

| 類型 | 來源 |
|-----|------|
| API 入口 | README 新彩票金流 POST `/api/v1/newlottery/transactions` |
| 方案驗證規則 | `payment-detail.md` Table `rechargeplans_newlottery` 讀取規則 |
| 交易表結構 | README 列舉 `payment.newlottery_transactions` 欄位（year, date_time, account, id） |
| 寫入限制 | `payment-detail.md` 保護制度（僅由 `NewLotteryTransactionService` 寫入） |
| 錢包表 | `newlottery-detail.md` Table `coinwallet`、`coinwallet_transactions` |
| 跨服務限制 | `newlottery-detail.md` 表示 newlotterysite 可更新 Balance，並須同時寫入 transactions |
| 常見錯誤 | 多組合規中的跨服務寫入限制與 `coinwallet` 餘額操作要求 |
| Redis | `newlottery-detail.md` 中的 `coin_wallet:{Account}` 快取規則 |
| 會員驗證 | `member-detail.md` 中 `gameusers.status` 與 `gamerobots` 過濾邏輯 |
| Code 結構 | Phase0 batch 語意中 `NewLotteryTransactionDataProvider` 存在性 |