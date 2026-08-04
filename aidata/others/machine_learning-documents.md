# machine_learning — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：{yyyy-MM-dd HH:mm}
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---


## 業務規範類


### 球頭取值規則

> Confluence 頁面 ID：24092140
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24092140)
> 摘要檔：[processed/24092140-summary.md](../../confluence/processed/24092140-summary.md)
> Confluence 最後更新：2022-01-17
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義從賽事數據中提取「球頭」(handicap/讓球盤口)的標準化規則，用於統一盤口數據的處理邏輯。說明了三種情境下的取值方法，為盤口數據清洗與正規化提供明確依據，確保賠率比較、數據聚合或特徵工程基於一致標準進行。

**關鍵業務規則**：
- 球頭取值規則：若球頭僅開在主隊，則直接取主隊球頭值
- 球頭取值規則：若球頭僅開在客隊，則取客隊球頭值乘以 -1
- 球頭取值規則：若球頭兩邊都有開，則直接取客隊球頭值

**注意事項**：
- ⚠️ 文件以截圖為主，缺少詳細文字說明與上下文，難以確認適用的具體交易場景、賽事類型或資料庫欄位
- ⚠️ 未說明當主客隊都未開盤時的處理方式（回傳 NULL 或預設值），需人工確認


### 台股移動平均線買賣規則

> Confluence 頁面 ID：15401756
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=15401756)
> 摘要檔：[processed/15401756-summary.md](../../confluence/processed/15401756-summary.md)
> Confluence 最後更新：2021-03-23
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義台股50移動平均線分析需求，要求導入5、7、13日均線，並給出基於均線交叉的買賣規則。提供可程式化的交易信號規則，可作為預測模型的特徵或回測策略的基礎。

**關鍵業務規則**：
- 買入條件：5日均線 > 7日均線 > 13日均線首次發生時觸發買入信號
- 賣出條件：5日均線 < 7日均線首次發生時觸發賣出信號

**注意事項**：
- ⚠️ 文件來自舊 Projects，最後更新於 2021 年，規則可能已過時或已被取代
- ⚠️ 「首次發生」的定義不夠明確，需人工確認是指每次交叉都算首次，還是僅在持倉狀態切換時生效


### 酒田戰法圖形篩選條件

> Confluence 頁面 ID：44664416
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44664416)
> 摘要檔：[processed/44664416-summary.md](../../confluence/processed/44664416-summary.md)
> Confluence 最後更新：2023-01-19
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
記錄酒田戰法多種K線組合的圖形篩選條件與實驗結果，包含每個圖形的辨識公式、相似度門檻、例外排除條件，以及標記「實驗成功」、「實驗失敗」或「再觀察」的狀態。可直接作為股票圖形選股AI的業務規則基礎，需注意版本狀態。

**關鍵業務規則**：
- 相似度預設至少 0.85 以上，部分圖形要求 0.99 以上
- 槌子線：相似度 0.99 以上；收盤價等於最高價；(開盤價 - 最低價) / (最高價 - 最低價) >= 2/3
- 貫穿線：第二根K棒收盤價位於第一根K棒開收價之間；開盤價在第一根K棒開盤價與最低價之間；兩根K棒不可收平盤
- 空頭遭遇（標記X，已棄用）：多頭遭遇實驗失敗，暫時不使用
- 多頭反攻（標記X，已棄用）：實驗失敗，暫時不使用

**注意事項**：
- ⚠️ 本文件為實驗記錄，多數規則標有狀態，篩選條件可能不穩定
- ⚠️ 部分規則中有刪除線標記，表示規則有演進，需確認最終版本
- ⚠️ 多頭反攻與空頭遭遇等圖形已標記X並註明實驗失敗，不應納入正式規則


### 回測API策略條件格式

> Confluence 頁面 ID：34767716
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=34767716)
> 摘要檔：[processed/34767716-summary.md](../../confluence/processed/34767716-summary.md)
> Confluence 最後更新：2022-05-25
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
記錄回測 API 的測試請求範例，涵蓋 SMA 乖離率、日 K/D、MACD 交叉、成交量等多種策略條件組合。歸納出策略條件的 JSON 編碼格式，可用於理解請求結構與條件參數語意。

