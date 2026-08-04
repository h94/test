# pricebackendservice — DB 操作邊界

> 產出時間：2025-03-27 17:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member keyspace | writer / reader | Schema：[db/member.md](../../db/member.md) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **gameusers**：
  - `authkey`、`account`、`password` 僅在建立用戶時由 `IGameSettingService.CreateUser` 寫入，**不可透過 UPDATE 修改**。
  - `email`、`site`、`siteid` 建立後僅允許 `UpdateUser` 修改非關鍵業務欄位（如 `username`、`headshotpath`、`rank`、`lastactiontime`、`lastchecktime`、`signindate`、`signindays`、`gamecount`、`renamecount`、`showcode`）。
  - `black_account`、`focus_account`、`follow_account`、`memberships` 列表需透過專用方法（如 `UpdateGameUserMembership`）更新，**禁止直接 REPLACE 整個列表**。
- **gameusers_banned**：僅由 `MemberService.CreateBannedGameUser` 寫入，**不允許直接 INSERT / UPDATE**，停權資料由系統統一管理。
- **gamesublogs**：僅由 `IGameSettingService.CreateSubcriber`（新增）或 `UpdateSubcriber`（修改 `autosub`、`subid`）寫入，**不可直接操作該表**。
- **forbidden_email_domains**：僅由 `MemberService.CreateForbiddenEmailDomains` 寫入，**不允許直接 DELETE 或 UPDATE**。
- **gamerobots**：本服務僅讀取，寫入由管理後台或外部工具負責。
- **appleinfos_game**：本服務僅讀取，寫入由 Apple 登入流程處理。

### 讀取規則

- **gameusers**：
  - 依 `authkey` 主鍵查詢單筆用戶（最常用）。
  - 依 `account` 批次查詢用於交易報表、商品兌換記錄關聯。
  - 依 `email` 索引（`myindex`）查詢用於商品兌換記錄匯出；**注意**：Scylla/Cassandra 次級索引不適合高並發大量掃描，僅限低頻管理操作。
  - 讀取時建議過濾 `status = 0`（正常狀態），避免回傳已停用或凍結用戶。
  - 查詢結果需排除 `member.gamerobots.account` 中的機器人帳號（透過 `HashAuthString(account)` 比對交易資料的 `AuthKey`）。
- **gamerobots**：
  - 讀取 `account`、`enabled` 欄位，用於過濾交易報表中的機器人交易記錄。
- **gamesublogs**：
  - 依 `authkey` 分區鍵查詢用戶訂閱歷史，可搭配 `addtime` 排序。
  - 查詢結果用於判斷用戶當前訂閱狀態（如 `subendtime` 是否過期、`autosub` 是否啟用）。
- **forbidden_email_domains**：
  - 全表讀取（通常快取），用於註冊時驗證電子郵件網域是否被禁止。
- **appleinfos_game**：
  - 依 `email` 或 `id` 查詢 Apple 用戶資訊（用於關聯遊戲資料）。
- **gameusers_banned**：
  - 依 `authkey` 查詢單筆停權記錄，或使用 `GetAllBannedGameUsers` 取得全量列表，用於判斷用戶是否被停權及查看停權原因。

### 不可回傳欄位

- **gameusers.password**：任何對外 API 皆不可回傳密碼欄位（無論是否雜湊）。
- **gameusers.authkey**：僅內部服務間傳遞，不對外暴露原始認證金鑰；對外應使用 DTO 轉換。
- **gameusers.email**：雖有索引，但仍視為敏感個資，**一般查詢 API 不應回傳**（除非是特定後台匯出或用戶本人修改資料場景）。
- **gameusers_banned.description**、**endtime**：對一般用戶不暴露停權細節，僅管理後台可回傳。

---

## payment

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra payment keyspace | writer / reader | Schema：[db/payment.md](../../db/payment.md) · 語意：[db/payment-detail.md](../../db/payment-detail.md) |

### 寫入限制

- **products_activity.id**：僅在建立產品時由系統自動生成，不允許後續更新。
- **products_activity.updatetime**：由系統在每次寫入時自動更新，不允許 API 直接設定。
- **products_activity_redeem_logs.addtime**：由系統在兌換發生時自動生成，不允許手動寫入。
- **products_activity_redeem_logs.id**：系統生成，不可修改。
- **commissions_betpool_newlottery.id**：系統生成，不可修改。
- **rechargeplans_newlottery.id**：系統生成，不可修改。
- **所有表的 lastupdatetime / updatetime**：應由系統自動更新，不得透過 API 直接寫入。

