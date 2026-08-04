# newsservice — DB 操作邊界

> 產出時間：2025-04-06 15:20
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

<!--
【產出規則 — 完成後刪除本段與所有 HTML 註解】
✅ 只寫：欄位誰能改、WHERE 業務理由、敏感欄位、Redis Key/TTL、服務邊界、易錯點
❌ 不要寫：職責描述、技術棧、完整 API 表、Table 用途表、註冊/登入流程步驟（README 已有）
📁 結構：每個相關 DB 一個「## {dbName}」章節；增量更新時只改本次觸發的 dbName 章節，其餘保留
🔗 Schema 連結 db/{dbname}.json；語意總覽連結 db/{dbname}-detail.md（正式路徑，勿連 _temps）
-->

---

## news

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra news | owner | Schema：[db/news.md](../../db/news.md) · 語意：[db/news-detail.md](../../db/news-detail.md) |

### 寫入限制

- **ainews / ainews_gs / ainews_lt** 複合主鍵（`gdate`, `gtype`, `lid`, `gid`, `llmhashkey`, `status`）：  
  寫入時必須提供完整主鍵順序，不允許單獨 UPDATE 主鍵欄位；`status` 由 AINewsService 內部狀態機控制，外部 API 不可直接修改。

- **ainews / ainews_gs / ainews_lt** 之 `question`、`anwser`、`reanwser`：  
  僅 `AINewsService` 自身在 LLM 呼叫完成後寫入，不接受外部寫入請求；`question` 須為原始用戶提問，不可手動篡改。

- **ainews / ainews_gs / ainews_lt** 之 `used`：  
  標記該記錄是否已被消費（0/1），僅 `AINewsService` 在擷取結果後設為 1，不可由其他服務直接更新。

- **ainews / ainews_gs / ainews_lt** 之 `bets`、`llmsettings`、`others`：  
  寫入時應為序列化格式（list / map），需保證類型與 Schema 一致；`llmsettings` 可能包含敏感參數（如模型名稱、溫度），不得未經檢查直接寫入。

- **aireports** 複合主鍵（`gdate`, `gtype`, `lid`）：  
  寫入必須包含完整主鍵，不允許部分更新；`results` 欄位僅由 AI 分析完成後寫入，外部不可主動填充。

- **aifunshits** 主鍵 `funsname`：  
  寫入前須確認 `funsname` 不重複（主鍵唯一）；`aihints` 與 `workspace` 僅由管理後台寫入。

- **sports_{gameType}** 動態表：  
  `id` 為唯一主鍵，寫入時須確保不重複；`addtime` 由服務內部填入當前時間戳，不接受外部指定。

### 讀取規則

- **ainews / ainews_gs / ainews_lt** 查詢：  
  業務查詢需至少給出 `gdate`（partition key）以免全表掃描；常見場景：依 `gdate`、`gtype`、`lid`、`gid` 獲取特定比賽的 AI 回答。  
  如需過濾有效記錄，應加入 `used = 0` 或 `status = 某有效值`（具體值定義見語意文件）。

- **aireports** 讀取：  
  主要透過 `gdate`、`gtype`、`lid` 精確查詢報表；不支援跨 `gdate` 範圍查詢，若需範圍應由上層服務彙整。

- **sports_{gameType}** 讀取：  
  通常依 `date` 與 `lang` 過濾新聞列表；`addtime` 可用於排序但不適合做條件過濾（無索引）。  
  動態表名 `sports_{gameType}` 需由調用方明確指定 gameType，不可模糊匹配。

### 不可回傳欄位

- **ainews / ainews_gs / ainews_lt**：  
  - `question`、`anwser`、`reanwser`：AI 內部對話內容，對外 API 一律隱藏（僅返回 `articleid`、`createtime` 等元資訊）。  
  - `llmsettings`：包含 LLM 模型設定與潛在敏感參數（如 API 金鑰雜湊），不可回傳至客戶端。  
  - `bets`：投注序列化列表，屬於內部分析數據，不對外暴露。

- **aireports**：  
  - `bets`、`results`：原始投注資料與分析結果，僅供內部聚合使用，對外 API 只回傳摘要或統計值。

- **aifunshits**：  
  - `aihints`：內部 AI 提示詞，若暴露可能洩漏模型行為，不應回傳。

- **sports_{gameType}**：  
  - `content`、`link`：新聞原始內容與外部連結，若為付費或授權內容，對外 API 不應直接傳遞。  
  - `tag`：內部標籤，不回傳。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| PostgreSQL games | reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |

> 說明：`games` 邏輯庫包含多張運動比賽表（如 `games_bk`、`games_bm`、`games_bs`、`games_ck` 等），各表結構相似，僅對應不同運動類型；本服務對其僅有查詢權限。

### 寫入限制
- 本服務**完全禁止**對 `games` 下的任何表執行 INSERT、UPDATE、DELETE；比賽資料生命週期由 sportsService 或 dataPipeline 管理。

