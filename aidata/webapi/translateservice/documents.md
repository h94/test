# TranslateService — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### Translate產品項目

> Confluence 頁面 ID：11436857
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=11436857)
> 摘要檔：[processed/11436857-summary.md](../../confluence/processed/11436857-summary.md)
> Confluence 最後更新：2020-12-17
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件界定 TranslateService 為基於 Google Translate 搭配內部快取的免費翻譯工具，僅供內部技術訓練使用。文件明確聲明此服務不提供資料外流保證、不保證資料準確性，且不承擔任何使用損害責任。AI 開發此服務時，應將其視為內部試驗工具而非對外承諾的服務，開發時需注意其穩定性與安全性限制。

**關鍵業務規則**：
- 服務完全免費，僅供本公司內部技術訓練使用，不對外收費
- 翻譯內容不會主動送出，但無法保證資料不外流
- 網站資料僅供參考，可能隨時更改而不另行通知，本網站不保證資料準確性，也不對任何錯誤或遺漏承擔責任
- 使用者若以此服務進行不當行為，須自行承擔後果

**注意事項**：
- ⚠️ 文件最後更新於 2020-12-17，距今已多年，服務實作可能已變更，建議人工確認現狀
- ⚠️ 文件中「我方不會將內容送出，但也不能給予資料外流之保證」存在邏輯矛盾，需釐清實際的快取與傳輸機制是否會觸及外部 API

---

### 站台語系整理

> Confluence 頁面 ID：40502435
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40502435)
> 摘要檔：[processed/40502435-summary.md](../../confluence/processed/40502435-summary.md)
> Confluence 最後更新：2022-09-21
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件記載了 ps3838、1xbet、tonybet 三個站台對西班牙文、葡萄牙文、法文、德文的支援狀態。ps3838 支援西班牙文、法文、德文（無葡萄牙文）；1xbet 支援全部四種語言；tonybet 支援西班牙文（秘魯西班牙文）、法文（加拿大法文）和德文（奧地利德文），不支援葡萄牙文。可作為多語言內容生成、語言選擇器顯示邏輯的設定參考。

**關鍵業務規則**：
- ps3838 站台支援語言：西班牙文、法文、德文；不支援葡萄牙文
- 1xbet 站台支援語言：西班牙文、葡萄牙文、法文、德文
- tonybet 站台支援語言：西班牙文（Español - PE）、法文（Français-CA）、德文（Deutsch - AT）；不支援葡萄牙文

**注意事項**：
- ⚠️ 文件最後更新於 2022-09-21，語言支援清單可能已變更，開發前需確認最新狀態
- ⚠️ tonybet 的西班牙文標註為「Español - PE」、法文為「Français-CA」、德文為「Deutsch - AT」，其中 PE 可能代表秘魯（Perú），但確切地區需人工確認

---

### V3站台測試修改

> Confluence 頁面 ID：40502092
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40502092)
> 摘要檔：[processed/40502092-summary.md](../../confluence/processed/40502092-summary.md)
> Confluence 最後更新：2022-09-13
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這是一份 V3 站台 2022 年 9 月的測試修改記錄，包含登入、語系、比賽狀態、時間顯示、置頂/我的最愛等多項 UI 與互動調整。其中明確記錄了多項已修復的問題，以及「進行中的比賽不可加入我的最愛」此類業務規則，並有「hotgame 與我的最愛不分開」的決策。對 AI 開發的幫助在於瞭解當時已定義的行為與已知限制，避免重複提案或誤解功能邊界。

**關鍵業務規則**：
- 登入視窗必須提供取消或關閉按鈕，且支援按 Enter 鍵登入
- 常見問題連結顏色改為亮藍色
- 語系服務需與其他功能分開，並在語言選項旁顯示國旗
- 當前查看的比賽狀態需增加有色底線以區分狀態
- 畫面上需顯示日期時鐘與時區；若比賽日期為當天，則僅顯示時間
- 置頂功能需提供清除置頂按鈕，並在操作時顯示提示
- 進行中的比賽不可加入我的最愛
- 勾選的項目在特定時間後會被清除（需人工確認觸發條件）

**注意事項**：
- ⚠️ 文件最後更新於 2022-09-13，且位於「舊的Projects」歸檔區，內容可能已過期，需比對當前站台行為
- ⚠️ 「勾選後一段時間會被清除」的具體時間或觸發機制未說明，需人工確認
- ⚠️ 圖片附件僅供參考，截圖中的 UI 可能已變更

---

## 技術設計類

### TranslateService

