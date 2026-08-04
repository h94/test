# NewLotterySite WebAPI

- **Git Repository**：<https://git.zbdigital.net/Biz/newlotterysite.git>
- **Portainer Key**：`PRD_Docker_Swarm|container|newlotterysite`
- **Kind**：`webapi`

## 職責

負責新運彩站台的前台功能整合，包含會員管理（註冊、手機簡訊驗證、登入登出、密碼變更、大頭貼更新、站內信通知查詢）、社群討論區（看板、文章、回文、按讚）、遊戲賽事與賠率查詢、預測投注管理、支付金流頁面與交易查詢，並依賴 MemberService、PaymentService、PredictService 等進行實際業務邏輯與資料操作。

## 技術棧

- **框架**：ASP.NET Core 8.0（.NET 8.0）
- **資料庫**：
  - **Cassandra**：`payment` keyspace（充值方案、活動產品、支付方式 — 唯讀）、`member` keyspace（會員帳號 — 主要寫入與讀取）、`ads` keyspace（廣告與公告 — 唯讀）、`community` keyspace（社群看板 — 唯讀）
  - **MySQL**：`Sport`（聊天室、群組、通知訊息、錢包交易 — 唯讀；`notification_sitemails` 可讀寫）、`NewLottery`（代幣錢包、交易記錄、錦標賽錢包 — 讀寫）
  - **PostgreSQL**：`Games`（賽事資料 — 唯讀）
- **快取**：Redis（支付方式快取、充值方案快取、廣告快取、錢包快取）、記憶體快取（`MemoryCache`，用於部分遊戲 API 結果）
- **驗證**：ECCore 3.0.3 內建機制（authKey）
- **其他**：Kafka（應用程式 Log）、REST 呼叫（MemberService、MQService）、MQService（簡訊發送）、檔案上傳（社群貼文圖片）、ECPay 金流 SDK

## 資料庫重要 Table

### 唯讀資料庫（Cassandra）

| Table / Keyspace                     | 用途           | 重要規則                                                                                                                         |
| ------------------------------------ | -------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `payment.rechargeplans_newlottery`   | 充值方案列表   | 僅回傳 `enabled=1` 且當前時間在 `[starttime, endtime)` 內；不可回傳 `lastupdatetime`                                               |
| `payment.paymethods_sport`           | 支付方式       | 僅回傳 `enabled=1`；`names` 須依請求語言轉單一字串，不可回傳完整 map                                                               |
| `payment.products_activity`          | 活動商品       | 需過濾 `status=1` 且 `quantity > 0`；不可回傳 `names` 完整 map（應依語言提取）                                                     |
| `payment.products_activity_redeem_logs` | 兌換紀錄   | 查詢需指定 `(site, activityevent, account)`，不可跨帳號                                                                          |
| `payment.subplans_sport`             | VIP 方案       | 僅回傳 `enabled=1` 且當前日期在 `[startdate, enddate)` 內；`names` 須依語系提取                                                    |
| `member.gameusers`                   | 會員主要資料   | 本服務為 owner，可讀寫；對外不可回傳 `password`, `authkey`, `email`（脫敏除外），`siteid`、`adsource` 等內部欄位                        |
| `member.gameusers_banned`            | 封禁紀錄       | `description` 不對外顯示                                                                                                         |
| `member.gamesublogs`                 | 訂閱紀錄       | 本服務可寫入；`tradeno` 不可回傳給非本人                                                                                         |
| `member.forbidden_email_domains`     | 禁止註冊網域   | 全表快取供註冊檢查                                                                                                               |
| `member.newlottery_users`            | 新運彩會員資料 | 本服務為主要讀寫方；不可回傳 `password`、`id`                                                                                      |
| `member.newlottery_banned`           | 新運彩封禁記錄 | 寫入時同步更新 `newlottery_users.status`                                                                                         |
| `member.gameusers_recommend`         | 推薦關係       | 查詢推薦關係時使用                                                                                                               |
| `ads.advertising`                    | 一般廣告       | 過濾 `enabled=1` 且 `starttime ≤ now < closetime`；不可回傳 `createdby`                                                             |
| `ads.advertising_sport`              | 體育廣告       | 查詢需帶 `adarea`；過濾 `enabled=1` 與日期區間；禁止回傳 `adclass`                                                                 |
| `ads.bulletinboard_sport`            | 公告           | 過濾 `status=1` 且時間在有效期內；多語言內容依請求語系回傳，不可回傳完整 map 或 `announcementmethod`                                 |
| `community.newlottery_forums`        | 社群看板       | 唯讀；僅回傳 `status=1` 的看板；`names` 依語系解析，不可回傳完整 map                                                               |

