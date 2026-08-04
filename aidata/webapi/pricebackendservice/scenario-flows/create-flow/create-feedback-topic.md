# 建立客服主題

## 1. 場景目的

後台管理人員在體育客服系統中建立一個新的客服主題（Topic），供用戶提交反饋時選擇歸類。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/feedback/sport/topics` | 建立一筆新的運動客服主題 |

---

## 3. 流程總覽

1. 後台管理員透過管理介面提交新主題資訊
2. `pricebackendservice` 接收請求，驗證管理員權限
3. 轉發請求至下游 `feedbackservice` 執行建立邏輯
4. `feedbackservice` 驗證主題 ID 是否重複、格式是否正確
5. 寫入 `feedback.topics_sport` 表
6. 回傳操作結果給後台

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `FeedbackController.CreateSportTopic` | 接收請求，從 JWT 解析權限，反序列化 request body |
| 2 | Service | `FeedbackService.CreateTopic` | 處理業務邏輯，組裝下游請求參數 |
| 3 | Provider | `FeedbackProvider.CreateSportTopicAsync` | 透過 REST API 轉發請求至 `feedbackservice` |
| 4 | Downstream | `FeedbackService.CreateTopic`（下游） | 驗證主題資料，寫入 Cassandra `feedback.topics_sport` |

**需人工確認**：實際的 Controller / Service / Provider 名稱。OpenAPI 檔案被截斷，code semantics 未提供 feedback 相關類別。上述 Layer 命名基於 README 定義的服務相依關係推斷。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `feedback.topics_sport` | Write | 儲存新建立的客服主題 |
| DB | `feedback.topics_sport` | Read | 檢查主題 ID 是否已存在 |

`pricebackendservice` 本身不直接操作資料庫，所有操作均由 `feedbackservice` 執行。`feedbackservice` 是 `feedback` keyspace 的唯一 owner。

**Cache / Queue**：無使用 Redis 或 Kafka 參與此流程（僅 `pricebackendservice` 使用 Kafka 記錄日誌，與業務流程無關）。

---

## 6. 重要規則

- **權限限制**：API 需要驗證（`✅`），僅後台管理人員可操作。
- **欄位限制**：
  - `id`（主鍵）：由請求端提供，**建立後不可修改**。
  - `enabled`：預設應為 `1`（啟用），僅能由後台 API 更新。
  - `sort`：排序序號，用於前端顯示順序。
  - `name`：多語言主題名稱（`map<text, text>`），至少需包含一種語言。
- **不可直接操作**：`pricebackendservice` 不得繞過 `feedbackservice` 直接寫入 `feedback` keyspace 的任何表。
- **TTL 規則**：無。
- **Transaction 規則**：單一 Cassandra partition 寫入，無跨表 transaction 需求。
- **Retry 規則**：下游呼叫失敗時，由 `pricebackendservice` 的 HTTP client 策略決定是否 retry（需人工確認）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未帶有效 JWT 或權限不足 | 回傳 `401 Unauthorized` 或 `403 Forbidden` |
| 請求 body 缺少必填欄位（如 `id`, `name`） | 回傳 `400 Bad Request`，提示缺少欄位 |
| 主題 ID 已存在 | 回傳 `409 Conflict` 或 `400 Bad Request`，提示 ID 重複 |
| 下游 `feedbackservice` 無法連線或 timeout | 回傳 `502 Bad Gateway` 或 `504 Gateway Timeout` |
| 請求 `name` map 為空 | 回傳 `400 Bad Request`，需至少一個語言鍵值 |
| 請求欄位型別錯誤（如 `sort` 傳入字串） | 回傳 `400 Bad Request`，格式驗證失敗 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| FT-01 | Flow Test | 正常建立主題：提供合法 id、name、sort | 回傳 200，`feedback.topics_sport` 出現新記錄 |
| FT-02 | Permission Test | 無 JWT 呼叫 API | 回傳 401 Unauthorized |
| FT-03 | API Test | 提供已存在的 topic id | 回傳 409 Conflict 或 400 |
| FT-04 | API Test | `name` map 為空 `{}` | 回傳 400 Bad Request |
| FT-05 | API Test | `sort` 欄位缺失 | 回傳 400 Bad Request 或系統自動填入預設值（需人工確認後者是否為設計行為） |
| FT-06 | Integration Test | `feedbackservice` 離線 | 回傳 502 或 504 |

---

## 9. 高風險區域

- **高風險 Table**：`feedback.topics_sport` — 所有客服回饋均依賴主題正確存在，刪除或停用主題會影響用戶反饋流程。
- **權限失誤**：若 API Gateway 或 Controller 層驗證配置錯誤，可能允許未授權使用者建立主題，污染客服資料。
- **下游耦合**：`pricebackendservice` 完全依賴 `feedbackservice` 可用性；下游故障時，後台管理功能直接中斷，無法 fallback。
- **Idempotency**：本 API 不具備天然冪等性；重複請求相同 id 會導致衝突錯誤，需由前端避免重複提交。
- **Map 覆蓋風險**：雖為新建操作，若後續提供更新主題功能，必須逐鍵更新 `name` map，不可直接 REPLACE 整個 map，否則會遺失其他語系名稱。

---

## 10. 常見錯誤

- ❌ **新人誤解**：以為 `pricebackendservice` 直接寫入 DB → 本服務是 BFF 聚合層，不持有任何 DB 連線，所有寫入操作均委派給下游 `feedbackservice`。
- ❌ **AI 誤判**：基於 OpenAPI schema 自動生成可直接 INSERT 的程式碼 → 必須繞道呼叫 `feedbackservice` 的 REST API。
- ❌ **漏檢查項目**：未驗證 `id` 是否包含非法字元；Cassandra 主鍵可能因特殊字元導致查詢錯誤。
- ❌ **常見流程錯誤**：直接在前端生成隨機 UUID 作為主題 ID，但未進行重複性檢查 → 應由後端或專用 ID 產生機制確保唯一性。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由定義 | `README.md` - 客服回饋管理表格，POST `/api/v1/feedback/sport/topics` |
| 服務角色 | `feedback-detail.md` - feedbackservice 為 `feedback` keyspace 唯一 owner |
| DB 寫入限制 | `feedback-detail.md` - `topics_sport.id` 建立後不可修改；`enabled` 僅由管理 API 更新 |
| DB Schema | `feedback.md` - `topics_sport` 主鍵 `id`，欄位包含 `enabled`, `sort`, `name` |
| 服務責任 | `README.md` - pricebackendservice 職責為「BFF 聚合層，不直接存取資料庫」 |
| 相依關係 | `README.md` - pricebackendservice 相依 `feedbackservice` 提供客服主題/訊息功能 |