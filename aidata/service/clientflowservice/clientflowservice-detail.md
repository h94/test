# clientflowservice — DB 操作邊界

> 產出時間：2025-04-09 14:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Predict Cassandra | writer / reader | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- `activities_cycles`：週期資料由管理後台寫入，本服務不得 INSERT／UPDATE／DELETE。
- `activities_record`：
  - `account`：僅可由通過認證的使用者寫入自己的記錄，嚴禁批次更新或直接寫入他人帳號。
  - `winbets`：清單欄位僅由內部結算邏輯根據投注結果附加，前端 API 不可直接傳入或修改。
  - `restday`：可由管理後台調整，一般使用者 API 禁止變更。
- `activities_winneraccounts`：排行榜資料由結算服務定期寫入，本服務僅可讀取，不得修改排名或勝率。
- `betpool_bets`：
  - `account`：僅可寫入當前登入使用者的投注記錄，禁止跨帳號寫入。
  - `betzcoin`、`profitzcoin`：建立投注時由系統計算寫入（根據遊戲設定），之後不可直接 UPDATE；派彩由結算服務透過特定流程更新。
  - `winlose`：由結算服務根據遊戲結果寫入，一般 API 不可修改。
- `betpool_games`：`status`、`payout`、`winresult`、`basicprofitzcoin`、`bonusprofitzcoin` 等欄位由遊戲設定與結算服務負責維護，本服務僅讀取，不寫入。
- `calculatelog`：結算記錄由排程服務寫入，本服務僅可讀取。
- `killeraccounts_BK`：備份表，資料來源不明確，本服務僅讀取，不寫入。

### 讀取規則

- 活動週期（`activities_cycles`）：依 `site` 與 `activityevent` 過濾，並確認 `enddate` ≥ 當前日期（或根據業務需要取出進行中與未開始的週期），避免取出已過期週期。
- 用戶活動記錄（`activities_record`）：必須包含 `site`、`eventname`、`account`，禁止跨帳號查詢，且只允許查詢自己的 `account`。
- 排行榜（`activities_winneraccounts`）：查詢時必須指定 `site`、`activityevent`、`cid`，並依 `rank` 遞增排序；僅回傳 `winpercentage >= 0` 的有效記錄；若需分頁，應搭配 `rank` 範圍或 `account` 過濾，避免全表掃描。
- 進行中遊戲（`betpool_games`）：只回傳 `status = 1` 且 `payout = false` 的遊戲；可按 `starttime` 或 `endtime` 範圍過濾，亦可依 `hot` 或 `viponly` 做進階篩選；不允許一次載入全部歷史遊戲。
- 用戶投注（`betpool_bets`）：查詢必須附帶當前登入的 `account`（從認證上下文取得），不允許跨帳號撈取；可選擇依 `gid` 或 `addtime` 區間縮小範圍；結算狀態可透過 `winlose` 判讀。
- 結算確認（`calculatelog`）：使用 `weekid` 或 `weekdate` 精確定位，避免掃描多個週期；可搭配 `done = 1` 篩選已完成結算的週期。
- 殺手帳號（`killeraccounts_BK`）：如有需要讀取，應以 `account` 或相關唯一鍵為條件，避免全表掃描；對外查詢時帳號必須遮蔽。

### 不可回傳欄位

- `activities_record.winbets`：包含用戶獲勝注單 ID，直接外洩可能造成競爭資訊暴露，任何對外 API 禁止回傳。
- `activities_winneraccounts.account`：排行榜對外展示時必須遮蔽（如僅顯示前幾個字元 + `***`），不得直接回傳完整帳號。
- `betpool_bets.account`（非本人）：查詢他人投注記錄不得包含帳號欄位；若允許查詢自己的記錄，則可回傳，但應確認呼叫端身份。
- `killeraccounts_BK.account`：同上方規則，對外查詢不得暴露完整帳號。
- `betpool_games.winresult`：在未派彩前對外隱藏，避免影響投注公平性；建議前端只在 `payout = true` 時才顯示。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| `activities_cycles` 的建立、更新與刪除 | 管理後台 / 活動設定服務 | clientflowservice 僅讀取週期資訊，不參與管理。 |
| `activities_winneraccounts` 的排行榜計算與寫入 | 結算服務（Settlement Service） | 勝率、排名、盈利點數等統計由後台定時任務計算，本服務僅提供查詢。 |
| `betpool_games` 的設定（遊戲建立、選項、開獎、派彩） | 遊戲管理服務 / 派彩服務 | 本服務僅讀取遊戲狀態，不負責遊戲生命週期管理。 |
| 用戶 Z幣餘額的扣減與加值 | Wallet Service | 投注時的幣種操作應交由錢包服務處理，本服務只記錄投注明細與最終 profit zcoin 數值。 |
| 活動排行榜最終歸檔與清理 | 歸檔服務（Archive Service） | 活動結束後長期保存由歸檔服務負責，本服務不負責將歷史數據轉移。 |
| 投注驗證與防重 | 訂單服務（Order Service） | clientflowservice 不檢查重複投注或頻率限制，此類邏輯應由上層服務實現。 |

