# 查詢使用者操作紀錄

## 1. 場景目的

後台管理人員需依日期查詢使用者於後台執行的操作歷程，作為行為稽核、問題追蹤與責任歸屬的依據。此場景為唯讀查詢，不涉及任何寫入或狀態變更。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/system/logs/action/{date}` | 依日期取得使用者操作紀錄 |

---

## 3. 流程總覽

1. 管理後台發送 GET request，指定查詢日期
2. MergeSite 驗證呼叫者的登入狀態與後台權限
3. 依日期向 PriceCenterService 查詢操作紀錄
4. PriceCenterService 回傳符合日期的操作紀錄清單
5. MergeSite 將資料序列化後回傳給管理後台

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | 需人工確認 | 接收 GET request，驗證 token 與權限 |
| 2 | Controller | 需人工確認 | 提取 date 路徑參數 |
| 3 | Provider | 需人工確認 | 呼叫 PriceCenterService Gateway 查詢操作紀錄 |
| 4 | Transfer | 需人工確認 | 序列化 PriceCenterService 回傳資料為 DTO |
| 5 | Controller | 需人工確認 | 回傳操作紀錄清單 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | 需人工確認（PriceCenterService 內部儲存） | Read | 讀取使用者操作紀錄 |
| Queue | Kafka (192.168.55.60) | 無直接操作 | 操作紀錄寫入時透過 Kafka 傳遞，查詢時不涉及 |

> **注意**：MergeSite 本身無直接資料庫，操作紀錄的實際儲存與查詢均由 PriceCenterService 負責。詳情需人工確認 PriceCenterService 的操作紀錄儲存機制。

---

## 6. 重要規則

- **權限限制**：所有系統 API 需要驗證（`需要驗證`）
- **日期格式**：`{date}` 路徑參數格式依 PriceCenterService 定義，需人工確認
- **唯讀操作**：查詢使用者操作紀錄為唯讀，不可有任何寫入或狀態變更
- **不可回傳欄位**：應避免回傳內部實作細節，如內部路徑、IP 等非營運必要資訊
- **時區處理**：日期查詢的時區基準需明確，避免跨時區誤判，需人工確認

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未登入或 token 無效 | 回傳 401 Unauthorized |
| 使用者無後台權限 | 回傳 403 Forbidden |
| 日期格式不正確 | 回傳 400 Bad Request |
| 指定日期無操作紀錄 | 回傳 200 OK，空陣列 |
| PriceCenterService 無法連線 | 回傳 502 Bad Gateway 或 503 Service Unavailable |
| PriceCenterService 回傳錯誤 | 依錯誤碼對應處理（需人工確認錯誤碼定義） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| LOG-01 | API Test | 無 token 呼叫 GET /api/system/logs/action/2024-01-01 | 回傳 401 Unauthorized |
| LOG-02 | Permission Test | 無後台權限的 token 呼叫 API | 回傳 403 Forbidden |
| LOG-03 | API Test | 正常 token 呼叫 GET /api/system/logs/action/2024-01-01 | 回傳 200，回傳當日操作紀錄清單 |
| LOG-04 | API Test | 查詢無資料的日期 | 回傳 200，空陣列 |
| LOG-05 | API Test | 日期格式錯誤（如 2024/01/01） | 回傳 400 Bad Request |

---

## 9. 高風險區域

- **跨服務相依**：MergeSite 依賴 PriceCenterService 提供操作紀錄查詢。若 PriceCenterService 變更 API 合約或儲存結構，將直接影響本查詢的正確性
- **操作紀錄完整性**：若操作記錄依賴 Kafka 非同步寫入，則查詢可能存在延遲，需人工確認資料一致性保證
- **全域查詢效能**：若只依日期過濾而無其他條件限制，當日操作量過大時可能導致查詢緩慢或逾時

---

## 10. 常見錯誤

- ❌ 未確認日期格式與時區，導致查詢結果不符預期
- ❌ 誤以為操作紀錄儲存在 MergeSite 本地資料庫，直接查詢 SQL
- ❌ 回傳過多操作紀錄欄位，包含不必要的內部細節
- ❌ 未處理 PriceCenterService 連線失敗，導致服務崩潰而非優雅降級

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md — 系統 API：`GET /api/system/logs/action/{date}` |
| 服務相依 | README.md — 服務相依：PriceCenterService（Gateway: 192.168.55.60） |
| 驗證規則 | README.md — 需要驗證：✅ |
| 操作紀錄寫入 | README.md — 系統 API：`POST /api/system/logs/action` |
| Kafka 寫入 | README.md — Kafka（192.168.55.60）：應用程式 Log 寫入 |
| 服務角色 | pricecenter-detail.md — mergesite：writer（accounts_* 表寫入） |

---

## 12. 需人工確認

以下項目因現有證據不足，需資深工程師或額外程式碼分析確認：

- **操作紀錄儲存位置**：PriceCenterService 使用何種儲存機制（Cassandra、MySQL、Elasticsearch 或檔案）？讀取時的查詢條件與索引為何？
- **日期參數格式**：`{date}` 的精確格式 (yyyy-MM-dd?) 與時區處理？
- **Controller 與 Provider 實作**：確切的類別名稱、方法名稱、呼叫鏈為何？
- **DTO 結構**：回傳的操作紀錄欄位有哪些？哪些欄位對外遮蔽？
- **PriceCenterService 錯誤碼**：對應的 HTTP 狀態碼與錯誤處理策略為何？