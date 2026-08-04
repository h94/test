# sitegameoddservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 11:14
> 完整索引：[aidata/sitegameoddservice/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB-4225 [SiteGameOddService] - 交易所賠率系統

> Confluence 頁面 ID：79468605
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79468605)
> 摘要檔：[processed/79468605-summary.md](../../confluence/processed/79468605-summary.md)
> Confluence 最後更新：2026-03-11
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文定義 SiteGameOddService 的核心業務：從 Redis db5 取得各站台賠率，套用公式 100/(1+港式賠率) 計算股價，並採用 ±0.7 滯後機制以避免微小價格波動導致頻繁更新。同時說明 API 回傳結構、不同球種對應的站台優先順序，以及「球頭定型」規則，即第一筆資料進來後球頭不得變更。

**關鍵業務規則**：
- 股價計算公式：股價 = 100 / (1 + 港式賠率)，結果為浮點數
- 股價更新採用滯後機制：僅當新計算股價與當前股價的差值絕對值達到 0.7 或以上時，才將當前股價更新為新計算股價四捨五入後的整數；否則維持原價格不變。例如當前價格為 50，新計算值在 49.4～50.6 之間則維持 50；若新值 ≥50.7 則更新為 51；若新值 ≤49.3 則更新為 49
- 球頭定型：比賽第一筆賠率資料進入系統後，該場的「球頭」即固定，後續資料不得變更球頭
- 站台優先順序：系統根據球種（gtype）對應的站台列表順序取得賠率資料（見文件中的各球種站台表）

**注意事項**：
- ⚠️ 「球頭」具體定義（如讓球盤口、大小分盤口等）在文件中未明確說明，需人工確認
- ⚠️ 站台順序的實際取用邏輯（是否依序嘗試直到取得有效賠率，或另有合併規則）未在文件中說明，需人工確認

---

### TCZB-2453[API] - SitegameOddService 賠率API

> Confluence 頁面 ID：44665214
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44665214)
> 摘要檔：[processed/44665214-summary.md](../../confluence/processed/44665214-summary.md)
> Confluence 最後更新：2023-02-01
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件定義了 sitegameoddservice 的 REST API，提供依賽事與玩法查詢最新賽前賠率的功能。AI 開發該服務時，需實作兩個端點（版本檢查與歷史賠率查詢），並在查詢邏輯中遵守三條核心規則：1) HA/OU 玩法取球頭賠率差值最小且最新的資料；2) 1X2 玩法僅取最新一筆；3) 賠率值為 -1 的記錄須被排除。資料來源為依球種及年月分割的 odds_his 表。

**關鍵業務規則**：
- HA 和 OU 玩法：若有多筆賠率，選擇球頭賠率相減（差值）最小的那筆；若差值相同，則取最新的一筆
- 1X2 玩法：僅取最新的一筆賠率資料，無需計算差值
- 賠率值為 -1 的資料列必須跳過，不列入計算與考慮

**注意事項**：
- ⚠️ 文件最後更新於 2023-02-01，且位於 Confluence 路徑「舊的Projects 1-200」中，可能代表該專案已歸檔或不再活躍，需人工確認當前服務狀態與 API 是否仍在使用
- ⚠️ 資料庫 IP (192.168.9.234, 192.168.55.80) 為內網地址，可能已變更，請向基礎設施團隊確認現行環境
- ⚠️ 回傳範例中 HA 物件同時包含 'HA' 與 '1X2' 子鍵，可能為筆誤或混用，實際結構需進一步確認

---

## 技術設計類

### Python SitegameOddService API

> Confluence 頁面 ID：47218925
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Python+SitegameOddService+API)
> 摘要檔：[processed/47218925-summary.md](../../confluence/processed/47218925-summary.md)
> Confluence 最後更新：2024-04-02
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件為 SitegameOddService 的 API 參考，定義了即時賠率（單場/多場）、歷史賠率、賠率變動趨勢、寫入檔案、寫入下注紀錄與取得內部 ID 等 REST 端點。對 AI 開發而言，此文件精確描述了賠率查詢的輸入參數（球種、玩法、站台、賽事 ID 等）與回傳的 JSON 結構，是實現數據擷取管道與賠率相關功能的關鍵技術規格。

