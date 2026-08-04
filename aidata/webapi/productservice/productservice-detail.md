# productservice — DB 操作邊界

> 產出時間：2025-04-11 14:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## payment

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| payment Cassandra | owner | Schema：[db/payment.md](../../db/payment.md) · 語意：[db/payment-detail.md](../../db/payment-detail.md) |

### 寫入限制

- **paymethods_sport.enabled**：僅後台支付設定 API 可寫入；啟用/停用不允許前端直接操作。
- **paymethods_sport.names**：多語系 Map，寫入時至少須包含一個有效語言代碼（如 `zh-TW`），不可為空 map；後續可新增語系但不可刪除既有主要語系。
- **paymethods_sport.paytype / mode**：為分區鍵與叢集鍵，建立後不可修改。
- **products_activity.status**：僅限 `IActivityDataProvider.UpdateSiteActivityEventProductStatus` 寫入，不可由其他 API 直接 UPDATE。數值範圍 0（暫停）/1（販售中）/2（售完），由系統管理端或條件觸發變更，前端不可寫入。
- **products_activity.price / quantity / names**：僅在 `CreateActivityProduct` 時一次寫入，後續不允許單一欄位更新；若要修改需整筆重建。
- **products_activity_redeem_logs.status**：僅由 `UpdateActivityProductRedeemLogStatus` 更新，數值 0（審核中）/1（成功）/2（失敗）。成功或失敗後不可再變更。
- **withdrawlogs_activity.accountname / contactnumber**：僅在建立提領記錄時由使用者提供，服務端不可事後直接修改。
- **withdrawlogs_activity.status**：僅由提領審核流程更新（0 審核中 /1 成功 /2 失敗），且成功或失敗後狀態不可再變更。
- **withdrawlogs_activity.site / activityevent / account / cid**：皆為叢集鍵或分區鍵的一部分，寫入後不可變更。
- **rechargeplans_newlottery**：僅後台新增/編輯充值方案時寫入，前台不可新增。`enabled` 不可與 `starttime` / `endtime` 衝突（如已過期方案不可設為啟用）。
- **reports_sport / reports_sport_recommend**：僅由報表結算排程寫入，不允許應用層手動 INSERT / UPDATE / DELETE。`finishing` 標記一旦設為 `true`，不可再回設為 `false`。

### 讀取規則

- **查詢支付方式（paymethods_sport）**：必須以 `paytype` 為分區鍵 WHERE；`mode` 為叢集鍵可選用。前端只查 `enabled=1`；後台可查所有狀態。
- **查詢活動商品列表（products_activity）**：必須以 `site` + `activityevent` 為分區鍵 WHERE，不可全表掃描。前端僅回傳 `status=1`（販售中）；後台可看全部狀態。
- **查詢兌換記錄（products_activity_redeem_logs）**：必須以 `site` + `activityevent` + `account` 為過濾條件。前端僅能查看自己的記錄；後台可依 `site` + `activityevent` 查詢全部。未審核（status=0）的記錄不應回傳給使用者。
- **查詢提領記錄（withdrawlogs_activity）**：必須以 `site` + `activityevent` + `account` 為 WHERE 條件（至少 `site` + `activityevent`）。前端僅能查自己 `account` 的記錄，且 `status=0`（審核中）的記錄不回傳；後台可查全部，支援以 `cid` 過濾並分頁。
- **查詢充值方案（rechargeplans_newlottery）**：查詢單一方案時必須以 `id` 為分區鍵；前端列表查詢須 `enabled=1` 且當前時間在 `[starttime, endtime)` 內；後台可全表掃描但建議附帶過濾條件。
- **佣金記錄（commissions_betpool_newlottery）**：前端僅能查自己 `source_uid` 的記錄，且限制回傳最近 N 筆（分頁）。
- **查詢報表（reports_sport / reports_sport_recommend）**：僅後台可讀，必須以 `year` + `month` 為主要過濾條件；跨月查詢需分頁且效能較差。

### 不可回傳欄位

- **commissions_betpool_newlottery.source_uid**：使用者 ID，對任何前端查詢都不應回傳。
- **commissions_betpool_newlottery.source_cid**：渠道 ID，僅內部統計使用，不回傳前端。
- **rechargeplans_newlottery.id**：內部主鍵，前端不應暴露；改用前端代號（若需）。
- **withdrawlogs_activity.account**：使用者帳號，對前端查詢不可回傳。
- **withdrawlogs_activity.contactnumber**：聯絡電話，對前端應完全遮蔽或僅顯示末四碼。
- **withdrawlogs_activity.accountname**：可能包含真實姓名，對前端應遮蔽處理。
- **reports_sport.leaguesunlock**：內部明細（聯賽代碼與次數），若提供給前端應摘要化，不傳遞原 JSON 細節。

