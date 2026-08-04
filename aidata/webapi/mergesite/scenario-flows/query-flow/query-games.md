# 查詢賽程列表

## 1. 場景目的

提供管理後台人員依據指定球種與日期查詢每日賽程資訊，並支援選擇性使用賽事狀態進行篩選，以便快速掌握各球種當日賽事分佈與進行狀況。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/games/{gameType}/{date}` | 依據球種與日期查詢賽程列表，可選填 status 篩選 |

---

## 3. 流程總覽

1. 前端呼叫 `GET /api/games/{gameType}/{date}`，攜帶必要路徑參數與選擇性查詢參數 `status`。
2. mergesite API（ASP.NET Core）接收請求，由 Controller 解析 `gameType`、`date` 與 `status` 參數。
3. 透過 PriceCenterService Gateway（`192.168.55.60`）呼叫遠端 REST API，轉發查詢條件。
4. PriceCenterService 處理查詢，從底層資料源（實際 DB 對 mergesite 透明）取得賽程資料。
5. 取得結果後，轉換為 `GameDTO` 列表返回給呼叫端。
6. 呼叫端接收 HTTP 200 與 `GameDTO` 陣列，完成查詢。

> **備註**：mergesite 無直接資料庫，所有資料存取均透過 PriceCenterService，因此實際 SQL 或 Cache 策略由該服務負責，此處僅描述合約層級的行為。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GameController.GetGames(gameType, date, status)` | 接收 request，調用 Service 層方法 |
| 2 | Service | `GameService.GetGames(gameType, date, status)` | 組織請求參數，調用 PriceCenterService 的 Provider |
| 3 | Provider | `PriceCenterProvider.GetGamesAsync(...)` | 透過 HTTP Client 向 PriceCenterService API 發送 GET 請求（含 gameType, date, status） |
| 4 | Transfer | `GameDTO` | 將遠端回應的反序列化物件映射為 `GameDTO` 列表 |
| 5 | Controller | `GameController.GetGames(...)` | 將 `GameDTO` 列表封裝為 HTTP 200 回應返回 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| API | PriceCenterService | Read | mergesite 轉發查詢請求；實際 DB 操作對 mergesite 透明 |

> **注意**：mergesite 本身未使用 Redis、Kafka、Queue。PriceCenterService 內部是否使用 Cache 未知，但 mergesite 端不參與快取邏輯。

---

## 6. 重要規則

- **權限限制**：需通過 ECCore 驗證機制，僅允許已認證的使用者（如管理後台人員）存取。
- **欄位限制**：`gameType` 與 `date` 為必填路徑參數，不得為空。`status` 為選填查詢參數，其有效值應由業務定義（如 `Scheduled`、`Live`、`Finished` 等），非法值應被忽略或回傳空集合。
- **不可暴露資料**：PriceCenterService 回傳的原始資料中若含有內部機敏欄位，應在 `GameDTO` 轉換層過濾，僅回傳前台所需欄位（如 `GID`, `LID`, `GDate`, `Status`, `HomeTeam`, `AwayTeam`, `StartTime` 等）。
- **Time-to-Live (TTL)**：不適用。
- **Transaction 規則**：此為唯讀查詢，不涉及 Transaction。
- **Retry 規則**：若呼叫 PriceCenterService 失敗，mergesite 端可能依 HTTP Client 策略進行有限次數重試（需人工確認實際 Polly 設定）。
- **狀態值限制**：`status` 的枚舉值應與 PriceCenterService 定義一致，前端傳入值若不符預期，應回傳空集合而非拋出 500 錯誤。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未通過驗證或 Token 過期 | HTTP 401 Unauthorized，不執行查詢 |
| `gameType` 傳入不支援的球種代碼 | 需人工確認：可能回傳 HTTP 200 但空陣列，或由 PriceCenterService 回傳 4xx |
| `date` 格式錯誤（非 `yyyy-MM-dd`）| HTTP 400 Bad Request，Model Binding 階段失敗 |
| 呼叫 PriceCenterService 超時或連線失敗 | HTTP 502 Bad Gateway 或 504 Gateway Timeout |
| PriceCenterService 回傳 5xx 錯誤 | mergesite 轉發非 200 狀態碼，可能為 502 或直接回傳上游錯誤碼 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| GAME-01 | API Test | 以合法 `gameType` 及 `date` 查詢，不帶 `status` | HTTP 200；回傳當日所有賽程 `GameDTO[]` |
| GAME-02 | API Test | 查詢時帶入有效 `status`（如 `Live`） | HTTP 200；回傳符合該狀態的賽程 |
| GAME-03 | Permission Test | 未帶驗證 Token 發送請求 | HTTP 401 Unauthorized |
| GAME-04 | Validation Test | `date` 參數格式為 `2026/06/01` | HTTP 400 Bad Request |
| GAME-05 | Validation Test | `status` 傳入未定義值（如 `Unknown`） | 需人工確認，預期 HTTP 200 空陣列或 400 Bad Request |
| GAME-06 | Flow Test | PriceCenterService 無響應 | mergesite 回應 502/504，並記錄錯誤 Log（可能寫入 Kafka） |

---

## 9. 高風險區域

- **高風險 API**：對 PriceCenterService 的強依賴。若該服務不穩定或賽程資料延遲，本查詢將直接受到影響。
- **跨服務資料同步**：賽程資料由外部服務（如 data-feed-service）同步至 PriceCenterService 底層 DB，此查詢不負責同步，但資料延遲將影響管理後台的即時性判斷。
- **Cache consistency**：mergesite 本身無 Cache，若 PriceCenterService 內部有快取，存在快取不一致風險，但 mergesite 無法介入。
- **Idempotency**：此為 GET 查詢，具備天然的冪等性，無額外風險。

---

## 10. 常見錯誤

- **新人容易犯錯**：混淆 `/api/games/{gameType}/{date}`（查詢賽程）與 `/api/merge/openclawmerge/{gameType}`（查詢合併資料），誤用 API 導致得到非預期的 OpenClaw 合併結果。
- **AI 容易誤解**：誤以為 mergesite 直接查詢 MySQL `bk_siteplayers` 或其他表，實際上 mergesite 不直接操作任何 DB，資料皆來自 PriceCenterService。
- **常見漏檢查項目**：忘記驗證 `status` 參數有效性，將任意字串直接傳給 PriceCenterService，可能觸發未知錯誤。
- **常見錯誤流程**：前端未處理 `status` 為空的情況，導致無法顯示「全部賽程」；或因 `date` 格式校驗不嚴謹，傳送不合規日期給 API。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI: `GET /api/games/{gameType}/{date}` |
| DTO | OpenAPI Response: `GameDTO` array |
| DB | mergesite-detail.md: 「本服務無直接資料庫，資料讀寫均透過 PriceCenterService 進行」 |
| Gateway | README: PriceCenterService（Gateway: 192.168.55.60） |
| Auth | OpenAPI tags: `Game`, README: 「需要驗證 ✅」|
| Log | README: Kafka（192.168.55.60）用於應用程式 Log 寫入 |