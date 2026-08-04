# 寫入聯盟合併結果

## 1. 場景目的
接收龍蝦前端設定的聯盟合併目標，將合併結果寫入 Cassandra。包含舊資料去重與合併邏輯，確保各球種的聯盟合併資料正確儲存，用於後續跨站台賽事合併比對。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | /api/merge_league/pending-result/{game_type} | 寫入聯盟合併結果（含舊資料去重合併） |

---

## 3. 流程總覽

1. 接收 POST 請求，包含 `game_type` 路徑參數與合併資料 body  
2. 驗證 `game_type` 是否為支援的球種（SC、BK、BS、FL、HL、ES、TN）  
3. 解析 request body 中的合併目標清單（主聯盟與被合併聯盟）  
4. 查詢 Cassandra 中該 `game_type` 既有的合併結果  
5. 執行去重邏輯：將新合併資料與舊資料合併，去除重複的合併關係  
6. 寫入合併後的結果至 Cassandra（`{table_prefix}mergeleague_{game_type}`，例如 `test_openclaw_mergeleague_SC`）  
7. 回傳成功訊息

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | MergeLeagueController | 接收 POST 請求，解析 `game_type` 與 body |
| 2 | Validator | 需人工確認 | 驗證 `game_type` 是否合法、body 結構是否正確 |
| 3 | Service | MergeLeagueService | 呼叫 Provider 查詢舊合併資料 |
| 4 | Provider | OtherProvider | 讀取 Cassandra 既有合併結果 |
| 5 | Service | MergeLeagueService | 執行去重與合併邏輯 |
| 6 | Provider | OtherProvider | 寫入合併後的結果至 Cassandra |
| 7 | Controller | MergeLeagueController | 回傳成功 response |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `{table_prefix}mergeleague_{game_type}` | Read | 查詢既有合併結果 |
| DB | Cassandra `{table_prefix}mergeleague_{game_type}` | Write (INSERT/UPDATE) | 寫入合併後的聯盟合併結果 |

**注意**：README 提及 Redis 用於異常隊伍快取與服務狀態，但此場景中未發現對 Redis 的操作。Kafka 僅用於日誌傳輸，與此業務流程無直接關聯。

---

## 6. 重要規則

### 權限限制
- 此 API 為內部服務間呼叫（龍蝦前端觸發），需人工確認是否有額外權限驗證（如 API Key 或 Token）。

### 欄位限制
- `game_type` 必須為支援的球種（SC / BK / BS / FL / HL / ES / TN 等），否則應回傳 400 錯誤。
- request body 結構需人工確認（推測包含主聯盟 ID 與被合併聯盟 ID 清單）。

### 不可暴露資料
- 合併結果僅供內部使用，不應對外公開原始站台資料。

### Transaction 規則
- Cassandra 不支援跨表 transaction；此場景操作單一 table，無需 transaction。
- 去重與寫入應在同一邏輯單元中完成，避免部分寫入。

### 狀態值限制
- 合併結果中的聯盟 ID 必須存在於對應的 `leagues_{game_type}` 表中（需人工確認是否實作驗證）。

### 不可修改欄位
- 需人工確認：合併結果表中是否有不可修改欄位（如 `site` 作為 partition key 不可變更）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `game_type` 不合法 | 回傳 400 Bad Request |
| request body 格式錯誤 | 回傳 422 Unprocessable Entity |
| Cassandra 連線失敗 | 回傳 500 Internal Server Error，並透過 Kafka 發送錯誤日誌 |
| 既有合併資料讀取失敗 | 回傳 500 Internal Server Error，記錄錯誤 |
| 寫入 Cassandra 失敗 | 回傳 500 Internal Server Error，記錄錯誤 |
| 合併目標中的聯盟 ID 不存在 | 需人工確認：是否回傳 400 或直接寫入 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| ML-01 | API Test | 合法 `game_type` 與正確 body | 200 OK，資料正確寫入 |
| ML-02 | API Test | 不合法 `game_type`（如 "XX"） | 400 Bad Request |
| ML-03 | API Test | body 格式錯誤 | 422 Unprocessable Entity |
| ML-04 | Flow Test | 寫入新合併資料後再次寫入不同合併資料 | 舊資料與新資料正確合併，無重複 |
| ML-05 | Flow Test | 寫入與既有資料完全相同的合併關係 | 去重後資料不變，無重複寫入 |
| ML-06 | Integration Test | Cassandra 無法連線 | 500 Internal Server Error，日誌記錄 |
| ML-07 | Integration Test | 寫入後查詢 `GET /api/merge_league/league/{game_type}` | 查詢結果反映最新合併狀態 |

---

## 9. 高風險區域

### 高風險 Table
- `{table_prefix}mergeleague_{game_type}`（如 `test_openclaw_mergeleague_SC`）：合併結果直接影響後續賽事合併邏輯，錯誤資料會導致前端顯示異常。

### 高風險 API
- `POST /api/merge_league/pending-result/{game_type}`：寫入操作無 rollback 機制，需確保去重邏輯正確。

### 跨服務資料同步
- 需人工確認：合併結果是否被其他服務（如 merge games）即時讀取，若有，需考慮資料一致性。

### Cache Consistency
- 此場景未使用 Redis，無快取一致性問題。

### Queue Retry
- Kafka 僅用於日誌傳輸，無 queue retry 需求。

### Idempotency
- 去重邏輯確保相同合併關係不會重複寫入，但需人工確認是否實作基於唯一鍵的 idempotency（如 `site + sitelid` 組合）。

---

## 10. 常見錯誤

### 新人容易犯錯
- ❌ 未先查詢既有資料就直接 INSERT，導致舊合併關係被覆蓋  
  → ✅ 必須先讀取舊資料，執行去重合併後再寫入
- ❌ `game_type` 參數未做白名單驗證  
  → ✅ 應驗證 `game_type` 是否在支援清單中

### AI 容易誤解
- ❌ 誤以為此 API 使用 Redis 快取合併結果  
  → ✅ 此場景直接讀寫 Cassandra，無 Redis 操作
- ❌ 誤以為需要跨表 transaction  
  → ✅ Cassandra 單表操作，無需 transaction

### 常見漏檢查項目
- 未驗證 request body 中的聯盟 ID 是否存在於 `leagues_{game_type}` 表
- 未記錄寫入操作的 audit log（需人工確認）

### 常見錯誤流程
- 直接 INSERT 新資料而不處理舊資料，導致合併關係重複或矛盾

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README: `POST /api/merge_league/pending-result/{game_type}` |
| DB | `pricecenter` keyspace, `{table_prefix}mergeleague_{game_type}` (如 `test_openclaw_mergeleague_SC`) |
| Code | `project/Provider/other.py` (推測包含合併結果的讀寫邏輯) |
| Flow | README: "寫入聯盟合併結果（含舊資料去重合併）" |
| DB Schema | `test_openclaw_mergeleague_SC` 欄位: site, sitelid, league, siteidmaps |

---

## 建議新增文件
- **API Request/Response Schema**：需明確定義 `POST /api/merge_league/pending-result/{game_type}` 的 body 格式與 response 結構
- **去重邏輯規格**：需詳細描述新舊資料合併與去重的演算法

## 建議新增規則
- 聯盟 ID 驗證規則：寫入前是否必須驗證聯盟 ID 存在於 `leagues_{game_type}` 表
- Idempotency 規則：若相同 request 重複發送，是否保證結果一致

## 建議新增測試情境
- 大量合併資料寫入的效能測試
- 並發寫入情境下的去重正確性測試