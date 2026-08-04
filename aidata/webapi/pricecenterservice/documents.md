# pricecenterservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-28 00:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### PlayMode Mapping List

> Confluence 頁面 ID：11436217
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/PlayMode+Mapping+List)
> 摘要檔：[processed/11436217-summary.md](../../confluence/processed/11436217-summary.md)
> Confluence 最後更新：2026-02-11
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了 PriceCenter 服務中所有標準化 PlayMode 代碼（如 HA、OU、Correct Score 等）及其對應的繁體中文名稱，並詳列每種玩法在 30 多家供應商（如 B365、KU、Bwin 等）的支援情況。區分 PreGame 和 InPlay 兩大情境，註明每個玩法適用的運動類別，特殊狀況則以備註補充。這對 AI 開發而言是解析數據源、過濾可用玩法、建立前端顯示中文選單的必要參考字典。

**關鍵業務規則**：
- PreGame 狀態下，Asian Handicap 的 PlayMode 代碼為 HA，大部分供應商支援（O 表示支援，空白表示不支援）
- 罰牌讓分 (CardHA)、罰牌大小 (CardOU)、角球讓分 (CornerHA) 僅適用於足球類賽事
- 籃球類賽事的單節讓分/大小/單雙（1st Quarter HA/OU/OddEven）僅部分供應商提供，需檢查對應欄位
- 供應商 ps3838 在 Dota 類地圖玩法中，會同時產出「比賽輸贏盤」和「擊殺輸贏盤」，PlayMode key 不同，實作時須區分處理
- InPlay 玩法的代碼通常加上 RB 前綴（如 RBHA、RBOU），與 PreGame 代碼區別
- 每個 PlayMode 均有對應的繁體中文名稱，前端顯示時應以此為準

**注意事項**：
- ⚠️ Δ 符號的具體含義文件中未說明，可能代表「部分支援」或「有條件支援」，會影響篩選邏輯，需向業務方確認
- ⚠️ 表格中部分欄位空白不代表該供應商未接入，可能為文件尚未更新，應以實際 API 回應為準
- ⚠️ ps3838 的電競 Dota 類備註提到有兩種輸贏盤，若未區分可能導致數據歸類錯誤

---

### B365 PlayByPlay Mapping List

> Confluence 頁面 ID：11436422
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/B365+PlayByPlay+Mapping+List)
> 摘要檔：[processed/11436422-summary.md](../../confluence/processed/11436422-summary.md)
> Confluence 最後更新：2020-12-01
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義 B365 賽事 PlayByPlay 事件名稱與繁體中文及 ZBDigital 代碼的對照表。對於需要解析或展示 B365 即時事件數據的服務，可根據此表進行統一名稱轉換。文件最後更新於 2020 年，需注意可能缺少後續新增的事件類型。

**關鍵業務規則**：
- 當系統接收 B365 事件代碼時，依此表查找對應繁體中文顯示文字，若繁體中文欄位為空則直接使用 ZBDigital 欄位或原始 B365 事件名稱
- 傷停時間事件（1 Mins ~ 12 Mins）統一轉為繁體中文「傷停時間」，ZBDigital 保持原數字加 Mins
- 事件「Bet365該畫面沒有任何資訊」為特殊事件，對應繁體中文「無」及 ZBDigital「None」

**注意事項**：
- ⚠️ 文件最後更新於 2020-12-01，距離現在已逾 4 年，B365 事件可能已有新增或變更，此表可能不完整
- ⚠️ 多個事件（如 Goal、Half Time 等）繁體中文欄位為空，需人工確認是否應補充中文或維持現狀

---

### B365 PlayByPlay對應

> Confluence 頁面 ID：11436242
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=11436242)
> 摘要檔：[processed/11436242-summary.md](../../confluence/processed/11436242-summary.md)
> Confluence 最後更新：2020-12-03
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了 B365 的 PlayByPlay 資料如何對應到 PriceCenter 系統中的 Event 與 Team 欄位。核心重點是：部分賽事（如電競）資料不完整、Team 欄位可能為空（因事件為兩隊共通）、以及只提供 Live 類型資料。特別需要注意例外狀況：當 B365 無提供及時比賽狀況時，PriceCenter 可能會有比賽時間但 Event 為 None 的情況，AI 處理這類資料時需要具備容錯機制。

**關鍵業務規則**：
- PlayByPlay 資訊完整度需參考 B365 對應賽事的資料完整性，電競類賽事資料可能不完整
- Team 欄位在部分情況下可為空，但 Event 欄位有值，這表示場上發生的事件是兩隊共通的（例如中場休息、比賽結束）
- PlayByPlay 資訊內容目前只提供 Live 類型資料，不提供 Scorers、Info、Summary、Table 類型
- 當 B365 未提供及時比賽狀況時，PriceCenter 可能出現「有比賽時間但無 Event 或 Event 為 None」的例外情況

**注意事項**：
- ⚠️ 文件最後更新於 2020-12-03，距今已超過三年，需人工確認 B365 的 PlayByPlay 資料格式是否仍有「只提供 Live」的限制
- ⚠️ 例外狀況表格中「B365情況」欄位只有截圖而無文字說明，需人工確認截圖內容並補上文字描述

---

### Vbet 特殊玩法列表

> Confluence 頁面 ID：40502531
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40502531)
> 摘要檔：[processed/40502531-summary.md](../../confluence/processed/40502531-summary.md)
> Confluence 最後更新：2022-09-28
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件列出 Vbet 支援的各種特殊體育投注玩法，包含分鐘進球、罰牌、角球、球員及組合玩法等類別。每個玩法均提供英文/中文名稱、玩法類型及下注類型（如 HA、OU、YES/NO 等）。對 AI 開發的幫助在於提供完整的市場玩法分類與投注選項結構。

**關鍵業務規則**：
- 所有 Vbet 特殊玩法均須定義「已新增」狀態（O 表示已啟用）、英文名稱、中文名稱、玩法類型、下注類型
- 玩法類型包括：分鐘、罰牌、角球、球員、組合等多種分類
- 下注類型涵蓋：HA（讓球/讓牌）、OU（大小）、YES/NO（是/否）、三選項、主隊/客隊、雙勝彩等
- 同一玩法類型下可有多個時間區段的子玩法，需根據名稱中的時間範圍區分
- 組合玩法將多種獨立事件結合成單一市場（例如「Winner, Corners and Yellow Cards」）

**注意事項**：
- ⚠️ 部分玩法僅有英文名稱，未提供中文名稱與下注類型，可能為開發中的項目或資料缺漏
- ⚠️ 最後更新時間為 2022-09-28，後續可能已有新增或修改的玩法

---

### Vbet所有玩法給予結果(result)（已整合至技術設計類）

> Confluence 頁面 ID：40502106
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40502106)
> 摘要檔：[processed/40502106-summary.md](../../confluence/processed/40502106-summary.md)
> Confluence 最後更新：2022-09-21
> 摘要最後同步：2026-05-27
> ⚠️ 此文件屬於歷史決策，詳細內容已整合至歷史決策類

---

### 站台賽程顯示

> Confluence 頁面 ID：47219601
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47219601)
> 摘要檔：[processed/47219601-summary.md](../../confluence/processed/47219601-summary.md)
> Confluence 最後更新：2023-04-13
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了多個外部體育資料站台（如 1xbet、SBO、HGA、betfair 等）的賽程顯示範圍，以及對應爬蟲的抓取天數規則。說明了從舊範圍到新範圍的調整，並標注各站台的實施進度與特殊限制。最後附帶 parser 修改後暫時的賠率輸出規則。對於 AI 開發而言，這份文件提供了爬蟲抓取行程的參數設定依據。

**關鍵業務規則**：
- KU、NK、KKK：不調整抓取範圍（Noneed），維持原有邏輯
- HGA：抓取範圍從 1 天改為全部；特別規定非當天比賽僅抓取 HA、OU、Half 等玩法，其他玩法不抓
- betfair、tonybet：抓取範圍改為全部天數
- betradar、cloudbet、nowscore、npbyahoo 等標注「比分站台無賠率」的站台，只回報比分資訊，不提供賠率
- parser 行為調整：2023/4/13 起，2 天後只輸出 HAOU 類型的賠率；過渡期 4/13～4/15 仍輸出全部賠率，4/16 起僅保留 HAOU

**注意事項**：
- ⚠️ 文件最後更新於 2023-04-13，其中 parser 輸出規則「4/16~只丟HAOU」已過該時間點，目前是否仍適用需人工確認

---

### 賽事站台需求

> Confluence 頁面 ID：40501592
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40501592)
> 摘要檔：[processed/40501592-summary.md](../../confluence/processed/40501592-summary.md)
> Confluence 最後更新：2022-09-15
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義賽事實況與賽事結果需新增的 OtherInfo、ResultInfo、單節比分等資訊，以及各球種（GameType）對應顯示的站台清單。提供相關 API 的請求與回應格式，包括 GameResult.json 及 LanguageMap.json 的結構。移除無作用的單場賽事實況與論壇頁面。

**關鍵業務規則**：
- 賽事實況須輸出 OtherInfo（天氣、地點等）、單節比分、playbyplay 資訊
- 賽事結果須輸出 ResultInfo，包含在 GameResult.json 中
- 各球種顯示站台規則：BS、BK、HL 顯示 zba,ku888,nk.net,vbet,1xbet.com,ps3838.com；SC 顯示 zba,hga.com,ku888,vbet,188bet,1xbet.com
- 移除無作用頁面：單場賽事實況、論壇
- API /pricecenter/api/system/gameresult 會同時儲存 GameResult.json 及 LanguageMap.json

**注意事項**：
- ⚠️ 文件最後更新於 2022-09，球種與站台對應關係可能已變更，需與現行系統確認

---

### TCZB-4036 [MonitorFile] - 文章檔案監控

> Confluence 頁面 ID：79466131
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79466131)
> 摘要檔：[processed/79466131-summary.md](../../confluence/processed/79466131-summary.md)
> Confluence 最後更新：2025-12-02
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文檔描述內部工具 WinSCPtool 的監控邏輯，該工具定時檢查 WinSCP 主機上爬蟲產出的賽事文章／走地情報檔案，並比對 pricecenter 資料庫中的賽事資料，在缺少對應檔案時發出 Telegram 告警。文中列出監控的站台清單、檔案命名格式、官網與非官網站台的不同檢查時機與週期規則，以及近期調整（如非官網延後至 06:30 檢查）以降低誤報率。

**關鍵業務規則**：
- 官網類型站台 cpbl.com 和 cbssports.com（賽前報）：檢查昨日、今日、明日每一場賽事是否有對應檔案
- 非官網站台統一規則：當天早上 06:30 才開始檢查當天的資料夾，避免凌晨就觸發誤報
- inplay 類型的 DB 數量檢查：只計算已開賽 5 分鐘或已完賽的場次，明天的比賽不列入計算
- DB 數量檢查方式：請求 pricecenter API（GET /pricecenter/api/sitegames/{game_type}/{site}/{game_date}）
- scores24 站台的特殊處理：DB 查詢時使用 site=aipredict，並需過濾 siteLTD 欄位包含 'scores24' 的資料
- 站台 lt、inplayZ、gs 已停止監控（2025.11.20），因這些站台的檔案是自己生成而非爬蟲產出

**注意事項**：
- ⚠️ 2025.11.24 的 8/2 小時檢查規則為測試階段，後續 11.25 又變更為 24 小時，需人工確認目前線上實際使用的規則版本
- ⚠️ 監控依賴的 pricecenter API 端點為內部 IP，若 API 位址或參數變更，監控會中斷

---

### TCZB-868 [PriceCenterService] - 合併隊伍swap機制

> Confluence 頁面 ID：21659995
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=21659995)
> 摘要檔：[processed/21659995-summary.md](../../confluence/processed/21659995-summary.md)
> Confluence 最後更新：2021-06-28
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義在自動合併賽事時，若以認定官網站台為基準，發現聯盟相同且賽事時間差距在 ±30 分鐘內的相似比賽，但隊伍資訊相反，則觸發 swap 機制。合併時會將 sitegames 表的 swap 欄位設為 1（0:正常，1:隊伍相反）。有助於開發時理解 swap 行為、驗證交換結果與賠率/分數的一致性。

**關鍵業務規則**：
- 自動合併賽事時，以認定官網站台為基準判斷是否為相似比賽
- 相似比賽判定條件：（1）聯盟相同；（2）賽事時間與合併後的賽事時間相差在 ±30 分鐘內
- 若判定為相似比賽且隊伍相反，則啟動 swap 機制：自動合併並將 sitegames 表中的 swap 欄位設為 1
- 賽事分割時，swap 欄位必須回復為 0（正常）

**注意事項**：
- ⚠️ 文件最後更新於 2021-06-28，部分 API 或行為可能已變更，需人工確認目前是否仍適用
- ⚠️ 賽事分割時 swap 欄位需回復為 0，容易在實作時遺漏

---

### TCZB-992 [PriceCenterService]-更新Sitegame策略

