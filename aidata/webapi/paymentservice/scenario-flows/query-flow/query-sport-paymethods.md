# 查詢體育支付方式

## 1. 場景目的

提供前台與後台查詢體育支付方式。前台僅顯示啟用中的支付方式，後台可查詢所有狀態（含停用）。流程優先讀取 Redis 快取以降低 DB 負載，並確保權限控制與多語言輸出。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/sport/paymethods` | 查詢所有支付方式（列表） |
| GET | `/api/v1/sport/paymethods/{payType}/{mode}` | 依主鍵查詢單一支付方式 |

均需通過 ECFramework.ECService 驗證。

---

## 3. 流程總覽

1. 接收 GET 請求，驗證使用者 Token。
2. 判斷是否為管理後台請求（依身份或權限標記）。
3. 嘗試讀取 Redis Key `SportCache:SportPayMethods`。
4. 若快取命中，直接取用並過濾（前台：`enabled=1`；後台：全部）。
5. 若快取未命中，查詢 Cassandra `payment.paymethods_sport` 全表。
6. 將查詢結果寫入 Redis `SportCache:SportPayMethods`（無 TTL，靠手動失效）。
7. 根據請求語言自 `names` map 中提取對應單一值，回傳資料。

---

## 4. 程式流程

| 順序 | Layer | Class / Method（推測，需人工確認） | 動作 |
|------|-------|-----------------------------------|------|
| 1 | Controller | `SportPayMethodController` | 接收請求，呼叫 Service |
| 2 | Service | `SportPayMethodService.GetPayMethods()` / `GetPayMethod(payType, mode)` | 判斷後台權限，呼叫 Cache Provider |
| 3 | Provider | `CacheDataProvider.GetSportPayMethodsCache()` | 讀取 Redis `SportCache:SportPayMethods` |
| 4 | Provider | `SportPayMethodDataProvider.GetAllSportPayMethods()` | 快取未命中時查詢 Cassandra |
| 5 | Provider | `CacheDataProvider.SetSportPayMethodsCache(data)` | 寫入 Redis |
| 6 | Service | （同上） | 依後台權限過濾 `enabled`，依語言處理 `names` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Redis | `SportCache:SportPayMethods` | Read | 快取所有支付方式 |
| Redis | `SportCache:SportPayMethods` | Write (SET) | DB 查詢後寫入，永久有效 |
| Redis | `SportCache:SportPayMethods` | Delete (DEL) | 支付方式更新時手動失效 |
| DB (Cassandra) | `payment.paymethods_sport` | Read (SELECT) | 快取未命中時全表查詢 |

無 Kafka/Queue 參與。

---

## 6. 重要規則

- **權限**：前台僅能取得 `enabled=1` 的記錄；後台（管理員）可取得全部。
- **欄位限制**：`paytype`、`mode` 為不可修改主鍵。
- **不可暴露資料**：`names` map 不可全文回傳，僅回傳請求語系對應的單一值。
- **快取 TTL**：無固定 TTL，更新支付方式時必須主動執行 `DEL`。
- **快取一致性**：所有變更 `enabled` 或 `names` 的 API（POST/PUT）都需刪除 `SportCache:SportPayMethods`。
- **單一查詢**：`/{payType}/{mode}` 需精確匹配；不存在時應回傳 404（需確認實作）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未登入或 Token 無效 | 401 Unauthorized |
| 前台用戶呼叫後台 API 或權限不足 | 403 Forbidden |
| Redis 不可用且 DB 查詢失敗 | 500 Internal Server Error |
| `payType`/`mode` 不存在 | 404 Not Found 或空結果 |
| 快取未因更新而失效，讀到舊資料 | 用戶看到過時資訊，需確保管理後台更新時刪除快取 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| QT-001 | API Test | 管理員呼叫 GET `/api/v1/sport/paymethods` | 200，含停用記錄 |
| QT-002 | API Test | 一般用戶呼叫 GET `/api/v1/sport/paymethods` | 200，僅 `enabled=1` |
| QT-003 | API Test | 查詢存在的 `/{payType}/{mode}` | 200，單一記錄 |
| QT-004 | API Test | 查詢不存在的 `/{payType}/{mode}` | 404 |
| QT-005 | Cache Test | 連續兩次請求，第二次命中 Redis | 回應一致且更快 |
| QT-006 | Cache Invalidation | 更新支付方式後立即查詢 | 已反應變更 |
| QT-007 | Permission Test | 未登入請求 | 401 |
| QT-008 | Language | 請求帶 `Accept-Language` | `names` 回傳對應單一語言字串 |

---

## 9. 高風險區域

- **快取一致性**：管理後台更新支付方式後未刪除 `SportCache:SportPayMethods`，將導致前台持續顯示舊狀態。
- **權限繞過**：若 Service 層未正確區分前台/後台，可能暴露停用支付方式給一般用戶。
- **不可回傳 map**：對外 API 若直接序列化 `names` 全部語言，違反個資與設計規範。

---

## 10. 常見錯誤

- ❌ 前台查詢未過濾 `enabled=1`，顯示停用支付方式。
- ❌ 更新 API 未刪除 Redis 快取，導致 stale data。
- ❌ 回傳完整的 `names` map，未依語言轉換。
- ❌ 未處理 Redis 故障 fallback，直接拋出例外。
- ❌ 單一查詢 API 使用全表掃描而非主鍵精確查找。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | README.md - 體育支付方式表格 |
| DB Table | Cassandra `payment.paymethods_sport` 結構，及 paymentservice-detail.md |
| Redis Key | paymentservice-detail.md - Redis 段落：`SportCache:SportPayMethods` |
| 讀取規則 | payment-detail.md - 支付方式清單：前端 `enabled=1`，後台全部 |
| 不可回傳 | payment-detail.md - `paymethods_sport.names` 限制 |
| 驗證框架 | README.md - ECFramework.ECService |
| 具體類別 | 需人工確認（Controller、Service、Provider 類別名稱） |