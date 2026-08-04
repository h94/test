# 查詢使用者活動兌換紀錄

## 1. 場景目的

讓已登入的使用者查看自己在特定活動中的兌換紀錄，僅顯示非審核中的紀錄，並確保不暴露其他使用者的資料或敏感欄位。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/activity/productredeemlogs/{site}/{activityEvent}/{account}` | 查詢使用者活動兌換紀錄 |

---

## 3. 流程總覽

1. 前端傳入 `site`、`activityEvent` 與目標 `account`。
2. API 層驗證使用者 token 並取得登入帳號。
3. 比對 token 帳號與路徑參數 `account` 是否一致，不一致則拒絕。
4. 調用 Service 查詢 Cassandra 表 `products_activity_redeem_logs`，條件：
   - `site`、`activityevent`、`account` 完全匹配
   - 排除 `status = 0`（審核中）的紀錄
5. 回傳結果時，移除 `account` 欄位（依安全規則），並適度分頁（避免單次回傳過多）。
6. 若無資料則回傳空陣列。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ActivityController.GetProductRedeemLogs` | 接收路由參數，呼叫驗證並轉交 Service |
| 2 | Validator | 驗證 Token (ECCore) | 確認使用者已登入並解析 token 中的帳號 |
| 3 | Controller | - | 比較 token帳號 與路徑 `account`，不符回傳 403 |
| 4 | Service | `ActivityService.GetUserRedeemLogs` | 組裝查詢條件，呼叫 Data Provider |
| 5 | Provider | `ActivityDataProvider.QueryLogsByAccount` | 執行 Cassandra CQL，過濾 `status != 0` |
| 6 | Transfer | DTO/Projection | 移除 `account`，選取必要欄位回傳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `product.products_activity_redeem_logs` | Read | 查詢指定 site/activityevent/account 的兌換紀錄 |
| Redis | - | - | 本場景無使用 |
| Queue | - | - | 本場景無使用 |

---

## 6. 重要規則

- **權限限制**：僅允許查詢與登入 token 相同 `account` 的紀錄，禁止跨帳號查詢。
- **狀態過濾**：`status = 0`（審核中）的紀錄一律不返回給使用者。
- **不可回傳欄位**：回傳物件中不可包含 `account`（即使前端已經知道），避免潛在隱私外洩。
- **查詢條件強制性**：Cassandra 查詢必須使用 `site`、`activityevent`、`account` 組合作為完整分割鍵，不得全表掃描或僅用部分鍵。
- **分頁建議**：若同一帳號兌換紀錄過多，應實作分頁（例如依 `addtime` 或 `id` 進行游標分頁），避免單次載入大量資料。
- **錯誤處理**：若任何必要參數缺失或 token 無效，直接回傳 401/403，不進行後續 DB 查詢。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未攜帶 Token | 回傳 401 Unauthorized |
| Token 有效但帳號與路徑 `account` 不符 | 回傳 403 Forbidden |
| 傳入不存在的 site 或 activityEvent | 回傳空陣列（200 OK） |
| Cassandra 查詢時發生異常 | 回傳 500 Internal Server Error，不暴露 DB 細節 |
| 查詢結果中包含 status=0 的紀錄（理論上已被過濾） | 回傳資料中不應出現 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T01 | API Test | 有效 Token，查詢自己帳號 | 200，回傳非審核中的紀錄，不含 `account` 欄位 |
| T02 | Permission Test | 有效 Token，但路徑 `account` 與登入帳號不同 | 403 Forbidden |
| T03 | API Test | 無 Token 請求 | 401 Unauthorized |
| T04 | Integration Test | 查詢的帳號有 status=0 與 status=1 的紀錄混雜 | 僅回傳 status!=0 的紀錄 |
| T05 | Flow Test | 查詢不存在的 site/activityEvent | 200 OK，空陣列 |
| T06 | API Test | 返回的 JSON 中不得出現 `account` 鍵 | Pass |

---

## 9. 高風險區域

- **隱私洩漏**：若未強制比對 token 帳號，可能讓使用者猜測他人紀錄。
- **審核中紀錄意外曝光**：若過濾條件錯誤，可能將未審核狀態的兌換提前展示給使用者。
- **Cassandra 查詢未使用完整分割鍵**：可能導致效能低落或全表掃描。
- **分頁缺失**：大量資料可能拖垮前端，應強制限制每頁筆數。

---

## 10. 常見錯誤

- ❌ 忘記在 Service 層加入 `status != 0` 條件。  
- ❌ 在回傳物件中直接包含 `account` 欄位。  
- ❌ 未檢查 token 與路徑 account 的一致性，導致越權。  
- ❌ 使用 LIKE 或非確切匹配查詢 Cassandra，觸發全叢集掃描。  
- ❌ 實作分頁時未正確使用 `addtime` 等排序鍵，導致資料遺漏或重複。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 定義 | OpenAPI `GET /api/v1/activity/productredeemlogs/{site}/{activityEvent}/{account}` |
| 讀取規則 | `product-detail.md` (讀取規則：「未審核(status=0)的記錄不應回傳給使用者」) |
| 不可回傳欄位 | `product-detail.md` (不可回傳欄位：`products_activity_redeem_logs.account`) |
| 權限限制 | 所有 Activity API 均需驗證 (README)；權限邏輯由 ECCore 處理 |
| DB Schema | `product.products_activity_redeem_logs` 結構 (Schema `product.md`) |
| 狀態值定義 | `AppDefine.ActivityProductLogStatus` (0=審核中, 1=成功, 2=失敗) |