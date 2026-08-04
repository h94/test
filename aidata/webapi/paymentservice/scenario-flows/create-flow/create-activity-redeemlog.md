# 建立活動兌換記錄

## 1. 場景目的

會員在活動頁面兌換商品，透過 `POST /api/v1/activity/productredeemlogs` 提交兌換請求。系統檢查商品庫存與資格後，建立一筆 `status=0`（審核中）的兌換記錄，並立即扣減該商品庫存，防止超賣。後續由管理員或排程審核結果，更新記錄狀態為成功（1）或失敗（2）。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/activity/productredeemlogs` | 建立活動商品兌換記錄，需驗證會員身份 |

---

## 3. 流程總覽

1. 接收會員兌換請求，解析 body（含 `site`、`activityEvent`、`account`、`pid` 等）。
2. 身份驗證：透過 ECFramework 驗證 token，取得 `account` 並與 body 中的 account 比對，確保僅本人操作。
3. 查詢 `payment.products_activity` 確認商品存在、`status=1`（販售中）、`quantity > 0`。
4. 檢查會員是否已有該商品的兌換記錄（`payment.products_activity_redeem_logs` 中以 `site`、`activityEvent`、`account`、`pid` 為條件查詢），若存在且狀態非失敗，則拒絕重複兌換（**需人工確認**實際限制規則）。
5. 生成唯一的 `id`（兌換記錄 ID）與 `addtime`（目前時間戳）。
6. 使用 Cassandra **批次寫入**（或逐筆寫入，但需維持一致性）：
   - INSERT `payment.products_activity_redeem_logs`，`status=0`。
   - UPDATE `payment.products_activity` SET `quantity = quantity - 1` WHERE `site=? AND activityevent=? AND id=?` **且** `quantity > 0`（使用條件式更新，避免超賣）。
7. 若庫存扣減成功，則清除相關活動商品快取（Redis key `SportCache:Activity_{site}_{activityEvent}_Products`）。
8. 回傳建立成功的兌換記錄（或僅回傳成功訊息）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `ActivityController.PostProductRedeemLog` | 接收請求，呼叫驗證框架，委派 Service |
| 2 | Service | `ActivityService.CreateRedeemLog` | 組合查詢與寫入邏輯，協調 Provider |
| 3 | Provider | `ActivityDataProvider` | 讀取商品狀態、使用者兌換歷史；寫入兌換記錄與更新庫存 |
| 4 | Cache Provider | `CacheDataProvider` | 寫入後清除活動商品 Redis 快取（`DelAsync`） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.products_activity` | Read | 讀取商品庫存與狀態 |
| DB | `payment.products_activity_redeem_logs` | Write (INSERT) | 建立審核中兌換記錄 |
| DB | `payment.products_activity` | Write (UPDATE, conditional) | 扣減庫存（`quantity = quantity - 1` IF `quantity > 0`） |
| Redis | `SportCache:Activity_{site}_{activityEvent}_Products` | Delete | 失效快取，確保下次查詢拿到最新庫存 |
| Queue | 無 | - | 此場景未使用佇列 |

---

## 6. 重要規則

