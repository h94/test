# tradegameservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 11:30
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類


### TradeGameController API 規劃 (Cursor生成)

> Confluence 頁面 ID：79470457
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79470457)
> 摘要檔：[processed/79470457-summary.md](../../confluence/processed/79470457-summary.md)
> Confluence 最後更新：2026-04-20
> 摘要最後同步：2026-05-27

**摘要**：
定義了 TradeGame 對外 REST API 的完整契約，包括端點、模型、業務規則與錯誤處理。它明確了開發順序（先凍結對外 I/O，再實作 DomainService），並強制參考 aidata 中的 .cursor_rules 與 tradegameservice.json。對 AI 開發的主要價值在於提供了可直接實現的下單驗證邏輯、餘額/持倉檢查，以及與 PredictService 一致的錯誤格式與語系富化策略。

**關鍵業務規則**：
- 下單時 `trade_price` 必須為整數且落在 1 到 99（含）之間，否則交易失敗。
- 下單價格必須等於盤口快照 `Odds` 中的最新價格，不一致則失敗。
- 買入 (`buy`) 總成本 (`trade_price × stock_num`) 不可超過 `GameUserWallet.Balance`。
- 賣出 (`sell`) 時，持有 `stock_num` 必須大於或等於下單的 `stock_num`。
- `trade_type` 只能為 `'buy'` 或 `'sell'`（不分大小寫），其他值一律失敗。
- 對外 API 不接受 `account` 參數，由服務端透過 `authKey` 查詢。
- 取得用戶交易倉時，需從每筆持倉的 `mode_spread_type` 拆分資訊，並對照賽事快照讀取 `NowPrice`，讀取失敗設為 0。
- 所有回應須在服務端依 `lang` 參數補齊賽事/聯盟/隊伍的對應語系。
- 下游 `tradegameservice` 非 200 回應，須將其 `message` 及 `status` 轉為 `ECException` 拋出。

**注意事項**：
- ⚠️ `authKey` 與 `account` 是否為一對一關係需確認。
- ⚠️ 權限控管規則未定義，由 `ECFramework` 中介層決定。
- ⚠️ API 快取策略（如 `[RequestCache]`）未定。
- ⚠️ 文件為規劃階段，部分內容可能調整。

---


## 技術設計類


### TCZB-4245 [TradeGameService] - 賽事交易所系統

> Confluence 頁面 ID：79468913
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79468913)
> 摘要檔：[processed/79468913-summary.md](../../confluence/processed/79468913-summary.md)
> Confluence 最後更新：2026-05-15
> 摘要最後同步：2026-05-27

**摘要**：
定義 TradeGameService 的核心設計，包括 API 規格、`stock_holdings_{game_type}` 表結構與結單流程。API 提供即時股價查詢、買賣、持股與交易紀錄查詢、重算等功能。結單流程透過永久迴圈掃描已結束比賽進行結算與 Z 幣交易。

**關鍵設計決策**：
- 採用 Cassandra，以 `gdate` 為 partition key 的時序分表設計（`stock_holdings_{game_type}`）來隔離不同球種。
- 使用 `spread` / `ratio` 兩個整數欄位處理非整數球頭。
- `trade_history` 以 JSON 字串儲存，犧牲查詢彈性換取儲存交易的靈活性。
- 採用永久迴圈輪詢 `games` 表觸發結單，非事件驅動。
- `recalculate` API 設計為先退回獲利再重新結算，確保比分修正後的正確性。

**影響範圍**：
- 核心交易與結算邏輯，不可輕易變更以下規則：手續費計算方式 (0.3%)、`trade_history` 的 JSON 結構、結單流程。

**注意事項**：
- ⚠️ `trade_history` 範例出現未定義的 `'resell'` 類型，需人工確認。
- ⚠️ 手續費計算後如何取整未明確說明。
- ⚠️ 重算時“原本的股價會退還”具體是指收回獲利或退回成本，描述不夠明確。

---

### 交易持有倉 DB table

> Confluence 頁面 ID：79471544
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471544)
> 摘要檔：[processed/79471544-summary.md](../../confluence/processed/79471544-summary.md)
> Confluence 最後更新：2026-05-15
> 摘要最後同步：2026-05-27

