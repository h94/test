# crawler — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 12:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### Bet365 Crawler Flow

> Confluence 頁面 ID：7111567
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Bet365+Crawler+Flow)
> 摘要檔：[processed/7111567-summary.md](../../confluence/processed/7111567-summary.md)
> Confluence 最後更新：2020-09-23
> 摘要最後同步：2026-05-27

**摘要**：
本文件說明 Bet365 爬蟲的整體技術流程：Bet365HtmlProvider 向 PriceCenter 查詢須爬取的遊戲類型，以瀏覽器開啟對應頁面後，將 HTML 存入 NFS 檔案；Bet365CrawlerAgent 從 NFS 取得檔案，交由 CrawlerAgent 解析數據，並寫入 DB 與 RBDB。同時，Bet365HtmlProvider 會從 RBDB 取得 RB game info。這份文件幫助開發者理解爬蟲與 PriceCenter 的互動方式、資料流經 NFS 的非同步設計，以及 RBDB 的角色。

**關鍵設計決策**：
- 使用 NFS 檔案作為 Bet365HtmlProvider 與 Bet365CrawlerAgent 之間的非同步緩衝，解耦提供者與爬蟲代理
- 解析後的數據分別寫入 DB（主要資料庫）與 RBDB
- Bet365HtmlProvider 從 RBDB 獲取 RB game info，可能用於遊戲類型比對或回滾需求

**注意事項**：
- ⚠️ 文件最後更新於 2020 年 9 月，目前系統爬蟲流程可能已有變更，需與現有程式碼比對確認
- ⚠️ RBDB 的具體含義不明，可能為 Rollback DB 或特定資料庫（如 Redis），實際用途需人工釐清


### KU 爬蟲抓取清單

> Confluence 頁面 ID：18645183
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=18645183)
> 摘要檔：[processed/18645183-summary.md](../../confluence/processed/18645183-summary.md)
> Confluence 最後更新：2021-04-29
> 摘要最後同步：2026-05-27

**摘要**：
這份文件定義了 KU 爬蟲針對不同遊戲類型(GameType)與不同階段(Inplay/Pregame/Future)的抓取範圍配置。對於 AI 開發來說，這份文件提供了清晰的爬蟲調度邏輯：哪些遊戲類型需要即時(Inplay)或賽前(Pregame)爬取，哪些特定時段才需要爬取(如 BS Future 僅在 8:00~12:00 執行)，以及哪些類型明確不需要爬取(No Need)。這是實作爬蟲流程控制與任務排程的核心業務規範。

**關鍵業務規則**：
- SC Inplay：需爬取，具體爬取範圍參照文件截圖（截圖內容無法直接解析，需人工確認具體聯賽或篩選條件）
- BS Inplay：需爬取，具體爬取範圍參照文件截圖（截圖內容無法直接解析，需人工確認具體聯賽或篩選條件）
- BK Inplay：需爬取，具體爬取範圍參照文件截圖（截圖內容無法直接解析，需人工確認具體聯賽或篩選條件）
- BS Future：僅在每日 8:00 至 12:00 期間執行爬取
- SC Future：無需爬取 (No Need)
- BK Future：無需爬取 (No Need)
- Top League：爬取規則比照 SC (Soccer) 處理
- SC Pregame：所有聯賽/賽事全部都需要爬取
- BK Pregame：需爬取，具體爬取範圍參照文件截圖
- BS Pregame：需爬取，具體爬取範圍參照文件截圖

**注意事項**：
- ⚠️ 文件依賴截圖：SC Inplay、BS Inplay、BK Inplay、BK Pregame、BS Pregame 的具體爬取範圍以截圖形式存在，無法從文本直接解析，需人工查看原始文件
- ⚠️ 潛在過期風險：文件最後更新於 2021-04-29，距今已久，爬蟲配置可能已變更


### TCZB-3676 [Crawler] - CrawlerAgentBC

> Confluence 頁面 ID：55585475
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3676+%5BCrawler%5D+-+CrawlerAgentBC)
> 摘要檔：[processed/55585475-summary.md](../../confluence/processed/55585475-summary.md)
> Confluence 最後更新：2025-04-16
> 摘要最後同步：2026-05-27

**摘要**：
這篇文件定義 CrawlerAgentBC 從 oddsfeed 取得賽事與賠率資料後，應如何過濾、轉換與解讀。核心規則包括：歐洲賠率需減 1；根據玩法 IsVisible 與 IsSuspended 決定是否跳過或強制設為 -1；定義了 7 種 outcome 結果代碼對應；並詳細列出比賽資訊、隊伍、日期、狀態等欄位的 JSON 路徑與組合方式。

**關鍵業務規則**：
- 從 oddsfeed 取得的歐賠數值必須減去 1 才成為實際使用的賠率
- 每個玩法 (Market) 帶有 IsSuspended 與 IsVisible 屬性。若 IsVisible=false，則整個玩法不解析，直接跳過；若 IsVisible=true 但 IsSuspended=true，則解析該玩法，並將其賠率強制設為 -1
- 玩法結果 (outcome) 代碼：0=尚未結算，1=名次入圍，2=本金退回，3=全輸，4=全贏，5=贏一半（半贏），6=輸一半（半輸）
- league 取 game_data['league']；team_home 為 MatchMembers 中 IsHome=true 的成員，team_away 為 IsHome=false 的成員
- game_date 與 game_time 取自 game_data['Date'] 並轉換為 UTC+8，格式分別為 YYYY-MM-DD 與 HH:mm
- game_id 組合規則：'{Id}-{日期部分}-{某部分}'（範例：26994316-2025-04-16-06，後綴 '06' 意義需人工確認）
- game_status 來自 MatchStatus，進行對應轉換，文件中範例 '2' 對應站台進行中（站台 0 為未開賽）
- 賠率資料來源為 game_data['MarketsList']

**注意事項**：
- ⚠️ game_id 組合中後綴 '-06' 的意義未說明，需人工確認其來源與用途
- ⚠️ score_home、score_away、scores、playbyplay 欄位在本文件中為空白，可能需從其他 API 或後續文件補充
- ⚠️ 賠率強制設為 -1 時，下游系統如何識別此特殊值？需確認是否約定成俗或另有處理
- ⚠️ 比賽狀態的完整對應表未提供，僅知 '2' 為進行中、站台 '0' 為未開賽，其餘狀態需人工確認


### TCZB-3932 [Crawler] - nowscore賽事分析資料

> Confluence 頁面 ID：79464750
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464750)
> 摘要檔：[processed/79464750-summary.md](../../confluence/processed/79464750-summary.md)
> Confluence 最後更新：2025-09-08
> 摘要最後同步：2026-05-27

**摘要**：
此文件定義 nowscore 賽事分析資料爬蟲需要擷取的欄位與規則：近期戰績僅保留最近五場、預測隊伍欄位來自 bet_HA 並寫入 other_info、賽前簡報（足球與籃球）會寫檔保存。

**關鍵業務規則**：
- 近期戰績只抓取最近五場比賽的資料
- 預測隊伍的資料來源為 bet_HA 欄位，存入 other_info
- 賽前簡報資料區分足球與籃球，分別以不同版面擷取，並將結果寫入檔案


### TCZB-4168 [MonitorFile] - 文章監控系統調整

> Confluence 頁面 ID：79467924
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467924)
> 摘要檔：[processed/79467924-summary.md](../../confluence/processed/79467924-summary.md)
> Confluence 最後更新：2026-05-18
> 摘要最後同步：2026-05-27

**摘要**：
本文件詳細定義 Winscptool 監控系統的業務規則，涵蓋官網走地、官網文章、比分站台走地、比分站台文章及其他（PTT、Yahoo）共五類站台的監控時間、頻率、資料擷取邏輯與報警條件。說明了如何透過 procecenter_api 計算 DB 數量，以及如何根據檔案路徑和命名規則統計檔案數量。

**關鍵業務規則**：
- 官網走地資訊監控：適用 nhl.com、nfl.com、naver.com、mlb.com、nba.com、baseball.yahoo.co.jp；監控時間和頻率依站台而異
- 官網文章類監控：適用 cpbl.com、cbssports.com；每 1 小時監控一次
- 比分站台走地資訊監控：適用 nowscore、leisu、90vs、8bo、7m.com；每 10 分鐘監控一次
- 比分站台文章類監控：適用 scores24、nowscore、leisu、covers、90vs、8bo、7m.com；每 1 小時監控一次
- 其他（PTT、Yahoo）監控：每 1 小時監控一次（非活躍時段不監控，早上 6 點以後）
- 檔案數量計算：計算 WinSCP 主機 (192.168.55.20) 路徑下的昨、今、明三天檔案數量
- DB 數量計算：請求 procecenter_api 計算比賽數量

**注意事項**：
- ⚠️ 7m.com 的熱門聯盟統計基於 2025 年 6 月至 2025 年 11 月的數據，若後續聯盟熱度變化需人工重新統計
- ⚠️ CBS 賽季監控日期硬編碼在邏輯中，每年賽程調整時需人工確認並更新
- ⚠️ PTT 的 article 與 Live 文章目前無明確檔名區分，需透過 DB 查詢或解析內容來區別


### TCZB-4035 [LSports] - 足籃走地即時資訊

> Confluence 頁面 ID：79466139
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79466139)
> 摘要檔：[processed/79466139-summary.md](../../confluence/processed/79466139-summary.md)
> Confluence 最後更新：2025-11-04
> 摘要最後同步：2026-05-27

**摘要**：
定義足球與籃球走地即時資訊的寫檔時機：足球每15分鐘、籃球每節結束前及剩餘5、6分鐘時觸發寫檔。寫檔內容為指定統計指標，資料來源為 rmq_inplay 訊息中的 playbyplay 解析結果。

**關鍵業務規則**：
- 足球走地寫檔時間點：比賽開始後第 15、30、45、60、75、90 分鐘時進行寫檔
- 籃球走地寫檔時間點：每一節結束前寫檔以及比賽時間剩餘第 5 分鐘、第 6 分鐘時寫檔
- 寫檔資料來源：從 rmq_inplay 的 score_update 訊息中解析 playbyplay
- rmq_inplay 僅接收已訂閱的賽事，因此即時資訊的賽事數量會較少
- 寫檔動作在獨立 thread 中進行，避免阻塞主流程

**注意事項**：
- ⚠️ 籃球「每一節結束前寫檔」的具體觸發秒數需人工確認
- ⚠️ 籃球「剩餘第5、6分時寫檔」可能指比賽時間剩餘5分鐘和6分鐘，需人工確認
- ⚠️「寫檔」目標儲存位置未定義，需人工確認是寫入資料庫還是檔案系統


### TCZB-1107 [CrawlerAgent]-Ku selenium other gameType

> Confluence 頁面 ID：24086102
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-1107%5BCrawlerAgent%5D-Ku+selenium+other+gameType)
> 摘要檔：[processed/24086102-summary.md](../../confluence/processed/24086102-summary.md)
> Confluence 最後更新：2026-04-29
> 摘要最後同步：2026-05-27

**摘要**：
文件定義了使用 Selenium 爬取 KU 平台其他球種（網球、冰球、排球、乒乓、橄欖球、撞球、電競等）的賽事賠率規則。內容包含球種分類（main/other1/other2）、各球種在 pregame 和 inplay 狀態下的頁面 URL 配置、切換球種與玩法群組的 JavaScript 觸發方式，以及每個玩法應蒐集的具體市場。

**關鍵業務規則**：
- 球種分類：main 包含 BK(籃球)、BS(棒球)、SC(足球)；other1 包含 FI、TN(網球)、IH(冰球)、PB(撞球)；other2 包含 CHP、VL(排球)、TT(乒乓)、AF(橄欖球)、ES(電競)
- 爬取方式：EO 供應商的主遊戲全頁面與其他全遊戲頁面限 PC 爬取，且兩地各一個
- KU 前端切換球種使用 Menu.ChangeSport(this, '球種代碼', 數字)；切換玩法群組使用 Menu.ChangeKGroup(this, '數字', 群組ID)
- 每種球種在不同狀態下的玩法有對應的 '送出代號'
- 爬取清單中指定了每個球種-狀態-玩法組合應蒐集的細項市場

**注意事項**：
- ⚠️ 文件位於 Confluence 路徑「舊的Projects 1-200」中，可能為歷史專案，內容是否仍適用需人工確認
- ⚠️ 部分球種的玩法爬取市場欄位為空白，表示尚未定義或暫不爬取，開發時應注意避免空跑
- ⚠️ 表格中 '送出代號' 在早期球種為空，後期如拳擊、羽毛球、水球等有明確代號，可能後續有規則擴充


---

## 技術設計類

### TCZB-3645 [Crawler] - beebet

> Confluence 頁面 ID：55583277
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3645+%5BCrawler%5D+-+beebet)
> 摘要檔：[processed/55583277-summary.md](../../confluence/processed/55583277-summary.md)
> Confluence 最後更新：2025-03-19
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義 beebet 網站爬蟲的完整資料獲取流程：透過三組 WebSocket 端點依序取得聯盟列表、比賽清單、比賽詳情與賠率資料。文件詳列每個 WebSocket 的連線 URL、訂閱訊息格式（含 STOMP 協定）、以及各步驟之間的資料依賴關係。賠率解析部分提供完整的 odd_setting 配置，定義各球種的盤口代號與輸出格式對應。

**關鍵設計決策**：
- 採用三層 WebSocket 架構分離關注點：eventlivedoc、eventmap、marketlivedoc，各自獨立端點
- 使用 STOMP over WebSocket 協定，所有連線須先發送 CONNECT 訊框，否則連線失敗
- 資料獲取順序強制為：league_id → game_id → 比賽詳情 → 賠率代號 → 賠率
- 賠率系統採用代號映射機制：每個球種對應一組盤口代號，盤口代號需從 eventmarketsmap 動態取得後再查詢實際賠率
- league 名稱需額外透過 competitions/{league_id} 請求取得，與比賽資訊分開獲取
- 比賽時間 anticipated.startTime 需轉換為台北時區

**注意事項**：
- ⚠️ eventmap 訂閱的 game_type 參數文件未列舉全部可能值，實作時需人工確認或從原始網站逆向
- ⚠️ 賠率訂閱時 count 參數需遞增否則無法取得資料
- ⚠️ odd_setting 中的部分註解格式不一致，這些代號的輸出轉換規則需對照 zbaparser 現有邏輯確認
- ⚠️ WebSocket URL 中的 token 可能為 session-based 或定期輪替，需確認是否需要動態取得
- ⚠️ marketlivedoc 端點的文件路徑 /288/ 可能不是固定值


### TCZB-3646 [Crawler] - Lsports Provider/ parser

> Confluence 頁面 ID：55584543
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55584543)
> 摘要檔：[processed/55584543-summary.md](../../confluence/processed/55584543-summary.md)
> Confluence 最後更新：2025-11-03
> 摘要最後同步：2026-05-27

**摘要**：
本文定義了從Lsports獲取比賽、賠率、比分及動畫數據的爬蟲設計。透過快照API與RabbitMQ雙通道接收數據，以緩存補全RMQ訊息缺失的球種/隊伍資訊，再統一送入Kafka。涵蓋事件統計結構、多語系拆分發送、StatScore動畫ID查詢、核心參數限制等具體實現約定。

**關鍵業務規則**：
- 後台Data Limit應設為2（最久接收後天比賽），嚴禁設為0；設為0代表不限制，會接收全部數據導致爬蟲Provider崩潰
- 賠率更新與比分更新的RMQ訊息僅含game_id與更新內容，需從本地快取補充球種、隊伍名稱後再發送Kafka
- RabbitMQ的heartbeat訊息必須過濾，不送入Kafka
- 快照API在Provider啟動時即刻執行一次，之後每隔10分鐘以球種為維度重新調用並推入Kafka
- 比賽開始時間為UTC+0，需要轉換時區；若時間字串末尾帶有'Z'字符，須先去除
- 多語系處理：取得快照後，將league id與participantIds調用翻譯API可一次請求所有語系，然後按語系拆分成多筆match送往namemap_service
- StatScore動畫資訊僅在賽前與賽中階段獲取：處理足球快照時，檢查快取中是否已有該比賽的動畫ID，若無才調用StatScore API查詢

**關鍵設計決策**：
- 採用兩條RabbitMQ連接分別處理賽前與賽中消息，以隔離不同生命週期的數據流
- 建立比賽資訊快取（球種、隊伍等），彌補RMQ推送訊息僅含game_id而無關聯數據的缺陷
- 多語系一次性請求全部語言，再由Provider拆分為多個match物件發送
- 動畫ID的查詢與快取在足球快照流程中批次處理，避免頻繁呼叫StatScore API

**注意事項**：
- ⚠️ Data Limit 設定為0將導致所有歷史與未來資料湧入，使Provider資源耗盡，文件強調絕對不可設定為0
- ⚠️ StartDate 字串可能帶有'Z'尾綴，需用replace移除；時間為UTC需轉為目標時區


### TCZB-3677 [Crawler] - BCProviderV2

