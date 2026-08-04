# openclawservice — DB 操作邊界

> 產出時間：2025-04-10 12:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| pricecenter（accounts_AU8, accounts_Fortuna888, accounts_HGA, accounts_HGA2, accounts_KKK, accounts_KU, accounts_NK, accounts_Panda, accounts_TG, accounts_TG999） | writer / reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |
| pricecenter（actionlog） | writer（insert only） | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **password**：僅註冊 API 或密碼修改 API 可寫入；須以雜湊形式儲存（不可明文）；不允許直接 UPDATE 其他欄位時連帶修改。
- **enabled**：僅帳號啟用/停用 API 可寫入（值 0 或 1）；不可透過一般資料修改接口變更。
- **closetime**：僅關閉帳號 API 可寫入；寫入時應同時設定 enabled=0。
- **handler**（`map<text,text>`）：僅後台管理 API 可寫入；寫入前須驗證 map 結構合法（不可含敏感鍵如 password）。
- **account**：主鍵，寫入後不可修改。
- **phone**：僅本人（通過驗證）或後台管理可修改；修改時須驗證格式。
- **username**（存在該欄位的表）：僅註冊或後台管理可設定；需確保同表內唯一（業務邏輯）。
- **actionlog**：僅允許 INSERT（由系統自動記錄），不允許 UPDATE 或 DELETE；所有欄位值由服務內部產生，不可由外部傳入或竄改。

### 讀取規則

- **登入驗證**（accounts_*）：查詢時須 `enabled = 1` 且 `(closetime IS NULL OR closetime = '')`，已關閉或停用帳號不可登入。
- **帳號清單查詢**（accounts_*）：若未指定站台（表），須依 `account` 前綴或目標 table 範圍過濾；不得跨表（UNION 所有 accounts_*）查詢全部帳號。
- **handler 僅內部查詢**：前端 API 讀取帳號資訊時不應回傳 handler 內容；僅供後台管理或排程使用。
- **actionlog 查詢**：必須指定 `date`（分區鍵）以定位分區；若未指定時間範圍，需應用合理預設（如當日）；查詢應限制 `addtime` 範圍防止全分區掃描；對外 API 應限制返回筆數並提供分頁。

### 不可回傳欄位

- **password**（所有表）：任何對外 GET API 皆不可回傳；即使雜湊值也不應洩漏（防離線破解）。
- **phone**（accounts_*）：除本人查詢或後台授權外，不應回傳完整號碼（可考慮遮蔽中間四位）。
- **handler**（accounts_*）：禁止對外回傳，僅後台內部使用。
- **actionlog.detail**：若記錄中包含敏感欄位（例如含密碼、個資），應於序列化時過濾或脫敏。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport PostgreSQL（games_bk, games_bm, games_bs, games_ck） | writer / reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- **id**：自增主鍵，僅 INSERT 時產生，禁止任何 UPDATE 操作修改此欄位。
- **source**：資料來源標識，於記錄建立時由系統根據上游資料設定，不可手動變更。
- **create_at**：記錄建立時間戳（毫秒），由系統在 INSERT 時自動填入，禁止外部傳入或後續修改。
- **status**：比賽狀態（如 'PreGame'、'Final'），僅允許通過內部狀態同步或結果更新流程變更；普通前端 API 不可直接寫入。
- **match_h**、**match_a**、**match_detail**、**resultinfo**：比分與結果相關欄位，僅限比賽結果同步/合併服務寫入；外部模組不得直接 UPDATE。
- **siteidmaps**：跨站點映射資料（JSONB），由內部合併邏輯（如 merge_game.py）生成，禁止外部 API 或手動寫入，且內容變化受版本控制。
- **teams**：額外隊伍結構資訊（JSONB），由內部服務根據合併邏輯維護，不可由前端直接修改；通常為空物件或系統生成。
- **teamid_h**、**teamid_a**：主/客隊內部識別碼，僅在隊伍合併或初始化時由系統根據內部主資料寫入，不可手動修改或偽造。
- **lid**：聯賽 ID，應與聯賽主資料一致；寫入時須確保存在於 leagues 表中，且不可隨意更改指到無效聯賽。
- **otherinfo**：附加資訊，若需寫入應由特定管理 API 控制，且內容須符合 schema 規範，避免濫用。
- 所有寫入操作均應透過對應的服務層介面，不得直接對表執行底層 SQL 語句。

### 讀取規則

- **比賽查詢必須指定日期範圍**：查詢 games_* 表時，務必帶 `gdate` 範圍條件（例如 `WHERE gdate BETWEEN ? AND ?`），避免全表掃描導致效能問題。
- **依運動類型隔離**：不同球種使用獨立實體表（籃球 → `games_bk`，棒球 → `games_bs`，博彩 → `games_bm`，板球 → `games_ck`），前端必須指定 `sport` 並路由至對應表，嚴禁跨表 UNION。
- **狀態過濾**：根據業務場景選用 `status`：
  - 顯示可投注賽事：`status = 'PreGame'`
  - 查詢歷史賽果：`status = 'Final'`
  - 即時或進行中賽事：依目前狀態（如 `'Running'`）過濾，避免一次載入所有歷史資料。
- **組合過濾**：可搭配 `lid`（聯賽）、`teamid_h` 或 `teamid_a`（隊伍）進一步精確查詢，並確保有合適的複合或部分索引。
- **比分明細**：`match_detail` 可依前端需求選擇性回傳（若僅需總分 `match_h`, `match_a` 則可省略），以減少傳輸量。
- **資料量控制**：所有對外 API 均應強制分頁（limit/offset）且限制回傳筆數上限。

### 不可回傳欄位

- **create_at**：內部時間戳記，外部 API 不得暴露（提供 `gdate` 與 `gtime` 即可）。
- **siteidmaps**：包含各來源站的映射細節與內部站台代碼，對終端使用者無意義，嚴禁回傳至前端。
- **teams**：可能含有冗餘的內部隊伍資訊，預設不對外公開；如需回傳應先過濾非公開內容，通常僅用 `team_h`, `team_a` 與 ID 展示。
- **resultinfo** 與 **otherinfo**（部分情境）：若包含內部統計或行政資料，應評估後僅回傳必要欄位，預設不對一般用戶顯示。

針對 `games_ck` 表（欄位較少），同樣適用上述限制，且無 `match_*`、`teams` 等欄位，因此在涉及該表的操作時，需注意欄位存在性與預設值。

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

---

## 常見錯誤

- ❌ 查詢帳號時未加上 `enabled=1` 或 `closetime` 條件 → ✅ 應同時過濾 `enabled=1 AND (closetime IS NULL OR closetime='')`，避免已關閉帳號被誤用。
- ❌ API 回傳中包含 `password` 欄位 → ✅ 應在查詢或序列化時明確排除 password 與 handler（若 handler 含敏感資訊）。
- ❌ 直接對 `accounts_*` 表執行 UPDATE 修改 password 或 enabled 而不經專用 API → ✅ 所有寫入必須通過對應服務接口，禁止裸 SQL 修改。
- ❌ 跨所有 `accounts_*` 表進行 UNION 查詢 → ✅ 每次查詢應限制於單一 site 對應的實體表，或透過 account 前綴指派目標表。
- ❌ 查詢 actionlog 時未指定 `date` 分區 → ✅ 必須帶分區鍵，否則會導致全資料庫掃描，嚴重影響效能。
- ❌ 試圖對 actionlog 執行 UPDATE/DELETE → ✅ actionlog 為僅附加（append-only）表，任何修改操作皆屬錯誤。
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