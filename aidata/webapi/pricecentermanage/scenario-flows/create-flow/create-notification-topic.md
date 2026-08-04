# 建立通知主題

## 1. 場景目的

管理後台人員建立新的推播通知主題。系統會將主題資料寫入 MySQL `sport.notification_topics` 表，並立即刪除 Redis 中的通知主題快取，確保前台能即時取得最新清單。建立後的主題預設為啟用狀態。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/sport/notifications/topics` | 建立新的通知主題 |

- 需要驗證：✅
- Request Body：`SportTopicDTO` (JSON)
- 權限：管理後台人員

---

## 3. 流程總覽

1. 驗證操作者權限，確認擁有管理後台角色。
2. 接收 `SportTopicDTO` Request Body，包含主題 ID、名稱、圖示等欄位。
3. 寫入一條新記錄至 MySQL `sport.notification_topics`，預設 `Enabled = 1`。
4. 更新成功後，立即刪除 Redis 快取 `NotificationTopics`。
5. 回傳成功（200 OK）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware | `ECFramework.ECService` | 驗證操作者身分，確認具備後台權限。 |
| 2 | Controller | `NotificationController`（推測） 或 `SportController` 相關子路由 | 接收並反序列化 `SportTopicDTO`，呼叫對應 Service。 |
| 3 | Service | `NotificationService`（推測） 或其內部方法 | 呼叫 Provider 執行資料寫入。 |
| 4 | Provider | `ISportNotificationProvider`（推測） 實作類 | 執行 SQL `INSERT INTO notification_topics`。 |
| 5 | Provider | 同上 | 寫入成功後，執行 `IDatabase.Del.Redis("NotificationTopics")` 刪除快取。 |
| 6 | Controller | - | 回傳 HTTP 200。 |

**需人工確認**：Controller 與 Service 的實際類別名稱與呼叫鏈。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (MySQL Sport) | `notification_topics` | INSERT | 新增一筆通知主題記錄，`Enabled=1`。 |
| Redis (SportCache) | `NotificationTopics` | DEL | 主題清單異動後，立即刪除整個 Hash 快取，觸發下次查詢回源 DB。 |

---

## 6. 重要規則

- **權限限制**：僅限管理後台（Admin）角色操作；透過 ECFramework 統一驗證。
- **欄位限制**：
  - `ID`：varchar(10)，不可重複。
  - `NameMap`：text，應為多語系 JSON 字串。
  - `IconPath` / `IconColorCode`：text，需符合 UI 規範。
- **預設狀態**：INSERT 時必須設定 `Enabled = 1`（啟用）。
- **TTL 規則**：`NotificationTopics` 快取為永久，由 DB 異動時手動刪除。**不可僅依賴 TTL**。
- **Queue**：此流程不涉及 Message Queue。
- **不可修改欄位**：`UpdateTime` 應由系統自動填入寫入當下時間戳（bigint）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求未帶有效驗證 Token，或權限不足（非管理員） | 回傳 401 Unauthorized 或 403 Forbidden。 |
| Request Body 缺少必填欄位（如 ID、NameMap） | 回傳 400 Bad Request，訊息提示缺少特定欄位。 |
| 主題 `ID` 已存在（重複新增） | DB 寫入失敗，回傳 409 Conflict 或 500，需提供有意義的錯誤訊息。 |
| Redis 快取刪除失敗（如連線瞬斷） | **不可影響主題建立結果**。應記錄 Error Log，但對 Client 仍回傳 200 OK。 |
| DB 寫入失敗（如連線超時、Table Lock） | 回傳 500 Internal Server Error。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| NT-01 | API Test | 管理員帶完整正確的 `SportTopicDTO` 呼叫 API。 | 回傳 200；DB 新增一筆 `Enabled=1` 的記錄；Redis `NotificationTopics` 被刪除。 |
| NT-02 | Permission Test | 一般使用者或未驗證請求呼叫 API。 | 回傳 401 或 403。 |
| NT-03 | API Test | 欄位格式錯誤（如 ID 超過 10 字元）。 | 回傳 400，錯誤訊息清楚說明違規欄位。 |
| NT-04 | Flow Test | 模擬 Redis 連線失敗後再呼叫 API。 | API 仍回傳 200，且 DB 記錄正確新增；Log 中可觀察到 Redis 寫入或刪除失敗的錯誤。 |

---

## 9. 高風險區域

- **高風險 table**：`sport.notification_topics` — 直接影響前台所有推播功能的顯示。
- **Cache consistency**：若新增主題後 Redis 快取刪除失敗，前台將無法看到新主題。需有監控告警 Redis 操作失敗。
- **Transaction**：DB 與 Redis 操作為非強制 Transaction，Redis 刪除失敗不應回滾 DB，但需確保可透過管理後台手動清除快取。

---

## 10. 常見錯誤

- ❌ **忘記刪除 Redis 快取**：新增或修改主題後未執行 `DEL NotificationTopics`，導致前台看不到最新資料。
- ❌ **直接操作 Redis 而未先更新 DB**：快取更新後 DB 寫入失敗，造成前端看到不存在的主題。
- ❌ **未驗證 `ID` 格式與唯一性**：導致 SQL Exception，且錯誤訊息對使用者不友善。
- ❌ **Request Body 未做欄位校驗**：將無效的 JSON、過長的文字直接寫入 DB。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/sport/notifications/topics` (from README & OpenAPI) |
| DB | `sport.notification_topics` (from README, DB Schema) |
| Redis | `NotificationTopics` Hash (from pricecentermanage-detail.md Redis section) |
| Rule: Enabled default=1 | `pricecentermanage` is writer, default is enabled (from DB detail sport `notification_topics.Enabled`) |
| Rule: Cache DEL on write | "DB 更新時 DEL" (from pricecentermanage-detail.md Redis section) |
| Auth | "需要驗證" (from README API table) |