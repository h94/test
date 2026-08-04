# Killer 周期結算

## 1. 場景目的
後台排程或管理員手動觸發，依據 Killer 機制的週期設定，計算該週期內殺手名單的排名與應得獎金，並透過金流服務發放獎金，完成整個 Killer 週期的派彩作業。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/killers/{gameType}/{lid}/{cid}` | 查詢週期內殺手名單（排名） |
| PUT | `/api/v1/settings/killer/cycles/{gameType}/{lid}/{cid}/payout` | 觸發（手動）Killer 派彩 |

⚠️ 內部排程可能繞過 API 直接調用 Service 層（需人工確認實際排程實作方式）。

---

## 3. 流程總覽
1. 取得待結算週期：檢查 `predict.killer_cycle_settings`，確認該週期（cid）已結束且 `pay_out` 為未派彩。
2. 讀取殺手排名：依 `game_type, lid, cid` 讀取 `predict.killer_accounts`，按 `profitpoint` 降冪排序取得最終排名。
3. 計算各名次獎金：依據 `killer_cycle_settings` 中定義的獎金分配規則，算出每位殺手可獲獎勵額度。
4. 呼叫金流發放：透過 `memberservice`（或 `TransactionService`）為每位得獎帳號加點，需確保冪等性。
5. 更新派彩狀態：將 `killer_cycle_settings.pay_out` 標記為已派彩（`true`），防止重複執行。
6. 記錄結算日誌：寫入 `predict.calculate_logs` 留存結算證據。
7. 清除相關快取（如 Killer 排行榜快取，若存在）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Scheduler / Controller | `KillerSettlementJob` 或 `KillerController.Payout` | 觸發結算流程 (需人工確認實際類別) |
| 2 | Service | `KillerService.SettleCycle(gameType, lid, cid)` | 組合結算邏輯 |
| 3 | Provider (DB) | `KillerCycleSettingProvider.GetSetting(gameType, lid, cid)` | 讀取 `killer_cycle_settings`，驗證是否可派彩 |
| 4 | Provider (DB) | `KillerAccountProvider.GetAccounts(gameType, lid, cid)` | 讀取 `killer_accounts` 排序後的名單 |
| 5 | Service | `PrizeCalculationService.Calculate(ranking, setting)` | 計算各排名獎金 (需人工確認) |
| 6 | Provider (External) | `MemberServiceClient.GrantBonus(account, amount, refId)` | 調用 memberservice 發放獎金 |
| 7 | Provider (DB) | `KillerCycleSettingProvider.UpdatePayout(gameType, lid, cid, true)` | 更新 `pay_out` 狀態 |
| 8 | Provider (DB) | `CalculateLogProvider.Insert(log)` | 記錄結算日誌 |
| 9 | Cache | `CacheManager.Remove($"killer:leaderboard:{gameType}:{lid}:{cid}")` | 清除排行榜快取 (需人工確認實際 Key) |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `predict.killer_cycle_settings` | Read | 檢查週期時效、派彩狀態、獎金設定 |
| DB | `predict.killer_cycle_settings` | Update | 派彩完成後寫入 `pay_out = true` |
| DB | `predict.killer_accounts` | Read | 讀取該週期殺手排名 (依 `profitpoint` 排序) |
| DB | `predict.calculate_logs` | Write | 寫入結算記錄 (需人工確認表名) |
| Cache | `predict:killer:{gameType}:{lid}:{cid}:leaderboard` (推測) | Delete | 結算後清除舊排名快取，確保前台資料一致 (需人工確認實際 Key) |
| Queue | 無 | - | 本流程未直接使用 Kafka/Queue |

---

## 6. 重要規則
- **權限限制**：手動派彩 API 僅限管理員角色呼叫，需通過驗證。
- **不可重複派彩**：`pay_out` 欄位僅可由 `false` → `true`，結算前必須檢查其值，已為 `true` 則拒絕執行。
- **時間限制**：僅當目前時間已超過該週期的 `enddate` + `endtime` 才允許結算（需人工確認實際比對方式）。
- **獎金發放冪等性**：調用金流務必帶有唯一 `refId`（例如 `cid + account`），避免因重試導致重複加點。
- **不可暴露帳號**：殺手排行榜對外回傳時，`account` 欄位須遮蔽（如只顯示前兩碼與後兩碼）。
- **金流負責方**：predictservice 不直接操作錢包，應透過 `memberservice` 或 `TransactionService` 完成實際加點。
- **快取一致性**：派彩完成後，必須主動刪除對應的快取（若存在），不可僅依賴 TTL 過期。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 週期尚未結束就觸發派彩 | 拒絕執行，回傳錯誤訊息（如「週期尚未結束」） |
| 該週期 `pay_out` 已為 `true` 又重複觸發 | 直接回傳成功（或回報已派彩），不重複發放 |
| 讀取 `killer_accounts` 為空（無殺手） | 視為正常，仍更新 `pay_out`，寫入空日誌 |
| 部分帳號獎金發放失敗（memberservice 回傳錯誤） | 拋出異常，整批回滾（或紀錄哪些已發，哪些未發，需人工處理）（需人工確認 transaction 機制） |
| `killer_cycle_settings` 中缺少獎金設定 | 結算中斷，回傳設定異常錯誤，需人工補正 |
| Cassandra 寫入 `pay_out` 失敗 | 丟出 exception，結算失敗，避免狀態不一致 |
| Redis 快取清除失敗 | 不影響結算成功性，但前台可能短暫顯示舊排行榜，需有告警 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| KT-01 | Flow Test | 週期結束後，排程自動觸發結算（模擬） | `pay_out` 變為 `true`，獎金正確入帳 |
| KT-02 | API Test | 管理員手動呼叫 payout API | 成功發放，與排程結果一致 |
| KT-03 | Idempotency | 重複呼叫 payout API 兩次 | 第二次立即回傳 200（或特定訊息），不重複發放 |
| KT-04 | Boundary | 結算時 `killer_accounts` 無任何資料 | 流程順利完成，無任何發放，`pay_out` 仍更新 |
| KT-05 | Permission | 一般使用者呼叫 payout API | 回傳 403 或驗證失敗 |
| KT-06 | Failure | 模擬 memberservice 發放失敗 | 結算失敗，`pay_out` 未變，無任何帳號加點 (或只有部分加點需確認) |
| KT-07 | Cache | 派彩後前台查詢排行榜 | 回傳最新結算後排名（快取已清除或重新計算） |

---

## 9. 高風險區域
- **金流一致性**：跨服務發放獎金若無 transaction 保護，可能部分成功部分失敗，遺留髒資料。
- **重複派彩**：`pay_out` 狀態若未原子化更新，或快取干擾，可能導致重複發放獎金。
- **手動觸發風險**：管理員誤觸發未結束週期，若未攔截時間，將導致未完成比賽即派彩。
- **快取不一致**：結算後未清除 ranking 快取，用戶持續看到舊排名，產生客訴。
- **大量殺手名單**：若該週期殺手數量極多，一次性調用金流可能超時，需考慮批量處理。

---

## 10. 常見錯誤
- ❌ 結算時未檢查 `pay_out`，導致重複發放獎金。
- ❌ 直接寫入 `profitpoint` 或 `rank` 到 `killer_accounts` 而忽略應由結算邏輯計算（推測該表由結算排程寫入，而非外部 API）。
- ❌ 調用金流時未攜帶 idempotency key，導致重試時重複加點。
- ❌ 忘記在結算後清除相關 Redis 快取，使用者持續看到舊資料。
- ❌ 對外回傳排行榜時暴露完整 `account`（違反個資規則）。
- ❌ 誤將 `pay_out` 欄位直接回傳給前端（內部狀態不應暴露）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| 場景觸發描述 | README.md → 常見使用場景 #3 |
| 派彩 API | OpenAPI → PUT `/api/v1/settings/killer/cycles/{gameType}/{lid}/{cid}/payout` |
| 殺手名單 API | OpenAPI → GET `/api/v1/killers/{gameType}/{lid}/{cid}` |
| 資料表定義 | README.md → 資料庫重要 Table：`killer_cycle_settings`, `killer_accounts` |
| DB 讀取規則 | predictservice-detail.md → `killeraccounts_{gameType}` 查詢規則 |
| 派彩狀態欄位 | predictservice-detail.md → 無直接提及，但根據 `betpool_games.payout` 推測類似的 boolean 機制 |
| 金流發放 | predictservice-detail.md → 本服務不負責彩金派發，由 TransactionService / WalletService 執行 |
| 帳號遮蔽規則 | predictservice-detail.md → 不可回傳欄位：公開 API 不可暴露 `account` |
| 快取相關 (推測) | predict-detail.md → Redis `predict:game:{gid}:status` 主動清除機制，推論 killer 亦需類似處理 |