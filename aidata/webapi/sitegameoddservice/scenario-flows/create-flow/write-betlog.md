# 寫入下注日誌

## 1. 場景目的
此場景描述 sitegameoddservice 如何提供內部 API 供其他服務將結構化下注記錄寫入 Cassandra。依據系統設計，寫入目標為特定的下注日誌表，但 sitegameoddservice 會在此流程中執行必要驗證並決定最終儲存位置。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/write/betlog` | 接收下注日誌的結構化資料並寫入資料庫。 |

---

## 3. 流程總覽

1. 接收包含下注記錄的 POST request。
2. 驗證 request body 的必要欄位（如 `gid`, `account`, `id` 等）。
3. 根據 request 中的站台(`site`)資訊，對應至正確的 `pricecenter` keyspace 中的 `accounts_{site}` 表。
4. 驗證帳號：查詢對應的 `accounts_{site}` 表中該 `account` 是否存在且 `enabled=1` 且 `closetime` 為空。若驗證失敗，則拒絕寫入。
5. 實體化下注記錄，準備寫入目標資料庫。
6. 將下注記錄寫入 Cassandra 的 `predict` keyspace 中對應的下注日誌表（例如 `betpool_bets`）。
7. 檢查寫入結果，若失敗則回報錯誤。
8. 回傳操作成功的確認訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `WriteController.WriteBetlog` | 接收 HTTP request，解析 JSON body，並調用 Service。 |
| 2 | Validator | `BetlogValidator` | 驗證 request body 的結構與必要欄位（e.g., `gid`, `account`, `id`, `betoption`）。 |
| 3 | Service | `BetlogService.create` | 協調整個寫入流程。 |
| 4 | Provider | `AccountProvider.get_enabled_account` | 根據 `site` 和 `account` 查詢 `pricecenter.accounts_{site}`，驗證帳號有效性 (`enabled=1` 且 `closetime IS NULL`)。若無效則拋出 `AccountInvalidException`。 |
| 5 | Provider | `BetlogProvider.insert` | 根據業務規則選擇目標表（例如 `predict.betpool_bets`），執行 Cassandra `INSERT` 操作。若失敗則拋出 `DatabaseException`。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `pricecenter.accounts_{site}` | Read | 驗證下注帳號的合法性與啟用狀態，確保只有有效帳號才能寫入日誌。 |
| DB | `predict.betpool_bets` (需人工確認) | Write (INSERT) | 儲存經過驗證的下注記錄。此為 append-only 日誌表。 |

---

## 6. 重要規則

- **權限限制**： 此 API 為內部服務間呼叫使用，應有適當的網路層級限制或簡單的服務間驗證，不應直接暴露於公網。
- **帳號驗證強制**： 寫入下注日誌前，強制驗證帳號在 `pricecenter.accounts_{site}` 中的狀態。必須滿足 `enabled=1` 且 `closetime` 為空，否則應拒絕寫入。
- **不可暴露資料**： 此 API 的回傳內容不應包含帳號的密碼、電話等敏感個資，僅回傳操作結果。
- **不可修改欄位**： `betpool_bets` 表中的 `id`, `gid`, `account` 等主鍵或分區鍵一旦寫入，不可更新。
- **Cross-Service Boundaries**：根據 `sitegameoddservice-detail.md` 與 `pricecenter-detail.md` 的規範，sitegameoddservice 角色為 `predict` 與 `strategy_bet_log` 的 **reader**，而非 writer。寫入 `predict` keyspace 應由 `predictservice` 或 `clientflowservice` 處理。此 API 的存在與規範衝突，需人工確認是否為架構破例或是遺留功能。
- **常見錯誤**: ❌ 直接寫入 `strategy_bet_log` 或相關策略表 → ✅ 寫入操作應由對應的 owner service 負責，sitegameoddservice 不負責此寫入。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求缺少必填欄位（如 `gid`, `account`） | API 回傳 `400 Bad Request` 並附帶明確的錯誤訊息，指出缺少的欄位。 |
| 帳號不存在或驗證失敗 | API 回傳 `400 Bad Request` 或 `404 Not Found`，提示帳號無效或未啟用，拒絕寫入。 |
| `accounts_{site}` 表根據 `site` 參數找不到 | API 回傳 `500 Internal Server Error` 或特定業務錯誤碼，提醒站台設定錯誤。 |
| 寫入 `predict` keyspace 時發生 Cassandra 異常 (e.g., Timeout) | API 回傳 `500 Internal Server Error`，並記錄錯誤日誌。後續可考慮實作重試機制。 |
| 任何寫入至 `betpool_bets` 的操作 | 由於架構限制，若此服務無寫入權，可能導致 `UnauthorizedException` 或權限錯誤，需根據實際 Cassandra 權限設定而定。此為高風險行為。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T-01 | API Test | 發送一個包含所有必要欄位的完整、合法的 request。 | API 回傳 `200 OK`，且資料成功寫入對應的 Cassandra 表中。 |
| T-02 | API Test | 發送一個缺少 `account` 欄位的 request。 | API 回傳 `400 Bad Request`，顯示驗證錯誤，且無任何資料寫入。 |
| T-03 | Permission Test | 提供一個 `enabled=0` 的帳號進行寫入。 | 帳號驗證失敗，API 回傳錯誤，拒絕寫入。 |
| T-04 | Integration Test | 提供一個合法的帳號，寫入成功後，直接查詢 `predict.betpool_bets` 表。 | 可透過 `gid` 和 `account` 查詢到該筆新寫入的資料。 |
| T-05 | Flow Test | 模擬 Cassandra 寫入失敗的情境。 | API 回傳 `500 Internal Server Error`，且錯誤被正確記錄至日誌系統。 |

---

## 9. 高風險區域

- **跨服務寫入權限**： sitegameoddservice 的主要職責是讀取賠率，其對 `predict` keyspace 的寫入權限與文件規範衝突。必須釐清此 API 的歷史背景與目前實際的 Cassandra 連線權限。
- **高風險 table**： `predict.betpool_bets`。錯誤的寫入（如重複 `id`）可能會影響下注記錄的完整性，干擾後續的結算流程（如 `predictresultservice`）。
- **帳號驗證依賴**： 寫入操作強依賴於 `pricecenter` 的 `accounts_*` 表，若 `pricecenter` 叢集暫時不可用，整個寫入流程將無法進行。
- **數據一致性**： 確保寫入資料的準確性，特別是金額相關欄位（如 `betzcoin`），錯誤的數據可能導致金流計算錯誤。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 直接寫入 `predict.betpool_bets`，卻未先理解 `pricecenter-detail.md` 中對帳號驗證的強制要求而跳過驗證步驟。
  - 混淆 `predict` keyspace 中各表的用途，將資料寫入錯誤的表。
- **AI 容易誤解**：
  - 誤以為 sitegameoddservice 是 `betpool_bets` 的 owner service，從而建議直接使用此 API 進行寫入。
  - 忽略 `sitegameoddservice-detail.md` 中關於不負責寫入 `predict` 的策略投注記錄的規範。
- **常見漏檢查項目**： 對帳號 `closetime` 欄位的檢查，僅驗證 `enabled=1` 是不夠的。
- **常見錯誤流程**： 在其他服務（如 clientflowservice）已提供標準下注介面的情況下，繞過正規流程直接透過此輔助 API 寫入日誌，導致核心下注邏輯（如扣款、限額檢查）被繞過。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README.md: `/api/write/betlog` |
| DB (寫入目標) | predict.betpool_bets (Schema)  |
| DB (驗證來源) | pricecenter.accounts_{site} (Schema 與 pricecenter-detail.md) |
| Rules | sitegameoddservice-detail.md (本服務不負責寫入策略投注紀錄) |
| Rules | pricecenter-detail.md (帳號驗證規則: enabled=1, closetime is null) |