# 活動商品兌換

## 1. 場景目的

處理使用者對「活動商品」的兌換請求：檢查商品狀態與庫存，透過 Cassandra LWT 原子扣減庫存，並產生一筆待審核的兌換記錄。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/activity/productredeemlogs/{site}/{activityEvent}/{authKey}` | 提交兌換請求 |

---

## 3. 流程總覽

1. 接收兌換請求，解析路徑參數 `site`, `activityEvent`, `authKey` 與請求體 `ActivityProductRedeemLogDTO`
2. 透過 `authKey` 查找 `member.gameusers` 取得使用者帳號（需 `status=1`）
3. 確認使用者未被封鎖（`member.gameusers_banned`）
4. 查詢目標商品 `product.products_activity`，驗證商品存在、`status=1` 且 `quantity` ≥ 請求兌換數量
5. 執行 Cassandra LWT 更新庫存：`UPDATE … SET quantity = quantity - 請求數 WHERE … IF quantity >= 請求數`
6. 若 LWT 失敗（庫存不足），回傳錯誤
7. 寫入兌換記錄 `product.products_activity_redeem_logs`，狀態設為 `0`（待處理）
8. 回傳成功結果

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ActivityController.PostProductRedeemLogs` | 接收請求，調用 Service |
| 2 | Service | `ActivityService.RedeemProduct` | 組織兌換邏輯 |
| 3 | Service | `ActivityService.RedeemProduct` | 調用 MemberProvider 取得使用者資訊（`gameusers`） |
| 4 | Provider | `MemberProvider.GetGameUser(authKey)` | 查詢 `member.gameusers` 並過濾 `status=1` |
| 5 | Provider | `MemberProvider.CheckBan(authKey)` | 檢查 `gameusers_banned`，若封禁中則拒絕 |
| 6 | Service | `ActivityService.RedeemProduct` | 調用 ProductProvider 讀取商品 |
| 7 | Provider | `ProductProvider.GetActivityProduct(site, activityevent, pid)` | 查詢 `product.products_activity`，檢查 `status=1` |
| 8 | Service | `ActivityService.RedeemProduct` | 執行 LWT 扣減庫存（調用 `ProductProvider.UpdateQuantityLWT`） |
| 9 | Provider | `ProductProvider.UpdateQuantityLWT(…)` | 執行 CQL `UPDATE product.products_activity SET quantity = quantity - ? WHERE site=… AND activityevent=… AND id=… IF quantity >= ?` |
| 10 | Service | `ActivityService.RedeemProduct` | LWT 成功後，寫入 `products_activity_redeem_logs` |
| 11 | Provider | `ProductProvider.InsertRedeemLog(…)` | 寫入記錄，`status=0`（待處理） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `member.gameusers` | Read | 取得使用者帳號與狀態 |
| DB | `member.gameusers_banned` | Read | 確認使用者是否封禁中 |
| DB | `product.products_activity` | Read + Write (LWT) | 讀取商品資訊，原子扣減庫存 |
| DB | `product.products_activity_redeem_logs` | Write | 建立兌換記錄 (status=0) |
| Redis | 無 | — | 此流程未使用 Redis 快取 (根據現有文件) |
| Queue | 無 | — | 無 Kafka 或其他訊息佇列使用 |

---

## 6. 重要規則

