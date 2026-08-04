# 更新活動提領狀態

## 1. 場景目的

後台管理或活動相關服務透過此 API 更新某一筆活動提領紀錄（`withdrawlogs_activity`）的狀態。
例如：使用者向客服申請提領後，管理人員審核通過（或拒絕），或系統自動標記提領已完成。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/v1/activity/withdrawlogs/{site}/{activityEvent}/{account}/{cid}/status` | 更新提領紀錄狀態 |

- 所有路徑參數皆為必填（`site`、`activityEvent`、`account`、`cid`）。
- `cid` 為整數，對應活動期別（Cycle ID）。
- Request Body：需包含 `status` 欄位（int），其值定義**需人工確認**（目前推測為 0／1／2，對應「待處理／成功／失敗」）。
- 驗證：需通過 EC Core 驗證（根據 README 中同類 API 皆標示 ✅）。

---

## 3. 流程總覽

1. 接收 PUT 請求，取得路徑參數及 Body 中的新狀態。
2. 驗證呼叫方權限（後台管理或內部服務呼叫）。
3. 以 `(site, activityevent, account, cid)` 查詢 `withdrawlogs_activity` 目前紀錄（DB：Cassandra `product.withdrawlogs_activity`）。
4. 檢查現有狀態是否允許變更（如：已為成功或失敗則不允許再次更新 — **需人工確認**）。
5. 將 `status` 及 `updatetime`（當前時間戳，秒級）寫入該筆紀錄。
6. 回傳成功（200）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `ActivityController.UpdateWithdrawLogStatus`（推測） | 解析路徑參數與 Body，呼叫 Service |
| 2 | Validator | 內建驗證機制（EC Core） | 驗證 Token 合法性、路徑參數格式 |
| 3 | Service | `IActivityService.UpdateWithdrawLogStatus(site, activityEvent, account, cid, newStatus)` | 執行業務邏輯 |
| 4 | Provider | `IActivityDataProvider.UpdateWithdrawLogStatus(...)` | 透過 Cassandra Driver 更新對應鍵的欄位 |
| 5 | Transfer | 若需要，轉換 Request → DB Model | 確保 updatetime 由系統產生，不接受外部傳入 |

> ⚠ 上述 Layer 與 Method 名稱基於產品中其他類似流程（如兌換紀錄狀態更新）推測，**需人工確認實際程式碼**。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `product.withdrawlogs_activity` | Read | 讀取現有提領紀錄，取得當前狀態 |
| DB | Cassandra `product.withdrawlogs_activity` | Update | 更新 `status` 與 `updatetime` 欄位 |

- 此流程未使用 Redis 或 Kafka。
- 無 Queue 發佈。

---

## 6. 重要規則

- **權限限制**：僅後台管理或內部服務可呼叫此 API；一般使用者不可自行變更提領狀態（推測基於 README 中同一群組的 API 皆須驗證）。
- **狀態機限制**（**需人工確認**）：
  - 推測 `status` 可能為 0（待處理）→ 1（成功）或 → 2（失敗）。
  - 一旦設為「成功」(1) 或「失敗」(2) 後，可能不可再次變更（類似 `products_activity_redeem_logs` 規則）。
- **不可修改欄位**：
  - `site`、`activityevent`、`account`、`cid` 為複合主鍵，不可變更。
  - `updatetime` 由系統設定，外部不得傳入或覆蓋。
- **不可暴露欄位**：
  - `account`、`contactnumber` 等個資不應在非後台情境回傳。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 路徑參數缺失或格式錯誤（如 `cid` 非整數） | 400 Bad Request |
| 權限不足（非後台角色） | 403 Forbidden |
| 查無該筆提領紀錄 | 404 Not Found 或對應錯誤響應 |
| 傳入的 `status` 不在允許的值域內 | 400 Bad Request 或自定義業務錯誤 |
| 目前狀態已為「成功」或「失敗」並設定不允許再變更，但收到變更請求 | 409 Conflict 或特定錯誤碼 |
| Cassandra 寫入失敗或逾時 | 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| W-01 | API Test | 正常更新狀態（例如 0→1） | 200，DB 資料已更新 |
| W-02 | Permission Test | 無效 token 呼叫 API | 401 / 403 |
| W-03 | API Test | 使用不在定義範圍內的 status 值 (e.g. 99) | 400 |
| W-04 | Flow Test | 重複對「成功」的記錄更新狀態（若規則禁止） | 409 或業務錯誤 |
| W-05 | DB Consistency Test | 更新後檢查 `updatetime` 欄位是否自動更新 | 符合期望 |

---

## 9. 高風險區域

- **資料一致性**：變更狀態前應讀取最新記錄，確認是否有並行修改（可考慮使用 Cassandra 的 `IF` 條件更新，避免競爭）。**目前實作方式需人工確認**。
- **狀態機保護**：若未強制檢查不可回退的狀態，恐造成業務邏輯混亂（如已發放的提領又退回審核中）。
- **權限控制**：若誤開放給一般使用者，可能出現未授權變更。

---

## 10. 常見錯誤

- ❌ 直接透過 API 更新 `status` 而不檢查目前狀態是否已終結 → ✅ 需在 Service 層強制檢查。
- ❌ 未更新 `updatetime` 或誤用客戶端提供的時間戳 → ✅ `updatetime` 必須由服務端產生。
- ❌ 更新 status 時未帶完整的 Partition Key 條件，可能造成 Cassandra 全表掃描 → ✅ 查詢與更新必須包含 `site`、`activityevent`、`account`、`cid`。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `PUT /api/v1/activity/withdrawlogs/{site}/{activityEvent}/{account}/{cid}/status` – OpenAPI |
| DB Table | `product.withdrawlogs_activity` – product-detail.md, product Schema |
| 狀態定義（推測） | 根據其他類似表（`products_activity_redeem_logs`）推測，**需人工確認** |
| 寫入限制規則 | productservice-detail.md 無明確規範，已標記**需人工確認** |
| 類似實作參考 | `UpdateActivityProductRedeemLogStatus` 方法，可推估類似架構 – product-detail.md |