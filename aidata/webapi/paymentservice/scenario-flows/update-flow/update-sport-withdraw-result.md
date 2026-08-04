# 更新體育提現結果

## 1. 場景目的
財務人員審核會員提現申請後，透過此 API 將提現記錄標記為「成功」或「失敗」，完成提現流程。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/v1/sport/withdrawlogs/{account}/{dateTime}/result` | 更新指定帳號、時間的提現記錄狀態 |

---

## 3. 流程總覽

1. 後台財務人員攜帶驗證 Token 呼叫 API。
2. 驗證 Token 有效性與操作權限（需財務角色）。
3. 根據路徑參數 `account`、`dateTime` 查詢 `payment.sport_withdraw_logs` 中的對應提現記錄。
4. 檢查記錄是否存在；若不存在，回傳 404。
5. 檢查記錄當前狀態（必須為待審核 `status=0`）。若已是最終狀態（成功/失敗），拒絕變更。
6. 更新記錄的 `status` 為請求中的目標值（成功或失敗），並寫入 `updatetime`。
7. （需人工確認）是否觸發其他操作，如透過 `mq` 發送通知信、呼叫 `memberservice` 更新餘額等。
8. 回傳成功結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SportWithdrawController.PutResult`（推斷） | 接收請求，驗證 Token，呼叫 Service |
| 2 | Service | `SportWithdrawService.UpdateWithdrawResult`（推斷） | 呼叫 DataProvider 取得記錄，執行狀態檢查與更新 |
| 3 | Provider | `SportWithdrawDataProvider.GetWithdrawLog / UpdateWithdrawLog`（推斷） | 讀取 `payment.sport_withdraw_logs`，執行 UPDATE |
| 4 | Validator | （可能無獨立 Validator，規則寫在 Service） | 檢查狀態值是否合法 |
| 5 | Transfer | 無 | 無跨服務轉換 |

> **需人工確認**：實際類別名稱、方法名稱可能不同，需檢視原始碼（phase2）。目前根據命名慣例推斷。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `payment.sport_withdraw_logs` | Read / Update | 查詢特定提現記錄，更新狀態與時間 |
| Redis | 無 | - | 此流程未使用快取 |
| Kafka | （需人工確認） | 可能 Publish | 記錄操作日誌（kafka+cassandra 日誌機制） |
| Queue | `mq`（需人工確認） | 可能 Publish | 發送提現結果通知信給用戶 |

---

## 6. 重要規則

- **權限限制**：僅限財務後台人員操作，需通過驗證並持有對應角色。
- **狀態流轉限制**：
  - `status` 初始值為 `0`（待審核）。
  - 僅允許將 `status` 從 `0` 更新為 `1`（成功）或 `2`（失敗）。
  - 已為 `1` 或 `2` 的記錄不可再變更。
  - **違反此規則將回傳錯誤**（如「該筆記錄已審核完成」）。
- **不可修改欄位**：`account`、`date_time` 等主鍵不可透過此 API 更新。
- **欄位驗證**：`status` 必須為有效的整數（如 `1` 或 `2`），不接受其他值。
- **時間戳**：`updatetime` 由系統自動設定為當前時間，不可由請求方指定。
- **Transaction 規則**：單一記錄更新，無跨表事務需求。但若有後續操作（如通知），建議記錄髮送狀態或使用最終一致性。
- **非同步**：若需要發送通知，更新狀態與訊息發送之間應使用 Queue 保證可靠性，避免同步調用增加延遲。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 提供的 `account` / `dateTime` 找不到對應的提現記錄 | HTTP 404，訊息「提現記錄不存在」 |
| 記錄目前的 `status` ≠ `0`（已審核） | HTTP 400，訊息「該筆已審核，不可重複操作」 |
| 請求中的 `status` 非法（非 `1` 或 `2`） | HTTP 400，說明狀態值必須為 1 或 2 |
| 未通過驗證或權限不足 | HTTP 401 或 403 |
| DB 連線失敗、寫入超時 | HTTP 500，系統錯誤 |
| 更新成功後發送通知失敗 | 記錄 Log 並觸發重試機制（若使用 Queue），不影響主流程 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | API Test | 正常審核通過（status=1） | 200 OK，DB 中 status 變為 1，updatetime 更新 |
| TC02 | API Test | 正常審核拒絕（status=2） | 200 OK，DB 中 status 變為 2 |
| TC03 | Flow Test | 對不存在的記錄操作 | 404 Not Found |
| TC04 | Flow Test | 對已審核（status=1）的記錄再次更新 | 400 Bad Request（不可重複審核） |
| TC05 | Permission Test | 使用一般會員 Token 呼叫 | 403 Forbidden |
| TC06 | Permission Test | 使用未授權後台角色 Token 呼叫 | 403 Forbidden |
| TC07 | Validation Test | 傳入 status=3（非法值） | 400 Bad Request |
| TC08 | Integration Test | 成功審核後檢查通知隊列（若有） | 訊息進入 `mq` 或日誌記錄 |

