# 查詢運動新聞

## 1. 場景目的

前端或後台人員依指定球種（`gameType`）、時間、語言及內部標籤，取得過濾後的運動新聞列表。主要用於「前端站台顯示最新新聞」。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/sports` | 依 `gameType`, `addTime`, `lang`, `tag` 參數過濾查詢運動新聞 |

- **需要驗證**：✅
- **權限說明**：透過 API Gateway 驗證 JWT，本服務不做額外角色檢查
- **來源**：README API 表格；newsservice-detail 權限規則

---

## 3. 流程總覽

1. 請求通過 API Gateway 驗證，附帶 JWT 或內部服務 Token
2. 進入 `GET /api/v1/sports` Controller
3. 取得查詢參數：`gameType`（必填）、`addTime`、`lang`、`tag`
4. Service 層依 `gameType` 決定目標表名（`sports_{gameType}`）
5. 由 `NewsDataProvider` 對 Cassandra 新聞表執行查詢
6. 依 `date`、`lang` 過濾，以 `addtime` 排序（可能為降冪）
7. 過濾不可回傳欄位（`content`, `link`, `tag`），僅回傳安全欄位
8. 回傳新聞清單給調用方

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `NewsController.GetSports` | 接收查詢參數、調用 Service |
| 2 | Service | `INewsService` / `NewsService` | 調用驗證器檢查 `gameType`，組合過濾條件 |
| 3 | Provider | `INewsDataProvider` / `NewsDataProvider` | 動態組裝 Cassandra 查詢語句（表名 `sports_{gameType}`），執行 SQL |
| 4 | Transfer | DTO / Response Model | 過濾 `content`, `link`, `tag`，轉換為客戶端安全結構 |

- **Code evidence**：`NewsService.Infrastructure/DataAccess/NewsDataProvider.cs`（動態表名拼接、查詢邏輯）

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `news.sports_{gameType}` | Read | 依 `date`, `lang`, `addtime` 查詢新聞列表 |
| Redis | 無 | – | – |
| Queue | 無 | – | – |

- **證據**：newsservice-detail 明確本服務未使用 Redis；Kafka 未引用

---

## 6. 重要規則

- **必須以 `gameType` 決定動態表名**：  
  `gameType` 缺漏或不合法將導致查無表或錯誤，無默認表名
- **不可回傳欄位**：  
  `content`, `link`, `tag` 必須在回傳 DTO 中過濾（`content`/`link` 具版權風險，`tag` 為內部標籤）
- **排序規則**：  
  `addtime` 可用於排序，但不可做為主要過濾索引（該欄位無 Cassandra 索引）
- **跨日期查詢**：  
  無限制（`sports` 表以 `id` 為主鍵，非 `date`），但仍建議加入時間範圍以免全表掃描
- **權限**：  
  需通過 API Gateway 驗證；本服務不實作角色驗證邏輯
- **欄位限制**：  
  `addtime` 由服務內部寫入時自動產生時間戳，此處查詢僅作為排序依據
- **TTL**：  
  無

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 請求缺少 `gameType` | 回傳 400 Bad Request（表名不可為空） |
| `gameType` 對應的動態表不存在 | 可能回傳空列表或 Cassandra 錯誤（需人工確認） |
| Cassandra 查詢超時 | 回傳 500 Internal Server Error |
| 回傳時未過濾 `content` / `link` / `tag` | 資安／版權風險，需在 DTO 層強制攔截 |
| `addTime` 格式錯誤 | 可能被忽略或產生 400 錯誤，需人工確認程式實作 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| QS-01 | API Test | 提供有效 gameType，無其他條件 | 回傳該球種全部新聞 |
| QS-02 | API Test | 同時使用 lang + addTime | 依時間及語言過濾 |
| QS-03 | Permission Test | 未帶 Token | 由 Gateway 攔截，不回傳資料 |
| QS-04 | Flow Test | 驗證 `content` / `tag` 是否洩漏 | 確認回應無此欄位 |
| QS-05 | Integration Test | 指定不存在的 gameType | 回傳空列表或錯誤（需確認） |

---

## 9. 高風險區域

- **動態表名注入風險**：  
  `gameType` 必須白名單驗證（`ValidateGameType`），禁止直接拼接 SQL 以防查詢非法表
- **敏感資料洩漏**：  
  未經篩選即回傳 `content`（全文）、`link`（外連）、`tag`（內部標籤）將違反版權或業務規範
- **全表掃描**：  
  若未提供任何過濾條件（如 `addTime` 或 `lang`），可能掃描整張 `sports_*` 表，造成 Cassandra 壓力
- **跨服務依賴**：  
  本服務不負責原始新聞爬取（由 crawlerService 寫入），若爬蟲停止則查詢結果為空

---

## 10. 常見錯誤

- ❌ **未傳入 `gameType` 或傳入 null**
- ❌ **直接返回 Cassandra 原始 row**，忘記遮蔽 `content`、`link`、`tag`
- ❌ **以 `addtime` 做為強制過濾條件**（例如只撈 > 某時間），可能因無索引而誤用
- ❌ **以為 `lang` 或 `tag` 不存在時會報錯**，實際上通常是可選參數，不回傳錯誤
- ❌ **混淆 `date` 與 `addtime`**：`date` 為新聞日期字串，`addtime` 為入庫 timestamp

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `GET /api/v1/sports`，OpenAPI 定義 |
| DB | `news.sports_{gameType}`，Cassandra schema & db-usage |
| Code | `NewsService.Infrastructure/DataAccess/NewsDataProvider.cs`（動態表名、查詢） |
| Code | `Validator.ValidateGameType(gameType)`（白名單檢查） |
| Rule | newsservice-detail 不可回傳欄位列表 |
| Rule | README 功能描述與 API 表格 |