> Confluence 頁面 ID：55585293
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3677+%5BCrawler%5D+-+BCProviderV2)
> 摘要檔：[processed/55585293-summary.md](../../confluence/processed/55585293-summary.md)
> Confluence 最後更新：2025-04-24
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了 BCProviderV2 爬蟲如何從 BetConstruct (BC) 取得賠率資料。包含 API 端點（Token 獲取、Snapshots、細節查詢、語言翻譯）、帳號資訊、支援球種及其 ID、以及呼叫限制。流程上先取得 Token，再週期性取得完整快照（每三小時），透過 RabbitMQ 接收即時更新，並每隔八分鐘重送快取內所有比賽至 Kafka。

**關鍵業務規則**：
- Token 取得 API 24 小時內不應請求超過 1 次（文件建議）
- DataSnapshot API 24 小時內總請求次數不應超過 10 次（文件建議）
- 每次快照後需對 game_id 與 league_id 做快取，因應次數限制，每三小時呼叫一次快照 API
- 需建立兩個 RabbitMQ 連線，分別訂閱 P18767618_live（inplay）與 P18767618_prematch（pregame）的更新訊息
- RabbitMQ 收到的 callback message 需直接轉送上 Kafka
- 每隔 8 分鐘需將快取中所有比賽資料重新發送至 Kafka，以確保消費端有最新狀態
- MatchById 查詢時若 IncludeMatchStats=true 可取得比賽比分，通常用於賽中及結束的比賽

**關鍵設計決策**：
- 採用先呼叫快照再以 RabbitMQ 訂閱更新的混合模式，平衡即時性與 API 呼叫次數限制
- 使用三小時快照週期符合 API 次數上限，同時維持資料新鮮度
- 採用八分鐘重送快取機制，作為即時更新的補充，確保下游服務資料一致性

**注意事項**：
- ⚠️ 文件中含有明文帳號密碼，後續實作建議改為環境變數或密鑰管理服務
- ⚠️ API 呼叫次數限制源自 BC 官方文件，但文中備註「限制說不應該」等語氣，可能為建議值而非硬性限制
- ⚠️ 球種列表中的備註（如 MMA、Boxing、Sumo 等對應同一 MA 代號）可能導致後續資料映射混淆


### TCZB-3703 [Crawler] - CrawlerAgent90vs

> Confluence 頁面 ID：55585507
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3703+%5BCrawler%5D+-+CrawlerAgent90vs)
> 摘要檔：[processed/55585507-summary.md](../../confluence/processed/55585507-summary.md)
> Confluence 最後更新：2025-04-21
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了 CrawlerAgent90vs 如何從 BK (gb8888.net) 和 SC (bf.90vs.com) 兩個來源獲取體育賽事資料。對 AI 開發而言，此文件提供了完整的 HTML 解析映射表：包含聯賽名稱、主客隊、比賽日期時間、賽事ID、比分及比賽狀態等欄位的具體 CSS/XPath 定位規則。特別重要的是文件明確定義了比賽狀態的判斷邏輯與輸出代碼對照，以及 BK 多節得分與 SC 半場得分的結構化輸出格式。

**關鍵業務規則**：
- 比賽狀態(page status)必須根據provider的page_type與頁面內容綜合判斷，不可僅依靠單一條件。Inplay: 0, Result: 1, Pregame: 2, 延期/待定: 3, 取消: 4
- BK(籃球)賽事狀態判斷：result和pregame可直接由page_type判斷；inplay中若出現「完場」則應歸為result；inplay和pregame的區分標誌是是否有class='gq'
- SC(足球)賽事狀態判斷：result和pregame可直接由page_type判斷；inplay中若td.st內容為「完」則為result；td.st無內容則為pregame；其餘為inplay
- SC(足球)下半場分數不能直接獲取，必須由「總分 - 半場分數」計算得出
- BK(籃球)的單節分數輸出為二維陣列格式 [[主隊,客隊],[主隊,客隊],...]，若某節無數據則補 [0,0]

**關鍵設計決策**：
- 根據provider的page_type進行初步的狀態分流，再根據HTML特徵進行二次判斷，這是因為BK和SC兩個來源的HTML結構不同，無法用統一的規則解析
- 選擇直接從tr id或HTML屬性中擷取原始的game id，而非自行生成，以確保與來源系統的一致性
- SC(足球)只提供半場比分和總分，設計決策為「下半場分數 = 總分 - 半場分數」進行計算

**注意事項**：
- ⚠️ 文件中的遊戲日期(game date)格式為 'MM/dd' 或 'yyyy年MM月dd日'，需人工確認是否需統一轉換為標準日期格式後再輸出
- ⚠️ SC的總比分可能存在於同一頁面的不同位置，需確認score home/away的定位規則是最終版
- ⚠️ 文件截圖中的CSS class名稱可能隨著網站改版而變更


### TCZB-3706 [MergeSite] - 隊伍解併API

> Confluence 頁面 ID：55585540
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55585540)
> 摘要檔：[processed/55585540-summary.md](../../confluence/processed/55585540-summary.md)
> Confluence 最後更新：2025-04-29
> 摘要最後同步：2026-05-27

**摘要**：
定義隊伍解併功能的 API 規格：MergeSite 提供 PUT /api/teams/split/{gameType} 接收請求，內部調用 PriceCenterService 的 PUT /pricecenter/api/split/teams/{gameType} 執行拆分。請求參數包含 TID 與 SiteTeams 陣列。

**關鍵業務規則**：
- 請求參數 TID 不得為空
- SiteTeams 陣列中的每個物件，其 Site、SiteLID、SiteTID 皆不得為空
- PriceCenter 解併的 SiteTeam 數量不超過 6 個（⚠️ 文件中標示為「设想」，可能非最終規則，需人工確認）

**關鍵設計決策**：
- 採用兩層 API 設計：合併站台服務 (MergeSite) 作為入口，轉調價格中心服務 (PriceCenterService) 執行實際隊伍拆分

**注意事項**：
- 「Pricecenter解併不超過6個的SiteTeam」寫在設想段落，尚未標注為正式規則，開發時需確認此限制是否已定案
- API 路徑中的 {gameType} 參數具體取值與含義未進一步說明，需人工確認


### TCZB-2262 [Crawler] StakeProvider

> Confluence 頁面 ID：76546621
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-2262+%5BCrawler%5D+StakeProvider)
> 摘要檔：[processed/76546621-summary.md](../../confluence/processed/76546621-summary.md)
> Confluence 最後更新：2025-05-27
> 摘要最後同步：2026-05-27

**摘要**：
本文件說明 StakeProvider 爬蟲如何從 Stake.com 擷取體育賽事與賠率資料。核心技術包含使用 GraphQL API 取得聯盟所有比賽及單場比賽的多玩法；透過 undetected_chromedriver 繞過 Cloudflare 5 秒盾，再以 curl_cffi 模擬 TLS 指紋處理不同 IP 的防護機制；並透過 x-language Header 設定多語系。

**關鍵設計決策**：
- GraphQL 查詢字串因不同用途而異，故將各個 query 字串寫死在程式碼中，呼叫時動態帶入變數
- 單場比賽資料一次請求即可取得多個 groups (玩法組)，減少 API 呼叫次數
- Cloudflare bypass 區分兩類 IP：有 5 秒盾的 IP 用 undetected_chromedriver 取得 cf_clearance 與 User-Agent 後，透過 curl_cffi.Session 後續請求；無 5 秒盾但會檢查 TLS 指紋的 IP 則直接以 curl_cffi 模擬指紋
- 球種僅抓取常用項目，因站台防護嚴格，減少不必要的請求以降低風險

**注意事項**：
- ⚠️ 文件提及「站台擋的蠻兇的」，可能需要人工確認現行防護機制是否已變更
- ⚠️ 對某些 IP 不認 cf_clearance 的情境，需依賴 curl_cffi 模擬 TLS 指紋，實作時須確保指紋庫更新


### TCZB-3759 [CrawlerAgentStake] - stake Parser

> Confluence 頁面 ID：76546935
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3759+%5BCrawlerAgentStake%5D+-+stake+Parser)
> 摘要檔：[processed/76546935-summary.md](../../confluence/processed/76546935-summary.md)
> Confluence 最後更新：2025-06-11
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了 Stake 資料源（game_data）的解析映射，指定比賽資訊欄位在 JSON 中的路徑與取值方式。特別注意籃球需額外呼叫 API 取得特殊玩法，且賠率路徑為 'group' 而非 'groups'。

**關鍵設計決策**：
- 採用 JSON 路徑直接映射方式提取欄位，而非結構化模型，以快速對應 Stake 的原始資料格式
- 賠率存於 game_data['group']（非 groups），可能是 Stake API 設計如此，Parser 需特別處理此命名
- 針對籃球比賽，需額外呼叫另一個 API 以取得 3 分球、助攻等附加玩法資料
- game_id 從 slug 欄位提取，僅取數字部分，因 slug 為混合格式

**注意事項**：
- ⚠️ game_status 欄位定義模糊：'1' 表明 ended 但註解為「賽前結束或者賽果」，可能包含兩種情境，需釐清邏輯
- ⚠️ 籃球玩法需額外呼叫另一 API，此依賴未詳細說明 API 端點及呼叫時機，可能影響系統整合


### TCZB-3760 [Crawler] - BetCity Provider

> Confluence 頁面 ID：76546891
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3760+%5BCrawler%5D+-+BetCity+Provider)
> 摘要檔：[processed/76546891-summary.md](../../confluence/processed/76546891-summary.md)
> Confluence 最後更新：2025-06-24
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義 BetCity Provider 的爬蟲整合細節，包括 inplay、pregame、賽前主要/額外玩法及賽果等 API 端點、HTTP 方法與參數格式。需先透過 Selenium 取得 cookies 才能調用 API，其時效長，每次執行僅需取得一次。

**關鍵設計決策**：
- 使用 Selenium 獲取 cookies 作為 API 授權憑證，因其時效長，設計為每次爬取工作階段只獲取一次
- 賽前主要玩法 API 採用 POST 請求，payload 格式為 "id_ev={game_id}"，僅支援單場查詢
- 賽前額外玩法 API 使用 GET 請求，參數 ids 直接帶入 game_id
- pregame API 以 GET 方式呼叫，需傳入日期參數 date，格式為 yyyy-MM-dd
- 賽果 API 同樣使用 GET，日期參數格式同 pregame


### TCZB-3803 [AI預測爬蟲] - MLB、NPB、CPBL AI預測分析資料爬取

> Confluence 頁面 ID：79462667
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79462667)
> 摘要檔：[processed/79462667-summary.md](../../confluence/processed/79462667-summary.md)
> Confluence 最後更新：2025-08-18
> 摘要最後同步：2026-05-27

**摘要**：
本文档详细描述了从Forebet、Sportspunter、Scores24三个站点抓取MLB、NPB、CPBL比赛AI预测数据的技术方案。包含每个站点的爬取入口、反爬策略、HTML/API解析方式以及最终统一的Match数据结构和存储路径。

**關鍵業務規則**：
- Forebet只抓赛前（game_status='1'）和赛后（game_status='2'）的比赛，赛中不处理
- Sportspunter不提供实时比分，score_home/away固定为'0'，scores为空数组，game_status固定为'2'
- Sportspunter和Scores24的game_id生成规则：将联盟、主队、客队拼接后使用MD5哈希取前10位，再拼接比赛日期
- Scores24存储到WinSCP主机时，需剔除文章中'popular bonuses'和'watch the broadcast'区域
- 所有联盟的game_type固定为'BS'（棒球）
- Forebet的OtherInfo中，若为赛前，hits和err字段送空数组；赛后才填充比赛安打/失误数

**關鍵設計決策**：
- 使用undetected_chromedriver获取cf_clearance cookie，配合cloudscraper绕过Forebet的Cloudflare防护
- Sportspunter通过httpx直接获取HTML，并利用分步匹配提取比赛列表
- Scores24采用GraphQL API获取比赛清单
- 处理队伍名称显示不全：可能需要设计namemap映射完整队伍名
- Forebet抓取逻辑独立为ForebetProvider，单独部署，降低耦合性

**注意事項**：
- ⚠️ 文档末尾'待處理'中注明：Scores24的pregame与result的GraphQL query相同但縮減未確認
- ⚠️ Scores24的赛事信息目前尚未抓取，score_home/away为'0'，game_status未实际解析
- ⚠️ Forebet Provider的部署位址描述存在笔误：'PRD3: "SRV132": "PRD3"'
- ⚠️ CPBL存在两个Scores24来源，一个放较近比赛，一个放较远比赛


### TCZB-3827 [CrawlerAgentNaver] - NaverParser

> Confluence 頁面 ID：79463033
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3827+%5BCrawlerAgentNaver%5D+-+NaverParser)
> 摘要檔：[processed/79463033-summary.md](../../confluence/processed/79463033-summary.md)
> Confluence 最後更新：2025-07-16
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義 CrawlerAgentNaver 從 Naver 的 game_data JSON 中提取比賽資料的欄位對應，包含聯賽、主客隊、比賽時間、賽事 ID、狀態、比分及比賽進展等。針對網球、籃球、棒球、足球等不同球種，分別說明了隊伍名稱、比分明細的擷取規則。

**關鍵業務規則**：
- league 欄位取自 game_data['categoryName']
- team_home 與 team_away 欄位：網球使用 participant 欄位；其他球種優先取 homeTeamFullName/awayTeamFullName，若無則取 homeTeamName/awayTeamName
- game_date 取自 game_data['gameDateTime'] 的日期部分，時區為韓國時區
- game_time 取自同一字串的時間部分，格式 HH:MM
- game_id 取自 game_data['gameId']
- game_status 取自 game_data['statusCode']，READY 或 READY=賽前，STARTED=賽中，ENDED 或 RESULT=賽後
- scores 欄位依球種不同結構：BK 取 homeTeamScoreByQuarter/awayTeamScoreByQuarter，BS 取 homeTeamScoreByInning/awayTeamScoreByInning，TN 取 scoreDetail，VB 取 currentScoreBySet；足球無此欄位
- playbyplay 取自 game_data['statusInfo']


### TCZB-3835 [NaverSport] - KBO賽事資訊

> Confluence 頁面 ID：79463163
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463163)
> 摘要檔：[processed/79463163-summary.md](../../confluence/processed/79463163-summary.md)
> Confluence 最後更新：2025-07-31
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了從 Naver Sport 取得 KBO 賽事資訊的技術實作細節。賽前戰力分析與預測資料需以指定 key 寫入 otherinfo 欄位；賽中直播事件由 provider 合併 1~9 局後單筆送入 Kafka，最後由 parser 轉為 Markdown 格式寫檔。

**關鍵業務規則**：
- 戰力分析資料寫入 otherinfo 時須使用固定 key：win/lose（勝敗）、base（局數）、defense（平均自責分）、whip（WHIP）、vs_home 或 vs_away（對戰成績）
- 投球類型資料需存放於 currentPitKindStats，並按 mapping：FAST→fastball、SLID→slider、FORK→forkball、CUTT→cutter、TWOS→two seam fastball、CURV→curveball、CHUP→changeup
- 關鍵球員統計使用固定 key：hra（打擊率）、hit（安打）、hr（全壘打）、rbi（打點）
- 預測資料從 API 取得 selectionCount，直接以 (某隊人數 / 總人數) 計算比例後寫入 otherinfo
- 直播事件中，若 relay 物件的 text 為空字串，代表為網站小標題，必須跳過不處理
- 直播事件 text 內以 `<br/>` 分隔，輸出時須轉換為無序清單（Markdown bullet list）
- 直播事件須由 provider 請求全部 1~9 局，將 2~9 局的 textrelays 集合附加至第 1 局清單後，才以單筆 Kafka 訊息送出
- relay_data 需額外加入 relay_type key，用來區分 inning（局事件）與 HL（highlight）

**關鍵設計決策**：
- 選擇將 2~9 局事件合併至第 1 局後一次性發送 Kafka，是為了簡化下游消費邏輯
- 最終輸出採用 Markdown 格式，推測是便於前端直接渲染或存入內容管理系統

**注意事項**：
- ⚠️ 文件未說明 otherinfo 的最終儲存結構，需人工確認是否對應到某個 DB 欄位或檔案
- ⚠️ 預測 API 的 gameId 格式需確認與其他系統的比賽 ID 對應規則
- ⚠️ 文件僅提供單一 highlight 範例，但 highlight API 據稱結構相同，仍需驗證


### TCZB-3861 [Crawler] - CBSSport/CPBL官網 爬蟲

> Confluence 頁面 ID：79463618
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463618)
> 摘要檔：[processed/79463618-summary.md](../../confluence/processed/79463618-summary.md)
> Confluence 最後更新：2025-10-01
> 摘要最後同步：2026-05-27

**摘要**：
本文件記錄了針對 CPBL 官網和 CBSSport 網站的新聞與數據爬蟲技術設計。詳細說明了如何透過逆向工程 API 與 HTML 解析來獲取結構化資料，並定義了標準化的 JSON 輸出格式與 DB 儲存規格。

