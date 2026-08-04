# 建立體育支付方式

## 1. 場景目的  
後台管理員在體育競猜平台新增一種支付方式（例如信用卡分期、第三方錢包）。需要指定支付類型（paytype）、模式（mode）與多語言名稱（names）。  

---

## 2. 入口 API  

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/payment/sport/paymethods` | 建立體育支付方式，需要驗證 |

---

## 3. 流程總覽  

1. 後台管理員透過 Web 前端提交 `paytype`、`mode` 及 `names`（多語言名稱）的 payload。  
2. `PriceBackendService`（BFF）驗證使用者登入（ECFramework 統一驗證）。  
3. 將請求轉送至下游 `paymentservice`（透過 REST API）。  
4. `paymentservice` 檢查 `paytype` + `mode` 複合主鍵是否已存在。  
5. 若不存在，寫入 Cassandra `paymethods_sport` 表，`enabled` 預設為 1（啟用）。  
6. 如需清除相關快取（如 `paymethods:enabled:{site}`），由 `paymentservice` 負責。  
7. 回傳成功結果給前臺。  

---

## 4. 程式流程  

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `PaymentController.CreatePaymethod` | 接收 POST，解析 request body，驗證 token |
| 2 | Service（BFF） | `PaymentService`（或 `IPaymentProvider`） | 呼叫下游 `paymentservice` 的 `CreatePaymethod` API |
| 3 | 下游 Service | `paymentservice`（`CreatePaymethod` handler） | 驗證參數、檢查重複、寫入 `paymethods_sport` |
| 4 | Provider（下游） | `PayMethodDataProvider`（推測） | 執行 Cassandra INSERT |

> ⚠️ 實際 BFF 層的類別與方法需人工確認，目前根據常見架構推測。

---

## 5. DB / Cache / Queue 使用  

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB   | `payment.paymethods_sport` | Write (INSERT) | 持久化新支付方式記錄 |
| Cache | `paymethods:enabled:{site}`（推測） | Delete | 寫入後可能需要清除對應站台的快取，避免前臺讀取過期資料。實際由 `paymentservice` 負責。 |
| Queue | – | – | 此流程無使用訊息佇列 |

---

## 6. 重要規則  

- **複合主鍵不可變**：`paytype` 與 `mode` 建立後無法修改，若要廢棄只能將 `enabled` 設為 0（停用）。  
- **enabled 預設值**：建立時由 `paymentservice` 自動設為 1（啟用），請求中不可強制傳入 0（即使傳入也應以服務端邏輯為準）。  
- **多語言名稱**：`names` 為 `map<text, text>`，key 為語言代碼（如 `zh-TW`、`en`），至少需提供一個語言鍵值，不可為空 map。  
- **權限限制**：僅通過後台驗證的管理員才能呼叫此 API。  
- **寫入不可部分成功**：此為單一 INSERT 操作，無 transaction 需求。  
- **重複檢查**：若相同 `paytype` + `mode` 已存在，必須回傳錯誤（409 Conflict）。  

---

## 7. 錯誤情境  

| 情境 | 預期結果 |
|------|----------|
| 未攜帶有效 token 或權限不足 | 401 Unauthorized 或 403 Forbidden |
| 缺少必要欄位（`paytype`、`mode`、`names`） | 400 Bad Request，明確指出缺少欄位 |
| `names` 為空 map | 400 Bad Request，「至少需提供一個語言名稱」 |
| `paytype` 或 `mode` 含有非法字元（如空白） | 400 Bad Request |
| 相同的 `paytype` + `mode` 已存在 | 409 Conflict，「支付方式已存在」 |
| 下游 `paymentservice` 無回應或 timeout | 502 Bad Gateway 或 504 Gateway Timeout |
| 下游服務寫入失敗（Cassandra 錯誤） | 500 Internal Server Error |

---

## 8. 測試重點  

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| PT-01 | API Test | 使用有效 token 建立新支付方式 | 200 OK，資料正確寫入 `paymethods_sport` |
| PT-02 | Permission Test | 無 token 或一般使用者 token 呼叫 | 401 / 403 |
| PT-03 | Flow Test | 建立後查詢 GET `/api/v1/payment/sport/paymethods` | 應能查到剛建立的記錄（`enabled=1`） |
| PT-04 | Integration Test | 重複建立相同 `paytype` + `mode` | 回傳 409 Conflict |
| PT-05 | Validation Test | `names` 為空 `{}` | 400 Bad Request |
| PT-06 | Validation Test | `names` 只有一個語言（如 `zh-TW`） | 200 OK，後續查詢時其他語言 fallback |
| PT-07 | Cache Test | 建立後前臺是否立即看到新支付方式 | 若快取存在，需確認清除機制正常（可能需人工觀察） |

---

## 9. 高風險區域  

- **主鍵（paytype, mode）不可逆**：輸入錯誤的 `paytype` 或 `mode` 會產生一個無法真正刪除的記錄（只能停用），管理介面需有二次確認機制。  
- **services dependency**：BFF 完全依賴 `paymentservice` 可用性，若下游服務暫停，整個功能不可用。  
- **快取一致性**：若前臺有快取 `paymethods:enabled:{site}`，建立後未立刻清除，前臺可能暫時看不到新支付方式；反之若清除失敗，則可能出現不一致。  
- **資料暴露**：`names` map 直接存在 DB 中，BFF 對外回傳時應根據請求語言過濾，避免暴露完整 map（雖然對管理後台可能全部回傳，但仍應注意）。  

---

## 10. 常見錯誤  

- ❌ 前端直接傳 `enabled=0` 企圖建立一個「未啟用」的支付方式 → 後端應無視此參數，強制設為 1。  
- ❌ 認為可以透過 PUT 修改 `paytype` 或 `mode` → 這兩個欄位是 primary key，無法修改，企圖修改會失敗。  
- ❌ 忘記在建立後清除對應快取 → 可能導致前臺新支付方式不顯示（需確認 `paymentservice` 是否已處理）。  
- ❌ `names` 中使用了非標準語言代碼（如 `chinese`）→ 應限制為 ISO 語言代碼，否則多語言切換會失效。  
- ❌ BFF 層做了過多的業務驗證而與下游 `paymentservice` 不一致 → BFF 只應做基本參數檢查，其餘交給下游。  

---

## 11. Evidence  

| 類型 | 來源 |
|------|------|
| API | README.md → 支付管理 `POST /api/v1/payment/sport/paymethods` |
| DB  | `payment.paymethods_sport` schema，主鍵 (paytype, mode)，欄位 enabled, names |
| DB 寫入規則 | `db/payment-detail.md` → paymethods_sport 章節，敘述 enabled 預設 1，paytype/mode 不可更新 |
| 下游服務 | README.md 相依服務列表：`paymentservice` 用途「支付方式、訂閱方案…」 |
| 快取 | `db/payment-detail.md` Redis 段落 → PayMethodsCache: `paymethods:enabled:{site}`，由 newlotterysite（前臺）使用，但寫入後清除的責任需人工確認 |
| 驗證 | README.md → API 表格「需要驗證 ✅」 |
| 狀態定義 | `db/payment-detail.md` → paymethods_sport 的 enabled 值定義：0 停用、1 啟用 |

> ⚠️ **需人工確認**：  
> - BFF 層實際呼叫的 `IPaymentProvider` 方法名稱與參數。  
> - `paymentservice` 建立後是否會主動清除 `paymethods:enabled:{site}` 快取。  
> - 建立 request 是否允許傳入 `enabled` 欄位（依現有規則應忽略）。