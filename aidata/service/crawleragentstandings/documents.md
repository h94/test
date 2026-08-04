# crawleragentstandings — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 11:09
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB Sprint 15 - CrawlerAgent Get Data form KU/betfair/nova

> Confluence 頁面 ID：11437041
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=11437041)
> 摘要檔：[processed/11437041-summary.md](../../confluence/processed/11437041-summary.md)
> Confluence 最後更新：2020-12-30
> 摘要最後同步：2026-05-26

**摘要**：
這份文件是 TCZB Sprint 15 的專案管理操作手冊，包含從分析、開發、測試到上線的完整時程表、每日檢查清單及各階段的詳細檢查項目。對 AI 開發的幫助在於理解該團隊的開發流程規範，可作為自動化流程設計或歷史規則的參考，但無具體業務邏輯。

**關鍵業務規則**：
- 如有新增 Service 或 API 接口，必須檢查 Gateway 是否已配置
- 新增 Service 或 API 接口時，需同步修改對應的 swagger.json 文件
- 進入測試階段後需追蹤 Bug 數量是否收斂
- 測試後期需要求成員補齊分析文件
- 上線時需安排人員監控系統狀況

**注意事項**：
- ⚠️ 文件最後更新時間為 2020-12-30，描述的 Sprint 流程可能已過期，工具與流程可能已調整，需人工確認當前做法。

### Crawler Agent 90vs review

> Confluence 頁面 ID：55585734
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Crawler+Agent+90vs+review)
> 摘要檔：[processed/55585734-summary.md](../../confluence/processed/55585734-summary.md)
> Confluence 最後更新：2025-04-23
> 摘要最後同步：2026-05-27

**摘要**：
本文件是針對 Crawler Agent（90vs 資料源）的程式碼審查意見，列出多項實作改進決策。這些決策可作為開發同類爬蟲邏輯時的遵循標準。

**關鍵業務規則**：
- get_match 發生異常時，錯誤訊息（except msg）必須包含該筆資料的時間戳，以便在 KafkaTool 中定位問題資料。
- 比賽狀態碼：1 僅用於「賽後」；推遲/延期/待定等狀態應傳送 3。
- play-by-play 輸出必須是 JSON 格式字串，先以字典形式組裝（包含 "Time" 鍵），再使用 json.dumps 序列化，最終字串範例：'{"Time":"2H 73:00"}'（period 與 time 之間有一個半形空格）。
- pregame 狀態時，每節分數（quarter scores）必須為空列表 []。

**注意事項**：
- ⚠️ 文件中以圖片呈現的 get_match 檢查規則（最後一項）無詳細文字說明，具體檢查條件需人工從圖片內容確認。

### TCZB-504-[CrawlerAgent] - Bet365 爬取BK各個聯盟頁面(原盤)

> Confluence 頁面 ID：11436590
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=11436590)
> 摘要檔：[processed/11436590-summary.md](../../confluence/processed/11436590-summary.md)
> Confluence 最後更新：2020-12-07
> 摘要最後同步：2026-05-27

**摘要**：
這份文件定義了 CrawlerAgent 對 Bet365 BK（籃球）原盤數據的爬取需求，為後續走地或單場賽事數據爬取做準備。

**關鍵業務規則**：
- 爬取 Bet365 BK 各聯盟頁面原盤（FullTime BK）數據時，必須使用 Bet365API 提供的 Function Parser Data 進行資料讀取。

**注意事項**：
- ⚠️ 文件最後更新於 2020-12-07，可能已過時，API 或資料結構可能已變更，需人工確認現行做法。

### TCZB-649 [CrawlerAgent]-KU Provider BS

> Confluence 頁面 ID：15401409
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-649+%5BCrawlerAgent%5D-KU+Provider+BS)
> 摘要檔：[processed/15401409-summary.md](../../confluence/processed/15401409-summary.md)
> Confluence 最後更新：2021-03-08
> 摘要最後同步：2026-05-27

