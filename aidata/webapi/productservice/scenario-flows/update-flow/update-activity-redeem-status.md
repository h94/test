# 更新活動商品兌換狀態

## 1. 場景目的
後台管理員或審核人員將一筆活動商品兌換記錄的狀態從「審核中（0）」更新為「成功（1）」或「失敗（2）」，且更新為成功或失敗後即鎖定，不得再變更。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/activity/productredeemlogs/{site}/{activityEvent}/{account}/{id}/status` | 更新指定兌換記錄的狀態 |

- 所有路徑參數（`site`、`activityEvent`、`account`、`id`）均為必填。
- Request Body 為 `ActivityProductRedeemLog` 物件，其中 `status` 欄位必填。
- 需要驗證（`ECCore 3.0.2` 內建機制）。

---

## 3. 流程總覽

1. **接收請求**：驗證 JWT Token 有效性與路徑參數完整性。
2. **路由匹配**：Controller 將 `site`, `activityEvent`, `account`, `id` 與 Body 傳入 Service。
3. **查詢既有兌換記錄**：透過分區鍵 `site`、`activityevent`、`account` 與 `id` 從 `products_activity_redeem_logs` 讀取現有記錄。
4. **狀態變更前驗證**：
   - 記錄必須存在。
   - 當前狀態不可為 `1`（成功）或 `2`（失敗），否則拒絕更新。
   - 新狀態限 `1` 或 `2`（來源：`ActivityProductLogStatus` 枚舉）。
5. **執行更新**：呼叫 `UpdateActivityProductRedeemLogStatus` 方法寫入新狀態與 `updatetime`。
6. **回傳成功**：HTTP 200。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ActivityController.UpdateActivityProductRedeemLogStatus` | 接收 PUT 請求，提取路徑參數與 Body |
| 2 | Service | `IActivityService.UpdateProductRedeemLogStatus(site, activityEvent, account, id, newStatus)` | 組合查詢條件，呼叫 Provider |
| 3 | Provider | `IActivityDataProvider.GetActivityProductRedeemLog(...)` | 執行 CQL `SELECT` 以 `site, activityevent, account, id` 為條件 |
| 4 | Service | `IActivityService.ValidateStatusTransition(currentStatus, newStatus)` | 檢查當前狀態允許變更為新狀態 |
| 5 | Provider | `IActivityDataProvider.UpdateActivityProductRedeemLogStatus(...)` | 執行 CQL `UPDATE ... SET status = ?, updatetime = ?` |
| 6 | Controller | 回應 HTTP 200 | |

