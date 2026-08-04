# crawleroddtrend — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 06:20
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### Python自動生成歷史紀錄

> Confluence 頁面 ID：18645800
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=18645800)
> 摘要檔：[processed/18645800-summary.md](../../confluence/processed/18645800-summary.md)
> Confluence 最後更新：2021-05-12 13:01
> 摘要最後同步：2026-05-27 06:20
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件描述 Python 服務如何透過多個 API 取得比賽、賠率、賽事資料，並根據不同球種（SC、BS、BK）與階段（pregame/inplay）自動生成歷史走勢圖。內容包含 API 規格、資料篩選規則、圖表參數設定以及 Docker 部署分隔策略。對 AI 開發而言，這份文件提供了賠率或比分視覺化歷史記錄功能的完整數據處理流程。

**關鍵業務規則**：
- Odd_his（賠率歷史）資料僅保留 HA、OU、RBHA、RBOU 四種類型，若有多筆則全部保留（用於後續公式換算）。
- 賽事資料（Match）優先使用 bet365.com 的資訊，若無則改用 ku888；pregame 階段不需包含賽事資料。
- 生成圖表時，必須先根據比賽（game）取得所有關聯的 sitegame，再合併為一張圖，僅包含有合併進來的賽事。
- 圖表縱軸參數規則：BK 取 Odd 的 Spread 且 Main=true；BS 同 BK，但需進一步公式換算（本次 Sprint 先簡單實作）；SC 取 Odd 的 OddValue 且 Main=true，同樣需後續換算。
- 比分差與比分合目前先直接加減計算，正式換算將於後續 Sprint 補上。
- pregame 和 inplay 產生的圖檔必須分開存放。
- 所有產生的圖表必須加上浮水印。
- GameType 可為 SC、BS、BK，對應 Docker 部署拆分為 3（球種） x 2（階段），各自設定獨立的執行間隔。

**注意事項**：
- ⚠️ 文件建立於 2021 年 5 月，其中 API 路徑皆為 v1，可能已升級或廢棄。
- ⚠️ 多次提到「下一次 Sprint 再詳細做」，包含 BS/SC 的公式換算、比分差/比分合的正式計算，這些規則可能已在後續 Sprint 中變更。
- ⚠️ 比分差、比分合「先直接相加相減」為暫時作法，最終實現應以人工確認後的公式為準。
- ⚠️ 合併規則中「有合併進來的才算」的判定條件不明確，需進一步定義何謂合併成功。
- ⚠️ 站點清單僅列出 6 個，可能後續有增減，需確認目前支援的 site 是否仍與此處一致。

---

## 技術設計類

### Python自動生成歷史紀錄

> Confluence 頁面 ID：18645800
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=18645800)
> 摘要檔：[processed/18645800-summary.md](../../confluence/processed/18645800-summary.md)
> Confluence 最後更新：2021-05-12 13:01
> 摘要最後同步：2026-05-27 06:20

**摘要**：
同上述「業務規範類」文件，本文件同時涵蓋技術設計層面，包含 API 規格、資料篩選邏輯、圖表參數設定、Docker 部署分隔策略等技術實作細節。

**關鍵設計決策**：
- 將不同球種和階段拆分為獨立 Docker 執行個體，以便各自定義不同的資料更新頻率（如滾球期需更高頻率）。
- 只選擇 HA/OU/RBHA/RBOU 這四類賠率進行記錄與繪圖，因其為後端公式換算所必需的基礎數據，其他類型暫不考慮。
- 賽事資料優先取用 bet365，推測因其數據覆蓋率或即時性較佳，在無 bet365 時才降級使用 ku888。
- 圖表生成初期先以簡單加減處理比分差/比分合，待後續 Sprint 再實作正確的換算公式，以快速交付基本功能。

**影響範圍**：
- 影響賠率歷史走勢圖的數據來源、篩選邏輯與圖表生成流程。
- Docker 部署架構需根據 GameType 和階段拆分為多個執行個體。
- API 路徑皆為 v1 版本，若已升級可能影響資料取得。

---

## 歷史決策類

### Python自動生成歷史紀錄

> Confluence 頁面 ID：18645800
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=18645800)
> 摘要檔：[processed/18645800-summary.md](../../confluence/processed/18645800-summary.md)
> Confluence 最後更新：2021-05-12 13:01
> 摘要最後同步：2026-05-27 06:20

**決策背景**：
2021 年 Sprint23 期間，需要為前端賠率、比分呈現功能建立後端數據支援，自動生成歷史走勢圖。當時需要決定數據來源、篩選規則、圖表參數與部署策略。

**決策結論**：
- 選擇僅使用 HA/OU/RBHA/RBOU 四種賠率類型作為基礎數據。
- 賽事資料優先使用 bet365.com 來源。
- Docker 部署拆分為 3 球種 x 2 階段共 6 個獨立執行個體。
- 部分公式換算延後至後續 Sprint 實作，初期先以簡單計算方式交付。

**影響**：
- 這些決策影響現有 crawleroddtrend 服務的數據處理邏輯與部署架構。
- API 版本與公式計算邏輯可能已變更，需人工確認目前實作是否仍符合此文件描述。

---

## 操作手冊類

### Python自動生成歷史紀錄

> Confluence 頁面 ID：18645800
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=18645800)
> 摘要檔：[processed/18645800-summary.md](../../confluence/processed/18645800-summary.md)
> Confluence 最後更新：2021-05-12 13:01
> 摘要最後同步：2026-05-27 06:20

**摘要**：
本文件涵蓋 Python 服務的操作流程，包括 API 呼叫方式、資料處理步驟、圖表生成規則與 Docker 部署配置。pregame 和 inplay 階段的圖檔需分開存放，各 Docker 執行個體有獨立的執行間隔設定。

**AI 開發需要注意的部分**：
- 程式需支援根據 GameType（SC、BS、BK）與階段（pregame/inplay）進行不同的圖表縱軸參數設定。
- 圖表生成前需先透過 game 取得所有關聯的 sitegame 再合併。
- 所有輸出圖表必須加上浮水印。
- API 路徑均為 v1 版本，實作時需確認是否已遷移至新版本。