# feedbackservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 10:30
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB-3113 [球王] - APP版 (pageId=55576712)

> Confluence 頁面 ID：55576712
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55576712)
> 摘要檔：[processed/55576712-summary.md](../../confluence/processed/55576712-summary.md)
> Confluence 最後更新：2024-01-12 10:02
> 摘要最後同步：2026-05-27

**摘要**：
文件定義了球王站點新增的使用者反饋與商業合作功能所需的 API，包括新增反饋訊息、新增商業合作訊息、獲取反饋種類、獲取會員反饋以及更新會員反饋問題等。對 AI 開發而言，需理解這些 API 的路由、參數格式、業務規則（如 status 含義、訊息長度限制、登入態處理），以便在反饋服務中實作相應的業務邏輯。

**關鍵業務規則**：
- 新增反饋訊息時，若使用者已登入（有 Account），則請求中帶上會員 authKey；否則 authKey 留空
- 商業合作訊息的 SendContent 最大長度為 200 字元
- 獲取會員反饋時，status 欄位：0 表示尚未回覆，1 表示已回覆，2 表示結束
- 更新會員反饋問題 API 需要提供 authKey, tid, dateTime, id 路徑參數，並在請求體中包含 Message 欄位

**注意事項**：
- ⚠️ 文件為 Sprint 147 的規劃，需確認目前實際實作狀態是否完整

---

### TCZB-2298 [StockKing-APP] - 反饋系統 (pageId=44662954)

> Confluence 頁面 ID：44662954
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44662954)
> 摘要檔：[processed/44662954-summary.md](../../confluence/processed/44662954-summary.md)
> Confluence 最後更新：2022-12-05 08:34
> 摘要最後同步：2026-05-27

**摘要**：
此文件定義了 StockKing APP 的反饋系統 API，包含取得罐頭回覆的 GET /api/v1/feedback/autoreply 與提交使用者反饋的 POST /api/v1/feedback/user。設計上區分客戶（需帳號）與訪客（僅需 Email）兩種反饋途徑，並限制反饋內容字數上限 100 字。當罐頭回覆無匹配時，系統需引導使用者另開分頁寄信。

**關鍵業務規則**：
- 取得罐頭回覆時，回應結構為 { Name, ID, Questions: [{ID, Question, Answer}] }
- 新增使用者反饋時，客戶需提供 Account、Email、Type、context；訪客僅需提供 Email，其餘欄位可忽略或為空
- context 欄位字數上限為 100 字，超過應在客戶端或 API 端攔截
- 若使用者提交的問題在罐頭回覆中無匹配項，系統必須以訊息引導其開啟新分頁寄信至客服信箱
- 客戶反饋的回覆記錄應顯示在個人設定的回饋紀錄中，訪客反饋則透過其提供的 Email 進行回覆

**注意事項**：
- ⚠️ 文件最後更新於 2022-12-05，實際 API 規格可能有變，實作前建議與後端確認最新契約
- ⚠️ 文件中僅列出成功回應範例，未描述錯誤情境的 HTTP Status Code 與錯誤結構，需補齊定義

---

⚠️ **業務規則潛在衝突**：context 字數上限 100 字（TCZB-2298）vs SendContent 最大長度 200 字元（TCZB-3113）— **請人工確認兩者是否為不同欄位或不同站台規範**

---

### TCZB-2909 [FeedbackService] - 客戶反饋和商業合作 (pageId=47223280)

> Confluence 頁面 ID：47223280
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47223280)
> 摘要檔：[processed/47223280-summary.md](../../confluence/processed/47223280-summary.md)
> Confluence 最後更新：2023-09-18 10:37
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義 FeedbackService 的運動站台反饋與商業合作 API，包含新增/查詢/更新/刪除反饋主題(SportTopic)、問題(SportQuestion)、反饋訊息(SportMessageDTO)及商業合作訊息(BusinessMessage)。同時提供對應的資料庫表格設計與狀態碼意義。

**關鍵業務規則**：
- SportTopic 的 Enabled 欄位：0 停用，1 啟用；Sort 欄位控制顯示順序
- SportQuestion 必須關聯一個 tid（主題 ID），且其 Enabled 同樣為 0/1
- SportMessageDTO 的 Status 欄位：0 尚未回覆、1 已回覆、2 結束
- BusinessMessage 的 Status 欄位：0 尚未回覆、1 已回覆
- 查詢反饋訊息時可選用 startDateTime、endDateTime、account 參數進行範圍篩選
- 更新反饋回覆內容時需提供完整路徑參數 {tid}/{dateTime}/{account}/{id}/respcontent

**注意事項**：
- ⚠️ Status = 2 (結束) 的觸發條件與後續行為（如是否允許再次更新）未在文件中說明，需人工補齊

---

### TCZB-2943 [PriceTools] - 通知中心和反饋系統 (pageId=55574533)