**關鍵業務規則**：
- 策略條件以 JSON 物件陣列傳遞，每個物件包含 text（描述文字）、ID（條件類型代碼）、Value（參數值陣列）
- ID=9（SMA乖離率）：Value 為 [均線類型, 天數, 比較運算符, 閾值]
- ID=1（日KDJ值）：Value 為 [線型（K/D/J）, 天數, 比較運算符, 閾值]
- ID=2（KD交叉）：Value 為 [天數, 幾天內, 交叉類型]
- ID=8（MACD交叉）：Value 為 [天數, 幾天內, 交叉類型]
- ID=13（成交量絕對值）：Value 為 [比較運算符, 張數]
- ID=3（成交量與均量比較）：Value 為 [比較運算符, 均量天數, 百分比]

**注意事項**：
- ⚠️ 截圖附件可能已無法存取，實際測試結果無法檢視
- ⚠️ 最後更新為 2022-05-25，API 規格可能已變更
- ⚠️ 文件僅為測試案例記錄，非正式規格文件


### 股票相關係數新算法

> Confluence 頁面 ID：40504312
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40504312)
> 摘要檔：[processed/40504312-summary.md](../../confluence/processed/40504312-summary.md)
> Confluence 最後更新：2022-11-10
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
記錄圖型選股功能中股票相關係數計算方式的變更，從四價比對改為每日最高價與最低價中點的單點比對。若實作股票相關性分析或選股邏輯時應遵循此新算法。

**關鍵業務規則**：
- 股票相關係數計算使用每日 (High + Low) / 2 作為代表價格，進行單點相關係數計算，不再使用四價比對

**注意事項**：
- ⚠️ 文件僅包含截圖與簡短描述，缺少完整算法定義、例外處理與適用場景
- ⚠️ 最後更新為 2022-11-10，需確認是否仍為現行做法

---

## 技術設計類


### OtherInfo 欄位格式定義

> Confluence 頁面 ID：79463406
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463406)
> 摘要檔：[processed/79463406-summary.md](../../confluence/processed/79463406-summary.md)
> Confluence 最後更新：2025-09-09
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義來自 Naver、PlaySport、Covers、Yahoo Japan、Forebet、CPBL、CBSSports、AiPredict、SoccerVital 等資料來源的 OtherInfo 欄位格式。詳列各來源的鍵值名稱、中文意義、巢狀結構路徑及資料型態範例，是實作資料解析器與特徵提取模組的必要參考。

**關鍵業務規則**：
- home_probability/away_probability/draw_probability 的值格式為百分比字串，需人工確認所有來源是否統一格式
- bet_HA 欄位值：若客隊預測比例較高則為 "Away"，否則為 "Home"（未定義相等時的處理方式）
- pit_kind 為巢狀結構，鍵為球種名稱，值包含 speed 與 percent
- SoccerVital 的 last_five_results 為固定長度的陣列，內容為 "won"、"lost"、"draw"
- AiPredict 的 predict_HA 格式為帶正負號的數字字串

**關鍵設計決策**：
- OtherInfo 欄位採用巢狀結構存放複雜資訊，解析時需遞迴處理
- 不同資料來源使用不同鍵值名稱代表相同語意數據，系統需依據來源套用 Mapping Table
- 文件依資料來源分章節定義，暗示以資料來源為單位進行解析與正規化

**影響範圍**：
- 所有需要解析爬蟲回傳 OtherInfo JSON 的模組

**注意事項**：
- ⚠️ 文件標題為「Naver.com」但實際為爬蟲資料定義，需確認 Naver 是否仍為有效來源
- ⚠️ PlaySport 的 vs_home/vs_away 定義為「對戰當前對手的數據」而非對主/客隊
- ⚠️ 部分路徑使用斜線表示「或」，需人工確認實際 JSON 結構


### 走地即時賽事資訊定義

> Confluence 頁面 ID：79465745
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465745)
> 摘要檔：[processed/79465745-summary.md](../../confluence/processed/79465745-summary.md)
> Confluence 最後更新：2025-10-31
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
明確列出足球、籃球、冰球和美式足球在走地賽事中系統涵蓋的統計資訊項目名稱。定義了需被系統捕捉、解析和儲存的即時比賽事件類型，是開發即時比分或賽事數據 AI 功能時 Data Features 範圍的基礎。

**關鍵設計決策**：
- 採用統計資訊分類直接以清單呈現，未定義數據結構、型別或取值範圍
- 涵蓋足球、籃球、冰球、美足四種運動，暗示系統對走地即時數據的支援範圍

**注意事項**：
- ⚠️ 本文僅為統計項目名稱列表，未定義數據型別、計算方式與更新頻率
- ⚠️ 冰球與美足項目僅有英文名稱，缺乏中文翻譯與業務解釋
- ⚠️ 無法判斷統計資訊是第三方原始字段還是系統轉換後的內部定義


