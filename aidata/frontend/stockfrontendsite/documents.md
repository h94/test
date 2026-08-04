Integrate Confluence summaries into documents.md. Output complete Markdown only.

# stockfrontendsite — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：{yyyy-MM-dd HH:mm}
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類


### Stock 規則列表

> Confluence 頁面 ID：32540498
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32540498)
> 摘要檔：[processed/32540498-summary.md](../../confluence/processed/32540498-summary.md)
> Confluence 最後更新：2022-06-21
> 摘要最後同步：{yyyy-MM-dd}

**摘要**：
本文件定義了 Stock（股票）模組中可用的篩選規則模板，涵蓋技術面（KD、MACD、Bias、Rel、MA）、成交量及籌碼面（券商、三大法人）等多種指標。每個規則模板提供可配置的參數選項，例如天數、比較運算符、數值範圍等，方便開發人員實現動態股票篩選與監控功能。文件還指出部分功能（如挖土機指標）已定義參數但尚未實裝，需於開發時注意。

**關鍵業務規則**：
- KD 隨機指標：可設定計算天數（如 9）、指標（K/D/J）、比較方式（大於、小於等）及目標數值（0-100），判斷當前值是否符合條件。
- KD 交叉：可設定發生天數（如近 1 天）及交叉類型（黃金交叉/死亡交叉），判斷是否出現交叉信號。
- MACD 指標：可設定計算天數（如 9）、比較對象（MACD/DIF/OSC）及與 0 軸或發生交叉的關係。
- Bias 乖離率：可設定均線類型（SMA/EMA/WMA）、天數及比較值或比較兩條乖離率線的關係。
- Rel 相對強度：可設定天數及比較值或比較兩條相對強度線。
- MA 移動平均線：可設定均線類型、天數、比較方式（突破/跌破）或多均線交叉關係。
- 成交量：可設定與 N 天均量的百分比或絕對張數比較，支援比較運算子，並可篩選創 N 日新高量或突破區間大量高/低價。
- 籌碼面－券商：可設定近 N 天內首次買入、買超/賣超連續天數等條件。
- 籌碼面－三大法人：可設定法人別、買賣超、連續天數及買賣超張數、排名等條件。
- 全域參數：支援依市場別（TSE/OTC）及產業類別篩選。

**注意事項**：
- ⚠️ 文件標註「挖土機指標有，但TCZB有參數(沒實裝)」，表示該指標功能尚未實現，開發時不應啟用。
- ⚠️ 文件最後更新於 2022-06-21，距今已有一段時間，可能部分規則已變更或棄用，建議與產品方確認。

---

### 精選股需求

> Confluence 頁面 ID：32540515
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32540515)
> 摘要檔：[processed/32540515-summary.md](../../confluence/processed/32540515-summary.md)
> Confluence 最後更新：2022-04-15
> 摘要最後同步：{yyyy-MM-dd}

**摘要**：
本文列出 Stock 模組的階段性功能需求，包含選股篩選條件可重複選擇、新增自選股頁面、標記股票是否首次符合條件（突破）、進階技術指標比對頁面、多項新增選股條件（MACD、SMA 乖離率、Rel 等）以及回測系統。對 AI 開發的幫助在於：提供清晰的前端功能範圍與篩選邏輯規則，可據此設計相應的 API 參數、後端篩選引擎與資料模型，特別是技術指標的比較條件需被精確轉化為運算邏輯。

**關鍵業務規則**：
- 選股篩選條件可重複選擇，不再限制單一條件。
- 選股時需標記該檔股票是否第一次符合條件（突破），輸出「突破」標記。
- 進階技術指標詳細頁面：使用者選取多檔股票後，需展示這些股票的所有技術指標以利比對。
- 新增篩選條件：近1天MACD發生黃金交叉（MACD線向上穿越訊號線）。
- 新增篩選條件：日MACD值小於0軸。
- 新增篩選條件：SMA20乖離率小於0。
- 新增篩選條件：SMA20乖離率大於SMA60乖離率。
- 新增篩選條件：Rel5大於Rel10。
- 新增篩選條件：Rel5大於0。
- 需提供回測系統功能（具體功能需參照附圖，細節需人工確認）。

