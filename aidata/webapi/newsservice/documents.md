# newsservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 10:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---


## 業務規範類


### NewsService API

> Confluence 頁面 ID：24087149
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/NewsService+API)
> 摘要檔：[processed/24087149-summary.md](../../confluence/processed/24087149-summary.md)
> Confluence 最後更新：2021-10-21 11:10
> 摘要最後同步：2026-05-26

**摘要**：
定義了 NewsService 三個 REST API 端點：POST 儲存運動新聞（支援 JSON 陣列批次寫入）、GET 查詢運動新聞（需指定遊戲類型、時間戳及語言，可選標籤過濾）、DELETE 刪除新聞（由 XXL JOB 排程每月最後一天晚上 11 點呼叫）。對 AI 開發的幫助在於：明確 API 輸入輸出格式、必填／選填參數及排程刪除機制，可用於建構模擬客戶端、撰寫整合測試或理解新聞資料的生命週期。

**關鍵業務規則**：
- 查詢運動新聞時，必須提供 gameType（遊戲類型）、addTime（時間戳）、lang（語言）參數，tag（標籤）為選填
- 刪除運動新聞的 API 由 XXL JOB 在每月最後一天的晚上 11 點自動呼叫，應確保此排程已正確設定且目標 gameType 路徑參數對應正確

**注意事項**：
- ⚠️ 文件最後更新於 2021-10-21，距現在已有一段時間，API 規格可能已變更或新增其他端點，需人工確認當前版本
- ⚠️ 文件中 Routing 欄位可能有筆誤（如 newsservice/api/sports/{gameType}），實際使用時應以環境實際路徑為準


### NewsService Flow

> Confluence 頁面 ID：24086876
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/NewsService+Flow)
> 摘要檔：[processed/24086876-summary.md](../../confluence/processed/24086876-summary.md)
> Confluence 最後更新：2021-10-20 10:54
> 摘要最後同步：2026-05-26

**摘要**：
PlantUML 流程圖說明三個核心流程：儲存爬蟲傳入的運動新聞（球種驗證、生成 ID、寫入 DB）；透過 PriceCenterSite 向客戶端提供新聞查詢（限 24 小時內新聞，依運動種類與語系過濾，並篩選標籤）；以及透過 xxljob 排程刪除過期新聞（依球種與日期比對後刪除）。

**關鍵業務規則**：
- 儲存爬蟲資料時必須驗證球種（運動項目），並由 NewsService 生成新聞 id 後才寫入資料庫。
- 查詢新聞時必須驗證運動種類與語系，只回傳 24 小時內的新聞資料，並根據標籤進行篩選。
- 刪除舊新聞時必須先驗證球種，計算特定日期，找出該日期前的所有資料後進行批次刪除。

**注意事項**：
- ⚠️ 文件最後更新於 2021-10-20，距今已久，流程或依賴的服務（如 PriceCenterSite、xxljob）可能已變更，需人工確認目前實作是否仍相同。
- ⚠️ 「球種」一詞可能指特定運動類型，其實際定義與對應值未於流程中說明，需查閱程式碼確認。
- ⚠️ 流程中的「篩選標籤」步驟並未詳細說明規則，可能包含黑名單或廣告標記等，需進一步釐清。


### TCZB-1163 [NewsService]-新聞處理API

> Confluence 頁面 ID：24086871
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24086871)
> 摘要檔：[processed/24086871-summary.md](../../confluence/processed/24086871-summary.md)
> Confluence 最後更新：2021-10-21 11:18
> 摘要最後同步：2026-05-27

**摘要**：
定義新聞服務（NewsService）中處理運動新聞的 API 規範，包含儲存、查詢、刪除三個端點。新聞資料依 gameType 寫入對應的分錶 sports_{gameType}，主鍵 id 由 sourcesite 雜湊產生，查詢預設依 addtime 降冪排序。另有定期任務每月底刪除一個月前的舊新聞，適用於爬蟲資料儲存與前台展示場景。

**關鍵業務規則**：
- 新聞 id 由 sourcesite 的值進行 hash 後產生，非自動遞增或 UUID。
- 取得新聞資料時，回應清單預設以 addtime 降冪排序。
- 系統會定期刪除一個月以前的運動新聞資料，由 XXL JOB 在每個月最後一天晚上 11 點觸發 DELETE API。
- 取得新聞時必填 gameType、addtime、lang 三個參數，tag 為選填，作為篩選條件。

**注意事項**：
- ⚠️ 文件最後更新於 2021-10-21，可能與當前實作有落差，例如分錶名稱、參數格式或刪除策略，需人工確認。
- ⚠️ gameType 參數比照「data define」頁面，但該頁面連結無法直接取得具體枚舉值，開發時需查閱最新定義。
- ⚠️ POST 儲存 API 的 Response 欄位未明確定義，需確認實際回應格式（如是否回傳 id 或成功狀態）。


### TCZB-2852 [球王] 新聞製造

> Confluence 頁面 ID：47222926
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47222926)
> 摘要檔：[processed/47222926-summary.md](../../confluence/processed/47222926-summary.md)
> Confluence 最後更新：2023-08-08 11:00
> 摘要最後同步：2026-05-27

**摘要**：
記錄對同一篇棒球新聞以不同 Prompt 進行改寫的實驗結果，包含多種風格的輸出範例，並觀察到即使 Prompt 明確要求繁體中文，偶爾仍會輸出簡體中文的問題。同時討論了新聞內容使用的版權風險：若原始新聞為單純事實傳達，可直接使用；若包含作者創作成分，則可能侵權。

