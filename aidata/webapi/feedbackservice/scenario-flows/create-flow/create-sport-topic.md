# 管理員建立運動主題

## 1. 場景目的
管理員在後台為運動站點新增反饋主題，將主題資訊寫入 `topics_sport` 表，供前端用戶提交反饋時選擇。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | 需人工確認 | 需人工確認管理後台建立運動主題的 API 路徑 |

---

## 3. 流程總覽

1. 管理後台 (pricecentermanage) 發送建立運動主題 request
2. feedbackservice 接收 request，驗證管理員權限 (需人工確認)
3. 驗證請求參數（`Name` 的 MAP 結構、啟用狀態等）
4. 生成唯一主題 ID (需人工確認生成規則)
5. 組合完整主題資料
6. 呼叫 `SportFeedbackDataProvider` 執行 INSERT
7. 寫入 `topics_sport` 表 (ScyllaDB)
8. 回傳操作結果

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | 需人工確認 | 接收管理後台 API 請求，轉發至 Service |
| 2 | Service | `SportFeedbackService` 或 `TopicService` | 驗證資料、組合主題物件 (需人工確認確切類別名稱) |
| 3 | Provider | `SportFeedbackDataProvider` (或 `TopicDataProvider`) | 執行 ScyllaDB INSERT CQL |
| 4 | Model | `SportTopic` | 作為資料傳輸物件 (需人工確認確切 DTO 名稱) |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `sport.topics_sport` | Write (INSERT) | 建立新運動主題記錄 |
| Redis | 無 | - | 此流程未使用快取 |
| Queue | 無 | - | 此流程未使用佇列 |

---

## 6. 重要規則

- **權限限制**：僅管理後台 (pricecentermanage 或具管理權限的角色) 可執行此操作。一般使用者無權限。
- **欄位限制**：
  - `Name` 欄位型別為 `MAP<VARCHAR, VARCHAR>`，存入多語言名稱，必須符合 MAP 格式。
  - `Enabled` 欄位型別為 `INT`，通常新建主題預設為啟用 (`1`)。
- **不可暴露資料**：系統內部使用的主題 `ID` 生成邏輯不應暴露給前端。
- **TTL 規則**：無。
- **Transaction 規則**：ScyllaDB 不支援傳統 RDBMS 的多表事務，此流程僅單表寫入，無分散式交易問題。
- **Retry 規則**：失敗時由管理員手動重試，或依賴應用層重試機制 (需人工確認)。
- **狀態值限制**：`Enabled` 值僅限 `0` (停用) 或 `1` (啟用)。
- **不可修改欄位**：建立後 `ID` 不可修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 權限不足 (非管理員請求) | 返回 HTTP 403 Forbidden 或權限錯誤訊息 |
| 缺少必要欄位 (如 `Name`) | 返回 HTTP 400 Bad Request 及欄位缺失錯誤訊息 |
| `Name` 欄位 MAP 格式錯誤 | 返回 HTTP 400 Bad Request 及格式錯誤訊息 |
| DB 連線失敗或寫入逾時 | 返回 HTTP 500 Internal Server Error (需人工確認是否有自定義錯誤代碼) |
| 主題 `ID` 重複 | 需人工確認 (ScyllaDB INSERT 若主鍵重複會失敗) |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T001 | API Test | 管理員成功建立有效主題 | 返回成功，`topics_sport` 出現新紀錄 |
| T002 | Permission Test | 非管理員嘗試建立 | 返回 403 或權限錯誤 |
| T003 | API Test | 發送無效的 `Name` MAP 格式 | 返回 400 及驗證錯誤訊息 |
| T004 | Flow Test | DB 暫時不可用 | 返回 500，`topics_sport` 無新記錄 |

---

## 9. 高風險區域

- **高風險 table**: `topics_sport`，此表為主資料，若遭誤刪或修改將直接影響前端顯示。
- **高風險 API**: 建立主題的 API，須嚴格控管權限，防止未授權呼叫。
- **跨服務資料同步**: 此流程無。
- **Transaction**: ScyllaDB 輕量級事務 (LWT) 可能影響效能，需評估是否必要。
- **Cache consistency**: 此流程無。
- **Queue retry**: 此流程無。
- **Idempotency**: 連續快速發送相同請求可能因主鍵衝突導致第二次失敗，需人工確認有無自定義冪等機制。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 誤將 `Name` 欄位傳入純文字字串，而非 `MAP` 結構。
  - 在請求中嘗試指定 `ID`，而 `ID` 應由系統/資料庫產生。
- **AI 容易誤解**：
  - 誤以為此操作與 `notification_topics` 表有關。此處為運動站點的反饋主題，儲存於 feedbackservice 管理的 `topics_sport` 表。
- **常見漏檢查項目**：
  - 未驗證 `Name` 的 MAP 結構中是否包含必要語系鍵值。
- **常見錯誤流程**：
  - 未確認權限就進行寫入操作。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | 需人工確認 Controller 與路由註冊 |
| DB | `SportFeedbackDataProvider.cs` (操作 `topics_sport` 表) |
| Code | `SportFeedbackDataProvider.cs`, 需人工確認對應的 Service 層邏輯 |
| Code | 語意分析批處理輸出，指明 `topics_sport` 表的 `name` 欄位語意為 "多语言主题名称映射" |
| Schema | `topics_sport` 表結構定義來自 Phase 1 語意分析，確認欄位 ID, Enabled, Name(MAP), Sort |