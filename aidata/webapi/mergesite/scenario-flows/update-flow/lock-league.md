# 鎖定／解鎖聯盟

## 1. 場景目的

管理員可透過管理後台鎖定特定聯盟，防止自動比對或合併操作變更該聯盟的資料；亦可解鎖以恢復自動化處理。此為維護資料一致性的保護機制。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/leagues/{gameType}/{lid}/locked` | 鎖定或解鎖指定聯盟 |

- **gameType**：球種代碼（路徑參數，必填）
- **lid**：聯盟 ID（路徑參數，必填）
- **需要驗證**：是（ECCore 內建機制）

---

## 3. 流程總覽

1. 接收 PUT 請求，含 `gameType` 與 `lid`
2. 通過 ECCore 驗證（需具備管理員權限）
3. 呼叫 `PriceCenterService` 的鎖定 API
4. PriceCenterService 更新該聯盟的鎖定狀態
5. 回傳操作結果（ServiceMsgCode）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `GameController.LockLeague` | 接收 `gameType`、`lid`，呼叫 Service |
| 2 | Service | `LeagueService.LockLeague` | 呼叫 PriceCenterService 遠端 API |
| 3 | Provider | `PriceCenterProvider` | 透過 HTTP Gateway 呼叫 PriceCenterService |
| 4 | 外部 | `PriceCenterService` | 更新聯盟鎖定狀態，回傳結果 |
| 5 | Controller | `GameController` | 回傳 `ServiceMsgCode` 給客戶端 |

> **需人工確認**：確切的 Controller / Service / Method 名稱需從 source code 確認（OpenAPI tag 為 `Game`，但無明確 class 名稱）

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| 外部 API | PriceCenterService（192.168.55.60） | Update | 更新聯盟鎖定狀態 |
| Kafka | 192.168.55.60 | Publish | 操作日誌寫入（應用程式 Log） |

> **需人工確認**：PriceCenterService 內部是否使用 DB 或 Cache 儲存鎖定狀態；本服務不直接操作 DB

---

## 6. 重要規則

- **權限限制**：僅具備管理員權限的帳號可執行（需通過 ECCore 驗證）
- **狀態值限制**：鎖定／解鎖為二元操作（locked / unlocked），不可設定其他狀態
- **不可修改欄位**：`gameType` 與 `lid` 為路徑參數，不可透過 request body 修改
- **Transaction 規則**：本服務無直接 DB 操作，不涉及 Transaction；鎖定操作為單一遠端呼叫
- **Retry 規則**：若 PriceCenterService 呼叫失敗，需提示使用者重試（不回自動 retry）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未通過驗證（無效 token） | 回傳 401 Unauthorized |
| 權限不足（非管理員） | 回傳 403 Forbidden |
| `gameType` 不存在 | 回傳 400 Bad Request（或 404） |
| `lid` 不存在 | PriceCenterService 回傳錯誤，前端顯示「聯盟不存在」 |
| 聯盟已鎖定，再次鎖定 | 應回傳成功（Idempotent），或提示「聯盟已鎖定」 |
| 聯盟已解鎖，再次解鎖 | 應回傳成功（Idempotent），或提示「聯盟已解鎖」 |
| PriceCenterService 無回應 | 回傳 502 Bad Gateway 或 504 Gateway Timeout |
| PriceCenterService 回傳內部錯誤 | 回傳 500 Internal Server Error，前端提示「操作失敗，請稍後再試」 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| T01 | Permission Test | 無 token 呼叫 API | 401 Unauthorized |
| T02 | Permission Test | 一般使用者 token 呼叫 API | 403 Forbidden |
| T03 | API Test | 管理員 token，傳入有效 `gameType` 與 `lid`，鎖定聯盟 | 200 OK，聯盟狀態變為 locked |
| T04 | API Test | 管理員 token，傳入有效 `gameType` 與 `lid`，解鎖聯盟 | 200 OK，聯盟狀態變為 unlocked |
| T05 | API Test | 管理員 token，傳入不存在的 `gameType` | 400 或 404 |
| T06 | API Test | 管理員 token，傳入不存在的 `lid` | 400 或 404（由 PriceCenterService 決定） |
| T07 | Flow Test | 鎖定後，嘗試對該聯盟執行自動比對或合併 | 應被拒絕或跳過 |
| T08 | Flow Test | 解鎖後，自動比對或合併恢復正常 | 操作成功 |

---

## 9. 高風險區域

- **高風險 API**：`PUT /api/leagues/{gameType}/{lid}/locked`（影響自動化流程）
- **跨服務資料同步**：鎖定狀態儲存於 PriceCenterService，若該服務異常，所有依賴聯盟狀態的操作皆受影響
- **Cache consistency**：若 PriceCenterService 使用 Cache 儲存聯盟狀態，鎖定後需確保 Cache 立即失效或更新
- **Idempotency**：重複鎖定／解鎖應支援冪等性，避免錯誤提示或狀態異常
- **Queue retry**：操作日誌透過 Kafka 寫入，若 Kafka 異常，不應影響主要操作流程（Log 失敗可容忍）

---

## 10. 常見錯誤

- ❌ 新人誤以為鎖定是 DELETE 操作 → ✅ 鎖定為狀態變更 (PUT)，並非刪除
- ❌ 新人直接操作 DB 更改狀態 → ✅ 必須透過 API 呼叫 PriceCenterService，不可繞過
- ❌ AI 誤解鎖定為永久操作 → ✅ 鎖定是可逆的，管理員可隨時解鎖
- ❌ 漏檢查權限 → ✅ 必須通過 ECCore 驗證，且需管理員角色
- ❌ 未處理 PriceCenterService 回應錯誤 → ✅ 必須根據回應碼正確對應 HTTP 狀態碼

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI: `PUT /api/leagues/{gameType}/{lid}/locked` |
| 服務相依 | README: PriceCenterService（192.168.55.60） |
| 驗證機制 | README: ECCore 3.0.2 內建機制 |
| 操作日誌 | README: Kafka（192.168.55.60）寫入應用程式 Log |
| 鎖定狀態儲存 | 需人工確認（PriceCenterService 內部實作） |

---

## 建議

- **建議新增文件**：PriceCenterService 的 API 規格（特別是聯盟鎖定／解鎖的 endpoint 與回應格式）
- **建議新增規則**：鎖定狀態的 TTL 或審計機制（記錄誰在何時鎖定／解鎖）
- **建議新增測試**：PriceCenterService 異常時的 fallback 行為測試（Circuit Breaker 或 Retry 機制）