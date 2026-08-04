# 获取Redis中的問題類型

## 1. 場景目的

從 Redis 快取中查詢所有已啟用的 IssueType（問題類型）清單，供聊天前端快速分類客服需求，無需直接存取 MySQL。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | /api/v1/issuetype/cacheredis | 取得 Redis 中快取的 IssueTypes 陣列 |

---

## 3. 流程總覽

1. 客戶端發出 `GET /api/v1/issuetype/cacheredis` 請求
2. Controller 接收請求（無需認證；需人工確認是否有內部 API 閘道認證）
3. Service 層調用 Redis Provider，以固定快取鍵值讀取 IssueType 列表
4. 若快取命中，直接反序列化為 IssueType 陣列並回傳
5. 若快取未命中，回傳空陣列（或觸發從 MySQL 重載快取？需人工確認）
6. 序列化後的 IssueType 陣列以 JSON 格式回傳給客戶端

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `IssueTypeController.GetCacheRedis()` | 接收 GET 請求，無參數，直接呼叫 Service |
| 2 | Service | `IssueTypeService.GetFromRedis()` *推斷* | 呼叫 Redis Provider 讀取特定 key |
| 3 | Provider | `RedisProvider.Get<T>(key)` *推斷* | 對 Redis 執行 `GET` 指令，回傳 JSON 字串或 null |
| 4 | Service | 同上 | 將 JSON 字串反序列化為 `List<IssueType>`，若為空則回傳空列表 |
| 5 | Controller | 同上 | 封裝為 200 OK，回傳 `List<IssueType>` |

> *推斷*：實際類別與方法名稱需人工確認原始碼。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | 固定 key（如 `issue_types`） | Read（GET） | 直接讀取已同步的 IssueType 快取，避免查詢 MySQL |
| MySQL | 無直接操作 | — | 此場景不存取 MySQL；寫入時才會同步 Redis 與 MySQL（需人工確認同步策略） |

---

## 6. 重要規則

- **權限限制**：OpenAPI 未標示認證需求，但實務上可能為內部服務間呼叫或經 API Gateway 驗證。**需人工確認**
- **欄位限制**：回傳的 IssueType 欄位應與 Schema 一致（OpenAPI 定義之 `IssueType` 元件，但未提供細節，需人工確認包含哪些欄位）
- **TTL 規則**：Redis 快取可能設定永不過期，或於寫入時主動刷新。**需人工確認**
- **不可修改欄位**：此為唯讀場景，無修改行為
- **一致性規則**：IssueType 的「新增/修改/刪除」均會同步寫入 Redis，確保快取與 MySQL 一致（README 所述）。但此讀取流程本身不進行檢查，若同步失敗可能回傳過時資料
- **重試機制**：需確認 Redis 連線失敗時是否有 retry 或 fallback（如從 MySQL 讀取）。**需人工確認**

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| Redis 連線失敗 | 回應 500 錯誤或回傳空陣列，視實作而定。**需人工確認** |
| Redis 中無資料（快取遺失） | 可能回傳空陣列，或觸發從 MySQL 重載快取後回傳資料。**需人工確認** |
| 資料反序列化失敗 | 記錄錯誤日誌，回應 500。**需人工確認** |
| 並發寫入導致 Redis 資料暫時不一致 | 讀取可能取得舊版本，若業務允許短暫不一致則無影響；否則應考慮版本檢查。**需人工確認** |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| IT-ISSUE-REDIS-001 | API Test | Redis 中存在有效 IssueTypes 資料 | 回傳 200，內容為正確的 IssueType 陣列 |
| IT-ISSUE-REDIS-002 | API Test | Redis 中無資料（key 不存在） | 回傳 200，空陣列 [] 或觸發重載，狀態碼不應為 500 |
| IT-ISSUE-REDIS-003 | Integration Test | Redis 連線不可用 | 服務應優雅降級（如回傳空陣列或 503），不可 crash |
| IT-ISSUE-REDIS-004 | Flow Test | 寫入一個新的 IssueType 後立即呼叫 `/cacheredis` | 應回傳包含新 IssueType 的列表，確認寫入與讀取一致性 |

---

## 9. 高風險區域

- **快取不一致**：Redis 寫入失敗或延遲可能導致前端看到不正確的問題類型清單，影響客服分類準確性
- **Redis 單點故障**：若 Redis 不可用，此 API 將無法提供服務，除非有 DB fallback
- **反序列化漏洞**：若 Redis 內容被竄改，可能導致反序列化異常；應確保 Redis 僅由內部服務寫入
- **並發寫入競爭**：多個寫入操作同步至 Redis 時需確保原子性，否則可能出現資料覆蓋

---

## 10. 常見錯誤

- ❌ 直接從 MySQL 查詢 IssueType 而忽略 Redis 快取，導致本應減輕 DB 負載的 API 反而增加壓力
- ❌ 使用錯誤的 Redis key（如大小寫不一致），導致永遠讀不到資料
- ❌ 誤以為 `/cacheredis` 回傳的資料即為 DB 最新狀態，而沒考慮同步延遲
- ❌ 在 Redis 中儲存非 JSON 字串或格式不符，造成反序列化失敗
- ❌ 沒有處理 Redis 為空的情形，導致 NullReferenceException

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `LiveChatController` 路由 `GET /api/v1/issuetype/cacheredis`（OpenAPI） |
| Cache | Redis（README：問題類型資料同步寫入 MySQL 與 Redis） |
| Schema | `IssueType` 元件定義於 OpenAPI，但內容未揭露（需人工確認） |
| 業務目的 | 即時客服聊天中需快速取得問題分類，透過 Redis 快取可降載 MySQL（README 功能描述） |

---

> ⚠️ **需人工確認項目**  
> 1. Controller / Service / Provider 具體類別與方法名稱  
> 2. Redis 快取鍵名稱與 TTL 設定  
> 3. Redis 無資料時的回退策略（是否從 MySQL 重載）  
> 4. API 是否需要認證（目前 OpenAPI 無 security 定義）  
> 5. IssueType 資料結構定義（欄位與型態）  
> 6. 同步機制：寫入 MySQL 時如何保證同步至 Redis（Transaction？或先寫 Redis？）  
> 7. 錯誤處理具體實作（Redis 斷線時的行為）