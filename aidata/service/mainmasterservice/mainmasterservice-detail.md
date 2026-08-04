# mainmasterservice — DB 操作邊界

> 產出時間：2025-04-09 12:00  
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）  
> ⚠️ AI 產出，需資深工程師審核後生效

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member | owner | Schema：[db/member.md](../../db/member.md) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **gameusers.authkey**：僅註冊 API 可寫入，由系統產生 UUID，後續不可變更
- **gameusers.password**：須使用 bcrypt/scrypt 雜湊後存入，禁止明文或弱雜湊(如 MD5)
- **gameusers.email**：註冊時寫入後不可直接 UPDATE；變更需透過驗證流程並記錄舊值
- **gameusers.status**：僅封禁/解封 API 可修改；正常註冊時預設 0，封禁時寫入 gameusers_banned 並更新 status
- **gameusers.rank / gamecount / signindays**：由積分/簽到邏輯自動累加，禁止手動 UPDATE
- **gameusers.black_account / focus_account / follow_account**：僅使用者本人或客服工具可操作；須防止清單過大(建議上限 1000 筆)
- **gameusers.memberships**：僅訂閱 API(gamesublogs 寫入成功後)可追加；不可直接刪除，須透過退訂流程
- **gamesublogs**：僅支付回調/訂閱系統可寫入；authkey + subtime + tradeno + addtime 為複合叢集鍵，寫入後不可變更
- **gameusers_banned**：僅封禁 API 可寫入；authkey + addtime 為複合鍵，endtime 為空表示永久封禁
- **forbidden_email_domains**：僅管理後台可寫入；註冊時需檢查 email 網域是否在此表
- **gamerobots.enabled**：僅管理後台或自動化腳本可變更；禁止透過一般 API 修改
- **appleinfos_game**：僅 Apple 第三方登入回調可寫入；id 為 Apple 提供的唯一識別碼

### 讀取規則

- **登入查詢**：`SELECT * FROM gameusers WHERE email=? ALLOW FILTERING` 須額外檢查 `status=0` (正常)，status≠0 拒絕登入
- **封禁檢查**：`SELECT * FROM gameusers_banned WHERE authkey=? AND addtime<=now()` 若 endtime 為空或 endtime > now() 則視為封禁中
- **機器人過濾**：查詢一般使用者清單時須排除 `account IN (SELECT account FROM gamerobots WHERE enabled=1)`
- **訂閱查詢**：`SELECT * FROM gamesublogs WHERE authkey=? AND subtime>=?` 依 subendtime 判斷有效期；autosub=true 表示自動續訂
- **禁用網域驗證**：註冊時 `SELECT name FROM forbidden_email_domains WHERE name=?` (email 的 domain 部分)，若存在則拒絕註冊
- **聯盟投注查詢**：`SELECT * FROM predictbets_{game_type} WHERE gdate>=? AND gdate<=? AND lid=? ALLOW FILTERING`；須限制日期範圍不超過 31 天
- **帳號關係查詢**：gameusers.black_account / focus_account / follow_account 需透過 `IN` 查詢批量取得對象資料，須防止 N+1 查詢

### 不可回傳欄位

- **gameusers.password**：任何 API 均不可回傳明文或雜湊值
- **gameusers.authkey**：僅登入時回傳作為 session token，其他查詢不可洩漏
- **gameusers.lastactiontime / lastchecktime**：內部監控用，不對外暴露
- **gameusers_banned.description**：封禁原因僅管理後台可見，前端僅顯示「帳號異常」
- **appleinfos_game.id / email**：第三方登入資訊不可回傳給非本人

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra predict | owner | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **activities_cycles.startdate / enddate / starttime / endtime**：僅活動排程 API 可寫入；後續變更需透過更新 API，不可直接 `UPDATE`
- **activities_cycles.resultcount**：僅活動結算程序可寫入；不可手動修改或透過後台直接設定
- **activities_record.account**：由活動參加 API 寫入，後續不可修改；退賽須透過刪除記錄流程
- **activities_record.winbets**：僅活動結算後台或自動程序可寫入，不可手動賦值
- **activities_record.restday / updatedate**：僅活動結算程序可寫入；restday 由程序計算，updatedate 自動更新，禁止手動設定
- **activities_winneraccounts.rank / profitpoint / winpercentage**：僅活動排名計算邏輯可寫入，禁止後台直接 `UPDATE`
- **activities_winneraccounts.predictcount**：僅活動計算程序依實際預測次數寫入，不可人工調整
- **betpool_bets.id / addtime**：由投注 API 寫入後不可變更
- **betpool_bets.winlose / profitzcoin**：僅遊戲結算程序寫入，不可後台修改
- **betpool_games.payout / winresult**：僅遊戲結算流程寫入；`payout=true` 後不可重複派彩
- **betpool_games.status**：僅遊戲生命週期管理 API 可變更（啟動、進行中、結束、關閉），禁止隨意修改
- **betpool_games.hot / viponly**：僅管理後台可設定
- **betpool_games.names / betoptions**：僅遊戲建立或編輯 API 可寫入，屬多語言配置
- **betpool_games.basicprofitzcoin / bonusprofitzcoin / feedrate**：僅管理後台在遊戲建立時設定，後續修改需審核流程；feedrate 為商業敏感資訊
- **calculatelog.done / weekid / weekdate / addtime**：僅活動排程結算程序可寫入；`done` 由程序計算後自動設為 1，不可手動變更；`addtime` 自動生成
- **killeraccounts_BK.addtime / avgodd**：僅反作弊腳本或管理後台可寫入；avgodd 由統計程序自動計算，不可人工直接更新

### 讀取規則

