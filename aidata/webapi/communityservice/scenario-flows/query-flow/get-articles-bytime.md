# 後台查詢文章（依時間）

## 1. 場景目的
後台管理員依遊戲類型與時間區間查詢社群文章，用於審核違規內容或管理文章狀態。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/community/backend/{game_type}/articles-bytime` | 後台查詢指定球種、時間範圍內的文章（需驗證） |

---

## 3. 流程總覽

1. 接收請求，由上游 middleware 或 auth 服務驗證 authKey。
2. 檢查使用者是否具備後台管理權限（**需人工確認**：係透過 member 服務讀取角色或 `rank`）。
3. 解析 query 參數：`start_time`、`end_time`（可能為 timestamps）、`page`、`page_size`。
4. 查詢 Cassandra `community.articles` 表，依 `game_type` 與時間區間過濾（**需人工確認**：articles 的 partition / clustering key 設計，以及是否支援範圍掃描）。
5. 遮蔽作者帳號：對外不回傳完整 `account`（僅顯示 username 或遮罩）。
6. 分頁回傳文章清單。

---

## 4. 程式流程（推估，需人工確認實作）

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Middleware | (auth) | 驗證 authKey，注入 current_user |
| 2 | Controller | `BackendArticleController.articles_by_time` | 接收請求參數，調用 Service |
| 3 | Service | `ArticleService.query_by_time_range` | 組裝 CQL 條件，呼叫 Provider |
| 4 | Provider | `CassandraArticleProvider` | 執行 Cassandra 查詢，回傳原始資料 |
| 5 | Transfer | `ArticleTransfer.to_backend_dto` | 遮蔽帳號、格式轉換 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `community.articles` | Read | 依 `game_type` + 時間範圍查詢文章 |
| Cache | Redis | **無**（community 無使用 Redis 快取） | - |
| Queue | Kafka | **無**（僅用於日誌） | - |

---

## 6. 重要規則

- **權限限制**：僅限後台管理員存取（**需人工確認**：角色權限透過 member 服務判斷，或 auth 層級區分）。
- **帳號遮蔽**：對外回傳的文章 author 欄位需遮蔽，不可回傳完整 `account` 或 `authkey`。[Evidence: communityservice-detail.md「討論串/留言帳號遮蔽」]
- **不可回傳欄位**：`user`（authkey）嚴格禁止對外輸出。
- **時間格式**：CQL 查詢應使用 UTC bigint timestamps，前端再轉換。
- **狀態過濾**：後台查詢應包含所有文章（含隱藏/刪除），除非有額外 filter；**需人工確認** articles 表的 `status` 欄位定義。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 缺乏或無效 authKey | 401 Unauthorized |
| authKey 有效但非後台角色 | 403 Forbidden |
| `game_type` 不存在 | 400 或空列表 |
| `start_time` > `end_time` | 400 Bad Request |
| Cassandra 連線失敗 | 500 Internal Server Error |
| 頁碼超出實際頁數 | 回傳空列表 |
| 時間範圍查詢無結果 | 空列表（非錯誤） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | Permission Test | 普通會員請求 API | 403 |
| T2 | API Test | 後台管理員查詢有效時間範圍 | 200，文章列表且帳號已遮蔽 |
| T3 | API Test | 缺少 `start_time` 或 `end_time` | 400 |
| T4 | Flow Test | 查詢無文章的時間段 | 200，空列表 |
| T5 | Integration Test | 資料庫連線中斷 | 500 |

---

## 9. 高風險區域

- **DB 查詢效率**：若 `articles` 表未依時間排序或非 partition key 範圍查詢，可能觸發全表掃描，影響效能。需確認 table schema。
- **帳號遮蔽實作**：若轉換邏輯有誤，可能將完整帳號洩漏至後台 UI。
- **分頁機制**：若未正確處理 page token / limit，可能造成資料缺失或過量。

---

## 10. 常見錯誤

- ❌ 回傳文章時直接暴露 `account` → 應遮罩或使用 username。
- ❌ 將 `authkey` 或內部 `user` 欄位納入 response。
- ❌ 未處理 `start_time` > `end_time` 的非法請求。
- ❌ 未使用 UTC 時間戳比對，導致時區錯誤。
- ❌ 後台查詢未包含隱藏或軟刪除文章，導致管理員無法審核。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | README.md: `GET /api/community/backend/{game_type}/articles-bytime` |
| 帳號遮蔽規則 | communityservice-detail.md「討論串/留言帳號遮蔽」及「不可回傳欄位」 |
| 無 Redis 快取 | communityservice-detail.md「community 無使用 Redis 快取」 |
| 必要驗證 | README 該路由標示「需要驗證」 |
| Cassandra articles 表存在 | README 列出 Cassandra `community.articles` 為社群文章主體 |

> **需人工確認**：articles 表的實際主鍵設計、後台權限驗證機制、及是否支援依時間範圍的 CQL 查詢。