# 建立匯出任務

## 1. 場景目的

操作人員針對特定篩選條件的大量警示資料，建立一個非同步的匯出任務。此任務會交由背景 Worker 處理，最終產生 CSV 或 XLSX 檔案並上傳至 NAS 儲存，供操作人員後續下載。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/alertbackendservice/api/exports` | 建立一個新的匯出任務（需人工確認實際路由） |

---

## 3. 流程總覽

1. 接收來自前端的匯出請求，包含篩選條件（球種、時間、來源等）及匯出格式（CSV/XLSX）。
2. 驗證必要參數與匯出格式（需人工確認：由 Controller 或 Service 層驗證）。
3. 產生唯一的任務 ID。
4. 將任務資訊（狀態 `pending`、篩選參數、操作者帳號）寫入 `export_tasks` 資料表。
5. 回傳任務 ID 與狀態給前端。
6. 背景 Worker 會後續撈取 `pending` 任務進行資料匯出與檔案上傳（非本場景範圍）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | ExportsResource.create（需人工確認） | 接收 HTTP POST 請求，解析請求體 |
| 2 | Service | ExportService.create_task（需人工確認） | 驗證參數、產生任務 ID，調用 Provider |
| 3 | Provider | ExportTaskProvider.insert（需人工確認） | 執行 `INSERT INTO export_tasks`，寫入任務記錄 |
| 4 | Controller | ExportsResource.create（需人工確認） | 回傳 HTTP 200/201 與任務摘要 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `export_tasks` | Write | 新增一筆狀態為 `pending` 的匯出任務記錄 |

---

## 6. 重要規則

- **權限限制**：需人工確認（可能需要特定角色或操作者帳號）。
- **欄位限制**：
  - `file_format`（CSV/XLSX）必須為系統支援的格式。
  - `status` 初始值必須為 `pending`。
  - `operator_account` 不可為空。
- **不可暴露資料**：任務 ID 可回傳，但內部檔案路徑 `file_path` 在任務建立時為空，不應回傳。
- **任務狀態機**：新任務只能處於 `pending` 狀態，不可直接設為 `processing` 或 `completed`。
- **不可修改欄位**：`id`、`created_at` 由系統或資料庫自動產生，不接受輸入。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求參數缺少必要欄位（如 `game_type`） | 回傳 HTTP 422，附帶驗證失敗訊息。 |
| `file_format` 為不支援的格式（如 PDF） | 回傳 HTTP 400，提示不支援的格式。 |
| 操作者帳號為空 | 回傳 HTTP 400 或直接拒絕請求（需人工確認）。 |
| DB 寫入失敗（例如連線中斷） | 回傳 HTTP 500，不應建立任務。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TE-01 | API Test | 傳入完整合法參數建立匯出任務 | HTTP 200/201，回傳任務 ID 且 status 為 `pending` |
| TE-02 | API Test | 傳入不支援的匯出格式 | HTTP 400，回應包含明確錯誤訊息 |
| TE-03 | Permission Test | 未經授權的使用者嘗試建立任務 | HTTP 401/403（需人工確認） |
| TE-04 | Flow Test | 建立任務後查詢 `export_tasks` | DB 中存在該筆任務，狀態為 `pending` |

---

## 9. 高風險區域

- **高風險 table**：`export_tasks` — 任務記錄是後續 Worker 處理的唯一依據，寫入失敗將導致任務遺失。
- **Idempotency**：若前端重複提交相同請求，系統是否會建立重複任務（需人工確認）？
- **Worker 觸發**：純 DB 輪詢可能造成延遲，需確認是否有 Kafka/Redis 通知機制，否則為高風險。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 誤將 `file_path` 或 `file_size_bytes` 等欄位在建任務時就寫入。
  - 未正確處理 `query_params` 的 JSON 序列化，導致寫入異常。
- **AI 容易誤解**：
  - 以為此場景包含背景 Worker 的撈取與檔案產生流程。
  - 誤將其他查詢（如 alerts 搜尋）的複雜邏輯帶入此任務建立流程。
- **常見漏檢查項目**：未驗證匯出格式是否在允許清單內。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB Schema | `migrations/002_create_supplement_tables.sql` (export_tasks 定義) |
| Provider Code | `exports.py:insert` (插入新任務) |
| 狀態定義 | `exports.py:insert` (status 初始為 pending) |
| 場域敘述 | `webapi/alertbackendservice/README.md` (匯出服務描述) |