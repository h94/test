# pricecentersite — DB 操作邊界

> 產出時間：2025-02-21 09:30  
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）  
> ⚠️ AI 產出，需資深工程師審核後生效

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member keyspace | reader / writer | Schema：[db/member.md](../../db/member.md) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **gameusers.password**：僅註冊（Register）、重設密碼（ResetPassword）、變更密碼（ChangePassword）可寫入；須經雜湊處理；不可明文儲存
- **gameusers.authkey**：註冊時由系統產生（SHA256 雜湊）；不可由外部直接指定；第三方登入透過 `tryLogin` 產生
- **gameusers.email**：註冊時須驗證格式與禁用網域（forbidden_email_domains）；索引欄位，變更需謹慎
- **gameusers.memberships**：訂閱成功後由 `gamesublogs` 同步更新；不可直接修改；停用訂閱時須移除對應值
- **gameusers.site / siteid**：第三方登入時寫入（Apple/Google/Discord/Line/Email/X/Partner）；註冊後不可變更
- **gameusers.focus_account / follow_account / black_account**：僅透過專屬 API（InsertGameUserFocusAccount/SetGameUserBlackAccount）新增/移除元素；不可直接覆寫整個 list
- **gamesublogs.subendtime**：由訂單成功後計算（方案有效期+當前時間或前次到期時間）；續訂時需比對前次記錄以決定起始時間
- **gamesublogs.autosub**：定期扣款訂單須設為 true；一次性訂單為 false；影響自動續訂判斷
- **gameusers_banned.authkey**：封禁前須檢查此表；若已存在記錄則不可重複登入

### 讀取規則

- **登入驗證**：gameusers 須 WHERE `email=? AND status=1`；被封禁帳號需額外查詢 gameusers_banned 並檢查 endtime 是否仍有效
- **訂閱狀態查詢**：gamesublogs 須 WHERE `authkey=?` ORDER BY `subtime DESC, addtime DESC`；取最新記錄並比對 subendtime 與當前時間
- **VIP 權限檢查**：結合 gameusers.memberships 與 gamesublogs.subendtime；memberships 非空且對應訂閱未過期時才有效
- **推薦關係查詢**：gameusers.showcode 作為推薦碼；註冊時可傳入他人 showcode 建立推薦關係（用於分潤報表）
- **社群文章過濾**：查詢時需排除 gameusers.black_account 清單中的帳號內容；避免已封鎖使用者內容出現
- **第三方帳號關聯**：WHERE `site=? AND siteid=?` 查詢 gameusers；若不存在則自動註冊；Apple 額外查詢 appleinfos_game 表

### 不可回傳欄位

- **gameusers.password**：任何對外 API（包含 GetGameUserData）皆不可回傳；重設密碼僅接受新密碼，不回傳舊密碼
- **gameusers.authkey**：僅登入成功時回傳一次作為 Token；其他查詢使用者資訊時不可外洩
- **gamesublogs 完整記錄**：對外僅回傳訂閱狀態（是否 VIP、到期時間）；不可暴露交易單號（tradeno）、支付方式細節
- **gameusers_banned.description**：封禁原因僅供內部管理；對被封禁用戶僅回傳「帳號已停用」訊息

---

## payment

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra payment keyspace | reader / writer | Schema：[db/payment.md](../../db/payment.md) · 語意：[db/payment-detail.md](../../db/payment-detail.md) |

### 寫入限制

- **paymethods_sport.enabled**：僅系統管理人員或後台工具可變更；一般 API 僅讀取，不可寫入
- **products_activity.price / quantity / status**：由商品管理後台統一維護；前端兌換 API 僅能讀取，不得直接寫入
  - 兌換時須使用 Cassandra LWT（`IF quantity >= ?`）避免超賣
- **products_activity_redeem_logs.status**：0 = 待處理，1 = 通過，2 = 拒絕
  - 僅後台審核流程可更新為 1 或 2；一般 API 寫入時初始值固定為 0
- **rechargeplans_newlottery.amount / coin / currency / enabled / starttime / endtime**：僅後台可新增/啟用/停用方案；前端不可直接異動
- **commissions_betpool_newlottery.betpool / id**：由產生佣金之服務（如 GameResultService）寫入；本服務僅讀取用於報表展示
- **reports_sport.year / month**：由排程批次產生，不可手動寫入

### 讀取規則

