# gamecombineservice — DB 操作邊界

> 產出時間：2025-04-10 18:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| predict Cassandra | writer | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **`activities_cycles.activityevent` / `cid`**：僅由管理後台或活動排程建立，不可經由前端或外部 API 直接寫入。
- **`activities_record.account` / `eventname`**：僅於預測活動參與時寫入，寫入後不可修改。
- **`activities_winneraccounts.rank` / `profitpoint` / `winpercentage`**：由結算排程計算後寫入，不可透過一般 API 手動修改。
- **`betpool_bets.betzcoin` / `profitzcoin`**：僅在下注時寫入，寫入後不可更新金額欄位。
- **`betpool_bets.winlose`**：僅結算時由排程設定，外部不具直接寫入權限。
- **`betpool_games.status` / `payout` / `winresult`**：僅限結算排程更新，外部不允許直接變更。
- **`calculatelog.done`**：僅內部計算任務可寫入 `done=1`，前端或外部 API 不可操作計算完成旗標。

### 讀取規則

- **活動週期查詢**：必須同時限制 `activityevent` 與 `cid`（clustering key），不可僅用 `site` 掃描整個 Partition。
- **進行中競猜遊戲**：讀取 `betpool_games` 時須過濾 `status`（如 `status=1` 表示進行中），且應搭配 `starttime <= now` 與 `endtime >= now`，已結束或尚未開始的遊戲不可提供下注。
- **下注記錄查詢**：查詢 `betpool_bets` 必須帶入 `gid`（partition key），再依 `id` 或 `account` 進行範圍過濾；嚴禁僅使用 `account` 進行全表掃描。
- **贏家排行**：讀取 `activities_winneraccounts` 必須以 `site`、`activityevent`、`cid` 限定週期，並按 `rank` 排序；不同週期資料不可混合。
- **計算日誌檢查**：讀取 `calculatelog` 時，應以 `weekid` 或 `weekdate` 為主要條件，判斷某週是否已完成計算。

### 不可回傳欄位

- **`betpool_bets.account`**：使用者帳號為個人識別資訊，任何對外查詢不得回傳。
- **`betpool_bets.betzcoin` / `profitzcoin`**：內部結算用原始金額，前端僅應看到聚合後的投注總量或派彩總額，不可暴露單筆明細。
- **`activities_record.winbets`**：內含投注 ID 列表，為內部關聯資料，不應直接回傳前端。
- **`betpool_games.feedrate`**：抽水比例為內部營運參數，不適合對外揭露。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport MySQL | reader | Schema：db/games.md · 語意：db/games-detail.md |

### 寫入限制

不適用。本服務對 games 資料庫僅具讀取權限。

### 讀取規則

- **比賽查詢**：必須以 `gdate` 和/或 `lid` 作為主要過濾條件，避免全表掃描。
- **啟用中比賽**：查詢 `games_bk`、`games_bm`、`games_bs` 時，通常需過濾 `status`，例如排除 `PreGame` 等尚未開始的比賽，僅向前端提供可投注或已結束的賽事。
- **特定來源查詢**：若需查詢特定資料來源（如 '1xbet.com'）的比賽，必須附帶 `source` 作為 `WHERE` 條件，以利索引使用。

### 不可回傳欄位

- **`games_bk.siteidmaps`**：`games_ck` 表結構中未定義，屬於其他 `games_` 分表的內部映射資料，前端不需要了解站台對照細節。
- **`games_bk.otherinfo`**：為內部備註或爬蟲原始資訊，可能包含未結構化的雜訊，不應直接回傳。

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| PriceCenter Cassandra | writer | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **`pricecenter.accounts_{brand}.password`**：僅 `gamecombineservice` 內部建立或更新遊戲平台帳號流程可寫入，必須雜湊處理，不可明文儲存。
- **`pricecenter.accounts_{brand}.phone`**：與帳號建立或更新流程綁定，寫入後不可由前端要求直接修改，須驗證後才能更新。
- **`pricecenter.accounts_{brand}.enabled`**：僅特定管理或狀態變更流程可修改其值（0 或 1），一般 UPDATE 不可無故變動啟用狀態。
- **`pricecenter.accounts_{brand}.handler`**：僅在建立或更新處理器配置映射時寫入；更新時必須使用合併寫入（如 INSERT JSON），不可直接以空 map 覆蓋已有細項，避免設定遺失。
- **`pricecenter.sitegames_{gtype}.gid`**：僅執行遊戲映射流程（SetGidToEmpty）時可將 `gid` 設為空字串；其他場景不可直接寫入或修改 `gid`。
- **`pricecenter.games_{gtype}.gtime`**：僅 `UpdGameTime` 操作可更新遊戲時間，不可逕行由其他 API 修改。
- **`pricecenter.actionlog`**：所有欄位僅可透過記錄操作日誌的寫入點新增（INSERT），不支援 UPDATE 或 DELETE；`detail` 必須為合法的 JSON 結構，不可事後修改。

### 讀取規則

