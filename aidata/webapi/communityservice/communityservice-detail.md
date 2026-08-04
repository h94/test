# communityservice — DB 操作邊界

> 產出時間：2025-04-15 16:00  
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）  
> ⚠️ AI 產出，需資深工程師審核後生效

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| predict Cassandra | writer | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **activities_cycles** 之 `site`、`cid`、`activityevent`：建立後不可變更；僅後臺管理能重新設計活動週期。
- **activities_cycles** 之 `startdate`、`starttime`、`enddate`、`endtime`、`resultcount`：僅由後臺活動排程 API 寫入，不可由端點任意修改。
- **activities_record** 之 `site`、`account`、`eventname`：寫入後不可修改，僅能更新 `restday`、`updatedate`、`winbets`。
- **activities_record** 之 `winbets`：派彩完成後由系統寫入，不可手動追加。
- **activities_record** 之 `restday`：由排程計算後更新，不可由客戶端直接填入。
- **activities_winneraccounts** 之 `site`、`activityevent`、`cid`、`account`：聚簇鍵不可變更；`rank`、`profitpoint`、`winpercentage`、`predictcount` 由結算邏輯統一計算寫入，不可個別更新。
- **betpool_bets** 之 `id`、`gid`、`account`：建立後不可修改；`betzcoin` 下注時由 API 寫入，`profitzcoin`、`winlose` 由派彩批次寫入，不可直接 UPDATE 上述欄位。
- **betpool_games** 之 `id`：不可變更；`status`、`payout`、`winresult` 僅系統內部定時任務可變更，前端不可寫入；`starttime`、`endtime`、`zcoinprice` 等遊戲參數由遊戲管理後臺設定，不可任意修改。
- **calculatelog** 之 `weekid`、`weekdate`：由系統生成，不可變更；`done` 由批次結算標記為 1，不可個別修改。
- **killeraccounts_BK** 之 `avgodd`：由內部統計計算後寫入，不可手動修改；`addtime` 自動生成，不可變更。

### 讀取規則

- **活動週期列表查詢**：須過濾 `enddate` 與 `endtime` >= 當下時間（僅顯示未結束的週期），或依業務需求檢查 `startdate` <= 當下時間。
- **玩家預測記錄查詢**：`activities_record` 須依 `site` + `account` + `eventname` 過濾，僅回傳該站點該玩家自己的記錄。
- **贏家榜單查詢**：`activities_winneraccounts` 須依 `site` + `activityevent` + `cid` 過濾，且 `rank` 需有值（NULL 不計入榜單），並按 `rank` 升序排列。
- **遊戲列表查詢**：`betpool_games` 須過濾 `status`（0:未開始, 1:進行中），對一般使用者隱藏 `viponly=true` 的遊戲（除非該使用者有 VIP 權限）。
- **賭注查詢**：`betpool_bets` 只能依 `account` + `gid` 過濾該玩家自己的注單；或依 `gid` 過濾遊戲的全體注單（僅管理後臺）。
- **僅限派彩後回傳結果**：查詢遊戲結果時，`betpool_games` 須 `payout=true` 才可回傳 `winresult`、`basicprofitzcoin`、`bonusprofitzcoin`。
- **計算記錄查詢**：`calculatelog` 僅供內部排程讀取，用於判斷某週期 `done=1` 是否已完成計算，不對外暴露查詢端點。
- **殺手帳號備份查詢**：`killeraccounts_BK` 僅供內部統計或備援程序讀取，不提供外部 API。

### 不可回傳欄位

