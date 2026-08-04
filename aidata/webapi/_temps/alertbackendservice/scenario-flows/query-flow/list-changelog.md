# 查詢閥值異動記錄

## 1. 場景目的
查閱閥值設定變更的 changelog。此流程提供操作員查詢所有閥值設定（賠率閥值、比分閥值、監控玩法等）的歷史變更記錄，用於稽核與追蹤設定異動。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/threshold_changelog` | 查詢閥值設定變更記錄，支援以日期範圍篩選。 |

---

## 3. 流程總覽

1. 接收查詢請求，可選帶入 `start` 和 `end` 日期時間參數（台灣時間）。
2. 驗證日期格式（若有帶入）。
3. 若未帶入時間範圍，預設查詢台灣時間今天整日（00:00:00 ~ 23:59:59）。
4. 查詢 PostgreSQL `threshold_changelog` 資料表，篩選 `changed_at` 在指定時間範圍內的記錄。
5. 依 `changed_at` 降冪排序，確保最新異動在前。
6. 回傳 changelog 清單，每筆包含：變更表名、記錄鍵值、玩法、新舊值、操作者帳號、變更時間。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `threshold_changelog_router.py: list_threshold_changelog` | 接收 `start` 與 `end` 查詢參數，呼叫 Service。 |
| 2 | Service | `threshold_changelog_service.py: list_changelog` | 處理預設日期範圍邏輯，呼叫 Provider。 |
| 3 | Provider | `threshold_changelog_provider.py: query_by_time_range` | 建立 SQL 查詢，對 `threshold_changelog` 表依 `changed_at` 進行範圍查詢，排序後回傳。 |

**需人工確認**：Controller、Service、Provider 的實際檔案名稱與方法簽名，可能因版本而異。應以實際程式碼為準。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `threshold_changelog` | Read | 查詢閥值異動記錄。 |

---

## 6. 重要規則

- **時間範圍查詢**：若請求未提供 `start` 和 `end`，系統預設查詢台灣時間（`Asia/Taipei`）當天 00:00:00 至 23:59:59 的記錄。
- **排序規則**：查詢結果應依 `changed_at` 降冪排序，確保最新的變更顯示在最前面。
- **唯讀操作**：此 API 僅供查詢，不涉及任何寫入、更新或刪除操作，且不觸發任何 Kafka 同步或 Webhook 通知。
- **權限限制**：無。此為後台管理查詢 API，一般視為內部操作員使用，需配合閘道或中介軟體進行身份驗證與授權。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 提供的 `start` 或 `end` 格式錯誤 | 回傳 HTTP 422 Unprocessable Entity，錯誤訊息指出日期格式不正確。 |
| 查詢時間範圍內無任何記錄 | 回傳 HTTP 200 OK，內容為空陣列 `[]`。 |
| 資料庫連線失敗或查詢逾時 | 回傳 HTTP 500 Internal Server Error。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 不帶任何參數查詢 | 回傳 200，內容為今日所有 changelog 記錄。 |
| TC02 | API Test | 帶入正確的 `start` 和 `end` 參數 | 回傳 200，內容精確符合時間範圍的記錄。 |
| TC03 | API Test | 帶入格式錯誤的 `start` 日期 | 回傳 422，指出日期格式錯誤。 |
| TC04 | Flow Test | 查詢一段已知無資料的時間範圍 | 回傳 200，內容為空陣列 `[]`。 |
| TC05 | Permission Test | 未經授權的請求（若適用） | 回傳 401/403。 |

---

## 9. 高風險區域

- **資料庫查詢效能**：若 `threshold_changelog` 資料表累積大量歷史資料，且查詢時間範圍過大，可能導致全表掃描，影響資料庫效能。
- **唯讀資料一致性**：此為純查詢場景，無需擔心快取一致性問題。

---

## 10. 常見錯誤

- **時間範圍誤解**：開發或測試時，未注意系統預設使用 `Asia/Taipei` 時區，導致查詢結果與預期不符。
- **參數格式錯誤**：請求時傳入未經 ISO 8601 格式化的日期字串。
- **濫用全範圍查詢**：實務上應避免不帶任何時間範圍的大規模查詢，以免拖慢系統。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `threshold_changelog_router.py` |
| DB | `threshold_changelog` |
| Code | `threshold_changelog_service.py` |
| Code | `threshold_changelog_provider.py` |
| DB Schema | `migrations/002_create_supplement_tables.sql` (threshold_changelog) |
| README | "閥值異動皆寫入 changelog" |