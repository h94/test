# openclawservice — DB 操作邊界

> 產出時間：2025-04-11 12:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| pricecenter Cassandra（accounts_*、games_SC/BK、teams_SC/BK、leagues_*、sitegames_*、siteleagues_*、siteteams_*、odds_*、aimerge_match_predictions、aimerge_predictions_by_id） | writer / reader | Schema：[db/pricecenter.json](../../db/pricecenter.json) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **accounts_* 密碼與敏感欄位**
  - `password`：僅註冊 API 或密碼修改 API 可寫入，須雜湊儲存；禁止直接 UPDATE 其他欄位時連帶修改。
  - `enabled`：僅帳號啟用/停用 API 可寫入（0 或 1），其他流程不可變更。
  - `closetime`：僅關閉帳號 API 可寫入，寫入時應同時將 `enabled` 設為 0。
  - `handler`（`map<text,text>`）：僅後台管理 API 可寫入，寫入前須驗證結構合法且不可包含密碼等敏感鍵。
  - `account`：主鍵，寫入後永久不可修改。
  - `phone`：僅本人或後台可修改，格式需驗證。
  - `username`：若表有此欄位，僅註冊或後台設定，同表內需保持唯一。

- **基礎資料表（games_SC/BK、teams_SC/BK、leagues_*）**
  - 本服務僅讀取，嚴格禁止任何 INSERT、UPDATE、DELETE 操作；此類資料由其他服務（爬蟲、基礎資料管理）維護。

- **站點映射表（sitegames_SC/BK、siteleagues_SC/BK、siteteams_SC/BK）**
  - 同為只讀表，本服務不負責站點資料的建立或修改；所有站點映射寫入由專屬的站點資料服務處理。

- **賠率表（odds_SC/BK）**
  - 僅讀取；賠率寫入屬於外部賠率採集或計算服務。

- **AI 合併預測表（aimerge_match_predictions、aimerge_predictions_by_id）**
  - `prediction_id`：寫入後不可變更。
  - `score`、`score_detail`：由匹配引擎依據特徵計算，禁止手動設定或覆寫。
  - `status`：僅允許透過預測狀態機（auto_confirmed / pending / conflict 等）或人工審核接口變更；不允許直接 UPDATE 跳過審核流程。
  - `reviewed_at`、`reviewed_by`：僅在人工審核時填入，其他流程不可置換。
  - `inferred_via`：由內部推理邏輯自動記錄，不允許外部傳入。
  - `merge_status` 等合併追蹤欄位（若存在）：僅由合併服務寫入，不開放給其他模組。
  - `aimerge_predictions_by_id`：輔助表，寫入時必須與主預測表保持事務一致性，不可單獨維護。

### 讀取規則

- **帳號認證（accounts_*）**
  - 登入查詢必須附加 `enabled = 1` 且 `(closetime IS NULL OR closetime = '')`；已關閉或停用帳號不允許登入。
  - 後台查詢帳號時，須指定目標站點對應的實體表（如 `accounts_AU8`），禁止跨表 UNION 全部帳號。

- **比賽與隊伍基礎資料**
  - 查詢 `games_SC/BK` 時，必須同時指定 `gdate` 範圍；不允許全表掃描。
  - `teams_SC/BK`、`leagues_*` 依主鍵或聯盟 ID 精準查詢，必要時搭配 `lid` 過濾。

- **站點資料（sitegames、siteleagues、siteteams）**
  - 任何查詢都必須包含 `site` 分區鍵；`sitegames` 還應帶 `gdate` 作為輔助條件，禁止跨站全掃。
  - 取得單一站點比賽時可加上 `sitegid`，但不允許僅以 `gid` 進行無索引掃描。

- **賠率快照（odds_SC/BK）**
  - 查詢必須攜帶與 `site` 及 `sitegid` 相關的條件，避免跨分區讀取；僅用於內部計算，不直接提供給前端 API。

