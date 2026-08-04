# 手動拆分球隊

## 1. 場景目的

管理員在後台手動將指定遊戲類型下的球隊資料，從來源站台的原始數據拆分並寫入正式球隊主表（`sport.Team`），並同步更新 Redis 聯賽對照表（`leagueMap:{gameType}`），以確保前台賽事顯示正確的球隊名稱與對照關係。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/split/teams/{gameType}` | 手動拆分指定遊戲類型的球隊 |

---

## 3. 流程總覽

1. 接收 PUT 請求，路徑包含 `gameType`（如 `BS`、`BK`）。
2. 驗證呼叫者權限（需通過 ECFramework.ECService）。
3. 調用 Service 層 `SplitTeams` 方法。
4. 從 Redis DB6 (`siteGame:{site}:{gameType}`) 或 Provider 層讀取指定 `gameType` 的所有站台球隊原始數據。
5. 遍歷站台球隊資料，依據拆分規則（如比對 `sport.Team` 現有資料及站點映射）進行拆分。
6. 將拆分後的正式球隊資料寫入 MySQL `sport.Team` 表：
   - 若球隊不存在則 INSERT。
   - 若球隊已存在則 UPDATE 相關欄位（如縮寫、站點對照）。
7. 更新 Redis DB7 中的聯賽對照表 `leagueMap:{gameType}`。
8. 記錄操作日誌至 Cassandra `pricecenter.datum_logs` 或透過 `/api/v1/log/game` 寫入工具日誌。
9. 回傳操作結果（成功 / 失敗）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `SplitTeamsController.Put` | 接收 `gameType` 參數，呼叫 `SplitTeamsService`。 |
| 2 | Validator | `AuthValidator` | 驗證 JWT Token 或內部驗證憑證，確保為管理員操作。 |
| 3 | Service | `SplitTeamsService.SplitTeamsAsync` | 協調拆分流程，調用 Provider 讀取站台數據，處理拆分邏輯，並寫入 DB 與 Redis。 |
| 4 | Provider | `SiteGameProvider.GetSiteTeamsAsync` | 從 Redis DB6 或外部 API 取得各站台原始球隊列表。 |
| 5 | Provider | `TeamProvider.UpsertTeamAsync` | 對 `sport.Team` 執行 INSERT 或 UPDATE。 |
| 6 | Provider | `RedisLeagueMapProvider.UpdateLeagueMapAsync` | 寫入 Redis DB7 `leagueMap:{gameType}`。 |
| 7 | Provider | `LogProvider.WriteToolLogAsync` | 透過 `/api/v1/log/game` 記錄操作日誌。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| MySQL | `sport.Team` | Write / Upsert | 寫入或更新正式球隊資訊。 |
| Redis | DB6 `siteGame:{site}:{gameType}` | Read | 讀取各來源站台的原始球隊資料（需人工確認是否此處讀取或直接從 Provider 查詢）。 |
| Redis | DB7 `leagueMap:{gameType}` | Write | 更新聯賽與球隊名稱對照快取。 |
| Cassandra | `pricecenter.datum_logs` | Write | 記錄資料來源操作日誌。 |

---

## 6. 重要規則

- **權限限制**：必須通過 `ECFramework.ECService` 驗證，且具備管理員權限。
- **遊戲類型限制**：`gameType` 必須為系統支援的有效球種代碼（如 `BS`、`BK` 等），否則應拒絕請求。
- **不可暴露欄位**：對外回傳結果不可包含 `password` / `AuthKey` / `phone` 等敏感欄位（遵循 `pricecenter-detail.md` 規範）。
- **Redis 更新規則**：更新 `leagueMap:{gameType}` 時，需確保寫入成功，若失敗應觸發重試機制或標記為部分成功。
- **Transaction 規則**：MySQL `sport.Team` 的寫入與 Redis 更新不屬於同一個 Transaction；若 Redis 更新失敗，需記錄錯誤日誌，但不應回滾已寫入的 MySQL 資料（需人工確認具體專案實作）。
- **狀態值限制**：無特定狀態欄位。
- **不可修改欄位**：`sport.Team` 中 `id` (Primary Key) 不可修改；球隊建立後 `lid` 不可變更。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未通過驗證或權限不足 | 回傳 401 Unauthorized 或 403 Forbidden。 |
| `gameType` 不存在或未提供 | 回傳 400 Bad Request，提示參數錯誤。 |
| Redis DB6 站台資料為空 | 回傳 200 OK 但訊息提示無需拆分的球隊。 |
| MySQL `sport.Team` 寫入失敗（如重複鍵衝突、連線逾時） | 回傳 500 Internal Server Error，記錄錯誤日誌，中斷流程。 |
| Redis DB7 更新失敗 | 回傳 200 OK 但附加警告訊息，或回傳 500（取決於實作），記錄錯誤日誌。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| SPLIT-01 | Permission Test | 使用無管理員權限的 Token 呼叫 API | 應回傳 403 Forbidden。 |
| SPLIT-02 | API Test | 傳入不存在的 `gameType`（如 `XYZ`） | 應回傳 400 Bad Request 或明確錯誤訊息。 |
| SPLIT-03 | Flow Test | 呼叫 API 拆分有站台資料的遊戲類型 | MySQL 中 `sport.Team` 應正確插入/更新，Redis DB7 `leagueMap:{gameType}` 應更新。 |
| SPLIT-04 | Flow Test | 拆分過程中 Redis DB7 模擬寫入失敗 | 應回傳錯誤日誌，MySQL 資料已寫入（或取決於專案實作）。 |
| SPLIT-05 | Integration Test | 拆分後查詢 `GET /api/v1/teams/{gameType}` | 應回傳包含新拆分球隊的列表。 |

---

## 9. 高風險區域

- **高風險 Table**：`sport.Team`（直接影響前台賽事顯示與競猜結算的球隊資料一致性）。
- **高風險 API**：`PUT /api/v1/split/teams/{gameType}`（管理員工具，錯誤操作會大量影響正式數據）。
- **跨服務資料同步**：拆分後 Redis DB7 `leagueMap` 與 MySQL `sport.Team` 必須保持一致，否則會導致前台顯示錯誤隊名或無法對應賽事。
- **Transaction**：MySQL 與 Redis 為異質儲存，此為非原子性操作。若拆分途中 Redis 掛掉，可能造成 MySQL 有新隊名但前台快取仍是舊資料。
- **Cache consistency**：更新 Redis DB7 後，需確保沒有遺留舊的快取。
- **Idempotency**：未提供冪等性 Token；重複呼叫會導致重複執行更新操作，雖不應重複 insert，但仍需注意。

---

## 10. 常見錯誤

- ❌ 新人容易犯錯：忘記 `sport.Team` 的表結構，直接將站台原始隊名當成正規隊名寫入，而沒有經過比對或正規化。
- ❌ AI 容易誤解：誤認為此流程僅修改 Redis 快取，而未對 MySQL `sport.Team` 進行持久化寫入。
- ❌ 常見漏檢查項目：寫入 Redis DB7 後，未驗證 `leagueMap:{gameType}` 內容是否成功更新成最新資料。
- ❌ 常見錯誤流程：在 MySQL 寫入成功後、Redis 更新前發生 Exception，沒有進行 Redis 補償或錯誤記錄，導致兩邊資料不一致。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `PUT /api/v1/split/teams/{gameType}` (README.md - 聯賽與球隊管理) |
| DB (Write) | `sport.Team` (README.md - 資料庫重要 Table) |
| Redis (Read) | `siteGame:{site}:{gameType}` (README.md - 資料庫重要 Table) |
| Redis (Write) | `leagueMap:{gameType}` (README.md - 資料庫重要 Table, 需人工確認寫入操作) |
| Code | `SplitTeamsService.SplitTeamsAsync` (推測) |
| Detail | `服務不負責` (pricecenterservice-detail.md: 運動數據同步由外部資料源匯入，pricecenter 僅負責映射與查詢，符合手動拆分職責) |