# 查詢文章留言列表

## 1. 場景目的
使用者於體育社群瀏覽特定文章時，取得該文章下所有公開留言，依發表時間排序分頁返回，以查看討論內容。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/community/{game_type}/articles/{id}/comments` | 查詢指定文章留言（分頁） |

- 參數（OpenAPI 中未詳細列出，依推測需人工確認）：
  - `page`（分頁索引）
  - `size`（每頁筆數）
  - 可能接受時間戳或 offset 用於遊標分頁

---

## 3. 流程總覽

1. 接收請求，從 Header 取得已驗證的 `authKey`（由閘道或 auth service 注入）。
2. 解析路徑參數 `game_type` 與文章 `id`。
3. 確認文章存在（可選：先讀取文章基本資訊以驗證文章狀態，避免對不存在文章查詢留言）。
4. 從 Cassandra `community.comments` 表中，以 `article_id` 為分割鍵讀取留言：
   - 只取 `status = 1`（公開）的留言（若有此欄位，需人工確認）。
   - 依 `created_at`（或 `comment_id`）降冪排序，實現分頁（通常使用 `LIMIT` 與 `PAGING STATE` 或 `WHERE created_at > last`）。
   - 需過濾「隱藏」留言（可能由使用者設定或系統標記，應用層過濾）。
5. 針對每筆留言，檢查留言者是否處於禁言狀態（`mute` 記錄），若為禁言中則不顯示該則留言（需人工確認實作位置：可能是讀取 `community` 內部的 mute 表，或透過 member 服務查詢）。
6. 遮蔽敏感欄位：`account` 轉換為顯示名稱或遮罩（如 `name***`），不直接暴露原始帳號；`authkey` 絕不回傳。
7. 組合回應，包含留言內容、時間、點讚數、回覆數等。
8. 回傳 JSON 陣列（或包裹分頁資訊）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `CommentController.get_comments` | 接收請求，調用 Service |
| 2 | Validator | `GetCommentsSchema` | 校驗 `game_type`、文章 ID 格式、分頁參數 |
| 3 | Service | `CommentService.list_by_article` | 業務邏輯：決定查詢參數、呼叫 Provider、執行遮蔽與過濾 |
| 4 | Provider | `CassandraCommentProvider` | 以 `article_id` 查詢 Cassandra `comments` 表（需指定 partition key） |
| 5 | Provider | `MuteProvider`（推測） | 查詢使用者禁言狀態（從 Redis 或 Cassandra `mute` 表） |
| 6 | Transfer | `CommentTransformer` | 將 DB 記錄轉換為 API 回應格式，執行帳號遮蔽 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `community.comments` | Read | 查詢文章留言，依 `article_id` 分區，按建立時間排序 |
| DB | Cassandra `community.mute`（推測） | Read | 檢查留言者是否禁言，過濾不顯示的留言 |
| Redis | 未使用 | - | 留言區無快取機制 |
| Kafka | 未使用 | - | 查詢流程不涉及訊息發佈 |

---

## 6. 重要規則

- **權限限制**：所有已登入使用者皆可查詢；無額外權限要求。
- **欄位遮蔽**：
  - `account`：對外回傳一律遮蔽（如 `name***`）或轉為使用者名稱（從 `member.gameusers.username` 取得，需人工確認是否由 communityservice 快取或即時查詢）。
  - `authkey`：絕不回傳。
- **分頁規則**：
  - 需採用基於遊標的分頁（Cassandra `PAGING STATE` 或 `WHERE comment_id > last_id`），避免全表掃描效能問題。
  - 每頁筆數有上限（需確認，建議 20~50）。
- **過濾規則**：
  - 留言僅顯示 `status = 1`（公開）的記錄；隱藏（`status = 0`）或已刪除（`status = 2`，如有）不回傳。
  - 使用者若曾將某留言加入自身隱藏清單（`hidden`），該則亦不回傳（若功能存在）。
  - 禁言中的使用者所發的留言應被過濾：以發言者帳號查詢禁言記錄，若存在有效禁言則不顯示。
- **不可暴露資料**：
  - 不可回傳 `report_table` 相關資訊。
  - 不可回傳原始 `authkey`。
- **TTL / 快取**：本場景讀路徑無 Redis 快取，每次查詢直接讀取 Cassandra。
- **Transaction**：無，Cassandra 單一查詢操作。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 文章不存在（`article_id` 無對應記錄） | 可回傳空列表，或 404（需人工確認：OpenAPI 描述「找不到時可能回傳空物件」，此處建議回傳空列表） |
| 參數格式錯誤（`game_type` 空白、`page` 非數字） | 回傳 422 Unprocessable Entity |
| 使用者未登入 | 回傳 401 Unauthorized |
| 分頁查詢越界（請求超出總頁數） | 回傳空列表 |
| Cassandra 連線超時 | 回傳 500，記錄錯誤日誌至 Kafka |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | Flow Test | 正常查詢第一頁留言 | 回傳正確留言列表，帳號經遮罩處理，排序為最新在上 |
| T2 | Flow Test | 留言存在隱藏狀態（status=0） | 隱藏留言不出現 |
| T3 | Flow Test | 留言者處於禁言中 | 該留言不顯示 |
| T4 | Permission Test | 未帶 authKey | 拒絕存取（401） |
| T5 | API Test | 文章 ID 不存在 | 回傳空列表（或 200 + 空陣列） |
| T6 | API Test | 分頁查詢最後一頁後下一頁 | 回傳空列表 |
| T7 | API Test | 無意見留言的文章 | 回傳空列表 |
| T8 | Integration Test | Cassandra 不可用 | 回傳 500，錯誤日誌正常 |

---

## 9. 高風險區域

- **高風險 table**：`community.comments`（若分區鍵設計不當，可能導致 hotspot；需確認以 `article_id` 為分區鍵，避免全表掃描）。
- **跨服務資料同步**：無，留言查詢僅讀取自家 Cassandra。
- **Cache consistency**：無 Redis 快取，不致失去一致性。
- **禁言判斷延遲**：若禁言狀態存於 Redis，且更新不及時，可能導致已禁言的使用者短期內仍顯示留言（需人工確認禁言資料同步機制）。

---

## 10. 常見錯誤

- ❌ 在列表回傳中直接暴露 `account` 完整帳號 → 容易違反個資保護，必須遮罩。
- ❌ 未過濾 `status = 0` 的隱藏留言 → 前台可能顯示已下架的內容。
- ❌ 使用 `SELECT * FROM comments` 全表掃描 → 必須指定 partition key（`article_id`）並限制範圍。
- ❌ 忽略禁言檢查 → 遭禁言使用者的歷史留言仍會出現，違反業務規則。
- ❌ 分頁使用 offset 方式（如 `LIMIT 20 OFFSET 100`） → Cassandra 不支援高效 offset，應使用遊標。
- ❌ 將 `authkey` 或 `report_table` 資訊回傳 → 必須在 Transfer 層過濾。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README - 體育社群留言 GET `/api/community/{game_type}/articles/{id}/comments` |
| DB | README - Cassandra `community.comments` |
| 遮罩規則 | community-detail.md - 討論串/留言帳號遮蔽 |
| 狀態過濾 | community-detail.md - 留言列表查詢須過濾 `status=1` |
| 禁言檢查 | README - 禁言管理 API `mute` / `mute_single` |
| 權限 | README - 所有體育社群留言 API 需要驗證 |