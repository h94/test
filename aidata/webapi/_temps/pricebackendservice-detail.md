# pricebackendservice — DB 操作邊界

> 產出時間：2025-03-28 10:30
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

## product

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra product keyspace | writer / reader | Schema：[db/product.md](../../db/product.md) · 語意：[db/product-detail.md](../../db/product-detail.md) |

### 寫入限制

- **products_store**：
  - `pclass`、`pid`：複合主鍵，建立後不可修改。
  - `status`：僅能透過商品管理 API 更新（'1'=上架，'0'=下架），不可由一般業務直接寫入。
  - `pnames`、`description`（`map<text, text>`）：**不可直接 REPLACE 整個 map**，應逐語言鍵值更新，確保 `zh-TW` 等必要語言不可為空。
  - `image_path`：為 `map<text, text>`，其中至少應包含 `title` 鍵；更新時應透過專用上傳流程，不允許 API 直接賦值內部路徑。
  - `originalprice`、`price`：僅能由營運人員透過管理後台設定，不允許用戶端 API 修改。
  - `lastup_time`：系統自動更新，不可手動寫入。
- **products_activity**：
  - `site`、`activityevent`、`id`：複合主鍵，建立後不可修改。
  - `quantity`：庫存數量應透過庫存管理方法（如增減庫存）操作，**禁止直接 UPDATE**。
  - `status`：僅管理 API 可更新。
  - `updatetime`：系統自動更新。
- **products_activity_redeem_logs**：
  - `site`、`activityevent`、`account`、`id`、`pid`：組成複合主鍵，建立後不可修改。
  - `addtime`：系統在兌換時自動生成，不允許手動寫入。
  - `status`：僅能透過兌換狀態管理 API 更新，不允許直接 UPDATE。
- **product_store_redeem_logs**：
  - `pclass`、`pid`、`addtime`、`account`、`id`：組成複合主鍵，建立後不可修改。
  - `deliverytime`、`status`：應由出貨流程或專用 API 更新，不得由一般業務直接寫入。
  - `cname`、`phonenumber`、`address`：僅用戶提交兌換時寫入，後續不允許修改（除非管理操作）。
- **product_store_stock_logs**：
  - `pclass`、`pid`、`addtime`、`id`：組成複合主鍵，建立後不可修改。
  - `quantity`：記錄該次入庫數量，不可修改原有記錄，如需調整庫存應新增一筆記錄。
- **withdrawlogs_activity**：
  - `site`、`activityevent`、`account`、`cid`：組成複合主鍵，建立後不可修改。
  - `status`：僅管理 API 可更新。
  - `contactnumber`：建立後如允許修改，應透過特定 API，不可直接 UPDATE。

### 讀取規則

- **products_store**：
  - 查詢商品列表時必須使用 `pclass` 為分區鍵，不可全表掃描。
  - 一般用戶端查詢需過濾 `status = '1'`（上架），並按 `sequence` 升序排序。
  - 多語言名稱和描述應由 API 層根據前端語系從 `pnames`、`description` map 中提取。
- **products_activity**：
  - 必須指定 `site` 為分區鍵，通常搭配 `activityevent` 查詢特定活動的商品。
  - 用戶端查詢過濾 `status = 1`。
  - 按 `updatetime` 或 `id` 排序。
- **products_activity_redeem_logs**：
  - 查詢時以 `site`、`activityevent` 為必要條件，可再依 `account`、`pid`、`status` 過濾。
  - 時間範圍查詢使用 `addtime`。
- **product_store_redeem_logs**：
  - 以 `pclass` 為分區鍵（或搭配 `pid`）進行查詢，可依 `account` 過濾用戶訂單。
  - 管理查詢時可依 `status` 篩選待處理或已發貨的記錄。
  - 排序常用 `addtime` 降序。
- **product_store_stock_logs**：
  - 以 `pclass` 為分區鍵，搭配 `pid` 查看商品庫存異動歷史。
  - 一般按 `addtime` 排序。
- **withdrawlogs_activity**：
  - 以 `site`、`activityevent` 為分區條件，可搭配 `account` 查詢用戶提領記錄。

### 不可回傳欄位