**注意事項**：
- ⚠️ 文件最後更新於 2022-04-15，距今已有一段時間，部分需求可能已實作或變更，需人工確認目前開發狀態。
- ⚠️ 回測系統需求僅附圖說明，無具體文字描述，需人工補充詳細規格。
- ⚠️ 技術指標縮寫（如 Rel）未明確定義，需確認其公式與資料來源。

---

## 技術設計類


### Flutter App Architecture

> Confluence 頁面 ID：44665608
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Flutter+App+Architecture)
> 摘要檔：[processed/44665608-summary.md](../../confluence/processed/44665608-summary.md)
> Confluence 最後更新：2023-02-03
> 摘要最後同步：{yyyy-MM-dd}

**摘要**：
這份文件規範了 Flutter 專案的標準目錄結構與程式分層，包含 presentation（路由與頁面）、widget（共用元件）、type（資料型別與序列化）、func（公用函式）、api（HTTP 封裝）以及 bloc（狀態管理）的組織方式。對 AI 開發的幫助在於：能快速掌握前端程式碼的架構慣例，生成符合規範的頁面、路由、狀態管理或 API 呼叫程式碼，並了解 auto_route 的生成流程與 widget 拆分原則以優化渲染效能。

**關鍵設計決策**：
- 使用 auto_route 套件管理路由，每次修改路由後需執行 `flutter pub run build_runner watch --delete-conflicting-outputs` 重新生成 main.gr.dart
- 狀態管理選用 Bloc 套件，目錄依功能／頁面分層，每層包含 bloc.dart、event.dart、state.dart 三個檔案
- 兩個頁面引用同一個 Bloc 時各自獨立；若要跨頁面共享，需在 main.dart 註冊為全域 Bloc
- Widget 拆分為 StatelessWidget（靜態）與 StatefulWidget（動態），並盡量將需刷新的部分獨立成子 Widget，避免上層 StatefulWidget 導致不必要的整體 rebuild
- API 呼叫統一透過 api/http.dart 中的 $http 實例進行，各功能／頁面在各自的 api 檔案中引用 $http 發送請求
- 進入點 main() 負責生成 App、執行登入判斷、註冊全域狀態及特定初始化（如 iOS Firebase 配置）

**注意事項**：
- ⚠️ 文件最後更新於 2023-02-03，部分套件版本或寫法可能已變更，使用時需確認最新相容性

---

### StockFilterService API List

> Confluence 頁面 ID：34766919
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/StockFilterService+API+List)
> 摘要檔：[processed/34766919-summary.md](../../confluence/processed/34766919-summary.md)
> Confluence 最後更新：2023-07-10
> 摘要最後同步：{yyyy-MM-dd}

**摘要**：
本文件定義了 StockFilterService 的 REST API 端點、請求參數與回應格式。AI 開發時可據此了解如何查詢股票基本資料、歷史價格、券商進出、技術分析策略篩選及股利資訊，並理解各 API 的市場種類區分方式與參數限制，用於設計數據驅動的選股或分析功能。

**關鍵設計決策**：
- API 設計採用統一透過 POST 方法傳遞 JSON 請求體進行查詢，而非使用 URL 路徑參數或查詢字串。
- 股票市場以代號（如 `tw`, `usa`）作為 `kind` 參數區分，而非使用複數服務端點。
- 日期範圍查詢時，`StartDate` 和 `EndDate` 參數為可選，未提供時的行為需人工確認。
- 券商連續買賣超 API 限制 `Days` 參數必須大於 2 且小於 10，以確保查詢範圍的有效性。
- 策略篩選器支援單日 (`/strategy`) 與區間 (`/strategyRange`) 兩種模式回應格式不同，前者直接回傳股票代碼列表，後者回傳以日期為鍵的物件。

