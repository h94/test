# tradegameresultservice — DB 操作邊界

> 產出時間：2025-04-14 16:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Pricecenter Cassandra | reader (accounts_*), writer (actionlog) | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- `accounts_*` 表系列（如 `accounts_AU8`、`accounts_Fortuna888`、`accounts_HGA` …）：**本服務不直接寫入**，帳號建立、啟用、關閉、密碼雜湊等一律由 `pricecenter` 管理服務或後台 API 負責。本服務僅讀取用於驗證。
- `actionlog` 表：
  - 本服務可執行 `INSERT`，但僅限記錄遊戲結果結算相關的操作（例如結算完成、結算失敗、重結算申請），不得記錄其他業務行為。
  - `INSERT` 時必須正確提供：分區鍵 `date`（操作當日，日期字串）、聚簇鍵 `addtime`（時間戳）、`user`（操作者帳號）、`gametype`（遊戲類型縮寫），以及 `action`、`actionclass`、`detail`（建議 `detail` 使用 JSON 結構）。
  - 禁止 `UPDATE` / `DELETE` 已存在的 `actionlog` 記錄，修正僅能透過後台稽核流程處理。

### 讀取規則

- `accounts_*` 表（依遊戲類型分表，如 `accounts_AU8`、`accounts_HGA` 等）：
  - 交易或結算前置驗證：必須讀取 `enabled`，僅 `enabled = 1` 可繼續；同時檢查 `closetime`，若為非空（帳號已關閉）則拒絕所有操作。
  - 查詢一律以主鍵 `account` 精確匹配，不可跨遊戲類型表進行全表掃描或無索引搜尋。
  - 內部需要第三方對接設定時可讀取 `handler`（`map<text, text>`），但此欄位不得透過任何對外 API 暴露。
- `actionlog` 表：
  - 任何查詢必須包含 `date` 條件（分區鍵），可輔以 `user`、`gametype`、`addtime` 範圍過濾，不允許全表掃描。
  - 主要用於內部稽核或結算回溯，不提供前端即時查詢。

### 不可回傳欄位

- `accounts_*` 表：
  - `password`：無論是否雜湊，皆不可透過 API 回傳，僅供內部驗證。
  - `phone`：用戶隱私，任何對外 GET 皆禁止輸出。
  - `closetime`：內部稽核專用，客戶端無需取得。
- `actionlog` 表：
  - `detail`：可能含結算金額、規則等敏感數據，對外 API 不得返回完整內容，如需展示必須脫敏。

---

## tradegame

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Tradegame Cassandra (stock_holdings_BK, BS, SC) | writer / reader | Schema：[db/tradegame.md](../../db/tradegame.md) · 語意：[db/tradegame-detail.md](../../db/tradegame-detail.md) |

### 寫入限制

- `winloss`：僅允許結算 API 在最終結果確認後寫入一次（值為 `W` / `L` / `N` / `C`），完成後不可再修改。異常重結算須由管理後台手動介入。
- `trade_history`：本服務不負責寫入，僅由交易服務維護。結算流程僅讀取該欄位作為計算依據。
- `stock_num`：結算時不可直接 UPDATE 改變庫存數量；庫存變動應由交易服務處理。
- `gdate`、`lid`、`gid`、`account`、`mode_spread_type`：這些構成 primary key 的欄位在寫入後不可更新，僅允許插入時設定。

### 讀取規則

- 結算批次掃描：查詢某日（`gdate`）所有尚未結算的持有記錄時，必須加上 `WHERE winloss = ''` 或 `winloss IS NULL`，避免重複處理已結算資料。
- 局結果查詢：依 `gid` 讀取當局所有玩家持倉時，需同時過濾 `gdate`（partition key），不可跨日期只使用 `gid` 查詢，否則可能導致全表掃描。
- 盈虧計算：讀取時需一次取回 `stock_num`、`trade_history`、`ratio`、`spread` 等欄位組合計算，避免多次讀取同一行。

### 不可回傳欄位

- `trade_history`：內含用戶每筆買賣詳細記錄，屬於敏感交易數據，任何對外 API 皆不可回傳。僅供內部結算運算使用。
- `account`：玩家帳號為個人資訊，若對外 API 需回傳用戶相關資料，應使用脫敏或 session token 替代。
- `addtime`：內部紀錄時間戳，無業務呈現價值，不應暴露給客戶端。

---