### 讀取規則
- 查詢任何 `games_*` 表**必須**提供 `gdate`（分區鍵），避免全表掃描；常見查詢條件還包括：
  - `lid`：聯盟識別碼
  - `status`：比賽狀態（如 `PreGame`、`Live`、`Final`）
  - `teamid_h`、`teamid_a`：主／客隊內部 ID
- **不支援**跨 `gdate` 的區間查詢；若需連續多日賽事，請逐日查詢後合併，或使用 sportsService 提供的聚合端點。
- `status` 過濾適合用於區分「進行中」與「已結束」賽事，但應避免高頻輪詢 `status = 'Live'`，建議由即時推送服務取代輪詢設計。
- 不同運動對應的表名（如 `games_bm`、`games_ck`）由業務方根據運動類型明確指定，不可用模糊匹配或萬用字元。
- `games_ck` 欄位較精簡（無 `teams`、`match_h` 等進階數據），查詢前務必確認所需欄位存在，否則須切換至完整表（例如 `games_bm`）。

### 不可回傳欄位

- `siteidmaps`：內部站台 ID 映射，可能包含分潤或追蹤資訊，嚴禁洩漏。
- `match_detail`：逐局／節比分細節，對外應只提供最終比分，原始結構不回傳。
- `resultinfo`、`otherinfo`：擴展結果與雜項資訊，未經清洗的原始數據，不回傳給客戶端。
- `create_at`：純內部審計用時間戳，無業務語意，不回傳。

---

## sport

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| MySQL sport | owner（Notification_Messages） / reader（其餘表） | Schema：[db/sport.md](../../db/sport.md) · 語意：[db/sport-detail.md](../../db/sport-detail.md) |

> 說明：`sport` 邏輯庫包含多張表，newsservice 對 `Notification_Messages` 有完整管理權限，對 `BK_SitePlayers`、`ChatRoomHistories_Backup`、`Community_Groups`、`GameUsers_Wallet`、`GameUsers_Wallet_Transactions` 僅具唯讀權限。

### 寫入限制

- **Notification_Messages**：
  - 複合主鍵（`TID`, `ID`）：寫入時必須同時提供，`ID` 須為唯一訊息識別碼，不可重複。
  - `Enabled`：僅可由管理後台啟用／停用（0／1），一般 API 不得變更；`Enabled=0` 的訊息不得發送。
  - `TW_Content`、`EN_Content`、`CN_Content`、`JP_Content`、`TH_Content`：多語言欄位需至少提供一種語系內容，且內容必須經安全清洗（如移除 HTML 標籤、禁止直接嵌入 JS），以防 XSS。
  - `UpdateTime`：每次 INSERT 或 UPDATE 時由服務層自動設為當前 Unix 時間戳，不接受外部傳入值。
  - `Title`：通知標題，內容同樣須遵循安全限制，不可包含未授權的格式。

- **其餘表（BK_SitePlayers、ChatRoomHistories_Backup、Community_Groups、GameUsers_Wallet、GameUsers_Wallet_Transactions）**：  
  - newsservice **完全禁止**執行任何 INSERT、UPDATE、DELETE，資料生命週期由各自所屬的後端服務維護。

### 讀取規則

- **BK_SitePlayers**：必須提供 `Site`（如 `nba.com`），強烈建議同時帶上 `Year`、`League` 等條件以縮小範圍；不可省略 `Site` 進行全表掃描。
- **ChatRoomHistories_Backup**：必須提供 `GID`；建議加上 `AddTime` 範圍（如 `BETWEEN start AND end`）限制資料量；若需查詢特定使用者訊息，可附加 `Account` 或 `UserName` 過濾。
- **Community_Groups**：查詢啟用中的群組應加上 `WHERE Enabled = 1`；排序請使用 `Seq`；`GType` 用於過濾群組類型（如 `personal`）。
- **GameUsers_Wallet**：僅允許透過 `AuthKey` 精確查詢單一錢包，禁止無 `AuthKey` 的全表掃描或模糊查詢。
- **GameUsers_Wallet_Transactions**：必須提供 `AuthKey`，並應限制 `TDate` 範圍（或 `AddTime`）；查詢時不可省略 `AuthKey`，避免撈取整表。
- **Notification_Messages**：發送時需透過 `TID` 並確認 `Enabled = 1`；管理查詢可依 `TID` + `ID` 或單獨 `TID` 進行。

### 不可回傳欄位

- **ChatRoomHistories_Backup**：
  - `LikeAccount`：點讚者帳號，涉及隱私，對外 API 必須剔除或匿名化。
  - `Account`：若對外顯示用戶身份，應改為 `UserName`，不可直接暴露 `Account`。
- **GameUsers_Wallet**：
  - `AuthKey`：用戶錢包密鑰，嚴禁洩漏。
  - `Balance`：錢包餘額，除使用者本人查詢外不得外流。