---

## 9. 高風險區域

- **高風險 Table**：`payment.sport_withdraw_logs`，狀態欄位若被錯誤覆寫可能導致重複出金或漏出金。
- **高風險 API**：本 API 直接影響財務結果，需要嚴格的記錄與審計日誌。
- **狀態機保護**：務必在 Service 層檢查當前狀態，不可僅依賴前端不允許；防止透過併發或重放攻擊繞過狀態檢查。
- **Cache consistency**：此流程未使用 Redis，無快取一致性問題。
- **跨服務資料同步**：若實際提現出金需變更 `gameusers_wallet`（sport keyspace）餘額（根據 README 場景可能由其他流程處理），則需確保狀態更新與餘額扣減的最終一致性。**需人工確認**：本服務是否負責更新錢包？目前資料未說明，高風險區域需待確認。
- **Queue retry**：若後續通知透過 MQ 發送，需保證至少一次送達，避免用戶未收到結果。
- **Idempotency**：API 本身非冪等（每次呼叫會改變狀態），但透過狀態檢查實現部分冪等（若狀態已是目標值，可回傳成功）。建議實作時檢查目標值是否與當前相同，避免報錯。

---

## 10. 常見錯誤

- ❌ **直接將 status 設為 1（成功）且未檢查原始狀態為 0** → 應用程式務必檢查原始狀態，防止已拒絕的申請被誤改為成功。
- ❌ **忘記更新 updatetime** → 影響審計與排序，程式在 UPDATE 時應自動設定當前時間。
- ❌ **API 回傳中包含了不必要的金融敏感資訊**（如提現金額、手續費明細）→ 僅回傳必要狀態。
- ❌ **審核成功或失敗後未發送通知給用戶** → 若規範要求，需確保通知邏輯被觸發，不可遺漏。
- ❌ **重複點擊或併發請求繞過狀態檢查** → 必須在 DB 層級進行樂觀鎖或使用 Cassandra 的 IF NOT EXISTS 條件（LWT）防止 race condition。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由 | README「對外 API 重點」表格 |
| DB Table 用途 | README「資料庫重要 Table」提到 `payment.sport_withdraw_logs` |
| 初始狀態限制 | README「常見錯誤」：提領申請初始 status=0(待審核) |
| 狀態更新限制 | payment-detail.md 中類似 table 的規則（活動兌換等）推斷，需人工確認本表具體規則 |
| 權限驗證 | README 所有 API 標示「需要驗證 ✅」 |
| 服務相依 | README「服務相依」：mq 用於發送付款成功通知；memberservice 驗證身份。提現通知需人工確認 |
| Controller / Service 推斷 | 基於命名慣例及 payment-detail.md 中的 DataProvider 命名方式，需 code evidence 確認 |

> **建議新增**：若本 API 涉及錢包操作（如拒絕後退回預扣金額），應在文件中明確流程，並補充對應的 Rule 及測試案例。目前資訊不足，標記「需人工確認」。