# paymentservice — DB 操作邊界

> 產出時間：2025-03-31 14:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## member

（保留原有內容，本次未觸發變更）

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member keyspace | reader | Schema：[db/member.md](../../db/member.md) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **本服務不寫入 member 資料庫**：所有會員資料（gameusers、gamesublogs 等）由 memberservice 管理；本服務僅讀取用於驗證訂閱資格與支付流程

### 讀取規則

- **訂閱資格驗證**：查詢 `gamesublogs` 時以 `authkey` + `subtime` + `tradeno` 定位特定訂閱記錄；用於確認用戶當前訂閱狀態與支付歷史
- **用戶身份驗證**：透過 `gameusers.authkey` 關聯支付訂單與會員帳號；必須確保 `status=正常` 才可執行支付操作
- **Apple ID 綁定**：透過 `appleinfos_game.id` 查詢 Apple Sign-In 關聯的會員資料
- **機器人帳號排除**：支付流程需排除 `gamerobots.enabled=1` 的測試帳號
- **禁用網域檢查**：註冊/綁定流程需比對 `forbidden_email_domains.name`；阻擋使用一次性信箱網域

### 不可回傳欄位

- `gameusers.password`：加密密碼絕不可透過任何 API 回傳
- `gameusers.email`：僅管理後台可見；一般 API 僅回傳遮罩版本（如 `a***@example.com`）
- `gameusers.black_account` / `focus_account` / `follow_account`：社交關係清單屬敏感資料；僅由 memberservice 提供

---

## payment

（保留原有內容，本次未觸發變更）

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra payment keyspace | owner | Schema：[db/payment.md](../../db/payment.md) · 語意：[db/payment-detail.md](../../db/payment-detail.md) |

### 寫入限制

- **commissions_betpool_newlottery**：所有欄位僅由 `NewLotteryCommissionService` 寫入，禁止人工 INSERT 或 UPDATE；`ctype`（ticket / sell）、`coin` 必須由佣金計算邏輯產生，不可由 API 直接設定。
- **paymethods_sport**：`enabled` 僅可由管理後台 API 修改；`paytype` 與 `mode` 為 Partition Key / Clustering Key，不可更新；`names` map 可透過管理 API 更新特定語言鍵值。
- **products_activity**：`price`、`quantity` 僅由活動管理後台更新；`status` 僅在商品上架/下架時變更；`id`、`site`、`activityevent` 不可修改。
- **products_activity_redeem_logs**：僅由兌換流程寫入 INSERT；`status` 應由後續審核或排程更新，不可由前端直接 UPDATE。
- **rechargeplans_newlottery**：`amount`、`coin`、`currency`、`enabled`、`starttime`、`endtime` 僅由方案管理後台設定；`id` 不可修改。
- **reports_sport**：`totalincome`、`shareamount`、`unlockcount`、`leaguesunlock`、`finishing` 由排程批次寫入，禁止人工 INSERT 或 UPDATE `finishing=true`（已完成標記）。

### 讀取規則

- **佣金查詢**：依 `betpool` 分區查詢特定彩池佣金；可使用 `ctype` 過濾類型（`'ticket'`、`'sell'`）。
- **支付方式清單**：前端下單僅查詢 `paymethods_sport` 中 `enabled=1` 的記錄；管理後台可列出所有（含停用）。
- **活動商品**：查詢特定 `site` 與 `activityevent` 下 `status=啟用` 且 `quantity > 0` 的商品（方可兌換）。
- **兌換紀錄**：依 `site`、`activityevent`、`account` 查詢用戶兌換歷史；管理後台可省略 `account` 查全站。
- **儲值方案**：僅過濾 `enabled=1` 且 `starttime <= now <= endtime` 的方案回傳前端。
- **月份財報**：僅查詢 `finishing=true` 的已結算報表（`year`、`month` 作為 WHERE 條件）。

### 不可回傳欄位

- `commissions_betpool_newlottery.source_uid`、`source_cid`：用戶與客戶識別資訊，除管理後台外不應回傳。
- `products_activity.names` 與 `paymethods_sport.names`：對外 API 應僅回傳對應語言的值，不可回傳完整 map。
- `reports_sport.leaguesunlock`：內部 JSON 結構，不對前端公開。

