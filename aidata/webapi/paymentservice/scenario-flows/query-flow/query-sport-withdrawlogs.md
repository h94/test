# 查詢體育提現記錄

## 1. 場景目的
提供後台管理員或會員查詢體育提現記錄，用於審核、對帳或會員查看自己的提現歷史。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/sport/withdrawlogs` | 查詢提現記錄（日期範圍），需驗證 |
| GET | `/api/v1/sport/withdrawlogs/{account}` | 查詢特定帳號提現記錄，需驗證 |

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，由驗證框架確認用戶身份。
2. 根據路由決定查詢模式：
   - 若路徑不帶 `{account}`（後台），解析 query parameters 中的日期範圍（如 `startDate`、`endDate`），可能支援可選的 `account` 過濾。
   - 若路徑帶 `{account}`（後台或會員），以該帳號為主要條件，可選附加日期範圍。
3. 權限檢查：
   - 普通會員：只能查詢自己的記錄，即 `{account}` 必須等於當前登入帳號，或在不帶 account 的端點自動代入自身。
   - 管理員：可查詢任意帳號，但需具備財務或管理角色。
4. Service 層調用 Provider，構建 Cassandra 查詢。
5. 查詢 `payment.sport_withdraw_logs`（實際表名待確認，常見變體為 `sport_withdraw_logs`）。
   - 假設主鍵為 `(account, date_time)`，則查詢必須包含 `account` 條件以利用分區鍵。
   - 若管理端日期範圍查詢不帶 `account`，可能導致全表掃描（高風險）。
6. 將結果映射為 DTO，回傳 JSON 列表（空陣列若無資料）。
7. 記錄操作日誌（可選，由框架或業務決定）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | SportWithdrawController.GetByDateRange / GetByAccount | 接收請求，調用驗證，傳遞參數至 Service |
| 2 | Service | IWithdrawService.QueryAsync(account, startDate, endDate) | 檢查會員權限，調用 Provider |
| 3 | Provider | ISportWithdrawLogProvider.QueryAsync(conditions) | 組建 CQL，執行 SELECT |

> 確切類別與方法名稱需人工核對原始碼。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.sport_withdraw_logs` | Read | 查詢提現記錄 |
| Cache | – | – | 未使用 |
| Queue | – | – | 未使用 |

---

## 6. 重要規則

- **權限限制**：會員僅能查詢自身帳號；管理員需特定角色（如 finance_admin）。
- **查詢限制**：必須提供有效的日期範圍，建議限制最大跨度（如 90 天）；Cassandra 查詢強烈建議包含 `account` 分區鍵。
- **不可暴露欄位**：回傳時應過濾掉內部審核備註、銀行敏感資訊（視業務需求）；會員端絕不可看到其他用戶記錄。
- **狀態值**：`status` 欄位可選過濾，常見值 `0` 待審核、`1` 成功、`2` 失敗。
- **Retry**：讀取操作失敗可重試，需搭配熔斷機制。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未登入或 token 無效 | 401 Unauthorized |
| 會員查詢他人帳號 | 403 Forbidden |
| 日期參數格式錯誤 | 400 Bad Request |
| DB 查詢超時 | 500 Internal Server Error，記錄日誌 |
| `account` 不存在或無符合記錄 | 200 OK，空陣列 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | Permission | 管理員查詢任意帳號記錄 | 成功取得資料 |
| T2 | Permission | 普通會員查詢自己記錄 | 成功取得自身記錄 |
| T3 | Permission | 普通會員查詢他人帳號 | 403 Forbidden |
| T4 | API | 提供有效日期範圍，有記錄 | 返回符合條件的列表 |
| T5 | API | 日期範圍內無記錄 | 返回空陣列 |
| T6 | API | 缺失必填參數 | 400 Bad Request |
| T7 | Integration | Cassandra 查詢失敗 | 500，記錄錯誤 |

---

## 9. 高風險區域

- **全表掃描**：若後台日期範圍查詢未使用 `account` 條件，將導致 Cassandra 全表掃描，可能造成效能瓶頸或超時。（證據：Cassandra 查詢最佳實踐，需以 partition key 為條件）
- **權限繞過**：若會員端未強制比對 `{account}` 與 token 持有者，可能洩漏其他用戶記錄。
- **敏感資料外洩**：回應未過濾內部狀態或流水號，尤其管理端容易疏忽。
- **日期跨度過大**：未限制查詢時間範圍可能導致查詢緩慢或記憶體壓力。

---

## 10. 常見錯誤

- ❌ 忘記驗證會員身份，導致任意帳號查詢。
- ❌ Cassandra 查詢未帶 `account` 分區鍵，引發全叢集搜尋。
- ❌ 回傳未經脫敏的銀行帳號、完整備註欄位。
- ❌ 忽略分頁，一次性回傳過多記錄。
- ❌ 將 `status` 數值直接暴露給前端而未提供語意映射。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由定義 | README.md – 對外 API 重點表格 |
| 驗證需求 | README.md – 體育提現 GET 路由標記 ✅ |
| 資料表及欄位概覽 | README.md – 資料庫重要 Table：`sport_withdraw_logs`，欄位 `account, date_time, amount, status` |
| 提現狀態規則 | paymentservice-detail.md – 常見錯誤提示：初始 `status=0`（待審核） |
| 查詢模式風險 | Cassandra 資料模型推斷；需人工確認主鍵定義與索引策略 |
| 權限模型 | 平台一般慣例；需人工確認會員端與後台路由的實際權限檢查邏輯 |

> **需人工確認**：
> - `payment.sport_withdraw_logs` 完整 schema 及主鍵設計
> - 兩個 GET 路由具體 query 參數（如 `startDate`, `endDate`、`status`、分頁）
> - 會員端 API 是否強制 `{account}` 等於 token 持有者
> - 後台權限角色（如 finance_admin）及其對應路由
> - 是否使用了任何快取層（目前未發現）