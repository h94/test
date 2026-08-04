# 刪除運動站台文章

## 1. 場景目的

提供後台管理人員或系統管理機制，能夠根據指定的文章 ID，從對應的球種運動站台文章表中，刪除一筆不再需要或有問題的站台文章。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| DELETE | `/api/v1/sportarticles/{id}` | 根據文章 ID 刪除指定文章 |

---

## 3. 流程總覽

1. 使用者（編輯人員或管理後台）發出刪除請求，指定路徑參數 `id`。
2. API Gateway 驗證請求是否包含有效的驗證資訊（由 `authService` 負責，newsservice 不處理憑證驗證）。
3. 請求通過驗證後，由 `newsservice` 的 Controller 接收。
4. Controller 將 `id` 傳遞給對應的 Service 層。
5. Service 層根據業務邏輯，判斷該文章儲存於哪一張動態表（`sports_{gameType}`），並呼叫 Data Provider（Provider 層）。
6. Provider 層組裝 Cassandra 的 DELETE CQL 語句，並針對目標表執行刪除。
7. Cassandra 完成刪除操作並回傳結果。
8. Service 層向上回傳成功或失敗的結果。
9. Controller 回傳 HTTP 狀態碼（例如 200 OK 或適當的錯誤碼）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | 推測為 `SportArticlesController.DeleteArticle` | 接收 `{id}` 參數，呼叫 Service 層的刪除方法。 |
| 2 | Service | 推測為 `ISportArticleService` 的刪除方法 | 執行業務邏輯：驗證 ID 格式、確認文章存在性（需人工確認是否檢查），並調用 Provider 層。 |
| 3 | Provider | 推測為 `INewsDataProvider` 的刪除方法 | 對 `sports_{gameType}` 動態表組裝並執行 DELETE CQL 指令。 |
| 4 | DB | Cassandra | 執行實際的物理刪除。 |

> **需人工確認**: 由於提供的原始碼分析資料主要集中於 `IAINewsService` / `IAINewsDataProvider`，缺乏 `SportArticlesController` 和相關 Service/Provider 的明確程式碼證據，此流程基於 API 結構和 DB 結構推斷。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `sports_{gameType}` (動態表) | Delete | 根據主鍵 `id` 刪除指定的站台文章記錄。 |

> **重要提示**: 本服務**未使用 Redis** 作為快取，也**未使用 Kafka** 或任何訊息佇列。因此，刪除操作是直接且立即反應在資料庫層。

---

## 6. 重要規則

- **權限限制**: 所有 API 端點均需要驗證（由 API Gateway 預先處理），只有經過授權的後台使用者才能執行刪除操作。
- **動態表名關鍵性**: 必須根據文章 ID 或其上下文，精確定位到對應的 `sports_{gameType}` 表（例如 `sports_football`）。根據 `newsservice-detail.md` 規範，不能模糊查詢，調用方必須明確指定 `gameType`。
- **不可恢復性**: 刪除操作通常是永久性的，請求應謹慎觸發，可能需要在前端有二次確認機制（實作細節）。
- **不可回傳欄位**: 雖然此為刪除操作，但在查詢或驗證存在性時，應避免回傳或記錄 `content`, `link`, `tag` 等受限制的欄位。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求未通過驗證或缺少憑證 | 由 API Gateway 攔截，返回 401 Unauthorized。 |
| 提供的文章 ID 格式無效 | 返回 400 Bad Request 或由 Service 層捕捉例外。 |
| 提供的文章 ID 在對應的動態表中不存在 | 返回 404 Not Found 或 200 OK（需人工確認：是否採取冪等設計，還是明確回報資源不存在）。 |
| 因為動態表名錯誤導致 DB 操作失敗 | 系統拋出例外，返回 500 Internal Server Error。建議在日誌中記錄詳細錯誤。 |
| Cassandra 連線逾時或暫時不可用 | 系統拋出例外，返回 503 Service Unavailable。 |

> **需人工確認**: 當 ID 不存在時的具體 HTTP 回應狀態碼，以及是否實現冪等性，需要進一步從程式碼中確認。

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC-DEL-01 | API Test | 使用有效的文章 ID 發送 DELETE 請求 | HTTP 200 OK，且後續以相同 ID 查詢應返回 404。 |
| TC-DEL-02 | Permission Test | 未帶驗證 Header 發送 DELETE 請求 | HTTP 401 Unauthorized。 |
| TC-DEL-03 | Flow Test | 使用不存在的文章 ID 發送 DELETE 請求 | 根據規格，返回 HTTP 404 或 200（需確認）。 |
| TC-DEL-04 | API Test | 使用無效格式的 ID 發送請求 | HTTP 400 Bad Request。 |
| TC-DEL-05 | Integration Test | 模擬 Cassandra 連線失敗 | 系統應記錄錯誤日誌並返回 HTTP 500 或 503，不應崩潰。 |

---

## 9. 高風險區域

- **高風險 API**: `DELETE /api/v1/sportarticles/{id}` 直接刪除資料，為高風險操作，若誤觸或授權不當，可能導致前端顯示異常或資料永久丟失。
- **資料一致性**: 因為沒有使用快取，所以沒有快取一致性問題。風險在於其他服務（如負責抓取的 `crawlerService`）是否會在短期內將其重新寫回，需考慮業務邏輯。
- **Transaction**: Cassandra 不支援跨表交易，本操作僅涉及單一表中的單一主鍵，相對安全。

---

## 10. 常見錯誤

- ❌ **新人容易犯錯**: 認為刪除後會觸發其他服務的同步（例如通知、日誌），實際上此 API 職責單一，僅負責從 DB 中移除記錄。
- ❌ **AI 容易誤解**: 混淆 `DELETE /api/v1/sports/{gameType}` 與 `DELETE /api/v1/sportarticles/{id}`，前者可能為批量刪除該球種的所有新聞，後者為刪除**單一站台文章**。
- ❌ **常見漏檢查項目**: 刪除前未確認文章是否存在，或錯誤處理 Cassandra 的回應，導致認為刪除成功但實際上沒有刪除到目標。
- ❌ **常見錯誤流程**: 試圖用不包含 `gameType` 資訊的 `id` 直接操作一個確定的表，開發者需要先有邏輯找出對應的動態表。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由與方法 | `webapi/newsservice/README.md` > 站台文章 > DELETE `/api/v1/sportarticles/{id}` |
| 權限驗證 | `webapi/newsservice/README.md` > 需要驗證 ✅ |
| 動態表寫入規範 | `webapi/newsservice/newsservice-detail.md` > 寫入限制 > `sports_{gameType}` 動態表 |
| 服務不負責範圍 | `webapi/newsservice/newsservice-detail.md` > 本服務不負責 > 用戶認證與授權、原始新聞抓取 |
| 無 Redis / Queue | `webapi/newsservice/newsservice-detail.md` > Redis, 及未提及任何 Queue 使用 |
| 表主鍵 | `Source code semantics` > `sports_$gameType` > `id` 為文章唯一ID，主鍵 |