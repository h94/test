# 刪除運動新聞

## 1. 場景目的

根據指定的球種類型 (`gameType`)，刪除對應動態資料表 (`sports_{gameType}`) 中的運動新聞資料。此功能通常用於清除過期或錯誤的新聞內容。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| DELETE | `/api/v1/sports/{gameType}` | 刪除指定 `gameType` 之動態表中的新聞。**需人工確認**具體刪除範圍（整表清除或條件刪除）。 |

---

## 3. 流程總覽

1.  請求進入 API，攜帶路徑參數 `gameType`。
2.  API Gateway 驗證請求身分（由 `authService` 負責）。
3.  驗證 `gameType` 參數的有效性。
4.  **需人工確認**：呼叫 `SportsNewsService` 或 `DataProvider` 組裝對應的資料表名稱 `sports_{gameType}`。
5.  連結 Cassandra `news` Keyspace。
6.  對目標表執行刪除指令。
7.  回傳成功 (HTTP 200)。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware | ApiGateway | 驗證 JWT Token |
| 2 | Controller | `SportsNewsController.Delete(gameType)` | 接收請求，呼叫 Service |
| 3 | Validator | `IValidator.ValidateGameType(gameType)` | 驗證 `gameType` 是否為允許球種 |
| 4 | Service | `ISportsNewsService` | 協調刪除邏輯（**需人工確認**具體 Service 名稱與實作） |
| 5 | Provider | `IDataProvider` | 組裝 `sports_{gameType}` 表名，執行 Cassandra 刪除語句 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `news` | Delete | 從 `sports_{gameType}` 表中移除新聞。**需人工確認**是否存在其他輔助索引或表需要連動。 |

- **Redis / Queue**：本服務與此場景均未使用。

---

## 6. 重要規則

-   **權限限制**：需要通過 API Gateway 驗證，僅允許具有刪除權限的後台服務或管理員呼叫。
-   **動態表名不可模糊**：`gameType` 必須明確指定，服務將動態組出精確表名 `sports_{gameType}`，不支援模糊匹配或萬用字元。
-   **不可修改欄位**：此操作為不可逆的物理刪除。
-   **刪除範圍**：**需人工確認**。API 定義中無 `RequestBody` 與其他查詢參數，無法從現有文件確定是「刪除整表」、「刪除指定日期前資料」還是「根據 ID 列表刪除」。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| JWT Token 無效或權限不足 | 返回 401 或 403 |
| `gameType` 參數未提供或無效 | 返回 400，提示球種代碼錯誤 |
| 目標表 `sports_{gameType}` 不存在 | **需人工確認**：應返回 404 或自動略過？ |
| Cassandra 連線中斷或寫入超時 | 返回 HTTP 500，記錄錯誤日誌 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| DEL-01 | Permission Test | 無效 Token 呼叫 API | 401 Unauthorized |
| DEL-02 | API Test | 提供有效 `gameType`，確認新聞已被移除 | 200 OK，再次查詢該球種回傳空列表 |
| DEL-03 | API Test | 提供無效的 `gameType` (例如 `unknown`) | 400 Bad Request |
| DEL-04 | Flow Test | 刪除一個空資料表 | **需人工確認**：200 OK，無錯誤發生 |

---

## 9. 高風險區域

-   **資料誤刪**：這是直接對生產資料表進行刪除的高風險操作。若 `gameType` 傳遞錯誤或刪除條件過於寬泛，可能導致大量新聞資料永久丟失。
-   **Cassandra 墓碑**：大量刪除可能在 Cassandra 中產生墓碑，若後續查詢不當，可能導致讀取效能下降。
-   **同步問題**：確認是否有其他服務快取或複製了 `sports_{gameType}` 的資料，刪除後是否需要通知它們（**需人工確認**）。

---

## 10. 常見錯誤

-   **新人**：誤以為可以透過查詢參數 (query string) 傳遞 `gameType`，但它其實是路徑參數 (path parameter)。
-   **新人**：嘗試直接操作 Cassandra 而未透過 NewsService API，導致資料不一致或跳過權限驗證。
-   **AI**：假設 DELETE API 有 `Body` 可以傳入要刪除的新聞 ID 列表。根據現有 OpenAPI，**此假設是錯誤的**，刪除方式需人工確認。
-   **常見漏檢查**：未檢查 `gameType` 對應的表是否真實存在，直接組裝 SQL 導致 Cassandra 報錯。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | DELETE `/api/v1/sports/{gameType}` (OpenAPI 定義) |
| DB | `sports_{gameType}` (README, newsservice-detail.md) |
| 驗證 | `IValidator.ValidateGameType` (程式碼語意分析) |
| 權限 | `用戶認證與授權 (authService)` (newsservice-detail.md: 本服務不負責) |