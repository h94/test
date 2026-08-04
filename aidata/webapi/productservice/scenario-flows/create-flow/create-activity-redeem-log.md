# 建立活動商品兌換紀錄

## 1. 場景目的

使用者參與活動並兌換活動商品時，呼叫此 API 寫入一筆兌換紀錄，狀態預設為「審核中(0)」，供後續管理員審核或系統批次處理。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/activity/productredeemlogs` | 建立活動商品兌換紀錄 |

---

## 3. 流程總覽

1. 接收請求，由 ECCore 驗證使用者身分（需登入）
2. Controller 綁定 `ActivityProductRedeemLog` 模型
3. Service 層組裝寫入資料：
   - `id`：系統自動產生（UUID）
   - `status`：固定寫入 `0`（審核中）
   - `addtime` / `updatetime`：系統寫入當前 Unix 秒
   - `account`：由驗證機制注入，前端不可自行指定
4. Provider 層將資料 INSERT 至 `products_activity_redeem_logs`（Cassandra）
5. 回傳成功（HTTP 200）
6. **注意**：本服務不負責扣減 `products_activity.quantity`，此邏輯由活動或支付服務處理

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `ActivityController.PostProductRedeemLog`（推測路徑） | 接收並驗證 Request body |
| 2 | Service | `ActivityService.CreateProductRedeemLog`（推測） | 組裝 `ProductsActivityRedeemLog` 物件，設定 `id`、`account`、`status=0`、時間戳 |
| 3 | Provider | `ActivityDataProvider.InsertActivityProductRedeemLog`（推測） | 對 `products_activity_redeem_logs` 執行 INSERT，寫入所有 Partition Key 與 Clustering 欄位 |

> **需人工確認**：因無確切程式碼，上述 Class/Method 名稱基於專案慣例與 OpenAPI tag 推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.products_activity_redeem_logs` 或 `product.products_activity_redeem_logs` | INSERT | 寫入兌換紀錄 |
| DB | `payment.products_activity` 或 `product.products_activity` | READ（非強制） | 驗證商品存在與狀態（可選，若實作驗證） |
| Redis | 無 | - | 此場景不使用 Redis 快取 |
| Queue | 無 | - | 此場景不使用 Message Queue |

---

## 6. 重要規則

- **權限限制**：API 需要 ECCore 驗證，僅登入使用者可呼叫；`account` 必須與登入身分一致
- **不可暴露資料**：回傳時不可包含 `account` 欄位；`id` 為內部主鍵，前端不應暴露（若有回傳需改用替代標識）
- **寫入限制**：`status` 初始值固定為 `0`（審核中）；後續僅可透過 `UpdateActivityProductRedeemLogStatus` 變更，且成功(1)後不可再改
- **不可修改欄位**：`account`、`pid`、`site`、`activityevent` 為 Partition/Clustering Key，寫入後不可變更
- **Transaction 規則**：Cassandra 不支援跨表交易，此步驟為單一 INSERT
- **Retry 規則**：若 INSERT 失敗，呼叫方可依狀況重試；Cassandra upsert 特性使重複寫入可能覆蓋舊記錄，但若使用 TTL 或狀態檢查需額外邏輯
- **狀態值限制**：`status` 僅可為 `0`（審核）、`1`（成功）、`2`（失敗）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未帶驗證 Token 或 Token 無效 | 回傳 401 Unauthorized |
| Request body 缺少必填欄位（site, activityevent, pid） | 回傳 400 Bad Request，須提示缺漏欄位 |
| Cassandra INSERT 失敗（Timeout/Unavailable） | 回傳 500 Internal Server Error，呼叫方應實作重試 |
| 同一 `site + activityevent + account + id + pid` 重複寫入 | Cassandra 會覆蓋（upsert），若 id 為 UUID 則重複機率極低；若需防止需在應用層檢查 |
| `account` 由客戶端指定（非由 token 注入） | 服務端需強制覆寫為登入身分或拒絕請求，避免偽造 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| APRL-C01 | API Test | 帶有效 Token，提供完整 body（site, activityevent, pid） | 200 OK，DB 寫入 status=0 |
| APRL-C02 | Permission Test | 不帶 Token 或 Token 過期 | 401 Unauthorized |
| APRL-C03 | API Test | 缺少必填欄位（如 pid） | 400 Bad Request |
| APRL-C04 | Flow Test | Cassandra 無法連線 | 500 Internal Server Error |
| APRL-C05 | Integration Test | 寫入後查詢 GET `/api/v1/activity/productredeemlogs/{site}/{activityEvent}/{account}` | 可查得該筆 status=0 紀錄 |
| APRL-C06 | Permission Test | 請求 body 中 account 非登入者 | 服務端須以登入身分覆蓋，回傳 200 且寫入正確 account 或直接 403 |

---

## 9. 高風險區域

- **高風險 table**：`products_activity_redeem_logs` — 若 `account` 寫入錯誤，將導致使用者無法查詢自身紀錄，且 partition key 寫入後無法修改
- **Transaction**：若有扣減庫存需求，需由呼叫方或排程處理，本 API 僅寫入 log，不保證庫存一致性
- **Idempotency**：Cassandra upsert 特性使重送可能覆蓋，若實作需檢查重複兌換（如同一 pid 同一 account 短時間內多筆），應由應用層加防重機制
- **Cache consistency**：此場景不操作快取，但若後續活動商品查詢使用快取，需注意狀態變更時失效

---

## 10. 常見錯誤

- ❌ 前端在 body 中自行傳入 `status` 非 0 → ✅ 服務端必須強制寫入 0，忽略前端傳入值
- ❌ 前端傳入自訂 `id` → ✅ 服務端必須自動產生 UUID，忽略或覆蓋前端傳入值
- ❌ 查詢兌換記錄時未依 `account` 過濾 → ✅ 查詢時必須帶入 `site + activityevent + account`
- ❌ 直接對兌換記錄執行 DELETE → ✅ 應透過更新 status 為失敗來軟刪除，保留歷史
- ❌ 回傳時將 `account` 欄位直接暴露給前端 → ✅ 回傳時必須排除此欄位

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI: `POST /api/v1/activity/productredeemlogs` |
| DB | `payment.products_activity_redeem_logs` / `product.products_activity_redeem_logs` |
| Code | `IActivityDataProvider.UpdateActivityProductRedeemLogStatus` |
| 寫入限制 | product-detail.md: `status` 僅由 `UpdateActivityProductRedeemLogStatus` 更新，值 0/1/2 |
| 預設狀態 | product-detail.md: INSERT status=0 (審核中) |
| 不可回傳欄位 | product-detail.md: `account` 對前端查詢不可回傳 |
| 權限 | README: 需要驗證 ✅ |
| 模型 | OpenAPI: `ActivityProductRedeemLog` schema（site, activityevent, account, id, pid, addtime, status, updatetime） |