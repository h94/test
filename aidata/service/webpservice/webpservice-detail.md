# webpservice — DB 操作邊界

> 產出時間：2025-01-24 10:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member keyspace | owner / writer / reader | Schema：[db/member.md](../../db/member.md) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **gameusers.authkey**：僅註冊流程可產生並寫入，使用 UUID 生成，不可由外部 API 直接修改
- **gameusers.password**：僅註冊/修改密碼 API 可寫入，須經過加密雜湊處理，不可明文儲存
- **gameusers.email**：註冊時須驗證格式且檢查 forbidden_email_domains 黑名單，註冊後不可修改（需透過專門的變更流程）
- **gameusers.status**：僅管理後台或系統定時任務可修改，前端 API 不可直接變更用戶狀態
- **gameusers.rank / gamecount**：僅遊戲邏輯服務可更新，本服務不直接寫入遊戲相關統計
- **gameusers.renamecount**：每次改名時遞增，需與業務規則（如改名次數上限、冷卻時間）配合檢查
- **gameusers.lastactiontime**：動態更新用戶最後活動時間，僅在用戶進行 API 操作時由服務端寫入，不可由 API 參數直接設定
- **gameusers_banned**：僅封禁管理功能可新增，新增時須同步更新 gameusers.status；刪除（解封）時也須一併還原 gameusers.status
- **gamesublogs**：訂閱記錄僅由付款回調邏輯寫入，不可由一般 API 手動建立或修改
- **forbidden_email_domains**：僅系統管理員可新增/刪除，註冊流程必須檢查此表
- **appleinfos_game**：僅 Apple 登入回調流程可寫入，id / email / name 均來自 Apple ID 授權回應，不可由前端 API 直接提供

### 讀取規則

- **登入驗證**：查詢 gameusers 時須 WHERE `status = 1`（啟用狀態），封禁/未啟用用戶不可登入
- **封禁檢查**：讀取用戶資料時需聯查 gameusers_banned，若存在記錄且 endtime 為空或未過期則拒絕存取
- **email 查詢**：透過 myindex 索引查詢，僅用於註冊時檢查重複及登入驗證，不對外暴露於搜尋功能
- **機器人過濾**：一般用戶列表查詢需排除 gamerobots.account，避免將測試帳號展示給真實用戶
- **訂閱紀錄**：gamesublogs 依 authkey 分區，查詢時須指定 authkey，可依 subtime/tradeno/addtime 排序
- **會員資格查詢**：查詢 gameusers 會員相關功能時，須過濾 memberships 清單中的有效資格，僅回傳仍在有效期內的會員類型
- **關注/黑名單查詢**：查詢 focus_account / black_account / follow_account 時，須限制僅回傳當前用戶自己的列表，不可跨用戶查詢

### 不可回傳欄位

- **gameusers.password**：任何對外 API 回應都不可包含此欄位，包含管理後台查詢
- **gameusers.authkey**：僅用於內部服務間認證與 URL 參數，不應出現在用戶資訊 GET 回應的 body 中（header/token 除外）
- **gameusers_banned.description**：封禁原因屬內部管理資訊，前端僅需知道「已封禁」狀態，不回傳具體原因
- **gameusers.lastchecktime / lastactiontime**：屬於內部監控用時間戳，不對外暴露
- **gameusers_banned.authkey**：封禁記錄的內部分區鍵，不應對外暴露

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra predict keyspace | writer / reader | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **betpool_games.status**：僅遊戲結算或管理後台可修改（0=開放,1=關閉,2=結算），前端 API 不可直接寫入
- **betpool_games.winresult**：僅結算流程設定，不可由外部寫入
- **betpool_games.payout**：僅付款流程設定為 true，不可手動改寫
- **betpool_bets.winlose**：僅結算服務可寫入（win/lose），下注時只可寫入 betoption、betzcoin，不可預設結果
- **activities_cycles**：僅活動管理後台可新增/修改周期，startdate/enddate 不可晚於現在（防止無效周期）
- **activities_record.winbets**：僅結算時由系統更新，不可手動寫入中獎投注列表
- **activities_winneraccounts**：僅活動結算時由系統批次寫入，不可單筆新增或修改帳號、排名