> Confluence 頁面 ID：2884081
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TranslateService)
> 摘要檔：[processed/2884081-summary.md](../../confluence/processed/2884081-summary.md)
> Confluence 最後更新：2020-06-27
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件說明了 TranslateService 的多語系翻譯架構：管理人員在 MaintainSite 編輯翻譯並存入 SQL 資料庫，RedisJob 定期將資料同步到 Redis（以 CountryCode 為 Key 的 Hash），WebSite 透過 TranslateService 從 Redis 讀取翻譯內容。AI 開發此服務時，需要了解 DB/Redis Schema、資料流以及第三方翻譯服務的 Log 紀錄機制，以正確實作或呼叫該服務。

**關鍵設計決策**：
- 採用 Redis Hash 快取翻譯，Key 為 `Translate_{{CountryCode}}`，HashKey 為 KeywordName，HashValue 為 Content，便於批次取得某語系的所有翻譯，顯著提升讀取效能
- 由 RedisJob 定期從 DB 抓取翻譯內容更新 Redis，確保讀取速度，但未說明同步頻率或即時性保證（需人工確認）
- DB 區分 Keywords（原始文字或代號）、Countries（語系代碼）、Translates（實際翻譯內容）及 Logs（記錄第三方翻譯服務呼叫），解耦管理與翻譯過程
- WebSite 統一向 TranslateService 請求翻譯，不直接存取 DB，實作顯示層與資料層的分離

**影響範圍**：
- WebSite 的多語言顯示架構直接依賴此設計，任何查詢翻譯的服務都應透過 TranslateService API，不可直接存取翻譯相關的 DB 或 Redis

**注意事項**：
- ⚠️ 文件最後更新於 2020-06-27，距今已超過三年，架構可能已變更，需人工確認現行設計
- ⚠️ Swagger 連結為內部 IP（192.168.1.232:32203），可能因環境遷移而失效，需查閱最新 API 文件
- ⚠️ Logs 表設計暗示曾調用第三方翻譯服務，但流程圖未體現此互動，需確認目前是否仍使用外部翻譯並理解其觸發方式

---

### TranslateService功能研究筆記

> Confluence 頁面 ID：2884114
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884114)
> 摘要檔：[processed/2884114-summary.md](../../confluence/processed/2884114-summary.md)
> Confluence 最後更新：2020-06-24
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這篇是 TranslateService 的早期研究筆記，記錄了翻譯服務的兩大核心需求：支援片語與整篇文章的翻譯代號機制、以及後台分群查找功能。技術面確定了批量查詢的 API 參數格式（逗號分隔多個詞彙）、回傳格式採用 Dictionary<string,string> 而非 List<Translate>。效能優化方面，提出了 translates.usecount 欄位來記錄調用次數，讓高頻且穩定的翻譯內容可以快取到記憶體中提高命中率。

**關鍵設計決策**：
- API 設計支援一次請求攜帶多筆詞彙，以逗號或特殊符號分隔（例：`translate/get?to=zh_cn&words=你好嗎,我很好,你是誰`）
- keyword 設計以繁體中文作為 keyword，英文作為代號（code）
- 回傳格式採用 Dictionary<string,string> 而非 List<Translate>，原因是 List<Translate> 不易轉換為 JSON
- 採用 translates.usecount 欄位記錄調用次數，次數多且不常被改動的內容可放入 app 記憶體中提高命中率
- 翻譯 API 研究了多種方案：Google API .NET Client、Microsoft Translator API、GoogleTranslateFreeApi 等 NuGet 套件（需人工確認最終採用方案）

**影響範圍**：
- API 參數設計與回傳格式定義了呼叫方與此服務的契約介面，不可輕易變更
- translates.usecount 的快取策略影響系統效能，移除或變更需謹慎評估

**注意事項**：
- ⚠️ 本文為 2020 年 6 月的研究筆記，屬於早期設計階段，需人工確認最終實作是否與筆記一致
- ⚠️ 文件中提及的多個第三方翻譯 API 方案（Google API、Microsoft Translator、GoogleTranslateFreeApi）未標註最終選擇，需人工確認
- ⚠️ 內容為筆記格式，部分需求（如後台分群）只有問題描述沒有解決方案，可能尚未定案

---

### TCZB-917 [ForntEndSite] - more language

> Confluence 頁面 ID：22544546
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-917+%5BForntEndSite%5D+-+more+language)
> 摘要檔：[processed/22544546-summary.md](../../confluence/processed/22544546-summary.md)
> Confluence 最後更新：2021-07-16
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件規劃前端多語言功能的實現方案，支援繁中、簡中、英文、日文四種語言切換。靜態介面內容由 i18n 套件處理，動態數據（如隊伍名稱）通過調用 API 獲取翻譯映射表來轉換。該設計分離了前後端翻譯職責，對 AI 理解多語言數據流和翻譯服務介面有幫助，尤其需關注 translateservice 如何提供映射數據及前端如何消費。

**關鍵設計決策**：
- 前端採用 i18n 套件管理靜態文案，與後端 API 翻譯映射解耦
- 動態內容（如隊伍名稱）的翻譯數據由後端 API 提供 mapping 表，保證數據一致性
- 用戶可自行選擇網頁語言，語言選項包括繁中、簡中、英文、日文

