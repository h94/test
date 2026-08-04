# 更新派彩狀態

## 1. 場景目的
標誌獎池賽事（BetPool Game）已完成派彩。此操作是結算流程的最終步驟，將 `betpool_games` 表中的 `payout` 欄位標記為 `true`，表示獎金已成功發放給所有中獎玩家。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/v1/betpool/games/{id}/payoutdtatus` | 更新指定獎池賽事的派彩狀態 |

---

## 3. 流程總覽
1. 接收包含遊戲 `id` 的 PUT 請求。
2. 驗證請求者的管理權限。
3. 根據 `id` 查詢 `predict.betpool_games` 表。
4. 驗證遊戲是否存在，以及其當前 `payout` 狀態為 `false`（防止重複派彩）。
5. 驗證遊戲 `status` 是否已達到可派彩狀態（例如：2 已結算）。
6. 更新 `betpool_games` 表中該遊戲的 `payout` 欄位為 `true`。
7. 主動刪除相關的 Redis 快取，確保前台能立即獲取到更新後的遊戲狀態。
8. 回傳操作成功。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `BetpoolController.PayoutStatus` | 接收請求，呼叫 Service。 |
| 2 | Service | `BetpoolService.UpdatePayoutStatus` | 協調流程。先查詢遊戲實體。 |
| 3 | Provider | `BetpoolGameProvider.GetGameById` | 根據 `id` 從 `predict.betpool_games` 讀取遊戲記錄。 |
| 4 | Service | `BetpoolService.UpdatePayoutStatus` | 驗證遊戲存在、`payout` 為 `false`、`status` 符合條件。 |
| 5 | Provider | `BetpoolGameProvider.UpdatePayoutFlag` | 執行 `UPDATE predict.betpool_games SET payout = true WHERE id = ?`。 |
| 6 | Service | `BetpoolService.UpdatePayoutStatus` | 呼叫 Cache Service 清除快取。 |
| 7 | Provider | `CacheProvider.DeleteAsync` | 刪除 Redis Key：`predict:game:{id}:status`。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.betpool_games` | Read | 讀取遊戲記錄以驗證當前狀態。 |
| DB | `predict.betpool_games` | Update | 將 `payout` 欄位從 `false` 更新為 `true`。 |
| Redis | `predict:game:{id}:status` | Delete | 遊戲狀態變更後，強制失效快取以保證資料一致性。 |
| Queue | `applogs` (Kafka) | Publish | 發送操作日誌。 |

---

## 6. 重要規則
- **狀態不可逆**：`payout` 只能從 `false` 改為 `true`，一旦設定為 `true` 後，**不可**再改回 `false`。
- **冪等性**：對同一個已標記為 `payout=true` 的遊戲再次呼叫此 API，應直接回傳成功或給出明確提示，不可重複執行派彩邏輯。
- **前置狀態檢查**：通常只有在 `status` 為 2 (結算) 且 `winresult` 不為空時，才允許將 `payout` 標記為 `true`。**需人工確認**具體的前置狀態條件。
- **權限限制**：此 API 屬於敏感操作，僅允許具有後台管理或結算權限的角色（如 `masterservice`, `predictresultservice` 觸發）呼叫。
- **快取一致性**：更新 `payout` 後，**必須** 主動刪除 Redis 快取。根據 `predict-detail.md`，`predict:game:{id}:status` 快取的 TTL 為 30 秒，若不及時失效，前台可能顯示未派彩的過期狀態。
- **不可修改欄位**：此 API 僅修改 `payout`，絕不可修改 `starttime`, `endtime`, `betoptions` 等其他欄位。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求的 `{id}` 不存在 | 回傳 404 Not Found。 |
| 遊戲的 `payout` 狀態已經為 `true` | 回傳 400 Bad Request 或 200 OK（根據冪等性設計），提示「遊戲已派彩」。 |
| 遊戲的 `status` 不滿足派彩條件（例如仍為 0 或 1） | 回傳 422 Unprocessable Entity，提示「遊戲尚未結算，無法派彩」。 |
| 請求者不具備管理員權限 | 回傳 403 Forbidden。 |
| 更新 DB (`betpool_games`) 失敗 | 回傳 500 Internal Server Error，並記錄錯誤日誌。 |
| Redis 快取刪除失敗 | 記錄錯誤日誌，但**不影響**主要業務流程（DB 更新已成功），可依靠 TTL 最終一致。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-01 | Unit Test | 正常流程：對一個 `status=2, payout=false` 的遊戲標記派彩。 | DB 的 `payout` 更新為 `true`，Redis Key 被刪除。 |
| UT-02 | Unit Test | 異常流程：重複派彩 (`payout` 已為 `true`)。 | 根據設計，應直接回傳成功或拋出特定異常。DB 無變化。 |
| IT-01 | API Test | 對不存在的遊戲 ID 發送請求。 | HTTP Status 404。 |
| IT-02 | API Test | 使用不具權限的用戶 Token 請求。 | HTTP Status 403。 |
| IT-03 | Flow Test | 模擬 Game Flow： 遊戲創建 → 下注 → 狀態改為關閉 → 狀態改為結算 → 更新派彩狀態。 | 每個步驟都需驗證狀態機的正確性。 |

---

## 9. 高風險區域
- **DB Table**：`predict.betpool_games`。此表記錄了遊戲核心狀態，錯誤的 `payout` 更新會導致獎金重複發放或無法發放，直接影響金流。
- **Cache Consistency**：DB 更新後若未清除 `predict:game:{id}:status` 快取，將導致 C 端用戶看到過時的遊戲狀態，可能引發客訴。
- **Idempotency**：若 API 不具冪等性，重複請求可能觸發下游重複執行派彩操作（如果此 API 不僅僅是標記，還觸發其他邏輯），造成嚴重金流錯誤。**需人工確認**此 API 是否僅為標記功能，或會觸發其他派彩流程。

---

## 10. 常見錯誤
- ❌ 在遊戲尚未結算 (`status != 2`) 或結果未確認時，就呼叫此 API 標記派彩。
- ❌ 忘記在 `payout` 更新後清除 Redis 快取。
- ❌ 未檢查 `payout` 的當前狀態就嘗試更新，可能導致錯誤地將 `true` 覆蓋（雖然業務上不應發生）。
- ❌ 認為更新 `payout` 失敗是無關緊要的錯誤，而未進行告警和重試。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README: `PUT /api/v1/betpool/games/{id}/payoutdtatus` |
| DB Table | `predict.betpool_games` (Schema: `payout boolean`) |
| DB 規則 | `predict-detail.md`: `payout` 僅能從 false 變更為 true，不可反向回退 |
| DB 規則 | `predict-detail.md`: payout=true 之前不可回傳 winresult 給前端 |
| Redis | `predict-detail.md`: Key `predict:game:{gid}:status`, 狀態變更時必須主動 DEL |
| Code | **需人工確認** `BetpoolController` 與 `BetpoolService` 的具體實作名稱。 |