- **支付方式列表**：`paymethods_sport` 須 WHERE `enabled=1` 回傳；不可露出已停用方式
- **商品列表**：`products_activity` 須 WHERE `status=1（上架）`；庫存量（quantity）僅用於前端顯示，不可作為兌換唯一判斷（需 LWT）
- **商品兌換記錄**：`products_activity_redeem_logs` 查詢時須依 `site + activityevent + account` 為分區鍵，避免跨分區掃描
- **充值方案列表**：`rechargeplans_newlottery` 須 WHERE `enabled=1` 且 `starttime <= 現在 <= endtime`；過期或未開始方案不回傳
- **佣金記錄**：`commissions_betpool_newlottery` 通常依 `betpool` 查詢單一彩池記錄；大量查詢時應分頁（LIMIT 100）

### 不可回傳欄位

- **commissions_betpool_newlottery.source_cid**：來源客戶 ID 僅供內部佣金計算，不對前端顯示
- **rechargeplans_newlottery.lastupdatetime**：內部維護時間戳，無需回傳

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra predict keyspace | writer / reader | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **betpool_games.status / payout / winresult**：僅由 GameResultService（或對應結算服務）依據比賽結果寫入；本服務（PredictCenterSite）僅讀取，不可直接修改此欄位
- **betpool_games.basicprofitzcoin / bonusprofitzcoin / feedrate / zcoinprice**：由上游或管理後台設定；本服務僅讀取用於建立投注時計算派彩
- **betpool_bets.winlose / profitzcoin**：僅由結算服務（如 GameResultService）在比賽結束後寫入；本服務建立投注時不可預設或寫入此值
- **activities_cycles**：由排程或管理後台新增/更新週期設定；本服務（ActivityProcess.GetNowActivityCycleSetting）僅讀取
- **activities_winneraccounts**：由排程或結算服務寫入贏家名單；本服務僅讀取用於排行榜展示
- **activities_record.winbets**：商店兌換（RedeemStoreProduct 流程）執行成功後由本服務寫入；寫入時需確保該筆投注確實為獲勝狀態
- **site（所有表）**：由 appsettings.json 的 CassandraSettings Keyspace 隱含決定；每個請求的 site 不可與其他不同 keyspace 的站點混淆

### 讀取規則

- **有效投注查詢（CreateHotBetPoolInplayGamePredictBets）**：`betpool_games` 須 WHERE `hot=true AND payout=false` 且 `endtime` > 當前時間戳；僅回傳尚未結束且未派彩的熱門遊戲
- **遊戲狀態過濾**：查詢 `betpool_games` 時須依 `status` 過濾（0 未開始、1 進行中、2 已結束）；前端顯示僅限 status=1 或 2（已結束展示結果）
- **活動週期查詢（GetNowActivityCycleSetting）**：`activities_cycles` 須 WHERE `site=? AND activityevent=? AND cid=?` 且 `startdate/starttime <= 現在 <= enddate/endtime`；回傳唯一有效週期
- **兌換記錄查詢**：`activities_record` 須 WHERE `site=? AND eventname=? AND account=?` 取得單一用戶的活動記錄；不支援全站掃描
- **排行榜查詢**：`activities_winneraccounts` 須 WHERE `site=? AND activityevent=? AND cid=?`；依 `rank` 排序回傳；無 rank 則依 `profitpoint` 降冪排
- **VIP 遊戲限制**：`hot` 與 `viponly` 雙重過濾；若 `viponly=true`，非 VIP 用戶的 API 請求不可回傳此遊戲

### 不可回傳欄位

- **betpool_bets.profitzcoin / winlose**：在未結算（payout=false）前禁止預測或回傳；僅結算服務寫入後才可回傳
- **betpool_bets.id**：作為內部主鍵，通常不回傳給前端（除非特定查詢單筆注單）；前端使用 `gid` + `account` 作為識別
- **accounts（特定情境）**：排行榜 `activities_winneraccounts` 可回傳帳號，但若站點有隱私政策要求，則須遮蔽部分字元
- **betpool_games.betoptions 原始 key**：前端應顯示語系對應的顯示值（來自 `names` map），而非內部識別 key
- **activities_record.winbets 完整清單**：回傳時可能僅需清單計數（`len(winbets)`），而非每個投注 ID 明細

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter keyspace | reader / writer | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **accounts_{site}.password**：僅可透過註冊或密碼管理 API 寫入；須經雜湊處理；不可明文儲存或寫入 log
- **accounts_{site}.handler**：僅提供給對應站點的管理後台或特定內部 API 寫入；前端使用者註冊時不可自行設定
- **accounts_{site}.enabled**：僅後台管理工具可變更；註冊 API 寫入時預設為 1（啟用）；一般 API（如登入）不可異動此欄位
- **accounts_{site}.closetime**：僅在帳號關閉/刪除流程由系統寫入格式 `yyyy-MM-dd HH:mm:ss`；非手動寫入；註冊時為空
- **sleeprecords**（若存在）：由排程批次寫入睡眠紀錄；本服務僅讀取用於報表展示

