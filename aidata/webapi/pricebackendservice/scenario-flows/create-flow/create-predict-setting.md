# 建立競猜設定

## 1. 場景目的

後台管理員為指定遊戲類型（如 sport、esport）建立一組新的競猜規則設定，定義下注方式、遊戲參數、時間規則等，供前台使用者參與競猜。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/predict/settings/{gameType}` | 建立特定遊戲類型的競猜設定 |

- 需要驗證：✅
- gameType：URL 路徑參數，代表遊戲類型（例如 `sport`、`esport`）
- Request Body：包含競猜設定所需的欄位（具體結構需人工確認，推測可能包含遊戲選項、賠率參數、時間設定等）

---

## 3. 流程總覽

1. 接收後台管理員的建立請求，包含 `gameType` 與設定內容。
2. 驗證管理員權限（ECFramework.ECService 驗證框架）。
3. 對請求參數進行基本校驗（如 gameType 是否為系統支援的類型）。
4. 將請求轉發至下游微服務 `predictservice` 的對應 API（推測為 `POST /api/predict/settings/{gameType}` 或類似）。
5. 下游服務執行寫入競猜設定資料（可能寫入 `predict` keyspace 中的特定設定表，需人工確認）。
6. 若寫入成功，pricebackendservice 回傳 200 OK；若失敗（如參數無效、遊戲類型不存在、服務不可用），回傳對應錯誤碼。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `PredictController.CreateSettings` | 接收 POST 請求，綁定 `gameType` 與 `request body` |
| 2 | Controller | `PredictController.CreateSettings` | 調用對應的 Service 方法（例如 `IPredictService.CreateSettings`） |
| 3 | Service | `PredictService` | 參數校驗（如 gameType 是否合法、必要欄位是否存在） |
| 4 | Service | `PredictService` | 組裝下游服務請求，呼叫 `predictservice` 的 REST API |
| 5 | Provider (HTTP Client) | `PredictServiceClient` | 發送 HTTP 請求至 predictservice |
| 6 | (下游) | predictservice 內部 | 執行競猜設定建立邏輯，寫入 DB |
| 7 | Provider | `PredictServiceClient` | 接收 predictservice 回傳結果 |
| 8 | Service | `PredictService` | 處理下游回傳，成功則回傳 DTO，失敗則拋出異常 |
| 9 | Controller | `PredictController` | 回傳 HTTP 200 或錯誤回應 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| API 呼叫 | predictservice | Write | 建立競猜設定資料，實際寫入由下游服務負責 |
| （pricebackendservice 本身無直接 DB 存取） | - | - | - |
| （推測）predictservice 寫入 | predict keyspace （設定表，需人工確認） | Write | 儲存競猜規則設定 |
| （可能使用）Redis 快取清除 | predictservice 內部 | Delete | 設定變更後清除相關快取，確保前台讀取最新設定 |

---

## 6. 重要規則

- **權限限制**：僅後台管理員可呼叫此 API，需通過 ECFramework 驗證。
- **欄位限制**：gameType 必須是系統支援的遊戲類型（可透過 `/api/v1/system/gametypes` 查詢有效值）。
- **不可暴露資料**：設定內容中可能包含內部運算參數（如 `feedrate`），建立後對外 API 不回傳完整原始值，僅回傳必要資訊。
- **Transaction 規則**：本服務僅為轉發層，無需處理事務，一致性由下游 predictservice 保證。
- **Retry 規則**：若呼叫 predictservice 失敗（例如超時、500），pricebackendservice 應回傳 502 或 503，不可自行重試（除非設計上有 idempotency 策略且與 predictservice 協商）。
- **Idempotency**：此 API 不可保證冪等，重複呼叫可能會建立多筆設定（除非 predictservice 內部有唯一性檢查）。
- **狀態值限制**：建立的設定初始狀態（如 `enabled`）由 predictservice 定義（推測預設為 1 啟用），pricebackendservice 不應指定。
- **不可修改欄位**：建立後，部分欄位可能不可變更（如遊戲類型、設定 ID），需透過專用更新 API 修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| gameType 路徑參數不存在或為空 | HTTP 400，無效的遊戲類型 |
| 管理員權限不足 | HTTP 401 或 403，拒絕存取 |
| 請求 body 缺少必要欄位 | HTTP 400，參數驗證失敗 |
| gameType 不在系統支援列表中 | HTTP 400，不支援的遊戲類型 |
| predictservice 回應 4xx（參數錯誤） | 轉發下游錯誤碼及訊息（如 400） |
| predictservice 回應 5xx 或無法連線 | HTTP 502 Bad Gateway 或 503 Service Unavailable |
| 下游服務逾時 | HTTP 504 Gateway Timeout |
| 重複建立完全相同的設定（若 predictservice 檢查唯一性） | HTTP 409 Conflict 或直接建立新筆（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| T01 | API Test | 正常建立（有效 gameType，完整 body） | 200 OK，回傳設定 ID 或成功訊息 |
| T02 | Permission Test | 未帶驗證 token 呼叫 | 401 Unauthorized |
| T03 | Validation Test | gameType 為空字串 | 400 Bad Request |
| T04 | Validation Test | body 中缺少必填欄位 | 400 Bad Request，提示缺少欄位 |
| T05 | Integration Test | predictservice 回傳 500 | pricebackendservice 回傳 502 或 503 |
| T06 | Integration Test | predictservice 逾時 | 504 Gateway Timeout |
| T07 | Flow Test | 建立後立即查詢設定（透過 GET API） | 能查詢到新建立的設定 |
| T08 | Flow Test | 以不存在的 gameType 呼叫 | 400 錯誤，不支援的遊戲類型 |
| T09 | Idempotency Test | 重複相同請求多次（需確認下游行為） | 若為防止重複，應產出相同結果或回傳 409；否則可能建立多筆 |

---

## 9. 高風險區域

- **高風險 API**：`POST /api/v1/predict/settings/{gameType}` — 若參數錯誤可能導致前台顯示異常或下注邏輯錯誤。
- **跨服務資料同步**：pricebackendservice 僅轉發，風險在於與 predictservice 的合約不一致（如 Schema 變更未同步）。
- **Cache consistency**：若 predictservice 內部使用 Redis 快取競猜設定，建立新設定後必須清除或更新快取，否則前台可能無法立即看見新設定。
- **Idempotency**：若下游未做防重，重複請求會造成資料不一致，需確認 predictservice 的 API 設計。
- **權限繞過**：確保驗證中間件正確攔截未授權請求，避免一般使用者竄改參數。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 直接在 pricebackendservice 嘗試寫入資料庫（本服務無 DB 存取權限）。
  - 未正確傳遞 `gameType` 路徑參數，導致路由匹配失敗。
  - 手動構造下游請求時忘記轉換 DTO 欄位命名（camelCase vs snake_case 等）。
- **AI 容易誤解**：
  - 誤以為 pricebackendservice 直接操作 Cassandra 的 `predict` keyspace，實際上所有操作皆透過 REST 呼叫 predictservice。
  - 擅自推測設定的 Schema，未查閱下游 API 文件。
- **常見漏檢查項目**：
  - 未驗證 gameType 是否在系統支援列表中。
  - 未處理下游服務回應中的 4xx 錯誤，直接回傳 200。
- **常見錯誤流程**：
  - 將敏感設定參數（如 `feedrate`）直接暴露給前台 API。
  - 忽略 Redis 快取失效，導致設定變更後前台資料不一致。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md：`POST /api/v1/predict/settings/{gameType}` |
| 服務依存 | README.md：`predictservice` 用於競猜設定 |
| 無直接 DB | README.md：本服務不直接存取資料庫 |
| 驗證框架 | README.md：ECFramework.ECService |
| 權限 | API routes 皆標記 ✅ 需要驗證 |
| 下游服務推測 | pricebackendservice-detail.md predict section 無直接設定表，推測由 predictservice 管理 |
| DB 可能寫入 | predict-detail.md：`betpool_games`、`predictbets_*` 等，但「設定」表需人工確認 |
| Redis 快取 | predict-detail.md：`predict:game:{gid}:status` 等，設定變更後應清除 |

---

⚠️ **需人工確認**：
- 競猜設定實際寫入的 predict DB table（目前文件未明確定義「設定」專用表）。
- predictservice 對應的 API endpoint 與 request body Schema。
- predictservice 是否支援 idempotent 建立，以及防重機制。
- 設定建立後是否有必要清除哪些 Redis 快取鍵（如 `predict:settings:{gameType}`）。