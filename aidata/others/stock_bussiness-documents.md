# stock_bussiness — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 12:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### Stock 訂閱付費策略 (pageId=40503753)

> Confluence 頁面 ID：40503753
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40503753)
> 摘要檔：[processed/40503753-summary.md](../../confluence/processed/40503753-summary.md)
> Confluence 最後更新：2022-12-23
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義 Stock 訂閱服務的層級（一般、高級、VIP）升降規則、到期日計算、差額補償公式及隱藏方案機制。前端需根據會員身分與剩餘天數計算總價並提示，後端透過「過水層」將前端選擇的方案轉換為對應的隱藏方案 subID 再進行扣款。文件亦記錄綠界各支付方式的手續費率。

**關鍵業務規則**：
- 一般升至高級/VIP：身分立即變更，訂閱到期日 = 付款日期 + 方案天數。
- 同級或往上升級續訂（高級→高級、VIP→VIP、高級→VIP）：到期日 = 原到期日 + 方案天數。
- 高級→VIP 升級：立即享有 VIP 權益，到期日同「原到期日 + 方案天數」，但需補繳原高級剩餘期間的價差。差額計算係數依剩餘天數決定：剩餘 ≥25 日補全額差額；≥15 日補差額×0.7；≥5 日補差額×0.4；<5 日不補差額。
- VIP 降級至高級：VIP 身分維持至原到期日，其後才以高級身分繼續，新到期日 = 原 VIP 到期日 + 方案天數；且此降級續訂僅能在原 VIP 到期日前 5 天內觸發。
- 綠界手續費：信用卡（國內）每筆 2.75%，最低收取 5 元；ATM/網路ATM 每筆 1%，最低收 10 元；超商代碼每筆 30 元；超商條碼每筆 15 元。

**注意事項**：
- ⚠️ 文件舉例日期有矛盾：高級→VIP 案例中寫「今日 11/15，原到期日 11/20」但補差額說明又寫「額外支付 11/10~11/20 VIP價格」，疑似筆誤，應為補 11/15～11/20 差額。需人工確認正確計算區間。
- ⚠️ 差額計算公式中的「補全額」定義不明確：可能指補繳剩餘天數的 VIP 與高級原價差（非折扣後），需進一步確認。

### 使用者權限 (pageId=38011517)

> Confluence 頁面 ID：38011517
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=38011517)
> 摘要檔：[processed/38011517-summary.md](../../confluence/processed/38011517-summary.md)
> Confluence 最後更新：2022-07-20
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義股票選股、券商買賣超、自選股、回測系統及通知等功能的會員權限矩陣。訪客參數限制最多，例如選股策略僅允許部分指標與限縮參數值，無法使用 MA、Rel、券商進出等功能；一般會員略多，高級會員則全功能開放。具體限制涵蓋參數範圍、使用次數、日期區間與通知管道。此文件可作為後端權限驗證及前端功能開關的業務規則單一資訊源。

**關鍵業務規則**：
- 選股策略：訪客使用KD指標時，K值限制1~10，僅能設定大於、小於條件，參數固定為20、50、80；一般及高級會員無限制。
- 選股策略：訪客使用MACD指標時，MACD9參數限制1~10，僅能大於、小於；若為黃金交叉事件，天數限制1~3，且僅允許黃金交叉。
- 選股策略：DIF9向上穿越0軸、Rel相對強度系列、MA移動平均線系列（突破、交叉、均線之上）等策略，訪客完全不可用。
- 選股策略中，Bias乖離率的SMA20乖離率大於0或大於SMA60時，訪客參數限制SMA天數1~10、僅大於小於、乖離率值1~10。
- 成交量策略：訪客僅能使用大於、小於條件，天數限制1~3，百分比限制1~100%，且「股價突破最大成交量區間高低點」策略完全不可用。
- 籌碼面-券商策略：訪客不可用；三大法人連續買超、買超排名、買超金額排名策略，訪客參數僅天數1~3。
- 券商買賣超：訪客「我的篩選紀錄」限制3個群組、5個券商；券商選擇僅顯示總行、台中分行、高雄分行；日期限前5個工作日；搜尋次數30次；無連續買賣超功能。
- 自選股：訪客群組上限5個，每群組股票上限20個，查詢券商進出次數每日限30次。
- 回測系統：訪客每日使用上限10次，日期區間限20個工作日。
- 通知：訪客無法使用任何通知；一般會員可使用Email及Telegram；高級會員額外可使用簡訊；策略通知一般及高級會員無限制。

