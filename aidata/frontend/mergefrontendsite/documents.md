# mergefrontendsite — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 12:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB-3743 [球王] - 首頁Google廣告/電子布告欄

> Confluence 頁面 ID：76546745
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76546745)
> 摘要檔：[processed/76546745-summary.md](../../confluence/processed/76546745-summary.md)
> Confluence 最後更新：2025-05-23
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義球王網站首頁的 Google 廣告區塊排版（右側 180px 跟隨滾動）與電子布告欄顯示規則。布告欄有電腦版與手機版尺寸規範，標題最多 9 字，副標題自動換行且無灰色背景。名單區塊使用綠色標題、灰色背景。數據以 JSON 格式提供，明確 title/sub 及名單結構。

**關鍵業務規則**：
- 電子布告欄（電腦版）：寬度 100%、高度 200px；背景寬 100%、高度 160px（80%）；螢幕圖維持原比例，螢幕高 200px
- 電子布告欄（手機版）：背景寬 100%、高度 135px；螢幕寬 405px、螢幕高 157px
- 布告欄標題文字最多 9 字
- 副標題超過邊界時換行顯示，且無灰色背景
- 副標題的數據格式為 {"title": "標題", "sub": "副標題內容"}
- 名單（如獎金賽）顯示綠色標題、灰色背景，獎金數字放不下則換行
- 名單的數據格式為 {"title": "獎金賽", "sub": [{"帳號": 金額}, ...]}
- Google 廣告區塊固定於首頁內文區域右側 180px，並跟隨使用者畫面下拉（sticky）

**注意事項**：
- ⚠️ Confidence 為 low，規則可能不完整或已變更，建議人工確認

---

## 技術設計類

### Cursor使用心得-在mergefrontendsite中加入OpenClawMerge展示和合併功能

> Confluence 頁面 ID：79469552
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469552)
> 摘要檔：[processed/79469552-summary.md](../../confluence/processed/79469552-summary.md)
> Confluence 最後更新：2026-04-15
> 摘要最後同步：2026-05-27

**摘要**：
記錄使用 Cursor 為 mergefrontendsite 加入「龍蝦自動合併」功能的實作過程。包含查詢頁面預設值（球種預設棒球、時間預設整點）、查詢結果主客隊顯示規則（主隊附加「(主)」）、SiteGame.swap=1 時 checkbox disabled、合併操作逐筆調用 API 並依回傳狀態顯示成功或失敗訊息。後續測試發現合併 API 調用有誤且缺少必要資料，功能尚未完全驗證。

**關鍵業務規則**：
- 查詢頁面預設值：球種預設為棒球；開始時間預設為當前時間的整點小時（如 11:25 → 11:00），結束時間預設為當前時間的整點小時，分鐘固定為 59（如 11:25 → 11:59）
- 查詢結果主/客隊顯示：客隊顯示 teamA.tName，主隊顯示 teamH.tName 並附加「(主)」，不同行呈現
- 待合併比賽表格中，若 SiteGame.swap = 1，則該列的合併 checkbox 必須為不可點選（disabled）
- 操作（合併）流程：針對所有勾選的 SiteGame，逐一調用 /api/combine/game/{GameType}，參數為 site, sitelid, sitegid, gid。若所有調用皆回傳 200，顯示「Merge Success.」；若有非 200 回應，則組裝失敗訊息並顯示。確認訊息後自動重新查詢並重繪表格
- 查詢 API (/api/merge/openclaw-merge) 的日期時間參數格式必須為「yyyy-MM-dd HH:mm」，不可使用 + 號（即不可用 URL 編碼的空白）
- 整體文字顏色使用白色，但查詢按鈕及操作按鈕的文字顏色為黑色

**關鍵設計決策**：
- 選用 Figma 生成 UI 草圖以加速前端設計
- 查詢功能直接調用 mergesite 的 openclaw-merge API；合併動作原先規劃調用 pricecenterservice 的 combine API，但後續測試發現此 API 不適用

**影響範圍**：
- 合併功能未完成，API 調用方式可能需重新設計
- 依賴 mergesite 和 pricecenterservice 的介面

**注意事項**：
- ⚠️ 合併功能測試階段發現不應調用 PriceCenter 的 combine API，且該 API 缺乏必要資料，此部分功能尚未正確完成，規則可能變更
- ⚠️ Confluence 路徑標題提到「在 PriceCenterService 中加入讀取 Merge 資料的功能」，但文件實際內容為 mergefrontendsite 的前端開發，需注意對應關係可能錯置