### 預測 API 規格

> Confluence 頁面 ID：47220400
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47220400)
> 摘要檔：[processed/47220400-summary.md](../../confluence/processed/47220400-summary.md)
> Confluence 最後更新：2023-04-26
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義兩個 REST API 端點：機器人賽事預測提交與賠率查詢。賠率結果包含主客隊資訊、多語系名稱、讓分（HA）與大小（OU）的賠率組合。同時說明各球種的賠率資料來源站台對應配置，可直接作為 API 呼叫規格與資料模型設計的實作參考。

**關鍵業務規則**：
- 機器人預測請求需包含 GDate、GID、LID、Mode、Spread、OddType、Odd、Point
- 賠率查詢回應中 odds 物件包含 HA 和 OU 兩大區塊，HA 的 key 為讓分數，OU 的 key 為總分線
- Mode='1X2' 時 Spread 須設定為 '1X2'（⚠️ 需人工確認此特殊設計）
- 賽事可能沒有賠率（HA 或 OU 為空物件），需設計容錯處理
- 隊伍名稱支援 11 種語系
- 賠率資料來源對應：BK→au8, SC→188bet, BS/HL/FL/ES→au8, 其他→zba

**注意事項**：
- ⚠️ OddType 取值（'H','A','O','U'）在主客場的對應關係需從其他文件確認
- ⚠️ 空 odds 物件代表未開盤或賠率未產生，調用方需有預設行為


### 預測模組資料表設計

> Confluence 頁面 ID：44664432
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44664432)
> 摘要檔：[processed/44664432-summary.md](../../confluence/processed/44664432-summary.md)
> Confluence 最後更新：2023-01-04
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義預測模組的三個資料表：單場預測表、串關預測主表及串關預測內容明細表。提供明確的資料欄位與型態，是開發預測 API、儲存預測資料及計算結果的基礎。

**關鍵設計決策**：
- 單場與串關採用不同表格設計，串關以主明細結構儲存，支援多場賽事組合
- 單場預測表結構較扁平，推測為簡化查詢與寫入

**影響範圍**：
- 所有預測相關的資料存取邏輯

**注意事項**：
- ⚠️ 串關內容表以 (GameType, GameId, PlayMode) 作為 PK，未納入 Spread，可能允許同玩法下多筆不同讓分值的預測
- ⚠️ 文件最後更新於 2023 年 1 月，需確認是否仍符合當前系統實作


### 酒田戰法圖形 ID 對照表

> Confluence 頁面 ID：44664268
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44664268)
> 摘要檔：[processed/44664268-summary.md](../../confluence/processed/44664268-summary.md)
> Confluence 最後更新：2023-02-02
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
提供酒田戰法中各類K線型態與內部圖形ID的對照表，涵蓋已完成編號 112~135 的型態及多筆未完成型態。可作為辨識技術型態的標準參照，確保不同模組使用一致的 ID。

**關鍵設計決策**：
- 型態 ID 從 112 開始連續編碼，區分多頭與空頭系列保持編號邏輯一致

**注意事項**：
- ⚠️ 「未完成」型態無對應 ID，當前版本僅覆蓋 ID 112~135
- ⚠️ 部分圖片僅以附件縮圖呈現，程式需讀取實際圖形特徵時需人工確認運算邏輯


### NBA 基礎與進階統計指標公式

> Confluence 頁面 ID：55575121
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55575121)
> 摘要檔：[processed/55575121-summary.md](../../confluence/processed/55575121-summary.md)
> Confluence 最後更新：2023-11-06
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
提供NBA基礎與進階統計指標的中英文對照與計算公式，包含有效命中率、球權佔有率、回合數等常用於機器學習預測的特徵。建立標準化的特徵計算規則，確保模型輸入的一致性和可重現性。

**關鍵設計決策**：
- 採用 basketball-reference.com 的官方計算公式作為標準
- 部分進階指標公式以圖片引用，未直接提供文字公式

**注意事項**：
- ⚠️ 公式中的圖片連結可能無法直接解析，需人工查閱
- ⚠️ 罰球製造率 (FTr) 公式僅提供 FTA/FGA，未說明是否考慮三分罰球


### ChatGPT API 內部代理使用方式

> Confluence 頁面 ID：47222177
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47222177)
> 摘要檔：[processed/47222177-summary.md](../../confluence/processed/47222177-summary.md)
> Confluence 最後更新：2024-05-24
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
提供內部搭建的 ChatGPT API 代理使用方式，封裝 OpenAI GPT-3.5-turbo 模型。說明請求格式、Response 範例、Python 呼叫範例，可直接使用此內部端點獲得 ChatGPT 回覆。

