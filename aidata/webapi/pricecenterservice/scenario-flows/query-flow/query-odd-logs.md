# 查詢賠率異動紀錄

## 1. 場景目的

提供後台或開發工具查詢指定站台賽事的賠率異動歷史。V1 回傳結構化 `OddLog`（Cassandra）；V2 回傳 `DeveloperLog`（Loki），支援依日期區間與小時篩選。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/log/odd` | 查詢賠率異動紀錄 V1（OddLog） |
| GET | `/api/v1/log/oddv2` | 查詢賠率異動紀錄 V2（DeveloperLog，Loki） |

---

## 3. V2 查詢參數

| 參數 | 必填 | 說明 |
|------|------|------|
| `gameType` | ✅ | 球種代碼（如 BK、BS） |
| `site` | ✅ | 站台代碼 |
| `sitelid` | ✅ | 站台聯盟 id |
| `sitegid` | ✅ | 站台賽事 id |
| `mode` | ✅ | 賠率模式（如 HA、OU）；`Match`、`PlayByPlay` 查 MatchLog |
| `startDate` | ❌ | 開始日期（yyyy-MM-dd）；缺省預設為該場賽事 `GDate` |
| `endDate` | ❌ | 結束日期（yyyy-MM-dd）；缺省預設為該場賽事 `GDate` |
| `startHour` | ❌ | 起始小時（0–23，預設 0） |
| `endHour` | ❌ | 結束小時（0–23，預設 23） |
| `startMinute` | ❌ | 起始分鐘（0–59，預設 0） |
| `endMinute` | ❌ | 結束分鐘（0–59，預設 59） |

---

## 4. 流程總覽（V2）

1. Controller 接收 GET 請求，通過 ECFramework 驗證。
2. `OddLogService.GetOddLogV2` 驗證必填參數與 hour 範圍（0–23）。
3. 依 `gameType/site/sitelid/sitegid` 查詢 `SiteGame`，取得賽事日期 `GDate`。
4. 解析日期：`startDate` 或 `endDate` 未傳時，各自預設為 `GDate`。
5. 若 `endDate < startDate`，回傳 HTTP 400。
6. 組 Loki 查詢時間範圍：
   - 開始：`startDate` + `startHour:startMinute:00`
   - 結束：`endDate` + `endHour:endMinute:59`
7. 若結束時間早於開始時間，回傳 HTTP 400。
8. 依 `mode` 呼叫 Loki：
   - `Match` / `PlayByPlay` → `GetMatchLogFormLoki`
   - 其他 → `GetOddLogFormLoki`
9. 解析 log 字串中的 `AddTime`，組裝 `DeveloperLog` 列表並依時間排序回傳。

---

## 5. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `PriceCenterServiceController.GetOddLogV2` | 接收 query 參數 |
| 2 | Service | `OddLogService.GetOddLogV2` | 驗證、解析日期、組 Loki 時間 |
| 3 | Provider | `SiteGameDataProvider.GetSiteSingleGameBySiteGID` | 取得賽事與 GDate |
| 4 | Provider | `OddLogProvider.GetOddLogFormLoki` / `GetMatchLogFormLoki` | 向 Loki query_range 查詢 |
| 5 | Service | `OddLogService.GetOddLogV2` | 解析 log、回傳 `List<DeveloperLog>` |

---

## 6. 重要規則

- **日期預設**：`startDate`、`endDate` 可獨立省略；省略者預設為該場賽事的 `GDate`（非系統今日）。
- **Loki 時間窗口**：查詢範圍由 API 參數決定，不再使用「賽事日期 ±1 天」固定窗口。
- **時段邊界**：開始時間秒數固定 `00`；結束時間秒數固定 `59`。分鐘由 `startMinute`（預設 0）、`endMinute`（預設 59）指定。
- **跨日查詢**：允許 `startDate` 與 `endDate` 不同，例如前一日 22:00 至隔日 02:59。
- **mode 分支**：`Match`、`PlayByPlay` 使用 MatchLog job；其餘 mode 使用 OddLog job。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 缺少 `site` / `sitelid` / `sitegid` / `mode` | HTTP 404 Not Found |
| `startHour` 或 `endHour` 不在 0–23 | HTTP 400 Bad Request |
| `startMinute` 或 `endMinute` 不在 0–59 | HTTP 400 Bad Request |
| `endDate < startDate` | HTTP 400 Bad Request（`endDate < startDate`） |
| 同天但 `startHour > endHour` 導致時間區間無效 | HTTP 400 Bad Request（`invalid time range`） |
| 查無 log | HTTP 200，body 為空陣列 `[]` |

---

## 8. 呼叫範例

```
GET /api/v1/log/oddv2?gameType=BK&site=bet365.com&sitelid=123&sitegid=456789&mode=HA

GET /api/v1/log/oddv2?gameType=BK&site=bet365.com&sitelid=123&sitegid=456789&mode=HA&startDate=2025-06-28&endDate=2025-06-29&startHour=10&startMinute=30&endHour=18&endMinute=45
```

---

## 9. Evidence

| 類型 | 來源 |
|------|------|
| API | `PriceCenterServiceController.GetOddLogV2` |
| Service | `OddLogService.GetOddLogV2` |
| Provider | `OddLogProvider.GetOddLogFormLoki` / `GetMatchLogFormLoki` |
| OpenAPI | `aidata/webapi/pricecenterservice/pricecenterservice.json` |
