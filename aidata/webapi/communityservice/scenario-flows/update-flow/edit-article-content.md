# 編輯文章內容

## 1. 場景目的

讓已發佈文章的作者能夠編輯其文章的純文字內容。此流程確保僅有原作者或具備管理權限的使用者可以修改，並同步更新 Cassandra 持久化儲存與 MeiliSearch 搜尋索引，以維持資料一致性。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/community/{game_type}/edit_articles` | 編輯指定 `game_type` 下的文章內容。請求體為 JSON，包含文章 ID 與新的文字內容。 |

---

## 3. 流程總覽

1. 接收包含文章 ID 與新內容的 PUT 請求。
2. 透過 auth 中介層（middleware）驗證請求中的 auth token，取得操作者 authkey。
3. 根據提供的文章 ID，從 Cassandra `community.articles` 資料表查出文章原文。
4. 驗證文章是否存在，以及操作者是否為原作者或後台管理員。
5. 驗證操作者是否處於禁言（mute）狀態。
6. 檢查編輯內容是否符合規範（如長度限制）。
7. 更新 Cassandra `community.articles` 資料表中的文章內容與編輯時間。
8. 同步更新 MeiliSearch `community` 索引中對應的文件。
9. 回傳更新後的文章資料。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware | `auth.login_required` | 驗證 request header 中的 token，取得 `authkey` 與 `account`。 |
| 2 | Controller | `ArticleController.edit_article` | 解析請求參數，取得 `article_id` 與 `content`。 |
| 3 | Service | `ArticleService.edit_article` | 調用 repository 查詢文章，進行權限、狀態與內容驗證。 |
| 4 | Provider | `ArticleRepository.get_article_by_id` | 從 Cassandra `community.articles` 查詢指定文章資料。 |
| 5 | Service | `ArticleService.edit_article` | 確認 `article.account == current_account` 或有後台權限。 |
| 6 | Service | `MuteService.check_mute_status` | 查詢 Cassandra `community.mute` 表，確認操作者未被禁言。 |
| 7 | Provider | `ArticleRepository.update_article` | 更新 Cassandra 中文章的 `content`、`edit_timestamp` 欄位。 |
| 8 | Provider | `MeiliSearchProvider.update_document` | 將更新後的文章資料（主體與內容）同步至 MeiliSearch `community` 索引。 |
| 9 | Controller | `ArticleController.edit_article` | 格式化並回傳更新後的文章。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `community.articles` | Read | 查詢原始文章以驗證作者與存在性。 |
| DB (Cassandra) | `community.articles` | Write | 更新文章的 `content` 與 `edit_timestamp` 欄位。 |
| DB (Cassandra) | `community.mute` | Read | 檢查操作者是否在禁言名單中。 |
| Search Index | MeiliSearch `community` | Partial Update | 同步更新文章在搜尋索引中的最新內容。 |
| Cache (Redis) | 無 | 無 | 根據 `communityservice-detail.md`，community 服務未使用 Redis 快取。 |

---

## 6. 重要規則

- **權限限制**：僅文章原作者或具備管理權限（如 `admin`）的使用者可以編輯文章。不可由第三方任意修改。
- **欄位限制**：
    - 僅允許編輯文字內容（`content`），不包含圖片或預測單。編輯圖片有專門的圖片上傳流程。
    - 內容長度必須符合限制（需人工確認確切字元上限）。
- **不可暴露資料**：更新後的回應中，`account` 等個資欄位需依規則遮蔽。
- **Mute 規則**：被禁言的使用者不可編輯文章，請求應被拒絕。
- **不可修改欄位**：文章的 `id`、`account`、`create_timestamp` 等關鍵欄位不可被修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 文章不存在 | 回傳 HTTP 404 Not Found。 |
| 操作者不是文章作者且非管理員 | 回傳 HTTP 403 Forbidden，並附帶權限不足的訊息。 |
| 操作者處於禁言狀態 | 回傳 HTTP 403 Forbidden，並附帶禁言提示。 |
| 編輯內容為空或超出長度限制 | 回傳 HTTP 422 Unprocessable Entity，附帶欄位驗證失敗訊息。 |
| Cassandra 寫入失敗或 timeout | 回傳 HTTP 500 Internal Server Error，不應更新 MeiliSearch。 |
| MeiliSearch 同步失敗 | **高風險**：Cassandra 已更新但索引未同步，會導致資料不一致。應記錄錯誤日誌並發送警報。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-EDIT-01 | API Test | 原作者編輯自己的文章，提供有效內容。 | HTTP 200，文章內容已更新。 |
| UT-EDIT-02 | Permission Test | 非作者且非管理員嘗試編輯文章。 | HTTP 403，內容未被修改。 |
| UT-EDIT-03 | Permission Test | 處於禁言狀態的作者嘗試編輯文章。 | HTTP 403，內容未被修改。 |
| UT-EDIT-04 | API Test | 發送不存在的文章 ID 進行編輯。 | HTTP 404。 |
| UT-EDIT-05 | Flow Test | 成功編輯文章後，查詢文章列表或搜尋。 | 查詢結果應顯示更新後的內容。 |
| UT-EDIT-06 | Flow Test | 編輯內容包含特殊字元或 Emoji。 | 成功編輯並正確顯示。 |

---

## 9. 高風險區域

- **高風險 Table**：
    - `community.articles`：核心文章資料，錯誤的寫入會直接影響使用者。
    - `community.mute`：若檢查邏輯有誤，可能導致禁言失效。
- **跨服務資料同步**：
    - **Cassandra 與 MeiliSearch 的一致性**：若 Cassandra 更新成功後 MeiliSearch 更新失敗，會導致搜尋結果與實際文章內容不符。這是本流程最大的風險點。
- **Cache consistency**：community 服務無 Redis 快取，因此沒有快取不一致的風險。
- **Queue retry**：未使用 Queue 處理此同步流程，若 MeiliSearch 更新失敗，無自動重試機制，需依靠日誌與監控處理。

---

## 10. 常見錯誤

- **新人/ AI 容易犯錯**：
    - 誤將「編輯文章內容」當作「編輯文章”（`edit_predict`）」，進而混淆業務邏輯。
    - 忘記在編輯後同步更新 MeiliSearch 索引，導致資料不一致。
    - 直接從 request body 取得 `account` 作為作者，而不是從已驗證的 session/token 中獲取，造成權限繞過漏洞。
    - 在更新 Cassandra 時，覆蓋了不應該變更的欄位，如 `id` 或 `account`。
- **常見漏檢查項目**：
    - 忘記檢查操作者是否被禁言。
    - 忘記驗證文章是否存在。
    - 內容長度未進行後端驗證，僅依靠前端限制。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `PUT /api/community/{game_type}/edit_articles` (OpenAPI) |
| DB | `community.articles` (README / community-detail.md) |
| DB | `community.mute` (相關 API 路由推斷) |
| Index | MeiliSearch `community` (README) |
| Code | `ArticleController.edit_article` (code semantics 推斷) |
| Code | `ArticleService.edit_article` (code semantics 推斷) |
| Rule | 僅作者或管理員可編輯 (`communityservice-detail.md`) |
| Rule | 無 Redis 快取 (`communityservice-detail.md`) |