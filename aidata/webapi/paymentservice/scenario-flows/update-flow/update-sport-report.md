# 更新體育收益報表

## 1. 場景目的

提供一個安全的 API，讓後台排程系統（如 pricebackendservice）可以批次更新已結算的月度體育收益報表。此操作的核心是鎖定報表（設置 `finishing=true`）以防止後續變更，並更新結算金額、分潤及解鎖數據。**嚴禁人工透過後台 UI 或直接 API 呼叫進行此操作。**

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/v1/sport/reports/{year}/{month}` | 更新指定年/月的體育收益報表，需驗證 |

---

## 3. 流程總覽

1.  接收外部服務（pricebackendservice）或內部排程的 PUT 請求。
2.  驗證請求者的權限（需通過 ECFramework 驗證）。
3.  解析路徑參數 `year` 和 `month`，並驗證其有效性。
4.  根據 `year` 和 `month` 從 Cassandra `payment.reports_sport` 表中讀取現有的報表記錄。
5.  檢查報表狀態：
    *   若報表不存在，返回 `404 Not Found`。
    *   **若報表的 `finishing` 欄位已為 `true`，則拒絕更新**，因為該報表已完成結算。
6.  使用請求中的數據更新報表記錄，其中應包含 `totalincome`, `shareamount`, `unlockcount`, `leaguesunlock` 以及關鍵的 `finishing=true`。
7.  將更新後的記錄寫回 Cassandra `payment.reports_sport` 表。
8.  返回操作成功的回應 (200 OK)。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SportReportController.UpdateReport` | 接收 HTTP 請求，解析 `year`, `month` 及請求體。需人工確認具體類別與方法名稱。 |
| 2 | Service | `SportReportService.UpdateReport` | 處理核心業務邏輯，包括調用 Provider 讀取資料、檢查 `finishing` 狀態。需人工確認具體類別與方法名稱。 |
| 3 | Provider | `SportReportDataProvider` | 向 Cassandra 執行 `SELECT` 語句，根據 `year` 和 `month` 查詢 `reports_sport` 表。 |
| 4 | Service | `SportReportService.UpdateReport` | 校驗報表存在且 `finishing == false`。若非如此，則拋出業務異常。 |
| 5 | Provider | `SportReportDataProvider` | 向 Cassandra 執行 `UPDATE` 語句，寫入新的報表數據並將 `finishing` 設為 `true`。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `payment.reports_sport` | Read | 根據主鍵 `(year, month)` 讀取現有報表記錄，以檢查其存在性與狀態。 |
| DB | `payment.reports_sport` | Update | 更新報表的收入、分潤、解鎖數等數據，並將其 `finishing` 狀態標記為 `true`。 |
| Redis / Cache | 無 | - | 經分析，目前未發現此場景有快取操作。 |
| Queue / Kafka | 無 | - | 經分析，目前未發現此場景有佇列操作。 |
| 外部 API | 無 | - | 經分析，目前未發現此場景有外部服務呼叫。 |

---

## 6. 重要規則

*   **寫入限制**：此 API **僅供排程系統 (pricebackendservice) 或具備同等權限的內部服務呼叫**。嚴禁前端或一般後台管理員手動觸發更新。
*   **狀態限制**：`finishing` 標記為 `true` 後，該報表記錄應被視為不可變，**任何後續的更新請求都必須被拒絕**。
*   **不可修改欄位**：主鍵 `year` 和 `month` 在創建後不可修改。
*   **欄位限制**：`totalincome`, `shareamount`, `unlockcount`, `leaguesunlock`, `finishing` 這類結算相關欄位，應只允許由此場景的批次作業進行更新，禁止人為 INSERT 或 UPDATE。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求的 `year`/`month` 格式無效 | 返回 400 Bad Request。 |
| 對應的 `reports_sport` 記錄不存在 | 返回 404 Not Found。 |
| 目標報表的 `finishing` 欄位已為 `true` | 返回 409 Conflict 或 422 Unprocessable Entity，並附帶錯誤訊息（例如："Report already finished."）。 |
| 呼叫方權限不足 | 返回 403 Forbidden。 |
| Cassandra 寫入操作失敗或超時 | 返回 500 Internal Server Error。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-01 | Flow Test | 對一個 `finishing=false` 的報表，發送有效的更新請求。 | 回傳 200 OK，DB 中的記錄被更新且 `finishing=true`。 |
| UT-02 | Flow Test | 對一個 `finishing=true` 的報表，發送更新請求。 | 回傳 409 Conflict，DB 中的記錄保持不變。 |
| UT-03 | API Test | 發送缺少必要欄位或格式錯誤的請求。 | 回傳 400 Bad Request。 |
| UT-04 | Permission Test | 以無效或不具備排程權限的 Token 發送請求。 | 回傳 403 Forbidden。 |

---

## 9. 高風險區域

*   **高風險 Table**：`payment.reports_sport`。此表包含核心財務數據，不當的修改（例如重複結算、修改已完成報表）會導致財務報表錯誤。
*   **高風險 API**：`PUT /api/v1/sport/reports/{year}/{month}`。權限控管失當或呼叫頻率過高，都可能直接破壞數據完整性。
*   **Transaction**：雖然 Cassandra 的事務能力有限，但在單一記錄的讀寫更新流程中，應確保邏輯上的原子性。需人工確認是否使用了 Cassandra 的 Lightweight Transaction (LWT) 來處理併發更新。

---

## 10. 常見錯誤

*   ❌ **直接手動更新 `finishing=true`** → ✅ `finishing` 標記應僅由結算流程在更新報表數據時一同設定。
*   ❌ **試圖更新一個已結算的報表而未進行檢查** → ✅ 必須在執行寫入操作前，明確檢查目標報表的 `finishing` 狀態。
*   ❌ **未經授權的服務或角色調用此 API** → ✅ 必須透過 API Gateway 或服務間認證 (如 Token) 嚴格限制呼叫來源。
*   ❌ **AI 或新手漏檢查 `finishing` 狀態** → 這是最常見且後果最嚴重的錯誤，可能導致已定案的財務數據被覆蓋，應列為 Code Review 的第一要點。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| **API 路由與權限** | `README.md`: `PUT /api/v1/sport/reports/{year}/{month}` (需驗證) |
| **DB 寫入限制** | `db-usage/payment-detail.md > Table: reports_sport > finishing`: "...僅由排程批次寫入，禁止人工 INSERT 或 UPDATE `finishing=true`"。這證實了寫入限制與狀態鎖定規則。 |
| **DB 表結構** | `dbschema/detail.md`: `reports_sport` 表結構，定義了 `year`, `month` 為 Primary Key，以及 `finishing` 等業務欄位。 |
| **服務角色** | `db-usage/payment-detail.md > Table: reports_sport`: 明確指出只有 `reportservice`（在此語境中等同於排程批次處理器）可以修改 `finishing`。 |