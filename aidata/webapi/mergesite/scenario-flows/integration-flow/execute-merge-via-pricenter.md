# 透過 PriceCenterService 執行合併

## 1. 場景目的

本文件說明後台管理人員對賽事、站台賽事或聯盟發起「強制合併」時，MergeSite 作為 Gateway 如何組裝請求、調用 PriceCenterService REST API 並處理回應的完整流程。所有合併操作的最終執行均由 PriceCenterService 負責，MergeSite 本服務不直接操作資料庫。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/merge/games/{gameType}` | 強制合併賽事 |
| PUT | `/api/merge/sitegames/{gameType}` | 合併站台賽事 |
| POST | `/api/merge/leagues/{gameType}` | 強制合併聯盟 |

以上 API 皆需驗證（ECCore 3.0.2），僅限授權後台人員調用。

---

## 3. 流程總覽

1. 後台人員於管理頁面點擊「強制合併」按鈕，觸發請求。
2. MergeSite Controller 接收請求，驗證身份與權限。
3. Service 層組裝合併參數（如 `gameType`、目標 ID、合併對應關係）。
4. 調用 `PriceCenterService` REST API（Gateway：192.168.55.60）執行合併。
5. 接收 PriceCenterService 回應（成功 / 失敗 / 業務錯誤碼）。
6. 若成功，記錄操作日誌（透過 Kafka / `/api/system/logs/action`）。
7. 回傳結果給前端，呈現成功訊息或錯誤原因。
8. 前端刷新管理頁面，顯示合併後的數據（查詢仍經由 PriceCenterService 的 GET API）。

需人工確認：PriceCenterService 合併 API 的具體契約、錯誤碼定義、逾時與重試策略。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | MergeController.GameMerge | 接收 PUT 請求，解析 `gameType` 與 request body |
| 2 | Controller | MergeController | 驗證身份（ECCore 驗證）與操作權限 |
| 3 | Service | MergeGameService | 組裝合併參數（依賽事 / 站台賽事 / 聯盟類型不同） |
| 4 | Service | MergeGameService | 調用 `PriceCenterServiceProxy` 傳送合併請求 |
| 5 | Provider | PriceCenterServiceProxy | 發送 HTTP 請求至 PriceCenterService REST API |
| 6 | Service | MergeGameService | 解析回應，判斷成功與否 |
| 7 | Service | ActionLogService | 記錄操作日誌（成功或失敗） |
| 8 | Controller | MergeController | 回傳 `ServiceMsgCode` 給前端 |

需人工確認：具體 Service 與 Provider 類別名稱、方法簽名、參數結構。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| API | PriceCenterService REST API | Write | 執行實際合併操作 |
| Kafka | 應用程式 Log Topic | Publish | 記錄合併操作日誌 |
| API | `/api/system/logs/action` | Write | 記錄操作稽核（透過 HTTP API） |

本服務在此場景中無直接 DB 讀寫，資料變更皆發生於 PriceCenterService 內部。

---

## 6. 重要規則

- **權限限制**：僅後台管理人員可執行強制合併；必須通過 ECCore 驗證。
- **欄位限制**：請求參數必須包含球種代碼（`gameType`）與合併對應關係；參數結構依合併類型而異。
- **不可暴露資料**：不可在回應中回傳 PriceCenterService 內部錯誤細節；必須包裝為 `ServiceMsgCode`。
- **Transaction 規則**：所有合併操作應為原子性，部分成功視為失敗並回滾。
- **Retry 規則**：需人工確認 PriceCenterService 的冪等性與重試機制。
- **狀態值限制**：合併後可能更改賽事／聯盟狀態，需人工確認狀態流轉規則（如「已合併」狀態碼）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未通過驗證 | 回傳 401 Unauthorized |
| 權限不足（非後台角色） | 回傳 403 Forbidden |
| 請求參數格式錯誤（缺少必填欄位） | 回傳 400 Bad Request，附帶校驗錯誤訊息 |
| 目標合併對象不存在（如聯盟 ID 無效） | PriceCenterService 回傳業務錯誤碼（需人工確認），前端顯示對應錯誤訊息 |
| PriceCenterService 無回應或逾時 | MergeSite 回傳 504 Gateway Timeout 或業務錯誤，記錄 Log |
| 合併參數邏輯衝突（如將聯盟合併至自身） | PriceCenterService 拒絕，回傳業務錯誤碼 |
| Kafka 寫入失敗 | 合併操作成功但日誌遺漏；需人工確認補償機制 |

需人工確認：PriceCenterService 的完整錯誤碼對照表。

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| TC-MERGE-01 | API Test | 有效權限 + 合法參數，強制合併賽事 | 200 OK，合併成功 |
| TC-MERGE-02 | Permission Test | 無權限令牌要求合併 | 401 / 403 |
| TC-MERGE-03 | API Test | 預計合併對象不存在 | 業務錯誤碼，非 200 |
| TC-MERGE-04 | API Test | PriceCenterService 逾時 | 504 或業務錯誤，不 Crash |
| TC-MERGE-05 | Flow Test | 合併後查詢 GET `/api/merge/openclawmerge` | 合併資料正確，不再出現舊關聯 |
| TC-MERGE-06 | API Test | 傳送非法字元（SQL 注入嘗試） | 400 Bad Request，阻止請求 |
| TC-MERGE-07 | API Test | 合併聯盟後查詢 `/api/leagues/{gameType}` | 聯盟為合併後狀態 |

需人工確認：具體測試輸入數據與 PriceCenterService Mock。

---

## 9. 高風險區域

- **高風險 API**：`PUT /api/merge/games/{gameType}`、`POST /api/merge/leagues/{gameType}`，可能導致大量資料關聯變更。
- **跨服務資料同步**：`PriceCenterService` 內部合併邏輯需確保所有關聯表一致性，MergeSite 無法感知內部失敗。
- **Cache consistency**：若 `PriceCenterService` 或其他讀取方有 Cache，合併後需確保 Cache 失效（本服務不直接管理 Cache）。
- **Idempotency**：需人工確認重複合併請求的保護機制（是否會重複合併導致錯誤）。
- **Transaction**：本服務無法控制分散式交易，強依賴 PriceCenterService 自身原子性。

需人工確認：合併操作的回滾策略與補償機制。

---

## 10. 常見錯誤

- ❌ **新人誤解合併寫入路徑**：以為 MergeSite 直接寫入 DB。應理解本服務僅為 Gateway，資料變更均由 PriceCenterService 執行。
- ❌ **AI 誤會合併流程為同步 DB 操作**：若 AI 嘗試生成直接 PriceCenter Cassandra 寫入的 SQL，屬於錯誤，應產出 HTTP Client 呼叫代碼。
- ❌ **忘記合併後刷新頁面**：合併成功後前端未即時重新查詢，導致顯示舊數據。
- ❌ **忽略 `ServiceMsgCode` 包裝**：直接將 PriceCenterService 錯誤訊息暴露給前端，可能洩漏內部架構細節。
- ❌ **未處理 PriceCenterService 無回應**：未設置逾時或未捕捉網路異常，導致操作懸掛或前端無回應。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | 路由定義來自 README.md：`PUT /api/merge/games/{gameType}`、`PUT /api/merge/sitegames/{gameType}`、`POST /api/merge/leagues/{gameType}` |
| Gateway | README.md 載明「資料讀寫均透過 PriceCenterService 進行」與相依服務列表 |
| 日誌 | README.md 記載操作紀錄 API 及 Kafka Log 寫入 |
| 服務相依 | `mergesite` 無直接 DB，所有合併操作均為 REST API 呼叫 PriceCenterService（證據來源：README.md 與 mergesite-detail.md） |
| 權限 | ECCore 3.0.2 驗證機制，定義於 README.md 技術棧 |
| Code | 程式流程僅基於典型 Controller-Service-Provider 推斷；具體類別名稱需人工確認 |

---

## 建議新增文件／規則

- 需人工確認：**PriceCenterService 合併 API 契約文件**（請求格式、錯誤碼、冪等性、逾時設定）。
- 需人工確認：**強制合併操作稽核規範**（誰可以合併、是否需要審核流程、日誌保留期限）。
- 建議新增測試：**PriceCenterService 合併 API 的 Contract Test**（由 MergeSite 角度驗證介面相容性）。