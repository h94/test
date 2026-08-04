# masterservice — DB 操作邊界

> 產出時間：2025-03-24 12:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| predict (Cassandra) | owner | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **activities_cycles**：僅活動管理後台可寫入 `site`、`activityevent`、`cid`、`startdate`、`starttime`、`enddate`、`endtime`；`resultcount` 由結算流程自動更新，不可人工修改。
- **activities_record**：參與者註冊或系統自動記錄時可寫入 `site`、`account`、`eventname`、`restday`；`winbets` 由活動結算批次寫入，`updatedate` 由系統自動更新；不可直接 INSERT 或 UPDATE 非當前活動的記錄。
- **activities_winneraccounts**：僅排名計算批次可寫入 `profitpoint`、`rank`、`winpercentage`、`predictcount`；`account` 與 `site`、`activityevent`、`cid` 由結算流程自動關聯，禁止手動指定。
- **betpool_games**：遊戲建立 API 可寫入 `id`、`starttime`、`endtime`、`betoptions`、`names`、`zcoinprice`、`feedrate`、`basicprofitzcoin`、`bonusprofitzcoin`、`hot`、`viponly`；`status`、`payout`、`winresult`、`updatetime` 由遊戲結算流程自動維護；除了結算流程外，禁止直接 UPDATE 這些欄位。
- **betpool_bets**：玩家下注 API 可寫入 `id`、`gid`、`account`、`betoption`、`betzcoin`、`addtime`（時間戳）；`profitzcoin`、`winlose` 由結算批次填寫，禁止人工設定。
- **calculatelog**：僅結算批次可寫入 `weekid`、`weekdate`、`done`、`addtime`；`done` 標記計算完成與否，一旦設為 `1` 則不可再降回 `0`；必須在同一個 `weekid` 下進行原子性檢查，避免重複計算。
- **killeraccounts_BK**：僅殺手帳戶統計計算批次可寫入 `addtime` 與 `avgodd`；`addtime` 由系統自動生成，不可人工指定；此表為備份性質，資料一旦寫入則不可修改。
- **常見欄位群組**：`site`、`account`、`gid` 等外鍵不可在非所屬服務的上下文中修改（例如不可經由管理介面修改玩家下注的 `account`）。所有時間戳欄位（`addtime`、`updatetime`、`startdate/time` 等）由系統自動生成，不可人工寫入。

### 讀取規則

- **activities_cycles**：查詢未過期活動週期時需過濾 `enddate >= today` 且 `endtime >= now`（前端展示）；結算時使用 `cid` 與 `activityevent` 精確定位。
- **activities_record**：玩家查詢個人記錄時必須加入 `site = ? AND account = ?`，避免跨站或跨帳號洩漏；管理端查詢可依 `eventname` 分批撈取。
- **activities_winneraccounts**：排行榜查詢僅回傳前 N 名（依 `rank` 排序），且需過濾 `site = ? AND activityevent = ?`；不允許直接依 `account` 查詢所有站點資料。
- **betpool_games**：玩家列表僅顯示 `status IN (1,2)` 的進行中或可投注遊戲；已結束遊戲 (`status=3`) 需透過歷史記錄 API 限縮查詢時間範圍；查詢熱門遊戲可使用 `hot = true` 過濾。
- **betpool_bets**：玩家查詢自己的投注歷史須強制過濾 `account = ?`；管理後台查詢單一遊戲的投注須依 `gid` 範圍掃描，避免全表掃描。
- **calculatelog**：查詢上週計算狀態時需依 `weekid = ?` 過濾，並判斷 `done = 1`；若 `done = 0` 則表示尚未結算，結算流程會檢查後執行。
- **killeraccounts_BK**：查詢殺手帳戶平均賠率歷史時應依 `addtime` 降序取最新一筆，避免全表掃描；可依業務需求限制時間範圍（例如僅取最近一週的記錄）。
- **VIP限制**：當 `betpool_games.viponly = true` 時，非 VIP 玩家不可查詢或下注該遊戲；需結合會員身份驗證。

### 不可回傳欄位

- **activities_record.account**：除了玩家本人查詢自己資料或管理後台必要場景外，對外 API 不應回傳其他玩家的帳號。
- **betpool_bets.account**：所有公開查詢（如遊戲投注明細）不得暴露下注玩家的帳號；僅玩家本人或管理後台可取得。
- **betpool_games.names**：多語言名稱是內部映射表，對外 API 應依 `Accept-Language` 回傳單一語言版本，而非原始 JSON。
- **betpool_games.betoptions**：同 `names`，對外應轉換為選項名稱列表，避免暴露原始映射結構。
- **任何 `site` 資訊**：在允許的情境下可回傳，但需注意跨站隔離，避免前端藉此推測其他站點數據。

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| member (Cassandra) | owner | Schema：[db/member.md](../../db/member.md) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **password**：僅註冊或修改密碼 API 可寫入，且必須經過雜湊處理；不可明文儲存。
- **email**：註冊時必須唯一，且須檢查 `forbidden_email_domains` 表，禁止使用已被列入黑名單的域名；禁止直接 UPDATE 為已被其他用戶使用的 email。
- **status**：僅管理後台或系統封禁流程可修改；不可由使用者自行變更。
- **black_account、focus_account、follow_account**：僅用戶本人可透過特定 API 維護自己的列表；管理後台不可直接修改這類隱私列表。
- **addtime、lastactiontime、lastchecktime、signindate 等時間戳**：由系統自動寫入，不可人工 UPDATE。
- **site、siteid**：一旦寫入不可變更（除非管理後台特殊操作），避免跨站資料錯亂。

