# 支付結果回調

## 1. 場景目的

接收 PaymentService 或第三方支付網關的回調通知，完成：  
- 寫入 `member.gamesublogs` 訂閱交易紀錄  
- 更新 `member.gameusers.memberships`（APPEND 方案權限）  
- 同步更新 `stock.users.SubEndTime` 為最新訂閱到期日  

此流程確保支付成功後會員資格即時生效。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/payment/callback`（推測） | 接收支付結果回調，實際路徑**需人工確認**（OpenAPI 未顯式列出） |

---

## 3. 流程總覽

1. 驗證回調來源簽名或 token（防止偽造）  
2. 解析回調參數：`authKey`、`tradeNo`、方案 ID、支付狀態  
3. 查詢 `member.gameusers` 確認使用者存在且 `status=1`  
4. 根據方案 ID 取得有效期長度（如從設定或方案表）  
5. 計算 `subendtime`：  
   - 若無前次訂閱或已過期 → 當前時間 + 方案有效期  
   - 若尚有有效訂閱 → 前次到期時間 + 方案有效期（續堆疊）  
6. 寫入 `member.gamesublogs`（authkey, subtime, tradeno, subendtime, autosub…）  
7. APPEND `member.gameusers.memberships` 對應方案權限字串  
8. 透過 `stock.users` 的 `Account` 查詢對應使用者，UPDATE `SubEndTime` 為新的 `subendtime`  
9. 清除相關 Redis 快取：`GameUser:{authKey}`  
10. 回傳成功（或異步通知）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `PaymentController.Callback`（推測） | 接收請求、簽名驗證 |
| 2 | Service | `SubscriptionService.ProcessCallback`（推測） | 協調寫入邏輯 |
| 3 | Provider | `MemberProvider.InsertGameSubLog`（推測） | 寫入 gamesublogs |
| 4 | Provider | `MemberProvider.AppendMembership`（推測） | 更新 gameusers.memberships |
| 5 | Provider | `StockProvider.UpdateSubEndTime`（推測） | 更新 stock.users.SubEndTime |
| 6 | Service | `CacheInvalidator.ClearUserCache`（推測） | 刪除 Redis 快取 |

**需人工確認**：以上類別與方法名為依慣例推測，實際以原始碼為準。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | member.gamesublogs | INSERT | 寫入訂閱紀錄（authkey, subtime, subendtime…） |
| DB (Cassandra) | member.gameusers | UPDATE (APPEND memberships) | 新增會員資格權限 |
| DB (MySQL) | stock.users | UPDATE (SubEndTime) | 更新股票使用者訂閱到期日 |
| Redis | `GameUser:{authKey}` | DEL | 清除會員快取，強制下次讀取新會員資料 |

無 Queue / Kafka 參與本流程（依據現有資料）。

---

## 6. 重要規則

- **權限限制**：回調端點必須驗證來源（例如 HMAC 簽章），僅允許 PaymentService 或信任閘道呼叫  
- **memberships 寫入**：僅可 APPEND 元素至 `gameusers.memberships`，禁止直接 SET 整個 list  
- **subendtime 計算**：  
  - 方案有效期長度需從設定取得（如 `rechargeplans_newlottery` 或內部配置）  
  - 續訂時需讀取前次 `gamesublogs` 最新記錄的 `subendtime` 決定起始時間  
- **stock.users.SubEndTime**：該欄位僅由訂閱回調流程寫入（本服務為 pricecentersite，**需人工確認**是否有直接寫入權限，和 db-usage 規則衝突）  
- **不可回傳欄位**：`gamesublogs.tradeno`、`paymethod` 等敏感資訊不可對外 API 露出  
- **TTL 規則**：Redis `GameUser:{authKey}` 須在會員資格變更後主動刪除，不可只靠 TTL  
- **Idempotency**：相同 `tradeNo` 重複回調不應重複寫入 `gamesublogs`（建議以 `authkey + tradeno` 檢查唯一性）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 回調簽名驗證失敗 | 拒絕請求，記錄異常 |
| authKey 不存在 | 回傳錯誤，不寫入任何記錄 |
| 方案 ID 不存在或已停用 | 回傳錯誤 |
| `gameusers.status != 1`（已停用） | 拒絕寫入，可能通知管理者 |
| `gamesublogs` 寫入成功但 `gameusers.memberships` 失敗 | 需補償或重試，避免會員資格遺失 |
| `stock.users` 查無對應 `Account` | **需人工確認**處理方式：可能該站點不需要此同步，或應記錄異常 |
| 重複 `tradeNo` | 跳過寫入，回傳已處理 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| WF-01 | Integration Test | 正常首次訂閱回調 | gamesublogs 新增一筆，memberships 新增，SubEndTime 更新 |
| WF-02 | Integration Test | 續訂（已有有效訂閱） | subendtime 基於前次到期日延長；memberships 不重複相同值 |
| WF-03 | API Test | 無效簽名 | 回傳 401/403 |
| WF-04 | API Test | authKey 不存在 | 回傳 404 或錯誤代碼 |
| WF-05 | Flow Test | Redis 快取清除 | 回調成功後 `GameUser:{authKey}` 被刪除，下次查詢取得新 memberships |
| WF-06 | Idempotency Test | 重複送同一 tradeNo | 第二次請求不重複寫入，回傳成功 |
| WF-07 | Permission Test | 外部直接呼叫（無簽名） | 拒絕 |

---

## 9. 高風險區域

- **跨資料庫一致性**：Cassandra (`member` keyspace) 與 MySQL (`stock.users`) 之間無分散式交易，若 `stock.users` 更新失敗需重試或記錄補償任務  
- **memberships 誤覆蓋**：若實作未使用 APPEND 而使用 SET，會導致其他服務寫入的資格遺失  
- **subendtime 計算錯誤**：未正確讀取前次到期日可能導致訂閱時間縮短或覆蓋  
- **Redis 快取未清除**：會員到期後前端仍顯示 VIP 狀態，造成誤導  
- **Idempotency**：缺少 tradeNo 唯一檢查可能重複寫入 gamesublogs

---

## 10. 常見錯誤

- ❌ 未檢查 `gameusers.status` 即寫入訂閱 → 已停用帳號不應獲得新訂閱  
- ❌ 直接 SET `gameusers.memberships` 而非 APPEND → 導致先前資格丟失  
- ❌ `subendtime` 計算使用當前時間而非前次到期日 → 續訂用戶損失剩餘天數  
- ❌ 忘記更新 `stock.users.SubEndTime` → 股票相關功能仍判斷為過期  
- ❌ 回調 API 未做來源驗證 → 可能被偽造請求開通 VIP  

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| DB Table | member.gamesublogs |
| DB Table | member.gameusers (memberships) |
| DB Table | stock.users (SubEndTime) |
| 寫入限制 | member-detail：gameusers.memberships 僅可 APPEND |
| 到期計算 | member-detail：subendtime 依前次記錄或當前時間計算 |
| Redis Key | `GameUser:{authKey}`（member-detail Redis 節） |
| 本服務權限 | pricecentersite-detail：stock.users.SubEndTime「僅付款成功後由訂閱服務寫入；本服務不可直接修改」⚠️ **衝突待人工確認** |
| API 入口 | **無直接 evidence，需人工確認回調端點定義** |