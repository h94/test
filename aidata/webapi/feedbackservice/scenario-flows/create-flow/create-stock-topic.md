# 管理員建立股票主題

## 1. 場景目的

管理員在後台新增股票站點的反饋主題，將主題資料寫入 `topics_stock` 表，供使用者提交反饋時選用。

---

## 2. 入口 API

需人工確認：由於未提供 OpenAPI 文件，以下為推測之 API 規格。

| Method | Path | 說明 |
|--------|------|------|
| POST   | /api/feedback/stock/topic | 管理員建立新主題 |

---

## 3. 流程總覽

1. 管理員通過管理後台發起建立主題請求
2. 系統驗證操作者身份與權限（需為管理員角色）
3. 檢查請求參數（主題名稱、排序等）
4. 生成唯一主題 ID
5. 寫入 `topics_stock` 表（ScyllaDB）
6. 回傳操作結果（成功 / 失敗）

---

## 4. 程式流程

需人工確認：未提供 Controller / Service 層代碼，以下為依據已知語意推測之呼叫鏈。

| 順序 | Layer      | Class / Method           | 動作                                               |
|------|------------|--------------------------|---------------------------------------------------|
| 1    | Controller | `StockTopicController.CreateTopic` | 接收 HTTP 請求，轉交 Service                         |
| 2    | Service    | `StockTopicService.CreateTopic`    | 執行業務邏輯：驗證權限、產生 ID、組裝資料             |
| 3    | Provider   | `StockTopicDataProvider.AddTopic`  | 執行 CQL `INSERT` 至 `topics_stock` 表             |
| 4    | Transfer   | `StockTopicTransfer.InsertTopic`   | 建構 CQL 語句（參數化）                             |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源         | 操作  | 用途                     |
|------|-------------|-------|--------------------------|
| DB   | `topics_stock` | Write | 新增一筆主題記錄         |

目前並無 Redis / Kafka / Queue 使用證據，該流程僅為同步寫入 ScyllaDB。

---

## 6. 重要規則

- **權限限制**：僅管理員可執行，需由驗證中間件檢查角色
- **欄位限制**：
  - `ID`：必須由服務端生成（例如 GUID），不可由前端傳入
  - `Name`：為純文字，不支援多語言（與體育站點不同，見 source code 語意）
  - `Enabled`：新增時預設應為 1（啟用）
  - `Sort`：整數，需≥0，不可為負
- **不可暴露資料**：無敏感欄位，但回應中不應包含內部生成的 ID 之格式細節（可由明文展示）
- **不可修改欄位**：`ID` 一旦寫入即不可變更
- **Transaction 規則**：ScyllaDB 不支援傳統 RDBMS 的事務，此處為單表 INSERT，無特殊 transaction 需求
- **TTL / Retry**：未觀察到相關機制；若寫入失敗，應由呼叫端重試，並確保錯誤記錄於日誌

---

## 7. 錯誤情境

| 情境                           | 預期結果                               |
|--------------------------------|----------------------------------------|
| 未登入或無效 token              | 回傳 401，拒絕操作                     |
| 權限不足（非管理員）           | 回傳 403                               |
| 請求參數缺少 `Name`            | 回傳 400，訊息提示欄位必填             |
| 請求參數 `Sort` 非整數或為負   | 回傳 400，提示格式錯誤                 |
| ScyllaDB 無法連線              | 回傳 500，並記錄錯誤，不回傳資料庫細節 |
| 主題 ID 重複（極少發生）       | 回傳 500，並記錄「Duplicate key」錯誤  |

---

## 8. 測試重點

| Test ID | 類型               | 情境                                   | 預期結果                           |
|---------|--------------------|----------------------------------------|-------------------------------------|
| T1      | Permission Test    | 一般使用者 token 呼叫 API              | 回傳 403 Forbidden                  |
| T2      | API Test           | 缺少 Name 欄位                         | 回傳 400 Bad Request                |
| T3      | API Test           | Sort 為 -1                             | 回傳 400 Bad Request                |
| T4      | Integration Test   | 正常管理員請求，寫入 DB                | 回傳 200 / 201，資料成功寫入 topics_stock |
| T5      | Integration Test   | 重複提交（相同參數但不同 ID）         | 應成功建立兩筆不同 ID 主題         |
| T6      | Flow Test          | 寫入後立即查詢啟用主題列表            | 新主題出現在列表中，Enabled=1      |

---

## 9. 高風險區域

- **高風險 table**：`topics_stock` 為直接操作表，若 ID 生成邏輯錯誤可能導致主鍵衝突，需確認 GUID 機制。
- **錯誤流程**：若需確保主題名稱唯一性，目前未見代碼實作 unique constraint；若重複名稱可能造成使用者混淆，需人工確認是否需防重名。
- **無 Queue / Cache 一致性問題**：此為簡單寫入，風險較低。
- **Idempotency**：API 本身不提供 idempotency key，重複請求會新增多筆，屬設計選擇，可接受。

---

## 10. 常見錯誤

- **新人易犯錯**：直接由前端傳入 ID，而非由後端生成。
- **AI 易誤解**：可能誤認為股票主題支援多語言名稱（類似體育站點），但基於 `StockTopic.Name` 語意為純文字，不應使用 Map 結構。
- **常見漏檢查**：未驗證 Sort 欄位型別與範圍，導致非預期值寫入 DB。
- **常見錯誤流程**：未區分體育與股票站點的 DataProvider，誤寫入 `topics_sport`（ScyllaDB 不同 keyspace / table）。

---

## 11. Evidence

| 類型     | 來源                                                                       |
|----------|----------------------------------------------------------------------------|
| DB       | `stock.topics_stock`（來自 DB schema stock）                               |
| Table    | `topics_stock` 包含 `id`, `name`, `enabled`, `sort`（來自 source code semantics） |
| Semantics| `StockTopic.ID`, `StockTopic.Name`, `StockTopic.Enabled`, `StockTopic.Sort`（來自 phase1 code semantics） |
| 服務角色 | feedbackservice 為股票站點操作者（來自 db-usage stock 服務角色總覽）       |
| 備註     | feedbackservice 對 `topics_stock` 的寫入權限未於 db-usage 明確列出，但由語意可推斷其具寫入能力，此處需人工確認實際權限設定 |