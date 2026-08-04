# 更新聯盟語系簡稱

## 1. 場景目的

後台編輯人員上傳多語系簡稱對照，更新指定聯盟在不同語系下的縮寫顯示，用於前端站台或 App 的聯盟名稱縮短顯示。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/leagues/{gameType}/{id}/abbrmap` | 更新聯盟語系簡稱 |

---

## 3. 流程總覽

1. 接收 PUT 請求，路徑含 `gameType` 與 `id`（聯盟唯一識別），Body 為多語系簡稱對照（JSON）。
2. 驗證登入 Session / Token（ECCORE 3.0.2 機制）。
3. 驗證 `gameType`、`id` 不為空，Body 格式正確。
4. 檢查操作權限（可能為後台特定角色）。
5. 呼叫 PriceCenterService 對外 API（PUT 或 POST），要求該服務更新對應聯盟的 `AbbrMap` 欄位。
6. PriceCenterService 回傳成功則回傳 `ServiceMsgCode`（成功）。
7. 若 PriceCenterService 回傳失敗或逾時，本服務回傳對應錯誤碼。
8. 非同步寫入 Kafka 操作紀錄（Log）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `LeagueController.UpdateAbbrMap` | 接收參數，呼叫 Service |
| 2 | Service | `LeagueService.UpdateAbbrMap` | 驗證權限、組裝 API 請求 |
| 3 | Provider | `PriceCenterServiceProvider.UpdateLeagueAbbrMap` | 透過 HTTP 呼叫 PriceCenterService |
| 4 | Provider | `KafkaLogProvider.WriteActionLog` | 非同步寫入操作紀錄 |
| 5 | Controller | 回傳 `ServiceMsgCode` | 成功或失敗訊息 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| 外部 API | PriceCenterService REST API | Write | 實際更新聯盟語系簡稱（目標儲存未知，但不在本服務） |
| Kafka | 192.168.55.60 | Publish | 應用程式 Log，記錄操作人員與動作 |
| 權限驗證 | ECCore Session / Token | Read | 確認登入與角色權限 |

> **注**：本服務無直接 DB 或 Cache 操作。

---

## 6. 重要規則

- **權限限制**：需具備後台編輯聯盟語系之角色權限（具體角色由 ECCore 定義，需人工確認）。
- **欄位限制**：`gameType` 僅允許特定球種字串（如 `NBA`, `MLB` 等），`id` 為聯盟唯一識別字串。
- **不可暴露資料**：無敏感資料在請求中，回應也僅有通用成功/錯誤訊息。
- **Transaction 規則**：無跨服務事務，若 PriceCenterService 失敗則直接回傳錯誤，不重試（或依業務設定有限重試）。
- **狀態值限制**：無狀態流轉。
- **不可修改欄位**：本 API 僅修改聯盟的 `AbbrMap`，不可影響其他欄位（如 `NameMap`、`Locked` 等）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未登入或 Token 過期 | 回傳 HTTP 401 或對應驗證錯誤 |
| 權限不足（非後台管理員） | 回傳 HTTP 403 |
| `gameType` 不存在或格式錯誤 | 回傳 400，錯誤訊息提示參數錯誤 |
| `id` 不存在 | PriceCenterService 回傳 404 Not Found，本服務轉發對應錯誤 |
| Request Body 格式錯誤（非 JSON 或欄位名稱不符） | 回傳 400 Bad Request |
| PriceCenterService 連線逾時或服務不可用 | 回傳 502 / 504 或自定義服務不可用錯誤 |
| PriceCenterService 內部更新失敗（如 DB 寫入錯誤） | 回傳 500，記錄錯誤 Log |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| T-01 | Permission Test | 未帶 Token 呼叫 | 401 |
| T-02 | Permission Test | 一般會員 Token 呼叫 | 403 |
| T-03 | API Test | 正常輸入，成功更新 | 200，PriceCenterService 收到正確請求 |
| T-04 | API Test | Body 遺漏必要欄位（如無對應語系 key） | 400 |
| T-05 | Integration Test | PriceCenterService 模擬失敗 | 本服務回傳 502，Kafka 記錄錯誤 |
| T-06 | Flow Test | 連續更新同一聯盟 | 正常更新，後蓋前 |

---

## 9. 高風險區域

- **高風險 API**：對外依賴 PriceCenterService，若其不穩定將直接影響本功能。
- **跨服務資料同步**：更新後，站台賽事與前端顯示的簡稱可能需要快取刷新，但不在本服務範圍（由 PriceCenterService 或下游服務負責）。
- **Cache consistency**：本服務不操作 Cache，但 PriceCenterService 若使用 Cache 需確保失效。
- **Idempotency**：多次相同請求會覆蓋資料，無冪等設計問題（符合業務預期）。

---

## 10. 常見錯誤

- 新人可能誤解「無直接資料庫」而嘗試直接寫入 pricecenter keyspace 或 sport MySQL（❌）→ 應全透過 PriceCenterService。
- AI 容易將此場景與「更新聯盟語系名稱」混淆，注意 API 路徑不同（`abbrmap` vs `namemap`），請求 Body 結構可能不同。
- 漏檢查權限：後台 API 必須驗證角色，不可僅依賴登入狀態。
- 未處理 PriceCenterService 回傳的非 200 狀態碼，直接當成成功回傳。
- 忘記將操作記錄寫入 Kafka，導致無法審計。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | README（#聯盟管理） |
| 請求參數與 Body schema | OpenAPI（`/api/leagues/{gameType}/{id}/abbrmap`） |
| 服務相依 | README（PriceCenterService Gateway） |
| 驗證機制 | README（ECCore 3.0.2） |
| Kafka 用途 | README（應用程式 Log） |
| DB 邊界 | mergesite-detail.md（無直接資料庫） |

> **需人工確認**：PriceCenterService 的實際 API 規格（URL、Method、Request/Response 格式）、權限角色定義、Kafka topic 名稱、是否具備 Retry 機制等，應根據內部文件補充。現有資料未提供 PriceCenterService 的 microservice-contract，故流程中與其互動細節為推論。