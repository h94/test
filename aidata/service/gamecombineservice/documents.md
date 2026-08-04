# gamecombineservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 11:30
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---


## 技術設計類


### GameCombineService（自動合併流程）

> Confluence 頁面 ID：47219664
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/GameCombineService)
> 摘要檔：[processed/47219664-summary.md](../../confluence/processed/47219664-summary.md)
> Confluence 最後更新：2023-03-13
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文描述 GameCombineService 的自動合併流程：按遊戲類型開啟獨立線程，週期性將 leagues、teams、games 等資料載入快取；逐一處理各站點尚無 gid 的 sitegames，主站點遊戲直接建立新的 gid、tid、lid 並回寫 DB 與快取，非主站點遊戲則需已有 tid/lid 才能透過 gametime 從快取中匹配 gid 後更新。對於 AI 開發此服務，可明確掌握快取結構、合併優先級與資料庫更新規則。

**關鍵業務規則**：
- 每個 gametype 使用獨立線程執行合併任務。
- 主站點（main site）的 sitegame：必定建立全新 gid，並更新 DB 與 game cache；若關聯的 siteleague 或 siteteam 缺少 tid/lid，則亦建立新的 tid/lid，更新 DB 與 team/league cache。
- 非主站點的 sitegame：若 siteteam 或 siteleague 沒有 tid/lid，則跳過該遊戲，不進行處理。
- 非主站點且擁有 tid/lid 的 sitegame：以 gametime 為比對條件，從 game cache 中查找對應的 gid，並將其更新至 DB。
- 每次線程初始化時，建立空的 league、team、game、siteleagues 快取映射。
- 處理前須逐日（for each days）將 games、teams、leagues 資料載入快取。
- 只針對尚無 gid 的 sitegames 進行合併處理。

**關鍵設計決策**：
- 採用依 gametype 分割的多線程設計，隔離不同遊戲類型的處理。
- 引入本地快取（league、team、game、siteleagues）以減少 DB 查詢次數，提高處理效率。
- 主站點遊戲先建立 id 映射（gid、tid、lid），確保後續非主站點遊戲可以依賴這些映射進行匹配。
- 非主站點若無完整 id 映射則直接跳過，避免建立無效關聯。

**注意事項**：
- ⚠️ 文件最後更新於 2023-03-13，需人工確認目前實作是否有變更（如快取策略、線程模型等）。
- ⚠️ 步驟 6 中提到「get gid form game cache (need to check gametime)」：gametime 的比對邏輯（精確匹配或容許範圍）未明確說明，可能容易誤解，需參考實際程式碼。

**影響範圍**：
- 合併流程的核心邏輯，影響所有球種的自動合併行為
- 快取結構與 DB 更新順序不可輕易變更

---


### TCZB-4359 [AutoMergeService] - 自動合併

> Confluence 頁面 ID：79471609
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471609)
> 摘要檔：[processed/79471609-summary.md](../../confluence/processed/79471609-summary.md)
> Confluence 最後更新：2026-05-20
> 摘要最後同步：2026-05-27

**摘要**：
AutoMergeService 的技術設計，定義從 sitegames 抽取賽事資料，依據球種、站台、聯盟進行合併的流程。透過建立內部 games、leagues、teams 關聯表，以內部 ID 取代外部 ID，並利用模糊比對產生合併建議。說明了測試環境連線、表結構、以及新舊 DB 主鍵差異，為實作自動合併功能提供明確規範。

**關鍵業務規則**：
- 合併時必須依序建立：1) leagues（新聯盟創建）2) teams（需要聯盟資料）3) games（需要團隊資料）。
- 所有 FK 必須使用內部 ID，不得直接使用外部 ID。
- 合併來源主站為 panda，合併站包括 playbet 與 1xbet，聯盟範圍為 nba、mlb，實際查詢需根據 source 欄位比對 teams、games、leagues 表，但最終需指定特定球種與站台，聯盟則查詢所有聯盟。
- games 表進入時需找聯盟關聯 ID，若不存在則新增並回填 ID；teams 同樣處理。
- games 表的 site 欄位必須先初始化為 {panda[]}（疑為 panda），第二階段合併完成後才寫入資料。
- 模糊比對相同賽事時，主站會提供 IDMAP 建議合併結果，該邏輯需參考龍蝦搬遷範例實作。
- sitegames 資料寫入 games 後，產生的 games.id 需回寫至 side_game 的 gid 欄位。
- 合併過程使用 merge_game_xx 表暫存資料，時間範圍為一小時。

