# predictrobotbyconnect — DB 操作邊界

> 產出時間：2025-04-07 16:00  
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）  
> ⚠️ AI 產出，需資深工程師審核後生效

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member keyspace | owner | Schema：[db/member.md](../../db/member.md) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **gamerobots.enabled**：僅由管理後台/自動化監控修改；策略執行時只讀取判斷帳號是否為機器人
- **gameusers.lastactiontime**：策略執行時不可直接修改；由專屬 action log 服務更新
- **gameusers.gamecount**：累計計數器，僅透過 counter update 遞增，不可直接 SET
- **gameusers.memberships**：訂閱會員資格清單，僅由訂閱服務（gamesublogs 寫入後）同步更新，本服務不可直接修改
- **gameusers.password**：密碼（雜湊）僅由註冊/密碼重設服務寫入，本服務不可操作
- **gamesublogs.tradeno**：交易編號為複合主鍵之一，寫入後不可變更
- **gamesublogs.authkey、subtime、addtime**：複合主鍵，寫入時須確保唯一性，不可 UPDATE

### 讀取規則

- **gamerobots 過濾**：`WHERE enabled = 1` — 策略執行時只處理啟用狀態機器人帳號進行自動下注
- **gameusers 狀態檢查**：`WHERE status = 1`（假設 1 為正常）— 凍結/停用帳號不得參與預測與下注
- **gamesublogs 訂閱有效性**：`WHERE subendtime > now()` — 查詢有效訂閱時須過濾已過期記錄
- **forbidden_email_domains 註冊攔截**：註冊時 email domain 須不存在於此表，否則拒絕註冊（本服務讀取判斷，實際註冊由其他服務處理）
- **appleinfos_game Apple 登入**：透過 Apple ID (`id` 欄位) 查詢綁定的 email 與 name，關聯至 gameusers.email

### 不可回傳欄位

- **gameusers.authkey**：內部認證金鑰，對外 API 不可直接回傳，僅用於內部服務間驗證
- **gameusers.password**：密碼（雜湊後仍屬敏感個資），對外不可回傳
- **gamesublogs.tradeno**：交易編號含敏感支付資訊，對外僅回傳遮罩後的部分字串
- **gamesublogs.paymethod**：詳細付款方式（如信用卡號末四碼）不可完整回傳，需遮罩處理
- **appleinfos_game.id**：Apple Sign-In 唯一識別碼，僅內部使用，不可對外洩漏

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra predict keyspace（`predictbets_BS/BK/SC/HL/FL`） | writer | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |
| Cassandra predict keyspace（`betpool_games`、`betpool_bets`、`activities_cycles`、`activities_record`、`activities_winneraccounts`） | reader | 同上 |

### 寫入限制

- **predictbets_\* 系列表**：機器人服務專用，僅可 INSERT（append-only），禁止 UPDATE 或 DELETE。寫入時必須提供完整複合主鍵（依據具體表為 `account`, `gid`, `mode`, `gdate` 等）及下注選項 `betoption`、固定整數 `point`（通常為 1000）。
- **betpool_bets**：本服務僅讀取，嚴禁直接寫入。`profitzcoin`、`winlose` 由結算服務非同步更新，不可異動。
- **betpool_games.status**：唯讀，賽事狀態由賽事同步服務管理，本服務不可修改。
- **betpool_games.winresult**：賽事結果僅由結算服務在比賽結束後寫入，機器人服務不可操作。
- **activities_\* 系列表**：活動相關資料（`activities_cycles`、`activities_record`、`activities_winneraccounts`）由活動管理服務寫入，本服務嚴格唯讀，不可進行任何 INSERT/UPDATE/DELETE。

### 讀取規則

- **betpool_games 進行中賽事**：`WHERE status = 1` — 僅對「進行中」的比賽執行策略。若已知 `id`（分區鍵）則直接單筆查詢，批次查詢時需傳入多個 `id`；禁止無分區鍵的全表掃描。
- **betpool_bets 重複下注檢查**：以分區鍵 `gid` 與聚簇鍵 `account` 查詢 `SELECT ... WHERE gid=? AND account=?`，若回傳記錄即代表該機器人已對該賽事投注，應跳過。
- **predictbets_\* 歷史查詢**：分區鍵通常為 `account` 或 `gid`，查詢時需提供完整分區鍵並可配合聚簇鍵 `gdate`、`mode` 做範圍過濾，例如 `WHERE account=? AND gid=? AND mode=? AND gdate>=?`。
- **activities_cycles 活動有效期**：依複合分區鍵（`site`, `activityevent`）取得所有 `cid`，再過濾當前時間介於 `startdate+starttime` 與 `enddate+endtime` 之間的週期。字串日期時間需轉換為可比格式。
- **activities_winneraccounts 排行榜**：查詢時須提供完整分區鍵 `site`, `activityevent` 與聚簇鍵 `cid`，可依 `rank` 排序讀取獲獎名單。