---

## product

（保留原有內容，本次未觸發變更）

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra product keyspace | owner | Schema：[db/product.md](../../db/product.md) · 語意：[db/product-detail.md](../../db/product-detail.md) |

### 寫入限制

- **product_store_redeem_logs**：僅由兌換流程寫入 INSERT；`status` 初始值為 `'pending'`（待處理）；後續審核或發貨排程更新 `status`；`address`、`recipient`、`phonenumber` 需由用戶提供且不可由前端直接 UPDATE 已建立的記錄。
- **product_store_stock_logs**：庫存變動日誌，僅由庫存扣減邏輯寫入（每當兌換成功後產生一筆 `quantity` 減少記錄）；禁止人工 INSERT。
- **products_store**：`price`、`popular`、`status`、`originalprice`、`sequence` 僅由管理後台 API 修改；`pclass` + `pid` 為複合主鍵，不可更新；`image_path`、`pnames`、`description` map 可透過管理 API 更新特定語言鍵值。
- **products_activity**：`price`、`quantity`、`status` 僅由活動管理後台更新；`site`、`activityevent`、`id` 不可修改；`names` map 僅可更新特定語言值。
- **products_activity_redeem_logs**：僅由兌換流程寫入 INSERT；`status` 初始 `0`（待審核），後續由審核排程更新為 `1`（成功）或 `2`（失敗）；不可直接由前端 UPDATE。

### 讀取規則

- **一般商店商品列表**：前端查詢 `products_store` 時僅回傳 `status='上架'` 的記錄；管理後台可查所有狀態。
- **熱門商品**：`popular=true` 可作為排序或推薦條件，但仍須符合 `status='上架'`。
- **庫存異動紀錄**：依 `pclass` + `pid` 查詢 `product_store_stock_logs`，用於後台審計或庫存對帳。
- **兌換歷史**：前端依 `account` 查 `product_store_redeem_logs`；管理後台可依 `pclass`、`pid`、`status` 過濾。
- **活動商品可用清單**：查 `products_activity` 時需 `status=0`（啟用）且 `quantity > 0`；`site` 與 `activityevent` 為必填 WHERE 條件。
- **活動兌換紀錄**：依 `site`、`activityevent`、`account` 查詢用戶兌換歷史；管理後台可省略 `account` 以查全站。

### 不可回傳欄位

- `product_store_redeem_logs` 中的 `address`、`phonenumber`、`recipient`、`cname`、`cheadshot`：屬個人資料，對外 API 僅回傳遮罩版本或省略；管理後台可視權限回傳完整值。
- `products_store.image_path`：內部存儲路徑，不直接暴露給前端；應回傳經 CDN 轉換的圖片 URL。
- `products_activity.names` 與 `products_store.pnames`、`description`：對外 API 應僅回傳對應請求語言的值，不可回傳完整 map 結構。

---

## stock

（本次更新，覆蓋並擴充原有內容）

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Stock MySQL | owner（tradeorder_stock、sublogs、messagelog）；reader（users、subplans_stock、favoritebroker、favoriterule、favoritestock、options、rules） | Schema：[db/stock.md](../../db/stock.md) · 語意：[db/stock-detail.md](../../db/stock-detail.md) |

### 寫入限制