- **權限限制**：僅登入使用者（持有有效 `authKey`）可進行兌換；帳號須非封禁狀態 (`status=1` 且不在 `gameusers_banned`)
- **商品狀態**：只能兌換 `status=1`（販售中）且 `quantity` ≥ 請求數量的商品
- **庫存扣減**：必須使用 Cassandra LWT (`IF quantity >= ?`)，禁止先讀後寫式扣減，避免超賣
- **兌換記錄 status**：初始值固定為 `0`（待審核），只有後台審核可更新為 `1`(通過) 或 `2`(拒絕)
- **不可修改欄位**：`products_activity.price`、`quantity` 僅由後台統一維護；兌換 API 不得直接改寫其他欄位
- **Transaction**：Cassandra 不支援傳統 ACID 交易，依賴 LWT 達成條件式原子更新
- **TTL**：未使用
- **不可暴露資料**：兌換記錄中不應回傳內部 `id` 機制對外暴露所有細節；對外僅回傳摘要

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| authKey 無效 | 回傳 401 或「使用者未登入」 |
| 使用者被封禁 | 回傳「帳號已停用」或禁止操作 |
| 商品不存在或 status ≠ 1 | 回傳「商品不可兌換」 |
| 庫存不足（LWT 失敗） | 回傳「庫存不足，兌換失敗」 |
| 重複兌換（相同使用者對同商品重複請求） | 需人工確認：若有防重機制則拒絕，若無則可能重複扣庫 |
| Cassandra 寫入失敗 | 回傳系統錯誤，不應部分成功（LWT 失敗則不容許後續寫入） |
| LWT 成功但 redeem_logs 寫入失敗 | 可能導致庫存已扣但記錄遺失（高風險） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC01 | API Test | 正常兌換（商品有庫存） | 200，庫存減 1，產生 status=0 記錄 |
| TC02 | Flow Test | 庫存僅剩 1，同時兩個請求 | 僅一筆成功，另一筆因 LWT 回覆庫存不足 |
| TC03 | Permission Test | 使用無效 authKey | 401 |
| TC04 | Permission Test | 封禁帳號兌換 | 拒絕，回傳帳號停用訊息 |
| TC05 | API Test | 商品 status=0 (下架) | 拒絕，回傳商品不可兌換 |
| TC06 | Integration Test | LWT 成功後 redeem_logs 寫入失敗 | 確認系統是否有補償機制或人工介入補救（高風險） |
| TC07 | API Test | 請求數量超過庫存 | 拒絕，庫存不足 |

---

## 9. 高風險區域

- **高風險 table**：`product.products_activity`（庫存欄位），`products_activity_redeem_logs`（記錄完整性）
- **高風險 API**：POST兌換 (超賣/庫存不一致)
- **跨服務資料同步**：本兌換流程僅涉及單一服務，唯後續審核需後台服務更新 redeem_logs status
- **Transaction**：LWT 保證庫存扣減原子性，但 redeem_logs 寫入失敗時缺乏分布式事務保護，庫存可能已扣但記錄未寫入
- **Cache consistency**：無快取
- **Idempotency**：目前無保證（需人工確認是否有基於請求 id 的冪等機制）

---

## 10. 常見錯誤

- ❌ 未使用 LWT，而是先 SELECT 庫存，再 UPDATE，導致超賣
- ❌ 在 LWT 失敗後仍寫入 redeem_logs
- ❌ 未檢查 `gameusers_banned` 或 `gameusers.status=1` 即允許兌換
- ❌ 誤改 `products_activity.price` 或直接寫入 `quantity` 為錯誤值
- ❌ 兌換記錄寫入 status 非 0 (例如 1 直接通過審核)
- ❌ 沒有處理 redeem_logs 寫入失敗的補償

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI: POST /api/activity/productredeemlogs/{site}/{activityEvent}/{authKey} |
| DB | product.products_activity (payment keyspace) |
| DB | product.products_activity_redeem_logs (payment keyspace) |
| DB | member.gameusers, member.gameusers_banned |
| Code | Service: ActivityService.RedeemProduct (推測) |
| Code | Provider: ProductProvider.UpdateQuantityLWT (推測) |
| Rules | payment-detail.md: products_activity.quantity 必須 LWT 扣減；redeem_logs.status 初始值 0 |

---

**建議新增**：
- 建議新增冪等性設計（例如以請求 id 判斷重複提交）
- 建議新增 redeem_logs 寫入失敗時的補償機制或 alert
- 若存在多站點同時兌換，需確認 LWT 在 Cassandra 多 DC 部署下的一致性