- **betpool_bets** 之 `account`：對外 API（如查詢遊戲全體注單）不可回傳完整帳號，僅可回傳遮蔽或用戶自定義名稱。
- **betpool_bets** 之 `profitzcoin`、`winlose`：未派彩前不可回傳；派彩後僅該注單所屬玩家可見。
- **betpool_games** 之 `basicprofitzcoin`、`bonusprofitzcoin`：僅內部系統使用，不對外公開。
- **activities_winneraccounts** 之 `account`：對外榜單僅回傳遮蔽帳號或暱稱，避免個資暴露。
- **activities_record** 之 `account`、`winbets`：詳細注單資訊僅個人頁面可查，同伴系統或其他玩家不可接觸。
- **calculatelog** 全部欄位：不對外回傳。
- **killeraccounts_BK** 全部欄位：不對外回傳。

---

## ads

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| ads Cassandra | writer | Schema：[db/ads.md](../../db/ads.md) · 語意：[db/ads-detail.md](../../db/ads-detail.md) |

### 寫入限制

- **advertising** 之 `createdby`：僅後台管理 API 寫入，前端不可修改。
- **advertising** 之 `enabled`、`starttime`、`closetime`：由後台排程或管理員控制，不可由一般客戶端直接寫入。
- **advertising** 之 `seq`：由後台排序邏輯統一分配，不允許隨機寫入。
- **advertising_sport** 之 `adarea`、`id`：分區鍵與聚簇鍵一旦建立不可修改；`enabled`、`startdate`、`closedate` 僅後台管理操作。
- **advertising_sport** 之 `supportlangs`：如上所述，語言設定僅後台維護。
- **bulletinboard_sport** 之 `status`：僅系統定時任務（過期檢查）或後台管理員可切換，前端不可修改。
- **bulletinboard_sport** 之 `maintopic`、`text1`、`text2`、`text3`（多語言 map）：由後台內容管理寫入，前端只能讀取。

### 讀取規則

- **廣告列表查詢（advertising）**：需過濾 `enabled=1`，且當前時間在 `starttime`～`closetime` 範圍內才顯示。
- **廣告列表查詢（advertising_sport）**：需過濾 `enabled=1`，且 `startdate` <= 當前日期 <= `closedate`。若 `supportlangs` 不為空，應比對使用者語言與 `supportlangs` 內有交集才回傳。
- **公告列表查詢（bulletinboard_sport）**：需過濾 `status=1`（啟用），且當前時間在 `starttime`～`endtime` 範圍內（日期字串可依 `yyyy-MM-dd HH:mm` 解析後比較，或由服務端轉換為 timestamp 判斷）。
- **公告查詢時多語言處理**：回傳 `maintopic`、`text1~3` 時應依據請求的 `Accept-Language` 篩選對應 map key，無匹配時不空回傳或回傳預設語言。

### 不可回傳欄位

- **advertising** 之 `createdby`：避免洩漏後台操作者資訊。
- **advertising_sport** 之 `adclass`：對外廣告清單無需顯示分類（內部用）。
- **bulletinboard_sport** 之 `lastup_time`：維護用途，終端用戶不需知道最後更新時間。
- **所有表** 之 `seq`：排序用，前端通常無需暴露序號（除非用於排序指示）。

---

## community

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| community Cassandra | writer | Schema：[db/community.md](../../db/community.md) · 語意：[db/community-detail.md](../../db/community-detail.md) |

### 寫入限制

