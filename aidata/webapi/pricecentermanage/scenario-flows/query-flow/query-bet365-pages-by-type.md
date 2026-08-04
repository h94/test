# 依類型查詢 Bet365 頁面

## 1. 場景目的

管理員或後台系統查詢特定類型（如 `PreMatch`、`InPlay`）的 Bet365 爬蟲頁面設定及其排程狀態。此為連續監控爬蟲健康度的一環，用於儀表板展示或排程管理。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/bet365/pages` | 依類型查詢 Bet365 頁面 |

| 參數 | 類型 | 說明 | 必要 |
|------|------|------|------|
| pagetype | query (string) | 欲查詢的頁面類型 (e.g. PreMatch, InPlay) | 是 |

---

## 3. 流程總覽

1. 接收 GET request 帶有 `pagetype` 查詢參數。
2. 驗證操作員後台權限。
3. 服務層依據 `pagetype` 從價格中心讀取對應頁面配置。
4. 組裝頁面清單與對應排程狀態。
5. 回傳符合類型的頁面集合。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `Bet365Controller.GetPages` | 接收 `pagetype`，呼叫 Service |
| 2 | Service | `IBet365Service.GetPagesByType` | 基於類型查詢 DB |
| 3 | Provider | `ISysManagerProvider` (推測) | 從 Cassandra `pricecenter` keyspace 讀取頁面設定 |
| 4 | Transfer | `Bet365PageDTO` | 組裝回傳物件，排除敏感金鑰 |

**需人工確認**：具體 Provider 名稱與 Cassandra 查詢細節未在目前 Code 摘要中揭露。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `pricecenter.accounts_{source}` | Read | 讀取爬蟲帳號啟用狀態與頁面綁定關係 |
| DB | `pricecenter.machines` | Read | 驗證爬蟲機器在線狀態 |
| Redis | `Bet365Pages:{pagetype}` | Read | 快取指定類型的頁面列表以加速查詢 (推測) |

**需人工確認**：Redis 快取鍵的實際命名、TTL 及更新策略。

---

## 6. 重要規則

- **權限限制**：`需要驗證`（後台管理權限），由 `ECFramework.ECService` 攔截。
- **欄位限制**：回傳頁面名稱、類型、排程設定與機器狀態。**不可回傳** `accounts_{source}.password`、`phone` 等敏感欄位。
- **不可暴露資料**：爬蟲帳號的明文密碼（即使為雜湊值）不可回傳。
- **狀態值限制**：僅應查詢並回傳 `enabled = 1` 且 `closetime` 為空的頁面相關帳號。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 缺少 `pagetype` 參數 | 400 Bad Request |
| 操作員未通過後台驗證 | 401 Unauthorized 或 403 Forbidden |
| Cassandra 查詢超時或失敗 | 500 Internal Server Error 或返回空列表 |
| Redis 快取查不到且 DB 無資料 | 回傳空集合 `[]` |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| BET365-01 | API Test | 輸入合法 `pagetype=PreMatch` | 200 OK，回傳 PreMatch 頁面清單 |
| BET365-02 | API Test | 不傳 `pagetype` 參數 | 400 Bad Request |
| BET365-03 | Permission Test | 無後台 token 呼叫 | 401 Unauthorized |
| BET365-04 | Flow Test | Cassandra 無資料時呼叫 | 回傳空陣列 `[]` |
| BET365-05 | Flow Test | 頁面綁定的帳號為 `enabled=0` | 該頁面應被排除或標記為離線 |

---

## 9. 高風險區域

- **高風險 API**：無寫入操作，風險較低。
- **Cache consistency**：若此處有 Redis 快取，後續「更新頁面設定」或「停止頁面」操作時**必須**立刻失效對應的 `pagetype` 快取，否則儀表板將顯示過期狀態。
- **跨服務資料同步**：爬蟲機器的線上狀態由心跳監控維護，本查詢需確保能取得最新的機器狀態。

---

## 10. 常見錯誤

- ❌ **查詢時未過濾已停用帳號** → ✅ 必須加上 `enabled=1` 條件，避免顯示已停用的爬蟲頁面。
- ❌ **回傳了 `password` 欄位** → ✅ DTO 應明確排除所有敏感欄位。
- ❌ **Redis 快取未清除導致後台顯示舊狀態** → ✅ 任何排程變更 API 都需主動 DEL 相關頁面快取。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `GET /api/v1/bet365/pages` (README.md) |
| DB | `pricecenter.accounts_AU8` (pricecenter-detail.md / OpenAPI) |
| 權限 | `需要驗證` (README.md: `系統監控與 Bet365 爬蟲管理`) |
| Rules | `pricecenter-detail.md: 讀取規則、不可回傳欄位` |
| Code | `Bet365Controller`（Phase 0/1 code summary） |