**關鍵設計決策**：
- 採用查詢參數（GET）搭配路徑參數（POST）的混合設計，單場查詢用 GET，多場次用 POST 傳遞批量參數
- 賠率資料結構以玩法（mode）為頂層 key，內部以讓分/大小值或玩法類型（如 1X2）為次層 key，使結構同時支援多種玩法與不同盤口
- 歷史賠率 API 用年月字串（yyyyMM）作為日期過濾，而非時間區間，簡化查詢粒度

**影響範圍**：
- modes 參數不帶時，回傳該站台賽事的所有玩法賠率（不限定玩法）
- 取得歷史賠率變動趨勢時，num 參數預設 0 回傳全部記錄，大於 0 則只回傳指定筆數
- 寫入下注紀錄 API 中，arg1~arg10 為自定義欄位，由各帳號自行決定意義

**注意事項**：
- ⚠️ 提供 Local 與 PRD 兩個不同 IP 端點，開發時需注意環境切換與主機名稱差異
- ⚠️ 寫入檔案到 55.21 的 API 看起來是內部管理用途，非一般查詢功能，需確認權限與使用場景

---

### 用Claude規劃資料庫

> Confluence 頁面 ID：79471010
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471010)
> 摘要檔：[processed/79471010-summary.md](../../confluence/processed/79471010-summary.md)
> Confluence 最後更新：2026-05-01
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文記錄了使用 Claude 對話設計 PostgreSQL 資料庫的過程，目標是儲存類似 PolyMarket 的多站台體育賽事（以棒球為例）的原始資料和賠率。核心結論是 AI 能快速產出框架，但缺乏效能與業務思考，需工程師以經驗引導調整。最終設計大量採用 JSONB 處理多語言名稱、各局比分、動態賠率等變動結構，並採用反正規化顯示名稱來避免後台查詢 JOIN。

**關鍵設計決策**：
- 多語言名稱從獨立 i18n 表改為存於主表 JSONB：因應不常更新、key 數量不固定、整包讀取等特性，且無需對語言欄位做複雜索引
- 各局比分以 JSONB array 儲存，並採用三元素格式 [局序號, 主隊分, 客隊分] 取代二元素，以防站台資料順序錯亂或跳號
- siteodds 表最終採用一個 market_type 一筆 Row，將所有 line 及其 selections（含賠率）合併成單一 JSONB，方便整包替換，利用 INSERT ... ON CONFLICT ... DO UPDATE 機制避免逐行更新
- 在 sitegames_bs 等表反正規化 display_name 欄位，存放站台原始提供的單一顯示名稱，節省後台查詢時的 JOIN
- 將 current_period、period_phase 合併為單一 JSONB 欄位 playbyplay，以適應不同球種和站台提供的變動結構
- 比賽日期與時間拆分為 gamedate、gametime 兩欄位，為 gamedate 建立索引以利依日期查詢，gametime 不單獨建索引，而是依賴 gamedate 索引過濾後再排序
- sitegames_bs 加入 gid（內部整合賽事 ID）以支援「某場整合賽事包含哪些站台比賽」的高頻查詢
- siteteams 與 siteleagues 分別加入 tid、lid 作為輔助欄位，雖非高頻熱路徑，但無明顯缺點，可省去後台偶發查詢的 JOIN
- 統一採用 VARCHAR 而非 CHAR，因 PostgreSQL 中 CHAR 無效能優勢且可能自動補空白，適合少數固定長度欄位（如語言代碼）才用 CHAR
- 即使 market_type 增至 50 種以上仍採用 JSONB，前提是應用層能承擔型別驗證責任，以降低寫入成本並簡化維運

**影響範圍**：
- 同一 market_type 的賠率（如 total_ou 下的所有 line）通常會整組變動，更新時應整包替換而非逐行更新，以避免遺留已關閉盤口，亦無需額外維護 is_active 狀態
- 多語言名稱（如隊伍名稱）屬於不常更新、總是整包讀取的資料，適合以 JSONB 儲存在主表
- 各局比分更新頻率不高，讀取時多為整包取出，符合 JSONB 儲存條件
- 後台管理只需一個可識別的顯示名稱（display_name），多語言名稱可留待前台透過 Redis 取得，設計上不必反正規化多語言至遊戲表
- 通用欄位命名應避免球種限定詞（如 innings），改用 match_detail 以適應不同運動的「節」概念

