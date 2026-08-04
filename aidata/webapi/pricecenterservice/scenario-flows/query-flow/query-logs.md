# 查詢日誌

## 1. 場景目的

提供管理後台查詢系統操作統計、工具操作日誌、資料來源日誌及盤口擴展日誌，用於審計與問題排查。所有查詢皆為唯讀。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/log/action/{date}` | 查詢操作統計 |
| GET | `/api/v1/log/game/{date}` | 查詢工具操作日誌 |
| GET | `/api/v1/log/datum/{gDate}/{gameType}` | 查詢資料來源日誌 |
| GET | `/api/v1/inplayspreadlogs/{gDate}/{gameType}/{gid}` | 查詢盤口擴展日誌 |

---

## 3. 流程總覽

1. Controller 接收 HTTP GET 請求，路徑參數包含日期、遊戲類型、賽事ID。
2. 請求通過 `ECFramework.ECService` 驗證框架進行身分驗證。
3. `LogController` 將請求參數傳遞至 `PriceService`。
4. `PriceService` 根據日誌類型呼叫對應的 Provider 或查詢方法。
5. 查詢 Cassandra 或 MySQL (Sport DB) 取得日誌資料。
6. 將結果序列化後透過 HTTP 200 回傳。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `LogController.GetActionStatistics` | 接收 `date` 參數，調用 Service |
| 2 | Controller | `LogController.GetGameLogs` | 接收 `date` 參數，調用 Service |
| 3 | Controller | `LogController.GetDatumLogs` | 接收 `gDate`, `gameType` 參數，調用 Service |
| 4 | Controller | `LogController.GetInplaySpreadLogs` | 接收 `gDate`, `gameType`, `gid` 參數，調用 Service |
| 5 | Service | `PriceService.QueryActionLogs` | 依據日期查詢操作統計資料 |
| 6 | Service | `PriceService.QueryGameLogs` | 依據日期查詢工具操作日誌 |
| 7 | Service | `PriceService.QueryDatumLogs` | 依據日期與遊戲類型查詢資料來源日誌 |
| 8 | Service | `PriceService.QueryInplaySpreadLogs` | 查詢盤口擴展日誌 |
| 9 | Provider | `LogProvider` / Cassandra Query | 執行實際資料庫查詢 |

> **需人工確認**：Provider 具體類別名稱與 Cassandra Query 語句需從 `PriceService` 或 `LogProvider` 的實際代碼中確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `pricecenter.datum_logs` | Read | 查詢資料來源日誌 |
| DB (Cassandra) | `pricecenter.games` (推測) | Read | 可能用於盤口擴展日誌查詢需人工確認 |
| DB (MySQL) | `sport` (推測) | Read | 部分操作統計可能來自 MySQL 報表需人工確認 |
| Cache | 無 | - | 本場景未使用 Redis |
| Queue | 無 | - | 日誌寫入可能經由 Kafka，但查詢為唯讀，不涉及 Queue 操作 |

---

## 6. 重要規則

- **權限限制**：所有日誌 API 皆需驗證（✅）。僅授權的管理員或後台服務可訪問。
- **唯讀操作**：所有查詢僅執行 `SELECT`，不允許任何寫入或修改行為。
- **欄位限制**：
  - 不可回傳敏感欄位（如 `password`, `phone`, `AuthKey`, `Balance`）。
  - 盤口擴展日誌查詢須以 `gDate`, `gameType`, `gid` 作為必要條件，避免全表掃描。
- **狀態值限制**：無特定狀態過濾，但查詢可能依日期範圍限制。
- **不可修改欄位**：日誌資料為不可變記錄（append-only），查詢端無修改風險。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未提供驗證 Token | 回傳 HTTP 401 Unauthorized |
| 權限不足 | 回傳 HTTP 403 Forbidden |
| 日期格式錯誤（例如 `2025/04/10`） | 回傳 HTTP 400 Bad Request，提示格式應為 `yyyy-MM-dd` |
| 查無資料（無符合條件的日誌） | 回傳 HTTP 200 OK，body 為空陣列 `[]` |
| DB timeout | 回傳 HTTP 500 Internal Server Error |
| Cassandra 無法連線 | 回傳 HTTP 503 Service Unavailable |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| QT-01 | API Test | 查詢操作統計 (`GET /log/action/2025-04-10`) | 200 OK，回傳統計資料陣列 |
| QT-02 | API Test | 查詢工具日誌 (`GET /log/game/2025-04-10`) | 200 OK，回傳日誌陣列 |
| QT-03 | API Test | 查詢資料來源日誌 (`GET /log/datum/2025-04-10/BS`) | 200 OK，回傳資料來源記錄 |
| QT-04 | API Test | 查詢盤口擴展日誌 (`GET /inplayspreadlogs/2025-04-10/BS/GID123`) | 200 OK，回傳擴展記錄 |
| QT-05 | Permission Test | 無 Token 訪問日誌 API | 401 Unauthorized |
| QT-06 | Flow Test | 使用無效日期格式請求 (`2025/04/10`) | 400 Bad Request |

---

## 9. 高風險區域

- **資料量過大**：若查詢未限制日期或範圍，可能導致 Cassandra 查詢逾時或記憶體不足。API 設計應強制要求日期或主要過濾條件。
- **敏感資料洩漏**：`datum_logs` 或操作日誌中可能包含 IP、帳號等資訊。回傳前需確保 DTO 已排除敏感欄位
- **Cassandra 查詢效能**：partition key 設計未知，若包含 `gameType` 的複合鍵未正確使用，可能導致跨節點掃描。

---

## 10. 常見錯誤

- ❌ **未傳遞必要的路徑參數**：例如查詢資料來源日誌時僅傳 `gDate` 而無 `gameType`。
- ❌ **日期格式錯誤**：傳遞非 `yyyy-MM-dd` 格式的日期字串。
- ❌ **跨權限查詢**：使用未授權的 Token 訪問管理後台 API。
- ❌ **誤解日誌為即時資料**：日誌通過 Kafka 寫入 Cassandra 存在延遲，查詢最近幾秒的日誌可能得不到結果。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md: 日誌查詢 API 路由表 |
| DB | Cassandra `pricecenter.datum_logs` 為資料來源日誌儲存 |
| DB | `sport-detail.md` 確認 pricecenterservice 僅有讀取權限 |
| Code | Phase 0/1 分析結果顯示 `LogController` 處理日誌請求 |
| Rules | `pricecenter-detail.md` 與 `sport-detail.md` 中的跨服務操作限制 |
| Rules | `service detail` 指出本服務未使用 Redis 且不負責錢包/聊天/站內信寫入 |