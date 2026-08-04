# 取得單一運動站台文章

## 1. 場景目的

根據文章 ID 查詢並回傳單一站台文章的詳細內容，供前台或管理後台使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sportarticles/{id}` | 查詢特定文章，需驗證 |

---

## 3. 流程總覽

1. 客戶端請求經由 API Gateway 進行 JWT 驗證（由 authService 負責，newsservice 不處理）
2. 通過驗證後，請求抵達 newsservice 的 Controller
3. Controller 從路徑取出文章 ID 並呼叫對應的 Service 層方法
4. Service 呼叫 Data Provider 查詢 Cassandra 中的文章資料
5. 若文章存在，回傳文章內容（經過 DTO 過濾，移除不可回傳欄位）
6. 若文章不存在，回傳適當錯誤

---

## 4. 程式流程

因原始碼未提供，以下為基於架構慣例與專案模組推斷的流程，部分層級名稱需人工確認。

| 順序 | Layer | Class / Method (推測) | 動作 |
|---|---|---|---|
| 1 | Controller | `SportArticleController.GetById(int id)` | 接收 id 參數，調用 Service |
| 2 | Service | `ISportArticleService.GetArticleById(int id)` | 業務邏輯層，可能包含權限檢查 |
| 3 | Provider | `ISportArticleDataProvider.GetById(int id)` | 組裝 CQL 查詢，透過 ECFramework 查詢 Cassandra |
| 4 | Data Layer | Cassandra `news.sportarticles` | 以主鍵 `id` 查詢一筆資料 |

> **需人工確認**：`SportArticleController`、`ISportArticleService` 與 `ISportArticleDataProvider` 的實際名稱，以及 `sportarticles` 表的確實存在與 Schema。根據 README，該 endpoint 存在，但 DB schema 清單中未列出 `sportarticles` 表，可能位於其他 keyspace 或為動態定義。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra table `sportarticles` (需確認) | Read (SELECT) | 根據文章 ID 查詢單筆文章記錄 |

本服務未使用 Redis 或 Message Queue。

---

## 6. 重要規則

- **權限限制**：所有 `/api/v1/sportarticles/*` 請求必須通過驗證（由 API Gateway 確保）。newsservice 本身不實作授權邏輯，僅信任上游傳入的身份。
- **不可暴露資料**：
  - 若文章表含有敏感欄位（如內部備註、原始 HTML 風險標籤等），應在 DTO 層過濾。目前無明文定義，**需人工確認**。
- **查詢限制**：
  - 文章 ID 應為有效的主鍵值，不允許模糊查詢或全表掃描。
- **狀態值限制**：
  - **需人工確認**：文章是否有狀態欄位（如草稿、已發布、已下架）。根據一般後台管理邏輯，應只回傳已發布狀態的文章。
- **Idempotency**：讀取操作具有冪等性，無需額外設計。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未攜帶有效 token 或 token 過期 | API Gateway 攔截，回傳 401 Unauthorized |
| 文章 ID 不存在 | 回傳 404 Not Found 或自定義錯誤碼 |
| Cassandra 查詢逾時或不可用 | 回傳 500 Internal Server Error，並記錄 log |
| 文章狀態為尚未發布 | **需人工確認**：應回傳 404 或 403，防止未發布內容被前台存取 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 以有效 token 查詢存在的文章 ID | 200 OK，回傳正確文章內容 |
| TC02 | Permission Test | 無 token 或無效 token | 401 Unauthorized |
| TC03 | Flow Test | 查詢不存在的 ID | 404 / 對應錯誤訊息 |
| TC04 | Data Filter Test | 文章包含不應暴露的欄位（如內部標記） | 回傳的 DTO 中不應包含該欄位 |

---

## 9. 高風險區域

- **高風險 DB**：`sportarticles` 表若存在且包含大量資料，應避免因不當查詢導致 full scan。
- **Cache consistency**：本場景無快取，若有日後加入 Redis 快取，需注意快取與 DB 的一致性。
- **敏感資料外洩**：需嚴格定義 DTO，防止原始內容或未過濾的 HTML 被直接傳遞。

---

## 10. 常見錯誤

- ❌ 忘記在路由上啟用驗證，導致 endpoint 可被匿名存取 → ✅ 所有 `/api/v1/sportarticles/*` 都要求在 gateway 層驗證。
- ❌ 回傳的 model 直接映射 DB entity，暴露所有欄位 → ✅ 應使用 DTO，僅回傳必要與對外開放的欄位。
- ❌ 誤以為 API 可接受多個 ID 或模糊搜尋 → ✅ `GET /api/v1/sportarticles/{id}` 僅支援單一 ID 精確查詢。
- ❌ 未處理 DB 層的例外狀況，導致服務 crash → ✅ 應實作全域例外處理，將 Cassanda 例外轉換為標準 HTTP 狀態碼。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README.md，提及 `GET /api/v1/sportarticles/{id}` |
| 驗證需求 | README.md，該路由標記需要驗證 |
| 推測 DB table | 服務職責為站台文章，但無直接 DB schema 定義，**需人工確認**：可能為 `news.sportarticles` |
| 授權說明 | newsservice-detail.md：「本服務不負責」章節說明認證由 authService/API gateway 處理 |
| 不可回傳欄位政策 | newsservice-detail.md 中不可回傳欄位一般性原則（如 anwser、llmsettings 等），本場景的文章內容亦應比照篩選 |
| 錯誤處理慣例 | 無程式碼證據，依照一般 ASP.NET Core Web API 慣例 |

> **建議新增文件**：`sportarticles` 表的 Schema 定義，以及 DTO 與 DB Entity 之間的對應規則，明確定義可回傳欄位清單。  
> **建議新增規則**：文章狀態值定義（如 Draft、Published、Archived）與前台過濾邏輯。  
> **建議新增測試**：狀態過濾測試，確保非發布狀態文章不會被 GET 請求回傳。