# 取得所有運動站台文章

## 1. 場景目的
返回系統中全部運動站台文章列表，供前端或編輯後台無過濾條件地瀏覽所有文章。此介面不提供任何篩選參數，直接從資料庫讀取並回傳完整的文章清單。

## 2. 入口 API
| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sportarticles` | 取得全部運動站台文章，需要驗證 |

## 3. 流程總覽
1. API Gateway 預先驗證 JWT，請求抵達 Controller。
2. Controller 呼叫 SportArticlesService 處理查詢，無需任何業務過濾參數。
3. Service 層調用 DataProvider，從 Cassandra 的 `sportarticles` 表讀取所有文章記錄。
4. 查詢結果在回傳前被映射為 DTO，遮蔽 `content` 與 `link` 等不可對外暴露的欄位。
5. 回傳包含 `id`、`date`、`title`、`addtime`、`lang`、`sourcesite` 等基本欄位的文章列表。

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | 需人工確認.controller.GetAllArticles | 接收 GET 請求，呼叫 Service |
| 2 | Service | 需人工確認.service.SportArticlesService.GetAll | 調用 DataProvider 讀取全部文章 |
| 3 | DataProvider | 需人工確認.data.SportArticlesDataProvider.GetAll | 執行 `SELECT id, date, title, addtime, lang, sourcesite FROM sportarticles`（或等價操作） |
| 4 | Service | 需人工確認.service.SportArticlesService.GetAll | 將 DB 實體映射為 DTO，過濾 `content`、`link` 等不可回傳欄位 |
| 5 | Controller | 需人工確認.controller.GetAllArticles | 回傳 `200 OK` 及 DTO 列表 |

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `sportarticles`（Cassandra table） | Read | 讀取全部站台文章記錄，用於回傳列表 |
| Redis | 無 | 無 | 本場景未使用快取 |
| Queue | 無 | 無 | 本場景無佇列操作 |

## 6. 重要規則
- **權限驗證**: 請求必須在 API Gateway 通過 JWT 驗證，newsservice 本身未處理角色或簽發；若驗證失敗則請求不會抵達此 API。
- **不可暴露欄位**: `content`（文章原始內容）、`link`（外部連結）不可直接回傳給前端。回傳 DTO 僅包含 `id`, `date`, `title`, `addtime`, `lang`, `sourcesite` 等基本資訊。
- **無參數查詢**: 此端點無查詢參數，直接讀取全表，預期用於後台管理或內部查詢，不適合前端高頻率呼叫。
- **排序規則**: 需人工確認預設排序欄位（如依 `addtime` 降冪），若未明確定義可能導致前後端不一致。
- **Timeout 與重試**: 若 Cassandra 回應緩慢，Cassandra 客戶端預設的 timeout 將觸發，Service 應回傳 `500 Internal Server Error`；不應在應用層進行自動重試以防止 DB 雪崩。

## 7. 錯誤情境
| 情境 | 預期結果 |
|---|---|
| Cassandra 讀取失敗或 timeout | Service 回傳 `500 Internal Server Error`，並記錄異常 |
| Cassandra 返回空結果（無任何文章） | Service 回傳 `200 OK` 與空列表 `[]` |
| 請求未帶合法 JWT | API Gateway 返回 `401 Unauthorized`，請求不會進入後續流程 |

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| FT-01 | Flow Test | 資料庫存在多筆文章時呼叫 API | 回傳 `200 OK`，列表包含所有對應記錄，且不含 `content`、`link` |
| FT-02 | Flow Test | 資料庫無任何文章 | 回傳 `200 OK`，body 為空陣列 `[]` |
| PT-01 | Permission Test | 無效或過期 JWT 呼叫 API | 收到 `401 Unauthorized` |
| IT-01 | Integration Test | 模擬 Cassandra 連線失敗 | 收到 `500 Internal Server Error`，不應 crash 服務 |
| IT-02 | API Test | 確認回傳 JSON 結構 | 每個物件包含 `id`、`title`、`date`、`addtime`、`lang`、`sourcesite`，無 `content` 或 `link` |

## 9. 高風險區域
| 項目 | 風險說明 |
|---|---|
| 全表查詢 | 無任何過濾條件的全表掃描，若文章數量龐大可能導致 Cassandra 效能問題或大量資料回傳，需人工確認是否有總量限制或分頁設計。 |
| 敏感資料洩漏 | 若 DTO 過濾未正確執行，可能將 `content`、`link` 等欄位暴露給前端，造成內容授權或資安問題。 |
| Cache consistency | 本場景未使用 Redis，但若未來加入快取，需注意快取失效與 DB 寫入之間的一致性問題（常見錯誤：直接回傳過期快取資料）。 |
| DB 單點故障 | Cassandra 為唯一資料來源，若叢集不可用將直接導致 API 失敗，應考慮監控與警報機制。 |

## 10. 常見錯誤
- **❌ 回傳包含 `content` 或 `link`**: 未在 DTO 映射時過濾，導致前端取得不應暴露的欄位。✅ 必須在回傳前排除或設為 `null`。
- **❌ 誤解查詢範圍**: 以為此 API 支援 `gameType` 或日期過濾，實際上為全表查詢。✅ 閱讀 API 規格：`GET /api/v1/sportarticles` 無參數。
- **❌ 未處理空結果**: 當資料表為空時未能回傳空列表，可能導致前端 `null` 例外。✅ 應確保回傳 `[]`。
- **❌ 未設定排序順序**: 直接回傳 Cassandra 預設順序（可能為 Partition Key 雜湊順序），導致前端顯示混亂。✅ 應在查詢時明確 `ORDER BY addtime DESC`（或其他業務定義欄位）。

## 11. Evidence
| 類型 | 來源 |
|---|---|
| API | README.md - 站台文章 `GET /api/v1/sportarticles`，需要驗證 |
| DB Table | `sportarticles`（Cassandra，news keyspace 內，需人工確認實際 table name 及對應 schema） |
| 不可回傳欄位 | newsservice-detail.md - `content`、`link` 對外 API 不應直接傳遞 |
| 欄位清單 | Phase1 code semantics - `sportarticles` 欄位包含 `id`, `date`, `title`, `addtime`, `content`, `link`, `sourcesite`, `tag`, `lang` |
| Code Reference | 需人工確認 - `SportArticlesService`, `SportArticlesDataProvider` 與對應的 Controller method |
| 驗證機制 | README.md - 所有 API 需要驗證；newsservice-detail.md - 驗證由 API Gateway 預先處理 |