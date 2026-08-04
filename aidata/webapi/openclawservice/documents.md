# OpenclawService — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB-4262 [OpenClawService] - 隊伍合併檢查

> Confluence 頁面 ID：79469160
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469160)
> 摘要檔：[processed/79469160-summary.md](../../confluence/processed/79469160-summary.md)
> Confluence 最後更新：2026-03-26
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義 OpenClawService 檢查隊伍合併資料（teams.tnamemap）錯誤的流程與業務規則。檢查兩個異常：隊伍被合併到明顯不同聯盟（如 MiLB 合到 MLB），以及同一隊伍在不同站台被合併成明顯不同的隊伍名稱。結果寫入 Redis，只檢查主站台，足球球種因聯盟過多需指定 lid 查詢，附帶賽視為正常案例不報錯。每週一早上 8:30 定時執行。

**關鍵業務規則**：
- 隊伍合併檢查核心規則：league_name 與 tnamemap 中的 SiteLID 明顯不同（如 MiLB 被合到 MLB），視為合併錯誤
- 團隊名稱明顯不同規則：team_name 與 tnamemap 中的 SiteTID 明顯不同，視為合併錯誤
- 附帶賽例外規則：如果 lname 或 SiteLID 包含 'play off' 文字，則視為相同聯盟，不報錯
- 只檢查主站台規則：合併檢查只過濾並檢查主站台的資料，其他站台忽略
- 足球球種查詢限制：足球球種聯盟過多，呼叫 GET /api/check-team/teams/{game_type} 必須帶 lid query 參數，否則回傳 400 錯誤
- 合併資料欄位解析規則：tnamemap 中的 SiteLID 和 SiteTID 如為中英文，直接與 lname 和 tname 比對是否明顯不同；如為數字，則在同站內有多筆合併紀錄時，檢查是否有不同 SiteLID/SiteTID
- 資料寫入規則：檢查出的異常資料格式與 GET teams API 回傳格式相同，但 tnamemap 只包含有問題的合併結果，透過 POST /api/check-team/wrong-teams-merge/{game_type} 寫入 Redis db3（55.80）
- 定時執行規則：此檢查流程每週一早上 8:30 執行一次，並非即時觸發

**注意事項**：
- ⚠️ 需人工確認：文件中提到的站台代碼對照表（如 BK=napoleon, TB=1xbet.com）是靜態清單，若未來新增站台，需更新此檢查邏輯
- ⚠️ 過期資訊或變更：文件提到「過濾其他站台，先只檢查主站台」，但過濾條件僅描述為「特定 Site」，具體判斷是否為主站台的邏輯未明確（需人工確認是否為 tnamemap 中不包含 JSON 格式的站台）
- ⚠️ 容易誤解：規則「某個站 SiteTID 有好幾個明顯看出來是不同隊伍的」中「明顯不同」的判斷標準未明確定義，可能依賴人工比對或模糊匹配，開發時需定義確切比對邏輯
- ⚠️ 未實現功能：文件提到「之後要想的功能」包含 Web 後台過濾清單，但此功能未開發，且前提是誤報率要低，目前無此後台

---

## 技術設計類

### TCZB-4284 [OpenClawService] - 站台聯盟合併

> Confluence 頁面 ID：79469834
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469834)
> 摘要檔：[processed/79469834-summary.md](../../confluence/processed/79469834-summary.md)
> Confluence 最後更新：2026-04-08
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
描述 OpenClawService 的站台聯盟合併功能：以具有系統內部 lid 的「主站台」聯盟為核心，查找其他站台尚無 lid 的相同聯盟，建立 mapping 後寫入 openclaw_mergeleague 表。處理未來 24 小時內有賽事的聯盟，並會聚合歷史已有的合併結果；TN 與 ES 等特殊站台則將多個聯盟合併為一個。提供 API 規格、DB schema 與關鍵業務規則。

