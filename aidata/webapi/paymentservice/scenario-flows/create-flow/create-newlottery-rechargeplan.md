# 建立新彩票儲值方案

## 1. 場景目的
管理後台人員透過 API 新增一筆新彩票儲值方案至 `payment.rechargeplans_newlottery`，供前端使用者查詢並發起儲值。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/newlottery/rechargeplans` | 建立新彩票儲值方案 |

> **需人工確認**: OpenAPI 規格中未能找到 `POST /api/v1/newlottery/rechargeplans` 的定義，但 README 已明確列出此路由並標記為需要驗證。

---

## 3. 流程總覽

1. 管理後台發送 POST 請求
2. 驗證操作員權限 (依據 `ECFramework.ECService`)
3. 驗證請求參數（含方案 ID、金額、幣別、有效時間等）
4. 寫入 `payment.rechargeplans_newlottery` 表，預設 `enabled=1`
5. 回傳建立成功的方案資訊

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `NewLotteryRechargePlanController.Post` | 接收請求，呼叫 Service |
| 2 | Service | `NewLotteryRechargePlanService.Create` | 驗證參數，呼叫 Provider |
| 3 | Provider | `NewLotteryRechargePlanDataProvider.Insert` | 寫入 Cassandra |
| 4 | Transfer | `NewLotteryRechargePlanTransfer` | 物件轉換（API Model ↔ DB Model） |

> **需人工確認**: 無 code evidence 可定位確切類別名稱，以上為基於命名慣例推測的架構層級。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `payment.rechargeplans_newlottery` | Write (INSERT) | 新增一筆儲值方案記錄 |
| Redis | `rechargeplans:all:{site}` | 無直接操作 | 建立後不主動更新快取；下次查詢時自動讀取 DB。（來自 `payment-detail.md` 規範） |
| Queue | 無 | 無 | 此流程未使用 Queue |

---

## 6. 重要規則

- **權限限制**: 需要驗證，僅管理後台可操作此 API。
- **欄位限制**:
  - `id` (方案識別碼) 為 Partition Key，建立後不可修改。
  - `amount`, `coin`, `currency`, `enabled`, `starttime`, `endtime` 僅由方案管理後台設定。
  - `enabled` 預設為 `1`（啟用）。
- **時間範圍**: 必須提供有效的 `starttime` 與 `endtime`，開始時間不得晚於結束時間。
- **跨服務寫入限制**: 只有 `paymentservice` 或 `productservice` 可修改 `rechargeplans_newlottery` 的資料；`newlotterysite` 僅唯讀。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未通過驗證（無效或過期 token） | 回傳 HTTP 401 Unauthorized |
| 權限不足（非管理後台角色） | 回傳 HTTP 403 Forbidden |
| 請求缺少必要欄位（如 `id`, `amount`） | 回傳 HTTP 400 Bad Request，並指出缺失欄位 |
| 方案 `id` 已存在 | 回傳 HTTP 409 Conflict |
| `starttime` 晚於 `endtime` | 回傳 HTTP 400 Bad Request |
| Cassandra 寫入失敗或逾時 | 回傳 HTTP 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| UT-01 | API Test | 使用有效參數建立方案 | HTTP 200, 回傳方案資料，DB 中 `enabled=1` |
| UT-02 | Permission Test | 使用一般用戶 token 呼叫 | HTTP 403 |
| UT-03 | Validation Test | 缺少 `amount` 欄位 | HTTP 400 |
| UT-04 | Validation Test | `starttime` > `endtime` | HTTP 400 |
| UT-05 | Flow Test | 建立後立即呼叫 GET API 查詢（若有效期內） | 新方案應出現在列表中 |
| UT-06 | Data Integrity Test | 建立後嘗試以 PUT 修改 `id` | 應失敗或 `id` 保持不變 |

---

## 9. 高風險區域

- **高風險資料表**: `payment.rechargeplans_newlottery`，因為 `id` (主鍵) 不可修改，錯誤的設定可能導致需要刪除整筆記錄。
- **Cache consistency**: 建立新方案後，`newlotterysite` 或其他服務的快取（Key: `rechargeplans:all:{site}`）不會被主動失效（依規範），可能導致前台查詢暫時看不到新方案，直到 TTL 過期。
- **參數驗證不足**: 若未嚴格檢查 `starttime`/`endtime` 的有效性，可能建立出已過期或永遠不會啟用的方案。

---

## 10. 常見錯誤

- **新人容易犯錯**: 未先確認 `id` 的唯一性就直接建立，導致衝突。
- **AI 容易誤解**: 誤以為此場景需要操作 Redis 快取或發送 Queue 訊息，但實際上規範中沒有此要求。
- **常見漏檢查項目**: 漏掉對 `starttime` 和 `endtime` 的邏輯校驗，或未檢查管理員權限。
- **常見錯誤流程**: 在建立時手動指定 `lastupdatetime`，此欄位應由系統自動產生。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md：`POST /api/v1/newlottery/rechargeplans` |
| DB Table | `db/payment.md` |
| DB Rules | `paymentservice-detail.md`：`rechargeplans_newlottery` 欄位規則 |
| Auth | README.md：此 API 標記為需要驗證 |
| Flow | `paymentservice-detail.md`：`id` 不可修改、`enabled` 僅管理後台可設定 |