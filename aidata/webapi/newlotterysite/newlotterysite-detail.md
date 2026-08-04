# newlotterysite — DB 操作邊界

> 產出時間：2025-04-09 14:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## payment

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra payment keyspace | reader | Schema：[db/payment.md](../../db/payment.md) · 語意：[db/payment-detail.md](../../db/payment-detail.md) |

### 寫入限制

- **paymethods_sport.enabled**：僅管理後台透過 `UpdatePaymentMethod` 端點設置；新抽獎服務不可直接寫入 `enabled` 欄位
- **rechargeplans_newlottery.starttime / endtime / enabled**：充值方案的啟用狀態必須與時間區間同時生效；不可單獨寫 `enabled=1` 卻忽略時間範圍檢查
- **products_activity.quantity**：僅能透過兌換邏輯遞減（扣庫存），不可直接 UPDATE 增加數量；無庫存時應返回錯誤（`quantity <= 0`）
- **products_activity.status**：僅系統管理功能可修改；影響前端是否展示（`status=0` 時不可兌換）
- **products_activity_redeem_logs.id**：由系統自動產生（UUID），任何 API 不可手動指定
- **commissions_betpool_newlottery**：`id`、`betpool`、`source_uid` 一旦寫入不可變更；佣金記錄不可 DELETE

### 讀取規則

- **取得可用充值方案**：需過濾 `enabled = 1` 且當前時間戳在 `starttime` 與 `endtime` 之間；過期或未啟用的方案不可暴露給前端
- **取得支付方式**：需過濾 `enabled = 1`；禁用支付方式不可返回（即使分區鍵存在）
- **活動產品查詢**：需以 `(site, activityevent)` 為分區鍵查詢，並過濾 `status = 1` 且 `quantity > 0`；不可回傳下架或已無庫存產品
- **兌換日誌查詢**：依 `(site, activityevent, account, status)` 可查詢使用者兌換紀錄；不可跨帳號查詢

### 不可回傳欄位

- **paymethods_sport.names**：多語言名稱映射（`map<text, text>`），對外 API 不可暴露完整 map，應轉為單一語言字串
- **rechargeplans_newlottery.lastupdatetime**：最後更新時間（內部管理時間戳），不對外公開
- **commissions_betpool_newlottery.source_cid**：來源客戶ID（代理商等級敏感的聯絡資訊），不可回傳給終端使用者

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member keyspace | owner | Schema：[db/member.md](../../db/member.md) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **gameusers.password**：僅註冊／修改密碼 API 可寫入；必須以 BCrypt 雜湊後儲存；任何查詢不得回傳明文或雜湊值
- **gameusers.authkey**：由系統自動產生（UUID），創建後不可修改；不可手動指定
- **gameusers.status**：僅管理後台或內部邏輯可修改（例如封禁／解封）；影響登入過濾（`status=1` 才視為正常）
- **gameusers.email**：僅註冊時寫入；若有修改流程，必須驗證新郵箱且原郵箱不可直接覆蓋（需驗證碼）
- **gameusers.addtime**：註冊時寫入後不可修改
- **gameusers.account**：一旦註冊不可修改（唯一登入名）；若允許改名，需透過專用 API 並檢查唯一性
- **gameusers.black_account / focus_account / follow_account**：僅使用者本人可操作（透過添加／移除 API）；列表修改需保證原子性（LWT 或批次寫入）
- **gamesublogs**：僅寫入（append-only），不支援 UPDATE 或 DELETE；訂閱記錄不可篡改
- **gameusers_banned**：僅管理後台可寫入；寫入後不可修改；封禁結束後記錄保留作為審計
- **gamerobots**：僅內部初始化寫入；`enabled` 可切換（1 啟用 / 0 禁用），但不可由外部 API 操作
- **forbidden_email_domains**：僅管理後台可新增／刪除；name 為唯一約束，不允許重複
- **appleinfos_game**：僅 Apple 登入綁定流程可寫入；`id` 為唯一鍵，不可修改

