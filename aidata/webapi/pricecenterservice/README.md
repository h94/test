# PriceCenterService WebAPI

- **Git Repository**：[https://git.zbdigital.net/biz/pricecenterservice.git](https://git.zbdigital.net/biz/pricecenterservice.git)
- **別名**：appsettings 中路由前綴為 `pricecenter`

## 職責
負責整合多個外部運動博弈站台的賽事資料（賠率、比分、狀態），作為平台的**價格中心核心服務**。從數十個博弈來源（如 bet365、pinnacle、ku888 等）擷取並合併賽事資訊，提供統一的賽事查詢、即時比分、盤口管理，以及聯賽/球隊名稱對照表維護。

## 技術棧
- 框架：ASP.NET Core (.NET 8.0)、MVC（內部工具頁面使用 Controllers with Views）
- 資料庫：
  - Redis：DB5（賽事即時資料）、DB6（站台賽事）、DB7（聯賽對照）— 本服務讀寫（如比分狀態更新、熱門賽事標記、聯賽對照表）
  - PostgreSQL `Games`：賽事歷史資料（`games_{gameType}` 表）及 AI 合併相關表（`aimerge_*`）— 本服務對 `games_{gameType}` **僅讀取**；對部分 `aimerge_*` 表（`aimerge_label_overrides`, `aimerge_source_mapping`, `aimerge_runtime_config`）有條件寫入權限
  - Cassandra `pricecenter`：業務主資料（聯賽、隊伍、賽事）、操作日誌（`actionlog`）、驗證帳號（`accounts_{brand}`）等；本服務可讀寫 (owner)
  - MySQL `Sport`：錢包（`GameUsers_Wallet` 等）、聊天記錄（`ChatRoomHistories_Backup`）、通知訊息（`Notification_Messages`）、社群群組（`Community_Groups`）、選手資料（`BK_SitePlayers`）— 本服務僅讀取，**不可寫入**
- 驗證：ECFramework.ECService（內部統一驗證框架）
- 配置中心：Zookeeper
- 日誌：Kafka + Cassandra
- 其他套件：ECCore 3.0.2、GameDataModels 2.0.198、Microsoft.AspNetCore.SignalR

## 資料庫重要 Table

| 儲存層 | Table / 結構 | 用途 |
|--------|------------|------|
| Redis DB5 | `{gameType}:{lid}:{gDate}` | 賽事即時資料（Hash 結構，含賠率、比分、狀態），本服務讀寫 |
| Redis DB6 | `siteGame:{site}:{gameType}` | 各站台原始賽事資料（JSON 陣列），本服務讀取 |
| Redis DB7 | `leagueMap:{gameType}` | 聯賽名稱對照表，本服務讀寫 |
| PostgreSQL Games | `games_{gameType}`（e.g., `games_bk`, `games_bs`） | 賽事歷史資料（結果、比分），**本服務僅讀取**；查詢必須指定 `gdate` 範圍與 `lid` |
| PostgreSQL Games | `aimerge_label_overrides` | AI 合併人工審核覆蓋，本服務有條件寫入（`override_label`, `excluded_from_training`, `reason`, `reviewed_by`, `reviewed_at`） |
| PostgreSQL Games | `aimerge_source_mapping` | AI 合併來源映射，本服務有條件寫入（`confirmed_at`, `confirmed_by`） |
| PostgreSQL Games | `aimerge_runtime_config` | AI 合併執行期配置，本服務有條件寫入（`params`, `is_active` 等） |
| PostgreSQL Games | `aimerge_match_predictions`, `aimerge_daily_reports`, `aimerge_backtest_runs`, `aimerge_historical_runs`, `aimerge_team_aliases` | AI 合併相關，**本服務僅讀取** |
| Cassandra pricecenter | `actionlog` | 操作日誌（`date` 為分區鍵） |
| Cassandra pricecenter | `accounts_{brand}` | 帳號驗證與管理（本服務可讀寫）；密碼欄位嚴禁對外回傳 |
| MySQL Sport | `GameUsers_Wallet` | 錢包餘額（僅讀，不可寫）；`AuthKey` 為內部金鑰，嚴禁對外暴露 |
| MySQL Sport | `GameUsers_Wallet_Transactions` | 錢包交易記錄（僅讀） |
| MySQL Sport | `BK_SitePlayers` | 選手資料（僅讀，查詢須以 `Site`+`SiteID`+`Year` 複合鍵）；`SiteID` 不可對外回傳 |
| MySQL Sport | `Notification_Messages` | 站內通知訊息（僅讀；查詢需過濾 `Enabled = 1`） |
| MySQL Sport | `Notification_Topics` | 通知主題（僅讀；查詢需過濾 `Enabled = 1`） |
| MySQL Sport | `Community_Groups` | 社群群組（僅讀；查詢需過濾 `Enabled = 1`；`Owner` 欄位不可對外回傳） |
| MySQL Sport | `ChatRoomHistories_Backup` | 聊天歷史記錄（僅讀；查詢須依 `GID` 過濾；`Account` 不可對外暴露） |

> **需人工確認**：
> - `Sport` 資料庫中的 `Team` 與 `League` 表結構（用於驗證聯賽/球隊是否存在於建立球隊流程中）在現有資料庫綱要中未直接列出，需人工核對程式碼中的具體實作。
> - `pricecenter` Keyspace 下的 `games` 表完整 Schema 與欄位定義（本服務可讀寫），需人工確認。

## 對外 API 重點

### 賽事查詢
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/v1/games/{gameType}` | 查詢指定日期賽事（query: `dateTime` 必填） | ✅ |
| GET | `/api/v1/games/{gameType}/{gid}` | 依 GID 查詢賽事（可選 `isGetSite` 取得站台對應、`gdate` 篩選日期） | ✅ |
| GET | `/api/v1/games/{gameType}/{lid}/{gDate}` | 查詢聯賽日期賽事 | ✅ |
| GET | `/api/v1/games/{gameType}/{lid}/{gDate}/{id}` | 取得指定聯盟、日期、賽事 id 的單場賽事 | ✅ |
| POST | `/api/v1/games/live` | 根據 Game 列表批次取得即時賽事（body 含 lid、gdate、id） | ✅ |
| GET | `/api/v1/games/live/{gameType}` | 查詢今日直播賽事（從 Redis DB5） | ✅ |
| GET | `/api/v1/games/live/{gameType}/{lid}/{gdate}/{id}` | 查詢單一直播賽事 | ✅ |
| GET | `/api/v1/games/inplay/{gameType}` | 查詢進行中賽事 | ✅ |
| GET | `/api/v1/games/final/{gameType}` | 查詢已結束賽事 | ✅ |
| GET | `/api/v1/games/combineinfo/{gameType}/{dateTime}` | 查詢賽事合併對照（可選 `onlyPregame`，預設 true） | ✅ |
| PUT | `/api/v1/games/{gameType}/score-status` | 更新賽事比分與狀態（body 含 LID、GDate、ID、Match_A、Match_H、Status 等） | ✅ |
| PUT | `/api/v1/games/{gameType}/{lid}/{gDate}/{id}/time-score-status` | 更新賽事時間/比分/狀態（body 含 GTime、Match_A、Match_H、Status） | ✅ |
| PUT | `/api/v1/games/{gameType}/{lid}/{gDate}/{id}/resultinfos` | 更新賽事結果資訊（body 含 OtherInfo 等延伸欄位） | ✅ |
| PUT | `/api/v1/games/{gameType}/setfinal` | 設定賽事為最終結果（觸發結算通知） | ✅ |
| DELETE | `/api/v1/games/{gameType}/{lid}/{gDate}/{id}` | 刪除賽事 | ✅ |

### 熱門進行中賽事
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/games/inplay/hot/{gameType}/{lid}/{gDate}/{gid}` | 設定熱門進行中賽事（寫入 Redis 熱門標記） | ✅ |
| GET | `/api/v1/games/inplay/hot` | 查詢熱門進行中賽事（從 Redis DB5 讀取） | ✅ |

### 站台賽事
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/v1/sitegames/{gameType}` | 依日期時間區間查詢站台賽事（query: `startDate`、`endDate` 必填，可選 `startTime`、`endTime`） | ✅ |
| GET | `/api/v1/sitegames/{gameType}/{startGameDate}` | 查詢站台賽事（可選 `site`、`status`、賠率相關參數） | ✅ |
| GET | `/api/v1/sitegames/{gameType}/{site}/{startGameDate}` | 查詢指定站台賽事（300 秒快取） | ✅ |
| GET | `/api/v1/siteleagues/{gameType}` | 查詢站台聯賽列表（可選 `sites` 篩選） | ✅ |
| GET | `/api/v1/siteleagues/map/{gameType}/{lid}` | 查詢聯賽語言對照 | ✅ |
| GET | `/api/v1/siteleagues/merged/{gameType}` | 查詢已合併站台聯賽 | ✅ |

### 聯賽與球隊管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/leagues/{gameType}/{lid}/teams` | 建立球隊（從站台隊伍對應，body: `SiteTeam`） | ✅ |
| GET | `/api/v1/teams/{gameType}` | 查詢球隊列表（可篩選聯賽、隊伍 ID，可選 `needOther`、`isGetSite`） | ✅ |
| PUT | `/api/v1/leagues/{gameType}/{id}/namemaps` | 更新聯賽名稱對照（body: `List<NameMapInput>`） | ✅ |
| PUT | `/api/v1/leagues/{gameType}/{id}/abbrmaps` | 更新聯賽縮寫對照（body: `League`，含 Abbr_Map） | ✅ |
| PUT | `/api/v1/teams/{gameType}/{id}/abbrmaps` | 更新球隊縮寫對照（body: `Team`，含 Abbr_Map） | ✅ |
| PUT | `/api/v1/split/teams/{gameType}` | 手動拆分（解除合併）站台隊伍（body: `SplitTeam`） | ✅ |
| DELETE | `/api/v1/leagues/{gameType}/{lid}/teams` | 刪除沒有主站台的聯盟下所有隊伍（手動維運用） | ✅ |

### OpenClaw 合併管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/v1/openclawmerge/{gtype}` | 查詢待合併賽事列表（依時間區間，query: `startQueryTime`、`endQueryTime` 必填同日；可選 `lid`） | ✅ |
| GET | `/api/v1/openclawmerge/row/{gtype}/{gdate}/{lid}/{id}` | 查詢單筆合併賽事，含 Game、SiteGames 及名稱對照 | ✅ |

### 日誌查詢
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/log/game` | 寫入一筆 GameTools 操作紀錄（body: `GameToolsLog`） | ✅ |
| GET | `/api/v1/log/action/{date}` | 查詢操作統計（各使用者／操作類型計數） | ✅ |
| GET | `/api/v1/log/game/{date}` | 查詢工具日誌（可選 `gameType`） | ✅ |
| GET | `/api/v1/log/datum/{gDate}/{gameType}` | 查詢資料來源日誌（可選 `league`, `gid`） | ✅ |
| GET | `/api/v1/inplayspreadlogs/{gDate}/{gameType}/{gid}` | 查詢盤口擴展日誌 | ✅ |
| GET | `/api/v1/log/odd` | 查詢賠率異動紀錄（OddLog；query: `gameType`, `site`, `sitelid`, `sitegid`, `mode`, `dateTime` 必填） | ✅ |
| GET | `/api/v1/log/oddv2` | 查詢賠率異動紀錄 V2（DeveloperLog；query: `gameType`, `site`, `sitelid`, `sitegid`, `mode` 必填；`startDate`, `endDate` 選填，缺省預設賽事日期；`startHour`/`endHour` 選填，預設 0/23；`startMinute`/`endMinute` 選填，預設 0/59；Loki 查詢時間為 startDate+startHour:startMinute:00 至 endDate+endHour:endMinute:59） | ✅ |

### 系統工具
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/system/autocreatetable` | 自動建立 DB Table（維運用） | ✅ |
| DELETE | `/api/v1/system/clear/sites/{site}` | 清除站台資料（含合併、賠率、站台資訊） | ✅ |
| GET | `/api/heart` | Health Check | ❌ |
| GET | `/api/version` | 查詢版本號 | ❌ |

## 服務相依

| 相依服務 | 用途 |
|---------|------|
| 外部博弈站台（70+ 個來源） | 擷取賽事賠率與比分資料（bet365、pinnacle、ku888 等） |
| `predictservice` | 結算時本服務通知其進行競猜結算 |
| `pricecentermanage` | 管理後台推播通知、App 裝置設定 |
| `gameliveservice` | 主要負責 Redis DB5 即時賽事資料及 PostgreSQL `games_{gameType}` 表的寫入與維護；本服務亦參與部分 Redis 更新 |
| `mergesite`、`sitegameoddservice` 等合併/站台服務群 | 站台賽事合併、賠率處理等（需人工確認：本服務與其互動細節） |
| 翻譯服務（內部實作 `ITranslateService`） | 翻譯聯賽與隊伍名稱 |
| 賠率服務（內部實作 `IOddService`） | 查詢與管理賠率資料 |
| 自動合併服務（內部實作 `IAutoCombineService`） | 自動合併聯賽、隊伍、賽事（後台排程用） |

## 常見使用場景

1. **前台查詢今日賽事**
   - 觸發：使用者開啟競猜首頁
   - 流程：GET `/api/v1/games/live/{gameType}` → 從 Redis DB5 讀取即時賽事資料回傳

2. **後台更新賽事比分**
   - 觸發：比分機器人或管理員手動更新
   - 流程：PUT `/api/v1/games/{gameType}/score-status` → 更新 Redis DB5 與 Cassandra `pricecenter.games`（歷史記錄）→ SignalR 推播前台

3. **賽事結算流程**
   - 觸發：賽事進入 Final 狀態
   - 流程：PUT `/api/v1/games/{gameType}/setfinal` → 通知 `predictservice` 進行競猜結算

4. **聯賽名稱對照維護**
   - 觸發：新聯賽上線或名稱異動
   - 流程：PUT `/api/v1/leagues/{gameType}/{id}/namemaps` → 更新 Redis DB7 對照表

5. **設定熱門進行中賽事**
   - 觸發：後台管理員選定熱門賽事
   - 流程：POST `/api/v1/games/inplay/hot/{gameType}/{lid}/{gDate}/{gid}` → 寫入 Redis 熱門賽事標記

## AI 判斷關鍵字

賽事, 價格中心, 賠率, 比分, 聯賽, 球隊, 直播, 即時, inplay, 站台, 合併, 對照表, 盤口, GameType, 足球, 籃球, 棒球, bet365, pinnacle, 熱門賽事, 結算, 隊伍合併, 聯賽對照

---

## 資料庫操作重要邊界與規則 (更新)

### PostgreSQL `Games`
- **本服務角色**：對 `games_{gameType}` 表為 Reader（唯讀）。嚴禁任何 `INSERT / UPDATE / DELETE` 操作。對部分 `aimerge_*` 表有條件寫入權限，詳見下方說明。
- **讀取規則**：
    - 查詢 `games_{gameType}` 表時，必須指定 `gdate`（日期）範圍並搭配 `lid`（聯盟 ID），避免全表掃描。
    - 判斷賽事是否結束應以 `status = 'Final'` 為準，不可僅依靠 `match_h` / `match_a` 非空。
- **不可回傳欄位**：`siteidmaps`（內部站台 ID 映射）對外 API 嚴禁回傳；`teams`、`create_at` 等內部或無業務意義欄位不建議直接暴露。
- **寫入限制（`aimerge_*` 表）**：
    - `aimerge_label_overrides`: 僅可寫入 `override_label`, `excluded_from_training`, `reason`, `reviewed_by`, `reviewed_at`。嚴禁修改 `game_type`, `gdate`, `prediction_id` 等關聯欄位。
    - `aimerge_source_mapping`: 可寫入 `confirmed_at` 與 `confirmed_by`。映射關係不可人工直接修改。
    - `aimerge_runtime_config`: 限授權管理員透過專用 API 新增或更新。修改時必須記錄 `updated_by`, `updated_at`, `change_reason`。不可直接刪除，停用應設 `is_active = false`。
    - 其他 `aimerge_*` 表（如 `aimerge_match_predictions`, `aimerge_daily_reports`, `aimerge_backtest_runs`, `aimerge_historical_runs`, `aimerge_team_aliases`）**唯讀**。

### Cassandra `pricecenter`
- **本服務角色**：Owner / Writer / Reader。
- **帳號驗證規則**：登入/驗證時必須同時檢查 `enabled = 1` 且 `closetime` 為空。
- **不可回傳欄位**：`password`（含雜湊值）嚴禁在任何對外 GET API 回傳；`phone`、`closetime`、`handler` 僅特定管理端 API 可有限度回傳。

### MySQL `Sport`
- **本服務角色**：Reader（唯讀）。除特定由 `pricecentermanage` 等負責的表外，**嚴禁任何寫入**。特別注意 `GameUsers_Wallet` 的餘額 (`Balance`) 與 `AuthKey` 是絕對禁止直接修改或暴露的。
- **讀取規則**：社群群組 (`Community_Groups`)、通知 (`Notification_*`) 查詢必須過濾 `Enabled = 1`。聊天記錄 (`ChatRoomHistories_Backup`) 查詢必須綁定 `GID` 且不可暴露 `Account`。

### Redis
- **本服務角色**：對 DB5、DB6、DB7 進行唯讀或寫入操作，但 Redis 中的主要資料由其他服務（如 `gameliveservice`、爬蟲等）負責寫入，本服務參與部分即時狀態更新（如比分、熱門標記）。

### 本服務不負責
| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 帳號註冊 | accountsService | 新帳號建立由 accountsService 負責，pricecenter 僅查驗與啟用停用 |
| 帳號刪除 / 軟刪除 | usercenter | 帳號邏輯刪除由 usercenter 處理，pricecenter 僅讀取啟用狀態 |
| 密碼修改 | memberSecurityService | 密碼變更流程由 memberSecurityService 負責，pricecenter 僅儲存密文 |
| 錢包交易處理 | walletService | 錢包出入金、交易紀錄寫入由 walletService 負責，pricecenter 僅讀取錢包資料用於報表或會員中心 |
| 站內信發送 | notificationService | 站內信的派送與收件管理由 notificationService 處理，pricecenter 僅提供查詢介面 |
| 聊天訊息發送 | chatService | 聊天室訊息的新增與編輯由 chatService 處理，pricecenter 僅讀取歷史記錄 |
| 社群群組管理 | communityService | 群組的建立、啟用、成員管理等由 communityService 負責，pricecenter 僅讀取群組列表與資訊 |
| 運動數據同步 | （外部資料源） | 球員、聯盟等基礎資料由外部資料源匯入，pricecenter 僅負責映射與查詢 |
| 賽事資料寫入（聯賽、比賽、隊伍） | 後台管理/數據同步 | leagues、games、teams 等表的建立與更新由專門的後台或數據同步服務處理，pricecenter 僅讀取 |
| 自動隊伍映射處理 | automapService | automapteams / automaperrs 表的寫入與映射邏輯由特定映射服務負責 |
| Games DB 賽事數據維護 | collector（數據同步） | games_bk/games_bm/games_bs/games_ck 等表的數據落地與更新由 collector 處理，pricecenterservice 僅讀取 |
| AI 合併預測與排程 | AI 合併排程服務 | `aimerge_match_predictions`、`aimerge_daily_reports`、`aimerge_backtest_runs`、`aimerge_historical_runs`、`aimerge_team_aliases` 等表由專屬排程服務維護，pricecenterservice 僅讀取（或對特定表進行有限度審核寫入） |