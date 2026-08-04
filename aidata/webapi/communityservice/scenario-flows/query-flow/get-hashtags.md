# 查詢 HashTag 列表

## 1. 場景目的
依據傳入的 `game_type` 及可選的 `hashtag_type`，從 MeiliSearch **hashtag** 索引中讀取已設定的 HashTag 清單，供前端渲染篩選或文章標記選項。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/community/{game_type}/hashtags` | 查詢指定遊戲類型的 HashTag 列表；`hashtag_type` 可作為 Query 參數進行篩選 |

---

## 3. 流程總覽

1. 接收 GET 請求（含 `game_type` 路徑參數，可選 `hashtag_type` query 參數）
2. 由 API Gateway / Middleware 進行身份驗證（本服務僅接收已驗證的 `authkey`）
3. Controller 將參數傳遞至 Service 層
4. Service 構造 MeiliSearch 查詢，主要過濾條件為 `game_type` 與 `hashtag_type`
5. 透過 MeiliSearch Client 對 **hashtag** 索引進行搜尋
6. 解析 MeiliSearch 回傳的 hits，組裝為 API 回應格式
7. 回傳 JSON 陣列（含 `hashtag_id`、`hashtag_type`、`name` 等欄位）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Middleware | (Auth Middleware) | 驗證 Token / authkey，拒絕未登入請求 |
| 2 | Controller | `HashtagController.GetList` | 接收 `{game_type}` 與 Query String，呼叫 Service |
| 3 | Service | `HashtagService.GetHashtags(game_type, hashtag_type)` | 組合 MeiliSearch 查詢條件 |
| 4 | Provider (Search) | `MeiliSearchClient.index('hashtag').search(...)` | 對 MeiliSearch hashtag 索引發送查詢 |
| 5 | Service | `HashtagService` | 將 hits 轉換為 DTO |
| 6 | Controller | `HashtagController` | 回傳 `200 OK` + JSON data |

> **備註**：確切的 Controller / Service 名稱需人工確認（OpenAPI 片段未包含 hashtag 路由定義，但 README 中明確列出該路由）。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Search Engine | MeiliSearch `hashtag` Index | Read | 全文搜尋 + 篩選，依據 `game_type`、`hashtag_type` 查詢 HashTag 記錄 |
| Cache (Redis) | **無** | - | community 模組目前無使用 Redis 快取，每次查詢皆直接讀取 MeiliSearch |

---

## 6. 重要規則

- **權限限制**：必須為已驗證的使用者（任何登入會員皆可查詢，無需特殊權限）
- **篩選條件**：`game_type` 為必填路徑參數，`hashtag_type` 為可選查詢參數；Service 層應依 `hashtag_type` 追加過濾
- **不可暴露資料**：HashTag 列表不包含任何會員個資，回傳內容可直接供前端使用
- **TTL 規則**：無快取，即時查詢
- **Transaction 規則**：不適用（唯讀流程）
- **Retry 規則**：MeiliSearch 暫時失敗時可進行最多 2 次重試，仍失敗則回傳 502 錯誤
- **狀態值限制**：MeiliSearch 索引中的文件不存在「停用」狀態，僅記錄已設定的 HashTag；刪除操作會直接從索引移除文件
- **不可修改欄位**：本流程僅讀取，無寫入行為

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未帶有效的 Token / authkey | 由 Middleware 攔截，回傳 `401 Unauthorized` |
| `game_type` 為空或不存在於允許清單 | 回傳 `422 Unprocessable Entity`（參數校驗失敗） |
| MeiliSearch 服務無法連線或 timeout | 回傳 `502 Bad Gateway` 或 `500 Internal Server Error` |
| 查詢結果為空 | 回傳 `200 OK` 並附帶空陣列 `[]`，不應回傳 404 |
| `hashtag_type` 傳入非法值（非預定義類型） | 忽略該 filter 或回傳 `422`（視業務需求而定，需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| HT-LIST-01 | API Test | 已登入使用者查詢籃球 `game_type` 的 HashTag，不帶 `hashtag_type` | 回傳 `200`，陣列中包含該 game_type 下所有 HashTag |
| HT-LIST-02 | Permission Test | 未登入（無 Token）請求 | 回傳 `401` |
| HT-LIST-03 | Flow Test | 帶入 `hashtag_type=team` 進行過濾 | 僅回傳符合 `hashtag_type=team` 的結果 |
| HT-LIST-04 | Error Test | MeiliSearch 停止服務 | 回傳 `502` 或 `500`，前端需顯示錯誤提示 |
| HT-LIST-05 | API Test | 查詢不存在的 `game_type`（但 API 接受到） | 回傳空陣列 `[]`，狀態碼 `200` |

---

## 9. 高風險區域

- **搜尋引擎可用性**：MeiliSearch 為唯一資料來源，若服務中斷，HashTag 功能完全無法使用；建議加入監控與降級回應
- **跨服務資料同步**：當後台透過 `POST /hashtags/update` 寫入 MeiliSearch 後，查詢端立即可見，無延遲問題，但需確保寫入時正確設定 `game_type`、`hashtag_type` 等欄位
- **Cache consistency**：無快取，無一致性風險
- **Idempotency**：讀取操作本質上是 idempotent，無額外處理需求

---

## 10. 常見錯誤

- ❌ **未正確處理空陣列**：MeiliSearch 找不到任何文件時，前端可能誤判為錯誤，應確保回傳空陣列而非 null 或錯誤物件
- ❌ **忽略必填的 `game_type` 過濾**：未將 `game_type` 放入查詢條件，導致跨類型資料洩漏（例如籃球版看到足球的 HashTag）
- ❌ **忘記對 MeiliSearch 查詢做重試機制**：瞬斷時直接拋出例外，影響可用性
- ❌ **假設前端不會傳送 `hashtag_type`**：若 API 文件宣稱支援但後端未實作，前端呼叫時將無效，應完整實作篩選
- ❌ **開放 MeiliSearch 的全索引查詢**（未加任何 filter）→ 可能拖垮搜尋引擎效能

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | README > HashTag 管理 `GET /api/community/{game_type}/hashtags` |
| 儲存層 | README > 資料庫重要 Table > MeiliSearch hashtag 索引 |
| 服務相依 | README > 服務相依 > MeiliSearch 用於 HashTag 查詢 |
| 讀取規則 | community-detail.md > 無特別列出，但從用途「依 hashtag_type 篩選」推斷 |
| Cache | communityservice-detail.md > 社群模組無使用 Redis 快取 |
| 認證方式 | communityservice-detail.md > communityservice 僅接收已驗證的 authkey |