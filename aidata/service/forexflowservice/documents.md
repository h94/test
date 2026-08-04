# forexflowservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 07:04
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB-1257 [ForexFlowService]-Forex data寫入DB

> Confluence 頁面 ID：24088432  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24088432)  
> 摘要檔：[processed/24088432-summary.md](../../confluence/processed/24088432-summary.md)  
> Confluence 最後更新：2021-11-15 14:43  
> 摘要最後同步：2026-05-27 07:04  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：  
定義了 ForexFlowService 將法幣匯率資料寫入資料庫的業務需求。核心規則為每正 5 秒（如 00:00:00、00:00:05）批次寫入一次，且每個 5 秒窗格內接收到的重複資料需先 distinct。對 AI 開發此服務的幫助是明確了寫入頻率與去重邏輯，可作為排程與資料清理模組的設計基礎。

**關鍵業務規則**：  
- 每正 5 秒（系統時鐘的 0, 5, 10, ... 秒）觸發一次寫入資料庫的作業。  
- 在每個 5 秒週期內，接收到的 Currency 資料若存在相同內容（重複記錄），必須先進行 distinct 處理，再將唯一資料寫入資料庫。

**注意事項**：  
- ⚠️ 文件位於「舊的Projects 1-200」與 Sprint 37 路徑下，最後更新於 2021 年；需人工確認此規則在現行系統中是否仍適用。  
- 引用的外部頁面（Currency Kafka Data Define、Currency Cassandra Table、時序圖、流程圖）未提供具體內容，完整實作需參考這些頁面。

---

## 技術設計類

暫無相關文件。

---

## 歷史決策類

暫無相關文件。

---

## 操作手冊類

暫無相關文件。