- **AI 預測與合併相關**
  - `aimerge_match_predictions` 所有查詢必須包含 `game_type` 和 `gdate`（分區鍵）；可選加 `source_b` 縮小範圍。
  - 查詢待審核項目應過濾 `status = 'pending'`，並限制最大回傳筆數。
  - 若需依 `prediction_id` 查詢，請使用 `aimerge_predictions_by_id` 索引表，避免對主表進行跨 partition 掃描。

### 不可回傳欄位

- `password`：任何對外 GET API 均不可回傳，雜湊值也不得洩漏。
- `handler`：僅供後台內部使用，前端不可見。
- `phone`：除本人查詢或明確授權外，應遮蔽中間位數或完全隱藏。
- `odds_*` 表的內部配置參數：不對外暴露。
- `sitegames` 的 `swap`、`match_h`、`match_a`、`addtime`、`mainspread` 等內部匹配輔助欄位：預設不輸出給終端用戶。
- `aimerge_match_predictions` 的 `score_detail`：可能包含調試資訊，未脫敏前禁止作為 API 回傳欄位。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport PostgreSQL（games_bk、games_bm、games_bs、games_ck） | writer / reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |
| Games.public（aimerge_backtest_runs、aimerge_daily_reports、aimerge_historical_runs、aimerge_label_overrides、aimerge_match_predictions、aimerge_runtime_config、aimerge_source_mapping、aimerge_team_aliases） | writer / reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- **比賽主表（games_bk / bm / bs / ck）**
  - `id`：自增主鍵，僅 INSERT 時生成，嚴禁 UPDATE。
  - `source`：由系統根據上游資料設定，不可手動變動。
  - `create_at`：系統自動填入，外部不可傳入或修改。
  - `status`：僅通過內部狀態同步或結果更新流程變更；禁止一般 API 直接寫入。
  - `match_h`、`match_a`、`match_detail`、`resultinfo`：比分與結果欄位，僅由結果同步 / 合併服務寫入。
  - `siteidmaps`：由內部合併邏輯產生，不可手動變更。
  - `teams`：由系統維護，外部不得直接修改。
  - `teamid_h`、`teamid_a`、`lid`：比賽建立後不可任意修改，須與對應的主資料保持一致。
  - 所有寫入須經由服務層對應介面，不得裸操作 SQL。

- **AI 回測與報表（aimerge_backtest_runs、aimerge_daily_reports、aimerge_historical_runs）**
  - 僅由系統排程（回測、報表產生、歷史學習）寫入；人工不得直接 INSERT 或 UPDATE 任何欄位。
  - 歷史執行紀錄 (`aimerge_historical_runs`) 的 `status` 由工作佇列更新，手動修改將導致狀態不一致。

- **標籤覆蓋（aimerge_label_overrides）**
  - `override_label`、`excluded_from_training`、`reason`：僅審核人員可設定；寫入時需記錄 `reviewed_by`、`reviewed_at`。
  - 記錄的 `prediction_id`、`game_a_sitegid` 等識別欄位不可二次更改。

- **AI 預測（PostgreSQL 版本 aimerge_match_predictions）**
  - 與 pricecenter 中的同名表限制類似：`prediction_id` 不變；`score`、`score_detail` 由匹配演算法寫入；`status` 僅經狀態機或審核接口變更。
  - `reviewed_at`、`reviewed_by` 僅於人工審核時賦值。

- **運行時配置（aimerge_runtime_config）**
  - 所有變更必須記錄 `change_reason`、`updated_by`。
  - `is_active` 的切換需確保同一 scope 只有一個啟用版本；不允許直接 DELETE 歷史版本（應保留作為回滾依據）。
  - `params`（jsonb）的內容必須符合預定義的結構，禁止寫入任意鍵值。

- **來源映射（aimerge_source_mapping）與隊伍別名（aimerge_team_aliases）**
  - 映射關係由自動確認或人工審核流程建立，禁止直接修改 `game_a_sitegid` 或 `source_b_sitegid`。
  - 隊伍別名僅允許透過管理工具或匯入腳本新增 / 修改；`confidence` 由評估程序計算，不可手動填寫。

### 讀取規則

