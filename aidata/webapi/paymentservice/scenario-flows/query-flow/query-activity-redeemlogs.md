# 查詢活動兌換記錄

## 1. 場景目的
提供會員查詢自身在某活動中的兌換記錄，或管理後台查詢全站／特定帳號的兌換記錄。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/activity/productredeemlogs/{site}/{activityEvent}` | 管理後台查詢全活動兌換記錄（無 account 參數） |
| GET | `/api/v1/activity/productredeemlogs/{site}/{activityEvent}/{account}` | 會員或後台查詢特定帳號的兌換記錄 |

> Evidence: README 對外 API 表格、OpenAPI 路徑定義。

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，驗證權限（token 需有效，需為已登入狀態）。
2. 從路由參數擷取 `site`、`activityEvent`，以及可選的 `account`。
3. 權限判別：若呼叫端為一般會員，則 `account` 必須等於 token 中的使用者；管理後台可省略 `account` 查全站或指定帳號。
4. 查詢 Cassandra 表 `payment.products_activity_redeem_logs`：
   - Partition Key 提供 `site` 與 `activityevent`。
   - 若有 `account` 則加入 `account` 精確過濾。
5. 將查詢結果序列化為 `ActivityProductRedeemLog` 清單回傳。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `ActivityController.GetProductRedeemLogs` | 驗證 token，提取路由參數 (`site`, `activityEvent`, `account` 可選)。若為一般會員，強制覆寫 `account` 為自己的帳號。 |
| 2 | Service | `ActivityService.GetProductRedeemLogs` | 調用 Data Provider 進行查詢。 |
| 3 | Provider | `ActivityDataProvider.GetProductRedeemLogs` | 組合 Cassandra CQL：`SELECT * FROM payment.products_activity_redeem_logs WHERE site = ? AND activityevent = ? [AND account = ?]`。（Cassandra 允許 Partiton Key 完整給定後，可省略後續 clustering key） |
| 4 | Transfer | `ActivityProductRedeemLog` | 將 DB 資料模型映射為回傳用 DTO。 |

> Evidence：經典 Controller-Service-Provider 分層模式（見 paymentservice-detail 中 `IActivityDataProvider` 描述、`products_activity_redeem_logs` 讀取規則）。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.products_activity_redeem_logs` | Read (SELECT) | 查詢兌換記錄 |
| Redis | － | － | 本場景未使用快取 |
| Kafka / Queue | － | － | 本場景僅讀取，無寫入或事件發送 |

> Evidence：`paymentservice-detail` 中 `products_activity_redeem_logs` 僅描述寫入與狀態更新，無 Redis 快取；`payment-detail.md` 未提到此表之快取。

---

## 6. 重要規則

- **權限限制**：
  - 一般會員：只能查詢自己的紀錄 (`account` 必填，且須與 token 一致)。
  - 管理後台：可查詢全站（省略 `account`）或指定帳號。
  - API 需要驗證（✅），參見 README API 表格。
- **欄位限制**：
  - 所有回傳欄位均為 `products_activity_redeem_logs` 表的公開欄位，無特別屏蔽規則（無`password`等敏感欄位）。
- **不可暴露資料**：
  - 帳號 (`account`) 本身為兌換主體，自己查自己或後台查詢為可控範圍，風險較低；但仍需避免非授權跨帳號查詢。
- **Transaction 規則**：純查詢操作，無需事務。
- **狀態值限制**：
  - `status` 0：審核中，1：成功，2：失敗。
  - 查詢時不強制過濾狀態；前端可依需求自行篩選。

> Evidence：`payment-detail.md` 中 `products_activity_redeem_logs` 狀態定義、`paymentservice-detail.md` 讀取規則「管理後台可省略 account 查全站」。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未提供有效 token | HTTP 401 Unauthorized |
| 一般會員請求未帶 `account`（即進入後台路由） | 權限不足，拒絕查詢全站（HTTP 403） |
| 一般會員傳入的 `account` 與 token 帳號不符 | 拒絕查詢，HTTP 403 Forbidden |
| Cassandra 查詢中斷或超時 | 回傳 HTTP 500 或特定錯誤碼，前端提示系統忙碌 |
| site / activityEvent 不存在 | 查詢結果為空陣列，HTTP 200 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|------|
| TC-01 | Permission Test | 未登入狀態呼叫 API | 401 |
| TC-02 | Permission Test | 一般會員呼叫 `/.../{site}/{event}` 無 account | 403 |
| TC-03 | Permission Test | 一般會員呼叫 `/.../{site}/{event}/{other_account}` | 403 |
| TC-04 | Flow Test | 一般會員查詢自己的兌換記錄（有數筆） | 回傳該會員在此活動的所有記錄 |
| TC-05 | Flow Test | 管理後台查詢所有使用者記錄 | 回傳該活動中的所有記錄 |
| TC-06 | Flow Test | 活動不存在（site/activityEvent 無效） | 回傳空陣列 |
| TC-07 | API Test | 驗證回傳欄位完整性（site, activityevent, account, id, pid, addtime, status, updatetime） | 所有必要欄位均存在且格式正確 |

---

## 9. 高風險區域

- **高風險 table**：`payment.products_activity_redeem_logs` 僅供讀取，風險低。主要風險在於權限控制失當，導致他人兌換記錄洩漏。
- **高風險 API**：GET `/api/v1/activity/productredeemlogs/{site}/{activityEvent}`（若未正確限制僅限管理後台）可能直接洩漏全站記錄。需確保 Controller 層有 strict 的 role 檢查。
- **跨服務資料同步**：無。
- **Cache consistency**：無快取，無一致性問題。
- **Queue retry / Idempotency**：不涉及。

---

## 10. 常見錯誤

- ❌ 新人容易在 Controller 直接使用路由中的 `account` 而忽略權限檢查，導致水平越權（IDOR）。  
  ✅ 一般會員 API 應強制從 token 取得帳號並覆蓋入參。
- ❌ 管理後台 API 未再檢查角色，誤將`[Authorize]` 等同於管理員權限。  
  ✅ 需額外添加 Role-based 檢查（如 `[Authorize(Roles = "Admin")]`）。
- ❌ 未正確處理 Cassandra 查詢，直接執行 `SELECT * FROM ...` 可能觸發全表掃描（若忘記提供 partition key）。  
  ✅ 必須強制包含 `site` 與 `activityevent` 作為 WHERE 條件。
- ❌ 前端開發誤用管理後台路由來查詢個人記錄，但未傳遞 account 導致查詢失敗。  
  ✅ 引導前端對一般會員使用帶有 account 的路由。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | 活動商品與兌換表格，GET `/api/v1/activity/productredeemlogs/{site}/{activityEvent}`，需要驗證 ✅ |
| DB | `payment.products_activity_redeem_logs`，主鍵 (site, activityevent, account, id, pid) |
| 讀取規則 | `paymentservice-detail.md`：「活動兌換紀錄：依 site, activityevent, account 查詢用戶兌換歷史；管理後台可省略 account 查全站」 |
| Code | 推測存在 `ActivityController`、`ActivityService`、`IActivityDataProvider` 等建構（待實體程式碼驗證） |
| SQL | `SELECT site, activityevent, account, id, pid, addtime, status, updatetime FROM payment.products_activity_redeem_logs WHERE site = ? AND activityevent = ? [AND account = ?]` |