---

## product

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| product Cassandra | owner | Schema：[db/product.md](../../db/product.md) · 語意：[db/product-detail.md](../../db/product-detail.md) |

### 寫入限制

- **products_store.status**：僅可透過 `UpdateStoreProductStatus` 方法變更，值為 `"1"`（上架）或 `"0"`（下架），不可直接 UPDATE。下架後若要重新上架，需確保庫存充足。
- **products_store.price / originalprice**：建立商品時寫入，後續不允許單一欄位直接更新；價格變更應整筆重建，以保留歷史記錄。
- **products_store.pnames / description / image_path**：多語言 Map 型態，寫入時必須包含 `zh-TW` 且其值不可為空；`image_path` 必須含有 `title` 鍵且其值不為空；psource 為必填欄位。
- **products_store.pclass / pid**：`pclass` 須為系統允許的 `productClassTypes` 之一；`pid` 由系統自動產生，寫入後不可修改。
- **products_activity.status**：僅可透過 `UpdateSiteActivityEventProductStatus` 寫入，值為 0（暫停）、1（販售中）、2（售完），前端不可直接寫入。
- **products_activity.price / quantity / names**：僅在 `CreateActivityProduct` 時一次寫入，後續不允許單一欄位更新；修改需整筆重建。
- **products_activity_redeem_logs.status**：僅由 `UpdateActivityProductRedeemLogStatus` 更新，值為 0（審核中）、1（成功）、2（失敗）；成功或失敗後不可再變更。
- **product_store_redeem_logs.status**：僅透過 `UpdateStoreProductRedeemLogStatus` 更新，值為 0（失敗）、1（成功）、2（審核中）、3（審核成功）、4（配送中）、5（已送達）、6（已簽收）、7（未簽收）；一旦設為 0 或 1 後不可再變更。
- **product_store_redeem_logs.recipient / phonenumber / address**：非 `inplayz` 類別商品建立時必填，不可省略。
- **product_store_stock_logs.quantity**：異動數量，必須大於 0（表示入庫量）；入庫/出庫邏輯由服務端程式控制，保證最終庫存非負。
- **withdrawlogs_activity.contactnumber**：僅建立時可由使用者提供，服務端不可事後修改。
- **withdrawlogs_activity.status**：僅由提領審核流程更新（數值含義待確認，可能為 0 審核中、1 成功、2 失敗），且成功或失敗後狀態不可再變更。
- 所有表的 Partition Key 與 Clustering Key（如 `site` / `activityevent` / `pclass` / `pid` / `account` / `id` / `cid` / `addtime` 等）寫入後均不可修改。

### 讀取規則

- **查詢商店商品列表（products_store）**：必須以 `pclass` 為分區鍵 WHERE，不可全表掃描。前端只回傳 `status="1"`（上架）商品；`status="0"`（下架）僅後台顯示。支援依 `popular`、`sequence` 排序，不可跨 `pclass` 排序。
- **查詢兌換記錄（product_store_redeem_logs）**：必須以 `pclass` + `pid` 為過濾條件（可加 `account`）。前端僅能查看自己的 `account` 對應記錄，且 `status=2`（審核中）不應回傳給使用者；後台可依 `pclass` + `pid` 查詢全部。
- **查詢庫存異動記錄（product_store_stock_logs）**：必須以 `pclass` + `pid` 為條件，不可無 `pid` 的全表查詢；前端僅回傳最近 N 筆（分頁）。
- **查詢活動商品列表（products_activity）**：必須以 `site` + `activityevent` 為分區鍵 WHERE。前端只回傳 `status=1`（販售中）；`status=0`（暫停）或 `status=2`（售完）僅後台顯示。
- **查詢活動兌換記錄（products_activity_redeem_logs）**：必須以 `site` + `activityevent` + `account` 為過濾條件。前端僅能查看自己的記錄，且 `status=0`（審核中）不應回傳給使用者；後台可依 `site` + `activityevent` 查詢全部。
- **查詢提領記錄（withdrawlogs_activity）**：必須以 `site` + `activityevent` + `account` 為條件（至少 `site` + `activityevent`）。前端僅能查自己 `account` 的記錄，且 `status=0`（審核中）不回傳；後台可查全部，支援以 `cid` 過濾並分頁。

### 不可回傳欄位

- **product_store_redeem_logs.account**：使用者帳號，對前端查詢不可回傳。
- **product_store_redeem_logs.phonenumber / address / recipient**：個人隱私資訊，僅後台管理或物流查詢時可回傳完整，前端查看記錄時應遮罩處理。
- **product_store_redeem_logs.id**：內部主鍵，前端不應暴露；改用替代標識（如兌換單號）。
- **products_activity_redeem_logs.account**：使用者帳號，對前端查詢不可回傳。
- **withdrawlogs_activity.account / contactnumber**：使用者帳號與聯絡電話，對前端查詢不可回傳，必要時應遮罩。

