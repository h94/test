# 查詢活動排行榜

## 1. 場景目的

查詢特定活動週期的贏家排行榜，支援依排名或獲利點數排序，並對帳號進行部分字元遮蔽以保護隱私。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/activity/leaderboards/winrate/{site}/{activityEvent}` | 查詢活動週期排行；authKey 為選填查詢參數 |

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，路徑包含 `site`、`activityEvent`，查詢字串可含 `authKey`。
2. 驗證權限：若有 authKey，需驗證其有效性（對應有效的 gameuser 且 status=1），但排行榜本身為公開資料，非強制登入。
3. 呼叫子流程查詢當前有效活動週期（`activities_cycles`）。
4. 依照週期 ID（`cid`）查詢 `activities_winneraccounts` 表，取得該週期所有贏家記錄。
5. 依優先序進行排序：
   - 先依 `rank` 升冪（若有值）。
   - 若無 rank，則依 `profitpoint` 降冪。
6. 將 `account` 欄位進行字元遮蔽處理（隱私保護）。
7. 組裝回應 DTO 並回傳。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `ActivityController.GetWinRateLeaderboard` | 接收請求，提取路徑參數與 authKey |
| 2 | Validator | ECCore 3.0.2 Auth Middleware | 若 authKey 存在，驗證其有效性（對應 `gameusers` record 且 `status=1`）。非強制 |
| 3 | Service | `PredictActivityLeaderboardService` 或類似 Activity Service | 協調組裝排行榜資料 |
| 4 | Provider | `ActivityProcess` 或 `PredictTransfer` | 讀取 `activities_cycles` 取得目前有效週期 |
| 5 | Provider | `ActivityProcess` 或 `PredictTransfer` | 讀取 `activities_winneraccounts`，WHERE `site=? AND activityevent=? AND cid=?` |
| 6 | Transfer | DTO Mapper | 對 `account` 欄位執行遮蔽邏輯，組裝回應模型 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `predict.activities_cycles` | Read | 查詢當前有效活動週期 (`cid`) |
| DB | `predict.activities_winneraccounts` | Read | 查詢指定週期所有贏家排名資料 |
| DB | `member.gameusers` | Read（若需驗證 authKey） | 確認會員存在且狀態有效 |
| Redis | `predict:activity:{site}:{eventname}:{cid}:leaderboard`（推測） | Get | 可選的排行榜快取，若命中則跳過 DB 查詢 |
| Queue | （無） | - | 本流程不使用訊息佇列 |

---

## 6. 重要規則

- **排序優先序**：先 `rank` ASC，再 `profitpoint` DESC。`rank` 為選填欄位，有值時優先使用。
- **帳號隱私遮蔽**：`account` 欄位必須遮蔽（如 `abc***xyz`），不可回傳完整帳號。具體遮蔽邏輯需符合站點隱私政策。
- **唯讀限制**：`pricecentersite` 服務僅可 SELECT `predict` keyspace，不可寫入。
- **週期有效性**：查詢 `activities_cycles` 時，須符合 `startdate/starttime <= now <= enddate/endtime`。
- **分區鍵強制**：查詢 `activities_winneraccounts` 時必須提供完整 Partition Key（`site, activityevent, cid`），避免跨分區掃描。
- **不可回傳欄位**：僅回傳 `rank`、`profitpoint`、`winpercentage` 等摘要指標，不可回傳 `winbets` 或其他注單明細。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 缺少 `site` 或 `activityEvent` 路徑參數 | HTTP 400 Bad Request |
| authKey 存在但無效或使用者被停用 | 忽略 authKey，仍回傳公開排行榜（或回 HTTP 401，視業務邏輯） |
| 無任何有效活動週期（`activities_cycles` 無符合記錄） | 回傳空列表或 HTTP 204 No Content |
| 指定週期尚無贏家記錄 | 回傳空列表 |
| Cassandra 查詢逾時 | HTTP 500 Internal Server Error，觸發重試機制（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| LB-01 | API Test | 提供有效 `site` 與 `activityEvent`，無 authKey | 成功回傳該週期所有贏家，account 已遮蔽，依 rank/profitpoint 排序 |
| LB-02 | API Test | 提供有效 authKey 且使用者為 VIP | 成功回傳，與 LB-01 相同 |
| LB-03 | Permission | 提供被停用使用者的 authKey | 仍回傳排行榜（或 401，需人工確認） |
| LB-04 | Flow Test | 活動剛開始，尚無 `activities_winneraccounts` 資料 | 回傳空陣列 `[]` |
| LB-05 | Data Masking | 檢查回傳的 `account` 欄位 | 所有 `account` 均被遮蔽，無完整帳號出現 |

---

## 9. 高風險區域

- **隱私洩漏**：若遮蔽邏輯錯誤或忘記呼叫，可能直接回傳完整帳號，違反隱私政策。
- **跨分區查詢**：查詢 `activities_winneraccounts` 時若省略 `cid`，將導致 Cassandra 跨分區掃描，極度耗費資源。
- **快取一致性**：若使用 Redis 快取排行榜，在週期更新或新結果產生時未即時清除，前端可能顯示過期資料。

---

## 10. 常見錯誤

- ❌ 回傳未遮蔽的 `account` 欄位 → 必須在 DTO 層或 Service 層處理。
- ❌ 未提供 `cid` 即查詢 `activities_winneraccounts` → 必須先取週期再查。
- ❌ 誤將 `activities_winneraccounts` 的 `winpercentage` 或 `predictcount` 直接作為敏感資料排除 → 此類摘要指標可安全回傳。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `ActivityController`（推測路徑 `/api/activity/leaderboards/winrate/{site}/{eventName}`） |
| DB | `predict.activities_winneraccounts`，`predict.activities_cycles` |
| Code | `PredictActivityLeaderboardService` 或類似 Activity Service |
| Rules | `predict-detail.md`：排行榜查詢、隱私遮蔽規則、排序規則 |