**關鍵設計決策**：
- CPBL 團隊成績需先請求靜態頁面以獲取動態的 __RequestVerificationToken，再以此 Token 請求 API，這是網站的反爬蟲機制
- CBSProvider 負責從網站原始 HTML 解析出所有資訊，並將初步解析結果推送到 Kafka，供 CrawlerAgentCBS 訂閱並進行二次處理
- CPBL 的比賽資料透過兩個 API 獲取：先用固定 payload 獲取全年比賽清單，再根據篩選條件請求單場比賽的即時數據 API
- CBSSport 的資料抓取設計為整合式爬蟲，透過統一的 CBSProvider 處理多個聯賽（MLB, NBA, WNBA, NFL, NHL）
- CPBL 官方網站的回應在 Docker 環境中為 Brotli 壓縮格式，需要使用 brotlicffi.decompress 進行解壓
- 投手資訊的獲取被拆分為多個請求：CBSSport 中分為基本資料、本季成績、逐場成績三個獨立 API

**注意事項**：
- ⚠️ CrawlerAgentCBS 針對 NFL 和 NHL 的賽前報解析正則表達式，文件中明確標注為「待確認」
- ⚠️ 文件中提及過往 CBSProvider 及 CrawlerAgentCBS 的開發文件目前未找到，部分背景資訊可能缺失
- ⚠️ SRV113 環境出現異常，已將原先部署於該環境的服務遷移至 SRV102，部署位置資訊已有變動


### TCZB-3863 [Crawler] - ESPN/COVERS 爬蟲

> Confluence 頁面 ID：79463611
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463611)
> 摘要檔：[processed/79463611-summary.md](../../confluence/processed/79463611-summary.md)
> Confluence 最後更新：2025-08-12
> 摘要最後同步：2026-05-27

**摘要**：
文件詳述了針對 ESPN 和 Covers 網站設計的爬蟲流程，用於抓取 MLB 比賽的先發投手、預測及戰前分析。包括定時爬取的觸發機制、HTML 解析策略、異常狀況判斷，以及最終資料的儲存位置與欄位對應。

**關鍵設計決策**：
- 定時爬取頻率設為約 20 分鐘一次，平衡資料即時性與系統負載
- Covers 戰前分析頁面：若 HTML 含「Check back shortly for a full preview.」則跳過該次爬取
- Covers 先發投手：只擷取 <section id='matchupHub-last5-section'> 區塊，減少不必要的 HTML 解析開銷
- Covers 投手資料：若顯示「starter TBD」表示先發投手尚未公布，則略過該場次
- ESPN 頁面：從 HTML 內的 JavaScript 變數 window['__espnfitt__'] 提取 JSON
- Covers 戰前分析完成後，將 game id 加入已完成列表，避免重複抓取


### TCZB-3887 [8bo] - 賽事分析資訊

> Confluence 頁面 ID：79464207
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464207)
> 摘要檔：[processed/79464207-summary.md](../../confluence/processed/79464207-summary.md)
> Confluence 最後更新：2025-08-25
> 摘要最後同步：2026-05-27

**摘要**：
這份文件詳述從8bo足球數據網站擷取賽事分析、情報與預測資料的技術流程。內容包含爬蟲請求發起、HTML區塊切片規則、Kafka傳遞資料以及後續解析方式，特別定義了情報頁如何轉換為Markdown格式。

**關鍵業務規則**：
- 情報頁必須提取主隊有利情報、主隊不利情報、客隊有利情報、客隊不利情報及中立情報，並以特定Markdown格式輸出，即使該分類無任何情報內容，標題也必須保留
- 預測頁的請求必須附帶GET參數 code=302，否則HTML中不會包含 __dataAiClientParam 這個JS變數
- 分析頁近期賽事的HTML區塊切片範圍為：從 class 包含 'z8boxs z8mini2sub z9recent2match' 的 div 開始
- 情報頁的HTML區塊切片範圍為：從 class 包含 'z8boxs z9info2analy' 的 div 開始，到 class 包含 'z8boxs z9info2total' 的 div 之前
- 單場賽事HTML解析規則：主隊資訊位於 div.z8home，客隊資訊位於 div.z8away

**關鍵設計決策**：
- 採用 provider 先抓取賽前比賽ID，再經由 queue 將ID傳遞給 info service，實現異步解耦的爬取流程
- 預測頁選擇直接以正則表達式提取JS變數 __dataAiClientParam，而非解析HTML
- 分析頁與情報頁採用「切片後傳輸」的策略，只擷取相關HTML區塊送至 Kafka
- 所有擷取的原始資料均透過 Kafka 傳遞，使得爬蟲、解析與寫入等後續處理可獨立伸縮

**注意事項**：
- ⚠️ 預測頁抓取時務必加上參數 code=302，否則無法獲得預測數據
- ⚠️ 分析頁的結束標記為HTML註解，若8bo網站調整頁面結構，可能導致切片範圍失效
- ⚠️ 情報頁的空資訊規則需在 parser 中正確處理，避免誤判為缺少數據而丟棄整個區塊


### TCZB-3845 [Crawler] - WNBA官網爬蟲

> Confluence 頁面 ID：79464606
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464606)
> 摘要檔：[processed/79464606-summary.md](../../confluence/processed/79464606-summary.md)
> Confluence 最後更新：2025-09-11
> 摘要最後同步：2026-05-27

**摘要**：
本文件描述 WNBA 官網爬蟲的技術實作，說明使用兩個 API 取得比賽數據，並規範各自的呼叫頻率與用途。文中詳細列出各資料欄位在 JSON 回應中的對應路徑或解析方式。

**關鍵業務規則**：
- 全年賽程 API 每10分鐘呼叫一次，不回解析走地比賽（因 PBP 延遲）
- 今日賽程 API 每10秒呼叫一次，用於走地比賽解析
- 聯盟 (league) 固定為 'Women's National Basketball Association'，直接寫死
- 主隊／客隊名稱由 teamName 與 teamCity 兩個欄位拼接而成
- game_status 對應：1 = 賽前，2 = 走地，3 = 賽果
- 節次得分 (scores) 僅存在於今日 API 的 periods 鍵中；全年 API 無此資料，須另行請求單場 HTML 頁面並用正則表達式解析

**關鍵設計決策**：
- 走地數據不使用全年 API 而改用今日 API，原因是前者 PBP 會延遲，故需更高頻率（10 秒）的今日 API
- 全年 API 即使比賽結束也不提供 periods 資料，因此設計獨立邏輯：針對單場賽事頁面做 HTML 正則解析以取得節次得分

**注意事項**：
- ⚠️ 文件最後更新於 2025-09-11，可能仍為現行實作；但若 WNBA 官網 API 變動，部分欄位路徑可能失效
- ⚠️ scores 欄位依賴單場 HTML 正則解析，容易因頁面改版而中斷


### TCZB-3922 [AI預測] - SoccerVital 足球預測爬蟲

> Confluence 頁面 ID：79464584
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464584)
> 摘要檔：[processed/79464584-summary.md](../../confluence/processed/79464584-summary.md)
> Confluence 最後更新：2025-11-21
> 摘要最後同步：2026-05-27

**摘要**：
本文件為一個新足球預測資料源的爬蟲技術設計，說明了如何從SoccerVital站台擷取賽事預測、隊伍近況、信心指標等數據。文件詳細提供了抓取流程、HTML解析的正規表達式邏輯，以及最終輸出至系統的標準化資料格式。

**關鍵業務規則**：
- 比賽日期時間以站台時間為準，產出時必須額外增加7小時，才是台北時間
- 比賽狀態映射規則：當原始狀態為 'FT' 或 'AET' 時視為已結束，game_status 設為 '1'；其餘狀態視為未開始或進行中，game_status 設為 '2'
- 站台給出的信心指標數值範圍為 1 到 10
- 預測的大小球盤口固定為 2.5
- 近5場比賽結果的順序規則：陣列中最左邊的為最近的一場比賽
- 賽事唯一識別碼的生成規則：將聯盟、主隊、客隊名稱結合，使用MD5產生雜湊值取前10位，並在尾端加上比賽日期
- 資料抓取的時間範圍：從當前日期往前2天到往後2天，共計5天的賽事資料
- 即時比分資訊是透過另一個API（loadresultnew.php）請求獲得

**關鍵設計決策**：
- 採用兩階段請求取得完整資訊：先用 Regex 解析賽事清單頁面獲取單場URL，請求單場頁面後，再從中解析 static_id，進一步請求 loadresultnew.php 取得即時比分
- playbyplay 的格式統一處理：HT轉換為 Half Time；數字若<=45歸為上半場（1H），>45歸為下半場（2H），並統一補上 ':00' 秒數
- game_id 的設計選擇：因為外部站台可能沒有全局唯一的賽事ID，故採用聯賽加隊伍名稱的組合雜湊並附加日期的方式
- 站台特有數據全部封裝在 send_data 結構的 OtherInfo 欄位中

**注意事項**：
- ⚠️ 部署位置為專案衝刺時期的規劃，可能隨著後續維運有所變動
- ⚠️ 文件提供的程式碼片段中存在筆誤或未定義變數的可能
- ⚠️ game_id 生成中使用 MD5 前10位並附加日期的做法，需人工確認碰撞機率是否在業務上可接受


### TCZB-3948 [Crawler] - 7M 賽事分析

> Confluence 頁面 ID：79464940
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464940)
> 摘要檔：[processed/79464940-summary.md](../../confluence/processed/79464940-summary.md)
> Confluence 最後更新：2025-09-22
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義從 7M 網站爬取賽事情報的實作規格：透過帶時間戳的 JS 陣列 API 取得情報清單與各場次詳細資料，解析欄位對應有利/不利情報、近五場戰績與戰前分析，並以 Markdown 輸出。

**關鍵設計決策**：
- 選擇以 JSONP 形式的 JS 陣列 API 取代 HTML 解析，提高資料提取穩定性
- API 呼叫強制帶入當前 Unix 時間戳（毫秒）作為查詢參數，避免伺服器端緩存
- 有利/不利情報以 HomeAway（0:主隊,1:客隊）與 UpDown（0:有利,1:不利,2:中立）欄位分類，寫入固定 Markdown 階層
- 近五場紀錄無直接勝負標記，需透過比對主隊/客隊 ID 與分數判斷勝平負
- 戰前分析中的推薦結果寫入 otherinfo 而非分析正文

**注意事項**：
- ⚠️ API 端點格式與時間戳參數為 2025-09 觀察結果，若網站改版可能失效
- ⚠️ 近五場勝負判斷規則依賴隊伍 ID 與分數對照，需確保日後資料結構不變
- ⚠️ 情報列表 API 回傳 JS 陣列，非標準 JSON，需自行處理開頭的變數賦值與分號


### TCZB-3949 [NapoleonProvider] - Napoleon賠率站台爬取

> Confluence 頁面 ID：79465112
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465112)
> 摘要檔：[processed/79465112-summary.md](../../confluence/processed/79465112-summary.md)
> Confluence 最後更新：2025-10-02
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了 Napoleon 賠率站台的資料爬取與解析規格。說明了如何透過 Superbet API 取得賽前/賽中/賽後資料及單場詳細賠率，並提供完整的 JSON 欄位對應規則，以及 Napoleon 內部 market_id 與 Panda 標準玩法的轉換對照表。

**關鍵業務規則**：
- 比賽時間使用 unix_date_millis 時間戳，轉換後即為台灣時間，不需再換算時區
- 主客隊名稱從 fixture.event_name 以 '‧' 分隔，前者為主隊，後者為客隊
- 聯盟名稱由「國家名 + 聯盟名」組成，由於比賽資料僅提供代號，需由 provider 端從其他 API 取得名稱後傳入
- 賽後單場詳細結果的 game_id 不可一次塞入過多，因玩法資料量大，可能導致訊息過大無法傳送到 Kafka
- 足球的黃牌、紅牌、角球數據僅存在於對應的 inplay_stats 欄位中，其他球種無此資料
- 賠率玩法轉換時需處理 template 變數，例如 {quarter}、{period}、{game}、{map}、{inn}，這些變數需根據實際資料動態替換

**關鍵設計決策**：
- 採用 Superbet API 而非直接爬取 Napoleon 前端頁面，透過 API 端點區分賽前、賽中、賽後及單場詳細資料
- 賠率刷新時使用 bulk API 一次帶入多個 game_id 取得單場詳細玩法與賠率，但一次能帶入的數量上限需實際測試
- 賽果玩法結果採用 Panda 格式輸出，直接從 API 回應的 results 欄位取得

**注意事項**：
- ⚠️ 單場 API 一次可帶入的 game_id 數量上限文件中標注「要再測試」，需人工確認後才能決定批量請求策略
- ⚠️ 聯盟名稱需由 provider 端從其他 API 取得後傳入 parser，若 provider 未正確處理，parser 收到的 league 欄位可能為空或錯誤
- ⚠️ 球種對照表中 Cycling (sport_id=25) 標注為「可能計畫會做」，但尚未有球種代碼
- ⚠️ 賽後單場 API 回應可能過大導致無法傳送到 Kafka，需注意 payload size 限制


### TCZB-3950 [Crawler] - 90vs 賽事分析

> Confluence 頁面 ID：79464944
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464944)
> 摘要檔：[processed/79464944-summary.md](../../confluence/processed/79464944-summary.md)
> Confluence 最後更新：2025-10-16
> 摘要最後同步：2026-05-27

**摘要**：
本文档记录了 90vs 爬虫为支持赛事分析新增的抓取功能：从 90vs 网站获取比赛对阵记录、主客队近期战绩和心水推介。文档说明了数据源、请求方式、解析流程、发送格式以及文件存储路径。

**關鍵業務規則**：
- 抓取主隊與客隊近5場對戰紀錄，限一年內的比賽，若一年內無對戰則不抓取
- 心水推介僅部分比賽有提供，包含信心指數（0‒5）、預測結果（1=主勝，2=客勝，3=和局）及文字評論
- 爬取週期：96 次約 10 分鐘為一個循環；pregame 頁面每 2 個週期抓取一次，inplay 頁面每 5 個週期抓取一次
- inplay 頁面需根據狀態碼判斷比賽狀態，僅賽前（status=2）才進一步抓取單場資料

**關鍵設計決策**：
- 使用 Selenium 請求完整 match_list 頁面，從中解析出每場比賽的 game_id，再透過內部 JS 檔案獲取單場詳細資料
- 將新增的賽事分析數據以 prediction 類型透過 Kafka 傳送，便於下游獨立消費
- 心水推介內容以文字檔寫入伺服器

**注意事項**：
- ⚠️ 部署位置已多次變更，當前實際運行環境需人工確認
- ⚠️ 「96次為一個週期，約10分鐘」的抓取頻率可能已根據賽事數量調整
- ⚠️ 心水推介寫入路徑的帳號密碼引用至 PRD系統資訊，該頁面可能有權限限制或已變更


### TCZB-4003 [NFL] - NFL官網賽事即時資訊

> Confluence 頁面 ID：79465598
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465598)
> 摘要檔：[processed/79465598-summary.md](../../confluence/processed/79465598-summary.md)
> Confluence 最後更新：2025-10-30
> 摘要最後同步：2026-05-27

**摘要**：
本文件說明如何透過 NFL 官方 API 取得賽程、賽事詳情與即時球員數據，包含兩個主要端點、授權 token 的取得方式、以及 API 回應的欄位對應規則。

**關鍵業務規則**：
- 比賽狀態依據 summary 欄位判斷：若 summary 不存在則 status = '2'；若 summary.phase = 'INGAME' 則 status = '0'；若 summary.phase = 'FINAL' 則 status = '1'
- league 固定為 'nfl'；game_type 固定為 'FL'
- 比賽日期與時間使用 API 回傳的 time 欄位進行時區轉換

**關鍵設計決策**：
- API 請求需帶 Bearer token。token 不透過一般登入獲取，而是以 Selenium 打開 NFL 官網，接受 cookies 後從 localStorage 讀取 accessToken
- 資料擷取分三步驟：先呼叫 weeks/date 取得當週資訊，再以 season 和 week 呼叫 weekly-game-details 取得比賽總覽，最後可選用 live/player-statistics 取得單場詳細數據

**注意事項**：
- ⚠️ 文件中硬編碼的 Bearer token 可能已過期或與特定 session 綁定，需實作自動更新的機制
- ⚠️ 取得 token 的方式依賴 Selenium 操作瀏覽器與 localStorage，可能因網站改版、反爬機制或執行環境不穩定而失效
- ⚠️ 時區轉換的具體邏輯未詳述，僅說明需使用 time 欄位進行轉換
- ⚠️ 玩家統計 API 的回應結構未提供完整欄位說明


### TCZB-4001 [90vs] - 足籃走地即時資訊

> Confluence 頁面 ID：79465561
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465561)
> 摘要檔：[processed/79465561-summary.md](../../confluence/processed/79465561-summary.md)
> Confluence 最後更新：2025-11-05
> 摘要最後同步：2026-05-27

**摘要**：
這份文件定義了從 90vs 網站擷取足球與籃球即時比賽數據的技術設計，包含兩個核心組件：90vsProvider 及 CrawlerAgent90vs。文件詳細說明了抓取流程，包括足球每15分鐘抓取一次、籃球在特定時間點抓取，以及資料最終儲存的格式規範。

