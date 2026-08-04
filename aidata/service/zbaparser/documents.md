# zbaparser — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-26 15:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### 整合資訊源-ZBA架構

> Confluence 頁面 ID：40502510
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40502510)
> 摘要檔：[processed/40502510-summary.md](../../confluence/processed/40502510-summary.md)
> Confluence 最後更新：2022-09-23 16:51
> 摘要最後同步：2026-05-26 12:35
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
ZBA 服務整合各爬蟲 sitegame 資訊與 EndUser 設定，產出統一且具備援的賽事資訊源，供下游服務使用。其核心在於合併所有可用站台資料以達到訊號完整性，並依據設定調整輸出。

**關鍵業務規則**：
- ZBA 會收集所有可用 sitegame 的資訊，合併為更完整的賽事資訊，避免單一資訊源斷訊或漏資料。
- ZBA 的訊號完整性取決於賽事合併的完整度（所有站台資料都收到才能達到最佳合併）。
- 整合時需依據 EndUser 的聯盟賽事設定值（Setting）來調整最終輸出的資訊內容。
- OddParser 會根據 setting 配置整合各 sitegame 的 odds，產出 ZBA game 的各玩法 odds。
- OddProtector 負責檢查各 sitegame 的 odds 是否正常，並對 Spread 變化進行監控。

**注意事項**：
- ⚠️ 文件最後更新於 2022-09-23，距今已逾一年，部分元件或流程可能已有變更，需人工確認是否仍符合現況。

---

## 技術設計類

### 整合資訊源-ZBA架構

> Confluence 頁面 ID：40502510
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40502510)
> 摘要檔：[processed/40502510-summary.md](../../confluence/processed/40502510-summary.md)
> Confluence 最後更新：2022-09-23 16:51
> 摘要最後同步：2026-05-26 12:35

**摘要**：
ZBA 服務從 DB 載入快取、訂閱 Kafka processedgamedata 取得 sitegame 資料，經元件化處理後輸出合併的 gamedata 至 Kafka，架構上透過快取、訊息解耦與多職責元件實現高效可靠的整合。

**關鍵設計決策**：
- 使用快取（ZBAMemCache）儲存 Game、SiteGame Mapping 及 Setting，避免每次處理都查詢 DB，提升效能。
- 從 Kafka 訂閱 processedgamedata 獲取即時 sitegame 數據，解耦爬蟲與整合邏輯，提高擴展性。
- 合併後的最終資料以 gamedata 主題輸出至 Kafka，供下游服務統一消費。
- 架構拆分為多個獨立元件（GameProvider、OddParser、Parser 等），每個元件負責單一職責，便於維護與除錯。
- 支援主客對換處理（ZBSwapTransfer），以應對不同站台主客隊標記不一致的情況。
- 分開處理 pregame/inplay 與 final 訊號：pregame/inplay 由 Worker 與 Parser 負責整合，final 則由 GameProvider 取賽事資訊時一併處理輸出。

---

## 歷史決策類

無相關文件。

---

## 操作手冊類

無相關文件。