- **product_store_redeem_logs 中的個人資料**：`cname`、`phonenumber`、`address`、`cheadshot` 等為用戶隱私，一般對外 API 不應完整回傳，僅後台或用戶本人查詢時可暴露。
- **products_store.pnames**、**description** 等：多語言 map 中可能包含所有語系，對外應只回傳前端指定的語言版本，避免大量冗餘資料。
- **withdrawlogs_activity.contactnumber**：用戶聯絡電話，僅管理用途。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 實際商品出貨與物流追蹤 | 物流系統 / 倉管服務 | 本服務僅記錄兌換狀態與出貨時間，不處理實際出貨流程 |
| 庫存數量即時同步（超高並發） | 可能需要獨立庫存服務 | Cassandra 的 `quantity` 欄位在高並發兌換時需特別處理競爭，必要時應由專責服務控管 |

### 常見錯誤

- ❌ 對 `products_store` 查詢時未指定 `pclass` 分區鍵 → 導致全表掃描，極度影響效能。
- ❌ 直接更新 `quantity` 欄位而不使用 CAS 或原子操作 → 可能導致超賣，應採用庫存專用方法（如 `UPDATE quantity = quantity - 1 IF quantity > 0`）。
- ❌ 在兌換記錄中直接覆蓋 `status` 而不檢查當前狀態 → 可能跳過必要的狀態機，例如從「待處理」直接改為「已發貨」，應遵循狀態流程。
- ❌ 將 `image_path` 視為可直接回傳的 URL → 內部路徑需拼接 CDN 域名，否則前端無法載入圖片。
- ❌ 在多語言欄位更新時直接 REPLACE 整個 map → 應只更新目標語言鍵值，避免遺失其他語言已存在的內容。

---

## news

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra news keyspace | reader | Schema：[db/news.md](../../db/news.md) · 語意：[db/news-detail.md](../../db/news-detail.md) |

### 寫入限制

- **aifunshits.funsname**：主鍵，建立後不可修改。
- **ainews / ainews_gs**：
  - 複合主鍵 (`gdate`, `gtype`, `lid`, `gid`, `llmhashkey`, `status`) 不可更新，寫入方（AI 新聞產生服務）須保證唯一性。
  - `status`：表示 AI 新聞的處理階段（如 11 已發布），**僅 AI 新聞服務可更新**，本服務不直接寫入。
  - `articleid`：當新聞被轉換為社區文章後，由轉換服務寫入，不應手動設定。
  - `used`：同樣由轉換服務標記，避免重複發布。
  - `anwser`、`reanwser`、`question` 等內容欄位：由 AI 生成服務寫入，**本服務不應修改**。

### 讀取規則

- **aifunshits**：
  - 依 `funsname` 主鍵查詢特定 AI 功能的配置。
- **ainews / ainews_gs**：
  - 必須以 `gdate` 為分區鍵，搭配至少一個集群鍵（如 `gtype`）進行查詢，嚴禁跨日期全表掃描。
  - 查詢特定比賽的 AI 新聞時，使用 `gdate`, `gtype`, `lid`, `gid` 等條件。
  - 過濾未使用或特定狀態的新聞時，可加上 `status` 條件（如 `status = 11` 表示已生成）。
  - 時間排序通常以 `createtime` 降序。
  - 多語言內容支援請注意 `others` map 中可能包含比分、預測等資訊，前端需根據 key 提取。

### 不可回傳欄位

- **ainews.llmsettings**：可能包含 API 金鑰或內部設定，不應對外暴露。
- **ainews.others**：其中的原始資料可能包含未經處理的盤口資訊，需注意數據敏感性，避免直接暴露給終端用戶。
- **aifunshits.aihints**：若包含內部提示詞或敏感指令，不宜公開。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| AI 新聞的生成與更新 | AI 新聞產生服務 | 本服務僅讀取已生成的 AI 新聞，不觸發生成或重新生成 |
| 將 AI 新聞轉換為社區文章 | 文章轉換服務（可能在其他服務） | 若有此需求，由專門的排程或服務負責 |

### 常見錯誤

- ❌ 對 `ainews` 進行無分區鍵的查詢 → 必須包含 `gdate`，否則將導致全集群掃描。
- ❌ 錯誤地在前端直接渲染 `reanwser` 的 Markdown 或 HTML，未進行消毒 → 可能導致 XSS 攻擊。
- ❌ 混淆 `anwser` 與 `reanwser`，使用錯誤的版本作為顯示內容 → 應根據業務需求選擇最終版本（通常為 `reanwser`）。
- ❌ 未過濾 `status` 即回傳新聞 → 可能回傳未完成或測試中的草稿。

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter keyspace | reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **所有 `accounts_*` 表**（如 `accounts_AU8`, `accounts_PinnacleV2` 等）：
  - `account`：主鍵，建立後不可修改。
  - `password`：**僅能由帳戶建立或密碼修改流程寫入**，並且必須加密儲存，不允許任何 API 直接設定明文密碼。
  - `closetime`：由帳戶管理服務在停用帳戶時設定，本服務不應寫入。
  - `handler`：為內部配置用的 map，只應由管理後台更新。
  - `phone`：用戶電話，僅透過特定個人資料修改 API 更新，不得任意修改。
  - `enabled`：帳戶啟用狀態，僅由帳戶管理服務控制。