## games

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Games MySQL (`games_bk`, `games_bm`, `games_bs`, `games_ck`) | reader | Schema：[db/games.md](../../db/games.md) · 語意：[db/games-detail.md](../../db/games-detail.md) |
| Tradegame Cassandra (`stock_holdings_{game_type}`) | reader | Schema：[db/tradegame.md](../../db/tradegame.md) · 語意：[db/tradegame-detail.md](../../db/tradegame-detail.md) |
| Tradegame Cassandra (`resultlogs`) | reader / writer | Schema：[db/tradegame.md](../../db/tradegame.md) · 語意：[db/tradegame-detail.md](../../db/tradegame-detail.md) |

### 寫入限制

- `games_bk`, `games_bm`, `games_bs`, `games_ck`：本服務**不具備任何寫入權限**；比賽資料、比分、狀態等全由上游賽事資料服務（`gameservice`）或資料爬取模組負責寫入，本服務僅讀取已確認的比賽結果進行結算。
- `stock_holdings_{game_type}`：本服務**不負責寫入**；帳戶、比賽ID (gid)、聯賽ID (lid)、交易歷史 (trade_history)、持有數量 (stock_num) 等均由 `tradeservice` 負責。
- `resultlogs`：
  - 本服務可執行 `INSERT`，用於記錄比賽結果的結算狀態（例如批次結算開始或完成），防止重複處理。
  - `INSERT` 時必須正確提供：分區鍵 `gdate`（比賽日期）、`gtype`（遊戲類型代碼，如 BK, BM）、以及`gid`、`lid`、`status`、`addtime`。
  - 結算完成後，應將 `status` 更新為 `1` 以標記已處理，此為**唯一允許的更新操作**。
  - 禁止刪除 `resultlogs` 中的任何記錄。

### 讀取規則

- `games_bk`, `games_bm`, `games_bs`, `games_ck`：
  - 結算前置驗證：讀取比賽結果時，必須嚴格過濾 `status = 'Final'`，僅取用已完賽且比分已鎖定的比賽；未完成的比賽（如 `PreGame`、`Live`）一律跳過，避免使用中間比分進行結算。
  - 查詢必須包含分區鍵與日期條件：各遊戲表以 `gdate`（比賽日期）為主要篩選維度，避免跨日期全表掃描；可輔以 `lid`（聯賽 ID）、`id`（比賽 ID）進行精確定位。
  - 結果擷取：結算時僅需讀取 `match_h`、`match_a`、`match_detail` 作為結算依據；`resultinfo`、`otherinfo` 為選讀，不應作為主要判斷來源。
  - `source` 欄位可能用於區分資料供應商，但**不應**在結算邏輯中被用來判斷比分可信度，請依賴標準化後的 `match_h`/`match_a`。
- `stock_holdings_{game_type}`：
  - 結算批次掃描：查詢某日（`gdate`）所有尚未結算的持有記錄時，必須加上 `WHERE winloss = ''` 或 `winloss IS NULL`，避免重複處理已結算資料。
  - 局結果查詢：依 `gid` 讀取當局所有玩家持倉時，需同時過濾 `gdate`（partition key），不可跨日期只使用 `gid` 查詢。
- `resultlogs`：
  - 任何查詢必須包含 `gdate` 條件（分區鍵），可輔以 `gtype`、`status` 過濾，不允許全表掃描。
  - 用於判斷當天特定遊戲類型的比賽是否已完成結算，以避免重複執行批次作業。

### 不可回傳欄位

- `games_*` 表：
  - `siteidmaps`：內含各外部站點的內部對應 ID，可能洩漏第三方爬取策略，任何對外 API 皆不可輸出。
  - `teams` 詳細 JSON：雖非極敏感，但可能包含內部分數標準化細節，前端應僅展示 `team_h`/`team_a`，如需隊伍 ID 可提供 `teamid_h`/`teamid_a`。
  - `resultinfo`、`otherinfo`：可能包含未經清洗的原始結果或內部附註，對外一律遮蔽。
- `stock_holdings_*` 表：
  - `trade_history`：內含用戶每筆買賣詳細記錄，屬於敏感交易數據，任何對外 API 皆不可回傳。
  - `account`：玩家帳號為個人資訊，應使用脫敏或 session token 替代。
- `resultlogs` 表：
  - 所有欄位均為內部結算流程使用，**不對任何對外 API 暴露**。

---

## stock

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Stock MySQL | reader (多數表), writer (MessageLog, FavoriteRule.FirstMatch) | Schema：[db/stock.json](../../db/stock.json) · 語意：[db/stock-detail.md](../../db/stock-detail.md) |

### 寫入限制

