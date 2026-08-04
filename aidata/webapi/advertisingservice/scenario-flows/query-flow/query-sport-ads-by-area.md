# 查詢指定版位體育廣告

## 1. 場景目的

前台頁面根據廣告版位（adArea）查詢應顯示的體育廣告。系統需回傳當前有效（`enabled=1` 且日期符合）的廣告，並可依前端請求的語言過濾結果，以提供精準的廣告展示內容。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sport/ads/{adArea}` | 查詢指定版位的體育廣告 |

- **需要驗證**：是 (`ECFramework.ECService`)
- **參數**：
  - Path: `adArea` (string, required) — 廣告版位
  - Query: `lang` (string, optional) — 客戶端語言代碼，用於過濾廣告

---

## 3. 流程總覽

1. 接收 GET 請求，包含路徑參數 `adArea` 與選擇性查詢參數 `lang`。
2. 驗證請求的 `AuthKey`（透過 ECFramework.ECService 中介軟體）。
3. Controller 接收 `adArea` 與 `lang`，傳遞至 Service 層。
4. Service 層調用 Provider，對 Cassandra `ads.advertising_sport` 資料表執行查詢，條件為 `adarea = '{adArea}'`。
5. 在應用程式層（Service）過濾查詢結果：
   - `enabled` 必須等於 `1`。
   - 當前日期（`yyyy-MM-dd` 格式字串）必須大於等於 `startdate` 且小於等於 `closedate`（字串字典序比對）。
   - 若請求包含 `lang` 參數，則 `supportlangs` 列表必須包含該語言代碼。
6. 將符合條件的廣告物件列表回傳。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware | `ECFramework.ECService` | 驗證請求的 AuthKey，確認呼叫端身份。 |
| 2 | Controller | `SportAdvertisementController` | 接收 `adArea` 與 `lang` 參數。**需人工確認**：實際 Controller 名稱與方法簽名。 |
| 3 | Service | `SportAdService` (推測) | 呼叫 Provider 取得原始資料。**需人工確認**：實際 Service 名稱。 |
| 4 | Provider | `SportAdProvider` (推測) | 執行 Cassandra 查詢：`SELECT * FROM advertising_sport WHERE adarea = ?`。**需人工確認**：實際 Provider 名稱與查詢語句。 |
| 5 | Service | `SportAdService` (推測) | 在記憶體中過濾 `enabled`、日期範圍 (`startdate`, `closedate`) 與語言 (`supportlangs`)。 |
| 6 | Service | `SportAdService` (推測) | 將過濾後的結果封裝為 Response DTO 並回傳。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `ads.advertising_sport` | Read | 根據 `adarea` (Partition Key) 查詢廣告原始資料。 |
| Redis | *(不使用)* | - | **重要**: `advertisingservice-detail.md` 明確聲明「本服務未使用 Redis」，推翻 README 描述。 |
| Queue | *(無)* | - | 此查詢流程為同步操作，未使用 Message Queue。 |

---

## 6. 重要規則

- **權限限制**：所有 `/api/v1/sport/ads` 路徑下的端點皆需要驗證。
- **資料來源衝突**：README 場景描述「從 Redis SportAdCache 讀取快取廣告資料」，但 `advertisingservice-detail.md` 聲明「本服務未使用 Redis，所有資料均直接讀寫 Cassandra」。**以此 detail 文件為準，資料直接來自 Cassandra。**
- **日期過濾規則**：`startdate` 與 `closedate` 以字串字典序與當天日期字串（`yyyy-MM-dd`）進行比對。**不是** UTC 時間戳比對。
- **語言過濾規則**：若傳入 `lang` 參數，僅回傳 `supportlangs` 列表包含該語言的廣告；若未傳入，則回傳該版位下所有有效廣告。
- **狀態過濾規則**：僅回傳 `enabled = 1` 的記錄。
- **不可暴露資料**：`advertising_sport` 所有欄位均需公開展示，無隱藏欄位。但需注意 `adclass` 在 `ads-detail.md` 中標記為 `productservice` 不可回傳，**需人工確認** advertisingservice 對外是否也應隱藏此欄位。
- **欄位限制**：
  - `supportlangs`: Cassandra List 型態，更新時需全量覆蓋，但查詢不涉及寫入操作，此規則僅供背景了解。
  - 日期格式必須為 `yyyy-MM-dd`，不含時間或時區。
- **排序規則**：**需人工確認**。檔案未明確定義此查詢的排序規則，推測可能依 `seq` 降冪排序。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求缺少 `AuthKey` 或 `AuthKey` 無效 | 回傳 HTTP 401 Unauthorized。 |
| 路徑參數 `adArea` 為空或格式不符 | 回傳 HTTP 400 Bad Request，可能由路由本身或驗證層觸發。**需人工確認**。 |
| 查詢的 `adArea` 在 Cassandra 中無任何資料 | 回傳 HTTP 200 OK，並帶有空陣列 `[]`。 |
| Cassandra 連線失敗或查詢逾時 | 回傳 HTTP 500 Internal Server Error。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| `GET_SPORT_AD_01` | Flow Test | 查詢包含有效廣告的 `adArea`，不帶 `lang` 參數。 | 回傳所有 `enabled=1` 且日期符合的廣告。 |
| `GET_SPORT_AD_02` | API Test | 查詢包含有效廣告的 `adArea`，並帶入 `lang=zh` 參數。 | 僅回傳 `supportlangs` 包含 `zh` 且其他條件符合的廣告。 |
| `GET_SPORT_AD_03` | API Test | 查詢的 `adArea` 下所有廣告的 `closedate` 皆已過期。 | 回傳空陣列 `[]`。 |
| `GET_SPORT_AD_04` | API Test | 查詢的 `adArea` 下僅有 `enabled=0` 的廣告。 | 回傳空陣列 `[]`。 |
| `GET_SPORT_AD_05` | Permission Test | 不帶 AuthKey 或帶無效 AuthKey 發送請求。 | 回傳 HTTP 401 Unauthorized。 |

---

## 9. 高風險區域

- **Cache 一致性**：README 與 detail 文件對 Redis 快取的使用描述矛盾。若實際部署與 detail 文件不符，前端可能讀取到陳舊的快取資料，導致廣告未即時更新。**需人工確認並統一文件與實作。**
- **日期字串比對**：使用字串字典序比對日期 (`startdate <= '2025-01-01' <= closedate`) 在邏輯上是可行的，但極度依賴日期格式嚴格為 `yyyy-MM-dd`。若格式不一（如 `2025-1-1`）將導致錯誤過濾，此為高風險實作細節。
- **跨服務資料同步**：`ads-detail.md` 指出 `advertising_sport` 的 `enabled` 欄位可由 `productservice` 變更。若 `productservice` 停用廣告，advertisingservice 的查詢將立即反映，無同步延遲問題，但需確保兩個服務對 `enabled` 狀態的理解一致。

---

## 10. 常見錯誤

- **新人容易犯錯**：誤信 README，在程式碼中尋找 Redis `SportAdCache` 的相關邏輯，或試圖實作快取讀取。
- **AI 容易誤解**：在生成測試案例時，為 `startdate` 或 `closedate` 使用 Unix 時間戳或 `DateTime` 物件進行比對，而非字串。
- **常見漏檢查項目**：忘記在查詢條件中加入 `enabled=1` 的過濾，或未在應用層過濾 `closedate` 小於今日的廣告。
- **常見錯誤流程**：直接將從 Cassandra 查詢到的所有記錄全數回傳，未進行任何應用層的狀態或日期過濾。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路徑與方法 | `OpenAPI: /api/v1/sport/ads/{adArea}` |
| 參數定義 | `OpenAPI: paths./api/v1/sport/ads/{adArea}.get.parameters` |
| 需要驗證 | `README: 對外 API 重點 > 廣告管理 > GET /api/v1/sport/ads/{adArea}` |
| DB Table 與讀取規則 | `advertisingservice-detail.md: advertising_sport 查詢` |
| 日期比對邏輯 (字串字典序) | `advertisingservice-detail.md: advertising_sport 查詢` |
| 語言過濾邏輯 | `advertisingservice-detail.md: advertising_sport 查詢` |
| **未使用 Redis** | `advertisingservice-detail.md: Redis 章節 ("本服務未使用 Redis")` |
| DB Schema | `ads.md: advertising_sport` (定義 Partition Key 為 `adarea`) |
| 欄位語意 | `Phase1 Code Semantics: advertising_sport` (定義 `supportlangs` 等欄位用途) |