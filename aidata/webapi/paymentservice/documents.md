# PaymentService — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### PaymentService DB Table (舊站台 MySQL)

> Confluence 頁面 ID：24085381
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/PaymentService+DB+Table)
> 摘要檔：[processed/24085381-summary.md](../../confluence/processed/24085381-summary.md)
> Confluence 最後更新：2021-09-01
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義支付系統 MySQL 核心資料表結構，包含儲值紀錄 depositlog_all、點數消費紀錄 consumptionlog_all、付費方案 plan、付費方式 channel、文章購買者列表 articlesaleslog，以及掛載在 members 資料表上的會員個人紀錄欄位。

**關鍵業務規則**：
- 交易狀態（status）：1 表示成功，0 表示失敗，2 表示審核中
- 付費方案 plan.type：`subscribe` 為訂閱方案，`point` 為點數方案
- 付費方案／付費方式 enabled 欄位：0 停用，1 啟用
- 會員的 d_logs（儲值記錄）包含 Orderid、Date、PlanName、Channel、Price、Point、Status
- 會員的 c_logs（消費記錄）包含 Orderid、Date、PlanName、Content、Price、Point
- 會員的 p_logs（購買文章記錄）包含 OrderID、Date、Pname、Price、Point

**注意事項**：
- ⚠️ 文件最後更新於 2021-09-01，可能部分結構已變更，需人工確認現行是否仍適用

---

### 新運彩 Payment DB Tables (Cassandra)

> Confluence 頁面 ID：79467538
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467538)
> 摘要檔：[processed/79467538-summary.md](../../confluence/processed/79467538-summary.md)
> Confluence 最後更新：2026-02-05
> 摘要最後同步：2026-05-26

**摘要**：
定義新運彩支付系統的 Cassandra 資料表結構，包含儲值方案表 rechargeplans_newlottery 與交易紀錄表 tradeorder_newlottery，為儲值流程與交易查詢功能的基礎資料模型。

**關鍵業務規則**：
- 交易狀態（status）：0=尚未付款、1=交易成功、2=交易失敗
- 儲值方案幣種 currency 目前僅支援 TWD
- rechargeplans_newlottery 以 id 為 partition key
- tradeorder_newlottery 以 year 為 partition key，clustering 依序為 datetime、account、orderid

**注意事項**：
- ⚠️ currency 欄位僅有 TWD，若未來支援多幣種需評估是否調整此限制

---

### TCZB-1038 支付系統實作 API

> Confluence 頁面 ID：24085460
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24085460)
> 摘要檔：[processed/24085460-summary.md](../../confluence/processed/24085460-summary.md)
> Confluence 最後更新：2021-09-10
> 摘要最後同步：2026-05-27

**摘要**：
定義支付系統的 REST API，涵蓋儲值、訂閱、購買文章、交易紀錄查詢及錢包餘額查詢，部分端點由 memberservice 提供。

**關鍵業務規則**：
- 查詢會員錢包餘額時若無訂閱紀錄，EndTime 欄位應回傳 0
- 付費方案 Type 為 `subscribe` 時，Value 代表訂閱天數；Type 為 `point` 時，Value 代表增加點數額度

**注意事項**：
- ⚠️ 本文件未涵蓋線上支付金流串接，需人工確認現行支付流程是否已實作

---

### TCZB-2837 球王付費方案 API

> Confluence 頁面 ID：47222576
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47222576)
> 摘要檔：[processed/47222576-summary.md](../../confluence/processed/47222576-summary.md)
> Confluence 最後更新：2023-07-24
> 摘要最後同步：2026-05-27

**摘要**：
定義球王運動站台付費方案重構 API，包含方案與支付方式的 CRUD、綠界支付訂單建立與驗證、以及交易訂單管理等共 16 支端點。

**關鍵業務規則**：
- 支付方式中，僅信用卡支援定期定額（Mode=`period`），其餘均為一次性付費（Mode=`disposable`）
- 訂單交易狀態：0=未交易，1=成功，2=失敗
- 定期定額訂單須記錄 firstorderid（首次授權成功的第三方訂單 ID）及累計成功授權次數
- 方案有效長度 effectivelength 依類型限制：D（天）1~365，M（月）1~12，Y（年）1
- 方案可設定 subLimit=true 表示該方案只能訂閱一次
- 交易訂單以 year 為 partition key，(datetime, account, orderid) 為 clustering key