### 讀取規則

- **下注前檢查**：查詢 betpool_games 時須 WHERE `status = 0`（開放）且 `starttime <= NOW` 且 `endtime > NOW`，非開放遊戲不可下注
- **活動周期查詢**：查詢 activities_cycles 時須指定 site，避免跨站資料混雜；僅回傳 enddate 未過期的周期
- **活動中獎名單**：查詢 activities_winneraccounts 時須過濾 site 與 activityevent，防止跨活動洩漏
- **用戶活動記錄**：查詢 activities_record 時須以 account + eventname 為準，只回傳當前用戶自己的記錄

### 不可回傳欄位

- **betpool_games.betoptions**（內部選項映射，前端僅需選項列表，不應暴露原始 key）
- **betpool_games.names**（多語系名稱映射，前端應透過 locale 參數取得單一值，不直接回傳完整 map）
- **betpool_bets.id**（投注內部 ID，僅用於追蹤，不對外暴露）
- **betpool_bets.winlose**（在未結算前不可回傳任何結果，包含空字串）

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter keyspace | writer / reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **accounts\_*.password**：僅會員帳戶註冊或變更密碼流程可寫入，須執行 bcrypt 或同等級別單向雜湊，禁止明文儲存
- **accounts\_*.enabled**：僅管理後台或系統定時任務可寫入，前端 API 不可直接變更；新增帳戶時預設值由服務端控制
- **accounts\_*.handler**：屬於內部結構化資料（map<text, text>），僅可由服務內部邏輯寫入或維護，不接受前端 API 直接提供 key-value 組合
- **accounts\_*.closetime**：僅當帳戶狀態轉為關閉（enabled=0）時由系統自動填充，不可由外部手動寫入或修改
- **accounts\_*.phone**：註冊後不可直接修改（需通過專門的變更流程），寫入前須驗證格式與唯一性

### 讀取規則

- **帳戶啟用檢查**：查詢 accounts\_* 進行登入驗證時，必須 WHERE `enabled = 1`（啟用狀態），已關閉帳戶不可登入
- **帳戶關閉過濾**：查詢活躍帳戶列表時須額外過濾 `closetime IS NULL`，避免回傳已關閉帳戶
- **跨品牌帳戶隔離**：本服務依品牌分表（如 accounts_AU8、accounts_Fortuna888），查詢時必須依當前品牌選擇對應資料表，不可跨品牌查詢或合併結果
- **handler 欄位使用**：讀取 handler 時僅供內部服務間傳遞或管理用途，前端 API 不應直接回傳 map 結構中的特定值

### 不可回傳欄位

- **accounts\_*.password**：任何 API（包含管理後台）回應皆不得包含此欄位
- **accounts\_*.handler**：此為內部儲存結構，不對外暴露其完整鍵值對；前端僅應透過專用欄位（如 phone、username）取得資料
- **accounts\_*.phone**：屬於隱私敏感欄位，對外 API 預設不回傳；若確需顯示（如客服後台）須經特殊權限驗證

---

## ads

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra ads keyspace | owner / writer / reader | Schema：[db/ads.md](../../db/ads.md) · 語意：[db/ads-detail.md](../../db/ads-detail.md) |

### 寫入限制

