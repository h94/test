# 查詢體育訂閱方案

## 1. 場景目的

提供已驗證的前端或後台用戶，查詢平台中可用的體育訂閱方案列表或特定方案細節。主要服務於會員訂閱流程的第一步，讓用戶能根據方案資訊（如價格、天數、支援的支付方式）進行選擇。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sport/subplans` | 查詢所有體育訂閱方案 |
| GET | `/api/v1/sport/subplans/{id}` | 查詢單一體育訂閱方案 |

---

## 3. 流程總覽

1.  API 端點接收到查詢請求。
2. 驗證請求的權限。
3. 嘗試從 Redis 讀取 Key `SportCache:SportSubPlans`。
4. 若 Redis 命中，直接回傳快取資料（查詢單一方案時，會從快取的列表中篩選）。
5. 若 Redis 未命中，則查詢 Cassandra 資料庫中的 `payment.sport_sub_plans` 表。
6. 將資料格式化後回傳給客戶端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SportSubPlanController.Get` | 接收請求，呼叫 Service 層 |
| 2 | Service | `SportSubPlanService.GetAllOrById` | 業務邏輯層，決定查詢全部或單一方案 |
| 3 | Provider | `CacheDataProvider.GetSportPlanCache` | 優先從 Redis `SportCache:SportSubPlans` 讀取 |
| 4 | Provider | `SportSubPlanDataProvider.GetSportSubPlans` | 當 Redis 未命中時，查詢 Cassandra `payment.sport_sub_plans` |
| 5 | Service | `SportSubPlanService.GetAllOrById` | 若查詢單一方案，從結果集中篩選對應 `id` 的資料 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | `SportCache:SportSubPlans` | Read | 快取所有訂閱方案資料，提升讀取效能 |
| DB (Cassandra) | `payment.sport_sub_plans` | Read | 當 Redis 快取不存在或未命中時，作為查詢的來源 |

---

## 6. 重要規則

- **權限限制**：此 API 需要驗證。
- **欄位限制**：回傳的 `names` 應僅回傳對應請求語言的值，不可回傳完整的多語言 map。
- **不可修改欄位**：方案的`id`為主鍵，不可透過 API 修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| Redis 未命中且 Cassandra 查詢失敗 | 回傳 `500 Internal Server Error` |
| 查詢單一方案，但提供的 `id` 不存在 | 回傳 `404 Not Found` 或空結果 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| `S-01` | Integration Test | Redis 未命中時，能否正確查詢 Cassandra 並回傳 | 回傳正確的方案列表 |
| `S-02` | Redis Cache Test | 當 Redis 中有資料時，是否不查詢 Cassandra | Cassandra 無查詢記錄，且能快速回傳 |
| `S-03` | API Test | 查詢一個不存在的 `id` | 回傳 `404` |
| `S-04` | Permission Test | 無效的 Token 呼叫 API | 回傳 `401 Unauthorized` |

---

## 9. 高風險區域

- **Cassandra 單點來源**：當 Redis 不可用時，所有讀取壓力將轉移到 Cassandra `payment.sport_sub_plans` 表。若該表成為瓶頸，會影響查詢效能。
- **Cache data structure**：若快取的 `SportCache:SportSubPlans` 資料結構變更，需確保所有讀取方能相容新舊版本。

---

## 10. 常見錯誤

- ❌ **誤解查詢需要過濾**：`payment.sport_sub_plans` 在管理後台為主要可查詢對象，一般會員查詢雖可能僅需啟用方案，但此處提供的原始資料查詢並無狀態過濾規則。
- ❌ **誤判寫入權限**：一般用戶或管理員查詢方案時，**絕不可**同時夾帶寫入或更新請求到此流程。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README.md: Sports Subscription Plan GET routes |
| DB | `payment.sport_sub_plans` |
| Redis | paymentservice-detail.md: `SportCache:SportSubPlans` |
| Code | `CacheDataProvider`, `SportSubPlanDataProvider` |