- **比賽查詢**
  - 任何 `games_*` 查詢必須包含 `gdate` 範圍條件；不同球種嚴格分流至對應實體表（如籃球 → games_bk），嚴禁跨表 UNION。
  - 顯示可投注賽事：`status = 'PreGame'`；查詢歷史賽果：`status = 'Final'`；進行中賽事依相符狀態過濾。
  - 所有對外 API 強制分頁（limit / offset）並限制最大回傳筆數。

- **AI 相關查詢**
  - `aimerge_match_predictions`（PostgreSQL）：查詢必須提供 `game_type` 和 `gdate` 過濾；依 `status` 縮小範圍，**不允許全表掃描**。
  - `aimerge_runtime_config`：獲取當前生效配置時，應查詢 `is_active = true` 且 `effective_from <= now()`，取最新 `version_id`，並確保 scope 符合球種。
  - `aimerge_team_aliases`：通常搭配 `game_type` 與 `source_id` 查詢，避免僅以 `alias_text` 進行模糊匹配導致性能問題。
  - 回測 / 報表 / 歷史執行表僅供內部分析查詢，應限制時間範圍或主鍵，不對外提供泛用查詢 API。

- **標籤覆蓋**
  - 查詢標籤覆蓋時必須帶 `game_type` 與 `gdate`，並可選 `prediction_id` 進行精確定位；避免一次撈取所有歷史覆蓋記錄。

### 不可回傳欄位

- `create_at`（games 表）：內部時間戳，外部 API 不得暴露。
- `siteidmaps`：含各站點映射細節，對終端無意義，嚴禁回傳。
- `teams`：可能含冗餘內部資訊，預設不對外輸出；若確需展示，僅提供必要欄位。
- `resultinfo` 及其他內部統計：未經脫敏評估前，不對一般用戶開放。
- `aimerge_runtime_config` 的完整 `params`：包含閾值、權重等商業機密，API 應僅回傳必要摘要，避免整包 JSON 洩露。
- `aimerge_backtest_runs` 的 `improved_samples`、`regression_samples`：僅內部調試使用，不應對外。
- `score_detail`（預測表）：含有除錯資訊，生產環境 API 禁止原樣輸出。

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| predict（Cassandra Keyspace） | writer / reader | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **activities_cycles**：分區鍵 `site`、集群鍵 `activityevent` 與 `cid` 組成唯一識別，INSERT 後不得修改；僅透過活動管理 API 變更 `startdate`、`starttime`、`enddate`、`endtime`、`resultcount` 等屬性。
- **activities_record**：主鍵 `(site, eventname, account)` 不可修改；`winbets`、`restday`、`updatedate` 由活動結算服務寫入，外部 API 不可直接寫入或篡改。
- **activities_winneraccounts**：主鍵 `(site, activityevent, cid, account)` 不可修改；統計數據（`predictcount`、`profitpoint`、`rank`、`winpercentage`）僅由活動排名計算批次寫入，其他服務只讀不寫。
- **betpool_bets**：分區鍵 `gid`、集群鍵 `id` 與 `account` 確立投注明細，投注一旦建立即不可刪除或修改 `id`、`betoption`、`betzcoin`。`profitzcoin` 與 `winlose` 僅由獎池結算服務更新，不得由其他流程直接改動。
- **betpool_games**：分區鍵 `id` 不可變更；遊戲的 `starttime`、`endtime`、`status`、`betoptions` 等由遊戲管理服務設定；`payout` 與 `winresult` 須在結算完成後由結算服務寫入，手動變更將導致派彩錯誤。
- **calculatelog**：分區鍵 `weekid` 不可變更；`done` 標記僅由週結算任務翻轉，其他系統僅應查詢，不應寫入。
- **killeraccounts_BK**：分區鍵 `lid`、集群鍵 `cid` 與 `account` 為複合主鍵，記錄新增後不允許直接修改；`avgodd` 等統計值由殺手帳號分析排程產出，禁止人工更正。

### 讀取規則