**關鍵業務規則**：
- 目前支援的模型僅為 gpt-3.5-turbo，GPT-4.0 尚未開放
- 請求須為 JSON 格式，包含 "content" 和 "model" 兩個欄位
- 一次請求不能餵入過多資料（有 token 上限）

**關鍵設計決策**：
- 建立內部代理服務集中管理 API key，降低各服務直接使用 OpenAI SDK 的複雜度
- 範例程式碼使用 requests 直接 POST，簡化依賴與部署

**注意事項**：
- ⚠️ 文件內含明文 OpenAI API key，資安風險極高，需確認金鑰是否已失效或輪換
- ⚠️ 內部 API 地址可能僅限測試/內網環境，生產環境地址需另行確認
- ⚠️ 費用資訊與模型可用性記錄於 2023 年中，現況可能已變動


### 機器學習框架與籃球模型特徵

> Confluence 頁面 ID：47221897
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47221897)
> 摘要檔：[processed/47221897-summary.md](../../confluence/processed/47221897-summary.md)
> Confluence 最後更新：2023-06-08
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
列出籃球預測模型使用的 10 項輸入特徵，包含球隊近10場勝率、各項攻守數據、得分與差分，以及對手近況。可用於確認資料欄位與資料預處理邏輯。

**關鍵設計決策**：
- 採用近10場比賽的平均數據作為特徵，而非全季數據，可能為捕捉近期狀態
- 納入對手近況作為對戰強度參考


### MLB 棒球 HA/OU 預測模型實驗

> Confluence 頁面 ID：47222757, 47222745
> 原始文件：[預測HA](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47222757) | [預測OU](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47222745)
> 摘要檔：[processed/47222757-summary.md](../../confluence/processed/47222757-summary.md) | [processed/47222745-summary.md](../../confluence/processed/47222745-summary.md)
> Confluence 最後更新：2023-08-08
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
記錄提高MLB棒球HA（讓分）和OU（大小分）預測準確率的多模型實驗結果，對比 GRU、XGBRegressor、SVR 等模型在直接預測分差和預測雙方分數兩種策略下的性能。最佳模型為 XGBRegressor（HA error 3.86）和 RandomForestRegressor（HA 準確度 0.66）。

**關鍵業務規則**：
- 訓練特徵需滿足皮爾森相關係數 > 0.3 的篩選條件
- 使用 MSE 作為損失指標
- 模型預測輸出需與盤口分數比較以決定預測方向
- 訓練欄位包含主客場的打擊與投球指標，最終訓練使用 32 個欄位（HA）或 24 個欄位（OU）

**關鍵設計決策**：
- 訓練集為 6/30 以前的 1204 筆數據，測試集為 7/1 以後的 473 筆比賽
- 使用 MSE 作為模型選擇指標，而非直接以賭盤勝率
- OU 預測中比較兩種架構後採用直接預測總分（OU error 較低且下注勝率較高）
- OU 缺失值處理最終採用「部分平均/部分取中位數（十場）」策略

**注意事項**：
- ⚠️ 文件僅包含 2023 年 7 月賽事資料，效能與特徵有效性距今已久
- ⚠️ OU 模型中發現系統性偏差：預測總分比實際大一些
- ⚠️ 部分預測結果出現極端數值（如預測分差 33），可能模型未完全收斂
- ⚠️ HA_spread、OU_spread、球頭等術語需人工確認與賭盤對應關係


### NBA-HA 模型調整實驗

> Confluence 頁面 ID：55575056
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55575056)
> 摘要檔：[processed/55575056-summary.md](../../confluence/processed/55575056-summary.md)
> Confluence 最後更新：2023-11-03
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
記錄 NBA 讓分預測模型的實驗過程，比較 XGBRegressor 與 CatBoostRegressor 在不同特徵工程手法下的表現。結果顯示 CatBoostRegressor 搭配特定加權特徵在勝負預測達 67.42%，讓分預測最高總勝率約 57.69%。

**關鍵設計決策**：
- 使用 XGBRegressor、CatBoostRegressor 進行讓分回歸預測，而非單純分類
- 特徵處理嘗試多種組合：填補今日值、值乘上 -1、前三場平均值、前三場平均值乘上 -0.9 再加 3.5
- 輸出格式包含 real_HA 與 predict_HA，用於後續比較

