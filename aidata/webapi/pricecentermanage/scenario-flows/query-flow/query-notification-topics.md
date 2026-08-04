# 查詢通知主題列表

## 1. 場景目的
後台管理員查詢所有已啟用的推播通知主題，以利後續進行通知訊息的建立與管理。支援使用 Redis 快取以提升查詢效能，避免高頻讀取對 MySQL 造成壓力。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sport/notifications/topics` | 查詢所有通知主題，可選從 Redis 快取讀取 |

**查詢參數**：
| 參數 | 類型 | 預設 | 說明 |
|---|---|---|---|
| cacheData | boolean | true | `true`：從 Redis 快取讀取；`false`：直接查詢 MySQL |

---

## 3. 流程總覽

1. 後台管理員透過管理介面請求通知主題列表。
2. 系統驗證管理員權限（需登入後台）。
3. 根據 `cacheData` 參數決定資料來源：
   - 若為 `true`：從 Redis 讀取 `NotificationTopics` Hash。
   - 若為 `false` 或 Redis 未命中：查詢 MySQL `notification_topics`。
4. 資料查詢時僅回傳 `Enabled = 1` 的啟用主題。
5. 若從 MySQL 查詢，將結果寫入 Redis 快取（無 TTL）。
6. 回傳主題列表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `NotificationController.GetTopics` | 接收請求，讀取 `cacheData` 參數，呼叫 Service |
| 2 | Service | `NotificationService.GetTopics` | 判斷是否從 Redis 讀取；若需要查 DB，呼叫 Provider |
| 3 | Provider | `NotificationProvider.GetEnabledTopics` | 查詢 MySQL `notification_topics WHERE Enabled = 1 ORDER BY Seq` |
| 4 | Provider | `RedisProvider.GetHashAll("NotificationTopics")` | 從 Redis 讀取完整 Hash |
| 5 | Service | `NotificationService.GetTopics` | 若從 DB 取得，將結果序列化後寫入 Redis `NotificationTopics` Hash |
| 6 | Controller | `NotificationController.GetTopics` | 將 `SportTopicDTO` 列表回傳給前端 |

> **需人工確認**：`NotificationService` 與 `NotificationProvider` 的實際類別名稱以程式碼為準，本文件依慣例命名推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | MySQL `sport.notification_topics` | Read | 查詢 `Enabled = 1` 的所有主題，依 `Seq` 排序 |
| Cache | Redis `NotificationTopics` | Read | 讀取 Hash 中所有已啟用的主題快取 |
| Cache | Redis `NotificationTopics` | Write | 當從 DB 查詢後，將結果寫入 Hash，field = Tid, value = SportTopic JSON |
| Queue | — | — | 本流程不涉及 Kafka / Queue 操作 |

---

## 6. 重要規則

- **權限限制**：需通過 ECFramework 驗證（後台管理員權限）。
- **狀態過濾**：僅回傳 `Enabled = 1` 的主題。不可回傳已停用 (`Enabled = 0`) 的主題。
- **快取一致性**：
  - 當 `notification_topics` 的資料發生變更（新增、更新、停用）時，必須**主動刪除** Redis 的 `NotificationTopics` Key，以確保下次查詢能取得最新資料。
  - 快取無 TTL，屬於永久型快取，完全依賴主動失效機制。
- **排序規則**：查詢結果依 `Seq` 欄位遞增排序。
- **不可回傳欄位**：`NameMap`、`IconPath`、`IconColorCode` 等欄位雖可回傳，但須注意內容不含惡意腳本（XSS 防範）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未登入或 Token 無效 | 回傳 HTTP 401 Unauthorized |
| 後台管理員權限不足 | 回傳 HTTP 403 Forbidden |
| Redis 連線失敗或逾時 | 應 fallback 至 MySQL 查詢，不可直接報錯 |
| MySQL 查詢失敗或逾時 | 回傳 HTTP 500 Internal Server Error |
| Redis 寫入失敗（從 DB 查詢後） | 記錄錯誤日誌，但查詢仍回傳成功（降級處理） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| NT-01 | API Test | `GET /api/v1/sport/notifications/topics?cacheData=true`，Redis 有資料 | 回傳 200，內容為 Redis 快取資料 |
| NT-02 | API Test | `GET /api/v1/sport/notifications/topics?cacheData=false` | 回傳 200，內容為 MySQL 即時資料 |
| NT-03 | Flow Test | 停用某主題後查詢 | 該主題不出現在列表中 |
| NT-04 | Integration Test | 查詢成功後 Redis 有對應 Key | `NotificationTopics` Hash 存在，且內容與 DB 一致 |
| NT-05 | Error Test | 停用 Redis 服務後查詢 | 仍可從 MySQL 查詢成功，不影響 API 回應 |
| NT-06 | Permission Test | 使用未登入或一般會員 Token 請求 | 回傳 401 或 403 |

---

## 9. 高風險區域

- **Cache consistency（快取一致性）**：在其他 API（如建立、更新主題）修改 `notification_topics` 後，若忘記刪除 `NotificationTopics` 快取，前台將顯示過時資料。
- **無 TTL 快取**：使用無 TTL 快取策略，高度依賴主動失效機制。若失效邏輯有缺陷，快取將永久不一致。
- **併發讀寫**：高併發下，若多個請求同時查詢 DB 並嘗試寫入 Redis，可能造成短暫的資源浪費（Cache Stampede），但不會造成資料錯誤。

---

## 10. 常見錯誤

- ❌ **查詢時忘記過濾 `Enabled=1`**：可能將已停用的主題一併回傳，造成前端顯示錯誤。
- ❌ **修改主題（PUT）後未刪除 Redis 快取**：導致後台顯示舊的主題名稱或設定。
- ❌ **查詢時 Redis 失敗就直接報錯**：未實作 fallback 至 MySQL 的機制，降低系統可用性。
- ❌ **在 API 回傳中加入非必要的內部欄位**：如內部註記或未清理的敏感資訊。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `GET /api/v1/sport/notifications/topics` |
| API Parameter | `cacheData` (boolean, default true) |
| DB | MySQL `sport.notification_topics` |
| Redis Cache | `NotificationTopics` (Hash, field=tid) |
| Read Rule | `WHERE Enabled = 1 ORDER BY Seq` |
| Write Rule | 建立/更新/停用主題時需 `DEL NotificationTopics` |
| Permission | ECFramework 後台管理員驗證 |
| Code | `NotificationController.GetTopics`（推測） |
| Code | `NotificationService.GetTopics`（推測） |
| Code | `RedisProvider.GetHashAll("NotificationTopics")`（推測） |