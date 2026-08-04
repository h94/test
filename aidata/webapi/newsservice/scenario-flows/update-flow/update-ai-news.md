# 場景：更新 AI 新聞記錄

## 1. 場景目的

允許管理後台或內部服務更新 `ainews` 表中現有 AI 新聞記錄的部分欄位（`anwser`, `reanwser`, `articleid`, `used`），同時確保 `status` 狀態機僅允許遞增（0→1→2）。相同邏輯亦適用於 `ainews_gs` 與 `ainews_lt` 表，但目前 API 僅定義於 `ainews` 路徑。

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/sports/ai/{gtype}/{gdate}/{lid}/{gid}/{llmhashkey}/{status}` | 更新指定主鍵記錄，請求體為 AINews 物件（部分欄位） |

## 3. 流程總覽

1. API Gateway 驗證 JWT（由 authService 處理）。
2. Controller 接收請求，提取路徑參數及 request body。
3. 驗證 `gtype` 合法性與 `status` 整數格式。
4. Service 層依主鍵讀取現有記錄（確認存在）。
5. 檢查狀態機及可修改欄位規則：
   - 若 body 含 `reanwser` 且當前 `status=1`，則自動遞增 status 至 2。
   - 更新 `anwser`, `articleid`, `used` 時不改變 status。
   - 拒絕修改 `question`、主鍵或降低 status。
6. 寫入 Cassandra：更新目標列；若 status 變更，需以新 status 重建記錄（因 clustering key 不可直接 UPDATE）。
7. 回傳成功或錯誤。

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `AINewsController.Put(...)` | 提取參數，呼叫 Service |
| 2 | Service | `AINewsService.UpdateAINews(...)` | 讀取現有記錄、狀態機驗證 |
| 3 | DataProvider | `AINewsDataProvider.GetAINews(...)` | 執行 SELECT，確認記錄存在 |
| 4 | Service | 內部邏輯 | 決定最終 status 及更新欄位 |
| 5 | DataProvider | `AINewsDataProvider.UpdateAINews(...)` | 執行 CQL UPDATE（或 DELETE+INSERT） |
| 6 | Controller | - | 回傳 HTTP 200 |

> **注意**：若 status 變更，因 status 為 clustering key，實際須先刪除舊行再插入新行，需確保原子性（例如使用 Cassandra Batch）。

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `news.ainews` | Read (SELECT) | 取得現有記錄進行狀態檢查 |
| DB | Cassandra `news.ainews` | Update (可能 DELETE + INSERT) | 寫入新欄位值及可能的 status |
| Cache | 無 | - | - |
| Queue | 無 | - | - |

## 6. 重要規則

- **狀態機規則**：
  - `status` 僅允許 0→1→2 遞增，不可回退。
  - 寫入 `reanwser` 時當前 status 必須為 1，並自動將 status 更新為 2。
  - 不允許直接在 request 中變更 status。
- **可更新欄位**：`anwser`, `reanwser`, `articleid`, `used`。
- **不可修改欄位**：`question`（原始提問，不可篡改）、主鍵（`gdate`, `gtype`, `lid`, `gid`, `llmhashkey`）、`llmsettings`、`bets`、`others`。
- **used 規則**：`used` 只能從 0 改為 1，不可重置為 0。
- **敏感欄位不回傳**：API 回應不應包含 `anwser`, `reanwser`, `question`, `llmsettings`, `bets`。
- **跨服務限制**：`zaiservice` 僅有 SELECT 權限；`gamesettingsite` 可能透過獨立管理 API 更新，此路徑限 `newsservice`。

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 主鍵無對應記錄 | 404 |
| Body 含 `question` 等不可更新欄位 | 400 拒絕 |
| 當前 status=0，欲寫入 `reanwser` | 400（狀態不合法） |
| 當前 status=2，欲再寫入 `reanwser` | 400 或忽略 |
| 嘗試將 `used` 從 1 改為 0 | 400 拒絕 |
| 嘗試降低 status | 400 拒絕 |
| `gtype` 不合法 | 400 |
| 缺少必要參數 | 400 |
| 無效 token | 401（由 Gateway 處理） |

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| UT-1 | Unit | 更新 `anwser`，status 不變 | 成功 |
| UT-2 | Unit | 更新 `reanwser`，status=1 | reanwser 寫入，status→2 |
| UT-3 | Unit | 更新 `reanwser`，status=0 | 拋出業務異常 |
| UT-4 | Unit | 更新 `question` | 忽略或拒絕 |
| UT-5 | Unit | 將 `used` 設為 0 | 拒絕 |
| API-1 | Integration | PUT 正確參數更新 `articleid` | 200，DB 值變更 |
| API-2 | Integration | PUT 不存在的 `gdate` | 404 |

## 9. 高風險區域

- **高風險 table**：`ainews`（含 `_gs`, `_lt`），因包含敏感內容且主鍵含 status，更新可能需刪除重建，原子性不足會產生髒資料。
- **高風險 API**：PUT 若狀態檢查有漏洞，可能導致 status 錯誤跳躍或 `reanwser` 內容錯位。
- **Transaction**：Cassandra 無跨行事務，若使用 DELETE+INSERT 需透過 Batch 或 IF 條件確保一致性。
- **Idempotency**：重送相同請求可能重複遞增 `used`，須以當前狀態做條件寫入（例如 `used` 已為 1 則忽略）。

## 10. 常見錯誤

- 直接修改 status 而不透過寫入 `reanwser`，違反狀態機。
- 未過濾回傳內容，將 `anwser` / `reanwser` / `llmsettings` 暴露給前端。
- 忘記同步更新 `ainews_gs` / `ainews_lt` 表（若業務需要）。
- 誤以為可 UPDATE clustering key，實際須重建記錄。

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI: `PUT /api/v1/sports/ai/{gtype}/{gdate}/{lid}/{gid}/{llmhashkey}/{status}` |
| DB Schema | Cassandra `news.ainews` (主鍵含 status) |
| 狀態機定義 | `db/news-detail.md`：status 0→1→2，寫入 reanwser 後觸發 1→2 |
| 可更新欄位 | `db/news-detail.md`：`anwser`, `reanwser`, `articleid`, `used`；`question` 不可篡改 |
| 敏感欄位隱藏 | `db/news-detail.md` 與 `newsservice-detail.md` 列出不可回傳清單 |
| Service 方法 | 語意分析推測 `IAINewsService.UpdateAINews` (需人工確認) |