# 後台查詢指定使用者文章

## 1. 場景目的

後台管理人員依使用者帳號查詢該使用者發佈的所有社群文章，用於審核內容、處理檢舉或分析使用者行為。此查詢為後台專屬功能，前台使用者無權限呼叫。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/community/backend/user/{user}/articles` | 依帳號查詢使用者的文章列表 |

- **Query 參數**：`page`（分頁索引）、`game_type`（選填，球種過濾）。
- **Response**：`200 ArticleListUserBackendResponse`，包含文章列表與分頁資訊。

---

## 3. 流程總覽

1. 後台管理員呼叫 API，傳入使用者帳號及可選的 `game_type`、`page`。
2. Controller 層接收參數並進行基本格式驗證（帳號不可為空、page 需為正整數）。
3. 驗證請求者的 authKey，確認具有後台管理權限。
4. 若傳入 `game_type`，校驗其為有效球種類型。
5. 呼叫 Service 層，組合 MeiliSearch 查詢條件：依 `account` 精確匹配，可選依 `game_type` 過濾，並依發文時間倒序分頁。
6. 向 MeiliSearch `community` 索引執行搜尋。
7. 取得文章 ID 列表後，批次查詢 Cassandra `articles` table 取得文章詳細內容（若 MeiliSearch 未儲存全文）。
8. 對文章列表進行帳號遮蔽處理（如需要）。
9. 回傳分頁後的文章列表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `BackendArticleController.GetUserArticles` | 接收 `user`、`page`、`game_type` 參數，觸發 Service |
| 2 | Service | `ArticleService.GetUserArticles` | 組合 MeiliSearch 查詢條件，呼叫 Provider |
| 3 | Provider | `SearchProvider.SearchUserArticles` | 執行 MeiliSearch 查詢，過濾 `account` 與選填 `game_type` |
| 4 | Provider | `ArticleProvider.GetArticlesByIds` | 依文章 ID 批次查詢 Cassandra `articles`，取得完整內容 |
| 5 | Service | `ArticleService.MaskAccount` | 對文章列表中的 `account` 進行遮蔽處理（後台可選擇遮蔽或顯示） |
| 6 | Controller | `BackendArticleController.GetUserArticles` | 組裝 Response，回傳分頁列表 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| MeiliSearch | `community` 索引 | Search | 依 `account`、`game_type` 過濾並排序文章 |
| Cassandra | `community.articles` | Read | 依 ID 批次讀取文章完整內容 |
| Redis | 無 | - | community 服務目前無 Redis 快取 |
| Kafka | `mq` | Publish | 可選：記錄後台查詢日誌 |

---

## 6. 重要規則

- **權限限制**：僅後台管理員可呼叫此 API，需驗證 authKey 具有對應角色。**communityservice 不負責權限核發，驗證依賴 auth/member service 提供的 authKey**。
- **account 遮蔽**：後台查詢時可依業務需求決定是否遮蔽 `account` 欄位。若遮蔽，規則同前台（如 `name***`）。
- **分頁規則**：`page` 為正整數，預設頁碼為 0。每頁筆數應有上限（需人工確認具體數值，例如 20 筆）。
- **game_type 驗證**：若傳入，須為系統支援的球種類型（如 `soccer`、`basketball`），否則回傳空列表或錯誤。
- **不可暴露欄位**：`report_table` 的 `reported_user`、`reported_username` 等無關欄位不能在此 API 回傳。
- **查詢帳號模糊匹配**：`user` 參數為精確帳號，不支援模糊搜尋。若帳號不存在，應回傳空列表而非 404 錯誤。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未提供有效 authKey | 401 Unauthorized |
| authKey 無後台權限 | 403 Forbidden |
| `user` 參數為空或格式不符 | 422 Unprocessable Entity |
| `page` 參數非正整數 | 422 Unprocessable Entity |
| `game_type` 非有效球種 | 422 或忽略參數回傳空列表 |
| 帳號存在但無文章 | 200 空列表，分頁資訊正確 |
| MeiliSearch 服務無法連線 | 500 Internal Server Error，需有 retry 機制 |
| Cassandra 查詢超時 | 500 Internal Server Error，需記錄錯誤日誌 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| TC01 | Permission Test | 無 authKey 呼叫 API | 401 |
| TC02 | Permission Test | 使用一般會員 authKey 呼叫 | 403 |
| TC03 | API Test | `user` 參數為空 | 422 |
| TC04 | API Test | `page` 為負數或非數字 | 422 |
| TC05 | Flow Test | 查詢有 10 篇文章的帳號，第 1 頁 | 200，回傳前 N 篇文章 |
| TC06 | Flow Test | 查詢無文章的帳號 | 200，空列表 |
| TC07 | Flow Test | 指定 `game_type` 過濾 | 200，僅回傳該球種文章 |
| TC08 | Integration Test | MeiliSearch 斷線 | 500，確認 retry 與 log |

---

## 9. 高風險區域

- **高風險 API**：此 API 暴露使用者所有文章，需嚴格控制權限，避免前台使用者誤用。
- **跨服務資料同步**：MeiliSearch 索引與 Cassandra 資料不一致時，可能回傳已刪除文章。需依賴 MeiliSearch 同步機制。
- **Cache consistency**：community 無 Redis 快取，直接查 MeiliSearch 與 Cassandra，一致性問題較低，但需注意 MeiliSearch 索引延遲。
- **效能風險**：若使用者文章數量極大，批次查詢 Cassandra 可能造成效能瓶頸。需限制單次查詢筆數上限。

---

## 10. 常見錯誤

- ❌ 新人誤認為此 API 為前台功能 → ✅ 僅後台管理可用，需檢查權限。
- ❌ AI 遺漏 `account` 遮蔽處理，後台直接回傳完整帳號 → ✅ 雖為後台，仍須依業務規則決定是否遮蔽。
- ❌ 未檢查 `game_type` 有效性，將無效參數傳入 MeiliSearch 導致錯誤 → ✅ 須先驗證球種類型。
- ❌ 混淆 `user` 參數為 `authKey` 而非 `account` → ✅ `user` 是使用者帳號名稱，非內部 authKey。
- ❌ 忘記處理 MeiliSearch 索引延遲，導致剛發佈的文章查不到 → ✅ 屬於系統設計限制，需文件說明。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `BackendArticleController` | OpenAPI `/api/community/backend/user/{user}/articles` |
| DB | `community.articles` (Cassandra) | README Table 清單 |
| Search | MeiliSearch `community` 索引 | README 技術棧 |
| Code | `ArticleService.GetUserArticles` | Source code semantics |
| Code | `SearchProvider.SearchUserArticles` | Source code semantics |
| Rule | 權限依賴 auth/member service | communityservice-detail.md「本服務不負責」 |
| Rule | community 無 Redis 快取 | communityservice-detail.md Redis 章節 |