- **身份驗證**：必須經過 ECFramework 驗證，且請求中的 `account` 必須等於登入帳號。
- **商品狀態**：僅允許兌換 `products_activity.status=1`（啟用）且 `quantity > 0` 的商品。
- **重複兌換限制**：同一會員對同一商品 (`site, activityevent, account, pid`) 應限制只能有一筆有效兌換（成功或審核中），需以實際業務規則為準（**需人工確認**）。
- **庫存扣減原子性**：必須使用 Cassandra 的 **條件式更新（IF quantity > 0）**，避免超賣。若條件失敗，回傳庫存不足。
- **不可修改欄位**：兌換記錄建立後，`site`、`activityevent`、`account`、`id`、`pid`、`addtime` 不可變更；`status` 僅能由後續審核 API（`PUT /api/v1/activity/productredeemlogs/{...}/status`）更新，前端不可直接 PUT。
- **ID 產生**：`id`（兌換記錄 ID）由系統自動產生（UUID），禁止從請求中指定。
- **快取失效**：成功扣減庫存後，**必須**刪除對應活動商品清單的 Redis 快取，確保前台立即看到最新庫存。
- **Transaction 規則**：Cassandra 不支援多表事務，但必須確保 INSERT log 與 UPDATE quantity 在邏輯上視為一體，若 UPDATE 失敗則不應寫入 log（透過條件式更新判斷，失敗時不執行 INSERT 或回滾已寫入 log？**需人工確認**實作方式，可能需業務補償）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 請求未帶有效 token | 回傳 401 Unauthorized |
| body 中 account 與 token 不符 | 回傳 403 Forbidden |
| 商品不存在或已下架（status != 1） | 回傳錯誤，提示「商品不可兌換」 |
| 庫存不足（quantity == 0） | 回傳錯誤，提示「庫存不足」 |
| 會員已兌換過該商品且記錄狀態為成功或審核中 | 回傳錯誤，提示「已兌換」 |
| 並發兌換導致庫存扣減失敗（IF quantity > 0 不成立） | 回傳錯誤，提示「庫存不足」，並確保未寫入無效 log |
| Cassandra 寫入或條件更新時發生逾時 | 回傳 500，需記錄錯誤日誌，前端可提示稍後再試 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| ACT-001 | API Test | 正常兌換流程 | 200，記錄寫入，庫存減1，快取被清除 |
| ACT-002 | Permission Test | 使用他人 account 兌換 | 403，無記錄產生 |
| ACT-003 | Integration Test | 商品庫存為 0 時兌換 | 錯誤回應，庫存仍為 0 |
| ACT-004 | Flow Test | 同一會員對同一商品連續發送兩次請求 | 第一次成功，第二次回「已兌換」或「庫存不足」 |
| ACT-005 | Concurrency Test | 多個會員同時兌換最後一件商品 | 僅一人成功，其他人收到庫存不足，庫存不變為負 |
| ACT-006 | Cache Test | 兌換後立即查詢活動商品列表 | 回傳的商品庫存已減少，不再出現已售完商品 |

---

## 9. 高風險區域

- **Cassandra 條件式更新**：若未正確使用 `IF quantity > 0`，可能導致超賣或庫存變為負數。
- **批次寫入與補償**：INSERT log 與 UPDATE quantity 不是原子性事務，若 UPDATE 成功但 INSERT 失敗，或反之，需要補償機制（如後續排程檢查孤兒記錄或補扣庫存）。**需人工確認**目前實作是否使用 Cassandra Batch 或手動補償。
- **Redis 快取不一致**：若扣減庫存成功但刪除快取失敗，前台可能持續顯示舊庫存，需有重試或 TTL 機制。
- **重複兌換防禦**：依賴業務邏輯而非資料庫唯一約束（Cassandra 可透過複合主鍵防重，但此處主鍵包含 `id`，無法防止同 `pid` 重複寫入），必須在 Service 層精確檢查。

---

## 10. 常見錯誤

- ❌ **忘記檢查商品 status** → 可能讓會員兌換到已下架商品。
- ❌ **未使用條件式更新直接 SET quantity = quantity - 1** → 可能造成庫存負數。
- ❌ **建立兌換記錄後未扣減庫存** → 典型邏輯遺漏，導致超發。
- ❌ **庫存扣減成功後未清除 Redis 快取** → 前台顯示錯誤。
- ❌ **允許前端自行指定 `id` 或 `status`** → 破壞系統控制，可能偽造成功記錄。
- ❌ **未限制同一商品重複兌換** → 可能被惡意連續兌換，造成資源濫用。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI: `POST /api/v1/activity/productredeemlogs` |
| DB: 商品表 | `payment.products_activity` (schema: site, activityevent, id, quantity, status) |
| DB: 兌換記錄表 | `payment.products_activity_redeem_logs` (schema: site, activityevent, account, id, pid, addtime, status) |
| 寫入限制 | paymentservice-detail.md: `products_activity_redeem_logs` 僅由兌換流程寫入 INSERT；status 初始 0，後續不可由前端 UPDATE |
| 庫存扣減 | paymentservice-detail.md: 兌換成功時必須同步 `UPDATE products_activity SET quantity = quantity - 1` |
| Redis 快取 | paymentservice-detail.md: `SportCache:Activity_{site}_{activityEvent}_Products`，活動商品清單快取 |
| 身份驗證 | README: 此 API 需要驗證 ✅ |