**摘要**：
文件定義 CrawlerAgent 服務新增棒球資料爬取和帳號管理兩個需求。有助於 AI 開發釐清爬蟲服務的業務邊界及帳號安全規則。

**關鍵業務規則**：
- KU 資料源需支援棒球比賽資料的爬取
- 必須實現帳號管理功能，用於防止大量帳號被禁止（BAN）

**注意事項**：
- ⚠️ 文件為 2021 年舊需求，可能已過時或變更，需確認現行 CrawlerAgent 的功能現狀

### TCZB-652 [CrawlerAgent]-Fix Pinnacle request time 流程 & TCZB-653 [CrawlerAgent]-Pinacle 部屬

> Confluence 頁面 ID：15401417
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=15401417)
> 摘要檔：[processed/15401417-summary.md](../../confluence/processed/15401417-summary.md)
> Confluence 最後更新：2021-03-08
> 摘要最後同步：2026-05-27

**摘要**：
這是一份關於 CrawlerAgent 的兩個需求：1) 部署 Pinacle 組件；2) 修正 request time 的計算順序。

**關鍵業務規則**：
- request time 的計算起始時機必須在成功拿到資料之後，而非發送請求時
- 需部署 Pinacle 到 CrawlerAgent 中（具體部署方式未詳述）

**注意事項**：
- ⚠️ 文件最後更新於 2021-03-08，距今已久，可能已有設計變更或實作方式調整

### TCZB-710 [CrawlerAgent] - KU result 0-6點抓取昨日資料

> Confluence 頁面 ID：15402272
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=15402272)
> 摘要檔：[processed/15402272-summary.md](../../confluence/processed/15402272-summary.md)
> Confluence 最後更新：2021-04-06
> 摘要最後同步：2026-05-27

**摘要**：
此文件定義 KU result 爬蟲在每日不同時段的資料抓取策略。目的是確保能正確收集跨日比賽的結果。

**關鍵業務規則**：
- KU result 爬蟲在每日 0:00-6:00 需先切換日期至昨日，抓取足球、籃球、棒球的比賽結果，然後再切換回今日抓取當日結果。
- KU result 爬蟲在每日 7:00-24:00 僅需抓取今日的足球、籃球、棒球比賽結果，無需切換日期。

**注意事項**：
- ⚠️ 文件最後更新於 2021-04-06，距今已久，可能已不再適用現行業務邏輯，需人工確認目前是否仍遵循此規則

### TCZB-780 [CrawlerAgent]-Twsl 抓中文Team、League

> Confluence 頁面 ID：18645928
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=18645928)
> 摘要檔：[processed/18645928-summary.md](../../confluence/processed/18645928-summary.md)
> Confluence 最後更新：2021-05-17
> 摘要最後同步：2026-05-27

**摘要**：
本文定義了從 TWSL 官方網站抓取中文隊名與聯盟的爬蟲需求。需呼叫 TWSL GameResult API。

**關鍵業務規則**：
- 爬取來源為 TWSL API: https://www.sportslottery.com.tw/api/services/app/GameResult/GetPagedSearchResult
- API 參數 GameType 對應運動類型：SC=441, BK=442, BS=443
- DayNum 參數可填 1/3/7/21/30/90，對應不同回朔天數
- Page 參數範圍 1-10，每種運動每日最多取得 10 頁
- 從回應 JSON 中提取聯盟欄位為 'ln'，主隊為 'htn'，客隊為 'atn'

**注意事項**：
- ⚠️ 文件最後更新於 2021-05-17，TWSL API 路徑或參數可能已變更，需確認目前仍可用

### TCZB-1210 [HouBiAgent]-火幣網資料Crawler

> Confluence 頁面 ID：24087609
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24087609)
> 摘要檔：[processed/24087609-summary.md](../../confluence/processed/24087609-summary.md)
> Confluence 最後更新：2021-11-01
> 摘要最後同步：2026-05-27

**摘要**：
這份文件定義了一個名為 HouBiAgent 的爬蟲需求，目標是從火幣網獲取虛擬貨幣的實時市場數據。

