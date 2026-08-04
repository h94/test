# 建立聯賽 HashTag

## 1. 場景目的
為指定遊戲類型與聯賽建立社群 HashTag，讓前端用戶可在社群發文時快速標記聯賽。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/community/hashtags/leagues/{gameType}/{lid}` | 建立聯賽 HashTag |

---

## 3. 流程總覽

1. 管理員經由後台管理介面觸發建立 HashTag 請求
2. `pricebackendservice` 接收 HTTP POST 請求
3. 進行參數驗證與身份認證（ECFramework.ECService）
4. 調用下游 `communityservice` REST API 建立 HashTag
5. 返回操作結果給後台管理介面

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `CommunityController.CreateLeagueHashTag` | 接收請求，驗證參數與權限 |
| 2 | Service | `CommunityService.CreateLeagueHashTag` | 調用 Provider 層進行業務處理 |
| 3 | Provider | `CommunityProvider.CreateLeagueHashTag` | 組合資料並發送 HTTP 請求至 `communityservice` |
| 4 | External | `POST [communityservice]/api/v1/community/hashtags/leagues/{gameType}/{lid}` | 建立聯賽 HashTag |

> **需人工確認**：因 raw code 未提供，上述 Class/Method 名稱為根據架構慣例推測，請以實際程式碼為準。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| HTTP | `communityservice` | POST | 建立 HashTag 紀錄 |
| Cassandra | `community.*` (推測) | Write | 儲存 HashTag 資料於 `communityservice` DB |
| Cache | 無 | — | — |
| Queue | 無 | — | — |

> **需人工確認**：`communityservice` 內部資料表結構未在提供的 DB Schema 中明確定義用於儲存 HashTag 的表，需確認實際表名（可能為 `newlottery_forums` 或獨立 HashTag 表）。

---

## 6. 重要規則

- **權限限制**：僅後台管理員可操作，需通過 ECFramework.ECService 驗證。
- **欄位限制**：`gameType` 與 `lid` 為必填路徑參數。
- **不可暴露資料**：無直接暴露 DB 資料。
- **Transaction 規則**：無跨服務交易，僅單一 HTTP 呼叫 `communityservice`。
- **狀態值限制**：無。
- **不可修改欄位**：`gameType` 與 `lid` 為路徑參數，不可於 API 內變更。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未通過權限驗證 | 回傳 401 Unauthorized |
| `gameType` 或 `lid` 格式無效 | 回傳 400 Bad Request |
| `communityservice` 呼叫失敗 | 回傳 502 Bad Gateway 或 500 Internal Server Error |
| 聯賽 HashTag 已存在 | `communityservice` 可能回傳 409 Conflict 或成功（冪等處理），**需人工確認** |
| 聯賽不存在（若 communityservice 內部需驗證） | `communityservice` 可能回傳 404 Not Found，**需人工確認** |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| HT-01 | API Test | 使用有效 `gameType` 與 `lid` 建立 HashTag | 201 Created |
| HT-02 | Permission Test | 無效 Token 訪問 API | 401 Unauthorized |
| HT-03 | Flow Test | 重複建立相同聯賽 HashTag | 409 Conflict 或 200 OK（視冪等設計而定）**需人工確認** |
| HT-04 | Integration Test | `communityservice` 停止回應 | 502 Bad Gateway |

---

## 9. 高風險區域

- **`communityservice` 內部資料一致性**：若 `communityservice` 未正確處理重複 HashTag 的冪等性，可能導致資料重複或錯誤。**需人工確認** `communityservice` 的冪等設計。
- **聯賽驗證**：若 `communityservice` 在建立 HashTag 時未驗證聯賽是否存在，可能產生孤兒資料（HashTag 對應到不存在的聯賽）。

---

## 10. 常見錯誤

- **新人容易犯錯**：未確實檢查 `gameType` 與 `lid` 的格式，直接發送請求導致下游錯誤。
- **AI 容易誤解**：誤以為 `pricebackendservice` 直接寫入 Cassandra。實際上僅透過 HTTP 呼叫下游微服務。
- **常見漏檢查項目**：忘記驗證 `communityservice` 返回的 HTTP 狀態碼，僅判斷請求成功與否。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/v1/community/hashtags/leagues/{gameType}/{lid}` |
| 流程 | `pricebackendservice` README 職責說明（作為管理後台 API 聚合層，不直接存取資料庫） |
| 相依服務 | `pricebackendservice` README 服務相依：`communityservice`（社群文章、HashTag 管理） |
| DB 角色 | `pricebackendservice-detail.md`：`pricebackendservice` 對 `community` keyspace 為 reader，僅 SELECT。寫入操作由 `communityservice` (owner) 執行。 |
| 權限 | `pricebackendservice` README API 路由標示為✅需要驗證 |