### 常見錯誤

- ❌ 直接回傳 `activities_record.winbets` 給前端，暴露用戶獲勝注單。  
  ✅ 此欄位僅供內部結算使用，對外 API 應省略或回傳注單數量而非明細。
- ❌ 排行榜查詢未帶 `cid` 或 `activityevent`，導致回傳混合多個活動或週期的資料。  
  ✅ 務必傳入活動週期相關過濾條件，確保資料正確性與效能。
- ❌ 投注查詢未檢查 `account` 是否為當前登入用戶，導致跨帳號資料洩漏。  
  ✅ 所有投注相關查詢的 `account` 條件必須由服務端從會話中取得，不可接受客戶端傳入的任意 account。
- ❌ 在未檢查 `payout` 狀態下，過早向用戶顯示 `betpool_games.winresult`，影響遊戲進行。  
  ✅ 僅在 `payout = true` 時才允許揭露開獎結果。
- ❌ 對 `betpool_games` 進行無 `status` 或 `starttime` 範圍的查詢，載入大量歷史遊戲。  
  ✅ 應至少過濾 `status = 1` 或近期起迄時間，並使用分頁機制。
- ❌ 誤將 `activities_winneraccounts.account` 完整值回傳至前端排行榜。  
  ✅ 需對 account 進行遮蔽處理（如 `user***`），保護用戶隱私。

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Price Center Cassandra (keyspace: pricecenter) | writer / reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- `accounts_*.password`：僅可由註冊或變更密碼 API 寫入，必須經過雜湊處理（不可儲存明文），不允許透過任何 API 直接回傳。
- `accounts_*.phone`：僅可由註冊或用戶資料更新 API 寫入，不可透過批次更新直接修改。
- `accounts_*.enabled`：僅可由帳號啟用/停用排程或管理後台操作，一般 API 不可更新。
- `accounts_*.closetime`：僅由關閉帳號流程（管理後台或登出銷戶 API）設定，寫入後不可再次修改（一旦關閉只能重新註冊）。
- `accounts_*.account`（主鍵）：寫入後不可變更；所有帳號表格共用相同主鍵結構。
- `games_{gameType}`、`leagues_{gtype}`、`teams_{gtype}`：本服務僅讀取，不執行任何寫入操作。資料由賽程資料同步服務負責維護。
- `sitegames_{gameType}.swap`：僅可由「交換主客 API」寫入（設為 1 或 0）。其他欄位（如 `site`, `gid`, `team_a` 等）由同步服務寫入，本服務不得直接修改。
- `sitegames_{gameType}` 其餘欄位：除 `swap` 外，均為唯讀，本服務不可寫入。
- `siteteams_{gameType}`、`siteleagues_{gameType}`：本服務僅讀取，不進行寫入。
- `actionlog`：僅允許透過操作記錄 API 寫入（INSERT），不允許 UPDATE 或 DELETE。`date`、`addtime`、`user`、`gametype` 由系統自動填入，不可手動修改。

### 讀取規則

- 帳號驗證（登入/查詢）：須過濾 `enabled = 1`，且 `closetime` 為空或大於當前時間（未關閉或已解封）。
- 帳號列表查詢（管理用）：僅可依 `account` 或 `username` 精確比對，不可返回全部帳號清單。
- 關聯查詢：僅允許依主鍵 `account` 進行 JOIN，不得以 `phone` 或 `handler` 等非唯一欄位作為關聯條件。
- `games_{gameType}` 查詢：必須包含 `gdate` 過濾（日期範圍），可搭配 `status` 過濾；禁止不帶日期條件的全表掃描。
- `leagues_{gtype}`、`teams_{gtype}` 查詢：主要用於增量同步，需帶 `addtime > ?` 條件，避免全量拉取；或按 `id` 精確查詢。
- `sitegames_{gameType}` 查詢：必須帶 `site` 條件，且至少包含 `gdate` 範圍或 `sitelid`/`sitegid`；查詢交換過的比賽時可加 `swap = 1`。
- `siteteams_{gameType}` 查詢：必須帶 `site` 條件，通常搭配 `sitelid` 過濾；支援依 `sitetid` 精確查詢。
- `siteleagues_{gameType}` 查詢：必須帶 `site` 與 `sitelid` 進行精確匹配，不開放全站點列表。
- `actionlog` 查詢：限管理後台使用，須過濾 `date` 分區鍵，並可依 `user`、`gametype` 等條件查詢，不提供對外 API。