**注意事項**：
- ⚠️ API #1 與 #11 修改既有的端點，實作時需注意向後相容性

---

### 綠界金流對接 SportKing

> Confluence 頁面 ID：47220420
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47220420)
> 摘要檔：[processed/47220420-summary.md](../../confluence/processed/47220420-summary.md)
> Confluence 最後更新：2023-05-03
> 摘要最後同步：2026-05-27

**摘要**：
為 SportKing 訂閱服務導入綠界金流，僅支援信用卡付款。定義 API 路由及 subplans_sport、tradeorder_sport 兩張資料表。

**關鍵業務規則**：
- SportKing 金流僅接受信用卡付費，不支援其他支付方式
- 方案類型 subtype 為 `D`（天）、`M`（月）、`Y`（年）之一
- 定期定額次數 paycount 上限：D 最多 999、M 最多 99、Y 最多 9

**注意事項**：
- ⚠️ tradeorder_sport 資料表欄位定義缺失，需人工補充

---

### 綠界信用卡定期定額串接

> Confluence 頁面 ID：47220857
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47220857)
> 摘要檔：[processed/47220857-summary.md](../../confluence/processed/47220857-summary.md)
> Confluence 最後更新：2023-05-16
> 摘要最後同步：2026-05-27

**摘要**：
定義 PaymentService 新增綠界信用卡定期定額功能的 API 規格，包含建立訂單、接收定期定額結果以及更新訂單三個端點。

**關鍵業務規則**：
- tradeorder_sport 新增 periodcount 和 totalsuccess 欄位，用於記錄定期定額次數及成功授權次數

**注意事項**：
- ⚠️ 文件中僅提供測試卡號，正式環境需更換
- ⚠️ 回呼端點的 returnURL 及 periodReturnURL 為測試域名，需確認正式環境設定

---

### 分潤系統

> Confluence 頁面 ID：55575371
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55575371)
> 摘要檔：[processed/55575371-summary.md](../../confluence/processed/55575371-summary.md)
> Confluence 最後更新：2023-11-22
> 摘要最後同步：2026-05-27

**摘要**：
定義運動站台分潤系統的技術設計，包含 Cassandra 資料表及 11 個 REST API 端點，每月 1 號透過 xxl-job 計算上個月分潤。

**關鍵業務規則**：
- 當月總收入 = 當月交易成功總金額
- 當月份潤金額 = (當月總收入 - 當月總收入*0.05) * 0.55
- 每月 1 號計算上個月分潤
- totalunlock = 一般莊殺解鎖次數 * 1 + 超級莊殺解鎖次數 * 1.3
- 提領紀錄狀態：0=處理中，1=成功，2=失敗

**注意事項**：
- ⚠️ 文件未說明不同球種（GameType）與聯盟（League）的業務分配規則，需人工確認

---

### 活動提領 API

> Confluence 頁面 ID：55577368
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55577368)
> 摘要檔：[processed/55577368-summary.md](../../confluence/processed/55577368-summary.md)
> Confluence 最後更新：2024-02-26
> 摘要最後同步：2026-05-27

**摘要**：
定義活動提領相關的三個 REST API 端點，包含新增、查詢、更新提領紀錄，以及對應的 Cassandra 表 withdrawlogs_activity。

**關鍵業務規則**：
- 提領紀錄狀態：0=審核中，1=成功，2=失敗
- 提領紀錄唯一鍵由 site、activityevent、account、cid 組成，不可重複
- 新增提領紀錄必須提供 Site、ActivityEvent、Account、CID、ContactNumber

**注意事項**：
- ⚠️ updateTime 為 Unix 時間戳（bigint），開發時需統一處理時區

---

### 第三方支付（綠界）

> Confluence 頁面 ID：40503469
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40503469)
> 摘要檔：[processed/40503469-summary.md](../../confluence/processed/40503469-summary.md)
> Confluence 最後更新：2022-10-27
> 摘要最後同步：2026-05-27

**摘要**：
整合綠界第三方支付 API 及訂閱方案管理 API，定義三個 Cassandra 表格：tradeorder_stock、shakehandslog_service、subplans_stock。