### 讀取規則

- **登入驗證**：查詢 `gameusers` 時必須指定分區鍵 `authkey` 或 `account`；若使用 `account`，必須使用全域索引（若無索引則不可行），否則應以 `authkey` 查詢；過濾 `status = 1`（正常狀態），不可登入狀態異常或已刪除用戶
- **查詢已註冊郵箱**：必須使用 `email` 二級索引（若存在）或全表掃描不可接受；實際應以 `account` 唯一性檢查為主
- **獲取用戶資料**：除了登入場景，應僅透過 `authkey` 查詢，避免回傳敏感欄位（`password` 等）
- **訂閱記錄查詢**：需使用 `authkey` 作為分區鍵，必要時加入 `subtime` 排序過濾（最新記錄）
- **封禁檢查**：查詢 `gameusers_banned` 需使用 `authkey`，並過濾 `endtime > now` 以判斷是否仍在封禁期
- **機器人帳號列表**：查詢 `gamerobots` 時可過濾 `enabled=1` 以取得活躍機器人
- **禁止域名檢查**：註冊流程中需查詢 `forbidden_email_domains` 檢查輸入的 email domain 是否存在於 `name` 欄位；此表很小，可全表快取
- **Apple 資訊查詢**：以 `id` 為分區鍵，不可跨 apple ID 查詢

### 不可回傳欄位

- **gameusers.password**：密碼雜湊值，任何對外 API 不可回傳（包括管理後台）
- **gameusers.authkey**：內部認證金鑰，不可暴露給前端或第三方；應使用代號或 token 代替
- **gameusers.email**：郵箱屬敏感個資，非必要不回傳；若需回傳需脫敏（如只顯示前後兩字元）
- **gameusers.siteid / adsource**：站點內標識及廣告來源，屬於內部資料，不對外公開
- **gamesublogs.tradeno**：交易編號，涉及支付隱私，不應回傳給非本人
- **gameusers_banned.description**：封禁原因描述僅供內部審計，不對外顯示
- **forbidden_email_domains**：內部安全列表，不應回傳給前端

---

## ads

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra ads keyspace | owner | Schema：[db/ads.md](../../db/ads.md) · 語意：[db/ads-detail.md](../../db/ads-detail.md) |

### 寫入限制

- **advertising.id**：由系統自動產生；僅內部管理 API 可指定（若為 UUID），前端不可自訂
- **advertising.createdby**：寫入後不可修改；僅於創建時填入當前操作帳號
- **advertising.closetime / starttime**：必須符合業務邏輯（`starttime < closetime`）；不可寫入過去時間作為開始時間（除非排程需求）
- **advertising.enabled**：僅管理後台可修改；新抽獎服務不可直接修改（若無後台權限）
- **advertising_sport.adarea** + **id**：組合為分區鍵與叢集鍵，一經寫入不可變更（C* 叢集鍵不可更新）
- **advertising_sport.startdate / closedate**：字串日期必須為 `YYYY-MM-DD` 格式；`startdate` 不得晚於 `closedate`
- **advertising_sport.supportlangs**：寫入時需校驗各語言代碼是否在允許清單內；不可包含封閉代碼
- **bulletinboard_sport.aid** + **addtime** + **announcementmethod**：組合主鍵（分區+叢集），寫入後不可修改
- **bulletinboard_sport.status**：僅管理後台可切換啟用/禁用；影響前端公告顯示
- **bulletinboard_sport.maintopic / text1 / text2 / text3**：多語言 map 鍵值對需符合支援的語言集合，不允許空 key 或非法語言代碼

### 讀取規則

