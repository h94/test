# 查詢運動主題列表

## 1. 場景目的

此場景讓運動站點的使用者或前端頁面取得所有已啟用的體育反饋主題列表，用於顯示主題選單或選擇反饋類別。系統會依主題排序顯示，並提供多語言名稱。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | /api/Sport/GetTopics (需人工確認確切路由) | 查詢所有已啟用的體育反饋主題 |

---

## 3. 流程總覽

1. 接收查詢請求（無需身份驗證，為公開資源）。
2. 查詢 `topics_sport` 表，過濾 `enabled = 1` 的記錄。
3. 依 `sort` 欄位升冪排序主題。
4. 回傳主題列表，每個主題包含 `id`、多語言 `name`（MAP 結構）、`sort`。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SportController.GetTopics()` (需人工確認) | 接收 HTTP GET 請求，呼叫 Service。 |
| 2 | Service | `SportTopicService.GetEnabledTopics()` (需人工確認) | 呼叫 Provider 取得 `enabled=1` 的主題資料。 |
| 3 | Provider | `SportTopicDataProvider.GetAllEnabled()` (需人工確認) | 執行 CQL 查詢 `topics_sport`，過濾並排序。 |
| 4 | Controller | `SportController.GetTopics()` | 將主題列表轉換為 JSON 格式並回傳。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (ScyllaDB) | `topics_sport` | Read | 查詢所有 `enabled = 1` 的運動主題。 |
| 無 | Redis / Cache | N/A | **需人工確認**：目前無明確證據顯示有使用快取。若主題列表不常變動，可考慮加入。 |
| 無 | Kafka / Queue | N/A | 此查詢流程不涉及非同步訊息傳遞。 |

---

## 6. 重要規則

- **權限限制**：為公開 API，無需驗證即可存取。
- **欄位限制**：
  - **查詢條件**：必須加上 `WHERE enabled = 1`，確保不顯示已停用的主題。
  - **回傳欄位**：僅回傳 `id`, `name`, `sort`。`Name` 為多語言 `MAP` 結構，例如 `{'zh-TW': '...', 'en': '...'}`。
- **不可暴露資料**：無。
- **TTL 規則**：無。
- **Transaction 規則**：無，此為單純讀取操作。
- **Retry 規則**：**需人工確認**，需確認 ScyllaDB Provider 是否有實作查詢失敗重試機制。
- **狀態值限制**：
  - `enabled` 欄位必須為 `1`（啟用）。
- **不可修改欄位**：此為唯讀查詢，無任何寫入行為。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| DB 無任何啟用主題 (`enabled=1` 的記錄數為 0) | 回傳 HTTP 200，但 `topicList` 為空陣列 `[]`。 |
| ScyllaDB 連線失敗或查詢逾時 | 回傳 HTTP 500 Internal Server Error 或適當的錯誤訊息。 |
| `topics_sport` 表不存在 | 因啟動時會自動建表，此情境不應發生；若發生則回傳 500。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| FT-TOPIC-01 | Flow Test (正常) | 資料庫中存在多筆 `enabled=1` 的主題 | 成功回傳所有啟用主題，並依 `sort` 升冪排列。 |
| FT-TOPIC-02 | Flow Test (過濾) | 資料庫中包含 `enabled=0` 與 `enabled=1` 的主題 | 只回傳 `enabled=1` 的主題。 |
| FT-TOPIC-03 | Flow Test (邊界) | 沒有任何 `enabled=1` 的主題 | 回傳成功的空陣列 `[]`。 |
| FT-TOPIC-04 | API Test (結構) | 檢查回傳的 JSON 結構 | 主題物件的 `name` 欄位應為多語言的鍵值對（MAP）。 |
| FT-TOPIC-05 | Permission Test | 未攜帶 token 請求 API | 請求成功，因為是公開 API。 |

---

## 9. 高風險區域

- **無**：此為低風險的唯讀查詢，不涉及任何交易、狀態變更或跨服務資料同步。
- **效能風險**：若主題數量極多，應注意查詢效能。目前有 `sort` 排序，需確認 ScyllaDB 叢集在此欄位上的查詢效率。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 在 CQL 查詢中沒有加入 `WHERE enabled = 1`，導致前端顯示已停用的主題。
- **AI 容易誤解**：
  - 可能會將 `topics_sport` 的名稱欄位當作純文字，而忽略其 `MAP<VARCHAR,VARCHAR>` 多語言結構。
  - 可能會自動推斷需要使用 `notification_topics` 表，而不是直接使用服務新建的 `topics_sport` 表。
- **常見漏檢查項目**：
  - 忘記驗證回傳的 JSON 中 `name` 欄位是否為物件（MAP），而非字串。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `SportController.GetTopics()` (依慣例推測) |
| DB | `topics_sport` |
| Table Schema | `SportFeedbackDataProvider.cs` (Phase1 分析) |
| Field Mapping | `SportTopic` 實體，`Name` 對應 `MAP<VARCHAR,VARCHAR>` (Phase0/1 語義分析) |
| Core Logic | 過濾條件 `WHERE enabled = 1` 來自 `SportTopic.Enabled` 語義定義 (Phase0/1 語義分析) |
| Service Role | `feedbackservice` 對 `sport` keyspace (ScyllaDB) 擁有讀寫權 (README) |

---
**建議新增文件**：
- **API 合約文件**：明確列出 `GetTopics` 的 request/response schema。
- **DB 查詢規範**：記錄對 `topics_sport` 表的查詢樣板，特別是 `WHERE enabled = 1` 的必要性。
- **暫無測試腳本**：需人工撰寫自動化測試。