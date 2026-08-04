# 設定熱門進行中賽事

## 1. 場景目的

後台管理員將特定賽事標記為「熱門進行中賽事」，並將設定寫入 Redis 熱門賽事標記，供前端查詢熱門進行中賽事時使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/games/inplay/hot/{gameType}/{lid}/{gDate}/{gid}` | 設定熱門進行中賽事（需驗證） |

（依據：README.md 對外 API 重點 > 熱門進行中賽事）

---

## 3. 流程總覽

1. 接收管理員 POST 請求（攜帶 `gameType`, `lid`, `gDate`, `gid`）
2. ECFramework 驗證權限（需具備管理熱門賽事權限）
3. Controller 將參數交由 Service 層處理
4. Service 層驗證賽事存在性（從 Redis DB5 讀取對應賽事資料）
5. 將賽事標記寫入 Redis 熱門賽事標記（需人工確認）
6. 回傳成功結果給管理員

（依據：README.md 常見使用場景 > 5. 設定熱門進行中賽事）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GameInplayController.SetHotGame` | 接收參數並確認要求，委派給 Service |
| 2 | Service | `GameInplayService.SetHotGame` | 執行賽事驗證與熱門標記寫入 |
| 3 | Provider | `RedisProvider`（需人工確認） | 寫入 Redis 熱門賽事標記 |

（依據：source code semantics phase1 定義了 GameInplayController 與 GameInplayService）

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | DB5（需人工確認） | Read | 驗證賽事是否存在 |
| Redis | DB5（需人工確認） | Write | 設定熱門賽事標記（需人工確認 TTL 與 KEY 結構） |

（依據：README.md 場景描述「寫入 Redis 熱門賽事標記」；Redis DB5 使用描述）

---

## 6. 重要規則

- 權限限制：需 ECFramework 驗證通過方可執行（README.md > 對外 API 重點）
- 欄位限制：`gameType` 必須為系統支援的賽事類型（如 BS, BK）（OpenAPI 定義）
- 不可暴露資料：不需回傳賽事詳細資料，僅需確認寫入成功
- TTL 規則：需人工確認（Redis 熱門賽事標記是否有 TTL 設定）
- Transaction 規則：需人工確認（寫入 Redis 的操作是否需與其他操作構成 Transaction）
- Retry 規則：需人工確認（Redis 寫入失敗時的重試機制）
- 狀態值限制：僅進行中賽事可設定為熱門（需人工確認是否有此限制）
- 不可修改欄位：`gid` 為既有賽事標識，不可修改

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求缺少 `gameType` 參數 | 400 Bad Request |
| 請求缺少 `gid` 參數 | 400 Bad Request |
| 權限不足（非管理員） | 403 Forbidden |
| 賽事不存在（Redis DB5 無此賽事） | 404 Not Found 或自訂錯誤碼（需人工確認） |
| Redis 寫入失敗 | 500 Internal Server Error 或透過重試機制處理（需人工確認） |
| Redis 連線 timeout | 500 Internal Server Error 或 fallback 機制（需人工確認） |
| Kafka publish 失敗 | 不涉及 Kafka，無影響 |
| DB timeout | 不涉及 MySQL，無影響 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| INPLAY-01 | Flow Test | 正常流程：以管理員權限設定熱門賽事 | 200 OK，Redis 熱門賽事標記成功寫入 |
| INPLAY-02 | Permission Test | 以一般使用者權限嘗試設定熱門賽事 | 403 Forbidden |
| INPLAY-03 | API Test | `gameType` 參數為空或無效值 | 400 Bad Request |
| INPLAY-04 | API Test | `gid` 參數指向不存在的賽事 | 404 Not Found 或自訂錯誤碼 |
| INPLAY-05 | Integration Test | Redis 連線失敗時的 fallback 行為 | 依設計 retry 或 500 Internal Server Error |
| INPLAY-06 | Flow Test | 重複設定同一賽事為熱門 | 應為冪等操作，不產生重複標記 |

---

## 9. 高風險區域

- **高風險 table**：無（此場景僅操作 Redis）
- **高風險 API**：POST `/api/v1/games/inplay/hot/{gameType}/{lid}/{gDate}/{gid}`（若 Redis 寫入非冪等，可能導致前端顯示錯誤）
- **跨服務資料同步**：無跨服務同步需求
- **Transaction**：無
- **Cache consistency**：需人工確認 Redis 熱門賽事標記與實際賽事狀態的一致性
- **Queue retry**：無 Queue 使用
- **Idempotency**：需人工確認（重複請求應返回成功而非建立重複標記）

---

## 10. 常見錯誤

- ❌ 未驗證 `gameType` 是否為合法值（導致 Redis key 寫入錯誤位置）
- ❌ 路徑參數順序錯誤（`gameType/lid/gDate/gid` 誤傳為 `gameType/gid/lid/gDate`）
- ❌ 誤解此 API 為「查詢熱門賽事」（應為設定 API，非 GET）
- ❌ 未處理 Redis 寫入失敗，前端卻顯示成功（導致熱門賽事不生效）
- ❌ AI 容易誤解此場景涉及 MySQL 或 Cassandra 寫入（此場景僅操作 Redis）

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `PriceCenterService` API 路由定義 (README.md) |
| DB | Redis DB5 賽事即時資料 (README.md > 資料庫重要 Table) |
| Redis | 熱門賽事標記寫入 (README.md > 常見使用場景 > 5. 設定熱門進行中賽事) |
| Code | `GameInplayController.SetHotGame` (`pricecenterservice` Source Code Semantics) |
| Code | `GameInplayService.SetHotGame` (`pricecenterservice` Source Code Semantics) |
| SQL | 無（此場景不使用 MySQL） |
| Validation | ECFramework.ECService (`pricecenterservice` Source Code Semantics) |
| 需人工確認 | Redis KEY 結構與 TTL 設定 |

---

### 建議新增文件

- `db/redis-usage.md`：記錄所有 Redis 的 KEY 結構、TTL 設定、操作模式，避免歧義
- `spec/inplay-hot-design.md`：記錄熱門賽事的設計決策（冪等性、TTL、驗證規則）

### 建議新增規則

- 應確認 Redis 熱門賽事標記是否為「每次覆寫」或「僅插入不覆蓋」
- 應確認是否需要每日自動清除過期熱門賽事（防止 Redis 累積過多 KEY）

### 建議新增測試情境

- 同一賽事重複設定為熱門時，確保不產生重複標記（Idempotency Test）
- Redis TTL 過期後，前端查詢熱門賽事是否自動移除（Cache Expiry Test）
- 管理員強制清除熱門賽事標記的測試（Delete Flow Test）