**注意事項**：
- ⚠️ 文件中提供的 IP 為私有 IP (192.168.x.x)，僅供內部開發與測試使用，實際部署時需替換為正式域名或服務發現名稱。
- ⚠️ 券商連續買賣超 API 的 `Days` 參數說明為「必須大於2, 小於10」，實際是否包含端點（如 3 到 9 天還是 2 到 10 天）需人工確認。
- ⚠️ `First` 參數（策略篩選器）的實際功能描述為「可帶可不帶, 預設False」，但其對回傳結果的具體影響未說明，需查閱程式碼或進一步測試。
- ⚠️ 部分 API（如版本、股票公司基本資料）為 GET 方法且無請求參數，可能查詢的是全量資料，需注意回應大小與效能問題。

---

## 歷史決策類


### 第一期分析報告(202206)

> Confluence 頁面 ID：38011167
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=38011167)
> 摘要檔：[processed/38011167-summary.md](../../confluence/processed/38011167-summary.md)
> Confluence 最後更新：2022-07-01
> 摘要最後同步：{yyyy-MM-dd}

**決策背景**：
本篇記錄了2022年6月一輪股票策略回測的方法與結果。重點在於透過兩兩規則組合逐步篩選強勢條件，找出能跨區間獲利的策略。結論發現兩個強勢條件（Rel9區間搭配WMA9乖離率，及大成交量搭配SMA5乖離率）分別對應小型飆股與權值股，且固定停損停利15%表現較佳，但不同停損停利需各自測試。此報告為後續回測參數調整與新策略組合提供了基準實驗方向。

**決策結論**：
- 為減少組合爆炸，先兩兩規則組成策略跑回測，挑獲利佳者再加入第三條規則繼續測試
- 淘汰的雙規則組合在後續加入新條件時仍有機會被重新選用，避免漏篩
- 採用多區間回測（不同年份、不同月份）驗證策略時間穩定性
- 後續規劃針對不同停損停利（5%,8%,20%）獨立測試，因發現無法通用

**影響**：
- ⚠️ 文件為2022年7月產出，市場條件已變化，結論的強勢條件與適用性可能不適用於當前
- ⚠️ 文中提到的未來規劃（測不同停損比例）可能已執行，但本篇未包含後續結果
- ⚠️ 回測條件截圖與 CSV 附件未附於本文，無法核對實際規則細節

---


## 操作手冊類


### Stock

> Confluence 頁面 ID：24091602
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Stock)
> 摘要檔：[processed/24091602-summary.md](../../confluence/processed/24091602-summary.md)
> Confluence 最後更新：2022-09-06
> 摘要最後同步：{yyyy-MM-dd}

**摘要**：
文件提供了一組測試帳號（zbdigital004）及對應密碼、Gmail 信箱，用於股票相關前端或後端服務的開發與測試。對 AI 開發者而言，此為存取測試環境所需的憑證資訊，可輔助進行功能驗證或除錯。

**注意事項**：
- ⚠️ 文件僅提供帳號資訊，無任何業務規則或設計細節。
- ⚠️ 帳號可能已過期或失效（最後更新於 2022-09-06），需確認目前是否仍可使用。
- ⚠️ 使用 Gmail 信箱可能涉及個人資料風險，應確認此為公司測試專用信箱。

---

### 手機站台操作說明

> Confluence 頁面 ID：38012173
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=38012173)
> 摘要檔：[processed/38012173-summary.md](../../confluence/processed/38012173-summary.md)
> Confluence 最後更新：2022-08-03
> 摘要最後同步：{yyyy-MM-dd}

**摘要**：
這份文件說明手機版股票站台的操作方式，涵蓋個股搜尋、技術分析圖表、新聞公告、自選股管理等核心功能模組。對 AI 開發而言，這份文件揭示了前端頁面的功能邊界與使用者互動流程，可作為理解 stockfrontendsite 服務操作邏輯的參考基礎。但文件偏向使用者操作手冊，缺乏後端業務規則的具體定義。

**注意事項**：
- ⚠️ 文件最後更新於 2022-08-03，距今已超過兩年，部分功能操作流程可能已變更，需人工確認與現行手機站台是否一致。
- ⚠️ 文件中提到台股大盤調整、類股周轉率排行等動態排行功能，但未說明資料更新頻率與計算邏輯，容易造成開發時誤解即時性需求。
- ⚠️ 交易所休市期間的延遲報價提示機制在文件中僅簡略提及，實際觸發條件與顯示邏輯需人工確認後台實作細節。