- **平台帳號查詢**：讀取 `pricecenter.accounts_{brand}` 時必須以 `account` 作為 WHERE 條件（partition key）；嚴禁僅使用 `username` 或 `phone` 進行查詢，否則將導致全表掃描。
- **帳號啟用檢查**：遊戲平台登入或操作前，須篩選 `enabled = 1`；`enabled = 0` 表示已停用，不可允許任何操作。
- **關閉時間過濾**：`closetime` 若為非空值（非空字串）表示帳號已關閉，該帳號不可被選用於任何流程。
- **站點遊戲查詢**：讀取 `pricecenter.sitegames_{gtype}` 時必須指定 `site`（partition key），並結合 `gdate` 範圍及 `status = 2` 過濾，避免掃描大量非生效遊戲。
- **中心遊戲查詢**：讀取 `pricecenter.games_{gtype}` 時應以 `gdate` 和 `status` 為主要過濾條件；非生效狀態的遊戲不可提供給前端選擇。
- **賠率歷史查詢**：讀取 `pricecenter.odds_his_{gtype}_{gdate}` 時，必須同時提供完整 partition key 條件：`site`、`sitelid`、`sitegid`，並限定 `gdate` 聚簇鍵範圍；未帶齊 partition key 將觸發全表掃描。
- **操作日誌查詢**：讀取 `pricecenter.actionlog` 須以 `date`（partition key）為主軸，輔以 `addtime`、`user`、`gametype` 進行範圍查詢；不可僅以 `user` 作為 WHERE 條件。

### 不可回傳欄位

- **`pricecenter.accounts_{brand}.password`**：密碼為極敏感個資，任何對外 API 不可回傳。
- **`pricecenter.accounts_{brand}.phone`**：電話號碼為使用者個人資料，不可於查詢列表或詳情中回傳。
- **`pricecenter.accounts_{brand}.handler`**：處理器內部配置映射，屬設定細節，對外僅需要知悉存在與否，不可回傳細部鍵值。
- **`pricecenter.actionlog.detail`**：原始操作細節可能包含敏感資訊，對外查詢時應進行遮蔽或僅回傳摘要欄位。
- **`pricecenter.odds_his_{gtype}_{gdate}.logs`**：原始賠率變動 JSON，前端不應直接取得完整結構，需由服務層進行轉換或摘要後提供。

---

## Redis

無使用 Redis 快取。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 活動週期建立 | acmanagement-service | predict 僅讀取活動週期資料，不負責週期生成與時間控制 |
| 使用者帳戶驗證 | auth-service | predict 僅記錄帳號，不處理驗證或登入 |
| 投注池派彩金流 | wallet-service | betpool 結算結果產生後由 wallet-service 執行轉帳 |
| 平台密碼驗證 | auth-service | pricecenter 儲存密碼但由 `auth-service` 進行驗證比對，本服務不處理登入驗證邏輯 |
| 遊戲賽程管理 | schedule-service | pricecenter 負責儲存站點遊戲與賠率，但賽程與時間變更由外部排程服務控制 |
| 預測結果統計與排名計算 | 內部結算排程 | predict `activities_winneraccounts` 及 `calculatelog` 由專責排程生成，本服務僅寫入基礎記錄 |

---

## 常見錯誤

- ❌ 直接對 `betpool_bets` 執行跨遊戲批量更新 → ✅ 每次更新應限定單一 `gid`（partition key），避免全表掃描或逾時。
- ❌ 未檢查 `betpool_games.status` 即允許下注 → ✅ 下注前須驗證該遊戲狀態為「進行中」或「可下注」，已結束或暫停的遊戲應拒絕。
- ❌ 下注時未檢查 `betpool_games.starttime` 與 `endtime` 範圍 → ✅ 必須確認當前時間位於投注時間窗內，否則拒絕請求。
- ❌ 查詢下注記錄時僅使用 `account` 作為條件 → ✅ 必須連同 `gid`（partition key）一起查詢，否則引發全表掃描。
- ❌ 直接將 `password` 寫入明文 → ✅ 寫入前須雜湊處理，即使測試資料亦不可使用明碼。
- ❌ 對 `accounts_{brand}` 執行 UPDATE 時未使用 `account` 或 `username` 進行 WHERE 過濾 → ✅ 必須指定帳號唯一鍵，避免單次更新影響整個 Partition。
- ❌ 為省事對 `enabled` 狀態執行 UPDATE 時不帶 `closetime` 檢查 → ✅ 若 `closetime` 非空，帳號已關閉，不應再變更其啟用狀態。
- ❌ 誤認 `handler` 為可選的純文字欄位，直接寫入空值導致設定遺失 → ✅ 寫入前須確保 map 結構正確，僅透過特定流程更新其中鍵值對。
- ❌ 前端顯示判賠等場景時回傳 `password` 或 `phone` → ✅ 任何對外輸出必須遮蔽或排除這兩欄位。
- ❌ 查詢 `odds_his_{gtype}_{gdate}` 時未限定 `gdate` 範圍 → ✅ `gdate` 為 CLUSTERING ORDER BY 欄位，需配合 `site` + `sitelid` + `sitegid` 查詢單一遊戲的賠率歷史，不可無限制掃描。
- ❌ 對 `accounts_{brand}` 使用 `username` 或 `phone` 作為查詢鍵時忽略 `account` 為 partition key → ✅ 必須以 `account` (唯一值) 作為 WHERE 篩選條件，否則可能觸發全表掃描。