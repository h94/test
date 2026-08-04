# 查詢充值方案

## 1. 場景目的

提供所有啟用中且符合當前時間範圍的充值方案清單，供前端用戶瀏覽並選擇欲購買的方案。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | /api/rechargeplans | 查詢所有啟用、未過期的充值方案（需人工確認實際路由） |

---

## 3. 流程總覽

1. Controller 接收查詢請求（無需驗證會員身份，因充值方案為公開資訊）。
2. Service 層調用 Provider 讀取 `rechargeplans_newlottery` 表。
3. Provider 建構 Cassandra 查詢，條件為 `enabled=1` 且 `starttime <= 當前 UTC 時間戳 < endtime`。
4. 將符合條件的方案列表回傳，排除 `lastupdatetime` 欄位。
5. 回傳給前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `RechargePlanController.Get()` | 接收請求，呼叫 Service |
| 2 | Service | `RechargePlanService.GetPlans()` | 呼叫 Provider 取得資料 |
| 3 | Provider | `RechargePlanProvider.GetEnabledPlans(now)` | 對 `payment.rechargeplans_newlottery` 執行 SELECT，過濾 `enabled=1` 與時間範圍 |
| 4 | Provider | – | 將結果映射為 DTO，排除 `lastupdatetime` |
| 5 | Controller | – | 回傳 JSON 清單 |

*註：實際類別名稱需對照原始碼，若不存在請人工確認。*

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `payment.rechargeplans_newlottery` | Read | 讀取符合時間與啟用條件的方案 |
| Cache | Redis（無） | – | 本場景未使用 Redis 快取，直接查詢 DB |

---

## 6. 重要規則

- **權限限制**：此 API 為公開查詢，無需會員驗證。
- **過濾規則**：
  - 必須過濾 `enabled = 1`。
  - 必須過濾 `starttime <= 當前 UTC 時間戳 < endtime`（左閉右開區間）。
- **不可暴露欄位**：`lastupdatetime` 不可回傳給前端。
- **時間格式**：`starttime`、`endtime` 為 bigint（UTC 毫秒），程式需以 UTC 比對，前端顯示時再轉本地時間。
- **無分頁機制**：目前未強制分頁，若方案數量可能過大需注意全表掃描風險，建議未來加入 LIMIT。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 當前無任何啟用方案 | 回傳空陣列 `[]` |
| 資料庫連線失敗 | 回傳 500 系統錯誤 |
| 時間解析錯誤 | 回傳 400 參數錯誤（若允許傳入時間參數） |
| 方案時間設定有誤（starttime > endtime） | 該方案依然會被過濾掉，不回傳 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 在有效時間內存在啟用方案 | 狀態碼 200，清單包含該方案 |
| TC02 | API Test | 所有方案皆已過期 | 狀態碼 200，回傳空清單 |
| TC03 | API Test | 存在方案但 enabled=0 | 該方案不回傳 |
| TC04 | Flow Test | 方案開始時間等於當前時間 | 方案應包含在結果中 |
| TC05 | Flow Test | 方案結束時間等於當前時間 | 方案不應包含（endtime 為 exclusive） |
| TC06 | Permission Test | 未登入狀態存取 | 應允許存取（公開 API） |

---

## 9. 高風險區域

- **時間處理一致性**：伺服器時間不同步可能導致方案比對錯誤，所有時間判斷皆須使用標準 UTC。
- **全表掃描**：`rechargeplans_newlottery` 以 `id` 為主鍵，若未加二級索引則查詢 `enabled=1` 會觸發全表掃描，效能可能隨著方案數量增加而下降。需確認 Cassandra 是否支援此類查詢（通常不建議無 partition key 的掃描），必要時應引入材料化視圖或快取（如 Redis）。
- **跨服務衝突**：雖然 pricecentersite 被標記為 reader/writer 角色，但 db-detail 中有限制「僅 paymentservice 或 productservice 可修改 enabled」，pricecentersite 必須遵守只讀原則，不可誤寫入。

---

## 10. 常見錯誤

- ❌ 只過濾 `enabled=1` 而未檢查時間範圍 → 可能顯示未開始或已過期的方案。
- ❌ 時間判斷用本地時間而非 UTC → 跨時區錯誤。
- ❌ 回傳 `lastupdatetime` 欄位 → 違反不可回傳規則。
- ❌ 對前端暴露方案原始 `starttime` 與 `endtime` bigint，未提供前端可讀格式（雖非禁止，但建議顯示前端友好的日期字串）。
- ❌ 誤解 pricecentersite 角色而嘗試寫入方案狀態 → 嚴格禁止。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 讀取規則 | [db/payment-detail.md](#) 中 `rechargeplans_newlottery` 讀取規則：「pricecentersite SELECT enabled AND 當前時間在 [starttime, endtime)」 |
| 不可回傳欄位 | 同上文件 `不可回傳欄位`：`lastupdatetime` |
| 時間型別 | 欄位定義 `starttime bigint`, `endtime bigint` 為 UTC 毫秒時間戳 |
| 服務角色 | [pricecentersite-detail.md](#) 中 `payment` 章節：pricecentersite 為 reader |
| 入口 API | OpenAPI 截圖中未明確列出，需人工確認實際路由 |