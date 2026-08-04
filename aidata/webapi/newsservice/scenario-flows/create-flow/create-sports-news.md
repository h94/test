# 新增運動新聞

## 1. 場景目的

爬蟲或內部服務調用此 API，將抓取到的運動新聞寫入對應球種的動態表 `sports_{gameType}`。`addtime` 欄位由服務內部自動設定，不接受外部傳入，以確保資料時間的一致性。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/sports/{gameType}` | 新增特定球種的運動新聞 |

---

## 3. 流程總覽

1. API Gateway 預先驗證請求方身份（JWT / 內部服務 Token）
2. Controller 接收 `gameType` 路徑參數與 `SportsNews` 陣列請求體
3. Validator 驗證 `gameType` 是否為已定義的有效球種（如 `SC`、`BK`）
4. NewsService 呼叫 DataProvider 將新聞批次寫入 `sports_{gameType}` 資料表
5. DataProvider 寫入時，對每一筆新聞：
   - 自動填入當前 UTC 時間戳至 `addtime` 欄位
   - 其餘欄位按請求內容直接寫入
6. 回傳寫入成功結果

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | SportsController.PostSports | 接收 gameType 與 sports 陣列 |
| 2 | Validator | SportsValidator.ValidateGameType | 驗證 gameType 為合法球種代碼 |
| 3 | Service | ISportsNewsService.AddSports | 調用 DataProvider 執行批次寫入 |
| 4 | DataProvider | NewsDataProvider.AddSports | 動態組合表名 `sports_{gameType}` 寫入 Cassandra |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `sports_{gameType}` | Write | 寫入爬蟲新聞，`addtime` 由服務自動填入 |

--- 
## 6. 重要規則

- **權限限制**：僅限內部服務調用，API Gateway 負責 mTLS 或 JWT 驗證，服務本身不做二次鑑權。  
- **欄位限制**：  
  - `id` 為唯一主鍵，由 client 端基於 content link hash 生成並提供，重複寫入會導致主鍵衝突。  
  - `addtime` 為服務內部自動帶入的寫入時間戳，外部傳入值會直接被忽略或複寫。  
  - `content`、`link`、`tag` 允許寫入但不對一般用戶回傳（唯讀場景規則）。  
- **不可修改欄位**：`id` 為寫入後不可變動主鍵，`addtime` 不接受外部指定，所有其他欄位由請求決定。  
- **Transaction 規則**：Cassandra 不支援多行交易，單一批次寫入僅保證原子性於 partition 層級；若部分行寫入失敗，需由 caller 自行重試。  
- **TTL 規則**：無預設 TTL（`default_time_to_live = 0`），新聞永久保存。  
- **狀態值限制**：目前無狀態欄位。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `gameType` 無效（不在合法列表） | 400 Bad Request，回傳無效球種錯誤 |
| 請求體為空陣列 | 成功但無寫入（或 200 OK） |
| 新聞 `id` 重複 | Cassandra 因主鍵衝突傳回 WriteError，回應 409 Conflict |
| DB 寫入 timeout | 500 Internal Server Error，需 caller 重試 |
| 缺少驗證 Header | API Gateway 攔截，回應 401 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SPORTS-01 | Flow Test | 寫入一筆合法籃球新聞 | 200 OK，DB 查詢得到記錄且 `addtime` 不為空 |
| SPORTS-02 | API Test | 使用無效 `gameType`（如 "xxx"） | 400，驗證錯誤 |
| SPORTS-03 | API Test | 傳入非陣列 JSON | 400，模型繫結錯誤 |
| SPORTS-04 | Data Test | 檢查寫入後 `addtime` 為服務端時間且不等於 0 | 資料正確 |
| SPORTS-05 | Idempotency Test | 重送同一筆 `id` 的新聞 | 409，主鍵衝突 |
| SPORTS-06 | Security Test | 未帶 Token 請求 | API Gateway 返回 401 |

---

## 9. 高風險區域

- **高風險 table**：`sports_{gameType}` 動態表，因為表名由外部輸入拼接，必須強制過濾字元避免 SQL Injection（Cassandra CQL 嚴格，仍建議做白名單校驗）。
- **高風險 API**：`POST /api/v1/sports/{gameType}` 開放寫入權限，需確保只有授權內部服務能呼叫。
- **Cache consistency**：無 Redis，每次查詢直接讀庫；寫入後無快取不一致風險。
- **Queue retry**：無使用 Queue，失敗需上游 crawlerService 自行重試。

---

## 10. 常見錯誤

- ❌ **誤將 `addtime` 傳入 request body 且預期被儲存** → ✅ `addtime` 以服務端時間為準。
- ❌ **對 `gameType` 未做防禦校驗，直接拼接 SQL** → ✅ 必須使用白名單驗證合法球種代碼。
- ❌ **以為寫入失敗會自動 rollback 整批資料** → ✅ Cassandra 無交易保證，批次內的失誤僅影響該行。
- ❌ **傳入陣列忘了加 `[ ]`，直接塞物件** → ✅ API 必須接受陣列格式。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/sports/{gameType}` [README.md](#) |
| DB | `sports_{gameType}` 動態表 [newsservice-detail.md](#) |
| DB 規則 | `id` 主鍵唯一，`addtime` 內部填入 [newsservice-detail.md](#) |
| Code | SportsController → INewsService → NewsDataProvider [source-code-batch1](#) |
| Validator | ValidateGameType 白名單驗證 [source-code-batch3](#) |