- **取得前台廣告列表（advertising）**：過濾 `enabled = 1` 且 `starttime <= 當前時間戳 <= closetime`；有效廣告回傳
- **取得前台廣告列表（advertising_sport）**：依 `adarea` 分區查詢，過濾 `enabled = 1`，且 `startdate <= 當前日期字串 <= closedate`；返回結果依 `seq` 遞增排序
- **取得前台公告列表（bulletinboard_sport）**：需以 `aid` 為分區鍵查詢，過濾 `status = 1`，且 `starttime <= 當前時間字串 <= endtime`；依 `sequence` 排序；若未指定 `aid` 則須全表掃描，不應使用（必須提供分區鍵）
- **廣告/公告多語言展示**：前端請求應攜帶語言代碼，後端從 `map` 中提取對應語言的內容；不可回傳完整 map 內容

### 不可回傳欄位

- **advertising.createdby**：創建者帳號，屬於內部管理資訊，對外 API 不可回傳
- **advertising_sport.adclass**：廣告分類代碼（若為內部代號）不對外暴露；前端只需顯示 `type` 區分
- **bulletinboard_sport.addtime / lastup_time**：內部時間戳，不對前端公開（前端使用 `starttime` / `endtime` 即可）
- **bulletinboard_sport.announcementmethod**：公告發布方式（推送、彈窗等），屬於內部設定，不應回傳

---

## sport

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport MySQL | owner | Schema：[db/sport.md](../../db/sport.md) · 語意：[db/sport-detail.md](../../db/sport-detail.md) |

### 寫入限制

- **gameusers_wallet.AuthKey**：由系統自動產生（UUID），寫入後不可修改；任何 API 不可手動指定或覆蓋
- **gameusers_wallet.Balance**：僅能透過交易邏輯遞增／遞減（對應 `gameusers_wallet_transactions` 寫入），不可直接 UPDATE；需搭配樂觀鎖或 LWT 避免超扣
- **gameusers_wallet_transactions.TID**：由系統自動增長（AUTO_INCREMENT），任何 API 不可手動指定
- **gameusers_wallet_transactions.Amount**：寫入後不可修改（交易流水不得篡改）；`Type` 與 `Amount` 正負號需匹配業務邏輯（存款為正、提款為負）
- **gameusers_wallet_transactions.AddTime**：寫入後不可修改，反映交易實際發生時間
- **community_groups.Enabled**：僅管理後台可修改（0 禁用 / 1 啟用）；影響前端群組列表顯示
- **community_groups.Owner**：寫入後不可轉讓；若需更改擁有者，需透過專用 API 並確保原子性
- **chatroomhistories** 與 **chatroomhistories_backup**：僅寫入（append-only），不支援 UPDATE 或 DELETE；訊息回覆關係（`ResponseID`）不可事後修改
- **chatroomhistories.LikeAccount**：僅使用者的按讚/取消按讚操作可修改；須保證原子性（更新時讀取原列表並寫回）
- **notification_messages.Enabled**：僅管理後台可切換；影響前端訊息顯示（`Enabled=0` 時不可回傳）
- **notification_sitemails.ReadStatus**：僅使用者本人可透過「標記已讀」API 修改（0 → 1）；不可逆向變更
- **notification_topics.Enabled**：僅管理後台可修改；影響主題分類是否在前端展示

### 讀取規則

- **聊天室歷史查詢**：必須以 `GID` 為分區鍵（若無索引則不可跨分區查詢）；可追加 `AddTime` 排序過濾（最新訊息優先）
- **取得活躍群組列表**：查詢 `community_groups` 時需過濾 `Enabled = 1`，返回結果依 `Seq` 遞增排序；禁用群組不可暴露
- **取得可用通知主題**：需過濾 `notification_topics.Enabled = 1`，依 `Seq` 排序
- **取得指定主題下啟用訊息**：查詢 `notification_messages` 時以 `TID` 為查詢條件（需搭配索引），並過濾 `Enabled = 1`
- **站內信查詢**：必須以 `Account` 為分區鍵（或搭配 `ID` 叢集鍵）；不可跨帳號查詢；可過濾 `ReadStatus`（0 未讀 / 1 已讀）
- **錢包餘額查詢**：以 `AuthKey` 為唯一查詢鍵；不可回傳 `gameusers_wallet_transactions` 明細（除非本人查詢歷史交易）
- **交易明細查詢**：須以 `AuthKey` 為分區鍵，可依 `TDate` 或 `AddTime` 範圍過濾；不可跨 AuthKey 查詢
- **每日報表查詢**：`memberdailyreport` 及 `predictdailyeport` 以 `Reportdate` 為分區鍵，不支援跨日期全表掃描（管理端除外）
- **運動球員資料查詢**：`bk_siteplayers` 以 `(Site, SiteID, Year)` 或 `(Site, League, Year)` 為複合分區鍵；查詢時必須提供完整分區鍵，不可模糊查詢

