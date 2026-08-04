# 查詢預測遊戲列表

## 1. 場景目的
提供前台熱門預測遊戲列表，僅顯示進行中且尚未派彩的遊戲，並根據使用者 VIP 身份過濾 viponly 遊戲。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | /api/game/hot (需人工確認確切路由) | 傳入 authKey (token 解析) 回傳過濾後的 betpool_games 清單 |

---

## 3. 流程總覽

1. 驗證請求中的 authKey，取得使用者 session。
2. 查詢 member.gameusers 與 member.gamesublogs，判斷使用者是否為 VIP。
3. 查詢 predict.betpool_games，條件：hot=true, payout=false, status=1, endtime > currentTime。
4. 過濾：若遊戲 viponly=true 且使用者非 VIP，則從結果移除。
5. 對外回傳時，隱藏內部欄位，並將 betoptions key 轉換為對應語系顯示值。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Middleware | AuthMiddleware | 解析 token，取得 authKey 與使用者 account |
| 2 | Service | VIPService / PredictService | 查詢 member.gameusers.memberships 與 gamesublogs.subendtime 判斷 VIP |
| 3 | Service | PredictService.GetHotGames | 對 predict.betpool_games 執行過濾查詢 |
| 4 | Service | PredictService.FilterVIPGames | 根據 VIP 狀態移除 viponly 遊戲 |
| 5 | Controller | GameController | 對外回傳 DTO，移除敏感欄位並處理語系 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | member.gameusers | Read | 取得 memberships |
| DB | member.gamesublogs | Read | 確認訂閱有效性 (subendtime) |
| DB | predict.betpool_games | Read | 撈取符合條件的熱門遊戲 |
| Redis | 可能使用 (需人工確認) | GET | 快取遊戲列表，減少 Cassandra 讀取壓力 |

---

## 6. 重要規則

- 權限限制：僅驗證通過的 token 可調用；viponly 遊戲僅 VIP 使用者可見。
- 欄位限制：查詢條件必含 `hot=true AND payout=false AND status=1 AND endtime > 當前 timestamps`。
- 不可暴露資料：`betpool_games.feedrate`、`basicprofitzcoin`、`bonusprofitzcoin`、`betoptions` 原始 map 不可直接回傳；對外僅回傳 id、names（依語系取對應名稱）、starttime、endtime、betoptions 顯示值（取自 names map）。
- VIP 判定：`memberships` 非空，且對應 `gamesublogs.subendtime` 大於當前時間。
- 時間以 UTC 為準，儲存與比對皆使用 UTC 時間戳。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未攜帶合法 token | 回傳 401 未授權 |
| VIP 身份驗證失敗 (DB timeout 或無記錄) | 預設為非 VIP，不顯示 viponly 遊戲 |
| 所有熱門遊戲皆為 viponly 且使用者非 VIP | 回傳空陣列 |
| betpool_games 查詢異常 | 回傳適當錯誤並記錄 log |
| endtime 欄位含有非 UTC 時間 | 比對錯誤導致顯示已結束遊戲 (須強制 UTC) |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T01 | API Test | 高級會員請求 | 回傳清單含 viponly 遊戲 |
| T02 | API Test | 一般會員請求 | 清單不含 viponly 遊戲 |
| T03 | Flow Test | 遊戲已結束 (endtime < now) | 不出現在結果中 |
| T04 | Flow Test | 狀態非 1 (進行中) 的遊戲 | 不會被撈出 |
| T05 | Flow Test | payout=true | 不會被撈出 |
| T06 | Permission Test | 無效 token | 401 |

---

## 9. 高風險區域

- 高風險 table：`member.gameusers`（VIP 狀態）、`predict.betpool_games`（遊戲資料）。
- 高風險 API：直接對外暴露內部遊戲欄位。
- 時間比對：任一環節未使用 UTC 可能造成邏輯錯誤。
- Cache consistency：若使用 Redis 快取遊戲列表，viponly 狀態變更時需清除快取。
- 跨服務讀取權限：應確保 pricecentersite 僅讀取，不誤寫 predict keyspace。

---

## 10. 常見錯誤

- ❌ 忘記過濾 `viponly`，導致非 VIP 看到限定遊戲。
- ❌ 只用 `hot=true` 但忽略 `payout=false` 或 `endtime` 檢查。
- ❌ 直接回傳 `betpool_games` 完整欄位（洩漏內部數值）。
- ❌ VIP 判定未檢查 `gamesublogs.subendtime`，僅憑 `memberships` 非空就當作有效。
- ❌ 時間比較時使用伺服器本地時間而非 UTC 時間戳。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| DB | pricecentersite-detail.md - predict 讀取規則 |
| Code | PredictService.GetHotGames（推測，未提供確切檔案） |
| DB | member-detail.md - VIP 權限檢查 |
| DB | predict-detail.md - betpool_games 過濾條件 |
| API | 需人工確認確切路由 (推測 /api/game/hot) |