# 建立競猜下注

## 1. 場景目的

使用者選擇賽事進行競猜下注，系統驗證帳戶有效性、會員狀態與錢包餘額，成功後寫入下注記錄並呼叫外部服務完成扣點。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/bets/{gameType}` | 建立指定遊戲類型的競猜下注，需在 Request Body 傳入 `PredictBet` 陣列 |

---

## 3. 流程總覽

1. 接收請求，從 Token 解析使用者帳號與站點 (site)。
2. 至 `pricecenter.accounts_{site}` 以 `account` 查詢，確認 `enabled = 1` 且 `closetime` 為空。
3. 向 `memberservice` 取得使用者的 `authkey`，再查詢 `member.gameusers`，驗證 `status = 1`（啟用）。
4. 讀取 `predict.betpool_games`，確認目標賽事 `status = 0`（開放）、`starttime <= now < endtime`、`payout = false`。
5. 必要時檢查會員 VIP 資格（透過 `member.gamesublogs.subendtime` 比對），若賽事為 `viponly = true` 則拒絕非 VIP。
6. 向 `memberservice` 查詢錢包餘額，確保足以支付下注金額。
7. 寫入 `predict.betpool_bets`（INSERT），包含 `gid`、`account`、`betoption`、`betzcoin`。
8. 呼叫 `memberservice` 或 `TransactionService` 執行扣點。
9. 回傳成功或失敗。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `BetController.Post(gameType, bets)` | 接收參數，轉送服務層 |
| 2 | Service | `BetService.PlaceBetAsync(gameType, bets)` | 流程編排、權限檢查、調用各 Provider |
| 3 | Provider | `AccountValidator` | 讀取 `pricecenter.accounts_{site}`，確認 `enabled=1` 且 `closetime` NULL |
| 4 | Provider | `MemberProvider` | 調用 Member 相關 API 取得 `authkey`，查詢 `gameusers.status` |
| 5 | Provider | `GameValidator` | 讀取 `predict.betpool_games`，驗證遊戲可下注 |
| 6 | Provider | `WalletCheckProvider` | 調用 `memberservice` 取得錢包餘額 |
| 7 | Provider | `BetWriter` | 對 `predict.betpool_bets` 執行 INSERT |
| 8 | Provider | `PointDeductionProvider` | 呼叫外部金流服務扣點 |
| 9 | Service | 組合結果回傳 | 若全部成功回 200，否則依錯誤類型回對應狀態碼 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `pricecenter.accounts_{site}` | Read | 驗證帳號啟用狀態 |
| DB | `member.gameusers` | Read | 驗證會員帳號狀態 (`status=1`) |
| DB | `member.gamesublogs` | Read | 判斷 VIP 資格（若遊戲為 VIP 專屬） |
| DB | `predict.betpool_games` | Read | 驗證賽事開放、時間與派彩狀態 |
| DB | `predict.betpool_bets` | Write (INSERT) | 寫入下注記錄 |
| Redis | `GameUser:{authkey}` | Read | 可能用於快取使用者狀態（需人工確認是否在此流程使用） |
| Queue | 未提及 | - | - |

---

## 6. 重要規則

- **權限限制**：僅已登入使用者可呼叫；帳號 `enabled=1` 且 `closetime` 為空；`gameusers.status` 須為 1（啟用）。
- **欄位限制**：`betzcoin`、`betoption` 僅於 INSERT 時寫入，後續不可修改。
- **不可暴露資料**：API 回傳絕對不可包含 `password`、`email`、`authkey`、`phone` 等敏感欄位。
- **Transaction 規則**：下注記錄寫入與扣點應視為一個邏輯單元。若扣點失敗需補償（例如刪除已寫入的 `betpool_bets` 記錄，或標記為無效），避免金流不一致。
- **Idempotency**：應防止相同 bet id 重複寫入，避免重複扣點。
- **狀態值限制**：`betpool_games.status` 必須為 0，`payout` 必須為 false；`starttime <= now < endtime`（以 UTC 時間戳比較）。
- **不可修改欄位**：`betpool_games.starttime`、`endtime` 建立後不可變更；`betpool_bets.betzcoin` 不可更新。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 帳號不存在或 `enabled=0` / `closetime` 非空 | 回傳 403 或帳號無效提示 |
| `gameusers.status` 不為 1（停用／凍結） | 回傳 403 或帳號停用提示 |
| 目標賽事不存在或 `status != 0` | 回傳 400，遊戲不可下注 |
| 當前時間不在 `starttime` 與 `endtime` 之間 | 回傳 400，不在下注區間 |
| 遊戲 `payout = true` | 回傳 400，遊戲已結算 |
| 賽事標記 `viponly = true` 且使用者非 VIP | 回傳 403，需 VIP 才能參與 |
| 錢包餘額不足 | 回傳 400，餘額不足 |
| Cassandra 寫入失敗 | 回傳 500，記錄錯誤並觸發補償 |
| 外部扣點服務失敗（逾時或執行錯誤） | 回傳 500，確保未寫入 `betpool_bets` 或已標記無效 |
| 重複送出相同下注內容 | 回傳 409 或忽略重複（需人工確認機制） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| BET-001 | API Test | 正常下注，提供合法 gid、option、金額 | 200，記錄寫入 `betpool_bets`，扣點成功 |
| BET-002 | Permission Test | 未帶 token 請求 | 401 |
| BET-003 | Permission Test | 帳號 `enabled=0` | 403 |
| BET-004 | Permission Test | 帳號 `status=2`（凍結） | 403 |
| BET-005 | Flow Test | 遊戲 `status=1`（關閉） | 400 |
| BET-006 | Flow Test | 遊戲 `payout=true`（已派彩） | 400 |
| BET-007 | Flow Test | 當前時間 > endtime | 400 |
| BET-008 | Flow Test | VIP 遊戲，使用者非 VIP | 403 |
| BET-009 | Flow Test | 餘額不足 | 400 |
| BET-010 | Integration Test | 同時多筆下注，金額接近餘額 | 無超賣，餘額一致性正確 |
| BET-011 | Error Handling | 扣點服務返回失敗 | 500，`betpool_bets` 無記錄或已標記無效 |
| BET-012 | Idempotency | 相同 bet id 重複請求 | 409 或忽略，不重複扣點 |

---

## 9. 高風險區域

- **高風險 table**：`predict.betpool_bets`（高併發寫入）、`member.gameusers`（狀態驗證）、`pricecenter.accounts_{site}`（帳號啟用查詢）。
- **高風險 API**：`POST /api/v1/bets/{gameType}`，高流量下須確保餘額檢核與寫入的原子性，避免超賣。
- **跨服務資料同步**：下注記錄寫入與外部扣點不在同一服務，需設計重試與補償機制（如 Saga），避免帳務不一致。
- **Transaction**：需訂定分散式交易邊界，扣點失敗後必須回滾（或標記）`betpool_bets`。
- **Cache consistency**：若 `betpool_games` 狀態快取（如 `predict:game:{gid}:status`），在遊戲關閉或結果變更時需立即清除，防止過期快取造成不該有的下注。
- **Queue retry**：若扣點失敗進入重試佇列，需確保冪等性，避免重複扣款。
- **Idempotency**：客戶端重試或網路抖動可能導致相同請求重複送達，需設計去重機制。

---

## 10. 常見錯誤

- ❌ **新人**：只檢查 `member.gameusers.status` 而忽略 `pricecenter.accounts_{site}.enabled` 或 `closetime`，導致已關閉站台帳號仍可下注。
- ❌ **AI**：誤以為 predictservice 會直接操作使用者錢包進行扣點，實際上應由 memberservice 或金流服務負責。
- ❌ **常見漏檢查**：忘記驗證 `betpool_games.payout` 或 `starttime/endtime`，允許對已結束比賽下注。
- ❌ **常見錯誤流程**：扣點失敗後未清除 `betpool_bets` 記錄，導致使用者被扣款但無下注記錄，或相反。
- ❌ **忘記過濾 VIP 遊戲**：非 VIP 使用者成功下注 VIP 賽事，違反商業規則。
- ❌ **對外 API 回傳時未遮蔽其他帳戶的 account**，洩漏隱私。
- ❌ **誤解 `closetime` 意義**，僅檢查 `enabled=1` 而忽略 `closetime` 非空，導致已關閉帳號仍通過驗證。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README: `POST /api/v1/bets/{gameType}` （建立競猜下注） |
| DB | `predict.betpool_bets`（記錄下注）、`predict.betpool_games`（驗證遊戲狀態） |
| DB | `member.gameusers`（驗證會員狀態）、`pricecenter.accounts_{brand}`（驗證帳號啟用） |
| DB | `member.gamesublogs`（VIP 資格檢查） |
| 流程 | README 常見場景：「會員競猜下注」→ 驗證錢包餘額 → 扣點 → 寫入 Cassandra |
| 服務邊界 | predictservice-detail.md：不負責彩金派發，僅計算 profitpoint/ profitzcoin |
| Redis | `GameUser:{authkey}` 可能用於快取使用者狀態（文件建議 TTL 5-10 分鐘） |
| 規則 | predict-detail.md：`betpool_games.status` 僅可由結算流程變更為 2，`starttime/endtime` 不可修改 |
| 規則 | predict-detail.md：`betpool_bets.betzcoin` 僅於下注時寫入，後續不可更新 |
| 規則 | pricecenter-detail.md：讀取 `accounts_{brand}` 須檢查 `enabled=1` 且 `closetime` 為空 |
| 規則 | member-detail.md：驗證 `gameusers.status` 須為 1，且不可回傳 `password`、`email`、`authkey` |

> **需人工確認**：目前缺少具體的扣點 API 合約與分散式交易實作細節（如 Saga 或補償步驟），同時流程中是否使用 Redis 快取使用者狀態也需開發團隊確認。建議補充相關程式碼或服務間 API 定義以完善文件。