---

## ads

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| ads Cassandra | owner | Schema：[db/ads.md](../../db/ads.md) · 語意：[db/ads-detail.md](../../db/ads-detail.md) |

### 寫入限制

- **advertising.enabled**：僅後台廣告管理 API 可寫入；前端不可直接修改啟用狀態。數值 0（禁用）/ 1（啟用）。
- **advertising.starttime / closetime**：寫入時需校驗 `starttime < closetime`，否則拒絕寫入。時間戳精度為秒。
- **advertising.createdby**：僅系統內部寫入（如 `"promotion"`），前端不可指定或修改。
- **advertising_sport.enabled**：僅後台體育廣告管理 API 可寫入。數值 0（禁用）/ 1（啟用）。
- **advertising_sport.startdate / closedate**：日期字串格式須為 `yyyy-MM-dd`，且 `startdate` 必須小於 `closedate`。
- **advertising_sport.adclass**：廣告類別內部標記，僅後台寫入，前端不可操作。
- **bulletinboard_sport.maintopic / text1 / text2 / text3**：僅設定公告 API 可寫入。Map 型態，每個 key 須為有效語言代碼（如 `zh-CN`, `en`），不可空 map；寫入時須確保至少有一個語言條目。
- **bulletinboard_sport.status**：僅後台公告管理 API 可更新，數值 0（草稿）/ 1（發布）/ 2（下架）。發布後不可直接刪除，需先設為下架。
- **bulletinboard_sport.announcementmethod**：僅公告建立時寫入，後續不可變更，且僅內部邏輯使用。

### 讀取規則

- **查詢廣告列表（advertising）**：對外 API 必須 WHERE `enabled=1` AND `starttime <= now < closetime`，過期或未開始的廣告不對前端暴露。後台可依 `createdby` 或 `type` 過濾查詢全部。廣告的 `lang` 欄位為支援語言列表（以 `&` 分隔），服務端只回符合時間與啟用狀態的廣告，前端需自行根據用戶語言篩選。
- **查詢體育廣告（advertising_sport）**：前端查詢須 WHERE `enabled=1` AND `startdate <= today < closedate`，日期比較使用 `yyyy-MM-dd` 字串比較。支援依 `adarea` 過濾。`supportlangs` 欄位為語言代碼列表，前端需自行匹配。
- **查詢公告列表（bulletinboard_sport）**：前端僅回傳 `status=1`（發布中）且當前時間在 `[starttime, endtime)` 內的公告；`status=0`（草稿）僅後台可讀。排序依 `sequence` 降冪，同序號依 `addtime` 降冪。
- **公告多語言回傳**：回傳 `maintopic`、`text1`、`text2`、`text3` 時，應依請求之 `Accept-Language` 取出對應語系內容；若無匹配則回退至預設語系（如 `en`）。

### 不可回傳欄位

- **advertising.createdby**：創建者內部帳號，不對外回傳。
- **advertising_sport.adclass**：廣告分類內部標記，僅後台統計使用，不回傳前端。
- **bulletinboard_sport.announcementmethod**：公告發布方式（整數枚舉），僅內部邏輯使用，不回傳前端。

---

## stock

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| stock MySQL | owner | Schema：[db/stock.md](../../db/stock.md) · 語意：[db/stock-detail.md](../../db/stock-detail.md) |

### 寫入限制

- **users.Password**：僅註冊或更新密碼 API 可寫入；須先雜湊，不可明文儲存；不可直接透過 UPDATE 修改。
- **users.Enabled**：僅後台管理 API 可寫入（0 禁用 / 1 啟用），前端不可自行啟用帳號。
- **users.Rank**：僅後台或訂閱服務 API 可寫入，反映會員層級；不可與 `SubEndTime` 邏輯衝突（如過期後 Rank 應降級）。
- **favoritebroker / favoritestock / favoriterule**：僅該 User 可寫入自己的資料；寫入時需以 User 為主鍵條件。Value 欄位為 JSON 或序列化字串，服務端應驗證格式正確。
- **favoriterule.NeedSend / FirstMatch**：僅由規則設定 API 寫入，數值 0/1，前端不可直接操作。
- **sublogs**：僅訂閱流程 API（如訂閱建立、續期）寫入；寫入後主鍵欄位（Account, AddTime）不可變更；SubEndTime 可由訂閱到期排程更新。
- **messagelog**：僅發送通知服務寫入；SendStatus 由發送結果回調更新（0→1 或 0→2），成功或失敗後不可再變更。
- **options / rules**：僅後台系統設定 API 寫入；options.Value 和 rules.Text 具有唯一約束，寫入前須檢查重複。

