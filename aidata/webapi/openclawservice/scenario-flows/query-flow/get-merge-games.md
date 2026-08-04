# 查詢合併賽事

## 1. 場景目的
提供龍蝦前端依日期與時間區間，查詢各球種（SC、BK、BS、FL、HL、ES、TN 等）的正式比賽，並自動補充聯盟名稱與隊伍詳細資訊（含多語系名稱），供前端展示或合併比對使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | /api/merge/games | 查詢指定日期區間、時間區間及球種的正式比賽，回傳附帶聯盟與隊伍名稱的比賽清單。 |

---

## 3. 流程總覽

1. 接收 query params：`date`（格式 yyyy-MM-dd）、`start_time`、`end_time`（HHmm）、`game_type`（可選，支援多值）、`lang`（可選）。
2. 驗證參數合法性（日期、時間格式、球種是否存在）。
3. 根據 `game_type`（若無則查詢所有啟用的球種列表）決定目標 Cassandra 表，如 `games_SC`、`games_BK`。
4. 查詢對應 `games_{type}` 表，條件：`gdate = date` 且 `gtime >= start_time AND gtime <= end_time`（需人工確認：Cassandra partition key 為 gdate，cluster key 為 gtime/id，以利範圍查詢）。
5. 蒐集所有比賽的 `lid`、`teamid_h`、`teamid_a`，批次查詢對應球種的 `leagues_{type}` 與 `teams_{type}` 表，取得 `lname`、`tname`、`name_map` 等欄位。
6. 將聯盟名稱與隊伍名稱（依據 `lang` 或由 `name_map` 預設）組裝進每筆比賽資料。
7. 若查詢多種球種，合併各球結果集，依日期時間排序後回傳。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | MergeGamesController.get_games | 接收請求、參數驗證、呼叫 Service |
| 2 | Service | MergeGamesService.query_merged_games | 根據球種分派查詢、組合 results |
| 3 | Provider | GamesProvider.query_games(game_type, date, start, end) | 組裝 CQL：`SELECT * FROM games_{type} WHERE gdate = ? AND gtime >= ? AND gtime <= ?`（需人工確認 partition/cluster key 設計） |
| 4 | Provider | TeamsProvider.batch_get_teams(type, team_ids) | 批次查詢 `teams_{type}`，key 為 `id`，取得 tname, name_map |
| 5 | Provider | LeaguesProvider.batch_get_leagues(type, league_ids) | 批次查詢 `leagues_{type}`，取得 lname, name_map |
| 6 | Service | MergeGamesService.enrich_game_data | 將名稱與多語系資訊填回清單 |
| 7 | Controller | MergeGamesController.get_games | 返回 JSON response |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | pricecenter.games_{game_type} | Read (SELECT) | 取得正式比賽基本資料（id, lid, teamid_h, teamid_a, gdate, gtime） |
| DB | pricecenter.leagues_{game_type} | Read (SELECT) | 根據 lid 取得聯盟名稱與多語系對照 |
| DB | pricecenter.teams_{game_type} | Read (SELECT) | 根據 teamid_h / teamid_a 取得隊伍名稱與多語系對照 |
| Cache | Redis | **未使用** | 本場景未使用 Redis 快取（證據：openclawservice-detail.md 指出「無使用 Redis」，且 games 查詢未見快取邏輯） |
| Queue | Kafka | **未使用** | 本場景未產生業務事件 |

---

## 6. 重要規則

