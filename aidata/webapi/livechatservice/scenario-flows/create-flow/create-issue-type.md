# 新增問題類型

## 1. 場景目的
客服人員在後台新增一個問題類型（IssueType），系統必須同步寫入 MySQL 與 Redis，確保即時查詢的資料一致性。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/issuetype` | 新增 IssueType 至 MySQL 與 Redis（OpenAPI 摘要） |

---

## 3. 流程總覽
1. 接收 IssueType 請求體（含必要欄位，如 content）。
2. 驗證請求格式與必要欄位。
3. 寫入 MySQL 資料表（推測為 `issuetype` 或類似名稱，需人工確認）。
4. 取得 MySQL 寫入後產生的 ID（若自增主鍵）。
5. 更新 Redis 快取（推測使用 `Issuetype` 快取鍵，需人工確認）。
6. 回傳成功結果（推測為新增筆數或 ID，需人工確認）。
7. 若有 Kafka 日誌，記錄操作。

---

## 4. 程式流程
（因未提供實際程式碼，以下層級為推測，需人工確認）

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `IssueTypeController.Post` | 接收請求，呼叫 Service |
| 2 | Service | `IssueTypeService.Add` | 商業邏輯：驗證、調用 Provider |
| 3 | Provider | `MySqlProvider.InsertIssueType` | 執行 MySQL INSERT |
| 4 | Provider | `RedisProvider.SetIssueTypeCache` | 更新 Redis 快取集合 |
| 5 | Logger | `KafkaLogger.Log` | 非同步記錄操作日誌 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | MySQL（表名待確認） | Write | 持久化儲存問題類型 |
| Redis | Cache | Write | 更新問題類型快取供即時查詢 |
| Kafka | Log Topic | Publish | 記錄新增操作（若啟用） |

---

## 6. 重要規則
- **權限限制**：需後台客服權限（推測，需人工確認）。
- **欄位限制**：請求體必須包含 `content`，否則失敗並回傳 0（OpenAPI PUT 描述暗示相同規則）。
- **不可暴露資料**：無敏感欄位定義，但須注意不洩漏內部錯誤訊息。
- **Transaction 規則**：MySQL 與 Redis 寫入不支援分散式交易，需確保 Redis 更新失敗時有補償機制或重試（需人工確認）。
- **Idempotency**：未提供冪等設計，需人工確認是否允許重複新增相同 content。
- **Redis TTL**：快取可能無 TTL 或與查詢政策相關（需人工確認）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求缺少必要欄位 content | 回傳 0，寫入失敗 |
| MySQL 連線失敗或寫入逾時 | 回傳錯誤，不更新 Redis |
| Redis 連線失敗 | 可能仍寫入 MySQL 但 Redis 快取失效，需人工確認處理策略 |
| 資料庫唯一鍵衝突（如 content 重複） | 需確認是否限制；若有限制，回傳錯誤或覆蓋 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| IT-01 | API Test | 正常新增含 content 的請求 | 回傳 > 0 的成功值；MySQL 與 Redis 均新增該筆 |
| IT-02 | API Test | 缺少 content | 回傳 0，資料未寫入 |
| IT-03 | Integration | MySQL 寫入後 Redis 失敗 | 確認系統行為（可能記錄錯誤但回傳成功，或回滾，需人工確認） |
| IT-04 | Permission | 無權限呼叫 | 回傳 401/403（需人工確認） |

---

## 9. 高風險區域
- **快取一致性**：Redis 更新失敗時，MySQL 已寫入，導致快取與 DB 不一致。
- **資料同步**：本服務未使用訊息佇列進行非同步同步，直接依序寫入，增加延遲與失敗風險。
- **Transaction**：跨儲存層無強制交易，必須仰賴重試或事後補償。

---

## 10. 常見錯誤
- 新人可能未處理 Redis 寫入失敗，導致後續查詢使用舊快取。
- AI 易誤解為使用 Cassandra `ads` 表單，實際 IssueType 操作在 MySQL，非 provided ads DB。
- 忽略 `content` 為必要欄位，測試時傳空值仍預期成功。
- 誤以為 DELETE API 是實體刪除，實際只將 `enabled` 設為 0（OpenAPI 顯示 `enabled=0`）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI `POST /api/v1/issuetype` 摘要 |
| DB 類型 | README「問題類型（Issue Type）管理：資料同步寫入 MySQL 與 Redis」 |
| Redis | README「透過 Redis 儲存…問題類型……資料同步寫入 MySQL 與 Redis」 |
| 必要欄位 | OpenAPI PUT 描述：「若無 content 則失敗-回傳0」推論 POST 同規則 |
| Kafka | README「使用 IKafkaLogger 記錄服務運作日誌」 |

---

**需人工確認**：
- MySQL IssueType 資料表結構與主鍵型態。
- Redis 儲存結構（Set / Hash / String）與鍵名。
- 失敗時的補償機制（回滾、重試或記錄）。
- 權限驗證機制與角色。