- **advertising.createdby**：僅系統內部或管理後台可設定，標記廣告/公告建立者，前端 API 不可自行指定
- **advertising.enabled / advertising_sport.enabled / bulletinboard_sport.status**：啟用/狀態欄位僅管理後台或系統定時任務可修改，前端 API 不可直接變更顯示狀態
- **advertising.type**：僅由管理後台選取預定義類型（如 popup、slide）寫入，不應由 API 參數任意代入新值
- **advertising_sport.supportlangs**：新增紀錄時須由服務端驗證語言代碼合法性（如 zh-TW、en-US），前端不可直接傳遞未經校驗的語言列表
- **bulletinboard_sport.maintopic / text1 / text2 / text3**：多語言映射欄位僅可由服務端組裝寫入，前端不可直接傳入 map 結構，須透過固定語言欄位傳遞後由服務端轉換
- **bulletinboard_sport.starttime / endtime**：日期時間欄位須驗證 `starttime < endtime`，不可寫入時序錯誤的資料
- **bulletinboard_sport.sequence**：排序序號須由管理後台分配或由服務端自動產生（如 max(sequence)+1），不可由 API 參數任意指定造成衝突

### 讀取規則

- **前端廣告列表**：查詢 advertising 時須 WHERE `enabled = 1` 且 `starttime <= NOW` 且 `closetime > NOW`，僅回傳有效時間內的啟用廣告
- **體育廣告列表**：查詢 advertising_sport 時須 WHERE `enabled = 1` 且 `startdate <= NOW` 且 `closedate > NOW`，僅回傳有效時間內的啟用廣告
- **公告板查詢**：查詢 bulletinboard_sport 時須 WHERE `status = 1`（啟用）且 `starttime <= NOW` 且 `endtime > NOW`，僅回傳正在生效的公告
- **語言過濾**：advertising 回傳時須依 lang 欄位過濾符合當前使用者語系的廣告；advertising_sport 須檢查 supportlangs 清單是否包含請求之語言
- **排序規則**：advertising 與 advertising_sport 預設依 seq 升序排列；bulletinboard_sport 預設依 sequence 升序排列

### 不可回傳欄位

- **advertising.createdby**：廣告建立者屬內部管理資訊，不對外暴露
- **bulletinboard_sport.lastup_time**：最後更新時間為內部監控用時間戳，不對外回傳
- **bulletinboard_sport.addtime**：建立時間屬內部稽核用途，前端 API 不回傳
- **bulletinboard_sport.aid**：公告內部 ID，僅用於資料庫分區與管理，不對外暴露

---

## product

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra product keyspace | owner / writer / reader | Schema：[db/product.md](../../db/product.md) · 語意：[db/product-detail.md](../../db/product-detail.md) |

### 寫入限制

- **products_store.price / originalprice**：僅管理後台或排程任務可修改，前端 API 不可直接更新商品價格
- **products_store.status**：僅管理後台可變更（上架/下架），前端不可直接改寫
- **products_store.popular / sequence**：僅管理後台可調整熱門標記與排序
- **products_store.pnames / description / image_path**：多語言映射欄位，僅由服務端組裝寫入（前端透過固定語言參數傳遞，服務端轉換為 map），不可由 API 直接傳入 map 結構
- **product_store_redeem_logs**：兌換記錄僅由兌換流程寫入，status（如配送狀態）僅管理後台可修改
- **product_store_stock_logs**：庫存變更日誌僅由庫存調整流程自動寫入，不可手動新增記錄
- **products_activity.price / quantity / status**：活動價格、數量、啟用狀態僅管理後台可修改
- **products_activity_redeem_logs**：活動兌換記錄僅由活動兌換流程寫入，status 僅管理後台可變更
- **products_activity.names**：多語言活動名稱，僅由服務端組裝寫入，前端不可直接提供 map

### 讀取規則

- **商品列表查詢**：查詢 products_store 時須 WHERE `status = '1'`（啟用狀態），僅回傳上架商品
- **活動查詢**：查詢 products_activity 時須 WHERE `status = 1`（啟用），避免回傳已下架或未啟用的活動
- **用戶兌換記錄**：查詢 product_store_redeem_logs / products_activity_redeem_logs 時須依 account 過濾，僅回傳當前用戶自己的兌換記錄，不可跨用戶查詢
- **庫存查詢**：庫存數量需透過聚合 product_store_stock_logs（依 pid/pclass 計算 quantity 總和）取得，不可直接讀取靜態值
- **多語言內容回傳**：products_store.pnames / description / image_path、products_activity.names 需依請求語言參數從 map 中取出對應值，不對外暴露完整 map