### 讀取規則

- **products_activity**：
  - 查詢商品清單時通常過濾 `status = 1`（上架），忽略下架商品。
  - 依 `site`、`activityevent` 組合篩選特定活動的商品列表。
- **products_activity_redeem_logs**：
  - 查詢時以 `site`、`activityevent` 為必要條件，可搭配 `account`、`id`、`status` 進行過濾。
  - 時間範圍查詢常用 `addtime` 排序（依業務需求）。
- **paymethods_sport**：
  - 讀取可用支付方式時須 `enabled = 1`，避免回傳已停用方式。
- **rechargeplans_newlottery**：
  - 讀取有效方案時須 `enabled = 1`，且 `starttime <= now < endtime`（若使用時間限制）。
- **commissions_betpool_newlottery**：
  - 查詢特定 `betpool` 的佣金記錄，通常按 `addtime` 降序排列以取得最新資料。

### 不可回傳欄位

- 無。本服務管理的 payment 表格中不含密碼、金鑰等敏感欄位，所有欄位皆可依業務需求回傳。但應注意 `names` 為多語言 map，依前端語言代碼過濾回傳。

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra predict keyspace | writer / reader | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **activities_cycles.site、activityevent、cid**：為複合主鍵，建立時由業務邏輯生成，不允許後續更新。
- **activities_cycles.startdate、starttime、enddate、endtime**：由系統根據活動週期設定，不允許 API 直接修改。
- **activities_cycles.resultcount**：由系統根據週期結果數量自動更新，不允許手動寫入。
- **activities_record.site、eventname、account**：為複合主鍵，建立時確定，不允許更新。
- **activities_record.updatedate**：由系統在每次記錄更新時自動設定，不允許 API 直接寫入。
- **activities_winneraccounts.site、activityevent、cid、account**：為複合主鍵，由系統在結算時生成，不允許手動建立或更新。
- **activities_winneraccounts.rank、predictcount、profitpoint、winpercentage**：由系統根據計算規則自動設定，不允許 API 直接寫入。
- **betpool_bets.id**：系統生成，不可修改。
- **betpool_bets.addtime**：由系統在投注發生時自動生成，不允許手動寫入。
- **betpool_games.id**：系統生成，不可修改。
- **betpool_games.starttime、endtime、updatetime**：由系統時間管理，不允許 API 直接寫入。
- **betpool_games.payout、winresult**：由系統在結算時設定，不允許手動修改。

### 讀取規則

- **activities_cycles**：
  - 查詢活動週期時通常依 `site`、`activityevent` 過濾，並搭配時間範圍條件（`startdate`、`enddate`）以取得有效週期。
  - 查詢特定週期時以 `site`、`activityevent`、`cid` 為必要條件。
- **activities_record**：
  - 查詢用戶活動記錄時以 `site`、`eventname`、`account` 為必要條件。
  - 依 `updatedate` 範圍篩選特定時間內的活動記錄。
- **activities_winneraccounts**：
  - 查詢排行榜時以 `site`、`activityevent`、`cid` 為必要條件，並按 `rank` 升序排列以取得排名順序。
  - 可搭配 `predictcount`、`profitpoint` 進行二次排序，但主排序仍以 `rank` 為準。
- **betpool_bets**：
  - 查詢特定遊戲的投注記錄時以 `gid` 為必要條件，可搭配 `account` 過濾單一用戶的投注。
  - 依 `addtime` 排序以取得投注時間序列。
- **betpool_games**：
  - 查詢遊戲清單時通常過濾 `status = 1`（開放），忽略關閉遊戲。
  - 查詢需要結算的遊戲時過濾 `payout = false` 且 `status = 2`（結束）。
  - 依 `starttime` 或 `endtime` 範圍篩選特定時間區間的遊戲。

### 不可回傳欄位

- 本服務管理的 predict 表格中不含密碼、金鑰等敏感欄位，所有欄位皆可依業務需求回傳。

---

## ads

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra ads keyspace | owner | Schema：[db/ads.md](../../db/ads.md) · 語意：[db/ads-detail.md](../../db/ads-detail.md) |