**關鍵業務規則**：
- 爬取目標：必須獲取火幣網虛擬貨幣的最新價、漲幅、24H量。
- 技術實現：必須使用 Golang 的 chromedp library 進行網頁爬取。
- 爬取對象：數據來源限定為火幣網。

**注意事項**：
- ⚠️ 過期/需人工確認：這是一份 2021 年的早期設計文件，只定義了基本方向。

### TCZB-1842 - [CrawlerAgent] - Pesa- add CK

> Confluence 頁面 ID：34767662
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-1842+-+%5BCrawlerAgent%5D+-+Pesa-+add+CK)
> 摘要檔：[processed/34767662-summary.md](../../confluence/processed/34767662-summary.md)
> Confluence 最後更新：2022-05-25
> 摘要最後同步：2026-05-27

**摘要**：
此文件定義了板球 (CK) 在 Pregame 狀態下的 HA（主客隊）玩法規則。

**關鍵業務規則**：
- 球種代碼為 'CK'，代表板球，適用於 Pregame 狀態的 HA（主客隊）玩法。
- HA 玩法對應的內部 PlayID 為 382。
- 主隊代碼為 1，客隊代碼為 2。

**注意事項**：
- ⚠️ 文件最後更新於 2022 年 5 月，可能已過期，需人工確認目前是否仍適用。

---

## 技術設計類

### TCZB-3779 [CrawlerAgentAipredict] - MLB/NHL賽事預測

> Confluence 頁面 ID：76547161
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76547161)
> 摘要檔：[processed/76547161-summary.md](../../confluence/processed/76547161-summary.md)
> Confluence 最後更新：2026-04-30
> 摘要最後同步：2026-05-27

**摘要**：
這份文件定義了 CrawlerAgentAipredict 服務擴充抓取 MLB 和 NHL 賽事預測數據的技術方案。

**關鍵設計決策**：
- 採用 page_type（網站名稱）區分不同來源的數據解析方法（sportsline、oddstrader、dimers、picksandparlays）。
- game_id 的產生方式：串接 league, team_home, team_away, game_date, game_time 五個欄位，再使用 MD5 哈希生成，確保唯一性。

**注意事項**：
- ⚠️ picksandparlays 的 game_info 格式不規律，文件中明確提到只抓取 value 的值，其他資訊的依賴性較低且不穩定，容易因站台改版而中斷。

### TCZB-587-[CrawlerAgent] - Bet365監控每場Game

> Confluence 頁面 ID：14155781
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=14155781)
> 摘要檔：[processed/14155781-summary.md](../../confluence/processed/14155781-summary.md)
> Confluence 最後更新：2021-01-18
> 摘要最後同步：2026-05-27

**摘要**：
文件描述了 Bet365 比賽單場網址組成的分析任務，目標是解析網頁代碼以提取 URL 模式。

**關鍵設計決策**：
- 決定將 Bet365 單場比賽網址組成分析結果持久化至資料庫，而非由爬蟲即時解析。

**注意事項**：
- ⚠️ 此文檔為 2021 年初期的需求描述，可能已被後續開發修改或棄用，需人工確認現有 CrawlerAgent 或相關服務的實現方式。

### TCZB-606 [CrawlerAgent]- Bwin Html Provider

> Confluence 頁面 ID：15401024
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-606+%5BCrawlerAgent%5D-+Bwin+Html+Provider)
> 摘要檔：[processed/15401024-summary.md](../../confluence/processed/15401024-summary.md)
> Confluence 最後更新：2021-02-19
> 摘要最後同步：2026-05-27

**摘要**：
本文件為 Bwin Html Provider 的技術設計草案，描述如何從 Page 表取得網址來爬取 Bwin 網頁 HTML，並送到 Kafka。

**關鍵設計決策**：
- 抓取的 HTML 直接發送至 Kafka 供後續消費，形成非同步處理管線。

**注意事項**：
- ⚠️ 文件位於「舊的Projects 1-200」下的 Sprint 17 練習，最後更新為 2021-02-19，可能已過期或不反映現行實作。

