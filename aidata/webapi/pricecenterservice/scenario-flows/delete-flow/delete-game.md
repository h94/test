# 刪除賽事

## 1. 場景目的

提供後台管理員或自動化工具移除指定賽事的能力。此操作會同時刪除 Redis DB5 即時賽事快取（Hash 中指定 field）與 Cassandra `pricecenter.games` 歷史記錄，以確保前台查詢不會再取得該賽事。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| DELETE | `/api/v1/games/{gameType}/{lid}/{gDate}/{id}` | 刪除指定賽事 |

---

## 3. 流程總覽

1. 接收刪除請求，包含 gameType、lid、gDate、id
2. 通過內部驗證框架驗證請求權限
3. 重組 Redis Key：`{gameType}:{lid}:{gDate}`，與待刪除 field（id）
4. 刪除 Redis DB5 中 Hash 的指定 field（`HDEL`）
5. 刪除 Cassandra `pricecenter.games` 中對應賽事列
6. 回傳操作成功

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Middleware | ECFramework | 驗證憑證有效性，提取請求者資訊 |
| 2 | Controller | GameController.DeleteGame | 接收參數，呼叫 Service 層 |
| 3 | Service | GameService.DeleteGame | 協調 Redis 與 Cassandra 刪除順序 |
| 4 | Provider | GameRedisProvider.DeleteGameField | 重組 Key，執行 `HDEL {gameType}:{lid}:{gDate} {id}` |
| 5 | Provider | GameCassandraProvider.DeleteGame | 執行 Cassandra `DELETE FROM games WHERE gameType=? AND lid=? AND gDate=? AND id=?` |
| 6 | Service | GameService.DeleteGame | 日誌記錄，回傳成功 |

> **需人工確認**：若 Service 層有 SignalR 推播邏輯通知前台移除賽事，此處未包含。需確認是否已實作。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Redis DB5 | `{gameType}:{lid}:{gDate}` | Delete (HDEL) | 移除 Hash 中指定賽事 field，前台即時查詢不再包含此賽事 |
| Cassandra | `pricecenter.games` | Delete | 移除賽事歷史記錄行 |
| Kafka | （若有變更日誌） | Publish | **需人工確認**：刪除賽事後是否發佈變更事件供其他服務消費 |

---

## 6. 重要規則

- **權限限制**：需通過 ECFramework 驗證，僅限管理後台或具備賽事管理權限角色呼叫
- **冪等性**：若 Redis Hash 中已無此 field，或 Cassandra 已無此列，刪除操作不應報錯，應正常回傳成功
- **Redis Key 清理**：當 `HDEL` 後 Hash 為空，應考慮是否執行 `DEL {key}` 以釋放記憶體（**需人工確認**：實作是否包含此自動清理邏輯）
- **Cassandra 一致性**：使用一致性等級 `LOCAL_QUORUM` 或依配置確保刪除成功
- **不可操作 MySQL Sport**：刪除賽事不應涉及 `sport` 資料庫中的聯賽/球隊主表資料

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 請求缺乏有效憑證 | 回傳 401 Unauthorized |
| 請求者不具備刪除權限 | 回傳 403 Forbidden |
| `gameType`、`lid`、`gDate`、`id` 任一參數格式無效 | 回傳 400 Bad Request |
| Redis 連線失敗 | 回傳 502 或特定錯誤碼，不執行 Cassandra 刪除（確保次序，避免部分刪除） |
| Cassandra 寫入 timeout | 回傳 504 Gateway Timeout 或重試 |
| 賽事不存在 | 回傳 200 OK（冪等） |
| GameType 不在允許清單 | 回傳 400 Bad Request |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| DELETE-01 | API Test | 正常刪除存在於 Redis 與 Cassandra 的賽事 | 200 OK，Redis field 消失，Cassandra 行不存在 |
| DELETE-02 | API Test | 刪除僅存於 Redis 的賽事（Cassandra 已無紀錄） | 200 OK，Redis field 成功移除 |
| DELETE-03 | API Test | 刪除不存在的賽事 | 200 OK（冪等） |
| DELETE-04 | Permission Test | 未帶憑證呼叫 | 401 Unauthorized |
| DELETE-05 | Permission Test | 非管理員角色呼叫 | 403 Forbidden |
| DELETE-06 | Integration Test | Redis 服務不可用 | 回傳 502，Cassandra 資料不受影響 |
| DELETE-07 | Flow Test | 刪除 Hash 內最後一個 field 後，檢查 Redis Key 是否自動移除 | 預期 Key 消失或 TTL 等待過期（**需人工確認**） |

---

## 9. 高風險區域

- **Redis 與 Cassandra 雙寫一致性**：無分散式事務，刪除順序應固定（先 Redis 後 Cassandra），若 Redis 成功但 Cassandra 失敗，需有重試或補償機制
- **Redis Key 洩漏**：若 Hash 變空但未刪除 Key，長期累積生成過多空 Key，佔用記憶體
- **權限誤放**：若 DELETE 端點未嚴格限制角色，可能遭誤刪大範圍賽事
- **Cache Consistency**：若有 `webpservice` 快取賽事資訊，需觸發快取失效，但目前已知 Redis 快取僅用於帳號 (`price:cache:*`)

---

## 10. 常見錯誤

- ❌ 新人誤以為只需刪除 Redis，忽略 Cassandra 歷史記錄 → 導致後續報表或歷史查詢仍出現已刪除賽事
- ❌ AI 工具在產生代碼時，未實作冪等邏輯，賽事已不存在時拋出 Exception
- ❌ 未驗證 `gameType` 是否在服務支援清單中（如 BS, BK, FB），直接進行刪除
- ❌ 直接將 `id` 當作 Redis Key 刪除，而非對 Hash 執行 `HDEL`

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `DELETE /api/v1/games/{gameType}/{lid}/{gDate}/{id}` |
| Redis DB5 | `README → 賽事即時資料（賠率、比分、狀態）` |
| Redis 結構 | `README → {gameType}:{lid}:{gDate}` |
| Cassandra | `README → Cassandra pricecenter → games` |
| 權限 | `README DELETE /api/v1/games/... 需要驗證 ✅` |
| 冪等性 | `db-usage pricecenterservice-detail → 不可回傳欄位、寫入限制，間接支持冪等設計原則` |