**注意事項**：
- ⚠️ 文件附掛的最終版 DDL（postgresql_last.txt）未內文呈現，需另行下載檢視完整 schema
- ⚠️ 「應用層承擔型別驗證責任」是選擇純 JSONB 的前題，若應用層無法保證，需回退至混合方案（部分結構化欄位）
- ⚠️ 比分儲存格式依賴「站台資料依序連續無跳號」的假設；若資料品質不佳，應選用防禦性三元素格式

---

### TCZB-3897 [SiteGameOddService] - 歷史賠率改寫

> Confluence 頁面 ID：79464274
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464274)
> 摘要檔：[processed/79464274-summary.md](../../confluence/processed/79464274-summary.md)
> Confluence 最後更新：2026-02-11
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文說明將 sitegameoddservice 的歷史賠率資料來源從資料庫改為 Loki 日誌系統。給出兩個主要 API（取得歷史主要賠率、取得賠率歷史變動）的請求參數與回傳格式，並提供 Loki 查詢的端點、query_range 參數及限制條件。開發者可藉此理解如何重構歷史賠率查詢以適應 Loki 資料源。

**關鍵設計決策**：
- 歷史賠率資料從關聯式資料庫改為從 Loki 的日誌索引中查詢，推測目的是利用日誌系統統一存儲與查詢歷史數據，減少 DB 依存
- 採用 Loki HTTP API /loki/api/v1/query_range 進行範圍查詢，使用 logql_query、起迄時間、limit=1000 等參數，推測後端需構建對應的 LogQL 語句來過濾站台賽事 ID 與球種等條件

**影響範圍**：
- 此改寫影響所有歷史賠率相關的查詢端點

**注意事項**：
- ⚠️ 文中未說明 Loki 查詢所需的確切 LogQL 寫法，僅提供 query_range API 呼叫格式，實作時需自行設計 LogQL
- ⚠️ limit=1000 可能導致資料被截斷，需確認是否需支援分頁或更大範圍查詢
- ⚠️ 舊 sitegameoddservice 文件（Python SitegameOddService API）可能已過時，需與現有實作對比

---

### WebSocket Api Document

> Confluence 頁面 ID：18646022
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/WebSocket+Api+Document)
> 摘要檔：[processed/18646022-summary.md](../../confluence/processed/18646022-summary.md)
> Confluence 最後更新：2021-05-17
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了 WebSocket 推送即時賽事數據的訊息結構，包含球種（GameType）、來源（Site）及多場比賽的賠率與比分資訊。巢狀結構將同一時間的所有比賽資料一次傳送，前端可直接解析並呈現即時賠率、比分，減少輪詢需求，對開發即時數據推送與前端呈現模組有直接幫助。

**關鍵設計決策**：
- 採用巢狀 JSON 結構，將同站點下多場比賽的賠率與比分全部包裹在 SiteGames 陣列中，一次性推送完整資料，而非逐場更新，以降低 WebSocket 訊息數量與前端狀態同步複雜度
- 賠率欄位 Odd 以整數型態儲存，可能隱含需要前端自行轉換為小數顯示，避免浮點數精度問題
- PlayMode 與 Prices 中有子結構劃分主盤（Main）及不同玩法，允許同一比賽帶有多組賠率組合，並以 OddType 區分主/客，利於彈性呈現多種投注選項

**影響範圍**：
- 此文件定義的訊息結構影響前端賠率、比分呈現模組的開發

**注意事項**：
- ⚠️ 文件最後更新於 2021-05-17，距今已超過兩年，數據結構可能已變更或擴充，使用前需確認是否與現行 WebSocket 推送格式一致
- ⚠️ 部分欄位（如 OriginSpread、V）值為 null 且無明確說明，實際使用時需注意空值處理邏輯

---

## 歷史決策類

*未找到 sitegameoddservice 的歷史決策類 Confluence 文件*

---

## 操作手冊類

*未找到 sitegameoddservice 的操作手冊類 Confluence 文件*