### 寫入限制

- **advertising.id**：主鍵，建立時生成，**建立後不可更新**。
- **advertising_sport.adarea**：分區鍵，建立後不可修改。
- **advertising_sport.id**：集群鍵，建立後不可修改。
- **bulletinboard_sport.aid**：主鍵，建立後不可修改。
- **advertising.enabled**、**advertising_sport.enabled**、**bulletinboard_sport.status**：僅能由管理後台或對應管理 API 更新，不允許一般業務邏輯直接修改。
- **advertising.path**、**advertising_sport.imgpath**、**advertising_sport.mobileimgpath**：圖片路徑由廣告建立 / 上傳流程寫入，**不允許透過 API 直接賦值原始路徑**（應經由上傳或專用方法）。
- **advertising_sport.supportlangs**（`list<text>`）：**不可直接 REPLACE 整個列表**，應透過驗證邏輯後以專用方法逐元素新增或刪除。
- **bulletinboard_sport.maintopic**、**text1**、**text2**、**text3**（`map<text, text>`）：**不可直接 REPLACE 整個 map**，應逐鍵更新，避免覆蓋未變更的語言鍵值。
- **advertising_sport.closedate**、**startdate**：僅在廣告活動編輯時可修改，必須符合日期格式，且不應被一般使用者 API 直接設定。
- **所有 `addtime` / `lastup_time` / `updatetime`**：由系統自動設定，**不允許手動寫入**。

### 讀取規則

- **advertising_sport**：
  - 必須以 `adarea` 為分區鍵條件，避免跨分區全表掃描。
  - 查詢有效廣告時需過濾 `enabled = 1`，且 `startdate <= 今天 <= closedate`（若日期欄位有值）。
  - 結果依 `seq` 升序排列。
  - 若需依語言篩選，應檢查 `supportlangs` 列表是否包含目標語系。
- **advertising**：
  - 查詢時通常過濾 `enabled = 1`，並依 `starttime`、`closetime` 時間範圍篩選有效廣告。
  - 可依 `type`（如 right）或 `lang`（支援語言包含目標語系）進一步過濾。
  - 結果依 `seq` 排序。
- **bulletinboard_sport**：
  - 查詢已發布公告時必須過濾 `status = 1`，且當前時間應在 `starttime` ~ `endtime` 之間。
  - 依 `addtime` 降序或 `sequence` 升序排列。
  - 多語言內容應由 API 層依照前端語系從 `maintopic`、`text1` 等 map 中提取對應語言文字。

### 不可回傳欄位

- **advertising_sport.imgpath**、**mobileimgpath**、**advertising.path**：可能為內部儲存路徑，對外 API 必須回傳完整可存取的 CDN URL。
- **advertising_sport.tageturl**：未經安全過濾的原始目標網址不應直接回傳，前端應在點擊時進行重定向驗證，防止惡意連結或釣魚。
- **advertising.createdby**：除非管理場景，一般 API 不應暴露創建者資訊。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 廣告點擊統計與曝光分析 | 第三方追蹤服務 | 僅提供廣告素材與連結，不負責統計與分析 |
| 廣告內容合規審查 | 法務/合規團隊 | 廣告內容審查由管理後台與法務團隊負責 |

### 常見錯誤

- ❌ 直接對 `advertising_sport` 全表掃描而無 `adarea` 分區鍵 → 應始終搭配 `adarea` 等分區鍵查詢，避免跨節點掃描。
- ❌ 在廣告圖片路徑更新中直接覆蓋 `supportlangs` 整個列表 → 應保留未變更的語言條目，避免遺失資料。
- ❌ 未檢查時間範圍就回傳廣告 → 應確保當前時間坐落於 `startdate` 與 `closedate` 之間，否則可能回傳過期廣告。
- ❌ 直接將內部圖片路徑回傳給前端 → 應先拼接為完整的 CDN URL。

---

## community

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra community keyspace | reader | Schema：[db/community.md](../../db/community.md) · 語意：[db/community-detail.md](../../db/community-detail.md) |

### 寫入限制