**影響範圍**：
- 前端依賴後端 API 提供動態內容的翻譯映射，API 介面變更將直接影響前端多語言功能
- i18n 與 API 翻譯的職責邊界確立後，新增或修改翻譯邏輯需遵循此分層架構

**注意事項**：
- ⚠️ 文件最後更新於 2021-07-16，可能與當前 translateservice 或前端實現有較大差異，需人工確認
- ⚠️ 文件內容極簡，缺少介面定義、數據格式、異常處理等關鍵實現細節

---

### [SportKing]-翻譯

> Confluence 頁面 ID：47219363
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47219363)
> 摘要檔：[processed/47219363-summary.md](../../confluence/processed/47219363-summary.md)
> Confluence 最後更新：2023-02-22
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這是一份運動統計術語（如得分、籃板、助攻等）的英文、繁中、簡中及日文翻譯對照表。它可作為翻譯服務的基礎資料，協助開發體育相關功能時提供多語系顯示，但部分語言欄位（西、葡、泰、越）尚缺值，待補全。

**關鍵設計決策**：
- 以英文為來源語言，提供繁中、簡中、日文三種語言的對應翻譯，作為運動統計術語的翻譯基準

**影響範圍**：
- 體育相關功能的多語言顯示需以此對照表為基礎，新增或修改體育術語翻譯時需參考此表

**注意事項**：
- ⚠️ 西班牙文、葡萄牙文、泰文、越南文翻譯欄位為空白，需人工確認是否已另有翻譯或待補齊
- ⚠️ 文件未標注語系版本或生效日期，可能需與當前系統中的翻譯對照比對確認一致性

---

## 歷史決策類

### V3站台測試修改

> Confluence 頁面 ID：40502092
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40502092)
> 摘要檔：[processed/40502092-summary.md](../../confluence/processed/40502092-summary.md)
> Confluence 最後更新：2022-09-13
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**決策背景**：
2022 年 9 月 V3 站台進行測試修改，針對登入、語系、比賽狀態、時間顯示、置頂/我的最愛等多項 UI 與互動功能進行調整與問題修復。

**決策結論**：
- hotgame 與我的最愛賽事保持合併顯示，不分開（狀態：不更改）
- 我的最愛功能在進行中的比賽上禁用（已修改）
- 語系服務分開獨立，不與其他模組耦合（已修改）

**影響**：
- my favorite 功能在進行中比賽的行為不可變更（已禁用）
- hotgame 與 my favorite 的合併顯示策略已定案，不可輕易拆分
- 語系服務與其他功能模組的分離架構已確立，新增功能時不可將語系模組與其他模組耦合

---

## 操作手冊類

### TranslateService功能研究筆記

> Confluence 頁面 ID：2884114
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884114)
> 摘要檔：[processed/2884114-summary.md](../../confluence/processed/2884114-summary.md)
> Confluence 最後更新：2020-06-24
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
TranslateService 的早期研究筆記，記錄了翻譯服務的兩大核心需求：支援片語與整篇文章的翻譯代號機制、以及後台分群查找功能。技術面確定了批量查詢的 API 參數格式（逗號分隔多個詞彙）、回傳格式採用 Dictionary<string,string>。

**AI 開發需要注意的部分**：
- API 呼叫時需支援一次請求攜帶多筆詞彙，以逗號分隔（例：`translate/get?to=zh_cn&words=你好嗎,我很好,你是誰`）
- 回傳格式為 Dictionary<string,string>，Key 為原始關鍵字，Value 為翻譯內容，而非 List<Translate> 結構
- 翻譯查找需同時支援片語（keyword）和整篇文章（code），不可只實作單一查找模式
- translates.usecount 欄位需記錄每次調用次數，用於判斷是否適合放入記憶體快取
- 後台查找功能需能同時針對片語（keyword）和代碼（code）進行查詢，直接對 Translate 表查詢

---

### [SportKing]-翻譯

> Confluence 頁面 ID：47219363
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47219363)
> 摘要檔：[processed/47219363-summary.md](../../confluence/processed/47219363-summary.md)
> Confluence 最後更新：2023-02-22
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
運動統計術語（如得分、籃板、助攻等）的英文、繁中、簡中及日文翻譯對照表，可作為翻譯服務的基礎資料，協助開發體育相關功能時提供多語系顯示。

**AI 開發需要注意的部分**：
- 體育術語翻譯時，需以本對照表為基準，不可自行創建新的翻譯詞彙
- 西班牙文、葡萄牙文、泰文、越南文翻譯欄位為空白，生成這四種語言的內容時需特別處理（不可憑空生成）
- 表中未列出的運動術語需遵循相同的翻譯風格進行擴充