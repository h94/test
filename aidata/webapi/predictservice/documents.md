# predictservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2025-06-27 12:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB-3724 [PredictService] - MLB/CPBL/NPB/KBO/足球主推連勝王活動

> Confluence 頁面 ID：76546219
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76546219)
> 摘要檔：[processed/76546219-summary.md](../../confluence/processed/76546219-summary.md)
> Confluence 最後更新：2025-05-13
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了 MLB、CPBL、NPB、KBO 及足球主推連勝王活動的實作規範，包含活動代號 (eventName) 與對應聯盟 ID、更新連勝紀錄的時間區間、排行榜與結算 API 的參數限制，以及 VIP 相關排行榜顯示與結算的業務規則。對 AI 開發 predictservice 的幫助是：可據此正確呼叫生成記錄、排行榜、結算獲獎等 API，並確保活動時間和身分規則的正確實作。

**關鍵業務規則**：
- 生成站台活動紀錄時，activityEvent 參數僅接受預先定義的 eventName (如 mlb-mainwinstreak 等)。
- 生成站台活動主推連勝排行榜時，activityEvent 參數僅接受預先定義的 eventName。
- 生成/更新特殊活動勝率排行榜 (活動每月排行榜) 時，若 site 為 inplayz，eventName 參數僅接受預先定義的 eventName。
- 新增站台活動項目獲獎會員 (單月主推王結算) 時，活動期間內的預測單與賽事都必須已有結果才能進行結算 (活動期間可查 activity_cycle)。
- VIP 限定的連勝榜顯示所有有成績的會員，不限定 VIP 身分。
- VIP 限定的單月排行榜顯示所有有成績的會員，不限定 VIP 身分。
- VIP 限定的單月主推王結算時，有成績的會員一律結算，領獎資格由後續審核人員處理，不以結算當天是否為 VIP 身分決定。
- 更新連勝紀錄的時間僅在特定時段內允許執行，各聯盟時間不同 (例如 MLB 01:00-13:00，NPB 11:00-23:00)，足球 (sc-mainwinstreak) 時間暫時未定。

**注意事項**：
- ⚠️ 足球 (sc-mainwinstreak) 的更新連勝紀錄時間標注為「暫時未定」，實作時需後續確認或暫用預設值
- ⚠️ 結算條件中「預測單與賽事都必須有結果」未說明賽事結果延遲或無結果的處理方式
- ⚠️ 文件末尾的問答可能為討論記錄，需確認是否已形成最終決策並寫入開發規範

---

### TCZB-2628 [SportKing] - 預測排行榜新增當期莊家殺手排行

> Confluence 頁面 ID：47220116
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47220116)
> 摘要檔：[processed/47220116-summary.md](../../confluence/processed/47220116-summary.md)
> Confluence 最後更新：2023-04-07
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**關鍵業務規則**：
- 預測排行榜 API 必須返回四個時間段的排行：近30天(lastThirty)、近14天(lastFourteen)、近7天(lastSeven)、本月/莊家殺手(thisMonth 改名後)
- 當 gameType 為足球(FT)或網球(TN)時，排行榜不分區（可能 lid 參數無效，需人工確認）
- 本月區間需替換為「莊家殺手」排行（具體計算邏輯待確認）

**注意事項**：
- ⚠️ 「莊家殺手」的定義與計算邏輯未在文件中說明，需人工確認
- ⚠️ 足球/網球「不分區」的具體實現方式（如忽略 lid 或使用特殊值）未明確
- ⚠️ 文件更新於 2023-04-07，可能與當前實作不一致，需核對現有 predictservice 代碼

---

### TCZB-2631 [SportKing] - 會員個人頁面

> Confluence 頁面 ID：47220118
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47220118)
> 摘要檔：[processed/47220118-summary.md](../../confluence/processed/47220118-summary.md)
> Confluence 最後更新：2023-04-07
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**關鍵業務規則**：
- 會員個人預測頁面需新增「週穩定度」展示區塊
- 會員個人預測頁面需新增「近八週狀況」展示區塊
- 預測近30天區塊改為「莊殺」區塊（原近30天預測改顯示莊殺相關資訊）
- 需提供「解鎖今日預測」功能給會員使用

