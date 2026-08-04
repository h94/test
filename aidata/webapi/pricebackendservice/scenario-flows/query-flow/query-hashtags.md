# 查詢 HashTag

## 1. 場景目的
提供後台管理人員查詢指定遊戲類型（GameType）的社群 HashTag 資料。用於後續管理或關聯參考，屬於唯讀查詢流程。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/community/hashtags/{gameType}` | 查詢指定遊戲類型的 HashTag，需驗證 |

---

## 3. 流程總覽

1. 後台前端發出 GET 請求
2. `pricebackendservice` 驗證請求權限
3. 呼叫下游 `communityservice` REST API
4. **不直接寫入 DB**：`pricebackendservice` 角色僅為 reader（參見 community-detail.md）
5. `communityservice` 從 Cassandra `community` keyspace 讀取資料
6. 回傳 HashTag 列表

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `CommunityController.GetHashTags` | 接收 GET 請求，取得 `gameType` 參數 |
| 2 | Service | `ICcommunityService.GetHashTags(gameType)` | 呼叫對應的社群服務介面 |
| 3 | Provider | `CommunityServiceProvider.GetHashTags(gameType)` | 透過 HTTP Client 向 `communityservice` 發起請求 |
| 4 | External | `communityservice` API | 讀取 DB，組裝並回傳 HashTag 資料 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `community` keyspace | Read | 由 `communityservice` 操作，`pricebackendservice` 不直接讀寫 |
| Cache | 無 | - | 根據現有 detail 文件，此功能未使用 Redis |
| Queue | 無 | - | 未使用 Kafka 或其他訊息佇列 |

---

## 6. 重要規則

- **唯讀限制**：`pricebackendservice` 對 `community` keyspace 僅有 `SELECT` 權限，不得執行任何寫入操作（參見 community-detail.md）。
- **權限限制**：所有對 `/api/v1/community/*` 的請求皆需要驗證（✅）。
- **跨服務依賴**：實際資料查詢邏輯完全由 `communityservice` 處理，本服務僅作為 BFF 層轉發。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未帶驗證或 token 失效 | 回傳 401 Unauthorized |
| gameType 參數為空或不存在 | 需人工確認：可能回傳空陣列或 404 |
| `communityservice` 無回應或超時 | 觸發重試機制或回傳 502/504 錯誤 |
| 下游回傳非 2xx 狀態碼 | 將錯誤狀態碼與訊息轉發給前端 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| CHT-01 | Permission Test | 無 token 請求 | 回傳 401 |
| CHT-02 | API Test | 使用有效 token 查詢存在的 gameType | 回傳 200，並包含對應的 HashTag 陣列 |
| CHT-03 | API Test | 查詢一個沒有 HashTag 的 gameType | 回傳空陣列 `[]` |
| CHT-04 | Flow Test | 模擬下游社群服務掛掉 | 回傳 5xx 錯誤 |

---

## 9. 高風險區域

- **跨服務資料同步**：資料來源完全依賴下游 `communityservice`，任何 Schema 或邏輯變動都可能導致查詢失敗。
- **一致性**：目前無快取機制，每次查詢皆穿透至下游與 DB，不涉及快取一致性問題。

---

## 10. 常見錯誤

- **誤認為直接存取 DB**：新人可能嘗試在 `pricebackendservice` 中直接寫 SQL，這是**錯誤**的，所有操作必須透過 Service/Provider 呼叫下游。
- **權限誤判**：後端常忘記此類查詢 API 也需驗證，導致未登入即可存取。
- **AI 誤解**：AI 可能誤認 `pricebackendservice` 對 `community` keyspace 有寫入權限（實際上僅為 reader），導致生成錯誤的 Plan。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由 | `README.md` — `GET /api/v1/community/hashtags/{gameType}` |
| DB 角色 | `community-detail.md` — 服務角色總覽: pricebackendservice 為 reader |
| 服務職責 | `README.md` — 「不直接存取資料庫」 |
| 技術架構 | `README.md` — 「資料庫：無直接 DB 存取」 |