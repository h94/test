# 建立獎池賽事（BetPool Game Create）

## 1. 場景目的
後台管理員透過此流程建立一個全新的獎池競猜賽事，設定遊戲基本參數、投注選項、時間範圍及 VIP 限制，完成後賽事即開放給前台會員查詢與下注。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/betpool/games` | 建立獎池賽事，需驗證管理員權限 |

---

## 3. 流程總覽
1. 接收建立獎池賽事 request（含遊戲設定、選項、時間等）
2. 驗證請求參數（時間合理性、選項有效性、必填欄位）
3. 驗證管理者權限（operation_token／auth）
4. 產生唯一賽事 ID
5. 寫入 `predict.betpool_games`（status=0 開放、payout=false 未派彩）
6. 回傳建立之賽事完整資訊（不包含內部運算欄位）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `BetPoolController` | 接收 POST request，驗證 operation_token 權限，轉送至 Service |
| 2 | Service | `BetPoolService` | 驗證商業邏輯：starttime < endtime、選項數量 ≥ 2、zcoinprice > 0 |
| 3 | Service | `BetPoolService` | 產生唯一 `id`（GUID / Snowflake） |
| 4 | Provider | `BetPoolProvider` | 組裝 INSERT CQL，寫入 `predict.betpool_games` |
| 5 | Provider | `BetPoolProvider` | 寫入包含：id, status=0, payout=false, starttime, endtime, betoptions, names, zcoinprice, viponly, hot 等 |
| 6 | Service | `BetPoolService` | 回傳 DTO（排除 feedrate、winresult 等內部欄位） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.betpool_games` | INSERT | 寫入新獎池賽事記錄，主鍵 `id` |
| DB | `member.gameusers` | SELECT | 驗證操作者 `status=1`（已啟用） |
| Cache | 無直接操作 | — | 賽事建立後不主動寫入 Redis，首次查詢由前台觸發快取 |
| Queue | 無 | — | 此建立流程不觸發 Kafka |

---

## 6. 重要規則

- **權限限制**：僅後台管理角色（如 `pricebackendservice` 代理或具備管理 token 者）可呼叫，**一般會員不可建立賽事**（需人工確認具體授權機制）
- **欄位限制**：
  - `status` 固定寫入 `0`（開放）；不可由請求參數指定
  - `payout` 固定寫入 `false`；不可由請求參數指定
  - `winresult` 不可於建立時寫入，預設為空
  - `feedrate` 為內部運算參數，不可從 API 傳入
- **不可暴露資料**：
  - `betoptions` 為內部映射（key → 顯示文字），對外僅回傳 key 清單或經過轉換
  - `feedrate` 絕不回傳給前端
- **不可修改欄位**：`starttime`、`endtime` 於建立後不可延長或縮短（需人工確認後台是否有例外修改 API）
- **時間驗證**：`starttime` < `endtime`，且兩者皆須為 UTC bigint timestamp（毫秒）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 無管理權限 | 回傳 403 Forbidden |
| `starttime` ≥ `endtime` | 回傳 400 Bad Request，錯誤訊息說明時間區間無效 |
| `betoptions` 少於 2 個選項 | 回傳 400 Bad Request，錯誤訊息說明至少需要兩個選項 |
| `zcoinprice` ≤ 0 | 回傳 400 Bad Request |
| `viponly` 為 true 但未提供 VIP 權限驗證邏輯 | 回傳 400 或依業務拒絕（需人工確認 VIP 賽事建立權限） |
| Cassandra INSERT 失敗 | 回傳 500 Internal Server Error，記錄錯誤日誌至 Kafka `applogs` |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| BP-CRT-01 | API Test | 正常建立賽事（含 3 個選項、有效時間） | 回傳 201，DB 寫入 status=0, payout=false |
| BP-CRT-02 | Permission Test | 使用一般會員 token 建立賽事 | 回傳 403 |
| BP-CRT-03 | Validation Test | starttime 晚於 endtime | 回傳 400 |
| BP-CRT-04 | Validation Test | 僅提供 1 個選項 | 回傳 400 |
| BP-CRT-05 | DB Test | INSERT 後檢查 `winresult` 為空、`payout` 為 false | 符合預設值 |
| BP-CRT-06 | Response Check | 檢查回傳 JSON 不包含 `feedrate`、`betoptions` 原始 map | 未暴露內部欄位 |

---

## 9. 高風險區域

- **高風險 table**：`predict.betpool_games` — 寫入錯誤的 `starttime`／`endtime` 將直接影響前台投注開放時段，事後無法直接修改（需人工確認是否可透過管理 API 調整）
- **高風險 API**：`POST /api/v1/betpool/games` — 若權限驗證被繞過，任意會員可建立賽事
- **跨服務資料同步風險**：無直接跨服務寫入；但 `pricebackendservice` 代理呼叫時需確保 token 傳遞正確（需人工確認代理機制）
- **Transaction 風險**：Cassandra 不支援多行 transaction，若 INSERT 後發生錯誤，賽事可能已建立但前台狀態異常
- **Cache consistency**：此流程不操作 Redis，但後續前台查詢若有快取，需確保賽事建立後快取無殘留過期資料

---

## 10. 常見錯誤

- ❌ **新人誤解**：在前端直接傳入 `status=0` 或 `payout=false`，誤以為 API 需要這些欄位 → 正確做法是完全不傳入狀態欄位，由後端寫死
- ❌ **AI 誤解**：推斷 `starttime` 與 `endtime` 可於賽事進行中動態修改 → 依 DB 規範，這兩個欄位建立後不可變更（需人工確認）
- ❌ **遺漏驗證**：未檢查選項數量導致建立只有一個選項的賽事，前台無法正常下注
- ❌ **錯誤流程**：在建立賽事時一併寫入 `betpool_bets`（下注記錄）或設定 `winresult`（勝出選項），混淆建立與結算流程
- ❌ **欄位洩漏**：回傳時包含 `feedrate` 或未過濾的 `betoptions` map，暴露內部計算邏輯

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/betpool/games` (README 獎池賽事區塊) |
| DB | `predict.betpool_games` (predict-detail.md / predict.md schema) |
| DB 寫入限制 | `status`, `payout`, `winresult` 僅由內部結算寫入 (predict-detail.md 寫入限制) |
| 欄位不可回傳 | `betoptions`, `betpool_bets.account` (predict-detail.md 不可回傳欄位) |
| 時間不可修改 | `starttime`, `endtime` 僅在建立時寫入 (predict-detail.md) |
| 服務角色 | predictservice 為 predict keyspace owner (predict-detail.md 服務角色總覽) |
| 權限驗證 | 所有獎池 API 皆需驗證 (README `需要驗證 ✅`) |