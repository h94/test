# 查詢單筆 AI 新聞詳細

## 1. 場景目的

利用完整主鍵（`gdate`, `gtype`, `lid`, `gid`, `llmhashkey`, `status`）精確查詢 `ainews`, `ainews_gs`, 或 `ainews_lt` 中的一筆 AI 生成新聞記錄。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/sports/ai/{gtype}/{gdate}/{lid}/{gid}/{llmhashkey}/{status}` | 查詢通用 AI 新聞 (table: `ainews`) |
| GET | `/api/v1/sports/gsai/{gtype}/{gdate}/{lid}/{gid}/{llmhashkey}/{status}` | 查詢 GS 站台 AI 新聞 (table: `ainews_gs`) |
| GET | `/api/v1/sports/ltai/{gtype}/{gdate}/{lid}/{gid}/{llmhashkey}/{status}` | 查詢 LT 站台 AI 新聞 (table: `ainews_lt`) |

---

## 3. 流程總覽

1.  API Gateway 驗證 JWT Token。
2.  Controller 接收請求，路由參數包含全部六個主鍵。
3.  Service 層依據路由（`/ai/`, `/gsai/`, `/ltai/`）決定查詢目標表：`ainews`, `ainews_gs`, 或 `ainews_lt`。
4.  呼叫 DataProvider (`AINewsDataProvider`) 執行 Cassandra 查詢。
5.  Cassandra 依據完整主鍵（`gdate` 作為 Partition Key）精準定位單筆記錄。
6.  若查無資料，回傳 `404 Not Found`。
7.  取得記錄後，於 DTO 層過濾敏感欄位（`question`, `anwser`, `reanwser`, `llmsettings`, `bets`）。
8.  回傳過濾後的 `AINews` 物件。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `NewsController` | 接收 GET 請求，解析路徑參數 `gtype`, `gdate`, `lid`, `gid`, `llmhashkey`, `status`。依據路由前綴決定 `tableName`。 |
| 2 | Service | `IAINewsService.GetAINews` | 調用 DataProvider 層，傳入完整主鍵與表名。 |
| 3 | Provider | `IAINewsDataProvider.GetAINews` | 組裝 Cassandra SELECT 語句，使用完整主鍵。執行查詢。 |
| 4 | Transfer | DTO 組裝 | 將查詢結果映射到 `AINews` DTO。排除 `question`、`anwser`、`reanwser`、`llmsettings`、`bets` 欄位。 |
| 5 | Controller | `NewsController` | 回傳 HTTP 200 OK 與單筆過濾後的 `AINews` 物件。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `news.ainews` / `news.ainews_gs` / `news.ainews_lt` | Read | 以完整主鍵查詢單筆記錄。 |

---

## 6. 重要規則

- **主鍵完整性**：必須提供完整的六個主鍵（`gdate`, `gtype`, `lid`, `gid`, `llmhashkey`, `status`），順序必須與 Schema 定義一致，不可缺漏。  
  - *Evidence: service detail - 讀取規則; OpenAPI路徑定義。*
- **分區鍵**：`gdate` 是 Partition Key，查詢時必須提供，以確保 Cassandra 查詢效能，避免全表掃描。  
  - *Evidence: service detail - 讀取規則。*
- **不可回傳欄位**：安全規則禁止回傳 `question`、`anwser`、`reanwser`（AI對話內容），以及 `llmsettings`（可能含敏感參數）和 `bets`（內部數據）。對外 API 僅應回傳如 `articleid`、`createtime` 等元資訊。  
  - *Evidence: service detail - 不可回傳欄位; db-detail - 各欄位說明。*
- **權限驗證**：所有請求必須通過 API Gateway 的身份驗證（JWT）。  
  - *Evidence: README.md - 所有API均標示需要驗證。*

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未提供 JWT 或 JWT 無效 | 401 Unauthorized |
| 請求路徑參數不完整或型別錯誤（例如 status 非 int） | 400 Bad Request |
| 根據主鍵查無資料 | 200 OK，但回傳內容為 null 或空（需人工確認具體回傳格式）|
| Cassandra 查詢逾時或連線失敗 | 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| 1 | API Test | 提供合法且存在的完整主鍵 (status=1) 進行查詢 | 200 OK，返回不包含 `question` 等敏感欄位的 `AINews` 物件。 |
| 2 | API Test | 提供合法但部分主鍵不存在（例如不存在的 `gid`）的查詢 | 200 OK，但無回傳資料或特定空值格式。 |
| 3 | Permission Test | 不帶 JWT Token 進行查詢 | 401 Unauthorized |
| 4 | Flow Test | 查詢三種路由 (`/ai/`, `/gsai/`, `/ltai/`) 各一筆 | 驗證分別從 `ainews`, `ainews_gs`, `ainews_lt` 成功讀取。 |

---

## 9. 高風險區域

- **資料外洩風險**：在 Service 或 Controller 層組裝回傳物件時，若未正確過濾 `question`, `anwser`, `llmsettings` 等欄位，將導致敏感資訊洩漏。
- **Cassandra 效能**：雖然此 API 強制提供 Partition Key (`gdate`)，但任何試圖繞過此限制或內部錯誤呼叫都可能導致全表掃描，影響資料庫效能。

---

## 10. 常見錯誤

- ❌ 在 DTO 或 ViewModel 中包含了 `anwser`, `llmsettings`, `bets` 等欄位，導致回傳時洩漏。→ ✅ 必須在資料 Mapping 層明確設定為忽略 (ignore) 或不映射。
- ❌ 從路由參數取得的參數順序與 Cassandra Schema 定義的主鍵順序不同（例如將 `status` 放在 `llmhashkey` 前面）。→ ✅ CQL 查詢時的 WHERE 子句欄位順序必須與 Schema 完全一致。
- ❌ 前端開發者誤用列表查詢 API (`/api/v1/sports/ai/{gtype}/{gdate}`) 來查找單筆資料，但未過濾精確 ID，導致取得大量資料後在前端篩選。→ ✅ 明確單筆查詢應使用此完整主鍵 API，以確保效能和精確性。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `GET /api/v1/sports/ai/{gtype}/{gdate}/{lid}/{gid}/{llmhashkey}/{status}` |
| DB Table | `news.ainews`, `news.ainews_gs`, `news.ainews_lt` |
| DB Schema | `news.md` (Partition Key: gdate) |
| Code | `AINewsDataProvider.cs` |
| Rule | `newsservice/newsservice-detail.md` (讀取規則, 不可回傳欄位) |
| Rule | `db/news-detail.md` (status, used, question 等欄位說明) |