### 不可回傳欄位

- **gameusers_wallet.AuthKey**：內部認證金鑰，對外 API 不可回傳；前端應使用 session token 代替
- **gameusers_wallet_transactions**：交易明細預設不對外回傳；若使用者請求查詢，僅回傳摘要欄位（`AddTime`, `Amount`, `Type`, `TypeInfo`），不可回傳 `TID` 以外的內部鍵
- **chatroomhistories.LikeAccount**：按讚帳號完整列表屬社交隱私，對外 API 不可回傳；應僅回傳按讚總數
- **chatroomhistories.UserName** 與 **HeadShotPath**：若涉及真實姓名或頭像路徑，對外 API 應脫敏（如僅回傳暱稱）或依權限控制
- **community_groups.Owner**：擁有者帳號為內部資訊，不對外暴露；前端僅顯示群組名稱與圖示
- **notification_messages.TW_Content / EN_Content / CN_Content / JP_Content / TH_Content**：對外 API 不可回傳完整多語言 map，應依請求語言回傳對應內容
- **notification_sitemails.Subject** 與 **Content**：屬個人隱私，對外 API 僅在本人查詢時回傳；管理端查詢需有明確權限

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET | `ads:advertising:enabled:{site}` | 後台更新廣告（advertising）後 | 快取該站點所有已啟用且未過期廣告；TTL 建議 5 分鐘或根據下一次排程更新時間 |
| DEL | `ads:advertising:enabled:{site}` | 廣告新增/修改/刪除時 | 主動失效，下次查詢重新載入 |
| SET | `ads:advertising_sport:area:{adarea}` | 後台更新或排程刷新廣告區域時 | 快取指定區域的啟用廣告列表；TTL 建議 10 分鐘 |
| DEL | `ads:advertising_sport:area:{adarea}` | 該區域廣告內容變動時 | 主動失效，確保一致性 |
| SET | `ads:bulletinboard:active:{site}` | 後台更新公告或定期刷新時 | 快取目前有效公告；TTL 建議 5 分鐘 |
| DEL | `ads:bulletinboard:active:{site}` | 公告狀態變更或內容修改時 | 主動失效 |
| SET | `sport:chatroom:history:{GID}` | 聊天室新訊息寫入時 | 快取最近 N 筆訊息（如 50 筆）；TTL 建議 3 分鐘或根據活躍度調整 |
| SET | `sport:community_groups:enabled` | 管理後台更新群組狀態時 | 快取所有啟用群組（`Enabled=1` 並依 `Seq` 排序）；TTL 建議 10 分鐘 |
| DEL | `sport:community_groups:enabled` | 群組新增/修改/刪除時 | 主動失效，確保列表一致 |
| SET | `sport:notification:active:{TID}` | 後台更新通知訊息時 | 快取指定主題下的啟用訊息；TTL 建議 5 分鐘 |
| DEL | `sport:notification:active:{TID}` | 該主題訊息狀態變更時 | 主動失效 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 支付金流處理 | payment 服務 | 本服務僅讀取 `paymethods_sport`、`rechargeplans_newlottery` 方案與設定，實際扣款、退款、支付閘道對接由 payment 服務負責 |
| 活動產品庫存扣減與補貨 | activity 或 inventory 服務 | `products_activity.quantity` 之扣減由本服務觸發（兌換），但補貨、庫存預留機制由活動服務管理 |
| 佣金結算與發放 | commission 或 settlement 服務 | `commissions_betpool_newlottery` 僅記錄佣金明細，實際佣金計算、結算、發放由專用佣金服務處理 |
| 廣告投放管理與點擊統計 | ad management 或 analytics 服務 | 本服務僅儲存廣告設定與展示；廣告投放規則、投放策略、點擊／曝光統計由其他專用服務負責 |
| 公告發送推送 | push notification 服務 | `announcementmethod` 定義方式，但實際推送觸發由 push 服務執行 |
| 聊天內容審核 | content moderation 服務 | `chatroomhistories.Message` 內容審核、敏感詞過濾由專用審核服務負責；本服務僅儲存與讀取 |
| 通知推送（站內信除外） | push notification 服務 | `notification_sitemails` 為站內信，由本服務管理；但其餘即時推送（如手機推播）由 push 服務觸發 |
| 錢包交易結算 | transaction settlement 服務 | `gameusers_wallet_transactions` 僅記錄明細；實際結算（如紅利發放、系統調整）由專用結算服務處理 |