### 唯讀資料庫（MySQL）

| Table / Keyspace                           | 用途           | 重要規則                                                                                                                         |
| ------------------------------------------ | -------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `Sport.Notification_Messages`              | 通知訊息       | 僅回傳 `Enabled=1`；多語言內容依請求語系回傳（`TW_Content` 等），不可回傳所有語系原始欄位                                           |
| `Sport.Notification_Topics`                | 通知主題       | 僅回傳 `Enabled=1`                                                                                                              |
| `Sport.ChatRoomHistories_Backup`           | 聊天紀錄備份   | 查詢須指定 `GID`；不寫入；`LikeAccount` 不可回傳完整清單，應僅回傳按讚總數                                                           |
| `Sport.Community_Groups`                   | 社群群組       | 僅回傳 `Enabled=1`；群組名稱 (`Name`) 為多語系 JSON，需解析並回傳對應語言；不可回傳 `Owner`                                            |
| `Sport.BK_SitePlayers`                     | 球員資料       | 不具寫入權限；`Record`、`TeamID` 及 `SiteID` 不可回傳                                                                              |
| `Sport.GameUsers_Wallet`                   | 現金錢包       | 唯讀，餘額查詢需透過 `AuthKey`；不可跨用戶查詢                                                                                     |
| `Sport.GameUsers_Wallet_Transactions`      | 現金交易明細   | 唯讀，不可跨 `AuthKey` 查詢；對外不可回傳 `TID` 以外的內部鍵                                                                       |

### 唯讀資料庫（PostgreSQL）

| Table / Keyspace           | 用途             | 重要規則                                                                                                                         |
| -------------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `Games.games_{sport_code}` | 各球種賽事資料   | 不具寫入權限；前台查詢需帶 `gdate` 範圍與 `lid`，避免全表掃描；`siteidmaps`, `teams`, `create_at`, `otherinfo` 不可回傳；完賽判斷應以 `status='Final'` 為準 |

### 可讀寫資料庫（MySQL）

| Table / Keyspace                          | 用途               | 重要規則                                                                                                                         |
| ----------------------------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| `Sport.notification_sitemails`            | 站內信             | `ReadStatus` 僅使用者本人可標記已讀（0→1）；不可逆向變更                                                                          |
| `NewLottery.CoinWallet`                   | 代幣錢包           | 扣減需透過交易記錄並檢查餘額；不可直接 `UPDATE Balance`                                                                            |
| `NewLottery.CoinWallet_Transactions`      | 代幣交易           | `T_ID` 自動遞增，不可手動指定；不可對外回傳內部主鍵                                                                               |
| `NewLottery.ChampionshipWallet`           | 錦標賽積分錢包     | `Balance` 變更須寫入對應交易記錄；不可直接 UPDATE                                                                                 |
| `NewLottery.ChampionShipWallet_Transactions` | 錦標賽交易     | `ID` 自動遞增，`Point` 寫入後不可修改；不可對外回傳內部主鍵                                                                       |

## 對外 API 重點

### 會員管理