### 不可回傳欄位

- **product_store_redeem_logs.phonenumber / address / recipient**：個人隱私資訊，僅管理後台可查看，一般 API 不可回傳
- **product_store_redeem_logs.cheadshot / cname / cmemo**：可依情境回傳，但 cmemo（客戶備註）涉及用戶輸入內容，需避免未經審核直接暴露
- **products_store.image_path**（多語言 map）：不回傳完整 map，僅回傳對應語系路徑
- **products_activity.names**（多語言 map）：不回傳完整 map，僅回傳對應語系名稱

---

## sport

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra sport keyspace | writer / reader | Schema：[db/sport.md](../../db/sport.md) · 語意：[db/sport-detail.md](../../db/sport-detail.md) |

### 寫入限制

- **bk_siteplayers** 全表寫入：僅系統排程或資料匯入流程可新增/修改，前端 API 不可直接寫入。欄位 `Record` 為文字記錄，僅由系統組裝寫入，前端不可提供未校驗內容
- **bk_siteplayers.SiteID / TeamID**：屬於內部關聯索引鍵，不應由 API 參數直接賦值，須根據上游系統對應後寫入
- **chatroomhistories / chatroomhistories_backup.Account**：寫入時須驗證帳號存在於 gameusers，否則拒絕寫入
- **chatroomhistories.Message**：長度上限 500 字元，寫入前須檢查長度，超長應拋錯而非截斷
- **community_groups.Enabled**：僅管理後台可變更（0/1），前端 API 不可直接修改群組啟用狀態
- **community_groups.Owner**：僅在建立群組時設定一次，不可透過普通 API 轉移群組擁有者
- **gameusers_wallet.Balance**：僅由交易結算流程原子增減（透過 Cassandra lightweight transactions 或 compare-and-set），不可直接 UPDATE 回寫
- **gameusers_wallet_transactions**：為唯追加表格，寫入後不可修改或刪除任何欄位（包含 Type / TypeInfo）
- **memberdailyreport**：全表由每日排程批次寫入，手動新增或修改應被禁止
- **notification_messages.Enabled**：僅管理後台可修改顯示狀態
- **notification_sitemails.ReadStatus**：僅用戶讀取站內信時由系統自動更新（0→1），不可由 API 參數指定
- **notification_topics.Enabled**：僅管理後台可修改主題啟用狀態，不可由前端 API 變更
- **predictdailyeport**：全表由每日排程批次寫入，不可由 API 直接 INSERT

### 讀取規則

- **聊天室歷史查詢**：查詢 chatroomhistories 時須指定 GID 分區鍵，否則造成全表掃描；可依 AddTime 排序
- **錢包餘額查詢**：查詢 gameusers_wallet 時必須指定 AuthKey，避免跨用戶掃描；僅回傳 Balance 與 LastUpdateTime
- **每日報告查詢**：查詢 memberdailyreport / predictdailyeport 時須指定 Reportdate，不可無日期條件掃描
- **站內信清單**：查詢 notification_sitemails 時須以 Account 為準，僅回傳當前用戶自己的郵件（不可跨帳號查詢）
- **社群群組查詢**：查詢 community_groups 時預設過濾 `Enabled = 1`，僅回傳啟用中的群組
- **通知主題查詢**：查詢 notification_topics 時須過濾 `Enabled = 1`，僅回傳啟用主題
- **通知訊息查詢**：查詢 notification_messages 時須指定 TID（主題ID），並過濾 `Enabled = 1`
- **球員資料查詢**：查詢 bk_siteplayers 時須指定 Site / Year / League 複合分區鍵，避免全表掃描；預設依 TeamID / Name 排序可能無法保證，應由應用層排序