> **通用原則**：本服務對 pricecenter 僅具讀取權限，所有寫入操作應由專門的帳戶管理服務執行。

### 讀取規則

- 所有 `accounts_*` 表查詢時均以 `account` 為主鍵，直接單筆查詢，無需額外過濾條件。
- 若業務需要取得啟用中的帳戶，應檢查 `enabled = 1`。
- 密碼 (`password`) 欄位絕不可讀取或用於回應，查詢時應排除此欄位。
- `handler` 欄位可能包含內部配置，對外回傳前應移除敏感資訊（如 API 密鑰）。

### 不可回傳欄位

- **`password`**：任何情況下皆不可回傳。
- **`phone`**：視為用戶個資，一般查詢不應回傳，除非特定管理場景或用戶本人確認。
- **`handler`**：若有包含第三方 API 金鑰等資訊，必須過濾。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 盤口帳戶的建立、啟用與停用 | 帳戶管理服務 | 本服務僅查詢帳戶資訊，不負責管理帳戶生命週期 |
| 帳戶密碼的變更與加密 | 帳戶管理服務 | 密碼相關作業由獨立服務處理 |

### 常見錯誤

- ❌ 在回應中不慎包含 `password` 欄位 → 查詢時應明確 SELECT 所需欄位，或使用 DTO 剔除敏感資訊。
- ❌ 試圖直接對 `accounts_*` 表執行 UPDATE → 僅可讀取，若需修改帳戶資料應呼叫帳戶管理服務 API。
- ❌ 忽略 `enabled` 狀態直接使用帳戶資訊 → 可能用到已停用的帳戶，應先檢查啟用狀態。
- ❌ 將 `handler` 中的全部資訊序列化後直接回傳給前端 → 應過濾掉內部使用的 key。

---

## tradegame

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra tradegame keyspace | writer / reader | Schema：[db/tradegame.md](../../db/tradegame.md) · 語意：[db/tradegame-detail.md](../../db/tradegame-detail.md) |

### 寫入限制

- **settings_gametype**：
  - `gametype`：主鍵，建立後不可修改。
  - `enabled`、`lids`：僅管理 API 可更新。
  - `addtime`：系統自動設定。
- **settings_score**：
  - 複合主鍵 (`gtype`, `layer`, `lid`) 不可修改。
  - `rules`：JSON 格式的計分規則，僅能由管理後台設定，不允許一般用戶修改。
- **settings_stock**：
  - 複合主鍵 (`gtype`, `layer`, `lid`, `gid`) 不可修改。
  - `initial_stock_num`、`rules`：僅管理 API 可設定，設定後若需調整應謹慎，避免影響已發行的股票。
  - `gdate`：開賽日期，僅建立時寫入。
- **resultlogs**：
  - `gdate`, `gtype`, `gid` 組成複合主鍵，建立後不可修改。
  - `status`：僅由結算服務寫入（如 1 表示已結算），本服務不應手動修改。
- **stock_holdings_BK / BS / ES**：
  - 複合主鍵 (`gdate`, `lid`, `gid`, `account`, `mode_spread_type`) 不可修改。
  - `stock_num`：持股數量，需透過交易邏輯（買入/賣出）處理，**禁止直接 UPDATE**。
  - `trade_history`：JSON 陣列記錄每次交易，應以 append 方式新增，**不可直接覆蓋**。
  - `winloss`：由結算服務更新，代表該筆持倉的輸贏結果（W/L），不允許手動設定。
  - `ratio`、`spread`、`mode`、`oddtype`：交易時的固定參數，不應事後修改。
  - `addtime`：系統自動設定。

### 讀取規則

- **settings_gametype**：
  - 查詢時以 `gametype` 為主鍵，可過濾 `enabled = 1` 取得已啟用的遊戲類型。
- **settings_score**、**settings_stock**：
  - 必須指定分區鍵 `gtype` 和 `layer`（或 `layer` 中的聯賽層級），再依集群鍵精準查詢。
  - 嚴禁跨遊戲類型的全表掃描。
- **resultlogs**：
  - 以 `gdate` 為分區鍵，搭配 `gtype`, `gid` 查詢特定比賽的結果記錄。
  - 通常會過濾 `status = 1` 來確認已結算的場次。
