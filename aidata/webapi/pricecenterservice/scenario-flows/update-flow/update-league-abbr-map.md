# 更新聯賽縮寫對照

## 1. 場景目的

允許後台管理員為指定 `gameType` 與 `id` 的聯賽，批次更新其縮寫對照表（Abbreviation Map），用於將不同外部站台的原始聯賽名稱統一向內部的聯賽縮寫，以支援後續賽事合併與對照。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/leagues/{gameType}/{id}/abbrmaps` | 更新聯賽縮寫對照 |

所有對外 API 均需通過 ECFramework.ECService 驗證。

---

## 3. 流程總覽

1. 接收 PUT 請求，路徑包含 `gameType` 與聯賽 `id`。
2. 驗證請求者權限（需為後台管理員）。
3. 從 Request Body 取得更新的縮寫對照資料（abbreviation maps）。
4. 將縮寫對照寫入 Redis DB7 `leagueMap:{gameType}` 結構中對應的聯賽欄位。
5. 回傳操作成功。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | 需人工確認 | 接收 PUT 請求，解析 `gameType` 與 `id`，將 body 反序列化 |
| 2 | Service | 需人工確認 | 驗證 `gameType` 與 `id` 存在於系統配置中（可能查詢 MySQL Sport.League） |
| 3 | Provider | 需人工確認 | 組裝 Redis Key `leagueMap:{gameType}`，更新指定 `id` 的縮寫對照 Hash |
| 4 | Controller | 需人工確認 | 回傳 HTTP 200 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Cache | Redis DB7 `leagueMap:{gameType}` | Write / Update | 儲存聯賽名稱對照表（含縮寫） |
| DB | MySQL Sport `League` | Read | 查詢聯賽是否存在（推測，或僅依賴 Redis 既有資料） |

---

## 6. 重要規則

- **權限限制**：需使用 `ECFramework.ECService` 進行驗證，僅允許授權的後台管理員呼叫。
- **欄位限制**：`gameType` 需符合系統定義的球種（如 `BS`、`BK`）。
- **不可暴露資料**：回傳內容應避免暴露內部 Redis 結構細節。
- **狀態值限制**：若聯賽 `id` 不存在（MySQL Sport.League 查無資料），應拒絕更新。
- **不可修改欄位**：此 API 僅更新縮寫對照，不應更動聯賽主鍵 `id` 或任何其他聯賽主表欄位。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 驗證失敗（無 token 或 token 過期） | 回傳 401 Unauthorized |
| 使用非管理員帳號呼叫 | 回傳 403 Forbidden |
| `gameType` 非法 | 回傳 400 Bad Request，提示球種無效 |
| Request Body 格式錯誤 | 回傳 400 Bad Request |
| `id` 不存在 | 回傳 404 Not Found 或 400 Bad Request |
| Redis DB7 寫入失敗（連線中斷） | 回傳 500 Internal Server Error，需記錄錯誤日誌 |
| Cassandra 寫入失敗（若有備援寫入） | 依 retry 策略處理，失敗則回傳 500 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| T1 | Permission Test | 未帶 token 呼叫 | 401 Unauthorized |
| T2 | Permission Test | 使用一般會員 token 呼叫 | 403 Forbidden |
| T3 | API Test | 對存在的 `gameType`/`id` 進行正常更新 | 200 OK，Redis DB7 中對照表更新 |
| T4 | API Test | `gameType` 傳入 `INVALID` | 400 Bad Request |
| T5 | API Test | 對不存在的 `id` 呼叫 | 404 或 400 |
| T6 | Flow Test | 更新後，查詢聯賽對照表 API | 確認已更新的縮寫值可被正確讀取 |

---

## 9. 高風險區域

- **高風險 Table**：Redis DB7 `leagueMap:{gameType}` 為聯賽名稱對照的單一真源，錯誤的更新將導致整個 `gameType` 賽事比對異常。
- **Cache Consistency**：Redis DB7 是對照表，無其他 Cache 層，直接寫入即生效。若有其他服務快取聯賽對照，需有失效機制（此處需人工確認其他服務的快取策略）。
- **Concurrent Update**：若後台多人同時更新同一聯賽的縮寫對照，需確認 Redis 操作為原子性（使用 Hash 的 HSET），否則可能導致資料覆蓋。
- **Data Loss Prevention**：此 API 通常為後台使用，應考慮加入操作日誌（透過 loggingService 寫入 Cassandra 或 Kafka），以利後續稽核。

---

## 10. 常見錯誤

- **AI 容易誤解**：可能將 `/api/v1/leagues/{gameType}/{id}/abbrmaps` 與更新聯賽名稱對照的 `/api/v1/leagues/{gameType}/{id}/namemaps` 混淆，需注意路徑與用途的差異。
- **新人容易犯錯**：直接修改 Redis DB7 的整個 Key，而非僅更新對應的 Hash Field，導致其他聯賽的對照資料遺失。
- **常見漏檢查項目**：更新前未驗證 `gameType` 是否有效，導致在 Redis 中產生無效的 Key。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | PUT /api/v1/leagues/{gameType}/{id}/abbrmaps |
| Cache | Redis DB7 `leagueMap:{gameType}` |
| DB | MySQL Sport.League (推測用於驗證聯賽存在) |
| Code | 需人工確認 (Controller/Service/Provider) |
| Rule | pricecenterservice-detail.md (讀取規則) |