### 讀取規則

- **查詢用戶資料（users）**：前端僅能查詢自己的 Account（WHERE Account = 登入用戶）；僅當 `Enabled=1` 時允許登入或取資料；禁用帳號（Enabled=0）不可查詢。
- **查詢自選清單（favoritebroker, favoritestock, favoriterule）**：必須以 User 為 WHERE 條件，僅回傳該用戶的資料；不可模糊查詢其他用戶。favoriterule 可依 Country 或 Industry 過濾，但必須搭配 User。
- **查詢訂閱記錄（sublogs）**：前端僅能查詢自己 Account 的記錄；回傳時依 AddTime 降冪排序，並限制筆數（分頁）。後台可依 Account 或 SubID 查詢全部。
- **查詢訊息日誌（messagelog）**：僅後台或管理 API 可查詢，需以 Date + Account 為過濾條件；前端一般不開放。若有需要，僅能查自己的記錄（Account 限制），且 MsgContent 應截斷或遮罩。
- **查詢系統選項（options）**：前端查詢時須 WHERE `Enabled=1`，禁用選項不顯示。
- **查詢規則列表（rules）**：前端查詢時須 WHERE `Enabled=1`，禁用規則不顯示；可依 Type 或 Indicator 過濾，但避免全表掃描。
- **會員資料回傳**：回傳 users 時必須排除 Password 欄位；Phone、Email、ChatID 等個資應視前端權限遮罩（如手機後四碼、信箱@前部分）或僅後台回傳完整。

### 不可回傳欄位

- **users.Password**：密碼雜湊值，任何情況下皆不可回傳。
- **users.Phone**（完整）：對前端遮罩後四碼，後台可看完整。
- **users.Email**（完整）：對前端遮罩@前部分，後台可看完整。
- **users.ChatID**：內部通訊用，不回傳前端。
- **favoriterule.FirstMatch**：內部邏輯標記，不回傳前端。
- **favoriterule.NeedSend**（若無前端展示需求）：不回傳。
- **messagelog.MsgContent**：若前端可查詢，內容應截斷或遮罩；後台可回傳完整。
- **sublogs.TradeNo**：內部交易序號，不對前端暴露；改用訂閱單號替代。
- **options.ID**：內部主鍵，前端不應暴露；改用 Value 作為識別。

---

## Redis

本服務未使用 Redis 存取任何 DB 資料。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 實際扣款 / 金流處理 | paymentservice | productservice 僅記錄兌換與商品庫存，不處理金錢交易 |
| 活動邏輯 / 條件判斷 | activityservice | 活動事件（activityevent）的創建、啟用/停用由活動服務管理 |
| 使用者帳號驗證 / Token | authservice | productservice 不處理登入或身分驗證 |
| 廣告圖片/素材儲存 | fileservice | productservice 僅記錄圖片路徑（`imgpath`, `path`），不負責上傳或存儲二進位檔案 |
| 多語言內容管理 | i18nservice / content management | 公告與廣告的多語言欄位由 productservice 記錄，但語言代碼有效性與翻譯流程由其他服務管理 |

---

## 常見錯誤

- ❌ 直接對 `products_store` 執行 UPDATE 修改 `status` 而不經由 `UpdateStoreProductStatus` → ✅ 皆須透過 DataProvider 方法，確保寫入前檢查庫存與狀態一致性。
- ❌ 直接對 `products_store` 執行 UPDATE 修改 `price` 而不重建記錄 → ✅ 價格變更應整筆重建商品記錄，避免歷史價格缺失。
- ❌ 查詢 `products_store` 時未以 `pclass` 為分區鍵，導致全表掃描 → ✅ 查詢時必須帶入 `pclass` WHERE 條件。
- ❌ 將 `products_store.pnames` 誤視為純字串直接回傳，忽略 Map 型態應依語系取值 → ✅ 回傳時應依 `Accept-Language` 取出對應 key 的值（若無則 fallback 預設語系）。
- ❌ 對 `product_store_redeem_logs` 或 `products_activity_redeem_logs` 直接執行 DELETE 刪除記錄 → ✅ 應透過設定 `status`（如 Failure(0)）來軟刪除，保留歷史記錄。
- ❌ 在庫存扣減時，僅檢查本地快取而未比對 DB 庫存量，導致超賣 → ✅ 應透過原子操作或樂觀鎖機制確保庫存非負。
- ❌ 前端查詢 `product_store_stock_logs` 時未限制回傳筆數（分頁），回傳大量歷史資料 → ✅ 必須實作分頁，每次限制最大回傳量（如 50 筆）。