- **newlottery_forums.id**：主鍵，建立後不可修改。
- **newlottery_forums.country_code**：分區鍵，建立後不可修改，寫入時必須指定有效的國家代碼。
- **newlottery_forums.edit_timestamp**：由系統在欄位變更時自動更新，不允許 API 直接寫入。
- **newlottery_forums.status**：僅能由管理後台或對應管理 API 更新（1=啟用，0=停用），不允許一般業務邏輯直接修改。
- **newlottery_forums.icon**：由管理流程寫入（如檔案上傳），不建議透過 API 直接賦值原始路徑，應使用專用方法設定。
- **newlottery_forums.names**（`map<text, text>`）：**不可直接 REPLACE 整個 map**，應逐鍵更新，避免覆蓋其他語言版本；其中 `zh-TW` 必須存在且不可為空。

### 讀取規則

- **newlottery_forums**：
  - 查詢論壇清單時，必須過濾 `status = 1`（已啟用），確保僅回傳公開的論壇。
  - 依 `country_code` 為必要分區鍵條件，避免跨分區全表掃描。
  - 依 `edit_timestamp` 降序排列以取得最近更新的論壇（常用於快取刷新判斷）。
  - 單筆查詢時建議以 `country_code` 與 `id` 組合，明確分區路由。
  - 多語言名稱應由 API 層根據前端語系從 `names` map 中提取對應文字。

### 不可回傳欄位

- **newlottery_forums.icon**：可能為內部儲存路徑，對外 API 應回傳完整可存取的 CDN URL，而非原始路徑。
- **newlottery_forums.edit_timestamp**：若對外 API 無明確時間戳排序需求，建議不回傳，避免暴露內部編輯時序。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 論壇內容管理 (發文、回覆) | communityservice | pricebackendservice 僅讀取論壇基礎資訊，不管理論壇內容 |
| 論壇權限控制 | communityservice | 論壇瀏覽與發文權限由 communityservice 控管 |

### 常見錯誤

- ❌ 直接對 `newlottery_forums` 全表查詢而無 `country_code` 分區鍵 → 應以 `country_code` 為條件，避免跨分區掃描。
- ❌ 直接返回 `icon` 內部路徑給前端 → 應拼接為完整的 CDN URL，否則前端無法載入。
- ❌ 未過濾 `status=1` 就返回所有論壇 → 應僅返回已啟用的論壇，避免顯示尚未發布或已取消的項目。
- ❌ 在 API 回傳中直接暴露 `edit_timestamp` → 若非必要，建議使用處理後的時間格式或省略。

---

## feedback

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra feedback keyspace | writer / reader | Schema：[db/feedback.md](../../db/feedback.md) · 語意：[db/feedback-detail.md](../../db/feedback-detail.md) |

### 寫入限制

- **所有表的複合主鍵**（如 `site, datetime, id`、`tid, datetime, account, id`）：建立後不可修改。
- **businessmessages**：
  - `status`：僅能透過專用 API（如 `UpdateSportSiteBusinessMessageRespContent`）間接更新，**不允許直接 UPDATE**。
  - `sendermail`、`sendcontent`：建立後不可修改，用於保留原始互動記錄。
- **feedbacks_sport** / **feedbacks_stock**：
  - `status`：僅能透過 `FeedbackService.UpdateSportSiteFeedbackMessageStatus` / `UpdateStockFeedbackMessageStatus` 更新（例如 1=待處理, 2=已回覆），不允許一般業務直接 UPDATE。
  - `adminimgpath`（`list<text>`）：**不可直接 REPLACE 整個列表**，應透過 `UpdateSportSiteFeedbackMessageRespImage` 逐步新增或刪除。
  - `problem`、`respcontent`（`list<text>`，每項為 JSON 字串）：追加新互動記錄時應使用專用方法，**禁止直接覆蓋整個列表**。
- **questions_sport** / **questions_stock**、**topics_sport** / **topics_stock**：
  - `id`：主鍵，不可修改。
  - `enabled`：僅能由管理後台或對應管理 API 更新（1=啟用, 0=停用），不允許一般業務邏輯直接修改。
- **所有 `updatetime`**：由系統在資料變更時自動設定，**不允許 API 直接寫入**。

### 讀取規則

- **feedbacks_sport** / **feedbacks_stock**：
  - 查詢時必須以 `tid`（feedbacks_sport）或 `id`（feedbacks_stock）為必要條件，避免全表掃描。
  - 處理狀態過濾：`status=1`（待處理）、`status=2`（已回覆），依需求選用。
  - 時間範圍查詢以 `datetime` 為條件（格式 `yyyy-MM-dd HH:mm`）。
  - 需注意 `problem` 與 `respcontent` 為 JSON 字串列表，解析時應處理可能為 null 的情況。