- **權限限制**：對外 API 不需身份驗證（龍蝦前端可直接呼叫），但可能限制內部網路存取（需人工確認）。
- **欄位限制**：回傳資料不可包含內部管理欄位（如 `name_map` 可能被過濾，僅回傳指定語言的名稱），不可洩漏站台映射用 `sitegames` 資料。
- **不可暴露資料**：`name_map` 中若包含未授權語言應過濾。
- **日期時間格式**：`gdate` 為 yyyy-MM-dd；`gtime` 為 HHmm 四位數字（如 1930）。
- **球種支援**：僅查詢有對應 `games_{type}` 表的球種，否則回傳錯誤。
- **Cassandra 連線**：使用預先建立的 session，若查詢失敗會重試（底層 cassandra-driver 機制）。
- **查詢效能**：嚴禁全表掃描，`gdate` 必須為 partition key 的一部分，否則為高風險操作（需人工確認 schema 設計）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 缺少必填參數（如 date） | HTTP 400 Bad Request，提示缺少參數 |
| date 格式錯誤（非 yyyy-MM-dd） | HTTP 400，參數格式錯誤 |
| start_time 或 end_time 格式錯誤 | HTTP 400 |
| start_time > end_time | HTTP 400，時間區間無效 |
| game_type 傳入不支援的球種 | HTTP 400，球種未定義 |
| Cassandra 查詢失敗（連線中斷、timeout） | HTTP 500 Internal Server Error，並記錄錯誤日誌（透過 Kafka 發送） |
| 指定日期區間無比賽 | HTTP 200，回傳空陣列 |
| 查詢時 teams/leagues 資料缺失（lid 或 teamid 查不到） | 比賽仍回傳，但名稱顯示為空或原始 ID（降級處理） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| FT-001 | Flow Test | 正常查詢：date=2025-06-01，start_time=0800，end_time=2359，game_type=SC | 回傳 SC 正式比賽，附帶聯盟名與隊伍名，數量符合 DB |
| FT-002 | Flow Test | 多球種合併查詢：game_type=SC,BK | 回傳兩種球類比賽合併，依時間排序 |
| FT-003 | API Test | 缺少 date 參數 | 400 錯誤 |
| FT-004 | API Test | 無效 game_type=XYZ | 400 錯誤 |
| FT-005 | Integration Test | Cassandra 異常時 | 500 錯誤，後端記錄錯誤 log |
| FT-006 | Permission Test | 外部匿名呼叫 | 正常回傳（無權限壁壘） |
| FT-007 | Data Test | 存在比賽但 leagues 中無對應 lid | 比賽仍回傳，lname 為空；不 crash |

---

## 9. 高風險區域

- **高風險 table**：`games_{type}` — 若 partition key 設計不當，範圍查詢可能觸發全表掃描，造成 Cassandra 節點壓力。需確認 `(gdate)` 為 partition key，`gtime` 及 `id` 為 clustering key。
- **高風險 API**：`GET /api/merge/games` — 無快取、無認證的讀取端點，若被濫用可能拖垮 DB。
- **跨服務資料同步**：正式比賽資料由爬蟲或其他服務寫入，openclawservice 僅讀取；資料延遲可能導致前端顯示不及時，但本場景無同步責任。
- **Transaction**：無事務需求（純讀取）。
- **Cache consistency**：目前無快取，無一致性風險。
- **Queue retry**：未使用。
- **Idempotency**：讀取操作冪等。

---

## 10. 常見錯誤

- ❌ **查詢時未限制 `gdate` 導致全表掃描** → ✅ 必須以日期為 partition 查詢。
- ❌ **回傳未補充聯盟/隊伍名稱** → ✅ 必須在組裝時批次查閱 leagues/teams 表。
- ❌ **多語系處理不當** → ✅ 若前端傳 `lang`，應從 `name_map` 提取對應值，若無則回退至 `lname`/`tname`。
- ❌ **誤用 sitegames 表提供前端** → ✅ 本 API 應回傳正式比賽（games），非站台原始資料；sitegames 由 `/merge/sitegames` API 負責。
- ❌ **忘記處理 teams/leagues 查詢缺失導致的 NPE** → ✅ teams/leagues 查詢結果應以 dict 儲存，訪問時使用 `.get(id, {})` 安全取值。
- ❌ **球種列表寫死於程式碼** → ✅ 應透過配置或自動偵測 Cassandra tables 中有哪些 `games_*` 表，以利未來新增（需人工確認實作方式）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `GET /api/merge/games`，README 列出 |
| DB Tables | pricecenter.games_SC, games_BK, teams_SC, teams_BK, leagues_SC, leagues_BK, leagues_TN, leagues_ES 等 (phase1 semantics) |
| Provider | project/Provider/games.py（推測包含 GamesProvider） |
| Service | project/Service/merge_games.py（需人工確認是否存在此模組，或合於 controller） |
| SQL | SELECT id, lid, teamid_h, teamid_a, gdate, gtime FROM games_{type} WHERE gdate = ? AND gtime >= ? AND gtime <= ? (依據欄位推導) |
| Cache / Queue | 無 Redis key；Kafka 僅用於日誌傳送（heartbeat 等），非業務流程。 |

---

（文件結束）