**注意事項**：
- ⚠️ 文件最後更新於2022-07-20，部分權限規則可能已調整，需人工確認目前是否仍適用。
- ⚠️ 表格中部分策略的參數限制存在不符常理之處（如SMA1日均線與1日均線交叉），可能為筆誤，需核對原始功能定義。

### Sprint 100 酒田戰法圖形篩選法 (pageId=44665539)

> Confluence 頁面 ID：44665539
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44665539)
> 摘要檔：[processed/44665539-summary.md](../../confluence/processed/44665539-summary.md)
> Confluence 最後更新：2023-02-09
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件整理酒田戰法多種K線組合的篩選邏輯，記錄每個圖形的具體數值條件（價格關係、實體/引線比例、相似度）、實驗結果（V可用、O待觀察、X不適用）及後續資料庫修改提示。這些條件可直接轉化為程式中的過濾規則，用於開發股票圖形篩選功能，並輔助AI理解每種組合的精確定義與歷史實驗結論。

**關鍵業務規則**：
- 倒狀槌子：相似度0.99以上，收盤價等於最高價，(開盤價-最低價)/(最高價-最低價) >= 2/3。
- 多頭遭遇（VO狀態）：兩天非平盤；第二天上引線比例>=2/3；第一根(最高-最低)/最低 < 0.01為False；第一根最低==收盤==第二根最低==min(收盤,開盤)為false；若第二根紅K則第二天收盤價 > 第一天最低價且第二天開盤價 <= 第一天收盤價；若黑K則第二天黑K >= 第一天最低價；第二根無下引線且最高價 >= 第一天實體中點；第一根實體比例不小於0.301。
- 晨星（V標記）：相似度0.99以上，最低價=開盤價，(最高-最低)/開盤 < 0.01為False（太短）。
- 低價配（V標記）：第二根收盤價和開盤價不超過第一根的開盤價和收盤價之間（不能等於）。
- 南方三星（V標記）：第一根收盤價與開盤價位於自己K棒內（不能等於）且不能收平盤，第二天收盤 > 第一天開盤 > 第一天收盤 > 第二天開盤。
- 大敵當前（X標記）：兩天非平盤，兩天收盤價相同（繼續觀察）。
- 空頭遭遇（X標記）：兩天非平盤，第二天最低點高於第一天實體中點，兩天(最高-最低)/最低 >= 0.01，第二天實體比例 <= 1/3，顏色需check，兩天收盤價相同。
- 其他多項圖形條件詳見文件表格，皆為具體數值邊界與價格關係定義，可直接轉換為代碼過濾條件。

**注意事項**：
- ⚠️ 多處標記「待觀察」、「再觀察」、「實驗成功只有一檔」，條件可能不穩定，需人工確認後再正式採用。
- ⚠️ 部分條件已劃刪除線（如「第三天開盤 <= 第一天收盤」），表示已修改，閱讀時應以最新版本為準。

### 股票King機制需求 (pageId=38011555)

> Confluence 頁面 ID：38011555
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=38011555)
> 摘要檔：[processed/38011555-summary.md](../../confluence/processed/38011555-summary.md)
> Confluence 最後更新：2022-07-15
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了股票King系統的會員機制與自動回測功能的業務需求。核心內容包括：會員層級流轉規則（未驗證→免費→付費/VIP）、第三方登入整合（Google/Facebook）、以及自動回測功能的權限控制與排程執行流程。

**關鍵業務規則**：
- 會員層級分為四級：未驗證會員、免費會員、付費會員、VIP會員
- 註冊成功後會員層級為「未驗證會員」，Email 驗證成功後自動變更為「免費會員」
- 付費會員和VIP會員須通過付款才能變更，且這兩個層級有期限限制
- 免費會員沒有自動回測功能
- 自動回測功能沒有數量限制（付費/VIP會員使用上無上限）
- 自動回測每日完成計算後，由 StockMessageService 更新策略狀態（endtime、status）
- 自動回測的 DB 表為 backtesting，透過 id=1 取得使用者新增的回測策略
- 自動回測排程僅針對付費使用者（StockMessageService 向 MemberService 請求 get pay user）
- 會員到期時間儲存於 User 表的 SubEndTime 欄位，到期時間為到期日的 23:59:59
- 同一使用者可透過第三方登入（Google、Facebook）綁定既有帳號或建立新帳號
- 支援取得使用者自動回測數量 API 和更新自動回測設定 API
- 登入成功後，Token 會快取於 Redis，後續請求使用者資料時先從 Redis 取得登入快取