- **topics_sport** / **topics_stock**、**questions_sport** / **questions_stock**：
  - 查詢時必須過濾 `enabled = 1`，只回傳啟用中的主題或問題。
  - 按 `sort` 升序取得顯示順序；questions 表查詢需搭配 `tid` 關聯主題。
- **businessmessages**：
  - 以 `site` 為必要分區鍵，搭配 `datetime` 範圍查詢。
  - 查詢未處理訊息時過濾 `status = 0`。
  - 排序依 `datetime` 降序。

### 不可回傳欄位

- **feedbacks_sport.email**、**feedbacks_stock.email**、**businessmessages.sendermail**：視為用戶個資，**一般查詢 API 不應回傳**（除非後台匯出或用戶本人查詢）。
- **feedbacks_sport.account**、**feedbacks_stock.account**：除非必要，不應在對外 API 回傳原始帳號名稱，避免帳戶枚舉。
- **feedbacks_sport.imgpath**、**adminimgpath**：內部儲存路徑，對外應拼接為完整 CDN URL。
- **feedbacks_stock 所有用戶個資欄位**：同理應予以保護，僅管理後台可查。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 使用者提交的工單處理與提醒 | feedbackservice (API) | 僅提供查詢與更新回覆狀態，不負責提醒或主動推播 |
| 常見問題內容審查 | 管理後台 | 常見問題內容由營運團隊透過管理後台編輯 |

### 常見錯誤

- ❌ 對 `feedbacks_sport` 進行全表掃描而無 `tid` 分區鍵 → 應始終指定 `tid` 為查詢條件，否則查詢效能極差。
- ❌ 錯誤地以字串比較取代日期範圍查詢 `datetime`→ 應使用正確的字串格式並注意時區問題。
- ❌ 未過濾 `status=1` (待處理) 而直接讀取所有反饋 → 可能回傳已關閉或無效的工單。
- ❌ 直接回傳 `imgpath` 或 `adminimgpath` 原始路徑給前端 → 應拼接完整 CDN URL。
- ❌ 直接覆蓋 `problem` 或 `respcontent` 整個列表 → 應使用 append 邏輯，避免遺失歷史對話記錄。

---

## news

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra news keyspace | reader | Schema：[db/news.md](../../db/news.md) · 語意：[db/news-detail.md](../../db/news-detail.md) |

### 寫入限制

- **aifunshits.funsname**：主鍵，建立後不可修改。
- **ainews / ainews_gs 複合主鍵**（`gdate, gtype, lid, gid, llmhashkey, status`）：建立後不可修改，寫入方（新聞生成服務）需保證主鍵唯一。
- **all `anwser`、`reanwser`、`question`、`bets`、`others`**：由 AI 生成流程寫入，本服務僅讀取，不允許任何寫入操作。
- **ainews.articleid**：由文章發布服務關聯，不可透過本服務修改。
- **ainews.used**：標記是否已採用，由新聞發布邏輯更新，不應由一般查詢 API 變更。
- **`createtime`、`addtime`**：由生成服務自動設定，禁止手動指定。

### 讀取規則

- **aifunshits**：依 `funsname` 主鍵查詢，取得對應的 AI 提示詞與工作區配置。
- **ainews / ainews_gs**：
  - 必須以 `gdate` 為分區鍵，搭配 `gtype`、`lid`、`gid` 等集群鍵進行查詢，避免跨分區掃描。
  - 查詢已生成且可用的 AI 文章時，應過濾 `used = 1` 或 `status` 為特定值（例如 11 表示已使用）。
  - 時間範圍以 `gdate` 為準；若需取得最新文章，可依 `createtime` 排序，但注意 `createtime` 非索引，可能需要應用層處理。
  - 多語言或內容提取：`anwser` 為最終呈現文本，`reanwser` 可作為備選；`others` map 中包含賽事數據，需依需求解析。

### 不可回傳欄位

