# 更新球隊縮寫對照

## 1. 場景目的
管理員更新指定球種內某支球隊的所有外部站台縮寫對照，用於將各博弈站台的別名統一對應至內部標準識別，確保賽事合併與顯示的一致性。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/teams/{gameType}/{id}/abbrmaps` | 更新指定球種與球隊的縮寫對照表（需驗證） |

---

## 3. 流程總覽

1. 接收 PUT 請求，包含路徑參數 `gameType`（球種）與 `id`（球隊內部 ID），以及 request body 的縮寫對照 JSON。
2. 驗證 API 呼叫者的授權（需驗證 token / 權限）。
3. 驗證 `gameType` 為支援的球種（如 BK、BS 等）。
4. 查詢對應的球隊記錄是否存在（推測為 MySQL `sport`.`Team` 表，**需人工確認**）。
5. 解析 request body 中的 `abbrmaps`，檢查格式是否為合法鍵值對（`Dictionary<string,string>`）。
6. 更新球隊的縮寫對照資料（**推測寫入 MySQL `sport`.`Team` 或對應的 Redis 緩存**，依據[聯賽縮寫對照 API](#9-高風險區域) 類比，**需人工確認**）。
7. 若有相關 Redis 快取（例如 `teamMap:{gameType}`），則同步更新或使其失效。
8. 回傳成功回應（可能回傳更新後的 Team 資源）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `TeamController.UpdateAbbrMaps` | 接收路由參數，調用 Service |
| 2 | Validator | (推測) `UpdateAbbrMapsRequestValidator` | 驗證 `gameType`、`id`、`abbrmaps` 格式 |
| 3 | Service | `TeamService.UpdateAbbrMaps` | 協調業務邏輯：檢查球隊存在，合併或替換縮寫對照 |
| 4 | Provider | `TeamRepository` (MySQL) | 寫入 MySQL `sport`.`Team` 表對應欄位 |
| 5 | Provider | `RedisProvider` (Redis DB7) | 更新或刪除相關快取鍵 (`teamMap:{gameType}`? **需人工確認**) |
| 6 | Controller | `TeamController.UpdateAbbrMaps` | 回傳 `200 OK` 並返回更新後的 Team 物件 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | MySQL `sport`.`Team` (推測) | `UPDATE` | 寫入或合併縮寫對照欄位 (如 `AbbrMaps`) |
| Redis | DB7 `teamMap:{gameType}` (推測) | `SET` 或 `DEL` | 使外部查詢能即時取得最新對照 (**需人工確認**) |

---

## 6. 重要規則

- **權限限制**：必須通過 ECFramework 驗證，限管理員或具有後台操作權的角色。
- **欄位限制**：`abbrmaps` 必須為合法的 `Dictionary<string,string>`，不允許空值或非字串值。
- **不可變更欄位**：不應修改球隊的其他屬性（如名稱、所屬聯賽），僅更新縮寫對照。
- **狀態檢查**：被更新的球隊必須存在且未被標記為刪除（若團隊有軟刪除機制）。
- **緩存一致性**：若使用 Redis 快取，更新 DB 後必須確保快取同步（更新或失效），不可只依賴 TTL。
- **Transaction 規則**：避免使用跨儲存層（MySQL + Redis）的分散式事務；先寫 MySQL，成功後再操作 Redis，若 Redis 操作失敗應記錄錯誤並可人工介入。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `gameType` 參數為不支援的球種 | 400 Bad Request，提示無效球種 |
| 球隊 `id` 不存在 | 404 Not Found |
| `abbrmaps` 格式錯誤（非物件） | 400 Bad Request，說明正確格式 |
| 寫入 MySQL 失敗（連線超時、鎖定） | 500 Internal Server Error，不影響緩存 |
| Redis 寫入失敗 | 記錄錯誤日誌，回傳 200 OK 但依賴後續 TTL 或手動修復緩存 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| T1 | Permission Test | 未帶 token 呼叫 API | 401 Unauthorized |
| T2 | Flow Test | 使用合法資料更新既存球隊 | 200 OK，查詢 API 回傳更新後的對照 |
| T3 | API Test | `gameType` 使用不存在值 | 400 Bad Request |
| T4 | API Test | `id` 對應的球隊不存在 | 404 Not Found |
| T5 | Integration Test | 更新後透過前台賽事查詢驗證縮寫是否生效 | 推播或查詢結果中球隊縮寫已變更 |

---

## 9. 高風險區域

- **高風險 table**：MySQL `sport`.`Team` 的 `AbbrMaps` 欄位（若結構為 JSON，需注意合併策略，避免全量覆蓋）。
- **Cache consistency**：若存在 Redis 快取，更新 MySQL 後 Redis 過期或不同步可能導致前台顯示舊縮寫。
- **跨服務資料同步**：此 API 的變更可能影響下游服務（如賽事合併、前台顯示），需要確保無 null 值導致 NPE。

---

## 10. 常見錯誤

- **新人容易犯錯**：未檢查 `abbrmaps` 中的值是否包含特殊字元，可能影響下游解析。
- **AI 容易誤解**：可能誤認為對照表僅存在 Redis 中，實際上應以 MySQL 為主要儲存，Redis 為快取。
- **常見漏檢查項目**：未驗證 `id` 是否在指定 `gameType` 下有效，可能造成跨球種寫入。
- **常見錯誤流程**：直接對外暴露內部 ID（如 `SiteID`）於回應中，需在回傳 DTO 移除敏感欄位。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README `PUT /api/v1/teams/{gameType}/{id}/abbrmaps` |
| OpenAPI | paths 中包含 `/api/v1/teams/{gameType}/{id}/abbrmaps`（需人工確認完整定義） |
| DB | MySQL `sport`.`Team` 為 README 所列球隊主表，**縮寫欄位待人工確認** |
| Redis | 類比聯賽縮寫對照使用 Redis DB7 `leagueMap:{gameType}`，推測球隊可能相似 |
| Code | Controller `TeamController`、Service `TeamService` 待由原始碼進一步確認 |
| 規則參考 | pricecentermanage 對 `bk_siteplayers` 僅讀取，pricecenterservice 對 `gameusers_wallet` 僅讀取，不影響此寫入流程 |

---

**需人工確認**  
- 球隊縮寫對照的最終儲存位置（MySQL `sport`.`Team` 表具體欄位結構）。  
- Redis 是否存在 `teamMap:{gameType}` 鍵，以及同步策略。  
- `UpdateAbbrMaps` 的合併語意（是替換還是合併）。