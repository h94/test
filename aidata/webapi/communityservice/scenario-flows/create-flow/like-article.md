# 文章按讚

## 1. 場景目的
會員對體育社群文章表達讚賞，系統記錄按讚行為至 MeiliSearch `like` 索引，供後續查詢文章的按讚數與按讚者列表。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/community/{game_type}/articles/{article_id}/likes` | 對指定文章按讚（需驗證） |

---

## 3. 流程總覽

1. 接收 POST 請求，從 header 取得 authkey。
2. 驗證 authkey 有效（依賴外部 member service 中介驗證，communityservice 不重複驗證）。
3. 確認目標文章存在（從 MeiliSearch `community` 索引或 Cassandra `articles` 表檢查，需人工確認具體檢查方式）。
4. 檢查是否已按讚（依 `content_id` + `user` 在 MeiliSearch `like` 索引中查詢，避免重複——業務規則需人工確認是否允許重複按讚）。
5. 將按讚記錄寫入 MeiliSearch `like` 索引（文件欄位可能包含 `content_id`、`user`、`timestamp` 等）。
6. 可選：透過 Kafka 發送按讚事件日誌（非核心流程）。
7. 回傳 200 成功響應。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Middleware | AuthMiddleware | 解析 authkey 並附加至 request context |
| 2 | Controller | LikeController (推測) | 接收路由參數 `game_type`、`article_id` |
| 3 | Service | LikeService (推測) | 業務邏輯：檢查文章存在性、是否已按讚、寫入 MeiliSearch |
| 4 | Provider | MeiliSearchProvider | 執行 MeiliSearch 查詢與寫入操作 |
| 5 | Provider | CassandraProvider（若有） | 可能用於讀取 `articles` 表確認文章存在 |

> 由於缺少實際 code evidence，方法名稱與類別為推測，需人工確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| MeiliSearch | `like` 索引 | Write | 儲存按讚記錄（content_id, user, timestamp） |
| MeiliSearch | `like` 索引 | Read | 檢查是否已按讚，避免重複 |
| MeiliSearch | `community` 索引 | Read（推測） | 驗證文章是否存在 |
| Cassandra | `community.articles` | Read（可能） | 備用文章驗證（若 MeiliSearch 不同步） |
| Kafka | `TCZB Logger` | Publish（非必定） | 發送按讚日誌，用於監控或審計 |

> 本場景 **不使用 Redis 快取**（communityservice 無 Redis 整合）。

---

## 6. 重要規則

- **權限限制**：僅已驗證的使用者（攜帶有效 authkey）可執行，authkey 驗證由外部 member service 提供。
- **文章存在性**：寫入 like 前必須確保 `article_id` 對應的文章存在（需人工確認檢查來源：MeiliSearch 或 Cassandra）。
- **重複按讚限制**：同一 user 對同一 content_id 可能不允許重複按讚（需人工確認業務規則），若限制則應返回衝突錯誤。
- **user 欄位隱私**：寫入 MeiliSearch 的 `user` 欄位應為內部識別碼（如 authkey 對應的 account），對外查詢 API 必須遮蔽或轉換為顯示名稱（參照 community-detail 中不可回傳欄位規則）。
- **冪等性**：若客戶端重試，需保證相同請求不會產生多條按讚記錄（藉由預先查詢或使用唯一約束，需 MeiliSearch 支援或應用層控制）。
- **TTL / 無**：MeiliSearch 索引無預設 TTL，按讚記錄為持久化。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 缺少 authkey 或 authkey 無效 | 401 或 403 拒絕 |
| 文章不存在（article_id 無效） | 404 Not Found |
| 使用者已對該文章按讚（若業務禁止重複） | 409 Conflict |
| MeiliSearch 服務不可用 | 500 Internal Server Error，按讚失敗 |
| 請求路徑參數格式錯誤 | 422 Unprocessable Entity |
| 使用者被禁言或封鎖 | 403 拒絕（需人工確認禁言規則是否影響按讚，目前禁言管理僅提及文章/留言） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | Permission Test | 無 authkey 發送按讚請求 | 401 Unauthorized |
| T2 | API Test | 對已存在的文章按讚（有效 authkey） | 200 OK，MeiliSearch 新增記錄 |
| T3 | Flow Test | 重複按讚（若禁止重複） | 409 Conflict |
| T4 | Flow Test | 按讚不存在的文章 | 404 Not Found |
| T5 | Integration Test | MeiliSearch 離線時的按讚請求 | 500 錯誤，無記錄寫入 |
| T6 | Security Test | 查詢按讚列表時，檢查 user 欄位是否脫敏 | 未洩漏完整帳號或 authkey |

---

## 9. 高風險區域

- **MeiliSearch 單點依賴**：按讚寫入與文章存在性檢查皆依賴 MeiliSearch，若服務中斷則功能完全不可用。
- **無 DB 交易**：按讚操作僅寫入 MeiliSearch，無 Cassandra 側記錄，無法實現跨庫一致；若後續需要與其他功能（如通知）關聯，可能產生孤兒記錄。
- **重複按讚控制**：若僅在應用層檢查再寫入，高併發下可能產生重複記錄；建議在 MeiliSearch 建立唯一約束（如 `content_id + user` 唯一鍵）或使用樂觀鎖，需人工確認目前實現。
- **隱私洩漏**：MeiliSearch 索引中的 `user` 欄位若直接暴露給前端查詢 API，將違反社區帳號遮蔽規則；必須在查詢按讚列表時進行脫敏處理。
- **外部驗證中斷**：若 member service 驗證 authkey 失敗（但 communityservice 依賴中介層），可能導致所有請求被拒，需確保中介層穩定。

## 10. 常見錯誤

- ❌ 未先檢查文章是否存在就直接寫入 MeiliSearch → 導致孤兒按讚記錄，前端顯示無效。
- ❌ 對外按讚查詢 API 直接回傳 `user` 欄位的原始帳號 → 應遮蔽為 `name***`。
- ❌ 未處理 MeiliSearch 寫入失敗 → 前端誤以為按讚成功，實際記錄遺失。
- ❌ 未限制重複按讚，且無唯一約束 → 同一使用者可無限次按讚，影響數據準確性。
- ❌ 忽略了按讚與文章計數更新的關聯（若文章文件有 `like_count` 欄位需同步更新）→ 需確認是否需即時更新文章熱門分數（README 提及 MeiliSearch 文章索引包含熱門分數，可能依賴 like 總數，需人工確認更新機制。）

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | 路由定義於 README「按讚」章節：`POST /api/community/{game_type}/articles/{article_id}/likes` |
| 儲存層 | README 資料庫重要 Table：MeiliSearch `like` 索引，用途為「依 content_id、user 篩選」 |
| 驗證 | README 對外 API 重點表格中，所有按讚路由皆標註「需要驗證 ✅」 |
| 無 Redis | `communityservice-detail.md` 明確指出 communityservice 無使用 Redis 快取 |
| 帳號遮蔽規則 | `community-detail.md` 中「不可回傳欄位」：所有表之 `user` (authkey) 不可直接回傳，需轉譯 |
| 禁言範圍 | 禁言管理路由僅針對文章/留言功能，未明確包含按讚，需人工確認是否影響按讚 |