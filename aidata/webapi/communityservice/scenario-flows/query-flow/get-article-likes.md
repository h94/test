# 查詢文章按讚

## 1. 場景目的
允許已登入的使用者查詢指定社群文章的按讚資訊（包含按讚者列表、按讚總數），以展示社群互動狀態。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/community/{game_type}/articles/{id}/likes` | 查詢文章按讚，需驗證 |

- `game_type`：球種代碼（路徑參數，必填）
- `id`：文章 ID（路徑參數，必填）

---

## 3. 流程總覽

1. 前端（或內部服務）發起 GET 請求，攜帶已驗證的 authkey（由上游 auth/member service 注入請求 context）
2. communityservice 接收請求，解析 `game_type` 與文章 `id`
3. 呼叫 MeiliSearch 的 `like` 索引進行搜尋，過濾條件：
   - `content_id` 等於 `id`
   - `content_type` 等於 `article`（或依慣例可省略，僅依內容 ID 查詢）
4. 取得按讚記錄清單（字段可能包含 `user`、`create_timestamp`）
5. 對每個按讚者的 `user` 欄位進行帳號遮蔽（例如 `name***`）
6. 回傳遮蔽後的按讚列表與總數

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `LikesController.get_article_likes`（推測） | 接收 GET 請求，取出 path 參數，呼叫 Service |
| 2 | Service | `LikeService.get_likes_by_article(game_type, article_id)` | 組合 MeiliSearch 查詢條件，呼叫 Provider |
| 3 | Provider | `LikeSearchProvider.search(content_id, content_type)` | 對 MeiliSearch `like` 索引執行 search，回傳原始紀錄 |
| 4 | Transfer | `LikeTransfer.to_response(records)` | 遮蔽 `user` 欄位，轉換為 API 回傳格式 |
| 5 | Controller | 同上 | 封裝 JSON response 回傳 |

> 實際 Layer 名稱需依程式碼證據，此處基於 Flask 專案常見結構推測。若原始程式無 Transfer 層，可能直接於 Service 中處理遮蔽。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| MeiliSearch | `like` 索引 | 讀取（search） | 查詢指定文章的按讚紀錄，篩選 `content_id={article_id}` |
| Redis | 無使用 | - | community 服務在按讚場景未使用 Redis（依 community-detail 描述） |
| Kafka | 無使用 | - | 日誌傳送為常規行為，非流程必要 |
| Cassandra | 無使用 | - | 按讚紀錄僅存於 MeiliSearch，不經過 Cassandra |

---

## 6. 重要規則

- **權限限制**：API 需已驗證（authkey 有效）。communityservice 不自行驗證，依賴上游 auth service 過濾非法請求。
- **帳號遮蔽**：回傳的按讚者帳號（`user` 欄位）必須遮蔽處理，僅顯示部分內容（如 `name***`），不可直接回傳完整帳號（依 `community-detail.md` 對討論串/留言的帳號遮蔽要求推廣至此）。
- **過濾條件**：必須嚴格以 `content_id` 等於文章 ID 查詢，不可跨文章取得其他按讚資料。
- **無 TTL**：MeiliSearch 索引為永久保存，無過期清理機制。
- **無 Transaction**：僅對 MeiliSearch 進行唯讀，無跨資料來源一致性問題。
- **無 Retry 規則**：若 MeiliSearch 暫時不可用，由前端或呼叫端決定是否重試。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 文章 ID 不存在（在 MeiliSearch 中無任何按讚記錄） | 回傳空列表，HTTP 200 |
| authkey 無效或未提供 | 由上游 auth service 攔截，回傳 401/403；communityservice 不會收到此請求 |
| MeiliSearch 連線失敗 | 回傳 HTTP 500 或自定義錯誤碼，並記錄日誌 |
| 傳入的 `game_type` 不存在該球種 | 不影響按讚查詢（因查詢以文章 ID 為主，`game_type` 僅用於路由），可正常回傳；實務上應驗證 game_type 與文章所屬球種一致，若不一致可考慮回傳空列表或錯誤（需人工確認業務規則） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| LK-GET-01 | API Test | 提供有效 authkey 與存在文章 ID，該文章有按讚記錄 | 回傳 200，內含遮蔽帳號的按讚列表 |
| LK-GET-02 | API Test | 提供有效 authkey，文章存在但無任何人按讚 | 回傳 200，空列表 |
| LK-GET-03 | Permission Test | 無 authkey 請求 | 回傳 401（由 auth filter 攔截） |
| LK-GET-04 | Field Masking | 確認回傳的 `user` 欄位不包含完整帳號 | 每個 user 僅顯示 `***` 後幾碼或遮蔽字串 |
| LK-GET-05 | Flow Test | MeiliSearch 服務暫時中斷 | 回傳 500 且不暴露內部細節 |

---

## 9. 高風險區域

- **隱私洩漏**：若程式未遮蔽按讚者帳號，會直接暴露使用者完整帳號，違反個資保護規則。
- **MeiliSearch 依賴**：查詢完全依賴 MeiliSearch，若 MeiliSearch 不可用則功能全面失效。需監控索引健康度。
- **不當索引查詢**：若過濾條件未嚴格限制 content_id，可能導致跨文章大量資料回傳，影響效能與安全。
- **帳號遮蔽方式不一致**：必須與其他列表（文章、留言）的遮蔽方式保持一致（例如固定顯示前 3 字元＋星號），否則可能逆向推導出完整帳號。

---

## 10. 常見錯誤

- ❌ 直接回傳 MeiliSearch 原始紀錄，未遮蔽 `user` 欄位 → 必須在 API 層轉換輸出前執行遮蔽。
- ❌ 未驗證 `game_type` 與文章實際所屬球種的一致性，可能導致前端顯示混淆（非功能性錯誤，但易誤解）。
- ❌ 使用巢狀循環對每個按讚記錄查詢其他系統（如 member service）補足資訊，造成效能問題 → 若非必須（如僅需遮蔽帳號），應直接從 MeiliSearch 資料進行遮蔽，無需額外查詢。
- ❌ AI 或新人誤以為此查詢需要寫入 Cassandra 或使用 Redis 快取 → 按讚功能完全在 MeiliSearch 中實現，不涉及 Cassandra，無 Redis 快取。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | 在 `OpenAPI` 路徑 `/api/community/{game_type}/articles/{article_id}/likes` 定義 GET 方法（推測） |
| 索引 | README `MeiliSearch like` 索引，用途為按讚搜尋索引 |
| DB 無使用 Cassandra | community keyspace 僅包含 `newlottery_forums` 表，無 likes 表 |
| 帳號遮蔽規則 | `community-detail.md`：「討論串/留言帳號遮蔽：對外列表時，account 欄位須遮蔽…不可回傳完整帳號」 |
| 無 Redis | `community-detail.md` 中 Redis 部分明確標示「community 無使用 Redis 快取」 |
| auth 處理 | README：「communityservice 僅接收已驗證的 authkey，不處理登入 token 驗證」 |