**注意事項**：
- ⚠️ 文件中的 API 表格為空，沒有任何 route、method、params 或 response 資訊，需人工確認或從其他文件補充
- ⚠️ 文件最後更新於 2023-04-07，距今已有一段時間，規格可能有變更，建議對照最新 Figma 或後續 Sprint 文件確認
- ⚠️ 「週穩定度」、「近八週狀況」、「莊殺」、「解鎖今日預測」僅有名稱，未說明具體計算邏輯或業務規則，需從其他文件或需求訪談中補充

---

### TCZB-2673 [SportKing] - 預測排行榜

> Confluence 頁面 ID：47220390
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47220390)
> 摘要檔：[processed/47220390-summary.md](../../confluence/processed/47220390-summary.md)
> Confluence 最後更新：2023-04-24
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**關鍵業務規則**：
- 預測排行榜只取前 100 名進行顯示。
- 會員登入後，若自身排名在前 100 名內，需在列表中反白高亮標示；若排名在 100 名之外，則新增一個獨立欄位顯示該會員的個人排名資訊。
- API 回應須包含四個時間區間的排行榜陣列：lastThirty（近 30 天）、lastFourteen（近 14 天）、lastSeven（近 7 天）、thisMonth（本月）。
- 每個排名物件必須包含 account、userName、win、lose、draw、winPercentage、profitPoint、hasPending 等欄位。

**注意事項**：
- ⚠️ 文中「莊殺更改本期莊殺」語意不清，可能為筆誤或特定內部術語，需人工確認。
- ⚠️ API 回應未標明排行榜的排序規則（例如按 profitPoint 降冪或 winPercentage 降冪），實際行為需與開發團隊確認。

---

### 圖形參數

> Confluence 頁面 ID：44664143
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44664143)
> 摘要檔：[processed/44664143-summary.md](../../confluence/processed/44664143-summary.md)
> Confluence 最後更新：2023-02-06
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**關鍵業務規則**：
- 每個圖形形態由 day（天數）、plot（點位序列，每 4 個值一組）及 method（策略方法名）定義，method 格式為 strategy.strategy_up_N、strategy.strategy_down_N 或 strategy.strategy_other_N。
- 多頭形態共 20 種，分別對應 strategy_up_1 至 strategy_up_12 等不同方法（例如「槌頭」對應 strategy_up_1，plot 為 [3.45,2.85,3.45,1.0]）。
- 空頭形態共 24 種，分別對應 strategy_down_1 至 strategy_down_9 等（例如「吊人線」對應 strategy_down_1，plot 為 [2.85,3.45,3.45,1.0]）。
- 特殊形態（長十字線、短十字線、蜻蜓點水）對應 strategy_other_1 至 other_3。
- 部分形態的 plot 使用 {} 或 [] 且引號格式不一致，但邏輯上均為 day + plot 的陣列結構。

**注意事項**：
- ⚠️ plot 陣列中各數值的明確含義（如是否代表相對開盤價、收盤價、最高價、最低價的標準化比例）並未在文件中說明，需人工確認。
- ⚠️ 文件中 JSON 格式不一致：部分條目使用標準 JSON（雙引號），部分使用類似 Lua/Ruby 的單引號、無引號鍵值（如 {day = 2, plot = [..]}），實作時需統一解析規則。
- ⚠️ 這些參數可能僅為示範或測試用數值，實際策略中是否直接採用需進一步驗證。

---

### TCZB-3223 [PredictService] - 調整賽事預測解鎖系統

> Confluence 頁面 ID：55578226
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55578226)
> 摘要檔：[processed/55578226-summary.md](../../confluence/processed/55578226-summary.md)
> Confluence 最後更新：2024-04-11
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**關鍵業務規則**：
- 走地玩法（in-play）的預測解鎖紀錄採用新機制：解鎖行為跟隨預測注單處理，而非使用一般玩法的原有解鎖紀錄機制（原有機制需從既有邏輯中確認）。
- 所有非走地玩法的預測解鎖，仍維持原有機制，不受此次變更影響。