| Method | 路由                                          | 說明                           | 需要驗證 |
| ------ | --------------------------------------------- | ------------------------------ | -------- |
| POST   | `/api/users/register`                         | 新運彩會員註冊                 | ❌       |
| POST   | `/api/users/forgetpassword`                   | 忘記密碼（發送驗證碼）         | ❌       |
| POST   | `/api/users/login`                            | 會員登入                       | ❌       |
| POST   | `/api/users/logout/{authKey}`                 | 會員登出                       | ✅       |
| POST   | `/api/users/resendtoken/{validateType}`       | 重發手機簡訊驗證碼             | ❌       |
| POST   | `/api/users/verificationcode`                 | 發送會員驗證碼                 | ❌       |
| POST   | `/api/users/register/verify`                  | 會員註冊驗證                   | ❌       |
| POST   | `/api/users/{authKey}/validation/{validateType}` | 驗證手機簡訊驗證碼           | ✅       |
| POST   | `/api/users/{authKey}/championshipwallets`    | 新增使用者錦標賽錢包           | ✅       |
| POST   | `/api/users/{authKey}/focus`                  | 設定使用者關注名單             | ✅       |
| POST   | `/api/users/{authKey}/sublogs`                | 建立使用者訂閱紀錄             | ✅       |
| PUT    | `/api/users/{authKey}/password`               | 更新密碼                       | ✅       |
| PUT    | `/api/users/{authKey}/headshot`               | 更新會員大頭貼                 | ✅       |
| PUT    | `/api/users/{authKey}/name-contactinfo`       | 更新使用者名稱與聯絡資訊       | ✅       |
| GET    | `/api/notifications`                          | 取得通知訊息（可選 `tid` 過濾）| ❌       |
| GET    | `/api/notifications/topics`                   | 取得通知主題列表               | ❌       |
| GET    | `/api/subplans`                               | 取得VIP方案列表                | ❌       |
| GET    | `/api/users/search`                           | 使用暱稱搜尋會員               | ❌       |
| GET    | `/api/accounts/{id}`                          | 取得會員資訊                   | ❌       |
| GET    | `/api/users/{authKey}/logininfo`              | 取得使用者登入資訊             | ✅       |
| GET    | `/api/users/{authKey}/coinwallet`             | 取得使用者代幣錢包資訊         | ✅       |
| GET    | `/api/users/{authKey}/coinwallet/transactions`| 取得使用者代幣交易紀錄         | ✅       |
| GET    | `/api/users/{authKey}/championshiptickets`    | 取得使用者錦標賽門票           | ✅       |
| GET    | `/api/users/{authKey}/championshipwallets/{gameType}/{id}` | 取得使用者錦標賽錢包 | ✅       |
| GET    | `/api/users/{authKey}/championshipwallets/transactions/topics` | 取得使用者錦標賽查詢標題 | ✅       |
| GET    | `/api/users/{authKey}/championshipwallets/transactions/{cid}` | 取得使用者錦標賽點數紀錄 | ✅       |
| GET    | `/api/users/{authKey}/focus`                  | 取得使用者關注名單             | ✅       |
| GET    | `/api/users/{authKey}/sublogs`                | 取得使用者訂閱紀錄             | ✅       |

### 社群討論區

| Method | 路由                                                          | 說明             | 需要驗證 |
| ------ | ------------------------------------------------------------- | ---------------- | -------- |
| GET    | `/api/community/forums`                                       | 取得看板列表     | ❌       |
| GET    | `/api/community/forums/{forumId}/subjects`                    | 取得看板內文章   | ❌       |
| GET    | `/api/community/subjects/{subjectId}`                         | 取得文章詳情     | ❌       |
| GET    | `/api/community/forums/{forumId}/subjects/{subjectId}/likes`  | 取得文章按讚清單 | ❌       |
| POST   | `/api/community/{authKey}/forums/{forumId}/subjects`          | 新增文章         | ✅       |
| POST   | `/api/community/{authKey}/subjects/{subjectId}/comments`      | 新增回文         | ✅       |
| POST   | `/api/community/{authKey}/forums/{forumId}/subjects/{subjectId}/like` | 文章按讚         | ✅       |
| POST   | `/api/community/{authKey}/subjects/{subjectId}/comments/{commentId}/like` | 回文按讚         | ✅       |
| POST   | `/api/community/{authKey}/forums/{forumId}/subjects/{subjectId}` | 修改文章         | ✅       |
| POST   | `/api/community/{authKey}/subjects/{subjectId}/comments/{commentId}` | 修改回文         | ✅       |
| DELETE | `/api/community/{authKey}/forums/{forumId}/subjects/{subjectId}` | 刪除文章         | ✅       |
| DELETE | `/api/community/{authKey}/subjects/{subjectId}/comments/{commentId}` | 刪除回文         | ✅       |
| POST   | `/api/community/{authKey}/forums/{forumId}/subjects/{subjectId}/unlike` | 文章收回讚       | ✅       |
| POST   | `/api/community/{authKey}/subjects/{subjectId}/comments/{commentId}/unlike` | 回文收回讚       | ✅       |

### 支付

| Method | 路由                                        | 說明               | 需要驗證 |
| ------ | ------------------------------------------- | ------------------ | -------- |
| GET    | `/api/payment/rechargeplans`                | 查詢可用充值方案   | ❌       |
| GET    | `/api/payment/users/{authKey}/tradeorders`  | 查詢交易紀錄       | ✅       |

> **注意**：信用卡、超商代碼、WebATM 等金流頁面由 ECPayController 提供 MVC 視圖，不在此 API 清單中。

### 遊戲與賽事

| Method | 路由                                              | 說明                         | 需要驗證 |
| ------ | ------------------------------------------------- | ---------------------------- | -------- |
| GET    | `/api/games/counters`                             | 取得各球種聯盟賽事計數       | ❌       |
| GET    | `/api/games/{gameType}`                           | 取得特定球種賽事列表         | ❌       |
| GET    | `/api/games/{gameType}/{lid}/{gDate}/{gid}`      | 取得指定賽事詳細資訊         | ❌       |

### 預測與錦標賽