### 讀取規則

- **登入驗證**：`accounts_{site}` 須 WHERE `account=?`；結果取出後須檢查 `enabled=1` 且 `closetime` 為空或已過期才視為有效帳號
- **站點帳號配置查詢**：查詢 `accounts_{site}` 時僅回傳 `account, username, phone, handler` 等非敏感欄位；不可回傳 `password`

### 不可回傳欄位

- **accounts_{site}.password**：任何對外 API 皆不可回傳；內部錯誤訊息亦不可暴露雜湊值
- **accounts_{site}.closetime**：對外 API 若無必要（如帳號狀態查詢）不應回傳；僅後台管理可查看

---

## community

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra community keyspace | reader / writer | Schema：[db/community.md](../../db/community.md) · 語意：[db/community-detail.md](../../db/community-detail.md) |

### 寫入限制

- **newlottery_forums.id**：主鍵，僅論壇創建時指定，不可修改。
- **newlottery_forums.status**：僅後台管理 API 可寫入（0=停用、1=啟用、2=封存）；一般 API 僅讀取。
- **newlottery_forums.names**：多語言名稱 map，僅後台或專用編輯 API 可寫入；前端不可直接修改。
- **newlottery_forums.country_code**：歸屬國家代碼，創建時指定，一般不可變更。
- **newlottery_forums.icon / edit_timestamp**：icon 由後台上傳更新；edit_timestamp 由系統自動寫入編輯事件，不可手動設定。

### 讀取規則

- **論壇列表查詢**：預設須 WHERE `status=1`（啟用）回傳；若需顯示已停用論壇需有管理權限。
- **依國家過濾**：可選用 `country_code=?` 進行區域化顯示，無則回傳全部啟用論壇。
- **名稱顯示**：前端應根據使用者語系從 `names` map 中提取對應語言名稱；若無則回傳預設語言（如 `en`）或 id。

### 不可回傳欄位

- **newlottery_forums.edit_timestamp**：編輯時間戳為內部維護資訊，對外 API 無需回傳（除非後台管理需要）。
- **newlottery_forums.names 完整 map**：對外 API 應只回傳當前語系對應名稱，不應暴露全部語言映射（若前端需轉語系則可例外，但需評估資安風險）。

---

## product

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra product keyspace | reader / writer | Schema：[db/product.md](../../db/product.md) · 語意：[db/product-detail.md](../../db/product-detail.md) |

### 寫入限制

- **products_activity.price / quantity / status**：由後台管理系統維護；前端兌換 API 僅能讀取，不可直接寫入。兌換時必須使用 Cassandra LWT（`IF quantity >= ?`）原子扣減庫存，防止超賣。
- **products_activity_redeem_logs.status**：初始值固定為 `0`（待處理）；僅後台審核流程可更新為 `1`（通過）或 `2`（拒絕）；一般 API 不可異動。
- **products_store.price / status / sequence**：由後台管理 API 統一維護；前端不得直接修改。StoreService 在兌換流程中僅讀取價格與狀態，不負責寫入。
- **product_store_redeem_logs**：兌換請求由前端提交，寫入時 `account`、`address`、`phonenumber`、`recipient` 等欄位需驗證格式（如電話號碼、地址不為空）；`status` 初始為 `"pending"`（待處理），後續由系統或後台更新。
- **product_store_stock_logs**：庫存變動記錄僅由內部服務（如兌換成功後的扣減邏輯）自動寫入；不可由外部 API 直接插入或修改。

### 讀取規則