**摘要**：
詳細定義了核心數據表 `stock_holdings_{game_type}` 的 schema。明確了 partition key 與 clustering key 的設計，以及 `winloss`、`trade_history` 等關鍵欄位的所有可能值與業務含義。

**關鍵設計決策**：
- Partition key 為 `gdate`，clustering key 依序為 `lid`, `gid`, `account`, `mode_spread_type`。
- `winloss` 使用單一字元枚舉 (`W`, `L`, `C`, `N`) 節省空間。
- `trade_history` 為 serialized JSON string，記錄包含 `trade_type` 與 `trade_operator` 的完整交易序列。

**影響範圍**：
- 所有涉及交易記錄的讀寫操作都以此表結構為準。不可輕易變更 `mode_spread_type` 和 `trade_history` 的內部規則。

**注意事項**：
- ⚠️ 球頭 `spread`/`ratio` 計算範例 (1.5 -> spread:2, ratio:100) 可能為筆誤，需人工確認正確規則。
- ⚠️ `trade_history` 為字串，需反序列化，且其結構可能變動。

---

### TCZB-4328 [TradeGameService] - 會員持倉/股價 API

> Confluence 頁面 ID：79471098
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471098)
> 摘要檔：[processed/79471098-summary.md](../../confluence/processed/79471098-summary.md)
> Confluence 最後更新：2026-05-07
> 摘要最後同步：2026-05-27

**摘要**：
定義了兩個新的 API：批次取得多賽事即時股價 (POST /api/tradegames) 和查詢會員交易持倉 (GET /api/usertradedata/{account})。提供了請求參數、回傳結構與過濾規則。

**影響範圍**：
- 前端獲取交易數據的來源。API 的請求/回應格式不可輕易變更。

---


## 歷史決策類


### TCZB-1771 [StockBacktesting]-回測系統相關設計

> Confluence 頁面 ID：34766903
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=34766903)
> 摘要檔：[processed/34766903-summary.md](../../confluence/processed/34766903-summary.md)
> Confluence 最後更新：2022-05-04
> 摘要最後同步：2026-05-27

**決策背景**：
定義股票回測系統的資料儲存設計。

**決策結論**：
採用兩個 Cassandra 表 (`backtesting`, `backtesting_view`) 來分別儲存回測設定與結果，並明確了 JSON 格式的進出場策略結構與多種狀態枚舉定義。

**影響**：
- ⚠️ 文件較舊 (2022)，需人工確認現行回測系統是否沿用此設計。

---

### TCZB-1999 - [Stock] - StockFilterService 新增大盤API

> Confluence 頁面 ID：38011963
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=38011963)
> 摘要檔：[processed/38011963-summary.md](../../confluence/processed/38011963-summary.md)
> Confluence 最後更新：2022-07-29
> 摘要最後同步：2026-05-27

**決策背景**：
為賽事交易所功能新增台灣大盤歷史價格查詢。

**決策結論**：
定義了一個 GET API 端點，並明確了按日期排序、Market 參數為空時同時回傳上市/上櫃資料的規則。

**影響**：
- ⚠️ 文件較舊，使用內部 IP，規格可能已變更，需人工確認。

---

### TCZB-2489 [SportKing] - 收藏頁面

> Confluence 頁面 ID：47218905
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47218905)
> 摘要檔：[processed/47218905-summary.md](../../confluence/processed/47218905-summary.md)
> Confluence 最後更新：2023-02-15
> 摘要最後同步：2026-05-27

**決策背景**：
實現用戶收藏聯盟的功能。

**決策結論**：
採用 POST 方法傳入聯盟 ID 陣列進行批次查詢，回傳以 ID 為 key 的物件，並依 `gtype` 篩選。

**影響**：
- 收藏功能的前端展示與資料獲取方式。

---

### 賽事站台result page

> Confluence 頁面 ID：40501767
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40501767)
> 摘要檔：[processed/40501767-summary.md](../../confluence/processed/40501767-summary.md)
> Confluence 最後更新：2022-08-30
> 摘要最後同步：2026-05-27

**決策背景**：
決定賽事結果頁面的資料結構。

**決策結論**：
API 回應結構包含 `OtherInfo` 與 `ResultInfo`，將詳細結果與其他資訊分開放置以增加彈性。

**影響**：
- 前端結果頁的資料解析方式。