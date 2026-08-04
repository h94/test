# 建立排行榜

## 1. 場景目的

提供後台管理員或自動化排程觸發，為特定活動賽事產生 **競猜排行榜**、**Killer 排行榜** 與 **勝率排行榜**。此場景涵蓋如何根據已結算的下注記錄，計算各帳號的總利潤點數 / 勝率，並最終寫入對應的排行榜儲存空間，供前台查詢使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/system/leaderboard/predicet` | 建立競猜排行榜 |
| POST | `/api/v1/system/leaderboard/killeraccount` | 建立 Killer 排行榜 |
| POST | `/api/v1/system/leaderboard/winningrate/{gameType}` | 建立勝率排行榜 |

> **需人工確認**：OpenAPI 文件中未包含上述 `/api/v1/system/leaderboard/*` 路由的具體 Request Body 與 Response Schema，此處資訊基於 `README.md`。

---

## 3. 流程總覽

1. 接收建立排行榜的 request（包含站點、活動事件、週期等參數）。
2. 驗證操作者權限（需管理員或內部服務呼叫）。
3. 根據請求類型，讀取對應的資料來源：
   - 競猜排行榜：查詢 `predict.predict_bets` 或 `predict.betpool_bets` 已結算記錄。
   - Killer 排行榜：查詢 `predict.killer_accounts` 帳號名單。
   - 勝率排行榜：查詢 `predict.predict_filter_reports` 或原始下注記錄。
4. 執行排行榜計算邏輯（彙總 `profitpoint`、`winpercentage`、`predictcount`）。
5. 將計算結果寫入排行榜儲存表，如 `predict.activities_winneraccounts`。
6. 若需要，發送 Kafka 事件通知前台或相關服務更新快取。

---

## 4. 程式流程

> **需人工確認**：因缺少 `LeaderboardController` 的具體程式碼，以下流程基於服務邊界與 DB 使用規則推斷。

| 順序 | Layer | Class / Method (推斷) | 動作 |
|------|------|----------------------|------|
| 1 | Controller | `SystemController.CreateLeaderboard()` | 接收 POST request，驗證權限 |
| 2 | Service | `LeaderboardService.Create()` | 解析輸入條件，協調計算流程 |
| 3 | Provider | `PredictDataProvider` | 讀取 Cassandra 中的 `predict_bets` 或 `betpool_bets` |
| 4 | Service | `LeaderboardService.Calculate()` | 依帳號彙總利潤、勝率、排名 |
| 5 | Provider | `PredictDataProvider` | 將結果寫入 `activities_winneraccounts` |
| 6 | Service | `LeaderboardService` | 清除 Redis 中的排行榜快取 (`predict:activity:{site}:{eventname}:{cid}:leaderboard`) |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `predict.predict_bets` | Read | 讀取已結算的下注記錄用於計算排行榜 |
| DB | `predict.betpool_bets` | Read | 讀取獎池下注記錄用於計算排行榜 |
| DB | `predict.activities_winneraccounts` | Write | 寫入計算後的排名、利潤點數、勝率、預測次數 |
| DB | `predict.activities_cycles` | Read | 驗證請求的活動週期是否有效 |
| DB | `predict.killer_accounts` | Read | 讀取 Killer 帳號名單用於計算 Killer 排行榜 |
| DB | `member.gameusers` | Read | 驗證帳號是否存在且狀態為啟用 (`status = 1`)，並讀取基本顯示資訊，但**嚴禁回傳 `email`、`authkey`、`password`** |
| Redis | `predict:activity:{site}:{eventname}:{cid}:leaderboard` | Delete | 排行榜更新後，主動清除舊快取以確保資料一致性 |

---

## 6. 重要規則

- **權限限制**：此操作僅限內部管理服務或具有管理員權限的角色呼叫。
- **狀態值限制**：只能對已結束且已派彩的賽事（`status=2`, `payout=true`）進行排行榜計算。
- **不可暴露資料**：
  - `member.gameusers.email`, `authkey`, `password` 在任何 API 回傳中均不可出現。
  - `predict.activities_winneraccounts.account` 在回傳給前台的公開排行榜中可能需要脫敏處理（依產品需求）。
- **寫入限制**：
  - 對 `predict.activities_winneraccounts` 的 `rank`, `profitpoint`, `predictcount`, `winpercentage` 等欄位，**僅能由內部結算排程或此排行榜建立流程寫入**，不可由外部 API 或人工直接修改。
- **快取規則**：排行榜計算完成並寫入 DB 後，**必須**立即刪除對應的 Redis 快取 Key，不可僅依賴 TTL 過期。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求的活動週期不存在或已失效 | 返回 400 Bad Request，提示活動無效 |
| 操作者權限不足（例如一般使用者呼叫） | 返回 403 Forbidden |
| 計算過程中 Cassandra 讀取超時 | 返回 500 Internal Server Error，紀錄錯誤日誌至 Kafka |
| 嘗試對尚未結算的賽事建立排行榜 | 返回 400 Bad Request，提示賽事狀態不符 |
| Redis 快取清除失敗（Redis 不可用） | 不影響主流程，僅記錄警告日誌，排行榜資料已更新為最新 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| LB-01 | Permission Test | 使用一般用戶 token 呼叫 API | 應返回 403 |
| LB-02 | Flow Test | 對已結算且派彩的活動建立競猜排行榜 | 成功返回 200，`activities_winneraccounts` 寫入正確排名，Redis 快取被清除 |
| LB-03 | Flow Test | 對進行中的活動建立排行榜 | 返回 400，無任何排行榜資料被建立 |
| LB-04 | API Test | 建立勝率排行榜，指定 gameType | 排行榜正確計算勝率並排序 |
| LB-05 | Flow Test | 建立 Killer 排行榜 | 成功計算殺手利潤排名並寫入對應表 |

---

## 9. 高風險區域

- **高風險 table**：`predict.activities_winneraccounts`。錯誤的寫入邏輯可能導致前台排行榜顯示混亂，且難以復原。
- **Transaction**：Cassandra 不支援傳統 RDBMS 的 ACID 事務。若寫入排行榜的過程中服務崩潰，可能導致部分資料已寫入。**需人工確認**：是否有 Rollback / idempotent 機制。
- **Cache consistency**：排行榜寫入 DB 後，未正確清除 Redis 快取將導致資料不一致。這是高風險項目。
- **跨服務資料同步**：若有其他服務直接讀取排行榜表，則本服務的寫入邏輯變更需同步通知。

---

## 10. 常見錯誤

- **新人容易犯錯**：在查詢下注記錄時，未過濾 `status=2` (結算) 和 `payout=true`，導致將未結算的投注納入計算。
- **AI 容易誤解**：直接用 `betpool_bets.account` 彙總後回傳排行榜，違反 DB 操作邊界中排行榜不應暴露其他帳號的規定。
- **常見漏檢查項目**：忘記在排行榜計算結束後清除 Redis 快取 (`predict:activity:{...}:leaderboard`)。
- **常見錯誤流程**：試圖在前台查詢排行榜的 API 中即時計算排名，而非讀取預先算好的 `activities_winneraccounts`，導致效能瓶頸。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | README.md - 系統工具 `/api/v1/system/leaderboard/predicet` |
| API | README.md - 系統工具 `/api/v1/system/leaderboard/killeraccount` |
| API | README.md - 系統工具 `/api/v1/system/leaderboard/winningrate/{gameType}` |
| DB | predictservice-detail.md - `predict.activities_winneraccounts` 寫入限制 |
| DB | predict-detail.md - `predict.activities_winneraccounts` 不可回傳欄位 |
| DB | predict-detail.md - `predict.activities_cycles` 讀取規則 |
| DB | member-detail.md - `member.gameusers` 不可回傳欄位 |
| Redis | predict-detail.md - `predict:activity:{site}:{eventname}:{cid}:leaderboard` 快取規則 |

---
**建議事項**：
- 建議新增文件：`rules/leaderboard-calculation` 規則檔，描述排行榜計算公式與排除條件（例如是否排除機器人、取消下注）。
- 建議新增測試：針對 `activities_winneraccounts` 的寫入 Idempotency 進行測試，確保重複觸發不會產生重複列或錯誤排名。