- **tradeorder_stock**：僅由 `StockTransactionDataProvider` 寫入，禁止人工 INSERT / UPDATE。`orderid` 由系統自動產生。`status` 初始值為 0（待付款），後續由金流回呼或排程更新，不可由 API 直接修改。`amount` 必須與訂閱方案 `subplans_stock.amount` 一致。`card4no` 應為信用卡末四碼（遮罩後），寫入時即不可揭露完整卡號。`periodsuccesscount` 初始化為 0，僅由續扣排程更新。
- **sublogs**：僅由 `NewLotteryTransactionService` 寫入 INSERT。`Account` 為對應支付用戶。`SubID` 必須存在於 `subplans_stock` 且 `enabled=1`。`SubRank` 需與 `subplans_stock.subrank` 一致。`SubEndTime` 根據方案有效長度計算，不可人工指定。`TradeNo` 由系統生成（關聯 `SportTradeOrder.OrderID` 對應之交易）。`AddTime` 為寫入時間戳（毫秒），不可修改。
- **messagelog**：僅由訊息發送邏輯寫入 INSERT / UPDATE。`SendStatus` 初始為 0（未發送），後續由發送排程更新為 1（成功）或 2（失敗）。`MsgContent` 不得包含用戶密碼、完整卡號等敏感資料。`Date` 作為分區鍵，建立後不可異動。
- **users**：本服務**不寫入**此表。帳號、密碼、聯絡方式等均由 memberservice / 管理後台維護。
- **subplans_stock**：本服務**不寫入**此表。方案啟用、金額、日期等僅由管理後台設定。
- **favoritebroker / favoriterule / favoritestock / options / rules**：本服務**僅讀取**，寫入由其他服務（如 stockservice、管理後台）負責。

### 讀取規則

- **訂閱方案**：查詢 `subplans_stock` 時僅回傳 `enabled=1` 且 `startdate <= 現在日期 <= enddate` 的記錄，用於前端支付頁面顯示。
- **用戶訂閱狀態**：查詢 `users` 時需過濾 `Enabled=1` 且 `SubEndTime > NOW()`（訂閱未過期），或透過 `sublogs` 依 `Account` 降冪取最新一筆確認到期日；`Rank` 欄位可輔助判斷會員等級。
- **交易訂單查詢**：依 `Account` 與 `Date`（分區鍵）查詢 `tradeorder_stock`，必須限定時間範圍避免全掃；可使用 `orderid` 或 `thirdpartyorderid` 精確定位。
- **佣金與規則**：讀取 `rules`、`favoriterule` 時需過濾 `Enabled=1` 且 `Country` 與用戶市場一致；`favoriterule` 需以 `User` 精確過濾；`options` 僅查詢 `Enabled=1` 的項目，`Value` 通常作為關鍵字搜尋。
- **用戶偏好**：查詢 `favoritebroker`、`favoritestock` 時以 `User` 過濾，僅回傳該用戶自有資料。
- **訊息紀錄**：查詢 `messagelog` 必須包含 `Date`（分區鍵），可搭配 `Account`、`SendAction` 過濾；`SendStatus` 可篩選成功/失敗。

### 不可回傳欄位

- `users.Password`：密碼（雜湊值）絕不可透過 API 回傳。
- `users.Phone`、`users.ChatID`、`users.Email`：個人聯絡資訊，前端應遮蔽或僅回傳遮罩版本（如 `a***@example.com`）；僅內部發送通知使用。
- `tradeorder_stock.card4no`：信用卡末四碼，屬金融敏感資料，對外 API 不可回傳；內部對帳使用。
- `messagelog.MsgContent`：可能包含機敏資訊，原則上不對前端公開，管理後台可依權限查詢。
- `sublogs.TradeNo`：雖為交易編號，但需注意關聯金流單號，避免於對外 API 直接暴露完整單號（應由後台管理）。

### Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| GET | `StockCache:StockSubPlans` | 查詢所有啟用的股票訂閱方案 | 永久（方案變動時需手動清除整個快取） |
| SET / DEL | `StockCache:StockSubPlans:{planID}` | 單一方案啟用、停用或內容異動 | 立即失效，確保前端取到最新方案資訊 |

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 用戶帳號、密碼及個人資料維護 | memberservice / 管理後台 | `users` 表所有寫入操作 |
| 訂閱方案（`subplans_stock`）的管理 | 管理後台 | 方案的啟用、金額、有效期限等設定 |
| 自選股、券商偏好、選股規則（`FavoriteStock`、`FavoriteBroker`、`FavoriteRule`）的寫入 | stockservice 或相關前端服務 | 僅透過 stockservice API 異動，paymentservice 不直接寫入 |
| 系統規則（`Rules`）與選項（`Options`）的維護 | 管理後台 | 策略、指標、參數的註冊與更新 |
| 訊息發送的外部通道（如 email、SMS 實際寄送） | notificationservice | 本服務只負責寫入 `messagelog`，不直接與外部通道互動 |
| 股票行情與策略比對 | stockservice / dataservice | 僅使用其結果，不負責運算 |

