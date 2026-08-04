# 停止指定爬蟲頁面

## 1. 場景目的

管理後台觸發「停止」指定提供者（provider）的 Bet365 爬蟲頁面。流程會關閉爬蟲帳號的啟用狀態，使該爬蟲立即停止運作。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/bet365/sendstop/{provider}/{pagename}` | 停止指定 provider 的爬蟲頁面 |

- **需要驗證**：✅（ECFramework 內部統一驗證）
- **參數說明**：
  - `provider`：爬蟲提供者代碼（如 `AU8`、`Fortuna888`、`HGA` 等），對應 Cassandra `pricecenter` keyspace 中的 `accounts_{provider}` 表
  - `pagename`：要停止的爬蟲頁面名稱（即爬蟲帳號）

---

## 3. 流程總覽

1. 接收 GET 請求，通過 ECFramework 驗證
2. Controller 解析 `provider` 與 `pagename` 路由參數
3. Service 層根據 `provider` 決定目標 Cassandra 表（`accounts_{provider}`）
4. 讀取 `pricecenter.accounts_{provider}` 表中 `account = pagename` 的記錄
5. 檢查帳號是否存在
6. 更新 `enabled` 欄位為 `0`（停用）
7. 更新 `closetime` 為當前時間（若有需要關閉帳號）
8. 清除相關 Redis 快取（若有）
9. 回傳操作成功

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Middleware | `ECFramework` | 驗證請求權限 |
| 2 | Controller | `Bet365Controller.SendStop` | 接收請求，呼叫 Service |
| 3 | Service | `Bet365Service` / `ISysManagerProvider` | 根據 provider 選擇目標表，執行停用邏輯 |
| 4 | Provider | `ISysManagerProvider.UpdateAccountStatus` | 更新 Cassandra `accounts_{provider}` 表 |
| 5 | Cache | Redis (SportCache 或自訂) | 若有快取，主動清除 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `pricecenter.accounts_{provider}` | Read | 查詢爬蟲帳號是否存在 |
| DB | Cassandra `pricecenter.accounts_{provider}` | Update | 設定 `enabled = 0` 停用爬蟲 |
| Redis | `price:cache:{provider}:{pagename}` | DELETE | 清除帳號快取（避免讀取到舊狀態） |
| Queue | 無 | 無 | 本流程不涉及 Kafka / Queue |

---

## 6. 重要規則

- **權限限制**：僅管理後台授權使用者可呼叫此 API（需通過 ECFramework 驗證）
- **欄位限制**：
  - 只能更新 `enabled` 為 `0`（停用），不可反向設定為 `1`
  - 若有需要關閉帳號，需同時寫入 `closetime`
  - **不可修改** `account`（主鍵）與 `password`
- **不可暴露資料**：
  - 回傳中不可包含 `password` 欄位
  - 不可回傳 `phone`（除非後台且有授權）
  - 不可回傳 `handler` 原始 map 結構
- **狀態值限制**：
  - `enabled` 僅可設為 `0`，不可從 `0` 回復為 `1`（需人工確認：是否允許重新啟用？建議明文規範）
  - 若 `closetime` 非空，代表帳號已關閉，不可再次操作（應回傳錯誤）
- **Transaction 規則**：Cassandra 單一 Partition 更新為原子操作，不需跨表 transaction
- **Retry 規則**：
  - Cassandra 寫入失敗時可重試（需確保冪等，因 `enabled` 設為 `0` 為固定值）
  - Redis DEL 為 optional，失敗時不影響主流程

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| provider 參數無效（如 `accounts_{provider}` 表不存在） | 回傳 400 Bad Request，錯誤訊息說明 provider 無效 |
| pagename 不存在於對應表中 | 回傳 404 Not Found，提示頁面不存在 |
| 帳號已被停用（`enabled` 已為 `0`） | 回傳 200 OK 或 409 Conflict（需人工確認） |
| 帳號已關閉（`closetime` 非空） | 回傳 409 Conflict，提示帳號已關閉不可操作 |
| Cassandra 寫入失敗 | 回傳 500 Internal Server Error，記錄錯誤日誌 |
| 未通過 ECFramework 驗證 | 回傳 401 Unauthorized |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| T01 | API Test | 正常停止一個啟用中的爬蟲頁面 | `enabled` 更新為 `0`，回傳 200 |
| T02 | Permission Test | 未帶有效 token 呼叫 API | 回傳 401 |
| T03 | Flow Test | 對不存在的 provider 呼叫 | 回傳 400 |
| T04 | Flow Test | 對不存在的 pagename 呼叫 | 回傳 404 |
| T05 | Flow Test | 重複停止同一頁面（`enabled` 已為 `0`） | 回傳適當狀態碼（需人工確認） |
| T06 | Integration Test | Cassandra 寫入後，驗證 Redis 快取是否被清除 | Redis Key 不存在或為更新後的狀態 |
| T07 | API Test | 帳號已關閉（`closetime` 非空）時嘗試停止 | 回傳 409 |

---

## 9. 高風險區域

- **高風險 table**：`pricecenter.accounts_{provider}`（所有品牌表）
  - 誤操作可能導致所有爬蟲停擺
  - 需確保 `provider` 參數嚴格對應存在的表，避免 SQL injection 或 table not found
- **高風險 API**：`GET /api/v1/bet365/sendstop/{provider}/{pagename}`
  - 雖然是 GET，但會觸發寫入操作，不符合 RESTful 語義（建議改為 POST / DELETE）
  - 需確保權限控制嚴格
- **跨服務資料同步**：爬蟲機器可能已經讀取並快取了帳號狀態，停用後需確認爬蟲端有偵測機制
- **Cache consistency**：
  - 更新 DB 後必須主動清除 Redis 快取（`price:cache:{provider}:{pagename}`），否則 `webpservice` 或其他讀取方可能取得舊狀態
  - 快取刪除失敗不應影響主流程，但需記錄警告日誌
- **Idempotency**：
  - 重複呼叫此 API（對已停用帳號）不應導致錯誤，應回傳成功或明確的狀態衝突訊息

---

## 10. 常見錯誤

- ❌ **直接 UPDATE `accounts_{provider}` 的 `enabled` 而不檢查 `closetime`** → ✅ 應先讀取當前狀態，若 `closetime` 非空則拒絕操作
- ❌ **忘記清除 Redis 快取** → ✅ 更新成功後應主動 DEL 快取（如 `price:cache:{provider}:{pagename}`）
- ❌ **沒有驗證 provider 參數是否對應合法的表名** → ✅ 應檢查 provider 是否為已知品牌代碼，避免操作不存在的表
- ❌ **更新 `handler` map 時直接覆蓋** → ✅ 若需更新 handler，應使用 Cassandra map 操作或先讀取後 merge（本場景可能不需更新 handler，需人工確認）
- ❌ **回傳中包含 `password` 或完整 `handler`** → ✅ 所有回傳都應排除敏感欄位
- ❌ **混淆「停用（enabled=0）」與「關閉（closetime 非空）」** → ✅ 本場景為停用爬蟲，不應寫入 `closetime`；關閉帳號是另一個獨立流程
- ❌ **AI 誤解此 API 為一般的 GET 查詢** → ✅ 實際上會觸發寫入操作，需在 AI 訓練或 CODE 生成時特別注意

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `GET /api/v1/bet365/sendstop/{provider}/{pagename}`（README.md 系統監控與 Bet365 爬蟲管理） |
| DB Table | `pricecenter.accounts_{provider}`（db/pricecenter-detail.md） |
| DB Operation | `enabled` 欄位更新為 `0`（db/pricecenter-detail.md enabled 狀態流轉） |
| Cache | `price:cache:{brand}:{account}`（db/pricecenter-detail.md Redis 段落） |
| Provider | `ISysManagerProvider.UpdateAccountStatus`（db/pricecenter-detail.md enabled 欄位操作明細） |
| Auth | `ECFramework.ECService 2.0.0`（README.md 驗證框架） |