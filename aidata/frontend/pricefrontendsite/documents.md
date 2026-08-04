# pricefrontendsite — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 11:30
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類


### TCZB-912 [ForntEndSite] — 顯示result資料

> Confluence 頁面 ID：22544541
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=22544541)
> 摘要檔：[processed/22544541-summary.md](../../confluence/processed/22544541-summary.md)
> Confluence 最後更新：2021-07-16
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件描述 PriceFrontEndSite 的 result 資料顯示功能需求，需透過 API 取得 result 資料，並提供日期選擇、聯盟選擇與排序功能，資料需即時更新。雖然缺乏具體規格細節，但確認了此頁面需要後端 API 支援來實現篩選與排序邏輯。

**關鍵業務規則**：
- 前端需透過呼叫 API 取得 result 資料（重要性高）
- 使用者可依日期與聯盟選擇篩選顯示的 result 資料
- 須支援排序功能（具體排序欄位未定義）
- result 資料應即時更新（推測為定期輪詢或即時推送，機制未定）

**注意事項**：
- ⚠️ 文件僅有基本需求描述，缺少 API 規格、UI 佈局、排序欄位、分頁等實作細節
- ⚠️ 標題中 'ForntEndSite' 可能為拼字錯誤（應為 FrontEndSite）
- ⚠️ 前端流程圖鏈接指向另一頁面，需人工查閱以取得完整互動設計


### TCZB-2438 [SportKing] — 收藏功能

> Confluence 頁面 ID：44665096
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44665096)
> 摘要檔：[processed/44665096-summary.md](../../confluence/processed/44665096-summary.md)
> Confluence 最後更新：2023-01-18
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了 SportKing 運動網站的收藏功能需求。收藏功能採用客戶端儲存方案，將賽事 ID 保存在 Cookie 中，而非透過後端服務維護收藏狀態。收藏頁面需要根據 Cookie 中的賽事 ID 向後端查詢賽事資料，並提供顯示和刪除功能。對 AI 開發來說，這表示收藏功能是純前端邏輯，不需要新增或修改後端 API 來管理收藏狀態。

**關鍵業務規則**：
- 賽事收藏以 Cookie 為儲存載體，將賽事 ID 保存在客戶端 Cookie 中
- 收藏頁面根據 Cookie 中儲存的賽事 ID 去後端撈取對應的賽事資料進行展示
- 收藏頁面必須提供刪除已收藏賽事的功能（即從 Cookie 中移除賽事 ID）

**注意事項**：
- ⚠️ 文件最後更新於 2023-01-18，距今超過一年，需確認此需求是否仍適用或已被其他方案取代
- ⚠️ Cookie 儲存方案有容量限制（通常 4KB），若賽事 ID 數量過多可能導致儲存失敗，文件未提及上限或處理方式
- ⚠️ Cookie 儲存代表收藏資料無法跨裝置同步，需確認此為預期行為


### 前端畫面規劃

> Confluence 頁面 ID：15401857
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=15401857)
> 摘要檔：[processed/15401857-summary.md](../../confluence/processed/15401857-summary.md)
> Confluence 最後更新：2021-07-16
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件規劃 PriceCenter 前端首頁的各個區塊及功能選單，包含用戶登入/註冊、促銷、客服、賽事推薦、球種列表、中央賽事內容（即時賠率、分析預測、推薦、論壇、賽果）與廣告區域等。以 checkbox 標記各功能開發狀態，部分項目以紅字或藍字標記可能表示待定或特殊狀態。對於 AI 開發，可以了解前端所需展示的功能模組，作為後端服務整合與 API 設計的參考。

**關鍵業務規則**：
- —

**注意事項**：
- ⚠️ 文件最後更新於 2021-07-16，距今已超過兩年，前端可能已經改版（如轉換至 Nuxt3），功能狀態與規劃應已變更，需人工確認當前有效性
- ⚠️ 紅色文字標記的功能（如 Help and FAQ, Become an Expert, Subscribe Solution 等）可能代表當時未完成或需調整，藍色文字（Analysis and Prediction, Advertising）可能同樣有特殊狀態，實際完成度不明

---

## 技術設計類


### PriceFrontEndSite 完整部署流程

> Confluence 頁面 ID：21660252
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=21660252)
> 摘要檔：[processed/21660252-summary.md](../../confluence/processed/21660252-summary.md)
> Confluence 最後更新：2021-07-14
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件記錄 PriceFrontEndSite 的部署 SOP，包含 CI/CD 觸發、Linux 自動更新靜態資源腳本、Windows SSH 連線輔助，以及 nginx 反向代理與快取設定。從 AI 開發角度，可瞭解該前端如何透過 nginx 路由至 forumservice、apiservice 等後端，並使用內部 zip 下載方式管理 js/css/img 快取，有助於重現或模擬其部署環境與資源管理邏輯。

**關鍵設計決策**：
- 靜態資源（CSS, JS, 圖片）部署時不重新建構映像，而是透過 shell 腳本從內部伺服器（192.168.55.83）下載壓縮檔，解壓後放入 nginx 靜態目錄，搭配 nginx expires 30d 快取
- Nginx 的 upstream 群組採用 ip_hash 策略，確保來自同一 IP 的請求維持導向同一後端伺服器
- 前端路由中 /forumservice 與 /apiservice 仰賴 rewrite_by_lua_file 進行位址改寫，再代理至對應的 upstream（forumservice:22308, apiservice:22307）
- Windows 端的 bat 腳本僅作為 SSH 輔助提示，無法全自動更新，仍需人工登入執行 build.sh

