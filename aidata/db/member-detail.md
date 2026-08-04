# member DB — 完整使用脈絡

> 產出時間：2026-05-30 09:00:00
> 欄位結構定義：[member.json](./member.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| memberservice | owner | 讀、寫、刪；管理會員生命週期（註冊、登入、密碼、狀態、訂閱） |
| webpservice | owner / writer / reader | 讀、寫特定欄位（如 `username`、`headshotpath`、封禁記錄）、唯讀部分（如 `password`、`authkey` 不可寫） |
| mainmasterservice | owner | 讀、寫；管理員後台操作（封禁、修改 email 等） |
| zaiservice | owner | 讀、寫；內部管理及第三方登入處理 |
| pricecentersite | reader / writer | 讀；寫入特定欄位（如 `memberships`、`focus_account`、第三方登入資訊、NewLottery 訂閱記錄等） |
| newlotterysite | owner | 讀、寫；NewLottery 平台會員管理 |
| newlotterybackendservice | owner / writer / reader | 讀、寫；NewLottery 後台管理（含通知、佣金、訂閱方案、封禁） |
| predictservice | reader | 唯讀；查詢會員資料用於權限驗證、VIP 資格判斷 |
| predictresultservice | reader / writer | 讀；寫 `gameusers.gamecount`、`lastchecktime`、`rank`（結算後更新） |
| predictrobotbyconnect | owner | 讀、寫；機器人下注策略（寫入 `gamerobots.enabled`、`gameusers.lastactiontime` 等） |
| predictrobot | reader | 唯讀；策略讀取機器人清單 |
| pricebackendservice | writer / reader | 讀、寫；管理後台及爬蟲報表 |
| pricecentermanage | reader | 唯讀；報表統計 |
| leaderboardsite | reader / writer | 讀、寫；排行榜及管理員操作 |
| masterservice | reader | 唯讀（僅讀取，無寫入權限） |

**📌 注意**：`password`、`authkey`（主鍵）不可由任何服務直接對外暴露或由非信任服務任意寫入；跨服務變更 `status`、`memberships` 等欄位必須遵循對應業務規則。

---

## Table：gameusers

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
     memberservice           memberservice          memberservice / 管理
       INSERT                  UPDATE                    UPDATE
     value=0 (未啟用) ────→ value=1 (已啟用) ──────→ value=2 (凍結)
         │
         └─────────────────────────────────────────→ value=0 (停用)
                      memberservice 管理操作
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 未啟用 | memberservice | 註冊時預設值（一般來源）；Email 驗證前 |
| 1 | 已啟用 | memberservice | Email 驗證完成或特定來源（如 uwin）自動啟用 |
| 2 | 凍結 | memberservice / 管理後台 | 系統封禁或管理員手動停用 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | INSERT status=0 | 註冊 | 一般來源預設未啟用 |
| memberservice | UPDATE status=1 | Email 驗證成功 | 或 uwin 等來源直接設為 1 |
| memberservice | UPDATE status=2 | 管理員封禁 | 同時寫入 `gameusers_banned` |
| memberservice | UPDATE status=0 | 管理員停用 | 解封後還原 |
| predictservice | SELECT WHERE status=1 | 登入驗證 | 非 1 拒絕登入 |
| webpservice | SELECT WHERE status=1 | 登入驗證 | 同上 |
| all readers | SELECT WHERE status=1 | 查詢活躍用戶 | 統計報表需排除非正常用戶 |

**⚠️ 跨服務限制**：
- 僅 `memberservice`、`webpservice`、`mainmasterservice`、`zaiservice` 等管理服務可 UPDATE status；`predictservice`、`predictrobot`、`pricecentermanage` 等 reader 不可寫入。
- status=2（凍結）後不可直接改為 1，需先解封（刪除 `gameusers_banned` 記錄）。

### password 欄位

**型別**：text（雜湊值）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | INSERT | 註冊 | 須經 `Hash.HashPasswordString` 雜湊 |
| memberservice | UPDATE | 變更密碼 | 需舊密碼驗證或特定流程 |
| zaiservice | UPDATE | 內部變更 | 僅特定 API 可執行 |
| 所有 reader | SELECT | 僅內部驗證 | 不可回傳給前端 |

**⚠️ 注意**：
- 任何 API 回傳都不可包含此欄位（含管理後台）。
- 不允許明文儲存，雜湊演算法為 BCrypt 或等效。

### authkey 欄位

**型別**：text（UUID / Hash）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | INSERT | 註冊 | 由 `Hash.HashAuthString(account)` 產生，不可變更 |
| 所有 reader | SELECT | 查詢依據 | 主鍵查詢，不可修改 |

**⚠️ 注意**：
- 對外 API 不可回傳 `authkey`，僅用於內部認證。
- 前端應透過 `account` 或 token 識別用戶。

### email 欄位

**型別**：text

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | INSERT | 註冊 | 須檢查 `forbidden_email_domains` 黑名單 |
| memberservice | UPDATE | 變更 email | 需驗證流程，不可直接 UPDATE |
| pricecentersite | UPDATE | 第三方登入 | Apple 登入時可能寫入 |
| predictservice | SELECT | 登入/查詢 | 僅用戶本人或後台可見，公開 API 不可暴露 |

**⚠️ 注意**：
- 不可透過一般 API 直接返回 `email`（隱私保護）。
- 已註冊的 email 不可再被其他帳號使用。

### memberships 欄位（list<text>）

**型別**：list<text>（會員資格代碼）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | APPEND | 訂閱成功 | 通常由 `gamesublogs` 寫入後同步 |
| pricecentersite | APPEND | 訂閱付款回調 | 同 memberservice |
| webpservice | APPEND | 活動獲獎 | 如 `supreme_*` 格式 |
| 所有 reader | SELECT | 查詢會員資格 | 比對 `gamesublogs.subendtime` 判斷有效 |

**⚠️ 注意**：
- 僅可 APPEND，不可直接 REPLACE 整個 list；刪除需透過退訂流程。
- 限制列表最大長度（建議 1000），避免 Cassandra 大 list 效能問題。

### focus_account / black_account / follow_account（list<text>）

**型別**：list<text>

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | APPEND / REMOVE | 用戶操作 | 透過專用 API，不可直接覆寫 |
| webpservice | APPEND / REMOVE | 用戶操作 | 同上 |
| pricecentersite | APPEND / REMOVE | 第三方登入延伸操作 | 例如第三方平台朋友清單同步 |
| all readers | SELECT | 查詢用戶社交關係 | 僅回傳當前用戶自己的清單 |

**⚠️ 注意**：
- `black_account` 與 `focus_account` 互斥（不可同時存在同一帳號）。
- 清單過大時應分頁存取，避免全表讀取。

### rank 欄位（int）

**型別**：int（預設 1）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | INSERT rank=1 | 註冊 | 預設一般會員 |
| predictresultservice | UPDATE | 結算後升級 | 依排名計算，設為 2 或 3 |
| webpservice | UPDATE | 管理員操作 | 後台直接設定 |

### gamecount 欄位（int）

**型別**：int

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | UPDATE | 完成一場遊戲 | 僅由後端邏輯遞增，不可直接 SET |
| predictresultservice | UPDATE | 結算時 | 每次結算 +1 |
| webpservice | UPDATE | 遊戲結束 | 同上 |

### lastactiontime / lastchecktime（bigint）

**型別**：bigint（時間戳，毫秒，UTC）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | UPDATE | 用戶 API 操作 | `lastactiontime`；`lastchecktime` 由排名檢查更新 |
| predictresultservice | UPDATE | 排名檢查 | `lastchecktime` 用於判斷是否需要重新計算 |
| all readers | SELECT | 活躍判斷 | `lastactiontime > 30 天前` 視為活躍 |

**⚠️ 注意**：
- 不可由 API 參數直接設定；僅服務端自動更新。

### showcode 欄位（text）

**型別**：text（推薦碼）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | INSERT | 註冊時可選填 | 寫入後不可變更 |
| all readers | SELECT | 推薦關係關聯 | 用於 `gameusers_recommend` 表建立推薦鏈 |

### renamecount 欄位（int）

**型別**：int

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | UPDATE（+1） | 用戶成功改名時 | 每次遞增，達到系統上限（如 3 次）後禁止再改名 |

---

## Table：gameusers_banned

### addtime 欄位（bigint）

**型別**：bigint（時間戳，毫秒）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | INSERT | 管理員封禁時 | 系統自動寫入 |
| webpservice | INSERT | 管理後台 | 同步更新 `gameusers.status` |
| 所有 reader | SELECT | 封禁檢查 | 配合 `endtime` 判斷是否仍封禁 |

### endtime 欄位（text）

**型別**：text（可為空，格式如 `2026-01-01`）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | INSERT | 永久封禁 | 設為 null |
| memberservice | UPDATE | 提前解封或延長 | 僅管理員可操作 |

**⚠️ 注意**：
- 空值表示永久封禁，`endtime > now()` 表示仍封禁中。
- 解封時須同時還原 `gameusers.status` 為 1。

### description 欄位（text）

**型別**：text

**⚠️ 注意**：
- 封禁原因僅內部管理使用，前端 API 不可回傳。

### cost / deducted / username 欄位

| 欄位 | 型別 | 說明 |
|------|------|------|
| cost | int | 罰款金額（若有），無則為 0 |
| deducted | boolean | 是否已從帳戶扣除 |
| username | text | 被封禁時的顯示名稱，用於記錄（不隨改名變動） |

---

## Table：gamesublogs

### subtime / subendtime（text）

**型別**：text（日期或時間字串）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | INSERT | 訂閱付款成功 | `subtime` 為訂閱開始時間 |
| pricecentersite | INSERT | 第三方登入時訂閱 | 同步寫入 |
| all readers | SELECT | VIP 資格驗證 | `subendtime > now()` 判斷有效 |

### autosub（boolean）

**型別**：boolean

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | INSERT | 定期扣款訂閱 | 設為 true；一次性訂閱為 false |
| pricebackendservice | UPDATE | 變更續訂設定 | 用戶可開關 |

### paymethod / paytype（text）

**型別**：text

**⚠️ 注意**：
- 付款方式含敏感資訊，對外 API 不可回傳完整內容（需遮罩）。

---

## Table：gamerobots

### enabled（int）

**型別**：int（0=停用，1=啟用）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | INSERT / UPDATE | 管理後台 | 僅管理員可操作 |
| predictrobotbyconnect | UPDATE | 策略執行 | 如 `SetRobotStop` 設為 3 |
| predictrobot | SELECT WHERE enabled=1/3 | 下注策略 | 不同策略使用不同類型 |
| all readers | SELECT | 機器人過濾 | 統計、排行榜需排除 enabled=1 |

---

## Table：forbidden_email_domains

### name（text）

**型別**：text（域名，如 `example.com`）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | SELECT | 註冊時檢查 | 若匹配則拒絕註冊 |
| webpservice | SELECT | 註冊或變更 email | 同上 |
| pricecentersite | SELECT | 註冊流程 | 同上 |
| 管理後台（mainmasterservice 等） | INSERT / DELETE | 管理員操作 | 僅後台可修改 |

---

## Table：appleinfos_game

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| memberservice | INSERT | Apple 登入回調 | `id`、`email`、`name` 來自 Apple |
| pricecentersite | INSERT / UPDATE | Apple 登入時同步 | 使用 pricecentersite 自身的 Apple 登入流程 |
| all readers | SELECT | 關聯查詢 | 透過 `id` 或 `email` 查找綁定帳號 |

**⚠️ 注意**：
- `id` 為 Apple 提供的唯一識別碼，對外 API 不可回傳。

---

## Table：gameusers_recommend

### status（int）

**型別**：int

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 待確認 | memberservice | 建立推薦關係時 |
| 1 | 有效 | memberservice | 被推薦人完成一定條件（如首次下注） |

---

## Table：gameuserviews

### views（int）

**型別**：int

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| webpservice | UPDATE | 用戶瀏覽時遞增 | 記錄每日瀏覽次數 |
| all readers | SELECT | 分析用途 | 組合條件查詢 |

---

## Table：gameuserviewsv2

### views（counter）

**型別**：counter

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| webpservice | UPDATE（increment） | 用戶瀏覽特定遊戲/聯賽 | counter 只能增量，不可直接 SET |
| all readers | SELECT | 統計分析 | 依各維度聚合 |

**⚠️ 注意**：
- Cassandra counter 欄位不可與一般欄位混用於同一批次，需獨立操作。

---

## Table：newlottery_users

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
     newlotterysite         newlotterysite          newlotterybackendservice
        INSERT                  UPDATE                      UPDATE
     value=0 (未啟用) ────→ value=1 (已啟用) ──────→ value=2 (凍結)
         │
         └─────────────────────────────────────────→ value=0 (停用)
                    newlotterysite 管理操作
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 未啟用 | newlotterysite | 註冊時預設值；Email 驗證前 |
| 1 | 已啟用 | newlotterysite | 驗證完成或特定條件自動啟用 |
| 2 | 凍結 | newlotterybackendservice | 管理員封禁 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterysite | INSERT status=0 | 註冊 | 預設未啟用 |
| newlotterysite | UPDATE status=1 | Email 驗證完成 | 允許登入 |
| newlotterybackendservice | UPDATE status=2 | 管理員封禁 | 同時寫入 `newlottery_banned` |
| newlotterybackendservice | UPDATE status=0 | 解封 | 還原為未啟用或已啟用（視流程） |
| predictservice | SELECT WHERE status=1 | 登入驗證 | 僅正常用戶可登入 |
| pricecentersite | SELECT WHERE status=1 | 查詢會員資訊 | 訂單、支付關聯查詢 |

**⚠️ 跨服務限制**：
- 僅 `newlotterysite` 與 `newlotterybackendservice` 可寫入 `status`；其他服務只能讀取。
- status=2 時禁止任何登入操作，且須清除該用戶所有快取及 session。

### password 欄位

**型別**：text（雜湊值）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterysite | INSERT | 註冊 | 雜湊儲存，同 `gameusers.password` 規則 |
| newlotterysite | UPDATE | 變更密碼 | 需舊密碼驗證 |
| 所有 reader | SELECT | 內部比對 | 絕不回傳 |

### email 欄位

**型別**：text

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterysite | INSERT/UPDATE | 註冊/變更 | 須檢查是否已存在 |
| pricecentersite | UPDATE | 第三方登入回寫 | Apple 等綁定可能寫入 |
| all readers | SELECT | 隱私保護 | 僅用戶本人及後台可見 |

### contact_info（map<text, text>）

**型別**：map<text, text>（如 `line`, `wechat`, `whatsapp`）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterysite | UPDATE | 用戶編輯個人資料 | 僅用戶本人可修改 |
| pricecentersite | SELECT | 查詢聯絡方式供客服使用 | 後台可控 |
| all readers | SELECT | 後台或報表 | 不可暴露至公開 API |

### focus_accounts（list<text>）

**型別**：list<text>

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterysite | APPEND / REMOVE | 用戶操作 | 類似 `gameusers.focus_account` |
| pricecentersite | APPEND | 第三方平台同步 | 如從其他系統匯入 |

### id（text）

**型別**：text（內部唯一識別碼）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterysite | INSERT | 註冊時產生 | 由 `Hash.HashAuthString(account)` 或類似邏輯生成 |
| 所有 reader | SELECT | 關聯查詢 | 不可對外暴露 |

### phone（text）

**型別**：text

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterysite | INSERT/UPDATE | 用戶綁定手機 | 可能用於雙因子或通知 |
| pricecentersite | SELECT | 必要時客服聯絡 | 不可在一般 API 中回傳 |

### 其他個人資訊欄位

| 欄位 | 型別 | 說明 |
|------|------|------|
| username | text | 顯示名稱，可修改（需遵守命名規則） |
| headshotpath | text | 頭像路徑，由用戶上傳 |
| addtime | text | 註冊時間，由系統自動寫入 |

---

## Table：newlottery_banned

### addtime（bigint）

**型別**：bigint（時間戳，毫秒）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT | 管理員封禁 | 自動產生，記錄封禁時間 |

### endtime（text）

**型別**：text（可空）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT / UPDATE | 設定或修改封禁期限 | 空值表示永久封禁 |

### description（text）

**型別**：text

**⚠️ 注意**：
- 封禁原因僅供內部管理，不得對外公布。

### username（text）

**型別**：text

**⚠️ 注意**：
- 記錄封禁時的顯示名稱，不隨使用者改名而變動。

---

## Table：newlottery_commissions_betpool

### 欄位說明

| 欄位 | 型別 | 說明 |
|------|------|------|
| gametype | text（PK） | 遊戲類型（如 BK） |
| gid | text（CK） | 遊戲 ID |
| btype | text（CK） | 佣金類型（如 week） |
| pid | int（CK） | 玩法 ID |
| id | bigint（CK） | 記錄 ID |
| coin | int | 佣金金額 |
| addtime | bigint | 加入時間，毫秒時間戳 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT / UPDATE | 結算佣金時 | 計算並寫入對應遊戲的佣金記錄 |
| pricecentersite | SELECT | 佣金報表查詢 | 後台或客服查詢用戶佣金，不可直接修改 |
| predictservice | SELECT | 可能需要讀取佣金資訊以驗證資格 | 僅讀取 |

---

## Table：newlottery_notification_messages

### 欄位說明

| 欄位 | 型別 | 說明 |
|------|------|------|
| tid | text（PK） | 對應的通知主題 ID（`newlottery_notification_topics.id`） |
| id | text（CK） | 訊息唯一 ID |
| titles | map<text, text> | 多語言標題（例如 zh-TW、en） |
| contents | map<text, text> | 多語言內容 |
| addtime | bigint | 訊息建立時間 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT / UPDATE | 管理員建立或編輯通知 | 需關聯已存在的 `tid` |
| newlotterybackendservice | DELETE | 刪除通知 | 可能軟刪除（狀態隱藏） |
| pricecentersite | SELECT WHERE tid 且顯示必要語言 | 推播給用戶 | 根據用戶語系提取對應 content |
| predictservice | SELECT | 可能需要顯示給用戶 | 僅讀取 |

**⚠️ 跨服務限制**：
- 僅 `newlotterybackendservice` 可寫入，pricecentersite 或其他服務不可新增/修改通知訊息。

---

## Table：newlottery_notification_topics

### 欄位說明

| 欄位 | 型別 | 說明 |
|------|------|------|
| id | text（PK） | 主題唯一 ID |
| enabled | int | 0=停用，1=啟用 |
| icon | text | 圖標名稱或路徑 |
| names | map<text, text> | 多語言主題名稱 |
| updatetime | bigint | 最後更新時間 |

### enabled 狀態值

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 停用 | newlotterybackendservice | 管理員手動關閉 |
| 1 | 啟用 | newlotterybackendservice | 管理員啟用，新主題預設為 1 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT / UPDATE | 管理員建立或修改主題 | 控制 `enabled` 狀態，`icon`、`names` 可編輯 |
| pricecentersite | SELECT WHERE enabled=1 | 顯示可用主題清單 | 僅取啟用的主題，並根據語系取 `names` |
| all readers | SELECT | 僅讀 | — |

---

## Table：newlottery_sublogs

### 欄位說明

與 `gamesublogs` 結構相似，主鍵 `account`，clustering `(subtime, tradeno)`。

| 欄位 | 型別 | 說明 |
|------|------|------|
| account | text（PK） | 使用者帳號 |
| subtime | text（CK） | 訂閱開始時間 |
| tradeno | text（CK） | 交易編號 |
| addtime | bigint | 記錄建立時間 |
| autosub | boolean | 是否自動續訂 |
| paymode | text | 支付模式 |
| paytype | text | 支付類型 |
| subendtime | text | 訂閱到期時間 |
| subid | text | 對應的方案 ID（`newlottery_subplans.id`） |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterysite | INSERT | 訂閱付款成功 | 記錄訂閱資訊，並根據情況更新 `newlottery_users` 相關權益 |
| pricecentersite | INSERT | 第三方登入關聯訂閱 | 同步寫入（如從價格中心發起的訂閱） |
| newlotterybackendservice | SELECT / UPDATE | 查詢用戶訂閱狀態、變更 `autosub`、處理續訂 | 僅後台可變更 `autosub`，前端 API 需額外驗證 |
| predictservice | SELECT WHERE subendtime > now() | VIP 驗證 | 判斷是否為有效訂閱 |

**⚠️ 注意**：
- 不能透過一般用戶 API 直接刪除或竄改訂閱記錄；所有修改必須經過支付驗證流程。

---

## Table：newlottery_subplans

### 欄位說明

| 欄位 | 型別 | 說明 |
|------|------|------|
| id | text（PK） | 方案唯一 ID |
| coin | int | 方案價格（虛擬幣或實際金額） |
| enabled | int | 0=停用，1=啟用 |
| subdays | int | 有效天數 |
| subdesc | text | 方案描述 |
| subtype | text | 方案類型（如 sale, promotion） |
| updatetime | bigint | 最後更新時間 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT / UPDATE | 管理員建立或修改方案 | `enabled` 控制顯示與否 |
| pricecentersite | SELECT WHERE enabled=1 | 價格中心顯示方案供用戶選購 | 僅讀取 |
| newlotterysite | SELECT WHERE enabled=1 | 訂閱頁面展示 | 用於前端渲染 |

---

## Table：newlottery_users_followers

### 欄位說明

| 欄位 | 型別 | 說明 |
|------|------|------|
| account | text（PK） | 被關注的用戶帳號 |
| followaccount | text（CK） | 關注者帳號 |
| addtime | bigint | 關注時間 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterysite | INSERT / DELETE | 用戶關注 / 取消關注 | 僅用戶本人可操作 |
| pricecentersite | INSERT | 第三方登入時匯入關注清單 | 需檢查重複 |
| all readers | SELECT | 查詢粉絲數或關注列表 | 可做數量統計，不可暴露隱私 |

---

## Redis — 無明確定義的 Redis 快取

> ⚠️ 目前 `member` keyspace 未在 schema 中揭露 Redis 結構，但系統實作上可能存在臨時快取（如 Session、會員基本資料）。若有使用，請遵循以下準則：

### 假設快取：member:session:{userId}

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET | memberservice / newlotterysite | 用戶登入成功 | TTL：依登入狀態設定（如 30 分鐘） |
| GET | pricecentersite / predictservice | API 請求驗證時 | 用於快速驗證 token 有效性 |
| DEL | memberservice / newlotterysite | 登出、變更密碼、帳號停用/凍結 | 必須主動清除，不可只依賴 TTL |

**⚠️ 注意**：
- 狀態變更（凍結、停用）時必須主動 DEL 對應 userId 的所有 session key，否則已登入的凍結用戶可繼續操作。
- 快取遺失時應 fallback 至 DB 查詢，並重新寫入快取，不可直接報錯。
- 任何服務不得在快取中寫入密碼或敏感個資。

---

## 常見錯誤（跨服務）

- ❌ `pricecentersite` 直接 UPDATE `gameusers.status` → 僅 `memberservice` 等核心服務有權限，跨服務寫入會破壞狀態機。
- ❌ 查詢 `newlottery_users` 時忘記加 `status=1` 條件 → 可能將凍結帳號當作正常會員，造成支付或登入漏洞。
- ❌ `predictservice` 或 `pricecentersite` 在 `member:session` 快取不存在時直接回傳 401，未 fallback 查 DB → 暫時性快取遺失導致大量拒絕。
- ❌ `newlotterybackendservice` 封禁用戶後未同步清除對應 Redis session → 封禁用戶仍可操作，安全漏洞。
- ❌ `gamesublogs` 寫入後忘記更新 `gameusers.memberships` → 前端顯示 VIP 但實際上無權限。
- ❌ `gameuserviewsv2` 的 counter 欄位與一般欄位混用同一批次更新 → Cassandra 限制，將導致寫入失敗。
- ❌ 直接對外回傳 `authkey`、`password`、`email` 等敏感欄位 → 僅在內部服務間傳遞，且應加密。
- ❌ `focus_account` 與 `black_account` 同時存在同一帳號 → API 應在寫入前檢查互斥。