> Confluence 頁面 ID：24084855
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24084855)
> 摘要檔：[processed/24084855-summary.md](../../confluence/processed/24084855-summary.md)
> Confluence 最後更新：2021-08-06
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義在 CloseFinalGame API 中新增一個站台賽事同步策略：以 game_{gameType} 的基底賽事為來源，當賽事 status=1 且結束超過 1 小時後，對於其他站台同場賽事中 status≠1 的記錄進行覆蓋。對 AI 開發的幫助是釐清 pricecenterservice 在結算後如何確保各站點賽事資料一致性。

**關鍵業務規則**：
- 觸發條件：來源賽事 status 必須為 1，且結束時間已超過 1 小時
- 檢查範圍：只針對其他站台（非來源站台）中與來源賽事同場的 sitegames 記錄
- 更新判斷：若目標 sitegames 記錄的 status ≠ 1，則判定為需要覆蓋
- swap 處理：當目標記錄的 swap 欄位為 1 時，需先將 match_a、match_h 對調後再寫入
- 狀態更新：覆蓋完成後，將目標記錄的 status 更新為 1
- 略過條件：若所有其他站台同場賽事 status 均已為 1，則完全不進行任何更新

**注意事項**：
- ⚠️ 文件最後更新於 2021-08-06，距今已久，CloseFinalGame API 的實作方式可能已調整，需人工確認該策略是否仍有效

---

### TCZB-1416 [PriceCenterService]-強制合併賽事功能API

> Confluence 頁面 ID：24092480
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24092480)
> 摘要檔：[processed/24092480-summary.md](../../confluence/processed/24092480-summary.md)
> Confluence 最後更新：2022-02-08
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義了三個手動合併 API（聯盟、隊伍、賽事），用於修復資料中重複的聯盟/隊伍/賽事，並說明兩種合併情境的操作流程：合併已合併的聯盟時需一併遷移站台與隊伍，以及同聯盟下重複隊伍的合併需求。對實現 pricecenterservice 強制合併功能有直接幫助。

**關鍵業務規則**：
- 手動合併聯盟 API (PUT /combine/league/{gametype}/{dstlid}/{srclid})：將 srclid 的所有站台、隊伍、已合併的隊伍移至 dstlid 聯盟，並刪除 srclid 聯盟資料
- 手動合併隊伍 API (PUT /combine/team/{gametype}/{dsttid}/{srctid})：將 srctid 轉移至 dsttid 並刪除來源隊伍
- 手動合併賽事 API (PUT /combine/game/{gametype}/{dstgid}/{srcgid})：將 srcgid 轉移至 dstgid 並刪除來源賽事
- 合併聯盟時必須將來源聯盟下的所有站台附加至目標聯盟，再將站台下的隊伍全部轉移
- 當相同賽事未合併但聯盟已合併時，應優先透過合併聯盟功能解決，後續若有同聯盟下重複隊伍則再合併隊伍

**注意事項**：
- ⚠️ 文件最後更新於 2022-02-08，屬於舊 Sprint，需確認當前系統是否仍沿用此 API 設計與流程

---

### TCZB-1560 [PriceCenterService] - 合併賽事只有比分的站台 不Show (gs)

> Confluence 頁面 ID：32538838
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32538838)
> 摘要檔：[processed/32538838-summary.md](../../confluence/processed/32538838-summary.md)
> Confluence 最後更新：2022-03-09
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此需求旨在降低操作頁面雜訊，新增一個 API 參數 passOnlyMatcheSite（布林值）到取得賽事資料的端點。當該參數為 true 時，應過濾掉合併賽事中那些只有比分資訊的站台，不顯示給前端，以減少使用者看到的無用資訊。

**關鍵業務規則**：
- 呼叫 GET v1/games/{GameType} 取得賽事資料時，若 passOnlyMatcheSite 參數為 true，則回傳的賽事列表中不應包含合併賽事裡「只有比分的站台」的賽事資料
- 「只有比分的站台」的明確定義需人工確認

**注意事項**：
- ⚠️ 文件非常簡略，缺少具體的過濾邏輯實作細節
- ⚠️ 需人工確認參數 passOnlyMatcheSite 的預設行為

---

## 技術設計類

### PriceCenter Service Tables

> Confluence 頁面 ID：5341684
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/PriceCenter+Service+Tables)
> 摘要檔：[processed/5341684-summary.md](../../confluence/processed/5341684-summary.md)
> Confluence 最後更新：2023-09-26
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件詳列 PriceCenter Service 使用的 Cassandra 資料表結構，包含依 GameType 區分的賽事相關表格（_BS、_BK、_HL、_FL）與站台帳號、爬蟲頁面設定等輔助表格。提供自動建表 API 的運作方式：透過 AppSetting 新增 GameType 後，API 會先檢查表格是否存在，若無則自動建立；但若需修改欄位，必須手動更新此 API 程式碼。此定義是理解與操作 PriceCenter 資料庫的核心技術規格。

**關鍵業務規則**：
- 自動建表 API 在創建表格前會先檢查該表格是否已存在於 DB，僅在不存在時才執行創建
- 在 AppSetting 中新增欲支援的 GameType 是使用自動建表功能的前置必要步驟
- autocreatetable API 不涵蓋 'performance' 表格的建立

**關鍵設計決策**：
- 採用 Cassandra 資料庫，以 (site, gamedate, sitegid) 等組合作為分區鍵與聚簇鍵，並建立物化視圖以支援不同查詢方向
- 自動建表 API 提供動態擴展 GameType 的方案，但欄位結構的變更仍需手動修改 PricecenterService 內的程式碼
- 表格依 GameType 後綴區分（如 _BS、_BK），使不同運動類型的資料隔離

**注意事項**：
- ⚠️ 若需新增或更動資料表欄位，必須手動至 PricecenterService 修改 autocreatetable API，此設計可能導致程式碼與實際表格結構不同步的風險

---

### PriceCenter建置注意事項

> Confluence 頁面 ID：10813629
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=10813629)
> 摘要檔：[processed/10813629-summary.md](../../confluence/processed/10813629-summary.md)
> Confluence 最後更新：2020-11-13
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文說明 PriceCenter 服務使用 WebSocket，因此在部署 gateway 時必須採用 ip_hash 負載均衡策略，以確保 WebSocket 交握階段不會因請求被分發到不同後端伺服器而失敗。這個配置對測試與正式環境的連線穩定至關重要。

**關鍵設計決策**：
- Gateway 負載均衡策略選用 ip_hash，而非輪詢或其他算法，因為 WebSocket 連線需要客戶端與同一伺服器維持交握，伺服器跳轉會導致連線中斷

**注意事項**：
- ⚠️ 本文撰於 2020 年，目前的基礎架構可能已改用其他 sticky session 方案，建議確認當前 gateway 實作是否需要 ip_hash

---

### 新訂閱模式規劃

> Confluence 頁面 ID：24088670
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088670)
> 摘要檔：[processed/24088670-summary.md](../../confluence/processed/24088670-summary.md)
> Confluence 最後更新：2021-12-10
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件規劃以 Game 為中心的訂閱模式，整合多個 SiteGame 的 Match/Odd 資料，供第三方訂閱者依客製化設定接收資料。核心機制包括設定值層級（球種 > 聯盟 > 賽事）與繼承規則、依玩法分類的資料來源與賠率計算規則，以及透過 ZBParser 將整合後資料模擬成新 Site 送回 CrawlerService，降低系統改動。

**關鍵業務規則**：
- 設定值優先級：賽事專屬設定 > 聯盟設定值 > 球種預設值
- 一個聯盟只能對應一個聯盟設定值，但一個聯盟設定值可涵蓋多個聯盟
- ZBParser 判斷賽事進入 Inplay 的規則：有 2 個以上 Site 進入 Inplay 即切換
- 香港盤賠率基準值換算：主客相加超過 2 時，先轉馬來盤再計算基準值，確保產出固定盤口

**關鍵設計決策**：
- ZBParser 整合 processgamedata 後產生新 gamedata 送回 Kafka 給 CrawlerService，並以新 Site 形式運作，避免大幅修改現有流程
- 使用 OperaLogs 監控 DB 關鍵變動，ZBParser 據此增量更新 GameCache，而非全量刷新
- 備援系統同步機制：定期同步設定至備援，PRD 恢復後需人工操作將備援資料回寫
- 緊急切換機制：提供介面暫時停止問題爬蟲 Site 的資料參與整合

**注意事項**：
- ⚠️ 文件最後更新時間為 2021-12-10，距今已超過兩年，部分設計可能已調整或不再採用

---

### 站台隊伍Logo

> Confluence 頁面 ID：47222271
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47222271)
> 摘要檔：[processed/47222271-summary.md](../../confluence/processed/47222271-summary.md)
> Confluence 最後更新：2023-07-04
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了如何從 API 返回的比賽數據中提取隊伍 Logo 的規則：home_logo 或 away_logo 字段可能包含序列化的 JSON，需要判斷其中是否有 file_path，若有則將 file_path 與基礎圖片域名 https://inplayz.com/ 拼接，產生完整的 Logo 圖片 URL。該機制支援多個數據供應商及多種運動。

**關鍵設計決策**：
- Logo 數據以序列化 JSON 字串形式存儲，並透過檢查 file_path 字段決定是否有效，以此靈活適應不同供應商的 Logo 存儲方式
- 基礎圖片 URL 固定為 https://inplayz.com/，與 file_path 直接拼接，減少配置複雜度

**注意事項**：
- ⚠️ 文件更新時間為 2023-07-04，可能存在後續供應商或運動增刪，需人工核對現狀
- ⚠️ 文件僅解釋了有 file_path 的情況，未提及反序列化失敗或缺少 file_path 時的顯示策略

---

### 1XBET PlayByPlay Mapping

> Confluence 頁面 ID：24087086
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/1XBET+PlayByPlay+Mapping)
> 摘要檔：[processed/24087086-summary.md](../../confluence/processed/24087086-summary.md)
> Confluence 最後更新：2021-11-16
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義了來自 1XBET 的即時比賽統計項目（PlayByPlay）與內部中文名稱、ZBDigital 名稱及 AppSetting CODE 的對應表，涵蓋籃球、足球、棒球、冰球和美式足球五種運動。主/客隊的統計項目需分別加上 'Home' 與 'Away' 前綴。這份映射表有助於理解 PriceCenter 服務如何標準化不同數據源的欄位。

**關鍵業務規則**：
- 所有主隊相關的 PlayByPlay 統計項目，在命名時須加上 'Home' 前綴；客隊相關項目則加上 'Away' 前綴
- 當對應的 ZBDigital 名稱為空時，表示該統計類型尚未定義或暫不使用

**注意事項**：
- ⚠️ 文件最後更新於 2021-11-16，距今日期較遠，部分映射可能已變更

---

### ResultInfo & 玩法結果 對照

> Confluence 頁面 ID：40501992
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40501992)
> 摘要檔：[processed/40501992-summary.md](../../confluence/processed/40501992-summary.md)
> Confluence 最後更新：2022-09-08
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義各種球種的統計指標的內部代碼 key，及其對應的中英文名稱。同時列出 1xbet、HGA、188bet、Leisu、Betsapi 等外部資料源是否提供該指標的現況。另外說明了 FirstScore/LastScore 的值意義以及通用玩法結果代碼（W、WR、LR、L、N、空值）的含義，可供解析結算結果與開發資料校驗邏輯參考。

**關鍵業務規則**：
- 玩法結果代碼：W 表示贏，WR 表示中洞贏，LR 表示中洞輸，L 表示輸，N 表示平手退還，空值表示無法計算結果
- FirstScore 與 LastScore 的值定義：'No' 表示未得分，'1' 表示 team1 隊伍得分，'2' 表示 team2 隊伍得分
- 外部資料源僅在欄位標記為 'O' 時才提供該統計指標

**關鍵設計決策**：
- 採用內部統一的代碼 key（如 Corner、Card、YellowCard 等）作為資料交換標準
- 結果狀態使用簡短英文字母代碼，方便程式判斷與儲存

**注意事項**：
- ⚠️ 文件最後更新於 2022-09-08，後續可能有新增指標或資料源變動
- ⚠️ 'Penalty'、'RedCardHalf' 等多個指標在所有資料源均無勾選，可能表示現行系統未使用這些統計

---

### Cursor使用心得-加強OpenClawMerge功能

> Confluence 頁面 ID：79469793
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469793)
> 摘要檔：[processed/79469793-summary.md](../../confluence/processed/79469793-summary.md)
> Confluence 最後更新：2026-04-01
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
為解決MergeSite前端合併後重新載入速度過慢，在PriceCenterService新增單筆OpenClawMerge查詢API，並於MergeSite提供對應接口。前端調整為僅針對操作行點對點更新，大幅提升效能。過程強調使用AI時文件設計與指令清晰度的關鍵性。

**關鍵業務規則**：
- 調用單筆OpenClawMergeAPI時，參數gtype、gdate（格式yyyy-MM-dd）、lid、id皆為必要
- 使用者進行合併操作後，應調用單筆API查詢該筆資料；若回傳有資料則重新繪製該行，無資料則移除該行

**關鍵設計決策**：
- 在PriceCenterService增加讀取單筆merge資料的API，讓MergeSite後端調用，避免前端重新載入整個列表以提升效能
- API URI設計從原初版本調整為/api/v1/openclawmerge/row/{gtype}/{gdate}/{lid}/{id}
- 開發時嚴格參考aidata中的.cursor_rules規範與.sample專案結構

---

### TCZB-128 [PriceCenterService] - CrawlerAgent get config from zookeeper

