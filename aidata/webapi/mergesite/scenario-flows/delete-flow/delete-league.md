# 刪除聯盟

## 1. 場景目的

提供後台管理員透過 mergesite WebAPI 移除指定球種（gameType）下的聯盟（LID），並觸發 PriceCenterService 執行實際刪除與關聯資料清理。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| DELETE | `/api/leagues/{gameType}/{lid}` | 刪除指定球種的聯盟，需要驗證（ECCore 3.0.2） |

> **Evidence**：OpenAPI paths `/api/leagues/{gameType}/{lid}` delete method（OpenAPI 文件片段）

---

## 3. 流程總覽

1. 後台管理員發起 DELETE 請求，攜帶 `gameType` 與 `lid`。
2. mergesite 驗證使用者身份（ECCore）。
3. mergesite 透過 Gateway 呼叫 **PriceCenterService** 的聯盟刪除 API（預期為 REST）。
4. PriceCenterService 執行業務邏輯：檢查聯盟狀態、移除聯盟主資料、連動刪除 SiteLeague 及相關合併對照。
5. 成功後 mergesite 可選擇性寫入使用者操作紀錄（`/api/system/logs/action` 或 Kafka log）。
6. 回傳 `ServiceMsgCode` 成功訊息。

> **需人工確認**：mergesite 是否在刪除成功後自動產生操作記錄，或由前端另行呼叫 log API。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `GameController.DeleteLeague(gameType, lid)` | 接收 DELETE 請求，驗證權限 |
| 2 | Service | `MergeService.DeleteLeague(gameType, lid)` | 組裝參數，呼叫 PriceCenterService Gateway |
| 3 | Provider/Client | `PriceCenterServiceClient.DeleteLeague(gameType, lid)` | 發送 HTTP DELETE 至 PriceCenterService |
| 4 | PriceCenterService | 內部 API `/leagues/{gameType}/{lid}` (DELETE) | 執行資料庫刪除、關聯資料清理 |
| 5 | Service | `MergeService` 接回回應 | 判斷 PriceCenterService 回傳狀態 |
| 6 | （可選） | `ActionLogService` | 寫入操作日誌（Kafka 或 `/api/system/logs/action`） |
| 7 | Controller | 回傳 `ServiceMsgCode` | 封裝成功訊息 |

> **Evidence**：
> - Controller / Service 層級推測基於 ASP.NET Core 常見分層，實際類別名需人工確認（無直接程式碼片段）。
> - 對 PriceCenterService 依賴來自 README「服務相依」：`PriceCenterService（Gateway: 192.168.55.60）`。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| 外部服務 | PriceCenterService API | DELETE | 實際刪除聯盟及關聯資料（資料庫操作由 PriceCenterService 負責，mergesite 無直接 DB 寫入） |
| Queue | Kafka（192.168.55.60） | Publish | 寫入應用程式 Log（操作紀錄） — **需人工確認**：是否由此 API 直接觸發 |

> **需人工確認**：
> - mergesite 對 PriceCenterService 的具體 API 合約（如回傳格式、錯誤碼）。
> - 是否使用 Redis 快取聯盟資訊，刪除時是否需要 invalidate cache。

---

## 6. 重要規則

- **權限限制**：API 需要 ECCore 驗證，且僅限後台管理員角色（規則待確認具體授權策略）。
- **不可恢復**：聯盟一經刪除，資料可能不可逆（PriceCenterService 端行為）。
- **關聯資料刪除**：PriceCenterService 應確保一併移除 SiteLeague 對應、自動比對紀錄等，避免孤兒資料。
- **操作記錄**：建議每次刪除皆記錄操作者、時間、目標聯盟（gameType + lid），符合稽核需求。
- **重複刪除**：PriceCenterService 應對已不存在的聯盟返回恰當錯誤，mergesite 須正確轉發。
- **不可暴露內部資源**：mergesite 不應回傳 PriceCenterService 內部錯誤細節。

> **Evidence**：
> - 驗證要求來自 README 中所有聯盟管理 API 皆標示「需要驗證」。
> - PriceCenterService 相依說明來自 README「服務相依」。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未登入或 Token 無效 | 401 Unauthorized。 |
| 使用者無後台管理權限 | 403 Forbidden。 |
| 聯盟 `lid` 不存在或已刪除 | PriceCenterService 回傳錯誤碼，mergesite 轉換為 404 或 422。 |
| PriceCenterService 無法連線（timeout） | 502/504，需有重試或 fallback。 |
| PriceCenterService 回傳業務規則拒絕（如聯盟仍有進行中賽事） | 將特定業務錯誤碼轉為有意義的 HTTP status（如 409 Conflict）。 |
| gameType 參數格式不合法 | 400 Bad Request。 |

> **需人工確認**：實際 HTTP status code 與錯誤格式，需參考 PriceCenterService 合約。

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| DEL-01 | Permission Test | 使用無管理權限的 Token 呼叫 | 403 Forbidden。 |
| DEL-02 | API Test | 刪除存在且可刪除的聯盟 | 200 OK，且後續查詢不得顯示該聯盟。 |
| DEL-03 | API Test | 嘗試刪除不存在的 `lid` | 404 或對應業務錯誤。 |
| DEL-04 | Flow Test | 刪除後檢查 SiteLeague 是否一併清除 | 可透過 `GET /api/siteleagues/{gameType}?lid={lid}` 確認回傳空。 |
| DEL-05 | Integration Test | 模擬 PriceCenterService 回應 500 | mergesite 應回傳 502，並記錄錯誤 log。 |
| DEL-06 | Log Test | 成功刪除後驗證操作記錄有正確內容 | 檢查 Kafka log 或 action log API。 |

---

## 9. 高風險區域

- **高風險 Table**：本服務無直接 Table，但 PriceCenterService 可能操作 Cassandra 的聯盟/站台聯盟相關表（如 `siteleagues` 等，未在本文件範圍內）。
- **跨服務資料同步**：mergesite 僅為觸發端，最終一致性由 PriceCenterService 保證，需確認刪除後是否有其他服務（如賽事查詢、賠率服務）的快取需同步失效。
- **Cache consistency**：若其他服務快取聯盟資訊，需具備失效機制。
- **Idempotency**：重複呼叫 DELETE 應返回相同結果（如已刪除則明確提示），避免誤報為成功而隱匿錯誤。

---

## 10. 常見錯誤

- **直接操作 DB**：新人可能誤以為 mergesite 有資料庫，實則所有資料操作都透過 PriceCenterService，嚴禁繞道。
- **忽略操作記錄**：AI 或開發者可能省略寫入 Log，不符稽核要求，應確保每次刪除都有紀錄。
- **未確認關聯資料清除**：若 PriceCenterService 刪除不全，可能殘留 SiteLeague 造成前端混亂，測試需涵蓋此項。
- **假設 API 一定成功**：mergesite 應妥善處理 PriceCenterService 的各種錯誤，並提供可讀訊息給前端。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI `DELETE /api/leagues/{gameType}/{lid}` |
| 服務相依 | README「服務相依」：PriceCenterService (Gateway: 192.168.55.60) |
| 驗證要求 | README 聯盟管理區塊所有 API 標示「需要驗證」 |
| 操作記錄 | README 系統 API：`POST /api/system/logs/action`；Kafka 用於 log |
| 無直接 DB | README「此服務無直接資料庫，資料讀寫均透過 PriceCenterService 進行」 |
| 程式流程 | 推測自 ASP.NET Core 慣例，實際類別需人工確認 |