### TCZB-942 [CrawlerAgent]-優化 tg parser

> Confluence 頁面 ID：23429264
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=23429264)
> 摘要檔：[processed/23429264-summary.md](../../confluence/processed/23429264-summary.md)
> Confluence 最後更新：2021-07-19
> 摘要最後同步：2026-05-27

**摘要**：
本文件記錄 TG 爬蟲（parser）的優化計畫，主要處理登入失敗、爬取中斷、日誌與 Dashboard 傳送等穩定性問題。

**關鍵設計決策**：
- 在 Windows 10 虛擬機上掛載 Fly VPN，並使用 Selenium 進行 TG 站台資料爬取。

**注意事項**：
- ⚠️ 文件僅為初步需求描述，實作細節不足，例如具體錯誤處理流程未明確。

### TCZB-1175 [CrawlerAgent]-聯盟歷史戰績Parser

> Confluence 頁面 ID：24086897
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24086897)
> 摘要檔：[processed/24086897-summary.md](../../confluence/processed/24086897-summary.md)
> Confluence 最後更新：2021-10-25
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義 CrawlerAgent 如何從 MLB、CPBL、NBA、KBO、NPB 官網 API 取得歷史戰績並進行解析。

**關鍵設計決策**：
- 採用各聯盟提供的官方 API（而非解析 HTML），以提升資料取得穩定性與維護性。
- 定義統一的 Key Define 對照表，將不同 API 回傳的欄位標準化。

**注意事項**：
- ⚠️ 文件僅提供 MLB API 的詳細 URL 與欄位對應，CPBL、NBA、KBO、NPB 的 API 細節均未說明，需人工補齊或確認。

### TCZB-1578 [CrawlerAgent] - 永利(新HGA)的資料爬取

> Confluence 頁面 ID：32538889
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32538889)
> 摘要檔：[processed/32538889-summary.md](../../confluence/processed/32538889-summary.md)
> Confluence 最後更新：2022-03-07
> 摘要最後同步：2026-05-27

**摘要**：
記錄了因 HGA 更換新站台，需為永利爬取資料的技術方案。

**關鍵設計決策**：
- 採用 selenium 進行動態爬取，而非直接 HTTP 請求，因為目標站台為新 HGA。

**注意事項**：
- ⚠️ 文件內容極其簡略，多處空白，可能為未定稿的需求草稿。

### TCZB-2044 [CrawlerAgent] - 1xbet新增other info

> Confluence 頁面 ID：40501432
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40501432)
> 摘要檔：[processed/40501432-summary.md](../../confluence/processed/40501432-summary.md)
> Confluence 最後更新：2022-10-20
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了CrawlerAgent在解析1xbet比賽「其他資訊」（Other Info）時的字段映射規則。

**關鍵設計決策**：
- 將1xbet的特定數值key直接映射為TCZB固定字段名稱，確保數據提取的一致性。

**注意事項**：
- ⚠️ 映射規則可能因1xbet API變更而過時，需人工確認是否仍適用。

### TCZB-2214 [CrawlerAgent] - kkk selenium provider

> Confluence 頁面 ID：40503932
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-2214+%5BCrawlerAgent%5D+-+kkk+selenium+provider)
> 摘要檔：[processed/40503932-summary.md](../../confluence/processed/40503932-summary.md)
> Confluence 最後更新：2022-11-16
> 摘要最後同步：2026-05-27

**摘要**：
這份文件定義了為CrawlerAgent開發的kkk網站Selenium資料提供者設計。

**關鍵設計決策**：
- 採用四執行緒併行架構，將賽前、賽中資料抓取與健康檢查（登出、維修）分離，避免阻塞。

**注意事項**：
- ⚠️ 文件最後更新於2022-11-16，相關API端點或目標網站結構可能已變更，需確認是否仍適用。

### TCZB-2578 [CrawlerAgent] - ESPN爬取多天資料

> Confluence 頁面 ID：47219786
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47219786)
> 摘要檔：[processed/47219786-summary.md](../../confluence/processed/47219786-summary.md)
> Confluence 最後更新：2023-03-23
> 摘要最後同步：2026-05-27