> Confluence 頁面 ID：5341622
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-128+%5BPriceCenterService%5D+-+CrawlerAgent+get+config+from+zookeeper)
> 摘要檔：[processed/5341622-summary.md](../../confluence/processed/5341622-summary.md)
> Confluence 最後更新：2020-08-17
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這篇文件說明 CrawlerAgent 需從 Zookeeper 讀取並監聽配置，支援按環境（開發、測試、正式）載入不同配置，目的是將各類爬蟲資料標準化為統一欄位格式供前端展示。對 AI 開發的意義在於：CrawlerAgent 的配置來源為 Zookeeper，啟動時需拉取配置並註冊監聽，以實作動態配置變更。

**關鍵設計決策**：
- 選用 Zookeeper 作為配置中心，實現集中式配置管理與動態更新
- 支援多環境配置，根據執行環境自動載入對應的 Zookeeper 節點設定

**注意事項**：
- ⚠️ 文件最後更新於 2020-08-17，內容可能已過時，須確認目前 CrawlerAgent 的配置機制是否仍依賴 Zookeeper

---

### TCZB-130 [PriceCenterService] - CrawlerAgent send data to kafka (include define data-format)

> Confluence 頁面 ID：5341615
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=5341615)
> 摘要檔：[processed/5341615-summary.md](../../confluence/processed/5341615-summary.md)
> Confluence 最後更新：2020-08-17
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文定义了 CrawlerAgent 处理完赛事数据后，通过 Nginx 的 /pricecenter/match.json 接口将数据写入 Kafka 的 matches topic，供 CrawlerService 订阅消费。提供了完整的 JSON 数据格式样例，包含比赛类型、来源、请求时间以及比赛列表。这为上下游服务的数据对接提供了明确的技术契约。

**關鍵設計決策**：
- 采用 Nginx 作为中间代理接收 HTTP 请求并转发至 Kafka，以实现统一的请求日志记录
- 规定数据格式以 matches topic 承载赛事实体，使用 JSON 数组包含当天所有变更的比赛

**注意事項**：
- ⚠️ 文档最后更新于 2020-08-17，距现在较久，需确认 Kafka topic 名称及数据格式是否仍有变更

---

### TCZB-131 [PriceCenterService] - CrawlerService send data to cassandra

> Confluence 頁面 ID：5341598
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-131+%5BPriceCenterService%5D+-+CrawlerService+send+data+to+cassandra)
> 摘要檔：[processed/5341598-summary.md](../../confluence/processed/5341598-summary.md)
> Confluence 最後更新：2020-08-14
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義了 CrawlerService 的一項功能：訂閱 Kafka 中的爬蟲數據，將其轉換為統一欄位格式，再寫入 Cassandra，以便前端統一顯示。

**關鍵設計決策**：
- 為統一前端顯示，將不同爬蟲來源的資料全部處理成同一種欄位格式後寫入 Cassandra

---

### TCZB-141 [PriceCenterService] - CrawlerAgent send log to kafka (include define data-format)

> Confluence 頁面 ID：5341611
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=5341611)
> 摘要檔：[processed/5341611-summary.md](../../confluence/processed/5341611-summary.md)
> Confluence 最後更新：2020-08-18
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義了 CrawlerAgent（Python）的日誌收集途徑：Python 封裝 Logger Function，以異步 HTTP 請求將結構化日誌發送至 Nginx，Nginx 經 Lua 轉發至 Kafka，最終由 applogxservice 寫入 Cassandra applogs 表。文件中提供了完整的 LogData 資料模型，方便 AI 開發時理解並實作一致的日誌格式與傳輸流程。

**關鍵業務規則**：
- 日誌必須通過 HTTP 異步請求發送至指定端點
- 日誌 JSON 結構須符合 LogData 模型，包含必填欄位：guid、appName、machineName、eventDate、eventTime、unixTime、logLevel、state、exception
- Nginx 使用 Lua 將接收到的日誌轉發到 Kafka
- applogxservice 負責將 Kafka 中的日誌寫入 Cassandra 的 applogs 表

**關鍵設計決策**：
- 採用 Nginx + Lua 作為日誌入口，統一收斂與轉發至 Kafka，避免 Python 直接寫 Kafka
- 採用異步 HTTP 請求發送日誌，避免阻塞主業務流程
- 日誌模型以 C# 類別定義並給出 Python 可複刻的欄位與初始化範例，確保跨語言一致性

---

### TCZB-143 [PriceCenterService] - PriceCenterService get leagues/teams/games/matches api

> Confluence 頁面 ID：7110935
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=7110935)
> 摘要檔：[processed/7110935-summary.md](../../confluence/processed/7110935-summary.md)
> Confluence 最後更新：2020-09-10
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義 PriceCenterService 取得聯賽、隊伍、比賽與賽事資料的多個 API，含參數規範與 isGetAll/isGetSite 的資料來源控制。對 AI 開發的幫助是明確各端點的查詢條件、必要性與所有權過濾邏輯。

**關鍵業務規則**：
- getLeagueDTOs: 必要參數 GameType、isGetSite；可選參數 isGetAll（預設 false，僅取自有資料；true 時併取 site 資料）
- getTeamDTOs: 必要參數 GameType、isGetSite；可選參數 lid（支援逗號分隔多值）、isGetAll
- getGameDTOs: 必要參數 GameType、GameDate、isGetSite；可選參數 lid、status（未填時取所有 status 0~4）、isGetAll
- getLeagueDTOByDate: 必要參數 Date、isGetSite；回傳當日有比賽的所有聯盟 ID

**注意事項**：
- ⚠️ 最後更新於 2020-09-10，已超過四年，規則可能已變更
- ⚠️ 參數名稱不一致：需求標題多用 isGetSite，但詳細說明欄位主要描述 isGetAll 的預設值行為

---

### TCZB-209-[PriceCenterService] - CrawlerAgent get real-time/history result form NHL.org

> Confluence 頁面 ID：7110851
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=7110851)
> 摘要檔：[processed/7110851-summary.md](../../confluence/processed/7110851-summary.md)
> Confluence 最後更新：2020-08-28
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了 PriceCenterService 中 CrawlerAgent 從 NHL.org 獲取即時與歷史資料的需求。需透過 API 取得資料，整理成指定格式，並定時執行。

**關鍵業務規則**：
- 從 NHL API 取得即時資料
- 從 NHL API 取得歷史資料
- 將取得的 NHL 資料整理成需要的格式
- 定時執行資料取得任務

**注意事項**：
- ⚠️ 文件最後更新於 2020-08-28，內容可能過時，API 端點或資料格式可能已變更

---

### TCZB-210[PriceCenterService] - PriceCenterService get siteteams/sitegames/sitematches api

> Confluence 頁面 ID：7110927
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=7110927)
> 摘要檔：[processed/7110927-summary.md](../../confluence/processed/7110927-summary.md)
> Confluence 最後更新：2020-11-05
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了 PriceCenterService 中 11 個用於查詢運動賽事相關資料的 API 端點，包含 SiteLeague、SiteTeam、SiteGame 和 SiteMatches 四大類。每個 API 都明確規範了必要參數和選用參數，其中 site 和 sitelid 等參數支援以逗號分隔的多值查詢。

**關鍵業務規則**：
- 所有 API 的 GameType 欄位皆為必要選擇欄位，不可省略
- GetSiteLeauges、GetSiteTeams API 的 site 欄位為非必要，可傳入多筆以逗號分隔
- GetSiteTeamsBySitelid API 的 sitelid 欄位為必要，支援多筆資料以逗號分隔
- GetSiteGames、GetSiteGamesBySite API 的 endGameDate 為選擇欄位，不帶時僅查詢 startGameDate 當天資料
- isGetOther 選擇欄位僅在 isGetOdd 為 true 時才有作用
- GetSiteSingleGamesByGid 僅需 GameType 和 gid 兩個必要欄位

**注意事項**：
- ⚠️ 文件建立於 2020-11-05，距今較久，API 參數規範可能已有變更

---

### TCZB-193 [PriceCenterService] - CrawlerAgent get real-time/history result - 電競

> Confluence 頁面 ID：7111447
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=7111447)
> 摘要檔：[processed/7111447-summary.md](../../confluence/processed/7111447-summary.md)
> Confluence 最後更新：2020-09-14
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件為 PriceCenterService 中 CrawlerAgent 的需求定義，說明需要從 chaofan.com 抓取電競比賽的即時與歷史資料，並進行格式整理與定時排程。

**關鍵業務規則**：
- 需從 chaofan.com 取得所有遊戲的即時比賽資料
- 需從 chaofan.com 取得所有遊戲的歷史比賽資料
- 需將原始資料整理成服務所需的格式
- 需具備定時執行機制

**注意事項**：
- ⚠️ 文件最後更新於 2020-09-14，距今已久，chaofan.com 的介面或資料結構可能已變更

---

### TCZB-242 [PriceCenterService] - Auto Merge Site Data

> Confluence 頁面 ID：7111391
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-242+%5BPriceCenterService%5D+-+Auto+Merge+Site+Data)
> 摘要檔：[processed/7111391-summary.md](../../confluence/processed/7111391-summary.md)
> Confluence 最後更新：2020-09-14
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這篇文件定義了 PriceCenterService 需要具備自動合併聯盟賽事隊伍的功能。此需求被標記為極高重要性，但文件內容極為簡略，僅列出一個 AutoCombine 需求項，缺乏具體的合併規則、判斷條件、執行頻率等細節。

**關鍵業務規則**：
- PriceCenterService 需支援自動合併聯盟賽事隊伍資料（AutoCombine），重要性為極高

**注意事項**：
- ⚠️ 文件內容極簡，缺乏具體業務規則，實際實作邏輯需要從其他文件或程式碼中補全

---

### TCZB-243 [PriceCenterService] - Manual Merge Site Data

> Confluence 頁面 ID：7111404
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-243+%5BPriceCenterService%5D+-+Manual+Merge+Site+Data)
> 摘要檔：[processed/7111404-summary.md](../../confluence/processed/7111404-summary.md)
> Confluence 最後更新：2020-09-11
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了 PriceCenterService 所需的手動合併站點數據功能，包括對聯盟、隊伍、賽事進行合併、刪除與分割共 9 項操作，全部為極高優先級。這項需求為後續開發手動管理工具與 API 提供了明確的功能範圍。

**關鍵業務規則**：
- 系統必須提供手動合併聯盟的功能（ManualCombineLeague）
- 系統必須提供手動合併隊伍的功能（ManualCombineTeam）
- 系統必須提供手動合併賽事的功能（ManualCombineGame）
- 系統必須提供手動刪除聯盟的功能（ManualDeleteLeague）
- 系統必須提供手動刪除隊伍的功能（ManualDeleteTeam）
- 系統必須提供手動刪除賽事的功能（ManualDeleteGame）
- 系統必須提供手動分割聯盟的功能（ManualSplitLeague）
- 系統必須提供手動分割隊伍的功能（ManualSplitTeam）
- 系統必須提供手動分割賽事的功能（ManualSplitGame）

**注意事項**：
- ⚠️ 文件最後更新於 2020 年，需確認現行 PriceCenterService 與 mergesite 的實作是否符合這些需求

---

### TCZB-270 [PriceCenterService] - api to update score for CrawlerService call

> Confluence 頁面 ID：8716349
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-270+%5BPriceCenterService%5D+-+api+to+update+score+for+CrawlerService+call)
> 摘要檔：[processed/8716349-summary.md](../../confluence/processed/8716349-summary.md)
> Confluence 最後更新：2020-09-29
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件提出一個新需求：在 PriceCenterService 中加入 UpdateMatch API，供 CrawlerService 在比分變化時調用。該 API 要求傳入 gameType、site、sitelid、sitegid 四個參數，但決定是否實際更新分數的具體策略或條件未在文件中定義。

**關鍵業務規則**：
- 呼叫 UpdateMatch API 時，必須傳入 gameType、site、sitelid、sitegid 這四個參數
- 當分數有變動時，由 CrawlerService 調用此 API

**注意事項**：
- ⚠️ 文件內容過於簡略，缺乏具體的更新決策邏輯，無法直接實作
- ⚠️ 最後更新日期為 2020-09-29，可能已過期或與現行設計不同

---

### TCZB-286 [PriceCenterService] - get odd data api

> Confluence 頁面 ID：8716379
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-286+%5BPriceCenterService%5D+-+get+odd+data+api)
> 摘要檔：[processed/8716379-summary.md](../../confluence/processed/8716379-summary.md)
> Confluence 最後更新：2020-09-30
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件定義 PriceCenterService 取得賠率資料的 8 個 API 端點，支援根據比賽 GID、日期、聯盟 LID、站點 site 等條件查詢一般賠率和滾球賠率，並可選回傳 other 賠率。對 AI 開發而言，這些 API 是價格中心服務的核心資料查詢接口。

**關鍵業務規則**：
- GetOddsByGID：根據 gametype 和 gid 取得所有 site 的 odd，可選參數 site（逗號分隔，預設全部站點）和 isGetOthers（預設 false）
- GetOddsByGDate：根據 gametype 和 gdate 取得該日期所有 site 的 odd
- GetOddsBySiteGid：根據 gametype, site, sitelid, sitegid 取得指定 site 的指定 game odd
- GetOddsByLID：根據 gametype 和 LID 取得該聯盟下所有 site 的 odd
- GetRBOddByGID：根據 gametype 和 gid 取得所有 site 的滾球 odd
- GetRBOddsNow：根據 gametype 取得當前所有 site 的滾球 odd
- GetRBOddsByLID：根據 gametype 和 LID 取得該聯盟下所有 site 的滾球 odd

