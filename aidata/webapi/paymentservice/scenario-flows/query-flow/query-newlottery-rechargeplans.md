# 查詢新彩票儲值方案

## 1. 場景目的

讓前台會員在儲值頁面，查詢目前系統中所有已啟用（enabled=1）且未過期的新彩票儲值方案，以便進行下一步儲值操作。此為 README 使用場景 4「新彩票會員儲值」的前置步驟。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/newlottery/rechargeplans` | 查詢所有有效的新彩票儲值方案 |

需驗證：是（依 README 標記 ✅）

---

## 3. 流程總覽

1. 前台會員送出 GET 請求至 `/api/v1/newlottery/rechargeplans`
2. ECFramework.ECService 執行身份驗證與權限檢查
3. Controller 轉交 Service 層處理業務邏輯
4. Service 查詢 `payment.rechargeplans_newlottery` 資料表
5. 過濾條件：`enabled = 1` 且 `starttime <= 當前時間戳 <= endtime`
6. 回傳符合條件的方案列表（包含 id、amount、coin、currency 等欄位）
7. 內部排除管理用途欄位（如 `lastupdatetime`）回傳給前端

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Middleware | ECFramework.ECService | 驗證 JWT token，確認請求者身份 |
| 2 | Controller | NewLotteryController.GetRechargePlans | 接收 GET 請求，無參數 |
| 3 | Service | NewLotteryRechargePlanService | 呼叫 DataProvider 執行查詢 |
| 4 | DataProvider | NewLotteryRechargePlanDataProvider | 執行 CQL SELECT，過濾 enabled=1 且在有效期內 |
| 5 | Transfer | - | 將資料轉換為 DTO，排除內部欄位後回傳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.rechargeplans_newlottery` | Read | 查詢所有啟用且在有效期內的方案 |
| Redis | `rechargeplans:all:{site}` | Read (可選) | 若存在快取則直接回傳；miss 時查 DB 並更新快取 |

> **備註**：根據 `db/payment-detail.md`，Redis 快取由 `newlotterysite` 負責 SET/GET/DEL；`paymentservice` 可能直接查 DB 或調用快取，需進一步確認 `paymentservice` 內部實作。

---

## 6. 重要規則

- **權限限制**：此 API 需要登入驗證，僅前台會員可使用；管理後台查詢方案請走後台專用 API
- **過濾條件**：嚴格過濾 `enabled = 1` 且 `starttime <= now <= endtime`；任何一項不符者不可回傳
- **欄位限制**：
  - `id` 不可修改，由後台建立時寫入
  - `lastupdatetime` 僅內部使用，不可回傳前端
- **禁止修改欄位**：`amount`、`coin`、`currency`、`enabled`、`starttime`、`endtime` 僅由方案管理後台設定；查詢端無寫入權限
- **快取規則**：
  - 若有快取，TTL 約 5 分鐘或由 `lastupdatetime` 計算
  - 方案變更時（後台新增／修改／刪除）必須主動 DEL 快取
  - 快取 miss 時須從 DB 重新載入
- **不可回傳欄位**：本場景無特殊不可回傳欄位，但內部使用之 `lastupdatetime` 不應暴露

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未帶 token 或 token 過期 | 回傳 401 Unauthorized |
| 無任何符合條件的方案（全部停用或過期） | 回傳空陣列 `[]`，HTTP 200 |
| Cassandra 查詢逾時 | 回傳 503 Service Unavailable 或 500 Internal Server Error |
| Redis 連線失敗（若有快取） | 降級直接查詢 DB 並回傳結果 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| NL-RP-01 | API Test | 正常查詢，存在啟用方案 | 回傳 200，列表僅包含 enabled=1 且在有效期內之方案 |
| NL-RP-02 | API Test | 所有方案皆過期或停用 | 回傳 200，空陣列 `[]` |
| NL-RP-03 | Permission Test | 未帶 token 請求 | 回傳 401 |
| NL-RP-04 | Flow Test | 快取尚未建立，首次查詢 | 成功讀取 DB 並建立快取（若有） |
| NL-RP-05 | Flow Test | 方案在有效期結束日當天查詢 | 若 `endtime` 為該日 `23:59:59`，仍應回傳；需驗證時間邊界邏輯 |
| NL-RP-06 | Integration Test | Cassandra 回應延遲 | 依 timeout 設定回傳錯誤或重試後成功 |

---

## 9. 高風險區域

- **快取一致性**：方案變更時若未正確清理 Redis 快取（`DEL rechargeplans:all:{site}`），前台將顯示過期或已停用方案
- **時間邊界檢查**：`starttime`、`endtime` 為 bigint（Unix timestamp），前端查詢的「當前時間」必須使用伺服器時間，不可依賴客戶端時間
- **Cassandra 全表掃描**：`rechargeplans_newlottery` 主鍵為 `id`，無明顯分區鍵可優化 `SELECT` 全表；若方案數量過大可能影響效能，建議評估是否需要加入站點分區或快取機制

---

## 10. 常見錯誤

- ❌ 前端或後端忘記過濾 `enabled=1`，導致停用方案仍顯示在頁面
- ❌ 只檢查 `enabled` 而忽略 `starttime`、`endtime`，導致未開始或已過期方案仍可被選擇
- ❌ 時間判斷使用客戶端時間，而非伺服器時間
- ❌ 方案更新後未清除 Redis 快取，前台持續顯示舊資料
- ❌ 回傳了內部管理欄位 `lastupdatetime`，揭露不必要的系統資訊
- ❌ 對外 API 回傳完整 `names` map（若有），應依請求 Accept-Language 僅回傳對應值

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README · 新彩票金流 · GET `/api/v1/newlottery/rechargeplans` |
| DB Schema | `db/payment.md` · `rechargeplans_newlottery` |
| DB 讀取規則 | `db/payment-detail.md` · 儲值方案：僅過濾 `enabled=1` 且 `starttime <= now <= endtime` |
| DB 寫入限制 | `db/payment-detail.md` · `rechargeplans_newlottery`：`amount`、`coin`、`currency`、`enabled`、`starttime`、`endtime` 僅由方案管理後台設定 |
| 快取規則 | `db/payment-detail.md` · Redis - RechargePlansCache：key 為 `rechargeplans:all:{site}`，TTL 5 分鐘，方案變更時主動 DEL |
| 常見錯誤 | `db/payment-detail.md` · 常見錯誤：`未檢查 enabled 與時間範圍` |
| 場景用途 | `README.md` · 常見使用場景 4「新彩票會員儲值」：GET 方案為第一步 |