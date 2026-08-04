# 場景：查詢競猜每日報表

## 1. 場景目的

提供管理後台查詢每日競猜統計資料的功能。使用者可指定日期區間（`sdate`, `edate`）以及遊戲類型（`gametype`），系統回傳符合條件的競猜報表數據，例如投注數、鎖定數、解鎖數等。

參考來源：README 的「每日報表」段落與 API 路由 `GET /api/v1/sport/report/predict`。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/sport/report/predict` | 查詢競猜每日報表，需要驗證 |

參考來源：README 的「每日報表」API 列表。

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，包含查詢參數：`sdate`、`edate`、`gametype`
2. 驗證請求者權限（由 ECFramework.ECService 攔截）
3. 驗證查詢參數不可為空，日期格式須符合 `YYYY-MM-DD`
4. 調用 Service 層執行報表查詢
5. Service 層透過 Provider 查詢資料庫
6. 組裝回傳結果並回傳 JSON 陣列

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `SportReportController.GetPredictReport` | 接收請求，將 `sdate`、`edate`、`gametype` 傳入 Service |
| 2 | Service | `SportReportService.GetPredictDailyReport` | 調用 Provider，組織查詢條件 |
| 3 | Provider | Cassandra Provider (預測基底) | 讀取 Cassandra `pricecenter` keyspace 中的 `predict_daily_reports` 表 |
| 4 | Transfer/Model | `PredictDailyReportDto` | 將查詢結果映射為回傳物件 |
| 5 | Controller | `SportReportController` | 回傳 `200 OK` 與 DTO 列表 |

參考來源：程式碼分析顯示 Controller > Service > Provider 結構。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `pricecenter.predict_daily_reports` | Read | 查詢競猜每日統計數據（投注、鎖定、解鎖等） |
| Redis | 未使用 | - | 每日報表讀取頻率相對低，直接查詢 Cassandra 即可 |

依據 `pricecenter` keyspace 定義與 Service 角色。**需人工確認**：`predict_daily_reports` 的 Cassandra 表是否已存在。

---

## 6. 重要規則

- **權限限制**：僅允許具備管理後台權限的使用者呼叫，驗證機制由 ECFramework 提供。
- **欄位限制**：查詢必須提供 `sdate` 與 `edate`，且格式為 `YYYY-MM-DD`。`gametype` 為必填，用於過濾特定遊戲類型。
- **不可暴露資料**：此報表為聚合統計數據，不包含個人身份資訊或財務細節，但僅限管理後台閱讀。
- **SQL 查詢限制**：查詢時必須加上日期區間條件，避免觸發全表掃描，遵守 Cassandra 查詢最佳實踐。
- **不可修改欄位**：`predict_daily_reports` 為唯讀表，pricecentermanage 無寫入權限。

參考來源：`pricecenter` 與 `predict` DB 操作邊界文件、`member` DB 的讀取規則（作為 similar pattern）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 缺少 `sdate` 或 `edate` 參數 | 回傳 `400 Bad Request` |
| 日期格式錯誤（例如 `2026/06/10`） | 回傳 `400 Bad Request` 或 `422 Unprocessable Entity` |
| 未提供 `gametype` | 回傳 `400 Bad Request` |
| 無符合條件的資料 | 回傳 `200 OK` 搭配空陣列 `[]` |
| Cassandra 連線失敗或逾時 | 回傳 `500 Internal Server Error` 或 `503 Service Unavailable` |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | API Test | 提供正確的 `sdate`, `edate`, `gametype` | 回傳 `200 OK` 與對應資料陣列 |
| T2 | API Test | 缺少 `sdate` | 回傳 `400 Bad Request` |
| T3 | API Test | `sdate` 格式錯誤 | 回傳 `400 Bad Request` |
| T4 | Flow Test | 資料庫中無符合區間的資料 | 回傳 `200 OK`，空陣列 |
| T5 | Permission Test | 使用未驗證的請求 | 回傳 `401 Unauthorized` |

---

## 9. 高風險區域

- **全表掃描風險**：若未限制日期區間，Cassandra 查詢可能觸發全表掃描，導致效能問題甚至超時。
- **跨服務資料同步**：報表資料由排程或其他服務寫入，若寫入延遲或失敗，pricecentermanage 將讀取不到最新或完整的數據。需監控寫入端的健康狀態。
- **Cache consistency**：目前未實作快取，若有高頻查詢需求再引入，屆時需注意快取與 Cassandra 的一致性。

---

## 10. 常見錯誤

- ❌ **未過濾日期區間直接查詢**：Cassandra 的 `predictdailyeport` 必須指定 `WHERE Reportdate >= ? AND Reportdate <= ?`，否則會導致全表掃描，嚴重影響效能。
- ❌ **誤認為 MySQL Sport 的 `predictdailyeport`**：請確認使用的實際資料來源，根據 README 表清單應為 Cassandra `pricecenter.predict_daily_reports`。混淆可能導致查詢錯誤的資料庫。
- ❌ **忽略 `gametype` 必填條件**：遺漏此條件將無法過濾出正確的遊戲類型統計。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `GET /api/v1/sport/report/predict` (README) |
| DB Table | `pricecenter.predict_daily_reports` (README, pricecenter-detail) |
| Service | `pricecentermanage` 角色為 `reader` (pricecenter-detail) |
| Query Pattern | `WHERE Reportdate >= ? AND Reportdate <= ? AND Gametype = ?` (pricecenter-detail) |
| Code (推測) | `SportReportController`, `SportReportService`, 對應 Provider |