- **GameUsers_Wallet_Transactions**：
  - `AuthKey`：同錢包表，需隱藏。
  - `Amount`、`TypeInfo`：交易金額與細節，內部使用，對外回應應過濾或僅保留必要資訊。
- **Notification_Messages**：
  - 各語言內容（`TW_Content`...）：未經授權請求不得返回所有語系，應根據要求語言回傳對應內容，其餘隱藏。
- **BK_SitePlayers**：
  - `Record` JSON：完整數據僅供內部分析，對外 API 應提供摘要而非原始結構。

---

## Redis

本服務未使用 Redis。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 用戶認證與授權 | authService | newsservice 不處理 JWT 簽發、角色驗證；所有請求應由 API gateway 預先鑑權 |
| 比賽資料建立與維護 | sportsService | 比賽（gid、lid、gtype、日期）由 sportsService 管理，newsservice 僅讀取相關 ID 作為主鍵 |
| 投注資料管理 | betService | `bets` 欄位內容由 betService 提供序列化數據，newsservice 不做投注邏輯驗證 |
| 原始新聞抓取 | crawlerService | `sports_{gameType}` 表中新聞的來源爬取與內容清洗由 crawlerService 負責，newsservice 只儲存結果 |
| 用戶錢包餘額與交易 | walletService | newsservice 僅讀取錢包與交易紀錄用於展示，不得進行任何餘額變動或交易建立 |
| 聊天室歷史的備份與遷移 | chatService | `ChatRoomHistories_Backup` 為唯讀快照，newsservice 不得修改或寫入該表 |
| 社群群組建立與成員管理 | communityService | newsservice 只讀取 `Community_Groups` 的基本資訊，群組的建立/編輯/刪除由社群服務負責 |
| 運動賽事統計數據的爬取與寫入 | dataPipeline | `BK_SitePlayers` 為爬蟲或數據管線寫入的結果，newsservice 禁止直接修改 |

---

## 常見錯誤

- ❌ 寫入 `ainews` 時未按 `gdate`, `gtype`, `lid`, `gid`, `llmhashkey`, `status` 順序給主鍵值 → ✅ 必須完整提供主鍵且順序與 Schema 一致。
- ❌ 直接對 `status` 或 `used` 執行 UPDATE 而不經 AINewsService 邏輯 → ✅ 狀態變更應由服務內部狀態機處理，外部僅透過 API 觸發。
- ❌ 查詢 `sports_{gameType}` 時遺漏動態表名參數 `gameType` → ✅ 調用時必須明確拼接完整的表名稱（例如 `sports_football`），無默認值。
- ❌ 回傳 `anwser` 或 `llmsettings` 給前端 → ✅ 這類欄位已在不可回傳列表中，應在 DTO 層過濾掉。
- ❌ 認為 `aireports` 可依 `lid` 單獨查詢（忽略 partition key） → ✅ 須同時提供 `gdate` 避免全區掃描。
- ❌ 試圖對 `games_*` 表執行比分修改或手動校正 → ✅ 比賽資料異動由 sportsService 統一揭露 API，newsservice 無寫入權限。
- ❌ 查詢 `games_*` 漏掉 `gdate` 過濾，導致逐行掃描巨量資料 → ✅ 須強制加入 `WHERE gdate = '2025-04-01'` 或等價條件。
- ❌ 在 API 回應中夾帶 `siteidmaps`、`match_detail` 等原始欄位 → ✅ DTO 層應過濾，僅保留安全且業務必要的欄位。
- ❌ 誤用 `games_ck` 查詢需要 `match_h` 或 `teams` 的場景 → ✅ 確認目標表結構，必要時改用 `games_bm`、`games_bk` 等完整表。
- ❌ 查詢 `BK_SitePlayers` 時遺漏 `Site` 條件 → ✅ 必須總是提供 `Site` 過濾，否則將觸發全表掃描。
- ❌ `ChatRoomHistories_Backup` 查詢時只過濾 `GID` 而無時間範圍 → ✅ 應同步綁定 `AddTime` 區間，避免載入過多歷史資料。
- ❌ 直接將 `Account` 或 `AuthKey` 回傳給客戶端 → ✅ 使用 `UserName` 或去識別化值取代，錢包相關欄位僅限本人查詢時回傳。
- ❌ 嘗試透過 newsservice API 更新 `GameUsers_Wallet.Balance` → ✅ 錢包異動必須呼叫 walletService 的專用接口。
- ❌ 發送通知時未對 `Notification_Messages` 的內容進行安全轉義 → ✅ 內容必須過濾 HTML/JS，確保無 XSS 風險。
- ❌ 手動設定 `Notification_Messages.UpdateTime` 或 `Enabled` 的值 → ✅ `UpdateTime` 由系統生成，`Enabled` 僅管理後台可改。