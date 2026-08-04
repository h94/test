# 查詢 Token 操作日誌

## 1. 場景目的

提供查詢指定日期範圍內 Token 操作紀錄（如建立、驗證）的功能。此功能供後端管理或稽核使用，根據請求來源的公司代碼，查詢該公司相關的操作歷史，包含操作時間與動作類型。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/log/{date}` | 查詢指定日期（含）後的操作日誌 |
| 參數 | `date` (路徑, 必要) | 查詢起始日期 (格式: date-time) |
| 參數 | `enddate` (查詢, 可選) | 查詢結束日期 (格式: date-time) |

---

## 3. 流程總覽

1.  API 接收含有 `date` 與可選 `enddate` 的 GET 請求。
2.  從請求上下文（如驗證過的 `authKey` 或內部配置）中取得請求方的 `CompanyCode`。
3.  查詢 `logs` 資料表，條件為 `CompanyCode` 匹配，且 `AccessTime` 在 `date` 和 `enddate` 範圍內。
4.  若未提供 `enddate`，則僅查詢 `AccessTime` 大於等於 `date` 的記錄。
5.  將查詢結果（ID, CompanyCode, AccessTime, Action）回傳給客戶端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `LogController` (推測) | 接收請求，取得路徑參數 `date` 與查詢參數 `enddate`。 |
| 2 | Controller | `LogController` (推測) | 從 `HttpContext` 或認證資訊中取得 `CompanyCode`。 |
| 3 | Provider | `LogProvider` (推測) | 呼叫資料存取層，根據條件查詢 `logs` 資料表。 |
| 4 | Provider | `LogProvider` (推測) | 將查詢結果映射為 `Log` 模型列表後回傳。 |
| 5 | Controller | `LogController` (推測) | 將結果包裝為 HTTP 200 回應。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `logs` | Read (`SELECT`) | 根據公司代碼與時間範圍，讀取操作日誌記錄。 |

---

## 6. 重要規則

- **權限限制**：此 API 僅供內部服務或具有特定 `authKey` 的客戶端呼叫，`CompanyCode` 由系統內部決定，不允許呼叫方透過參數自行傳入 (需人工確認)。
- **時間範圍**：
  - 起始時間 `date` 為必要參數，且格式必須符合 date-time。
  - 結束時間 `enddate` 為可選，若無提供則代表查詢從 `date` 至今的所有記錄。
  - 查詢條件應為 `AccessTime >= 'date' AND AccessTime < 'enddate + 1天'`，以確保日期範圍的正確與完整 (需人工確認)。
- **不可暴露資料**：`logs` 表中不包含 `HashKey` 等敏感資訊，但回應的 `Action` 內容可能含有 token 的前綴或部分資訊，需確認是否需要遮蔽處理 (需人工確認)。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求缺少路徑參數 `date` | HTTP 404 或 400，無法匹配路由。 |
| `date` 或 `enddate` 格式錯誤 | HTTP 400，回傳參數格式錯誤的訊息。 |
| `CompanyCode` 無法從請求中取得 | HTTP 401 (Unauthorized)，因為無法識別查詢對象。 |
| 資料庫查詢失敗或超時 | HTTP 500，回傳內部伺服器錯誤。 |
| 符合條件的記錄為空 | HTTP 200，回傳空的 JSON 陣列。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T-QL01 | API Test | 提供有效的 `date` 和 `enddate`，且該區間內有記錄 | HTTP 200，回傳正確的記錄列表。 |
| T-QL02 | API Test | 僅提供 `date` 參數 | HTTP 200，回傳當日及之後的所有記錄。 |
| T-QL03 | API Test | 提供有效參數但該 `CompanyCode` 無任何記錄 | HTTP 200，回傳空陣列 `[]`。 |
| T-QL04 | Permission Test | 以未帶合法 `authKey` 的請求呼叫 | 預期授權失敗，回傳 HTTP 401 或 403。 |

---

## 9. 高風險區域

- **大量資料查詢**：若無 `enddate` 限制或日期範圍過大，`logs` 表可能被掃描大量資料，有效能風險。應考慮在 DB 層級對 `CompanyCode` 和 `AccessTime` 建立複合索引。
- **時間範圍精確性**：`Logs` 表的 `AccessTime` 預設為 `CURRENT_TIMESTAMP`，需確認整個系統（包含 MySQL）的時區一致性，皆為 UTC，否則可能導致查詢結果錯亂。

---

## 10. 常見錯誤

- 誤解 `date` 參數為一個範圍，實際上它是一個起點。
- 將 `enddate` 的邊界值設定為當天的 00:00:00，導致最後一天的記錄未被納入查詢。應將結束時間的條件設定為小於次日。
- 忘記在請求中攜帶合法的認證資訊。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI `/api/v1/log/{date}` |
| DB | DB schema `logs` |
| Model | OpenAPI schema `Log` |
| 業務規則 | 場景描述、README 主要功能「操作日誌查詢」 |