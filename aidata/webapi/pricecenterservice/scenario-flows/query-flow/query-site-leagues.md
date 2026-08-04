# 查詢站台聯賽

## 1. 場景目的

提供後台管理人員查詢各球種（GameType）於不同資料來源站台（如 bet365、pinnacle）的聯賽列表、特定聯賽的語言對照資訊，以及已合併（對應到主站聯賽）的站台聯賽清單。此流程用於聯賽資料稽核、名稱對照管理與合併狀態確認。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/siteleagues/{gameType}` | 查詢站台聯賽列表 |
| GET | `/api/v1/siteleagues/map/{gameType}/{lid}` | 查詢聯賽語言對照 |
| GET | `/api/v1/siteleagues/merged/{gameType}` | 查詢已合併站台聯賽 |

---

## 3. 流程總覽

1. 接收請求，由 `ECFramework.ECService` 驗證呼叫方權限（所有 API 皆須驗證）。
2. Controller 將 `gameType` 與對應參數傳遞至 SiteGame Service。
3. Service 層根據請求類型，組合 Redis Key 並讀取對應的 Redis 資料庫：
   - 查詢聯賽列表：讀取 **Redis DB6** 中的站台賽事資料，從中解析出聯賽資訊。
   - 查詢語言對照：讀取 **Redis DB7** 中的 `leagueMap:{gameType}` 結構，查找對應 `lid` 的名稱對照。
   - 查詢已合併聯賽：讀取 **Redis DB6** 或內部對照結構，找出已設定合併映射的聯賽。
4. 將資料轉換為 DTO 後回傳。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware | ECFramework.ECService | 驗證請求的 Auth Token 有效性。 |
| 2 | Controller | `SiteGameController.GetSiteLeagues` | 接收 `gameType`，呼叫 Service。 |
| 3 | Controller | `SiteGameController.GetSiteLeagueMap` | 接收 `gameType`, `lid`，呼叫 Service。 |
| 4 | Controller | `SiteGameController.GetMergedSiteLeagues` | 接收 `gameType`，呼叫 Service。 |
| 5 | Service | `SiteGameService` (需人工確認實際類別名稱) | 依據請求類型，決定查詢的 Redis DB 與 Key。 |
| 6 | Provider | `RedisCacheProvider` (需人工確認) | 執行對 Redis DB6 或 DB7 的讀取操作。 |
| 7 | Service | `SiteGameService` | 將 Redis 原始資料映射為 `SiteLeague` 或 `LeagueMap` 模型。 |
| 8 | Controller | `SiteGameController` | 回傳 `200 OK` 與模型列表。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | Redis DB6 (`siteGame:{site}:{gameType}`) | Read | 讀取各站台原始賽事資料，從中取得聯賽資訊。 |
| Redis | Redis DB7 (`leagueMap:{gameType}`) | Read | 讀取聯賽名稱對照表，提供特定聯賽的語言名稱對照。 |
| Cache | （無額外快取） | - | 直接讀取 Redis，無二次快取。 |
| Queue | （未使用） | - | 此查詢流程為同步請求，不涉及非同步或佇列機制。 |

---

## 6. 重要規則

- **權限限制**：所有 API 皆須通過 `ECFramework.ECService` 驗證，確保僅授權的內部服務或管理後端可呼叫。
- **查詢條件**：`gameType` 為必填路徑參數，必須符合系統規範的球種代碼（如 `BS`、`BK`、`FT`）。
- **不可暴露資料**：對外回傳的聯賽列表中，不應包含站台的原始帳號資訊或內部連線配置。
- **資料一致性**：此為純讀取場景，無 Transaction 需求。資料一致性由寫入端的 Provider 保證，此處僅讀取。
- **效能考量**：讀取 `siteGame:{site}:{gameType}` 時，若 `gameType` 下站台眾多，批量讀取需考慮 Redis Pipeline 或連線池管理。
- **合併聯賽判斷**：`merged` 查詢依賴系統內的合併映射規則，若資料未完成合併設定，清單可能為空。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求未帶有效 Token | `401 Unauthorized` |
| `gameType` 不存在或不符合規範 | `400 Bad Request` 或回傳空列表 |
| Redis DB6 或 DB7 連線失敗 | `500 Internal Server Error`，並記錄錯誤日誌 |
| 指定的 `lid` 在 `leagueMap` 中不存在 | `200 OK` 但回傳空或預設值 |
| 無任何站台聯賽資料 | `200 OK` 並回傳空陣列 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SITELEAG-01 | API Test | 以有效 `gameType` 查詢聯賽列表 | `200`，回傳包含 `site`、`lid`、`leagueName` 的列表 |
| SITELEAG-02 | API Test | 以無效 `gameType` 查詢 | `400` 或空列表 |
| SITELEAG-03 | Permission Test | 無 Token 請求 | `401` |
| SITELEAG-04 | API Test | 查詢指定 `lid` 的語言對照 | `200`，回傳多語系名稱對照 |
| SITELEAG-05 | API Test | 查詢已合併聯賽 | `200`，回傳清單中聯賽皆需具備合併映射 |
| SITELEAG-06 | Flow Test | Redis 模擬中斷後請求 | `500`，驗證服務熔斷或錯誤處理機制 |

---

## 9. 高風險區域

- **高風險 Redis Key**：`siteGame:{site}:{gameType}` 與 `leagueMap:{gameType}`，若因快取擊穿或 Key 設計變更導致大量空讀，可能衝擊 Redis 效能。
- **跨服務資料同步**：`leagueMap` 的資料由聯賽名稱對照維護 API (`PUT /api/v1/leagues/{gameType}/{id}/namemaps`) 寫入，若寫入流程異常，此查詢將取得過時或不完整的對照表。
- **Cache consistency**：此場景無快取，直接讀取 Redis，故無快取一致性風險。但需注意 Redis 作為 primary data store，其資料正確性由上游寫入服務保證。

---

## 10. 常見錯誤

- **新人容易犯錯**：誤以為聯賽列表儲存在 MySQL `sport.League` 表中，直接查詢關聯式資料庫。實際上，此處是查詢**站台原始聯賽**，儲存在 **Redis DB6**，與平台定義的標準聯賽（MySQL）不同。
- **AI 容易誤解**：將 `siteleagues/map` 理解為查詢所有聯賽對照，但其實此 API 是**依 `lid` 單筆查詢**。全量查詢應使用聯賽列表 API。
- **常見漏檢查項目**：未驗證 `gameType` 輸入值是否為合法的枚舉值，直接將其作為 Redis Key 的一部分，可能導致非預期的 Key 錯誤或注入風險。
- **常見錯誤流程**：誤將「已合併站台聯賽」理解為從 MySQL 取得資料。此類合併關係同樣儲存於 Redis 或內部對照結構，須從站台賽事或合併配置中解析。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `README.md` - 站台賽事章節中列出 `/api/v1/siteleagues/{gameType}` 等路由 |
| DB | `README.md` - "Redis DB6 `siteGame:{site}:{gameType}` 各站台原始賽事資料" |
| DB | `README.md` - "Redis DB7 `leagueMap:{gameType}` 聯賽名稱對照表" |
| Rule | `README.md` - 所有 `/api/v1/` 下的 API 皆標記為 `需要驗證` |
| Code | （需人工確認）`SiteGameController` 與 `SiteGameService` 實際檔案路徑與實作細節 |