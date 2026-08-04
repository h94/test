# 查詢單篇文章

## 1. 場景目的

讓已驗證的使用者根據文章 ID 查詢指定體育社群文章的所有詳細內容（包含作者、圖片、內容、競猜、HashTag、按讚數等），用於前端文章內頁或後台審核查詢。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/community/{game_type}/articles/{article_id}` | 查詢單篇文章 |

**需要驗證**：✅（需帶入有效的 authkey，由 member service / auth 驗證後取得）。

---

## 3. 流程總覽

1. 接收請求：`game_type`（路徑參數）、`article_id`（路徑參數）、authkey（Header／驗證層注入）。
2. 驗證 `game_type` 非空、`article_id` 非空。
3. 呼叫對應 Controller → Service → Provider 查詢文章。
4. 從 Cassandra `community.articles` 表讀取文章主體（含作者、內容、圖片、競猜資訊、HashTag 等）。
5. 併行查詢 MeiliSearch 按讚索引（`like`），取得該文章的按讚總數與當前使用者是否已按讚。
6. 對敏感欄位（如 `authkey`）進行遮蔽或轉換為顯示名稱（需透過 member service 或內部邏輯，但 db-usage 指明 communityservice 僅遮蔽，不轉譯）。
7. 回傳文章完整內容（含按讚數、作者顯示名稱、圖片 URL、HashTag、是否已編輯等）。

> **需人工確認**：按讚數是否由 MeiliSearch `like` 索引提供，還是另有其他查詢邏輯。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Validator | 路徑參數校驗 | 驗證 `game_type`、`article_id` 非空且格式適當 |
| 2 | Controller | ArticleController.GetArticle | 接收 request，呼叫 Service |
| 3 | Service | ArticleService.GetArticleById | 組合查詢邏輯，處理遮蔽與回應格式 |
| 4 | Provider | ArticleProvider（或直接 Cassandra Accessor） | 執行 Cassandra CQL 查詢 `articles` 表 |
| 5 | Provider | MeiliSearchAccessor（或 LikeProvider） | 查詢 MeiliSearch `like` 索引取得按讚狀態與總數 |
| 6 | Service | ArticleService.GetArticleById | 合併文章＋按讚資料、遮蔽敏感欄位 |
| 7 | Controller | ArticleController.GetArticle | 回傳 JSON response |

> **需人工確認**：實際 Controller / Service / Provider class 名稱可能為 `ArticleApi`、`ArticleService`、`CommunityArticleProvider` 等，此處基於 Python Flask 慣例推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `community.articles` | Read（SELECT WHERE `id` = article_id） | 取得文章主體內容 |
| MeiliSearch | 索引 `like` | Read（filter by `content_id` = article_id AND `user` = current user） | 取得按讚總數與使用者是否已按讚 |
| Redis | 無使用 | — | 依 README：community 無 Redis 快取 |
| Queue / Kafka | 無使用 | — | 查詢流程不涉及異步處理或日誌 |

---

## 6. 重要規則

- **權限限制**：任何已登入會員皆可查詢已發布的公開文章；隱藏文章或 VIP 限定文章查詢規則需依 `db-usage` 決定是否過濾。
- **欄位不可暴露**：
  - `authkey`（或內部的 `user` 欄位）：回傳時須遮蔽，僅保留或顯示為使用者暱稱（依 `db-usage community` 一節：`user` 不可直接回傳）。
  - 若要顯示作者名稱，應回傳 `username`（來自 member table）或遮蔽後的帳號，不可回傳 authkey。
- **按讚狀態**：若查詢時需要得知「當前使用者是否已按讚」，應以 MeiliSearch 的 `like` 索引過濾 `content_id`＋`user`，存在即為已按讚。
- **找不到文章時**：OpenAPI schema 標註「找不到時可能回傳空物件」，應由前端判斷；服務端應回傳 200 而非 404。
- **無 Transaction 需求**：查詢為唯讀，不涉及 Transaction。
- **無 TTL、Retry 規則**：查詢為即時讀取，不適用快取或重試。

> **需人工確認**：`articles` 表是否有 `status` 或 `enabled` 欄位，用以辨別文章是否已刪除／隱藏。若存在，則查詢應過濾已刪除文章。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| `article_id` 不存在 | 回傳空物件（`{}`）或 null，HTTP 200 |
| `game_type` 無效 | 回傳 422 或參數錯誤 |
| 使用者未登入（未帶 auth） | 回傳 401 Unauthorized |
| Cassandra 讀取超時 | 回傳 500 錯誤，記錄 Kafka 日誌 |
| MeiliSearch 查詢失敗（連線中斷） | 按讚相關欄位回傳 0 或 null，文章主體仍回傳（graceful degradation）；應記錄錯誤日誌 |
| 文章被標記為刪除／隱藏（若存在） | 不應回傳內容，可能回傳特定狀態或空物件 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| QS-1 | API Test | 提供有效的 `game_type` 與已存在的 `article_id` | 回傳完整文章，按讚數正確 |
| QS-2 | API Test | 提供從未按讚的使用者查詢文章 | `is_liked` 為 false，`like_count` 正確 |
| QS-3 | API Test | 提供已按讚的使用者查詢文章 | `is_liked` 為 true，`like_count` 包含自身 |
| QS-4 | Error Test | 提供不存在的 `article_id` | 回傳空物件或 null，HTTP 200 |
| QS-5 | Permission Test | 未驗證請求（無 auth header） | HTTP 401 |
| QS-6 | Integration Test | MeiliSearch 無法連線時 | 按讚數顯示 0 或 null，文章內容正常回傳 |
| QS-7 | Flow Test | 文章包含競猜預測內容 | 競猜選項、預測資訊正確呈現 |

---

## 9. 高風險區域

- **敏感資料洩漏**：若未遮蔽 `authkey` 或 `account` 欄位，將導致個資外洩。
- **MeiliSearch 相依**：若 MeiliSearch 服務中斷，按讚數顯示不正確，可能影響使用者體驗，需透過監控告警。
- **Cassandra 讀取延遲**：大型文章或跨分區查詢可能導致延遲（尤其當文章包含大量 HashTag 或內嵌圖片）。
- **無快取**：高頻查詢的文章可能造成 Cassandra 壓力，後續可考慮引入 CDN 或 Redis 快取（但目前無 Redis）。

---

## 10. 常見錯誤

- ❌ **回傳 authkey**：在 response 中未遮蔽或過濾 `authkey` / `user` 欄位。
- ❌ **未查詢按讚索引**：只從 Cassandra 讀取文章，但遺漏按讚數或按讚狀態，導致前端顯示錯誤。
- ❌ **當文章不存在時回傳 404**：OpenAPI 明確標記可能回傳空物件，應避免使用 404。
- ❌ **未處理 MeiliSearch 容錯**：若 MeiliSearch 查詢拋出例外，直接回傳 500 中斷整個請求。
- ❌ **忽略已刪除／隱藏文章過濾**：若 `articles` 表有 `deleted` 或 `status` 欄位，未過濾可能回傳不應顯示的內容。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | README 體育社群文章 API 列表：GET `/api/community/{game_type}/articles/{id}` |
| 需要驗證 | README 該路由標記 ✅ |
| OpenAPI 回傳格式 | OpenAPI paths: `/api/community/{game_type}/articles/{article_id}` → responses 200 → ArticleDocumentResponse |
| DB 儲存 | README 表格：Cassandra community.articles |
| MeiliSearch 按讚索引 | README 表格：MeiliSearch like 索引，依 `content_id`、`user` 篩選 |
| 不可回傳 authkey | `community-detail.md`：所有表之 `user`（authkey）對外部 API 不可直接回傳 |
| 無 Redis 快取 | `communityservice-detail.md` Redis 段落：community 無使用 Redis 快取 |