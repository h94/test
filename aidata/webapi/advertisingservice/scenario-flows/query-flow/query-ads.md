# 場景名稱：查詢一般廣告列表

## 1. 場景目的
提供前台客戶端取得目前生效中的一般廣告資料，用於頁面展示。僅回傳 `enabled=1`、時間有效且符合語言的廣告，依排序權重降冪排列，並隱藏管理人員資訊 (`createdby`)。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/ads/{lang}` | 查詢指定語言的一般廣告 (可選附加 `type` 參數) |

> **Evidence**: OpenAPI `paths./api/v1/ads/{lang}.get`  
> **需人工確認**: 一般查詢預設前端呼叫 `GET /api/v1/ads/{lang}` 且不帶 admin token。

---

## 3. 流程總覽

1. 客戶端攜帶驗證 token 發起請求。
2. 驗證 token 有效性（透過 ECFramework 驗證框架）。
3. 從路徑參數取得 `lang`（可為空字串代表全部語言）及可選查詢參數 `type`（預設 `All`）。
4. 呼叫 Service 層組合查詢條件。
5. 透過 Provider 對 Cassandra `ads.advertising` 表執行查詢：
   - 篩選 `enabled = 1`
   - 若 `lang` 不為空，則 `lang = 傳入語言` 或符合模式；空字串則略過
   - 時間範圍 `starttime <= 當前時間戳 < closetime`
   - 依 `seq` 降冪排序
6. 取得結果後，將每筆記錄的 `createdby` 欄位移除（不回傳至客戶端）。
7. 回傳廣告物件清單。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `AdsController.GetAdsByLang(lang, type)` | 接收請求，檢查驗證，呼叫 Service |
| 2 | Service | `AdService.GetEnabledAds(lang, type)` | 組合過濾條件，轉換當前時間為比對用時間戳 |
| 3 | Provider | `CassandraAdProvider.QueryAds(...)` | 執行 CQL 查詢，回傳原始資料 |
| 4 | Service | `AdService.FilterAndMap(res)` | 移除 `createdby`，轉成 DTO |
| 5 | Controller | 回傳 `IEnumerable<AdvertisingDto>` | 序列化為 JSON |

> **需人工確認**: 實際 class 名稱、方法名須參照 source code。  
> **Evidence**: `db-ads-detail` 中提到 `GetEnabledAds`、`GetAdsDataByType` 等語意；Controller 邏輯推導自 API 路由與驗證符記。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Cassandra `ads.advertising` | Read（SELECT） | 查詢啟用且時間有效的一般廣告 |
| 無 | 無使用 Redis / Kafka | - | 本服務於此場景不涉及快取或佇列 |

> **Evidence**: `detail` 明確指出「本服務未使用 Redis」，且無 Kafka 敘述。

---

## 6. 重要規則

- **權限限制**：所有廣告查詢 API 皆需驗證（`✅`），前端應帶合法 token。
- **廣告啟用狀態**：僅回傳 `enabled = 1` 的記錄，停用廣告不可由一般查詢取得。
- **時間範圍過濾**：`starttime <= 當前時間戳 < closetime`，兩邊界皆為**包含/排除**語意需確認；過期或未開始的廣告不回傳。
- **不可回傳欄位**：`createdby` 必須從回應中完全移除，不可暴露管理人員資訊。
- **語言過濾**：`lang` 為空字串時代表全部語言，否則精確匹配或使用包含邏輯（實作可能使用 `IndexOf`）→ 須注意效能。
- **排序規則**：結果必須依 `seq` 降冪排序，`seq` 相同時行為未知，應避免業務上重複。
- **⚠️ 時間戳單位風險**：`starttime` / `closetime` 在 Schema 定義為 `bigint`，`code semantics` 標註為**毫秒**，但 `db-detail` 及 `advertisingservice-detail` 聲明為**秒級**。需人工確認實際儲存單位，避免過濾失效。

> **Evidence**: `advertisingservice-detail` 讀取規則、`db-ads-detail` 時間欄位說明、`code semantics` 語意差異。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未帶 token 或 token 無效 | 回傳 401 Unauthorized |
| `lang` 為不合法代碼（非空白且不在預定義清單） | 查無資料（不回傳任何廣告，或可能回傳空陣列） |
| 廣告 `enabled=0` | 排除，不回傳 |
| 廣告 `closetime` 小於當前時間 | 排除 |
| 廣告 `starttime` 大於當前時間 | 排除 |
| 資料庫超時或連線失敗 | 回傳 5xx 錯誤，可重試 |
| 回應中意外包含 `createdby` | 嚴重違反規則，應阻擋於 Service 層 |
| 時間戳單位不一致導致過濾錯誤 | 可能展示過期廣告，需人工校準 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC1 | API Test | 呼叫 API 帶有效 token 與 `lang=zh` | 僅回傳 enabled=1、starttime <= now < closetime、lang 符合的廣告，且無 createdby，依 seq 降冪 |
| TC2 | API Test | `lang` 為空字串 | 回傳所有語言、符合時間的有效廣告 |
| TC3 | API Test | 無 token | 回傳 401 |
| TC4 | Integration Test | 資料庫含停用廣告 (enabled=0) | 該筆不出現在回應中 |
| TC5 | Integration Test | 廣告 `closetime` 為過去時間 | 該筆不出現 |
| TC6 | Integration Test | 廣告 `starttime` 為未來時間 | 該筆不出現 |
| TC7 | Flow Test | Service 層回傳物件確認 `createdby` 為 null 或被移除 | 所有物件不含該欄位 |

---

## 9. 高風險區域

- **時間戳單位不明確**：Cassandra 儲存值可能為毫秒，但文件多處指為秒級。比對當前時間時若單位不統一，將導致有效廣告被過濾或過期廣告被顯示，為業務高風險。
- **Cassandra 查詢效能**：`ads.advertising` 表中 `lang`、`enabled`、`starttime`、`closetime` 非 Primary Key 且無二級索引，查詢可能觸發全表掃描。若資料量大需注意，可考慮應用層篩選或設計快取（此處未實作）。
- **`seq` 重複導致順序不穩定**：業務應確保不重複或增加第二排序鍵（如 `id`）。
- **管理端 vs 一般端混淆**：開發或 AI 可能誤用一般查詢 API 取得停用廣告，違反隔離規範。

---

## 10. 常見錯誤

- ❌ 忘記過濾 `enabled=1`，將停用廣告展示給使用者。
- ❌ 未過濾時間區間或使用錯誤的比較運算子（如只比對 `starttime <= now` 忘了 `now < closetime`）。
- ❌ 回傳時未剝離 `createdby`，洩漏後台人員帳號。
- ❌ 錯誤假定時間戳單位為秒，但實際儲存為毫秒，產生錯誤過濾。
- ❌ 語言過濾使用 LIKE 或 IndexOf 未考慮精確性，導致誤配（例如 “zh” 可能匹配到 “zh-CN” 或 “en-zh”）。
- ❌ 認為此 API 有 Redis 快取，實際上並無，導致設計錯誤的快取策略。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | OpenAPI `paths./api/v1/ads/{lang}.get` |
| 讀取規則 (enabled/時間過濾/lang/排序/createdby 隱藏) | `advertisingservice-detail.md` - 讀取規則章節 |
| Cassandra 表結構 | `ads.md` 中 `advertising` 表定義 |
| 時間戳語意差異 | `code semantics` 標註毫秒 vs `db-ads-detail` 標註秒級 |
| 無 Redis / Kafka 使用 | `advertisingservice-detail.md` - Redis 章節明確寫「本服務未使用 Redis」 |
| 驗證需求 | README API 重點表格，標示廣告 API 需驗證 |
| 錯誤情境與常見錯誤 | `advertisingservice-detail.md` 常見錯誤章節、`db-ads-detail.md` 時間過濾警告 |