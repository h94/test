# 冠軍賽結算

## 1. 場景目的

後台管理員觸發冠軍賽（Supreme）週期的結算流程，根據該週期內所有參與者的預測表現，產生最終排名並記錄獲勝者名單，可能伴隨點數發放或會員資格更新。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/member/supreme/winners` | 觸發冠軍賽結算，產出獲勝者 |
| PUT | `/api/v1/member/supreme/cycles/{gameType}/{lid}/{cid}/settlement` | 更新特定週期的結算狀態（推測用於確認結算或手動修正） |

（以上路由來自 pricebackendservice README 會員管理區塊）

---

## 3. 流程總覽

1. 後台管理員透過後台前端呼叫冠軍賽結算 API（POST winners）。
2. `PriceBackendService`（BFF）接收請求，驗證管理者權限。
3. BFF 將請求轉發至下游服務（推測為 `memberservice` 或 `predictservice`，需人工確認）。
4. 下游服務執行結算核心邏輯：
   - 讀取 `activities_cycles` 確認週期存在、未結算且已結束。
   - 彙整該週期的預測/投注資料（可能來自 `betpool_bets` 或 `predictbets_{gtype}` 系列表），計算每位會員的排名（命中數、勝率、獲利點數等）。
   - 將計算結果寫入 `activities_winneraccounts`（不允許 API 直接寫入，由系統自動設定）。
   - 更新 `activities_cycles.resultcount`（由系統自動更新）、設定週期結束時間或狀態。
   - 若有發放點數需求，呼叫相關錢包服務（`memberservice`）進行點數增加，並可能寫入會員資格標記（如 `memberships` 中新增 `supreme_*` 記錄）。
   - 清除相關快取（如 `predict:winners:{cid}`、活動排行快取等）。
5. 回傳成功結果給後台。
6. （可選）後台可再用 PUT settlement 更新週期結算狀態，進行確認或手動干預。

> 註：PriceBackendService 為 BFF，不直接存取 DB；因此實際的 DB 操作均發生在下游服務（predictservice / memberservice）內部。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `MemberController.SupremeWinners` | 接收 POST，驗證授權，呼叫 Service |
| 2 | Service | `SupremeService`（推測） | 組裝參數，選擇下游路由，發送 HTTP 請求至下游 `memberservice` 或 `predictservice` |
| 3 | (下游) Service | `MemberService` 或 `PredictService` | 執行結算邏輯（讀寫 activities_* 表、計算排名） |
| 4 | (下游) Provider | `PredictDataProvider` 或 `ActivityProvider` | 實際操作 Cassandra `predict.activities_cycles`、`activities_winneraccounts` |
| 5 | (下游) Provider | `MemberWalletProvider`（若發點數） | 呼叫錢包服務或直接寫入 `member.gameusers_wallet`、`memberships` |
| 6 | (下游) Cache | Redis | 結算完成後清除 `predict:winners:{cid}` 等快取 |

> 由於無 pricebackendservice 內部 controller/service source code，以上層次為基於 BFF 架構的推測，需人工確認實際呼叫鏈。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `predict.activities_cycles` | Read | 驗證週期狀態、取得時間範圍 |
| DB | `predict.activities_cycles` | Update | 寫入 `resultcount`（系統自動更新） |
| DB | `predict.activities_winneraccounts` | Write | 新增獲勝者紀錄（rank, predictcount, profitpoint, winpercentage 由系統計算寫入） |
| DB | `member.gameusers_wallet` | Update（可能） | 發放點數，增加 `Balance`（需透過交易 API，不可直接 UPDATE） |
| DB | `member.gameusers.memberships` | Append（可能） | 添加冠軍賽會員資格標記（`supreme_*`） |
| DB | `member.gameusers.lastactiontime / lastchecktime` | Update（可能） | 更新最後活動或檢查時間 |
| Redis | `predict:winners:{cid}` | Set / Del | 結算後更新或清除 Winners 快取 |
| Redis | `predict:activity:{site}:{eventname}:{cid}:leaderboard` | Del | 結算後使排行榜快取失效 |

---

## 6. 重要規則

- **權限限制**：僅後台管理員可操作，需通過內部驗證（ECFramework）。
- **週期狀態檢查**：必須確認 `activities_cycles` 的 `cid` 有效，且其 `enddate` / `endtime` 已過（或符合結算條件），避免對未結束週期結算。
- **不可重複結算**：同一週期若已存在 `activities_winneraccounts` 紀錄，應拒絕再次結算或採用冪等設計。
- **不可回傳敏感欄位**：排行榜回傳時須對 `account` 進行脫敏（如遮蔽後四碼），對外不應暴露原始帳號。
- **資料不可手動寫入**：`activities_winneraccounts` 的 `rank`、`predictcount`、`profitpoint`、`winpercentage` 必須由系統根據實際投注記錄計算，API 不可直接傳入這些數值。
- **點數發放限制**：若涉及點數，必須透過 `TransferMember` 等專用交易 API，不可直接 `UPDATE Balance`。
- **會員資格附加**：若寫入 `memberships`，僅可 `APPEND`，禁止直接 `REPLACE` 整個 list，避免遺失其他服務寫入的資格。
- **快取一致性**：結算完成後必須主動刪除相關 Redis key，確保前台不會讀到舊排名。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 週期 `cid` 不存在 | 回傳錯誤，提示週期無效 |
| 週期尚未結束（當前時間 < endtime） | 回傳錯誤，不允許提前結算 |
| 該週期已結算（`activities_winneraccounts` 已存在資料） | 回傳錯誤或直接回傳已結算結果（冪等） |
| 週期內無任何預測記錄 | 回傳成功但排名列表為空，或回傳特定訊息 |
| 下游 `predictservice` 或 `memberservice` 不可用 | 回傳 502 或特定服務錯誤訊息 |
| 點數發放失敗（錢包服務異常） | 可能導致部分成功？需確認是否需 rollback 或記錄失敗日誌；建議整個結算流程為原子性或使用補償機制 |
| 權限不足（非管理員 token） | 回傳 401/403 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T01 | Permission Test | 無效 token 或無管理者權限呼叫 | 401/403 |
| T02 | Flow Test | 對已結束且未結算的週期執行結算 | 成功，回傳獲勝者列表，DB 寫入正確 |
| T03 | Flow Test | 週期內有 100 筆下注，驗證排名計算正確性 | 排名與 profitpoint 符合公式 |
| T04 | API Test | 重複呼叫結算 API | 第一次成功，第二次回傳錯誤或冪等返回相同結果 |
| T05 | API Test | 週期尚未結束呼叫 | 錯誤回應，狀態碼 400 |
| T06 | Integration Test | 下游 predictservice 模擬異常 | BFF 回傳 5xx，並記錄錯誤 |
| T07 | Cache Test | 結算後查詢排行榜是否更新 | 舊快取被清除，新資料正確 |
| T08 | Flow Test | 結算時包含點數發放 | 錢包餘額增加，交易記錄存在 |
| T09 | Data Integrity Test | 確認 `activities_winneraccounts` 寫入的欄位均由系統生成，無外部傳入 | 即使 request 帶有 rank 參數也被忽略 |

---

## 9. 高風險區域

- **高風險 table**：`predict.activities_winneraccounts`（寫入排名不可逆）、`member.gameusers_wallet`（餘額異動）。
- **高風險 API**：`POST /api/v1/member/supreme/winners`（可能觸發金流及會員狀態變更）。
- **跨服務資料同步**：BFF 呼叫下游服務，需確保請求的冪等性與逾時重試機制。
- **Transaction**：若結算包含多個寫入（排名 + 點數 + 會員資格），可能需要分散式事務或基於 Saga 的補償；目前資訊不足，需人工確認實作方式。
- **Cache consistency**：結算後必須立即清除相關快取，否則前台顯示過期排名，可能導致用戶投訴。
- **Idempotency**：結算操作必須冪等，重複請求不應產生雙重點數或重複排名記錄。

---

## 10. 常見錯誤

- 新人容易誤解為 API 完全由 `pricebackendservice` 直接寫入 DB，實際上它是 BFF，不直接操作 DB。
- AI 容易將此流程與一般的 `predict/payout` 混淆，冠軍賽結算為獨立活動（supreme），但可能底層使用相同的 `activities_*` 表格，需確認 `activityevent` 識別。
- 常見漏檢查：未驗證週期是否已結算；結算時未清除排行榜快取。
- 常見錯誤流程：直接 UPDATE `activities_winneraccounts` 的 `rank`；或手動塞入 `profitpoint` 值，繞過計算邏輯。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | README.md - 會員管理 `/api/v1/member/supreme/winners` |
| API 路由 | README.md - 會員管理 `/api/v1/member/supreme/cycles/{gameType}/{lid}/{cid}/settlement` |
| DB Table (predict) | predict schema & detail: `activities_cycles`, `activities_winneraccounts` |
| DB 寫入限制 | predict-detail.md: `activities_winneraccounts` 欄位不可手動寫入，由系統自動設定 |
| BFF 職責 | README.md 明述本服務不直接存取 DB，所有操作透過下游微服務 |
| 服務相依 | README.md 列出 `memberservice` 和 `predictservice` 為下游 |
| 點數發放規則 | member-detail.md: `gameusers_wallet.Balance` 僅能透過 `TransferMember` 更新 |
| 快取規範 | predict-detail.md: `predict:winners:{cid}` 用於排行榜加速，結算後需更新 |

---

**⚠️ 資訊缺口**：
- 未找到 pricebackendservice 的 `MemberController.cs` 或相關 Service 層代碼，無法確認實際呼叫的下游服務端點與參數映射。
- 結算的具體計算公式（如何將 betpool_bets / predictbets 轉換為 rank/profitpoint）未揭露。
- 不清楚點數發放的業務規則（數量、來源、觸發條件）。
- 建議新增文件：冠軍賽活動週期定義與結算規則說明（業務規格書）。