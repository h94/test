# 场景：設定活動得獎帳號

## 1. 場景目的

後台管理人員或特定排程，將活動優勝者帳號及其相關數據（如預測次數、盈利點數、排名、勝率）寫入得獎名單。此操作為活動結算流程的一部分，確保排行榜與獎勵派發有據可查。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/special/winners/{site}/{activityEvent}` | 設定特定活動、特定週期的得獎帳號 |

---

## 3. 流程總覽

1. 接收寫入得獎者請求，包含 `site`, `activityEvent`, `cid` (週期ID) 及得獎者清單。
2. 驗證請求者是否具有後台管理或結算相關權限。
3. 驗證目標週期 `activities_cycles` 是否存在且處於可寫入狀態（例如：活動進行中或已結束，但尚未鎖定）。
4. 批次寫入得獎帳號資料至 `activities_winneraccounts` 表。
5. 若寫入成功，回傳成功響應；若發生資料衝突或驗證失敗，回傳錯誤訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware | `AuthMiddleware` | 驗證請求的 JWT Token，確認身份。 |
| 2 | Controller | `SpecialController.SetWinners` | 接收請求，將 `site`, `activityEvent`, `winners` 等參數傳遞給 Service。 |
| 3 | Service | `ActivityService.SetWinnersAsync` | 執行核心業務邏輯：驗證活動狀態、檢查帳號有效性、組裝資料。 |
| 4 | Provider | `PredictDataProvider` | 將得獎資料 **INSERT** 至 `predict.activities_winneraccounts`。 |
| 5 | Service | `ActivityService.SetWinnersAsync` | 處理寫入結果，可能需要清除相關的排行榜快取。 |
| 6 | Controller | `SpecialController.SetWinners` | 根據執行結果，回傳 `200 OK` 或 `4xx/5x` 錯誤。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.activities_cycles` | Read | 驗證指定的 `site`, `activityEvent`, `cid` 是否存在且有效。 |
| DB | `predict.activities_winneraccounts` | Write | 將優勝者資訊（`account`, `rank`, `profitpoint`等）寫入。 |
| DB | `pricecenter.accounts_{suffix}` | Read | (若需要驗證帳號是否存在且啟用) 查詢對應站點的帳號表。 |
| Cache | `predict:winners:{cid}` | Delete | (若存在) 寫入成功後，需清除該週期的得獎快取，確保查詢一致性。 |

---

## 6. 重要規則

- **權限限制**：此 API 僅限後台管理角色或具備活動管理權限的服務呼叫。
- **欄位限制**：`activities_winneraccounts` 表格中的 `predictcount`, `profitpoint`, `rank`, `winpercentage` 欄位，根據 `predictservice-detail.md`，**僅能由結算排程依演算法計算寫入，不可人工調整**。此 API 應僅負責寫入經結算模組計算後的最終結果。
- **不可暴露資料**：回傳或儲存時，須確保不會將 `account` 資訊洩露至未經授權的公開 API。
- **狀態值限制**：需確認 `activities_cycles` 表中的 `startdate`, `starttime`, `enddate`, `endtime` 組合，確保活動週期有效，但該表欄位不可由此流程修改。
- **不可修改欄位**：`activities_winneraccounts` 的四個主鍵 (`site`, `activityevent`, `cid`, `account`) 組合在 INSERT 後不可更新，若需修改排名需透過重新結算流程。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求未包含有效的管理者憑證 | 回傳 `401 Unauthorized`。 |
| 請求的 `site` 或 `activityEvent` 參數為空 | 回傳 `400 Bad Request`，並提示缺少必要參數。 |
| 目標 `activities_cycles` 不存在 | 回傳 `422 Unprocessable Entity`，表示活動週期無效。 |
| 請求寫入的 `account` 包含無效或已停用的帳號 | 回傳 `422 Unprocessable Entity`，並指明無效的帳號。 |
| Cassandra 寫入逾時或失敗 | 回傳 `500 Internal Server Error`，並記錄詳細錯誤日誌。 |
| 嘗試寫入已存在於得獎名單的帳號（重複寫入） | 根據業務規則，可能回傳 `409 Conflict` 或直接覆蓋。 |
| 活動週期已結束且 `resultcount` 已達上限 | 回傳 `422 Unprocessable Entity`，表示週期已鎖定。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| ACL-01 | Permission Test | 使用一般使用者 Token 呼叫 API | 應收到 `401` 或 `403` 錯誤。 |
| ACL-02 | Permission Test | 使用後台管理者 Token 呼叫 API | 請求被接受並執行。 |
| FLOW-01 | Integration Test | 對一個有效的活動週期寫入得獎者 | Cassandra `activities_winneraccounts` 表中出現新記錄。 |
| FLOW-02 | Integration Test | 寫入成功後，查詢該週期得獎者 | 快取應被清除，查詢結果為最新的得獎者名單。 |
| VALID-01 | Validation Test | 寫入一個不存在的 `cid` | 收到 `422` 錯誤，錯誤訊息指出週期不存在。 |
| VALID-02 | Validation Test | 在得獎者名單中放入一個空字串或 Null | 收到 `400` 或 `422` 驗證錯誤。 |

---

## 9. 高風險區域

- **高風險 Table**：`predict.activities_winneraccounts` (直接影響排行榜與獎金發放準確性)。
- **高風險 API**：`POST /api/v1/special/winners/{site}/{activityEvent}` (直接寫入關鍵結果資料)。
- **Transaction**：若存在多個得獎者，應考慮使用批次語句或確保部分寫入失敗時的處理機制。
- **Cache consistency**：寫入成功後**必須**清除相關的快取 (如 `predict:winners:{cid}`)，否則查詢結果會不一致。

---

## 10. 常見錯誤

- **新人容易犯錯**：未驗證 `activities_cycles` 是否確實存在就直接嘗試寫入得獎者。
- **AI 容易誤解**：誤以為此 API 負責計算排名，實際上它只負責寫入已計算好的結果。
- **常見漏檢查項目**：未檢查待寫入的 `account` 在 `pricecenter` 中是否為 `enabled=1` 的有效帳號。
- **常見錯誤流程**：在結算流程尚未完全確認最終結果前，就提前呼叫此 API 寫入部分得獎者，導致後續需手動修正。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `SpecialController` (基於路徑 `/api/v1/special/winners/{site}/{activityEvent}`) |
| DB | `predict.activities_winneraccounts` |
| DB | `predict.activities_cycles` |
| Code | `ActivityService.SetWinnersAsync` (推測命名) |
| Code | `PredictDataProvider` (推測命名) |
| Rule | `predictservice-detail.md` 中對 `activities_winneraccounts` 的寫入限制。 |