---

## 常見錯誤

- ❌ **讀取池方案時未檢查 `starttime` / `endtime`** → ✅ 查詢 `rechargeplans_newlottery` 時必須加入 `enabled = 1` 且 `now >= starttime AND now <= endtime` 條件，避免回傳已失效方案
- ❌ **計算佣金時忽略 `betpool` 分區鍵** → ✅ `commissions_betpool_newlottery` 查詢時必須指定 `betpool`（分區鍵），否則會 full scan 或查詢錯誤
- ❌ **兌換日誌寫入時未指定 `activityevent` 與 `site`** → ✅ `products_activity_redeem_logs` 的 (`site`, `activityevent`) 為分區鍵，寫入時必須提供完整分區鍵
- ❌ **活動產品庫存扣減時未使用輕量級事務（LWT）** → ✅ 扣減 `products_activity.quantity` 時應搭配 LWT (`quantity > quantity - 1`) 避免超賣
- ❌ **查詢兌換紀錄時以非分區鍵查詢** → ✅ 只能以 `(site, activityevent, account, id)` 或 `(site, activityevent, account, pid)` 等叢集鍵模式查詢，不可跨分區查詢
- ❌ **讀取廣告（advertising_sport）時未過濾 `enabled` 或時間區間** → ✅ 需同時檢查 `enabled = 1` 且 `startdate <= 今日 <= closedate`，避免回傳已下架或未上線廣告
- ❌ **未指定分區鍵查詢 `bulletinboard_sport`** → ✅ 必須以 `aid` 作為分區鍵查詢，若需獲取所有公告應透過後台或設計專用查詢（如使用二級索引或全表掃描僅允許管理端）
- ❌ **公告多語言 map 直接回傳前端** → ✅ 應僅回傳請求語言對應的內容，避免暴露完整 map 結構（可能洩漏支援語言及內部資料）
- ❌ **聊天室歷史以非分區鍵查詢** → ✅ 查詢 `chatroomhistories` 或 `chatroomhistories_backup` 時必須指定 `GID` 為分區鍵；不可跨群組全表掃描
- ❌ **錢包餘額直接 UPDATE 未用交易記錄** → ✅ 所有 `Balance` 變更必須透過 `gameusers_wallet_transactions` 插入交易記錄後同步更新；不可直接 `UPDATE gameusers_wallet SET Balance = Balance + X`
- ❌ **站內信未以帳號分區鍵查詢** → ✅ 查詢 `notification_sitemails` 時必須以 `Account` 為分區鍵；不可跨帳號查詢或全表掃描
- ❌ **運動球員資料查遺漏分區鍵** → ✅ 查詢 `bk_siteplayers` 時必須提供完整分區鍵（如 `Site`, `SiteID`, `Year` 或 `Site`, `League`, `Year`）；不可無限制模糊查詢