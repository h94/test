# 標記 AI 新聞已使用

## 1. 場景目的

前台展示服務使用 AI 預測新聞後，將 `ainews.used` 欄位更新為 1，避免同一則新聞被重複展示。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT / POST | **待人工確認** | 依 DB 規則推測有對應端點，但 OpenAPI 未揭露 |

---

## 3. 流程總覽

1. 前台取得已過濾的新聞列表（`/api/ainews/{gameType}/{date}` 等）。
2. 決定展示特定新聞（由前端或 BFF 邏輯判斷）。
3. 呼叫標記 API，傳遞主鍵資訊（`gdate`, `gtype`, `lid`, `gid`, `llmhashkey`, `status`）。
4. gamesettingsite 接收請求，驗證必須欄位是否存在。
5. 確認目標記錄 `status = 1` 且 `used = 0`。
6. 執行 Cassandra UPDATE：`SET used = 1`。
7. 若更新成功回傳成功碼；若已為 1 視為冪等成功。
8. 發生錯誤時依狀況回傳對應錯誤碼。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `AINewsController`（推測） | 接收 HTTP 請求，驗證參數 |
| 2 | Service | `AINewsService`（推測） | 檢查記錄狀態，組裝 UPDATE CQL |
| 3 | Provider | `AINewsRepository` / `NewsProvider` | 執行 Cassandra 寫入操作 |
| 4 | Provider | 同前 | 處理 `RowSet` 結果 |

> ⚠️ 實際類別與方法待程式碼確認

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `news.ainews`（或 `ainews_gs`, `ainews_lt`） | UPDATE | 將 `used` 欄位設為 1 |

- 本流程**未使用 Redis、Kafka、Queue**。
- 寫入時必須帶完整分區鍵（`gdate`）與全部叢集鍵（`gtype`, `lid`, `gid`, `llmhashkey`, `status`）。

---

## 6. 重要規則

- `used` 僅可由使用方（如 gamesettingsite）透過 `UPDATE SET used=1` 遞增，**不可重設為 0**。
- 寫入前務必確保該記錄 `status = 1`（已回應）且 `used = 0`。
- 對外 API **不得**回傳 `anwser`、`reanwser`、`llmsettings`、`bets` 等欄位。
- 查詢或標記時必須攜帶 `gdate`（分區鍵），否則 Cassandra 可能拒絕執行。
- 此操作不涉及 Transaction，由應用層確保狀態一致性。
- Retry 規則未明，建議實作冪等保護。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 請求缺少 `gdate` 或任何主鍵欄位 | 回傳 400 Bad Request |
| 目標記錄不存在 | 回傳 404 Not Found |
| `status` 不為 1（0 或 2） | 回傳 422 Unprocessable Entity |
| `used` 已為 1 | 視為成功（204 No Content）或回傳 208 Already Reported |
| Cassandra 寫入逾時 | 回傳 503 Service Unavailable，並記錄錯誤 |
| 未授權請求（如外部直接呼叫） | 需依內部安全機制決定，**待人工確認** |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | API Test | 合法請求，`used=0`, `status=1` | HTTP 200/204，DB `used` 變為 1 |
| T2 | API Test | 重複請求（`used` 已為 1） | 成功或 208，DB 維持 1 |
| T3 | API Test | 請求目標 `status=0` | 422 錯誤，`used` 維持 0 |
| T4 | API Test | 缺少必要主鍵 | 400 錯誤 |
| T5 | Integration Test | Cassandra 連線失敗 | 503 錯誤，原始記錄不變 |
| T6 | Permission Test | 使用無權帳號呼叫 | 403 或 401（**待確認**） |

---

## 9. 高風險區域

- **不可逆操作**：`used=1` 一經寫入無法回退，誤標記將影響 AI 重新回答與新聞去重邏輯。
- **多表對應**：根據 `gtype` 可能需要更新不同實體表（`ainews`, `ainews_gs`, `ainews_lt`）—**表名映射規則需人工確認**。
- **並行標記**：無分散式鎖定，可能兩次請求同時標記，但 Cassandra UPDATE 為冪等，風險低。
- **狀態判斷**：若未正確過濾 `status`，可能將未回應或修正中的記錄標記為已使用，破壞後續流程。

---

## 10. 常見錯誤

- ❌ 發起請求時未帶 `gdate`，導致 Cassandra 報錯。
- ❌ 將 `used` 設為 0 試圖重置，違反 DB 邊界。
- ❌ 未先確認 `status=1` 就直接更新，使無效新聞被視為已使用。
- ❌ 回傳標記結果時誤包含 `anwser` 等敏感欄位。
- ❌ 未明確 `gtype` 與實體表的對應關係，寫入錯誤的表。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| DB 寫入限制 | `gamesettingsite-detail.md` § news.ainews.used |
| 服務角色 | `gamesettingsite-detail.md` § 服務角色總覽：gamesettingsite 為 writer |
| 主鍵必要條件 | `news` Schema 定義 (`PRIMARY KEY (gdate, gtype, lid, gid, llmhashkey, status)`) |
| 狀態機限制 | `news-detail.md` § ainews.status：僅遞增不可回退，前台只顯示 status=1 |
| 不可回傳欄位 | `gamesettingsite-detail.md` § 不可回傳欄位 |
| API 路徑 | **需人工確認**，OpenAPI 無對應端點 |