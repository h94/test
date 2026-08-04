# 設定商家進行中賽事

## 1. 場景目的
營運管理員透過後台為特定商家設定目前正在進行的賽事（In‑Play Games）。系統將更新該商家的 `inplaycount` 及相關進行中站台設定，確保商家即時取得正確的滾球賽事數量與對應站台資訊。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/businesses/{businessCode}/inplaygames` | 設定指定商家的進行中賽事，需驗證 |

---

## 3. 流程總覽

1. 接收 HTTP POST 請求（內含 `businessCode` 路徑參數與 JSON Body）。
2. 驗證呼叫方的身份與授權（可能使用 `gamesettings.businesses.authtoken` 或 `gm.teams.AuthToken`）。
3. 檢查 `businessCode` 是否存在於 `gamesettings.businesses` 表。
4. 解析請求內容，計算 `inplaycount` 應遞增或遞減的變動量（不允許客戶端直接指定最終值）。
5. 更新 `gamesettings.businesses` 表中對應商家的 `inplaycount` 與 `subinprogresssites`（如有變更）。
6. 更新 `updatetime` 時間戳。
7. 回傳成功回應（HTTP 200）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `BusinessController.SetBusinessInplayGame` | 接收 request，讀取 `businessCode`，進行授權驗證（需人工確認實體類別名稱） |
| 2 | Service | `IBusinessService.SetBusinessInplayGame` | 接收 DTO，負責業務邏輯與 DB 操作 |
| 3 | Provider | `BusinessProvider`（需人工確認） | 讀取 `businesses` 表單一資料，計算增量，寫入更新 |
| 4 | Validator | （若有） | 驗證 request body 格式與必要欄位（需人工確認） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `gamesettings.businesses` | Read | 取得目前 `inplaycount`、`subinprogresssites` 及訂閱狀態 |
| DB | `gamesettings.businesses` | Write / Update | 寫入新的 `inplaycount`、`subinprogresssites` 及 `updatetime` |
| Cache | Redis（BusinessCache） | 無直接操作 | 本服務未直接使用 Redis，所有查詢走 Cassandra（需人工確認事後是否需由 syncservice 失效快取） |
| Queue | Kafka | 無 | 此流程無 Queue 參與 |

---

## 6. 重要規則

- **inplaycount 不可由客戶端直接設定**：客戶端傳入的請求必須經過 Service 邏輯處理，不得將 body 中的數值直接寫入 DB；僅能透過 `SetBusinessInplayGame` 方法遞增或遞減。
- **權限限制**：呼叫端需具備有效的 `authtoken` 或團隊授權（`gm.teams.Enabled=1` 且白名單驗證通過）。具體驗證方式需人工確認。
- **不可回傳敏感欄位**：API 回傳不得包含 `authtoken` 或 `business_accounts.password`。
- **inplaycount 下限**：應確保遞減後不小於 0（需人工確認程式內檢查邏輯）。
- **訂閱狀態檢查**：更新前需確認 `subenddate` 未過期（格式 `YYYY-MM-DD`），否則拒絕新增。
- **更新者記錄**：目前 `businesses` 表無 `updater` 欄位，操作者記錄可能寫入 `logs_business` 或 `action_logs`（需人工確認）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `businessCode` 不存在 | 回傳 404 或對應錯誤碼 |
| 權限不足（無效 token） | 回傳 401 / 403 |
| 請求 body 格式錯誤 | 回傳 400 並附帶驗證失敗訊息 |
| `inplaycount` 遞減後為負數 | 拒絕操作，回傳 422 或業務錯誤碼 |
| 商家訂閱已過期 (`subenddate < today`) | 拒絕操作，回傳業務錯誤碼（可能 409） |
| Cassandra 寫入失敗 | 回傳 500，可能觸發重試機制（需人工確認） |
| 同時併發更新導致計數錯亂 | 依賴 Cassandra 的 LWT 或樂觀鎖（需人工確認如何處理） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| IP-01 | API Test | 正常新增進行中賽事，`inplaycount` 由 5 增加為 8 | 200 OK，DB 中 `inplaycount` 更新為 8，`updatetime` 異動 |
| IP-02 | API Test | 移除部分賽事，`inplaycount` 由 8 減少為 6 | 200 OK，DB 中 `inplaycount` 更新為 6 |
| IP-03 | Permission Test | 使用無效 token 呼叫 API | 401 或 403 |
| IP-04 | Flow Test | 對不存在的 `businessCode` 呼叫 | 404 |
| IP-05 | Flow Test | 要求遞減至負數（如目前為 1，要求減少 2） | 拒絕，DB 資料不變 |
| IP-06 | Flow Test | 商家訂閱已過期時要求新增 | 拒絕，回傳適當錯誤 |

---

## 9. 高風險區域

- **高風險 Table**：`gamesettings.businesses` — 直接影響商家功能與賽事派送，錯誤更新可能導致前端顯示異常。
- **高風險 API**：本 API 是唯一修改 `inplaycount` 的入口，若邏輯出錯將直接破壞資料一致性。
- **Cache consistency**：若 syncservice 管理的 Redis 快取 `gamesettings:company:*` 未被主動失效，可能導致前端讀取舊數據（需人工確認快取清除機制是否包含此場景）。
- **Transaction**：需確保 `inplaycount` 的讀取與更新為原子操作，避免 concurrent updates 造成計數錯誤；Cassandra 的輕量級事務（IF 子句）可能被使用（需人工確認）。

---

## 10. 常見錯誤

- ❌ 直接在 request body 中傳入最終 `inplaycount` 值，繞過 Service 遞增/遞減邏輯。
- ❌ 更新 `subinprogresssites` 時直接覆蓋整個 map，遺漏未傳入的站台資料（若使用全量覆蓋）。
- ❌ 忘記檢查商家訂閱是否過期，導致已到期商家仍可設定進行中賽事。
- ❌ 未在 `inplaycount` 變更後觸發下游通知或快取失效，使 frontend 無法即時反映最新數量。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/businesses/{businessCode}/inplaygames` (OpenAPI) |
| DB 寫入限制 | gamesettings-detail.md：「inplaycount（businesses）：僅 SetBusinessInplayGame 可遞增或遞減；客戶端不可直接設定。」 |
| Service 方法 | `IBusinessService - SetBusinessInplayGame` (source code semantics) |
| 欄位定義 | Schema: `gamesettings.businesses.inplaycount` (type int) |
| 授權機制 | 需人工確認（可能參考 `gm.teams` 或 `authtoken`） |
| 訂閱檢查 | `subenddate` 必須大於等於今日（推論自 business-detail.md 跨服務限制） |