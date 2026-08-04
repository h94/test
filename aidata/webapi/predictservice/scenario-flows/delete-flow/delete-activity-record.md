# 删除活动记录

## 1. 場景目的

允許管理員根據指定的站點(`site`)、活動事件(`activityEvent`) 及使用者帳號(`account`)，將該使用者在特殊活動中的所有記錄（包含勝場、剩餘天數等）從系統中永久移除。此動作通常用於資料矯正或清除測試資料。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| DELETE | `/api/v1/special/records/{site}/{activityEvent}/{account}` | 刪除指定帳號的活動記錄 |

---

## 3. 流程總覽

1.  API 閘道器 (API Gateway) 接收請求，進行身份驗證。
2.  驗證請求者是否具有管理員權限。
3.  解析路徑參數 (`site`, `activityEvent`, `account`)。
4.  依據參數組合出 Cassandra 的 partition key。
5.  向 `predict.activities_record` 資料表發出刪除指令。
6.  若記錄不存在或刪除成功，皆回傳成功；若發生非預期錯誤，則回傳失敗。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware | ECFramework.ECService | 驗證 JWT Token 有效性。 |
| 2 | Controller | `SpecialController` | 接收請求，呼叫對應的 Service。 |
| 3 | Service | `SpecialService` | 執行業務邏輯驗證（如: 權限）。 |
| 4 | Provider | `ActivityRecordProvider` | 組裝 Cassandra 查詢語法並執行。 |
| 5 | Data | `predict.activities_record` | 執行 DELETE 操作。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.activities_record` | Delete | 刪除指定 `site`, `eventname`, `account` 的活動記錄。 |

---

## 6. 重要規則

- **權限限制**：必須是管理員才可執行此操作（需人工確認）。
- **不可逆操作**：此為物理刪除，資料無法復原。
- **參數對應**：路徑中的 `{activityEvent}` 對應到 `activities_record` table 中的 `eventname` 欄位。
- **不可回傳欄位**：雖然 API 不涉及查詢，但若操作失敗需回傳訊息，不可包含活動記錄內的 `winbets` 等明細。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未帶入合法 Token | 回傳 401 Unauthorized。 |
| Token 有效但帳號無管理權限 | 回傳 403 Forbidden。 |
| 嘗試刪除不存在的記錄 | 回傳 2xx 成功（冪等性），或回傳 404 依實際實作為準（需人工確認）。 |
| Cassandra 連線逾時或不可用 | 回傳 5xx Server Error。 |
| 參數格式錯誤 (e.g., 包含非法字元) | 回傳 4xx Bad Request。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SRA-DEL-01 | Permission Test | 一般使用者嘗試刪除他人活動記錄 | 403 Forbidden |
| SRA-DEL-02 | Flow Test | 管理員刪除已存在的活動記錄 | 200 OK，且該記錄確實從 DB 消失 |
| SRA-DEL-03 | API Test | 管理員刪除不存在的活動記錄 | 200 OK (冪等) 或 404 (視實作) |
| SRA-DEL-04 | API Test | 請求參數 `site` 或 `account` 為空 | 404 Not Found 或 400 Bad Request |

---

## 9. 高風險區域

- **高風險 API**：DELETE 操作具破壞性。若被惡意利用或誤刪，可能導致活動數據遺失，影響排行榜準確性。
- **Cache consistency**：刪除記錄後，若存在相關的快取（如: `predict:activity_record:{site}:{eventname}:{account}`），必須一併清除，否則使用者可能在前端仍然看到已刪除的資料。需人工確認此處是否實作快取清除機制。
- **Idempotency**：需確認對於同一請求反覆執行的冪等性設計，避免重複請求造成非預期結果。目前的 DB 操作（刪除）具備天然冪等性。

---

## 10. 常見錯誤

- ❌ **新人容易犯錯**：直接將 `activityEvent` 對應到 `activities_cycles` 或 `activities_winneraccounts` 表。應對應至 `activities_record` 表。
- ❌ **AI 容易誤解**：誤會此 API 會連帶刪除 `activities_winneraccounts` 中的得獎記錄。此 API 僅針對 `activities_record`，得獎記錄需由其他專門 API 管理。
- ❌ **常見漏檢查項目**：未驗證請求者是否具有管理員身份即執行刪除。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | PredictService README: `DELETE /api/v1/special/records/{site}/{activityEvent}/{account}` |
| DB Table | `predict.activities_record` |
| DB Schema | `predict.md`: `CREATE TABLE predict.activities_record (...)` |
| Service Role | `predictservice-detail.md`: predictservice 對 predict keyspace 為 owner，負責讀、寫、刪。 |