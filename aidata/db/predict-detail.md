# predict DB — 完整使用脈絡

> 產出時間：2026-06-01 14:00
> 欄位結構定義：[predict.json](./predict.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| predictservice | owner | 讀、寫、刪，管理活動週期與預測結果 |
| tradegameservice | owner | 讀、寫（遊戲建立與管理）、管理後台操作 |
| newlotterybackendservice | owner / writer / reader | 讀、寫、查詢，管理新彩票遊戲、活動、排行榜 |
| predictresultservice | owner | 讀、寫，結算遊戲結果、活動排名、殺手統計 |
| masterservice | owner | 讀、寫，活動管理、遊戲投注管理 |
| pricecentermanage | writer / reader | 讀、寫，後台管理操作 |
| flowcontrolservice | writer / reader | 讀取，執行派彩流程時寫入結算相關欄位 |
| gamecombineservice | writer | 讀、寫，合併站點時建立活動週期、管理投注池 |
| clientflowservice | writer / reader | 讀、寫，處理用戶預測提交、投注、活動記錄 |
| zaiservice | writer / reader | 讀、寫，AI 預測結果與活動結算 |
| communityservice | writer | 讀、寫，社群排行、活動資訊 |
| gameliveservice | writer | 讀、寫，即時遊戲狀態、活動排行、投注統計 |
| webpservice | writer / reader | 讀、寫，遊戲結算、活動管理 |
| predictrobotbyconnect | writer / reader | 讀取遊戲資料，寫入機器人預測注單（predictbets_* 系列） |
| predictrobot | reader | 唯讀，機器人策略分析（不寫入任何表） |
| mainmasterservice | 無 | 不直接存取 predict keyspace |
| pricebackendservice | 無 | 不直接存取 predict keyspace |
| pricecentersite | 無 | 不直接存取 predict keyspace |

**⚠️ 衝突待人工**：predictservice 與 tradegameservice 都標示為 owner，需確認實際主控服務。

---

## Table：betpool_games

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
     predictservice        排程服務              結算相關服務
      INSERT               UPDATE                UPDATE
     status=0 (開放) ────→ status=1 (關閉) ────→ status=2 (結算)
         │
         └──────────────────────────────────→  status=3 (取消)
                     管理後台 (masterservice)
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 開放 | predictservice / tradegameservice / newlotterybackendservice | 遊戲建立時預設值 |
| 1 | 關閉 | predictservice / newlotterybackendservice（排程觸發） | 到達 starttime 時自動停止下注 |
| 2 | 結算 | predictresultservice / flowcontrolservice | 比賽結果確認且派彩完成 |
| 3 | 取消 | masterservice / pricecentermanage（管理後台） | 人工取消遊戲，任何狀態均可強制取消 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| predictservice | INSERT status=0 | 建立遊戲 | 預設開放 |
| tradegameservice | INSERT status=0 | 建立遊戲 | 預設開放 |
| newlotterybackendservice | INSERT status=0 | 建立新彩票遊戲 | 預設開放 |
| newlotterybackendservice | UPDATE status=1 | starttime 到達 | 關閉投注 |
| predictservice | UPDATE status=1 | starttime 到達 | 關閉投注 |
| predictresultservice | UPDATE status=2 | 結果確認且 payout=true | 結算完成 |
| flowcontrolservice | UPDATE status=2 | 派彩流程執行 | 結算時由 PayoutService 寫入 |
| masterservice | UPDATE status=3 | 管理後台操作 | 取消遊戲 |
| pricecentermanage | UPDATE status=3 | 管理後台操作 | 取消遊戲 |
| clientflowservice | SELECT WHERE status IN (0,1) | 玩家瀏覽 | 只顯示可投注遊戲 |
| predictrobot | SELECT WHERE status=0 AND payout=false | 策略準備 | 過濾未開始比賽 |
| communityservice | SELECT WHERE status IN (0,1) | 社群顯示 | 隱藏已結算或取消 |
| gameliveservice | SELECT WHERE status IN (0,1) | 即時推送 | 同步前端狀態 |

**⚠️ 跨服務限制**：
- status=2 僅能由 predictresultservice 或 flowcontrolservice 設定，其他服務不可直接寫入
- status=3 之後不可再變更為其他值，任何服務皆禁止修改
- clientflowservice、communityservice 對 status 只有 SELECT 權限，不可寫入
- status 變更時，必須主動清除 Redis 快取 `game:live:{gid}`（gameliveservice 負責）

### winresult 欄位

**型別**：text

**值定義**：儲存獲勝的投注選項 key（例如 "8"、"2"、"draw"）

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| {選項key} | 遊戲獲勝選項 | predictresultservice / flowcontrolservice | 比賽結束且結果確認後寫入 |
| null | 尚未開獎 | INSERT 預設 | 遊戲建立時 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| predictresultservice | UPDATE winresult | 結算時 | 僅 payout=false 時可設定 |
| flowcontrolservice | UPDATE winresult | 派彩流程 | 結算寫入 |
| tradegameservice | SELECT | 前台顯示 | 需 payout=true 才可回傳 |
| communityservice | SELECT WHERE payout=true | 社群結果頁 | 已派彩才公開 |
| gameliveservice | SELECT | 推送變更 | 僅 payout=true 時推送 |

**⚠️ 跨服務限制**：
- winresult 僅可由 predictresultservice / flowcontrolservice / masterservice 寫入
- payout=true 後 winresult 即為不可變更
- 對於尚未 payout=true 的遊戲，任何服務皆不可回傳 winresult 給前端

### payout 欄位

**型別**：boolean

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| false | 未派彩 | INSERT 預設 | 遊戲建立時 |
| true | 已派彩 | predictresultservice / flowcontrolservice | 結算完成後 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| predictresultservice | UPDATE payout=true | 結算完成且 winresult 已設定 | 設定後不可再修改 winresult |
| gameliveservice | SELECT WHERE payout=true | 推送狀態變更 | 確保前端顯示正確 |
| predictrobot | SELECT WHERE payout=false | 排除已結算 | 避免重複分析 |

**⚠️ 注意**：
- payout 僅能從 false → true，不可反向
- 查詢待結算比賽條件：`status > 1 AND payout = false`

### starttime / endtime 欄位

**型別**：bigint（UTC 時間戳）

| 服務 | 操作 | 說明 |
|------|------|------|
| predictservice / tradegameservice / newlotterybackendservice | INSERT starttime, endtime | 遊戲建立時設定，後續不可修改 |
| predictservice | SELECT | 判斷遊戲是否到達結束時間 |
| clientflowservice | SELECT WHERE endtime >= now() | 查詢進行中游戲 |
| predictrobot | SELECT WHERE status=0 AND payout=false | 排程判斷 |
| gameliveservice | SELECT starttime, endtime | 即時推送階段資訊 |

**⚠️ 注意**：
- 時間值僅在建立時寫入，不可動態延長或縮短
- 所有後端服務統一使用 UTC 比較，前端顯示時再轉換為當地時間

### betoptions 與 names 欄位

**型別**：map<text, text>

| 服務 | 操作 | 說明 |
|------|------|------|
| predictservice | INSERT betoptions, names | 遊戲建立時寫入多語言選項對照 |
| newlotterybackendservice | INSERT betoptions, names | 新彩票建立時寫入 |
| tradegameservice | SELECT | 讀取選項（不可直接回傳原始 map） |
| pricecentermanage | SELECT | 管理後台查驗 |
| gameliveservice | SELECT names | 推送時根據前端語系提取對應名稱 |

**⚠️ 注意**：
- betoptions 與 names 寫入時須進行 schema 校驗，不可存入未定義的 key
- 對外 API 不應回傳完整的原始 map，僅回傳 key 與對應的顯示名稱

### feedrate / viponly / hot 欄位

**型別**：double / boolean / boolean

| 服務 | 操作 | 說明 |
|------|------|------|
| predictservice | INSERT feedrate, viponly, hot | 遊戲建立時設定 |
| predictservice / pricecentermanage | UPDATE viponly, hot | 管理後台調整 |
| communityservice | SELECT WHERE viponly=false | 一般玩家僅能看到非 VIP 遊戲 |
| predictrobot | SELECT hot | 可能用於判斷熱門程度 |

**⚠️ 跨服務限制**：
- feedrate（抽水比例）為內部營運參數，任何對外 API 皆不可回傳
- viponly=true 的遊戲，僅驗證為 VIP 的使用者才可存取

---

## Table：betpool_bets

### betzcoin / profitzcoin / winlose 欄位

**型別**：int / int / text（winlose: "W"=贏、"L"=輸、"pending"=未結算）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| predictservice / clientflowservice | INSERT betzcoin | 玩家下注 | 僅可建立時寫入，禁止後續修改 |
| predictresultservice | UPDATE profitzcoin, winlose | 結算時 | 根據 winresult 計算後回填 |
| flowcontrolservice | UPDATE profitzcoin, winlose | 派彩流程 | 結算寫入 |
| tradegameservice | SELECT | 後台查詢 | 不可直接 UPDATE |
| clientflowservice | SELECT WHERE account=? | 個人注單查詢 | 不可查詢他人 |
| predictrobot | SELECT WHERE gid=? AND account=? | 機器人分析 | 歷史投注模式計算 |
| gameliveservice | SELECT WHERE gid=? | 即時統計 | 用於顯示遊戲投注數 |

**⚠️ 跨服務限制**：
- betzcoin 僅在 INSERT 時寫入，任何服務不可事後修改
- profitzcoin 與 winlose 只能由結算服務（predictresultservice/flowcontrolservice）寫入
- 金額錯誤時應透過新增沖正記錄處理，不可直接 UPDATE 原始記錄
- 非本人查詢時，account 與詳細投注金額不得回傳（communityservice、gameliveservice 需脫敏）

### account / gid / id 欄位

**型別**：text / text / text

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gameliveservice | SELECT account, gid, id | 內部統計 | 對外推送時需遮蔽或移除 account |

**⚠️ 不可回傳欄位**：
- account：對外 API（非本人）必須脫敏或完全隱藏
- predictrobot 內部可讀取但禁止對外輸出
- communityservice 不可回傳他人帳號

---

## Table：activities_cycles

### startdate / starttime / enddate / endtime 欄位

**型別**：text (YYYY-MM-DD) / text (HH:mm)

| 服務 | 操作 | 說明 |
|------|------|------|
| predictservice / newlotterybackendservice / gamecombineservice | INSERT startdate, starttime, enddate, endtime | 活動週期建立時寫入，後續不可修改 |
| clientflowservice | SELECT WHERE enddate >= today | 列出可參與的活動週期 |
| gameliveservice | SELECT WHERE enddate >= today | 即時活動狀態推送 |
| predictrobot | SELECT WHERE startdate <= today AND enddate >= today | 定位有效週期以參與預測 |

### resultcount 欄位

**型別**：int

| 服務 | 操作 | 說明 |
|------|------|------|
| predictresultservice | UPDATE resultcount | 活動結算後自動累加 |
| zaiservice | UPDATE resultcount | AI 預測服務在結算後寫入 |
| pricecentermanage | SELECT | 後台查看活動統計 |

**⚠️ 注意**：
- resultcount 僅可由結算服務寫入，不可透過管理後台手動修改
- 活動進行中不可提前設定此值

---

## Table：activities_record

### winbets 欄位

**型別**：list<text>

| 服務 | 操作 | 說明 |
|------|------|------|
| predictresultservice | APPEND winbets | 派彩後由系統寫入中獎注單 ID |
| zaiservice | APPEND winbets | AI 預測服務寫入 |
| communityservice | SELECT | 社群系統查詢，不可對外回傳完整列表 |

**⚠️ 跨服務限制**：
- winbets 僅允許 APPEND 追加，不可覆寫整個列表
- 任何服務對非本人查詢時，皆不可回傳此欄位

### account / eventname / restday 欄位

**型別**：text / text / int

| 服務 | 操作 | 說明 |
|------|------|------|
| predictservice | INSERT account, eventname | 用戶參與活動時寫入 |
| clientflowservice | SELECT WHERE account=? | 個人活動記錄查詢 |
| pricecentermanage | SELECT WHERE restday > 0 | 管理後台過濾有效天數 |
| predictrobot | SELECT WHERE account=? AND eventname=? | 機器人分析用戶剩餘天數與獲勝列表 |

**⚠️ 不可回傳欄位**：
- restday、winbets：非本人查詢時不可回傳
- predictrobot 讀取的 winbets 僅供策略判斷，禁止任何對外輸出

---

## Table：activities_winneraccounts

### rank / profitpoint / predictcount / winpercentage 欄位

**型別**：int / int / int / double

| 服務 | 操作 | 說明 |
|------|------|------|
| predictresultservice | UPDATE rank, profitpoint, predictcount, winpercentage | 排名結算時計算寫入 |
| zaiservice | UPDATE rank, profitpoint, winpercentage | AI 預測服務寫入 |
| pricecentermanage | SELECT WHERE site=? AND activityevent=? AND cid=? ORDER BY rank ASC | 管理後台讀取 |
| communityservice | SELECT（排行榜查詢） | 社群回傳排行榜，需對 account 脫敏 |
| gameliveservice | SELECT WHERE site=? AND activityevent=? AND cid=? | 即時活動排行推送，需遮蔽 account |
| predictrobot | SELECT WHERE site=? AND activityevent=? AND cid=? ORDER BY rank ASC | 機器人內部分析，禁止外洩 |

**⚠️ 跨服務限制**：
- account：對外公開的排行榜，必須進行脫敏處理（僅顯示開頭字母或部分遮罩）
- profitpoint、winpercentage 等財務數據：不可在公開排行榜中直接顯示
- 此表所有數值僅由 predictresultservice / zaiservice 寫入，管理端禁止手動調整

---

## Table：calculatelog

### done 欄位

**型別**：int

**值定義**：

| 值 | 意義 |
|----|------|
| 0 | 未完成 |
| 1 | 已完成 |

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 內部結算排程（如 masterservice） | INSERT weekid, weekdate, addtime, done=0 | 建立新週期記錄 |
| 內部結算排程 | UPDATE done=1 | 計算完成後標記 |
| predictrobot | SELECT WHERE weekid=? AND done=1 | 確認該週是否已處理，避免重複 |

**⚠️ 注意**：
- done 僅可由排程服務從 0 設為 1，不可回退
- predictrobot 僅讀取，不可寫入；若查無 done=1 記錄應視為未完成，不得擅自繼續

---

## Table：predictbets_{gtype}（BS, BK, SC, HL, FL…）

### enabled 欄位

**型別**：int

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 1 | 啟用 | predictservice / tradegameservice（INSERT 預設） | 建立預測選項時 |
| 0 | 停用 | masterservice / pricecentermanage（管理後台） | 手動停用 |

**⚠️ 注意**：
- 前端查詢時必須 `WHERE enabled = 1`
- 停用後的選項不可再被下注

### winloss / profitpoint / status 欄位

**型別**：int / int / int

| 服務 | 操作 | 說明 |
|------|------|------|
| predictresultservice | UPDATE winloss, profitpoint, status | 結算時寫入（status: 2=已結算,3=取消） |
| predictrobotbyconnect | INSERT（僅針對 predictbets_*） | 機器人下注時寫入新記錄，不可 UPDATE/DELETE |

**⚠️ 注意**：
- predictbets_* 系列表僅允許 INSERT（append-only），禁止 UPDATE 或 DELETE
- status 欄位僅可由結算邏輯變更，外部服務不可直接指定

---

## Table：killeraccounts_{gtype}（BK, BM, BS, ES, FL, HL, PG…）

### 核心欄位說明

- **lid**：聯賽或全體 (all) 標識
- **cid**：週期 ID
- **account**：玩家帳號（對外需脫敏）
- **username**：玩家暱稱（可直接顯示）
- **killertype**：殺手級別（"super" 或 "normal"）
- **profitpoint**：總盈利點數
- **avgodd**：平均賠率
- **winpercentage**：勝率（如 75.0）
- **totalbetcount**：總投注數
- **winbetcount**：贏取投注數
- **firstweekbetcount** / **secondweekbetcount**：雙週投注統計
- **addtime**：寫入時間（UTC 時間戳）

### 各服務操作明細

| 服務 | 操作 | 說明 |
|------|------|------|
| predictresultservice | INSERT / UPDATE（結算後） | 活動週期結算時寫入殺手排行榜數據 |
| zaiservice | INSERT / UPDATE | AI 輔助計算寫入 |
| pricecentermanage | SELECT WHERE lid=? AND cid=? | 管理後台查詢 |
| communityservice | SELECT 排行榜查詢 | 需對 account 脫敏後回傳 |
| gameliveservice | SELECT 即時推送 | 推送更新，需脫敏 account |
| predictrobot | SELECT WHERE lid=? AND cid=? | 策略分析，內部使用，嚴禁外洩財務數值 |

**⚠️ 跨服務限制**：
- account 對外時一律脫敏（如顯示部分字元）
- profitpoint、avgodd、winpercentage 等敏感數據不可在公開排行榜中展示
- 寫入僅限 predictresultservice 與 zaiservice，其他服務禁止修改
- killertype 變動需記錄操作日誌供稽核

---

## Table：championships

### 核心欄位說明

- **GameType**：遊戲類別（分區鍵）
- **ID**：錦標賽 ID（聚簇鍵）
- **Names**：多語言名稱對照 (map<text,text>)
- **Leagues**：關聯聯賽集合 (set<text>)
- **Sell_Commission_Options**：銷售佣金選項 (list<...>)
- **CloseTime**：自動結算關閉時間（由系統計算，通常為結束時間前兩天）

### 各服務操作明細

| 服務 | 操作 | 說明 |
|------|------|------|
| predictservice / newlotterybackendservice | INSERT 建立錦標賽 | 初始化遊戲資料 |
| predictservice / pricecentermanage | UPDATE 更新名稱、聯賽等 | 後台編輯 |
| clientflowservice | SELECT WHERE GameType=? AND ID=? | 前台查詢錦標賽資訊 |
| communityservice | SELECT | 社群頁面顯示 |
| gameliveservice | SELECT | 即時推送錦標賽狀態 |

**⚠️ 注意**：
- CloseTime 不可由手動設定，必須由系統根據結束時間自動計算
- 此表僅供查詢，寫入權限嚴格限制在後台管理服務

---

## Table：predictfilterreports

### 核心欄位說明

- **reportdate**：報表日期（分區鍵）
- **gametype**：遊戲類型（聚簇鍵）
- **lid**：聯賽 ID
- **filtertype**：過濾類型
- **startdate / enddate**：統計區間
- **account**：玩家帳號
- **avgwinodd**：平均贏取賠率
- **predictcount**：預測次數
- **predictwin**：預測贏次數
- **profitpoint**：盈利點數
- **winlose_detail**：輸贏細節
- **seq_score / seq_score_fix**：序列分數
- **winstreakdays**：連勝天數

**⚠️ 寫入限制**：
- 所有統計欄位僅由內部報表產生排程寫入，不可經由 API 或人工修改
- 分區鍵與聚簇鍵在產生時寫入，不可事後變更
- predictservice 僅能讀取這些報表數據，不得寫入

---

## Table：predictfilterreports_mainbet

### 核心欄位說明

類似 predictfilterreports，但專注於主投注統計。

**⚠️ 寫入限制**：
- 與 predictfilterreports 相同，所有數值僅由內部排程寫入
- predictservice 僅有讀取權限

---

## Table：strategy_bet_log

### 核心欄位

- **id**：記錄 ID
- **result**：策略結果（僅由策略執行模組寫入）
- **strategy_id**：策略編號
- 其他投注相關欄位

**⚠️ 跨服務限制**：
- `result` 欄位僅由策略執行模組透過 UPDATE 寫入，外部服務（含 predictservice）不可寫入
- predictservice 可讀取策略記錄用於分析，但禁止修改任何欄位

---

## Redis — GameLive

### game:live:{gid}

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET | gameliveservice | 遊戲建立或狀態變更時 | TTL：與遊戲結束時間一致 |
| GET | clientflowservice, communityservice, predictrobot | 查詢即時遊戲狀態 | 避免直接查詢 DB |
| DEL | gameliveservice | status 變更（尤其切換至 2 或 3）時 | 強制清除快取，確保資料一致 |

**⚠️ 注意**：
- status 變更時必須主動 DEL，不可只靠 TTL 自然過期
- predictservice 讀不到此 Key 時必須 fallback 查 DB，不可直接報錯

---

## 常見錯誤（跨服務）

- ❌ predictservice 直接把 betpool_games.status 改為 2 → 只有 predictresultservice / flowcontrolservice 可以設定結束狀態
- ❌ backendservice 查詢忘記排除 status=0 和 3 → 前台看到不該顯示的比賽
- ❌ status 變更後沒有主動 DEL Redis `game:live:{gid}` → 前台讀到過期快取，資料不一致
- ❌ betpool_bets 的 profitzcoin 被非結算服務直接修改 → 應由結算流程計算並寫入，錯誤時用沖正記錄
- ❌ 對外排行榜直接回傳 activities_winneraccounts 的 account 或 profitpoint → 必須脫敏 account，隱藏財務數據
- ❌ betoptions 或 names 寫入未驗證 key → 可能導致前端顯示異常，必須校驗 schema
- ❌ feedrate 透過對外 API 回傳 → 洩漏營運成本，所有對外 API 必須過濾此欄位
- ❌ strategy_bet_log.result 被 predictservice 誤寫 → result 僅可由策略模組寫入，predictservice 只能讀取
- ❌ predictfilterreports 統計欄位經由後台手動修改 → 所有報表數據必須由排程自動產生，保持數據一致性