**注意事項**：
- ⚠️ 資料僅涵蓋 2023 年 4 月，可能已過期
- ⚠️ 未說明特徵工程的選擇理由，無法得知業務意義
- ⚠️ 部分表格內容折疊，無法確認完整數據


### NBA 比賽勝負預測實驗

> Confluence 頁面 ID：55574733
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55574733)
> 摘要檔：[processed/55574733-summary.md](../../confluence/processed/55574733-summary.md)
> Confluence 最後更新：2023-10-19
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
記錄以 CatBoost 和 RidgeCV 模型進行 NBA 比賽勝負預測的實驗。從 resultinfo 構建多層特徵表格，測試多種特徵組合。加入 HA、ELO 及主客隊差分並移除 PF、TOV 後，RidgeCV 最高總勝率達 72.73%。

**關鍵設計決策**：
- 採用 CatBoost 和 RidgeCV 兩種模型比較，RidgeCV 表現較穩健
- 特徵工程方向：球員數據→球隊級→比賽級，逐步匯總
- 嘗試加入進階 ELO 評分及主客隊差分，並刪除 PF 和 TOV 特徵

**注意事項**：
- ⚠️ 最高勝率組合僅在 121 場比賽上回測，可能有過擬合風險
- ⚠️ 內部僅記錄總勝率，未提供混淆矩陣或盈虧比
- ⚠️ 實驗結果距今已超過一年，可能不適用於當前賽季


### Crawler History Data Record

> Confluence 頁面 ID：8716869
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Crawler+History+Data+Record)
> 摘要檔：[processed/8716869-summary.md](../../confluence/processed/8716869-summary.md)
> Confluence 最後更新：2021-03-23
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
運動賽事歷史資料來源清單，記錄不同 GameType 對應的資料來源、起始日期與添加日期。可用於回溯分析或模型訓練的資料可用性判斷。

**影響範圍**：
- 歷史數據回溯分析
- 模型訓練資料來源確認

**注意事項**：
- ⚠️ 最後更新於 2021-03-23，資料來源與時間範圍可能已變更
- ⚠️ 所有 betradar 來源的 Data Start Date 均為 None，可能代表未啟用或未接入


### 加密貨幣相關策略彙整

> Confluence 頁面 ID：55582575
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55582575)
> 摘要檔：[processed/55582575-summary.md](../../confluence/processed/55582575-summary.md)
> Confluence 最後更新：2025-02-13
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
彙整加密貨幣交易相關的工具、技術線圖、投資策略、算法策略以及 AI 應用方法（強化學習、LSTM），涵蓋策略開發、回測、自動化交易到風險管理等環節。可作為對接加密貨幣數據或構建交易智能代理的參考資源。

---

## 歷史決策類


### GPT 查詢聯盟/球隊訊息取捨決策

> Confluence 頁面 ID：55579253
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55579253)
> 摘要檔：[processed/55579253-summary.md](../../confluence/processed/55579253-summary.md)
> Confluence 最後更新：2024-05-28
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**決策背景**：
定期從 DB 查詢明日足球比賽，透過 GPT API 生成繁體中文介紹。開發過程中發現 GPT 輸出常有不精確數據且 API 無連網能力，未訓練過的實體錯誤率高。

**決策結論**：
經評估後決定不刻意過濾數據，接受「看起來有模有樣」的介紹。原因：若要求不輸出數據會使內容空洞，而餵入正確資料會失去使用 GPT 的意義。

**影響**：
- 每24小時執行，生成的介紹開頭固定為中英文名稱
- 使用 opencc 進行簡轉繁處理
- 每筆聯盟或隊伍的介紹僅寫入一次
- ⚠️ GPT 產出數據準確度粗估不到 50%，使用者需認知此為近似內容


### 回測系統停利邏輯邊界問題

> Confluence 頁面 ID：34767617
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=34767617)
> 摘要檔：[processed/34767617-summary.md](../../confluence/processed/34767617-summary.md)
> Confluence 最後更新：2022-05-21
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**決策背景**：
回測系統測試發現 bugs：移動停利設為0卻仍有賣出紀錄、停利條件當天達成但賣出時間延遲至次日、當天賣出後又立即滿足買入條件是否執行。

**影響**：
- 回測買賣邏輯存在邊界情況需要釐清
- 停利判斷的時間基準與同日買賣的處理規則未明確定義
- 相同停利問題出現於多個 Hash ID，可能為系統性缺陷
- ⚠️ 停利判斷基準日與執行日尚未明確定義，需人工確認

---

## 操作手冊類

無相關文件。

---

> **整合狀態更新**
> 最後更新：2026-05-27
> 審核者：_待填寫_