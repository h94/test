# 發布論壇主題

## 1. 場景目的

會員在指定的新彩票論壇看板中建立新的討論主題，寫入 MeiliSearch `newlottery_subjects` 索引供前台查詢，並於 Cassandra `community` keyspace 持久化儲存。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/newlottery/forums/{forum_id}/subjects` | 會員在指定論壇發布主題，需要驗證 |

---

## 3. 流程總覽

1. 接收會員發布主題請求（含 `forum_id`、主題內容），並驗證 authkey
2. 驗證目標論壇存在且狀態為啟用 (`status=1`)
3. 組成主題文件，產生 `subject_id`，設定初始狀態 (`status=1` 公開) 與時間戳
4. 寫入 MeiliSearch `newlottery_subjects` 索引
5. 寫入 Cassandra `community` keyspace 對應的 `newlottery_subjects_index` 表（需人工確認 Table 名稱）
6. 回傳建立成功的主題文件

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `NewlotteryController` 或對應 Blueprint | 接收 POST 請求，解析 `forum_id` 與 request body |
| 2 | Validator | `NewlotteryValidator` (或 schema) | 驗證請求格式、body 必填欄位、內容長度等 |
| 3 | Service | `NewlotteryService.create_subject(forum_id, data, user)` | 組合業務邏輯，驗證論壇、產生主題 ID、呼叫 Provider 寫入 |
| 4 | Provider (Cassandra) | `NewlotteryCassandraProvider` | 查詢 `community.newlottery_forums` 驗證論壇狀態；寫入主題至 `community.newlottery_subjects_index` |
| 5 | Provider (MeiliSearch) | `NewlotteryMeiliSearchProvider` | 寫入主題文件至 `newlottery_subjects` 索引 |
| 6 | Controller | `NewlotteryController` | 包裝回應並回傳 200 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `community.newlottery_forums` | Read | 查詢論壇是否存在且 `status=1` |
| DB (Cassandra) | `community.newlottery_subjects_index` | Write | 持久化儲存主題主體（需人工確認精確 Table 名稱） |
| Search | MeiliSearch `newlottery_subjects` | Write | 寫入主題全文搜尋索引，供前台以論壇、帳號、時間排序查詢 |
| Cache | Redis | — | **本服務 community 無使用 Redis 快取** |
| Queue | Kafka | — | **本場景無 Queue 操作** |

---

## 6. 重要規則

- **權限限制**：僅已驗證（登入）會員可發布主題。`communityservice` 僅接收已驗證的 `authkey`，認證由 auth/member service 負責。
- **論壇狀態限制**：僅 `newlottery_forums.status=1`（啟用）的論壇可發布主題；停用（`status=0`）應拒絕請求。
- **主題狀態初始值**：預設為 `status=1`（公開），僅作者或管理員後續可修改為隱藏 (`0`)。
- **不可修改欄位**：主題 `id` (subject_id) 與 `create_timestamp` 寫入後不可修改。
- **帳號遮蔽**：對外回傳的 `account` 欄位須遮蔽（如 `name***`），不可回傳完整帳號。
- **不可回傳欄位**：`user` (authkey) 對任何外部 API 皆不可直接回傳，需轉譯為使用者顯示資訊。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 請求未帶 valid token（authkey 失效或缺失） | 回傳 401 Unauthorized |
| `forum_id` 對應的論壇不存在 | 回傳 404 Not Found |
| 論壇存在但 `status=0`（停用） | 回傳 400 Bad Request 或 403 Forbidden，提示論壇未啟用 |
| 請求 body 缺少必填欄位或內容為空 | 回傳 422 Unprocessable Entity |
| 使用者被禁言（需人工確認是否有禁言機制應用於新彩票） | 回傳 403 Forbidden |
| MeiliSearch 寫入失敗 | 需要重試機制，最終失敗回傳 500；Cassandra 寫入應有對應補償或 error log |
| Cassandra 寫入失敗 | 回傳 500 Internal Server Error；需人工確認是否需 rollback MeiliSearch |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| FT-01 | Flow Test | 正常發布主題，提供有效 authkey、存在的 `forum_id` 且論壇 `status=1`、合法內容 | 200 OK；主題出現在 MeiliSearch 查詢中，Cassandra 存在對應 record |
| PT-01 | Permission Test | 無 authkey 呼叫 API | 401 Unauthorized |
| PT-02 | Permission Test | 對 `status=0` 的論壇發布主題 | 4xx 錯誤，不可寫入 |
| AT-01 | API Test | 缺少必填欄位（例如無標題或內文） | 422 Unprocessable Entity |
| IT-01 | Integration Test | MeiliSearch 暫時無法寫入 | 系統返回 5xx 錯誤，且 Cassandra 狀態與最終回應一致（需確認一致性策略） |
| IT-02 | Integration Test | 使用禁言會員 token 請求 | 403 Forbidden（若禁言適用此範圍） |

---

## 9. 高風險區域

- **跨儲存層一致性**：Cassandra 與 MeiliSearch 寫入需確保最終一致。若 MeiliSearch 寫入失敗而 Cassandra 已寫入，會造成搜尋不到的孤立資料；需確認 retry 或補償邏輯。
- **ID 生成唯一性**：`subject_id` 須保證分散式唯一，若依賴應用層 UUID 應無衝突；若使用自增需注意分散式鎖或碰撞風險。
- **Cache Consistency**：無 Redis，但若後續新增主題列表快取，需於發布時主動失效 `forum:{forum_id}:subjects` 快取。
- **權限驗證**：仰賴上游 auth member service；若 authkey 被竄改，本服務不額外校驗，風險在認證層。

---

## 10. 常見錯誤

- ❌ 發布主題時未驗證 `forum_id` 對應的論壇是否存在 → 可能產生孤兒主題，應先查詢 `community.newlottery_forums` 並檢查 `status=1`。
- ❌ 寫入 MeiliSearch 時未正確設定 `forum_id`、`create_timestamp` → 前台依論壇或時間排序時資料錯誤。
- ❌ 對外回傳主題時暴露完整 `account` 或 `user` → 需遮蔽帳號並隱藏 authkey。
- ❌ 直接將 request body 內容未經校驗就寫入 Cassandra / MeiliSearch → 容易造成 Injection 或內容長度溢出，須由 pydantic schema 驗證。
- ❌ 主題建立後未在應用層過濾已靜音或隱藏的主題（後續查詢情境）→ 但本場景僅處理發布，風險在查詢端。

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 定義 | README: `POST /api/newlottery/forums/{forum_id}/subjects` |
| DB (論壇驗證) | Cassandra `community.newlottery_forums`；`community-detail.md`：唯 `status=1` 可顯示 |
| DB (主題寫入) | MeiliSearch `newlottery_subjects`；`community-detail.md`：須過濾 `status=1` 且依 `forum_id` 匹配 |
| 寫入規則 | `community-detail.md`：`newlottery_subjects_index.status` 預設公開 (`1`)，由作者/管理員修改 |
| 帳號遮蔽規則 | `community-detail.md`：對外列表須遮蔽 `account`；不可回傳 `user` |
| 無 Redis | `communityservice-detail.md`：`community 無使用 Redis 快取` |
| 服務權責 | `community-detail.md`：communityservice 為 community keyspace 的 owner |