---

### TCZB-864 [ForntEndSite] 文件頁面

> Confluence 頁面 ID：21659954
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=21659954)
> 摘要檔：[processed/21659954-summary.md](../../confluence/processed/21659954-summary.md)
> Confluence 最後更新：2021-06-22
> 摘要最後同步：2026-05-27

**摘要**：
定義通用文件頁面前端設計：所有文件頁面使用同一 page 框架，透過 router params 切換內容，從 config 取得文件內容渲染。參考 betradar、Sportradar、台灣運彩等隱私頁面作為相似案例，可讓開發者在實作靜態文件展示功能時複用框架。

**關鍵設計決策**：
- 所有文件頁面採用同一 page 框架，透過 router params 動態決定顯示哪份文件，並向 config 取得對應內容

**影響範圍**：
- 文件展示頁面的實作方式

**注意事項**：
- ⚠️ 文件最後更新於 2021-06-22，可能已過期或實作方式已變更
- ⚠️ 需求表格僅包含 #1（準備文件內容），未列出其他需求，可能不完整
- ⚠️ 文件來自「舊的Projects 1-200」路徑，專案結構或已重組，需人工確認現行做法

---

### TCZB-3115 [MergeSite] - 新增服務

> Confluence 頁面 ID：55576739
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55576739)
> 摘要檔：[processed/55576739-summary.md](../../confluence/processed/55576739-summary.md)
> Confluence 最後更新：2024-04-24
> 摘要最後同步：2026-05-27

**摘要**：
定義 MergeSite 服務從 PriceCenterSite 獨立出來的技術設計。將控制器拆分為 SiteGameController 與 GameController，移除路由 /backend 前綴，規範模型層結構與命名，並彙整新舊 API 路由對照。MergeSite 依賴 PriceCenterService 提供數據。

**關鍵業務規則**：
- 取得站台範圍日期時間賽事時，startDate 與 endDate 預設為今日，startTime 預設 00:00，endTime 預設 23:59
- 合併聯盟時，若 lid 傳入 'null'，則執行站台聯盟與站台聯盟的合併

**關鍵設計決策**：
- 控制器拆成 SiteGameController（管理 SiteLeague、SiteGame、SiteTeam）與 GameController（管理 League、Game、Team），以分類職責
- Infrastructure 層的 DataAccess 以資料源命名（例如 PriceCenterServiceProvider），強化依賴來源的清晰度
- Model 層將相關類別放在同一資料夾（如 sitegame 相關放同資料夾），DTO 為 Provider 轉換後的資料結構，專供前端使用
- 所有 API 路由移除 /backend/ 前綴，改為更簡潔的 REST 路徑（如 /leagues/{gameType}）
- 於 PriceCenterService 新增 /pricecenter/api/sitegames、/pricecenter/api/siteteams、/pricecenter/api/games 等介面，舊的 PriceCenterSite API 不再使用
- MergeSite 透過 PriceCenterServiceProvider 調用 PriceCenterService API 取得站台賽事或球隊，再轉換成 DTO 回傳前端

**影響範圍**：
- mergefrontendsite 透過 mergesite 查詢資料，此設計決策直接影響前端可用的 API 路由與回傳格式
- 舊的 PriceCenterSite API 應已不再使用

**注意事項**：
- ⚠️ 文件時間為 2024-04，需確認當前 MergeSite 實現是否完全依照此設計
- ⚠️ 使用者紀錄上傳端點（/system/logs/action）備註「需確認哪個地方用」，應人工確認呼叫方後才能安全移除或重構
- ⚠️ API response 範例中出現亂碼（如 "message":"\b"），可能為複製貼上問題，實際回應應以實作或測試為準
- ⚠️ 新舊路由對照中，部分參數命名有大小寫或拼法差異（如 SiteLID vs siteLID），實作時需遵從統一名稱（建議以新路由定義為準）
- ⚠️ 多處備註「pricecenterservice會新增對應的api, 舊有的api不使用」，代表舊 API 需確認已下線，否則可能引發並行問題
- ⚠️ 此文件主要描述 mergesite 後端設計，但因 mergefrontendsite 為其前端，相關業務規則與設計決策將直接影響前端開發

---