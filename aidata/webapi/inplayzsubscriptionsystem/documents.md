# inplayzsubscriptionsystem — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2025-07-04 15:42
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### [測試用] 走地賽事關盤快慢紀錄

> Confluence 頁面 ID：79462850
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79462850)
> 摘要檔：[processed/79462850-summary.md](../../confluence/processed/79462850-summary.md)
> Confluence 最後更新：2025-07-04
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件以表格列出足球、籃球、棒球三種球類，各數據源（站台）的走地賽事關盤快慢順序。越上方的數據源關盤越快，可用於 AI 開發時了解不同來源的關盤優先級，輔助訂閱系統設計關盤等待或切換策略。表中數據可供參考，但需注意標題標註「測試用」，可能非正式規則。

**關鍵業務規則**：
- 足球走地賽事關盤快慢順序（從快到慢）：bwin, leisu, sa88, 90vs, 188bet, nowscore, betcity
- 籃球走地賽事關盤快慢順序（從快到慢）：nowscore, leisu, espnbet, bwin, sofascore, stake, tonybet, aiscore
- 棒球走地賽事關盤快慢順序（從快到慢）：panda, stake, nowscore, espn, espnbet, betradar, bc, lsport, mlb, sa8888, cbs, twsl, playsport, covers, sofa, kkk

**注意事項**：
- ⚠️ 標題註明「[測試用]」，內容可能為測試數據或已過時，正式環境的順序需人工確認。
- ⚠️ 文件未說明「關盤快」的具體含義（是指數據源先行關閉盤口，還是數據處理延遲較低），需結合業務上下文理解。

---

## 操作手冊類

### 3rd

> Confluence 頁面 ID：55575762
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/3rd)
> 摘要檔：[processed/55575762-summary.md](../../confluence/processed/55575762-summary.md)
> Confluence 最後更新：2023-12-15
> 摘要最後同步：2026-05-26

**摘要**：
這份文件提供第三方（Partner）串接的入口索引，包含 Confluence 上的串接方法說明頁面、GitLab 專案 inplayz3rd 的連結，以及更新圖片的操作指引（需參考專案 README.md 並同步更新串接方法文件）。對 AI 開發者而言，可快速定位相關技術文檔與程式碼倉庫。

**AI 開發需要注意的部分**：
- 第三方串接的技術文件與程式碼皆位於 inplayz3rd 專案，開發相關功能時需參考該專案 README.md。
- 更新圖片後需同步更新串接方法文件，確保文件與實作一致。

---

## 技術設計類

（目前尚無相關文件）

---

## 歷史決策類

（目前尚無相關文件）