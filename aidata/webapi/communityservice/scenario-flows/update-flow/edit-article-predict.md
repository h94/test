# 編輯文章競猜內容

## 1. 場景目的

允許文章作者修改已發佈文章的競猜相關設定，例如預測選項或競猜內容。此操作僅變更文章中的競猜區塊，不影響文章其他內容。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/community/{game_type}/edit_predict` | 編輯文章競猜內容 |

- **需驗證**：是（authkey 由上游 auth/member service 驗證後傳入）
- **Content-Type**：`application/json`
- **Request Body Schema**：`EditPredictArgs`

---

## 3. 流程總覽

1. 接收編輯競猜 request，包含 `game_type` 路徑參數與 JSON body
2. 由 auth/member service 驗證 authkey（communityservice 不自行驗證）
3. 解析 `EditPredictArgs`，取得文章 `id` 與更新後的 `predict` 內容
4. 查詢 Cassandra `community.articles`（需人工確認：articles 表結構未包含在此次 DB schema 中，但 README 與 API 路由定義明確提及）
5. 驗證文章存在性與作者身份（`author` 須等於目前登入使用者）
6. 更新該文章的 `predict` 欄位
7. 將更新後的內容同步至 MeiliSearch `community` 索引
8. 回傳更新後的文章文件

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `ArticleController.edit_predict` | 接收 request，提取 `game_type` 與 JSON body，呼叫 Service |
| 2 | Validator | `EditPredictArgs` (schema) | 驗證 `id`（必填，字串）與 `predict`（必填，結構由業務定義） |
| 3 | Service | `ArticleService.edit_predict` | 依 `article_id` 查詢文章；檢查作者身份；執行更新邏輯 |
| 4 | Provider | `ArticleProvider.update_predict` | 對 Cassandra 執行 UPDATE 操作（寫入 `predict` 欄位） |
| 5 | Provider | `MeiliSearchProvider.update_article` | 將更新後的文章文件同步至 MeiliSearch `community` 索引 |
| 6 | Transfer | `ArticleTransfer.to_response` | 將 DB 層回傳的文章物件轉換為 `ArticleDocumentResponse` 格式 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `community.articles` | Read | 查詢文章存在性與作者身份 |
| DB | Cassandra `community.articles` | Write | 更新文章的 `predict` 欄位 |
| Index | MeiliSearch `community` | Write | 同步更新後的競猜內容至全文檢索索引 |
| Queue | 無 | - | 此流程未使用 Kafka / Queue |
| Cache | 無 (Redis) | - | **community 無 Redis 快取**（證據：`communityservice-detail.md`） |

---

## 6. 重要規則

- **權限限制**：僅文章原作者可編輯競猜內容；authkey 與文章建立者 `author` 欄位必須匹配
- **欄位限制**：`predict` 為必填，格式需符合 `EditPredictArgs` schema 定義（需人工確認：predict 的具體結構，如是否為 `betpool_games.id` 的引用或其他自訂格式）
- **不可修改欄位**：`id`、`author`、`create_timestamp` 等文章核心欄位不可透過此 API 變更
- **搜索同步**：更新後必須即時同步至 MeiliSearch，確保全體使用者查詢時取得最新競猜內容
- **Transaction 規則**：無分散式交易；Cassandra 寫入成功後才更新 MeiliSearch（先 DB 後 Index，若 Index 寫入失敗需記錄錯誤 log 但不影響主流程回應，或依業務規則決定是否 rollback）
- **狀態限制**：需人工確認——已結算或已過期的競猜文章是否允許編輯？推測應禁止，但未在現有文件中明確定義

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| authkey 無效或遺失 | 由上游 auth service 拒絕，回傳 401 Unauthorized |
| `game_type` 不支援 | 回傳 422 Unprocessable Entity（路徑參數驗證失敗） |
| `id` 對應的文章不存在 | 回傳 404 Not Found（OpenAPI 標記「文章不存在 404」） |
| 目前使用者非文章作者 | 回傳 403 Forbidden 或業務錯誤碼（需人工確認：實際實作的回應格式） |
| `predict` 欄位格式錯誤 | 回傳 422 Unprocessable Entity（schema 驗證失敗） |
| Cassandra 寫入失敗 | 回傳 500 Internal Server Error，需記錄錯誤 log |
| MeiliSearch 同步失敗 | 可能回傳 200 但記錄 error log（最終一致性）；或回傳 500（需人工確認：目前實作策略） |
| 文章已刪除（status=deleted） | 回傳 404 或 400（不可編輯已刪除文章） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| TC-EP-01 | API Test | 以作者身份正常更新 `predict` 內容 | 回傳 200，內容更新成功，MeiliSearch 查詢可見新競猜 |
| TC-EP-02 | Permission Test | 以非作者身份嘗試更新 | 回傳 403 或對應權限錯誤 |
| TC-EP-03 | API Test | 傳入不存在的文章 `id` | 回傳 404 |
| TC-EP-04 | Validation Test | `predict` 欄位為空或不合法格式 | 回傳 422 |
| TC-EP-05 | Flow Test | 更新後立即查詢文章（GET by id） | 回傳的 `predict` 為更新後內容 |
| TC-EP-06 | Flow Test | 更新後透過搜尋 API 查詢 | MeiliSearch 索引中的文章競猜內容已更新 |
| TC-EP-07 | Integration Test | Cassandra 可用但 MeiliSearch 不可用 | 確認服務回應策略（200 or 500）及 log 記錄 |

---

## 9. 高風險區域

- **高風險 table**：`community.articles`（直接寫入競猜欄位可能影響已結算遊戲的公平性，需確認是否應禁止對已開獎或已派彩遊戲的競猜文章編輯）
- **跨服務資料同步**：Cassandra ↔ MeiliSearch 非交易性同步，若 Index 寫入失敗可能造成搜尋結果與實際內容不一致
- **Cache consistency**：無 Redis 快取，風險較低；但需確認是否有其他服務層級的快取（如 MeiliSearch 本身的內部 cache）
- **Idempotency**：此 API 為冪等操作（多次呼叫相同 request，結果一致），但仍需注意重複更新時的 MeiliSearch 同步壓力

---

## 10. 常見錯誤

- ❌ **未驗證作者身份**：任何使用者皆可編輯他人文章的競猜內容 → 應嚴格比對 `authkey` 對應的 `account` 與文章的 `author` 欄位
- ❌ **更新後未同步 MeiliSearch**：導致搜尋與文章詳情不一致 → 必須於每次成功更新後觸發 Index 更新
- ❌ **對已結算競猜文章仍允許編輯**：可能破壞競猜公平性 → 需在 Service 層加入遊戲狀態檢查（需人工確認：predict 是否關聯 `betpool_games.status`）
- ❌ **`predict` 欄位允許任意結構輸入**：可能儲存非法或惡意資料 → 必須透過 schema 嚴格驗證格式與型別

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI: `PUT /api/community/{game_type}/edit_predict` |
| API 說明 | README: 「編輯文章競猜內容」 |
| DB 表 | README: `community.articles`（Cassandra） |
| 索引 | README: MeiliSearch `community` 索引 |
| 無 Redis | `communityservice-detail.md`：「community 無使用 Redis 快取」 |
| 權限模型 | `communityservice-detail.md`：使用者帳號認證由 auth/member service 處理 |
| 404 情境 | OpenAPI: summary 標記「文章不存在 404」 |
| 請求結構 | OpenAPI: `EditPredictArgs` schema |

---

## 12. 需人工確認

- `community.articles` 的完整 schema（包含 `predict` 欄位的型別與格式）
- `predict` 欄位的具體結構定義（是否引用 `betpool_games.id`、`betoptions` 等）
- 已結算競猜文章是否禁止編輯的業務規則
- MeiliSearch 同步失敗時的回應策略（最終一致性 vs 強制 rollback）
- API 回應中是否包含 MeiliSearch 同步狀態或僅回傳 Cassandra 寫入結果