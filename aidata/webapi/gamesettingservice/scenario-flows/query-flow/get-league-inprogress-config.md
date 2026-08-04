# 查詢聯賽進行中設定

## 1. 場景目的
後台管理人員查詢指定商家 (`businessCode`) 與遊戲類型 (`gameType`) 的聯賽進行中設定，藉此取得目前已套用且進行中的聯賽列表與設定內容，供前台投注顯示或後台確認配置使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/leagueinprogressconfigs/{businessCode}/{gameType}` | 查詢聯賽進行中設定 |

---

## 3. 流程總覽

1. 接收 GET 請求，路徑包含 `businessCode` 與 `gameType`
2. 驗證請求方是否帶有有效的認證資訊 (ECFramework 驗證)
3. 將 `businessCode` 與 `gameType` 傳入 Service 層
4. Service 層查詢 `gamesettings.league_logs` 表
5. 將查詢結果轉換為對外 DTO
6. 回傳聯賽進行中設定 (包含聯賽列表等資訊)

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Middleware | ECFramework AuthFilter | 驗證請求權杖 |
| 2 | Controller | `ConfigController.GetLeagueInProgressConfig` | 接收 `businessCode`, `gameType` 參數，呼叫 Service |
| 3 | Service | `IConfigService.GetLeagueInProgressConfig` | 調用 Provider 查詢資料 |
| 4 | Provider | Cassandra Provider | 執行 CQL 查詢 `gamesettings.league_logs` |
| 5 | Transfer | DTO Mapper | 將 `league_logs` 實體轉換為 API 回應 DTO，排除敏感欄位 |
| 6 | Controller | `ConfigController.GetLeagueInProgressConfig` | 回傳 HTTP 200 與 DTO |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `gamesettings.league_logs` | Read | 以 `company` (即 `businessCode`) + `gametype` 查詢進行中聯賽設定 |
| Redis | 無 | 無 | 依現有資訊，本操作無 Redis 快取機制，直接查詢 Cassandra |
| Queue | 無 | 無 | 此查詢不觸發任何 Queue 或 Kafka 事件 |

---

## 6. 重要規則

- **權限限制**：必須通過 ECFramework 驗證，確保請求方具有後台管理權限。
- **查詢條件**：必須指定 `company` (等同 `businessCode`) 與 `gametype` 作為查詢條件，不可全表掃描。
- **不可暴露資料**：回傳的 DTO 中不可包含任何內部敏感資訊（如 `password`, `authtoken` 等）。此表無明顯敏感欄位，但仍須確保未揭露內部實作細節。
- **欄位限制**：`league_logs` 表的 `leagues` 欄位為 `list<text>` 型態，服務應原樣回傳或進行必要的前端可讀轉換，不可變更其資料本質。
- **狀態值限制**：此查詢不涉及狀態值限制，僅回傳已儲存的設定。
- **不可修改欄位**：此為查詢操作，不涉及任何欄位修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未提供有效的認證權杖或認證已過期 | 回傳 HTTP 401 Unauthorized |
| 提供的 `businessCode` 不存在於 `gamesettings.league_logs` 表 | 回傳空結果或對應的 HTTP 404 / 204，需人工確認具體實作 |
| 提供的 `gameType` 不存在或不合法 | 回傳空結果，不應回傳其他 `gameType` 的資料 |
| 資料庫連線逾時或查詢失敗 (Cassandra timeout) | 回傳 HTTP 500 Internal Server Error，並記錄錯誤日誌 |
| DTO 轉換過程中發生類型不匹配錯誤 | 回傳 HTTP 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| LIP-01 | API Test | 以有效管理者權杖查詢存在的 `businessCode` 與 `gameType` | HTTP 200，回傳包含 `leagues` 列表的 JSON |
| LIP-02 | Permission Test | 使用無效或過期的權杖進行請求 | HTTP 401 |
| LIP-03 | Permission Test | 使用無後台權限的帳號進行請求 | HTTP 403 (需人工確認具體權限控制粒度) |
| LIP-04 | Flow Test | 查詢一個不存在的 `businessCode` | HTTP 200 但回傳空資料，或 HTTP 404 |
| LIP-05 | Flow Test | 查詢存在的 `businessCode` 但不存在的 `gameType` | HTTP 200 但回傳空資料 |
| LIP-06 | Integration Test | 在 DB 中插入一筆 `league_logs` 資料後立即查詢 | 能正確回傳剛插入的資料 |

---

## 9. 高風險區域

- **直接全表掃描**：若實作中未正確以 `company` 和 `gametype` 作為查詢條件，將導致在 Cassandra 中進行昂貴的全表掃描，嚴重影響效能。
- **權限驗證繞過**：若 ECFramework 驗證中介軟體未正確配置於此路由，可能導致未經授權的資料存取。

---

## 10. 常見錯誤

- ❌ 前端或新人誤以為此 API 會因賽事狀態變動而「即時」反映，但此設定仰賴後台設定或同步服務更新 `league_logs` 表。
- ❌ 在查詢時未傳入 `gameType`，或 Service 層未將其作為查詢條件，導致回傳了整個 `businessCode` 下的所有設定。
- ❌ AI 或開發者在測試時直接拼接 CQL，未使用參數化查詢，可能導致語法錯誤或注入風險。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | `README.md` - `GET /api/v1/leagueinprogressconfigs/{businessCode}/{gameType}` |
| Controller | `ConfigController` (推斷自 README 分類) |
| Service 介面 | `IConfigService` (推斷自 code semantics 中的 `GetBusinessGameTypeLeagueLog`) |
| DB Table | `gamesettings.league_logs` |
| DB Schema | `league_logs` 建立語句: `PRIMARY KEY (company, gametype)` |
| 驗證機制 | `README.md` - 驗證框架: ECFramework.ECService 2.0.0 |
| 快取 | `gamesettingservice-detail.md` - "本服務未直接使用 Redis（所有查詢均直接存取 Cassandra）" |