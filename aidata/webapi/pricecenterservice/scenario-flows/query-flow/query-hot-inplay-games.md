# 查詢熱門進行中賽事

## 1. 場景目的

提供前台使用者查詢當前被後台標記為「熱門」且仍在進行中的賽事列表。此流程為唯讀查詢，完全依賴 Redis，無需存取 Cassandra 或 MySQL。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/games/inplay/hot` | 查詢熱門進行中賽事 |

- 需要驗證：✅
- Evidence：README 熱門進行中賽事段落

---

## 3. 流程總覽

1. 接收查詢請求
2. 通過內部驗證框架 ECFramework.ECService 驗證權限
3. 從 Redis 讀取熱門賽事的識別標記（取得 GID 列表）
4. 根據 GID 列表從 Redis DB5 讀取對應的即時賽事資料（賠率、比分、狀態）
5. 過濾出狀態為 `inplay` 或 `live` 的賽事（確保仍為進行中）
6. 組裝並回傳賽事列表

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Middleware | ECFramework.ECService | 驗證請求權限 |
| 2 | Controller | GameController.GetInplayHotGames | 接收 GET 請求，調用 Service |
| 3 | Service | GameService.GetInplayHotGames | 協調 Redis 讀取與資料組裝 |
| 4 | Provider | RedisProvider / CacheProvider | 讀取熱門標記 Key，取得賽事 GID 列表 |
| 5 | Provider | RedisProvider / CacheProvider | 逐一或批次從 Redis DB5 讀取賽事詳情 |
| 6 | Service | GameService.GetInplayHotGames | 過濾狀態，組裝回傳 DTO |
| 7 | Controller | GameController.GetInplayHotGames | 回傳 JSON 結果 |

- 需人工確認：實際 Controller / Service / Provider 的具體名稱與方法簽章，上述為基於常見 ASP.NET Core 分層慣例推斷

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Redis | `inplay:hot:games`（推測 Key） | Read | 讀取後台設定的熱門賽事標記與 GID 列表 |
| Redis | `{gameType}:{lid}:{gDate}`（DB5） | Read | 根據 GID 讀取賽事即時資料（賠率、比分、狀態） |

- 需人工確認：熱門賽事標記在 Redis 中的確切 Key 名稱與資料結構
- Evidence：README Table 清單 Redis DB5 用途；README 場景 5「寫入 Redis 熱門賽事標記」

---

## 6. 重要規則

- 權限限制：需通過內部驗證，未授權請求應拒絕
- 狀態過濾：必須只回傳狀態為「進行中」的賽事，若熱門標記中的賽事已結束或未開始，不應回傳
- TTL 規則：熱門賽事標記可能設有 TTL，需人工確認過期策略
- 不可暴露資料：賽事資料中的內部識別碼或原始來源資料不應直接暴露
- 欄位過濾：回傳的賽事資料應只包含前台所需的必要欄位

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 請求未攜帶有效憑證 | 401 Unauthorized |
| 權限不足 | 403 Forbidden |
| Redis 連線失敗或逾時 | 500 Internal Server Error 或降級回傳空列表（需人工確認降級策略） |
| 熱門賽事 Key 不存在 | 回傳空列表 `[]` |
| 熱門賽事 GID 對應的賽事資料不存在 | 略過該賽事，不回傳 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| HOT-01 | API Test | 正常查詢，存在熱門進行中賽事 | 200，回傳賽事列表 |
| HOT-02 | API Test | 查詢時無任何熱門賽事 | 200，回傳空列表 `[]` |
| HOT-03 | API Test | 熱門標記存在但賽事已結束 | 200，該賽事不出現在列表中 |
| HOT-04 | Permission Test | 未登入或 Token 過期 | 401 Unauthorized |
| HOT-05 | Integration Test | Redis 連線失敗 | 500 或降級回傳空列表（需人工確認） |
| HOT-06 | Flow Test | 後台設定熱門賽事後，前台立即查詢 | 200，回傳剛剛設定的賽事 |

---

## 9. 高風險區域

- **Redis 可用性**：此 API 完全依賴 Redis，若 Redis 發生故障，整個查詢流程將失敗
- **Cache 一致性**：若後台更新熱門賽事標記，需確保前台查詢能立即取得最新標記（需人工確認是否有 cache 失效機制）
- **資料一致性**：熱門標記中的 GID 與 DB5 中的賽事資料需保持一致；若有賽事被刪除，熱門標記應同步清除

---

## 10. 常見錯誤

- 新人容易犯錯：忘記過濾賽事狀態，將已結束或未開始的賽事一併回傳
- AI 容易誤解：認為此 API 需要查詢 Cassandra 或 MySQL，但根據 README 與場景說明，此為純 Redis 讀取流程
- 常見漏檢查項目：未處理 Redis 連線失敗的例外狀況，導致無回應或 crash
- 常見錯誤流程：未對熱門標記中的 GID 做存在性檢查，直接組裝可能導致 NullReferenceException

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README：GET `/api/v1/games/inplay/hot` |
| DB | README：Redis DB5 `{gameType}:{lid}:{gDate}` 賽事即時資料 |
| DB | README 場景 5：POST `/api/.../hot/...` 寫入 Redis 熱門賽事標記 |
| Code | GameController（推測） |
| Code | GameService（推測） |
| Code | RedisProvider（推測） |