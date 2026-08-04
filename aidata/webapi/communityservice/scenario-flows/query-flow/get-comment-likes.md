# 查詢留言按讚

## 1. 場景目的

提供已登入用戶查詢指定留言的按讚資訊，取得點讚該留言的用戶清單，以及當前登入者是否已點讚該留言。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/community/{game_type}/comments/{id}/likes` | 查詢指定留言按讚 |

> ⚠️ **需人工確認**：當前 OpenAPI 片段未包含此路由的完整定義，以上路由來源為 README 中的 API 路由表。

---

## 3. 流程總覽

1. 接收 GET request，解析 `game_type`（球種類型）與 `id`（留言 ID）
2. 由上游 auth service 驗證 authkey，communityservice 僅接收已驗證的 authkey
3. 從 MeiliSearch「`like`」索引中查詢該留言所有按讚記錄，過濾條件為 `content_id = {comment_id}` 且 `content_type = 'comment'`
4. 從 MeiliSearch 查詢當前使用者（依 authkey 對應的 account）是否已對該留言按讚
5. 組合回傳結果：按讚使用者清單與當前使用者的按讚狀態
6. 對按讚使用者清單中的 `account` 欄位進行遮蔽處理
7. 回傳結果

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|------|---------------|------|
| 1 | Controller | LikeController | 接收 route parameter `game_type`、`comment_id`，傳入 Service |
| 2 | Service | LikeService | 組合查詢條件，調用 MeiliSearch Provider |
| 3 | Provider | MeiliSearchProvider | 查詢 MeiliSearch `like` 索引：`content_id={comment_id} AND content_type=comment` |
| 4 | Provider | MeiliSearchProvider | 查詢當前使用者是否有 `content_id={comment_id}` 的按讚記錄 |
| 5 | Service | LikeService | 遮蔽清單中非本人的 `account` 欄位 |
| 6 | Service | LikeService | 組合 response，標記當前使用者是否已按讚 |
| 7 | Controller | LikeController | 回傳 JSON response |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| MeiliSearch | `like` 索引 | Read | 查詢指定留言 ID 的所有按讚記錄 |
| MeiliSearch | `like` 索引 | Read | 查詢當前使用者是否對該留言按讚 |

> **注意**：communityservice 為 **無 Redis 快取** 服務（依 `communityservice-detail.md` 中 Redis 章節確認），此場景所有查詢直接走 MeiliSearch。

---

## 6. 重要規則

- **權限限制**：需通過上游 auth service 驗證（`Authorization` header），communityservice 僅接收已驗證的 authkey
- **帳號遮蔽**：按讚使用者清單中，`account` 欄位必須遮蔽處理（如 `name***`），不可回傳完整帳號（依 `communityservice-detail.md` 不可回傳欄位規範）
- **非本人不可暴露完整帳號**：僅當前使用者區塊可標記「是否已按讚」，清單中其他使用者帳號一律遮蔽
- **留言與文章按讚共用索引**：查詢時必須過濾 `content_type = 'comment'`，避免回傳文章按讚記錄
- **需人工確認**：MeiliSearch `like` 索引的實際欄位結構（如 `content_type` 欄位是否存在）若與文件所述不符，需以實際 schema 為準

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 留言 ID 不存在（MeiliSearch 無對應記錄） | 回傳空清單，當前使用者未按讚 |
| authkey 無效或過期 | 回傳 401 Unauthorized（由 auth service 攔截） |
| MeiliSearch 查詢逾時或不可用 | 回傳 503 Service Unavailable |
| 缺少必要 path parameter | 回傳 422 Unprocessable Entity |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| T1 | API Test | 查詢已有人按讚的留言 | 回傳按讚清單，account 遮蔽正確 |
| T2 | API Test | 查詢無人按讚的留言 | 回傳空清單，已按讚=false |
| T3 | Permission Test | 未帶 authkey 查詢 | 回傳 401 |
| T4 | Flow Test | 當前使用者已按讚該留言 | 回傳按讚清單，自身記錄顯示已按讚=true |
| T5 | Flow Test | 當前使用者未按讚該留言 | 回傳按讚清單，自身記錄顯示已按讚=false |

---

## 9. 高風險區域

- **帳號隱私外洩**：未遮蔽清單中其他使用者 `account`，直接回傳完整帳號（違反個資保護）
- **內容類型混淆**：未過濾 `content_type`，文章按讚與留言按讚混淆顯示
- **MeiliSearch 效能**：無 Redis 快取，高流量下直接查詢 MeiliSearch 可能造成延遲
- **無降級機制**：MeiliSearch 不可用時僅能回傳錯誤，無 cache fallback

---

## 10. 常見錯誤

- ❌ 回傳完整 `account` 欄位給前台 → ✅ 應統一遮蔽非本人的帳號
- ❌ 未過濾 `content_type`，將文章按讚也當作留言按讚回傳 → ✅ 查詢時必須包含 `content_type=comment` 條件
- ❌ 誤用 Cassandra `comments` 表查詢按讚 → ✅ 按讚資料僅存在 MeiliSearch `like` 索引中
- ❌ 忘記檢查 authkey，導致未登入用戶也可查詢 → ✅ 所有 API 需依賴 auth service 驗證

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README 路由表：`GET /api/community/{game_type}/comments/{id}/likes` |
| 技術棧 | README 技術棧：MeiliSearch 作為主要查詢引擎 |
| DB | communityservice-detail.md：community 無使用 Redis 快取 |
| 不可回傳欄位 | communityservice-detail.md：account 對外 API 一律遮蔽 |
| 索引 | README：MeiliSearch `like` 按讚搜尋索引，依 content_id、user 篩選 |