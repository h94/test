# 更新聯賽名稱對照

## 1. 場景目的

當有新聯賽上線或聯賽名稱需要異動時，後台管理員可透過此 API 更新聯賽的多語言名稱對照表。更新成功後會同步至 Redis DB7，確保前台查詢聯賽名稱時能即時反映最新對照資料。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/leagues/{gameType}/{id}/namemaps` | 更新指定聯賽的名稱對照表 |

---

## 3. 流程總覽

1. 接收 PUT 請求，帶入 `gameType`（球種）、`id`（聯賽 ID）及 Request Body（多語言名稱對照）。
2. 驗證 API 權限（ECFramework.ECService 驗證）。
3. 參數校驗：檢查 `gameType` 與 `id` 是否合法、Request Body 格式是否正確。
4. 寫入 Redis DB7：將新的名稱對照寫入 `leagueMap:{gameType}` 結構中。
5. 回傳成功或失敗結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `LeagueController` | 接收 PUT 請求，解析 `gameType`、`id` 與 Body |
| 2 | Service | `LeagueService` | 驗證聯賽是否存在、處理名稱對照邏輯 |
| 3 | Provider | `RedisProvider` | 將名稱對照寫入 Redis DB7 `leagueMap:{gameType}` |
| 4 | Controller | `LeagueController` | 回傳 HTTP 200 或錯誤狀態碼 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Redis DB7 | `leagueMap:{gameType}` | Write / Update | 更新指定聯賽的多語言名稱對照 |

---

## 6. 重要規則

- **權限限制**：需通過 ECFramework.ECService 驗證，僅允許授權使用者操作（證據：README 標記需要驗證、Service detail 提及 ECFramework.ECService）。
- **參數限制**：`gameType` 須為支援的球種類型（如 `BS`、`BK` 等），`id` 須為系統內存在的聯賽 ID。
- **不可暴露資料**：對照表內容可公開，無敏感欄位。
- **更新規則**：此 API 為全量更新 `leagueMap:{gameType}` 中對應聯賽的名稱對照欄位，需確保 Request Body 結構正確。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未通過驗證 | 回傳 401 Unauthorized |
| `gameType` 不合法 | 回傳 400 Bad Request，提示球種類型錯誤 |
| `id` 不存在 | 需人工確認：是否回傳 404 或直接建立新對照 |
| Request Body 格式錯誤 | 回傳 400 Bad Request，提示格式錯誤 |
| Redis 寫入失敗 | 回傳 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC-01 | API Test | 使用有效參數與合法 Body 更新 | 回傳 200，Redis DB7 資料更新 |
| TC-02 | Permission Test | 未帶驗證 Token 或 Token 無效 | 回傳 401 |
| TC-03 | API Test | `gameType` 為空或非支援值 | 回傳 400 |
| TC-04 | Flow Test | 更新後呼叫查詢 API 驗證 | 查詢結果應為最新對照 |
| TC-05 | API Test | Request Body 缺少必要欄位或格式不符 | 回傳 400 |

---

## 9. 高風險區域

- **Redis 寫入**：`leagueMap:{gameType}` 是前台聯賽名稱顯示的即時資料來源，寫入錯誤將直接影響使用者看到的聯賽名稱，可能造成全部使用者顯示異常。
- **並發寫入**：需人工確認：是否存在分散式鎖或樂觀鎖機制，防止同時多個更新請求造成資料錯亂。

---

## 10. 常見錯誤

- ❌ 直接拼接 Redis Key 時格式錯誤，例如誤寫成 `leagueMap:{gameType}:{id}`。
- ❌ 誤以為此 API 同時更新 MySQL 或 Cassandra，實際上本場景僅操作 Redis DB7（需人工確認：是否需要同步更新其他儲存層）。
- ❌ 未考慮 namemaps 的語言欄位是否需要完整傳入，可能造成部分語言被清空。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | PUT `/api/v1/leagues/{gameType}/{id}/namemaps` |
| Redis | `leagueMap:{gameType}` (Redis DB7) |
| 驗證框架 | `ECFramework.ECService` (Service detail) |
| 使用場景 | README 場景 4：聯賽名稱對照維護 |