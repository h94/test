# 清除站台資料

## 1. 場景目的

提供一個系統工具端點，讓管理員能**完整清除指定博弈站台的所有相關資料**。此為不可逆的高風險操作，用於站台資料異常或站台下線時的大規模清理，確保所有與該站台相關的賽事、站台賽事索引及聯賽對照快取等資料能被一併移除，避免殘留資料影響系統運算或前台顯示。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| DELETE | `/api/v1/system/clear/sites/{site}` | 清除指定站台的所有相關資料 |

來源：README "系統工具" 章節，路由 `/api/v1/system/clear/sites/{site}`，標記需要驗證。

---

## 3. 流程總覽

1. 接收 DELETE request，由路由參數取得 `site`（站台代碼，例如 `bet365`、`pinnacle`）。
2. 由 ECMiddleware 驗證呼叫者身分與權限（需人工確認授權層級）。
3. Controller 呼叫對應的 Service 執行清除邏輯。
4. Service 掃描 Redis DB6 中符合 `siteGame:{site}:*` 模式的 key，刪除該站台所有站台原始賽事資料。
5. Service 掃描 Redis DB5 中符合 `*:*:*` 的賽事即時資料，移除那些僅屬於該站台的賽事（需人工確認判斷邏輯）。
6. Service 掃描 Redis DB7 中符合 `leagueMap:*` 的聯賽對照表，若該對照僅關聯此站台則一併移除（需人工確認）。
7. 寫入 Cassandra `datum_logs` 表，記錄此次清除操作（需人工確認）。
8. 回傳成功訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Middleware | ECFramework.ECService | 驗證呼叫者 token 與授權範圍 |
| 2 | Controller | SystemController.ClearSites | 接收 `{site}` 參數，傳遞至 Service |
| 3 | Service | ClearSiteService.ClearBySite | 執行站台資料清除邏輯 |
| 4 | Provider | RedisProvider.DeleteByPattern | 掃描並刪除 Redis DB6 中 `siteGame:{site}:*` 的所有 key |
| 5 | Provider | RedisProvider.DeleteGamesBySite | 掃描 Redis DB5 中 `{gameType}:{lid}:{gDate}` 的賽事，若僅屬於該站台則刪除（需人工確認） |
| 6 | Provider | RedisProvider.DeleteLeagueMapsBySite | 掃描 Redis DB7 中 `leagueMap:{gameType}`，若對照僅關聯此站台則刪除（需人工確認） |
| 7 | Provider | CassandraProvider.InsertLog | 寫入 Cassandra `datum_logs` 記錄操作日誌（需人工確認） |
| 8 | Controller | SystemController.ClearSites | 回傳 `200 OK` |

⚠️ 上述 Service / Provider 名稱與呼叫層級為基於專案結構的推測，實際名稱需人工確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Redis | Redis DB6 `siteGame:{site}:{gameType}` | Delete | 刪除該站台的所有原始賽事資料（站台賽事索引） |
| Redis | Redis DB5 `{gameType}:{lid}:{gDate}` | Delete（部分） | 若賽事僅屬於該站台，則移除即時賽事快取 |
| Redis | Redis DB7 `leagueMap:{gameType}` | Update（部分） | 若聯賽對照僅關聯該站台，則移除或更新該對照 |
| Cassandra | `pricecenter.datum_logs` | Insert | 寫入操作日誌以供後續稽核（需人工確認） |

---

## 6. 重要規則