- **商品列表（常規商店）**：`products_store` 須 WHERE `status='上架'`；必要時依 `sequence` 排序回傳。
- **活動商品列表**：`products_activity` 須 WHERE `status=1`（上架）且 `quantity > 0`（仍有庫存）；已售罄（status=2）商品不回傳。
- **兌換記錄查詢（常規商店）**：`product_store_redeem_logs` 查詢時須至少指定 `pclass` 分區鍵，避免全分區掃描；通常依 `pclass + account` 查詢特定用戶的兌換紀錄。
- **庫存變動查詢**：`product_store_stock_logs` 依 `pclass + pid` 讀取歷史變動，常用於庫存審計或後台報表。
- **活動兌換記錄查詢**：`products_activity_redeem_logs` 須以 `site + activityevent + account` 為分區鍵查詢，不支援跨分區全文檢索。

### 不可回傳欄位

- **product_store_redeem_logs 中的 address / phonenumber / recipient**：對一般用戶或第三方 API 回傳時須遮蔽部分資訊（如手機號顯示 `138****1234`）；僅用戶本人或後台可查看完整資訊。
- **product_store_redeem_logs.cheadshot / cmemo**：客服填寫的頭像與內部備註，不對前端顯示。
- **products_store.originalprice**：原價僅供後台或特殊展示，對外 API 通常不須回傳。
- **products_activity.status**：內部狀態值（0=下架, 1=上架, 2=售罄），僅後台管理需要，前端不應暴露原始數值。
- **product_store_stock_logs 完整記錄**：一般 API 不應回傳庫存變動細節，僅提供當前庫存總量或變動摘要。

---

## stock

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| MySQL stock | owner | Schema：[db/stock.md](../../db/stock.md) · 語意：[db/stock-detail.md](../../db/stock-detail.md) |

### 寫入限制

- **users.Password**：僅註冊與密碼重設 API 可寫入；須經雜湊處理；不可明文儲存或輸出
- **users.Enabled**：僅後台管理工具可變更；註冊 API 寫入時預設為 1；一般 API 不可直接 UPDATE
- **users.SubEndTime**：僅付款成功後由訂閱服務寫入（推測透過 PaymentService 回調）；本服務不可直接修改
- **favoriterule.NeedSend / FirstMatch**：僅規則比對流程（PredictProcess）自動寫入；前端 API 不可直接設定
- **favoriterule.Country / favoritestock.Country**：預設值為 `tw`；使用者自行設定時僅能選用系統支援的國家代碼（對應 `rules.Countries`）
- **sublogs**：紀錄由付款服務寫入（`TradeNo`、`SubID`、`SubRank` 由 PaymentTransfer 提供）；本服務僅讀取用於展示或判斷訂閱狀態
- **messagelog.SendStatus**：初始值為 0（待發送）；發送成功後由郵件/簡訊服務更新為 1 或 2；本服務不可直接寫入
- **rules** 與 **options**：由管理後台或排程維護；前端 API 不可直接新增/修改/刪除

### 讀取規則

- **使用者登入/驗證**：`users` 須 WHERE `Account=? AND Enabled=1`；不可回傳已停用帳號
- **規則比對**：`favoriterule` 須依 `User` 查詢；比對時需檢查 `NeedSend` 與 `FirstMatch` 以決定是否觸發通知
- **訂閱有效性檢查**：`users.SubEndTime` 與 `sublogs` 最新記錄比對；若 `SubEndTime` 早於當前時間則視為已過期
- **訊息記錄查詢**：`messagelog` 常依 `Account + Date` 查詢；需注意分區鍵為 `Date + Account`
- **系統規則選項**：`rules` 查詢時須 WHERE `Enabled=1`；`options` 同樣只回傳 `Enabled=1` 的項目
- **國家過濾**：`favoriterule` 與 `favoritestock` 可選 `Country=?` 進行區域化顯示；不帶條件時回傳全部

### 不可回傳欄位

- **users.Password**：任何對外 API 皆不可回傳
- **users.ChatID**：僅用於後端發送訊息（Telegram），不對前端露出
- **sublogs.TradeNo**：交易單號僅供內部對帳，不對使用者公開
- **messagelog.MsgContent**：對一般查詢不回傳訊息完整內容（僅提供狀態與時間）；若需顯示則須遮罩敏感資訊
- **favoriterule.Value**：內含規則參數（JSON），對外僅回傳規則摘要即可

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `AuthToken:{email}` | 活動驗證碼發送（SendActivityVerifyMail） | 300 秒；同一 email 60 秒內不可重複發送（檢查 CreateCount 與 LastSendTime） |
| SET / GET | `GameUserLastActionTime:{authKey}` | 更新會員最後活動時間（setGameUserLastActionTime） | 300 秒；快取 gameusers.lastactiontime 欄位，減少 Cassandra 寫入 |
| SET / GET | `ResponseCacheInfo:{cacheKey}` | API 回應快取（如廣告、公告） | 依業務設定（通常 300-600 秒）；降低外部 API 呼叫與 DB 查詢 |