### 不可回傳欄位

- `accounts_*.password`：任何 API 皆不可回傳（包括管理後台），僅內部驗證流程可比對雜湊值。
- `accounts_*.phone`：對外 API（如帳號資訊查詢）應遮蔽部分號碼（如 `+886-***-***-1234`），避免完整電話號碼暴露。
- `accounts_*.handler`：內部擴展資訊不可回傳給客戶端，避免操作員或系統資訊外洩。
- `games_{gameType}.logs`、`datum`、`otherinfo`、`resultinfo`、`match_detail`：包含內部處理資訊或敏感數據，對外 API 不應直接暴露。
- `sitegames_{gameType}.otherinfo`、`resultinfo`、`moneylineodd`、`match_detail`：可能含賠率、結算細節，僅供內部使用，不得直接回傳給未授權前端。
- `actionlog.detail`：可能包含敏感操作詳細資訊，對外不可揭露；僅限管理後台且權限足夠的用戶檢視。

### Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `pricecenter:account:{site}:{account}` | 帳號建立或更新後快取，查詢時讀取 | TTL = 3600 秒（1 小時），存取活躍帳號加速 |
| DEL | `pricecenter:account:{site}:{account}` | 帳號停用、刪除或關閉時清除 | 主動失效，避免舊快取影響驗證結果 |
| GET | `pricecenter:game:{gameType}:{gid}` | 比賽詳情查詢時讀取快取 | TTL = 300 秒（5 分鐘），減輕 Cassandra 讀取壓力 |
| GET | `pricecenter:lgame:{gameType}:{gdate}` | 依日期查詢比賽列表時，先讀快取 | TTL = 600 秒（10 分鐘） |

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 活動週期（cycle）建立與更新 | Admin Service / 管理後台 | `activities_cycles` 表由後台操作，clientflowservice 僅讀取 |
| 遊戲派彩（payout）計算 | Payout Service（或定時任務） | `betpool_games.payout` 與 `profitzcoin` 結算不屬於本服務 |
| 用戶餘額扣減與加值 | Wallet Service | 投注扣款、獎金發放應交由錢包服務處理 |
| 活動排行榜最終歸檔 | Archive Service | 活動結束後長期保存 `activities_winneraccounts` 由歸檔服務負責 |
| 密碼雜湊驗證 | Authentication Service | `accounts_*.password` 的比對邏輯由認證服務實作，clientflowservice 僅傳遞或儲存雜湊值 |
| 帳號註冊與建立 | Registration Service | `accounts_*` 表格的初始建立應由專門的註冊服務處理，clientflowservice 僅後續讀取與部分更新 |
| 賽程資料（`games_{gameType}`, `leagues_{gtype}`, `teams_{gtype}`）的初始寫入與更新 | Data Sync Service | 上游賽程同步服務負責，clientflowservice 僅消費這些資料 |
| `sitegames_{gameType}`、`siteteams_{gameType}`、`siteleagues_{gameType}` 的初始建立與欄位（除 `swap` 外）維護 | 站台設定管理後台或同步服務 | 本服務只讀取或更新 `swap`，其餘欄位由專門服務管理 |
| 操作日誌（`actionlog`）的歸檔與清理 | 定時歸檔服務 | clientflowservice 僅負責寫入操作紀錄 |

### 常見錯誤

- ❌ 直接回傳 `accounts_*.password` 或 `accounts_*.phone` 至前端。  
  ✅ 應永遠不回傳密碼與完整電話號碼；電話如需顯示須遮蔽，密碼僅內部驗證使用。
- ❌ 查詢帳號時未檢查 `enabled = 1` 導致已停用帳號仍可登入或操作。  
  ✅ 所有帳號相關查詢必須加上 `enabled = 1` 條件，且確認 `closetime` 為空或大於當前時間。
- ❌ 在 `games_{gameType}` 查詢中未加 `gdate` 條件，導致全表掃描。  
  ✅ 必須使用 `gdate` 限制日期範圍，搭配 `status` 過濾，避免大量數據擷取。
