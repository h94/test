# 設定運動站台文章

## 1. 場景目的

編輯人員於後台新增或更新站台文章，系統將文章內容寫入對應的站台文章資料表（推測為 `commonarticles` 或獨立表，需確認），供前端站台查詢展示。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/sportarticles` | 新增或更新站台文章，需驗證 |

---

## 3. 流程總覽

1. API Gateway 驗證 JWT，確認請求為後台編輯人員。
2. Controller 接收 Article 物件（含 id、title、content、lang 等）。
3. Service 層進行欄位驗證，判斷 id 是否存在決定 INSERT 或 UPDATE。
4. 透過 DataProvider 將文章寫入 Cassandra `news` keyspace 的目標表。
5. 回傳成功與否訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | SportArticlesController | 接收請求，調用 ISportArticlesService |
| 2 | Service | ISportArticlesService | 驗證欄位、判斷新增/更新邏輯 |
| 3 | Provider | SportArticlesDataProvider | 執行 Cassandra 寫入（Upsert） |
> 實作類別待確認，以上為推測架構。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | news.commonarticles（推測） | Write/Update | 儲存站台文章 |
> 本服務無 Redis 或 Queue，Cassandra 為唯一持久化儲存。

---

## 6. 重要規則

- **權限**：僅驗證過的後台編輯人員可寫入，API 需攜帶有效 JWT。
- **欄位限制**：需提供 title、content、lang 等必要欄位；`articleid`（若有）由服務產生或請求帶入。
- **不可暴露欄位**：若使用 `commonarticles`，內部評分（scores）或預測內容（predict）不應回傳給前端（需確認）。
- **狀態管理**：文章是否有發佈/下架狀態未知，需確認後補充規則。
- **Idempotency**：若支援冪等，應以 id 作為主鍵；重複請求不應產生重複資料。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未攜帶有效 JWT | 401 Unauthorized |
| 缺少必填欄位（如 title） | 400 Bad Request |
| Cassandra 寫入失敗 | 500 Internal Server Error |
| 文章 id 不存在但意圖更新 | 視業務邏輯自動新增（upsert 特性）或返回錯誤，需確認 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC-01 | Flow Test | 新增一篇完整文章 | 200 OK，DB 出現新記錄 |
| TC-02 | Permission Test | 無 Token 呼叫 | 401 |
| TC-03 | API Test | 缺少 title 欄位 | 400 |
| TC-04 | Integration Test | 更新已存在文章 | 200 OK，記錄更新 |

---

## 9. 高風險區域

- **Table 確認**：實際使用的表未在 README 明確指定（可能為 `commonarticles` 或 `botarticles`），錯誤指定將導致寫入失敗或資料混亂。
- **Upsert 語義**：Cassandra 寫入為 upsert，缺少明確的新增/更新區分邏輯可能誤覆蓋現有文章。
- **權限控制**：若閘道未正確攔截未授權請求，文章可能被任意修改。
- **無 Redis 快取**：寫入後前端查詢可能需自行處理資料同步，無快取失效問題。

---

## 10. 常見錯誤

- ❌ 將站台文章寫入 `sports_{gameType}` 動態表（此為爬蟲新聞，非後台文章）。
- ❌ 忽略必填欄位檢查，導致寫入不完整資料。
- ❌ 未過濾不可回傳欄位（如 scores），直接返回完整記錄。
- ❌ 未處理 upsert 可能造成的覆蓋風險。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md `POST /api/v1/sportarticles` |
| DB 推測 | detail.md 提及 `commonarticles` / `botarticles` 由 newsservice 寫入 |
| 權限 | README 標記「需要驗證 ✅」 |
> ⚠️ 實際 Controller/Service 實作、確切 Table 名稱需從程式碼補足，建議查閱 `SportArticlesController` 與相關 DataProvider。