**注意事項**：
- ⚠️ 文件最後更新於 2022-07-15，距今已超過兩年，部分實作細節可能已變更，需人工確認現狀

---

## 技術設計類

### Stock API List (pageId=44665643)

> Confluence 頁面 ID：44665643
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Stock+API+List)
> 摘要檔：[processed/44665643-summary.md](../../confluence/processed/44665643-summary.md)
> Confluence 最後更新：2023-02-17
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件是 Stock 模組測試版的 API 列表，記錄了所有測試中 API 的 HTTP 方法、路徑、參數與回傳範例。涵蓋版本檢查、資料寫入、券商資料、公司資訊、FlowControl 狀態、指數與股價查詢、技術指標等端點。

**關鍵設計決策**：
- 測試環境的 API 路徑與主線分開，因尚未 merge 至主線，開發時需注意到路徑差異。
- FlowControl 相關 API 用於追蹤各國資料處理的完成狀態（如 broker_check_complete、calculation_complete 等），並以 kind 參數區分國家（台灣可省略）。
- API `get_flowcontrol_single_date` 標記為「美國會減一天」且「之後會刪除」，設計上將由 v2 API 取代。
- 部分 API 的 `kind` 參數在台灣市場時可省略，預設為台灣，設計上簡化台灣使用者的呼叫。

**注意事項**：
- ⚠️ 文件最後更新於 2023-02-17，測試版網址 (192.168.9.231:22332) 為內部 IP，現階段可能已無法存取或已被新版本取代。
- ⚠️ API `get_flowcontrol_single_date` 標注「之後會刪除」，可能已由 `get_flowcontrol_single_date_v2` 替換，開發時應優先使用 v2。

### stock API (pageId=24092771)

> Confluence 頁面 ID：24092771
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/stock+API)
> 摘要檔：[processed/24092771-summary.md](../../confluence/processed/24092771-summary.md)
> Confluence 最後更新：2022-02-21
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義一個股票後台工具的 API 規格，包含六個端點：取得分點進出用的股票代碼清單、移除特定代碼、取得所有股票在指定日期的價格資料（含 limit）、取得單一股票向前推若干交易日的歷史、取得加權指數及櫃買指數向前推若干交易日的歷史。

**關鍵設計決策**：
- 採用 RESTful GET 方法提供股票代碼、價格、指數等查詢，參數以 query string 傳遞，回應統一為 JSON
- 使用 page 概念管理股票代碼集合，可能用於分批處理或分點進出篩選，實際 page 實作方式未知
- 指數資料與個股資料使用相同結構（code、date、change、closeprice 等），但加權指數 code 值為 '發行量加權股價指數'，櫃買指數 code 值為 '櫃買指數'
- 均線計算採用先撈原始資料、再計算平均值後寫入 DB 的離線處理模式，避免即時運算負擔

**注意事項**：
- ⚠️ 文件最後更新於 2022-02-21，且路徑歸類於「舊的Projects 1-200」，這些 API 可能已變更或淘汰，請確認是否為現行服務

### TCZB-1736 - [StockRuleService] - API實作 (pageId=32540251)

> Confluence 頁面 ID：32540251
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32540251)
> 摘要檔：[processed/32540251-summary.md](../../confluence/processed/32540251-summary.md)
> Confluence 最後更新：2022-04-14
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文档定义了 StockRuleService 的 REST API 接口，包括规则、选项、我的策略、我的券商等资源的读取、新增、修改、删除操作，以及最后交易日查询。

**關鍵設計決策**：
- API 采用 REST 风格设计，资源操作对应 HTTP 方法（GET 读取、POST 新增、PUT 修改、DELETE 删除）。
- 用户（user）参数使用路径或查询参数传递，代表账户（Account），用于区分个人自定义数据（我的策略、我的券商）。
- 新增规则时，ID 和 Enabled 字段由系统自动生成，前端不需要提供。
- 新增选项时，已存在的数据会自动跳过，避免重复。
- 修改我的策略/券商名称使用独立的 PUT 接口，仅需提供新名称字段（Name）。