- `llmsettings`、`llmhashkey`：內部 LLM 配置與雜湊鍵，不應對外暴露。
- `question`：原始提示詞可能包含業務敏感資訊，一般查詢不應回傳。
- `aihints`：提示指令可能包含商業邏輯，限內部使用。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| AI 新聞內容生成與排程 | newsservice (AI 生成模組) | 本服務僅讀取已生成的 AI 新聞，不負責觸發生成或內容管理 |
| 文章發布與前端展示邏輯 | 前端 / CMS 服務 | 查詢結果僅提供原始數據，前端自行決定如何渲染與過濾 |

### 常見錯誤

- ❌ 對 `ainews` 查詢未指定 `gdate` 分區鍵，導致全表掃描 → 必須以比賽日期作為首要查詢條件。
- ❌ 未過濾 `used = 1` 就回傳所有記錄 → 可能包含未採用或暫存生成結果，使用前應確認狀態。
- ❌ 將 `anwser` 與 `reanwser` 同時回傳，未指定優先順序 → 應定義預設回傳 `anwser`，`reanwser` 僅在特定 flag 下使用。
- ❌ 解析 `others` map 時未處理 null → `others` 可能為空 map，需防禦性檢查。

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter keyspace | writer / reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **accounts_* 系列表**（如 `accounts_AU8`, `accounts_Fortuna888`, `accounts_HGA`, `accounts_HGA2`, `accounts_KKK`, `accounts_KU`, `accounts_NK`, `accounts_Panda`, `accounts_TG`, `accounts_TG999`）：
  - `account`（主鍵）：**建立後不可更改**，由註冊或帳戶建立流程寫入。
  - `password`：僅由帳戶建立或專用密碼修改流程寫入（須經雜湊處理），**禁止以一般 UPDATE 直接修改**。
  - `closetime`：僅在帳戶關閉時由系統寫入，不允許 API 直接設定。
  - `enabled`：僅由管理啟用/停用操作更新，不允許一般業務 API 直接修改。
  - `handler`（`map<text, text>`）：**不可直接 REPLACE 整個 map**，應透過專用方法更新特定 key。
  - `phone`：為敏感個資，更新時需驗證，不建議一般 API 直接修改。
- **actionlog**：
  - `date`（分區鍵）、`addtime`（集群鍵）：由系統自動生成，不可手動寫入。
  - `user`、`gametype`、`action`、`actionclass`：由操作服務根據實際行為寫入，不允許事後篡改。
  - `detail`（JSON 字串）：由系統組裝，不可直接由外部輸入未經驗證的 JSON。

### 讀取規則

- **accounts_* 系列表**：
  - 查詢活躍帳戶時必須過濾 `enabled = 1`，避免回傳已停用帳戶。
  - 判斷帳戶是否存在：僅以 `account` 主鍵查詢，不可依 `phone` 或 `username` 等非主鍵欄位推斷。
  - 若 `closetime` 非空，應將該帳戶視為已關閉，在多數業務場景中跳過（除非查詢關閉記錄）。
  - 多平台帳戶需根據表名對應平台（如 `accounts_AU8` 對應 AU8 平台），跨平台操作時應確認目標表。
- **actionlog**：
  - 必須以 `date` 為分區鍵查詢，搭配 `addtime` 範圍、`user` 或 `gametype` 過濾，避免跨分區掃描。
  - 排序依 `addtime` 降序以取得最新操作記錄。
  - 解析 `detail` JSON 時應注意其結構可能隨動作類別不同而異。

### 不可回傳欄位

- `password`：任何對外 API 皆不可回傳密碼欄位（無論是否已雜湊），僅供內部驗證使用。
- `account`：雖為主鍵，但在對外 API 中若無必要（如用戶本人查詢自己資料），不應回傳原始帳戶名稱，避免帳戶枚舉。
- `phone`：視為敏感個資，**不應在一般查詢 API 中回傳**（除非用戶本人修改資訊或特定後台匯出場景）。
- `handler` 中的內部配置資訊：可能包含金鑰或私有路徑，對外不應暴露。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 第三方遊戲平台帳號同步 | pricecenterservice | 僅管理本系統內第三方帳號記錄，不負責與外部平台同步或建立 |
| 密碼雜湊與安全儲存 | authservice / 帳戶模組 | 密碼雜湊處理由專門模組負責，不應直接在業務層實作 |

### 常見錯誤

