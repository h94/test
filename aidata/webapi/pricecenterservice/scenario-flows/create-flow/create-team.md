# 建立球隊

## 1. 場景目的

管理員在指定聯賽（League）下建立一支新球隊。此操作會同時寫入球隊資訊至 MySQL `sport.Team` 表，並更新 Redis DB7 的聯賽對照表快取，以確保前台查詢時能取得最新的聯賽與球隊對照資訊。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/leagues/{gameType}/{lid}/teams` | 在指定聯賽下建立新球隊 |

---

## 3. 流程總覽

1. 接收建立球隊的 request，包含 `gameType`、`lid`（聯賽 ID）
2. 驗證請求者是否具備後台管理權限
3. 驗證 `gameType` 與 `lid` 是否存在於 MySQL `sport.League` 表
4. 檢查球隊名稱是否重複（同一聯賽下）
5. 寫入球隊主檔至 MySQL `sport.Team`
6. 更新 Redis DB7 `leagueMap:{gameType}` 中該聯賽的球隊對照表
7. 回傳新建立的球隊資訊

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `TeamController.PostTeam` | 接收 `gameType`、`lid`、`SiteTeam` body，呼叫 Service |
| 2 | Service | `TeamService.CreateTeam` | 協調驗證、寫入 DB 與更新快取 |
| 3 | Service | `TeamService.CreateTeam` | 查詢 MySQL `sport.League` 確認聯賽存在（❓需人工確認：League 表結構未完整提供）|
| 4 | Service | `TeamService.CreateTeam` | 檢查 MySQL `sport.Team` 同名球隊是否存在 |
| 5 | Provider | `TeamProvider.Insert` | INSERT 新球隊至 MySQL `sport.Team` |
| 6 | Service | `CacheService.UpdateLeagueMap` | 更新 Redis DB7 `leagueMap:{gameType}` 快取 |
| 7 | Controller | `TeamController.PostTeam` | 回傳 `Team` 物件 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| MySQL | `sport.League` | Read | 驗證聯賽是否存在 |
| MySQL | `sport.Team` | Read | 檢查球隊名稱是否重複 |
| MySQL | `sport.Team` | Write | 寫入新建球隊主檔 |
| Redis | DB7 `leagueMap:{gameType}` | Update | 更新聯賽－球隊對照表快取 |
| Kafka | （無） | － | 此場景未使用 Queue |
| Cassandra | （無） | － | 此場景未使用 Cassandra |

---

## 6. 重要規則

- **權限限制**：僅後台管理員可呼叫此 API（基於 README「需要驗證」標記）。
- **不可重複**：同一聯賽下球隊名稱不可重複（需人工確認：從 `sport.Team` Schema 無法推導唯一約束，但業務邏輯通常限制）。
- **聯賽存在性**：`lid` 必須在 `sport.League` 中存在。
- **快取一致性**：寫入 MySQL 後，**必須立即更新** Redis DB7 對照表，不可僅依賴 TTL 過期。
- **不可修改欄位**：`sport.Team` 主鍵（❓需人工確認：Team 表 Schema 未提供，無法確認主鍵欄位與不可修改欄位）。
- **回傳欄位限制**：任何對外 API 不可回傳內部流水號（如 `TeamID` 若為內部對照用）。
- **無 Transaction**：目前架構 MySQL 寫入與 Redis 更新為非交易性操作。若 Redis 更新失敗，可能導致快取與 DB 不一致（高風險）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未提供驗證 token 或權限不足 | 回傳 401 Unauthorized |
| `gameType` 或 `lid` 為空 | 回傳 400 Bad Request，提示必要參數 |
| `lid` 不存在於 `sport.League` | 回傳 404 Not Found |
| 球隊名稱已存在於同一聯賽 | 回傳 409 Conflict，提示名稱重複 |
| MySQL `sport.Team` INSERT 失敗 | 回傳 500 Internal Server Error，寫入 Kafka 錯誤日誌 |
| Redis DB7 更新失敗 | 回傳 200（寫入 MySQL 已成功）但記錄錯誤日誌，快取需後續修復（❓需人工確認：目前無實作 Retry 或補償機制） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| CT-01 | API Test | 正常建立球隊 | 回傳 200，MySQL 寫入成功，Redis 快取更新 |
| CT-02 | Permission Test | 無 token 呼叫 | 回傳 401 |
| CT-03 | Validation Test | 重複球隊名稱 | 回傳 409 |
| CT-04 | Flow Test | 聯賽不存在 | 回傳 404 |
| CT-05 | Consistency Test | MySQL 寫入成功但 Redis 更新失敗 | MySQL 有資料，Redis 缺漏；日誌記錄錯誤（手動驗證） |

---

## 9. 高風險區域

- **快取一致性**：MySQL 與 Redis 為非原子操作，Redis 更新失敗時出現短期不一致。
- **重複球隊**：若未在應用層或 DB 層強制唯一約束，可能寫入重複球隊名稱。
- **聯賽驗證**：若 `sport.League` 查詢失敗但未正確處理，可能對不存在的聯賽建立球隊，導致孤立資料。
- **無 Transaction**：若 MySQL INSERT 成功後應用層 crash，Redis 將遺失更新。

---

## 10. 常見錯誤

- ❌ 未驗證聯賽是否存在就直接 INSERT → ✅ 必須先查 `sport.League`。
- ❌ 忘記更新 Redis DB7 → ✅ 前台將查不到新建球隊，直到快取過期或被其他操作刷新。
- ❌ 回傳內部對照用的 `TeamID` 或 `SiteID` → ✅ 對外 API 應只回傳 `Name`、`League` 等展示層資訊。
- ❌ 未處理 Redis 更新失敗 → ✅ 至少應記錄錯誤日誌，建議加入重試或補償排程。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `TeamController.PostTeam` |
| DB | MySQL `sport.League`, `sport.Team` |
| Cache | Redis DB7 `leagueMap:{gameType}` |
| Code | `TeamService.CreateTeam`, `TeamProvider.Insert` |
| Schema | `pricecenter.md`, `sport.md` |
| README | POST `/api/v1/leagues/{gameType}/{lid}/teams` 需要驗證 |

---

## 建議新增文件 / 規則 / 測試

- **需人工確認**：`sport.Team` 完整 Schema（主鍵、唯一約束、所有欄位定義）。
- **需人工確認**：`sport.League` 完整 Schema，確認 `lid` 對應欄位名稱。
- **需人工確認**：Redis 更新失敗時的 Retry 或補償機制是否存在。
- **建議新增規則**：明確 `sport.Team` 不可回傳欄位（如內部流水號、SiteID）。
- **建議新增測試**：Redis 更新失敗後的監控告警與修復流程測試（CT-05 延伸）。