- **權限限制**：此 API 需要驗證，且僅限系統管理員或擁有站台管理權限的角色呼叫。需人工確認授權層級。
- **不可逆操作**：清除後的資料無法復原，除非重新由外部站台擷取。應在前端或呼叫端提供二次確認機制。
- **Redis 掃描效能**：`KEYS` 或 `SCAN` 操作在 Redis 中為 O(N) 複雜度。若 DB5 / DB6 中 key 數量龐大，此操作可能造成 Redis 短暫阻塞，建議在低流量時段執行。
- **不可修改欄位**：此 API 不應影響 Cassandra `accounts_*` 系列表格或 MySQL Sport 中的任何結構性資料。
- **日誌記錄**：操作完成後應寫入 Cassandra `datum_logs`，記錄 `site`、`timestamp`、`operator`，供後續稽核。需人工確認目前實作是否包含此步驟。
- **Cassandra `games` 歷史資料**：此 API 是否應同步刪除 Cassandra `games` 表中屬於該站台的歷史賽事，需人工確認。根據 README，`games` 用於賽事歷史資料，若站台下線，歷史資料可能仍需保留或移轉。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 呼叫者未通過驗證 | 回傳 401 Unauthorized |
| 呼叫者權限不足（非管理員） | 回傳 403 Forbidden |
| `{site}` 參數為空或不存在 | 回傳 400 Bad Request，提示站台代碼無效 |
| Redis DB6 連線失敗 | 回傳 500 Internal Server Error，停止操作 |
| Redis DB5 連線失敗 | 回傳 500 Internal Server Error，停止操作 |
| Cassandra `datum_logs` 寫入失敗 | 需人工確認：是否應 rollback Redis 操作，或僅記錄錯誤並繼續 |
| 操作過程中 Redis 發生部分刪除失敗 | 需人工確認：目前是否支援 rollback 或重試機制 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| SYS-001 | API Test | 以有效管理員 token 呼叫，指定已存在的 `site` | 回傳 200；Redis DB6 中 `siteGame:{site}:*` 全數刪除 |
| SYS-002 | API Test | 以無權限 token 呼叫 | 回傳 403 |
| SYS-003 | API Test | 未帶 token 呼叫 | 回傳 401 |
| SYS-004 | API Test | `site` 參數為不存在的站台 | 回傳 200 或 400（需人工確認目前行為）；Redis 無實際刪除 |
| SYS-005 | Flow Test | 清除站台後，以 GET `/api/v1/sitegames/{gameType}/{site}/{date}` 查詢 | 應回傳空資料 |
| SYS-006 | Flow Test | 清除站台後，檢查 Redis DB5 中是否仍殘留該站台唯一賽事 | 應已移除 |
| SYS-007 | Flow Test | 操作後檢查 Cassandra `datum_logs` | 應存在本次操作日誌（需人工確認） |
| SYS-008 | Performance Test | 在 Redis DB6 key 數量 > 10 萬時執行清除 | 回應時間應在可接受範圍內，Redis 無明顯延遲或崩潰 |

---

## 9. 高風險區域

- **高風險 API**：`DELETE /api/v1/system/clear/sites/{site}` — 大規模刪除 Redis 資料，無回復機制，屬於破壞性操作。
- **高風險 Table / Key**：
  - Redis DB6 `siteGame:{site}:*` — 站台賽事原始索引，刪除後無法恢復。
  - Redis DB5 `{gameType}:{lid}:{gDate}` — 即時賽事快取，若僅因站台清除而刪除，可能影響其他站台合併賽事的資料完整性（需人工確認）。
- **Cache consistency**：若 `price:cache:{brand}:{account}` 中有與站台相關的快取，此操作未主動失效，需人工確認是否會導致不一致。
- **Idempotency**：此 API 不具備冪等性設計。重複呼叫相同 `site` 第二次時，Redis 中已無對應 key，操作仍視為成功但無實際刪除。
- **Transaction**：Redis 不支援跨資料庫交易，刪除 DB5、DB6、DB7 的過程中若發生錯誤，需明確失敗處理策略。需人工確認目前實作是否支援 rollback 或 retry。

---

## 10. 常見錯誤

- ❌ **誤以為此 API 會刪除 MySQL Sport 中的結構性資料（`League`、`Team`）** → ✅ 此 API 僅操作 Redis 快取，不影響 MySQL。
- ❌ **誤以為此 API 會刪除 Cassandra `games` 歷史資料** → ✅ 需人工確認。根據 README，`games` 用於儲存賽事歷史結果，通常不應隨站台清除而刪除。
- ❌ **誤以為此 API 可在任何時間安全呼叫** → ✅ 應在低流量時段操作，避免 `KEYS` / `SCAN` 影響 Redis 效能。
- ❌ **誤以為 `site` 參數對應 `accounts_*` 品牌表** → ✅ `accounts_*` 屬於站台帳號管理，此 API 操作的 `site` 為博弈資料來源站台（如 bet365），兩者無關聯。
- ❌ **忘記在清除後通知相依服務（如 `gamecombineservice`、`sitegameoddservice`）** → ✅ 需人工確認：這些服務是否快取了站台資料，是否需要主動失效。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | README "系統工具" 章節：DELETE `/api/v1/system/clear/sites/{site}` |
| 驗證需求 | README 標記此 API "需要驗證" ✅ |
| Redis DB6 結構 | README "資料庫重要 Table"：`siteGame:{site}:{gameType}` |
| Redis DB5 結構 | README "資料庫重要 Table"：`{gameType}:{lid}:{gDate}` |
| Redis DB7 結構 | README "資料庫重要 Table"：`leagueMap:{gameType}` |
| Cassandra 日誌表 | README "資料庫重要 Table"：`datum_logs` |
| DB 寫入限制 | pricecenterservice-detail：本服務為 pricecenter Cassandra owner，可讀寫刪 |
| DB 不可寫入 | pricecenterservice-detail：sport MySQL 僅 reader，不可寫入 `gameusers_wallet` 等表 |
| 服務相依 | README：相依 `pricecentermanage`，與此 API 的直接互動需人工確認 |
| Code evidence | 需人工確認：`SystemController.ClearSites`、`ClearSiteService.ClearBySite` 實際程式碼路徑 |