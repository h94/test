# 查詢站台聯盟

## 1. 場景目的
提供管理後台人員查詢不同站台的聯盟(league)與站台間的對應關係，支援依時間、lid、sitelid或站台代碼等不同維度查詢。這是一個純查詢流程，目標是讓運營人員能快速找出特定站台聯盟資料進行比對或後續管理。

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/siteleagues/{gameType}/bytime` | 依時間區間查詢站台聯盟 |
| GET | `/api/siteleagues/{gameType}/bylid` | 依多個lid查詢站台聯盟 |
| GET | `/api/siteleague/{gameType}` | 依單一sitelid查詢站台聯盟 |
| GET | `/api/siteleagues/{gameType}/bysite` | 依站台代碼查詢站台聯盟 |

## 3. 流程總覽
這是一個讀取流程，mergesite本身無直接資料庫，全部透過PriceCenterService取得資料。

1. 管理後台使用者進入站台聯盟查詢頁面，選擇球種與查詢條件
2. 依不同查詢維度，前端請求對應API端點
3. mergesite驗證使用者權限(ECCore機制)
4. Controller接收請求，解析gameType與其他必要查詢參數
5. 呼叫對應的Service方法，由Service透過Gateway呼叫PriceCenterService REST API
6. PriceCenterService回傳對應的站台聯盟資料
7. mergesite將資料封裝為DTO回傳前端

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware | ECCore驗證機制 | 驗證使用者後台權限 |
| 2 | Controller | `SiteLeagueController.GetByTime` | 接收`gameType`、時間區間等查詢條件 |
| 3 | Controller | `SiteLeagueController.GetByLid` | 接收`gameType`、lid清單 |
| 4 | Controller | `SiteLeagueController.GetBySiteLid` | 接收`gameType`、sitelid |
| 5 | Controller | `SiteLeagueController.GetBySite` | 接收`gameType`、站台代碼 |
| 6 | Service | `SiteLeagueService` (需人工確認實際類名) | 組裝查詢條件，呼叫PriceCenterService |
| 7 | Gateway | `PriceCenterGateway` (需人工確認實際類名) | 發送HTTP請求至PriceCenterService |
| 8 | External | PriceCenterService REST API | 處理查詢，回傳站台聯盟資料 |
| 9 | Controller | `SiteLeagueController` | 將結果序列化為對應DTO回傳前端 |

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| REST API | PriceCenterService | Read | 取得站台聯盟資料(主要資料來源) |
| Kafka | Log Topic | Publish | 記錄使用者操作日誌(查詢行為) |

**說明**：
- mergesite本身無直接資料庫操作，所有站台聯盟資料透過PriceCenterService取得
- Redis未使用（cache機制由PriceCenterService內部決定）
- Kafka僅用來記錄使用者操作行為，不參與查詢邏輯

## 6. 重要規則

- **權限限制**：所有API皆需驗證，由ECCore 3.0.2處理，未登入或不具後台權限者應被拒絕
- **查詢參數**：
  - `gameType`為必填路徑參數，代表球種
  - `bytime`需提供時間區間參數（如startDate、endDate）
  - `bylid`需提供lid參數（可能為多個lid）
  - `bysite`需提供站台代碼參數
  - `sitelid`為單一值精確查詢
- **不可暴露資料**：站台內部敏感欄位應在回傳前過濾，僅回傳可供管理後台顯示的欄位
- **無寫入操作**：此場景為純讀取，不可修改任何資料庫或快取內容

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| gameType不存在或無效 | 回傳空結果或適當錯誤訊息 |
| 必要查詢參數缺失 | 回傳400 Bad Request |
| 查詢時間區間無資料 | 回傳空列表 |
| lid或sitelid不存在 | 回傳空結果或404 |
| PriceCenterService無回應或超時 | 回傳502/504，前端顯示服務異常訊息 |
| 使用者無後台權限 | 回傳401/403 |

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SL-01 | API Test | 以有效`gameType`與時間區間呼叫`bytime` | 回傳200，包含該時間範圍的站台聯盟列表 |
| SL-02 | API Test | 以多個lid呼叫`bylid` | 回傳200，包含對應lid的站台聯盟 |
| SL-03 | API Test | 以單一sitelid呼叫查詢 | 回傳200，包含該sitelid的詳細資料 |
| SL-04 | API Test | 以有效站台代碼呼叫`bysite` | 回傳200，包含該站台的所有聯盟 |
| SL-05 | Flow Test | 無有效權限呼叫API | 回傳401/403 |
| SL-06 | Flow Test | PriceCenterService離線時呼叫 | 回傳502/504，不crash |
| SL-07 | API Test | 提供無效的gameType | 回傳適當錯誤或空結果 |

## 9. 高風險區域

- **外部服務相依性**：此服務高度依賴PriceCenterService，若該服務不穩定或回應緩慢，查詢功能將直接受影響
- **大量資料查詢**：
  - `bytime`若時間區間過大，可能導致PriceCenterService回傳大量資料，需確認是否有分頁或限制機制
  - `bylid`若lid數量過多，也需注意請求大小限制
- **無快取保護**：mergesite本身無redis cache，重複查詢將每次都打到PriceCenterService
- **權限驗證**：需確認ECCore驗證機制是否足夠防止未授權查詢

## 10. 常見錯誤

- ❌ **新人容易犯錯**：誤以為mergesite有直接資料庫，試圖編寫SQL查詢站台聯盟資料
- ❌ **AI容易誤解**：
  - 誤認為查詢結果會寫入mergesite本地快取
  - 誤認siteleagues資料來自sport MySQL或pricecenter Cassandra
- ❌ **常見漏檢查項目**：
  - 未檢查`gameType`參數是否合法
  - 未處理PriceCenterService超時或錯誤回應
- ❌ **常見錯誤流程**：
  - 當PriceCenterService回應延遲時，前端重複點擊導致重複請求
  - 未限制查詢時間區間，導致一次拉取過多資料

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `README.md` — SiteLeague路由定義 |
| 服務相依 | `README.md` — 「服務相依」章節：資料讀寫均透過PriceCenterService |
| 無直接DB | `mergesite-detail.md` — 「此服務無直接資料庫」 |
| 驗證機制 | `README.md` — 「需要驗證」欄位標記為✅ |
| Kafka操作 | `README.md` — 「Kafka（192.168.55.60）：應用程式Log寫入」 |
| 場景定義 | `README.md` — 「常見使用場景」章節 |
| 權限規則 | `db-usage` / `mergesite-detail.md` — 權限與驗證流程說明 |
| Code Evidence | 需人工確認 — Controller、Service、Gateway實際類別名稱 |