### 不可回傳欄位

- **gameusers_wallet.AuthKey**：錢包授權金鑰，任何 API 回應皆不可包含，內部服務間傳遞亦須最小化暴露
- **chatroomhistories.Account**（聊天室歷史）：在一般聊天室列表回傳中應以 UserName 替代，不直接暴露原始帳號
- **notification_sitemails.Content**：內容可能包含敏感資訊，預設不回傳完整內文，須點擊開啟時另行取得
- **chatroomhistories.LikeAccount**（按讚帳號 list）：涉及用戶隱私，不對外暴露完整清單，僅顯示總讚數
- **notification_messages 的 TW_Content / EN_Content / CN_Content / JP_Content / TH_Content**：不回傳完整多語言 map，僅依請求語言參數回傳對應內容

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `session:{authkey}` | 登入成功後建立、每次 API 驗證時讀取 | 7200 秒（2 小時），sliding window 每次存取自動延長 |
| DEL | `session:{authkey}` | 登出或封禁時 | 立即失效 |
| SET / GET | `email:verify:{email}` | 註冊時發送驗證碼 | 600 秒（10 分鐘） |
| SET / GET | `rate:login:{ip}` | 登入失敗計數 | 900 秒（15 分鐘），超過 5 次則鎖定該 IP |
| SET / GET | `cache:user:{authkey}` | 頻繁查詢的用戶基本資訊 | 1800 秒（30 分鐘），用戶資料更新時主動刪除 |
| SET / GET | `price:cache:{brand}:{account}` | 成功查詢 pricecenter 帳戶後建立 | 1800 秒（30 分鐘），帳戶啟用/禁用時主動刪除 |
| SET / GET | `rate:pricecenter:write:{ip}` | 寫入 pricecenter 失敗時計數 | 900 秒（15 分鐘），超過 3 次則鎖定該 IP 寫入 |
| DEL | `price:cache:{brand}:{account}` | 帳戶狀態（enabled/password）更新時 | 立即失效，確保下一次讀取為最新資料 |
| SET / GET | `cache:ads:list` | 首次查詢廣告/公告列表後建立，或後台更新廣告資料後主動刷新 | 3600 秒（1 小時），廣告/公告變更時主動刪除 |
| SET / GET | `cache:wallet:{authkey}` | 首次查詢錢包餘額後建立 | 600 秒（10 分鐘），交易發生時主動刪除 |
| DEL | `cache:wallet:{authkey}` | 錢包餘額變更時 | 立即失效，確保餘額最新 |
| SET / GET | `cache:group:{gid}` | 查詢社群群組資訊後建立 | 3600 秒（1 小時），群組資料變更時主動刪除 |
| DEL | `cache:group:{gid}` | 群組名稱/啟用狀態變更時 | 立即失效 |
| SET / GET | `cache:topics:{site}` | 首次查詢通知主題列表後建立 | 1800 秒（30 分鐘），主題資料變更時主動刪除 |
| DEL | `cache:topics:{site}` | 通知主題啟用/停用時 | 立即失效 |
| SET | `rate:chat:write:{account}` | 發送聊天訊息 | 1 秒，防止單一帳號濫發訊息 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 廣告圖片/檔案上傳與儲存 | mediaservice | advertising.path、advertising_sport.imgpath / mobileimgpath 僅儲存路徑，實際檔案管理由媒體服務處理 |
| 廣告點擊追蹤與分析 | trackingservice | 廣告 url / tageturl 的點擊事件記錄與數據分析由追蹤服務負責 |
| 公告內容審核與上架流程 | admin service | 廣告/公告的審核流程、上架排程由管理後台服務處理，本服務僅提供 CRUD 資料存取 |
| 遊戲對戰邏輯與分數計算 | gameservice | 本服務僅儲存 gamecount/rank，實際對戰與排名由遊戲服務處理 |
| 付款交易處理 | paymentservice | 本服務僅記錄 gamesublogs 訂閱結果，金流串接與對帳由付款服務負責 |
| 頭像圖片上傳與儲存 | mediaservice | headshotpath 僅儲存路徑字串，實際檔案上傳、壓縮、CDN 由媒體服務處理 |
| Apple 登入 OAuth 流程 | authservice | 本服務僅儲存 appleinfos_game 最終結果，OAuth token 驗證由認證服務處理 |
| 會員登入 session 管理 | webpservice（member keyspace） | pricecenter 僅儲存帳戶基本資料，登入 session token、驗證與快取由 member 章節負責 |
| Apple / Google 第三方 OAuth 驗證 | authservice | pricecenter 僅儲存最終帳戶資料（如 account、password），OAuth 授權流程由外部認證服務處理 |
| 付款交易與訂閱金流 | paymentservice | pricecenter 不處理任何付款邏輯，帳戶餘額或付費狀態若存在需透過專有服務維護 |
| 商品圖片上傳與儲存 | mediaservice | products_store.image_path 僅儲存路徑，實際圖檔管理由媒體服務處理 |
| 商品兌換發貨物流 | logistics service | product_store_redeem_logs 僅記錄配送資訊，實際發貨流程由物流服務執行 |
| 活動審核與上架流程 | admin service | 活動的審核、啟用/停用排程由管理後台處理，本服務僅提供資料存取 |
| 庫存實時計算與扣減 | stock service | 庫存數量需依賴 stock service 提供原子扣減，本服務僅記錄 stock_logs 作為追蹤 |
| 錢包交易原子扣減 | paymentservice / game engine | gameusers_wallet.Balance 的原子增減由付款或遊戲結算服務處理，本服務僅查詢與記錄交易明細 |
| 聊天訊息即時推送 | chatservice | 聊天室歷史寫入資料庫後，即時推送由獨立聊天服務處理，本服務不維護 WebSocket |
| 球員資料來源與同步 | dataservice | bk_siteplayers 資料由上游體育資料提供商匯入，本服務不負責原始資料抓取 |
| 每日報告計算 | report service | memberdailyreport / predictdailyeport 由排程批次計算寫入，本服務僅提供查詢介面 |