**關鍵設計決策**：
- 使用 PostgreSQL asyncpg 作為非同步資料庫驅動。
- 測試環境連線 DB: Games (192.168.9.231:5432)，包含 game_xx、leagues_xx、teams_xx 等分表，區分方式為球種代碼。
- 新資料庫使用 auto increment 主鍵，舊 DB 使用亂數字串主鍵，遷移時需注意對映。
- leagues 表原記錄各站點資訊的 source_name 欄位因合併需求移除，改以 abbr_map 存放各語系簡稱。
- 合併時先產生 games 記錄，再從 games 拆出 leagues 與 teams 進行比對與建立，確保外鍵完整。
- 合併建議儲存格式為 JSON 陣列，包含 site、sitelid、sitegid、sitegdate、sitegtime、swap 等欄位。

**注意事項**：
- ⚠️ 文件中「penda」 疑為筆誤，應為「panda」。
- ⚠️ 合併目標描述中『最後需要指定某些球種與站台, 聯盟是找所有聯盟』語意模糊，需人工確認實際過濾邏輯。
- ⚠️ merge_game_xx 表時間範圍一小時的用途（是指查詢區間還是資料有效區間）未明確說明。
- ⚠️ 模糊比對演算法及 IDMAP 產生方式文件僅提供參考範例，實作細節需從『龍蝦搬遷』查找，此處為待完成項目。
- ⚠️ leagues source_name 欄位移除的替代方案未詳細描述，可能影響跨站點查詢。

**影響範圍**：
- 定義合併流程的資料流與表結構，影響所有合併相關功能
- 新舊 DB 主鍵差異需在遷移時特別處理

---


### TCZB-4359 [AutoMergeService]（第一階段重構）

> Confluence 頁面 ID：79471725
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471725)
> 摘要檔：[processed/79471725-summary.md](../../confluence/processed/79471725-summary.md)
> Confluence 最後更新：2026-05-20
> 摘要最後同步：2026-05-27

**摘要**：
本文是 AutoMergeService 第一階段重構的技術設計，定義了主站賽事合併的 CLI 工具架構。重點在於從 sitegames 表讀取 gid 為空且 siteleagues.lid 已存在的記錄，依序建立/匹配 teams 與 games 後回寫 int8 gid 與 status，採用 asyncpg 直接操作 Games 資料庫，不提供 HTTP API。文件釐清了範圍（不含跨站比對）、觸發方式、表名後綴規則及 Hub 資料依賴，並列出已確認的業務規則與待對齊項目，對 AI 開發合併邏輯的邊界與實作約束具有直接參考價值。

**關鍵業務規則**：
- 僅處理主站（由 --site 指定，預設 panda）且 gid 為空、siteleagues.lid 已有值的 sitegames 記錄。
- 合併順序：先 get_or_create_team（主客隊）並記錄 siteteams.tid，再依 lid+gdate+gtime 查現有 games；不存在則插入 games_{suffix} 並將 status 設定為 sitegames.status 的值，最後將生成的 games.id 以 int8 寫回 sitegames.gid。
- games 已存在時直接沿用其 id，不重複建立。
- 第一階段不進行跨站模糊比對、不寫入 siteidmaps，也不提供 preview/dry-run 子命令（dry-run 參數可能保留但未實作）。
- 依賴 Hub 管線已將完整記錄寫入 siteleagues 並產生 lid；合併服務不新建 league。
- 球種後綴必須與 AppSettings 中的 sport_suffixes 白名單一致，並通過驗證防止 SQL 注入。

**關鍵設計決策**：
- 設計為 BackgroundService（但實際以 CLI 手動/排程觸發，無 HTTP API），降低對外依賴。
- 採用分層架構：Provider 層封裝 asyncpg 資料庫操作，Service 層實作合併流程，便於測試與維護。
- 不從頭建立 league，因為 Hub 已在 siteleagues.lid 中寫入自增 id；合併服務僅讀取該欄位作為關聯，減少重複邏輯。
- 將跨站比對、siteidmaps、preview 等功能延後至第二階段，以降低第一階段複雜度並快速交付主站合併能力。
- 表名使用動態 suffix 拼接並以白名單校驗，兼顧多球種彈性與安全性。
- 合併流程基於 Hub 已落庫的紀錄（sitegames.source 區分站台），不依賴外部 API，確保與 crawler 落庫路徑一致。

