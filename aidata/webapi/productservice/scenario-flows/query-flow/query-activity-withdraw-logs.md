# 查詢使用者活動提領紀錄

## 1. 場景目的

提供使用者或管理端查詢指定帳號在特定活動事件下的所有提領紀錄，用於追蹤活動獎品發放狀態與歷史。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/activity/withdrawlogs/{site}/{activityEvent}/{account}` | 查詢特定帳號在指定活動的提領歷史 |

---

## 3. 流程總覽

1. 接收 GET 請求，解析路徑參數 `site`、`activityEvent`、`account`
2. 進行身份驗證與權限檢查（需人工確認具體驗證機制）
3. 驗證 `site`、`activityEvent`、`account` 參數不為空
4. 透過 DataProvider 查詢 `withdrawlogs_activity` 表，以 `site`、`activityEvent`、`account` 為條件
5. 將查詢結果轉換為回傳模型
6. 回傳提領紀錄列表（可能為空陣列）

**需人工確認**：具體的 Controller / Service / Provider 方法名稱與實作細節。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `ActivityController.GetWithdrawLogs`（推測） | 接收請求，調用 Service 層 |
| 2 | Service | `ActivityService.GetWithdrawLogs`（推測） | 業務邏輯處理，調用 Provider |
| 3 | Provider | `IActivityDataProvider`（實作類別） | 查詢 `withdrawlogs_activity` 表 |
| 4 | Transfer | `ActivityWithdraw` 模型 | 將資料庫結果映射為回傳物件 |

**需人工確認**：實際的類別與方法名稱。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `product.withdrawlogs_activity` | Read | 查詢指定帳號的提領紀錄 |

**需人工確認**：
- 是否使用 Redis 快取（目前文檔未明確指出）
- 是否有 Kafka / Queue 參與

---

## 6. 重要規則

- **權限限制**：前端僅能查詢自己的 `account` 對應的提領紀錄；後台可查詢全部（需人工確認）。
- **查詢限制**：必須以 `site` + `activityEvent` + `account` 為條件查詢，不可跨 partition 掃描。
- **不可暴露欄位**：`account` 欄位對前端查詢不可回傳（需人工確認是否在此 API 遵循此規則）。
- **狀態值限制**：提領狀態（`status`）的具體定義與流轉規則需人工確認。
- **不可修改欄位**：寫入後的 `site`、`activityevent`、`account`、`cid` 不可變更（僅供查詢，不在此 API 寫入）。
- **欄位限制**：查詢時 `site`、`activityEvent`、`account` 為必填路徑參數，不可為空。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 參數 `site` 為空 | 400 Bad Request |
| 參數 `activityEvent` 為空 | 400 Bad Request |
| 參數 `account` 為空 | 400 Bad Request |
| 使用者查詢他人帳號 | 403 Forbidden 或限制僅回傳自身資料（需人工確認） |
| DB 連接失敗或 timeout | 500 Internal Server Error |
| 查無任何提領紀錄 | 200 OK，但回傳空陣列 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| WDL-01 | API Test | 傳入有效的 `site`、`activityEvent`、登入使用者 `account` | 成功回傳該帳號的提領紀錄列表（可為空陣列） |
| WDL-02 | Permission Test | 一般使用者嘗試查詢其他帳號的提領紀錄 | 403 Forbidden 或僅回傳空（需人工確認） |
| WDL-03 | Flow Test | 先建立提領紀錄（透過 POST），再查詢該紀錄 | 回傳列表包含剛建立的紀錄 |
| WDL-04 | API Test | 傳入不存在的 `site` 或 `activityEvent` | 回傳空陣列 |
| WDL-05 | API Test | 未通過驗證直接呼叫 API | 401 Unauthorized |

---

## 9. 高風險區域

- **高風險 API**：本 API 若無嚴格的權限控制，可能導致使用者提領隱私資料外洩。
- **DB 查詢效能**：若 `withdrawlogs_activity` 分區設計不當或查詢條件不完整，可能導致全表掃描影響效能。
- **隱私資料外洩**：回傳時需確認已排除或遮罩個人敏感資訊（如 `account`）。
- **需人工確認**：`withdrawlogs_activity` 的完整結構與狀態定義。

---

## 10. 常見錯誤

- ❌ 查詢時未以 `site` + `activityEvent` + `account` 為完整條件，導致跨分區掃描。
- ❌ 對外 API 回傳原始資料庫模型，暴露內部欄位（如 `account`）。
- ❌ 未驗證請求者身份，允許查詢任意帳號的提領紀錄。
- ❌ 未處理 `account` 不存在的情境，直接拋出例外而非回傳空陣列。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI `paths./api/v1/activity/withdrawlogs/{site}/{activityEvent}/{account}.get` |
| DB | Table `product.withdrawlogs_activity`（來自 Phase1 sem） |
| Code | 需人工確認對應的 Controller / Service / Provider 實作 |
| SQL | 查詢 `SELECT * FROM product.withdrawlogs_activity WHERE site=? AND activityevent=? AND account=?`（推測） |