- **activities_cycles**：查詢活動週期時必須指定 `site` 和 `activityevent`；若查詢當前有效週期，應增加 `startdate <= 今天 AND enddate >= 今天` 條件避免撈出過往資料。
- **activities_record**：查詢特定帳號的活動參與狀態需帶入完整主鍵 `(site, eventname, account)`；不允許全表掃描或僅以 `site` 分區鍵查詢。
- **activities_winneraccounts**：排行榜查詢需提供 `site`、`activityevent`、`cid`，可依 `rank` 排序限制筆數，避免一次載入所有帳號。
- **betpool_bets**：任何查詢都必須包含分區鍵 `gid`；查詢個人投注記錄可再加 `account`；不允許僅用 `account` 做跨分區查詢。
- **betpool_games**：透過 `id` 取得單一遊戲，或利用 `status`、`starttime`/`endtime` 範圍過濾有效遊戲，但應確保使用合適的 ALLOW FILTERING 或設計索引。
- **calculatelog**：依 `weekid` 精準查詢計算狀態；若需歷史查詢須限制時間範圍，避免全分區掃描。
- **killeraccounts_BK**：查詢時務必提供 `lid` 分區鍵；可按 `cid` 或 `account` 進一步篩選。

### 不可回傳欄位

- **無特殊敏感欄位**：目前 predict 中的統計與遊戲資料未發現密碼或個資等高度敏感欄位，但仍建議 API 僅回傳前端所需的欄位，避免洩漏 `feedrate`（內部抽水比例）等商業機密資訊。若後續加入用戶關聯資料，請審慎評估再決定是否過濾。

---

## Redis

本服務未使用 Redis（無相關快取或狀態儲存實作）。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 密碼重設 / 驗證碼發送 | auth-service | openclawservice 僅儲存密碼雜湊，不處理密碼重設流程或簡訊驗證 |
| 帳號註冊 / 第三方登入綁定 | register-service / oauth-service | openclawservice 只維護帳號啟用狀態，不處理註冊邏輯 |
| 帳號餘額 / 交易記錄 | wallet-service | pricecenter 的 accounts_* 表僅存帳號基礎資訊，不含餘額或交易明細 |
| 操作記錄備份 / 歸檔 | log-service（或排程） | actionlog 寫入後，本服務不負責長期儲存或遷移，僅提供查詢接口 |
| 比賽賠率 / 盤口資訊 | odds-service | openclawservice 僅管理比賽基本資訊與比分，所有賠率相關欄位由 odds-service 負責 |
| 隊伍詳細資料（隊員、教練等） | team-service | games 表僅儲存主/客隊 ID 與名稱，隊伍擴展資訊由 team-service 維護 |
| 聯盟資訊管理 | league-service | `lid` 的詳細內容（聯賽名稱、等級等）歸 league-service 管轄 |
| 即時比賽事件/文字轉播 | live-service | 比賽過程中的事件串流不由 openclawservice 處理 |
| 比賽記錄備份／歸檔 | data-pipeline / log-service | openclawservice 不負責 games 表的資料生命週期管理或歷史歸檔 |
| Z 幣的實際加扣款 | wallet-service | predict 的投注與盈利僅為統計記錄，真正的虛擬幣帳務變動由 wallet-service 處理 |
| 活動獎勵派發 | promotion-service | 活動優勝者的實際獎勵發送與通知由 promotion-service 負責 |
| 預測模型訓練與推論 | ai-service | 賽事預測分數的計算與模型管理由 ai-service 執行，openclawservice 只儲存預測結果 |
| 站點帳號爬取與站點資料寫入 | crawler-service / site-data-service | openclawservice 僅讀取 sitegames / siteteams / siteleagues，不負責站點資料的建立與更新 |
| AI 合併參數最佳化建議 | aimerge-optimizer / ai-service | 回測報表與建議由專屬服務處理，openclawservice 僅提供資料存取與觸發 |

---

## 常見錯誤