**注意事項**：
- ⚠️ 文件 I/O 設計中列出 --dry-run 參數，但 §4 Out of Scope 明確排除 preview/dry-run 子命令，可能為保留參數或未實作，需人工確認實際行為。
- ⚠️ 實作步驟中部分 checkbox 未勾選（如 Phase 2 中止點前後的部分項目），可能部分功能仍在開發中，驗收標準尚未完全滿足。
- ⚠️ 文中描述為「BackgroundService」，但觸發方式為 CLI 手動執行，並非長駐背景服務，易產生混淆；實際上是一個可排程的 CLI 工具。
- ⚠️ 假設中要求 DSN 可被環境變數 TPCRAWLER_PG_DSN 覆寫，但未說明該變數需在何種環境設定，部署時需留意。

**影響範圍**：
- 第一階段合併的實作邊界與約束，不可輕易變更
- 分層架構與表名後綴規則影響程式碼結構

---


### 合併 API 與其受影響之資料庫欄位

> Confluence 頁面 ID：7111735
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=7111735)
> 摘要檔：[processed/7111735-summary.md](../../confluence/processed/7111735-summary.md)
> Confluence 最後更新：2020-09-30
> 摘要最後同步：2026-05-26

**摘要**：
本文檔列出了合併相關 API（自動合併、手動合併、手動刪除、手動拆分）對資料庫的影響範圍，包括 League、SiteLeague、Team、SiteTeam、Game、SiteGame 等資料表及其受影響的欄位。它有助於理解數據合併操作時的變更範圍與數據同步關係。

**關鍵設計決策**：
- 合併操作依自動與手動分為 AutoCombine 與 ManualCombine，手動操作進一步區分有目標合併、無目標合併、刪除與拆分場景。
- 有目標的手動合併僅更新特定欄位（如 lnamemap、logs），無目標時則影響整筆記錄（標記為 *）。
- 刪除操作會移除對應的 League/Team/Game 記錄，以及所有相關 Site 記錄。
- 拆分操作只更新原記錄的 lnamemap 與 logs，並處理相關的 Site 記錄。

**注意事項**：
- ⚠️ 文檔最後更新於 2020 年，可能已有更新或變更，需人工確認當前系統是否仍套用此設計。

**影響範圍**：
- 定義合併 API 對 DB 的寫入範圍，影響所有合併相關功能

---


## 業務規範類


### TCZB-979 [賽事後臺工具]-人工合併功能

> Confluence 頁面 ID：24084774
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24084774)
> 摘要檔：[processed/24084774-summary.md](../../confluence/processed/24084774-summary.md)
> Confluence 最後更新：2021-08-13
> 摘要最後同步：2026-05-27

**摘要**：
本文檔定義一個後台工具，用於人工執行賽事聯盟與隊伍的合併功能。工具可查詢某場比賽前後 30 分鐘內的其他比賽，並透過 API 進行聯盟合併（支援指定主站或合併所有站台）與隊伍合併（支援單站合併、全站合併、隊伍間合併）。合併隊伍時需優先查詢最先合併的站台，且若 tid 已有值則須先驗證 team 表資料。

**關鍵業務規則**：
- 查找比賽時，範圍為該場比賽過去及未來 30 分鐘，且限定在 sitegames_{球種} 底下。
- 合併聯盟 API 中，若不傳入 lid 參數，則以指定 site 為主要站台進行合併。
- 透過各站台聯盟名稱查詢 siteteams 表時，應優先查詢合併聯盟時最先合併的站台。
- 合併隊伍 API 中，若 tid 已有值，需先透過 SQL 檢查 team 表的名稱是否正確，才能繼續合併。

**注意事項**：
- ⚠️ 文檔最後更新於 2021-08-13，可能已過期。
- ⚠️ API 端點使用內網 IP (192.168.55.83:22302)，可能非生產環境或已變更。
- ⚠️ 需求中的 {球種} 需替換為實際的球種類別，未明確列出所有球種。
- ⚠️ 文件內的問題列表為空，無後續討論或確認紀錄，規則可能有未解決之處。

---

## 歷史決策類


### 無獨立歷史決策文件

> 相關決策記錄分散於技術設計文件中：
> - GameCombineService (pageId=47219664)：採用依 gametype 分割的多線程設計
> - TCZB-4359 [AutoMergeService] (pageId=79471725)：第一階段不含跨站比對的範圍決策
> - 合併 API 與其受影響之資料庫欄位 (pageId=7111735)：手動/自動合併的 DB 影響範圍定義

---

## 操作手冊類


### 無獨立操作手冊文件

> 相關操作說明分散於技術設計文件中：
> - TCZB-4359 [AutoMergeService] (pageId=79471725)：CLI 工具使用方式（--site 參數、球種後綴白名單）
> - TCZB-979 [賽事後臺工具] (pageId=24084774)：人工合併 API 端點與參數說明