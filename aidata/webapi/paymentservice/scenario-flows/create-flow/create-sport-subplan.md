# 建立體育訂閱方案

## 1. 場景目的

管理人員透過管理後台建立一筆新的體育訂閱方案，包含方案名稱、價格、有效期間與可用支付方式。寫入 `payment.sport_sub_plans` 表，並同步更新 Redis 快取，確保前台查詢時立即反應最新方案。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/sport/subplans` | 建立體育訂閱方案 |

此路由在 README 中標示為需要驗證。

---

## 3. 流程總覽

1. 管理後端呼叫 API，攜帶 admin token
2. 驗證 token 有效性與操作權限
3. 參數驗證：檢查必填欄位（name, price, duration, pay_methods）格式
4. 驗證 pay_methods 中的支付方式是否存在且為啟用狀態（查 `payment.paymethods_sport` 或快取）
5. 產生方案唯一 id (UUID)
6. 寫入 Cassandra `payment.sport_sub_plans` 表
7. 寫入成功後，更新 Redis 快取：
   - 刪除或重建 `SportCache:SportSubPlans`（全方案清單）
   - 可選：設置 `SportCache:SportSubPlans:{id}` 單一方案快取
8. 回傳新建立的方案資料

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `SportController.CreateSubPlan` | 接收 request，呼叫 Service |
| 2 | Service | `SportSubPlanService.Create` | 驗證權限、組裝資料、呼叫 Provider |
| 3 | Validator | 輸入驗證 | 檢查必填、格式、pay_methods 有效性 |
| 4 | Provider | `SportSubPlanDataProvider.Insert` | 產生 id，寫入 `sport_sub_plans` |
| 5 | Cache | `SetSportPlanCache` | 更新 Redis 快取（`SportCache:SportSubPlans`） |
| 6 | Controller | 回傳 | 將儲存後的方案 DTO 回傳給客戶端 |

> **備註**：Class 與 Method 名稱基於常見命名慣例，未取得實際程式碼，需人工確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `payment.sport_sub_plans` | INSERT | 儲存新建方案 |
| DB (Cassandra) | `payment.paymethods_sport` | SELECT (讀取) | 驗證支付方式存在且啟用 (`enabled=1`) |
| Redis | `SportCache:SportSubPlans` | DEL / SET | 讓全方案快取失效或重建，確保前台取得最新清單 |
| Redis | `SportCache:SportSubPlans:{id}` | SET (可選) | 建立個別方案快取，加速單一查詢 |

無 Queue / Kafka 參與此流程。

---

## 6. 重要規則

- **權限限制**：僅限管理後台 token，非 admin 請求應拒絕（403）。
- **欄位限制**：
  - `id` 由系統產生（UUID），不可由客戶端傳入。
  - `price` 必須為正整數（或符合幣別單位）。
  - `duration` 格式需符合設計（例如天數或日期區間）。
  - `pay_methods` 必須為有效列表，至少一項；每項需對應 `paymethods_sport.paytype/mode` 且 `enabled=1`。
- **不可暴露資料**：回傳時避免洩漏內部 `authkey`、多語言 map 完整結構（依 README 規則）。
- **TTL 規則**：Redis `SportCache:SportSubPlans` 設為永久，但方案異動時主動清除或重建；單一方案快取可設 TTL 或隨全列表一併清除。
- **Transaction 規則**：Cassandra 寫入與 Redis 更新**不在同一個交易**中，應先確保 DB 寫入成功後再更新快取；若 Redis 失敗，不影響主流程，但需記錄錯誤並可依賴後續查詢重建快取。
- **狀態值限制**：方案新建預設視為啟用（`enabled = 1`），除非另有設計；需參考 `sport_sub_plans` schema 確認。
- **不可修改欄位**：方案 id 在建立後永不變更（UUID），後續僅可透過 PUT 更新 name、price 等。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未攜帶有效 admin token | 401 或 403 |
| 缺少必填欄位（如 name） | 400，提示缺失參數 |
| price 非正整數或為 0 | 400，數值無效 |
| pay_methods 中包含不存在的支付方式 | 400，支付方式無效（查無記錄或未啟用） |
| Cassandra 寫入失敗（timeout） | 500，可能觸發重試 |
| Redis 更新失敗 | 後端可記錄警告；API 仍回傳成功（200），因為 DB 已寫入，但前台可能短時間顯示舊資料，後續靠快取失效機制 |
| 重複 id（極低機率） | 寫入失敗，系統應重試或報錯 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| SP01 | API Test | 正常建立，提供有效欄位 | 201，回傳完整方案 JSON |
| SP02 | Permission Test | 無 token 或一般用戶 token | 401/403 |
| SP03 | API Test | 缺少 name | 400，錯誤訊息 |
| SP04 | API Test | price = -10 | 400 |
| SP05 | API Test | pay_methods 包含不存在的 paytype/mode | 400，提示支付方式無效 |
| SP06 | API Test | 連續建立兩次不同方案 | 兩次皆成功，id 不同 |
| SP07 | Flow Test | 建立後立即 GET /api/v1/sport/subplans | 新方案出現在清單中，快取已更新 |
| SP08 | Flow Test | 模擬 Redis 更新失敗 | API 仍回傳成功（若設計如此），檢查日誌含有警告 |

---

## 9. 高風險區域

- **高風險 table**：`payment.sport_sub_plans` — 是前台用戶訂閱時的核心參考；錯誤寫入可能導致無法下單或支付金額錯誤。
- **快取一致性**：DB 寫入成功但 Redis 未更新或不一致，前台用戶可能看不到新方案，需確認清除快取的動作確實執行；建議在 DB 寫入成功後同步更新，若失敗應重試或記錄以供排程修復。
- **支付方式驗證**：若未檢查 `paymethods_sport.enabled`，可能建立包含停用支付方式的方案，造成用戶支付時錯誤。
- **不存在外部相依**：無跨服務同步，風險較低。

---

## 10. 常見錯誤

- ❌ 建立方案後未呼叫 `SetSportPlanCache` 清除 `SportCache:SportSubPlans`，導致前台仍顯示舊方案清單。
- ❌ 直接使用客戶端傳入的 id，可能造成重複或格式錯誤。應由服務端生成 UUID。
- ❌ 未驗證 `pay_methods` 陣列中的值是否存在於 `paymethods_sport` 或未檢查 `enabled`，可能建立無效支付方案。
- ❌ 回傳時將 `pay_methods` 轉換為包含所有語言的多語言 map，違反「不可回傳完整 map」的規則。
- ❌ 誤認為 Redis 快取同步是自動的，忽略手動清除步驟。
- ❌ 在 Redis 更新失敗時仍未記錄日誌，導致無法發現不一致問題。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/v1/sport/subplans` [README - 體育訂閱方案] |
| DB | `payment.sport_sub_plans` [README - 資料庫重要 Table] |
| DB field | `id, name, price, duration, pay_methods` [README table 描述] |
| Redis | `SportCache:SportSubPlans` [paymentservice-detail - Redis] |
| Redis update | `SetSportPlanCache` [paymentservice-detail - Redis 說明] |
| Payment method validation | `paymethods_sport.enabled=1` [paymentservice-detail - 讀取規則] |
| Schema | `payment.sport_sub_plans` 的完整 schema 未在文件提供，需人工確認。 |

> ⚠️ **需人工確認**：
> 1. `payment.sport_sub_plans` 表的詳細 schema（欄位型別、主鍵設計）。
> 2. Redis 快取更新的確切實作（是刪除整個 list 還是 rebuild）。
> 3. 是否允許同名方案建立；`name` 是否有唯一性限制。
> 4. pay_methods 的儲存格式（list<text>、set 或 JSON）。
> 5. 錯誤時 Redis 的重試機制是否存在。

---