- ❌ 查詢帳號時未加上 `enabled=1` 或 `closetime` 條件 → ✅ 應同時過濾 `enabled=1 AND (closetime IS NULL OR closetime='')`，避免已關閉帳號被誤用。
- ❌ API 回傳中包含 `password` 欄位 → ✅ 應在查詢或序列化時明確排除 password 與 handler（若 handler 含敏感資訊）。
- ❌ 直接對 `accounts_*` 表執行 UPDATE 修改 password 或 enabled 而不經專用 API → ✅ 所有寫入必須通過對應服務接口，禁止裸 SQL 修改。
- ❌ 跨所有 `accounts_*` 表進行 UNION 查詢 → ✅ 每次查詢應限制於單一 site 對應的實體表，或透過 account 前綴指派目標表。
- ❌ 查詢 `sitegames`、`siteleagues`、`siteteams` 時未帶 `site` 分區鍵 → ✅ 必須攜帶 `site`，並搭配 `gdate` 等條件，避免全表掃描拖垮效能。
- ❌ 手動 UPDATE `aimerge_match_predictions` 的 `score` 或 `status` → ✅ `score` 由匹配引擎決定，`status` 僅能通過審核或狀態機 API 修改。
- ❌ 查詢 `aimerge_match_predictions` 時未帶 `game_type` 和 `gdate` → ✅ 必須同時指定這兩個分區鍵，否則會導致全叢集掃描。
- ❌ 修改 `aimerge_runtime_config` 時未記錄 `change_reason` 或直接刪除舊版本 → ✅ 所有變更須保留歷史，且需通過配置管理 API 寫入。
- ❌ 將 `sitegames` 的 `swap`、`match_h` 等內部調試欄位直接回傳給前端 → ✅ 在 DTO 層過濾，只輸出業務需要的欄位。
- ❌ 手動 UPDATE `id` 或 `create_at` → ✅ 這兩個欄位僅應在 INSERT 時賦值，任何程式碼都不應包含修改邏輯。
- ❌ 查詢比賽忘記 `status` 過濾，一口氣撈出所有歷史記錄 → ✅ 依前端意圖加上 `status = 'PreGame'` 或 `status = 'Final'` 限制。
- ❌ 在同一個 SQL 查詢中 UNION 多個 `games_bk`、`games_bs` 等表 → ✅ 必須根據運動類型分流查詢，且每個請求只應訪問一張實體表。
- ❌ 將 `siteidmaps` 或 `create_at` 直接回傳給前端 → ✅ 在 DTO 或序列化階段明確排除這些欄位。
- ❌ 隨意修改 `status` 與比分，未透過結果同步流程 → ✅ 比分寫入必須由內部服務（如 merge_game）觸發，且寫入時應同時更新 `status` 至對應狀態（例如 'Final'）。
- ❌ 不帶 `gdate` 條件直接 `SELECT * FROM games_bk` → ✅ 所有 API 層查詢必須包含日期範圍，強制使用分頁，並監控查詢效能。
- ❌ 查詢 `betpool_bets` 時未提供 `gid` 分區鍵 → ✅ 任何 betpool_bets 查詢都必須包含 `gid`，避免跨分區掃描拖垮效能。
- ❌ 結算時直接 UPDATE `profitzcoin` 或 `winlose` → ✅ 應透過專屬的結算 API 或排程任務，並記錄相關日誌。
- ❌ 修改 `activities_winneraccounts` 的排名數據而未帶完整主鍵 `(site, activityevent, cid, account)` → ✅ 所有寫入必須指定全部分區與集群鍵，防止誤覆蓋其他帳號。
- ❌ 在無索引的欄位上進行範圍查詢（如 `endtime`）而未啟用 ALLOW FILTERING 或設計二級索引 → ✅ 應評估查詢模式和數據量，必要時建立適當索引或修改資料模型。
- ❌ 直接對 `aimerge_label_overrides` 執行 DELETE 而不是設 `excluded_from_training` → ✅ 標籤覆蓋應保留歷史，建議以邏輯標記方式處理。
- ❌ 查詢 `aimerge_runtime_config` 時未過濾 `is_active` 或 `effective_from`，導致拿到過期配置 → ✅ 應精確查詢當前生效的版本。