**關鍵業務規則**：
- 新聞改寫功能應輸出繁體中文，但 Prompt 無法完全保證，需有後處理機制（如語言偵測與轉換）或更強力的約束。
- 當來源新聞為單純事實報導（不包含主觀意見或創作）時，可原文或改寫後使用；若新聞內容有作者的原創表達，則改寫後仍可能涉及版權問題，需謹慎評估或取得授權。

**注意事項**：
- ⚠️ 即使 Prompt 結尾強調「一定要用繁體中文輸出」，偶爾還是會得到簡體中文，此為已知風險，需從程式或模型參數層面補強。
- ⚠️ 版權疑慮僅為討論中的原則，尚未有正式法務確認或具體簽約條款，需人工進一步核實。


### ⚠️ 請人工確認：查詢時間範圍不一致
- NewsService Flow 提到查詢新聞時只回傳 24 小時內的新聞資料，但 NewsService API 和 TCZB-1163 的文件中未明確提及此限制，請確認實際 API 行為。


## 技術設計類


### NewsService DB Table

> Confluence 頁面 ID：24086858
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/NewsService+DB+Table)
> 摘要檔：[processed/24086858-summary.md](../../confluence/processed/24086858-summary.md)
> Confluence 最後更新：2021-10-20 08:25
> 摘要最後同步：2026-05-26

**摘要**：
定義 NewsService 所使用的動態資料表 sports_{gameType} 的結構，包含新聞 ID（由網址 hash 產生）、日期、標題、內容、連結、來源網站、標籤及語系等欄位。此表用於儲存從各來源爬取的運動新聞資料。

**關鍵業務規則**：
- —

**注意事項**：
- ⚠️ 文件內容僅包含資料表欄位定義，未說明 partition 策略或 gameType 的實際對應值，需查閱其他文件或程式碼。
- ⚠️ 最後更新於 2021-10-20，需確認表結構是否仍與現行服務一致。


### TCZB-4172 [NewsService] - 熱門討論賽事

> Confluence 頁面 ID：79467890
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467890)
> 摘要檔：[processed/79467890-summary.md](../../confluence/processed/79467890-summary.md)
> Confluence 最後更新：2026-01-13 13:03
> 摘要最後同步：2026-05-27

**摘要**：
定義了新聞服務中「AI熱門討論賽事」的管理功能，包含設定、查詢與刪除API，以及對應的Cassandra資料表 inplayzsettting（可能為 inplayzsetting）。對AI開發而言，可明確知道API路徑、請求/回應格式、必填欄位及資料表結構，作為實作此功能的依據。

**關鍵業務規則**：
- 設定AI熱門討論賽事時，gdate、gtype、lid、gid、title 欄位不得為空。
- 取得AI熱門討論賽事使用 GET /newservice/api/sports/ai/hotdiscussiongames/{gameType}/{gdate}，其中 gameType 為球種，gdate 為賽事日期。
- 刪除AI熱門討論賽事使用 DELETE /newservice/api/sports/ai/hotdiscussiongames/{gameType}/{lid}/{gdate}/{gid}，需提供完整路徑參數。

**注意事項**：
- ⚠️ 文件中的表名拼寫為 inplayzsettting，可能有誤，需人工確認正確名稱。
- ⚠️ footer 欄位在設定API中可傳入，但在取得API的回應範例中為 null，可能為可選欄位，但未明確說明。
- ⚠️ API 路由前綴 /newservice 與 NewsService 的服務名稱對應，但文件未明確指出服務實體，建議核對現有服務設定。


### TCZB-3506 [PriceCenterSite] - 台灣運彩文章API

> Confluence 頁面 ID：55581589
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55581589)
> 摘要檔：[processed/55581589-summary.md](../../confluence/processed/55581589-summary.md)
> Confluence 最後更新：2024-10-28 10:48
> 摘要最後同步：2026-05-27

**摘要**：
定義一個取得台灣運彩文章的 API 端點 (GET news/twsl/articles)，返回按文章類型（單場推薦、低賠串關）分組的文章列表，每篇文章包含 id、titleImage、title、date、description、content（HTML）與 languages 等欄位。此文件提供了 AI 開發 newsservice 時實作台灣運彩文章查詢功能的具體契約與回傳結構。

**關鍵業務規則**：
- —

**注意事項**：
- ⚠️ 需人工確認此 API 是否確實屬於 newsservice，而非 pricecentersite 或其他服務


### TCZB-3507 [NewsService] - 運動站台文章功能

> Confluence 頁面 ID：55581592
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55581592)
> 摘要檔：[processed/55581592-summary.md](../../confluence/processed/55581592-summary.md)
> Confluence 最後更新：2024-10-28 09:55
> 摘要最後同步：2026-05-27

**摘要**：
簡短的技術變更記錄：為了支援台灣運彩文章，在既有的 NewsService 取得運動站台文章 API（GET /newsservice/api/sportarticles）上新增查詢參數 articleClass（例如 twsl）。此變更修改舊有 API 的輸出邏輯，以根據參數篩選特定類別的文章。

**關鍵業務規則**：
- —

**注意事項**：
- ⚠️ 文件未說明 articleClass 的有效值（僅舉例 twsl），以及其他可能的分類。
- ⚠️ 輸出邏輯的變更細節缺失，無法判斷回傳結構是否相容舊有呼叫。
- ⚠️ 需人工確認此變更是否已上線，以及是否有對應的 API 文件更新。