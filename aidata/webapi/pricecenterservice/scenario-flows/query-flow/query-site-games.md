# 查詢站台賽事

## 1. 場景目的
提供內部或後台服務查詢各外部博弈站台（如 bet365、pinnacle、ku888 等）的原始賽事資料。資料直接從 Redis DB6 讀取，不經過合併或加工，用於後續賽事對照、比對或除錯。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/sitegames/{gameType}` | 查詢指定球種全部站台的賽事（可能含日期區間參數） |
| GET | `/api/v1/sitegames/{gameType}/{startGameDate}` | 依球種與開始日期查詢所有站台賽事 |
| GET | `/api/v1/sitegames/{gameType}/{site}/{startGameDate}` | 依球種、站台與開始日期查詢該站台賽事 |

所有 API 皆需要通過 ECFramework 驗證（✅ 需要驗證）。

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，路徑包含 `gameType`（必要）、可選的 `site` 與 `startGameDate`。
2. ECFramework 驗證層攔截，驗證呼叫方身份（token / authKey），未通過直接回傳 401/403。
3. 參數檢查：`gameType` 不可為空，`startGameDate` 若提供需符合日期格式。
4. 依據參數組合決定 Redis 查詢的 Key Pattern：
   - 若有指定 `site`：`siteGame:{site}:{gameType}` 單一 Key 查詢。
   - 若無指定 `site`：需掃描符合 `siteGame:*:{gameType}` 的所有 Key（具體實作視設計而定，可能使用 Redis SCAN 或預先定義站台清單）。
5. 從 Redis DB6 讀取對應 Key 的 Value（通常為 JSON 或序列化物件）。
6. 若需依日期過濾，在應用層解析 Value 中的賽事日期欄位，篩選 >= `startGameDate` 的資料。
7. 組裝回傳結果（可能是單一站台或合併多站台賽事）。
8. 回傳 HTTP 200 與 JSON 陣列。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Middleware | `ECFramework.AuthMiddleware` | 驗證請求是否攜帶有效 token，失敗則回傳 401/403 |
| 2 | Controller | `SiteGameController.Get()` （需人工確認實際類別） | 接收 `gameType`、`site`、`startGameDate` 參數，呼叫對應 Service |
| 3 | Service | `SiteGameService.GetSiteGames(gameType, site, startGameDate)` | 組合 Redis Key，呼叫 Redis Provider；若無指定 site，可能先取得站台清單再逐一讀取 |
| 4 | Provider | `RedisProvider.Get(redisDB, key)` 或 `RedisProvider.Scan(redisDB, pattern)` | 對 Redis DB6 執行 GET 或 SCAN 操作，返回原始資料 |
| 5 | Service | 同上 | 反序列化 Redis 值，依 `startGameDate` 過濾賽事（若 Value 中包含日期欄位） |
| 6 | Controller | 同上 | 將結果轉換為 DTO 並回傳 200 |

> ⚠️ 具體 Controller / Service 名稱與實際 code 可能不同，需人工確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Redis | DB6，Key：`siteGame:{site}:{gameType}` | 讀取（GET / SCAN） | 取得指定站台與球種的原始賽事 JSON 資料 |
| MySQL/Cassandra | 無 | 無 | 此場景不操作其他 DB |
| Kafka / Queue | 無 | 無 | 僅查詢，不涉及寫入或佇列 |

---

## 6. 重要規則

- **權限限制**：所有此系列 API 都標記為需要驗證，呼叫方必須持有有效的內部服務授權 token。
- **欄位限制**：回傳資料為站台原始賽事，可能包含未經脫敏的站台內部 ID 或賠率來源標記，**不可直接對外（終端使用者）暴露，僅供內部服務或管理後台使用**。
- **Redis Key 結構**：`siteGame:{site}:{gameType}`，其中 `{site}` 為站台代碼（如 BET365），`{gameType}` 為球種（如 BK、BS）。
- **日期處理**：API 路徑中的 `startGameDate` 用於篩選賽事開始日期；若 Redis 儲存結構中未包含日期，則可能直接回傳整個 Key 的內容而不做日期過濾（需人工確認實際實作）。
- **資料格式**：Redis Value 為 JSON 陣列或物件，應由專門的 DataModel 反序列化（如 `GameDataModels` 套件）。
- **不可只依賴 TTL**：Redis DB6 的 Key 可能無 TTL，由資料汲取服務（crawler）負責寫入與更新，本服務僅唯讀。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 請求未帶認證或 token 無效 | 回傳 401 Unauthorized 或 403 Forbidden |
| `gameType` 未填或空白 | 回傳 400 Bad Request，帶錯誤訊息 |
| `startGameDate` 格式錯誤（非日期） | 回傳 400 Bad Request |
| 指定的 `site` 不存在對應 Redis Key | 回傳空陣列 `[]` 或 200 但資料為空 |
| Redis 連線失敗或逾時 | 回傳 500 Internal Server Error 或 503 Service Unavailable，並記錄錯誤日誌 |
| Redis Key 存在但 Value 不是合法 JSON | 回傳 500，記錄反序列化錯誤 |
| 傳入的 `gameType` 不存在於任何站台 | 回傳空結果 `[]` |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| UT-SG-01 | API Test | 正常查詢，帶有效 `gameType` 與 `site` | 200，返回該站台對應球種的賽事 JSON |
| UT-SG-02 | API Test | 查詢不指定 `site`，僅給 `gameType` 與 `startGameDate` | 200，返回所有站台在該日期後的賽事合併結果 |
| UT-SG-03 | Permission Test | 無 token 呼叫 | 401 或 403 |
| UT-SG-04 | API Test | 提供不存在的 `site` | 200，回傳空陣列 |
| UT-SG-05 | Flow Test | Redis 服務中斷 | 500 或 503，不可 crash |
| UT-SG-06 | Flow Test | 部分 Redis Key 回傳格式錯誤 | 正確 Key 仍能回傳，錯誤部分略過並記錄 log（視實作而定） |

---

## 9. 高風險區域

- **高風險 API**：此 API 用於內部資料對照，若權限控制不當，可能洩漏站台原始結構與賠率來源細節。必須確保僅限內部服務呼叫。
- **跨服務資料同步**：Redis DB6 的資料由外部爬蟲或 data pipeline 寫入，若該 pipeline 延遲或失敗，本服務回傳的資料將過時或不完整，**無自行修復能力**。
- **Cache consistency**：本服務僅讀取，一致性風險低；但若未來引入本地快取，需考量失效機制。
- **Idempotency**：該 API 為 GET，天然具備冪等性，無額外風險。

---

## 10. 常見錯誤

- 新人容易以為此 API 是給前端使用者直接查詢，其實是內部服務用，應避免對外暴露。
- 忘記在呼叫前檢查 Redis Key 是否存在，導致直接反序列化 null 值而拋出 NullReferenceException。
- 在沒有統一處理的情況下，對多個站台掃描時使用 KEYS 指令（應使用 SCAN），可能造成 Redis 阻塞。
- 對 `startGameDate` 只做字串比對而非日期比較，導致篩選邏輯錯誤（例如 `"2025-10-01" > "2025-09-30"` 需確保格式一致）。
- 誤解 Redis DB 編號：必須使用 DB6，寫錯 DB 會拿到其他模組的資料或空值。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由與驗證需求 | README：站台賽事 API 表格 |
| Redis 結構 | README：`siteGame:{site}:{gameType}` 為 DB6 用途 |
| 技術棧與驗證框架 | README：使用 ECFramework.ECService 內部統一驗證框架 |
| 資料庫角色 | README：Redis DB6 儲存各站台原始賽事資料 |
| 服務相依 | README：外部博弈站台（70+ 來源）擷取資料，暗示資料由其他服務寫入，本服務唯讀 |
| 需人工確認項目 | 實際 Controller / Service 類別名稱、Redis SCAN 實作方式、是否支援無 site 查詢所有站台、日期過濾究竟在 Redis 層還是應用層，須從 code 驗證 |