（當前程式碼中未明確使用 stock 相關的 Redis Key；未來若需快取使用者收藏清單或規則比對結果，可依此格式擴充）

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 預測投注結算 | GameResultService | 本服務僅建立 PredictBet 並關聯社群文章；賽事結果與輸贏計算由 GameResultService 處理 |
| 活動週期創建與更新 | 管理後台或排程服務 | 本服務僅讀取 `activities_cycles` 作為有效週期判斷；不負責新增/編輯週期 |
| Z 幣餘額變動通知 | NotificationService | 錢包交易成功後發送站內信由 NotificationService 負責；本服務僅記錄交易（gameuserwalletransactions） |
| ECPay 金流回調處理 | PaymentService | 本服務不處理 ECPay 定期扣款通知；訂單狀態更新與 gamesublogs 新增由 PaymentService 統一管理 |
| 社群文章內容審核 | （人工或外部審核系統） | 本服務僅驗證格式（10-2000 字）；違規內容偵測與刪除需另外實作 |
| 賽事即時賠率更新 | OddsDataService | PredictBet 建立時抓取當下賠率；後續賠率變動不影響已建立的投注記錄 |
| pricecenter 帳號密碼重設 | 認證中心服務（AuthService） | 本服務不直接處理密碼重設邏輯；密碼重設請求應轉發至專用認證服務 |
| **訂閱金流寫入 sublogs** | **PaymentService / SubscriptionService** | stock 資料庫的 `sublogs` 僅由付款結果回調寫入，本服務不直接操作 |
| **訊息實際發送** | **MailService / SMSService** | stock 的 `messagelog` 僅記錄待發送任務，實際發送由其他服務執行並更新狀態 |
| **常見問題（FAQ）內容管理** | **後台管理系統** | `questions_sport` / `questions_stock` 的增刪改由後台負責；本服務僅提供查詢 API |
| **意見回饋狀態流轉** | **客服管理後台** | 回饋的 `status` 更新（處理中、已結案）由客服系統觸發；本服務不擅自變更 |
| **商務訊息回覆發送** | **客服系統 / MailService** | `businessmessages` 的 `respcontent` 寫入後，實際郵件發送由外部服務執行；本服務僅記錄內容 |

---

## 常見錯誤

- 
---

## feedback

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra feedback keyspace | writer / reader | Schema：[db/feedback.md](../../db/feedback.md) · 語意：[db/feedback-detail.md](../../db/feedback-detail.md) |

### 寫入限制

- **feedbacks_sport / feedbacks_stock.status**：初始值固定為 `0`（未處理）；僅後台客服 API（管理權限）可更新為 `1`（處理中）、`2`（已結案）；使用者提交時只能寫入 `0`
- **feedbacks_sport / feedbacks_stock.respcontent**：僅管理員回覆時可新增元素（append 至 list）；使用者只能寫入 `problem` 欄位，不可碰觸此欄
- **feedbacks_sport / feedbacks_stock.adminimgpath**：僅管理員上傳圖片時可寫入；一般 API 不得異動
- **feedbacks_sport / feedbacks_stock.email**：使用者提交回饋時可寫入自己的信箱；格式需驗證；若為登入會員，應從帳號資訊自動帶入，不可由前端任意更改
- **feedbacks_sport / feedbacks_stock.problem**：使用者提交時寫入，每個元素為 JSON 物件 `{"DateTime": "...", "Message": "..."}`；前端傳入時須驗證 JSON 結構與長度（單則訊息上限 2000 字）
- **businessmessages.sendcontent**：使用者發送商務訊息時寫入；內容需過濾特殊字元並限制長度（上限 1000 字）
- **businessmessages.respcontent**：僅客服/管理員可寫入；寫入後自動更新 `status` 為對應數值（如 1 代表已回覆）
- **businessmessages.status**：系統可自動管理（如 0: 未處理, 1: 已回覆）；客服可手動變更；使用者不可修改
- **topics_sport / topics_stock.enabled**：僅後台管理 API 可切換；查詢時必須過濾 `enabled=1`
- **questions_sport / questions_stock.enabled**：同 topics，僅後台可啟用/停用