| Method | 路由                                                          | 說明                           | 需要驗證 |
| ------ | ------------------------------------------------------------- | ------------------------------ | -------- |
| POST   | `/api/championships/{gameType}/{id}/bets`                     | 新增錦標賽注單                 | ✅       |
| POST   | `/api/predicts/accounts/{id}/bets/unlock`                     | 解鎖會員賽事預測資訊           | ❌       |
| GET    | `/api/betpoolgroups`                                          | 取得彩池群組資訊               | ❌       |
| GET    | `/api/betpoolgroups/{gameType}/{id}/winnertopics`             | 取得彩池群組獲獎名單項目       | ❌       |
| GET    | `/api/betpoolgroups/{gameType}/{id}/winners/{bType}/{pid}`    | 取得彩池群組彩池得獎名單       | ❌       |
| GET    | `/api/championships/{gameType}`                               | 取得特定球種錦標賽列表         | ❌       |
| GET    | `/api/championships/{gameType}/{id}/games`                    | 取得錦標賽賽事與賠率           | ❌       |
| GET    | `/api/championships/{gameType}/{id}/leaderboard`              | 取得錦標賽排行榜               | ❌       |
| GET    | `/api/mypredicts/{authKey}/today`                             | 取得使用者今日預測注單         | ✅       |
| GET    | `/api/predicts/accounts/{id}/today`                           | 取得指定會員今日預測           | ❌       |
| GET    | `/api/predicts/accounts/{id}/history/championships`           | 取得會員歷史投注主題           | ❌       |
| GET    | `/api/predicts/accounts/{id}/history/championships/{gameType}/{cid}` | 取得會員歷史錦標賽投注 | ❌       |
| GET    | `/api/championships/tickets`                                  | 取得錦標賽門票列表             | ❌       |
| PUT    | `/api/mypredicts/{authKey}/lockfee`                           | 更新預測注單鎖定費用與啟用狀態 | ✅       |

### 系統

| Method | 路由                                        | 說明               | 需要驗證 |
| ------ | ------------------------------------------- | ------------------ | -------- |
| GET    | `/api/heart`                                | 服務心跳檢測       | ❌       |
| GET    | `/api/version`                              | 服務版本資訊       | ❌       |

## Redis 快取使用

| Key Pattern | 用途 | 時機 | TTL / 說明 |
|-------------|------|------|-----------|
| `ads:advertising:enabled:{site}` | 一般廣告快取 | 後台更新廣告後 | TTL 5 分鐘 |
| `ads:advertising_sport:area:{adarea}` | 體育廣告快取 | 區域廣告內容變動時 | TTL 10 分鐘 |
| `ads:bulletinboard:active:{site}` | 公告快取 | 公告狀態變更時 | TTL 5 分鐘 |
| `payment:paymethods:enabled` | 支付方式快取 | 支付方式變更時 | 需人工確認 TTL |
| `payment:rechargeplans:enabled:newlottery` | 充值方案快取 | 方案變更時 | 需人工確認 TTL |
| `member:forbidden_domains` | 禁止註冊網域快取 | 管理後台更新時 | 全表快取，變更時失效 |
| `coin_wallet:{Account}` | 代幣錢包快取 | 查詢餘額後 | TTL 300 秒，交易後 DEL |
| `championship_wallet:{Account}:{CID}` | 錦標賽錢包快取 | 查詢餘額後 | TTL 300 秒，交易後 DEL |
| `sport:chatroom:history:{GID}` | 聊天室訊息快取 | 新訊息寫入時 | TTL 3 分鐘 |
| `sport:community_groups:enabled` | 社群群組快取 | 群組變更時 | TTL 10 分鐘 |
| `sport:notification:active:{TID}` | 通知訊息快取 | 通知狀態變更時 | TTL 5 分鐘 |

## 關鍵業務規則

### 會員管理
  ✅ 密碼必須以 BCrypt 雜湊後儲存，任何 API 不可回傳明文或雜湊值
  ✅ 註冊時須檢查 `forbidden_email_domains`，禁止使用黑名單網域
  ✅ Email 修改必須驗證新郵箱，不可直接覆蓋
  ✅ `focus_account` 僅使用者本人可操作，需原子性保證
  ✅ 封禁檢查需查詢 `gameusers_banned` 並過濾 `endtime > now()`

