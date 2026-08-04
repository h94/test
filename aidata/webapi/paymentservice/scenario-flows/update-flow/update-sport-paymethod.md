# 更新體育支付方式

## 1. 場景目的

管理後台透過 `PUT /api/v1/sport/paymethods/{payType}/{mode}` 修改特定體育支付方式的 `enabled` 狀態或多語言名稱 (`names`)，更新 `payment.paymethods_sport` 後立即清除 Redis 快取 `SportCache:SportPayMethods`，確保前台查詢能取得最新設定。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/v1/sport/paymethods/{payType}/{mode}` | 更新單一體育支付方式（需驗證） |

---

## 3. 流程總覽

1. 管理後台發送 PUT 請求，包含 `payType`、`mode` 路徑參數與 request body
2. 驗證管理員權限（ECFramework.ECService）
3. 根據 `payType` 與 `mode` 查詢 `payment.paymethods_sport` 確認記錄存在
4. 更新 `enabled` 狀態（若提供）或 `names` 多語言名稱映射（若提供）
5. 寫入 Cassandra `payment.paymethods_sport`
6. 立即清除 Redis 快取 `SportCache:SportPayMethods`（對應 `DEL` 操作）
7. 回傳更新後的支付方式資料

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SportPayMethodController.Put` | 接收請求、呼叫 Service |
| 2 | Validator | `ECFramework.ECService` | 驗證 JWT Token 與管理員權限 |
| 3 | Service | `SportPayMethodService.Update` | 查詢現有記錄、合併更新欄位 |
| 4 | Provider | `SportPayMethodDataProvider.Update` | 寫入 Cassandra `payment.paymethods_sport` |
| 5 | Provider | `CacheDataProvider.Remove` | 刪除 Redis Key `SportCache:SportPayMethods` |
| 6 | Controller | `SportPayMethodController.Put` | 回傳 200 OK 與更新後物件 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `payment.paymethods_sport` | Read | 確認記錄存在（根據 `paytype` + `mode`） |
| DB | `payment.paymethods_sport` | Update | 寫入 `enabled` 或 `names` 新值 |
| Redis | `SportCache:SportPayMethods` | Delete | 清除支付方式清單快取，確保前台查詢最新資料 |

---

## 6. 重要規則

- **權限限制**：僅管理後台角色可呼叫此 API（需 JWT 驗證，不可為一般會員）。
- **不可更新欄位**：`paytype` 與 `mode` 為 Partition Key / Clustering Key，不可修改。請求路徑中的 `payType`、`mode` 僅用於定位記錄。
- **可更新欄位**：`enabled`（0 停用 / 1 啟用）與 `names`（map<text, text> 多語言名稱）。
- **不可暴露資料**：對外 API 回傳 `names` 時，應僅回傳對應請求語言的值，不可回傳完整 map。
- **快取規則**：更新後**必須**立即清除 Redis `SportCache:SportPayMethods`，不可僅依賴 TTL 過期。此快取 Key 為固定值，用於查詢所有支付方式清單。
- **Transaction 規則**：無跨表 Transaction，僅單一 Cassandra Update + Redis DEL，順序為先寫 DB 後清快取。
- **狀態值限制**：`enabled` 僅可為 0 或 1；`names` 的 key 必須為有效語言代碼（如 `zh-CN`、`en`）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求未帶 JWT Token 或 Token 無效 | 回傳 401 Unauthorized |
| JWT Token 有效但無管理員權限 | 回傳 403 Forbidden |
| 路徑參數 `payType` 或 `mode` 對應的記錄不存在 | 回傳 404 Not Found |
| Request body 包含 `paytype` 或 `mode` 欄位 | 忽略或回傳 400 Bad Request（需人工確認） |
| Cassandra 寫入失敗（timeout / 連線中斷） | 回傳 500 Internal Server Error，快取未清除（DB 狀態與快取不一致） |
| Redis DEL 失敗 | 需人工確認：應記錄錯誤日誌但不影響 API 回傳 200（因 DB 已更新） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-SPM-01 | Integration Test | 傳入合法 `enabled=0` 與 `names` 更新 | DB 記錄更新、Redis 快取被清除、回傳 200 與更新後物件 |
| UT-SPM-02 | API Test | 查詢不存在的 `payType` / `mode` | 回傳 404 |
| UT-SPM-03 | Permission Test | 使用一般會員 Token 呼叫 | 回傳 403 |
| UT-SPM-04 | Flow Test | 更新後立即以 GET 查詢所有支付方式 | 應回傳更新後的 `enabled` 狀態與 `names` |
| UT-SPM-05 | Flow Test | Cassandra 寫入成功但 Redis DEL 失敗 | API 回傳 200，但需有錯誤日誌；下次 GET 可能因快取未失效而讀到舊資料（需人工確認此情境處理策略） |

---

## 9. 高風險區域

- **高風險 API**：此 API 為後台專用，誤開權限可能導致支付方式設定被任意修改。
- **Cache consistency**：Cassandra 寫入成功但 Redis DEL 失敗時，前台 GET 查詢會因命中舊快取而顯示未更新的資料，造成不一致。需監控 Redis 刪除操作的失敗率。
- **No Transaction**：DB 寫入與 Cache 刪除非原子操作，可能產生暫時或永久不一致。需人工確認是否接受此風險或需加入補償機制（如重試 DEL）。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 在 request body 中嘗試傳入 `paytype` 或 `mode` 試圖修改主鍵 → 應忽略或明確拒絕。
  - 忘記更新後清除 Redis 快取 `SportCache:SportPayMethods` → 導致前台無法立即看到變更。
- **AI 容易誤解**：
  - 認為此 API 可建立或刪除支付方式（實際上只有 POST 建立、此 PUT 僅更新）。
  - 誤以為清除的是單一支付方式快取，但實際上是整個支付方式清單快取（影響所有支付方式查詢）。
- **常見漏檢查項目**：
  - 未驗證 `names` 的 key 是否為合法語言代碼。
  - 未驗證 `enabled` 值是否僅為 0 或 1。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | SportPayMethodController.Put (from README API route table) |
| DB | payment.paymethods_sport (from README, paymentservice-detail.md, dbschema, code semantics) |
| Redis | SportCache:SportPayMethods (from paymentservice-detail.md Redis section) |
| Code | SportPayMethodService.Update (inferred from service structure) |
| Code | SportPayMethodDataProvider.Update (from code semantics phase1 batch-2) |
| Code | CacheDataProvider.Remove (from paymentservice-detail.md Redis DEL behavior) |
| Rule (不可更新 PK) | paymethods_sport paytype/mode 不可更新 (from paymentservice-detail.md) |
| Rule (names 回傳限制) | paymentservice-detail.md: "對外 API 應僅回傳對應語言的值" |
| Rule (enabled 僅 0/1) | paymentservice-detail.md: "enabled 僅可由管理後台 API 修改" + code semantics |
| Rule (Cache DEL) | paymentservice-detail.md: "更新方案時主動失效" (for SportPayMethods) |