### 讀取規則

- **回饋清單查詢（會員）**：`feedbacks_sport` 須 WHERE `account=?`（依帳號）或搭配 `tid=?` 進行主題分類；不可跨使用者查詢
- **回饋清單查詢（後台）**：可依 `tid=?` 掃描，但需分頁（LIMIT 50）；避免全表掃描；可選 `status=?` 過濾
- **FAQ 查詢**：`questions_sport` 須 WHERE `tid=? AND enabled=1` ORDER BY `sort ASC`；依使用者語系從 `question` / `answer` map 中提取對應語言文本
- **熱門問題**：可額外依 `sort` 降序排列，取前 N 筆
- **主題清單**：`topics_sport` 須 WHERE `enabled=1` ORDER BY `sort ASC`；前端依語系提取 `name` map 中的名稱
- **商務訊息查詢**：`businessmessages` 須以 `site=?` 為分區鍵，可額外過濾 `sendermail=?` 或 `status=?`；排序依 `datetime DESC`；不支援跨 site 查詢
- **狀態過濾**：商務訊息若不需全部回傳，前台只應顯示使用者相關的訊息（依 `sendermail` 或關聯帳號）

### 不可回傳欄位

- **feedbacks_sport / feedbacks_stock.email**：公開 API（如其他使用者查看）不可回傳電子郵件；僅使用者本人登入後可查看自己的信箱
- **feedbacks_sport / feedbacks_stock.respcontent（跨使用者）**：使用者僅能看見自己回饋中的管理員回覆；後台可看全部，但 API 應避免暴露其他用戶的對話
- **businessmessages.sendermail**：對外查詢時若為其他使用者的訊息，不得洩漏寄件者信箱；僅個人訊息查詢可回傳本人的
- **businessmessages.respcontent**：若訊息狀態為「未處理」或非目標用戶，前台不應顯示管理員回覆內容；後台管理完整顯示
- **adminimgpath**：僅後台管理可見；一般使用者無需看到管理員上傳的圖片路徑

### Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `feedback_topics:{site}` | 取得主題清單時快取 | 600 秒；減少 Cassandra 讀取，變動時由後台觸發清除（DEL） |
| SET / GET | `feedback_faq:{site}:{tid}` | 取得 FAQ 時快取 | 300 秒；內容較固定，可主動失效 |
| SET | `feedback_user_last_submit:{account}` | 防止使用者短時間內重複提交回饋 | 60 秒，若存在則拒絕寫入，避免濫用 |

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 回饋內容審核與敏感詞過濾 | 外部審核服務 | 本服務僅儲存原始內容；是否包含不當內容需由其他服務或人工判斷後呼叫刪除 API |
| 回饋狀態變更後的通知 | NotificationService | 當管理員回覆或狀態改為「已結案」時，通知使用者由統一通知服務發送，本服務僅提供資料 |
| 商務訊息實際郵件發送 | MailService | `businessmessages` 寫入後，郵件發送由專門的郵件服務透過佇列執行；本服務不直接 SMTP 發送 |
| 圖片上傳與病毒掃描 | ImageService / 安全服務 | 使用者上傳的圖片（`imgpath`）僅儲存路徑；上傳、壓縮、防毒由獨立服務處理 |

### 常見錯誤

- ❌ 查詢 `feedbacks_stock` 時未指定分區鍵 `id`，導致 Cassandra 全表掃描
  ✅ 必須以 `id=?` 或結合 `account` 等條件查詢；若需依 `tid` 查詢，應使用 `feedbacks_sport` 結構（以 `tid` 為分區鍵）
- ❌ 使用者提交回饋時直接寫入 `status=1` 試圖跳過客服處理
  ✅ 後端強制設定 `status=0`，忽略前端傳入的值
- ❌ 管理員回覆時直接覆蓋整個 `respcontent` list，導致歷史對話遺失
  ✅ 回覆應使用 append 操作（`+` 或 `ADD` 語法），保留完整對話串
- ❌ FAQ 查詢時忘記過濾 `enabled=1`，顯示已停用的問答
  ✅ 所有對外 API 必須加上 `enabled=1` 條件；若無符合結果則回傳空陣列
- ❌ 商務訊息查詢時未限制 `site`，跨站查詢導致資料錯誤
  ✅ 每個請求的 `site` 必須從請求上下文取得，並作為強制條件

---