> 需人工確認：具體類別與方法名稱以實際原始碼為準，本文件依據命名慣例推斷。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.products_activity_redeem_logs` (Cassandra) | Read | 查詢現有兌換記錄 |
| DB | `payment.products_activity_redeem_logs` (Cassandra) | Update | 寫入新狀態與更新時間 |
| Redis | 無 | — | 本場景無快取操作 |
| Queue/Kafka | 無 | — | 本場景無訊息佇列 |

- 由於 `productservice` 是 `payment` keyspace 的 owner，實際操作的 keyspace 為 `payment`。
- 另一份 `product.products_activity_redeem_logs` 表亦有定義，但目前產品服務主要使用 `payment` keyspace。

---

## 6. 重要規則

- **寫入限制**：`products_activity_redeem_logs.status` 僅能由 `UpdateActivityProductRedeemLogStatus` 方法更新，不可直接執行 UPDATE 語句。（Evidence: DB 操作邊界文件）
- **狀態流轉規則**：
  - `status = 0`（審核中）可轉換為 `1`（成功）或 `2`（失敗）。
  - `status` 一旦為 `1` 或 `2` 即不可再變更；重複請求應拒絕。
- **狀態值定義**（來源：`AppDefine.ActivityProductLogStatus`）：
  - `0`：審核中
  - `1`：成功
  - `2`：失敗
- **不可變更欄位**：`id`、`account`、`pid`、`addtime` 寫入後不可修改；本 API 僅更新 `status` 與 `updatetime`。
- **回傳限制**：不得在 Response 中暴露 `account` 欄位；不可回傳其他敏感資訊。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 請求缺少任一必填路徑參數 | HTTP 400 Bad Request |
| 未附帶有效 JWT Token 或 Token 過期 | HTTP 401 Unauthorized |
| 兌換記錄不存在（`site, activityevent, account, id` 組合無資料） | HTTP 404 Not Found |
| 當前狀態已為 `1`（成功），嘗試再次更新 | HTTP 409 Conflict（或 400），錯誤訊息指出狀態不得變更 |
| 當前狀態已為 `2`（失敗），嘗試再次更新 | HTTP 409 Conflict（或 400） |
| Body 中的 `status` 不是合法的 `1` 或 `2`（例如 `3`） | HTTP 400 Bad Request（狀態值無效） |
| Cassandra 寫入失敗（Timeout 或 Quorum 不足） | HTTP 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| ACT-UP-01 | API Test | 使用合法 Token，將 status 從 0 更新為 1 | HTTP 200，DB 狀態變更為 1 |
| ACT-UP-02 | API Test | 使用合法 Token，將 status 從 0 更新為 2 | HTTP 200，DB 狀態變更為 2 |
| ACT-UP-03 | Flow Test | 對同一記錄連續執行兩次成功更新（第一次 0→1，第二次嘗試任何更新） | 第二次請求應回 409 或 400 |
| ACT-UP-04 | Permission Test | 使用一般使用者（非後台角色）Token 呼叫 | HTTP 403 Forbidden（需確認權限設定） |
| ACT-UP-05 | API Test | 傳入不存在的 id | HTTP 404 |

---

## 9. 高風險區域

- **狀態鎖定**：成功或失敗後不可再變更，若程式未正確檢查當前狀態，可能造成重複發貨或重複拒絕。
- **併發寫入**：兩個後台管理員幾乎同時對同一筆記錄進行審核，須確保樂觀鎖或條件更新（例如僅在 status=0 時才更新）以避免狀態覆蓋。
- **keyspace 混淆**：`product` 與 `payment` keyspace 皆有同名表，寫入時需確保操作正確的 keyspace，否則會遺失記錄。
- **不可回傳帳號**：Response 中可能不小心序列化 `account` 欄位，需嚴格控制輸出 DTO。

---

## 10. 常見錯誤

- ❌ 直接使用 `UPDATE` CQL 變更 `status`，而非呼叫 `UpdateActivityProductRedeemLogStatus` 方法 → ✅ 必須透過專用方法，以確保業務邏輯集中檢查與審計。
- ❌ 未檢查當前狀態就寫入新狀態，導致將已成功的記錄再次改為失敗 → ✅ 務必先讀取原始狀態，僅當狀態為 `0` 時才允許寫入。
- ❌ 對外 API 回傳整個 `ActivityProductRedeemLog` 物件，暴露 `account` → ✅ 需建立不含 `account` 的 Response DTO。
- ❌ 忘記更新 `updatetime`，導致記錄無變更時間戳 → ✅ 每次寫入都必須一併更新 `updatetime`。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | OpenAPI: `PUT /api/v1/activity/productredeemlogs/{site}/{activityEvent}/{account}/{id}/status` |
| 狀態值定義 | `ProductService.Model.AppDefine.ActivityProductLogStatus`（code semantics 標註） |
| 寫入限制 | `product-detail.md`: "products_activity_redeem_logs.status 僅由 `UpdateActivityProductRedeemLogStatus` 更新，成功後不可再變更" |
| 狀態枚舉 | `payment-detail.md`: "0=審核中, 1=成功, 2=失敗" |
| 不可變更 Clustering Key | `product-detail.md`: "pid、account 寫入後不可變更" |
| 服務角色 | `payment-detail.md`: productservice 是 payment keyspace 的 owner，可讀寫 products_activity_redeem_logs |
| 驗證要求 | README: 所有 `/api/v1/activity/*` 路由標記需要驗證 ✅ |