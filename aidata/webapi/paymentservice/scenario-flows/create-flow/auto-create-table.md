# 自動建立 Cassandra 表

## 1. 場景目的

系統管理員（例如維運人員或自動化腳本）透過 `POST /api/v1/system/autocreatetable` 端點，在 Cassandra `payment` keyspace 中自動建立或驗證支付服務所需的所有必要表格。此流程用於服務初次部署、Cassandra 集群重建後，或需要手動確保表格結構存在時。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/system/autocreatetable` | 自動建立 Cassandra 表 |
| - | 需人工確認：是否有RequestBody？ | 需人工確認 |

根據 `README.md`，此 API 需要驗證 (`✅`)，屬於系統工具的一部分。

---

## 3. 流程總覽

1. 接收 API 請求。
2. 驗證請求者身份與權限。（需人工確認：需要哪些權限？）
3. 連接到 Cassandra 集群。
4. 針對 `payment` keyspace 中定義的所有必要表格，逐一執行 `CREATE TABLE IF NOT EXISTS` 語句。
5. 檢查每個表格建立的結果或任何潛在錯誤。
6. 回傳操作結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 | Evidence |
|---|---|---|---|---|
| 1 | Controller | 需人工確認 | 接收 HTTP POST 請求。 | 需人工確認。OpenAPI 未定義此端點的具體規格。 |
| 2 | Controller | 需人工確認 | 調用驗證框架 (`ECFramework.ECService`) 進行身份驗證。 | 需人工確認。`README.md` 中 `autocreatetable` 標記為需要驗證。 |
| 3 | Controller | 需人工確認 | 調用相應的 Service 層方法。 | 需人工確認。 |
| 4 | Service | 需人工確認 | 獲取 Cassandra 會話 (Session)。 | 需人工確認。 |
| 5 | Service | 需人工確認 | 對 `payment` 相關表格的 DDL 語句列表進行迭代。 | 需人工確認。此列表可能來自於配置或硬編碼，對應 `payment.md` 中的表。 |
| 6 | Service/DAL | 需人工確認 | 執行 `session.Execute(statement)`。 | 需人工確認。 |
| 7 | Service | 需人工確認 | 記錄結果或任何異常。 | 需人工確認。可能使用 Kafka + Cassandra 進行日誌記錄。 |
| 8 | Controller | 需人工確認 | 回傳成功或失敗的 HTTP Response。 | 需人工確認。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 | Evidence |
|---|---|---|---|---|
| DB | Cassandra `payment` keyspace | Write (DDL) | 建立表格的 schema 定義。 | 場景描述與 `README.md` 均指出目標為 Cassandra `payment` keyspace。 |
| DB | Cassandra `payment` keyspace | Read | 檢查表格是否已存在 (透過 `IF NOT EXISTS`)。 | Cassandra 的標準 `CREATE TABLE IF NOT EXISTS` 行為。 |
| Queue/Kafka | 需人工確認 | Publish | 發送操作日誌。 | 需人工確認。`README.md` 提到日誌使用 Kafka + Cassandra。 |

---

## 6. 重要規則

- **權限限制**：
  - API 需要驗證，具有系統管理員權限才可呼叫。 (`README.md` 中的 "✅" 標記)
  - 需人工確認：具體的角色或策略名稱。
- **操作範圍**：
  - 根據場景，操作限定在 `payment` keyspace。
  - 需人工確認：是否會建立 `payment` keyspace 本身，還是只建立其中的 tables？
- **Idempotency**：
  - 操作應是冪等的，即多次呼叫不應導致錯誤，DDL 語句應使用 `IF NOT EXISTS`。
- **不可回傳欄位**：
  - 無。此為管理操作，不涉及業務數據查詢。
- **TTL 規則**：
  - 無。此操作與數據 TTL 無關。
- **Transaction 規則**：
  - 無。Cassandra 的 DDL 操作不是事務性的。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| **請求未經驗證或權限不足。** | 回傳 HTTP 401 Unauthorized 或 403 Forbidden 錯誤。 |
| **Cassandra 集群無法連接。** | 回傳 HTTP 500 Internal Server Error，並記錄連線超時或被拒的日誌。 |
| **DDL 語句語法錯誤。** | 回傳 HTTP 500 Internal Server Error，並在服務端記錄包含語法錯誤原因的日誌。 |
| **Cassandra 回報 schema 不一致或資源不足。** | 回傳 HTTP 500 Internal Server Error，具體原因由 Cassandra 驅動程式回傳。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| `SYS-AC-01` | API Test | 使用有效的管理員 Token 向 `POST /api/v1/system/autocreatetable` 發送請求。 | HTTP 200 OK。Cassandra `payment` keyspace 中的所有表格都應存在。 |
| `SYS-AC-02` | Idempotency Test | 連續兩次呼叫 API。 | 兩次呼叫都應回傳 HTTP 200 OK，不產生任何錯誤。 |
| `SYS-AC-03` | Permission Test | 使用無效或無權限的 Token 呼叫 API。 | HTTP 401/403，表格不應受到影響。 |
| `SYS-AC-04` | Flow Test | 假設一個或多個表格已存在，再次呼叫 API。 | HTTP 200 OK。日誌應顯示 `IF NOT EXISTS` 跳過了已存在的表格。 |

---

## 9. 高風險區域

- **高風險 API**：`POST /api/v1/system/autocreatetable`。此操作會直接修改資料庫 schema，若使用不當（例如執行了 drop table 或錯誤的修改語句），會導致服務中斷。需人工確認：該端點是否僅執行 `CREATE TABLE`，還是會執行其他 DDL？
- **Cassandra 集群穩定性**：對生產環境集群發出 DDL 可能會引起 schema 不一致或其他短暫的性能影響。
- **安全風險**：若此端點被未經授權存取，可能被用來探測或破壞資料庫結構。

---

## 10. 常見錯誤

- **新人容易犯錯**：在本地開發環境未啟動 Cassandra 或配置錯誤連線資訊的情況下呼叫此 API。
- **AI 容易誤解**：認為此操作是同步的，沒有考慮到 Cassandra 的 schema 變更最終一致性帶來的延遲。
- **常見漏檢查項目**：操作完成後未在 Cassandra 中透過 `DESCRIBE KEYSPACE payment` 等命令驗證表格是否正確建立。
- **常見錯誤流程**：直接操作 Cassandra 建立表格，而非透過此 API，導致權限未被統一管理。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `README.md`: POST `/api/v1/system/autocreatetable` |
| API 權限 | `README.md`: 路由標記為 `✅` (需要驗證) |
| DB | `db/payment.md`: 定義 `payment` keyspace 及其所有表格的結構。 |
| DB | `db/payment-detail.md`: paymentservice 為 `payment` keyspace 的 owner。 |
| 架構 | `README.md`: 技術棧包含 Cassandra。 |
| **需人工確認** | `Controller`, `Service` 的實作類別/方法。 |
| **需人工確認** | 具體的 DDL 語句來源與執行邏輯。 |
| **需人工確認** | 服務如何處理 `payment` keyspace 的建立。 |
| **需人工確認** | 權限驗證的具體機制。 |