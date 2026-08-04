# newlotterysite — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 11:51
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### 新運彩社群 API

> Confluence 頁面 ID：79470704
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79470704)
> 摘要檔：[processed/79470704-summary.md](../../confluence/processed/79470704-summary.md)
> Confluence 最後更新：2026-05-22
> 摘要最後同步：2026-05-26

**摘要**：
這是一份新運彩社群功能的 API 技術規格文件，涵蓋了看板、討論、留言及按讚等核心功能的 CRUD 操作。對於 AI 開發，此文件提供了精確的 API 路徑、請求/回應格式、業務邏輯驗證規則（如字數限制、重複檢查）以及錯誤處理回應，是開發或整合前端社群功能與後端服務的關鍵參考。

**關鍵業務規則**：
- 看板名稱（names）為必填，最少需要 1 個字元，且名稱不能與先前已有的看板重複。
- 看板的狀態（status）欄位以整數 1 或 0 表示（需人工確認具體含義，推測為啟用/停用）。
- 討論的標題（subject）為必填，字數限制在 1 到 100 個字元之間，且不能與同看板內的其他討論標題重複。
- 討論建立時的留言（comment）為必填，字數限制在 1 到 2000 個字元之間。
- 討論取得分頁（page_index）預設從第 1 頁開始，每頁最多回傳 20 筆討論。回應中的 next_page 欄位（布林值）用來判斷是否還有下一頁。
- 留言建立時的內容（comment）字數限制為 2000 個字元。若提供 respond 欄位回覆其他留言，若指向的留言 ID 不存在，API 將回應 400 錯誤。
- 對同一討論串或留言，同一使用者（account）不允許重複按讚，重複按讚會回應 409 Conflict 錯誤。
- 討論按讚或留言按讚時，請求體（payload）必須包含 userName, account, headShotPath。
- 圖片上傳的儲存路徑遵循特定規則：以討論的發文日期為基礎建立日期目錄，格式為 /usr/local/openresty/nginx/html/downloads/newlottery/img/YYYY-MM-DD/討論ID/留言ID/圖片檔名。
- 將看板、討論或留言的標的物（如 forum_id, subject_id）作為路徑參數傳入，若該資源不存在，API 一律回應 404 Not Found 及對應的錯誤訊息（如「看板不存在」、「討論不存在」、 「留言不存在」）。

**注意事項**：
- ⚠️ status 欄位的值 0 和 1 分別代表的確切狀態（例如：0=關閉/停用，1=開啟/啟用）在文件中未明確定義，需要人工確認或從前後端程式碼確認。
- ⚠️ 關於「看板不能與先前重複」的規則，是在「建立」和「編輯」時都會觸發嗎？編輯時是否允許保留原名稱不變而不觸發重複檢查？需人工確認驗證範圍。
- ⚠️ 編輯討論內容的 HTTP 方法為 POST 而非語意上更合適的 PUT 或 PATCH，這可能是一個需要留意的設計選擇，或僅為草稿階段的筆誤。
- ⚠️ 圖片路徑章節提到「正式路徑會再修改」，表明當前文件中的圖床路徑為開發/測試環境，正式環境部署時需特別注意此設定。

---

## 技術設計類

### 新運彩社群 API

> Confluence 頁面 ID：79470704
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79470704)
> 摘要檔：[processed/79470704-summary.md](../../confluence/processed/79470704-summary.md)
> Confluence 最後更新：2026-05-22
> 摘要最後同步：2026-05-26

**摘要**：
這是一份新運彩社群功能的 API 技術規格文件，涵蓋了看板、討論、留言及按讚等核心功能的 CRUD 操作。對於 AI 開發，此文件提供了精確的 API 路徑、請求/回應格式、業務邏輯驗證規則（如字數限制、重複檢查）以及錯誤處理回應，是開發或整合前端社群功能與後端服務的關鍵參考。