### 常見錯誤

- ❌ **未帶分區鍵 `Date` 查詢 `messagelog`** → ✅ 所有查詢必須包含 `Date` 範圍，避免全表掃描。
- ❌ **手動設定 `sublogs.SubEndTime` 或 `sublogs.SubRank`** → ✅ `SubEndTime` 由方案有效長度與 `SubTime` 計算得出，`SubRank` 需從 `subplans_stock` 取得，嚴禁任意指定。
- ❌ **在寫入 `tradeorder_stock` 時儲存完整卡號** → ✅ 僅保存 `card4no`（末四碼遮罩），絕不紀錄完整 PAN。
- ❌ **直接更新 `users.SubEndTime` 來延長訂閱** → ✅ 訂閱必須透過正規交易流程產生 `sublogs` 記錄，由排程或金流回呼更新 `users` 相關欄位，不可直接 UPDATE。
- ❌ **對前端回傳 `users.Email`、`users.Phone` 等完整聯絡資訊** → ✅ 應使用遮罩或由管理後台視權限提供。
- ❌ **修改 `subplans_stock` 後未清除 Redis 快取** → ✅ 必須執行 `DEL StockCache:StockSubPlans:{planID}` 或重建 `StockCache:StockSubPlans` 集合。

---

## sport

（保留原有內容，本次未觸發變更）

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport MySQL | owner（tradeorder_sport, withdrawlogs_sport, shakehandlogs_site_sport, shakehandlogs_service_sport）；reader（BK_SitePlayers, ChatRoomHistories_Backup, Community_Groups, GameUsers_Wallet, GameUsers_Wallet_Transactions, Notification_Messages）| Schema：[db/sport.md](../../db/sport.md) · 語意：[db/sport-detail.md](../../db/sport-detail.md) |

### 寫入限制

- **tradeorder_sport**：僅由 `SportTransactionDataProvider` 寫入，禁止人工 INSERT / UPDATE；`orderid` 由系統自動產生；`status` 初始值為 0（待付款），後續由金流回呼或排程更新；`amount` 需與 `subplans_sport.amount` 一致；`datetime` 作為分區鍵不可異動；`card4no` 應僅寫入信用卡末四碼（不得揭露完整卡號）；`periodsuccesscount` 僅由續扣排程更新（首次寫入為 0）。
- **withdrawlogs_sport**：僅由 `SportWithdrawDataProvider` 寫入 INSERT；`status` 初始值為 0（待審核），僅可由管理後台審核後更新為 1（成功）或 2（失敗）；`amount` 以實際申請金額為準，不得與內部餘額相乘；`datetime` 作為分區鍵，創建後不可異動。
- **shakehandlogs_site_sport**：僅由 `SportLogDataProvider` 寫入 INSERT；用於記錄與外部站台交互；`req` 內容不可包含未加密的敏感參數。
- **shakehandlogs_service_sport**：僅由 `SportLogDataProvider` 寫入 INSERT；用於記錄服務間內部呼叫；`req`、`resp` 不可印出客戶端完整卡號、密碼等明細。
- **BK_SitePlayers**：本服務**不寫入**該表；球員數據由數據爬取服務負責。
- **ChatRoomHistories_Backup**：本服務**不寫入**該表；聊天記錄由聊天服務負責。
- **Community_Groups**：本服務**不寫入**該表；社群群組由社群服務負責。
- **GameUsers_Wallet**：本服務**不寫入**該表；錢包餘額由 `walletservice` 負責維護。
- **GameUsers_Wallet_Transactions**：本服務**不寫入**該表；交易流水由 `walletservice` 或對應遊戲服務寫入。
- **Notification_Messages**：本服務**不寫入**該表；通知模板由通知服務負責配置。

### 讀取規則