**注意事項**：
- ⚠️ 文档最后更新于 2022-04-14，可能已过时，接口或模型可能已变更，使用前需确认最新版本。
- ⚠️ 接口路径中存在格式错误，如 DELETE /stockruleservice/api/favoriterule/{user/{favoriterulename} 缺少斜杠，实际应为 /stockruleservice/api/favoriterule/{user}/{favoriterulename}，同样问题出现在删除我的券商接口中。

### TCZB-2008 [Stock] - 後臺會員管理API (pageId=38012014)

> Confluence 頁面 ID：38012014
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=38012014)
> 摘要檔：[processed/38012014-summary.md](../../confluence/processed/38012014-summary.md)
> Confluence 最後更新：2022-08-10
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義了股票後台會員管理的 API 設計，包含對外接口 (memberservice) 和內部過水層 (pricebackendservice) 的六個端點：新增使用者、查詢使用者列表（含分頁、模糊搜尋、排序）、變更聯絡資訊、變更會員層級、變更密碼、變更啟用狀態。

**關鍵設計決策**：
- 採用過水層架構：外部 API 掛在 memberservice 路徑下，實際邏輯由 pricebackendservice 處理，以隔離直接暴露後端服務。
- 變更資源類的 API（聯絡資訊、層級、密碼、啟用狀態）採用 PUT 方法，並將 Account 作為路徑參數（{account}），使 URI 更符合 REST 風格且避免在 body 中重複指定。
- 查詢列表 API 設計了豐富的查詢參數（模糊搜尋、過濾、排序），允許前端靈活獲取資料。
- 響應統一使用 MsgCode Model，包含 Code 與 Message 以標準化錯誤與成功回應。

**注意事項**：
- ⚠️ 文件最後更新於 2022-08-10，距今已有一段時間，需人工確認這些 API 及規則目前是否仍現行有效。

---

## 歷史決策類

### 相關係數選股與挖土機相似度低原因 (pageId=40503929)

> Confluence 頁面 ID：40503929
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40503929)
> 摘要檔：[processed/40503929-summary.md](../../confluence/processed/40503929-summary.md)
> Confluence 最後更新：2022-11-03
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**決策背景**：
本文解釋挖土機的型態選股採用轉折波方法（以均線分界高低點連線），與 stockcandle 模組基於每日股價的相關係數方法差異過大，因此兩者相似度比對無意義。

**決策結論**：
型態篩選應參考 XQ 的做法，而非使用相關係數。

**影響**：
理解不應嘗試用相關係數去匹配挖土機的轉折波型態結果，可避免設計錯誤的相似度演算法。

---

## 操作手冊類

### 回測系統 (pageId=34767218)

> Confluence 頁面 ID：34767218
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=34767218)
> 摘要檔：[processed/34767218-summary.md](../../confluence/processed/34767218-summary.md)
> Confluence 最後更新：2022-08-05
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件是 StockKing 網站回測功能的操作手冊，說明使用者如何設定回測參數（日期、手續費、進出場時機、股票範圍、策略），以及執行回測後查看詳細損益與買賣紀錄。高級會員可啟用每日盤後自動回測功能。

**AI 開發需要注意的部分**：
- 手續費預設 0.1425%，可設定折扣，折扣後手續費會即時顯示。
- 進出場時機必須選擇，否則無法開始回測。
- 自動回測功能限高級（付費）會員勾選，每日盤後資料更新後自動執行。

### 自選股 (pageId=34767210)

> Confluence 頁面 ID：34767210
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=34767210)
> 摘要檔：[processed/34767210-summary.md](../../confluence/processed/34767210-summary.md)
> Confluence 最後更新：2022-08-05
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件說明StockKing網站自選股功能的操作流程，包含新增/刪除群組、搜尋股票、以星號加入或移除自選股、以及跳轉券商進出頁面。並揭示一般會員在群組數量（5個）、每群組股票數（20個）、查詢券商進出次數（30次）上的限制。

**AI 開發需要注意的部分**：
- 一般會員只能建立最多5個自選股群組。
- 每個自選股群組最多可加入20檔股票。
- 一般會員查詢券商進出頁面的次數限制為30次。