# 建立模板玩法設定

## 1. 場景目的

提供運營人員一個可重複使用的玩法配置模板，設定後可供後續的聯賽設定或單場遊戲設定套用，減少重複配置工作。此模板以 `businessCode` + `gameType` 為維度進行管理。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/playmodeconfigs/template` | 建立新的模板玩法設定 |

需要驗證：✅

---

## 3. 流程總覽

1. 接收建立模板玩法的 request，包含 `company`、`gameType`、`name`、`settings` 等參數
2. 驗證操作者權限（透過內部驗證框架）
3. 驗證 `settings` 欄位為合法 JSON 字串
4. 產生唯一的模板 ID
5. 寫入 Cassandra `gamesettings.template_settings` 表
6. 同時記錄操作日誌至 Cassandra `pricecenter.action_logs`（或對應日誌表）
7. 回傳建立成功的模板設定資訊

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `ConfigController.CreateTemplatePlayModeConfig` | 接收 request 並轉送至 Service |
| 2 | Service | `IConfigService.CreateTemplatePlayModeConfig` | 處理業務邏輯、驗證與資料組裝 |
| 3 | Provider | （需人工確認） | 將資料寫入 Cassandra |
| 4 | Validator | （需人工確認） | 檢查 `settings` 為合法 JSON、`company` 與 `gameType` 不為空 |
| 5 | Transfer | DTO 轉換邏輯（需人工確認） | 將 request body 映射至 Cassandra entity |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB（Cassandra） | `gamesettings.template_settings` | Write（INSERT） | 儲存模板玩法設定 |
| DB（Cassandra） | `pricecenter.action_logs` | Write（INSERT） | 記錄操作日誌（審計需求） |
| Redis | 此流程未直接使用 | – | README 標註 Redis 用於 LoginCache / BusinessCache，本場景未涉及 |

---

## 6. 重要規則

- **權限限制**：必須通過內部驗證框架 (`ECFramework.ECService`) 驗證，無有效憑證則拒絕請求。
- **欄位限制**：`settings` 必須為合法 JSON 字串，不可包含非序列化物件。
- **不可暴露資料**：回傳的設定內容中不應包含任何敏感內部資料（如內部服務 token）。
- **Transaction 規則**：Cassandra 寫入為最終一致性，無跨表 transaction 保證，但 `template_settings` 與 `action_logs` 寫入應視為同一業務操作。
- **Retry 規則**：需人工確認是否有 retry 機制，或仰賴 Cassandra 自帶的 `speculative_retry` 策略。
- **狀態值限制**：模板設定本身沒有 `enabled` 欄位（需人工確認 schema），狀態控制可能在套用模板時才發生。
- **不可修改欄位**：建立後，`id`（主鍵）不可更新。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| request 中 `settings` 不是合法 JSON | 回傳 400 Bad Request，並提示格式錯誤 |
| 缺少必要欄位（如 `company`、`gameType`） | 回傳 400 Bad Request，並提示缺少欄位 |
| 驗證失敗（無有效 auth token） | 回傳 401 Unauthorized |
| Cassandra 寫入失敗或 timeout | 回傳 500 Internal Server Error |
| `company` 與 `gameType` 組合已存在相同模板名稱（需人工確認唯一性約束） | 回傳 409 Conflict 或依業務規則覆蓋 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 正常建立模板 | 回傳 200，DB 可查詢到新模板 |
| TC02 | API Test | `settings` 傳入非法 JSON 字串 | 回傳 400 |
| TC03 | Permission Test | 無 token 呼叫 | 回傳 401 |
| TC04 | Integration Test | Cassandra 暫時不可用 | 服務能回傳 500 且不 crash |
| TC05 | API Test | 查詢剛建立的模板 (`GET .../template/{businessCode}/{gameType}/{id}`) | 能正確回傳模板內容 |

---

## 9. 高風險區域

- **高風險 table**：`gamesettings.template_settings` — 寫入失敗或資料不一致會影響後續聯賽／遊戲設定。
- **高風險 API**：若此 API 被大量調用且無 rate limit，可能造成 Cassandra 寫入壓力。
- **跨服務資料同步**：目前無明確同步機制，若其他服務（如 `gamesettingsite`）直接讀取此表，需確保讀取一致性。
- **Cache consistency**：此場景未直接使用 Redis，但若後續查詢端點使用快取，需注意模板更新時的快取失效策略。
- **Idempotency**：若重複呼叫相同參數是否會重複建立模板？需人工確認是否有冪等設計。

---

## 10. 常見錯誤

- **新人容易犯錯**：未驗證 `settings` 為合法 JSON 就直接寫入，導致後續讀取時解析失敗。
- **AI 容易誤解**：誤以為此 API 會同時更新 `game_settings` 或 `league_settings`，實際上模板僅為設定模板，套用需透過其他 API。
- **常見漏檢查項目**：忘記檢查 `company` 是否屬於該操作者的權限範圍（跨公司查詢限制）。
- **常見錯誤流程**：建立模板後未記錄操作日誌，導致審計追蹤遺失。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README: `POST /api/v1/playmodeconfigs/template` |
| DB | Cassandra `gamesettings` keyspace |
| Code | `IConfigService` — `CreateTemplatePlayModeConfig` （需人工確認確切實作） |
| Rule | `gamesettingservice-detail.md` → `settings` 須為合法 JSON |
| Rule | README → 驗證依賴 `ECFramework.ECService` |

> **需人工確認**：
> 1. `template_settings` table 完整 schema（目前未提供完整定義，僅在 DB 語意中作為 `game_settings` 類似結構被推斷）。
> 2. 確切的 Service / Validator 實作細節，以及是否有 idempotency 機制。
> 3. 建議新增文件：`template_settings` 的獨立 db-detail 說明（類似 gamesettings-detail.md）。