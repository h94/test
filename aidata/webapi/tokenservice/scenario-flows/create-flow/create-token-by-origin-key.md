# 依原始金鑰建立 Token

## 1. 場景目的

提供外部服務依據原始金鑰（`originKey`）建立授權 Token 的流程。系統會將 `originKey` 雜湊為固定 10 字元的 `HashKey`，為該公司建立一組具有效期、啟用狀態的唯一 Token，並將舊有衝突 Token 強制停用，確保同一公司代碼與金鑰組合下僅存在一個啟用 Token。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/licence` | 傳入 `originKey` 與可選的 `expirationtime`，回傳產生的 Token 字串 |

---

## 3. 流程總覽

1. 接收請求，取得 `originKey` 與 `expirationtime`（預設 60 秒）。
2. 從請求上下文或設定檔取得 `CompanyCode`（不允許 API 呼叫方自行指定）。
3. 將 `originKey` 以雜湊演算法轉換為 10 字元 `HashKey`。
4. 查詢 `tokens` 資料表，檢查是否存在同一 `CompanyCode` 與 `HashKey` 且 `Enabled = 1` 的 Token。
5. 若有衝突，將該筆 Token 的 `Enabled` 設為 `0`（停用）。
6. 依據請求的 `expirationtime` 計算 `ExpirationTime`（UTC 時間），須介於 0～432,000 秒之間，否則直接報錯。
7. 新增一筆 `tokens` 記錄：`HashKey`、`CompanyCode`、`AddTime`（當前 UTC）、`ExpirationTime`、`Enabled = 1`。
8. 寫入 `logs` 表，記錄此次建立操作。
9. 透過 Kafka 發送一筆建立日誌。
10. 回傳該 `HashKey` 字串作為 Token。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `TokenController.GetLicence` | 接收 `originKey` 與 `expirationtime`，呼叫 Service |
| 2 | Service | `TokenService.CreateTokenByOriginKey` | 執行業務邏輯：雜湊、檢查衝突、停用舊 Token、建立新 Token、記錄日誌 |
| 3 | Provider / Utility | `TokenService.GenerateHashKey` | 將 `originKey` 雜湊為固定 10 字元 `HashKey` |
| 4 | Provider / Data | `TokenRepository` (或 `DbContext`) | 查詢 `tokens` 表確認衝突 Token 存在與否 |
| 5 | Provider / Data | `TokenRepository` (或 `DbContext`) | 若存在衝突 Token，執行 `UPDATE tokens SET Enabled=0` |
| 6 | Provider / Data | `TokenRepository` (或 `DbContext`) | `INSERT` 新 Token 記錄至 `tokens` 表 |
| 7 | Provider / Data | `TokenRepository` (或 `DbContext`) | `INSERT` 操作記錄至 `logs` 表 |
| 8 | Provider / Messaging | `KafkaProducer` | `Publish` 建立事件日誌至 Kafka |
| 9 | Controller | `TokenController` | 回傳 `HashKey` 字串 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `tokens` | `SELECT` WHERE `CompanyCode` + `HashKey` + `Enabled=1` | 檢查是否有啟用中的衝突 Token |
| DB | `tokens` | `UPDATE` SET `Enabled=0` | 停用衝突的舊 Token（若存在） |
| DB | `tokens` | `INSERT` | 新增 Token 記錄（`HashKey`, `CompanyCode`, `ExpirationTime`, `Enabled=1`） |
| DB | `logs` | `INSERT` | 記錄 Token 建立操作（`Action='CreateTokenByOriginKey'`） |
| Queue | Kafka | `Publish` | 非同步發送建立事件日誌 |

---

## 6. 重要規則

- **權限限制**：`CompanyCode` 由請求上下文或組態決定，API 不可開放外部任意指定。需人工確認公司代碼的提取與驗證機制。
- **欄位限制**：`ExpirationTime` 需在 0～432,000 秒（5 天）範圍內，逾限請求應直接拒絕並回傳錯誤。
- **不可暴露資料**：API 回應僅為產出的 Token 字串（即 `HashKey`）。任何場景下均不可回傳或洩漏 `originKey` 或其他內部運算邏輯。
- **TTL 規則**：Token 有效期限由 `expirationtime` 參數決定，單位為秒。
- **Transaction 規則**：停用舊 Token 與建立新 Token 應放置於同一資料庫交易範圍內，確保兩操作原子性（all-or-nothing）。
- **冪等性**：`originKey` 加上 `CompanyCode` 為業務上的唯一組合鍵。重複請求會先停用舊的再建立新的，因此操作本身為覆蓋型（非完全冪等但結果確定），需注意並發控制。
- **不可修改欄位**：建立後即不可再透過 UPDATE 變更 `HashKey`、`ExpirationTime` 或 `CompanyCode`。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `originKey` 為空或未提供 | 回傳 400 或明確錯誤訊息 |
| `expirationtime` 小於 0 或大於 432,000 | 回傳錯誤，不建立 Token |
| 停用舊 Token 時 DB 寫入失敗 | 應終止操作，不回傳 Token，避免同時存在兩個啟用 Token |
| 建立新 Token 時 DB 寫入失敗 | 應回傳錯誤，且舊 Token 保持已停用狀態 (取決於交易隔離層級) |
| Kafka 發送失敗 | Token 仍建立成功，僅影響日誌記錄；需人工確認系統是否記錄發送失敗警示 |
| 並發請求以相同 `originKey`+`CompanyCode` 同時觸發 | 可能造成短暫雙 Token 啟用、後者停用前者後再建；高流量下需評估加鎖或資料庫唯一約束 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | Flow Test | 傳入有效 `originKey` 與預設 `expirationtime`，確認新建 Token | 回傳 10 字元 HashKey，DB 新增 `Enabled=1` 記錄 |
| TC02 | Integration Test | 重複建立同 `originKey`+`CompanyCode` 的 Token | 舊 Token `Enabled` 變為 0，新 Token 成功建立 |
| TC03 | API Test | `expirationtime` 超過 432,000 秒 | API 回傳錯誤，無 Token 建立 |
| TC04 | API Test | 未提供 `originKey` | API 回傳錯誤 |
| TC05 | Permission Test | 嘗試於請求中自訂 `CompanyCode` 參數 | 系統忽略或拒絕，以服務端授權為準（需人工確認） |
| TC06 | Longevity Test | 快速連續發出多次相同請求 | DB 中僅保留一筆 `Enabled=1` 記錄，無孤兒資料 |

---

## 9. 高風險區域

- **高風險 table**：`tokens`（停用舊、新增新於同一交易，需確保原子性與隔離層級）。
- **高風險 API**：`/api/v1/licence`，為建立 Token 的敏感入口，需嚴格控制此 API 的存取來源。
- **跨服務資料同步**：`tokens` 資料由 tokenservice 獨佔寫入，但 `authservice` 擁有讀取權限以執行後續驗證；停用 Token 後需確保快取清除，避免驗證端誤用。
- **Transaction**：停用舊 Token（`UPDATE`）與新增 Token（`INSERT`）務必包裹在同一資料庫交易中，以維持狀態一致性。
- **Cache consistency**：此建立流程主要操作 DB，不直接操作快取。但需人工確認是否有觸發 Redis 清除舊 token cache 的後續機制。
- **Queue retry**：Kafka 發送失敗不應影響主要流程，但需有日誌與警示機制監控訊息遺失。
- **Idempotency**：重複請求的副作用為舊 Token 被停用，對依賴舊 Token 的服務會造成中斷，需事先告知整合方。

---

## 10. 常見錯誤

- ❌ 新人容易在檢查衝突時遺漏 `Enabled=1` 條件，造成誤判已存在 Token。
- ❌ AI 可能誤認為 `/api/v1/licence` 為 POST，實際上依 OpenAPI 顯示為 GET 方法，應引導引用。
- ❌ 忘記驗證 `expirationtime` 最大值 432,000 秒，導致建立無效 Token 或時間異常。
- ❌ 在回應中洩漏 `HashKey` 以外的 Token 內部資訊。
- ❌ Kafka 發送直接耦合在主流程中（如同步等待），當 Broker 無回應時導致請求逾時；應維持非同步發送。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `GET /api/v1/licence` (OpenAPI) |
| DB Table | `tokens` (schema, tokens) |
| DB Table | `logs` (schema, logs) |
| Semantics | HashKey 為 10 字元雜湊，由 `originKey` 產生 (tokenservice-detail, Phase 程式語意分析) |
| Code | `TokenService.GenerateHashKey` (Phase 分析: `generateHashKey() returns 10-char string`) |
| 規則 | `ExpirationTime` 限制 0~432,000 秒 (README) |
| 規則 | 衝突時先停用 `Enabled=0`，再建立 `Enabled=1` (tokenservice-detail) |
| 規則 | API 外部不可指定 `CompanyCode` (tokenservice-detail) |
| Queue | Kafka 用於日誌傳送 (`TokenService` 整合 Kafka，README) |

---

## 建議新增文件/規則/測試

- **建議新增文件**：`originKey` 雜湊演算法說明（以供安全稽核與跨服務一致性實作）。
- **建議新增規則**：並發控制規則（如 `CompanyCode + HashKey` 唯一約束或樂觀鎖定），防止極端條件下的雙 Token 啟用。
- **建議新增測試**：Redis 快取清除整合測試，確保 Token 停用後舊快取被移除。
- **需人工確認**：關於 API 權限控制（`CompanyCode` 究竟從 `authKey` 還是 `appsettings` 取得）與 Kafka 發送失敗的監控告警機制。