# 寫入商家操作日誌

## 1. 場景目的
將商家相關的後台操作記錄（如建立、更新、刪除設定）寫入 Cassandra `pricecenter.action_logs` 表，作為審計追蹤與後續查詢的基礎。所有對遊戲設定、聯賽設定、模板設定等業務資料的異動，都應透過此流程留下一筆不可竄改的 log。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/businesses/{businessCode}/logs` | 由後台管理端呼叫，寫入一筆商家操作日誌 |

---

## 3. 流程總覽

1. 前端或後台服務呼叫寫入日誌 API，攜帶 `businessCode` 及 log 內容
2. Controller `BusinessController` 接收請求，驗證 auth（ECFramework.ECService）
3. Service `BusinessService` 組裝 `BusinessLog` 物件，填入 businessCode、actionType、content、updater 等欄位
4. 透過 `IActionLogService` 寫入 Cassandra `pricecenter.action_logs` 表
5. Cassandra 寫入成功後，回傳 `200 OK`；失敗則拋出 exception

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `BusinessController.WriteBusinessLog` | 接收 POST request，驗證授權，呼叫 Service |
| 2 | Service | `IBusinessService.WriteBusinessLog` | 組裝 `BusinessLog` model，設定 updater 為當前登入者 |
| 3 | Provider | `IActionLogService.AddActionLog` | 將 log 寫入 `pricecenter.action_logs` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Cassandra | `pricecenter.action_logs` | Write | 儲存商家操作日誌，欄位含 businessCode、actionType、content、updater、addtime |
| MySQL | `gm.teams` | Read | 需人工確認：若驗證包含 team token 檢查，則會讀取此表 |
| Redis | N/A | N/A | 本流程未直接使用 Redis |
| Kafka | N/A | N/A | 本流程未直接使用 Kafka（日誌直接寫入 Cassandra） |

---

## 6. 重要規則

- **權限限制**：API 需通過 ECFramework 驗證（ECService 2.0.0）。僅具備 `Business` 管理權限的帳號可呼叫。
- **不可暴露資料**：`action_logs` 中的 `content` 若包含密碼或 authtoken 等敏感欄位，寫入前必須過濾（需人工確認目前實作是否已過濾）。
- **欄位限制**：`businessCode` 必須是已存在的商家代碼；`actionType` 需符合定義（如 create、update、delete、status_change）。`updater` 自動填入當前操作者帳號，不接受 request body 指定。
- **狀態值限制**：無特定狀態機限制，但 `addtime` 應為 server 端寫入時間。
- **Transaction 規則**：日誌寫入應為獨立操作，不應與業務資料異動包在同一個跨表 transaction 中（Cassandra 不支援跨表交易）。若業務寫入成功但日誌寫入失敗，應視為「需人工確認」的情境。
- **TTL 規則**：需人工確認 `action_logs` 是否有 TTL 設定。根據現有文件，未明確提及 TTL。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未攜帶有效 token | 回傳 401 Unauthorized |
| businessCode 不存在 | 回傳 400 Bad Request 或 404 Not Found（具體需人工確認） |
| request body 格式錯誤（缺少必要欄位） | 回傳 400 Bad Request |
| Cassandra 寫入 timeout | 回傳 500 Internal Server Error，需觸發 alert |
| Cassandra 連線失敗 | 回傳 503 Service Unavailable |
| updater 無法識別（token 異常） | 回傳 401 Unauthorized |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T01 | API Test | 正常寫入一筆商家操作日誌 | 200 OK，Cassandra 可查到該筆 log |
| T02 | API Test | 不帶 token 呼叫 | 401 Unauthorized |
| T03 | API Test | 使用不存在的 businessCode | 400 / 404 |
| T04 | API Test | 傳入非法 actionType | 400 Bad Request |
| T05 | Flow Test | 模擬 Cassandra 寫入失敗 | 500，後端 log 記錄錯誤 |
| T06 | Permission Test | 使用無 Business 管理權帳號 | 403 Forbidden |
| T07 | Integration Test | 從其他 API 異動設定後，確認有對應 log 寫入 | log 查詢 API 可查到該筆記錄 |

---

## 9. 高風險區域

- **高風險 table**：`pricecenter.action_logs`（所有審計追蹤的核心，不可遺失）
- **高風險 API**：此 API 為 write-only，若被濫寫可能造成 storage 膨脹（需監控寫入量）
- **跨服務資料同步**：無（本服務直接寫入 pricecenter keyspace）
- **Transaction**：無跨表 transaction，但需注意「業務成功、日誌失敗」導致 audit trail 不完整的風險
- **Cache consistency**：無 cache 依賴
- **Queue retry**：未使用 Queue，若 Cassandra 寫入失敗，預設無 retry 機制（需人工確認是否有內部 retry policy）
- **Idempotency**：此 API 不具備冪等性，重複呼叫會產生多筆 log

---

## 10. 常見錯誤

- ❌ **新人**：直接將整個 request body 透傳寫入 `content`，未注意可能含有密碼或 token → 應在寫入前過濾敏感欄位
- ❌ **新人**：手動傳入 `updater` 欄位 → 應由後端從 token 中取出，不可信任 client 傳入
- ❌ **AI**：誤以為 `action_logs` 在 `gamesettings` keyspace → 正確位置是 `pricecenter.action_logs`
- ❌ **AI**：在「遊戲設定異動」的邏輯中，忘記一併呼叫此日誌流程 → 應確保所有 Config / League / Template / Game 等 Controller 的寫入操作都有對應的 log 寫入
- ❌ **常見漏檢查**：`actionType` 未做白名單驗證，接受任意字串 → 可能導致日誌混亂，查詢困難
- ❌ **常見錯誤流程**：業務寫入用 try-catch，日誌寫入放在 try 外且失敗未處理 → 可能導致 audit trail 遺失

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/v1/businesses/{businessCode}/logs` - README & OpenAPI |
| API 驗證 | ECFramework.ECService 2.0.0 - README 技術棧 |
| DB Table | `pricecenter.action_logs` - README, Cassandra schema |
| Service | `IBusinessService` / `IActionLogService` - 程式碼語意分析 |
| 不可更新欄位 | `updater` 自動填入，不接受 client 傳入 - gamesettings-detail.md |
| 品牌隔離 | 查詢 `business_accounts` 須指定 `businesscode` - gamesettings-detail.md |