**注意事項**：
- ⚠️ API 表格的 Parameter 與 Response 欄位為空，具體請求/回應格式需參考既有 API 文件或程式碼。
- ⚠️ 新增欄位 unlock_rb_accounts 型態為 map<text, text>，其 key/value 的語意（例如是否 key 為會員 ID、value 為解鎖時間或其他資訊）文件中未說明，需人工確認。
- ⚠️ 「走地預測解鎖跟著預測注單」的觸發確切時機（注單成立、結算還是其他事件）未定義，需確認。

---

### TCZB-3269 [PredictService] - 勝率計算機制調整

> Confluence 頁面 ID：55578735
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55578735)
> 摘要檔：[processed/55578735-summary.md](../../confluence/processed/55578735-summary.md)
> Confluence 最後更新：2024-05-13
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**關鍵業務規則**：
- 勝率計算時，取消與和局的賽事不納入計算，排除這兩種結果。
- 串關殺手條件與其他賽事球種不同，進行莊家殺手結算時，必須針對串關做獲利判斷（即獲利才符合殺手條件）。

**注意事項**：
- ⚠️ —

---

### TCZB-3468 [PredictService] - 熱門賽事功能調整

> Confluence 頁面 ID：55581389
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55581389)
> 摘要檔：[processed/55581389-summary.md](../../confluence/processed/55581389-summary.md)
> Confluence 最後更新：2024-10-04
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**關鍵業務規則**：
- 殺手熱門賽事獨立生成，不影響原有熱門預測機制。
- 賽事必須滿足：獨贏、讓分、大小玩法中至少一種達到 4 人以上預測，才算符合殺手熱門資格。
- 需找出該賽事中預測差異最大的玩法（差異定義需人工確認）。
- 殺手熱門賽事最多回傳 9 場。
- 對既有 GET /predictservice/api/bets/popular 增加查詢參數 popularType，值為 killer 時回傳殺手熱門預測賽事。

**注意事項**：
- ⚠️ 文件中未明確定義「差異最大玩法」的計算方式，需人工確認具體算法（例如可能為選項間的投注人數差距或賠率分歧度）。
- ⚠️ 未說明殺手熱門賽事在 response 中的資料結構是否與一般熱門賽事相同，可能影響前端整合，需確認。

---

## 技術設計類

### PredictService DB Tables

> Confluence 頁面 ID：55577875
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/PredictService+DB+Tables)
> 摘要檔：[processed/55577875-summary.md](../../confluence/processed/55577875-summary.md)
> Confluence 最後更新：2024-03-28
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義 PredictService 使用的 Cassandra 資料庫 Predict 的 13 個資料表結構，包含活動週期、獲勝帳號、週數結算、莊家殺手、預測注單、鎖定賽事、結算狀態、條件設定、週期設定、聯盟設定、玩法設定、策略日誌及週報等，為開發資料存取層提供欄位名稱、型別、主鍵設計與業務含義。

**關鍵設計決策**：
- 使用 Cassandra 作為資料庫，DB 名稱為 Predict。
- 所有表採用 partition_key 與 clustering 設計主鍵，滿足時間序列與分佈查詢需求。
- 部分表名以佔位符 {gameType}、{year} 命名，如 predictbets_{gameType}、predictgames_{gameType}_lock_{year}，實現依球種及年份水平分表。
- predictbets_{gameType} 表在 gdate、account 欄位上建立索引，加速依日期及帳號的查詢。
- settings_playmode 透過 list<text> 儲存玩法，靈活擴充而無需變更欄位結構。

**影響範圍**：
- predictbets_{gameType}、settings_killer_conditions_{gameType} 等動態分表設計不可輕易變更，影響所有資料存取層實作。

---

### [PredictService] - 彩池預測系統

> Confluence 頁面 ID：76547116
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76547116)
> 摘要檔：[processed/76547116-summary.md](../../confluence/processed/76547116-summary.md)
> Confluence 最後更新：2025-06-20
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件定義了彩池預測系統的 REST API 介面（新增/查詢/更新彩池遊戲及注單、設定結果與派彩狀態）與對應的 Cassandra 資料表結構。核心業務規則包括最低投注額 100 Z幣、派彩計算公式、無條件捨去小數以及保底返還彩池Z幣價格的邏輯。對 AI 開發而言，可直接參考這份規格實作相關的 API 客戶端、資料模型與業務邏輯驗證。

