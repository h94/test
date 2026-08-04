# 新增運動文章

## 1. 場景目的

後台編輯人員建立一筆新的運動相關新聞文章，用於前台展示或推播。本場景描述從 pricebackendservice 接收請求到完成儲存的完整流程，重點在於 BFF 層的驗證、轉發與下游 newsservice 的協作。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/news/sportarticles` | 新增運動文章 |

---

## 3. 流程總覽

1. 後台管理者透過前端提交運動文章資料（標題、內容、遊戲類型等）。
2. pricebackendservice 接收請求，驗證管理者權限。
3. 進行輸入資料基本驗證（必填欄位、格式）。
4. 呼叫下游 `newsservice` 對應 REST API（例如 POST `/articles/sport`），傳遞文章內容。
5. `newsservice` 進行業務邏輯處理，將文章寫入 Cassandra `news` keyspace（推測為 `commonarticles` 或 `sports_{gameType}` 表，需人工確認）。
6. 若寫入成功，回傳成功訊息及文章 ID。
7. 若任何環節失敗，回傳對應錯誤訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `NewsController.CreateSportArticle` | 接收 request，呼叫 service |
| 2 | Service | `NewsService.CreateSportArticle` | 資料驗證、組合 DTO、呼叫 provider |
| 3 | Provider | `NewsApiProvider.CreateArticle` | 發送 HTTP POST 到 newsservice 端點 |

> **注意**：此處的 class 及方法名稱為慣例推測，實際名稱需以程式碼為準（**需人工確認**）。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| REST API | newsservice `POST /articles/sport` (推測) | Write | 實際儲存運動文章資料 |
| DB | news keyspace（下游 newsservice 負責） | Write | 持久化文章內容（推測表：`commonarticles` 或 `sports_{gameType}`，**需人工確認**） |
| Cache | 無 | – | – |
| Queue | 無 | – | – |

**說明**：pricebackendservice 為 BFF 層，不直接操作任何 DB 或快取，所有持久化行為均由 newsservice 代理。

---

## 6. 重要規則

- **權限限制**：僅後台管理者（具備編輯新聞權限的帳號）可呼叫此 API，需通過 `ECFramework.ECService` 驗證。
- **欄位限制**：文章內容應包含必要欄位如標題、內文、語言代碼、遊戲種類（如 `sport`），但實際欄位由 newsservice 定義，pricebackendservice 僅做基本格式校驗。
- **不可暴露資料**：在 BFF 層不可洩漏內部服務位址、下游 API 細節或 Cassandra raw query。
- **不可修改欄位**：一經建立，部分欄位（如 `articleid`）可能由 newsservice 自動生成，後續不可透過此 API 直接更新。
- **Transaction 規則**：無分散交易需求，下游寫入失敗即回傳錯誤，不進行補償。
- **Retry 規則**：pricebackendservice 對 downstream 的呼叫可設定簡易 retry（如 1 次），但需避免重複建立（由 newsservice 保證 idempotency，**需人工確認**）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 請求未帶 token 或 token 無效 | 401 Unauthorized |
| 管理員不具備新聞編輯權限 | 403 Forbidden |
| 必填欄位缺失或格式錯誤 | 400 Bad Request，提示具體錯誤欄位 |
| newsservice 無回應或 timeout | 502 Bad Gateway 或 504 Gateway Timeout |
| newsservice 回應業務錯誤（如重複文章、內容違規） | 將下游錯誤碼轉換後回傳（如 409 Conflict） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| TC01 | API Test | 正常新增一篇運動文章 | 201 Created，回傳文章 ID |
| TC02 | Permission Test | 未登入或使用無效 token 呼叫 API | 401 回應 |
| TC03 | Flow Test | newsservice 下線或回傳 500 | pricebackendservice 回傳 5xx 並記錄錯誤日誌 |
| TC04 | Validation Test | 缺少標題欄位請求 | 400 回應，錯誤訊息指出缺少標題 |

---

## 9. 高風險區域

- **newsservice 相依性**：pricebackendservice 完全依賴下游服務的可用性，任何 newsservice 的停機或慢響應都會直接影響後台功能。
- **資料一致性**：若未來文章有更新或刪除操作，必須確保 newsservice 對應的實體一致，並避免因 BFF 層的快取或 retry 導致重複建立。
- **跨服務資料同步**：若前台讀取文章也透過其他服務（如 gamesettingsite），需確保發布狀態的同步，此部分不在本場景範圍內。

---

## 10. 常見錯誤

- ❌ 新人誤以為 pricebackendservice 直接操作資料庫 → 所有持久化均由 newsservice 負責，本服務僅做轉發。
- ❌ 忘記進行管理者權限檢查 → 必須在 Controller 或 Middleware 層驗證角色。
- ❌ 未對下游回傳的錯誤進行映射，直接拋出原始錯誤 → 應轉換為統一的 API 錯誤格式。
- ❌ 忽略 idempotency：若前端重複提交同一文章，可能因無唯一約束導致重複建立 → 需由 newsservice 提供冪等機制（如基於 client-id）並在 BFF 層傳遞對應 token。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 定義 | README「新聞與 AI 資訊管理」路由表 |
| 驗證機制 | README：使用 ECFramework.ECService 驗證 |
| 服務相依 | README：newsservice 負責文章管理 |
| DB 操作邊界 | pricebackendservice-detail.md：本服務無直接 DB 存取 |
| 下游 DB 推測 | news-detail.md：存在 commonarticles、botarticles，但運動文章對應表待確認 |

---

**建議新增文件**：newsservice 的內部 API 文件（OpenAPI/Swagger），明確定義 sports article 的請求/回應 Schema、idempotency-key 機制以及對應的 Cassandra 表格結構。