**關鍵設計決策**：
- 使用 RESTful API 風格設計，對資源（看板、討論、留言）進行標準的 CRUD 操作，路由結構清晰地反映了資源的階層關係（如 /forums/{forum_id}/subjects）。
- 狀態欄位（如看板開關、討論/留言狀態）統一使用整數型態（1 或 0）而非布林值或字串，方便擴充更多狀態。
- 按讚和收回讚設計為兩個獨立的 API 端點（POST /likes 和 POST /unlike），而不是透過同一個端點用 HTTP 方法（如 PUT/DELETE）或參數來控制，簡化了請求的語意。
- 討論和留言的回應中嵌入了使用者資訊（userName, account, headShotPath），使前端不需再為每個評論單獨查詢使用者服務，減少了請求次數。
- 圖片路徑規則以討論的建立日期為基準，即使後續的留言在不同日期發布，其上傳的圖片依然存放在討論建立日期的目錄下，此設計保持了同一討論串所有圖片資源在儲存層的聚合性。

**注意事項**：
- ⚠️ status 欄位的值 0 和 1 分別代表的確切狀態（例如：0=關閉/停用，1=開啟/啟用）在文件中未明確定義，需要人工確認或從前後端程式碼確認。
- ⚠️ 關於「看板不能與先前重複」的規則，是在「建立」和「編輯」時都會觸發嗎？編輯時是否允許保留原名稱不變而不觸發重複檢查？需人工確認驗證範圍。
- ⚠️ 編輯討論內容的 HTTP 方法為 POST 而非語意上更合適的 PUT 或 PATCH，這可能是一個需要留意的設計選擇，或僅為草稿階段的筆誤。
- ⚠️ 圖片路徑章節提到「正式路徑會再修改」，表明當前文件中的圖床路徑為開發/測試環境，正式環境部署時需特別注意此設定。

---

## 操作手冊類

### NewLottery-Predict報表

> Confluence 頁面 ID：79471324
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471324)
> 摘要檔：[processed/79471324-summary.md](../../confluence/processed/79471324-summary.md)
> Confluence 最後更新：2026-05-10
> 摘要最後同步：2026-05-27

**摘要**：
本文件為使用 AI 生成 NewLottery-Predict 報表後端 API 與前端 UI 的開發指引。提供了針對 PredictService 和 NewLotteryBackEndService 的 Prompt 範本，指導 AI 如何根據資料表 predictbets_*_newlottery 和 championships_newlottery 設計查詢流程（A~D），並產生 Plan 與程式碼。同時說明如何利用 AI Review Server 自動檢查計畫與程式碼合規性，以及前端畫面設計的 Prompt 範例。對 AI 開發者的幫助在於可複用這些 Prompt 快速生成報表功能，並理解相關資料表結構與報表邏輯。

**AI 開發需要注意的部分**：
- 採用 AI 生成 Plan 與 Code，並由 AI Review Server 透過 /aidata/PLAN_SPEC.md 和 /aidata/csharp/.cursor_rules 自動檢查合規性。
- 報表查詢分為依錦標賽（A 流程）、依會員（B 流程）、依帳號與錦標賽（C 流程）、依起訖日期（D 流程）四種場景，每種場景又分為群組彙總與明細查詢。
- 使用 pricecenterservice 取得比賽隊伍與聯盟資訊，並對 PredictBet.GID 的查詢結果進行快取，避免重複請求。
- 前端報表設計使用兩個 Tab 切換（依錦標賽／依會員），並以多層 Grid 展開明細，支援排序。

**注意事項**：
- ⚠️ championships_newlottery.gid 與 predictbets_{gameType}_newlottery.gid 意義完全不同，不可混淆。
- ⚠️ 文件提到的流程 D.1 後會回到 A.1，可能隱含前端互動需要循環查詢，需人工確認實際 UX 設計。
- ⚠️ 目前流程描述基於 perdict.json 的資料結構，若資料表結構變動，需重新驗證 Prompt。
- ⚠️ 檢查結果的圖片顯示 Rocket Chat 通知，僅供參考，實際審查標準以 PLAN_SPEC.md 和 .cursor_rules 為準。