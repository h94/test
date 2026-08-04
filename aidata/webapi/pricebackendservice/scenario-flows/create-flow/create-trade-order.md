# 後台手動建立體育交易訂單

## 1. 場景目的

後台管理員為指定會員手動建立一筆體育交易訂單（例如補單、線下付款確認、特殊商品購買），完成支付流程並確保會員資格或商品權益生效。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/payment/sport/tradeorders` | 建立交易訂單，需後台驗證 |

---

## 3. 流程總覽

1. 後台管理員透過前端發起建立交易訂單請求，攜帶會員帳號、支付方式、金額、商品／方案識別資訊。
2. `PriceBackendService` 驗證 JWT 權限（後台角色）。
3. 呼叫 `memberservice` 查詢會員詳細資訊（`gameusers`），確認會員存在、狀態正常。
4. 根據請求中的商品或方案類型，呼叫 `paymentservice` 建立交易訂單（`CreateTradeOrder`）。
5. `paymentservice` 執行支付邏輯：驗證支付方式可用、檢查庫存（若為商品）、記錄交易流水、更新會員錢包或訂閱狀態。
6. 回傳交易訂單編號及結果給後台前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method（推估） | 動作 |
|------|-------|------------------------|------|
| 1 | Middleware | `AuthenticationMiddleware` | 驗證 JWT，確保使用者具有後台權限 |
| 2 | Controller | `PaymentController.CreateTradeOrder` | 接收請求，轉發給 Service |
| 3 | Service | `PaymentService.CreateTradeOrderAsync` | 組合參數，依序呼叫下游服務 |
| 4 | Service | `MemberServiceClient.GetGameUserAsync(account)` | 透過 `memberservice` HTTP API 查詢會員（`GET /member/game/users/{authKey}` 或類似） |
| 5 | Service | 內部檢查 | 確認會員 `status == 1`、非機器人、未被封禁 |
| 6 | Service | `PaymentServiceClient.CreateTradeOrder(request)` | 呼叫 `paymentservice` 建立訂單（HTTP POST） |
| 7 | Provider | `PaymentServiceClient` (HTTP) | 發送請求至 `paymentservice` 的內部 API，例如 `POST /api/internal/tradeorders` |
| 8 | Downstream | `paymentservice` 內部邏輯 | 寫入交易記錄（可能 Table：`paymentservice` 專用訂單表）、更新會員餘額（呼叫 `memberservice` 更新 `gameusers_wallet`）、記錄兌換日誌（若為商品時寫入 `products_activity_redeem_logs`） |
| 9 | Service | 組裝回應 | 成功時回傳交易 ID 與狀態；失敗時拋出錯誤訊息 |

> **注意**：上述流程為推測，具體下游 API 路徑與方法名需人工確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源（由下游服務操作） | 操作 | 用途 |
|------|----------------------|------|------|
| DB | `member.gameusers`（讀） | Read | 驗證會員狀態、取得 `authkey`、`account` |
| DB | `member.gameusers_banned`（讀） | Read | 確認會員未被停權 |
| DB | `member.gamerobots`（讀） | Read | 排除機器人帳號 |
| DB | `payment.products_activity`（讀/寫） | Read/Update | 若交易涉及商品，檢查庫存、狀態，更新數量 |
| DB | `payment.products_activity_redeem_logs`（寫） | Write | 記錄商品兌換日誌（需人工確認） |
| DB | `payment.paymethods_sport`（讀） | Read | 確認支付方式有效（`enabled=1`） |
| DB | 下游內部交易訂單表（推測） | Write | 儲存交易訂單紀錄 |
| DB | `member.gamesublogs`（寫） | Write | 若為訂閱方案，記錄訂閱資訊 |
| DB | `member.gameusers_wallet`（MySQL） | Update | 更新會員錢包餘額（需人工確認） |
| Redis | `Predict Cache` 等（無直接影響） | — | 本場景未使用 Redis |
| Queue | Kafka（`applogs`） | Publish | 記錄交易日誌，供後續分析 |

> 註：`pricebackendservice` 不直接存取任何 DB，所有操作均透過下游 REST API 完成。

---

## 6. 重要規則

- **權限限制**：僅後台管理角色可呼叫，JWT 驗證必須通過。
- **會員驗證**：必須檢查 `status = 1`、未停權（`gameusers_banned` 無有效記錄）、非機器人。
- **支付方式**：必須為啟用狀態（`enabled = 1`），且支付方式代碼與請求一致。
- **庫存限制**：若為商品交易，`products_activity.quantity > 0` 且 `status = 1`。
- **不可修改欄位**：交易訂單建立後，其金額、會員、時間等核心欄位不可變更，任何異常需走退款或沖正流程。
- **餘額充足**：若涉及錢包扣款，需確保 `gameusers_wallet.Balance >= amount`。
- **冪等性**：相同請求（含 idempotency key）應避免重複建立訂單。
- **不可暴露**：`password`、`authkey`、`email` 等敏感欄位不可在 API 回應中返回。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 帳號不存在或非體育會員 | 回傳 404，錯誤碼通知「會員不存在」 |
| 會員被封禁（`status=2` 或 `gameusers_banned` 有記錄） | 回傳 403，禁止交易 |
| 支付方式不存在或已停用 | 回傳 400，提示「支付方式不可用」 |
| 商品庫存不足或已下架 | 回傳 409，提示「庫存不足」或「商品已下架」 |
| 錢包餘額不足 | 回傳 402，提示「餘額不足」 |
| 下游 `paymentservice` 或 `memberservice` 呼叫失敗 | 回傳 502 或 503，記錄錯誤日誌 |
| 請求體格式錯誤 | 回傳 400，列出缺失欄位 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T01 | Permission Test | 無 JWT 或非後台角色呼叫 API | 401 或 403 |
| T02 | API Test | 提供有效的會員與支付資訊 | 201 Created，返回交易 ID |
| T03 | Flow Test | 建立商品交易後，確認庫存減少 | 商品數量 -1，兌換記錄產生 |
| T04 | Flow Test | 訂閱方案交易後，確認會員 `memberships` 增加 | 會員具備有效訂閱 |
| T05 | Error Test | 使用已停用支付方式 | 400 Bad Request |
| T06 | Idempotency | 相同請求重送兩次 | 只建立一筆訂單，第二次回傳相同 ID |
| T07 | Integration Test | 下游服務回應逾時 | 系統 504，無訂單建立 |

---

## 9. 高風險區域

- **金額正確性**：手動建立訂單易出錯，需雙重驗證金額與商品對應關係。
- **錢包操作**：直接呼叫 `memberservice` 更新錢包，需確保原子性，避免餘額不一致。
- **跨服務交易**：`paymentservice` 與 `memberservice` 之間若無分散式事務，失敗時需有補償機制。
- **庫存超賣**：商品兌換需在 `paymentservice` 內使用原子操作（如 Cassandra 的輕量級事務或鎖）。
- **冪等性缺失**：若無 idempotency key，重複請求可能造成重複扣款或多次出貨。
- **敏感資料**：後台操作可能攜帶會員 email 或 authkey，日誌記錄時應脫敏。

---

## 10. 常見錯誤

- ❌ 新人直接嘗試存取 DB，未透過下游 API → `pricebackendservice` 無 DB 連線，此舉無法運作。
- ❌ 未檢查會員 `status=1` 或 `enabled=1` 即建立訂單 → 可能為已停權會員建立交易。
- ❌ 修改已建立訂單的金額或會員 → 訂單核心資料不可改，應以新交易取代。
- ❌ 忘記檢查支付方式 `enabled=1` → 可能使用已停用管道。
- ❌ 未建立 idempotency key，導致重複請求時產生多筆訂單。
- ❌ 回傳時未過濾 `password`、`authkey` 等敏感欄位。
- ❌ 直接對外暴露下游服務的錯誤細節，洩漏內部架構。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md「支付管理」`POST /api/v1/payment/sport/tradeorders` |
| 服務相依 | README.md 相依服務列表：`memberservice`、`paymentservice` |
| DB 寫入限制 | `db/payment-detail.md`：`products_activity.quantity` 不可直接 UPDATE，需經兌換邏輯遞減 |
| DB 讀取規則 | `db/member-detail.md`：查詢會員需 `status=1`、排除 `gamerobots` |
| 權限 | OpenAPI 標記此路由需要驗證（`✅ 需要驗證`） |
| 程式流程 | Controller/Service/Provider 推測基於一般 BFF 架構，具體實作需人工確認 |
| 不可回傳欄位 | `db/member-detail.md`：不可回傳 `password`、`authkey`、`email`（特定場景除外） |
| 錯誤處理 | 標準 HTTP 狀態碼，實際回應需參考 `paymentservice` 錯誤格式 |