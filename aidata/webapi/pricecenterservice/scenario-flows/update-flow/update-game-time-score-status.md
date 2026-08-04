# 更新賽事時間比分狀態

## 1. 場景目的
允許後台管理員或比分機器人同時更新指定賽事的比賽時間、即時比分與狀態，並透過 SignalR 即時推播至前台，確保顯示的資料為最新。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/games/{gameType}/{lid}/{gDate}/{id}/time-score-status` | 更新賽事時間、比分與狀態 |

- **需要驗證**：是（✅）
- **來源**：[README.md](#對外-api-重點) ・ OpenAPI（需人工確認）

---

## 3. 流程總覽

1. 接收 PUT 請求，包含 `gameType`、`lid`、`gDate`、`id`，與 Body 中的時間、比分、狀態資訊。
2. 驗證認證資訊（E C 內部統一驗證框架）。
3. 驗證路徑參數與 Body 結構（時間格式、比分格式、狀態值範圍）。
4. 從 Redis DB5 讀取現有賽事資料（Key：`{gameType}:{lid}:{gDate}`，內部包含該賽事物件）。
5. 更新賽事物件中的時間、比分、狀態欄位。
6. 將更新後的賽事資料寫回 Redis DB5。
7. 寫入 Cassandra `pricecenter.games` 表，記錄歷史比分狀態（異步或同步 - 需人工確認）。
8. 透過 SignalR 將更新事件推送至對應的前台頻道。
9. 回傳 200 OK 及更新後的賽事摘要（或不回傳明細，避免暴露過多資料）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `GameController.PutTimeScoreStatus`（*待確認*） | 接收請求，調用 Service |
| 2 | Validator | `TimeScoreStatusValidator`（*待確認*） | 驗證輸入格式 |
| 3 | Service | `GameService.UpdateTimeScoreStatusAsync`（*待確認*） | 組合流程，控制事務邊界 |
| 4 | Provider | `RedisProvider.GetGameAsync` / `SetGameAsync` | 讀寫 Redis DB5 |
| 5 | Provider | `CassandraProvider.UpsertGameAsync`（*待確認*） | 寫入 Cassandra |
| 6 | Provider | `SignalRPublisher.PublishAsync`（*待確認*） | 推送即時更新 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Redis | DB5: `{gameType}:{lid}:{gDate}` | Read, Write | 賽事即時資料快取，讀取現有賽事後修改並寫回 |
| Cassandra | `pricecenter.games` | Write (Insert/Update) | 持久化賽事歷史比分、狀態變更 |
| SignalR | Hub 群組（例：`game-{gameType}-updates`） | Publish | 即時通知前台更新比分與狀態 |

- **Queue/Kafka 未使用**（此場景未涉及，除非有後續結算流程觸發，但非此 API 範圍）。

---

## 6. 重要規則

- **權限限制**：僅後台管理角色或授權的比分機器人可調用；需驗證身分。
- **欄位限制**：比分、時間、狀態更新時，**不可修改不允許的欄位**（如 `gid`、`lid`、`gDate` 主鍵屬性）。
- **不可暴露資料**：回應中**不應包含盤口內部資料、賠率計算參數**等敏感資訊。
- **狀態值限制**：狀態必須符合定義值（例如 0:未開始, 1:進行中, 2:結束 等，需人工確認）。變更為結束狀態時可能視為高風險操作（需檢查是否觸發結算）。
- **Transaction 規則**：Redis 寫入與 Cassandra 寫入不在同一交易中，存在短暫不一致，需透過後端補償或記錄日誌處理（*需人工確認補償機制*）。
- **TTL 規則**：Redis 賽事資料無 TTL（default 0，由業務管理），更新後不更改 TTL。
- **Retry 規則**：Cassandra 寫入失敗可重試 3 次（需人工確認），仍失敗則觸發告警。
- **不可修改欄位**：`lid`, `gDate`, `id` 路徑參數僅用於定位，不可透過 Body 修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 認證失敗（無效 Token） | 回傳 401 Unauthorized |
| 參數缺失或格式錯誤 | 回傳 400 Bad Request，明確錯誤訊息 |
| Redis 中不存在該賽事（Key 不存在） | 回傳 404 Not Found |
| Redis 寫入失敗（連線中斷） | 回傳 500 Internal Server Error，記錄錯誤 |
| Cassandra 寫入失敗 | 回傳 200（前端仍可使用最新 Redis 資料），但記錄錯誤，需人工確認是否需 rollback Redis |
| SignalR 推送失敗 | 不影響回應，記錄警告，後續可考慮重試機制 |
| 併發更新（兩個請求同時更新同一賽事） | 後處理者覆蓋前處理者，應確保更新為全量寫入（需人工確認是否使用樂觀鎖） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| UT001 | API Test | 正常更新比分、狀態 | 200 OK，Redis 與 Cassandra 更新 |
| UT002 | API Test | 缺少必填 Body 欄位 | 400 Bad Request |
| UT003 | Permission Test | 無 Token 呼叫 | 401 Unauthorized |
| UT004 | Flow Test | 更新後檢查前台 SignalR 訊息 | 前台收到對應更新事件 |
| UT005 | Integration Test | Redis 不可用時呼叫 | 500 或降級處理，記錄錯誤 |
| UT006 | Idempotency Test | 重複傳送相同更新 | 第二次請求成功，無副作用（冪等） |

---

## 9. 高風險區域

- **Redis 與 Cassandra 雙寫一致性**：先寫 Redis 後寫 Cassandra，若 Cassandra 失敗則歷史缺失，必須記錄並補償。
- **賽事狀態變更觸發結算**：若狀態變更為「已結束」，可能應呼叫 `setfinal` API 或通知 `predictservice`（需人工確認此端點是否自動觸發）。
- **並發寫入**：可能造成資料被蓋回舊值，需確認是否加入 `version` 欄位或使用 Redis 的 WATCH 機制（*需人工確認*）。
- **時間同步**：服務器時間與請求時間的處理，可能影響排序（*需人工確認規範*）。

---

## 10. 常見錯誤

- ❌ **只更新 Redis 而忘記寫 Cassandra** → 導致歷史資料無法追溯。
- ❌ **直接覆蓋整個 Redis 物件而未先讀取** → 可能遺失其他即時資料（如賠率）。
- ❌ **API 回應中包含不必要資料** → 應只回傳成功標誌或精簡摘要。
- ❌ **未處理時間格式** → 時間應以統一的 UTC 或特定格式儲存（*需人工確認*）。
- ❌ **狀態值使用未定義的數值** → 需列舉狀態碼，否則可能導致後續流程判斷錯誤。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | README：`PUT /api/v1/games/{gameType}/{lid}/{gDate}/{id}/time-score-status` |
| Redis DB5 賽事資料 | README：「`{gameType}:{lid}:{gDate}` 賽事即時資料（賠率、比分、狀態）」 |
| Cassandra games 表 | README：「Cassandra pricecenter: games 賽事歷史資料（結果、比分）」 |
| SignalR 即時推播 | README：技術棧包含 SignalR，場景2「更新 Redis + Cassandra → SignalR 推播前台」 |
| 驗證 | README：API 標記需要驗證 ✅ |
| 程式架構 | 推測：Controller → Service → Provider（Redis / Cassandra / SignalR），僅憑命名慣例，需人工確認具體類名。 |