- **newlottery_forums** 之 `names` 中 `zh-TW` 名稱：建立／更新時須檢查唯一性（不同看板不可使用相同 `zh-TW` 名稱），且 `names` 至少需提供一個語系名稱。
- **newlottery_forums** 之 `status`：僅允許值 0（停用）或 1（啟用），且變更 `status` 需管理員權限；一般使用者不得直接寫入。
- **newlottery_subjects_index** 之 `status`：隱藏（0）／公開（1）狀態僅作者或管理員可修改，且不可有未驗證的欄位值。
- **newlottery_comments_index** 之 `status`：同上，僅作者或管理員可修改。
- **report_table** 之 `status`：僅後台處理程序可變更（`open` → `done`），一般使用者僅可建立檢舉，不可變更狀態。
- **report_table** 之 `reason`：長度限制 1～100 字元；`article_id` 需符合 22 位字母數字格式。
- **article** 之 `like_count`、`comments`：僅由按讚／回文 API 寫入，不可直接 UPDATE；`create_timestamp` 首次建立時設為系統時間（13 位 Unix 毫秒），後續不可變更。
- **like** 之 `like_id`、`timestamp`：由按讚 API 生成（shortuuid 與 13 位 Unix 毫秒），不可由客戶端指定；`user`、`userName`、`rank`、`headShotPath` 來自認證使用者資訊，不可由請求參數直接寫入。
- **hashtag** 之 `id`：不可包含底線（`_`），且建立後不可修改；僅後台管理員可執行新增與刪除。
- **hashtag** 之 `hashtag_type`：須為預定義類型（如 `leagues`、`articTopics`、`memberShips` 等），僅後台管理員可寫入。
- **hashtag** 之 `data`：必須為合法 JSON 物件，且至少包含一個語言的對應名稱；修改時僅管理員可操作。
- **hashtag** 整體：新增時不允許 `id` 為空或重複，複合鍵 `(hashtag_type, id)` 必須唯一。

### 讀取規則

- **論壇列表查詢**：僅回傳 `status=1`（啟用）的看板；若需依 `country_code` 過濾則加上該條件。
- **討論串列表查詢**：須過濾 `newlottery_subjects_index.status=1`（公開），並依 `forum_id` 匹配；排序可依 `create_timestamp` 或 `last_comment_timestamp` 倒序。
- **留言列表查詢**：須過濾 `newlottery_comments_index.status=1`，且 `subject_id` 匹配；隱藏的留言不應回傳。
- **靜音／隱藏內容過濾**：若使用者已隱藏特定討論串或留言，查詢時應在應用層過濾（`hidden=true` 的文章或留言不顯示），資料庫層不直接處理。
- **檢舉記錄查詢**：一般使用者只能查詢自己發起的檢舉（過濾 `user` 等於自己）；後台可查全部。
- **討論串/留言帳號遮蔽**：對外列表（非個人頁面）時，`account` 欄位須遮蔽（如 `name***`），不可回傳完整帳號。
- **文章查詢**：無狀態旗標，一律視為公開；回傳的 `comments` 內部留言須遮蔽 `user`（authkey）及 `account` 欄位。
- **按讚列表查詢**：查詢特定文章或回文的按讚時，僅回傳 `userName`、`rank`、`headShotPath`、`emoji`，不可回傳 `user`（authkey）。
- **hashtag 列表查詢**：必須過濾 `hashtag_type`，不可直接全表掃描；回傳時應根據請求的語言篩選 `data` 內對應鍵的值；若無匹配，可回傳預設語言（如 `en`）。

### 不可回傳欄位

- **newlottery_subjects_index**、**newlottery_comments_index**、**report_table** 之 `account`：對外 API 一律遮蔽或轉為暱稱，避免個資外洩。
- **report_table** 之 `reported_user`、`reported_username`：僅檢舉人自身及後台可見，其他人不可查看被檢舉人身份。
- **所有表** 之 `user`（authkey）：對任何外部 API 皆不可直接回傳，需轉譯為使用者顯示資訊。
- **newlottery_forums** 之 `edit_timestamp`：對一般使用者無意義，可不回傳（除非編輯時間需顯示）。
- **article** 之 `comments` 內部物件的 `user`、`account` 欄位：對外一律遮蔽，只回傳顯示名稱。
- **like** 之 `user`（authkey）：對外一律遮蔽，僅回傳 `userName`。

---

## newlottery

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| newlottery Cassandra | writer | Schema：[db/newlottery.md](../../db/newlottery.md) · 語意：[db/newlottery-detail.md](../../db/newlottery-detail.md) |

### 寫入限制

