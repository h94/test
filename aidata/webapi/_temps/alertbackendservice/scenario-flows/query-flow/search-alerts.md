# 搜尋警示清單

## 1. 場景目的
依據球種、時間區間、來源、聯盟等條件，查詢警示清單（不包含 detail、threshold_snapshot、game_info 等大欄位），提供快速篩選與概覽。

---

## 2. 入口 API

| Method | Path                        | 說明                                                                              |
|--------|-----------------------------|-----------------------------------------------------------------------------------|
| POST   | `/api/alerts/{game_type}`   | 球種代碼（不分大小寫）；Body 傳入 `AlertSearchBody`，支援 start/end/source/league_id |

---

## 3. 流程總覽

1. 接收 request，提取路徑參數 `game_type` 與 Body 參數 `start`、`end`、`source`、`league_id`。
2. 若未提供 `start` 或 `end`，預設為台灣時間當日 00:00:00 至 23:59:59。
3. 呼叫 Service 層建構動態查詢條件。
4. Provider 層產生 SQL，僅選取不含 `detail`、`threshold_snapshot`、`game_info` 的欄位。
5. 對 `alerts` 表執行查詢（需確認是否會查詢 `alerts_archive`，目前設計只查線上表）。
6. 回傳符合條件的警示清單。

---

## 4. 程式流程

| 順序 | Layer      | Class / Method                 | 動作                                                                                      |
|------|------------|--------------------------------|-------------------------------------------------------------------------------------------|
| 1    | Controller | Resources/Alerts.py           | 接收 POST 請求，解析 path param `game_type` 與 Body                                      |
| 2    | Controller | -                              | 若 start/end 為空，填入今日台灣時間範圍（需確認時區轉換）                                  |
| 3    | Service    | Service/AlertsService.py      | 呼叫 `search(game_type, start, end, source, league_id)`，調用 Provider 組合查詢            |
| 4    | Provider   | Provider/AlertsProvider.py    | `build_search_query` 根據條件動態組成 SQL，排除 detail, threshold_snapshot, game_info 欄位    |
| 5    | Provider   | -                              | 使用 asyncpg 執行查詢，返回 records                                                       |
| 6    | Service    | -                              | 整理結果並回傳 Controller                                                                 |
| 7    | Controller | -                              | 回傳 JSON 陣列                                                                           |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源       | 操作 | 用途                                   |
|------|------------|------|----------------------------------------|
| DB   | `alerts`   | Read | 使用動態條件查詢警示（不含大欄位）       |
| -    | Redis      | -    | 本場景未使用 Redis                      |
| -    | Kafka      | -    | 本場景未涉及佇列                        |

---

## 6. 重要規則

- **預設時間範圍**：若無指定 start/end，查詢「今日台灣時間 00:00:00 ~ 23:59:59」。
- **欄位排除**：必然不返回 `detail`、`threshold_snapshot`、`game_info`，以減少傳輸量與加速查詢。
- **球種不分大小寫**：`game_type` 一律轉為小寫後查詢。
- **權限驗證**：需人工確認是否有 API 層級驗證（目前 OpenAPI 未標註 security）。
- **查詢效能**：預期 `alerts` 表有 `game_type`、`created_at` 複合索引，否則需注意全表掃描風險。

---

## 7. 錯誤情境

| 情境                           | 預期結果                            |
|--------------------------------|-------------------------------------|
| 無效的 `game_type`（不存在）   | 回傳空陣列 `[]`，不報錯              |
| 日期格式錯誤                   | FastAPI 自動回傳 422 Validation Error |
| 資料庫連線失敗                 | 500 Internal Server Error            |
| 查詢條件組合不合理（如 end < start） | 應回傳空陣列或前端阻擋（需人工確認） |
| 查詢結果過大（數萬筆）         | 目前無分頁，可能造成記憶體濫用（高風險） |

---

## 8. 測試重點

| Test ID                 | 類型          | 情境                                           | 預期結果                              |
|-------------------------|---------------|------------------------------------------------|---------------------------------------|
| SEARCH-01               | API Test      | 正確球種、不帶時間                             | 回傳今日所有警示，不含 detail 欄位      |
| SEARCH-02               | API Test      | 指定 start/end 範圍                             | 僅回傳該時間區間資料                   |
| SEARCH-03               | API Test      | 提供 source 或 league_id                       | 正確過濾                               |
| SEARCH-04               | API Test      | 球種大小寫混用 (`SocCer`)                       | 應正常查詢，不區分大小寫               |
| SEARCH-05               | Flow Test     | 無任何警示時                                    | 回傳空陣列 `[]`                        |
| SEARCH-06               | Performance   | 大量資料無分頁查詢                              | 須評估回應時間與記憶體（目前無分頁機制） |

---

## 9. 高風險區域

- **無分頁機制**：若查詢結果集龐大，可能導致回應緩慢、記憶體過高，甚至服務超時。
- **全表掃描風險**：`alerts` 表若無覆蓋 `game_type + created_at` 的索引，查詢效能極差。
- **時間範圍預設**：預設值為今日整天，若前端未傳，可能產生大量資料（需監控）。
- **欄位排除**：若有程式誤讀這些大欄位，會造成不必要效能損耗；但本場景已明確排除。

---

## 10. 常見錯誤

- **忘記排除大欄位**：使用 `SELECT *` 而非指定欄位清單，導致回應膨脹。
- **時區錯誤**：預設時間未轉換為台灣時區，可能查詢到 UTC 今日而非台灣今日。
- **球種未轉小寫**：未做大小寫正規化，可能因大小寫不同而查不到資料。
- **誤查 `alerts_archive`**：常態查詢不應包含封存表，需確保只查 `alerts`。
- **無效條件仍然查詢**：例如 start > end 時，應直接返回空或拋錯，但目前可能仍執行 SQL（需確認）。

---

## 11. Evidence

| 類型   | 來源                                          |
|--------|-----------------------------------------------|
| API    | `POST /api/alerts/{game_type}` (OpenAPI)       |
| DB     | `alerts` 表 (migrations/001_create_core_tables.sql) |
| Code   | `alerts.py:build_search_query` (Provider)      |
| Schema | `AlertSearchBody` (OpenAPI components)         |
| 規則   | 預設時間說明（API 描述：start / end 未帶時預設查台灣時間今天整天） |
| 欄位排除 | 明確描述「不含 detail 欄位」(OpenAPI 與 API description) |