**注意事項**：
- ⚠️ 文件最後更新於 2020-09-30，可能已不是 pricecenterservice 的最新設計

---

### TCZB-326 [PriceCenterService] - update bet365pages api

> Confluence 頁面 ID：8716643
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-326+%5BPriceCenterService%5D+-+update+bet365pages+api)
> 摘要檔：[processed/8716643-summary.md](../../confluence/processed/8716643-summary.md)
> Confluence 最後更新：2020-10-12
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了 PriceCenterService 中的 UpdateBet365page API 需求。該 API 的作用是根據 CrawlerService 傳來的頁面資訊來更新資料庫中的 bet365page 表。這是一個供爬蟲系統調用的接口，用以控制和管理需要爬取的網頁設定。

**關鍵業務規則**：
- 更新 bet365page 資料表時，必須根據 pagename, pagetype, url, enabled 這四個欄位進行操作
- 此 API 的觸發方為 CrawlerService，而非前端用戶直接操作

---

### TCZB-325 [PriceCenterService] - Update Redis API

> Confluence 頁面 ID：9797863
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-325+%5BPriceCenterService%5D+-+Update+Redis+API)
> 摘要檔：[processed/9797863-summary.md](../../confluence/processed/9797863-summary.md)
> Confluence 最後更新：2020-10-26
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件為 PriceCenterService 的一項技術設計，規劃新增一個 API，將系統接收到的 sitegame 與 odds 資料寫入 Redis。

**關鍵業務規則**：
- 接收到 sitegame 與 odds 後，必須寫入 Redis

**注意事項**：
- ⚠️ 內容過於簡略，缺少資料結構、Redis Key 命名規則、寫入策略等關鍵資訊

---

### TCZB-423 [PriceCenterService] - Api訂閱

> Confluence 頁面 ID：10813481
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=10813481)
> 摘要檔：[processed/10813481-summary.md](../../confluence/processed/10813481-summary.md)
> Confluence 最後更新：2020-11-12
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義一個供訂閱者使用的 GetData API，透過 access time 機制支援增量資料查詢。初次請求無需帶 access time，回傳今明兩天資料與當前 access time；後續請求帶上次 access time，回傳期間內有變化的資料。必要參數為 gamtype、site、subscribeType。為此需新增 Redis 資料庫並設計結構以儲存與比對資料變更。

**關鍵業務規則**：
- API 初次取值時不帶 last accessTime，系統回傳今明兩天的 data 以及當次 access time
- 非初次取值必須帶入 access time，系統回傳從上次 access time 到本次 access time 之間所有變化的資料
- 請求必要欄位：gamtype、site、subscribeType
- subscribeType 有效值為：Match、Odds、RBOdds

**關鍵設計決策**：
- 採用 Redis 作為 API 背後的資料儲存，以實現快速的變更比對與增量回傳

**注意事項**：
- ⚠️ 文件最後更新於 2020-11-12，距今較久，需確認 API 與 Redis 設計是否仍在使用或已變更

---

### TCZB-424 [PriceCenterService] - WebSocket訂閱

> Confluence 頁面 ID：10813488
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=10813488)
> 摘要檔：[processed/10813488-summary.md](../../confluence/processed/10813488-summary.md)
> Confluence 最後更新：2020-11-09
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
規劃 PriceCenterService 的 WebSocket 即時數據推送機制：設計 GetData API 讓訂閱者初次取得今明兩天資料，設計多種 Channel 供訂閱不同類型數據，並新增 Redis 資料庫儲存即時資料與存取結構。

**關鍵業務規則**：
- GetData API 在訂閱者首次請求時，必須回傳當天和隔天的資料

**關鍵設計決策**：
- 採用 WebSocket 作為即時推送通道，讓訂閱者持續接收更新
- 提供 GetData API 作為初次數據拉取端點，確保訂閱者能獲得初始狀態
- 設計多種 Channel 以分類推送不同類型的即時數據
- 引入 Redis 資料庫作為 WebSocket 後端的即時數據儲存與檢索層

**注意事項**：
- ⚠️ 文件最後更新於 2020-11-09，距今超過 5 年，可能已過時
- ⚠️ Channel 的具體分類、名稱和篩選規則未定義，實作時需補充明確規範

---

### TCZB-508 [PriceCenterService] betsapi-result整合

> Confluence 頁面 ID：11436599
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=11436599)
> 摘要檔：[processed/11436599-summary.md](../../confluence/processed/11436599-summary.md)
> Confluence 最後更新：2020-12-07
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件描述了 PriceCenterService 整合 betsapi 關盤數據的規則：每5分鐘輪詢 BetApi，查詢已關盤遊戲的 gid，然後根據 gid 查找並覆蓋 Bet365 資料庫中的對應記錄，實現 Bet365 關盤資訊的同步。

**關鍵業務規則**：
- 每5分鐘定時查詢 BetApi 中已關盤的遊戲 ID（gid）
- 根據查詢到的 gid 在 Bet365 資料庫中定位對應記錄，覆蓋其關盤狀態/資訊
- 同步過程關閉 Bet365 相關的資料庫數據

**注意事項**：
- ⚠️ 文檔較舊（2020-12），是否仍適用當前架構需人工確認
- ⚠️ BetApi 的具體接口、返回格式和授權方式未在文檔中說明

---

### TCZB-582 [PriceCenterSrevice] - Betfair/Bwin Pages Table API

> Confluence 頁面 ID：14155786
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=14155786)
> 摘要檔：[processed/14155786-summary.md](../../confluence/processed/14155786-summary.md)
> Confluence 最後更新：2021-01-18
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義了 Betfair/Bwin 爬蟲中央控制 API，包括取得待處理網頁、通知停止、心跳重啟、關閉頁面、刪除比賽等五個主要端點，用於協調爬蟲機器人的工作流程。

**關鍵業務規則**：
- 提供 GetBetfairHandlePage/GetBwinHandlePage 端點，用於取得需要處理的網頁
- 提供 SendBetfairHandlePageStop 端點，通知系統該網頁機器人已停止處理
- BetfairHeartBeat/BwinHeartBeat 端點，用於機器人重啟時清除所有之前控制的 Page
- CloseBetfairPage/CloseBwinPage 端點，用於更新要爬取的頁面
- DeleteBetfairRBG/DeleteBwinRBG 端點，用於刪除已結束的比賽

**注意事項**：
- ⚠️ 文件最後更新於 2021-01-18，可能已過時
- ⚠️ 標題中有拼寫錯誤 '[PriceCenterSrevice]'，可能是 'PriceCenterService'

---

### TCZB-583 [PriceCenterService] - 大Leagues 合併

> Confluence 頁面 ID：14155792
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=14155792)
> 摘要檔：[processed/14155792-summary.md](../../confluence/processed/14155792-summary.md)
> Confluence 最後更新：2021-01-18
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了 PriceCenterService 的大 League 合併功能需求。需提供一個 UI 讓使用者執行合併操作，以及一個 API 接受 source league id 與 destination league id，將來源聯盟合併至目標聯盟。

**關鍵業務規則**：
- 使用者可透過 UI 進行 League 合併，UI 需呈現合併操作介面
- 提供自我合併 API，傳入 sourcelid 與 destionlid，將來源聯盟合併至目標聯盟

**注意事項**：
- ⚠️ 文件最後更新於 2021-01-18，距離現在較久，需人工確認功能是否仍適用

---

### TCZB-613 [PriceCenter]-Bwin/Betfair定期清除Enable=0的賽事

> Confluence 頁面 ID：15401013
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=15401013)
> 摘要檔：[processed/15401013-summary.md](../../confluence/processed/15401013-summary.md)
> Confluence 最後更新：2021-02-19
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
為控制 PriceCenter 中 Page 資料的增長，需定期刪除 Bwin 與 Betfair 來源、Enable 欄位為 0（已結束）的賽事。刪除作業須記錄於 Log 表，並提供兩支 HTTP DELETE API 端點供排程或外部呼叫。

**關鍵業務規則**：
- 系統必須支援定期刪除 Bwin 與 Betfair 中 Page.Enabled = 0 的賽事資料
- 每次執行刪除時，被刪除的賽事記錄必須寫入 Log 表
- 提供 API 端點供觸發刪除：DELETE v1/bwin/RBG/delete 與 DELETE v1/betfair/RBG/delete
- 此功能優先級為「極高」

**注意事項**：
- ⚠️ 文件最後更新於 2021-02-19，距今較久，需人工確認此清除規則是否仍適用

---

### TCZB-641 [PriceCenterHub]-拆分PriceCenterService 功能

> Confluence 頁面 ID：15401750
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=15401750)
> 摘要檔：[processed/15401750-summary.md](../../confluence/processed/15401750-summary.md)
> Confluence 最後更新：2021-03-19
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件描述將 PriceCenterHub 的功能拆分至 pricecentermanage 服務的設計決策。核心原則是：原屬於 hub 的功能直接遷移；不屬於 hub 但需要被使用的功能，則改為通過 API 方式請求其他服務。

**關鍵業務規則**：
- 在 pricecentermanage 中，若功能不屬於原本的 hub 範圍，但需要被使用時，必須改用 API 的方式向其他服務請求

**關鍵設計決策**：
- 將 hub 功能從 PriceCenterService 拆分並遷移至 pricecentermanage，以明確功能歸屬並降低耦合
- 對於非 hub 功能使用 API 調用方式，維持服務間清晰的介面邊界

**注意事項**：
- ⚠️ 文件更新於 2021-03-19，可能已不反映當前架構

---

### TCZB-678 [PriceCenterService]-新增Bet365 & bwin比賽結束策略

> Confluence 頁面 ID：15401752
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=15401752)
> 摘要檔：[processed/15401752-summary.md](../../confluence/processed/15401752-summary.md)
> Confluence 最後更新：2021-03-30
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定义了 Bet365 和 bwin 两个数据源针对篮球与足球比赛的结束判定规则。篮球比赛当出现第四节计时显示为 00:XX 且数据更新时间超过 15 分钟时，视为比赛结束；足球比赛当比赛时间超过 90:00 且更新时间超过 15 分钟时，视为比赛结束。

**關鍵業務規則**：
- Bet365 篮球：当比赛状态中出现 Q4 00:0X 且该比赛数据更新时间超过 15 分钟时，判定比赛结束
- Bet365 足球：当比赛计时显示大于 90:00 且更新时间超过 15 分钟时，判定比赛结束
- bwin 篮球：当出现 Q4 00:XX 且更新时间超过 15 分钟时判定比赛结束
- bwin 足球：当出现大于 90:00 且更新时间超过 15 分钟时判定比赛结束

**注意事項**：
- ⚠️ 文件最后更新于 2021-03-30，距今较久，比赛结束判定规则可能已有调整

---

### TCZB-683 [PriceCenterHub] - Mapping PlayByPlay

> Confluence 頁面 ID：15401754
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-683+%5BPriceCenterHub%5D+-+Mapping+PlayByPlay)
> 摘要檔：[processed/15401754-summary.md](../../confluence/processed/15401754-summary.md)
> Confluence 最後更新：2021-04-01
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義了從 bwin 和 ku 數據源將 PlayByPlay 事件名稱與時間值轉換為 bet365 統一名稱的映射規則。包含 BK（籃球）和 SC（足球）兩種運動的 Event 與 Time 欄位轉換邏輯，並明確列出未轉換的例外項目。

**關鍵業務規則**：
- bwin 籃球 Event '1-pointer scored' 或 '1 pt scored' -> 轉換為 'Free Throw'
- bwin 籃球 Event '2 pt missed' 或 '3 pt missed' -> 轉換為 'Shot Missed'
- ku 籃球 Time 值 'Quarter x' (x=1~4) -> 轉換為對應的 'Q1'~'Q4'
- ku 足球 Time 值 '2H, 10+' -> 去掉符號後，分鐘數加上 45，轉為 '55:00'
- ku 籃球及足球 Time 值，若聯賽名稱類似電競且時間不為 'Full Time' 或 'Half Time'，則全部轉為 'LIVE'

**注意事項**：
- ⚠️ 文件建立於 2021-04-01，距今較久，可能已有更新或規則已應用於程式碼中
- ⚠️ 文中提到「電競類聯賽名稱類似...」，未明確列出所有電競聯賽名稱

---

### TCZB-775 [PriceCenterService]-數值分析 API

> Confluence 頁面 ID：18646079
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=18646079)
> 摘要檔：[processed/18646079-summary.md](../../confluence/processed/18646079-summary.md)
> Confluence 最後更新：2021-05-20
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
该文档定义了 Python 数值分析服务需要通过 PriceCenterService 获取的数据及使用规则。核心包括：支持 BK、BS、SC 三类游戏，按 inplay/pregame 分成六种配置；数据获取优先选择 bet365 站点；只拉取 HA/OU/RBHA/RBOU 四种 odd history 模式；最终合并所有 site game 生成一张图表。

