# 查詢歷史賠率

## 1. 場景目的

根據特定賽事 ID，從 Grafana Loki 日誌系統中查詢並解析該賽事的歷史主要賠率（最新的球頭賠率），提供給內部系統使用。
**Evidence**：`README.md` 主要功能 - "歷史賠率查詢：從 Loki 日誌取得指定賽事的歷史主要賠率（最新球頭）"。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| `需人工確認` | `需人工確認` | 具體的 API 路徑、方法及參數未在現有文件中明確定義，需 review Controller 層程式碼（如 `app/controllers` 或路由定義）後補充。 |

---

## 3. 流程總覽

1.  接收包含賽事識別碼（如 `gid`、`lid`）的查詢請求。
2.  驗證請求參數的有效性。
3.  連線至 Loki API 端點（內部 URL）。
4.  構建 LogQL 查詢語句，根據 `gid`、`lid`、球種、玩法等條件過濾 Loki 中的賠率日誌。
5.  執行 Loki 查詢，獲取原始日誌流。
6.  解析日誌內容，提取最新的 "主要賠率"（最新球頭）紀錄。
7.  格式化提取出的賠率資料並回傳。

**需人工確認**：由於缺乏具體 Controller 和 Service 層的程式碼證據 (`phase0/1` 代碼分析未包含 `sitegameoddservice` 業務邏輯)，此流程基於 README 功能描述推導，需審核實際程式碼以確認細節，特別是 Loki 查詢的構建與日誌解析邏輯。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | 需人工確認 | 需人工確認 | 接收請求，驗證參數 |
| 2 | 需人工確認 | 需人工確認 | 調用 Loki Client / Service |
| 3 | 需人工確認 | 需人工確認 | 構建並執行 LogQL 語句 |
| 4 | 需人工確認 | 需人工確認 | 解析 Loki 回傳結果 |
| 5 | 需人工確認 | 需人工確認 | 回傳格式化後的歷史賠率 |

**限制說明**：`webapi/sitegameoddservice/sitegameoddservice-detail.md` 與 `webapi/sitegameoddservice/README.md` 僅定義了服務邊界與職責，未包含類別與方法層級的 code evidence。此表需在檢視實際程式碼後補充。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| 無 | 無 | 無 | 此場景資料來源為 Loki，不直接讀寫 Cassandra、Redis 或 Kafka。 |

**Evidence**：`README.md` 技術棧 - "Grafana Loki (HTTP API)"。`sitegameoddservice-detail.md` Redis 章節 - "本服務未使用 Redis 快取帳戶或賽事資料"。

---

## 6. 重要規則

- **權限限制**：需人工確認。未明確此端點是否為內部服務專用，或是否需要驗證 `authKey`。
- **欄位限制**：從 Loki 查詢的是日誌，非 DB 欄位。但回傳的賠率資料結構應遵循內部規範，不可暴露無關的日誌細節。
- **不可暴露資料**：`pricecenter-detail.md` - `accounts_*.password`, `accounts_*.handler`, `accounts_*.phone`。此場景雖不直接讀取 DB，但若 Loki 日誌意外包含這些敏感資訊，解析時必須過濾，不可回傳。
- **TTL 規則**：不適用。
- **Transaction 規則**：不適用。
- **Retry 規則**：需人工確認。對 Loki API 的呼叫是否有重試機制。
- **狀態值限制**：不適用。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求參數缺失或無效（如 `gid` 為空） | 返回 400 Bad Request，提示參數錯誤。 |
| Loki 服務不可用或連線逾時 | 返回 502 Bad Gateway 或 504 Gateway Timeout，提示上游服務錯誤。 |
| Loki 中查無相關日誌 | 返回 200 OK 並帶有空結果列表或 404 Not Found，依實作而定。 |
| Loki 回傳的日誌格式不符預期，解析失敗 | 返回 500 Internal Server Error，並記錄錯誤日誌。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| `需人工確認` | API Test | 提供有效的 `gid` 和球種，查詢歷史賠率 | 成功返回 200，並包含正確結構的歷史賠率資料。 |
| `需人工確認` | API Test | 提供不存在的 `gid` | 返回空結果或 404。 |
| `需人工確認` | Integration Test | 模擬 Loki 服務中斷 | API 返回 5xx 錯誤，不能 Hang 住或崩潰。 |
| `需人工確認` | Flow Test | 驗證返回的賠率是否確實為“最新球頭” | 比較 Loki 原始日誌與 API 返回結果，確認邏輯正確。 |

---

## 9. 高風險區域

- **Loki 查詢效能**：對 Loki 的 LogQL 查詢若未限制時間範圍或返回條數，可能導致查詢耗時過長或拉取大量無效數據，影響 API 效能。**需人工確認**：程式碼中是否有強制時間範圍或 limit 參數。
- **相依服務穩定性**：此功能強依賴 Loki 的可用性。Loki 故障會直接導致此 API 不可用。
- **日誌格式變更**：若產生賠率日誌的服務變更了日誌格式，解析邏輯將失效，導致 API 返回錯誤或空值。

---

## 10. 常見錯誤

- ❌ **直接在前端調用此 API**：若此 API 設計為內部服務間調用，直接暴露給前端可能導致 Loki 端點或內部數據結構洩露。
- ❌ **混淆 Loki 查詢與 DB 查詢**：新人可能誤以為歷史賠率儲存在 Cassandra 的 `sitegames_*` 或 `games_*` 表中，從而查錯資料源。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 場景與功能定義 | `webapi/sitegameoddservice/README.md` |
| 服務邊界與職責 | `webapi/sitegameoddservice/sitegameoddservice-detail.md` |
| DB 操作限制 | `db/pricecenter-detail.md`, `db/predict-detail.md` |
| Loki 技術棧 | `webapi/sitegameoddservice/README.md` |