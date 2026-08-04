# flowcontrolservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 12:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB-312 [FlowControlService] - 接收Kafka訊號Call Pricecenter Update Redis API

> Confluence 頁面 ID：9797885
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=9797885)
> 摘要檔：[processed/9797885-summary.md](../../confluence/processed/9797885-summary.md)
> Confluence 最後更新：2020-10-26 09:30
> 摘要最後同步：2026-05-27 05:45
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義了 FlowControlService 從 Kafka 訂閱訊息的處理邏輯。FlowControlService 需根據訊息中的資料類型（一般分數 vs. 賠率），分別呼叫 PriceCenterService 的兩支不同 API，以更新 Redis。對 AI 開發來說，這提供了 FlowControlService 中 Kafka 消費後的分派邏輯，確保分數和賠率資料流各自獨立處理，避免資料寫入錯誤。

**關鍵業務規則**：
- Kafka 訊息中的「一般分數」與「賠率」資料必須分別處理，呼叫 PriceCenterService 的對應 API，不可混用同一 API 寫入 Redis。

**注意事項**：
- ⚠️ 文件最後更新於 2020-10-26，距今較久，可能 FlowControlService 實作或 PriceCenter API 已變更，需與現有程式碼對照確認。

---

### TCZB-509 [FlowControlService] - Update PinnaclePages Table

> Confluence 頁面 ID：11436920
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-509+%5BFlowControlService%5D+-+Update+PinnaclePages+Table)
> 摘要檔：[processed/11436920-summary.md](../../confluence/processed/11436920-summary.md)
> Confluence 最後更新：2020-12-22 08:55
> 摘要最後同步：2026-05-27 11:11
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了 FlowControlService 需要新增的四個功能：根據賽事資料寫入 PinnaclePages 資料表；提供取得 PinnaclePages 資料的 API；提供關閉 PinnaclePages 遊戲的 API；以及提供心跳檢查 API 以定期檢查服務狀態。這些需求對開發 FlowControlService 的 Pinnacle 相關功能有直接指引作用。

**關鍵業務規則**：
- FlowControlService 須根據賽事資料寫入 PinnaclePages Table。
- 須提供一個 API 供外部取得 PinnaclePages 資料。
- 須提供關閉 PinnaclePages Game 的 API（Close RBG PinnaclePages Game）。
- 須提供心跳檢查 API，定期檢查服務心跳狀態。

**注意事項**：
- ⚠️ 文件中未提供具體的資料結構、API 規範或實作細節，需人工補充。
- ⚠️ PinnaclePages 表的定義、賽事資料來源未說明。
- ⚠️ 「Close RBG PinnaclePages Game」中的 RBG 意義不明，需確認。

---

### TCZB-1993 [Stock]-美.韓.陸A完成抓取和檢查資料後要更新flowcontrol表示做完成

> Confluence 頁面 ID：38011930
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=38011930)
> 摘要檔：[processed/38011930-summary.md](../../confluence/processed/38011930-summary.md)
> Confluence 最後更新：2022-07-29 16:12
> 摘要最後同步：2026-05-27 11:50
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了美、韓、陸A股票爬蟲完成任務後，需要透過 API 更新 flowcontrol 記錄的完成狀態。在 flowcontrol 表中新增六個欄位（astock_complete, astock_time, korstock_complete, korstock_time, usastock_complete, usastock_time），並提供 POST /api/write API 來寫入這些欄位。此機制讓其他系統可以確認爬蟲解析工作已全部完成。

**關鍵業務規則**：
- 美、韓、陸A股票爬蟲任務需完成兩次爬取和解析後，才可更新 flowcontrol 中對應市場的 complete 欄位為 1 並記錄時間。
- 每次更新只針對指定的市場（如 astock, korstock, usastock），不同市場可獨立完成。

**注意事項**：
- ⚠️ API 使用的 IP 位址 (192.168.9.231:22319) 可能已變更，需確認。
- ⚠️ 「兩次爬取和解析」的具體定義（如是否必須連續成功、間隔等）文件未說明，需人工確認。
- ⚠️ flowcontrol 表的新增欄位若已存在於正式環境，此設計可能已過時，需與目前 DB schema 比對。

---

## 技術設計類

### TCZB-1993 [Stock]-美.韓.陸A完成抓取和檢查資料後要更新flowcontrol表示做完成

> Confluence 頁面 ID：38011930
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=38011930)
> 摘要檔：[processed/38011930-summary.md](../../confluence/processed/38011930-summary.md)
> Confluence 最後更新：2022-07-29 16:12
> 摘要最後同步：2026-05-27 11:50
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了美、韓、陸A股票爬蟲完成任務後，需要透過 API 更新 flowcontrol 記錄的完成狀態。在 flowcontrol 表中新增六個欄位，並提供 POST /api/write API 來寫入這些欄位。

**關鍵設計決策**：
- 選擇在 flowcontrol 表中新增欄位來標記爬蟲完成狀態，而非建立獨立表。
- 使用統一 POST /api/write 介面，透過傳入 flowcontrol 陣列更新特定欄位，簡化 API 設計。

**影響範圍**：
- 影響 flowcontrol 表結構與相關 API 實作。
- 影響股票爬蟲任務完成後的回報流程。

---

## 歷史決策類

（目前無相關文件）

---

## 操作手冊類

（目前無相關文件）

---

> **版本紀錄**
> - v1.0 2026-05-27：初始版本，匯入三份 Confluence 文件摘要