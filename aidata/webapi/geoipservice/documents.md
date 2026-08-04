# geoipservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-26 10:00
> 完整索引：[aidata/confluence/_index.md](../confluence/_index.md)

---


## 業務規範類


### IP 查詢結果地址中文化規則

> Confluence 頁面 ID：2884231
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884231)
> 摘要檔：[../confluence/processed/2884231-summary.md](../confluence/processed/2884231-summary.md)
> Confluence 最後更新：2020-06-28 09:11
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
該研究筆記明確指出 IP 查詢回傳的地址必須以中文呈現，為滿足業務需求，GeoIP 服務需依賴 TranslateService 進行翻譯。對 AI 開發而言，這是強制性的輸出格式約束。

**關鍵業務規則**：
- IP 查詢結果的地址必須以中文輸出

**注意事項**：
- ⚠️ 翻譯介面尚未定義，需人工補齊錯誤處理規則
- ⚠️ 此需求距今已久，確認目前是否仍適用

---

## 技術設計類


### GeoIP Service

> Confluence 頁面 ID：2884229
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/GeoIP+Service)
> 摘要檔：[../confluence/processed/2884229-summary.md](../confluence/processed/2884229-summary.md)
> Confluence 最後更新：2020-06-28 14:41
> 摘要最後同步：2026-05-26

**摘要**：
本文件描述 GeoIP Service 的技術設計：服務使用 MaxMind 做為 IP 地理位置資料源，並將資料下載後內置於服務中，更新時需重新打包。查詢時使用 Redis 快取，定義在 db2 中，key 為 IP 前兩碼加上語系，hashkey 為 IP 後兩碼。對 AI 開發而言，這有助於理解服務的資料依賴、更新方式與快取結構，便於模擬或測試相關功能。

**關鍵設計決策**：
- 資料源選擇 MaxMind，並將資料下載後直接內置於服務內部，不即時連線查詢外部 API。
- 資料更新方式：需定期至 MaxMind 官網下載新檔案，重新打包服務後部署，無法熱加載。
- Redis 快取設計：使用 db2，key 由「IP 前兩碼 + 語系」組成，hashkey 為「IP 後兩碼」，以支援多語系且利用 Redis hash 結構減少 key 數量。

**影響範圍**：
- 這些設計影響到服務的資料更新流程、部署方式及 Redis 結構，不可輕易變更。

**注意事項**：
- ⚠️ 文件最後更新於 2020 年，Redis schema、MaxMind 帳號可能已變更，需人工確認是否仍現行。
- ⚠️ 更新流程需重新打包服務，可能影響部署自動化，需確認目前的 CI/CD 流程是否已調整。

---

## 歷史決策類


### GeoIP 功能研究筆記

> Confluence 頁面 ID：2884231
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884231)
> 摘要檔：[../confluence/processed/2884231-summary.md](../confluence/processed/2884231-summary.md)
> Confluence 最後更新：2020-06-28 09:11
> 摘要最後同步：2026-05-26

**摘要**：
這是一份 GeoIP 功能的研究筆記，記錄了初步選型：採用 MaxMind GeoLite2 資料庫與對應的 .NET 套件進行 IP 查詢，並識別出輸出地址需翻譯成中文的業務需求，預計依賴 TranslateService 完成英譯中。

**決策背景**：
在專案開發初期，需為系統增加 IP 地理位置查詢功能，經調研後選定技術方案。

**決策結論**：
- 資料來源選用 MaxMind GeoLite2 資料庫
- 在 .NET 環境中選用 GeoIP2-dotnet 或 GeoIP NuGet 套件進行整合
- 地址翻譯功能由 TranslateService 提供，GeoIP 服務需呼叫 TranslateService 將英文地址轉為中文

**影響**：
- 該決策奠定了 GeoIP Service 的基礎架構與對 TranslateService 的依賴關係；因文件距今已久，需確認目前方案是否仍沿用，以及翻譯機制的具體實作。

**注意事項**：
- ⚠️ 需求表格中解決方案欄位為空，顯示當時翻譯機制尚未具體設計
- ⚠️ 僅提及「需要 TranslateService」，未定義介面或錯誤處理規則，需人工補齊

---

## 操作手冊類

暫無相關操作手冊文件。