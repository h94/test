# 更新商家帳號狀態

## 1. 場景目的

管理員停用或啟用商家帳號，更新 `gamesettings.business_accounts` 表的 `status` 欄位。此操作由 `gamesettingsite` 服務執行，允許管理員凍結 (status=0) 或啟用 (status=1) 指定商家的帳號。

---

## 2. 入口 API

需人工確認：目前提供的 OpenAPI 文件僅包含 AINews 相關端點，未涵蓋此場景的 API 定義。根據 DB 操作邊界推測可能存在的 API：

| Method | Path | 說明 |
|---|---|---|
| PUT/PATCH | `/api/business/account/status` | 更新商家帳號狀態 |

需人工確認：實際 API 路徑、HTTP 方法、Request/Response 結構

---

## 3. 流程總覽

需人工確認：以下流程根據 DB 操作邊界推測，實際實作可能不同

1. 管理員透過 API 發送更新 status 請求
2. 驗證操作者身份與權限 (role 必須為 admin)
3. 以 `businesscode` + `account` 查詢 `gamesettings.business_accounts`
4. 驗證目標帳號存在且當前 status 允許變更
5. 更新 status 欄位 (1→0 停用 / 0→1 啟用)
6. 自動設定 updatetime 為當前時間戳
7. 回傳操作結果

---

## 4. 程式流程

需人工確認：以下流程基於 DB 分析，實際程式碼因未提供 code evidence 而無法確認

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | 需人工確認 | 接收 status 更新請求 |
| 2 | Validator | 需人工確認 | 驗證請求參數與權限 |
| 3 | Service | 需人工確認 | 執行業務邏輯：查詢現有記錄、驗證狀態轉換規則 |
| 4 | Provider | 需人工確認 | 寫入 `gamesettings.business_accounts` 表 |
| 5 | Transfer | 需人工確認 | 組裝回傳結果，排除敏感欄位 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | gamesettings.business_accounts | Read | 查詢現有帳號資訊（以 businesscode + account 為完整主鍵） |
| DB | gamesettings.business_accounts | Update | 更新 status 欄位與 updatetime |

需人工確認：是否有 Redis/Kafka 等快取或訊息佇列操作。根據 gamesettingsite 的 DB 操作邊界，此服務目前未使用 Redis。

---

## 6. 重要規則

### 權限限制
- 此操作僅限 role=admin 的管理員執行
- `business_accounts.status=0` 的帳號無法登入，前台必須過濾 `status=1` 的記錄

### 欄位限制
- `businesscode` + `account` 為主鍵，不可修改
- 更新時不可修改 `password`、`role`（除非是角色管理 API）
- `updatetime` 必須由服務端自動填入當前時間戳，不可由請求端指定
- `updater` 應由服務端自動填入當前操作者帳號

### 不可暴露資料
- `password` 欄位不可回傳（任何情況）
- `businesses.authtoken` 不可回傳

### 狀態值限制
- status 狀態轉換：1 (啟用) → 0 (凍結) 或 0 → 1
- 不可直接將 status 設定為未定義的值

### 不可修改欄位
- `businesscode`、`account`（主鍵）
- `password`（需獨立 API 處理）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 操作者 role 非 admin | 回傳 403 Forbidden 或權限不足錯誤 |
| 目標 `businesscode` + `account` 不存在 | 回傳 404 Not Found |
| 請求的 status 值無效（非 0 或 1） | 回傳 400 Bad Request 或驗證錯誤 |
| 嘗試設定與當前相同的 status | 可選擇性回傳成功或提示無需更新 |
| DB 寫入失敗 / Cassandra timeout | 回傳 500 Internal Server Error，記錄錯誤日誌 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-001 | API Test | admin 將 status=1 更新為 status=0 | 更新成功，回傳 200 |
| UT-002 | API Test | admin 將 status=0 更新為 status=1 | 更新成功，回傳 200 |
| UT-003 | Permission Test | 非 admin 角色嘗試更新 status | 回傳 403 或權限錯誤 |
| UT-004 | Validation Test | status=99 無效值 | 回傳 400 驗證錯誤 |
| UT-005 | API Test | 目標帳號不存在 | 回傳 404 |
| UT-006 | Flow Test | 停用後嘗試登入 | 登入失敗，因為 status=0 |
| UT-007 | Flow Test | 啟用後嘗試登入 | 登入成功，因為 status=1 |

---

## 9. 高風險區域

### 高風險 table
- **gamesettings.business_accounts**：直接影響商家帳號的可用性，誤設為 status=0 可能導致商家立即無法使用服務

### 高風險 API
- 此 API 直接影響商家業務運作，需嚴格權限控管與操作日誌記錄

### 需特別注意
- **權限控管**：確保只有授權管理員可以變更狀態
- **審計日誌**：操作應記錄到 logs 或 logs_business 表，包含操作者、時間、變更前後狀態
- **連帶影響**：status=0 的帳號登入時會被拒絕，需確認業務上無其他依賴該帳號的服務

---

## 10. 常見錯誤

### 新人容易犯錯
- 忘記驗證操作者權限（role 必須為 admin）
- 未使用完整主鍵查詢（只使用 account 而忽略 businesscode，觸發 Cassandra 全表掃描）
- 回傳 `password` 欄位（嚴重違規）
- 未自動填入 `updatetime`

### AI 容易誤解
- 誤以為可以任意變更 status 值（只能設定 0 或 1）
- 誤以為可以同時更新其他欄位（如 password、role）
- 忽略 Cassandra 寫入限制（主鍵不可變更）

### 常見漏檢查項目
- 目標帳號是否存在
- 操作者是否有權限
- 是否需要記錄操作日誌
- status 變更後的連帶影響（如已登入的 session 是否需要失效）

### 常見錯誤流程
- 直接執行 UPDATE 而未先 SELECT 確認記錄存在
- 未使用 `businesscode` + `account` 完整主鍵條件
- 將 `password` 欄位包含在回傳結果中

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB Schema | gamesettings.business_accounts (status int, updatetime bigint) |
| DB 操作邊界 | gamesettings-detail.md: business_accounts status 由 gamesettingservice/gamesettingsite 維護 |
| 寫入限制 | gamesettings-detail.md: updater 由服務端自動填入，不可由請求端指定 |
| 不可回傳欄位 | gamesettings-detail.md: password 任何 GET 路由不可回傳 |
| 讀取規則 | gamesettings-detail.md: 查詢 business_accounts 必須以 businesscode + account 為完整條件 |
| 跨服務限制 | gamesettings-detail.md: status=0 (凍結) 只能由 UpdateBusinessAccountStatus API 設定 |

需人工確認：
- 具體的 Controller、Service、Provider 類別名稱與方法
- API 路徑與 HTTP 方法
- 是否有 Redis/Kafka/Queue 操作
- 操作日誌記錄機制（logs 表或 logs_business 表）