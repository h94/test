# tradegameresultservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 08:06
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---


## 業務規範類


### TCZB-4263 [TradeGameResultService] - 交易結算

> Confluence 頁面 ID：79469182
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469182)
> 摘要檔：[processed/79469182-summary.md](../../confluence/processed/79469182-summary.md)
> Confluence 最後更新：2026-04-08
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義 TradeGameResultService 的核心結算流程：從 games 表找出已結束比賽 (status=1)，再到 stock_holdings 表找出對應未結算交易 (winloss 為空)，根據球頭（讓分）或大小分規則判斷輸贏 (W/L/N/C)，並調用 Z 幣 API 派彩。設計上要求確認 API 請求成功後才更新 winloss，避免資料不一致。

**關鍵業務規則**：
- 結算判斷以客隊為基準：HA 玩法中，若球頭為正（被讓），主隊球頭為負，客隊獲勝即贏；若球頭為負（讓），主隊球頭為正，客隊需贏超過讓分才算贏。OU 玩法中，比較比賽總分是否超過盤口大小，超過則大分贏。
- winloss 可能值：W（贏）、L（輸）、N（平手）、C（取消），分別對應贏、輸、平手、比賽取消。
- 只有 stock_holdings 表中 winloss 欄位為空的記錄才會被結算處理。
- 已結算的交易超過 30 天後會被清除，由另一個循環 thread 定期執行。

**注意事項**：
- ⚠️ HA 規則的描述需要對應 stock_holdings 中的具體欄位，實作前需確認欄位名稱及正負號意義。
- ⚠️ 「以客隊為主」的概念需與現有交易系統的買入方向對齊，避免應用在對稱玩法（如主隊讓分）時誤判。
- ⚠️ 文件中 Z 幣 API 範例參數（如 AuthKey）可能為測試用，正式環境應使用安全方式管理憑證。

---

## 技術設計類


### TCZB-4263 [TradeGameResultService] - 交易結算

> Confluence 頁面 ID：79469182
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469182)
> 摘要檔：[processed/79469182-summary.md](../../confluence/processed/79469182-summary.md)
> Confluence 最後更新：2026-04-08
> 摘要最後同步：2026-05-27

**摘要**：
此文件描述 TradeGameResultService 的技術架構：使用兩個獨立循環 thread 分別處理未結算交易結算和清除超過 30 天的已結算交易。結算邏輯從 games 和 stock_holdings 表查詢資料，根據球頭或大小分規則判斷輸贏，調用 Z 幣 API 進行派彩。

**關鍵設計決策**：
- 使用兩個獨立循環 thread：一個負責結算未結算交易，另一個負責清除 30 天前的交易資料。
- 為避免 Z 幣 API 超時導致資料不一致，採用兩種策略之一：① 確認 API 請求成功後才更新 winloss；② 將需派彩的請求暫存於 cache，排隊依序發送，成功後再更新。

**影響範圍**：
- 涉及 stock_holdings 表的 winloss 欄位更新邏輯，不可輕易變更。
- 涉及 Z 幣 API 的呼叫與錯誤處理機制，變更時需確保資料一致性。

---

### Result information

> Confluence 頁面 ID：40501389
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Result+information)
> 摘要檔：[processed/40501389-summary.md](../../confluence/processed/40501389-summary.md)
> Confluence 最後更新：2022-09-01
> 摘要最後同步：2026-05-27

**摘要**：
此文件定義足球比賽結果資訊的數據格式，包含多個時間區段及事件（角球、罰牌、先/最後得分）的 JSON 結構。用於 API 回傳或前端顯示時的數據 schema 標準化。

**關鍵設計決策**：
- 時間區段比分使用陣列字串格式 "[主隊分, 客隊分]"，統一一種表示法；特殊事件如 FirstScore 以 "1"/"2"/"No" 字串表示。
- 每個 result 類別都是一個獨立的 JSON 鍵值對，便於前端按需解析。

**影響範圍**：
- 影響 result 相關接口的數據格式，不可輕易變更。
- ⚠️ 最後更新日期為 2022-09，可能已過時，需人工確認此數據格式是否仍為現行標準。

---

## 操作手冊類


### TCZB-4263 [TradeGameResultService] - 交易結算

> Confluence 頁面 ID：79469182
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469182)
> 摘要檔：[processed/79469182-summary.md](../../confluence/processed/79469182-summary.md)
> Confluence 最後更新：2026-04-08
> 摘要最後同步：2026-05-27

**摘要**：
TradeGameResultService 的自動化結算與清理流程，無需手動操作，由兩個循環 thread 定期執行。

**AI 開發需要注意的部分**：
- 結算 thread 需從 games 表查詢 status=1 的比賽，再從 stock_holdings 表查詢 winloss 為空的交易進行結算。
- 清理 thread 需定期清除 stock_holdings 中已結算超過 30 天的交易資料。
- Z 幣 API 呼叫需確保成功後才更新 winloss 欄位，否則可能導致資料不一致。

---

### Result information

> Confluence 頁面 ID：40501389
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Result+information)
> 摘要檔：[processed/40501389-summary.md](../../confluence/processed/40501389-summary.md)
> Confluence 最後更新：2022-09-01
> 摘要最後同步：2026-05-27

**摘要**：
足球比賽結果資訊的數據結構規範，定義每個 result 類別的 JSON 格式，用於 API 回傳。

**AI 開發需要注意的部分**：
- 時間區段比分格式固定為 "[主隊分, 客隊分]"，不可變更。
- FirstScore 等特殊事件僅接受 "1"/"2"/"No" 三種字串值。
- ⚠️ 此文件最後更新於 2022-09，實作前需確認格式是否仍為現行標準。