- **FavoriteRule**：
  - 僅允許本服務在「首次匹配發送通知」成功後，**精確更新** `FirstMatch` 欄位為 `1`，代表該規則已觸發過，避免重複發送。
  - 更新時必須以 `User`、`Name`、`Strategy` 三個主鍵為條件，且不得變更其他任何欄位（如 `Value`、`NeedSend`、`Industry` 等）。
  - 禁止直接 `INSERT` 或 `DELETE` FavoriteRule，規則的新增/刪除由其他管理服務負責。
- **MessageLog**：
  - 本服務可執行 `INSERT`，記錄每次遊戲結果通知的發送情況。
  - 插入時必須完整提供：`Date`（發送當日的日期字串，分區鍵）、`Account`、`SendAction`、`TargetAddress`、`SendStatus`、`MsgContent`、`AddTime`（應用服務端當前時間）、`LastUpdateTime`（可設為相同值）。
  - 禁止對已有 MessageLog 記錄進行 `UPDATE` 或 `DELETE`，確保發送記錄不可竄改。
- 其餘表（`FavoriteBroker`, `FavoriteStock`, `Users`, `Options`, `Rules`, `SubLogs`）：**本服務不具備任何寫入權限**，所有資料維護由相應的業務服務或後台系統負責。

### 讀取規則

- **Users**：
  - 讀取使用者通知管道設定時，**必須檢查帳號有效且訂閱未到期**：`Enabled = 1` 且 `SubEndTime IS NULL OR SubEndTime > NOW()`（依 DB 時間函數），避免對停用或過期用戶發送。
  - 查詢一律以主鍵 `Account` 精確匹配，無特殊業務理由不得使用 `Phone` 或 `Email` 作為查詢條件。
- **FavoriteRule**：
  - 排程或即時匹配任務讀取需通知的規則時，**必須加入**：
    - `NeedSend = 1`（明確要求發送通知）
    - `FirstMatch = 0`（只取尚未首次匹配的規則，避免重複發送；若業務允許重複發送則另議）
  - 可依 `User`, `Country` 進一步過濾，但嚴禁全表掃描（若無合適索引應先確認 DBA 建立）。
- **Rules**：
  - 讀取全域規則定義時，必須過濾 `Enabled = 1`，僅取啟用中的規則。
  - 通常以 `ID` 或 `Type` 搭配條件查詢，避免不必要的全表讀取。
- **Options**：
  - 讀取系統選項時，需過濾 `Enabled = 1`，確保使用最新且有效的設定值。
- **MessageLog**：
  - 內部稽核或重送檢查時，任何查詢必須包含 `Date` 分區鍵條件，可輔以 `Account` 或 `SendStatus`，不允許跨分區全掃。
- **其他表** (`FavoriteBroker`, `FavoriteStock`, `SubLogs`)：
  - 僅允許使用主鍵或已知索引進行精確查詢；本服務無需對這些表進行複雜業務過濾。

### 不可回傳欄位

- **Users**：
  - `Password`：無論加密與否，**絕對不可透過任何 API 回傳**。
  - `Phone`、`Email`、`ChatID`：屬個人隱私，對外 API 不可返回完整內容；如需顯示，應脫敏處理（例如 `0987***123`）。
  - `SendAction`、`Rank`：內部業務邏輯使用，前端不應直接取得原始值。
- **FavoriteRule**：
  - `Value`、`FirstMatch`、`NeedSend`：內部匹配流程所用，不得直接暴露給客戶端。
- **FavoriteStock / FavoriteBroker**：
  - `Value`：雖然是使用者自訂，但可能包含大量細節，對外 API 可回傳，但不宜在非必要場景中整包送出。
- **MessageLog**：
  - `MsgContent`：可能含有交易結果、通知內文等敏感資訊，對外 API 應遮蔽或不提供歷史查詢端點。
  - `TargetAddress`：涉及用戶手機或郵箱，禁止對外直接暴露。

---

## Redis

無 Redis 使用。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 股票持倉寫入與庫存變動 | `tradeservice` | `stock_holdings_*` 表的插入、`stock_num` 及 `trade_history` 更新均由交易服務處理，本服務僅讀取。 |
| 遊戲比分來源及結果判定 | `gameservice` 或上游遊戲供應商 | 本服務從遊戲服務取得已確認的最終結果，不負責比分驗證。 |
| 玩家帳號管理與權限驗證 | `authservice` / `memberservice` | `account` 取自外部系統，本服務不負責帳號建立或停用。 |
| 外部遊戲平台帳號連動 | `pricecenter` 相關服務 | `tradegame` 庫不儲存平台帳密，結算時不處理第三方金流。 |
| `games_*` 系列表的任何寫入操作 | `gameservice` | 比賽建立、比分更新、狀態異動皆由賽事服務負責，本服務僅讀取。 |
| 用戶喜好設定與規則編輯（FavoriteBroker、FavoriteStock、FavoriteRule） | 前端或後台管理服務 | 本服務僅讀取，不提供新增、修改、刪除功能。 |
| 系統規則（Rules）與選項（Options）的啟用/停用維護 | 系統管理後台 | 本服務僅讀取已啟用的規則，不參與配置管理。 |
| 訂閱記錄（SubLogs）的產生與管理 | 金流/訂閱服務 | 本服務僅讀取以驗證訂閱狀態，不寫入訂閱歷程。 |