### 社群討論區
  ✅ 看板僅回傳 `status=1` 的項目，`names` 依請求語系解析
  ✅ 討論標題字數限制 1-100 字元，內文字數限制 1-2000 字元
  ✅ **討論標題在同看板內不可重複**（待人工確認是否適用於編輯場景）
  ✅ 同一使用者對同一討論或留言不可重複按讚，重複按讚會回應 409 Conflict
  ✅ 圖片上傳路徑規則：`/usr/local/openresty/nginx/html/downloads/newlottery/img/{YYYY-MM-DD}/{subjectId}/{commentId}/`
  ✅ **status 欄位值含義**：0=停用，1=啟用（需人工確認是否有其他狀態）
  ✅ 資源不存在時應回應 404（看板不存在、討論不存在、留言不存在）
  ✅ 編輯討論/留言使用 POST 方法而非 PUT/PATCH（設計決策，需注意）
  ✅ **看板名稱重複檢查**：建立和編輯時是否都觸發需人工確認

### 支付與錢包
  ✅ 充值方案查詢必須同時檢查 `enabled=1` 與時間範圍
  ✅ 代幣錢包餘額變動必須透過交易記錄，不可直接 UPDATE
  ✅ 錦標賽錢包 `Balance` 變動須寫入對應交易記錄
  ✅ 交易記錄的 `Point`/`Coin` 寫入後不可修改，錯誤需以沖正記錄處理
  ✅ 支付方式 `names` 須依請求語言轉單一字串

### 遊戲與賽事
  ✅ 賽事查詢必須帶 `gdate` 範圍與 `lid`，避免全表掃描
  ✅ 完賽判斷應以 `status='Final'` 為準，不可僅靠比分判斷
  ✅ `siteidmaps`、`teams`、`create_at` 等內部欄位不可回傳
  ✅ 需過濾 `status` 為 `Live` 或 `Final` 的比賽，不顯示 PreGame 或 Cancelled

### 廣告與公告
  ✅ 一般廣告需過濾 `enabled=1` 且 `starttime ≤ now < closetime`
  ✅ 體育廣告需指定 `adarea` 分區鍵查詢，過濾 `enabled=1` 與日期區間
  ✅ 公告多語言內容依請求語系回傳，不可回傳完整 map
  ✅ `createdby`、`adclass`、`announcementmethod` 等內部欄位不可對外回傳

## 服務相依與限制

| 相依服務 | 用途 | 限制 |
|---------|------|------|
| MemberService | 會員核心邏輯、驗證、訂閱管理 | 密碼、authKey 不可回傳；email 需脫敏 |
| PaymentService | 支付金流、訂單建立與查詢 | 僅讀取方案與支付方式；實際扣款由 PaymentService 處理 |
| PredictService | 賽事預測、注單管理 | status='Final' 僅能由 PredictService 設定 |
| GameService | 賽事資料、賠率資訊 | 不可寫入 Games 資料庫；必須帶分區鍵查詢 |
| MQService | 簡訊發送、非同步通知 | 不可同步等待回應 |
| ECPay | 信用卡、超商代碼、WebATM 金流 | 透過 MVC 視圖處理，非 REST API |

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 支付金流處理 | payment 服務 | 本服務僅讀取方案與設定，實際扣款、退款由 payment 服務負責 |
| 活動產品庫存管理 | activity/inventory 服務 | 僅觸發兌換扣減，補貨與庫存管理由活動服務處理 |
| 佣金結算 | commission/settlement 服務 | 僅記錄佣金明細，計算與發放由佣金服務處理 |
| 廣告投放統計 | ad management/analytics 服務 | 僅儲存設定與展示，投放策略與統計由其他服務負責 |
| 聊天內容審核 | content moderation 服務 | 訊息內容審核由專用服務負責 |
| 推播通知 | push notification 服務 | 站內信由本服務管理，即時推播由 push 服務觸發 |
| 錢包交易結算 | transaction settlement 服務 | 僅記錄明細，結算處理由專用服務負責 |

## 常用指令

```bash
# 本地開發啟動
dotnet run --project NewLotterySite

# 心跳檢查
curl http://localhost:5000/api/heart

# 版本查詢
curl http://localhost:5000/api/version
```

## 技術備註

- 時區設定為 `Asia/Taipei`（容器內已配置）
- 使用 `RequestCacheAttribute` 提供記憶體快取，支援 `forceupdcache=1` 強制更新
- 檔案上傳限制：社群貼文圖片最多 5 個，透過 `multipart/form-data` 上傳
- 分頁機制：社群文章每頁 20 筆，使用 `page_index` 參數，回應含 `next_page` 布林值
- 語言代碼支援：`zh-TW`、`zh-CN`、`en-US`、`ja-JP`、`th-TH` 等，預設 `zh-TW`
- 多語系處理：對外 API 只回傳請求語系內容，不回傳完整多語系 map
- Kafka 用於應用程式日誌收集，非業務訊息傳遞