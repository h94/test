# 查詢賽事

## 1. 場景目的
根據遊戲類型、日期、聯賽、GID 等組合條件，從 **Redis DB5** 或 **Cassandra** 讀取賽事即時或歷史資料。支援多種前端查詢場景（全部賽事、聯賽賽事、直播賽事、進行中賽事、已結束賽事），並提供合併對照資訊。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/games/{gameType}` | 根據球種、日期取得當日全部賽事 |
| GET | `/api/v1/games/{gameType}/{gid}` | 依 GID 查詢單筆賽事（支援 `isGetSite=true` 取得原始站台資料） |
| GET | `/api/v1/games/{gameType}/{lid}/{gDate}` | 查詢指定聯賽、日期的全部賽事 |
| GET | `/api/v1/games/{gameType}/{lid}/{gDate}/{id}` | 查詢單一特定場次賽事 |
| GET | `/api/v1/games/live/{gameType}` | 查詢該球種今日直播賽事 |
| GET | `/api/v1/games/inplay/{gameType}` | 查詢進行中（inplay）賽事 |
| GET | `/api/v1/games/final/{gameType}` | 查詢已結束（final）賽事 |
| GET | `/api/v1/games/combineinfo/{gameType}/{dateTime}` | 查詢賽事合併對照資訊 |

所有查詢類 API 皆需通過 **ECFramework 驗證**。

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，內含 `gameType`、`dateTime`、`lid`、`gid` 等參數。
2. **GameController** 接收參數後，呼叫對應的 **GameService** 方法（如 `GetGames`、`GetTodayLiveGames`、`GetInplayGames` 等）。
3. Service 層根據請求路徑及參數，決定從 **Redis DB5** 或 **Cassandra** 讀取。
   - **一般賽事查詢**：優先以 `{gameType}:{lid}:{gDate}` 作為 Key 前綴，從 Redis DB5 讀取即時賽事快取。
   - **歷史或最終狀態查詢**：當 Redis 中無資料或賽事狀態已進入 `Final` 時，需回退至 **Cassandra `pricecenter.games`** 讀取完整賽事記錄。
   - **站台資料** (`isGetSite=true`)：額外從 **Redis DB6** (`siteGame:{site}:{gameType}`) 讀取原始站台賽事。
4. 讀取到的資料由 **GameDTO / Game** 模型承載，經過必要欄位過濾後序列化回傳。
5. 若 Redis 或 Cassandra 發生查詢異常，拋出標準化錯誤回應。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|:---:|-------|----------------|------|
| 1 | Controller | `GameController.GetGames(gameType, dateTime)` | 綁定路由參數，呼叫 Service |
| 2 | Service | `GameService.GetGames(gameType, gDate)` | 判斷查詢日期，組合 Redis Key 前綴進行批次讀取 |
| 3 | Provider | `RedisProvider/RedisService` | 對 Redis DB5 執行 `HGETALL` 或 `SCAN` 命令，取得賽事集合 |
| 4 | Provider | `CassandraProvider/CassandraService` (備援) | 若 Redis 無資料或需要歷史記錄，對 `pricecenter.games` 執行查詢 |
| 5 | Service | `GameService` (站台查詢) | 若 `isGetSite=true`，額外讀取 Redis DB6 |
| 6 | Service | `GameService` | 將 `Game` 物件轉換為 `GameDTO`，過濾不可回傳欄位 |
| 7 | Controller | `GameController` | 回傳 `ActionResult<IEnumerable<GameDTO>>` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Cache | Redis DB5：`{gameType}:{lid}:{gDate}` | Read | 取得特定聯賽日期的即時賽事（含賠率、比分、狀態） |
| Cache | Redis DB5：`{gameType}:live` (推測) | Read | 取得今日直播賽事列表 |
| Cache | Redis DB6：`siteGame:{site}:{gameType}` | Read | 取得原始站台賽事資料（當 `isGetSite=true`） |
| DB | Cassandra `pricecenter.games` | Read | 查詢歷史賽事、最終比分、結果資訊 |
| Queue | N/A | N/A | 單純查詢流程不涉及 Kafka/Queue 寫入 |

---

## 6. 重要規則

- **權限限制**：所有 `/api/v1/games/*` 需通過 `ECFramework` 驗證；`/api/heart` 及 `/api/version` 為公開端點。
- **資料一致性**：若 Redis 快取的賽事狀態已為 `Final`，回傳資料必須與 Cassandra 中的最終結果一致。
- **欄位不可暴露**：對外 API 回傳的 `GameDTO` 不得包含內部除錯資訊、原始站台金鑰等。
- **狀態值限制**：`inplay`、`live`、`final` 是預定義的查詢情境，Service 層需確保狀態過濾邏輯準確。
- **無 TTL 規則**：DB5 賽事資料的 TTL 由寫入的爬蟲或合併服務控制，查詢方不負責設定。
- **Retry 規則**：Redis 查詢失敗時，無自動 Retry；由客戶端或上層服務重試。Cassandra 查詢若失敗，直接拋出 500 錯誤，需人工確認。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 缺少必填路徑參數（例如 `gameType`） | 回傳 400 Bad Request |
| `gameType` 不在允許範圍 | 回傳 400 Bad Request 或空陣列 `[]` |
| 提供的 `gid` 不存在於系統中 | 回傳 404 Not Found 或空陣列 `[]` |
| `dateTime` 格式錯誤 | 回傳 400 Bad Request |
| Redis DB5 連線失敗或回應超時 | 回傳 503 Service Unavailable 或 500 Internal Server Error |
| Cassandra 查詢逾時 | 回傳 500 Internal Server Error，並記錄錯誤日誌 |
| 驗證 Token 無效或過期 | 回傳 401 Unauthorized |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| QG-01 | API Test | GET `/api/v1/games/BS?dateTime=2026-01-01` | 200 OK，回傳 BS 球種當日賽事陣列 |
| QG-02 | API Test | GET `/api/v1/games/BK/invalid-gid` | 404 或空陣列 |
| QG-03 | Flow Test | 查詢後端 Cassandra `games` 有資料、Redis 過期的賽事 | Service 正確從 Cassandra 讀取並回傳，不中斷 |
| QG-04 | Flow Test | `isGetSite=true` | 回傳的 `GameDTO` 包含原始站台賠率資料 |
| QG-05 | Permission Test | 未帶 Auth Header | 401 Unauthorized |
| QG-06 | API Test | GET `/api/v1/games/live/BS` | 200 OK，僅回傳狀態為直播中的賽事 |
| QG-07 | API Test | 輸入超大 `dateTime` 範圍 | 查詢效能可接受，無 Timeout |

---

## 9. 高風險區域

- **高流量 Redis 讀取**：`GET /games/live/{gameType}` 為前台首頁主要 API，瞬間流量大。需確保 **Redis DB5 連線池** 及 **Key 設計** 能承載。
- **資料一致性**：Redis 與 Cassandra 之間的最終狀態同步。若 `Final` 狀態更新延遲，可能導致前端看到不一致的比分。
- **賽事合併對照**：`combineinfo` 路由涉及多站台間的 GID 對照，邏輯複雜，容易出現對照錯誤導致漏賽或重複賽事。
- **Cassandra 備援查詢**：當 Redis 資料遺失或過期時，對 Cassandra 的查詢負載會瞬時升高，必須確認 Cassandra 的 `games` 表查詢效能。

---

## 10. 常見錯誤

- **新人常犯**：直接查詢 Cassandra 而不先檢查 Redis 快取，導致不必要的延遲與資料庫壓力。
- **AI 誤解**：誤以為所有賽事都存於 Redis；實際上已結束 (`Final`) 的賽事最終應以 Cassandra 資料為準。
- **漏檢查**：忘記驗證 `gameType` 的存在性，導致對 Redis 發送無效 Key 的查詢。
- **錯誤流程**：在 Service 層直接序列化 Redis 的原始 Hash 欄位，而未映射到 `GameDTO` 模型，可能不慎暴露內部欄位。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI `paths./api/v1/games/{gameType}.get` |
| DB | README.md：資料庫重要 Table — Redis DB5、Cassandra pricecenter.games |
| DB | README.md：Redis DB5 結構為 `{gameType}:{lid}:{gDate}` |
| Code | Controller：`GameController` (Phase0 semantics) |
| Code | Service：`GameService` (Phase0 semantics) |
| Permission | README.md：對外 API 重點 — 賽事查詢所有 GET 皆需驗證 ✅ |
| Flow | README.md：常見使用場景 1. 前台查詢今日賽事：從 Redis DB5 讀取即時賽事資料回傳 |