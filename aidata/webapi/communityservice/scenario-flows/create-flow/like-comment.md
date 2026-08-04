# 留言按讚

## 1. 場景目的
會員對已發布的留言執行按讚操作，系統將按讚紀錄同步寫入 MeiliSearch `like` 索引，以利後續查詢與統計。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/community/{game_type}/articles/{article_id}/comments/{comment_id}/likes` | 對指定文章下的一則留言按讚 |

---

## 3. 流程總覽

1. 接收前端 request（含路徑參數 `game_type`, `article_id`, `comment_id` 與 authkey）
2. 驗證 authkey 對應會員是否存在且 status=1（由上游 auth/member service 完成）
3. 查詢 Cassandra `community.comments` 驗證留言存在
4. 驗證留言未被隱藏（status=1）且非當前使用者自讚（若有此規則）
5. 查詢 MeiliSearch `like` 索引，確認無重複按讚記錄（idempotency check）
6. 寫入 MeiliSearch `like` 索引（一筆 like 文件：含 content_id, content_type, user, 時間戳）
7. 回傳操作成功

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `CommentLikesController.post` | 接收 request，轉交 Service 處理 |
| 2 | Service | `LikeService.add_comment_like` | 組織按讚邏輯：存在性檢查、重複檢查、寫入 MeiliSearch |
| 3 | Provider | `CommentProvider.get_comment` | 查詢 Cassandra `comments` 表確認留言存在 |
| 4 | Provider | `MeiliSearchProvider.add_document` | 將按讚文件寫入 MeiliSearch `like` 索引 |

> 註：Controller / Service / Provider 為推測分層；**需人工確認**實際 class 名稱。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `community.comments` | Read | 驗證留言存在及狀態（如 status=1） |
| Search | MeiliSearch `like` | Write | 記錄按讚事件 |
| Search | MeiliSearch `like` | Read | 檢查是否重複按讚 |

> communityservice 並未使用 Redis 或 Kafka（非日誌），本場景保持簡潔。

---

## 6. 重要規則

- **權限限制**：authkey 必須有效，會員 status 須為 1（啟用狀態）  
  Evidence: README「需要驗證」標示 POST like API 為 ✅；db-usage 文件提及 communityservice 接收已驗證的 authkey。
- **欄位限制**：按讚記錄 user 欄位僅儲存 user_id，對外回傳不可暴露完整 account，須遮蔽處理  
  Evidence: db-usage「不可回傳欄位」章節。
- **不可重複按讚**：同一 user 對同一 content_id 不可重複按讚，API 層須做 idempotency check  
  Evidence: MeiliSearch `like` 索引查詢後判斷。
- **留言存在檢查**：`comment_id` 對應的留言必須存在且未被刪除（status=1），否則拒絕  
  Evidence: 流程邏輯依循 Cassandra `comments` 表狀態。
- **無 Transaction**：Cassandra 寫入與 MeiliSearch 寫入非 Transactional，按讚紀錄最終一致性  
  Evidence: README 無 Transactional 設定說明。
- **無 Retry**：若 MeiliSearch 寫入失敗，此場景無預定義 retry 機制  
  **需人工確認**：是否需實作 retry 或 fallback 記錄。
- **狀態值限制**：按讚文件無狀態欄位；刪除按讚非本場景範圍（由 DELETE like API 處理）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 留言不存在（comment_id 無效） | 404 Not Found |
| 留言已刪除/隱藏（status=0） | 400 Bad Request（「該留言無法按讚」） |
| 重複按讚（相同 user 對相同 content_id） | 409 Conflict（「已按讚過」） |
| 缺少必要參數（authkey, comment_id） | 422 Unprocessable Entity |
| 會員不存在或被停用（status != 1） | 401 Unauthorized / 403 Forbidden |
| MeiliSearch 寫入失敗 | 500 Internal Server Error（需人工確認 retry 策略） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| TC01 | Permission Test | 未攜帶 authkey | 401 Unauthorized |
| TC02 | API Test | authkey 有效，comment_id 不存在 | 404 Not Found |
| TC03 | Flow Test | 第一次按讚 | 201 Created，MeiliSearch 產生一筆 like 文件 |
| TC04 | Idempotency Test | 同一 user 對同一 comment_id 按讚兩次 | 409 Conflict |
| TC05 | API Test | comment_id 對應的留言 status=0（隱藏） | 400 Bad Request |
| TC06 | Integration Test | MeiliSearch 服務中斷 | 500 Internal Server Error |
| TC07 | Data Verification | 按讚後查詢 MeiliSearch `like` 索引 | 文件包含正確的 content_id, user, timestamp |
| TC08 | Account Masking | 查詢按讚列表 API（GET） | 回的 user 欄位已遮蔽（非完整 account） |

---

## 9. 高風險區域

- **高風險 API**：POST like（直接影響 MeiliSearch 寫入，無 rollback 機制）
- **跨服務資料同步**：Cassandra `comments` 與 MeiliSearch `like` 非事務性同步，可能出現不一致
- **Cache consistency**：無 Redis 快取介入，低風險
- **Queue retry**：無佇列，失敗直接返回錯誤
- **Idempotency**：仰賴應用層檢查，非 MeiliSearch 內建

---

## 10. 常見錯誤

- ❌ 未檢查留言是否存在即寫入 MeiliSearch → ✅ 應先查詢 Cassandra `comments` 驗證
- ❌ 對外 API 回傳按讚者完整 account → ✅ 應遮蔽處理
- ❌ 未防範重複按讚，導致 MeiliSearch 存在多筆重複文件 → ✅ 寫入前先查詢 `like` 索引
- ❌ 忽略留言 status=0（隱藏）仍允許按讚 → ✅ 須過濾 status=1 才允許操作

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/community/{game_type}/articles/{article_id}/comments/{comment_id}/likes` |
| DB | Cassandra `community.comments` |
| Search | MeiliSearch `like` 索引 |
| Code | Flow: Controller → LikeService → CommentProvider(DB) + MeiliSearchProvider |
| Rules | db-usage: 不可回傳 account、status 檢查、權限驗證 |

## 12. 建議新增

- **建議新增文件**：`like-flow.md`（本文即為此目的產出）
- **建議新增規則**：MeiliSearch 寫入失敗 retry 策略（**需人工確認**）
- **建議新增測試**：MeiliSearch 寫入延遲時的前端行為測試；大量併發按讚的 idempotency 壓力測試