- ❌ 直接修改 `accounts_*` 的 `password` 欄位，未經雜湊處理 → 應使用專用密碼雜湊方法寫入。
- ❌ 查詢帳戶未過濾 `enabled=1`，導致包含已停用帳戶參與交易 → 需始終檢查 enabled 狀態。
- ❌ 以 `phone` 或 `username` 作為唯一查詢條件判斷帳戶存在 → 應以 `account` 主鍵查詢，避免因非主鍵重複或遺漏導致誤判。
- ❌ 直接覆蓋 `handler` map 而導致遺失既有配置 → 應使用合併或逐鍵更新方式。

---

## product

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra product keyspace | owner | Schema：[db/product.md](../../db/product.md) · 語意：[db/product-detail.md](../../db/product-detail.md) |

### 寫入限制

- **products_store**：
  - `pclass`（分區鍵）、`pid`（集群鍵）：建立後不可修改。
  - `status`：商品上架狀態（`'1'`=上架, `'0'`=下架）僅能由後台管理服務變更，不允許一般 API 直接修改。
  - `price`、`originalprice`：價格異動需經管理審批流程，**不可由前端 API 直接 UPDATE**。
  - `pnames`（`map<text, text>`）：`zh-TW` 必須存在且不可為空；更新時**不可直接 REPLACE 整個 map**，應逐鍵更新。
  - `psource`：不可為空，應為有效的商品來源連結。
  - `lastup_time`：由系統自動更新。
- **products_activity**：
  - `site`（分區鍵）、`activityevent`（集群鍵）、`id`（集群鍵）：建立後不可修改。
  - `status`：僅由活動管理流程更新（0=未發布, 1=已發布）。
  - `price`、`quantity`：由活動建立時初始化，後續僅允許特定管理 API 調整。
- **產品兌換與庫存日誌**（`products_activity_redeem_logs`, `product_store_redeem_logs`, `product_store_stock_logs`）：
  - 主鍵（`site`, `activityevent`, `account`, `id`, `pid` 或 `pclass`, `pid`, `addtime`, `account`, `id` 等）由系統生成，**不可手動寫入或修改**。
  - `status`：遵循狀態機，須透過專用 update 方法（如 `UpdateStoreProductRedeemLog`）變更。
  - `addtime`, `updatetime`：系統自動設定，禁止直接賦值。
  - `account`：記錄兌換用戶，建立後不可修改。
- **withdrawlogs_activity**：
  - `site`, `activityevent`, `account`, `cid` 複合主鍵，建立後不可修改。
  - `status`：僅由提領處理流程更新。

### 讀取規則

- **products_store**：
  - 查詢上架商品時必須過濾 `status = '1'`。
  - 以 `pclass` 為必要分區鍵，搭配 `pid` 查詢單一商品。
  - 列表查詢按 `sequence` 升序排列。
  - 多語言字段 (`pnames`, `description`) 由 API 層根據請求語系提取對應文字；`image_path` map 需注意前端需完整 URL。
- **products_activity**：
  - 查詢時以 `site` 和 `activityevent` 為分區與集群鍵，過濾 `status = 1`。
- **兌換記錄 (redeem_logs)**：
  - 以相關分區鍵和集群鍵組合查詢，過濾 `account` 時須注意隱私。
  - 時間範圍查詢：`addtime` 或 `updatetime` 為排序依據。
  - 狀態過濾：依業務需求篩選（如 1=成功, 2=已出貨）。
- **product_store_stock_logs**：
  - 以 `pclass`, `pid` 為條件，按 `addtime` 降序查看庫存變動歷史。

### 不可回傳欄位

- **product_store_redeem_logs** 中的個人資訊：`address`, `phonenumber`, `recipient`, `cname`, `cheadshot` 等，除非必要（如後台管理或本人查詢），**不應在一般 API 回傳**。
- **products_activity_redeem_logs** 的 `account`：若無業務需求，避免回傳。
- **image_path** 內部路徑：應轉換為完整的 CDN URL 後回傳。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 實體商品物流追蹤 | 物流系統 | 僅記錄出貨狀態，不負責物流追蹤 |
| 活動商品點數發放 | paymentservice | 活動商品兌換後的點數發放由 paymentservice 執行 |

### 常見錯誤

