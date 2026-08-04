# 查詢活動兌換記錄

## 1. 場景目的

後台管理人員查詢特定站台（site）及活動（activityEvent）下，會員兌換活動商品的歷史記錄，用於審核、出貨或客服調閱。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/activity/{site}/{activityEvent}/redeemlogs` | 查詢活動兌換記錄 |

---

## 3. 流程總覽

1. 後台前端呼叫 API，帶入路徑參數 `site`、`activityEvent` 及必要的身份驗證資訊。
2. `pricebackendservice` 驗證操作者權限（需後台管理角色）。
3. 將請求轉發至下游 `productservice`（或 `paymentservice`，視實際路由而定）的兌換記錄查詢介面。
4. 下游服務查詢 Cassandra 表 `payment.products_activity_redeem_logs`，條件為 `site` 與 `activityevent` 必須等於傳入值，可選過濾 `account`、`status` 等。
5. 下游服務回傳記錄集合。
6. `pricebackendservice` 將結果映射為 `ActivityRedeemLogDTO` 陣列後返回前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ActivityController.GetRedeemLogs` | 接收 GET 請求，抽取 `site`、`activityEvent` 參數，呼叫 Service |
| 2 | Service | `ActivityService.GetRedeemLogs` | 組裝查詢條件，呼叫下游 Provider |
| 3 | Provider | `ProductServiceProvider` 或 `PaymentServiceProvider` | 發送 HTTP GET 至 `productservice` 或 `paymentservice` 的對應端點（ex: `/api/product/redeemlogs`） |
| 4 | (下游) | `ProductService` | 執行 Cassandra 查詢 `SELECT * FROM payment.products_activity_redeem_logs WHERE site=? AND activityevent=?`，可選過濾 `account`, `status`，按 `addtime` 降序排列 |
| 5 | Transfer | `ActivityRedeemLogDTO` 轉換 | 將下游回應的資料轉為 DTO，屏蔽敏感欄位（如帳號部分遮罩或僅後台顯示完整） |

> ⚠️ 因缺乏直接程式碼，上述分層為基於 BFF 模式的合理推斷；實際方法名稱需人工確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `payment.products_activity_redeem_logs` | Read | 查詢活動商品的兌換記錄 |
| — | 無 Redis 快取 | — | 此場景無快取，直接查詢下游 |
| — | 無 Queue / Kafka | — | 僅為查詢操作 |

---

## 6. 重要規則

- **權限限制**：僅後台管理人員可呼叫此 API（需通過 ECFramework 驗證）。
- **必要條件**：`site` 與 `activityEvent` 為必填，且必須對應於既有站點與活動（由下游服務校驗）。
- **查詢限制**：下游服務必須強制以 `site` 和 `activityevent` 作為分區鍵條件，避免全表掃描。
- **不可暴露資料**：回傳的 `account` 欄位需視業務決定是否遮蔽（後台通常可顯示完整帳號，但需確保前端權限控制）；`email` (若有) 不應回傳。
- **排序規則**：常用 `addtime` 降序排列，以最新一筆在前。
- **狀態過濾**：若不指定 `status`，可回傳所有狀態（0:審核中, 1:成功, 2:失敗, 3:已發貨），前端可自行篩選。
- **不可修改欄位**：本 API 為唯讀，不可變更兌換記錄狀態（狀態更新請用 `PUT /api/v1/activity/{site}/{activityEvent}/redeemlogs/status`）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 缺少必要路徑參數 (`site` 或 `activityEvent`) | 400 Bad Request，提示參數錯誤 |
| 操作者未登入或權限不足 | 401 / 403，拒絕存取 |
| `site` 或 `activityEvent` 不存在於系統中 | 200 OK 但回傳空陣列（或下游回報 404，BFF 轉為 200 空列表） |
| 下游微服務 (productservice/paymentservice) 不可用 | 502 Bad Gateway 或 503，返回明確錯誤訊息 |
| Cassandra 查詢逾時 | 504 Gateway Timeout，需記錄 error log |
| 傳入的 `account` 過長或格式非法 | 400（若下游有驗證），BFF 可直接過濾 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | API Test | 正常查詢，提供有效 `site` 與 `activityEvent` | 200，返回記錄陣列，格式符合 `ActivityRedeemLogDTO` |
| T2 | Permission Test | 未帶 Auth Token 或 Token 無效 | 401 或 403 |
| T3 | Flow Test | 下游服務回應空列表 | 200，返回空陣列 |
| T4 | Flow Test | 提供 `account` 過濾參數，查詢特定會員記錄 | 返回僅該會員的記錄，不包含其他會員資料 |
| T5 | Flow Test | 傳入不存在的 `site` | 返回空列表（或依下游設計回報 404） |
| T6 | Flow Test | 模擬下游服務逾時 | BFF 返回 504，並產生 error log |
| T7 | API Test | 檢查回傳 JSON 不包含敏感欄位 (如會員 email) | 不出現 `email` 欄位 |

---

## 9. 高風險區域

- **高風險 table**：`payment.products_activity_redeem_logs` – 包含用戶兌換行為及狀態，需確保查詢時只回傳必要欄位，不可洩漏 `email` 等個資。
- **高風險 API**：此查詢 API 若未做權限控管，可能被未授權使用者取得所有會員兌換記錄，建議在 BFF 層強制檢查後台角色。
- **跨服務資料同步**：無。本流程僅讀取兌換記錄，無狀態同步問題。
- **Transaction**：無。
- **Cache consistency**：無快取，即時查詢下游，一致性好。
- **Queue retry**：不適用。
- **Idempotency**：查詢為冪等，無副作用。

---

## 10. 常見錯誤

- **新人容易犯錯**：忘記在 Service 層傳遞必要參數 `site` 和 `activityEvent`，導致下游全表掃描或報錯。
- **AI 容易誤解**：誤以為此服務直接存取 DB；應透過下游 `productservice` 或 `paymentservice` 的 REST API 取得資料。
- **常見漏檢查項目**：未驗證請求者的後台管理權限；未處理下游服務可能回傳的 404 或空結果。
- **常見錯誤流程**：BFF 層對下游回傳的資料未做 DTO 轉換，直接透傳底層 Cassandra 原始結構，導致不該暴露的欄位（如內部 ID 格式）洩漏。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `ActivityController` (推測) 對應 `GET /api/v1/activity/{site}/{activityEvent}/redeemlogs` |
| DB | `payment.products_activity_redeem_logs` (Cassandra) |
| DB 操作 | `pricebackendservice-detail.md` → payment section → products_activity_redeem_logs 為 writer/reader；下游查詢規則詳見 `db/payment-detail.md` |
| 權限 | README: 所有 `/api/v1/activity/*` 路由標示「需要驗證 ✅」 |
| 結構 | OpenAPI 定義回傳 `ActivityRedeemLogDTO` 陣列 |
| 服務相依 | README: pricebackendservice 相依 `productservice` 用於活動商品與兌換記錄 |