---

## 常見錯誤

- ❌ 結算掃描時未過濾 `winloss`，導致已結算資料被重新處理而重複扣除庫存 → ✅ 每次結算批次必須先讀取 `winloss = ''` 的記錄，處理後立即寫入 `winloss` 避免二次處理。
- ❌ 跨日期查詢時忽略 `gdate` 條件，僅以 `gid` 搜尋引發全表掃描或逾時 → ✅ 查詢前必須帶入 `gdate` 作為 partition key 限制，必要時使用 `IN` 搭配多日期。
- ❌ 結算完成後允許透過一般 API 直接 `UPDATE winloss` 改變結果 → ✅ `winloss` 應僅由結算內部流程寫入，且寫入後鎖定，變更需走管理後台人工覆核。
- ❌ 將 `trade_history` 回傳給前端，暴露用戶交易明細 → ✅ 前端如需查詢歷史交易應透過 `tradeservice` 提供的專用 API，本服務不予暴露。
- ❌ 讀取 `accounts_*` 時未檢查 `enabled` 或 `closetime`，導致已停用/關閉的帳號繼續進行交易 → ✅ 每次驗證帳號必須同時確認 `enabled = 1` 且 `closetime` 為空。
- ❌ 寫入 `actionlog` 時未提供 `date` 分區鍵或寫入錯誤格式，導致寫入失敗或落入錯誤分區 → ✅ 必須以操作當日正確填入 `date`，並確保其他聚簇鍵一致。
- ❌ 將 `password` 或 `actionlog.detail` 透過 API 暴露給客戶端 → ✅ 嚴格過濾所有對外輸出，僅在內部使用。
- ❌ 結算時讀取 `games_*` 表未過濾 `status = 'Final'`，誤用未完成比賽的即時比分 → ✅ 在讀取 `match_h`/`match_a` 前，務必確認 `status` 為 `'Final'`，避免使用 `Live` 或 `PreGame` 狀態的比賽。
- ❌ 直接信任 `resultinfo` 或 `match_detail` JSON 中的數值而未與 `match_h`/`match_a` 欄位比對，導致取錯結算用比分 → ✅ 以 `match_h`、`match_a` 為最終比分來源；`match_detail` 僅供特殊規則（如局分）使用，且須標準化解析。
- ❌ 批次結算前未檢查 `resultlogs`，導致同一日期的同一遊戲類型被重複結算 → ✅ 每次執行結算批次前，必須查詢 `resultlogs` 確認該 `gdate` 與 `gtype` 組合的 `status` 尚未為 `1`。
- ❌ 發送股票通知時未檢查 `Users` 的 `Enabled` 或 `SubEndTime`，導致停用/過期帳號仍收到訊息 → ✅ 發送前務必確認 `Enabled = 1` 且 `SubEndTime` 未過期。
- ❌ 讀取 `FavoriteRule` 時未過濾 `NeedSend` 或 `FirstMatch`，造成不該通知的規則被觸發 → ✅ 匹配邏輯必須加入 `NeedSend = 1` 且（依業務）`FirstMatch = 0` 條件。
- ❌ 更新 `FirstMatch` 時使用無主鍵條件的 `UPDATE`，錯誤將其他用戶或規則一併設為已匹配 → ✅ 嚴格以 `User`、`Name`、`Strategy` 三個主鍵作為 WHERE 條件，且僅修改 `FirstMatch` 一個欄位。
- ❌ 寫入 `MessageLog` 時省略 `Date` 分區鍵或使用錯誤格式（例如 timestamp 而非日期字串） → ✅ 統一使用通知發送當日 `YYYY-MM-DD` 字串填入 `Date`。
- ❌ 對外 API 回傳 `Users` 的 `Phone`、`Email` 或 `ChatID` 完整值 → ✅ 隱私欄位應脫敏或完全不回傳，僅在內部使用。