**關鍵業務規則**：
- 足球即時資訊每 15 分鐘抓取一次
- 籃球即時資訊於每節剩餘 6 分鐘、5 分鐘及該節結束時抓取；僅限大型賽事（如 NBA）才有此服務
- Provider 以 96 次請求為一個週期（約 10 分鐘），且每 3 次請求才解析一次 inplay 頁面的單場數據
- 資料輸出檔名固定為 '{game_id}_stats.txt'，儲存在以日期命名的目錄下
- PRD 環境中，抓取任務由特定伺服器負責

**關鍵設計決策**：
- 採用 Selenium 與正則表達式解析 HTML：先解析 inplay 頁面的 match_list 以取得所有進行中賽事的 game_id，再對每個 game_id 單獨請求詳細數據
- 流程設計為先判斷比賽狀態，只針對狀態為進行中的賽事進行後續的詳細數據請求
- 足球狀態判斷採雙重檢查機制：先以 class 屬性判斷有球在滾，若無則進一步檢查 st_status 中的圖片檔名
- 籃球狀態判斷使用固定的 playbyplay 階段關鍵字列表進行比對

**注意事項**：
- ⚠️ 部署規則變更：已將原負責籃球的 SRV36 改為抓取足球賽事，部署拓撲可能已與表格所列不同
- ⚠️ 籃球資料可用性限制：文件提到籃球只有大型賽事才有即時資訊，開發時需考慮資料不完整的例外處理
- 需人工確認：provider code snippet 中的區塊註解提到籃球狀態判斷有 pregame 頁面，但 main flow 說明僅區分 inplay 和 else 兩種頁面類型
- 需人工確認：籃球數據源 URL 與足球不同，且請求內容格式有別


### TCZB-4000 [Nowscore] - 足籃走地即時資訊

> Confluence 頁面 ID：79465592
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465592)
> 摘要檔：[processed/79465592-summary.md](../../confluence/processed/79465592-summary.md)
> Confluence 最後更新：2025-11-05
> 摘要最後同步：2026-05-27

**摘要**：
這份文件定義了從 NowScore 網站抓取足球與籃球走地即時統計資訊的技術規格。明確了資料獲取的觸發時間點、API 端點與參數格式，以及最終要寫入的 JSON 輸出結構和 stats_mapping 對照表。

**關鍵業務規則**：
- 足球走地數據應在比賽開始後的第 15、30、45、60、75 分鐘時觸發寫檔
- 籃球走地數據應在每一節結束前及該節剩餘第 5、6 分鐘時觸發寫檔
- 足球數據的輸出 JSON 結構需包含 Time, stats（含 type, home, away）, at_time 欄位
- 籃球數據的輸出 JSON 結構需包含 Time, stats（含 type, home, away）, at_time 欄位
- 籃球數據需額外計算並加入多項統計項
- 使用 stats_mapping 將 API 返回的代碼轉換為中文 type 名稱

**關鍵設計決策**：
- 數據寫入採用定時觸發機制，而非事件驅動，根據比賽經過時間點來決定何時抓取
- 足球和籃球使用不同的 API 端點獲取細節數據，但輸出格式統一
- 籃球 API 數據結構與足球不同，需自行組合計算部分衍生數據

**注意事項**：
- ⚠️ 籃球 API 返回數據可能不完整，開發時需確認資料完整性與錯誤處理機制
- ⚠️ 文件僅提供 API 端點與範例，未明確說明寫檔的目標位置
- ⚠️ 足球範例數據中出現 '2H 90:00' 的時間點，但規則僅提到第 75 分鐘，此處可能為範例或包含補時階段規則
- ⚠️ stats_mapping 中 SC 部分缺少多個代碼，可能為未使用的項目或遺漏


### TCZB-4100 [Fortuna888Provider] - fortuna888爬蟲

> Confluence 頁面 ID：79467228
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467228)
> 摘要檔：[processed/79467228-summary.md](../../confluence/processed/79467228-summary.md)
> Confluence 最後更新：2025-12-22
> 摘要最後同步：2026-05-27

**摘要**：
這是一份針對 Fortuna888 體育博彩站台的新爬蟲技術設計文檔。文件詳細描述了如何透過 VPN 訪問日本伺服器、使用 undetected_chromedriver 繞過反爬機制進行登入、以及如何透過 API 直接抓取多種運動的賽前和滾球賠率及賽果比分。

**關鍵業務規則**：
- 需開啟 VPN 連接至日本伺服器才能訪問目標站台
- 若訪問首頁時回應包含 'Sorry, you have been blocked'，則判定 VPN 失敗，需暫停 600 秒後重啟程式
- 爬蟲資料包含足球、籃球、棒球、美式足球、冰球的 pregame、inplay 賠率以及賽果比分
- 賽前賠率有兩種模式：R 和 HR
- 抓取前需檢查 36588 Sports 是否處於例行維護狀態，若在維護中則跳過

**關鍵設計決策**：
- 使用 undetected_chromedriver 而非一般 selenium webdriver，以繞過網站的機器人檢測機制
- 賠率數據採用直接調用內部 API 的方式獲取，而非透過 DOM 解析
- 所有請求的 Content-Type 設為 'application/x-www-form-urlencoded'，且 POST 資料需將 payload 包在 'cmd' 參數內並以 JSON 字串形式傳送
- 爬蟲部署於全部 41 台 VM 機器中，推測為分散式執行設計

**注意事項**：
- ⚠️ 文件提到此為新站台，相關程式碼及流程可能仍處於開發或早期迭代階段
- ⚠️ 文件中的圖片附件無法顯示，實際 DOM 結構可能因站台改版而失效


### TCZB-4109 [籃球即時資訊] - NBA官網、Naver

> Confluence 頁面 ID：79467348
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467348)
> 摘要檔：[processed/79467348-summary.md](../../confluence/processed/79467348-summary.md)
> Confluence 最後更新：2025-12-18
> 摘要最後同步：2026-05-27

**摘要**：
這份文件定義了兩個籃球即時數據源的 API 端點與 JSON 結構：NBA官網提供英文的 play-by-play 數據，Naver 提供韓文的文字轉播數據。文件提供了事件的具體範例與欄位對照。

**關鍵設計決策**：
- 選擇 NBA官網 的 API 端點以取得結構化的 play-by-play JSON 數據
- 選擇 Naver 的 API 端點，需按各節分開請求後再統整為完整數據
- 事件結構採用統一的欄位格式，包含時間、比分、隊伍、事件類型與子類型，以利跨數據源整合
- NBA官網範例顯示時間格式為倒數計時，Naver 範例顯示時間格式為順時記錄，兩者時間方向不同，需注意轉換

**注意事項**：
- ⚠️ 文件僅提供部分事件類型的範例，完整的 actionType 與 subType 枚舉清單需人工確認
- ⚠️ Naver 的 API 需要針對每節分別請求，需注意合併時的順序與去重處理
- ⚠️ 文件中的比分欄位在特定事件中未提供，可能代表比分僅在得分事件後才更新


### TCZB-4167 [Crawler] - 台灣YAHOO賽事、新聞

> Confluence 頁面 ID：79467866
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467866)
> 摘要檔：[processed/79467866-summary.md](../../confluence/processed/79467866-summary.md)
> Confluence 最後更新：2026-01-14
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義台灣 Yahoo 運動賽事與新聞的爬蟲技術方案。賽事透過 Scoreboard API 獲取比賽資訊，新聞則從 HTML 中提取文章 URL、發布時間與 ID，僅抓取當日文章並限制單次 20 篇。

**關鍵業務規則**：
- 賽事 API 的 date 參數需涵蓋昨天、今天、明天三天的比賽
- 足球聯盟需先請求足球頁面以取得動態的聯盟列表
- API 回傳的比賽時間需進行時區/格式轉換後使用
- 主客隊名稱由 team_id 透過回傳物件中的 teams 集合查找 full_name 賦值
- 比賽各節分數取自 game_periods 陣列中的 home_points 與 away_points
- 文章抓取時僅保留發布時間為當日的文章，非當日者跳過
- 單次文章抓取最多 20 篇，因此爬蟲頻率需加快以覆蓋所有新文章

**關鍵設計決策**：
- 優先使用結構化 API 而非網頁解析來獲取賽事與新聞數據
- 透過 date 參數指定日期範圍，使爬蟲可靈活回溯歷史賽事
- 文章僅抓取當日發布的內容，避免累積過期資訊
- 足球聯盟列表動態變化，因此不硬編碼聯盟 ID

**注意事項**：
- ⚠️ 足球聯盟需「額外請求頁面取得」聯盟列表的具體解析方式未詳述
- ⚠️ 賽事 API 請求中 date 參數的實際用法未明確
- ⚠️ 評論 API 的 count 參數指定為 10，是否需處理分頁以獲得完整評論未說明


### TCZB-4197 [Crawler] - PTT Live文賽事

> Confluence 頁面 ID：79468222
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79468222)
> 摘要檔：[processed/79468222-summary.md](../../confluence/processed/79468222-summary.md)
> Confluence 最後更新：2026-01-28
> 摘要最後同步：2026-05-27

**摘要**：
本文檔說明如何實作一個PTT爬蟲，用於監控並爬取NBA版的Live賽事文章。內容涵蓋了爬蟲的部署位置、資料抓取邏輯、HTML解析規則以及最終的資料產出路徑與格式。

**關鍵業務規則**：
- 僅爬取PTT NBA版中，標題含有「Live」字樣的文章
- 僅處理當日的文章，非當日文章會停止往下頁爬取
- game_id 的規則是取PTT文章網址中，去除「.html」後綴的字串
- 寫入DB的game_status預設為'2'，且主客隊分數預設值皆為'0'；若非賽前/賽中，分數則設為'-1'
- 主隊為文章標題中右側的隊伍，客隊為左側的隊伍
- 比賽時間的解析邏輯是從HTML的meta description中搜尋特定格式的字串
- 文章內容及其回覆會寫入檔案系統，存檔路徑遵循特定規則
- 若文章回覆數少於20篇，則不進行寫檔處理
- 針對同一場賽事，系統會使用快取機制避免重複開啟執行緒進行爬取

**關鍵設計決策**：
- 爬蟲並非直接從PTT文章內文解析主客隊，而是從文章「標題」中萃取
- 為防止對PTT伺服器造成過大負擔，每開啟一個新的爬取執行緒會間隔5秒
- 爬取頻率會根據文章發布時間動態調整：發布4小時內每120-180秒爬取一次，超過4小時則每720-900秒爬取一次
- 使用執行緒非同步處理多場Live賽事文章的爬取

**注意事項**：
- ⚠️ 本文檔為Sprint 228的開發內容，部分流程細節未詳列，需搭配完整程式碼才能完全理解
- ⚠️ 文中PRD寫檔路徑引用了WinSCP主機及帳密文件，這些憑證與主機位置可能隨時間變更
- ⚠️ check_status_time 的檢查邏輯在當前程式碼被關閉，若直接視為最終版本可能導致正式環境的資料錯誤


### TCZB-4198 [Crawler] - Winna賠率站台爬蟲

> Confluence 頁面 ID：79468287
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79468287)
> 摘要檔：[processed/79468287-summary.md](../../confluence/processed/79468287-summary.md)
> Confluence 最後更新：2026-01-27
> 摘要最後同步：2026-05-27

**摘要**：
本文件為 Winna 賠率站台的爬蟲技術設計，說明了如何透過 Selenium 取得賽前和賽中比賽的 game ID，再透過單場 API 並行抓取比賽詳細資料。

**關鍵設計決策**：
- 使用 Selenium 而非 API 取得 game ID（需人工確認原因）
- 先調用站台 JS 取得 brand id，才能呼叫後續 API
- 每個 game ID 開獨立 thread 並行呼叫單場 API，提升抓取效率
- 僅抓取 48 小時內的比賽，減少無效請求
- 採用硬編碼對照表將站台球種字串映射為內部代碼

**注意事項**：
- ⚠️ game_status 值 prematch=2, live=0 可能與系統內其他爬蟲定義不同，需核對統一
- ⚠️ 文件未說明 Selenium 瀏覽器驅動的配置
- ⚠️ 使用了特定的 JS URL 獲取 brand id，該 URL 可能隨站台改版變動


### TCZB-4199 [Crawler] - BoomeRang賠率站台爬蟲

> Confluence 頁面 ID：79468212
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79468212)
> 摘要檔：[processed/79468212-summary.md](../../confluence/processed/79468212-summary.md)
> Confluence 最後更新：2026-01-27
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了 BoomeRang 賠率站台的爬蟲技術設計，包括 5 支核心 API 端點、17 種球種與網站 ID 的對應關係、4 種語言的 lang_code，以及從 API 回應 JSON 中萃取比賽資料的欄位路徑對照表。

**關鍵業務規則**：
- 取得賽前比賽資料的 API 的 startDate 參數需帶入前一天的日期才能取得今日的賽事
- 球種名稱需從 API 回傳的 sport.name 進行轉換，共定義 17 種球種對應
- 賽果資料只能分聯盟去請求，需先透過 GetSportMenu API 取得所有球種的聯盟清單，再逐個請求 GetEventResults
- 賽果中 isDropped=true 表示比賽終止（可能是延賽或取消，但無法區分是延賽還是取消）
- 賽果若完全沒有 score 欄位也沒有 isDropped 標記，屬於異常情況
- 比賽時間 startDate 需再轉換時區（timezoneOffset=-480，即 UTC+8）
- scores 欄位需由 [score_home, score_away] 組成

**關鍵設計決策**：
- 選擇直接呼叫 altenar 平台的 API 而非爬取網頁 HTML，可獲得結構化 JSON 資料
- 賽前和賽中資料使用不同 API 端點
- 賽果查詢需要先取得完整聯盟清單再逐個請求，而非單一 API 批次取得
- date 參數需帶入前一天日期的設計，可能是因為平台時區轉換的特定邏輯

**注意事項**：
- ⚠️ 賽果的 isDropped 無法區分延賽和取消，若系統需要區分這兩種狀態，需人工確認來源端是否有其他判斷方式
- ⚠️ date 參數需帶入前一天日期的規則，需確認這是否為永久規則
- ⚠️ 文件提到「一種是完全沒給結果也沒有寫終止」，這種情況下爬蟲應如何標記比賽狀態，文件中未明確定義


### TCZB-4264 [WidgetApi] - ParserController

> Confluence 頁面 ID：79469193
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-4264+%5BWidgetApi%5D+-+ParserController)
> 摘要檔：[processed/79469193-summary.md](../../confluence/processed/79469193-summary.md)
> Confluence 最後更新：2026-04-08
> 摘要最後同步：2026-05-27

**摘要**：
本文檔描述 WidgetApi 新增透過 Redis 控制爬蟲 Parser 停止/暫停解析的功能。當用戶於 Google 試算表設定停止或暫停監控時，WidgetApi 將狀態寫入 Redis，爬蟲 Parser 定期讀取並據此停止發送數據。

**關鍵業務規則**：
- 停止/暫停監控時，將停止信號寫入 Redis hash parser_controller，值為 0 代表停止/暫停（或移除 key 表示停止），值為 1 代表解析中
- 停止解析狀態若持續超過 2 天，對應的 Redis key 值將被自動刪除（清理機制）
- WidgetApi 會自動從 Crawler Server Site Info 表格抓取所有站台，若 Google 表單中不存在則自動新增
- 因 Parser 停止送數據導致 Dashboard 的 SiteInfo 變為紅字時，會觸發 ErrorSiteInfo 警報，需手動關閉該警報

**關鍵設計決策**：
- 選用 Redis (192.168.55.80 db13) 作為控制信號的傳遞媒介，利用 hash 結構 parser_controller 儲存各站點的解析狀態
- WidgetApi 的每個站點必須設定與 SiteInfo 相同的 Redis key
- 在 WidgetApi 服務中建立監聽執行緒（listen_status），持續檢查 Redis 狀態
- 舊專案需在安裝 TCZB 套件時使用 --upgrade 參數

**注意事項**：
- ⚠️ Redis 狀態值的定義與移除規則有模糊：文件指出「停止會將key值移除」以及「停止解析超過2天會將 Redis 對應的值刪除」，實際行為需確認
- ⚠️ 文中提到「停止/暫停監控」但未明確區分「停止」和「暫停」的 Redis 信號差異
- ⚠️ WidgetApi 監聽執行緒的目的未詳細說明


### TCZB-4287 [Crawler] - Playbet 爬蟲

> Confluence 頁面 ID：79470002
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79470002)
> 摘要檔：[processed/79470002-summary.md](../../confluence/processed/79470002-summary.md)
> Confluence 最後更新：2026-04-23
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義 Playbet 平台的爬蟲實作細節，包含賽前/賽中/賽果資料的 API 端點、查詢參數、回傳 JSON 欄位對應，以及球種代碼對照表。同時說明了語系參數與賠率需要除以 1000 的轉換規則。

**關鍵設計決策**：
- 採用 Playbet 官方 API v2 端點獲取比賽資料，避免頁面解析，提高穩定性
- 透過 HTTP query parameters 實現篩選與分頁
- 使用多欄位排序後取 limit 筆
- 賠率數值來自 outcomes 中的 odds 欄位，原始值需除以 1000 得到實際賠率