---

## 常見錯誤

- ❌ 直接用 `SELECT * FROM gameusers WHERE email = ?` → ✅ 須明確排除 password 欄位：`SELECT authkey, account, username, email, status FROM gameusers WHERE email = ?`
- ❌ 註冊時未檢查 forbidden_email_domains 就寫入 → ✅ 先查詢黑名單：`SELECT name FROM forbidden_email_domains WHERE name = ?`，有結果則拒絕註冊
- ❌ 前端 API 直接更新 gameusers.status → ✅ 狀態變更應由管理後台或系統定時任務執行，前端僅能「申請」變更
- ❌ 登入時僅驗證密碼正確就回傳 authkey → ✅ 須額外檢查 `status = 1` 且不在 gameusers_banned 中
- ❌ 封禁用戶時僅寫入 gameusers_banned → ✅ 需同步更新 gameusers.status 並清除 Redis session
- ❌ 用 authkey 做為對外 API 回應的用戶 ID → ✅ 對外應使用 account 或 showcode，authkey 僅用於內部認證
- ❌ 改名時未檢查 renamecount 上限 → ✅ 需先查詢當前次數，並依業務規則（如每月 1 次）判斷是否允許
- ❌ 查詢 gamesublogs 時未指定 authkey 分區鍵 → ✅ Cassandra 複合主鍵查詢必須包含分區鍵，否則會 full scan
- ❌ 下注 API 允許傳入 betzcoin 超過用戶可用餘額 → ✅ 需先透過餘額服務檢查餘額足夠才允許寫入 betpool_bets
- ❌ 結算時未檢查 betpool_games.status 是否為「可結算」狀態就直接寫入 winresult → ✅ 需先將 status 改為 1（關閉），再執行結算邏輯，最後更新 winresult 與 payout
- ❌ 活動周期寫入時未驗證時間邏輯（startdate > enddate）→ ✅ 寫入前須比較 startdate <= enddate，否則拒絕寫入並回傳錯誤
- ❌ `SELECT * FROM accounts_AU8 WHERE account = ?` → ✅ 應明確排除敏感欄位：`SELECT account, username, enabled, closetime FROM accounts_AU8 WHERE account = ?`
- ❌ 註冊時未檢查 enabled 狀態就直接寫入 password → ✅ 寫入前須由服務端設定 enabled=1，不可依賴請求內容
- ❌ 查詢所有品牌帳戶時直接對 accounts_* 執行 LIKE 或全域掃描 → ✅ 應依品牌參數選擇對應資料表，必要時使用多分區批次查詢（如 IN 查詢）
- ❌ 前端 API 可直接傳入 handler: `{ "key": "value" }` → ✅ handler 欄位僅由服務端內部邏輯組裝，前端不應直接提供 map 結構
- ❌ 登入時僅比對 password 正確就通過驗證 → ✅ 須額外檢查 enabled=1 且 closetime IS NULL
- ❌ 變更密碼時未清除 price:cache 快取 → ✅ 密碼變更後必須 DEL 對應快取，否則舊密碼可能被暫存讀取
- ❌ 寫入 accounts\_* 時未檢查品牌對應的資料表是否存在 → ✅ 初始化時應確認該品牌的表已存在（如透過 Schema migration），否則拒絕寫入
- ❌ 處理 handler 欄位時假設其 map 結構固定不變 → ✅ handler 內容依業務動態擴展，讀取時應採彈性解析（如 getOrNull）而非固定欄位取值
- ❌ 創建廣告或公告時未驗證時間欄位邏輯（starttime > endtime / startdate > closedate）→ ✅ 寫入前須比較開始時間小於結束時間，否則拒絕寫入並回傳錯誤參數
- ❌ 查詢廣告列表時未過濾啟用狀態與有效時間範圍 → ✅ 查詢 advertising / advertising_sport 時須附加 `enabled = 1` 及時間範圍條件，避免回傳已下架或未上架的廣告
- ❌ 前端 API 直接操作 bulletinboard_sport 的 status 欄位 → ✅ 狀態變更僅應由管理後台或排程任務執行，前端僅能請求變更
- ❌ 回傳 bulletinboard_sport 多語言映射欄位（maintopic / text1）時未依語言代碼轉換 → ✅ 服務端須依請求的語言參數從 map 中取出對應內容，不應直接回傳完整 map 結構
- ❌ 廣告/公告資料更新後未清除 Redis 快取 → ✅ 管理後台修改廣告/公告後，須主動 DEL `cache:ads:list` 以確保前端取得最新資料
- ❌ 新增 advertising_sport 時未驗證 supportlangs 中的語言代碼是否合法 → ✅ 寫入前須比對支援的語言白名單，不合法語言應拒絕寫入或回傳警告
- ❌ 查詢聊天室歷史時未指定 GID 分區鍵 → ✅ 必須將 GID 加入 WHERE 條件，否則 Cassandra 會拒絕查詢或掃描全部節點
- ❌ 直接 UPDATE gameusers_wallet.Balance → ✅ 應使用 Cassandra lightweight transactions 或依賴上游付款服務進行原子扣減
- ❌ 寫入 chatroomhistories 時未檢查 Account 是否存在於 gameusers → ✅ 寫入前應驗證 Account 有對應的會員紀錄
- ❌ 回傳站內信列表時包含 Content 欄位 → ✅ 預設僅回傳 Subject / SendTime / ReadStatus，Content 須點擊後才取得
- ❌ 新增玩家資料 bk_siteplayers 時未指定複合分區鍵（Site / Year / League）→ ✅ 寫入時需提供完整分區鍵，否則無法確定資料所屬站台與賽季