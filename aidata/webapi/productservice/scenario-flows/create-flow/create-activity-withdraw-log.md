# 建立活動提領紀錄

## 1. 場景目的

此場景用於活動結束後的獎品領取流程。當使用者完成活動兌換（`POST /api/v1/activity/productredeemlogs`）後，為建立實體獎品或需要後續處理的提領申請，前端會呼叫此 API 來寫入一筆待處理的活動提領紀錄。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/activity/withdrawlogs` | 新增活動提領紀錄 |

---

## 3. 流程總覽

1. 接收前端 POST request，body 包含 `ActivityWithdraw` 模型。
2. 必須通過 `ECCore` 驗證（權限檢查）。
3. 建立一筆 `withdrawlogs_activity` 紀錄。
4. 回傳成功結果（200 OK）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `ActivityController.WithdrawLogs` | 接收 `ActivityWithdraw` body 參數。 |
| 2 | Service | `ActivityService.WithdrawLogs` | 驗證輸入參數，準備寫入資料。 |
| 3 | Service | `ActivityService.WithdrawLogs` | 產生 `id`。引入 `AppExtensions.Get13Timestamp`。 |
| 4 | Service | `ActivityService.WithdrawLogs` | 呼叫 `_dataProvider.InsertWithdrawlog(...)`。 |
| 5 | Provider | `ActivityDataProvider.InsertWithdrawlog` | 將資料寫入 `product.withdrawlogs_activity` 表。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `product.withdrawlogs_activity` | Write | 寫入一筆新的提領紀錄。 |

---

## 6. 重要規則

- **權限限制**：`POST /api/v1/activity/withdrawlogs` 需要驗證（authenticated）。
- **欄位限制**：
    - `site`, `activityevent`, `account`, `cid` 為寫入 `withdrawlogs_activity` 的必填欄位。
    - `account` 由前端傳入，需人工確認是否有在後端進行與登入 token 一致的校驗。
- **不可修改欄位**：`site`, `activityevent`, `account`, `cid` 為 Partition Key 與 Clustering Key 的一部分，寫入後不可變更。
- **狀態值限制**：寫入時，`status` 由系統硬編碼為 `0`（需人工確認狀態定義，推測為待處理）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未通過驗證 | 回傳 401 Unauthorized |
| 缺少必填欄位 (e.g., `site`, `account`) | 回傳 400 Bad Request |
| `ActivityWithdraw` 模型驗證失敗 | 回傳 400 Bad Request |
| Cassandra 寫入失敗 | 回傳 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| AW-INT-01 | Integration Test | 使用完整且有效的 `ActivityWithdraw` 模型呼叫 API | 回傳 200。成功寫入 `withdrawlogs_activity`。 |
| AW-PERM-01 | Permission Test | 使用未授權的使用者呼叫 API | 回傳 401 Unauthorized。 |
| AW-VAL-01 | Validation Test | 呼叫 API 但 body 缺少必填欄位 | 回傳 400 Bad Request。 |

---

## 9. 高風險區域

- **無 Idempotency 機制**：若前端短時間內因網路問題重複請求，可能會產生多筆重複的提領紀錄。需人工確認商業邏輯是否能接受或需加上冪等性設計。
- **跨服務資料一致性**：`productservice` 不負責實際活動邏輯，若 `activityevent` 或 `cid` 在 `activityservice` 中無效，此處仍可能寫入孤立的提領紀錄。

---

## 10. 常見錯誤

- 新人可能誤以為此 API 僅由後台呼叫，實際上根據 README，此為使用者活動兌換流程的一環。
- AI 可能誤將 `withdrawlogs_activity` 的 `id` 欄位視為需要前端傳入的參數。從 OpenAPI 與 Code Semantics 來看，此 `id` 由後端 `Service` 層自動產生，前端無需提供。
- 常見漏檢查項目：未驗證 `ActivityWithdraw` model 的 `cid` 是否為正整數。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `ActivityController.WithdrawLogs` (POST) |
| DB | `product.withdrawlogs_activity` |
| Code | `ActivityService.WithdrawLogs` |
| Code | `ActivityDataProvider.InsertWithdrawlog` |
| OpenAPI | `POST /api/v1/activity/withdrawlogs` |
| 語意 | `withdrawlogs_activity` fields semantic (status=0) |
| 驗證 | README.md: "需要驗證" 標記 |

---

> **建議人工確認事項**
> - `status` 欄位值 `0` 的正式定義及後續更新流程(route: `/api/v1/activity/withdrawlogs/{site}/{activityEvent}/{account}/{cid}/status`)的權責歸屬。
> - 寫入 `withdrawlogs_activity` 時，是否需同步檢查 `products_activity` 或 `products_activity_redeem_logs` 中的狀態以確保業務正確性。