**注意事項**：
- ⚠️ match_status 參數值 3 定義為 close，但有標注問號，需人工確認其語意
- ⚠️ sport_type 參數值 'reguler' 應為 'regular' 的拼寫錯誤
- ⚠️ 分數欄位路徑中的雙層陣列索引未詳列，可能因不同運動而有差異


### TCZB-4302 [Parser] - PlayBet

> Confluence 頁面 ID：79470316
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-4302++%5BParser%5D+-+PlayBet)
> 摘要檔：[processed/79470316-summary.md](../../confluence/processed/79470316-summary.md)
> Confluence 最後更新：2026-04-17
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了從 PlayBet 數據源提取比賽資訊的解析規則，包含比賽 ID、球種、主客隊名稱與編號、比賽時間、聯盟、遊戲狀態、節數、各回合比分、賠率等欄位的 JSON 路徑對應。

**關鍵業務規則**：
- 賠率 (odds) 的值需要除以 1000 才是實際賠率
- game_status 欄位：0 表示 pregame，1 表示 inplay
- playbyplay 中的 remaining_time_in_period 為該局剩餘時間，clock_updated_at 為上傳時間，目前階段暫不使用
- 語系參數設定為 {"language":"en"}


### TCZB-4326 [Crawler] - KU爬蟲

> Confluence 頁面 ID：79470871
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79470871)
> 摘要檔：[processed/79470871-summary.md](../../confluence/processed/79470871-summary.md)
> Confluence 最後更新：2026-05-18
> 摘要最後同步：2026-05-27

**摘要**：
本文件為 KU 體育博彩爬蟲的技術設計規格，涵蓋站台連線（需 VPN 至日本）、登入流程、時間轉換（UTC+7→台灣+1h）、主客隊方向（主隊在下）、比賽狀態處理及維護判斷。詳細定義 pregame 與 inplay 的賠率資料結構、game_id 生成邏輯與後端 API 端點。

**關鍵業務規則**：
- 必須使用 NordVPN 連線至日本伺服器，否則無法存取站台
- 站台時間為 UTC+7，轉換為台灣時間需加 1 小時
- 頁面與資料中主隊在下、客隊在上，資料順序依此對應
- 站台無原生 game_id，採用 hash(聯盟 + 主隊名稱 + 客隊名稱) + '-' + 日期 生成唯一識別
- 維護狀態僅在登入後才能確認，未登入時無法判斷是否維護中
- pregame 的 game_status 設為 '2'，inplay 設為 '0'
- BS 球種 pregame 抓取玩法：獨贏、讓分、大小、上半場獨贏、上半場大小、上半場讓分
- BS 球種 inplay 抓取玩法：走地讓分、走地大小、上半場讓分、上半場大小
- 帳號管理透過 ls2 API：get_page 取得帳號、heart_beat 回報心跳、remove_handler 通知停止
- 爬蟲部署分佈：KUSeleniumProvider 部署於指定 VM，CrawlerAgentKU 以服務/容器形式部署於 Docker Swarm

**關鍵設計決策**：
- 採用 Selenium 進行瀏覽器自動化與網頁資料擷取
- 使用 NordVPN 強制切換至日本 IP，避免站台封鎖或地區限制
- 實作帳號輪換機制，搭配 IP 切換以降低封鎖風險
- 爬蟲拆分為 Provider（負責頁面取得）與 Agent（負責解析），降低耦合並提高可維護性
- 透過後端 API（ls2）管理爬蟲工作節點的帳號分配與生命週期
- 因站台無提供 game_id，選擇以聯盟與兩隊名稱雜湊加日期方式生成
- 賠率資料採用巢狀 JSON 結構，按玩法類別與盤口線值分組
- 爬取排程安排於 UTC+8 凌晨 0-6 點抓取前一日資料

**注意事項**：
- ⚠️ 文中 API URL 標示了「原:...」表示已變更過，需確認當前有效端點
- ⚠️ 例行維護時間「尚未發現」，可能需要透過監控在維護發生後記錄
- ⚠️ 文件包含大量截圖，解析規則依賴畫面元素位置，若站台改版可能導致爬蟲失效


### TCZB-4357 [Crawler] - 泰金999賠率站台爬蟲

> Confluence 頁面 ID：79471567
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471567)
> 摘要檔：[processed/79471567-summary.md](../../confluence/processed/79471567-summary.md)
> Confluence 最後更新：2026-05-20
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了針對泰金999（tg666.net）的爬蟲實作，包括帳號列表、登錄 API 獲取認證 token、使用 GameDetail API 分兩步抓取比賽清單與完整玩法，以及 GameResult API 取得賽果。

**關鍵業務規則**：
- 對於彩球（LB）與賽馬（HR）無主客隊之分，teamhome 與 teamaway 無法套用常規名稱
- 為區分同聯盟內多場彩球/賽馬賽事，可將描述資訊放入 other_info，或組合成 game_id+game_date 作為唯一標識（方案未最終決定）
- 分數欄位 scores 僅使用主隊與客隊總分組成，不採用各節分數，因為網站提供的各節分數有問題
- 比賽狀態 GameType 值：3 表示 Pregame（賽前），2 表示 Inplay（滾球）

**關鍵設計決策**：
- 登錄流程設計為先呼叫 /api/mb/sin/login，從回應中獲取 ssstoken 與 sssmbid
- 獲取比賽資料分成兩階段：先用第一個 payload 獲取該球種下所有比賽；再用第二個 payload 取得單場比賽的全部玩法資訊
- 對彩球/賽馬的處理設計兩種方案，但文件中未明確選定
- 分數設計只取總分，因原始網站各節分數存在異常
- 語言切換需在登入頁面設定

**注意事項**：
- ⚠️ 文件中的帳號與密碼為測試用，可能已失效或變更，勿直接用於生產環境
- ⚠️ 彩球/賽馬的處理方案文件中僅列舉兩種可能，未記錄最終採用方案
- ⚠️ 爬蟲目標網站 API 與結構可能隨時間變動
- ⚠️ 「帳號會變化」的註記需釐清是帳號輪換、帳號動態獲取或其他機制


### TCZB-2499 [CrawlerAgent] - sofa parser

> Confluence 頁面 ID：47218903
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-2499+%5BCrawlerAgent%5D+-+sofa+parser)
> 摘要檔：[processed/47218903-summary.md](../../confluence/processed/47218903-summary.md)
> Confluence 最後更新：2023-11-10
> 摘要最後同步：2026-05-27

**摘要**：
这份文件详细说明如何解析 SofaScore 赛事 JSON 数据，包含联盟、队伍、比赛状态、比分、即时事件及球员统计资料的完整字段路径与格式转换规则。提供丰富的游戏状态代码对照表与不同球种局数、比分结构的差异处理逻辑。

**關鍵業務規則**：
- 联盟名称 league 的组成规则：用连字符组合「国家-联盟名称」，若联盟名称已包含国家则避免重复
- 比赛时间需自行转换 Unix timestamp，SofaScore API 提供的 timestamp 单位是「秒」，而系统内部使用的是「毫秒」，转换时需乘以 1000
- game_id 从 API 取出的类型为 int，必须强制转换为 string 类型再使用
- 比分应优先使用 current 字段，而不是 normaltime 字段
- 针对板球 (CK) 比赛，其 scores 结构为嵌套阵列，需要特殊解析逻辑
- 篮球 playbyplay 中的 event_time 应使用 reversedPeriodTimeSeconds 计算倒数时间
- 新版本 API 中 status 已无 description 栏位，实作时必须自行依据 status_code 对照表产生相对应的 description 文字

**關鍵設計決策**：
- gametype 不自行从原始 data 转换，原因是 SofaProvider 爬取时已经会转换，Parser 直接取用其转换后的值
- 比分来源从原本的 normaltime 字段改为使用 current 字段，此设计是因应赛况进行中分数变化的需求
- 处理足球比分时，发现 period 比分会有资料延迟的问题，因此决定额外使用 score_home 与 score_away 这两个即时的总分栏位
- 选择从原始码提取 game_status code 对照表，并将还在观察中的行为透过 Trace 纪录持续追踪

**注意事項**：
- ⚠️ 文件中 gametype、score_home/score_away、playbyplay 的 period 取得方式均有删除线标记，表示基于早期 API 版本的解析方式已失效或变更
- ⚠️ 棒球的局数区分（Top/Bottom）因缺乏即时比赛数据，无法验证判断方式
- ⚠️ 手写的 status_description 字典存在版本不一致的问题，需确认哪一份为最终实作版本


### TCZB-3156 [Crawler]-大發體育爬蟲 (dafabet)

> Confluence 頁面 ID：55577445
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55577445)
> 摘要檔：[processed/55577445-summary.md](../../confluence/processed/55577445-summary.md)
> Confluence 最後更新：2025-07-02
> 摘要最後同步：2026-05-27

**摘要**：
這份文件定義了大發體育 (dafabet) 爬蟲的 API 請求格式與資料映射規則。主要說明如何組合 Payload 呼叫三個核心 API 來取得完整的比賽、賠率與節數分數資料。

**關鍵設計決策**：
- 為了統一處理滾球與非滾球賽事，決定在請求事件資料 API 時固定將 periodType 設為 PRE_MATCH，並透過 includeLiveEvents 參數來控制是否輸出進行中的比賽
- 為了解決部分球種在事件 API 中只能取得總分而無法取得各節分數的問題，決定額外引入兩支 PBP API
- 定義了 API 請求中僅允許動態調整的參數

**注意事項**：
- ⚠️ 文件中的 API Payload 範例註解提到 dateTo 的兩種不同用法，實作時需釐清確切邏輯
- ⚠️ PBP API 使用到的球種 ID 明確標注「不等於站台的球種 ID」，AI 開發時不可混用
- ⚠️ 文件中提及 Feedcode 如果開頭為 1 用 nextbet 路由，開頭為 4 用 akamaized，需確認實際情況是否包含其他前綴的處理方式


### TCZB-3182 [Crawler]-1xBET賽果

> Confluence 頁面 ID：55577885
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55577885)
> 摘要檔：[processed/55577885-summary.md](../../confluence/processed/55577885-summary.md)
> Confluence 最後更新：2024-04-18
> 摘要最後同步：2026-05-27

**摘要**：
本文件說明如何透過 1xbet.com 的 Service-API 取得賽果資料，包含兩個端點以及對應的查詢參數。提供球種 ID 對照表，並詳列從 game_data 萃取各欄位的鍵值與處理方式。

**關鍵業務規則**：
- dateFrom 參數須設為六小時前，dateTo 為現在時間，以查詢近期賽果
- sportIds 及 champId 參數支援多個 ID 以逗號分隔
- 爬取的賽果狀態（game_status）一律視為 Final，不區分進行中或取消
- game_id 不可直接取用 game_data['id']，須透過 self.get_game_id 函式產生
- 分數欄位 scores 的格式為巢狀列表

**關鍵設計決策**：
- 採用 1xbet Service-API 取得結構化 JSON 資料，而非解析網頁 HTML
- 查詢中加入固定參數確保回傳內容一致
- 不保留遊戲原始狀態，統一設為 Final，簡化後續資料處理
- 自定義 get_game_id 取代直接使用 API 回傳的 id

**注意事項**：
- ⚠️ game_data['id'] 被劃去，表示曾為舊版做法，開發時應避免直接取用
- ⚠️ scores 的巢狀格式需正確解析，可能包含多組子分數
- ⚠️ 外部 API 端點與參數可能隨時變動


### TCZB-3323 [Crawler] - 訂閱twsl寫入DB

> Confluence 頁面 ID：55579610
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55579610)
> 摘要檔：[processed/55579610-summary.md](../../confluence/processed/55579610-summary.md)
> Confluence 最後更新：2024-06-28
> 摘要最後同步：2026-05-27

**摘要**：
這是一份Crawler訂閱數據並寫入資料庫的技術實作說明文件。描述了如何透過SignalR的WebSocket連線到twsl數據源，步驟包括：先發送POST請求取得connectionToken，再建立WSS連線並向伺服器註冊要訂閱的群組。接收到的訊息經過Base64解碼和GZip解壓縮後，需將數據寫入Cassandra的games_{game_type}表和Redis的特定DB。

**關鍵業務規則**：
- 訂閱twsl數據前必須先POST請求取得connectionToken
- 建立WSS連線後必須先發送protocol訊息和addgroup訊息，才能開始接收資料
- 接收到的訊息類型為type:1（invocation），需從arguments[0]中取出Base64字串進行解碼
- 解碼後的資料前4位為壓縮前的字串長度，解壓縮時需忽略這4個bytes
- 解壓縮後的gamedata需寫入Cassandra的games_{game_type}表
- 賽事基本資訊存入Redis DB7，賽事賠率資訊存入Redis DB6

**關鍵設計決策**：
- 選擇使用WSS（WebSocket Secure）而非HTTP polling來接收即時賽事數據
- 資料傳輸採用Base64+GZip雙重編碼是為了在WebSocket通道中高效傳輸大量賽事數據
- 將賽事資訊和賠率分別儲存在Redis的不同DB，是為了分離資料類別方便查詢
- 選擇寫入Cassandra games_{game_type}表，可能是為了分散寫入壓力
- 解碼時跳過前4位元組，因為twsl實際傳送的資料格式與標準GZip有差異

**注意事項**：
- ⚠️ 文件標題為「TCZB-3323」，但歸檔在「舊的Projects 1-200」目錄下，此功能可能已變更或過期
- ⚠️ 文件只列出了如何訂閱和寫入DB的結構，但沒有說明誰觸發訂閱、何時開始、何時停止
- ⚠️ Cassandra的games_{game_type}表中未被描述具體欄位結構
- ⚠️ Redis DB6的key格式推測為BK_twsl_聯賽名稱_賽事編號，但文檔未明確說明命名規則
- ⚠️ 程式碼範例是Python實作，但推測crawlerservice是C# .NET，需人工確認技術棧


### TCZB-3326 [Crawler] - covers 加入走地訊息

> Confluence 頁面 ID：55580120
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55580120)
> 摘要檔：[processed/55580120-summary.md](../../confluence/processed/55580120-summary.md)
> Confluence 最後更新：2024-07-16
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義 covers.com 爬蟲加入走地訊息的實作方式，包含籃球、棒球、冰球等運動的網頁結構解析規則與正則表達式。說明如何區分賽前、賽中、賽後資料，以及時區轉換、分數提取、即時狀態等技術細節。

**關鍵設計決策**：
- 籃球/足球走地網頁改為抓取昨天、今天、明天三天的對戰頁面，以統一賽前與賽後的抓取邏輯
- BK/FL 的比賽列表使用正則 `<article(.*?)Matchup</a>` 提取
- 籃球賽中分數不分主客隊，以出現順序推斷：第一個分數為客隊，第二個為主隊
- 棒球壘包狀態以圖片 alt 屬性的數字對應
- 比賽時間非台灣時間，需進行時區轉換，且賽後無時間資訊，需從賽前快取保留時間
- 棒球/冰球的 game_id 需加上 league 前綴組成完整識別碼

**注意事項**：
- ⚠️ covers.com 頁面結構可能隨網站改版變動，爬蟲正則需持續維護
- ⚠️ 文件提到「賽後沒有時間，只有日期，把賽前的時間存cache」，需注意快取失效或錯誤的可能
- ⚠️ 籃球賽中分數的主客隊判斷基於作者觀察，非官方文件保證


### TCZB-3377 [Crawler]-ASC site 重構

> Confluence 頁面 ID：55580594
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55580594)
> 摘要檔：[processed/55580594-summary.md](../../confluence/processed/55580594-summary.md)
> Confluence 最後更新：2024-08-02
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義 ASCbet 爬蟲的重構技術細節：列出賽前/賽中 API 端點與 payload，說明取得 cookie 的流程，提供 SportID 對照表，並詳細規範比賽基本資訊、比分、playbyplay 的 parser 欄位。同時記錄多球種的賠率結構與特例玩法。

**關鍵業務規則**：
- SportID 與運動類型對應：1=SC, 2=BK, 3=FL, 4=BS, 5=HL, 7=TN, 9=TB, 11=CK, 12=VB, 13=HB, 17=SN, 20=DT, 21=MA, 26=ES
- 取得資料前必須先以 session.get 取得 cookie
- 賽前 API 的 Stage 參數可為 1,2,4；賽中 API 的 Stage 固定為 3
- 遊戲基本資訊從 match 陣列解析，其中 team_home/away 與 ID 需以 '|' 做 split
- 比分欄位：score_home 為 match[13]、score_away 為 match[14]
- playbyplay 取自 match[7]，足球包含節數與時間，其他球種待觀察
- 通用賠率結構包含 HA(1X2,讓分), OU(大小), Others-HalfHA, Others-HalfOU
- 足球另有「角球數」「第一角球」「罰牌」「第一張罰牌」等玩法區塊

**關鍵設計決策**：
- 選用 POST 方式呼叫 ASCbet 的 Live/NLive API，並以固定 payload 傳遞參數
- 資料解析採用 match 陣列索引對應欄位，簡化 parser 實作
- 針對不同球種的賠率欄位索引與玩法組合，定義在 AppSetting 結構中
- 特殊玩法以獨立區塊描述，允許針對特定球種客製擴展

