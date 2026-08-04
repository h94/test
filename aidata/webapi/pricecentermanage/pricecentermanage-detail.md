# pricecentermanage — DB 操作邊界

> 產出時間：2025-07-12 15:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member keyspace | reader | Schema:[db/member.md](../../db/member.md) · 語意:[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **本服務不寫入 member 資料庫**:pricecentermanage 為管理後台與爬蟲監控服務,僅讀取會員相關資料用於統計報表,不負責會員資料的增刪改操作

### 讀取規則

- **memberdailyreport 查詢**:`WHERE Reportdate >= ? AND Reportdate <= ?`,依日期區間統計會員註冊/活躍/聊天/交易數量
- **predictdailyeport 查詢**:`WHERE Reportdate >= ? AND Reportdate <= ? AND Gametype = ?`,依日期區間與遊戲類型統計預測投注/鎖定/解鎖數量
- **gameusers 讀取**:透過 `authkey` 主鍵或 `email` 索引查詢,不做全表掃描
- **gamesublogs 讀取**:透過 `authkey` 分區鍵查詢特定用戶訂閱記錄,依 `subtime`、`tradeno`、`addtime` 叢集鍵排序

### 不可回傳欄位

- **gameusers.password**:用戶密碼雜湊值,絕不可透過任何 API 回傳
- **gameusers.email**:除管理員權限外,一般查詢不可暴露完整 email
- **gamesublogs.tradeno**:交易流水號涉及金流敏感資訊,僅供內部稽核使用

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET | `AppDevices` | 運動站台 APP 裝置版本更新時 | 永久,手動刪除;Hash 結構,field 為 device,value 為 JSON 序列化的 AppDevice 物件 |
| GET | `NotificationTopics` | 查詢運動站台通知主題時 | 永久,隨 DB 更新刪除;Hash 結構,field 為 tid,value 為 SportTopic JSON |
| GET/SET | `NotificationMessages_{hashKey}` | 查詢/更新通知訊息時 | 永久,隨 DB 更新刪除;Hash 結構,field 為 message id,value 為 SportMessage JSON |
| GET/SET | `SiteMails_{account}` | 查詢/更新用戶站內信時 | 永久,隨讀取狀態更新;Hash 結構,field 為 mail id,value 為 SportSiteMailSubjectCache JSON |
| DEL | 以上所有 Key | 管理後台手動刪除快取或 DB 資料變更時 | 主動刪除,確保快取與 DB 一致性 |

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra predict keyspace | writer / reader | Schema:[db/predict.md](../../db/predict.md) · 語意:[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **activities_cycles.startdate / starttime / enddate / endtime**：由預測活動管理 API 設定，不可直接 UPDATE 修改時間區間；不可與已結算週期的 resultcount 同時異動
- **activities_cycles.resultcount**：僅供管理後台在週期結算後寫入結果數量，不可在活動進行中提前設定
- **activities_record.winbets**：此字段為 `list<text>`，僅由對賬系統自動寫入中獎注單 ID；不可人工追加或刪除元素
- **betpool_bets.winlose**：僅允許設定為 `"win"`, `"lose"`, `"pending"` 三種值；須由結算流程統一寫入，不可直接 SET
- **betpool_games.zcoinprice**：僅可在遊戲創建時寫入，上線後不可再改；若需調整牌價應開新局，而非 UPDATE
- **betpool_games.betoptions / names**：為 `map<text, text>`，Key 與 Value 格式由前端規範綁定，寫入時須做 schema 校驗，不可存入未定義的 Key

### 讀取規則

- **activities_cycles 查詢**：`WHERE site = ? AND activityevent = ?` 為必填條件；`cid` 可選擇性過濾；不可省略 site 做全 Keyspace 掃描
- **betpool_games 狀態過濾**：前端顯示未結束遊戲時，`WHERE status = 0`（進行中）；派彩時 `WHERE payout = false AND status = 1`（已結束未派彩）
- **betpool_bets 用戶查詢**：須同時指定 `gid` 與 `account`（組合主鍵）；不允許只給 `account` 做全表掃描
- **activities_winneraccounts 排行讀取**：`WHERE site = ? AND activityevent = ? AND cid = ?` 後 `ORDER BY rank ASC`；不允許跳過 cid 直接查詢
- **activities_record 剩餘天數過濾**：`WHERE restday > 0` 僅顯示仍在活動期間的記錄，不可回傳 `restday <= 0` 的數據

### 不可回傳欄位

- **betpool_bets.betoption / betzcoin / profitzcoin**：涉及用戶投注明細，不可對非本人或非管理員權限的 GET API 回傳任何真實金額欄位
- **betpool_games.winresult**：未開獎前不可提前洩漏結果；該字段只供派彩模塊內部讀取
- **activities_winneraccounts.winpercentage**：為內部排行精度數據，除管理後台報表外，前端排行榜不應回傳原始百分比（只回傳 rank）

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| GET/SET | `PredictGame:{id}` | 查詢/更新 betpool_games 資料時 | 永久；遊戲狀態改變（status、payout）時主動 DEL |
| GET/SET | `PredictBets:{gid}` | 查詢某遊戲所有投注時 | TTL 300 秒；投注新增或結算時主動 DEL |
| SET | `PredictCycles:{site}:{activityevent}` | 活動週期設定時 | 永久；週期狀態變更時主動 DEL |
| SET | `PredictWinnerRank:{site}:{activityevent}:{cid}` | 活動開獎排行產生後回寫 | TTL 180 秒；排行資料無須常駐 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 會員註冊/登入/修改密碼 | memberservice (推測) | pricecentermanage 僅讀取 gameusers 資料用於報表,不處理會員生命週期 |
| 訂閱付款處理 | paymentservice (推測) | gamesublogs 僅供查詢交易記錄,實際金流與訂閱邏輯由專門支付服務處理 |
| 即時賽事資料推送 | realtimeservice (推測) | 本服務負責爬蟲配置與狀態監控,實際賽事資料推送由即時服務負責 |
| 封禁帳號決策 | moderationservice (推測) | gameusers_banned 僅供本服務查詢封禁狀態,封禁決策與執行由稽核服務負責 |
| 活動結算邏輯 | predictsettlement (推測) | 本服務僅管理預測活動週期與設定，實際計算 winneraccounts 利潤點數由結算服務執行 |
| 預測週期開獎/派彩 | predictsettlement (推測) | betpool_games 的 winresult 寫入與 payout 切換不由 pricecentermanage 處理 |
| 投注金流扣點 | userwalletservice (推測) | betpool_bets 的 betzcoin 異動應由錢包服務寫入，後臺管理只讀 |
| VIP 權限判斷 | memberservice (推測) | betpool_games.viponly 僅為標記，實際檢查用戶 VIP 資格由會員服務負責 |

---

## 常見錯誤

- ❌ **直接操作 member.gameusers 修改 status** → ✅ member 資料由會員服務統一管理,pricecentermanage 只讀
- ❌ **WHERE email LIKE '%@example.com'** → ✅ email 有索引但不支援前綴模糊查詢,改用 `forbidden_email_domains` 黑名單比對或由會員服務提供專用 API
- ❌ **Redis Key 不加前綴直接存** → ✅ 統一加上業務前綴(如 `AppDevices`、`NotificationTopics`),避免與其他服務衝突
- ❌ **查詢報表不限日期區間** → ✅ memberdailyreport/predictdailyeport 必須指定 `sdate` 與 `edate`,避免全表掃描超時
- ❌ **刪除 Redis 快取後未通知相關服務** → ✅ 刪除 `NotificationMessages` 等快取時,需確認是否有前端服務依賴該快取,避免短時間內大量 DB 查詢
- ❌ **直接 UPDATE activities_record.winbets 追加注單** → ✅ winbets 為 list 類型，應由對賬服務以 `list.append` 方式新增；人工 SET 可能覆蓋歷史數據
- ❌ **WHERE site = '' 省略條件讀 activities_winneraccounts** → ✅ 必須指定 site + activityevent + cid 三欄位；省略任一條件會觸發全 Keyspace 掃描
- ❌ **SET betpool_games.zcoinprice 調整已有遊戲的牌價** → ✅ zcoinprice 僅在建局時寫入；若要改價需開新局
- ❌ **直接回傳 betpool_bets.betzcoin 給前端排行榜** → ✅ 金額欄位只內部用作對賬，前端排行改回傳 profitpoint（非實際金額）
- ❌ **Redis 快取 PredictGame 永久未清理** → ✅ 遊戲 status / payout 變更時必須主動 DEL，否則前端可能顯示過期遊戲狀態

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter keyspace | owner / writer / reader | Schema：[db/pricecenter.json](../../db/pricecenter.json) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **accounts_{source}.password**：密碼欄位，僅透過帳號管理 API 寫入；須避免明文儲存或暴露於 log
- **accounts_{source}.phone**：電話號碼（選填），僅透過帳號管理 API 寫入；應進行部分遮蔽（如 middle 4 碼）後再儲存，不可以明文形式記錄於 log 或返回給非管理員用戶
- **accounts_{source}.username**：使用者名稱（選填），僅在管理後台設定，不得包含敏感個資或密碼
- **accounts_{source}.enabled**：啟用狀態，僅能由 `ISysManagerProvider.UpdateAccountStatus` 設定為 0（停用）或 1（啟用）；不可與 `closetime` 同時異動（關閉帳號時應只寫 `closetime`）
- **accounts_{source}.handler**：為 `map<text, text>`，Key 為機器名稱，Value 為心跳時間戳；寫入時須確保不覆蓋其他機器的 handler 資訊（應使用追加或合併方式，不可直接整筆 SET）
- **accounts_{source}.closetime**：僅在關閉帳號（`closeAccount`）時寫入；正常啟用狀態下不應設定此欄位
- **agents.lastupdtime**：為 `map<varchar, bigint>`，Key 為欄位名稱（機器名），Value 為時間戳；只應由 `agents_lastupdtime` 相關 API 以合併方式更新特定機器時間，不可直接 SET 整個 map
- **agents.minworks**：最小工作進程數（int），僅由管理後台設定，值不可小於 0
- **machines.machinename**：主鍵，新增機器後不可修改名稱；若需改名應刪除後重建
- **machines.adddate**：新增機器時由系統自動設為當前時間，不可手動指定或修改
- **machines.status**：機器狀態（如 `online`、`offline`），僅可由監控服務或管理 API 變更，避免直接 DB 操作
- **machines.controllerstatus**：控制器狀態，僅由控制器服務更新，不可直接手動 SET
- **machines.crawlerservicestatus**：為 `map<text, text>`，Key 為服務名稱，Value 為狀態；寫入時應合併更新，不可直接 SET 整個 map 而覆蓋其他服務狀態
- **extension_version.version**：版本號，僅透過版本管理 API 寫入；不可隨意 UPDATE，主鍵 `site` 不可變更
- **actionlog.date**：分區鍵，必須為當日實際日期，不可未來日期
- **actionlog.addtime**：操作時間戳，必須由系統自動生成，不可手動指定或回溯
- **actionlog.user**：執行使用者，必須為當前已認證的操作者，不可偽造或手動錯填
- **actionlog.gametype**：必須為系統定義的有效遊戲類型枚舉值，不可寫入未定義的類型
- **actionlog.detail**：操作詳情，須為合法 JSON 字串，且不得包含明文密碼或未脫敏的個資（如手機號碼）

### 讀取規則

- **accounts_{source} 查詢**：`WHERE account = ?` 為必要條件，不可省略 `account` 進行全表掃描
- **agents 查詢**：必須同時指定 `WHERE site = ? AND gametype = ?`，不可省略任一條件；若需查詢某站點所有遊戲類型，應分批指定 gametype 或使用迭代，避免全 Keyspace 掃描
- **machines 查詢**：系統監控頁面讀取時，按 `status` 過濾僅顯示線上機器（`status = 'online'`），避免回傳離線或停用機器
- **extension_version 查詢**：`WHERE site = ?` 為必填條件，不可省略 site
- **Notification_Topics / Notification_Messages 查詢**：`WHERE enabled = 1` 僅顯示已啟用的主題與訊息，避免回傳已停用或軟刪除的資料
- **Sport.memberdailyreport / predictdailyeport 查詢**：須指定 `WHERE Reportdate >= ? AND Reportdate <= ?` 日期區間，不可無限制查詢
- **actionlog 查詢**：必須以 `date` 為分區起點，例如 `WHERE date >= ? AND date <= ?`；可選加入 `user`、`gametype` 等聚簇鍵進一步過濾，避免全分區掃描；分頁時可利用 `addtime` 排序，不允許不帶 `date` 的查詢

### 不可回傳欄位

- **accounts_{source}.password**：登入密碼，任何對外 API 皆不可回傳
- **accounts_{source}.phone**：電話號碼，除管理後台權限外，一般查詢不應完整暴露
- **actionlog.detail**：若內含密碼或機敏個資，回傳前應進行攔截或脫敏處理（由服務層管控）

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| GET/SET | `NotificationTopics` | 查詢/更新通知主題時 | Hash 結構，field 為 tid；DB 更新時 DEL |
| GET/SET | `NotificationMessages_{hashKey}` | 查詢/更新通知訊息時 | Hash 結構，field 為 message id；DB 更新時 DEL |
| GET/SET | `SiteMails_{account}` | 查詢/更新用戶站內信時 | Hash 結構，field 為 mail id；讀取狀態更新時 DEL |
| DEL | 以上所有 Key | 管理後台手動刪除快取或 DB 資料變更時 | 主動刪除，確保快取與 DB 一致性 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 遊戲平台帳號密碼加密儲存 | 加密／憑證服務 | pricecenter 僅儲存 password 欄位，實際加密與 Hash 邏輯應由專屬服務處理 |
| 爬蟲實際執行與資料爬取 | crawler service | pricecentermanage 僅管理爬蟲帳號狀態、機器資訊與爬蟲配置，不執行爬蟲工作 |
| 報表資料的真實寫入 | report service（推測） | memberdailyreport / predictdailyeport 的寫入由其他服務負責，pricecentermanage 僅讀取 |
| 通知訊息的推送 | notification service | pricecentermanage 僅管理通知內容與主題設定，實際推送（email、APP push）由通知服務執行 |
| 操作日誌長期歸檔 | 日誌歸檔服務（推測） | actionlog 僅保存近期操作記錄，長期歸檔與離線分析由專門的日誌服務負責 |
| 機器健康檢查與自動上下線 | monitoring service | machines 的狀態心跳與上下線決策由監控服務負責，本服務僅提供機器查詢與配置界面 |
| 爬蟲代理（agents）的工作分配與負載均衡 | scheduler service | 本服務僅提供 agents 配置管理，實際任務分配由調度服務執行 |

---

## 常見錯誤

- ❌ **直接 UPDATE accounts_{source}.password 未經加密** → ✅ 密碼應透過專用 API 寫入，並確保已加密或雜湊
- ❌ **WHERE enabled = ? 未帶 account 主鍵進行查詢** → ✅ 查詢 accounts_{source} 必須以 account 為過濾條件，不得全表掃描
- ❌ **SET accounts_{source}.handler 時覆蓋其他機器資訊** → ✅ 應先讀取 handler map，僅新增或更新對應機器 Key，而非直接 SET 整個欄位
- ❌ **未過濾 machines.status 直接回傳所有機器** → ✅ 讀取機群時應加上 `status = 'online'` 條件，避免回傳已離線或暫停的機器
- ❌ **省略 agents 查詢的 site 條件** → ✅ agents 表須同時指定 site 與 gametype，否則可能造成全 Keyspace 掃描
- ❌ **查詢 actionlog 不帶 date 條件** → ✅ actionlog 以 date 為分區鍵，查詢必須指定 date（範圍），否則將導致全 Keyspace 掃描
- ❌ **在 actionlog.detail 中記錄 accounts 密碼** → ✅ 寫入 detail 前應檢查並排除密碼欄位，或先脫敏再寫入
- ❌ **寫入 accounts_{source} 時將 phone 號碼以明文記錄於 log** → ✅ 電話號碼應遮蔽中間幾碼（如 `0987****12`），避免個資外洩
- ❌ **修改 machines.machinename** → ✅ 不可直接修改主鍵，若需更名應刪除舊機器並重新新增
- ❌ **直接 SET machines.crawlerservicestatus 覆蓋整個 map** → ✅ 應讀取當前 map，只更新特定服務的狀態，避免丟失其他爬蟲服務的狀態記錄
- ❌ **設定 agents.minworks 為負數** → ✅ 最小工作進程數必須為 >= 0 的整數
- ❌ **在 actionlog.user 填入非操作者帳號** → ✅ user 欄位必須為當前已認證的用戶，不可偽造或錯填

---

## sport

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport MySQL | reader / writer（通知、社群群組） | Schema：[db/sport.md](../../db/sport.md) · 語意：[db/sport-detail.md](../../db/sport-detail.md) |

### 寫入限制

- **Notification_Messages.Enabled**：僅能由通知管理 API 設定為 0（停用）或 1（啟用），不可設為其他值。
- **Notification_Messages.Title**：須為合法 JSON 格式的多語言結構（如 `{"zh-TW":"...","en-US":"..."}`），不可寫入純文字或語法錯誤的 JSON。
- **Notification_Messages.TW_Content / EN_Content / CN_Content / JP_Content / TH_Content**：對應語系的內容必填（至少 TW_Content 不可為空），若無適當內容應提供預設佔位訊息，不可留空白或 NULL。
- **Notification_Topics.Enabled**：僅能設為 0 或 1；更新時必須保留既有主題 ID，不可直接刪除後重建導致歷史訊息孤兒。
- **Notification_Topics.NameMap**：為多語系名稱 JSON 字串，格式須與前端一致，不可包含未定義語系 Key。
- **Notification_SiteMails.ReadStatus**：僅能從 0（未讀）改為 1（已讀），不可逆轉或設為其他值；且必須由站內信服務依據用戶操作觸發。
- **Community_Groups.Enabled**：僅能設為 0 或 1，啟用/停用群組時須記錄操作日誌，不可直接 DELETE 群組資料。
- **Community_Groups.Name**：為多語系 JSON（如 `zh-TW`、`en-US`），格式須與前端約定一致；不可寫入未定義的語系 Key。
- **GameUsers_Wallet.Balance / LastUpdateTime**：pricecentermanage **禁止直接寫入**錢包餘額或更新時間，這些欄位由遊戲錢包服務專責管理。
- **GameUsers_Wallet_Transactions.Amount / Type / TypeInfo**：禁止透過管理後台人工新增交易記錄，所有交易流水應由對應的遊戲或錢包結算服務自動產生。

### 讀取規則

- **BK_SitePlayers 查詢**：若需撈取多名球員資料，建議加上 `WHERE League = ? AND Year = ?` 或 `WHERE Site = ?`，避免因缺漏條件導致全表掃描。
- **ChatRoomHistories_Backup 查詢**：`WHERE GID = ?` 為必要條件，必須指定群組 ID 以限定範圍；不可僅以 `Account` 或關鍵字進行全表掃描。
- **Community_Groups 列表**：對外展示時應過濾 `WHERE Enabled = 1`，不應回傳已停用的群組。
- **GameUsers_Wallet 查詢**：僅能以 `AuthKey` 主鍵查詢單一用戶錢包，嚴禁無條件批次撈取所有用戶餘額。
- **GameUsers_Wallet_Transactions 查詢**：必須搭配 `AuthKey` 與時間範圍（如 `TDate`）過濾，避免全表掃描；查詢結果分頁建議使用 `TID` 或 `AddTime` 排序。
- **Notification_Messages 查詢**：應以 `TID` 為主條件（必要）及 `Enabled = 1` 過濾；若需撈取特定 ID，可額外帶入 `ID`。
- **Notification_Topics 查詢**：後台管理頁面可查詢所有主題，但對外公告端點須加上 `WHERE Enabled = 1` 過濾。
- **Notification_SiteMails 查詢**：必須以 `Account` 作為分區條件，並可選加上 `ReadStatus` 過濾；不可跨帳號全表掃描。

### 不可回傳欄位

- **GameUsers_Wallet.Balance**：錢包餘額屬敏感財務數據，僅限有管理員權限且用途為稽核時方可回傳；一般 API 不應暴露。
- **GameUsers_Wallet_Transactions.Amount**：交易金額同屬機敏，除稽核用途後台外，不可回傳。
- **ChatRoomHistories_Backup.Message**：聊天內容涉及用戶隱私，回傳前需確認請求者有對應群組查閱權限或為管理員；直接對外公開列表不應包含訊息全文。
- **Community_Groups.Owner**：群主帳號可能暴露用戶社交關係，除管理員審查外，不應於一般列表 API 回傳。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| GET/SET | `NotificationTopics` | 查詢/更新運動通知主題時 | Hash 結構，field 為 tid；DB 變更時 DEL |
| GET/SET | `NotificationMessages_{hashKey}` | 查詢/更新通知訊息時 | Hash 結構，field 為 message id；DB 變更時 DEL |
| GET/SET | `SiteMails_{account}` | 查詢/更新用戶站內信時 | Hash 結構，field 為 mail id；讀取或 DB 更新時 DEL |
| DEL | 以上所有 Key | 管理後台手動刪除快取或 DB 資料變更時 | 主動刪除，確保快取與 DB 一致性 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 錢包餘額變更與交易記錄產生 | 錢包/遊戲服務 | GameUsers_Wallet 與其 Transactions 表的寫入由專屬遊戲服務處理，pricecentermanage 僅讀取與查詢 |
| 聊天訊息發送與清理 | Chat service | ChatRoomHistories_Backup 為備份表，即時聊天推送與歷史管理由聊天服務負責 |
| 球員數據爬取與更新 | Sports data service | BK_SitePlayers 的寫入由賽事資料爬取或同步服務負責，管理後台僅查詢使用 |
| 站內信實際推送與通知發送 | Notification service | pricecentermanage 管理通知模板與主題，但即時推送（APP、WebSocket）由通知服務處理 |

---

## 常見錯誤

- ❌ **直接 SQL UPDATE GameUsers_Wallet SET Balance = ? 試圖調整餘額** → ✅ 餘額變更須透過錢包服務的交易 API，本服務不可直接寫入。
- ❌ **查詢 ChatRoomHistories_Backup 不帶 GID，試圖全表搜尋關鍵字** → ✅ 必須指定 GID 分區鍵，否則將引發全表掃描並影響性能。
- ❌ **Notification_Messages 內容留空或 JSON 格式錯誤** → ✅ 寫入前必須驗證多語言內容格式與必填欄位，避免前端顯示異常。
- ❌ **停用 Community_Groups 時直接 DELETE** → ✅ 應以 `Enabled = 0` 進行軟停用，並記錄操作日誌，防止關聯資料孤兒。
- ❌ **未過濾 Enabled 即回傳 Notification_Topics 或 Messages** → ✅ 對外 API 須加上 `Enabled = 1` 條件，避免誤推已停用的主題。
- ❌ **查詢 GameUsers_Wallet_Transactions 未限制時間範圍** → ✅ 必須結合 AuthKey 與日期範圍（如 TDate）進行過濾與分頁。