# 查詢即時賠率

## 1. 場景目的

根據球種（gtype）、玩法、站台（site）及賽事 ID（gid），從 Cassandra 查詢並回傳單場或多場次的主要賠率。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/price/{gtype}` | 依球種查詢單場或多場賽事的主要賠率。 |

需人工確認：此路徑為推測，實際路由定義需核對 `src/server.py` 或 `router.py`。

---

## 3. 流程總覽

1. 接收查詢請求，包含 `gtype`（球種）、`site`（站台）、`play_type`（玩法）及 `gid`（賽事 ID，可多筆）。
2. 驗證必要參數。
3. 根據 `site` 動態決定 Cassandra keyspace 中的目標表名：`sitegames_{gtype}` 或 `games_{gtype}`。
4. 連線 Cassandra `pricecenter` keyspace。
5. 組合查詢條件 `WHERE site=? AND gid IN (...)`，讀取符合條件的賽事賠率資料。
6. 過濾並組裝主要賠率（僅回傳 `play_type` 指定的玩法賠率）。
7. 記錄查詢日誌（透過 Kafka）。
8. 回傳結果。

---

## 4. 程式流程

需人工確認：以下表格為基於系統架構的推測流程，具體的 Class 與 Method 名稱需核對程式碼。

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `PriceController.get_price` | 接收請求，提取 `gtype`, `site`, `play_type`, `gid`。 |
| 2 | Validator | `PriceValidator.validate` | 驗證參數格式，`gid` 不可為空，`gtype` 與 `play_type` 為必要。 |
| 3 | Service | `PriceService.get_real_time_odds` | 組裝查詢條件，呼叫 Provider。 |
| 4 | Provider | `CassandraProvider.execute` | 組裝 CQL，執行對 `pricecenter` 的讀取。 |
| 5 | Transfer | `OddsTransfer.to_response` | 將 DB row 轉換為 response DTO，過濾不可暴露欄位。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `pricecenter`.`sitegames_{gtype}` | Read | 讀取單一或多場賽事的主要賠率資料。 |
| DB | Cassandra `pricecenter`.`games_{gtype}` | Read | 依球種讀取賽事主要賠率。 |
| Queue | Kafka | Publish | 發送查詢行為日誌，供監控或歷史追蹤。 |

需人工確認：根據 `sitegameoddservice-detail.md`，本服務明確未使用 Redis。

---

## 6. 重要規則

- **資料庫權限限制**：本服務對於 `pricecenter` 的 `sitegames_{gtype}` 與 `games_{gtype}` 為**唯讀**。嚴禁任何寫入操作。
  - **證據**：`sitegameoddservice-detail.md` > pricecenter > 寫入限制。
- **欄位限制**：查詢時應避免 `SELECT *`，結合 `site`、`gid` 作為條件。
  - **證據**：`sitegameoddservice-detail.md` > pricecenter > 讀取規則。
- **不可回傳欄位**：`accounts_*.password`, `accounts_*.handler`, `accounts_*.phone` 絕不可暴露。
  - **證據**：`pricecenter-detail.md` > Table: accounts_{brand}。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 缺少必要參數（如 `gtype` 或 `site` 為空） | 回傳 400 Bad Request，提示缺少必要參數。 |
| `gid` 不存在或不符合條件 | 回傳 200 OK 但清單為空，不應回傳 `404`。 |
| Cassandra 連線失敗或查詢逾時 | 回傳 503 Service Unavailable，並記錄錯誤日誌。 |
| 請求不支援的 `gtype` 或對應的表不存在 | 回傳 400 Bad Request，提示不支援的球種。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | API Test | 提供有效 `gtype`, `site`, `play_type`, 單一 `gid` | 回傳對應賽事的單筆賠率。 |
| T2 | API Test | 提供有效參數，多個 `gid` | 回傳多筆賽事賠率組成的清單。 |
| T3 | Flow Test | Cassandra 端無符合的 `gid` 資料 | 回傳成功，但資料陣列為空。 |
| T4 | Permission Test | 嘗試對 `sitesgames_{gtype}` 使用非 GET 方法 | 預期框架自動拒絕或回傳 405 Method Not Allowed。 |

需人工確認：缺少針對特定玩法（`play_type`）篩選準確性的自動化測試情境。

---

## 9. 高風險區域

- **高風險 Table**：`pricecenter.sitesgames_{gtype}` 及 `games_{gtype}`。
  - 原因：多個外部服務（feed service）會直接寫入資料，若寫入延遲或錯誤，本服務回傳的將是過時或不正確的賠率。
- **Cache consistency**：本服務未使用 Redis 快取賽事資料，故無此風險。讀取的一致端賴 Cassandra 的設定。
  - **證據**：`sitegameoddservice-detail.md` > Redis。

---

## 10. 常見錯誤

- ❌ 在賠率查詢流程中直接 UPDATE `accounts_*.password` 或 `accounts_*.enabled`。
  - **證據**：`sitegameoddservice-detail.md` > 常見錯誤。
- ❌ 讀取 `sitesgames_{gtype}` 時未使用 `site` 或 `gid` 過濾條件，導致全表掃描。
  - **證據**：`sitegameoddservice-detail.md` > pricecenter > 讀取規則。
- ❌ 未正確處理 `gtype` 對應的表，導致查詢失敗或查錯表。

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 服務職責 | `README.md` > 主要功能 |
| DB 角色與限制 | `sitegameoddservice-detail.md` > pricecenter > 讀取規則 |
| 技術棧 (Cassandra) | `README.md` > 技術棧 |
| 未使用 Redis | `sitegameoddservice-detail.md` > Redis |
| 入口 API | 需人工確認，請參考 `src/server.py`。 |