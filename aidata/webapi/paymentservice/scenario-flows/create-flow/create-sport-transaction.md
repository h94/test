# 建立體育交易訂單

## 1. 場景目的
會員選定訂閱方案後，透過 API 建立一筆體育交易訂單。系統驗證會員身份、訂閱方案有效性，並將訂單寫入 `payment.sport_transactions`，初始狀態設為待付款，為後續金流流程做準備。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/sport/transactions` | 建立體育交易訂單，需驗證 |

---

## 3. 流程總覽

1. 接收 POST 請求，包含方案 ID、支付方式、金額等資訊
2. 驗證請求格式與必填欄位
3. 查詢 `member.gameusers` 驗證會員身份（`status=正常`）
4. 排除機器人帳號（`gamerobots.enabled=1`）
5. 查詢 `payment.sport_sub_plans` 驗證方案有效性（需人工確認：此表結構未在 schema 中提供）
6. 比對請求金額與方案定價
7. 產生訂單 ID 與 `date_time`
8. 寫入 `payment.sport_transactions`（`status` 設為待付款）
9. 回傳訂單資訊（訂單 ID、狀態）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | SportTransactionController.Post | 接收請求，呼叫 Service |
| 2 | Service | SportTransactionService.CreateTransaction | 協調驗證與資料寫入 |
| 3 | Provider | MemberDataProvider | 查詢 `member.gameusers` 驗證會員狀態 |
| 4 | Provider | MemberDataProvider | 查詢 `member.gamerobots` 排除機器人 |
| 5 | Provider | SportSubPlanDataProvider | 查詢 `payment.sport_sub_plans` 驗證方案 |
| 6 | Validator | SportTransactionValidator | 驗證金額一致性、方案有效性 |
| 7 | Provider | SportTransactionDataProvider | INSERT `payment.sport_transactions` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `member.gameusers` | Read | 驗證會員身份（`status=正常`） |
| DB | `member.gamerobots` | Read | 排除機器人帳號（`enabled=1` 排除） |
| DB | `payment.sport_sub_plans` | Read | 驗證訂閱方案有效性與價格（需人工確認表結構） |
| DB | `payment.sport_transactions` | Write | 寫入訂單記錄 |
| Redis | `SportCache:SportSubPlans` | Read | 查詢訂閱方案快取（若存在） |
| Queue | mq | Publish | 後續可能觸發付款通知（非本場景直接操作） |

---

## 6. 重要規則

- **會員狀態限制**：`member.gameusers.status` 必須為正常（值 = 1）才可建立訂單
- **機器人排除**：`member.gamerobots.enabled=1` 的帳號不可建立訂單
- **金額驗證**：請求金額必須與 `payment.sport_sub_plans.price` 一致
- **方案有效性**：訂閱方案必須為啟用狀態（`enabled=1`）
- **訂單狀態初始值**：`payment.sport_transactions.status` 初始為待付款（值 = 0，需人工確認確切值）
- **不可修改欄位**：`payment.sport_transactions.year`、`account`、`id` 寫入後不可變更
- **帳號關聯**：使用 `authkey` 關聯 `gameusers`，不可直接使用 `account`（跨站台可能重複）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 會員 `status` 非正常（凍結/停用） | 拒絕建立，回傳權限錯誤 |
| 帳號為機器人（`gamerobots.enabled=1`） | 拒絕建立，回傳權限錯誤 |
| 方案不存在或已停用 | 拒絕建立，回傳方案無效錯誤 |
| 請求金額與方案定價不符 | 拒絕建立，回傳金額驗證錯誤 |
| DB 寫入失敗（Cassandra timeout） | 回傳系統錯誤，訂單未建立 |
| `authkey` 無效或不存在 | 拒絕建立，回傳驗證錯誤 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | Flow Test | 正常會員建立訂單 | 成功寫入 DB，回傳訂單 ID |
| TC02 | Permission Test | 停用會員建立訂單 | 拒絕，回傳權限錯誤 |
| TC03 | Permission Test | 機器人帳號建立訂單 | 拒絕，回傳權限錯誤 |
| TC04 | Validation Test | 金額不符方案定價 | 拒絕，回傳金額錯誤 |
| TC05 | Validation Test | 使用不存在的方案 ID | 拒絕，回傳方案無效 |
| TC06 | API Test | DB 寫入失敗模擬 | 回傳系統錯誤，訂單未建立 |

---

## 9. 高風險區域

- **高風險 Table**：`payment.sport_transactions`（金融交易核心表，狀態流轉需嚴格控制）
- **高風險 API**：`POST /api/v1/sport/transactions`（金額寫入不可逆，需防重複提交）
- **Cache consistency**：若方案資訊從 Redis 快取讀取，需確保方案異動時主動失效快取（`SportCache:SportSubPlans`）
- **Transaction**：需確認 Cassandra 寫入為原子操作，訂單 ID 需具唯一性
- **Idempotency**：需確認是否有防重複提交機制（如 client-side idempotency key），避免重複建立訂單

---

## 10. 常見錯誤

- ❌ **直接使用 `account` 建立訂單** → ✅ 必須使用 `authkey`，避免跨站台帳號衝突
- ❌ **未檢查 `gameusers.status` 直接寫入訂單** → ✅ 必須確認會員狀態正常
- ❌ **未排除機器人帳號** → ✅ 需查詢 `gamerobots` 排除測試帳號
- ❌ **訂單金額未與方案驗證** → ✅ 必須比對 `sport_sub_plans.price`，避免前端篡改
- ❌ **快取方案資訊後未處理失效** → ✅ 方案異動時必須更新 Redis 快取
- ❌ **訂單 `status` 初始值設錯** → ✅ 初始必須為待付款，不可直接設為成功
- ❌ **重複提交相同訂單** → ✅ 需有主鍵或唯一約束防止重複（需人工確認實作）
- ❌ **忽略 `authkey` 無效的錯誤處理** → ✅ 必須明確回傳驗證失敗錯誤

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/sport/transactions`（README - 體育交易訂單） |
| DB | `payment.sport_transactions`（README - 資料庫重要 Table） |
| DB | `member.gameusers`（member-detail.md - 用戶身份驗證） |
| DB | `member.gamerobots`（member-detail.md - 機器人帳號排除） |
| Code | `SportTransactionService.CreateTransaction`（需人工確認實際類別名稱） |
| Code | `MemberDataProvider`（需人工確認實際類別名稱） |
| Redis | `SportCache:SportSubPlans`（paymentservice-detail.md - Redis 章節） |
| Rule | `gameusers.status=正常` 才可執行支付操作（paymentservice-detail.md - 讀取規則） |
| Rule | `authkey` 關聯支付訂單與會員帳號（paymentservice-detail.md - 訂閱資格驗證） |