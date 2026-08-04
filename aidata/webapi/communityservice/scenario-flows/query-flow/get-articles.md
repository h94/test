# 查詢文章列表

## 1. 場景目的
供已登入的會員在體育社群前台，依遊戲類型(game_type)、聯賽、會員等級等條件進行全文檢索與篩選，並取得分頁的文章列表。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/community/{game_type}/articles` | 查詢文章列表 |

**參數**：
- `game_type` (Path): 球種，如 `basketball`。
- `index` (Query): 發文時間戳，用於分頁。
- `page` (Query): 頁數索引。
- `show_hidden` (Query): 是否顯示隱藏文章 (需本人或管理員)。
- `leagues` (Query): 聯賽過濾條件。
- `articTopics` (Query): 文章類型過濾。
- `memberShips` (Query): 使用者會員等級過濾。

**驗證**：✅ 需要驗證 (從 auth header 取得 `authKey`)。

---

## 3. 流程總覽

1.  Gateway 驗證請求的 authKey 是否有效，無效則拒絕。
2.  Controller 接收請求，從 auth header 解析使用者身份 (authKey)。
3.  呼叫 Service 層，根據請求的 `game_type` 決定查詢的 MeiliSearch 索引 (Index)。
4.  Service 層透過 `authKey` 取得請求者的會員資訊 (等級) 以用於後續過濾。
5.  Service 層將請求參數 (聯賽, 會員等級, 隱藏狀態等) 組合成 MeiliSearch 的查詢過濾條件 (`filter`)。
6.  呼叫 MeiliSearch Provider 執行查詢。
7.  取得 MeiliSearch 回傳的搜尋結果。
8.  將搜尋結果組裝成回應的格式，對敏感欄位 (如 `account`) 進行遮蔽處理。
9.  回傳分頁後的文章列表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware | `AuthMiddleware` | 驗證 authKey，解析使用者資訊注入 `g` 物件。 |
| 2 | Controller | `ArticleController.GetArticles` | 接收請求，提取 `game_type`, `leagues`, `memberShips` 等參數。 |
| 3 | Service | `ArticleService.search_articles` | 組合查詢條件：呼叫內部方法取得請求者等級，並依據 `show_hidden` 決定是否過濾隱藏文章。 |
| 4 | Service | `ArticleService.search_articles` | 將 `leagues` 轉換為 `league IN [...]` 的 filter；將 `memberShips` 轉換為 `membership_level IN [...]` 的 filter。 |
| 5 | Provider | `MeiliSearchProvider.search` | 調用 MeiliSearch Python SDK，對 `community` 索引進行 `search`。 |
| 6 | Service | `ArticleService.search_articles` | 處理 MeiliSearch 回傳的 `hits`，格式轉換。 |
| 7 | Service | `ArticleService.search_articles` | 進行帳號遮蔽：`account` 欄位遮罩為 `name***`。 ➡️ *Evidence: community-detail.md* |
| 8 | Controller | `ArticleController.GetArticles` | 回傳 `ArticleListPageResponse` JSON。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Search | MeiliSearch `community` index | Read | 全文搜尋與條件篩選文章主資料。 |
| DB | `member.gameusers` | Read | 取得請求者的 `rank` 或 `memberships` 以判斷會員等級。 |
| Queue | 無使用 | - | 此場景為查詢，無寫入或非同步操作。 |

**⚠️ 注意**：根據 `communityservice-detail.md`，社群模組 **無 Redis 快取**，所有查詢直接命中 MeiliSearch。

---

## 6. 重要規則

- **權限限制**：所有請求都必須通過 `authKey` 驗證，未登入使用者無法存取。 ➡️ *Evidence: README.md 的「需要驗證」欄位*
- **不可暴露資料**：文章列表中的 `account` 欄位，對於非作者本人的請求，必須進行遮蔽處理 (`name***`)。 ➡️ *Evidence: community-detail.md*
- **狀態值限制**：`show_hidden` 選項僅允許作者本人或管理員查看被隱藏的文章，Service 層會根據請求者身份和參數決定是否過濾。
- **會員等級過濾**：若請求中帶有 `memberShips` 參數，服務會根據請求者自己的等級來過濾，**不是**讓使用者看到所有等級的文章。 ➡️ **需人工確認**：此處業務邏輯是「僅顯示符合指定等級的文章」還是「僅顯示該使用者同等級的文章」，待確認。
- **不可憑空猜測**：未提供 `leagues` 或 `memberShips` 時，視為不進行該項過濾。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求未帶 auth header 或 authKey 無效 | 回傳 HTTP 401 Unauthorized。 |
| `game_type` 不存在或為空 | 回傳 HTTP 422 Unprocessable Entity。 |
| `index` 或 `page` 格式錯誤 (非數字) | 回傳 HTTP 422 Unprocessable Entity。 |
| MeiliSearch 服務無法連接 | 回傳 HTTP 500 Internal Server Error，並記錄錯誤日誌。 |
| 查詢條件無匹配結果 | 回傳 HTTP 200，包含空的文章列表與分頁資訊。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC_QL_01 | Integration | 不帶任何過濾條件，查詢預設文章列表。 | 成功回傳第一頁文章，按熱門分數或時間倒序。 |
| TC_QL_02 | API | 帶有 `leagues=NBA` 條件查詢。 | 只回傳聯賽為 NBA 的文章。 |
| TC_QL_03 | Permission | 請求 `show_hidden=true`。 | 非作者/管理員時，不回傳隱藏文章；作者本人則回傳。 |
| TC_QL_04 | API | 請求 `page=2` 進行翻頁。 | 成功回傳第二頁，且內容與第一頁不重複。 |
| TC_QL_05 | Flow Test | 對文章列表中的 `account` 進行檢查。 | 非作者本人的文章，帳號已遮蔽為 `name***`。 |

---

## 9. 高風險區域

- **MeiliSearch 索引一致性**：文章寫入 Cassandra 後再寫入 MeiliSearch 有一個微小時間差。若查詢在此之間發生，可能暫時看不到新文章。這是一個最終一致性的設計。
- **查詢效能**：全文檢索搭配多個複合篩選條件可能對 MeiliSearch 造成壓力，特別是 `articleTopics` 或 `leagues` 等低基數欄位。需確保 MeiliSearch 的 `filterableAttributes` 有正確設定。 ➡️ *需確認 MeiliSearch 索引設定*
- **會員等級取得**：每次查詢都需要從 `member.gameusers` 取得請求者等級，高併發時可能對 Cassnadra 造成讀取壓力，但社群業務尚無快取，需監控。

---

## 10. 常見錯誤

- ❌ 前端未處理 `account` 遮罩，直接顯示原始帳號。 → ✅ 後端已處理遮蔽，前端可直接顯示。
- ❌ 前端請求 `show_hidden=true`，預期能看到別人的隱藏文章。 → ✅ 這是後端權限問題，非作者請求會自動忽略此參數，只回傳公開文章。
- ❌ AI 誤解 `memberShips` 參數是用來「查詢」特定等級的文章。 → ✅ 根據參數語意，更像是「以特定身份」瀏覽，需與人工確認確切邏輯。
- ❌ 漏檢查 `game_type` 參數的有效性，導致對 MeiliSearch 的查詢失敗。 → ✅ Controller 層應有參數校驗，阻擋非法輸入。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI spec: `/api/community/{game_type}/articles` |
| Search Engine | README.md: 「MeiliSearch 作為主要查詢引擎」 |
| DB Usage | communityservice-detail.md: community 無 Redis 快取 |
| Account Masking Rule | community-detail.md: 「account 欄位須遮蔽」 |
| Auth Requirement | README.md API 表格: GET /api/community/{game_type}/articles 需要驗證 |