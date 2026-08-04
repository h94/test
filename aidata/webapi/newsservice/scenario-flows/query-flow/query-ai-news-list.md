# 查詢 AI 新聞列表（依日期與類型）

## 1. 場景目的
提供已生成回應的 AI 新聞列表（status=1），供站台前端展示。透過強制傳入日期 `gdate`（分區鍵）與遊戲類型 `gtype`，避免全表掃描，並於回應中過濾敏感欄位。

---

## 2. 入口 API
| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sports/ai/{gtype}/{gdate}` | 查詢通用 AI 新聞（讀取 `ainews` 表） |
| GET | `/api/v1/sports/gsai/{gtype}/{gdate}` | 查詢 GS 站台 AI 新聞（讀取 `ainews_gs` 表） |
| GET | `/api/v1/sports/ltai/{gtype}/{gdate}` | 查詢 LT 站台 AI 新聞（讀取 `ainews_lt` 表） |

三組 API 行為相同，僅查詢的 Cassandra 表不同。參數：`gtype`（球種代碼）、`gdate`（日期字串，例 `2025-03-28`）。

---

## 3. 流程總覽
1. API Gateway 完成 JWT 驗證後將請求轉發至 NewsController。
2. 驗證路徑參數 `gtype` 是否為合法球種代碼（如 SC, FB）。
3. 驗證 `gdate` 格式（預期 yyyy-MM-dd）。
4. 呼叫 `AINewsService.GetDateAINews(gdate, gtype, tableName)`，其中 `tableName` 由路由決定（`ainews` / `ainews_gs` / `ainews_lt`）。
5. Service 調用 `AINewsDataProvider.GetDateAINews` 執行 Cassandra 查詢，條件：`WHERE gdate = ? AND gtype = ? AND status = 1`（僅回已處理的新聞）。
6. 將查詢結果轉換為 `AINewsDto`，排除不可對外暴露的欄位（`question`, `anwser`, `reanwser`, `llmsettings`, `bets`）。
7. 回傳 `200 OK` 與過濾後的列表。

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `NewsController.GetAINews(gtype, gdate)` / `GetAINewsGS` / `GetAINewsLT` | 接收路由參數，調用 Service |
| 2 | Validator | `Validator.ValidateGameType(gtype)` | 檢查 gtype 是否為允許值 |
| 3 | Service | `AINewsService.GetDateAINews(gdate, gtype, tableName)` | 組合查詢條件，呼叫 DataProvider |
| 4 | Provider | `AINewsDataProvider.GetDateAINews(gdate, gtype, tableName)` | 執行 Cassandra CQL：`SELECT * FROM {tableName} WHERE gdate = ? AND gtype = ? AND status = 1` |
| 5 | Transfer | DTO 轉換邏輯（於 Service 或 Controller 內） | 移除敏感欄位後投影至 `AINewsDto` 列表 |

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `news` keyspace | Read | 從 `ainews` / `ainews_gs` / `ainews_lt` 表中查詢已回應的新聞 |
| Cache | Redis | 未使用 | — |
| Queue | Kafka | 未使用 | — |

---

## 6. 重要規則
- **分區鍵強制傳入**：查詢必須包含 `gdate`，否則會導致全表掃描（Cassandra 特性）。API 強制以路徑參數提供。
- **狀態過濾**：前台只顯示 `status = 1`（已回應）的新聞，避免洩漏待處理內容。
- **不可回傳欄位**：`question`, `anwser`, `reanwser`, `llmsettings`, `bets` 必須從回應中完全移除，只回傳 `articleid`, `createtime`, `gid`, `lid`, `gtype` 等元資訊。
- **表名由路由決定**：不同站台對應不同物理表，不可跨表查詢，且表名不可由客戶端任意指定。
- **無 Transaction**：此場景為唯讀查詢，無需交易控制。
- **Retry 規則**：Cassandra 客戶端通常內建自動重試，服務層不設額外邏輯。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|---|---|
| 未提供 `gdate` 或 `gtype` | 404 Not Found（路由不匹配）或 400 Bad Request（參數驗證） |
| `gtype` 不在允許清單中 | 400 Bad Request 並帶有驗證錯誤訊息 |
| 指定日期內無任何已回應新聞 | 200 OK 空陣列 `[]` |
| Cassandra 連線逾時 | 500 Internal Server Error，記錄錯誤日誌 |
| 查詢時未帶 `status=1`（不符前台需求） | 可能回傳 `status=0` 或 `status=2` 的不應顯示資料（屬邏輯錯誤，應由測試確保） |
| 回應未過濾敏感欄位 | 洩漏 `anwser`、`llmsettings` 等資訊，違反安全規則 |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | API Test | `GET /api/v1/sports/ai/SC/2025-03-28` 正常請求 | 200，回傳指定日期與球種的 AI 新聞列表，不含敏感欄位 |
| T02 | API Test | 省略 `gdate` → `GET /api/v1/sports/ai/SC` | 404 Not Found |
| T03 | Permission Test | 無效 JWT 或無權限 | 401 / 403（API Gateway 攔截） |
| T04 | Validation Test | `gtype=XX`（不存在的球種） | 400 Bad Request，錯誤訊息指出無效球種 |
| T05 | Data Test | 資料庫中存在 `status=0` 與 `status=1` 記錄 | 回應僅包含 `status=1` 的記錄 |
| T06 | Data Test | 確認回應中不包含 `anwser`, `question`, `reanwser`, `llmsettings`, `bets` | 所有物件中均無上述欄位 |
| T07 | Flow Test | 模擬 Cassandra 查詢失敗 | 服務回傳 500，前端得到錯誤提示 |

---

## 9. 高風險區域
- **全表掃描風險**：若未來有人在無分區鍵情況下查詢（例如內部批量），將嚴重影響效能。必須嚴格限制。
- **敏感資料外洩**：若 DTO 轉換不完全，可能意外回傳 `llmsettings`（含 API 金鑰雜湊）或 `anwser`（AI 生成內容），對外暴露契約機密。
- **狀態錯誤**：查詢條件若遺漏 `status=1`，可能顯示尚未生成的草稿或修正中的內容，損害使用者體驗。
- **表名混淆**：不同站台的路由未對應到正確的表（如 `/ai` 卻讀取 `ainews_gs`），將造成資料錯亂。

---

## 10. 常見錯誤
- ❌ 新人誤以為可透過 Query String 傳遞 `tableName`，實際上表名由後端路由寫死。
- ❌ 在 DTO 映射時未排除 `reanwser`，誤以為只有 `anwser` 是敏感內容。
- ❌ AI 自動補全時忘記加入 `status=1` 條件，導致將待處理或修正中的新聞也加入回應。
- ❌ 在 OpenAPI 或文件上未標註 `articleid` 之外的回傳結構，前端誤判仍有 `content` 等欄位。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由 | `GET /api/v1/sports/ai/{gtype}/{gdate}` 等三條路徑（OpenAPI） |
| DB 表與主鍵結構 | `news.ainews` 複合主鍵 `(gdate, gtype, lid, gid, llmhashkey, status)` |
| 讀取規則 | `ainews` 查詢「需至少給出 `gdate`（partition key）以免全表掃描」；`status` 狀態機 `1=已回應`（news-detail.md） |
| 不可回傳欄位 | `question`, `anwser`, `reanwser`, `llmsettings`, `bets`（db-usage: newsdetail.md） |
| 驗證 | Controller 側應使用 `Validator.ValidateGameType`（語義推斷，由 phase1 分析結果確認 `gtype` 有效性校驗存在） |
| Provider 方法 | `IAINewsDataProvider.GetDateAINews(gdate)` 用於依日期查詢（phase1 分析）；推斷搭配 `status=1` 過濾 |