- **活動循環查詢**：`SELECT * FROM activities_cycles WHERE site=? AND activityevent=? AND cid=?` 須指定完整主鍵，避免全表掃描
- **活動記錄查詢**：`SELECT * FROM activities_record WHERE site=? AND eventname=? AND account=?` 須以 `site+eventname+account` 為主鍵查詢
- **獲勝者清單查詢**：`SELECT * FROM activities_winneraccounts WHERE site=? AND activityevent=? AND cid=? ORDER BY rank ASC` 用於頒獎顯示，無需過濾
- **投注查詢**：`SELECT * FROM betpool_bets WHERE gid=?` 預設回傳所有注單；若需依帳戶過濾應在應用層篩選，或另以 `account+gid` 索引查詢（若存在）
- **遊戲清單查詢**：`SELECT * FROM betpool_games WHERE status IN (1,2)` 只回傳進行中或上線的遊戲；`status=0`（未上線）、`status=-1`（關閉）不應出現在使用者端；若為一般使用者，應額外過濾 `viponly=false`（或由應用層判斷VIP身份後決定是否顯示VIP限定遊戲）
- **遊戲詳細查詢**：`SELECT * FROM betpool_games WHERE id=?` 回傳單一遊戲，須檢查 `status` 是否符合前台可見條件（status≥1）
- **歷史遊戲查詢**：`SELECT * FROM betpool_games WHERE status=3 AND starttime>=?` 查詢已結束遊戲，須限制時間範圍避免全掃
- **計算日誌查詢**：`SELECT done FROM calculatelog WHERE weekid=?` 檢查指定週是否已完成計算；歷史查詢 `SELECT * FROM calculatelog WHERE weekid=? AND addtime>=?` 限制時間範圍
- **殺手帳號統計查詢**：`SELECT avgodd, addtime FROM killeraccounts_BK` 無需指定條件，返回最新一筆記錄；如需歷史分析可依 `addtime` 篩選

### 不可回傳欄位

- **activities_record.winbets**：僅供結算內部使用；對外 API 不應回傳完整注單列表（可回傳數量）
- **betpool_bets.account**：使用者投注隱私；除本人查詢外，公開查詢（如遊戲注單熱度）不應回傳完整 account
- **betpool_games.basicprofitzcoin / bonusprofitzcoin**：內部利潤配置，不對外披露
- **betpool_games.feedrate**：費率為敏感商業資訊，僅管理後台可見
- **activities_winneraccounts.winpercentage**：排名清單中可回傳，但為避免被視為營運機密，可僅對獲勝者本人顯示
- **killeraccounts_BK.avgodd**：內部統計指標，不對外暴露

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `session:{authkey}` | 登入成功後寫入 | 7 天；續期邏輯每次 API 呼叫自動延長 |
| GET | `banned:{authkey}` | 封禁時寫入，每次請求檢查 | 永久；解封時 DEL |
| SET / GET | `email_verify:{email}` | 發送驗證信時寫入驗證碼 | 10 分鐘；驗證成功後 DEL |
| INCR / EXPIRE | `login_fail:{email}` | 登入失敗時累計 | 15 分鐘；超過 5 次觸發鎖定 |
| SET / GET | `membership:{authkey}` | 訂閱成功後快取會員資格 | 1 小時；memberships 異動時主動 DEL |
| GET | `robot_accounts` | 啟動時載入 gamerobots.enabled=1 清單 | 永久；有變更時主動 PUBLISH 更新 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 支付流程處理 | paymentservice | gamesublogs 由支付回調寫入，本服務僅讀取訂閱狀態 |
| 積分計算與發放 | pointservice | gameusers.rank / gamecount 由積分服務更新，本服務僅讀取 |
| 遊戲場次結算 | gameservice | predictbets_{game_type} 的 winloss / profitpoint 由遊戲服務寫入 |
| 簽到獎勵邏輯 | taskservice | signindays 累計由任務服務負責，本服務僅更新 signindate |
| 頭像上傳與儲存 | fileservice | headshotpath 僅儲存路徑，實際檔案由檔案服務管理 |

---

## 常見錯誤

- ❌ **直接 `UPDATE gameusers SET status=1` 封禁帳號** → ✅ 須同時寫入 gameusers_banned，並快取至 Redis `banned:{authkey}`，否則分散式環境可能漏檢
- ❌ **註冊時未檢查 forbidden_email_domains** → ✅ 必須先 `SELECT` 確認 email domain 不在禁用清單
- ❌ **使用 `ALLOW FILTERING` 查詢 gameusers.account** → ✅ account 無索引，應改用 email(有索引)或 authkey(主鍵)查詢
- ❌ **查詢 predictbets_{game_type} 未限制 gdate 範圍** → ✅ Cassandra 必須指定分區鍵(gdate)範圍，否則全表掃描導致超時
- ❌ **黑名單清單無上限檢查** → ✅ black_account / focus_account / follow_account 須限制單一使用者不超過 1000 筆
- ❌ **密碼使用 MD5 雜湊** → ✅ 必須使用 bcrypt(cost≥10)或 scrypt，並加鹽
- ❌ **登入失敗未做頻率限制** → ✅ 應透過 Redis `INCR login_fail:{email}` 累計，超過 5 次/15 分鐘鎖定帳號
- ❌ **memberships 清單直接覆蓋寫入** → ✅ Cassandra list 需使用 `UPDATE ... SET memberships = memberships + ['new_item']` 追加語法
- ❌ **authkey 明文記錄在日誌** → ✅ 日誌中 authkey 須遮罩(如僅保留前 8 碼)
- ❌ **activities_winneraccounts 排名手動調整** → ✅ 應由結算程序重新計算，手動覆蓋可能導致資料不一致
- ❌ **直接對 activities_record.winbets 進行字串解析比對** → ✅ winbets 為 list 結構，應用層需使用集合操作，避免全表掃描