### 讀取規則

- **登入驗證**：查詢 `gameusers` 時，必須使用 `authkey` 或 `account` 並在服務層比對 `password`（雜湊後比對），且強制過濾 `status = 1`（正常）；`status = 0`（未激活）或 `status = -1`（封禁）不可通過驗證。本服務僅提供資料查詢，最終驗證邏輯由 authservice 完成。
- **用戶資料查詢（依 authkey）**：必須確認請求者的 token 所對應的 authkey 與查詢的 authkey 一致，避免越權存取。
- **郵箱查詢**：若使用 `email` 欄位查詢，應利用已建立的索引 `myindex` 並限制同一站點範圍，避免全表掃描。
- **黑名單/關注列表查詢**：僅用戶本人可查詢自己的 `black_account`、`focus_account`、`follow_account`；管理後台查詢須有明確授權記錄。
- **封禁記錄查詢**：`gameusers_banned` 表僅管理後台可查詢完整記錄（含 `description`、`endtime`）；一般用戶不可查看他人封禁原因。

### 不可回傳欄位

- **password**：任何對外 API（含管理後台）均不可回傳，僅內部比對使用。
- **authkey**：對外 API 不應回傳用戶的內部主鍵；應使用 `account` 或 `username` 作為識別。
- **email**：非必要場景（如用戶個人資訊編輯頁）不應回傳；列表或公開查詢必須遮蔽。
- **black_account、focus_account、follow_account、memberships**：這些列表屬用戶隱私，僅用戶本人可取用；對外 API（如其他用戶查詢個人資料時）不得回傳。
- **headshotpath**：若路徑含有內部目錄結構，對外應轉換為可供前端直接存取的 URL，避免暴露內部路徑。

---

## Redis

（本服務 code 中未使用 Redis，暫無 Key 定義。）

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 使用者帳號隱私加密 | authservice | 帳號 `account` 在 predict 中以明文儲存，但外洩風險由 authservice 的 Token 驗證機制管控；predict 僅負責業務查詢。 |
| 投注金流扣款與退款 | walletservice | `betpool_bets.betzcoin` 僅為記錄，實際扣款需呼叫 walletservice；退款或派彩金額透過 walletservice 處理，predict 不操作餘額。 |
| 活動獎品兌換 | rewardservice | 玩家在 predict 活動中獲得的點數 (`profitpoint`) 僅作為排名依據，實際兌換獎品由 rewardservice 處理。 |
| 會員密碼驗證 | authservice | member 僅儲存雜湊後的密碼，實際驗證流程由 authservice 負責；member 不參與 session/token 管理。 |

---

## 常見錯誤

- ❌ 在查詢 `betpool_bets` 時未加入 `site` 條件，導致跨站資料混淆 → 所有查詢均須包含 `site` 條件，避免 Cassandra 跨分割區全表掃描及資料錯亂。
- ❌ 直接將 `betpool_games.names` 整個 map 回傳給前端 → 應依用戶語言環境轉換為單一文字後回傳，避免洩漏多語言結構。
- ❌ 管理後台更新 `betpool_games.status` 而不檢查 `payout` 狀態，導致已派彩遊戲被覆寫為未派彩 → 更新狀態前必須讀取 `payout` 並經由結算流程控制，禁止直接 UPDATE。
- ❌ 對 `activities_winneraccounts` 使用全表排序查詢取得排行榜資料 → 應限縮 `site`、`activityevent`、`cid`，且只取前 N 筆（依 `rank` 索引）。
- ❌ 查詢 `gameusers` 時未過濾 `status`，導致已封禁用戶仍可取得 token → 所有登入驗證查詢必須加入 `status = 1` 條件。
- ❌ 將 `password` 欄位包含在更新 API 的回傳結果中 → `password` 必須永遠從 SELECT 結果中移除或遮蔽，僅寫入時使用。
- ❌ 未檢查 `calculatelog.done` 就直接執行週期結算，造成重複計算並產生髒資料 → 必須先查詢 `SELECT done FROM calculatelog WHERE weekid=?`；僅在 `done = 0` 時執行計算，並於完成後原子性更新 `done = 1`。
- ❌ 結算流程更新 `betpool_games.winresult` 或 `payout` 時未使用輕量級交易（LWT） → 重要狀態欄位的變更應透過 `IF payout = false` 等條件確保冪等性，避免並發衝突。
- ❌ `betpool_games.basicprofitzcoin` 等獎池欄位被手動修改 → 這些數值應由系統根據投注金額與規則自動計算，直接 UPDATE 將破壞獎池公平性。
- ❌ 查詢 `killeraccounts_BK` 時未設定時間範圍，導致全表掃描 → 應以 `addtime` 降序取最新一筆或加入 `addtime >= ?` 限縮查詢區間。
- ❌ 手動寫入或修改 `killeraccounts_BK` 的 `avgodd` → 該值僅由統計批次計算，人工干預將導致後續分析失準。