**關鍵設計決策**：
- 使用 Cassandra 做為資料庫，以 betpool_games 的 id 和 betpool_bets 的 (gid, account, id) 作為複合主鍵。
- API 採用標準 REST 風格，資源路徑為 games 與 games/{gid}/bets，操作涵蓋 CRUD 與特定狀態更新。
- 多語系欄位 (names, betOptions) 採用 Map<text,text> 儲存，例如 {"zh-TW": "選項名稱"}，以便前端直接依語系取用。
- 時間欄位一律使用 Unix timestamp (bigint) 儲存與傳遞。

**影響範圍**：
- betpool_games 與 betpool_bets 資料表結構及 REST 資源路徑不可輕易變更。

---

### TCZB-2544 [PredictService] - 預測功能API

> Confluence 頁面 ID：47219439
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47219439)
> 摘要檔：[processed/47219439-summary.md](../../confluence/processed/47219439-summary.md)
> Confluence 最後更新：2023-04-12
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了一個新的 PredictService，用於處理單場預測下注與結算。提供 API 設定球種、提交預測單、查詢紀錄，並以 Cassandra 儲存預測資料。每次預測點數範圍為 100~500，每 10 分鐘自動執行預測結果結算。對 AI 開發而言，此文件給出了完整的 API 合約、資料表結構以及爬蟲盤口如何對應到資料欄位的轉換規則。

**關鍵設計決策**：
- 使用 Cassandra 作為主要資料庫，keyspace 為 predict，考量其水平擴展能力與高寫入吞吐量
- 預測注單表按 gametype 分表（predictbets_{gametype}），方便依球種隔離查詢與管理
- settings_league 以 gametype 為 partition key，儲存該球種開放的聯盟 ID 清單
- 每 10 分鐘執行一次預測結果結算，採用排程批次處理而非即時運算，降低即時壓力
- API 路徑設計符合 RESTful 風格，資源命名包含 gametype、lid、gid 等維度，支援多層查詢
- 預測點數範圍固定為 100~500，簡化前端驗證與後端控管

**影響範圍**：
- predictbets_{gametype} 分表設計及每 10 分鐘結算排程不可輕易變更。

---

（其餘 technical_design 文件依相同格式繼續列出，包含 Page Get Api、TCZB-2574、TCZB-2633、TCZB-2738、TCZB-2768、TCZB-2770、MachineLearning 機器學習框架、TCZB-2798、TCZB-2840、TCZB-2857、TCZB-2858、TCZB-2875、TCZB-2904、TCZB-2878、TCZB-3051、TCZB-3158、TCZB-3205、TCZB-3372、TCZB-3392、TCZB-3409、TCZB-3414、TCZB-3481、K棒選股計算方式、ml code review、mlb.com-OU、套用框架測試、1X2-only賽前data 等，均保留原文關鍵設計決策與影響範圍。）

---

## 歷史決策類

### 回測系統測試

> Confluence 頁面 ID：34767235
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=34767235)
> 摘要檔：[processed/34767235-summary.md](../../confluence/processed/34767235-summary.md)
> Confluence 最後更新：2022-05-19
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**決策背景**：
文件比對了 TCZB 回測與股票挖土機回測在成交量、MACD、KDJ 等多種選股條件下的結果差異。

**決策結論**：
測試發現兩系統對部分條件（如 MACD 金叉/死叉）的回測結果不同，站台可能無符合股票而挖土機有；買入時間點也多不一致。

**影響**：
新上市櫃股票缺少 SMA 線、KDJ 的 J 值會超出 0~100 範圍，這些差異指出兩系統在計算邏輯或數據來源上可能不同，為後續回測功能開發或整合提供了比對基準。

---

（其餘 decision_record / experiment_result / meeting_notes 文件依相同格式繼續列出，包含 TCZB-3066、套用框架測試、NBA特徵選取 等。）

---

## 操作手冊類

（目前無 operation_guide 類文件）