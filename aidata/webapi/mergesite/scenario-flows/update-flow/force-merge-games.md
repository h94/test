# 強制合併賽事

## 1. 場景目的

提供後台管理人員對指定球種的賽事執行強制合併操作，將原本分屬不同外站來源（OpenClaw）的相同賽事建立關聯，並透過 PriceCenterService 執行底層資料的邏輯合併，以解決自動比對失敗或需要人工介入的賽事配對問題。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/merge/games/{gameType}` | 強制合併指定球種的賽事 |

---

## 3. 流程總覽

1. 接收後台管理人員的強制合併賽事 request
2. 驗證 request 的授權 token（由 ECCore 驗證機制處理）
3. 根據 request body 內的合併參數，呼叫 MergeService 進行強制合併邏輯
4. MergeService 透過 Gateway 呼叫 PriceCenterService REST API，執行底層的賽事資料合併
5. PriceCenterService 回傳合併結果
6. 若合併成功，回傳成功訊息；若失敗，回傳錯誤碼與說明

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | MergeController.ForceMergeGames | 接收 PUT /api/merge/games/{gameType}，取出 gameType 與 request body，調用 MergeService |
| 2 | Service | MergeService.ForceMergeGames | 驗證 gameType、解析合併請求，組裝呼叫 PriceCenterService 的必要參數 |
| 3 | Provider | PriceCenterGateway（或同等級別） | 以 HTTP 方式呼叫 PriceCenterService 的強制合併 API（需人工確認 PriceCenterService 端確切的 API 路由） |
| 4 | External | PriceCenterService | 執行實際的賽事合併資料寫入，將多個來源的賽事（OpenClaw 資料）關聯至同一 master game |
| 5 | Service | MergeService | 根據 PriceCenterService 回傳結果，決定回傳成功或失敗的 ServiceMsgCode |
| 6 | Controller | MergeController | 回傳合併結果給前端 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | N/A（MergeSite 本身無直接資料庫操作） | 無 | 所有資料操作均透過 PriceCenterService 處理 |
| Redis | N/A（本服務未使用 Redis） | 無 | 無 cache 機制，每次操作皆即時呼叫後端 |
| Queue | 本服務不直接使用 MQ | 無 | 賽事合併為同步操作，不透過 message queue 非同步處理 |

---

## 6. 重要規則

- **權限限制**：所有 `/api/merge/*` 路由皆需要驗證（`✅`），未通過授權的 request 會被 ECCore 攔截
- **欄位限制**：需人工確認 request body 的精確欄位定義（可能包含來源賽事 ID 與目標合併 ID 的配對清單）
- **不可暴露資料**：合併操作的內部實作細節（如 PriceCenterService 的內部儲存）不可直接回傳或暴露給前端
- **Transaction 規則**：強制合併為原子操作，由 PriceCenterService 保證；若合併過程失敗，應回傳明確的錯誤代碼，不留下部分合併的狀態
- **Retry 規則**：本服務不實作自動 retry，合併失敗時前端應要求管理者手動重新發起
- **狀態值限制**：賽事與聯盟都有既有的生命週期，合併行為可能會互相影響（如已被鎖定的比賽不可變更關聯），需人工確認 PriceCenterService 端的業務規則

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求未帶有效 token | ECCore 攔截，回傳 401 Unauthorized |
| gameType 路徑參數不合法（不存在或格式錯誤） | 回傳 400 Bad Request 或相應的 ServiceMsgCode 錯誤 |
| request body 格式錯誤或缺少必要欄位 | 回傳 400 Bad Request 並附上欄位驗證錯誤訊息 |
| PriceCenterService 呼叫失敗（網路逾時、服務無回應） | MergeService 捕捉 Gateway 錯誤，回傳 502 Bad Gateway 或通用錯誤代碼 |
| PriceCenterService 回傳合併邏輯失敗（如賽事已關閉、關係衝突） | MergeService 轉發 PriceCenterService 的錯誤訊息給前端 |
| 同時多人對相同賽事發起合併請求 | PriceCenterService 應實作樂觀鎖或等冪性設計，若發生衝突回傳明確錯誤；MergeSite 僅負責轉發 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-001 | API Test | 合法 token 及正確參數呼叫 | 回傳 200 及成功訊息 |
| UT-002 | Permission Test | 無效或過期 token 呼叫 | 回傳 401 Unauthorized |
| UT-003 | API Test | gameType 為空或不存在 | 回傳 400 或 404 |
| UT-004 | API Test | request body 缺少必要欄位（需人工確認確切欄位定義） | 回傳 400 Bad Request 及驗證錯誤說明 |
| UT-005 | Integration Test | 模擬 PriceCenterService 回應失敗 | MergeSite 回傳對應的錯誤訊息，不可 crash |
| UT-006 | Flow Test | 成功合併後，用 GET API 查詢該賽事資料 | 確認關聯已建立，不再出現在待合併清單中 |

---

## 9. 高風險區域

- **高風險 API**：`PUT /api/merge/games/{gameType}`，因為它直接改動賽事間的底層關聯，影響前端顯示、賠率計算、報表等下游功能
- **跨服務資料同步**：MergeSite 完全不持有資料，任何查詢或合併都建立在 PriceCenterService 正常回應的假設下；若對方服務資料不一致或有延遲，會直接反映在管理後台上
- **Idempotency**：需人工確認 PriceCenterService 的合併 API 是否具備等冪性；若無，重複操作可能導致資料關聯錯誤或重複合併的邏輯問題
- **待合併資料時效**：管理人員發起強制合併前所看到的資料，可能在送出請求的瞬間已被其他管理者異動，導致合併時產生衝突，錯誤處理需要明確

---

## 10. 常見錯誤

- ❌ **對 MergeSite 進行壓力測試時模擬 DB call 行為**：MergeSite 無直接 DB，若測試時 mock 了 DB 操作，不代表真實行為
- ❌ **誤以為合併是透過 Queue 非同步執行**：目前為同步 HTTP 呼叫，無非同步機制；若前端長時間等待，可能是 PriceCenterService 回傳過慢
- ❌ **將合併失敗的錯誤直接轉換為 500 Internal Server Error**：應區分服務內部錯誤與下游服務業務錯誤，將 PriceCenterService 的錯誤碼及說明正確轉換回傳
- ❌ **於測試階段直接修改 PriceCenterService 後端資料以準備測試情境，卻未考慮其他服務的資料一致性**：可能導致不可預期的 side effect

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | MergeController.ForceMergeGames |
| DB | N/A（所有資料操作透過 PriceCenterService） |
| Redis | N/A（本服務未使用 Redis） |
| Code | MergeService.ForceMergeGames |
| Dependency | PriceCenterService（Gateway: 192.168.55.60） |
| Auth | ECCore 3.0.2 內建機制，路由定義於 README |

---

## 建議新增文件 / 規則 / 測試

- **建議新增文件**：
  - `ref/scenarios/force-merge-games-request-schema.md`（記錄 request body 確切欄位定義、多站台賽事對應寫法，目前 OpenAPI 未收錄 request body schema）
  - `ref/scenarios/pricecenter-force-merge-api.md`（記錄 PriceCenterService 端合併 API 的規格、錯誤碼、等冪性行為，目前資訊不足）
- **建議新增規則**：
  - 當 PriceCenterService 回傳錯誤時，MergeService 的錯誤代碼對應表
  - 若合併邏輯有冪等性要求，應於 `rules/` 中明確定義「同一筆請求重複發送不得產生重複關聯」的規則
- **建議新增測試情境**：
  - 合併後立即執行 GET 查詢，驗證關聯正確性（Integration Test）
  - 模擬 PriceCenterService 逾時，確認前端收到正確的逾時錯誤代碼
  - 連續發送兩筆相同合併請求，驗證等冪性行為（無論是否預期等冪，都能確認系統實際表現）