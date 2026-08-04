# 訂閱者註冊

## 1. 場景目的

外部系統透過此流程完成遊戲設定的訂閱者註冊，寫入訂閱者基本資料。此流程是訂閱者管理的前置條件，註冊後方可使用帳號進行登入、查詢等操作。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/subscriber/register` | 訂閱者註冊，需驗證 |

---

## 3. 流程總覽

1. 接收訂閱者註冊 request
2. 驗證 request 結構與必要欄位
3. 依據品牌（brand）決定寫入目標 Cassandra `accounts_{brand}` 表
4. 檢查 `account` 是否已存在
5. 對密碼執行 bcrypt 強雜湊
6. 寫入 Cassandra `accounts_{brand}` 表
7. 記錄操作日誌至 Cassandra `action_logs`
8. 回傳註冊成功或失敗

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | GameSettingServiceController.SubscriberRegister | 接收 request，呼叫 SubscriberService |
| 2 | Service | SubscriberService.Register | 驗證輸入、決定目標 brand table、檢查帳號唯一性 |
| 3 | Provider | SubscriberProvider | 封裝 Cassandra CQL 操作 |
| 4 | Validator | SubscriberValidator | 驗證 account / password 格式、欄位限制 |
| 5 | Provider | CassandraWrite `INSERT INTO accounts_{brand}` | 寫入資料 |
| 6 | Provider | CassandraWrite `INSERT INTO action_logs` | 記錄註冊操作 |

（註：SubscriberService、SubscriberProvider、SubscriberValidator 皆為從路由映射推斷的命名，需人工確認實際 class 名稱）

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB（Cassandra） | `pricecenter.accounts_{brand}` | Write（INSERT） | 寫入訂閱者帳號資料 |
| DB（Cassandra） | `pricecenter.action_logs` | Write（INSERT） | 記錄註冊操作日誌 |
| Redis | LoginCache | 無直接操作 | 後續登入時寫入 session；註冊階段無 cache 操作 |
| Kafka | － | 無直接操作 | 日誌透過 Cassandra 記錄；無 queue 非同步 |

---

## 6. 重要規則

- **驗證要求**：此 API 需經過 `ECFramework.ECService` 統一驗證框架（證據：README 路由標示 `✅`）
- **密碼儲存**：必須使用 bcrypt / pbkdf2 強雜湊，禁止明文或 MD5 寫入（證據：`db-usage` 寫入限制）
- **帳號不可更新**：`account` 為主鍵，建立後不可異動（證據：`db-usage` 寫入限制）
- **品牌隔離**：所有操作須指定對應品牌表（如 `accounts_AU8`），不可跨品牌寫入（證據：`db-usage` 品牌隔離規則）
- **不可回傳欄位**：`password`、`handler` 不得於任何 API response 回傳（證據：`db-usage` 不可回傳欄位）
- **enabled 預設值**：INSERT 時 `enabled` 預設為 1（啟用）（證據：`pricecenter-detail` 值定義）
- **TTL**：帳號表無預設 TTL（`default_time_to_live = 0`）（證據：`pricecenter` schema）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `account` 已存在於目標品牌表 | 回傳 409 Conflict 或自訂錯誤碼（需人工確認錯誤回傳格式） |
| 密碼為空或格式不符（如長度不足） | 回傳 400 Bad Request |
| Cassandra `accounts_{brand}` 寫入失敗（timeout / unavailable） | 回傳 500 Internal Server Error |
| 未經驗證呼叫 API | 回傳 401 Unauthorized |
| request body 缺少必要欄位 | 回傳 400 Bad Request |
| 跨品牌寫入（如寫入非對應 brand 的表） | 邏輯錯誤，應被品牌隔離規則攔截 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SUB-REG-01 | Integration Test | 正常註冊新 account，使用合法密碼 | 201 Created，可查到該 account 且 enabled=1 |
| SUB-REG-02 | API Test | 傳入缺少 account 欄位的 request | 400 Bad Request |
| SUB-REG-03 | Permission Test | 無驗證 header 呼叫註冊 API | 401 Unauthorized |
| SUB-REG-04 | Flow Test | 重複註冊相同 account | 409 Conflict 或對應錯誤碼 |
| SUB-REG-05 | Flow Test | 密碼寫入前確認已 hash | `accounts_{brand}` 中 password 非明文 |
| SUB-REG-06 | Flow Test | 註冊後使用密碼登入 | 登入成功（後續流程驗證 bcrypt verify 可正常比對） |
| SUB-REG-07 | Flow Test | 註冊後 GET 查詢該 account | response 不包含 password 欄位 |

---

## 9. 高風險區域

- **高風險 table**：`pricecenter.accounts_{brand}`（直接影響登入驗證與各服務帳號控管）
- **高風險 API**：POST `/api/v1/subscriber/register`（具備寫入權限，需嚴格驗證輸入）
- **密碼明文洩漏**：若 `password` 寫入為明文，或 GET API 回傳此欄位，將造成安全漏洞
- **跨品牌寫入**：誤將帳號寫入錯誤品牌表，會導致帳號無法登入或跨品牌資料外洩
- **操作日誌遺漏**：若 `action_logs` 寫入失敗未正確處理，後續無法追溯註冊操作紀錄
- **Idempotency**：需人工確認是否有設計 idempotency key 機制，避免重複 request 建立多筆相同帳號

---

## 10. 常見錯誤

- ❌ 寫入 `password` 時使用明文 → ✅ 必須先以 bcrypt 等強雜湊處理
- ❌ GET 訂閱者列表回傳 `password` 欄位 → ✅ DTO 轉換時明確排除
- ❌ 未指定品牌表名稱寫入 → ✅ 所有 Cassandra 操作須指定 `accounts_{brand}`
- ❌ 新人誤解「訂閱者」為 `subscriptionservice` 責任 → ✅ 此處僅為帳號註冊，訂閱管理由 `subscriptionservice` 負責（證據：`gamesettings-detail` 本服務不負責事項）
- ❌ AI 誤判訂閱者資料儲存在 MySQL `gm` 或 `gamesettings` keyspace → ✅ 訂閱者帳號寫入 `pricecenter` keyspace（證據：`pricecenter` schema 含 `accounts_*` 系列表）

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `GameSettingServiceController` - POST `/api/v1/subscriber/register` |
| DB | `pricecenter.accounts_{brand}` |
| DB | `pricecenter.action_logs` |
| 規則 | `db-usage` - password 強雜湊、account 不可更新、品牌隔離、不可回傳欄位 |
| 規則 | `pricecenter-detail` - enabled 預設 1、closetime 非空不可逆 |
| 技術棧 | Cassandra、Redis LoginCache、ECFramework.ECService 驗證 |

---

## 需人工確認事項

- 訂閱者資料表確認為 `pricecenter.accounts_{brand}` 或另有 `subscriber_*` 專用表？目前 Context 中未見 subscriber 專用 table，推斷使用 `accounts_{brand}`
- `SubscriberService` / `SubscriberProvider` / `SubscriberValidator` 實際 class 名稱與所在的專案結構
- 操作日誌 `action_logs` 寫入的實作細節（同步寫入或非同步 queue）
- 是否有 idempotency key 設計（如使用 requestId 避免重複 INSERT）
- `password` 欄位在部分 `accounts_*` 表（如 `accounts_HGA`）未見於 schema，需確認帳號表完整欄位定義