- **stock_holdings_***：
  - 以 `gdate` 為分區鍵，加上 `lid`, `gid` 查詢單場比賽的所有持倉，或再加上 `account` 查詢特定用戶的持倉。
  - 需注意 `winloss` 可能為空（尚未結算），處理時應容錯。
  - 歷史交易資料 (`trade_history`) 為 JSON 字串，解析時需處理格式錯誤。

### 不可回傳欄位

- **resultlogs**、**stock_holdings** 中的 `lid`、`gid` 等內部標識：可回傳，但無特殊敏感性。
- **settings_* 的 `rules`**：此配置可能涉及業務邏輯細節，對外暴露無妨，但應注意如果是敏感性規則可考慮遮蔽。
- 本模組無明顯使用者個資欄位，但 `account` 為用戶帳號，應避免在無授權的場景中暴露。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 股票交易撮合與清算 | tradegameservice (或獨立交易引擎) | pricebackendservice 負責管理設定與查詢結果，不處理即時交易邏輯 |
| 比賽結果的判定與比分來源 | 外部資料提供者 / 賽事服務 | resultlogs 中的結算資料由上游服務填入，本服務僅儲存與查詢 |

### 常見錯誤

- ❌ 直接 UPDATE `stock_num` 而不檢查剩餘可用股數與用戶餘額 → 應使用交易方法（如買入時檢查資金與庫存）。
- ❌ 覆蓋 `trade_history` 陣列 → 每次交易應將新記錄 append 到陣列末端，否則歷史數據丟失。
- ❌ 對 `settings_stock` 查詢時未使用 `gtype` + `layer` 分區鍵 → 可能導致跨多個分區掃描，務必帶上完整分區鍵。
- ❌ 在結算前就依賴 `winloss` 欄位 → 未結算時該欄位可能為空或預設值，業務邏輯需防禦。
- ❌ 將 `stock_holdings` 表中的 `mode_spread_type` 直接展示給前端而無說明 → 該值為複合標識（如 `HA_-1.5_A`），前端可能需要解析。

---

## Redis

<!-- 尚無 Redis 相關資訊，待後續分析程式碼後補充 -->

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 廣告點擊統計與曝光分析 | 第三方追蹤服務 | 僅提供廣告素材與連結，不負責統計與分析 |
| 論壇內容管理 (發文、回覆) | communityservice | pricebackendservice 僅讀取論壇基礎資訊 |
| 用戶工單處理與提醒 | feedbackservice (API) | 僅查詢與更新狀態，不負責提醒或主動推播 |
| AI 新聞的生成與更新 | AI 新聞產生服務 | 本服務僅讀取已生成的 AI 新聞 |
| 盤口帳戶的建立、啟用與停用 | 帳戶管理服務 | 僅查詢帳戶資訊 |
| 股票交易撮合與清算 | tradegameservice / 交易引擎 | 負責管理設定與查詢結果，不處理即時交易 |
| 比賽結果的判定與比分來源 | 外部資料提供者 / 賽事服務 | resultlogs 由上游服務填入 |
| 實際商品出貨與物流追蹤 | 物流系統 / 倉管服務 | 僅記錄兌換狀態與出貨時間 |
| 庫存數量即時同步（超高並發） | 可能需要獨立庫存服務 | Cassandra 的 quantity 欄位在高並發時需特別處理 |

---

## 常見錯誤

- ❌ 對任何 Cassandra 表進行全表掃描而無分區鍵 → 應始終搭配分區鍵查詢。
- ❌ 在多語言 map 或列表欄位更新時直接 REPLACE 整個集合 → 應逐條新增或刪除。
- ❌ 直接將內部圖片/檔案路徑回傳給前端 → 應拼接為完整的 CDN URL。
- ❌ 未檢查 `enabled` 或 `status` 等啟用狀態就回傳資料 → 可能暴露未發布或已停用的內容。
- ❌ 在回應中意外暴露密碼、信箱、電話等個資 → 查詢時應精確選擇所需欄位，或於 DTO 過濾。
- ❌ 試圖對僅讀取的 DB（如 pricecenter）執行寫入操作 → 應呼叫對應的負責服務。
- ❌ 直接更新 `stock_num` 或 `quantity` 而不使用原子操作 → 可能導致超賣或庫存不一致。
- ❌ 未處理 JSON 格式欄位 (如 `trade_history`, `problem`) 的可能異常或 null → 應加入防禦性解析。
- ❌ 忽略時間範圍檢查即顯示廣告或公告 → 可能回傳過期內容。