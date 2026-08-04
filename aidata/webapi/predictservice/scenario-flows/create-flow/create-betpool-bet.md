# 场景名稱：獎池下注 (BetPool Place Bet)

## 1. 場景目的
使用者在前端選擇一個正在進行中的獎池賽事，選定一個預測選項並支付指定數量的 Z 幣進行下注。系統需完成使用者身份及狀態驗證、獎池遊戲狀態/時間/權限檢查、餘額扣款，並最終生成一條下注記錄。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/betpool/games/{id}/bets` | 建立獎池下注 |

需驗證：✅

---

## 3. 流程總覽

1. 前端呼叫 API，傳入 `{id}` (遊戲 ID) 及 Request Body (含 `betoption`, `betzcoin` 等)
2. 從 JWT 或認證 Header 中解析當前使用者 (`account`, `site` 等)
3. 驗證使用者狀態：透過 `member.gameusers` 檢查 `status` 是否為 1 (已啟用)，並確認未被封禁
4. 讀取 `predict.betpool_games`，以遊戲 `id` 查詢
5. 驗證遊戲狀態：`status` 必須為 0 (開放中)，`starttime <= now < endtime`
6. 檢查 VIP 限制：若遊戲 `viponly = true`，則檢查使用者是否具有有效 VIP 資格 (`memberships` + `gamesublogs`)
7. 驗證下注內容：檢查 `betoption` 是否存在於遊戲的 `betoptions map` 中，`betzcoin` 需等於 `zcoinprice`
8. 呼叫 `memberservice` 檢查使用者 Z 幣餘額是否足夠
9. 呼叫 `memberservice` (或 `TransactionService`) 扣減對應的 Z 幣 (`betzcoin`)
10. 生成唯一的投注 ID (`id`)，寫入 `predict.betpool_bets` 記錄 (`gid`, `account`, `id`, `betoption`, `betzcoin` 等)
11. 回傳成功結果

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `BetPoolController.CreateBet` | 接收請求，調用 Service |
| 2 | Service | `BetPoolService.CreateBet` | 組合業務邏輯，驗證與檢查 |
| 3 | Provider | `UserValidationProvider` (概念) | 根據 `account` 查詢 `member.gameusers`，驗證 `status=1` 且未被封禁 |
| 4 | Provider | `BetPoolProvider` | 從 `predict.betpool_games` 讀取單一遊戲資訊 |
| 5 | Service | `BetPoolService.CreateBet` | 驗證遊戲狀態、時間、VIP 限制、下注選項與金額 |
| 6 | Service | `BetPoolService.CreateBet` | 向 `memberservice` 發起餘額查詢與扣款請求 |
| 7 | Provider | `BetPoolProvider` | 生成 `id`，INSERT 一筆記錄至 `predict.betpool_bets` |
| 8 | Service | `BetPoolService.CreateBet` | 組合回應資訊 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `member.gameusers` | Read | 查詢使用者狀態 (`status`)、會員資格 (`memberships`) |
| DB | `member.gameusers_banned` | Read | 檢查帳號是否處於封禁狀態 |
| DB | `member.gamesublogs` | Read | (若為 VIP 遊戲) 驗證付費會員資格是否有效 (`subendtime`) |
| DB | `predict.betpool_games` | Read | 讀取遊戲規則、狀態、時間、選項、價格 |
| DB | `predict.betpool_bets` | Write | 寫入一條新的下注記錄 |
| Redis | `GameUser:{authkey}` | Get | (可選) 高頻場景下，快取使用者狀態與會員資格，避免反覆查 DB |
| Redis | `predict:game:{gid}:status` | Get | (可選) 查詢遊戲狀態快取，降低對 `betpool_games` 的直接讀取壓力 |

---

## 6. 重要規則

- **權限限制**：所有請求必須包含有效的存取權杖；API 需驗證使用者身份。
- **遊戲狀態**：下注僅允許在 `predict.betpool_games` 的 `status = 0` 且當前時間在 `[starttime, endtime)` 區間時進行。
- **VIP 限制**：若遊戲的 `viponly = true`，則使用者必須具有有效的 VIP 會員資格方可下注。
- **下注金額**：`betzcoin` 必須與 `betpool_games.zcoinprice` 完全一致。
- **選項有效性**：`betoption` 必須是 `betpool_games.betoptions` 中的一個有效 Key。
- **不可修改**：`betpool_bets` 中的 `betzcoin`, `betoption` 寫入後終生不可修改。
- **餘額檢查**：下注前必須確保使用者錢包有足夠的 Z 幣。
- **不可暴露欄位**：對外 API 回傳下注清單時，若非本人查詢，不可回傳他人的 `account` 和 `id`。
- **不可回傳敏感資訊**：任何 API 回傳皆不可包含 `member.gameusers.password`、`email`、`authkey`。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 帳號不存在或已被停用/凍結 (`status != 1`) | 拒絕下注，回傳 403 Forbidden 或對應業務錯誤碼 |
| 遊戲不存在 (`betpool_games` 無對應 `id`) | 回傳 404 Not Found |
| 遊戲狀態不為開放 (`status != 0`) | 回傳錯誤，例如 "Game is not open for betting" |
| 下注時間不在遊戲的 `[starttime, endtime)` 範圍內 | 回傳錯誤，例如 "Betting period has ended" |
| VIP 遊戲但使用者非 VIP | 回傳 403 Forbidden，"VIP only game" |
| `betoption` 無效 | 回傳 400 Bad Request，"Invalid bet option" |
| `betzcoin` 與 `zcoinprice` 不符 | 回傳 400 Bad Request，"Invalid bet amount" |
| Z 幣餘額不足 | 拒絕下注，回傳 402 Payment Required 或對應業務錯誤碼 |
| 會員服務 (`memberservice`) 超時或錯誤 | 下注失敗，回傳 503 Service Unavailable |
| 寫入 `betpool_bets` 失敗 (Cassandra錯誤) | 交易失敗，需考慮扣款是否需回滾 (需人工確認) |
| 同一使用者對同一遊戲重複下注 | 需人工確認：是拒絕重複下注，還是允許追加下注？若主鍵為 `(gid, account, id)`，`id` 為 UUID，則可支援多次下注 |
| 使用者被封禁 (`gameusers_banned` 有未過期記錄) | 拒絕下注，回傳 403 Forbidden |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| BP-001 | Flow Test | 正常下注：開放遊戲、有效選項、足夠餘額 | 成功寫入 `betpool_bets`，錢包扣款成功 |
| BP-002 | Permission Test | VIP 遊戲，非 VIP 使用者下注 | 失敗，回傳 VIP 權限不足 |
| BP-003 | Permission Test | 封禁帳號下注 | 失敗，回傳帳號異常 |
| BP-004 | API Test | 對不存在的遊戲 ID 下注 | 失敗，回傳 404 |
| BP-005 | API Test | 對已關閉(`status=1`)的遊戲下注 | 失敗，回傳遊戲未開放 |
| BP-006 | API Test | 使用遊戲中不存在的 `betoption` 下注 | 失敗，回傳選項無效 |
| BP-007 | Flow Test | 下注金額 (`betzcoin`) 與遊戲要求 (`zcoinprice`) 不符 | 失敗，回傳金額錯誤 |
| BP-008 | Flow Test | 餘額不足時下注 | 失敗，回傳餘額不足 |
| BP-009 | Integration Test | 扣款成功後寫入 Cassandra 失敗 | 確認交易一致性，是否觸發退款 (需人工確認) |
| BP-010 | Flow Test | 重複下注 (相同/不同選項) | 確認業務規則，成功或失敗都須符合預期 |

---

## 9. 高風險區域

- **交易一致性**：扣款 (memberservice) 與寫入下注記錄 (Cassandra) 的原子性。若寫入失敗，扣款需能回滾或補償，此為**需人工確認**的關鍵點。
- **餘額驗證**：餘額不足時必須嚴格拒絕，避免會員負債。
- **快取一致性**：若使用 `predict:game:{gid}:status` 快取遊戲狀態，在狀態變更時 (如遊戲截止) 需立即失效，否則玩家可能對已關閉遊戲下注。
- **VIP 資格即時性**：VIP 判斷若依賴快取 (`GameUser:{authkey}`)，需確保會員資格變更時，快取已被清除。

---

## 10. 常見錯誤

- ❌ **查詢 `betpool_games` 未過濾 `status=0` 或時間區間**：僅憑前端傳來的 `id` 查詢，未在服務端校驗遊戲狀態，導致對已關閉遊戲下注。
- ❌ **寫入 `betpool_bets` 時遺漏 `account` 或 `gid`**：這兩個是 Cassandra 主鍵的重要組成部分，遺漏將導致資料無法正確分區或查詢。
- ❌ **直接修改 `betpool_bets.betzcoin` 或 `betoption`**：這些欄位在 `predict-detail.md` 中有明確限制 (`僅於下注時寫入，不可修改`)。
- ❌ **回傳其他使用者的下注明細**：查詢 API 忘記加上 `account` 過濾條件，導致資料外洩。
- ❌ **忘記檢查 `gameusers_banned`**：僅檢查 `gameusers.status` 是不夠的，封禁記錄可能獨立存在。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `BetPoolController.CreateBet` |
| DB | `predict.betpool_games`, `predict.betpool_bets`, `member.gameusers`, `member.gamesublogs` |
| Redis | `GameUser:{authkey}`, `predict:game:{gid}:status` (Concept) |
| Code | `BetPoolController.CreateBet`, `BetPoolService.CreateBet`, `BetPoolProvider` |
| Rules | `predict-detail.md` - write restrictions for `betpool_bets`, `predict-detail.md` - read rules for `betpool_games`, `member-detail.md` - `status` and `membership` validation |
| External Service | `memberservice` for balance check and deduction |