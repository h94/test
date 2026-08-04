# 執行競猜獲利點數發放

## 1. 場景目的
後台管理員手動觸發指定賽事的競猜獲利結算與點數發放。此流程為最終資金操作,將根據投注結果計算獲利,並調用會員服務將點數發放至中獎用戶的錢包。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/predict/payout/{gameType}/{lid}/{gdate}/{gid}` | 觸發指定賽事獲利點數結算發放 |

來源: README.md 競猜管理 API 表格

---

## 3. 流程總覽

1. 接收後台管理員的 payout request,包含遊戲類型(gameType)、聯賽ID(lid)、賽事日期(gdate)、賽事ID(gid)
2. 驗證操作者權限(後台管理 token)
3. 呼叫 `predictservice` 執行獲利點數計算,取得結算報表
4. `predictservice` 內部讀取 `predict.betpool_bets` 取得所有下注記錄,根據 `betpool_games.winresult` 和 `feedrate` 計算每個用戶的獲利點數
5. `predictservice` 更新 `betpool_bets.profitzcoin`、`winlose` 並寫入結算結果
6. `predictservice` 標記 `betpool_games.payout = true`,防止重複結算
7. 呼叫 `memberservice` 將獲利點數發放至用戶錢包 (`gameusers_wallet.Balance`)
8. 回傳結算完成結果

來源: README.md「競猜賽事結算與點數發放」使用場景、README.md 服務相依 predictservice / memberservice

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `PredictController.Payout` | 接收 POST request,驗證參數 |
| 2 | Service | `IPredictService.PayoutGame` | 呼叫 predictservice 結算 API |
| 3 | Provider | `PredictProvider.PayoutGame` | 發送 HTTP request 至 predictservice |
| 4 | (下游) | predictservice 內部邏輯 | 讀取 betpool_bets,計算獲利,更新 betpool_games.payout |
| 5 | Service | `IMemberService.TransferMember` | 呼叫 memberservice 發放點數 |
| 6 | Provider | `MemberProvider.Transfer` | 發送 HTTP request 至 memberservice |
| 7 | (下游) | memberservice 內部邏輯 | 寫入 gameusers_wallet_transactions,更新 gameusers_wallet.Balance |

來源: README.md 服務相依 predictservice / memberservice、pricebackendservice-detail.md member.gamesublogs 寫入限制

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | predict.betpool_bets | Read | 讀取該賽事所有下注記錄 |
| DB | predict.betpool_bets | Update | 寫入 profitzcoin、winlose |
| DB | predict.betpool_games | Read | 取得 winresult、feedrate、payout 狀態 |
| DB | predict.betpool_games | Update | 標記 payout = true |
| DB | member.gameusers_wallet | Update | 增加中獎用戶 Balance |
| DB | member.gameusers_wallet_transactions | Write | 記錄點數發放交易流水 |
| Redis | predict:game:{gid}:status | Delete | payout 狀態變更時需清除快取,確保資料一致性 |

來源: db/predict-detail.md betpool_games payout 欄位規則、betpool_bets profitzcoin 規則、Redis predict:game:{gid}:status 操作表、pricebackendservice-detail.md member.gameusers_wallet 寫入限制

---

## 6. 重要規則

- **權限限制**: 僅後台管理員可呼叫,需要驗證 token
- **不可逆操作**: `betpool_games.payout` 一旦設為 true 不可回退為 false
- **重複結算防護**: 執行前須檢查 `payout` 是否已為 true,若已結算則拒絕重複操作
- **Payout 前置條件**: `betpool_games.status` 必須 > 1(遊戲已結束或已結算) 且 `payout = false`
- **Winresult 不可為空**: 未開獎遊戲不可執行 payout,winresult 必須有值
- **點數寫入規則**: `gameusers_wallet.Balance` 不可直接 UPDATE,必須透過 `TransferMember` 交易邏輯更新,同時寫入 `gameusers_wallet_transactions` 交易流水記錄
- **Betzcoin 不可修改**: 原始下注金額寫入後不可變更;若金額錯誤應新增沖正記錄
- **Redis 快取失效**: payout 完成後必須主動刪除 `predict:game:{gid}:status` Redis key
- **Profitzcoin 寫入限制**: 僅結算相關服務(predictresultservice / flowcontrolservice)可寫入,其他服務不可直接 UPDATE

來源: db/predict-detail.md betpool_games payout 規則、status 規則、betpool_bets 寫入規則、db/member-detail.md gameusers_wallet 寫入限制、db/pricebackendservice-detail.md member.gameusers_wallet 規則

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 遊戲不存在或 gid 無效 | 回傳 404,提示賽事不存在 |
| 遊戲尚未結束 (status < 2) | 回傳 400,提示賽事未結束不可結算 |
| Payout 已執行 (payout = true) | 回傳 409,提示已結算不可重複操作 |
| Winresult 為空(未開獎) | 回傳 400,提示需先設定開獎結果 |
| 計算獲利時 betpool_bets 為空 | 回傳 200,但無點數發放(無用戶下注) |
| predictservice 呼叫失敗 | 回傳 502,記錄錯誤日誌 |
| memberservice Transfer 失敗 | 需人工確認:部分用戶點數可能未發放,需重試或手動補發 |
| Redis 快取刪除失敗 | 前台可能暫時顯示舊狀態,不影響核心流程,但應記錄 warning |

來源: db/predict-detail.md betpool_games payout 規則、status 規則

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| PT-01 | API Test | 正常 payout,遊戲已結束且有下注記錄 | 200,profitzcoin 正確寫入,gameusers_wallet.Balance 正確增加 |
| PT-02 | Flow Test | payout 已執行,重複呼叫 | 409 Conflict |
| PT-03 | Flow Test | 遊戲 status=0 (尚未開始) | 400 Bad Request |
| PT-04 | Flow Test | winresult 為空 | 400 Bad Request |
| PT-05 | Integration Test | 無用戶下注 (betpool_bets 為空) | 200,無點數變動 |
| PT-06 | Permission Test | 未帶 token 呼叫 | 401 Unauthorized |
| PT-07 | Permission Test | 非管理員 token 呼叫 | 403 Forbidden |
| PT-08 | Integration Test | predictservice 回應失敗 | 502,錯誤日誌記錄 |
| PT-09 | Integration Test | memberservice Transfer 失敗 | 回傳錯誤,需確認無部分發放 |
| PT-10 | Cache Test | payout 完成後檢查 Redis | predict:game:{gid}:status 已刪除 |

---

## 9. 高風險區域

- **高風險 table**: `member.gameusers_wallet` (點數餘額)、`member.gameusers_wallet_transactions` (交易流水)
- **高風險 API**: POST `/api/v1/predict/payout/{gameType}/{lid}/{gdate}/{gid}` (直接觸發資金操作)
- **跨服務資料同步**: predictservice 計算獲利 → memberservice 發放點數,需確保兩服務資料一致;若 Transfer 失敗可能造成不一致
- **Transaction**: 跨服務操作無分散式事務,需依賴冪等性設計(payout 標記)防止重複發放
- **Cache consistency**: payout 後須立即清除 Redis `predict:game:{gid}:status`,防止前台顯示過期 payout 狀態
- **Idempotency**: `betpool_games.payout` 為不可逆標記,確保即使重試也不會重複發放

來源: db/predict-detail.md betpool_games payout 規則、db/member-detail.md gameusers_wallet 寫入限制、Redis predict:game:{gid}:status 說明

---

## 10. 常見錯誤

- **新人容易犯錯**: 未檢查 `payout` 是否已執行就觸發結算,導致重複呼叫 API
- **新人容易犯錯**: 直接 UPDATE `gameusers_wallet.Balance` 而非透過 `TransferMember`,造成交易流水缺失
- **AI 容易誤解**: 誤認為點數發放由 predictservice 直接寫入 DB,實際上預測服務只負責計算,點數發放由 memberservice 執行
- **常見漏檢查項目**: 未檢查 `winresult` 是否為空,導致未開獎遊戲執行結算
- **常見漏檢查項目**: 未在 payout 後清除 Redis 快取,前台持續顯示未結算狀態
- **常見錯誤流程**: 先發放點數再標記 `payout = true`,若發放失敗但已標記,將導致無法重試;正確順序應為:計算獲利 → 標記 payout → 發放點數
- **需人工確認**: 若 memberservice Transfer 部分失敗(部分用戶發放成功、部分失敗),目前無自動重試機制,需人工檢查並補發

來源: db/predict-detail.md 常見錯誤、db/member-detail.md gameusers_wallet 寫入限制

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md POST `/api/v1/predict/payout/{gameType}/{lid}/{gdate}/{gid}` |
| DB | db/predict-detail.md betpool_games.payout、betpool_bets.profitzcoin |
| DB | db/member-detail.md gameusers_wallet.Balance、gameusers_wallet_transactions |
| DB | db/pricebackendservice-detail.md member.gameusers_wallet 寫入限制 |
| Cache | db/predict-detail.md Redis predict:game:{gid}:status |
| Code | Phase1 semantics: predict.betpool_bets, predict.betpool_games, member.gameusers_wallet |