**關鍵業務規則**：
- 交易訂單狀態：0 未完成、1 成功、2 失敗
- 訂閱方案 subplans_stock 啟用狀態：0 關閉、1 開啟

**注意事項**：
- ⚠️ API 失敗時回傳 null（無詳細錯誤訊息），建議實作時額外考慮錯誤回應機制

---

### 運動站台商品功能

> Confluence 頁面 ID：55581555
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55581555)
> 摘要檔：[processed/55581555-summary.md](../../confluence/processed/55581555-summary.md)
> Confluence 最後更新：2025-02-13
> 摘要最後同步：2026-05-27

**摘要**：
定義運動站台活動商品功能的 API 設計，包含商品 CRUD 及兌換紀錄，使用 Cassandra 儲存，支援 Redis 快取。

**關鍵業務規則**：
- 查詢商品時預設從 Redis 讀取（cache=true），可指定 cache=false 強制讀取 Cassandra
- API 資源路徑：/activity/products 與 /activity/productredeemlogs

**注意事項**：
- ⚠️ 商品狀態與兌換狀態欄位僅標示為 int，未定義具體值與含義，需人工確認

---

## 技術設計類

### PaymentService Flow（流程圖）

> Confluence 頁面 ID：24085199
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/PaymentService+Flow)
> 摘要檔：[processed/24085199-summary.md](../../confluence/processed/24085199-summary.md)
> Confluence 最後更新：2021-08-24
> 摘要最後同步：2026-05-26

**摘要**：
透過 PlantUML 序列圖描述 PaymentService 的 10 種互動流程，涵蓋儲值、購買文章、訂閱專家、交易記錄查詢、點數查詢及方案取得。

**關鍵設計決策**：
- 儲值前必須先確認會員是否存在於 DB
- 所有交易都必須產生獨立的交易編號並儲存交易紀錄
- 查詢會員點數時，需驗證錢包餘額與交易紀錄計算之總額一致

**影響範圍**：
- 支付流程的系統互動邊界設計

---

## 歷史決策類

### PaymentService 功能設計規劃

> Confluence 頁面 ID：2884116
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884116)
> 摘要檔：[processed/2884116-summary.md](../../confluence/processed/2884116-summary.md)
> Confluence 最後更新：2021-08-20
> 摘要最後同步：2026-05-26

**決策背景**：
早期 PaymentService 的功能規劃與設計階段，決定先簡化支付流程，暫不考慮真實支付方式。

**決策結論**：
- 儲值 API 暫不處理支付方式，僅用 authkey 與 point
- 儲值與消費紀錄依日期分表，用於報表查詢
- 系統 log 統一寫入 logs 資料庫
- 會員錢包在註冊驗證完成後自動建立

**影響**：
- 支付方式查詢 API 雖規劃但未實作，需確認現行是否已擴充
- authkey 參數的產生、驗證與權限範圍需參考 auth 相關文件

---

### 2025-10-14 錦標賽需求確認

> Confluence 頁面 ID：79465505
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465505)
> 摘要檔：[processed/79465505-summary.md](../../confluence/processed/79465505-summary.md)
> Confluence 最後更新：2025-10-14
> 摘要最後同步：2026-05-26

**決策背景**：
錦標賽功能需求確認會議，列出待釐清的問題。

**決策結論**：
尚無決策，所有問題皆為待確認事項，包含：
- 報名費支付管道
- 點數通用性與有效期

**影響**：
- ⚠️ 直接影響 paymentservice 的業務邏輯設計，AI 開發前需取得明確答案

---

## 操作手冊類

### PaymentService 流程名稱列表

> Confluence 頁面 ID：24085309
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24085309)
> 摘要檔：[processed/24085309-summary.md](../../confluence/processed/24085309-summary.md)
> Confluence 最後更新：2021-08-24
> 摘要最後同步：2026-05-26

**摘要**：
僅列出九個流程名稱（儲值、購買文章、訂閱專家、購買/儲值紀錄查詢、點數查詢、付費方案查詢等），但未提供任何流程細節。

**AI 開發需要注意的部分**：
- 此文件資訊量不足，僅供了解服務功能範疇，需從其他文件取得實作細節
- ⚠️ 最後更新於 2021-08-24，需確認當前狀態