- **ChampionshipWallet** 之 `ID`：自動生成，不可手動插入或修改。
- **ChampionshipWallet** 之 `Account`、`CID`：寫入時須驗證對應使用者存在且該錦標賽（championship）處於有效狀態；`CID` 寫入後不可變更；同一個使用者在同一個錦標賽中只能有一條錢包記錄（`Account` + `CID` 組合唯一）。
- **ChampionshipWallet** 之 `Balance`：僅可透過新增 `ChampionShipWallet_Transactions` 記錄（`Point` 正負表示增減）後由系統批次寫入，不可直接 UPDATE。
- **ChampionshipWallet** 之 `LastUpdateTime`：由系統在更新餘額時自動設定，不可手動寫入。
- **ChampionShipWallet_Transactions** 之 `ID`、`AddTime`：自動生成，不可由客戶端指定。
- **ChampionShipWallet_Transactions** 之 `Account`、`CID`：必須對應已存在的 `ChampionshipWallet` 記錄；若目標錢包不存在，系統可依配置自動建立或拒絕交易。
- **ChampionShipWallet_Transactions** 之 `Point`：不可為零；若為負值，系統必須先檢查對應 `ChampionshipWallet.Balance` 是否大於等於該扣減額（避免超扣），否則拒絕交易。
- **ChampionShipWallet_Transactions** 之 `T_Type`：須為預定義枚舉值（如 1：存入、2：支出、3：調整），不可接受未定義類型。
- **ChampionShipWallet_Transactions** 之 `T_Detail`：長度限制（`varchar`），且不可包含 HTML 標籤或敏感資訊。
- **CoinWallet** 之 `Account`：主鍵，不可重複；建立時須驗證使用者存在。
- **CoinWallet** 之 `Balance`：僅可透過新增 `CoinWallet_Transactions` 記錄後由系統批次寫入，不可直接 UPDATE。
- **CoinWallet** 之 `LastUpdateTime`：由系統自動設定，不可手動寫入。
- **CoinWallet_Transactions** 之 `T_ID`、`AddTime`：自動生成。
- **CoinWallet_Transactions** 之 `Account`：必須對應已存在的 `CoinWallet` 記錄（若不存在可依系統邏輯自動建立錢包，或拒絕交易）。
- **CoinWallet_Transactions** 之 `Coin`：不可為零；若為負值，系統須檢查 `CoinWallet.Balance` 是否足夠。
- **CoinWallet_Transactions** 之 `T_Date`：由系統自動填入交易日期（預設與 `AddTime` 日期一致），不可由客戶端寫入。
- **CoinWallet_Transactions** 之 `T_Type`：預定義枚舉值，不可接受未定義類型。
- **CoinWallet_Transactions** 之 `T_Detail`：長度限制，不可包含 HTML 或敏感資訊。
- **CoinWallet_Transactions** 之 `T_UID`：可選；若提供，須驗證對應實體（如使用者、主題）的有效性；不可包含敏感資訊。

### 讀取規則

- **錢包餘額查詢**：須依當前 authkey 對應的 `Account` 過濾，僅回傳該使用者自己所屬的記錄（`ChampionshipWallet` 可用 `Account` + `CID` 查單一錦標賽錢包；`CoinWallet` 依 `Account` 查詢）。
- **交易記錄查詢**：一般使用者只能查詢自己的交易記錄（過濾 `Account`）；管理後台可依 `CID` 或全域查詢，但不得洩漏個別使用者帳號；查詢可選擇性加入時間範圍過濾（`AddTime` 或 `T_Date`）。
- **錦標賽錢包總覽（後台）**：若需要彙總，僅回統計資訊（如總餘額），不可回傳個別使用者餘額。

### 不可回傳欄位