- **支付方式**：查詢 `paymethods_sport` 時過濾 `enabled=1`，僅回傳啟用中的支付方式。
- **訂閱方案**：查詢 `subplans_sport` 時需過濾 `enabled=1` 且 `startdate <= 今日日期 <= enddate`。
- **交易訂單查詢**：依 `account` 與 `datetime`（分區鍵）查詢 `tradeorder_sport`；應限定時間範圍避免全分區掃描；可使用 `orderid` 或 `thirdpartyorderid` 作為精確查找條件；**禁止不帶分區鍵查詢**。
- **提領紀錄**：依 `account` + `datetime` 查詢 `withdrawlogs_sport`；管理後台可依 `status` 過濾待審核項目。
- **財報查詢**：`reports_sport` 與 `sharereports_sport` 僅查詢 `finishing=true`（或 `payout=1`）的已結算月份；前端不可查詢未結算報表。
- **推薦報表查詢**：`reports_sport_recommend` 與 `sharereports_sport_recommend` 僅查詢已結算紀錄；`year` + `month` 為必要條件。
- **操作日誌查詢**：查詢 `shakehandlogs_site_sport` 與 `shakehandlogs_service_sport` 應依 `date`（分區鍵）及 `account` 進行過濾，**禁止不帶分區鍵的全表掃描**。

### 不可回傳欄位

- `tradeorder_sport.card4no`：信用卡末四碼屬金融敏感資料，對外不可完整揭露（建議僅內部對帳留存）。
- `withdrawlogs_sport.accountname`、`contactnumber`：個人身份與聯絡資訊，僅管理後台可查；前端應遮蔽或隱藏。
- `shakehandlogs_site_sport.req`、`shakehandlogs_service_sport.req`、`shakehandlogs_service_sport.resp`：內部請求與回應 JSON 可能含 Token 或短暫敏感資料，不可對外 API 回傳完整內容。
- `GameUsers_Wallet.AuthKey`：錢包驗證金鑰，等同於錢包存取憑證，不可對外回傳。
- `GameUsers_Wallet_Transactions.TypeInfo`：交易明細 JSON 可能包含關聯帳號與遊戲行為，非必要不應對前端開放。

### Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| GET | `SportCache:SportPayMethods` | 查詢運動支付方式 | 永久；後台修改 `paymethods_sport` 時須手動清除快取 |
| GET | `SportCache:SportSubPlans` | 查詢運動訂閱方案 | 永久；方案異動時需透過排程或 API 更新 |
| SET / DEL | `SportCache:SportSubPlans:{planID}` | 單一方案停用或異動 | 立即失效，避免前端取到已停用方案 |

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 體育數據爬取與清洗 | dataservice | 包含 `BK_SitePlayers.Record` 等數據之來源與轉換 |
| 聊天室管理與訊息儲存 | chatservice | 包含 `ChatRoomHistories_Backup` 讀寫 |
| 社群功能（群組建立、邀請） | communityservice | 包含 `Community_Groups` CRUD |
| 錢包變動與交易流水 | walletservice | 本服務僅讀取 `GameUsers_Wallet` 與 `GameUsers_Wallet_Transactions` 進行查核，不直接異動餘額 |
| 通知模板管理與排程派送 | notificationservice | `Notification_Messages` 之內容維護與發送規則 |

### 常見錯誤

- ❌ **未帶分區鍵 (`datetime`/`date`) 查詢 `tradeorder_sport` 或提領/日誌表** → ✅ 所有查詢必須包含分區鍵，避免全表掃描導致查詢逾時。
- ❌ **寫入 `tradeorder_sport.card4no` 時傳入完整卡號** → ✅ 僅保留末四碼並做遮罩處理，嚴禁儲存完整 PAN。
- ❌ **直接更新 `GameUsers_Wallet.Balance` 進行退款或加值** → ✅ 錢包操作必須透過 `walletservice`，由交易流水紀錄驅動。
- ❌ **未過濾 `finishing=true` 即回傳財報資料給前端** → ✅ 月份未結算資料不可顯示，避免使用者混淆。
- ❌ **手動寫入 `withdrawlogs_sport.status=1`（直接設為成功）** → ✅ 提領需經後台人工審核流程，僅審核通過方可更新狀態。
- ❌ **更新 `subplans_sport` 後未清除對應 Redis 快取** → ✅ 必須執行 `DEL SportCache:SportSubPlans:{planID}` 或更新整個 `SportCache:SportSubPlans` 集合。