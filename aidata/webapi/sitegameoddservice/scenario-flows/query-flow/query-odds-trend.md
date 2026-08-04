# 查詢賠率走勢

## 1. 場景目的
根據指定的球種、玩法、站台及賽事 ID，從 Grafana Loki 日誌系統中擷取歷史賠率記錄，經過解析與整理後，回傳賠率隨時間變化的序列，用於前端繪製如 HA (香港盤)、OU (大小盤) 等玩法的賠率走勢圖。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/odd-trend` | 查詢指定賽事玩法的賠率走勢 |

---

## 3. 流程總覽
1. 接收含有 `site`, `gid`, `gtype`, `mtype`, `date` 等參數的 GET request。
2. 根據 `gtype` (球種) 與 `mtype` (玩法) 組裝 Loki 查詢所需的 LogQL 標籤。
3. 調用 Loki HTTP API，查詢指定時間範圍內的賠率日誌。
4. 解析 Loki 回傳的日誌串流，提取 `datetime` 與 `oddsvalue`。
5. 根據玩法類型 (`HA`, `OU` 等) 對賠率值進行結構化整理。
6. 將整理後的時間序列數據回傳。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `TrendController` / `odd_trend` | 接收並驗證請求參數 (`gid`, `gtype`, `mtype` 等)，調用 Service。 |
| 2 | Service | `TrendService` / `get_odd_trend` | 組合 Loki 查詢語句，調用 Loki Provider，並處理回傳的資料流。 |
| 3 | Provider | `LokiProvider` / `query_range` | 封裝對 Loki API `loki/api/v1/query_range` 的 HTTP 請求，取得原始日誌 JSON。 |
| 4 | Transfer | `TrendTransfer.to_trend_vo` | 將原始日誌中的 JSON 字串反序列化，提取並組裝成純時間與物件的結構。 |
| 5 | Transfer | `TrendTransfer.parse_trend` | 根據玩法對賠率物件進行扁平化處理（如將 `h`, `a`, `o`, `u` 拆分成陣列）。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| 外部 API | Loki | Read | 查詢歷史賠率日誌。目前發現服務不直接讀取 Cassandra `pricecenter` 或 `predict`，僅作為日誌查詢的代理。 |

---

## 6. 重要規則
- **參數限制**：`gid` 為必填，`gtype` (球種代碼，如 `FT`、`BK`) 與 `mtype` (玩法，如 `HA`、`OU`) 決定 Loki 標籤過濾條件，不可為空。
- **時間範圍**：查詢通常鎖定在賽事進行的日期範圍內，避免全表掃描式查詢 Loki，影響效能。
- **Loki 相依性**：此功能完全依賴 Loki 的日誌完整性，若日誌未正確推送至 Loki (如 Kafka 故障)，將無走勢資料。
- **不可回傳欄位**：不應直接回傳 Loki 原始日誌行中的其他內部資訊 (如 `account`, `handler` 等)，僅可回傳時間與賠率值。
- **玩法特化處理**：賠率走勢會根據玩法判斷是單一值 (如大小盤) 還是雙物件 (如讓分盤的主客)，再由 Transfer 層輸出統一的 `Trend` 結構。
- **需人工確認**：目前並未發現此流程有調用 Redis 快取，若請求頻繁可能導致 Loki 負載過高，需確認是否有快取策略或限制機制。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 缺少必填參數 (`gid`, `gtype`, `mtype`) | 返回 400 Bad Request，提示參數缺失。 |
| 指定的 `date` 格式不正確 | 返回 400 Bad Request，提示日期格式錯誤。 |
| Loki 端點無回應或超時 | 返回 502 Bad Gateway 或 504 Gateway Timeout，提示外部服務異常。 |
| Loki 回傳成功但無數據 (空串流) | 返回 200 OK 並帶有空陣列 `[]`。 |
| 日誌內容格式損毀無法解析 | 記錄錯誤日誌，跳過該筆損毀數據，返回可解析的部分或空陣列。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-01 | Flow Test | 提供有效 `gid`/`gtype`/`mtype`，且 Loki 有正常日誌 | 成功回傳結構化走勢陣列。 |
| UT-02 | Flow Test | 提供有效參數，但 Loki 查無資料 | 成功回傳空陣列 `[]`。 |
| UT-03 | API Test | 請求缺少 `gid` | 返回 400。 |
| UT-04 | API Test | 請求缺少 `mtype` | 返回 400。 |
| UT-05 | Integration Test | 模擬 Loki 返回 500 錯誤 | 系統返回 502 或 504，並記錄錯誤日誌。 |
| UT-06 | Flow Test | 模擬 Loki 返回包含部分損毀 JSON 的日誌 | 成功回傳，損毀資料被跳過，僅包含正常資料。 |

---

## 9. 高風險區域
- **外部依賴**：此服務作為資料聚合層，極度依賴 Loki 的可用性，沒有任何 Cassandra 層的 Fallback 機制。
- **Loki 查詢效能**：不當的 LogQL 查詢範圍若無日期過濾或 `limit` 機制，可能造成 Loki 查詢負擔過重，拖垮整個日誌查詢叢集。
- **日誌格式耦合**：解析邏輯緊密耦合於寫入端 (如 feed service) 的日誌格式，一旦日誌 schema 變更而此服務未同步更新，將導致永久解析失敗。

---

## 10. 常見錯誤
- 新人容易將此功能與「即時賠率」混淆，即時賠率是直接從 Redis/Cassandra 撈取，而走勢是從 Loki（歷史）撈取。
- 在沒有確認 Loki 是否有日誌的情況下，直接宣稱資料遺失，未先檢查上游 feed 服務是否正常推送日誌。
- 誤解 `gtype` 與 `mtype` 參數的對應關係，導致 LogQL 標籤過濾錯誤，查不到資料。
- 認為此 API 會回傳 Cassandra 裡的賠率，實則僅查詢 Loki。

---

## 11. Evidence
| 類型 | 來源 |
|---|---|
| API | `TrendController.odd_trend` |
| Code - Service | `TrendService.get_odd_trend` |
| Code - Provider | `LokiProvider.query_range` |
| Code - Transfer | `TrendTransfer.parse_trend` |
| Data Source | Loki (Grafana Loki HTTP API) |