**注意事項**：
- ⚠️ 文件中的圖片連結無法直接讀取，僅能依文字說明推斷
- ⚠️ playbyplay 欄位在非足球球種尚未完整觀察，存在未知行為
- ⚠️ 部分球種的「是否要做」標記可能隨需求變動


### TCZB-3406 [Crawler] - 1xbet parser

> Confluence 頁面 ID：55580963
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3406+%5BCrawler%5D+-+1xbet+parser)
> 摘要檔：[processed/55580963-summary.md](../../confluence/processed/55580963-summary.md)
> Confluence 最後更新：2024-08-21
> 摘要最後同步：2026-05-27

**摘要**：
這份文件定義了從1xbet API回應中提取比賽基本資料、賽中分數、play-by-play統計、場地環境資訊以及賠率列表的具體字段映射規則。所有數據提取均以原始JSON字段為基礎，部分數值需進行時間戳轉換或整數運算。

**關鍵業務規則**：
- 比賽球種(game_type)從 data["SN"] 取得
- 比賽ID(game_id)從 data["I"] 取得
- 比賽時間(game_date & game_time)從 data["S"] 取得，為時間戳，需轉換為日期與時間
- 賽中主隊分數(score_home)從 data["SC"]["FS"]["S1"] 取得，客隊分數從 data["SC"]["FS"]["S2"] 取得
- 各節分數(scores)從 data["SC"]["PS"] 取得
- play-by-play 進行時間(time)從 data["SC"]["TS"] 取得
- 節數(section)從 data["SC"]["CPS"] 取得
- play-by-play 統計項通過 pbp_mapping 字典映射
- 場地環境資訊如地點、溫度、國家、天氣、風速等分別從 data["MIS"]["K"] 的對應值取得
- 賠率玩法名稱由 data["PN"] 與 data["TG"] 拼接而成
- 賠率玩法代號映射表定義了常見玩法如 HA:1X2、讓分、OU 等

**關鍵設計決策**：
- 直接使用供應商 JSON 原始字段名進行數據映射，無中間轉換層
- 多種運動的 play-by-play 統計代碼集中在一個 pbp_mapping 字典中
- 環境信息通過 data["MIS"]["K"] 的整數值區分不同參數類型
- 賠率玩法以 raw data 的 PN 和 TG 拼接作為唯一標識

**注意事項**：
- ⚠️ 遊戲狀態(game_status)由 provider 提供，文件中未列出可能的值
- ⚠️ pbp_mapping 涵蓋多種運動的統計代碼，但未說明如何根據 game_type 篩選適用的統計項
- ⚠️ 賠率玩法表格僅提供參數拼接示例，其他玩法的 PN、TG 組合需人工確認
- ⚠️ 玩法代號列表與前面玩法名稱的對應關係沒有完整說明


### TCZB-3431 [Crawler] - HGA provider V2

> Confluence 頁面 ID：55581201
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3431+%5BCrawler%5D+-+HGA+provider+V2)
> 摘要檔：[processed/55581201-summary.md](../../confluence/processed/55581201-summary.md)
> Confluence 最後更新：2024-09-04
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了從 HGA 足球數據提供商 V2 獲取賽前、賽中、賽果數據的 API 請求方式與參數。賽前需透過三步驟；賽中可直接請求 live 比賽列表；賽果則分為主賽果頁與單場賽果，且需從主頁 HTML 判斷比賽類型。

**關鍵業務規則**：
- 賽果主頁的完整 HTML 須直接發送到 Kafka 的 result topic
- 單場賽果僅需提取頁面中 var gdata 和 var heads 陣列的資料，發送到 Kafka 的 singleresult topic
- 單場賽果必須附帶 page type 資訊，其值為 FullTime 或 Cornor（角球）
- page type 由主賽果頁 HTML 中是否包含「角球數」字樣來判斷

**注意事項**：
- ⚠️ 日期參數說明較模糊：date 欄位可為 'all'、空字串或數字，數字代表星期幾
- ⚠️ Cornor 一詞可能為 Corner 的筆誤
- ⚠️ Kafka topic 名稱、uid/ver 認證機制等上下文缺失
- ⚠️ 文件未說明此 provider V2 版本是否仍為現行版本


### TCZB-3432 [Crawler] - nowscore provider

> Confluence 頁面 ID：55581192
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3432+%5BCrawler%5D+-+nowscore+provider)
> 摘要檔：[processed/55581192-summary.md](../../confluence/processed/55581192-summary.md)
> Confluence 最後更新：2024-09-03
> 摘要最後同步：2026-05-27

**摘要**：
定義從nowscore網站爬取SC、BK、TN、BS、HL、FL、SN七種球種資料的API端點與timestamp規則。賽前、賽中、賽果及playbyplay各有對應URL，timestamp須以time模組取得一次13碼Unix毫秒值。

**注意事項**：
- ⚠️ 文件中date參數格式描述為yyyy/MM/dd，但範例中出現2024-09-02格式，不一致，需人工確認正確格式
- ⚠️ timestamp需13碼，但未說明精確到毫秒還是微秒
- ⚠️ playbyplay API需要gameID拆分規則，但未提供gameID來源


### TCZB-3450 [Crawler] - konibet providerV2

> Confluence 頁面 ID：55581300
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3450+%5BCrawler%5D+-+konibet+providerV2)
> 摘要檔：[processed/55581300-summary.md](../../confluence/processed/55581300-summary.md)
> Confluence 最後更新：2024-09-30
> 摘要最後同步：2026-05-27

**摘要**：
本文定義了從Konibet體育網站抓取賽前/賽中比賽、賠率及賽果數據的爬蟲任務，並將結果上傳至Kafka。提供了完整的API清單、頻率限制、球種與語言對映表，並標註跳過NBA2K-和FIFA-開頭的聯盟。

**關鍵業務規則**：
- 抓取時需跳過聯盟名稱以「NBA2K-」或「FIFA-」開頭的賽事
- 賽前所有比賽API限制：每分鐘最多10次請求
- 賽前主要玩法賠率API限制：每分鐘最多100次請求
- 賽中主要玩法賠率API限制：每分鐘最多10次請求
- 賽中所有比賽API限制：每分鐘最多10次請求
- 賽中單場比賽詳細資料API限制：每分鐘最多100次請求
- 賽果聯盟所有比賽API限制：每分鐘最多20次請求
- 比賽其他玩法賠率API限制：每分鐘最多30次請求
- 所有API均以GET方法呼叫，且需透過LangCode參數指定語言版本

**關鍵設計決策**：
- 採用Konibet公開API作為單一數據來源，透過路徑參數切換語言與賽事ID
- 以game_type到site code的靜態對映表進行球種分類
- 分別針對不同API端點設定呼叫頻率上限
- 過濾特定聯盟名稱前綴以排除非目標賽事

**注意事項**：
- ⚠️ 需人工確認API端點是否近期有變更
- ⚠️ 賽中主要玩法賠率API缺少具體請求參數範例


### TCZB-3451 [Crawler] PS3838 providerV2

> Confluence 頁面 ID：55581320
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3451+%5BCrawler%5D+PS3838+providerV2)
> 摘要檔：[processed/55581320-summary.md](../../confluence/processed/55581320-summary.md)
> Confluence 最後更新：2024-09-19
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了從 PS3838 體育搏彩供應商抓取賽事賠率的 API 規格，包括端點、請求頻率限制（每 2 秒 1 次）、game_type 與數值對應表，以及兩個關鍵 payload 設計。

**關鍵設計決策**：
- 採用兩個獨立 payload 請求一般盤口（btg=1）與總分盤口（btg=100），以區分不同市場類型
- 透過 mk 參數（0=早盤, 1=今天, 2=賽中）控制獲取不同時間區段的盤口資料
- v 參數設為空或 '0' 時返回比賽基礎資訊，傳入 13 位時間戳則返回特定時間點的賽況（pbp）
- sp 參數設為 '4' 代表棒球（需人工確認對應關係）

**注意事項**：
- ⚠️ API 有嚴格速率限制（每 2 秒 1 次），但文件未說明應對 429 狀態碼的重試機制或退避策略
- ⚠️ game_type 字典中部分條目被註解，可能已廢棄或暫未使用
- ⚠️ 'sp' 參數註解為「球種」，實際值為 '4'，推測為棒球，但未提供完整球種代碼表
- ⚠️ v 值的行為描述可能與實際 API 測試有出入


### TCZB-3469 [Crawler] - sbo providerV2

> Confluence 頁面 ID：55581435
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3469+%5BCrawler%5D+-+sbo+providerV2)
> 摘要檔：[processed/55581435-summary.md](../../confluence/processed/55581435-summary.md)
> Confluence 最後更新：2024-09-30
> 摘要最後同步：2026-05-27

**摘要**：
本文档定义了SBO ProviderV2爬虫的技术实现细节。核心信息包括：联盟数据必须通过比赛列表页动态加载的JS脚本URL获取，且URL包含会变动的乱码参数，不可写死；给出了游戏类型与球种代号的标准映射字典；明确了需要过滤的联盟名称列表。

**關鍵業務規則**：
- 必须忽略 ignore_league 列表中的联盟数据：["Which team", "Total Assist", "Total 3 Points Made", "Total Points", "Total Rebounds"]
- 需要处理并过滤列表数据异常情况：赛前的列表中不能出现赛中的比赛，反之亦然
- 联盟名称需要通过Kafka消息队列发送

**關鍵設計決策**：
- 联盟数据源获取方式：不采用直接调用固定API的方式，而是通过解析比赛列表HTML，提取动态JS脚本URL来获取
- 动态参数处理：JS脚本URL后的乱码参数会周期性变动，系统设计上不能将其写死在代码或配置中，必须实时从HTML解析获取全量URL再请求

**注意事項**：
- ⚠️ 联盟数据JS脚本URL的乱码参数为动态生成，硬编码会导致数据缺失
- ⚠️ 此为旧项目的文档，game_type映射表可能已过时


### TCZB-3470 [Crawler] - sbo parser V2

> Confluence 頁面 ID：55581420
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3470+%5BCrawler%5D+-+sbo+parser+V2)
> 摘要檔：[processed/55581420-summary.md](../../confluence/processed/55581420-summary.md)
> Confluence 最後更新：2024-10-04
> 摘要最後同步：2026-05-27

**摘要**：
這份文件定義了一個新的體育比賽資料解析器(SBO Parser V2)，從Kafka訊息中解析比賽基本資料、賽中分數、playbyplay以及各球種的賠率玩法代號對照表。

**關鍵業務規則**：
- game_id使用team_home、team_away、league、game_date組合後以MD5生成
- league_id與league相同，team_home_id與team_home相同，team_away_id與team_away相同
- 賽中分數：目前觀察只有SC和FL會有分數，其他球種分數為0:0
- playbyplay只有SC有提供
- scores欄位格式為[[score_home, score_away]]的陣列

**關鍵設計決策**：
- 採用MD5雜湊產生game_id，確保唯一性
- 所有資料解析直接從Kafka訊息的data欄位提取
- 賠率玩法以球種為單位，用代號對應不同的玩法類型和球頭


### TCZB-3488 [Crawler] - 188bet providerV2

> Confluence 頁面 ID：55581526
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3488+%5BCrawler%5D+-+188bet+providerV2)
> 摘要檔：[processed/55581526-summary.md](../../confluence/processed/55581526-summary.md)
> Confluence 最後更新：2024-10-16
> 摘要最後同步：2026-05-27

**摘要**：
本文详述了针对 188bet 体育网站的爬虫实现：通过模拟登录获取验证码，分赛前、赛中、赛果三条链路抓取足球比赛数据。

**關鍵業務規則**：
- 球种只抓足球，站台球种代号为 1
- 所有后端 API 请求必须携带验证码头部，否则返回 401
- 赛果数据抓取当天和昨天的页面，HTML 内容嵌入 JSON 的 data 字段
- 语系只发送英文 namemap，键固定为 "EN_SC_List"
- 赛中 HTML 切分起始标记为 "主要市场"，结束标记为 "sbk-footer-container"
- 赛前从 today 页面抓取当天所有比赛 ID，从 early 页面通过联盟 API 获取明天和后天比赛 ID

**關鍵設計決策**：
- 采用队列（queue）+线程模式分离 ID 收集与数据处理，实现并发请求
- 赛中数据使用 Selenium 抓取整页 HTML 后按固定文本标记截取
- 验证码通过模拟登录接口获取，从响应头直接提取
- 赛果数据以统一的 JSON 结构包裹原始 HTML，并附加机器名和时间戳

**注意事項**：
- ⚠️ 验证码提取未指定 header 的具体字段名，需人工确认取自哪个响应头
- ⚠️ 赛中 HTML 截取依赖页面结构，若站点改版导致标记文本变化，可能失效


### TCZB-3489 [Crawler] - tonybet providerV2

> Confluence 頁面 ID：55581516
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3489+%5BCrawler%5D+-+tonybet+providerV2)
> 摘要檔：[processed/55581516-summary.md](../../confluence/processed/55581516-summary.md)
> Confluence 最後更新：2024-10-14
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義 Tonybet 體育數據爬蟲的實作規格，包含球種、語言、比賽狀態對應表，以及取得比賽列表與單場細節的 API 端點與參數。

**關鍵業務規則**：
- 球種 ID、game_type 與 site code 的對應關係，需正確傳入 API 參數
- 語言代碼對應（en-US → en, es-ES → es, fr-FR → fr, de-DE → de）
- 比賽狀態 status_code：prematch 使用 0，inplay 使用 2
- 比賽列表 API 使用分頁（limit=500，page 從 1 開始），需循環取得所有比賽
- 單場比賽 API 必須指定 relations=league, odds, result, competitors, sportCategories, statistics 以獲得完整資訊

**關鍵設計決策**：
- 採用官方 API 直接取得結構化數據，而非網頁爬蟲
- 分兩階段 API 呼叫：先取得比賽列表，再逐一請求詳細資料
- 資料最終推送至 Kafka，便於下游服務統一消費

**注意事項**：
- ⚠️ 文件未說明 API 是否需要認證或 token
- ⚠️ 電競子分類共用 ES game_type，但 site code 不同，需特別處理映射


### TCZB-3508 [Crawler] - ladbrokes provider V2

> Confluence 頁面 ID：55581605
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3508+%5BCrawler%5D+-+ladbrokes+provider+V2)
> 摘要檔：[processed/55581605-summary.md](../../confluence/processed/55581605-summary.md)
> Confluence 最後更新：2024-10-29
> 摘要最後同步：2026-05-27

**摘要**：
本文定義了從 ladbrokes 取得賽前資料的爬蟲實作設計：先以球種 ID 請求聯盟清單，再依聯盟 ID 與時間、玩法等過濾條件取得比賽簡易資訊，最後針對單場比賽請求完整詳細資料並發布至 Kafka。

**關鍵業務規則**：
- 僅抓取賽前（pre-match）資料，不包含滾球
- 需先取得特定球種的所有聯盟 ID，才能進行後續比賽查詢
- 比賽清單 API 必須傳入多個聯盟 ID（以逗號分隔），並限制 startTime 範圍、isStarted=false
- 單場詳細資料 API 取得後以原始 JSON 格式送至 Kafka，不需再進行轉換

**關鍵設計決策**：
- 選用 OpenBet Drilldown API 2.31 版本作為資料來源
- 分三層請求：Class（聯盟）→ EventToOutcomeForClass（比賽清單）→ EventToOutcomeForEvent（單場詳情）
- 多個聯盟 ID 於比賽清單請求中直接用逗號拼接，減少 HTTP 請求數
- 使用 Kafka 發布單場完整資料

**注意事項**：
- ⚠️ 球種對應的站台代號及玩法名稱需人工確認，文件未列出完整對應表
- ⚠️ API 版本及端點可能隨 ladbrokes 平台變更


### TCZB-3509 [Crawler] - Pesa providerV2

> Confluence 頁面 ID：55581598
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3509+%5BCrawler%5D+-+Pesa+providerV2)
> 摘要檔：[processed/55581598-summary.md](../../confluence/processed/55581598-summary.md)
> Confluence 最後更新：2024-10-28
> 摘要最後同步：2026-05-27

**摘要**：
這份文件定義了 SportPesa 網站的爬蟲技術規格，包含賽前與賽中比賽資料的 API 端點、參數格式與球種代碼對照表。

**關鍵設計決策**：
- 賽前與賽中比賽皆採用兩段式查詢：先獲取比賽列表並儲存 ID，再依據該 ID 批次取得單場比賽詳細賠率
- 賽前比賽列表使用 unix timestamp 的日期範圍進行查詢過濾
- 賽中比賽列表採用分頁參數進行資料擷取
- 賽中比賽的即時動態是透過另一個不同的 domain 取得，需要獨立的 API 呼叫
- 賽果資料使用 POST 請求，並以 yesterday_timestamp 作為請求體參數

**注意事項**：
- ⚠️ 文件中未提供將資料上傳至 Kafka 的具體 topic 名稱與訊息格式
- ⚠️ 賽果資料僅列出搜尋列表 API，未提供單場賽果詳情的 API，資料擷取流程可能不完整
- ⚠️ 文件中的流程圖為圖片，無法從文字內容直接解析其具體邏輯