**關鍵業務規則**：
- Python docker 应根据 GameType(SC, BS, BK) 和 inplay/pregame 分为 3×2=6 种配置
- 站点清单为 bet365.com, ku888, pinnacle.com, betfair.com, twsl, bwin.com
- Odd history 数据仅需拉取 HA / OU / RBHA / RBOU 四种模式
- Match 数据优先使用 bet365，无 bet365 时才使用 ku888；pregame 阶段不需要 match 数据
- 画图参数：BK/BS 取 Spread 且 Main=true，SC 取 OddValue 且 Main=true
- pregame 和 inplay 的图表文件需分开生成
- 图表必须添加浮水印

**關鍵設計決策**：
- 采用 6 种独立的 docker 配置来隔离不同游戏类型和比赛状态的执行频率
- 数据源优先选择 bet365，确保稳定性和数据质量
- 合并所有 site game 后再生成单张图片，保证数据完整性

**注意事項**：
- ⚠️ BS 和 SC 的纵轴计算、比分差/分合计算均标注为「下一次 Sprint 再详细做」，当前文档可能未反映最终实现状态

---

### TCZB-781 [PriceCenterService]-新增中文Game、League API

> Confluence 頁面 ID：18645949
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=18645949)
> 摘要檔：[processed/18645949-summary.md](../../confluence/processed/18645949-summary.md)
> Confluence 最後更新：2021-05-17
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了 PriceCenterService 新增的寫入聯盟/隊伍多語言名稱 API。該 API 接受包含 GameType、Site、SiteLID、SiteTID、CountryCode 與 Name 的列表，寫入 SiteLeague 與 SiteTeam 資料表的 name_map 欄位。CountryCode 採用語言代碼，寫入前需驗證 CountryCode 的有效性。

**關鍵業務規則**：
- CountryCode 必須是有效的語言代碼，格式為 language-region（如 zh-TW、en-US），寫入前需進行驗證
- 聯盟/隊伍各語言名稱需寫入 SiteLeague 與 SiteTeam 表的 name_map 欄位，而非獨立的多語言表
- API 回傳寫入是否成功的狀態，供調用方確認

**注意事項**：
- ⚠️ 文件最後更新於 2021-05-17，可能已過時

---

### TCZB-783 [PriceCenterService]-SiteGame API

> Confluence 頁面 ID：18645901
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-783+%5BPriceCenterService%5D-SiteGame+API)
> 摘要檔：[processed/18645901-summary.md](../../confluence/processed/18645901-summary.md)
> Confluence 最後更新：2021-05-19
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義前端賠率與即時比分的資料供給流程。主要說明 PriceCenterService 如何透過 Redis 提供 Game Mapping、熱門賽事資料，並與 PriceSubscriptionSystem 合作實現即時推送。包含 Redis Key/Value 模型、API 端點及 TWSL 支援的設定。

**關鍵業務規則**：
- Game 撈取時只有同時存在 twsl、b365、ku888 的賽事才會寫入 Redis mapping
- Hot game 撈取條件相同，且必須是 inplay 並合併到 bet365 的 sitegame
- Match_UI 只提供 b365 的比分資訊，但包含所有 b365 的 sitegame
- {球種}_UI 提供的 odd 資料會包含所有 site，前端若無對應 sitegame 則拋棄不顯示
- 熱門賽事預設取 BS、BK、SC 各 3 場 inplay 且有 b365 sitegame 的賽事

**關鍵設計決策**：
- 使用 XXL-Job 定時將 Game mapping 與 Hot Game mapping 寫入 Redis
- UI 透過 PriceSubscriptionSystem 訂閱對應 channel 以接收即時更新

**注意事項**：
- ⚠️ 熱門賽事採用 hardcode 球種與數量，後續可能已調整

---

### TCZB-828 [PriceCenterService]-賠率分析折線圖

> Confluence 頁面 ID：20873261
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=20873261)
> 摘要檔：[processed/20873261-summary.md](../../confluence/processed/20873261-summary.md)
> Confluence 最後更新：2021-06-04
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文档说明了如何开发一个赔率分析折线图工具。首先从 PriceCenter API 获取赛事资料，再依据场次取得各网站的让分与大小历史赔率，以及比分变化。最后将数据按时间序列整理，并使用 Python 绘图库画出包含赔率线、最终比分线及浮水印的双轴折线图。

**關鍵業務規則**：
- 必须被分析的网站范围：bet365, KU, TWSL
- 数据整理成 DataFrame 时，若不同玩法的赔率笔数长度不同，需以最长者为基准，使用 forward fill 补足缺失值
- 棒球的让分赔率计算规则：图表 Y 轴需显示 '1+60' 格式
- 图表需包含标示最终比分和与比分差的水平线
- 图表必须包含浮水印

**關鍵設計決策**：
- 数据获取分三步：获取所有赛事 -> 获取单场赛事所有网站赔率 -> 合并整理
- DataFrame 索引使用时间序列，以便按时间画出变化线
- 使用双轴图呈现赔率变化
- 图表直接保存为文件到 Docker 容器挂载的外部文件夹

---

### TCZB-918 [PriceCenterService] - Game result +聯盟隊伍多國語言Mapping表 API

> Confluence 頁面 ID：22544593
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=22544593)
> 摘要檔：[processed/22544593-summary.md](../../confluence/processed/22544593-summary.md)
> Confluence 最後更新：2021-07-14
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件描述 PriceCenterService 中用于生成游戏结果与多语言联盟/队伍映射静态 JSON 文件的设计。API 通过 GET /api/v1/system/gameresult 接收日期参数，输出 GameResult.json 和 LanguageMap.json 两个文件，文件按日期和球种分目录存储。前端直接读取 nginx 暴露的静态文件。

**關鍵設計決策**：
- 采用静态 JSON 文件输出而非动态 API，降低服务端请求压力
- 联盟队伍映射数据按球种和日期分文件，解决一次加载所有数据过大的问题
- 文件通过 Docker 卷映射暴露给 OpenResty，由 /usr/local/openresty/nginx/html/downloads 提供静态访问

---

### TCZB-918 [PriceCenterService] - 聯盟隊伍翻譯

> Confluence 頁面 ID：22544620
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=22544620)
> 摘要檔：[processed/22544620-summary.md](../../confluence/processed/22544620-summary.md)
> Confluence 最後更新：2022-03-08
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了聯盟與隊伍名稱多語系翻譯功能的技術規格。翻譯流程以 Translateservice 為核心，繁體/簡體中文互轉使用 NuGet 套件本地處理，英文與其他語系則轉發 Google Translate API。系統透過 XXL-JOB 每 30 分鐘定時觸發批次翻譯。

**關鍵業務規則**：
- 聯盟翻譯 API 路由為 PUT /api/v1/system/leaguelanguage
- 隊伍翻譯 API 路由為 PUT /api/v1/system/teamlanguage
- XXL-JOB 每 30 分鐘觸發一次翻譯任務
- 支援語系：英文、繁體中文、簡體中文、日文
- 資料格式錯誤時，該筆資料直接跳過不翻譯

**關鍵設計決策**：
- 繁體中文與簡體中文互轉使用 NuGet 套件本地處理，不呼叫外部 API
- 英文翻譯至其他語系使用 Google Translate API，限制為僅 PRD 環境可用
- 採用 XXL-JOB 定時任務而非即時翻譯，降低系統負載

**注意事項**：
- ⚠️ 文件最後更新為 2021-07-14，已超過 2 年，翻譯 API 規格或 Google API 使用方式可能已變更

---

### TCZB-984 [PriceCenterService]-提供當天比賽聯盟隊伍資訊(多國語言)API

> Confluence 頁面 ID：24084804
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24084804)
> 摘要檔：[processed/24084804-summary.md](../../confluence/processed/24084804-summary.md)
> Confluence 最後更新：2021-08-06
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義一個 GET API，用於根據球種和日期查詢當天比賽的聯盟隊伍資訊，回應為多國語言字典結構。支援英文、日文、繁體中文、簡體中文。路由為 /api/leagueteams/{gametype}/{datetime}。

**關鍵業務規則**：
- gametype 參數必須為 'BS'、'BK' 或 'SC' 之一
- datetime 參數必須為有效日期格式，例如 '2021-08-05'
- 回應的 Dictionary key 為隊伍類別 ID，value 為多國語系物件
- 每個語系物件包含 En、Jp、Tw、Cn 四種語言欄位
- SiteLang 比 MapLang 多一個 Site 屬性

**關鍵設計決策**：
- 採用 Dictionary<string, LanguageTeamLang> 結構，方便以隊伍識別碼快速取得語系資料
- 分離 MapLang 與 SiteLang 類別，因不同顯示情境需要不同的語言對應方式

---

### TCZB-985 [PriceCenterService]-提供各站台Result比分結果API

> Confluence 頁面 ID：24084820
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24084820)
> 摘要檔：[processed/24084820-summary.md](../../confluence/processed/24084820-summary.md)
> Confluence 最後更新：2021-08-06
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義一個新 API 端點 GET /api/sitegameresult/{gametype}/{datetime}，回應 List<GameDtoModel>，用於根據球種和時間取得各站台的比分結果。

**關鍵設計決策**：
- 採用 RESTful GET 方法，以路徑參數傳遞 gametype 和 datetime
- 回應結構為 GameDtoModel 列表

**注意事項**：
- ⚠️ 資訊過期：最後更新於 2021-08-06，可能與當前實現不一致

---

### TCZB-1026 [賽事後臺工具]-原始賽事合併功能

> Confluence 頁面 ID：24085501
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24085501)
> 摘要檔：[processed/24085501-summary.md](../../confluence/processed/24085501-summary.md)
> Confluence 最後更新：2021-08-24
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本篇說明一個後臺手動合併原始賽事至聯盟賽事的 API 設計。透過 PUT /pricecenter/api/combine/game/{GameType}/{site}/{sitelid}/{siteGID}，傳入主站台資訊及所有待合併的 SiteGame 列表，即可立即觸發合併。

**關鍵業務規則**：
- 合併時必須指定一個主站台，該主站台的 site、sitelid、siteGID 需作為路由參數帶入
- 請求體為 List<SiteGame>，必須包含主站台本身的資料及所有欲合併的其他 SiteGame 資料
- 合併動作是同步的，送出後約 30 秒到 1 分鐘內資料更新

---

### TCZB-1137 [PriceCenterService]-生成聯盟戰績資料API

> Confluence 頁面 ID：24086629
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24086629)
> 摘要檔：[processed/24086629-summary.md](../../confluence/processed/24086629-summary.md)
> Confluence 最後更新：2022-09-27
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文档设计了联盟战绩数据的三个视图（总览、一对一、积分榜）及其数据格式，但注明总览和积分榜未实现。重点定义了一对一视图的 JSON 结构，并给出了棒球积分榜数据库表结构与新增/编辑 Overview 的 API 端点。

**關鍵業務規則**：
- 一对一页面仅需展示用户选定的 A 队与 B 队数据
- 部分较大的联盟数据直接爬取官网获取

**關鍵設計決策**：
- 前端每个页面仅读取一个预生成的 JSON 文件，以减少前端逻辑动作
- 一对一视图的 JSON 文件名使用 gameid.json，包含 Status、RecentGame、BeforeGame、AfterGame 四个主要区块
- 新增/编辑 Overview 使用 POST /overview 端点

---

### TCZB-1159 [PriceCenterService]-生成戰績總覽積分API

> Confluence 頁面 ID：24086865
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24086865)
> 摘要檔：[processed/24086865-summary.md](../../confluence/processed/24086865-summary.md)
> Confluence 最後更新：2021-10-26
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了產出聯盟戰績總覽所需的 JSON 格式、後端資料庫結構（涵蓋棒球、籃球、冰球、美足四種球類）與一組新增／匯出 API。

**關鍵業務規則**：
- 部分較大的聯盟直接爬取官網資料，不經過其他轉換
- 前端每個頁面只需讀取一個 JSON 檔案，以減少前端邏輯動作

**關鍵設計決策**：
- 以 gameType 路徑參數區分不同運動類型，共用同一 API 路由
- 採用依運動分別設計的 DB 表格結構，各表的必要欄位不同
- 前端採用靜態 JSON 檔案模式，由後端定期匯出

**注意事項**：
- ⚠️ 文件最後更新時間為 2021-10-26，距今已逾兩年，部分設計可能已變更或被取代

---

### TCZB-1294 [PriceCenterService]-根據球種設定官方站台

> Confluence 頁面 ID：24088961
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088961)
> 摘要檔：[processed/24088961-summary.md](../../confluence/processed/24088961-summary.md)
> Confluence 最後更新：2021-11-29
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件說明如何將官方站台的設定從站台層級（IsOffice）細化到球種層級（GameTypeIsOfficial），以滿足不同球種可指定不同官方站台的需求。核心變更是 AppSettings 中的站台設定格式，將原本的布林值 IsOffice 取代為陣列 GameTypeIsOfficial。

**關鍵業務規則**：
- GameTypeIsOfficial 與 IsOffice 不相關，兩者邏輯獨立，不應混用
- 若站台設定中包含 GameTypeIsOfficial 陣列，則該站台為陣列內指定球種的官方站台
- IsOffice 欄位應拋棄不用，所有判斷官方站台的邏輯需改用 GameTypeIsOfficial
- 官方站台資訊最終需透過 setOfficeData 函式寫入 odds Table

