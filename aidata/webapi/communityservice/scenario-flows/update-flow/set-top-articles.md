# 設定置頂文章

## 1. 場景目的
管理員將指定已發布的體育社群文章設定為置頂狀態，使其在文章列表中被優先展示。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/community/{gameType}/top_articles` | 設定指定文章為置頂（需要驗證與管理權限） |

---

## 3. 流程總覽

1. 驗證呼叫者身份（authkey）
2. 驗證管理員權限
3. 驗證 request body 參數
4. 查詢指定文章是否存在
5. 檢查文章所屬 `game_type` 與 API path 是否匹配
6. 檢查文章是否已是置頂狀態
7. 更新 Cassandra `articles` table（設定 `is_top=1`）
8. 同步更新 MeiliSearch `community` 索引中的 `is_top` 欄位
9. 回傳更新結果

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `TopArticleController` | 接收 PUT request，擷取 `gameType`、`article_id` |
| 2 | Validator | `SetTopArticleArgs` (Pydantic) | 驗證 `article_id` 必填且格式正確 |
| 3 | Service | `TopArticleService.set_top_article` | 協調權限驗證、文章檢查、DB/索引更新 |
| 4 | Provider | `ArticleProvider.get_article_by_id` | 從 Cassandra `articles` table 查詢文章 |
| 5 | Service | `AuthService.verify_admin_role` | 檢查 authkey 是否擁有管理員權限 |
| 6 | Provider | `ArticleProvider.set_article_top` | 寫入 Cassandra `articles.is_top=1` |
| 7 | Provider | `MeiliSearchProvider.update_article` | 更新 MeiliSearch 索引中 `is_top=true` |
| 8 | Controller | `TopArticleController` | 回傳成功訊息 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `community.articles` | Read | 查詢文章是否存在、是否已置頂 |
| DB (Cassandra) | `community.articles` | Write (Update) | 設定 `is_top=1` |
| MeiliSearch | `community` 索引 | Read/Write (Update) | 同步文章置頂狀態至搜尋索引 |
| Redis | 無 | 無 | community 無使用 Redis 快取 |

---

## 6. 重要規則

- **權限限制**：僅管理員可執行置頂操作（須驗證 authkey 對應角色）。
- **狀態值限制**：文章 `is_top` 欄位僅接受 `0`（否）或 `1`（是），置頂操作時更新為 `1`。
- **不可修改欄位**：`article_id`、`game_type` 在更新時不可變更。
- **冪等性**：若文章已是置頂狀態（`is_top=1`），API 應回傳成功或忽略，而非報錯。
- **一致性規則**：Cassandra 與 MeiliSearch 更新須同步完成；若 MeiliSearch 更新失敗應觸發重試或記錄錯誤日誌，避免前端搜尋結果不一致。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未提供 authkey 或 authkey 無效 | 回傳 401 Unauthorized |
| authkey 不具備管理員權限 | 回傳 403 Forbidden |
| request body 缺少 `article_id` | 回傳 422 Unprocessable Entity |
| 文章不存在 | 回傳 404 Not Found |
| 文章所屬 `game_type` 與 API path 不符 | 回傳 400 Bad Request（或 403） |
| Cassandra 寫入失敗 | 回傳 500 Internal Server Error，且不更新 MeiliSearch |
| MeiliSearch 更新失敗 | 需人工確認（應記錄錯誤並重試，或回傳 500） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TOP-01 | Permission Test | 一般會員呼叫置頂 API | 403 Forbidden |
| TOP-02 | API Test | 管理員置頂未被置頂的文章 | 200 OK，文章 `is_top=1` |
| TOP-03 | API Test | 管理員置頂已置頂的文章 | 200 OK（冪等） |
| TOP-04 | Flow Test | 文章不屬於指定 `game_type` | 400 或 403 |
| TOP-05 | Integration Test | 模擬 MeiliSearch 寫入失敗 | 相應錯誤處理（重試或記錄錯誤） |
| TOP-06 | API Test | 文章不存在 | 404 Not Found |

---

## 9. 高風險區域

- **跨儲存一致性**：Cassandra 與 MeiliSearch 的 `is_top` 狀態必須保持一致，避免搜尋結果與實際文章列表不同步。
- **無 Redis 快取**：community 無快取層，每次查詢直接讀取 Cassandra/MeiliSearch，需確保資料庫查詢性能。
- **權限驗證**：若管理員權限驗證不嚴格，可能導致一般使用者任意置頂文章，影響社群內容排序。

---

## 10. 常見錯誤

- ❌ **忘記驗證文章所屬 `game_type`**：可能導致跨球種文章被置頂。
- ❌ **MeiliSearch 更新失敗但回傳成功**：前端將無法搜尋到置頂文章，開發者應確保錯誤被妥善處理。
- ❌ **未檢查文章是否存在**：直接嘗試更新可能導致 Cassandra 寫入異常或不一致。
- ❌ **AI 誤解流程**：誤以為需重新寫入整筆文章資料（應僅更新 `is_top` 單一欄位）；誤以為需清理或寫入 Redis 快取（community 無使用 Redis）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `PUT /api/community/{gameType}/top_articles` |
| Controller | `TopArticleController` |
| Service | `TopArticleService.set_top_article` |
| Provider | `ArticleProvider` (lookup / status update) |
| Provider | `MeiliSearchProvider.update_article` |
| DB (Cassandra) | `community.articles` (含 `is_top` 欄位) |
| MeiliSearch | `community` 索引 (含 `is_top` 欄位) |
| Redis | 無使用（community 無 Redis 快取） |
| 規則 | README: 需要驗證 (✅) |
| 規則 | communityservice-detail: community 無 Redis 快取 |