**關鍵設計決策**：
- 只處理主站台有 lid 且其他站台無 lid 的配對，因為已有 lid 的聯盟會由系統其他自動機制處理，避免重複工作
- 採用查詢 → 寫入的兩階段設計，先透過 GET API 取得可合併的主/其他聯盟清單，再由後續服務或手動觸發寫入
- 歷史合併結果聚合：每次寫入時都從 DB 讀取已存在的合併目標並與新目標合併，保持最終映射完整
- 針對 TN/ES 因聯盟過多而簡化為單一聯盟，減少前端呈現複雜度

**影響範圍**：
- 僅處理未來 24 小時內有賽事（sitegames）的聯盟，以每小時為單位分批請求
- 主站台查詢結果（main_league）僅包含確認有系統 lid 的聯盟，無 lid 者忽略
- 其他站台的合併目標僅挑選沒有 lid 的聯盟
- 寫入 DB 時必須將新目標與舊目標合併後一同寫回
- TN 與 ES 站台的聯盟處理方式特殊：直接使用球王提供的聯盟，並將多個子聯盟合併為一個總聯盟
- 合併結果透過 POST /api/merge_league/pending-result/<game_type> 寫入，payload 需包含主站台資訊與目標聯盟陣列

**注意事項**：
- ⚠️ 文件未明確說明其他站台聯盟與主站台聯盟的比對規則（如名稱完全相等或模糊匹配），需人工確認實作細節
- ⚠️ DB 欄位 siteidmaps 的存儲格式（可能是 JSON 或特殊分隔字串）未提供範例，實作前須查閱程式碼或補充規格
- ⚠️ TN/ES 的處理邏輯「直接拿球王的聯盟」與一般站台透過 siteleagues 查詢 lid 的流程不同，需進一步確認其實作邊界

---

### TCZB-4241 [OpenclawService] 賽事合併應用(龍蝦API)

> Confluence 頁面 ID：79468888
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79468888)
> 摘要檔：[processed/79468888-summary.md](../../confluence/processed/79468888-summary.md)
> Confluence 最後更新：2026-03-19
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
描述 OpenclawService 的賽事合併功能，提供兩支 GET API 分別查詢 games 與 sitegames（含聯盟、隊伍多語翻譯），供外部系統「龍蝦」排程取得資料並以模糊比對進行合併，結果按球種回傳並寫入 PRD DB 新表 openclaw_merge_<game_type>。合併比對依賴詞集關鍵字匹配，容許時間差 10-15 分鐘，支援主客隊互換辨識；GPT 合併方案已棄用，現改為本地腳本透過 Windows 排程全自動執行。定義了合併服務的 API 合約、資料格式、排程規則與已知限制。

**關鍵設計決策**：
- 捨棄 GPT 合併方案，採用龍蝦本地執行模糊比對，因早期 GPT 測試結果不佳且消耗 token
- 透過 Windows 排程器觸發腳本，每個整點執行一次，將整個流程封裝為獨立排程任務
- 每次僅查詢一小時範圍的資料（共 12 次循環），避免單次資料量過大；最初設計為每次兩小時，後續修改為一小時
- 合併結果獨立儲存於新表 openclaw_merge_<game_type>，以 gdate、lid、id 為分區鍵和叢集鍵
- 對於非英文名稱翻譯障礙，提供手動觸發的翻譯快取機制（透過龍蝦訊息請求），但不內建自動翻譯

**影響範圍**：
- 定時任務每整點執行一次，處理從當前整點到隔天同一整點之間每小時的資料（例如 16:00 執行，處理 16:00-17:00、17:00-18:00... 直到隔天 15:00-16:00，共 12 個小時）
- /api/merge/games 與 /api/merge/sitegames 均透過 query 參數 date、start_time、end_time 過濾，一次性返回該時段所有球種的比賽資料
- 合併結果為 dict，key 為 game_type（球種代碼如 SC、BK），value 為合併物件陣列
- 合併邏輯採用模糊比對，將聯盟名稱與隊伍名稱拆分為關鍵字集後比對，時間相近 10-15 分鐘視為相同
- 寫入合併結果使用 POST /api/merge/pending-result/<game_type>，資料存入 PRD DB 新表 openclaw_merge_<game_type>