### TCZB-3544 [Crawler] NK Provider V2

> Confluence 頁面 ID：55581815
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3544+%5BCrawler%5D+NK+Provider+V2)
> 摘要檔：[processed/55581815-summary.md](../../confluence/processed/55581815-summary.md)
> Confluence 最後更新：2024-11-25
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義 NK998 站台爬蟲的資料擷取流程。每個球種會分配到獨立執行緒，定期呼叫 5 個 API，並每隔 10 分鐘呼叫賽果 API。賽果同時抓取今天與昨天的資料，分別以 result 和 result2 欄位輸出。

**關鍵業務規則**：
- 每個球種獨立使用一個 thread 進行資料抓取
- 每個 thread 定期呼叫下列 5 個 API：gamebase, inplay, odd_r, odd_hr, odd_re
- 每 10 分鐘額外呼叫一次 result API（賽果）
- result API 同時抓取今天與昨天的賽果，資料中 key=result 為今天，key=result2 為昨天
- 部分球種可能分多頁，需依照實際情況處理
- 使用指定的站台 game type 對應表，將站台的 game type 代碼轉換為內部使用的代碼

**關鍵設計決策**：
- 採用多執行緒設計，每個球種一個 thread，以實現並行抓取，提高效率與降低延遲
- 賽果 API 每 10 分鐘抓取一次，可能為了平衡即時性與請求頻率


### TCZB-3545 [Crawler] - crawleragentsa8888

> Confluence 頁面 ID：55581801
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3545+%5BCrawler%5D+-+crawleragentsa8888)
> 摘要檔：[processed/55581801-summary.md](../../confluence/processed/55581801-summary.md)
> Confluence 最後更新：2024-11-26
> 摘要最後同步：2026-05-27

**摘要**：
定義從 sa8888 網站爬取運動賽事基本資訊、賽中分數、playbyplay 時間及賽果附加資訊的正則表達式解析規則與欄位轉換方式。

**關鍵設計決策**：
- 基本資料欄位透過正則匹配 HTML 特定標籤擷取
- game_status 代號需經由設定檔映射為實際狀態文字
- team_home 與 team_away 由同一正則擷取所有球隊後依索引區分
- game_date 格式需將 '/' 替換為 '-'
- game_id 由 league, team_home, team_away, game_date, game_time 組合後生成雜湊值
- 賽中分數從 scoreFinal 區塊依索引解析主客隊分數
- 賽果 SC 球種時，紅黃牌無數字預設為 0；BS 球種時，安打數依類似邏輯處理

**注意事項**：
- ⚠️ game_status 代號需人工確認對應的狀態設定，文件中未提供映射表
- ⚠️ 正則表達式依賴於文件當下的 HTML 結構，若網站改版需重新驗證


### TCZB-3569 [Crawler] - AIScore provider / parser

> Confluence 頁面 ID：55581991
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55581991)
> 摘要檔：[processed/55581991-summary.md](../../confluence/processed/55581991-summary.md)
> Confluence 最後更新：2024-12-13
> 摘要最後同步：2026-05-27

**摘要**：
本文件說明如何從 aiscore.com 爬取比賽資料，使用 Selenium 自動化瀏覽器。因比賽列表為動態載入，需要滾動頁面逐批獲取賽前、賽後及即時比賽。文中定義了針對不同球種的輪流爬取邏輯，以及 inplay 與非 inplay 頁面的滾動與抓取頻率規則。

**關鍵業務規則**：
- 爬蟲必須使用 Selenium 開啟瀏覽器，分別抓取賽中、賽前、賽後頁面
- 因比賽資料為動態載入，需通過滾動頁面觸發加載以獲取所有比賽
- 賽前與賽後頁面每隔 10 輪次才抓取一次
- inplay 頁面每輪皆抓取，抓取流程為：先處理 A 球種 inplay，再處理 B 球種 inplay
- 比賽 ID 需通過組合方式生成，具體組合規則未於本文件詳述
- 比賽狀態使用 provider 提供的 page_type 決定

**注意事項**：
- ⚠️ 比賽 ID 的生成方式僅提及「用組的」，無具體規則，需要參考其他文件或程式碼
- ⚠️ playbyplay 欄位的 HTML 結構在其他球種中可能不同，實作時需要驗證並對應調整
- ⚠️ 滾動頁面的 inplay 流程描述為「比較不一樣」，但未提供具體差異細節


### TCZB-3586 [Crawler] - CrawlerAgentUba

> Confluence 頁面 ID：55582122
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3586+%5BCrawler%5D+-+CrawlerAgentUba)
> 摘要檔：[processed/55582122-summary.md](../../confluence/processed/55582122-summary.md)
> Confluence 最後更新：2024-12-24
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了 CrawlerAgentUba 從 uba.tw 擷取大專籃球聯賽資料的技術規格，區分一級與二級比賽頁面，詳細列出每個欄位的 HTML 來源、資料格式轉換、計算方式及狀態判斷邏輯。

**關鍵業務規則**：
- 抓取日期範圍為昨天到後天
- league 欄位由固定字串「UBA大專籃球聯賽」加上 provider.py 傳入的 page_type 組合成
- 一級比賽的 game_id 取自 schedule 連結的 scheduleId 查詢參數；二級比賽無原生 ID，需自行生成
- 一級比賽狀態直接由 data-status 屬性決定；二級比賽狀態由分數陣列判斷
- 一級比賽主客得分由每節分數加總得到，二級比賽僅有總分，無單節明細
- 二級比賽的 game_date 因 HTML 中不含年份且處理繁瑣，直接使用爬蟲執行時的系統日期
- 遊戲時間 game_time 需從 12 小時制轉換為 24 小時制

**關鍵設計決策**：
- 二級比賽 game_date 不從頁面解析，改用系統時間，避免因缺乏年份資訊導致日期錯誤
- 二級比賽無唯一 game_id，採用自定義組合字串來識別
- 一級比賽總分由各節分數獨立加總計算

**注意事項**：
- ⚠️ 二級比賽 game_id 的生成規則僅給出範例，未說明組合邏輯
- ⚠️ 二級比賽狀態判斷的邊界條件：已達開打時間但分數仍為 0 時，會維持「賽前」狀態
- ⚠️ 文內截圖無法直接查看，實際 HTML 結構若有變動可能導致規則失效


### TCZB-3587 [Crawler] - CrawlerAgentHbl

> Confluence 頁面 ID：55582098
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3587+%5BCrawler%5D+-+CrawlerAgentHbl)
> 摘要檔：[processed/55582098-summary.md](../../confluence/processed/55582098-summary.md)
> Confluence 最後更新：2024-12-23
> 摘要最後同步：2026-05-27

**摘要**：
本文档说明了爬取HBL高中篮球联赛赛程与比分数据的技术方案：给出目标网站与5个REST API端点，详细列出从API响应中提取比赛、队伍、分数等字段的JSON路径与清洗规则，并规定只抓取当前日期前后两天内的比赛。

**關鍵業務規則**：
- 比赛状态映射：status=2 代表赛前，status=0 代表赛中，status=1 代表赛果
- 联赛名称拼接规则：league = '高中籃球甲級聯賽' + division（去除'A '、'B '和'外卡'后的部分）+ stageName
- 比赛日期过滤：以当前日期为基准，只抓取前后两天的比赛
- 各节分数：根据current_quarter决定取几节分数

**注意事項**：
- ⚠️ 比赛日期过滤建议明确是包含当天及前后各两天共5天，或仅前后两天不含当天
- ⚠️ league字段中去除'A '、'B '和外卡文字，但未说明'外卡'的具体出现形式与位置


### TCZB-3588 [Crawler] - CrawlerAgentUbl

> Confluence 頁面 ID：55582158
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3588+%5BCrawler%5D+-+CrawlerAgentUbl)
> 摘要檔：[processed/55582158-summary.md](../../confluence/processed/55582158-summary.md)
> Confluence 最後更新：2024-12-25
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了 CrawlerAgentUbl 從 UBL 棒球聯賽網站爬取比賽數據的技術設計。流程為：由外部 provider 提供 game_id 與 league 資訊，爬蟲進入特定比賽頁面，使用正則表達式解析 HTML 內容。

**關鍵設計決策**：
- 選擇直接對 HTML 原始碼使用正則表達式擷取資料，而非 DOM 解析或 API
- game_id 與 league 由外部 provider 提供，爬蟲自身不負責探索或管理比賽清單
- 比賽狀態透過判斷頁面內容中是否出現特定字串來決定
- 主客隊名稱與分數靠正則匹配結果的索引區分

**注意事項**：
- ⚠️ game_id 與 league 由 provider 提供的機制需人工確認
- ⚠️ 主客隊分數的正則匹配後索引與直覺相反，實作時須特別標注避免對調
- ⚠️ 各節分數解析未區分主客，可能僅為一段連續分數列表
- ⚠️ 文件中的螢幕截圖連結已失效


### TCZB-3155 [Crawler]-CrawlerAgentPleague

> Confluence 頁面 ID：55582319
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3155+%5BCrawler%5D-CrawlerAgentPleague)
> 摘要檔：[processed/55582319-summary.md](../../confluence/processed/55582319-summary.md)
> Confluence 最後更新：2025-01-08
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義一個爬蟲從 P. League+ 官網抓取比賽資料的技術規範。內容說明了從賽程頁面提取比賽詳細頁面 URL 的方法，以及從比賽頁面中透過正則表達式擷取各欄位的規則。

**關鍵業務規則**：
- 比賽狀態值映射: HTML 中的「尚未開始」→ '2', 「LIVE」→ '0', 「已完賽」→ '1'
- 聯盟名稱映射: HTML 中擷取的 'PLG' → 'Plus League', 'EASL' → '東亞超級聯賽'
- game_id 組合規則: {league_id}_{比賽日期年份}_{從 window.gid 擷取的數字 ID}
- 每節分數擷取規則: 依序匹配多個 score_home 與 score_away，組合成 tuple 列表
- 比賽詳細頁面 URL 規則: 從賽程頁中擷取所有符合模式的連結作為標的頁面

**關鍵設計決策**：
- 選擇解析 HTML 而非使用結構化 API：因為目標網站未提供正式 JSON API，故以 HTML 匹配正則表達式提取資料
- 入口設計：以多個 schedule 頁面為清單來源，再逐一爬取比賽細節
- game_id 組合設計：使用人工可讀的格式，以便於後續資料庫儲存與人工識別

**注意事項**：
- ⚠️ 爬蟲依賴官網 HTML 結構，若 PLG 網站改版，本文件的正則表達式可能失效
- ⚠️ 比賽狀態的對應值未見於官網文件，為內部約定
- ⚠️ 聯盟名稱映射目前僅有 PLG 與 EASL，若未來新增其他聯盟，爬蟲需額外擴充


### TCZB-3604 [Crawler] - CrawlerAgentSbl

> Confluence 頁面 ID：55582282
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3604+%5BCrawler%5D+-+CrawlerAgentSbl)
> 摘要檔：[processed/55582282-summary.md](../../confluence/processed/55582282-summary.md)
> Confluence 最後更新：2025-01-06
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了從 SBL 後端 GraphQL API 擷取資料的完整流程，包含三個步驟：取得聯盟 ID與事件/組別列表、根據組別 ID 取得比賽列表與比賽 ID、再根據比賽 ID 取得單場詳細資料。

**關鍵業務規則**：
- 比賽狀態對應：NOT_STARTED → 2，COMPLETED → 1，IN_PROGRESS → 0
- 比賽日期時間取自 matchedAt 欄位，需從 UTC 時區轉換為 GMT+8
- 比賽 ID 的儲存格式為 'SBL_年份_比賽ID'
- 比賽各節分數由 homeSquadRoundScores 與 awaySquadRoundScores 兩個列表配對產生
- 聯盟名稱由 '超級籃球聯賽_第X季_例行賽' 格式組成

**關鍵設計決策**：
- 採用單一 GraphQL 端點，透過不同 operationName 區分查詢類型
- 資料擷取分三階段進行：先取得聯盟與組別 ID，再取得比賽列表，最後取得單場詳細資料

**注意事項**：
- ⚠️ 年份來源未明確：game_id 中的年份推測來自 matchedAt，但文件未清楚說明提取規則
- ⚠️ 節分數組合邏輯：roundScores 中的 round 欄位排序可能不保證與節次一致


### TCZB-3605 [Crawler] - 美嘉站台 MCProvider / CrawlerAgentMc

> Confluence 頁面 ID：55582300
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55582300)
> 摘要檔：[processed/55582300-summary.md](../../confluence/processed/55582300-summary.md)
> Confluence 最後更新：2025-06-30
> 摘要最後同步：2026-05-27

**摘要**：
這份文件記錄了美嘉站台（MC766）爬蟲 MCProvider / CrawlerAgentMc 的技術實作細節，包含支援的球種清單、資料抽取 API 的端點與 payload 參數設定，以及解析比賽資料時對應的 JSON 欄位路徑。

**關鍵業務規則**：
- 所有 API 請求的 oddsType 一律使用 3（歐洲盤），因為其他盤口頁面存在 bug
- 足球（sportId=1）和籃球（sportId=2）只抓比賽列表，不需要透過單場比賽 API 請求賠率
- 除足球、籃球外的球種必須對每場比賽使用單場比賽 API 請求才能取得賠率
- 走地比賽列表的 pageSize 統一設為 999，今日與早盤則設為 10
- 早盤比賽可透過 selectDate 參數指定日期，1 代表明天，2 代表後天
- 賽果資料僅支援足球和籃球，其餘球種無賽果 API
- 比賽狀態由 game_data['isb'] 決定：0 表示 pregame，1 表示 inplay
- 網域名稱無法解析時，代表站台可能已更換 domain，需手動調整

**關鍵設計決策**：
- 因美嘉站台的香港盤等頁面存在 bug，故強制所有 request 使用 oddsType=3（歐洲盤）
- 足球與籃球的賠率在比賽列表中已涵蓋較多盤口，為減少請求數量與效能負擔，設計為僅擷取列表
- 走地比賽為了減少分頁請求，pageSize 特別設定為 999
- Game ID 採用 hash 組合而成，但文件未揭露具體組成方式

**注意事項**：
- ⚠️ 2025/6/30 觀察到 API 回應 502/503，美嘉站台可能已故障或改版
- ⚠️ 網域名稱變更時需手動更新
- ⚠️ 分數解析的 mo 字典中，不同球種所用的 key 值不一致，實作時需針對各球種獨立處理
- ⚠️ Game ID 的 hash 演算法未明確給出


### TCZB-3610 [Crawler] - CrawlerAgentPanda

> Confluence 頁面 ID：55582393
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3610+%5BCrawler%5D+-+CrawlerAgentPanda)
> 摘要檔：[processed/55582393-summary.md](../../confluence/processed/55582393-summary.md)
> Confluence 最後更新：2025-01-10
> 摘要最後同步：2026-05-27

**摘要**：
本文件說明 CrawlerAgentPanda 如何從多個娛樂城平台統一登入後，再進入「熊貓體育」爬取資料。關鍵點在於登入後只需取得 requestId、cuid、host 三項資訊即可進行 API 請求，不必保持瀏覽器連線。

**關鍵業務規則**：
- 新平台加入時需測試爬取速度與支援球種，速度慢或缺球種者直接排除不用
- 僅使用成功進入「熊貓體育」的平台，日本地區因無法進入熊貓體育，其 VM 需被跳過
- 大老爺娛樂城的帳號在 DB 中必須以平台代號為前綴，格式為「代號_電話號碼」

**關鍵設計決策**：
- 選擇僅依賴 requestId、cuid、host 進行後續資料抓取，不需保持瀏覽器會話
- 程式中加入判斷邏輯，自動跳過開啟日本 VPN 的 VM 以及效能較弱的機器
- DB 帳號格式使用「平台代號_帳號」的規範

**注意事項**：
- ⚠️ 目前使用的平台清單可能已有變動，需核對試算表最新版
- ⚠️ 大老爺娛樂城的帳號/電話/密碼範例僅供參考


### TCZB-3628 [Crawler] - CrawlerAgentAipredict

> Confluence 頁面 ID：55582731
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3628+%5BCrawler%5D+-+CrawlerAgentAipredict)
> 摘要檔：[processed/55582731-summary.md](../../confluence/processed/55582731-summary.md)
> Confluence 最後更新：2025-02-11
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了 CrawlerAgentAipredict 從四個外部網站爬取 NBA AI 預測資料的技術實作細節。包括各網站 AI 預測的大小分與讓分在 JSON 中的確切欄位路徑與解析規則，以及 game_id 的組合規則。

**關鍵設計決策**：
- 使用 page_type 參數讓 DataTransformer 區分不同資料來源的解析邏輯
- league 參數採用「網站名稱_聯盟名稱」組合
- game_id 由 league、team_home、team_away、game_date、game_time 五個欄位組合而成
- other_info 欄位以 JSON 格式儲存 AI 預測結果
- sportsline：從 HTML 內嵌的 competitions JSON 區塊提取比賽清單
- oddstrader：從 window.__INITIAL_STATE__ 全域變數提取資料
- dimers：從特殊 JSON 結構提取比賽資料
- picksandparlays：透過 API 直接獲取 JSON