- **ChampionshipWallet**、**CoinWallet**、**ChampionShipWallet_Transactions**、**CoinWallet_Transactions** 之 `Account`：對外 API 一律遮蔽或轉為顯示名稱；僅個人查詢自身時可回傳完整帳號。
- **CoinWallet_Transactions** 之 `T_UID`：對外列表不可回傳（僅內部用於關聯作業者或受益者）。
- **ChampionshipWallet.Balance** 與 **CoinWallet.Balance**：如 API 非該使用者自身查詢，則不應回傳（例如管理後台查詢他人錢包時遮蔽）。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| GET / SET | `predict:games:{gid}` | 取得單一遊戲資訊時 | TTL 30 秒，避免頻繁讀取 Cassandra |
| DEL | `predict:games:{gid}` | 遊戲狀態更新（派彩/變更）時 | 主動失效，確保後續讀取新資料 |
| GET / SET | `predict:activities_winner:{site}:{activityevent}:{cid}` | 查詢該活動該週期贏家榜單時 | TTL 60 秒，榜單變動低可適度快取 |

**community 無使用 Redis 快取。**  
**newlottery 涉及錢包與交易相關操作，目前未啟用 Redis 快取。**

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 使用者帳號認證與權限驗證 | auth / member service | communityservice 僅接收已驗證的 authkey，不處理登入 token 驗證 |
| ZCoin 交易（充值、提領） | wallet / payment service | betzcoin 等金額由 wallet 服務扣減與返還，底注者不直接操作餘額 |
| 賽事/賠率管理 | sports service | 遊戲 `betoptions`、`winresult` 等資料可能由上游 sports service 推送 |
| 論壇、討論串、留言的內容審核與檢舉處理 | moderation / admin service | communityservice 僅儲存檢舉記錄，不負責審核、通知、自動隱藏等後續流程 |
| 錦標賽（championship）賽程與規則管理 | championship service | communityservice 僅管理錦標賽相關錢包（championshipwallet），不建立或修改錦標賽本身 |
| 金幣充值、出金與外部金流 | payment / wallet service | coinwallet 僅記錄遊戲內幣值變動，貨幣的轉入轉出由專屬服務處理 |

---

## 常見錯誤

- ❌ 在 communityservice 內直接讀取 `activities_record` 的 `account` 欄位提供給其他玩家查詢 → ✅ 應只回傳遮蔽帳號（如 `name***`），或透過 member service 轉譯為顯示名稱。
- ❌ 查詢 `betpool_games` 時未過濾 `payout=true` 就回傳 `winresult` → ✅ 必須先確認派彩完成（`payout=true`）才能揭露結果。
- ❌ 手動寫入 `activities_winneraccounts.rank` 或 `profitpoint` 導致結算不公 → ✅ 應由結算排程批次寫入，前端僅讀取。
- ❌ 未檢查 `viponly` 旗標，將 VIP 限定遊戲顯示給一般使用者 → ✅ 查詢時應先比對使用者權限，若無 VIP 資格應過濾隱藏。
- ❌ 建立新論壇時未檢查 `names.zh-TW` 唯一性，導致兩個看板使用相同中文名稱 → ✅ 寫入前應查詢現有看板的 `zh-TW` 值，若重複則拒絕請求。
- ❌ 回傳討論串或留言列表時直接暴露 `account` 完整帳號 → ✅ 應統一遮蔽處理，僅回傳 `userName` 或遮蔽後的帳號。
- ❌ 在 `championshipwallet` 或 `coinwallet` 上直接 UPDATE `Balance` 未透過交易記錄 → ✅ 餘額變更必須先寫入對應的交易表（`championshipwallet_transactions`、`coinwallet_transactions`），再由系統批次或觸發更新餘額。
- ❌ 回傳錢包餘額 API 未驗證 authkey 歸屬，允許查詢他人餘額 → ✅ 查詢時必須以 authkey 對應的 `Account` 作為過濾條件，僅回傳該使用者自己的記錄。
- ❌ 新增或修改 hashtag 時，`id` 包含了底線或 `hashtag_type` 使用未定義類型 → ✅ 必須在寫入前校驗 `id` 格式（不含底線）且 `hashtag_type` 為許可值（如 `leagues`、`articTopics`、`memberShips` 等）。