**摘要**：
文件定義 ESPN 爬取 30 天內賽事資料的技術方案，包括目標球種與對應 API 端點。

**關鍵設計決策**：
- 決定改用新框架取代舊有實作，以提高可維護性。
- 新增爬取未來賽事 API 以擴展功能。

**注意事項**：
- ⚠️ ESPN API 可能已變更，端點與參數需人工驗證。

### [Crawler] CrawlerAgentMarathonbet

> Confluence 頁面 ID：55580845
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/%5BCrawler%5D+CrawlerAgentMarathonbet)
> 摘要檔：[processed/55580845-summary.md](../../confluence/processed/55580845-summary.md)
> Confluence 最後更新：2024-08-07
> 摘要最後同步：2026-05-27

**摘要**：
文档描述了 CrawlerAgentMarathonbet 针对 'asian view' 类型站点的数据抓取字段映射规则。

**關鍵設計決策**：
- 使用 provider 的 game_path 和 data 两个 key 分别解析字段。

**注意事項**：
- ⚠️ 手动变更网站显示模式的操作依赖人工，需确认自动化流程中是否已更改。

### API 參數

> Confluence 頁面 ID：10813577
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=10813577)
> 摘要檔：[processed/10813577-summary.md](../../confluence/processed/10813577-summary.md)
> Confluence 最後更新：2020-11-12
> 摘要最後同步：2026-05-27

**摘要**：
這份文件定義了從 Betsapi 取得其他語言隊伍名稱時，針對聯賽和隊伍所預期的 JSON 資料結構。

**注意事項**：
- ⚠️ 文件最後更新於 2020 年，可能已過時或不再使用

---

## 歷史決策類

### Crawler Agent 90vs review

> Confluence 頁面 ID：55585734
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Crawler+Agent+90vs+review)
> 摘要檔：[processed/55585734-summary.md](../../confluence/processed/55585734-summary.md)
> Confluence 最後更新：2025-04-23
> 摘要最後同步：2026-05-27

**決策背景**：
本文件是針對 Crawler Agent（90vs 資料源）的程式碼審查意見，列出多項實作改進決策。

**決策結論**：
這些決策可作為開發同類爬蟲邏輯時的遵循標準。

**影響**：
決策涵蓋錯誤處理、比賽狀態碼、play-by-play 輸出格式等方面，具參考價值。

### TCZB-1138 [Selenium]- ku add HalfCorrect Score and HalfCorner

> Confluence 頁面 ID：24087651
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-1138+%5BSelenium%5D-+ku+add+HalfCorrect+Score+and+HalfCorner)
> 摘要檔：[processed/24087651-summary.md](../../confluence/processed/24087651-summary.md)
> Confluence 最後更新：2021-11-01
> 摘要最後同步：2026-05-27

**決策背景**：
這篇文件記錄了一項任務：在 CrawlerAgent 中新增 HalfCorrect Score 和 HalfCorner 兩種賠率。

**決策結論**：
決策是沿用原有程式碼進行擴充，以增加更多賠率來支援分析。

**影響**：
文件內容極簡，無具體需求細節，屬於歷史任務紀錄。

---

## 操作手冊類

### TCZB Sprint 15 - CrawlerAgent Get Data form KU/betfair/nova

> Confluence 頁面 ID：11437041
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=11437041)
> 摘要檔：[processed/11437041-summary.md](../../confluence/processed/11437041-summary.md)
> Confluence 最後更新：2020-12-30
> 摘要最後同步：2026-05-26

**摘要**：
這份文件是 TCZB Sprint 15 的專案管理操作手冊，包含從分析、開發、測試到上線的完整時程表、每日檢查清單及各階段的詳細檢查項目。

**AI 開發需要注意的部分**：
- 如有新增 Service 或 API 接口，必須檢查 Gateway 是否已配置
- 進入測試階段後需追蹤 Bug 數量是否收斂
- 上線時需安排人員監控系統狀況