**注意事項**：
- ⚠️ 時間範圍規則有不一致：前半段描述「每次拿兩小時的資料」，後半段給龍蝦的指示為「一次只拿一個小時的資料」，最終排程採用後者；需確認並統一口徑
- ⚠️ GPT 合併方案已棄用，但文件中仍保留其 prompt、API key 位置等資訊，開發時不應依賴或實作此路徑
- ⚠️ 合併結果寫入 PRD DB，IP 192.168.55.80，表名 openclaw_merge_<game_type>，CQL 範例為 test_openclaw_merge_SC，正式表結構可能略有差異，需與實際 DB 對照
- ⚠️ 聯盟名稱過長或非英文名稱無法自動化處理，屬於已知缺陷，需評估是否投入自動翻譯或改善比對演算法，否則合併涵蓋率受限
- ⚠️ 文中所有 IP 位址（55.87、55.80）為內網環境，外部開發需透過 VPN 或對應叢集 IP 訪問

---

## 歷史決策類

### TCZB-4241 [OpenclawService] 賽事合併應用(龍蝦API)

> Confluence 頁面 ID：79468888
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79468888)
> 摘要檔：[processed/79468888-summary.md](../../confluence/processed/79468888-summary.md)
> Confluence 最後更新：2026-03-19
> 摘要最後同步：2026-05-27

**決策背景**：
早期嘗試使用 GPT 進行賽事合併，但測試結果不佳且消耗大量 token，需要找到更經濟有效的合併方案。

**決策結論**：
捨棄 GPT 合併方案，改為龍蝦本地執行模糊比對。透過 Windows 排程器每個整點觸發腳本，將聯盟名稱與隊伍名稱拆分為關鍵字集後比對，時間相近 10-15 分鐘視為相同。實現零 token 成本全自動化合併。

**影響**：
- 合併邏輯依賴本地模糊比對，不應依賴或實作 GPT 路徑（但文件中仍保留相關資訊）
- 非英文名稱翻譯障礙仍需透過手動通知龍蝦觸發翻譯快取，無法全自動化
- 合併涵蓋率受限於比對演算法和翻譯問題，屬於已知缺陷

### TCZB-4262 [OpenClawService] - 隊伍合併檢查

> Confluence 頁面 ID：79469160
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469160)
> 摘要檔：[processed/79469160-summary.md](../../confluence/processed/79469160-summary.md)
> Confluence 最後更新：2026-03-26
> 摘要最後同步：2026-05-27

**決策背景**：
需要自動化檢查隊伍合併資料的錯誤，包括聯盟錯誤和隊伍名稱明顯不同。

**決策結論**：
採用定時任務（每週一早上 8:30）而非即時檢查，使用 Redis（db3, 55.80）暫存結果而非寫入資料庫。足球球種因聯盟數量過多，強制要求指定 lid 查詢。白名單/過濾功能（Web 後台）暫緩開發，因誤報率可能過高導致人工過濾成本不划算。

**影響**：
- 資料合併錯誤不必立即修正，採用定期檢查降低系統負載
- 目前功能僅止於偵測與記錄，不具備自動排除機制
- 站台代碼對照表為靜態清單，新增站台需更新檢查邏輯
- 「明顯不同」的判斷標準未明確定義，影響誤報率和準確性
- Web 後台過濾功能未實作，依賴人工介入排解

### TCZB-4284 [OpenClawService] - 站台聯盟合併

> Confluence 頁面 ID：79469834
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469834)
> 摘要檔：[processed/79469834-summary.md](../../confluence/processed/79469834-summary.md)
> Confluence 最後更新：2026-04-08
> 摘要最後同步：2026-05-27

**決策背景**：
需要自動化站台聯盟合併，建立主站台聯盟與其他站台聯盟的 mapping 關係。