> Confluence 頁面 ID：55574533
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55574533)
> 摘要檔：[processed/55574533-summary.md](../../confluence/processed/55574533-summary.md)
> Confluence 最後更新：2023-09-20 15:39
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義了在 PriceTools 中新增通知中心（公告列表與公告訊息管理）與反饋系統（反饋類別管理、會員反饋、訪客反饋、商業合作訊息）的功能範圍，共規劃 18 個 API 端點，但尚未提供 Method、Route、參數等細節。對 AI 開發而言，可先了解需實作的後端功能模組與頁面結構，作為後續補足 API 規格的起點。

**關鍵業務規則**：
- 功能範圍包含公告管理（列表、訊息）與反饋管理（類別、會員、訪客、商業合作）
- 所有資源需支援列表查詢、新增、修改操作
- 反饋和商業合作訊息可修改狀態並進行回覆

**注意事項**：
- ⚠️ API 表格的 Method、Route、Parameter、Response 等欄位全部為空，詳細規格尚未定義，開發時需自行設計或等待補充

---

### Feedback功能研究筆記 (pageId=2884226)

> Confluence 頁面 ID：2884226
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884226)
> 摘要檔：[processed/2884226-summary.md](../../confluence/processed/2884226-summary.md)
> Confluence 最後更新：2020-07-28 20:47
> 摘要最後同步：2026-05-26

**摘要**：
文件記錄了 Feedback 功能的早期使用者需求，包括各公司可自定義問題模板、API 依 feedback id 回傳版型、前端自行設計 UI、以及儲存、後台查詢回覆等流程。可作為 Feedback Service 需求背景參考，但資訊較為簡略，需確認後續實作狀態。

**關鍵業務規則**：
- 各公司可自行定義 Feedback 問題模板，模板支援下拉選單、Radio、單/多行文字框、Checkbox 等欄位類型
- API 必須根據各公司的 feedback id 取得並回傳問題版型
- UI 由各公司取得模板後自行設計渲染，不強制統一介面
- 使用者填寫完成後，提交的資料必須儲存到系統的資料庫
- 管理者可在後台查詢所有使用者的 Feedback 留言資料
- 管理者可在後台直接回覆使用者的留言
- 使用者可在前台看到自己的留言以及管理者的回覆

**注意事項**：
- ⚠️ 文件最後更新於 2020-07-28，已逾 5 年，內容可能已過時或未實現，僅供早期需求背景參考
- ⚠️ 情緒分析僅為研究連結，尚未確認是否導入

---

## 技術設計類

### TCZB-2179 [FeedbackService] - 股票站台反饋機制 (pageId=40503909)

> Confluence 頁面 ID：40503909
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40503909)
> 摘要檔：[processed/40503909-summary.md](../../confluence/processed/40503909-summary.md)
> Confluence 最後更新：2022-11-10 13:40
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義股票站台反饋功能的 API 技術規格，包含 13 個端點來管理反饋主題、常見問題、使用者反饋訊息及回覆。採用 Cassandra 資料庫（keyspace: feedback）儲存，並提供完整的資料表 schema（topics_stock, questions_stock, feedbacks_stock）與資料傳輸模型（DTO）。

**關鍵設計決策**：
- 選擇 Cassandra 作為資料持久化儲存，資料庫名稱定為「feedback」
- API 回應格式統一採用 MsgCode Model，包含 Code 與 Message 欄位

**影響範圍**：
- DB 結構基於 Cassandra keyspace feedback，變更需考量分散式資料庫特性
- API Response 格式統一 MsgCode Model，所有端點需遵循此契約

**注意事項**：
- ⚠️ 文件建立於 2022-11，使用 Cassandra 資料庫，需確認目前 feedbackservice 是否仍採用此儲存方案
- ⚠️ 部分 Model 定義（如 StockFeedback、StockFeedbackReq）的欄位類型可能為 C# 專屬，實際 API 對應的 JSON 格式或 DB 結構需依據現行實作確認

---

## 歷史決策類

### Feedback功能研究筆記 (pageId=2884226)— 情緒分析導入評估

> Confluence 頁面 ID：2884226
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884226)
> 摘要檔：[processed/2884226-summary.md](../../confluence/processed/2884226-summary.md)
> Confluence 最後更新：2020-07-28 20:47
> 摘要最後同步：2026-05-26

**決策背景**：
2020 年 Feedback Service 早期規劃階段，團隊考慮加入情緒分析技術來分析使用者反饋情感，提供更深入的客服洞察。

**決策結論**：
研擬導入情緒分析技術，但僅提供參考連結進行評估，未確認是否導入。

**影響**：
目前系統中可能未實作情緒分析功能，AI 開發無需考量此需求，除非後續有新規格。

---

## 操作手冊類

> 目前無操作手冊類文件