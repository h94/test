# 寫入合併結果

## 1. 場景目的

龍蝦前端完成跨站台賽事合併後，將合併結果寫入 Cassandra，供後續查詢使用。API 依球種動態決定目標表名 `{table_prefix}{game_type}`。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/merge/pending-result/{game_type}` | 龍蝦寫入合併結果至 Cassandra |

---

## 3. 流程總覽

1. 接收 POST request，含 `game_type` 路徑參數與合併結果 payload
2. 根據 `game_type` 與 `AppSettings.table_prefix` 決定目標表名
3. 驗證合併結果資料結構
4. 寫入 Cassandra `pricecenter.{table_prefix}{game_type}` 表
5. 透過 Kafka 傳送操作日誌（非同步隊列）
6. 回傳成功或失敗

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | MergeController | 接收 POST request，提取 `game_type` 與 body |
| 2 | Service | MergeService | 驗證資料結構、決定目標表名 |
| 3 | Provider | GamesProvider / SiteGamesProvider | 執行 Cassandra INSERT/UPDATE |
| 4 | Transfer | LoggerTransfer | 非同步寫入 Kafka 日誌 |

> **需人工確認**：實際 Controller / Service / Provider 的 class 與 method 名稱，目前無直接 code evidence，需查閱 `project/` 目錄內具體實作。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `pricecenter.{table_prefix}{game_type}` | Write (INSERT/UPDATE) | 儲存合併後的賽事結果 |
| DB | Cassandra `pricecenter.sitegames_{game_type}` | Read | 讀取站台原始比賽，協助合併比對 |
| DB | Cassandra `pricecenter.games_{game_type}` | Write | 寫入合併後的正式比賽 |
| Queue | Kafka (`49.213.1.158:29096`) | Publish | 非同步傳送操作日誌 |
| Cache | Redis（db=3） | 無直接使用 | 本場景不涉及 Redis 操作 |

> **需人工確認**：目標表是 `games_{game_type}` 或 `sitegames_{game_type}` 或其他表，取決於 `table_prefix` 設定與合併類型。

---

## 6. 重要規則

- **動態表名**：目標表由 `{table_prefix}` + `{game_type}` 組成，不可跨球種寫入。
- **game_type 限制**：僅允許 SC、BK、BS、FL、HL、ES、TN 等已定義球種。
- **資料驗證**：合併結果必須包含完整的比賽識別欄位（id、lid、teamid_h、teamid_a、gdate、gtime 等）。
- **不可回傳密碼欄位**：若合併結果回傳中包含帳號資訊，不得洩漏 password、handler。
- **Kafka 日誌**：操作日誌透過 `TCZB` 套件經 Kafka 非同步傳送，不阻塞主流程。
- **Cassandra 連線**：寫入前須確保 Cassandra 連線已建立（服務啟動時重試 10 次、間隔 5 秒）。

> **需人工確認**：Table 的 Primary Key、Clustering Key 等 Schema 細節，以及是否使用 `IF NOT EXISTS` 語法。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| game_type 不合法 | HTTP 400，回傳錯誤訊息 |
| Cassandra 寫入失敗 | HTTP 500，日誌記錄錯誤 |
| Kafka publish 失敗 | 不影響主流程，日誌寫入本地 queue 待重試 |
| 合併資料格式不符 | HTTP 422，回傳欄位驗證錯誤 |
| Cassandra 連線中斷 | HTTP 503，服務無法寫入 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| MRG-01 | API Test | 寫入合法 SC 合併結果 | HTTP 200，Cassandra 寫入成功 |
| MRG-02 | API Test | 寫入不合法 game_type | HTTP 400 |
| MRG-03 | API Test | 寫入缺少必填欄位 | HTTP 422 |
| MRG-04 | Flow Test | Cassandra 異常時回傳 | HTTP 500，不 crash |
| MRG-05 | Flow Test | Kafka 不可用時仍寫入 DB | HTTP 200，不阻塞 |
| MRG-06 | Data Test | 寫入後查詢驗證 | 資料正確存入目標表 |

---

## 9. 高風險區域

- **動態表名寫入**：`table_prefix` 設定錯誤可能寫入錯誤的表，需人工確認環境變數。
- **Cassandra Write Consistency**：合併結果寫入後，需確認讀取的一致性層級（預設 `LOCAL_QUORUM` 或 `ONE`）。
- **跨球種資料隔離**：務必確保 `game_type` 對應正確的表，避免資料混雜。
- **Kafka 日誌遺失**：若 Kafka 不可用，日誌僅存於記憶體 queue，服務重啟後可能遺失。

---

## 10. 常見錯誤

- ❌ 誤解 `{table_prefix}{game_type}` 為固定表名 → ✅ 表名由環境設定與球種動態決定。
- ❌ 未驗證 game_type 就寫入 → ✅ 應限制允許的球種清單。
- ❌ 合併結果缺少 source 追蹤欄位 → ✅ 需保留來源站台與原本 ID 以供稽核。
- ❌ 忽略 Cassandra TTL 設定 → ✅ 確認表是否有 `default_time_to_live`，避免資料意外過期。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/merge/pending-result/{game_type}`（README） |
| DB Table | `pricecenter.games_{game_type}`、`sitegames_{game_type}`（Source code semantics） |
| Kafka | `49.213.1.158:29096`、`TCZB` 套件（README） |
| Redis | db=3，用於異常隊伍快取，本場景不涉及（README） |
| Cassandra Keyspace | `pricecenter`（README、pricecenter-detail.md） |
| Table Prefix | 由 `AppSettings.py` 環境變數決定（README） |