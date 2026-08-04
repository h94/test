# 查詢置頂文章

## 1. 場景目的

查詢指定 `gameType` 下，所有被設定為置頂的文章列表，用於前台社群頁面優先展示重要或熱門內容。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/community/{gameType}/get_top_articles` | 查詢指定遊戲類型下的所有置頂文章 |

- 需要驗證：✅
- 路徑參數 `gameType`：指定遊戲類型（如 `NBA`、`MLB`）

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，提取路徑參數 `gameType`
2. 驗證請求的 `authkey`（由 auth / member service 完成，communityservice 接收已驗證的 authkey）
3. Service 層收到請求後，調用 Provider 查詢該 `gameType` 下的所有置頂文章
4. 需人工確認：查詢來源為 MeiliSearch 或 Cassandra（目前證據指向 MeiliSearch 作為主要查詢引擎）
5. 對回傳的文章列表進行帳號遮蔽處理
6. 回傳處理後的文章列表

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | 需人工確認 | 接收 GET 請求，提取 `gameType` 參數 |
| 2 | Service | 需人工確認 | 調用 Provider 查詢置頂文章 |
| 3 | Provider / Transfer | 需人工確認 | 查詢 MeiliSearch 索引（需人工確認：`community` 索引或特定 `top_articles` 索引） |
| 4 | Transfer | 需人工確認 | 對文章列表中的 `account` 欄位進行遮蔽處理 |
| 5 | Controller | 需人工確認 | 回傳處理後的文章列表 |

- 需人工確認：Controller、Service、Provider 的具體類名與方法名
- 需人工確認：是否涉及從 MeiliSearch 讀取資料後，再從 Cassandra 進行補全（如文章內容）
- 需人工確認：置頂文章在 MeiliSearch 或 Cassandra 中的儲存方式（獨立索引、標記欄位、或獨立 Table）

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| MeiliSearch | `community` 索引 | Read | 需人工確認：查詢已建立索引的置頂文章，篩選條件為 `game_type` + 置頂標記 |
| Cassandra | `community.articles` | Read | 需人工確認：若置頂資訊僅存於 Cassandra，則查詢文章主體 |
| Redis | 無 | - | 根據 `communityservice-detail.md`，community 無使用 Redis 快取 |

- 需人工確認：置頂文章的持久化與索引儲存策略
- 需人工確認：是否有獨立的 `top_articles` MeiliSearch 索引，或是在主索引中透過特定欄位標記

---

## 6. 重要規則

- **權限限制**：需通過 authkey 驗證，但一般登入會員皆可查詢。
- **帳號遮蔽**：對外回傳的文章列表，作者的 `account` 欄位須進行遮蔽處理（如 `name***`），不可回傳完整帳號。（來源：`communityservice-detail.md` 的不可回傳欄位規則）
- **需人工確認**：若文章本身有 `status` 或 `hidden` 欄位，查詢時是否需過濾隱藏或刪除的文章。
- **需人工確認**：置頂文章的排序規則（例如依設定置頂的時間倒序、或依管理員指定的順序）。
- **需人工確認**：`gameType` 的有效範圍與白名單驗證。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未通過驗證（無 authkey） | 回傳 401 Unauthorized 或由上游 auth service 攔截 |
| `gameType` 不存在或為空 | 回傳 422 或 400，提示參數錯誤 |
| 該 `gameType` 下無任何置頂文章 | 回傳空列表或空物件 |
| MeiliSearch 服務無法連線 | 回傳 500 或特定錯誤訊息，需人工確認：是否降級至 Cassandra 查詢 |
| Cassandra 查詢超時（若有直接查詢） | 回傳 500 或特定錯誤訊息 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TOP-01 | API Test | 查詢有置頂文章的 gameType | 回傳置頂文章列表，且帳號已遮蔽 |
| TOP-02 | API Test | 查詢無置頂文章的 gameType | 回傳空列表，HTTP 200 |
| TOP-03 | Permission Test | 未帶 authkey 請求 | 回傳 401 |
| TOP-04 | Flow Test | 查詢文章後檢查作者資訊 | `account` 欄位已遮蔽，無完整帳號 |
| TOP-05 | Integration Test | 設定一篇文章為置頂後立即查詢 | 新置頂文章出現在列表中 |
| TOP-06 | API Test | 傳入無效的 gameType | 回傳 422 或 400 |

---

## 9. 高風險區域

- **帳號資訊暴露**：若未正確遮蔽 `account` 欄位，可能導致個資外洩。此為高風險行為，須在 Transfer 或 Service 層嚴格執行遮蔽邏輯。
- **資料一致性**：需人工確認：設定置頂（PUT `/api/community/{gameType}/top_articles`）後，MeiliSearch 索引是否即時更新。若存在延遲，可能導致查詢結果不一致。
- **MeiliSearch 相依性**：若 MeiliSearch 服務中斷，整個查詢流程將受阻，需人工確認是否有降級機制。

---

## 10. 常見錯誤

- ❌ 查詢置頂文章時未過濾隱藏或已刪除的狀態 → ✅ 需人工確認：查詢時應加上狀態過濾條件（如 `status=1`）。
- ❌ 回傳文章列表時直接暴露 `account` 完整帳號 → ✅ 應統一遮蔽處理，僅回傳遮蔽後的帳號或顯示名稱。
- ❌ 未對 `gameType` 進行白名單驗證，接受任意字串 → ✅ 需人工確認：應定義有效的 `gameType` 列表，並在 Controller 層進行校驗。
- ❌ 新人或 AI 誤認為此 API 是直接查詢 Cassandra → ✅ 需注意 MeiliSearch 為主要查詢引擎，Cassandra 為持久化儲存，但需人工確認在此場景中的實際讀取路徑。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `README.md`：`GET /api/community/{gameType}/get_top_articles` - 查詢置頂文章 |
| 權限 | `README.md`：所有 `/api/community/*` 路由皆需要驗證 ✅ |
| 帳號遮蔽規則 | `webapi/communityservice/communityservice-detail.md`：community 的不可回傳欄位中，`account` 對外 API 一律遮蔽 |
| 無 Redis 快取 | `webapi/communityservice/communityservice-detail.md`：community 無使用 Redis 快取 |
| 查詢引擎 | `README.md`：以 MeiliSearch 作為主要查詢引擎 |
| OpenAPI | `GET /api/community/{gameType}/get_top_articles` 存在於路徑中（需從完整 OpenAPI 文件確認參數與回傳格式） |

- **需人工確認項目**：
    1. 置頂文章的實際儲存位置與查詢方式（MeiliSearch index name / Cassandra table）
    2. 是否有獨立的 `top_articles` 索引或僅透過 `is_top` 等欄位標記
    3. 具體的 Controller / Service / Provider 類別與方法名稱
    4. 排序規則（依時間、依指定順序等）
    5. 是否需要過濾文章狀態（如 `status`、`hidden`）
    6. 對應的程式碼路徑（`controllers/`, `services/`, `providers/` 下的具體檔案）