**關鍵設計決策**：
- 新增 GameTypeIsOfficial 陣列而非沿用 IsOffice：為了支援按球種區分官方站台
- 棄用多個舊版合併 Function（如 AutoCombineGame、setOfficeData、compareAndCombine）

**注意事項**：
- ⚠️ 文件中標記為棄用的 API 和 Function：AutoHistoryCombineGame、UpdateRedis、Official、UpdateMatch 等

---

### TCZB-1312 [PriceCenterService]-Get NameMap API

> Confluence 頁面 ID：24090301
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-1312+%5BPriceCenterService%5D-Get+NameMap)
> 摘要檔：[processed/24090301-summary.md](../../confluence/processed/24090301-summary.md)
> Confluence 最後更新：2021-12-28
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了 PriceCenterService 的 NameMap 系列 API，提供針對聯盟與隊伍在不同站台的名稱翻譯對照。核心價值在於提供一個結構化的資料字典，讓前端或其他服務可以根據 GameType、Date、LeagueId 等條件查詢合併或原始的翻譯名稱。

**關鍵業務規則**：
- API 1 根據 gameType 和 date 取得當日合併翻譯資料，回傳 List<NameMapsDto>
- API 2 根據 gameType 和 lid 取得合併翻譯資料，回傳單一 NameMapsDto
- API 3 根據 gameType、site 和 date 取得當日原始翻譯資料
- API 4 根據 gameType、site 和 sitelid 取得原始翻譯資料
- NameMap 資料分為「合併翻譯」與「原始翻譯」兩種類型

**關鍵設計決策**：
- 使用 Name_Map 欄位（Dict<String,String>）而非固定結構，以彈性容納多語系或不同站台的名稱對應關係
- 將合併翻譯資料與原始翻譯資料分開設計成不同 DTO 和 API

---

### TCZB-1327 [PriceCenterService]-Get Siteteams/SiteGames/SiteLeagues detail data API

> Confluence 頁面 ID：24090312
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24090312)
> 摘要檔：[processed/24090312-summary.md](../../confluence/processed/24090312-summary.md)
> Confluence 最後更新：2021-12-30
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文档列出了 PriceCenterService 中关于 site league、team、game 的详细数据查询 API（共 13 个端点），以及 GameSettingService 的联盟和赛事设置查询 API。每个 API 以 GET 方法提供，通过路径参数指定资源。

**關鍵設計決策**：
- API 采用 RESTful 风格，路径按资源层级组织，并使用查询参数进行过滤

**注意事項**：
- ⚠️ 文档最后更新于 2021-12-30，距今较久，部分 API 可能已变更或废弃
- ⚠️ 路径参数名称大小写不一致，需人工确认实际接口规范

---

### TCZB-1583 [PriceCenterService] - SA聯盟簡稱API

> Confluence 頁面 ID：32539098
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32539098)
> 摘要檔：[processed/32539098-summary.md](../../confluence/processed/32539098-summary.md)
> Confluence 最後更新：2022-03-14
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
為 PriceCenterService 新增兩個 API，用於同步 SA8888 足球聯盟簡稱資料。POST 端點更新站台層級的聯盟簡稱映射，PUT 端點更新指定球種的聯盟簡稱。資料由 xxl-job 定時任務每 30 分鐘觸發一次。

**關鍵設計決策**：
- 使用 RESTful 風格：POST 處理站台概括變更，PUT 處理單一球種更新
- 採用 xxl-job 排程，間隔 30 分鐘，平衡即時性與系統負載

---

### TCZB-1630 [PriceCenterService]-Get Log API

> Confluence 頁面 ID：32539199
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-1630+%5BPriceCenterService%5D-Get+Log+API)
> 摘要檔：[processed/32539199-summary.md](../../confluence/processed/32539199-summary.md)
> Confluence 最後更新：2022-03-09
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了一個新的 API 端點，用於查詢 GameTools 的操作日誌。用戶可透過 GET 請求，傳入日期與遊戲類型，取得對應的操作記錄清單。

**關鍵設計決策**：
- 選擇 GET 方法並以 /log/game/{date} 路徑接收日期參數，透過 query string ?gameType=XX 過濾遊戲類型

---

### TCZB-1370 [PriceCenterService]-針對ZB系列合併API

> Confluence 頁面 ID：24091314
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24091314)
> 摘要檔：[processed/24091314-summary.md](../../confluence/processed/24091314-summary.md)
> Confluence 最後更新：2022-01-10
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義 PriceCenterService 針對 ZB 系列的特化合併功能。由於 ZB 系列不適用通用的相似度比對合併，故另建 API `/pricecenter/api/system/zbcombine`，接收 `gameType` 參數，內部依序調用合併函數完成合併。

**關鍵業務規則**：
- ZB 系列資料的合併必須透過專用端點，不可使用通用的 AutoCombine 機制

**關鍵設計決策**：
- 因 ZB 系列結構不適用相似度比對合併，故獨立實作一套合併 API 與內部函數
- API 方法、路由與參數設計延續 AutoCombine API 的設定，維持呼叫一致性

---

### TCZB-1421 [PriceCenterService]-賽事基底變化時合併資料也須變更

> Confluence 頁面 ID：24092297
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24092297)
> 摘要檔：[processed/24092297-summary.md](../../confluence/processed/24092297-summary.md)
> Confluence 最後更新：2022-01-25
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件說明如何實作賽事基底變化的偵測、記錄與同步機制：透過定時任務比對 games 表的 sitegid 與 Redis 中的 gtime，將不一致的賽事寫入 datum_log 表，同時更新 games 表和 zba sitegames，並提供兩個 API 供寫入與查詢變化紀錄。

**關鍵業務規則**：
- 當賽事基底 gtime 變更時，必須同步更新對應的 games_{gameType} 表與 zba sitegames
- 變化紀錄保存於 datum_log 表
- 第三方可透過 GET /pricecenter/api/log/datum/{gDate}/{gameType} 查詢指定日期與聯賽的賽事變化紀錄

**關鍵設計決策**：
- 以定時任務週期性比對今明兩天的 games 表與 Redis 中的 gtime，而非事件驅動
- 選用 Cassandra 模型（datum_log）儲存變化日誌
- 同時更新 games 表和 zba sitegames，確保價格中心與合併資料的一致性

---

### TCZB-1433 [PriceCenterService]-get sitegames spread api

> Confluence 頁面 ID：24092538
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-1433+%5BPriceCenterService%5D-get+sitegames+spread+api)
> 摘要檔：[processed/24092538-summary.md](../../confluence/processed/24092538-summary.md)
> Confluence 最後更新：2022-02-08
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義了一個根據遊戲 ID 列表取得各站點讓分（spread）的 API，供 GameSetting Tools 檢查賽事合併資料使用。API 以 POST 方法調用 /pricecenter/api/frontend/sitegames/{gameType}，回傳 GameSpread 列表。

**關鍵設計決策**：
- 採用 POST 方法而非 GET，以便在請求體中傳遞 gids 列表
- 路徑使用 {gameType} 參數區分不同球種
- 回傳結構以 GID 為單位聚合各站點讓分，且將亞盤與大小球合併為單一字串

---

### TCZB-1509 [PriceCenterService]-補齊原始聯盟隊伍的翻譯資料API

> Confluence 頁面 ID：32079876
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32079876)
> 摘要檔：[processed/32079876-summary.md](../../confluence/processed/32079876-summary.md)
> Confluence 最後更新：2022-02-23
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
為解決前端無法顯示 siteleagues 與 siteteams 的 source_name，定義了兩個內部 PUT API，用於補充 namemap 欄位。API 由 xxl-job 每 3 小時依球種排程呼叫，且不經過 gateway。

**關鍵業務規則**：
- 定時任務每 3 小時執行一次，依球種分別觸發對應的修復 API
- PUT /api/v1/system/fix/siteleagues/namemap/{gameType} 用於補齊 siteleagues 的 namemap
- PUT /api/v1/system/fix/siteteams/namemap/{gameType} 用於補齊 siteteams 的 namemap
- API 僅供內部 job 呼叫，不透過 gateway

**關鍵設計決策**：
- 採用 xxl-job 分散式任務調度，每 3 小時執行，並以球種為粒度分開處理
- 不經過 gateway，直接暴露內部 endpoint，因為僅限 job 使用

---

### TCZB-1510 [PriceCenterService]-校正翻譯資料API

> Confluence 頁面 ID：32079878
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32079878)
> 摘要檔：[processed/32079878-summary.md](../../confluence/processed/32079878-summary.md)
> Confluence 最後更新：2022-03-08
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件定義了一次性校正翻譯資料的 API，用於修復因 Google 翻譯差異過大導致的聯盟與隊伍名稱翻譯錯誤。依據球種與語系，從指定的基底站台取得翻譯並更新 league 和 teams 的 namemap。

**關鍵業務規則**：
- 校正翻譯時不使用 Google 翻譯（暫時，需看測試結果）
- 根據球種和語系，優先從以下基底站台取翻譯寫入 namemap：
  - 足球繁中->hga.com
  - 籃球、棒球、美式足球、網球、電競繁中->sa8888.net
  - 冰球、綜合格鬥繁中->ps3838.com
  - 所有球種的英文、日文、韓文、泰文、越南文->ps3838.com
- 簡中由對應球種的繁中轉換
- 如果基底站台沒有對應的聯盟或隊伍，跳過不處理

**關鍵設計決策**：
- 不使用 Google 翻譯，改從既有基底站台拉取翻譯，因為 Google 翻譯差異過大
- 設計為一次性 PUT API，按球種分別執行

---

### TCZB-1518 [PriceCenterService]-強制合併隊伍API，直接替換賽事的隊伍

> Confluence 頁面 ID：32079907
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32079907)
> 摘要檔：[processed/32079907-summary.md](../../confluence/processed/32079907-summary.md)
> Confluence 最後更新：2022-02-21
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義 PriceCenterService 中一個強制合併隊伍的 API。呼叫此 API 時，會將指定賽事中的源隊伍直接替換為目標隊伍，同時保留賽事其他資料不變。

**關鍵業務規則**：
- 呼叫 v1/combine/team/{gametype}/{dsttid}/{srctid} 時，應保留賽事原有資料，僅將源隊伍替換為目標隊伍

---

### TCZB-1831 [PriceCenterService]-取得今日賽事站台資訊

> Confluence 頁面 ID：34767451
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=34767451)
> 摘要檔：[processed/34767451-summary.md](../../confluence/processed/34767451-summary.md)
> Confluence 最後更新：2022-05-24
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義 PriceCenterService 新增一個 REST API 提供今日賽事站台資訊，取代既有的 WebSocket 方式。詳細說明了 GET /pricecenter/api/games/live/{gameType} 的回應格式，並包含站台與球種的對應規則。數據由排程每分鐘寫入 Redis DB7 快取。

**關鍵業務規則**：
- 球種 SC 賽事對應的站台清單為：ZB, HGA, KU, NK, KKK, 188Bet, 1xBet, PS3838
- 其他球種對應：ZB, KU, NK, KKK, 1xBet, PS3838
- 當日賽事站台資訊會由排程每 1 分鐘抓取一次，寫入 Redis DB7 快取

**關鍵設計決策**：
- 從 WebSocket 推送改為 HTTP API 輪詢：降低客戶端複雜度，減少長連線依賴
- 採用 Redis 快取 + 排程定時更新：在可接受的延遲內提供高效讀取

---

### TCZB-1848 [PriceCenterService]-改寫Get Hot Game API

> Confluence 頁面 ID：36306961
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=36306961)
> 摘要檔：[processed/36306961-summary.md](../../confluence/processed/36306961-summary.md)
> Confluence 最後更新：2022-05-27
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件描述 PriceCenterService 的 Get Hot Game API 改寫需求，將以 GameLive 服務提供的比賽資料為基礎，根據球種 BS、BK、SC 各自預設的熱門聯賽進行篩選，並透過新的 API 端點回傳 List<RedisTodayGame> 格式的熱門賽事清單。

**關鍵業務規則**：
- 球種 BS 預設熱門聯盟：MLB, CPBL, Japan NPB, KBO
- 球種 BK 預設熱門聯盟：NBA, Australia NBL, Korea KBL, WNBA
- 球種 SC 預設熱門聯盟：England Premier League, Spain Primera Liga, Germany Bundesliga I, France Ligue 1, Italy Serie A
- 熱門賽事篩選資料基底為 GameLive 服務提供的比賽資訊

**關鍵設計決策**：
- 採用 GameLive 作為資料來源，以既有比賽資料驅動熱門賽事邏輯
- 各球種的預設熱門聯賽以靜態定義方式處理

---

### TCZB-1854 [PriceCenterService]-優化GameLive API

> Confluence 頁面 ID：34767935
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=34767935)
> 摘要檔：[processed/34767935-summary.md](../../confluence/processed/34767935-summary.md)
> Confluence 最後更新：2022-06-01
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文描述 PriceCenterService 中 GameLive API 的 Redis 快取更新優化設計。透過判斷賽事、聯盟、隊伍三層快取的存在狀態與今日資料，逐步增量更新或全量寫入，以減少 DB 查詢壓力並達到效能目標（首輪 ≤20s，後續 ≤10s）。

