# tradegame DB — 完整使用脈絡

> 產出時間：2025-04-12 14:30
> 欄位結構定義：[tradegame.json](./tradegame.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| tradegameservice | owner | 讀、寫、刪（交易下單、庫存管理、帳戶驗證快取） |
| tradegameresultservice | writer | 僅更新 `resultlogs.status` 與 `stock_holdings_*.winloss` 欄位（結算流程） |

---

## Table：resultlogs

*此表記錄各比賽（gid）在各局次（lid）的結算狀態，以 `gdate` 為分區鍵。本表資料由上游比賽結果服務寫入，結算流程更新狀態。*

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
     tradegameservice           tradegameresultservice
      INSERT（預設）              UPDATE
     value=0 ──────────────→ value=1（結算中）
                                    │
                                    └─────→ value=2（已結算，不可再變更）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 0 | 待結算 | tradegameservice | INSERT 時預設值（上游比賽結果寫入後建立） |
| 1 | 結算中 | tradegameresultservice | 結算批次掃描到該記錄，開始處理持倉結算時 |
| 2 | 已結算 | tradegameresultservice | 該局次所有持倉結算完成後，最終寫入 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| tradegameservice | INSERT status=0 | 上游比賽結果回傳時建立記錄 | 預設待結算 |
| tradegameresultservice | UPDATE status=1 | 結算批次選取待處理記錄時 | 標記為處理中，避免重複選取 |
| tradegameresultservice | UPDATE status=2 | 所有持倉結算完成後 | 最終狀態，不可再變更 |
| tradegameresultservice | SELECT WHERE status=0 | 結算批次掃描 | 選出待處理的記錄 |
| tradegameservice | SELECT WHERE status IN (0,1,2) | 查詢比賽結算進度 | 供前台或後台顯示狀態 |

**⚠️ 跨服務限制**：
- `status=2` 一旦設定後，**任何服務皆不可再修改**此記錄的 status 欄位。
- tradegameservice **不得**直接 UPDATE `status` 為 1 或 2，僅 tradegameresultservice 可執行結算狀態變更。
- `gdate`、`gtype`、`gid`、`lid` 由上游比賽結果服務寫入（透過 tradegameservice INSERT），一經建立即不可修改。

---

### 其他欄位總覽

| 欄位 | 型別 | 說明與角色 |
|------|------|-----------|
| `gdate` | text | 分區鍵（PK），代表比賽日期。寫入後不可修改。 |
| `gtype` | text | 比賽類型（如 BS、BK、SC 等），對應持倉表後綴。寫入後不可修改。 |
| `gid` | text | 比賽 ID。寫入後不可修改。 |
| `lid` | text | 局次 ID。寫入後不可修改。 |
| `addtime` | bigint | 記錄建立時間 (UTC Unix timestamp)。tradegameservice 在 INSERT 時自動寫入。 |

**⚠️ 讀取規則**：
- 所有查詢必須包含分區鍵 `gdate`，可附加 `gtype`、`gid` 縮小範圍。嚴禁全表掃描（禁用 `ALLOW FILTERING`）。

---

## Table：stock_holdings_BK

*此表記錄 BK（指定模式）的玩家持倉明細，以 `gdate` 為分區鍵，複合主鍵為 `(gdate, lid, gid, account, mode_spread_type)`。*

### winloss 欄位

**型別**：text

**值定義與狀態流轉**：

```
     tradegameservice           tradegameresultservice
      INSERT（NULL）              UPDATE（結算結果）
        ──────────────────────→ value={W / L / N / C}
                                       │
                                       └──→ 不可再修改
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 空（NULL） | 尚未結算 | tradegameservice | INSERT 時預設值 |
| W | 贏 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| L | 輸 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| N | 平局（不贏不輸） | tradegameresultservice | 結算流程在賽果判定平局後寫入 |
| C | 取消 | tradegameresultservice | 結算流程在比賽取消時寫入 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| tradegameservice | INSERT winloss=NULL | 玩家交易時建立持倉 | 預設未結算 |
| tradegameresultservice | UPDATE winloss=W/L/N/C | 結算批次處理後 | 結算完成才可設定，設定後不可再修改 |
| tradegameservice | SELECT | 查詢庫存明細 | 依業務需要過濾結算狀態 |
| tradegameresultservice | SELECT WHERE winloss IS NULL | 結算批次掃描 | 只處理未結算的持倉，避免重複處理 |

**⚠️ 跨服務限制**：
- `winloss` 在寫入非空值（W/L/N/C）後，**任何服務都不可再修改**。包含 tradegameservice 或管理後台。
- tradegameservice **不得**直接 UPDATE `winloss`，此欄位僅可由 tradegameresultservice 的結算流程寫入。

---

### mode_spread_type 欄位

**型別**：text

**值定義與狀態流轉**：

```
     tradegameservice（INSERT 時一次寫入）
     value={mode}_{spread}_{oddtype}
        （例如：1X2_1X2_H）
        │
        └──→ 寫入後不可修改
```

| 值格式 | 意義 | 由誰設定 | 時機 |
|--------|------|---------|------|
| `{mode}_{spread}_{oddtype}` | 複合主鍵，由下注模式、讓分盤、賠率類型組合 | tradegameservice | INSERT 時一次寫入，後續不可變更 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| tradegameservice | INSERT `{mode}_{spread}_{oddtype}` | 交易建倉時 | 依玩家選擇的模式、讓分、賠率類型組合寫入 |
| tradegameresultservice | SELECT | 結算時讀取持倉 | 供計算盈虧使用 |

**⚠️ 跨服務限制**：
- `mode_spread_type` 一旦寫入即固定，**所有服務皆不可修改**。若需變更，只能先刪除後重建。

---

### trade_history 欄位

**型別**：text（JSON Array 格式，儲存每筆買賣記錄）

**值定義與狀態流轉**：

```
     tradegameservice（交易流程）
     value=初始為空，每下一筆單即累加記錄
        │
        └──→ 僅供結算運算使用，對非本人不可回傳完整內容
```

| 值（範例） | 意義 | 由誰設定 | 時機 |
|-----------|------|---------|------|
| 空或 `[]` | 無交易歷史（新建倉） | tradegameservice | INSERT 時預設 |
| `[{...}]` | 玩家每一筆買賣詳細記錄 | tradegameservice | 每次交易（買/賣）時 APPEND |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| tradegameservice | INSERT `trade_history=[]` | 建立持倉時 | 預設無交易歷史 |
| tradegameservice | UPDATE（APPEND） | 每次進行買賣交易時 | 將新交易記錄附加至陣列 |
| tradegameresultservice | SELECT `trade_history` | 結算時讀取 | 作為計算盈虧的依據，不負責寫入 |

**⚠️ 跨服務限制**：
- tradegameresultservice **不負責寫入** `trade_history`，僅供讀取。
- `trade_history` 對本人（帳號相同）可完整回傳；對非本人（含管理後台查詢）應遮蔽或統計化，不可暴露使用者級別的交易明細。

---

### stock_num 欄位

**型別**：int

**值定義與狀態流轉**：

```
     tradegameservice（交易流程）
     INSERT stock_num={初始數量}
        │
        └──→ UPDATE（買/賣時增減庫存，最小為 0）
   
     tradegameresultservice（僅讀取，不修改）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 正整數 | 當前持有數量 | tradegameservice | INSERT 時設定初始值，後續依買賣增減 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| tradegameservice | INSERT `stock_num=N` | 建立持倉時 | 設定初始持有數量 |
| tradegameservice | UPDATE `stock_num` | 每次買賣交易時 | 依交易量增減庫存（僅可由交易下單流程更新） |
| tradegameresultservice | SELECT `stock_num` | 結算時讀取 | 作為計算盈虧的依據，不可修改此欄位 |

**⚠️ 跨服務限制**：
- tradegameresultservice **不得直接 UPDATE** `stock_num`。庫存變動僅由 tradegameservice 的交易流程（buy/sell）處理。
- 不可直接以 UPDATE 語句變更 `stock_num`，必須透過交易下單流程。

---

### 其他欄位總覽

| 欄位 | 型別 | 說明與角色 |
|------|------|-----------|
| `gdate` | text | 分區鍵（PK），代表交易日或週期。寫入後不可修改。 |
| `lid` | text | 局次 ID（CK）。寫入後不可修改。 |
| `gid` | text | 比賽 ID（CK）。寫入後不可修改。 |
| `account` | text | 玩家帳號（CK）。寫入後不可修改。對外 API 回傳時需脫敏。 |
| `addtime` | bigint | 建立時間 (UTC Unix timestamp)。tradegameservice 在 INSERT 時自動寫入，不可手動異動。 |
| `mode` | text | 下注模式。寫入後不可修改。 |
| `oddtype` | text | 賠率類型。寫入後不可修改。 |
| `ratio` | int | 賠率係數（如無係數則為 0）。由 tradegameservice 設定。 |
| `spread` | int | 讓分數（如無讓分則為 0）。由 tradegameservice 設定。 |

**⚠️ 讀取規則**：
- 一般使用者僅能查詢自身持倉：`WHERE account = ? AND gdate = ?`（必須含分區鍵 `gdate`）。
- 管理後台可查詢特定比賽所有持倉：`WHERE gdate = ? AND lid = ? AND gid = ?`，仍須提供分區鍵。

---

## Table：stock_holdings_BS

*此表記錄 BS（指定模式）的玩家持倉明細，欄位結構、操作規則與 `stock_holdings_BK` 完全相同，用途對應不同彩種或模式。*

### winloss 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK.winloss` 完全一致，請參照。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 空（NULL） | 尚未結算 | tradegameservice | INSERT 時預設值 |
| W | 贏 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| L | 輸 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| N | 平局 | tradegameresultservice | 賽果判定平局後寫入 |
| C | 取消 | tradegameresultservice | 比賽取消時寫入 |

**各服務操作明細**：與 `stock_holdings_BK.winloss` 相同，請參照。

**⚠️ 跨服務限制**：與 `stock_holdings_BK` 相同。
- `winloss` 寫入非空值後不可再修改，tradegameservice 不得直接 UPDATE。

---

### mode_spread_type 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- 寫入後不可修改。

---

### trade_history 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- tradegameresultservice 不負責寫入，僅供讀取。
- 對非本人不可回傳完整內容。

---

### stock_num 欄位

**型別**：int

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- tradegameresultservice 不得 UPDATE，僅讀取。
- 僅可由交易下單流程（trade.py）更新。

---

### 其他欄位總覽

| 欄位 | 型別 | 說明與角色 |
|------|------|-----------|
| `gdate` | text | 分區鍵，寫入後不可修改。 |
| `lid` | text | 局次 ID，寫入後不可修改。 |
| `gid` | text | 比賽 ID，寫入後不可修改。 |
| `account` | text | 玩家帳號，寫入後不可修改。 |
| `addtime` | bigint | 建立時間 (UTC)。不可手動異動。 |
| `mode` | text | 下注模式，寫入後不可修改。 |
| `oddtype` | text | 賠率類型，寫入後不可修改。 |
| `ratio` | int | 賠率係數。 |
| `spread` | int | 讓分數。 |

---

## Table：stock_holdings_ES

*此表記錄 ES（指定模式）的玩家持倉明細，欄位結構、操作規則與 `stock_holdings_BK` 完全相同，用途對應不同彩種或模式。*

### winloss 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK.winloss` 完全一致，請參照。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 空（NULL） | 尚未結算 | tradegameservice | INSERT 時預設值 |
| W | 贏 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| L | 輸 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| N | 平局 | tradegameresultservice | 賽果判定平局後寫入 |
| C | 取消 | tradegameresultservice | 比賽取消時寫入 |

**各服務操作明細**：與 `stock_holdings_BK.winloss` 相同，請參照。

**⚠️ 跨服務限制**：與 `stock_holdings_BK` 相同。
- `winloss` 寫入非空值後不可再修改，tradegameservice 不得直接 UPDATE。

---

### mode_spread_type 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- 寫入後不可修改。

---

### trade_history 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- tradegameresultservice 不負責寫入，僅供讀取。
- 對非本人不可回傳完整內容。

---

### stock_num 欄位

**型別**：int

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- tradegameresultservice 不得 UPDATE，僅讀取。
- 僅可由交易下單流程（trade.py）更新。

---

### 其他欄位總覽

| 欄位 | 型別 | 說明與角色 |
|------|------|-----------|
| `gdate` | text | 分區鍵，寫入後不可修改。 |
| `lid` | text | 局次 ID，寫入後不可修改。 |
| `gid` | text | 比賽 ID，寫入後不可修改。 |
| `account` | text | 玩家帳號，寫入後不可修改。 |
| `addtime` | bigint | 建立時間 (UTC)。不可手動異動。 |
| `mode` | text | 下注模式，寫入後不可修改。 |
| `oddtype` | text | 賠率類型，寫入後不可修改。 |
| `ratio` | int | 賠率係數。 |
| `spread` | int | 讓分數。 |

---

## Table：stock_holdings_FL

*此表記錄 FL（指定模式）的玩家持倉明細，欄位結構、操作規則與 `stock_holdings_BK` 完全相同，用途對應不同彩種或模式。*

### winloss 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK.winloss` 完全一致，請參照。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 空（NULL） | 尚未結算 | tradegameservice | INSERT 時預設值 |
| W | 贏 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| L | 輸 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| N | 平局 | tradegameresultservice | 賽果判定平局後寫入 |
| C | 取消 | tradegameresultservice | 比賽取消時寫入 |

**各服務操作明細**：與 `stock_holdings_BK.winloss` 相同，請參照。

**⚠️ 跨服務限制**：與 `stock_holdings_BK` 相同。
- `winloss` 寫入非空值後不可再修改，tradegameservice 不得直接 UPDATE。

---

### mode_spread_type 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- 寫入後不可修改。

---

### trade_history 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- tradegameresultservice 不負責寫入，僅供讀取。
- 對非本人不可回傳完整內容。

---

### stock_num 欄位

**型別**：int

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- tradegameresultservice 不得 UPDATE，僅讀取。
- 僅可由交易下單流程（trade.py）更新。

---

### 其他欄位總覽

| 欄位 | 型別 | 說明與角色 |
|------|------|-----------|
| `gdate` | text | 分區鍵，寫入後不可修改。 |
| `lid` | text | 局次 ID，寫入後不可修改。 |
| `gid` | text | 比賽 ID，寫入後不可修改。 |
| `account` | text | 玩家帳號，寫入後不可修改。 |
| `addtime` | bigint | 建立時間 (UTC)。不可手動異動。 |
| `mode` | text | 下注模式，寫入後不可修改。 |
| `oddtype` | text | 賠率類型，寫入後不可修改。 |
| `ratio` | int | 賠率係數。 |
| `spread` | int | 讓分數。 |

---

## Table：stock_holdings_HL

*此表記錄 HL（指定模式）的玩家持倉明細，欄位結構、操作規則與 `stock_holdings_BK` 完全相同，用途對應不同彩種或模式。*

### winloss 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK.winloss` 完全一致，請參照。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 空（NULL） | 尚未結算 | tradegameservice | INSERT 時預設值 |
| W | 贏 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| L | 輸 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| N | 平局 | tradegameresultservice | 賽果判定平局後寫入 |
| C | 取消 | tradegameresultservice | 比賽取消時寫入 |

**各服務操作明細**：與 `stock_holdings_BK.winloss` 相同，請參照。

**⚠️ 跨服務限制**：與 `stock_holdings_BK` 相同。
- `winloss` 寫入非空值後不可再修改，tradegameservice 不得直接 UPDATE。

---

### mode_spread_type 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- 寫入後不可修改。

---

### trade_history 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- tradegameresultservice 不負責寫入，僅供讀取。
- 對非本人不可回傳完整內容。

---

### stock_num 欄位

**型別**：int

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- tradegameresultservice 不得 UPDATE，僅讀取。
- 僅可由交易下單流程（trade.py）更新。

---

### 其他欄位總覽

| 欄位 | 型別 | 說明與角色 |
|------|------|-----------|
| `gdate` | text | 分區鍵，寫入後不可修改。 |
| `lid` | text | 局次 ID，寫入後不可修改。 |
| `gid` | text | 比賽 ID，寫入後不可修改。 |
| `account` | text | 玩家帳號，寫入後不可修改。 |
| `addtime` | bigint | 建立時間 (UTC)。不可手動異動。 |
| `mode` | text | 下注模式，寫入後不可修改。 |
| `oddtype` | text | 賠率類型，寫入後不可修改。 |
| `ratio` | int | 賠率係數。 |
| `spread` | int | 讓分數。 |

---

## Table：stock_holdings_SC

*此表記錄 SC（指定模式）的玩家持倉明細，欄位結構、操作規則與 `stock_holdings_BK` 完全相同，用途對應不同彩種或模式。*

### winloss 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK.winloss` 完全一致，請參照。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 空（NULL） | 尚未結算 | tradegameservice | INSERT 時預設值 |
| W | 贏 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| L | 輸 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| N | 平局 | tradegameresultservice | 賽果判定平局後寫入 |
| C | 取消 | tradegameresultservice | 比賽取消時寫入 |

**各服務操作明細**：與 `stock_holdings_BK.winloss` 相同，請參照。

**⚠️ 跨服務限制**：與 `stock_holdings_BK` 相同。
- `winloss` 寫入非空值後不可再修改，tradegameservice 不得直接 UPDATE。

---

### mode_spread_type 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- 寫入後不可修改。

---

### trade_history 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- tradegameresultservice 不負責寫入，僅供讀取。
- 對非本人不可回傳完整內容。

---

### stock_num 欄位

**型別**：int

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- tradegameresultservice 不得 UPDATE，僅讀取。
- 僅可由交易下單流程（trade.py）更新。

---

### 其他欄位總覽

| 欄位 | 型別 | 說明與角色 |
|------|------|-----------|
| `gdate` | text | 分區鍵，寫入後不可修改。 |
| `lid` | text | 局次 ID，寫入後不可修改。 |
| `gid` | text | 比賽 ID，寫入後不可修改。 |
| `account` | text | 玩家帳號，寫入後不可修改。 |
| `addtime` | bigint | 建立時間 (UTC)。不可手動異動。 |
| `mode` | text | 下注模式，寫入後不可修改。 |
| `oddtype` | text | 賠率類型，寫入後不可修改。 |
| `ratio` | int | 賠率係數。 |
| `spread` | int | 讓分數。 |

---

## Table：stock_holdings_TN

*此表記錄 TN（指定模式）的玩家持倉明細，欄位結構、操作規則與 `stock_holdings_BK` 完全相同，用途對應不同彩種或模式。*

### winloss 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK.winloss` 完全一致，請參照。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 空（NULL） | 尚未結算 | tradegameservice | INSERT 時預設值 |
| W | 贏 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| L | 輸 | tradegameresultservice | 結算流程在最終結果確認後寫入一次 |
| N | 平局 | tradegameresultservice | 賽果判定平局後寫入 |
| C | 取消 | tradegameresultservice | 比賽取消時寫入 |

**各服務操作明細**：與 `stock_holdings_BK.winloss` 相同，請參照。

**⚠️ 跨服務限制**：與 `stock_holdings_BK` 相同。
- `winloss` 寫入非空值後不可再修改，tradegameservice 不得直接 UPDATE。

---

### mode_spread_type 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- 寫入後不可修改。

---

### trade_history 欄位

**型別**：text

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- tradegameresultservice 不負責寫入，僅供讀取。
- 對非本人不可回傳完整內容。

---

### stock_num 欄位

**型別**：int

**值定義與狀態流轉**：與 `stock_holdings_BK` 相同，請參照。

- tradegameresultservice 不得 UPDATE，僅讀取。
- 僅可由交易下單流程（trade.py）更新。

---

### 其他欄位總覽

| 欄位 | 型別 | 說明與角色 |
|------|------|-----------|
| `gdate` | text | 分區鍵，寫入後不可修改。 |
| `lid` | text | 局次 ID，寫入後不可修改。 |
| `gid` | text | 比賽 ID，寫入後不可修改。 |
| `account` | text | 玩家帳號，寫入後不可修改。 |
| `addtime` | bigint | 建立時間 (UTC)。不可手動異動。 |
| `mode` | text | 下注模式，寫入後不可修改。 |
| `oddtype` | text | 賠率類型，寫入後不可修改。 |
| `ratio` | int | 賠率係數。 |
| `spread` | int | 讓分數。 |

---

## Redis — TradeGameCache

*此處列出 tradegameservice 使用的 Redis 快取，非 Keyspace 層級，但攸關服務行為一致性。*

### key：`price:acc:verify:{account}`

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET | tradegameservice | 交易前第一次查詢 account 驗證結果 | TTL：3600 秒；避免頻繁查詢 Cassandra |
| GET | tradegameservice | 每次交易前檢查 account 是否有效 | 確認 account 存在且 `enabled = 1` |
| DEL | tradegameservice | 帳戶狀態變更（如 `enabled = 0` 或 `closetime` 非空） | 主動失效，立即清除快取，防止讀取舊狀態 |

**⚠️ 注意**：
- 此快取資料來自 `pricecenter` 的 `accounts_*` 表，但由 tradegameservice 管理其生命週期。
- 當 account 狀態變更時，必須**主動 DEL**，不可只靠 TTL 自然過期，否則可能發生舊快取導致交易放行或拒絕錯誤。

---

## 常見錯誤（跨服務）

- ❌ tradegameservice 直接 UPDATE `winloss` 欄位（如寫入 'W' 或 'L'） → 只有 tradegameresultservice 的結算流程可以設定該欄位，異常寫入會導致結算邏輯錯亂。
- ❌ tradegameservice 直接 UPDATE `resultlogs.status` 為 1 或 2 → 只有 tradegameresultservice 可執行結算狀態變更。
- ❌ 查詢 `stock_holdings_*` 時未提供分區鍵 `gdate`（如只帶 `gid` 或 `account` 查詢） → 可能導致全表掃描，應至少提供 `gdate` 作為查詢條件。
- ❌ `trade_history` 在非本人查詢時回傳原始值 → 管理後台查詢時應遮蔽或統計化，不可暴露使用者級別的買賣明細。
- ❌ Redis 快取 (`price:acc:verify`) 在 account 狀態變更後未主動 DEL → 前台可能讀取到舊狀態（如已停用帳號仍被允許交易）。
- ❌ 寫入後試圖修改 `mode_spread_type`、`gdate`、`lid`、`gid`、`account` 等主鍵欄位 → 此類欄位一旦 INSERT 即固定，必須透過刪除後重建來變更。
- ❌ `winloss` 寫入非空值後再次嘗試 UPDATE → 此操作不被允許，任何服務都不可修改已結算的記錄。
- ❌ 對 `stock_holdings_*` 或 `resultlogs` 執行直接 DELETE → 常規業務不允許直接刪除，僅透過修改狀態達到邏輯刪除。
- ❌ `resultlogs` 查詢時未包含 `gdate` 分區鍵 → 嚴禁全表掃描，不可使用 `ALLOW FILTERING`。