- ❌ 直接修改 `products_store.price` 或 `originalprice` 而未經審批流程 → 可能導致價格錯亂，應透過管理後台流程變更。
- ❌ 未正確處理 `image_path` 多語系 Map，前端無法取得對應圖片 → 確保 Map 中包含 `title` 鍵作為預設值，或依語系回傳正確 URL。
- ❌ 直接覆蓋 `products_store.pnames` Map 而遺失其他語系的翻譯 → 應逐鍵更新或合併，避免資料丟失。
- ❌ 對 `product_store_redeem_logs` 查詢無分區鍵 `pclass` → 應始終以 `pclass` 和 `pid` 組合查詢，避免跨分區掃描。
- ❌ 在兌換記錄 API 中直接暴露收件人個資（如電話、地址） → 僅在授權的後台或個人查詢時才回傳。

---

## tradegame

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra tradegame keyspace | reader | Schema：[db/tradegame.md](../../db/tradegame.md) · 語意：[db/tradegame-detail.md](../../db/tradegame-detail.md) |

### 寫入限制

- **resultlogs**：
  - `gdate`（分區鍵）、`gtype`、`gid`（集群鍵）：建立後不可修改。
  - `addtime`：由系統在結果寫入時自動設定，不可手動指定。
  - `status`：結果狀態（如 1=已結算）由交易遊戲結算服務更新，本服務僅讀取。
- **stock_holdings_* 系列表**（`BK`, `BS`, `ES`, `FL`, `HL` 等）：
  - 複合主鍵 `gdate, lid, gid, account, mode_spread_type`：建立後不可修改。
  - `addtime`：由交易服務寫入時自動設定。
  - `stock_num`：目前持股數量，由交易服務更新，不可直接變更。
  - `trade_history`（JSON 字串）：由交易服務追加交易記錄，**不可直接覆蓋或手動修改**。
  - `winloss`（W/L）：結算後設定，本服務不應修改。
  - `mode`, `oddtype`, `ratio`, `spread`：這些為交易的固定參數，建立後不應變更。

### 讀取規則

- **resultlogs**：
  - 必須以 `gdate` 為分區鍵，搭配 `gtype`、`gid` 查詢特定比賽的結果。
  - 判斷比賽是否已結算，過濾 `status = 1`。
  - 若需要某聯賽的結果，可再以 `lid` 輔助過濾（但 `lid` 非集群鍵，可能在應用層過濾）。
- **stock_holdings_***：
  - 查詢用戶持股時，必須以 `gdate` 為分區鍵，並指定 `account` 集群鍵，避免跨分區掃描。
  - 可依 `gid` 或 `mode_spread_type` 進一步過濾特定比賽或玩法。
  - `stock_num > 0` 表示仍持有部位，用於計算即時盈虧。
  - `trade_history` 為 JSON，解析時需注意其結構可能包含多筆交易記錄。
  - 不建議對 `trade_history` 進行全量掃描式查詢，應僅在需要時按需提取。

### 不可回傳欄位

- **trade_history**：內部交易細節，除非必要（如用戶個人交易記錄查詢），一般 API 不應回傳完整的 JSON 內容，可僅提供摘要。
- **account**：在一般公開查詢中不應洩漏用戶帳號，僅限用戶本人或管理後台查詢。
- **mode_spread_type** 底層複合鍵：對外可轉換為可讀的玩法描述，避免暴露原始拼接格式。
- **resultlogs 中的 `lid`**：雖非敏感，但無業務需求時可不回傳，精簡回傳欄位。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 交易遊戲的撮合、結算與持股計算 | tradegameservice | 本服務僅讀取結果與持股數據，不參與交易邏輯 |
| 比賽結果的判定與寫入 | tradegameservice / data feed | resultlogs 由交易遊戲服務根據官方結果寫入，本服務僅消費 |

### 常見錯誤

- ❌ 對 `stock_holdings_*` 查詢未指定 `gdate` 分區鍵，導致全表掃描 → 必須以比賽日期為必要條件。
- ❌ 未過濾 `stock_num > 0` 就直接計算用戶的總持股 → 應排除已平倉部位（stock_num=0）。
- ❌ 直接將 `trade_history` JSON 全文回傳給前端 → 可能暴露過多細節，建議僅回傳必要摘要或經過清洗的資料。
- ❌ 在程式碼中硬編碼 `mode_spread_type` 格式，當格式變更時導致解析失敗 → 應使用共用的解析函數或從配置讀取。