# newlottery DB — 完整使用脈絡

> 產出時間：2026-06-06 10:00:00
> 欄位結構定義：[newlottery.json](./newlottery.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| newlotterybackendservice | owner / writer / reader | 讀、寫、刪（所有欄位），須透過專用 API 進行餘額變動，遵守寫入限制與讀取規則 |
| newlotterysite | ⚠️ 衝突待人工：服務摘要中未定義，現有文件標示為 owner，角色待確認 | 讀、寫（特定欄位），僅可透過抽獎結算或管理 API 增減餘額 |
| memberservice | writer / reader（錢包相關） | 可讀寫 CoinWallet、ChampionshipWallet 相關表格，但必須透過定義好的交易 API，不可直接 UPDATE 餘額欄位 |

---

## Table：ChampionshipWallet

### ID 欄位

**型別**：bigint

**值定義與狀態流轉**：

此欄位為自動遞增主鍵，無業務語義。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT ID = AUTO | 首次建立錢包時 | 主鍵自動生成，不可手動指定 |
| newlotterysite | - | 無寫入權限 | 不可直接 INSERT 此表 |
| memberservice | INSERT ID = AUTO | 首次建立錢包時 | 主鍵自動生成，不可手動指定 |

**⚠️ 跨服務限制**：
- `ID` 僅為內部主鍵，不可對外暴露，更不可傳遞給前端

---

### Balance 欄位

**型別**：bigint

**值定義與狀態流轉**：

此欄位為數值型，代表特定用戶在特定錦標賽中的積分結餘，無狀態流轉。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | UPDATE Balance = Balance + ? / Balance - ? | 下注扣減、派彩獎勵、手動加值 | 必須在具備 `SELECT ... FOR UPDATE` 的事務中執行，並同時寫入 `ChampionShipWallet_Transactions`；不可直接 SET 任意值 |
| newlotterysite | UPDATE Balance = Balance + ? / Balance - ? | 抽獎結算、特定管理充值 API | 僅限後端定義的業務流程，不可直接透過一般後台寫入；扣減必須有對應交易記錄 |
| memberservice | UPDATE Balance = Balance + ? / Balance - ? | 透過交易 API 增減（如活動派獎、退款） | 必須在同一事務中搭配寫入 `ChampionShipWallet_Transactions`；不可直接 SET 任意值；須先檢查餘額 |

**⚠️ 跨服務限制**：

- `Balance` 不得被任何服務直接 `UPDATE` 為任意數值，只能透過原子增減操作
- 扣減操作必須先確認餘額充足，使用樂觀鎖或悲觀鎖確保一致性
- 任何餘額變動必須同步寫入 `ChampionShipWallet_Transactions`，且兩者需在同一個資料庫事務中
- memberservice 亦須遵守上述規則，不可繞過事務直接寫入餘額

---

### Account / CID 欄位

**型別**：Account varchar, CID char(4)

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT | 首次建立錦標賽錢包時 | 聯合唯一標識，寫入後不可變更 |
| newlotterybackendservice / newlotterysite | SELECT ... WHERE Account=? AND CID=? | 查詢餘額或交易記錄 | 所有查詢須同時提供兩個欄位，避免跨 CID 洩漏 |
| memberservice | SELECT ... WHERE Account=? AND CID=? | 查詢餘額或交易記錄 | 同樣必須同時帶入 Account 與 CID；不可僅用 Account 查詢並彙總跨 CID 餘額 |

**⚠️ 跨服務限制**：

- 查詢 ChampionshipWallet 或相關交易時，必須同時指定 `Account` 與 `CID`，不可全表掃描或僅用其中一個欄位

---

### LastUpdateTime 欄位

**型別**：timestamp（預設 CURRENT_TIMESTAMP，隨更新自動變動）

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| newlotterybackendservice | 自動更新 | 每次餘額變動時由資料庫自動更新為當前時間，不可手動寫入 |
| newlotterysite | 自動更新 | 同上，自動記錄變更時間 |
| memberservice | 自動更新 | 同上，不可手動設定 |

**⚠️ 注意**：
- 此欄位僅供內部審計，無業務邏輯用途，不可對外暴露精確時間戳（需轉換為語意化摘要，如“最近活躍時間”）
- 所有服務都不得手動指定或修改此值

---

## Table：ChampionShipWallet_Transactions

### ID 欄位

**型別**：bigint (Auto Increment)

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT ID = AUTO | 新增交易記錄時 | 主鍵自動增長，不可手動指定 |
| newlotterysite | INSERT ID = AUTO | 新增交易記錄時 | 同上 |
| memberservice | INSERT ID = AUTO | 新增交易記錄時 | 同上 |

**⚠️ 注意**：

- `ID` 為內部交易序號，不可回傳給前端，對外回應須使用業務訂單號
- 查詢交易記錄時應以 `(Account, CID)` 為基礎，並加上時間範圍（`AddTime`），避免全表掃描

---

### Account / CID 欄位

**型別**：Account varchar, CID char(4)

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT | 寫入交易記錄時 | 與對應的 ChampionshipWallet 關聯，必須為有效組合 |
| newlotterybackendservice / newlotterysite | SELECT ... WHERE Account=? AND CID=? | 查詢交易記錄 | 所有查詢須同時提供兩個欄位，不可僅用 Account 或 CID |
| memberservice | INSERT / SELECT | 寫入或查詢時 | 同上，必須提供完整複合鍵 |

**⚠️ 跨服務限制**：
- 查詢所有交易記錄時，必須同時指定 `Account` 與 `CID`，嚴禁跨帳戶或跨賽事掃描

---

### Point 欄位

**型別**：bigint

**值定義與狀態流轉**：

此欄位為數值型，代表積分變動量。正數（>0）為增加（獎勵），負數（<0）為扣減（消費），不可為 0。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT Point = ? | 下注扣減、派彩獎勵、手動加值 | 寫入後不可修改；金額錯誤應透過新增沖正記錄處理 |
| newlotterysite | INSERT Point = ? | 抽獎結算或管理充值 | 同上，寫入後不可修改 |
| memberservice | INSERT Point = ? | 透過交易 API 增減 | 寫入後不可修改；金額錯誤應以沖正記錄處理 |

**⚠️ 跨服務限制**：

- `Point` 寫入後不可直接 `UPDATE`；金流修正必須以相反的新交易記錄沖銷
- 交易記錄必須與對應的 ChampionshipWallet.Balance 變動在同一個事務內完成

---

### T_Type 欄位

**型別**：int

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT T_Type | 新增交易記錄時 | 服務端依業務情境決定，不可接收客戶端傳入的值 |
| newlotterysite | INSERT T_Type | 新增交易記錄時 | 同上 |
| memberservice | INSERT T_Type | 新增交易記錄時 | 由服務端依業務決定，不可接收客戶端傳入值 |

**⚠️ 注意**：

- `T_Type` 必須使用後端定義的枚舉值（如充值、消費、退款），不可寫入未定義代碼
- 對外 API 不可直接回傳原始數值，應轉換為語意化摘要

---

### T_Detail 欄位

**型別**：varchar(200)（可為 NULL）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice / newlotterysite | INSERT T_Detail | 新增交易記錄時 | 由後端定義固定格式（如 "bet:{orderId}"），不可儲存前端任意輸入字串 |
| memberservice | INSERT T_Detail | 新增交易記錄時 | 後端定義格式，不可儲存前端任意字串 |

**⚠️ 注意**：

- `T_Detail` 不得包含使用者提供的原始字串，必須由服務端消毒或生成
- 對外 GET 介面一律移除或置空，避免洩漏內部資訊

---

### AddTime 欄位

**型別**：timestamp（預設 CURRENT_TIMESTAMP）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT AddTime = CURRENT_TIMESTAMP | 新增交易記錄時 | 自動填入，不可手動指定 |
| newlotterybackendservice / newlotterysite | SELECT ... WHERE AddTime BETWEEN ? AND ? | 查詢交易記錄 | 必須強制帶入時間範圍，避免全表掃描 |
| memberservice | INSERT AddTime = CURRENT_TIMESTAMP | 新增交易記錄時 | 自動填入，不可手動指定 |
| memberservice | SELECT ... WHERE AddTime BETWEEN ? AND ? | 查詢交易記錄 | 必須搭配 Account、CID 與時間範圍，並實施分頁 |

**⚠️ 跨服務限制**：

- 任何查詢交易記錄的 API 必須限制時間範圍（`AddTime`），且每頁筆數須有上限

---

## Table：CoinWallet

### Account 欄位（主鍵）

**型別**：varchar(20)

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT Account | 首次建立錢包時 | 主鍵，寫入後不可變更 |
| newlotterybackendservice / newlotterysite | SELECT ... WHERE Account = ? | 查詢錢包或交易記錄 | 查詢必須指定 Account，批次查詢亦須限定帳號範圍 |
| memberservice | INSERT Account | 首次建立錢包時 | 主鍵，寫入後不可變更 |
| memberservice | SELECT ... WHERE Account = ? | 查詢錢包或交易記錄 | 查詢必須指定 Account |

**⚠️ 注意**：

- `Account` 一經建立不可修改

---

### Balance 欄位

**型別**：int

**值定義與狀態流轉**：

數值型欄位，代表用戶金幣結餘，無狀態流轉。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | UPDATE Balance = Balance + ? / Balance - ? | 加幣、扣幣操作 | 僅能透過專用 API 並在事務中搭配 `SELECT ... FOR UPDATE` 執行，同時寫入 `CoinWallet_Transactions` |
| newlotterysite | UPDATE Balance = Balance + ? / Balance - ? | 抽獎參與（消費）或獎勵結算 | 不可直接 UPDATE，必須有對應交易記錄，且需先檢查餘額 |
| memberservice | UPDATE Balance = Balance + ? / Balance - ? | 透過交易 API 增減 | 必須在事務中搭配 `SELECT ... FOR UPDATE`，同時寫入 `CoinWallet_Transactions`；不可直接 SET 任意值 |

**⚠️ 跨服務限制**：

- `Balance` 不得被任何服務直接設定為任意值，必須透過原子增減
- 任何餘額變動必須與 `CoinWallet_Transactions` 寫入在同一事務中
- 扣減前必須讀取當前餘額並確認充足，防止負數餘額

---

### LastUpdateTime 欄位

**型別**：timestamp（預設 CURRENT_TIMESTAMP，隨更新自動變動）

| 服務 | 操作 | 說明 |
|------|------|------|
| newlotterybackendservice | 自動更新 | 每次餘額變動時由資料庫自動更新為當前時間，不可手動寫入 |
| newlotterysite | 自動更新 | 同上 |
| memberservice | 自動更新 | 同上 |

**⚠️ 注意**：
- 此欄位僅供內部審計，無業務用途，不可對外暴露精確時間戳

---

## Table：CoinWallet_Transactions

### T_ID 欄位

**型別**：bigint (Auto Increment)

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT T_ID = AUTO | 新增交易記錄時 | 主鍵自動增長，不可手動指定 |
| newlotterysite | INSERT T_ID = AUTO | 新增交易記錄時 | 同上 |
| memberservice | INSERT T_ID = AUTO | 新增交易記錄時 | 同上 |

**⚠️ 注意**：

- `T_ID` 為內部主鍵，不可回傳給前端
- 查詢交易記錄時必須搭配 `Account` 與時間範圍（`AddTime` 或 `T_Date`），並實施分頁

---

### Account 欄位

**型別**：varchar(20)

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT Account | 寫入交易記錄時 | 必須對應已存在的 CoinWallet.Account |
| newlotterybackendservice / newlotterysite | SELECT ... WHERE Account = ? | 查詢交易記錄 | 所有查詢必須指定 Account |
| memberservice | INSERT / SELECT | 寫入或查詢時 | 必須指定 Account，不可跨帳戶彙總 |

**⚠️ 跨服務限制**：
- 所有 CoinWallet_Transactions 的讀取都必須帶上 `Account` 條件，防止資料外洩

---

### Coin 欄位

**型別**：int

**值定義與狀態流轉**：

數值型，代表金幣變動量。正數（>0）增加，負數（<0）扣減，不可為 0。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT Coin = ? | 加幣、扣幣成功後 | 寫入後不可修改；金額錯誤應以沖正記錄處理 |
| newlotterysite | INSERT Coin = ? | 抽獎參與或獎勵結算時 | 同上，寫入後不可修改 |
| memberservice | INSERT Coin = ? | 加幣、扣幣成功後 | 寫入後不可修改；金額錯誤應以沖正記錄處理 |

---

### T_Type 欄位

**型別**：int

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT T_Type | 新增交易記錄時 | 由服務端依業務決定，不可接收客戶端傳入值 |
| newlotterysite | INSERT T_Type | 新增交易記錄時 | 同上 |
| memberservice | INSERT T_Type | 新增交易記錄時 | 由服務端依業務決定，不可接收客戶端傳入值 |

**⚠️ 注意**：

- `T_Type` 須符合內部定義代碼，寫入後不可修改
- 對外 API 回應時不應直接暴露原始數值

---

### T_UID 欄位

**型別**：char(20)（可為 NULL）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT T_UID | 新增交易記錄，且與外部訂單關聯時 | 寫入前須檢查唯一性以保證冪等，不得重複插入相同 `T_UID`；無關聯時可為 NULL 或空字串 |
| newlotterysite | INSERT T_UID | 同上 | 同上 |
| memberservice | INSERT T_UID | 與外部訂單關聯時 | 寫入前必須檢查唯一性，確保冪等；無關聯時可為空 |

**⚠️ 注意**：

- `T_UID` 可能包含跨系統用戶識別用途，對外 API 不得直接暴露，必要時須脫敏（如隱去部分字符）

---

### T_Detail 欄位

**型別**：varchar(1000)（可為 NULL）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice / newlotterysite | INSERT T_Detail | 新增交易記錄時 | 後端定義格式，不可儲存前端任意字串 |
| memberservice | INSERT T_Detail | 新增交易記錄時 | 後端定義格式，不可儲存前端任意字串 |

**⚠️ 注意**：

- `T_Detail` 對外 GET API 一律移除或置空
- 內容不得包含未消毒的使用者輸入

---

### T_Date / AddTime 欄位

**型別**：date / timestamp（AddTime 預設 CURRENT_TIMESTAMP）

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| newlotterybackendservice | INSERT AddTime = CURRENT_TIMESTAMP, T_Date = CURDATE() | 新增交易記錄時 | 自動填入，不可手動指定 |
| newlotterybackendservice / newlotterysite | SELECT ... WHERE AddTime BETWEEN ? AND ? OR T_Date BETWEEN ? AND ? | 查詢交易記錄 | 必須強制帶入時間範圍，避免全表掃描 |
| memberservice | INSERT AddTime = CURRENT_TIMESTAMP, T_Date = CURDATE() | 新增交易記錄時 | 自動填入，不可手動指定 |
| memberservice | SELECT ... WHERE AddTime BETWEEN ? AND ? | 查詢交易記錄 | 必須搭配 Account 與時間範圍，並實施分頁 |

**⚠️ 跨服務限制**：

- 查詢 CoinWallet_Transactions 時，務必搭配 `Account` 與時間範圍，否則可能造成效能問題

---

## Redis — WalletCache

⚠️ 衝突待人工：`newlotterybackendservice` 摘要顯示「暫無明確使用證據」，但現有文件定義了以下快取結構。需由開發團隊確認實際是否使用。

### 金幣錢包快取

**Key pattern**：`coin_wallet:{Account}`

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET / GET | newlotterybackendservice | 查詢 CoinWallet 後快取 | TTL：300 秒 |
| DEL | newlotterybackendservice | 加減幣成功後 | 主動失效，確保一致性 |

### 冠軍賽錢包快取

**Key pattern**：`championship_wallet:{Account}:{CID}`

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET / GET | newlotterybackendservice | 查詢 ChampionshipWallet 後快取 | TTL：300 秒 |
| DEL | newlotterybackendservice | 交易發生時 | 主動失效 |

**⚠️ 注意**：

- 上述結構僅為推測，實際使用與否尚待確認
- 若有使用，交易發生後必須主動 `DEL`，不可只依賴 TTL 過期
- 讀取不到快取時必須 fallback 查 DB，不可直接報錯

---

## 常見錯誤（跨服務）

- ❌ **直接 `UPDATE ChampionshipWallet.Balance = ?` 或 `CoinWallet.Balance = ?`** → 餘額變動必須透過專用 API 並搭配 `SELECT ... FOR UPDATE`，同時寫入交易記錄
- ❌ **扣減餘額前未檢查是否足夠** → 必須在事務中讀取當前餘額並判斷，防止餘額變負
- ❌ **交易記錄寫入後又 `UPDATE Point` 或 `Coin`** → 金額錯誤應以沖正記錄處理，不可修改原記錄
- ❌ **`T_Type` 接收客戶端傳入的值** → 服務端必須根據業務情境硬性決定，不得信任前端
- ❌ **`T_Detail` 直接儲存使用者輸入字串** → 僅能由後端填入固定格式內容，避免注入或洩漏
- ❌ **對外 API 回傳 `T_Detail`、`T_UID`、`T_Type` 原始值** → 應予以移除或轉換為語意化摘要；`T_UID` 必要時須脫敏
- ❌ **對外 API 回傳內部主鍵（如 `ID`、`T_ID`）** → 應使用業務編號或直接隱藏
- ❌ **查詢交易記錄未限制時間範圍或 Account** → 可能導致全表掃描，必須強制帶入 `Account` 與 `AddTime`/`T_Date` 範圍
- ❌ **餘額變動後未同步寫入交易表** → 帳務無法稽核，應在一個事務內完成
- ❌ **`newlotterysite` 繞過 API 直接寫入 `Balance`** → 僅 `newlotterybackendservice` 擁有最終寫入權限，其他服務應透過定義好的 API 操作
- ❌ **`memberservice` 直接操作餘額欄位未透過交易記錄** → 必須使用事務包裹餘額更新和交易插入，確保帳務一致性
- ❌ **`CoinWallet_Transactions.T_UID` 重複插入** → 寫入前必須檢查唯一性，確保冪等