**注意事項**：
- ⚠️ 文件包含硬編碼密碼（9uV@a9fEW$）與內部 IP，有資訊安全疑慮，需人工確認是否已遷移至安全方案
- ⚠️ 最後更新日為 2021-07-14，部署方式與內部服務位址可能已經改變，應與當前團隊確認
- ⚠️ build.sh 中靜態資源下載位址 192.168.55.83:22400 若失效，部署即失敗，需確保該服務存在且內容正確
- ⚠️ Nginx 設定中的 SSL 憑證路徑與 server_name（www.zbdigital.net）可能僅適用特定環境，直接套用其他環境可能導致憑證不符


### PriceFrontEndSit 效能測試結果

> Confluence 頁面 ID：20152503
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=20152503)
> 摘要檔：[processed/20152503-summary.md](../../confluence/processed/20152503-summary.md)
> Confluence 最後更新：2021-05-27
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件提供 PriceFrontEndSit 前端應用在 Dev 與 Production 模式下的效能測試結果，包含首頁、登入、忘記密碼、註冊、修改個人資料等頁面的記憶體占用、CPU 使用率、Lighthouse 評比與記憶體成長率數據。測試顯示 Production 模式記憶體明顯較低（如首頁 18-38 MB vs Dev 100-179 MB），WebSocket 僅首頁啟用。這些歷史基線可幫助 AI 開發時評估前端資源需求與潛在記憶體問題，但須注意數據來自 2021 年，可能已過時。

**關鍵設計決策**：
- —

**注意事項**：
- ⚠️ 文件建立於 2021-05-27，測試對象為舊版 PriceFrontEndSit（可能非目前 Nuxt3 架構），數據可能已過時，使用前需對照當前環境重新驗證
- ⚠️ 部分測試點存在不一致：Production 首頁記憶體有一次記錄從 38 MB 開始，與另一次穩定 18 MB 的測試不同，原因不明，需人工確認
- ⚠️ Dev 環境 Lighthouse Performance 分數僅 26（首頁），顯示未優化；Production 則為 75，差異顯著，但具體優化手段未在文件中說明
- ⚠️ 文件中未說明測試時的系統負載、並發用戶數等背景條件，可能影響數據代表性

---

## 歷史決策類


### 架構師問題解決及回覆

> Confluence 頁面 ID：20873517
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=20873517)
> 摘要檔：[processed/20873517-summary.md](../../confluence/processed/20873517-summary.md)
> Confluence 最後更新：2021-06-01
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件記錄了前端 pricefrontendsite 專案中 API 請求模組化實作（分類至 apis 文件夾），以及 RWD 響應式設計中 navbar/backdrop 使用 CSS 取代 v-if 判斷畫面寬度的建議。問題部分提出 userbar 的 transition 效果在畫面寬度變換時跟不上，目前採用點擊時動態添加 transition 並於 0.5 秒後移除的作法，涉及原生 DOM 操作，詢問更好做法。

**關鍵設計決策**：
- 架構師建議使用 CSS 代替 v-if 判斷來處理 navbar 和 backdrop 的顯示/隱藏，以避免 JavaScript 判斷畫面寬度
- 對於 userbar 的 transition，當前方案是點擊時透過 document.getElementById 新增 transition，並在 0.5 秒後移除，因為直接給 transition 會導致 RWD 變換寬度時動作跟不上。這是一種折衷方案，原因在於屏幕寬度變化時 transition 會造成不良視覺效果

**影響**：
- 影響 RWD 響應式設計的實作方式，特別是導航元件（navbar/backdrop）的顯示/隱藏邏輯應優先使用 CSS 而非 JavaScript
- userbar 的 transition 處理為折衷方案，若未來重構需尋找更優雅的解決方案

**注意事項**：
- ⚠️ 文件最後更新於 2021-06-01，資訊可能過時，前端實作可能已有變更
- ⚠️ 問題(1)未提供最佳解法，僅記錄了現行作法，需人工確認後續是否已有更好的解決方案

---

## 操作手冊類


### PriceFrontEndSite 完整部署流程（同技術設計類）

> Confluence 頁面 ID：21660252
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=21660252)
> 摘要檔：[processed/21660252-summary.md](../../confluence/processed/21660252-summary.md)
> Confluence 最後更新：2021-07-14
> 摘要最後同步：2026-05-26

**摘要**：
這份文件記錄 PriceFrontEndSite 的部署 SOP，包含 CI/CD 觸發、Linux 自動更新靜態資源腳本、Windows SSH 連線輔助，以及 nginx 反向代理與快取設定。

**AI 開發需要注意的部分**：
- 靜態資源部署不重新建構映像，需確保內部資源伺服器（192.168.55.83:22400）可達且內容正確
- Nginx 反向代理設定中 /forumservice 和 /apiservice 的路由規則需保持，否則前端 API 請求會失敗
- 部署腳本中包含硬編碼密碼，需改用環境變數或密鑰管理服務

---