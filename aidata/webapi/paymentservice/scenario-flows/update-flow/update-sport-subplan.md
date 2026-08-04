# 更新體育訂閱方案

## 1. 場景目的

管理後台人員修改已存在的體育訂閱方案內容，例如調整方案名稱、價格、支付方式關聯等，並確保系統快取失效，使前台能立即取得最新資料。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/v1/sport/subplans/{id}` | 更新指定 ID 的體育訂閱方案 |

---

## 3. 流程總覽

1. 接收 PUT 請求，路徑包含待更新方案的 `id`，請求體為 JSON，包含欲更新的欄位。
2. 驗證請求者身份，必須具備管理後台權限。
3. 驗證請求參數，例如 `price` 必須為正整數，`name` 不可為空。
4. 讀取 `payment.sport_sub_plans` 中對應的現有方案。
5. 合併更新欄位，寫入 Cassandra `payment.sport_sub_plans`。
6. 使 Redis 快取 `SportCache:SportSubPlans` 失效。
7. 回傳更新後的方案資料或 204 No Content。

---

## 4. 程式流程

> **需人工確認**：以下流程基於常見 Controller → Service → Provider 分層與現有 DB 邊界文件推導，實際 class/method 名稱以程式碼為準。

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SportSubPlanController.UpdateSubPlan` | 接收 PUT `/api/v1/sport/subplans/{id}` 請求，呼叫 Service |
| 2 | Service | `SportSubPlanService.UpdateAsync` | 權限檢查、欄位驗證、調用 Provider |
| 3 | Provider | `SportSubPlanDataProvider.UpdateAsync` | 執行 Cassandra `UPDATE` 語句 |
| 4 | Provider | `CacheDataProvider.RemoveAsync` 或類似 | 刪除 Redis Key `SportCache:SportSubPlans` 與 `SportCache:SportSubPlans:{planID}` |
| 5 | Service | (同 2) | 組裝並回傳結果 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `payment.sport_sub_plans` | Read | 讀取現有方案資料，確認存在 |
| DB | `payment.sport_sub_plans` | Update | 寫入合併後的方案欄位 |
| Redis | `SportCache:SportSubPlans` | Delete | 使全方案清單快取失效 |
| Redis | `SportCache:SportSubPlans:{planID}` | Delete | 使單一方案快取失效 |

---

## 6. 重要規則

- **權限限制**：僅限管理後台 API 呼叫（需驗證）。
- **不可修改欄位**：方案 `id` 為 Primary Key，建立後不可更新。
- **價格欄位**：`price` 必須為正整數，不可為 0 或負數。
- **支付方式關聯**：`pay_methods` 更新時，應驗證其所參考的 `paytype` 和 `mode` 存在於 `payment.paymethods_sport`。
- **快取失效**：寫入 DB 成功後，**必須** 刪除 Redis 快取，不可只依賴 TTL。
- **未提供欄位**：請求體中未提供的欄位，應保持原值不變（部分更新）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 方案 ID 不存在 | 回傳 404 Not Found |
| 權限不足（非管理員） | 回傳 401 或 403 Forbidden |
| 請求體格式錯誤（如 `price` 為字串） | 回傳 400 Bad Request，含錯誤訊息 |
| 請求體包含不可修改欄位（如 `id`） | 回傳 400 Bad Request 或直接忽略 |
| Cassandra 寫入失敗 | 回傳 500 Internal Server Error，快取不應被清除 |
| 參考的支付方式不存在 | 回傳 400 Bad Request，提示參考無效 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UPD-SUB-01 | API Test | 正常更新方案名稱與價格 | 200，回傳更新後方案。確認 DB 值已變更，Redis 快取已清除 |
| UPD-SUB-02 | Permission Test | 無效 token 或一般使用者呼叫 | 401 或 403 |
| UPD-SUB-03 | Flow Test | 更新不存在的方案 ID | 404 |
| UPD-SUB-04 | Flow Test | 更新後立即查詢 `GET /api/v1/sport/subplans` | 回傳的資料為最新版本（無快取舊資料） |
| UPD-SUB-05 | API Test | 請求體缺少必要欄位 | 400 Bad Request |
| UPD-SUB-06 | API Test | 請求體包含 `id` 欄位 | 應被忽略或回傳錯誤，不以請求體中的 `id` 覆蓋路徑參數 |

---

## 9. 高風險區域

- **高風險 table**：`payment.sport_sub_plans`（直接影響前台顯示與訂閱購買）
- **Cache consistency**：DB 寫入成功但 Redis 刪除失敗 → 前台持續顯示舊資料。需記錄錯誤並觸發重試。
- **Transaction**：若 Cassandra 操作與 Redis 刪除需保證最終一致性，建議採用「先刪快取，再寫 DB」或補償機制。（此處依現有文件為「先寫 DB 後刪快取」）
- **Idempotency**：重複的更新請求會連續執行，可能導致後端處理無意義的寫入。須確保冪等性（相同請求多次執行結果一致）。

---

## 10. 常見錯誤

- ❌ **更新後忘記清除 Redis 快取** → ✅ 更新方案後必須呼叫 `SetSportPlanCache` 或直接刪除相關 Key。
- ❌ **請求體中覆蓋了 `id` 欄位** → ✅ 應以路徑中的 `id` 為準，忽略請求體中的 `id` 或直接報錯。
- ❌ **未驗證關聯的支付方式是否存在** → ✅ 更新 `pay_methods` 前，應查詢 `paymethods_sport` 確認 `paytype` + `mode` 存在且 `enabled=1`。
- ❌ **使用一般的更新方法直接覆蓋整個 object** → ✅ 應先讀取現有方案，合併請求體後再寫入，確保未提供的欄位維持原值。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `PUT /api/v1/sport/subplans/{id}` |
| DB | `payment.sport_sub_plans` |
| Redis | `SportCache:SportSubPlans`, `SportCache:SportSubPlans:{planID}` |
| DB 邊界 | `paymentservice-detail.md`：快取操作 |
| README | 體育訂閱方案 API 列表，驗證需求 |
| OpenAPI | `PUT /api/v1/sport/subplans/{id}` 路由（需人工確認確切 request/response schema） |