**關鍵業務規則**：
- 賽事快取：若快取為空，則撈取今日賽事、濾除已結束賽事後全量寫入快取；若非空，則檢查快取中是否有今日比賽，若無則執行全量寫入，若有則撈取 addtime ≥ 4 秒前的更新資料並部分更新
- 聯盟快取：若快取為空，則撈取今日賽事關聯的聯盟並寫入；若非空，則僅在快取中沒有今日賽事聯盟時才追加
- 服務重啟後初始化：需撈取明、今、昨共三天的賽事資料
- 效能要求：第一輪處理時間上限 20 秒，第二輪起上限 10 秒

**關鍵設計決策**：
- 採用三層級聯快取（賽事、聯盟、隊伍）來分離關注點
- 增量更新機制：對已有今日賽事的快取，僅撈取 addtime ≥ 4 秒前的資料進行更新
- 冷啟動策略：重啟時載入三天賽事

---

### vbet

> Confluence 頁面 ID：40501521
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/vbet)
> 摘要檔：[processed/40501521-summary.md](../../confluence/processed/40501521-summary.md)
> Confluence 最後更新：2022-09-12
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文档定义了来自 vbet 供应商的数据格式，包括静态实体（Regions、Competitions、Matches）的字段映射和实时推送命令（MatchUpdate、MatchStat）的 JSON 结构。此外，按球种列举了各类投注打法的 model 代码和赔率示例。

**關鍵業務規則**：
- Regions.Id 与 Competitions.RegionId 关联映射
- Competitions.Id 与 Matches.CompetitionId 关联映射，Competitions.SportId 表示球种
- Matches.Date 为伦敦时间
- MatchUpdate 命令 Type='Match' 更新赛事数据，Type='Market' 更新赔率数据
- Outcome 值定义：0-无结果，1-Place，2-退款，3-输，4-赢，5-赢退款，6-输退款
- 每个投注选项的 Price 和 OriginalPrice 分别表示当前赔率和初始赔率

**關鍵設計決策**：
- 采用 Command/Objects 结构推送增量更新，MatchUpdate 命令可同时携带多个对象
- 赔率使用 Selection 内的 Outcome 字段而非市场级别直接判定输赢，支持多种结算状态
- 区分 OriginalPrice 和 Price，支持赔率变化跟踪

---

### TCZB-2330 [PriceCenterService] - 聯盟合併API

> Confluence 頁面 ID：44663392
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44663392)
> 摘要檔：[processed/44663392-summary.md](../../confluence/processed/44663392-summary.md)
> Confluence 最後更新：2022-12-21
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了 PriceCenterService 提供聯盟合併相關的四個 API 端點：取得聯盟列表、取得範圍時間內 sitegame、取得 siteleague 清單、以及執行聯盟合併。

---

### TCZB-2495 [PriceCenterService] - SportKing相關功能

> Confluence 頁面 ID：47218964
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47218964)
> 摘要檔：[processed/47218964-summary.md](../../confluence/processed/47218964-summary.md)
> Confluence 最後更新：2023-03-01
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了為 SportKing 專案新增或修改的 PriceCenterService API，包含取得聯盟名稱 Map、站台聯盟年度隊伍球員、站台聯盟球員紀錄等端點，以及為 NBA 資料新增獨立的 overview 輸出路徑。

**關鍵設計決策**：
- 因 NBA overview 輸出格式與其他運動不同，決定新增獨立 API 專門處理 NBA overview 資料
- 為統一取得站台聯盟球隊球員數據，新增 /pricecenter/api/siteleagues/teams/players/{gametype} 端點
- 設計 SitePlayer 模型封裝站台、年度、聯盟、球員姓名、隊伍與統計記錄字串

---

### TCZB-2740 [SportKing] - DB寫入棒球賽事系列訊息

> Confluence 頁面 ID：47221445
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47221445)
> 摘要檔：[processed/47221445-summary.md](../../confluence/processed/47221445-summary.md)
> Confluence 最後更新：2023-06-07
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義在 pricecenter schema 的 sitegames_result 表新增多個欄位，以支援棒球賽事的進階統計顯示。這些欄位包括系列賽場次、初始賠率、主客隊本季勝率、當前連勝情形，以及三種歷史對戰記錄。

**關鍵業務規則**：
- series 欄位表示該場為系列賽的第幾場，預設值為 1
- firstspread 為初始賠率，mainspread 為收盤賠率
- winrate_h / winrate_a 以字串形式表示主／客隊本季勝率
- currentstreak_h / currentstreak_a 表示連勝情況，正數為連勝場數，負數為連敗場數
- latest_10_a_any / latest_10_h_any / latest_10_same_team 分別儲存歷史對戰記錄，格式為 JSON 陣列

**關鍵設計決策**：
- 歷史對戰紀錄以 VARCHAR 儲存 JSON 字串而非正規化為獨立表，降低讀取時的 JOIN 成本
- 地圖類型欄位使用 MAP 結構提供動態屬性的彈性
- 表以 (site, sitelid) 為分區鍵，並按 gdate DESC 進行叢集排序

---

### TCZB-2996 [PriceCenterService] - 賽事API

> Confluence 頁面 ID：55574770
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55574770)
> 摘要檔：[processed/55574770-summary.md](../../confluence/processed/55574770-summary.md)
> Confluence 最後更新：2023-10-25
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義了 PriceCenterService 中賽事相關 API 的端點與職責劃分。現有 API 提供球種時間範圍賽事查詢及特定站台賽事查詢，新增了按聯盟/日期/ID 查詢單場賽事以及更新比數狀態的端點。設計上將 Controller 區分為 game 和 sitegame。

**關鍵業務規則**：
- GET /pricecenter/api/games/{gameType} 支援選擇性查詢參數 ?dateTime=yyyy-MM-dd
- GET /pricecenter/api/games/{gameType}/{lid}/{gDate}/{id} 根據聯盟、日期和 ID 取得單一賽事
- PUT /pricecenter/api/games/{gameType}/score-status 用於更新賽事比分與狀態
- PUT /pricecenter/api/sitegames/{gameType}/score-status 用於更新站台賽事比分與狀態

**關鍵設計決策**：
- Controller 依照功能區分為 game controller 和 sitegame controller
- game controller 處理 league, game, team 資源
- sitegame controller 處理 siteleague, sitegame, siteteam 資源

---

### 自動合併流程

> Confluence 頁面 ID：7111394
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=7111394)
> 摘要檔：[processed/7111394-summary.md](../../confluence/processed/7111394-summary.md)
> Confluence 最後更新：2020-09-15
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件描述「自動合併站台資料」的技術設計流程：從 siteLeague 取出缺少英文名稱的紀錄，透過翻譯服務取得 En_Name 後回寫；之後將所有來源為官網的 siteLeague 加入 League，比對 En_Name 與 League.Name 相似度，達到門檻則將映射寫入 NameMap。

**關鍵業務規則**：
- 若 siteLeague.EnName 與 League.Name 的相似度高於門檻值，則將該 {En_Name, Site} 組合加入 League.NameMap 中

**關鍵設計決策**：
- 將加入 league、相似度比對、寫入 NameMap、更改 lid 合併成一個 function
- 翻譯需求由獨立的 TranslateProvider 處理，降低耦合
- 使用 PublicLibrary 進行名稱相似度比對

**注意事項**：
- ⚠️ 相似度門檻值未填寫，為關鍵缺失資訊
- ⚠️ 文件最後更新於 2020 年，服務名稱可能已淘汰或合併

---

### bet365pages init sql

> Confluence 頁面 ID：11436366
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/bet365pages+init+sql)
> 摘要檔：[processed/11436366-summary.md](../../confluence/processed/11436366-summary.md)
> Confluence 最後更新：2021-04-19
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件是 pricecenter.bet365pages 資料表的初始化 SQL 腳本，定義了 14 個 bet365 爬蟲採集頁面的配置參數。每個頁面配置包含頁面名稱、類型、爬取間隔、工作線程數和目標 URL。這些配置直接影響 pricecenterservice 的資料採集行為和系統負載。

**關鍵設計決策**：
- 每個 bet365 頁面類型被設計為獨立的配置項，有各自的 pagename 和 url
- SC（讓球盤）頁面配置了 maxworks=2，其他多數頁面為 maxworks=1
- 所有頁面的 popular 值均設為 1000，adddate 均為 2020/09/21

**注意事項**：
- ⚠️ 文件最後更新於 2021-04-19，bet365 的頁面結構可能已變更
- ⚠️ 這是一份 INSERT 腳本而非完整的資料表結構說明

---

### 站台賽果資料

> Confluence 頁面 ID：24086515
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24086515)
> 摘要檔：[processed/24086515-summary.md](../../confluence/processed/24086515-summary.md)
> Confluence 最後更新：2025-03-27
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件以表格形式記錄了各外部供應商所能提供的賽果數據項目支持情況，涵蓋足球、籃球、棒球等球種的比分、角球、罰牌、天氣等資訊。此表為 PriceCenter 服務選用數據源與開發爬蟲解析邏輯時的基礎依賴。

**關鍵業務規則**：
- 表格中標記為 'O' 的儲存格代表該供應商支援該賽果數據項目，未標記則不支援
- 188bet 的 Result 數據僅包含有開盤玩法的結果，非開盤玩法無對應賽果
- 足球賽果包含：全場比分、上半場比分、角球、罰牌、黃牌、15分鐘內比分等子項
- 籃球賽果包含：全場比分、上半場比分、兩分球、三分球、罰球等子項
- 棒球賽果包含：全場比分、安打數、球員資料等子項

**注意事項**：
- ⚠️ 文件中表格部分儲存格內容為空或顯示特殊符號，需人工確認其確切含義

---

### B365 PlayMode Mapping List-Backup

> Confluence 頁面 ID：15401189
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/B365+PlayMode+Mapping+List-Backup)
> 摘要檔：[processed/15401189-summary.md](../../confluence/processed/15401189-summary.md)
> Confluence 最後更新：2021-02-26
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件為 B365 體育賽事玩法與 ZBDigital 系統內部代碼的映射對照表，分成賽前與滾球兩大類型。對於 AI 開發 PriceCenter Service 時，可作為解析外部賠率資料、統一內部玩法標識的參照依據。

**關鍵業務規則**：
- 賽前玩法「Asian Handicap」對應 ZBDigital 代碼「HA」
- 賽前玩法「Over/Under」對應 ZBDigital 代碼「OU」
- 賽前玩法「Double Chance」對應 ZBDigital 代碼「Others-Double Chance」
- 滾球玩法「Asian Handicap」對應 ZBDigital 代碼「RBHA」
- 滾球玩法「Goal Line」對應 ZBDigital 代碼「RBOU」
- 其餘滾球玩法均以「RBOthers-{玩法名稱}」格式對應 ZBDigital 代碼

**關鍵設計決策**：
- 設計上採用「RBOthers-」前綴來區隔滾球的其他類型玩法，與賽前的「Others-」前綴形成對稱命名規則

**注意事項**：
- ⚠️ 滾球玩法「Fulltime Result」與「Asian Handicap」共用 ZBDigital 代碼「RBHA」，需檢查系統實作中如何區分

---

### Bwin PlayMode Mapping List

> Confluence 頁面 ID：24089164
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Bwin+PlayMode+Mapping+List)
> 摘要檔：[processed/24089164-summary.md](../../confluence/processed/24089164-summary.md)
> Confluence 最後更新：2021-12-03
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了 Bwin 提供的賽事玩法（BK 籃球、SC 足球）與系統內部 PlayMode 代碼之間的映射規則。涵蓋 PreGame 與 In Game 兩種狀態，In Game 的代碼會加上「RB」前綴以示區別。

**關鍵業務規則**：
- PreGame 狀態下，BK 的 Totals → OU，Money Line / Spread → HA
- In Game 狀態下，上述代碼均加入「RB」前綴，例如 RBOU、RBHA
- 單節玩法（如 1st Quarter）可在代碼中以「1st QuarterHA」表示
- SC 足球的 Match Result 對應 HA（PreGame）/ RBHA（In Game）
- Correct Score 玩法代碼為 Correct Score（PreGame）與 RBCorrect Score（In Game）
- 部分代碼尾部有「Score」字樣表示單隊大小

**注意事項**：
- ⚠️ 文件最後更新於 2021-12-03，可能已過期
- ⚠️ 同一個代碼（如 HA）在 BK 與 SC 中代表不同含義，實作時須根據球種區分

---

## 歷史決策類

### Cursor使用心得-3.在PriceCenterService中加入讀取Merge資料的功能

> Confluence 頁面 ID：79469429
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469429)
> 摘要檔：[processed/79469429-summary.md](../../confluence/processed/79469429-summary.md)
> Confluence 最後更新：2026-04-15
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**決策背景**：
在PriceCenterService中用Cursor開發一個新API端點的過程，功能是根據gtype、日期範圍和可選的lid查詢openclaw merge資料，並輸出包含game、sitegame、聯賽、隊伍名稱的結構化結果。

**決策結論**：
- 開發順序：先定義 Provider（資料讀取），再實作 Service（組裝與業務邏輯），最後建立 Controller（暴露 API）
- 不使用 MCP 處理 Schema，而是將 Cassandra 匯出的 .json 結構放入 .dbschema 資料夾
- Provider 僅負責資料存取，日期格式與範圍的檢查邏輯移至 Service

