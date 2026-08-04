# 查詢論壇主題列表

## 1. 場景目的

此場景讓已驗證的使用者查詢指定論壇看板中所有公開的主題列表，預設依主題建立時間或最後留言時間倒序排列。主要用於新彩票前台用戶瀏覽討論看板內容。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/newlottery/forums/{forum_id}/subjects` | 查詢指定論壇下的主題列表 |

**需驗證**：✅（需在 request header 攜帶有效 auth token，由 auth/member service 前置驗證，communityservice 僅接收已驗證的 authkey）

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，從 URL 路徑取得 `forum_id`，並從 header 或 request context 取得驗證後的用戶資訊。
2. 驗證論壇是否存在且狀態為啟用（`status=1`）。
3. 向 MeiliSearch 索引 `newlottery_subjects` 發起查詢，過濾 `forum_id` 且 `status=1`（公開）的主題。
4. 依預設排序（如 `create_timestamp:desc` 或 `last_comment_timestamp:desc`）取得主題列表。
5. 對回傳結果中的 `account` 欄位進行遮蔽處理（如 `name***`），確保不暴露完整帳號。
6. 回傳處理後的主題列表 JSON。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | NewLotteryController.GetForumSubjects | 接收請求，解析 `forum_id`；轉拋 Service |
| 2 | Service | NewLotteryService.GetSubjects | 呼叫 Provider 查詢論壇狀態與主題索引 |
| 3 | Provider | ForumProvider.GetForumById | 向 Cassandra `community.newlottery_forums` 查詢論壇記錄，確認 `status=1` |
| 4 | Provider | SubjectSearchProvider.Search | 向 MeiliSearch `newlottery_subjects` 發起查詢，參數包含 filter: `forum_id = {forum_id} AND status = 1`，sort: `create_timestamp:desc` |
| 5 | Service | NewLotteryService.GetSubjects | 將 MeiliSearch 返回的原始結果進行清洗：移除 `user`（authkey）欄位、遮蔽 `account` 欄位 |
| 6 | Controller | NewLotteryController.GetForumSubjects | 序列化結果並回傳 HTTP 200 |

> **需人工確認**：具體分頁邏輯（`page` / `pageSize`）與排序參數是否支援前臺傳入、MeiliSearch index attributes 的實際欄位名稱。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `community.newlottery_forums` | Read | 驗證論壇是否存在且啟用（過濾 `id` 且 `status=1`） |
| Index | MeiliSearch `newlottery_subjects` | Read | 全文搜尋與篩選，查詢指定論壇下的公開主題並排序 |
| Cache | 無 | - | community 無使用 Redis 快取（依據 `communityservice-detail.md` 註記） |
| Queue | 無 | - | 查詢場景無佇列操作 |

---

## 6. 重要規則

- **權限限制**：所有 API 需攜帶有效 auth token；未驗證請求將由上游 gateway 或 auth service 攔截，不進入本服務。
- **論壇狀態驗證**：僅回傳存在且 `status=1`（啟用）的論壇；若 `status=0` 或論壇不存在，應回傳對應錯誤。
- **主題狀態過濾**：只回傳 `status=1`（公開）的主題；隱藏（`status=0`）的主題應完全過濾，不在列表中暴露（根據 `community-detail.md`）。
- **帳號遮蔽**：對外列表 API 中，`newlottery_subjects_index` 的 `account` 欄位必須遮蔽（如 `name***`），**不可回傳完整帳號**（根據 `community-detail.md` 之不可回傳欄位）。
- **不可回傳欄位**：`user`（authkey）對任何外部 API 皆不可回傳；需在服務層清洗。
- **排序規則**：主題列表預設依建立時間或最後留言時間倒序排列（根據 README 表定義及 `community-detail.md` 建議）。
- **靜音／隱藏過濾**：若後續存在 per-user 靜音主題或隱藏設定，應在應用層（Service）過濾，不可從 MeiliSearch filter 硬性排除所有隱藏（根據 `community-detail.md` 靜音規則）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 用戶未登入或 token 無效 | 回傳 401 Unauthorized（由 auth/member service 或 gateway 處理） |
| 論壇 `forum_id` 不存在 | 回傳 404 Not Found，錯誤訊息指明論壇不存在 |
| 論壇 `status=0`（隱藏或停用） | 回傳 404 Not Found 或 403 Forbidden，視業務規範；**需人工確認** |
| MeiliSearch 連線失敗或 timeout | 回傳 503 Service Unavailable，記錄錯誤日誌 |
| 指定的 `forum_id` 下無任何公開主題 | 回傳 200 OK，空列表 `[]` |
| MeiliSearch 返回資料含有非預期欄位或格式 | 回傳 500 Internal Server Error，記錄異常 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| QF-01 | API Test | 提供有效 `forum_id`，登入狀態 | 200 OK，回傳主題列表（`account` 已遮蔽） |
| QF-02 | API Test | 提供有效 `forum_id` 但無任何主題 | 200 OK，空列表 |
| QF-03 | API Test | 提供不存在的 `forum_id` | 404 Not Found |
| QF-04 | Permission Test | 對隱藏論壇（`status=0`）發起請求 | 404 或 403 |
| QF-05 | API Test | 未攜帶 token 發起請求 | 401 Unauthorized |
| QF-06 | Flow Test | MeiliSearch 查詢時發生連線錯誤 | 503 Service Unavailable，不可 crash |
| QF-07 | Data Test | 驗證回傳資料內無完整 `account` 與 `user` 欄位 | 列表每筆資料的 `account` 已遮蔽，`user` 不存在 |

---

## 9. 高風險區域

- **高風險 API**：此場景為**唯讀查詢**，風險較低，但仍需注意 MeiliSearch 查詢效能與資料一致性。
- **跨服務資料同步**：主題寫入由發文 API 寫入 MeiliSearch，若寫入延遲或失敗，使用者可能查不到最新主題。但此場景**不負責同步**，風險在接受範圍內。
- **Cache consistency**：目前無快取，無快取一致性風險。
- **帳號遮蔽邏輯**：若遮蔽邏輯失敗或未正確套用，將導致個資外洩，合規風險極高。

---

## 10. 常見錯誤

- ❌ 查詢時未過濾 `newlottery_forums.status=1`，導致回傳隱藏論壇的主題列表。
- ❌ 查詢 MeiliSearch 時未加上 `status=1` filter，將隱藏主題暴露給前台。
- ❌ 回傳的 `account` 欄位未遮蔽，直接暴露完整帳號——違反 `community-detail.md` 規定。
- ❌ 將 `user`（authkey）欄位直接序列化回傳——應於 Service 層完全移除。
- ❌ 誤以為該 API 有使用 Redis 快取，或錯誤地快取未遮蔽的原始資料——**community 無 Redis**，直接查詢 MeiliSearch 即可。
- ❌ 未檢查論壇是否存在就直接查詢 MeiliSearch，可能導致查詢不存在論壇的主題時仍回傳空列表（應先回報論壇不存在，`404`）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | `README.md` - 新彩票論壇：`GET /api/newlottery/forums/{forum_id}/subjects` |
| API 驗證 | `README.md` - 新彩票論壇 API：需要驗證 ✅ |
| DB 讀取（論壇） | `db/community.md` - `community.newlottery_forums` |
| DB 讀取（主題索引） | `README.md` - MeiliSearch Index：`newlottery_subjects` |
| 讀取規則（主題過濾、帳號遮蔽） | `community-detail.md` - 讀取規則：討論串列表查詢、不可回傳欄位 |
| Redis 無使用 | `webapi/communityservice/communityservice-detail.md` - Redis 章節：「community 無使用 Redis 快取。」 |
| 權限驗證 | `webapi/communityservice/communityservice-detail.md` - 本服務不負責章節：communityservice 僅接收已驗證的 authkey |
| 排序建議 | `community-detail.md` - 討論串列表查詢讀取規則與 `newlottery_subjects_index` 使用說明 |