# 取得球種聯盟盤口快照

## 1. 場景目的

當使用者進入交易遊戲賽事列表頁時，前端呼叫此 API 取得指定球種（game_type）與聯盟（lid）的即時盤口快照，包含賠率（odds）與讓分模式（use_spread），並支援以比賽日期（gdate）或比賽 ID（gid）過濾。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/tradegames/{game_type}/{lid}` | 取得單一球種聯盟盤口快照列表 |
| POST | `/api/tradegames` | 批次查詢多球種盤口快照 |

---

## 3. 流程總覽

1. 接收 GET 請求，取得路徑參數 `game_type`、`lid` 及可選查詢參數 `gdate`、`gid`
2. 驗證 API Key / 內部服務授權（TCZB Globals）
3. 建立 Redis 鍵名模式：`{game_type}:{lid}:*`
4. 從 Redis DB5 讀取所有符合模式的即時盤口快照 hash 資料
5. 若有指定 `gdate`，僅保留 `gdate` 相符的快照
6. 若有指定 `gid`，僅保留 `gid` 相符的快照
7. 回傳符合條件的快照列表，包含 `odds`、`use_spread`、`gdate`、`gid`、`gtype`、`lid`、`source`、`write_time`、`first_data` 等欄位

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | TradeGamesController.GetTradeGamesList | 接收 GET 請求，解析 `game_type`、`lid`、`gdate`、`gid` |
| 2 | Validator | GameTypeValidator | 驗證 `game_type` 為有效球種代碼（如 SC、BK）且非空字串 |
| 3 | Service | TradeGameService.GetSnapshots | 建立 Redis key pattern，呼叫 RedisHelper 查詢 |
| 4 | Provider | RedisHelper.HScan / HGetAll | 從 Redis DB5 讀取所有符合模式的 hash 快照 |
| 5 | Service | TradeGameService.FilterByGdate | 若 `gdate` 非空，逐筆比對 hash 中的 `gdate` 欄位 |
| 6 | Service | TradeGameService.FilterByGid | 若 `gid` 非空，逐筆比對 hash 中的 `gid` 欄位 |
| 7 | Transfer | TradeGameSnapshotResponse | 將過濾後的 hash 序列化為 response schema 回傳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | DB5: `{game_type}:{lid}:*` | Read（HScan / HGetAll） | 讀取即時盤口快照（odds、use_spread） |
| Redis | DB5: `{game_type}:{lid}:{gid}` | Read（HGetAll） | 當指定 `gid` 時，可能直接讀取特定比賽快照（需人工確認） |
| DB | 無 | 無 | 此場景不涉及 Cassandra 或 MySQL |

---

## 6. 重要規則

- **權限限制**：需通過 API Key 或內部服務授權驗證（TCZB Globals）
- **欄位限制**：`game_type` 為必填路徑參數，必須非空；`lid` 為必填路徑參數，必須非空
- **不可暴露資料**：Redis 快照中的內部欄位（如 `source`、`write_time`、`first_data`）若無業務需求，不應回傳至前端
- **TTL 規則**：Redis 快照的 TTL 由寫入端（可能為 crawler 或 oddservice）控制，本服務不設定 TTL
- **Status 規則**：無
- **Transaction 規則**：無，本場景為唯讀操作
- **Retry 規則**：若 Redis 連線失敗，應回傳 HTTP 500，不進行自動重試（需人工確認）
- **狀態值限制**：無特定狀態值
- **不可修改欄位**：本場景不涉及寫入操作

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `game_type` 為空字串 | HTTP 422 Validation Error |
| `lid` 為空字串 | HTTP 422 Validation Error |
| Redis 連線失敗或逾時 | HTTP 500 Internal Server Error |
| Redis 中無符合模式的快照 | HTTP 200，回傳空陣列 `[]` |
| 指定 `gdate` 或 `gid` 過濾後無匹配資料 | HTTP 200，回傳空陣列 `[]` |
| API Key 驗證失敗 | HTTP 401 Unauthorized |
| Redis 快照資料無法解析為 JSON | HTTP 500 Internal Server Error（需人工確認） |
| `gid` 格式錯誤（非預期字串） | HTTP 200，回傳空陣列或忽略該過濾條件（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TG-SNAP-01 | API Test | 不帶 `gdate` 與 `gid`，查詢 SC 球種、lid=123 | 回傳所有符合模式的快照 |
| TG-SNAP-02 | Flow Test | 指定 `gdate=2026-05-20` 過濾 | 僅回傳 `gdate` 為 2026-05-20 的快照 |
| TG-SNAP-03 | Flow Test | 指定 `gid=match-456` 過濾 | 僅回傳 `gid` 為 match-456 的快照 |
| TG-SNAP-04 | API Test | 提供無效 `game_type`（如 XYZ） | Redis 中無此模式，回傳空陣列 |
| TG-SNAP-05 | Permission Test | 不帶 API Key 呼叫 | HTTP 401 |
| TG-SNAP-06 | Integration Test | Redis DB5 無任何快照時呼叫 | HTTP 200，空陣列 |
| TG-SNAP-07 | Flow Test | 指定 `gdate` 與 `gid` 同時過濾 | 僅回傳同時滿足兩條件的快照 |

---

## 9. 高風險區域

- **高風險 table**：無（本場景不涉及 DB）
- **高風險 API**：若 Redis 鍵名格式變更，但此 API 未同步更新，會導致查無資料
- **跨服務資料同步**：盤口快照由外部服務（如 crawleragent）寫入 Redis，本服務僅讀取。若寫入端未更新，本 API 會回傳過時資料
- **Transaction**：無
- **Cache consistency**：本場景不維護快取一致性，每次 request 皆直接讀取 Redis DB5
- **Queue retry**：無
- **Idempotency**：本 GET API 為冪等操作

---

## 10. 常見錯誤

- ❌ **新人容易犯錯**：誤以為 `gdate` 或 `gid` 是必填參數，導致過濾掉所有資料而回傳空陣列
- ❌ **AI 容易誤解**：誤以為此 API 會查詢 Cassandra `stock_holdings` 表（此為交易查詢，非盤口查詢）
- ❌ **常見漏檢查項目**：未驗證 `game_type` 是否為有效球種代碼，直接傳入 Redis key pattern
- ❌ **常見錯誤流程**：在 Redis 無資料時回傳 404 Not Found（正確應回傳空陣列 200 OK）
- ❌ **Redis 鍵名假設錯誤**：前端或 QA 直接假設 Redis 鍵名為固定格式，未注意到不同球種可能有不同 prefix

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI: `GET /api/tradegames/{game_type}/{lid}` |
| API | OpenAPI: `POST /api/tradegames` |
| Cache | README: Redis DB5 儲存即時盤口快照（odds、use_spread） |
| Code | Controller: `trade_games.py`（TradeGamesController） |
| Service | README: 常見使用場景 3「前端載入賽事盤口」 |
| Schema | OpenAPI: `TradeGameSnapshotResponse`（use_spread, odds, gdate, gid, gtype, lid, source, write_time, first_data） |
| Auth | README: 驗證機制為 API Key / 內部服務授權（TCZB Globals） |