**影響**：
- 此API提供從Provider到Service到Controller的開發順序標準化
- 提示詞設計技巧：直接引用匯出的schema、避免讓AI誤解去修改原始Model
- 輸出欄位規範：game 輸出欄位排除 siteIDMaps、logs、otherInfo、resultInfo；sitegame 排除 otherInfo、resultInfo、playByPlay

**注意事項**：
- ⚠️ 步驟14提到AI未按規範分層，需確保提示詞完整指定所有需修改的層級
- ⚠️ 文件強調「不要去修改原始Model，撈取資料排除即可」

---

### TCZB-2077 [PriceCenter] - Vbet所有玩法給予結果(result)

> Confluence 頁面 ID：40502106
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40502106)
> 摘要檔：[processed/40502106-summary.md](../../confluence/processed/40502106-summary.md)
> Confluence 最後更新：2022-09-21
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**決策背景**：
为Vbet站点（SC）新增的黄牌、角球等24种特殊玩法的结果计算实现任务，同时列出了46种无需额外测试但已支持的玩法。

**決策結論**：
- PriceCenter在比赛Final且收到resultinfo后，必须为Vbet站点的多种PlayMode计算所有odd的result
- 需测试新玩法包含：YellowCardHalfHA, YellowCardOU, YellowCardHA, Corner2ndHalfOU 等24种
- 已支持的玩法包含：Draw No Bet, 3wayHA, 3wayOU, Goals In Both Halves 等46种

**影響**：
- 兩個 PlayMode：T1 Team Total Goals和T2 Team Total Goals明确标记为"没有做"，需人工确认当前状态

**注意事項**：
- ⚠️ 文件最后更新于2022-09-21，Vbet玩法可能已有新增或调整

---

### TCZB-537 [PriceCenterService] - Update Pages Leagues Data & Compare Leagues

> Confluence 頁面 ID：11436914
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=11436914)
> 摘要檔：[processed/11436914-summary.md](../../confluence/processed/11436914-summary.md)
> Confluence 最後更新：2020-12-21
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**決策背景**：
本文件定義了 PriceCenterService 的兩項需求：一是 Update Pages Leagues Data，接收 pageName、pageType、url 三個參數並寫入；二是 Compare Leagues，每次輸入新的聯盟資料後，要比對資料庫現有紀錄。

**決策結論**：
- Update Pages Leagues Data 功能必須接受 pageName、pageType、url 三個輸入參數
- Compare Leagues 功能需將輸入的聯盟資料與資料庫現有資料進行比對，對於本次輸入中未出現的聯盟，應執行關閉（Close）操作

**注意事項**：
- ⚠️ 文件最後更新於 2020 年，可能已有過時或變更的規則

---

### TCZB-641 [PriceCenterHub]-拆分PriceCenterService 功能（已整合至技術設計類）

> 此文件的決策內容已整合至技術設計類

---

## 操作手冊類

### Cassandra PriceCenter 資料備份

> Confluence 頁面 ID：24085974
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24085974)
> 摘要檔：[processed/24085974-summary.md](../../confluence/processed/24085974-summary.md)
> Confluence 最後更新：2023-02-03
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件說明每年針對 PriceCenter 的 Cassandra 資料庫進行年度備份與歷史資料清除的標準操作流程。備份日期為每年一月份第二個禮拜一，若該日早於 1/8 則順延一週；備份後須根據表格規則分類處理 tables，之後在 pricecenterservice 中設定三個時間區段，並手動觸發 xxl-job 清除任務。

**AI 開發需要注意的部分**：
- 備份流程：必須先完成 DB 備份至備源機或本地，才能開始執行清除流程
- Table 清理分類：matches_his_{球種}_202109 等特定歷史表需 Drop；fixdatalog、bet365pages_log 等表需 Truncate；sitegames_{球種}、odds_{球種} 等表只保留今年資料
- 清除時段設定：必須先在 pricecenterservice 中更改三個清除時間區段
- 執行負載控制：刪除時不可一次執行三個 job，需拉長時間分批執行

---

### PriceCenter訂閱方案

> Confluence 頁面 ID：10813627
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=10813627)
> 摘要檔：[processed/10813627-summary.md](../../confluence/processed/10813627-summary.md)
> Confluence 最後更新：2022-09-08
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件說明 PriceCenter 服務提供的三種資料訂閱方案：API 查詢、WebSocket 即時傳輸、以及我方主動推送。文中詳列各方案的使用流程、即時性差異、初始資料來源，並提供常用 API 場景與參數。最後定義了回傳的賽事與賠率資料結構。

**AI 開發需要注意的部分**：
- API 訂閱方案：第一次呼叫 /api/data/{companyCode}/{gameType}/{site}/{subscribeType} 可取得今明兩天所有未結束賽事，之後加上 lastAccessTime 參數可取回該時間點後的變動資料
- WebSocket 訂閱方案：需使用 .NET Core 客戶端建立連線，資料壓縮為 Gzip
- 心跳機制：回傳 SiteGamesDto.HeartBeat 欄位為 0 表示正常資料，為 1 表示固定時間發送一次全部資料
- 賠率格式：Odds.Odds 中的 Odd 數值為不含本金的港式賠率，若對方關盤或無賠率則顯示 -1
- API 驗證：所有 API 請求的 Header 必須包含 X-Auth 作為驗證

**注意事項**：
- ⚠️ 文件最後更新於 2022-09-08，部分資訊可能已過期

---

### 站台停啟用設定

> Confluence 頁面 ID：24091093
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24091093)
> 摘要檔：[processed/24091093-summary.md](../../confluence/processed/24091093-summary.md)
> Confluence 最後更新：2023-02-16
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文說明了後台「站台停啟用設定」的 UI 操作方式，可依球種查詢各站台，並切換其啟用或停用狀態，以控制該站台的賠率是否輸出顯示。開發時需考量此設定對賠率生成邏輯的影響。

---

### 聯盟設定值維護-聯盟

> Confluence 頁面 ID：24089954
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24089954)
> 摘要檔：[processed/24089954-summary.md](../../confluence/processed/24089954-summary.md)
> Confluence 最後更新：2022-10-14
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件說明如何在後台管理聯盟設定值，包括依球種、日期、聯盟名稱等條件搜尋，以及新增、變更、批次變更聯盟設定值的操作流程。重點業務規則為設定值優先順序：賽事設定值 > 聯盟設定值 > 系統設定值。

**AI 開發需要注意的部分**：
- 設定值優先順序為賽事設定值 > 聯盟設定值 > 系統設定值
- 修改聯盟設定值時，已有賽事設定值的賽事輸出不受影響，但僅套用系統設定值的賽事輸出會隨之改變
- 當設定值為「No Set」時，最後更新時間不會更新

---

### 站台連結

> Confluence 頁面 ID：36995137
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=36995137)
> 摘要檔：[processed/36995137-summary.md](../../confluence/processed/36995137-summary.md)
> Confluence 最後更新：2026-05-26
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件是一個外部博彩網站的連結總表，共列出 45 個站台及其對應網址。這份清單定義了 PriceCenter 比價系統需要爬取或串接的外部資料源，每個站台的網址是爬蟲爬取的入口點，VPN 標記則影響網路環境配置。

**注意事項**：
- ⚠️ 部分站台有多個網址，但未說明各網址的角色差異
- ⚠️ Fun88 備註「不能用 Chrome 開」，替代方案未說明

---

### 合併/原始 聯盟隊伍資料維護 API

> Confluence 頁面 ID：24084932
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24084932)
> 摘要檔：[processed/24084932-summary.md](../../confluence/processed/24084932-summary.md)
> Confluence 最後更新：2021-08-03
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件描述後台工具中「合併/原始聯盟隊伍資料維護」的四個 API 操作流程：顯示合併聯盟、修改合併名稱、修改翻譯名稱、顯示合併隊伍。所有操作均透過 PriceCenterService 與資料庫互動。

**AI 開發需要注意的部分**：
- 預設球種設定為 BK，查詢聯盟或隊伍資訊時皆依此球種進行過濾
- 更新名稱與翻譯名稱採用直接覆寫的方式，不回傳更新後的完整資料，僅回傳成功或失敗訊息
- 聯盟與隊伍的查詢介面獨立，由同一個 PriceCenterService 提供端點

---

### 詳細賽果站台

> Confluence 頁面 ID：38012219
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=38012219)
> 摘要檔：[processed/38012219-summary.md](../../confluence/processed/38012219-summary.md)
> Confluence 最後更新：2022-08-03
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件記錄多個外部詳細賽果站台的網址與截圖，如 HGA、Sa8888、Bwin、Betradar 等，主要用於提供賽果數據的來源參考。對於開發 pricecenterservice 或相關爬蟲服務，可作為需要對接或抓取的目標站台清單。

**注意事項**：
- ⚠️ 文件最後更新於2022年8月，所列站台網址可能已變更或失效

---

### 帳密資料

> Confluence 頁面 ID：24091226
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24091226)
> 摘要檔：[processed/24091226-summary.md](../../confluence/processed/24091226-summary.md)
> Confluence 最後更新：2022-01-06
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件記錄了 ZBA 相關的系統帳號與密碼，存放於 PriceCenter Service 的產品項目路徑下。這些帳密可能用於 PriceCenter 相關服務的認證或自動化測試。

**注意事項**：
- ⚠️ 文件最後更新於 2022-01-06，帳密可能已過期或被修改
- ⚠️ 密碼包含特殊字元（如 +、*、\），在程式碼或設定檔中使用時需注意正確的轉義處理

---

### TCZB-613 [PriceCenter]-Bwin/Betfair定期清除Enable=0的賽事（已整合至技術設計類）

> 此文件已整合至技術設計類

---

### TCZB-532 [PriceCenterService] - 合併賽事後臺工具(UI)

> Confluence 頁面 ID：11437164
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=11437164)
> 摘要檔：[processed/11437164-summary.md](../../confluence/processed/11437164-summary.md)
> Confluence 最後更新：2021-01-04
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件为合併賽事後臺工具的早期需求，定义了手动合并赛事功能所需的用户界面和对应 API。

**注意事項**：
- ⚠️ 文件内容极度简略，绝大部分需求留空，无法提取具体规则
- ⚠️ 此需求距今已過三年，可能已过期或被后续迭代取代

---

### Flow Chart

> Confluence 頁面 ID：10813541
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Flow+Chart)
> 摘要檔：[processed/10813541-summary.md](../../confluence/processed/10813541-summary.md)
> Confluence 最後更新：2020-11-11
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件應為 PriceCenterService 的 API 訂閱流程圖，因內容缺失無法確認細節。可能描述服務如何接收或提供數據訂閱的流程。

**注意事項**：
- ⚠️ 文件內容為空，可能流程圖以圖片附件形式存在而未被解析
- ⚠️ 文件最後更新於 2020 年，距今已超過三年，可能與現行系統不一致

---

### HGA借用帳號密碼

> Confluence 頁面 ID：55578088
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55578088)
> 摘要檔：[processed/55578088-summary.md](../../confluence/processed/55578088-summary.md)
> Confluence 最後更新：2024-04-01
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件記錄了 HGA 系統的多個訪問網址以及一組共用帳號密碼。開發人員在與 HGA 平台對接時，可使用這些憑證進行測試或開發。

**注意事項**：
- ⚠️ 文件提供的帳號密碼可能已過期或僅適用於特定環境
- ⚠️ 應避免用於生產環境或洩露

---

### 錯誤問題整理

> Confluence 頁面 ID：47219690
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47219690)
> 摘要檔：[processed/47219690-summary.md](../../confluence/processed/47219690-summary.md)
> Confluence 最後更新：2023-03-14
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
整理人工賽事合併功能目前已知的問題與異常，包含非主站台自動合併、讀取時間過長導致 Timeout、編輯隊伍缺少批量刪除、合併後跳轉到錯誤站台等未解決的錯誤。所有項目均未完成修正。

**注意事項**：
- ⚠️ 所有列出的問題均未標示完成，且缺乏詳細的復現步驟、根本原因或解決方案

---

### 賽事隊伍資訊

> Confluence 頁面 ID：34767575
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=34767575)
> 摘要檔：[processed/34767575-summary.md](../../confluence/processed/34767575-summary.md)
> Confluence 最後更新：2022-05-25
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了賽事隊伍資訊頁面的兩種顯示規則：總覽頁中，網球和足球不顯示總覽資訊；一對一頁面則根據近期是否有對戰紀錄，動態切換兩種不同的顯示格式。

**AI 開發需要注意的部分**：
- 總覽頁：網球和足球球種不顯示總覽資訊區塊
- 一對一頁：需判斷近期是否有對戰紀錄，若無對戰紀錄則顯示「近期無對戰格式」畫面佈局
- 一對一頁：若近期有對戰紀錄，則顯示「近期有對戰紀錄格式」畫面佈局

**注意事項**：
- ⚠️ 文中未說明「近期」的時間範圍定義
- ⚠️ 未說明對戰紀錄的資料來源是哪個 API 或服務

---

## 更新記錄

| 日期 | 更新內容 | 更新人 |
|------|---------|--------|
| 2026-05-28 | 初始版本，整合 79 份 Confluence 文件摘要 | AI 自動生成 |