### 不可回傳欄位

- **`account`（所有表）**：內部機器人帳號應遮罩或使用匿名別名，對外 API 不得傳輸明文。
- **`betzcoin`、`profitzcoin`（`betpool_bets`）**：下注金額與獲利為敏感金流，對外應限制或脫敏。
- **`winbets`（`activities_record`）**：獲勝注單 ID 列表可能包含其他玩家帳號，不可完整曝露。
- **`profitpoint`（`activities_winneraccounts`）**：活動積分可展示但應避免與真實貨幣直接關聯。
- **`zcoinprice`、`feedrate`（`betpool_games`）**：商業費率與定價資訊，不應於公開 API 中洩漏。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `bet_log_history:{account}_{gid}_{mode}` | 策略執行前查詢該帳號對同一賽事同一玩法是否已下注 | 賽事結束後 24 小時自動失效；用於防止重複下注 |
| SET / GET | `robot_enabled_cache:{account}` | 策略執行時快取機器人啟用狀態 | 5 分鐘；減少對 Cassandra gamerobots 的查詢壓力 |
| SET / GET | `user_subscription:{authkey}` | 策略執行前快取用戶訂閱會員資格 | 10 分鐘；避免頻繁查詢 gamesublogs |
| DEL | `bet_log_history:{account}_*` | 賽事結果確認後 | 主動清除該帳號所有相關賽事的下注記錄快取 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 會員註冊與登入驗證 | member-auth-service | 本服務僅讀取 gameusers 狀態判斷是否可參與預測，不處理密碼驗證與 token 發放 |
| 訂閱支付與交易處理 | subscription-payment-service | 本服務僅讀取 gamesublogs 判斷訂閱有效性，不處理金流與 tradeno 生成 |
| 賽事資料同步 | sport-data-sync-service | 本服務從 support_data.result_page_data / predict_data 讀取賽事資料，不負責爬蟲與資料更新 |
| 機器學習模型訓練與預測結果產出 | ml-prediction-service | 本服務從 support_data.ml_predict_data 讀取預測結果，不負責模型訓練與 predict_1X2 產出 |
| 下注結果結算與餘額更新 | betting-settlement-service | 本服務產出 bet_output 後交由結算服務處理輸贏計算與 gameusers.gamecount 更新 |

---

## 常見錯誤

- ❌ 策略執行時直接 UPDATE gameusers.lastactiontime → ✅ 透過 action-log-service 非同步更新，避免影響策略執行效能
- ❌ 未檢查 Redis `bet_log_history` 直接寫入 predictbets_* 表導致重複下注 → ✅ 每次策略執行前先 GET Redis Key，已存在則跳過
- ❌ 讀取 gamerobots 時未過濾 enabled = 0 的帳號 → ✅ WHERE 條件必須加上 `enabled = 1`，避免對停用機器人下注
- ❌ 直接回傳 gameusers.authkey 至前端 → ✅ authkey 僅用於後端服務間驗證，對外 API 需移除此欄位
- ❌ 查詢 gamesublogs 未檢查 subendtime 導致已過期訂閱仍可使用 → ✅ WHERE 條件加上 `subendtime > currentTimestamp()`
- ❌ 策略執行時對同一 gid 重複查詢 support_data.result_page_data → ✅ 在策略開始時一次性載入所有相關賽事資料至記憶體快取
- ❌ 未處理 winrate_h / winrate_a 為字串型態導致比較錯誤 → ✅ 從 result_page_data 取得後先轉換為 float 再進行數值比較
- ❌ 策略產出 bet_output 時 Point 欄位使用浮點數 → ✅ Point 必須為整數型態 (int)，固定值 1000
- ❌ 未檢查 predict_data.odds 是否為空物件直接存取 odds.HA.1X2 導致 KeyError → ✅ 先判斷 `if 'HA' in odds and '1X2' in odds['HA']` 再取值
- ❌ 查詢 betpool_games 時省略分區鍵 `id` 導致全表掃描 → ✅ 必須提供 `id` 或使用 `IN` 子句明確指定該分區下的多個 id
- ❌ 對 activities_* 表直接進行 INSERT 企圖創建活動週期 → ✅ 活動資料僅由活動管理服務寫入，本服務應只讀取不寫入