- ❌ 直接對外回傳 `games_{gameType}.logs` 或 `sitegames_{gameType}.otherinfo` 等內部欄位。  
  ✅ 對外 API 應僅回傳必要的比賽摘要，內部細節欄位禁止暴露。
- ❌ 在 `sitegames_{gameType}` 查詢時未帶 `site` 條件，造成跨站台資料混雜。  
  ✅ 所有站台相關查詢必須精確過濾 `site`。
- ❌ 誤將 `sitegames_{gameType}.swap` 以外欄位（如 `gid`、`team_a`）透過 API 更新，導致資料不一致。  
  ✅ 更新交換狀態僅能修改 `swap`，其他欄位一律拒絕寫入。
- ❌ 忘記在 `leagues_{gtype}`、`teams_{gtype}` 查詢時使用 `addtime` 增量條件，造成效能問題。  
  ✅ 應採用 `addtime > ?` 以減少資料量。
- ❌ 在未授權的情境下回傳 `actionlog.detail`，導致敏感資訊外洩。  
  ✅ 僅限內部管理後台，並嚴格控管欄位回傳。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| games (PostgreSQL) | reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |

### 寫入限制

- `games_{gameType}` 所有欄位：本服務**僅讀取**，不得執行 INSERT、UPDATE 或 DELETE。
- 隊伍名稱、比分、狀態等欄位由比賽資料同步服務（Game Sync Service）寫入與維護，clientflowservice 無寫入權限。
- `swap`、賠率或其他計算欄位不存在於本資料庫，clientflowservice 不得妄想寫入這類欄位。

### 讀取規則

- 比賽查詢必須包含 `gdate` 範圍過濾（例如 `WHERE gdate BETWEEN ? AND ?`），可進一步搭配 `status`（如 `'PreGame'`、`'InPlay'`、`'Final'`），禁止無日期條件的全表掃描。
- 依 `lid`（聯賽ID）或 `teamid_h` / `teamid_a` 查詢時，仍須保留 `gdate` 條件，避免結果集失控。
- 若需區分不同來源站點，需同時過濾 `source` 欄位，以免不同站點資料混淆。
- 查詢僅能回傳目前系統認定已完整同步且未標記刪除的記錄；必要時可加上 `create_at > ?` 做增量輪詢。

### 不可回傳欄位

- `resultinfo`、`otherinfo`、`match_detail`、`siteidmaps`、`teams`：這些 JSONB 或結構化欄位可能包含內部賠付細節、爬蟲原始資料或跨站對應關係，對外 API 一律不應回傳。
- `create_at`：內部時戳，無業務展示需求，對外不可洩漏。
- `gtime`：雖為比賽時間，但部分前端可能不需原始 time 值；若 API 設計需回傳，應確認無資訊洩漏風險後再開放。

### 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| `games_{gameType}` 資料的初始寫入、更新與刪除 | Game Sync Service / 爬蟲同步服務 | clientflowservice 僅消費這些比賽資料，不涉及任何寫入或狀態變更 |
| 比賽賠率、讓分等動態資料的提供 | Odds Service 或 Price Center | games 資料庫僅存基礎比賽資訊，不包含即時賠率 |
| 比賽結果的結算與派彩 | Payout Service | clientflowservice 不根據本表直接進行獎金計算，結果應由派彩服務處理 |

### 常見錯誤

- ❌ 對 `games_{gameType}` 執行無 `gdate` 條件的查詢，導致資料庫全表掃描而逾時。  
  ✅ 所有查詢務必搭配 `gdate` 範圍；若情境特殊，應至少帶上 `create_at` 範圍或分頁限制。
- ❌ 將 `match_detail`、`resultinfo` 等內部原始資料直接序列化回傳給前端。  
  ✅ API 應僅回傳比賽摘要欄位（如 `id`, `source`, `lid`, `team_h`, `team_a`, `match_h`, `match_a`, `status`），內部資料僅供後台或內部服務使用。
- ❌ 誤將 `siteidmaps` 中的站點 ID 當作唯一的比賽編號回傳，導致跨站台混淆。  
  ✅ 對外應使用自身系統的 `id` 或業務定義的 composite ID，`siteidmaps` 僅用於後端站點對照。
- ❌ 直接使用未經轉換的 `gtime`（time without time zone）進行前端展示，忽略時區問題。  
  ✅ 應與 `gdate` 合併後，套用系統時區（或 UTC）再輸出，並在文件標示時區資訊。