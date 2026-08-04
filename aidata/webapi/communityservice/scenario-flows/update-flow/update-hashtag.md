# 建立/更新 HashTag

## 1. 場景目的
後台管理員為指定遊戲類型（game_type）的聯賽設定或更新 HashTag。HashTag 儲存於 MeiliSearch 索引中，用於前端文章發布時快速搜尋與標記。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/community/{game_type}/hashtags/update` | 建立或更新指定遊戲類型的 HashTag |

---

## 3. 流程總覽

1. 接收來自後台管理員的 request，包含 authKey 與 HashTag 內容
2. 由 auth / member service 驗證 authKey，確認操作者具備後台管理權限
3. 解析路徑參數 `game_type`，驗證其合法性
4. 驗證 request body 中 HashTag 的必要欄位
5. 寫入或更新 MeiliSearch `hashtag` 索引中的文件
6. 回傳操作結果

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `HashTagController.update_hashtag` | 接收 request，轉交 Service 處理 |
| 2 | Service | `HashTagService.update_hashtag` | 組合文件，呼叫 Provider 更新 MeiliSearch |
| 3 | Provider | `MeiliSearchProvider.update_documents` | 對 `hashtag` 索引執行文件新增或更新操作 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| MeiliSearch | `hashtag` 索引 | Write（Add or Update） | 將 HashTag 文件寫入或更新至搜尋索引 |

依據 `communityservice-detail.md`，**community 無使用 Redis 快取**，此流程不涉及 Kafka 訊息佇列。

---

## 6. 重要規則

- **權限限制**：僅允許後台管理員操作。communityservice 本身不實作權限檢查，依賴外部（auth/member service）在 API Gateway 層完成驗證。
- **必要欄位驗證**：
  - 須提供 `hashtag_type`（HashTag 分類）與 `hashtag_id`（HashTag 識別碼）。
  - 其他顯示名稱與關聯的聯賽資訊需符合 API schema 定義。
- **寫入限制**：
  - `hashtag_type` 與 `hashtag_id` 作為文件主鍵，不可變更。僅能透過 `update` API 更新同主鍵文件。
  - 不可直接操作 Cassandra，此場景所有資料操作僅限 MeiliSearch 索引。
- **冪等性**：同一 `hashtag_type` + `hashtag_id` 組合重複呼叫，效果為更新，具備冪等性。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未攜帶有效的 authKey 或權限不足 | API Gateway 攔截，回傳 401 或 403 |
| 路徑參數 `game_type` 不合法 | Controller 或 Validator 攔截，回傳 422 |
| request body 缺少必要欄位（如 `hashtag_type`） | Controller 或 Validator 攔截，回傳 422 |
| MeiliSearch 寫入失敗或逾時 | Service 層捕獲例外，回傳 500，並記錄錯誤日誌 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| HT-UPD-01 | Permission Test | 使用一般使用者 token 呼叫 API | 403 Forbidden |
| HT-UPD-02 | Flow Test | 對同一個 `hashtag_id` 連續呼叫兩次 | 第二次成功（更新），回傳 200 OK |
| HT-UPD-03 | Integration Test | 成功更新後，以 GET `/api/community/{game_type}/hashtags` 查詢 | 列表中包含更新後的 HashTag |
| HT-UPD-04 | Flow Test | 使用不合法的 `game_type` 發送 request | 422 Unprocessable Entity |

---

## 9. 高風險區域

- **跨服務權限依賴**：若 auth/member service 的後台權限定義錯誤或 API Gateway 配置疏漏，可能導致非管理員寫入 HashTag，造成內容汙染。**這是最大風險，需人工確認權限配置。**
- **MeiliSearch 索引唯一性**：需確保 `hashtag_id` 在不同 `hashtag_type` 下可以重複，或文件設計已包含 `hashtag_type` 作為主鍵組合，否則可能意外覆蓋其他類型的 HashTag。

---

## 10. 常見錯誤

- ❌ AI 或新人誤以為 HashTag 儲存於 Cassandra 的某個 table 中
- ✅ **更正**：HashTag 僅存在 MeiliSearch `hashtag` 索引，用於前端搜尋與篩選，無對應的 Cassandra table。

- ❌ 試圖直接修改文件主鍵（如 `hashtag_id`）
- ✅ **更正**：應理解 `update` API 的行為是依主鍵 upsert，若需變更主鍵，應先刪除舊文件再新增。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `README.md` 中 HashTag 管理路由 |
| API | OpenAPI spec 中該路由的定義（需人工確認具體 schema 細節）|
| DB 職責 | `db-usage/communityservice-detail.md`：community 無 Redis 快取 |
| Code | `communityservice` 原始碼中 `HashTagController` 與 `HashTagService` 的類別與方法簽名 |