**注意事項**：
- ⚠️ picksandparlays 的 URL rangeStart=0&rangeEnd=4 看起來是測試用的分頁範圍
- ⚠️ 四個資料來源的網站皆為外部第三方，HTML 結構或 API 格式隨時可能變動
- ⚠️ bet_OU 欄位在文件中註明是「測試時需要」，正式環境是否仍需要此欄位需人工確認


---

## 歷史決策類

### TCZB-3950 [Crawler] - 90vs 賽事分析 (部署變更)

> Confluence 頁面 ID：79464944
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464944)
> 摘要檔：[processed/79464944-summary.md](../../confluence/processed/79464944-summary.md)
> Confluence 最後更新：2025-10-16
> 摘要最後同步：2026-05-27

**決策背景**：
90vs 爬蟲為支持賽事分析功能，新增了比賽對陣記錄、主客隊近期戰績和心水推介的抓取功能。

**決策結論**：
- 使用 Selenium 請求完整 match_list 頁面，從中解析出每場比賽的 game_id，再透過內部 JS 檔案獲取單場詳細資料
- 將新增的賽事分析數據以 prediction 類型透過 Kafka 傳送
- 心水推介內容以文字檔寫入伺服器

**影響**：
- 部署位置已多次變更（原在 SRV32/SRV33，後移至 SRV35，再移至 SRV30）
- 抓取頻率可能已根據賽事數量調整


### TCZB-1030 [CrawlerAgent]-Study 凱利公式

> Confluence 頁面 ID：24085675
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24085675)
> 摘要檔：[processed/24085675-summary.md](../../confluence/processed/24085675-summary.md)
> Confluence 最後更新：2021-09-14
> 摘要最後同步：2026-05-27

**決策背景**：
這是一份早期研究文件，探索如何利用歷史賽前賽後資料模擬下注，並套用凱利公式計算獲利。

**決策結論**：
- 決定先由歷史資料的賽前與賽後資料模擬下注，再套入凱利公式計算獲利（此為待研究構想）
- 凱利公式 f* = (bp - q) / b，其中 b 為賠率，p 為獲利機率，q 為虧損機率

**影響**：
- 文件中的規則和設想可能已被後續開發實現或廢棄
- 提到的獲利機率 p 並未在文件中定義如何從歷史數據取得或估算

**注意事項**：
- ⚠️ 文件標題為「Study 凱利公式」，內容為早期研究工作，最後更新於2021年
- ⚠️ 所有讓球盤口規則皆為示例，並非完整的運動博弈規則規範


### TCZB-2084 [SportSite]-時區

> Confluence 頁面 ID：40502116
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40502116)
> 摘要檔：[processed/40502116-summary.md](../../confluence/processed/40502116-summary.md)
> Confluence 最後更新：2022-09-13
> 摘要最後同步：2026-05-27

**決策背景**：
本文件為SportSite時區功能的需求記錄，目標是讓inplay、pregame、hotgame及分析時間依照使用者選擇的時區顯示。

**決策結論**：
- inplay、pregame、hotgame的比賽時間必須根據使用者選擇的時區動態轉換顯示
- 分析時間也必須根據使用者時區調整
- 時區選項應包含文件所列的UTC偏移清單（從UTC-12:00到UTC+14:00）
- result日期選單不套用使用者時區設定，固定以+8時區顯示

**關鍵設計決策**：
- 決定參照1xbet的時區清單作為可選時區範圍
- result頁面不支援時區切換，原因是提示標記為+8

**注意事項**：
- ⚠️ 文件最後更新於2022年9月，時區規則或支援範圍可能已變更
- ⚠️ 時區列表為直接參照1xbet，後續可能根據實際業務調整
- ⚠️ result不支援時區設定的決策需要確認是否仍生效，或後續已加入支援


### playbet provider review

> Confluence 頁面 ID：79470555
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/playbet+provider+review)
> 摘要檔：[processed/79470555-summary.md](../../confluence/processed/79470555-summary.md)
> Confluence 最後更新：2026-04-21
> 摘要最後同步：2026-05-27

**摘要**：
這份文件記錄了對 playbet provider 程式碼的審查決策，重點在於簡化代碼與避免資源洩漏。

**關鍵業務規則**：
- 所有變數必須被使用，未使用的變數應立即移除
- 當邏輯僅需兩行程式碼時，不應封裝成獨立函數，應直接內聯處理
- 避免引入中間變數暫存資料結構，尤其在需要清理的場景
- 發送 Kafka 訊息後，必須確保相關的資料結構都已被清空或重設
- 開發環境應配置自動移除行尾空格，並開啟存檔時自動格式化功能

**關鍵設計決策**：
- 決定移除未使用的變數，因為它們增加維護成本且無實際功能
- 決定將「分頁 key + 補隊伍 key」邏輯內聯
- 決定避免使用 to_send 這類中間變數
- 決定統一使用 Trailing Spaces 插件並啟用自動格式化


---

## 操作手冊類

### KU 爬蟲抓取清單 (操作部分)

> Confluence 頁面 ID：18645183
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=18645183)
> 摘要檔：[processed/18645183-summary.md](../../confluence/processed/18645183-summary.md)
> Confluence 最後更新：2021-04-29
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- SC Inplay、BS Inplay、BK Inplay、BK Pregame、BS Pregame 的具體爬取範圍以截圖形式存在
- BS Future 僅在每日 8:00 至 12:00 期間執行爬取
- SC Future、BK Future 無需爬取
- Top League 爬取規則比照 SC 處理


### TCZB-3834 [VLSportProvider] - 緯來 CPBL/MLB 賽事轉播資訊

> Confluence 頁面 ID：79463188
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463188)
> 摘要檔：[processed/79463188-summary.md](../../confluence/processed/79463188-summary.md)
> Confluence 最後更新：2025-07-23
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- 從緯來體育官網抓取 CPBL 與 MLB 賽事轉播資訊
- 流程：先從首頁取得各聯盟專區的連結，再從專區頁面爬取當日比賽清單

**注意事項**：
- ⚠️ 文件仰賴截圖說明，截圖中的實際 HTML 結構或 API 可能已變動
- ⚠️ 爬取流程未提及反爬或資料授權限制


### TCZB-3856 [EltaottSport] - 愛爾達賽事資訊

> Confluence 頁面 ID：79463283
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463283)
> 摘要檔：[processed/79463283-summary.md](../../confluence/processed/79463283-summary.md)
> Confluence 最後更新：2025-07-29
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- 從愛爾達OTT取得體育賽事節目資訊
- 提供單一API端點取得全部節目，再依日期和指定的聯盟進行篩選

**注意事項**：
- ⚠️ 文件附有操作截圖，但無法從內容中取得完整資訊
- ⚠️ 未提及API請求頻率限制、資料更新週期或錯誤重試機制


### TCZB [CrawlerAgent] - KU888 桌球-TB 羽球-BM 撞球-SN 手球-HB 水球-WP

> Confluence 頁面 ID：36995251
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=36995251)
> 摘要檔：[processed/36995251-summary.md](../../confluence/processed/36995251-summary.md)
> Confluence 最後更新：2022-06-21
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- 主機路徑 WinSCP 192.168.55.20
- 各爬蟲監控頻率詳見監控系統文件
- DB 數量計算透過 pricecenter API
- 檔案命名規則：{站台}{類型}_{比賽ID}{副檔名}（具體格式需人工確認）

**注意事項**：
- ⚠️ PTT article 與 Live 文章目前透過 DB 或內容區分，具體方式需人工確認
- ⚠️ 7m.com 熱門聯盟統計基於 2025/06-2025/11 期間，若後續變更需重新統計


### TCZB-3837 [AI預測爬蟲] - WNBA賽事預測

> Confluence 頁面 ID：79463252
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463252)
> 摘要檔：[processed/79463252-summary.md](../../confluence/processed/79463252-summary.md)
> Confluence 最後更新：2025-07-30
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- game_id 生成規則：MD5(聯盟+主隊+客隊) 前10碼加日期
- forebet 籃球賽後資料寫入需針對 game_type='BK' 做分支處理
- oddstrader 目前無 WNBA 賠率，OtherInfo 內容為空
- scores24 除了 DB 寫入外，另將 AI 預測文章存為檔案

**注意事項**：
- ⚠️ Sportspunter、Scores24 抓取多種聯盟，WNBA 是本次新增
- ⚠️ Forebet 棒球與籃球賽後欄位結構不同
- ⚠️ Oddstrader 若日後站台開出賠率，OtherInfo 結構會變動


### TCZB-4002 [NHL] - NHL官網賽事即時資訊

> Confluence 頁面 ID：79465689
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465689)
> 摘要檔：[processed/79465689-summary.md](../../confluence/processed/79465689-summary.md)
> Confluence 最後更新：2025-10-23
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- Game Stats 數據已在 score_cache JSON 內，不需額外請求
- teamGameStats 中的 category 值作為統計項目標識
- 資料落盤分兩處：local 儲存於 D://GameData，PRD 則透過 WinSCP 上傳

**注意事項**：
- ⚠️ 文件標題雖提及 TCZB-4002，但內文引用 TCZB-209 和 TCZB-3050
- ⚠️ teamGameStats 的 category 與 send_data 的 type 對應關係僅給出範例，未列出完整映射表
- ⚠️ send_data 範例中的 Time 欄位採 '4H 00:00' 字串格式，at_time 為 Unix timestamp，兩者語意可能不同


### TCZB-2577[CrawlerAgent] - betradar爬取多天資料

> Confluence 頁面 ID：47219766
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47219766)
> 摘要檔：[processed/47219766-summary.md](../../confluence/processed/47219766-summary.md)
> Confluence 最後更新：2023-03-22
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- Betradar event_fullfeed API 路徑中的整數參數表示相對日期偏移：0 = 當天，1 = 隔天，-1 = 前一天
- 將 API 改造為可格式化模板（使用 {} 佔位）的方式，以便動態傳入天數參數，實現多天賽事資料的爬取


### TCZB-3199 [Crawler] - 台灣運彩provider

> Confluence 頁面 ID：55578776
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55578776)
> 摘要檔：[processed/55578776-summary.md](../../confluence/processed/55578776-summary.md)
> Confluence 最後更新：2024-05-23
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- 使用單一 API 端點並以 POST 傳遞 payload，通過 cloudscraper 繞過 Cloudflare
- payload 中的 contentId 隨不同功能改變 type 與 id 組合
- pregame 需 5 步 API 取得完整數據
- inplay 需 3 步獲得即時比賽
- 賽果資料每 2 分鐘輪詢，同一場比賽只發送一次到 Kafka

**注意事項**：
- ⚠️ 文件最後更新於 2024-05-23，需人工確認 target API 與 cloudscraper 仍可正常運作


### TCZB-3244 [Crawler] - 7M籃球抓取

> Confluence 頁面 ID：55578456
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55578456)
> 摘要檔：[processed/55578456-summary.md](../../confluence/processed/55578456-summary.md)
> Confluence 最後更新：2024-05-09
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- 區分籃球（BK）與足球（SC）的不同路徑
- league_id 與 league 必須從賽事 API 獲得，而非從其他 API 直接取得
- game_status 欄位含義：'2' 代表賽前，'0' 代表賽中，'1' 代表賽果，'4' 代表取消
- 數據源採用 7m.com.cn 的 .js 檔案格式而非 HTML 解析

**注意事項**：
- ⚠️ {tomorrow} 與 {yesterday} 的日期格式不同，需注意實作時的轉換
- ⚠️ 文件中的 API 範例網址包含硬編碼日期，需確認是否需要動態代入參數
- ⚠️ 'game_info' 陣列的索引順序可能依 7M 網站變動


### TCZB-3246 [Crawler] - footballant抓取聯盟 隊伍訊息

> Confluence 頁面 ID：55578460
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55578460)
> 摘要檔：[processed/55578460-summary.md](../../confluence/processed/55578460-summary.md)
> Confluence 最後更新：2024-04-29
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- 透過 cloudscraper 繞過 Cloudflare 防護
- 使用正則表達式從網頁 HTML 中提取聯盟 ID 與隊伍 ID
- 檔案存放路徑依語言（zh/en）與資料類型（league/team）區分

**注意事項**：
- ⚠️ 正則表達式高度依賴 footballant 網站當前的 HTML 結構，網站改版可能導致匹配失效
- ⚠️ 聯盟介紹並非所有聯盟都有，需處理不存在的情況


### TCZB-3256 [Crawler] - footballant provider

> Confluence 頁面 ID：55578572
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3256+%5BCrawler%5D+-+footballant+provider)
> 摘要檔：[processed/55578572-summary.md](../../confluence/processed/55578572-summary.md)
> Confluence 最後更新：2024-05-07
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- 賽前資料透過 API 直接指定日期（今天與明天）取得
- 賽中資料呼叫 getMatchListByState API，傳入狀態參數
- 賽後資料則從頁面以正則表達式擷取 class="matchInfo" 區塊
- 多語言站台及其 API 語言代號對照，越南文無對應 API 代號

**注意事項**：
- ⚠️ 文件內附圖片可能包含重要資料格式或範例，但未提供內容
- ⚠️ 越南文無對應站台 API 代號，使用 vi-VN 時需確認是否有替代方案
- ⚠️ 文中部分 API 參數可能隨 footballant 改版變動


### TCZB-3257 [Crawler] - footballant抓取

> Confluence 頁面 ID：55578642
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55578642)
> 摘要檔：[processed/55578642-summary.md](../../confluence/processed/55578642-summary.md)
> Confluence 最後更新：2024-05-14
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- page_type 參數用來標示比賽狀態（賽前、賽中、賽果），爬蟲需根據不同狀態對應不同的資料結構
- 賽中資料的 team_home_id 與 team_away_id 需從圖片來源字串中取出數字
- 賽果資料的 league_id 需使用正則表達式從 href 屬性中抓取
- start_time 欄位應用於計算 playbyplay 的相對時間

**注意事項**：
- ⚠️ 文件中的圖片無法顯示，需人工確認對應的 JSON 結構或 HTML class name 是否仍然存在
- ⚠️ 賽前 game_id 從 ScheduleID 取得，賽中則從 matchId 取得，命名不一致
- ⚠️ team_home_id 與 team_away_id 的提取方式依賴圖片 URL 的格式


### TCZB 3271 [Crawler] - 台灣運彩parser

> Confluence 頁面 ID：55578909
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55578909)
> 摘要檔：[processed/55578909-summary.md](../../confluence/processed/55578909-summary.md)
> Confluence 最後更新：2024-08-16
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- 赛前与赛后使用不同的数据来源路径：赛前直接从 data 字段取值，赛后需进入 html['settledevents'][0]
- 比赛ID统一从 data['externalreference'] 中提取数字部分
- 赛前比赛时间使用 data['tsstart']，赛后则使用 html['tsrealstart']
- 主客队名称在赛前与赛后使用不同的字段名
- 每种运动的每个玩法通过 idefmarkettype 数值进行唯一识别
- JSON 输出的 key 命名规则按玩法类别区分：HA、OU、Others-XXX
- 上半场玩法统一使用 Half 前缀、第一节使用 1st Quarter/1Inn 前缀

**注意事項**：
- ⚠️ 文件为旧 Projects 1-200 范围，可能已是旧版爬虫逻辑
- ⚠️ 图片附件内容无法读取，文件中有多处关键信息以截图展示
- ⚠️ 部分玩法 JSON 格式有语法错误


### TCZB-3301 [Crawler] - betsapi ES 爬取

> Confluence 頁面 ID：55579286
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55579286)
> 摘要檔：[processed/55579286-summary.md](../../confluence/processed/55579286-summary.md)
> Confluence 最後更新：2024-05-30
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- betsapi 的 team_to_win 欄位對應內部獲勝者玩法
- Match Handicap(1.5) 對應讓分盤，讓分數值需從 api key 名稱中解析
- Total_maps(2.5) 的 O 和 U 分別對應大小盤的 Over 和 Under
- 三種玩法的數據最終皆輸出至 match_lines 結構
- 利用 api key 名稱直接辨識玩法與盤口數值

**注意事項**：
- ⚠️ 文件中的圖片連結無法直接檢視，可能缺少部分對應細節
- ⚠️ 未提及賠率刻度或轉換規則


### TCZB-3321 [Crawler] - AU8賽果修正

> Confluence 頁面 ID：55579632
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55579632)
> 摘要檔：[processed/55579632-summary.md](../../confluence/processed/55579632-summary.md)
> Confluence 最後更新：2024-06-13
> 摘要最後同步：2026-05-27

**AI 開發需要注意的部分**：
- 賽果 GID 由 gtime、gdate、league、team 四個欄位組合而成
- 球種 BS 一場比賽會有三種結果，應忽略部分資料
- 球種 HL 有兩個分數需分別處理
- TN（網球）的總分需從「盤」資料取得
- VB（排球）的總分需從非「分數」的欄位取得
- scores 格式依球種不同

**注意事項**：
- ⚠️ ES、HL、MA 三種球種的 score_home/away 說明需人工確認實際來源格式
- ⚠️ BS 的取消狀態尚未獲得實例驗證
- ⚠️ TN 和 VB 等球種的總分擷取方式與多數球種不同