**決策結論**：
只處理主站台有 lid 且其他站台無 lid 的配對，避免重複工作。採用查詢 → 寫入的兩階段設計，歷史合併結果聚合確保完整性。TN/ES 因聯盟過多而簡化為單一聯盟，減少前端呈現複雜度。

**影響**：
- 已有 lid 的聯盟會由系統其他自動機制處理，不在此服務範圍
- 其他站台聯盟與主站台聯盟的比對規則未明確說明，需確認實作細節
- DB 欄位 siteidmaps 的存儲格式未提供範例，實作需查閱程式碼
- TN/ES 的處理邏輯「直接拿球王的聯盟」與一般站台流程不同，需確認實作邊界

---

## 操作手冊類

### TCZB-4241 [OpenclawService] 賽事合併應用(龍蝦API)

> Confluence 頁面 ID：79468888
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79468888)
> 摘要檔：[processed/79468888-summary.md](../../confluence/processed/79468888-summary.md)
> Confluence 最後更新：2026-03-19
> 摘要最後同步：2026-05-27

**摘要**：
OpenclawService 的賽事合併功能透過兩支 GET API（/api/merge/games 與 /api/merge/sitegames）提供遊戲和站台遊戲資料，供「龍蝦」系統進行合併。合併結果透過 POST /api/merge/pending-result/<game_type> 寫入 PRD DB。

**AI 開發需要注意的部分**：
- Windows 排程器每個整點執行一次，處理未來 12 小時內每小時的資料（每次僅查詢一小時範圍）
- API 透過 query 參數 date、start_time、end_time 過濾，一次性返回該時段所有球種資料
- 合併結果存於 PRD DB（IP 192.168.55.80）的 openclaw_merge_<game_type> 表
- GPT 合併方案已棄用，開發時不應依賴或實作此路徑
- 非英文名稱翻譯僅能手動觸發，無法自動化處理

### TCZB-4262 [OpenClawService] - 隊伍合併檢查

> Confluence 頁面 ID：79469160
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469160)
> 摘要檔：[processed/79469160-summary.md](../../confluence/processed/79469160-summary.md)
> Confluence 最後更新：2026-03-26
> 摘要最後同步：2026-05-27

**摘要**：
隊伍合併檢查功能定時執行，檢查 teams.tnamemap 中的錯誤合併，結果寫入 Redis 供後續使用。

**AI 開發需要注意的部分**：
- 檢查流程每週一早上 8:30 執行一次，非即時觸發
- 只檢查主站台資料，需確認主站台過濾邏輯
- 足球球種呼叫 GET /api/check-team/teams/{game_type} 必須帶 lid 參數，否則回傳 400 錯誤
- 異常資料透過 POST /api/check-team/wrong-teams-merge/{game_type} 寫入 Redis db3（55.80）
- 「明顯不同」的判斷標準需定義確切比對邏輯，影響誤報率和準確性

### TCZB-4284 [OpenClawService] - 站台聯盟合併

> Confluence 頁面 ID：79469834
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469834)
> 摘要檔：[processed/79469834-summary.md](../../confluence/processed/79469834-summary.md)
> Confluence 最後更新：2026-04-08
> 摘要最後同步：2026-05-27

**摘要**：
站台聯盟合併功能以主站台有 lid 的聯盟為核心，查找其他站台無 lid 的相同聯盟，建立 mapping 後寫入 openclaw_mergeleague 表。

**AI 開發需要注意的部分**：
- 僅處理未來 24 小時內有賽事（sitegames）的聯盟，以每小時為單位分批請求
- 主站台查詢結果僅包含有系統 lid 的聯盟，無 lid 者忽略
- 寫入 DB 時必須將新目標與舊目標合併後一同寫回，聚合歷史合併結果
- TN 與 ES 站台處理方式特殊：直接使用球王提供的聯盟，將多個子聯盟合併為一個總聯盟
- 比對規則未明確說明（名稱完全相等或模糊匹配），DB 欄位 siteidmaps 存儲格式未提供範例，實作前需查閱程式碼