# 取得近期AI預測新聞

## 1. 場景目的

本場景描述前台使用者請求指定球種（gameType）最近期間的 AI 預測新聞內容與結果。API 會從 `news` Cassandra keyspace 查詢已完成的預測資料，組合對應的聯賽、隊伍名稱與比分等資訊，回傳統一的 `RecentAINews` 結構供前臺展示。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/ainews/lastest/{gameType}` | 取得指定球種的近期 AI 預測新聞 |

**參數**：
- `gameType`（path，string）：球種代碼，限 `SC`（足球）、`BS`（棒球）、`BK`（籃球）。

---

## 3. 流程總覽

1. 接收 `GET /api/ainews/lastest/{gameType}` 請求。
2. 驗證 `gameType` 是否為支援的球種代碼（SC、BS、BK）。
3. 動態計算「近期」日期範圍（例如最近 N 天的賽事日期，確切範圍需人工確認）。
4. 查詢 `news.ainews` — 依 `gdate`、`gtype` 並限定 `status=1`（前台展示規則）擷取可展示的預測記錄。
5. 若有需要，查詢 `news.ainews_gs` 取得對應的補充資訊（含聯賽、隊伍、時間等）。
6. 從 `others` map 解析每筆記錄的背景資訊（如 `league`、`teamA`、`teamH`、`gtime`）。
7. 根據 `status` 及預測邏輯組合最終需回傳的預測封裝物件（含勝負結果 `winLoss`）。
8. 轉換為 `RecentAINews` 陣列回傳。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `AINewsController.GetLatestAINews` | 接收 `gameType` 並呼叫對應 Service 方法 |
| 2 | Service | `IAINewsService.GetLatestAINews`（實際類別需人工確認） | 組合查詢條件與日期範圍計算 |
| 3 | Provider/Data | `AINewsProvider.GetAINewsByGameTypeAndStatus`（名稱需人工確認） | 對 `news` Cassandra 執行 CQL SELECT |
| 4 | Transfer/Util | Mapper 或 Helper（需人工確認） | 解析 `others` map 並組裝 `RecentAINews` DTO |
| 5 | Controller | `AINewsController.GetLatestAINews` | 回傳 `List<RecentAINews>` 並回應 HTTP 200 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `news.ainews` | Read（SELECT） | 查詢指定球種與日期區間且狀態為已回應（status=1）的新聞 |
| DB | `news.ainews_gs` | Read（SELECT） | 取得台站版本（GS）的 AI 文章補充資訊（若預測存在不同平台版本） |
| Cache | （目前未使用） | — | 無 Redis 操作。所有請求直接進 Cassandra |
| Queue | （目前未使用） | — | 場景為純查詢流程，不涉及 Kafka 發布或消費 |

---

## 6. 重要規則

### 權限限制
- 此 API 為公開前台介面，目前資料未顯示需驗證，但實際需人工確認是否有 Token/Guest 驗證介入。

### 欄位限制
- 回傳 **不應包含** `anwser`、`reanwser`、`llmsettings`、`bets` 欄位，這些屬於內部 AI 資料。
- 對外僅提供結構化的預測結果（如 `aiPredicts` 列表）及賽事背景資訊（隊伍、聯賽、時間、比分）。

### 不可暴露資料
- 嚴禁向前台暴露 `anwser`、`reanwser`（AI 原始回答）、`question`（內部提問）、`llmsettings`（LLM 參數）。

### TTL 規則
- 無 Redis Cache TTL，資料直接來自 DB。

### Transaction 規則
- 此場景為純讀取查詢，無跨表 Transaction。

### Retry 規則
- 發生讀取逾時或暫時性錯誤時，呼叫方或服務端應實作常見的冪等重試機制（具體 policy 需人工確認）。

### 狀態值限制
- 前台查詢**僅能讀取 `status=1`**（已回應且無待修正），絕對不可向外部顯示 `status=0`（待處理）或 `status=2`（已修正）。

### 不可修改欄位
- 本流程為查詢，無任何寫入或修改操作。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `gameType` 為空或非 `SC`/`BS`/`BK` 的值 | HTTP 400 Bad Request，回傳無效球種訊息 |
| 找不到該球種近期 `status=1` 的記錄 | HTTP 200，回傳空陣列 `[]` |
| Cassandra 查詢逾時或連線失敗 | HTTP 500 Internal Server Error，前端顯示暫不可用 |
| `others` map 中缺少必要的展示欄位（例如 `league`）| 該欄位可為 null，但整體結構必須正確，不可導致序列化崩潰 |
| 日期範圍計算錯誤致查無資料 | 返回空結果；負責應固定提供「近期」合理的窗口（如 3 天內），避免查詢過期資料庫 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | API Test | 傳入合法 `gameType=SC` | 200，回傳陣列中包含結構正確的 RecentAINews |
| T02 | API Test | 傳入非法 `gameType=XYZ` | 400，提示無效的球種 |
| T03 | Flow Test | 資料庫中有 status=1 與 status=0 的記錄 | 僅回傳 status=1 的項目，不含待處理或修正中 |
| T04 | Schema Test | 檢查回傳 JSON 結構 | 不得包含 `anwser`, `reanwser`, `llmsettings`, `bets` |
| T05 | Flow Test | 資料庫內完全無對應資料 | 200，回傳空陣列 |
| T06 | Integration Test | Cassandra 暫時不可用 | 500，服務應有錯誤處理而非直接崩潰 |
| T07 | Data Integrity | `others` map 缺少 gtime | 對應欄位為 null，但 DTO 應可正常序列化 |

---

## 9. 高風險區域

- **高風險 table**：`news.ainews` — 若未強制帶入 `gdate`（分區鍵）進行範圍查詢可能導致全表掃描，嚴重影響效能。
- **高風險 API**：此 GET API 若沒有快取且流量高，直接撞擊 Cassandra 可能導致熱點。
- **跨服務資料同步**：`ainews` 的寫入由 `newsservice` 或 LLM 回調服務負責。`gamesettingsite` 僅讀取展示，若寫入服務更新結構需同步變更本場景的 DTO 映射。
- **Cache consistency**：目前無快取，風險較低，但若未來引入 Redis 快取，必須確保 status 異動或新資料進入時能主動失效。
- **Queue retry**：無。

---

## 10. 常見錯誤

- ❌ **AI 直接回傳 `anwser` 或 `reanwser` 欄位**：這兩個欄位包含未經包裝的原始 LLM 回答，對外 API 不可直接暴露。
- ❌ **忘記過濾 `status=1`**：導致使用者看到尚未完成 (`status=0`) 或修正中 (`status=2`) 的 AI 草稿。
- ❌ **新人誤以為此 API 會寫入資料**：此為純查詢場景，任何寫入邏輯應由其他管理介面或 LLM 服務觸發。
- ❌ **查詢 ainews 時未指定 `gdate`**：Cassandra 必須提供分區鍵 `gdate`，否則將報錯或做全表掃描（即使業務層相容也不應允許）。
- ❌ **將內部欄位（`llmsettings`, `bets`, `question`）暴露在 OpenAPI schema 外或回傳給前端**：會造成敏感資訊外洩。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 定義 | OpenAPI `paths./api/ainews/lastest/{gameType}.get` |
| 參數定義 | OpenAPI 路徑參數 `gameType`：`SC`, `BS`, `BK` |
| 回傳結構 | OpenAPI `components.schemas.RecentAINews` 與 `AIPredict` |
| DB 結構 | `news.ainews` Cassendra 主鍵 `(gdate, gtype, lid, gid, llmhashkey, status)` |
| 讀取規則 | `gamesettingsite-detail.md` 規定前台展示新聞只讀 `status=1` 記錄 |
| 不可回傳欄位 | `gamesettingsite-detail.md` 寫明 `anwser`, `reanwser`, `llmsettings`, `bets` 不對外暴露 |
| Code | Controller `AINewsController`（需人工確認確切方法名） |
| Code | Model/Transfer `RecentAINews`，`AIPredict` 定義於 OpenAPI 或 Codebase 中 |