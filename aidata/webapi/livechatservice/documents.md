# livechatservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 12:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB-25 [LivechatService]-Quick Message

> Confluence 頁面 ID：2884489
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-25+%5BLivechatService%5D-Quick+Message)
> 摘要檔：[processed/2884489-summary.md](../../confluence/processed/2884489-summary.md)
> Confluence 最後更新：2020-07-13
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義 Quick Message（罐頭訊息）與 HelloMessage 的管理規則。Quick Message 的增刪修必須根據請求中的 X-Company 限制該公司資料，且所有寫入操作需同時更新 Redis；查詢則直接從 Redis 讀取，以 GroupType 為必填參數並隱含 CompanyCode，不需要分頁。HelloMessage 每個 Company 僅有一筆，僅允許更新，新增需手動於 DB 操作。

**關鍵業務規則**：
- QuickMessage 增刪修只能依據請求 Header 中的 X-Company 對該 Company 的 QuickMessage 進行管理
- QuickMessage 增刪修必須同時更新 Redis 中的對應資料
- QuickMessage 查詢的資料來源為 Redis，查詢時需傳入 GroupType（必填）來區分回傳資料，並隱含 CompanyCode（Header），不回傳分頁，直接全撈
- HelloMessage 僅支援 update 功能，因為一個 Company 只存在一筆資料
- HelloMessage 的 Insert 需要手動進 DB 新增，不提供 API

**注意事項**：
- ⚠️ 文件最後更新於 2020-07-13，距今日久，相關實作可能已變更，需人工確認
- ⚠️ 文件依賴 Table/Redis Schema 文件（頁面 ID 2884397），但未附上實際 Schema，AI 需另外取得欄位定義

---

### TCZB-27 [LivechatService]-File upload and encry / decry

> Confluence 頁面 ID：2884491
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884491)
> 摘要檔：[processed/2884491-summary.md](../../confluence/processed/2884491-summary.md)
> Confluence 最後更新：2020-07-13
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義了 LiveChat 服務的檔案上傳功能需求：允許上傳 JPG、PNG、BMP 圖片，單檔限制 4MB，傳輸過程需加密/解密以確保安全。儲存路徑基於日期、公司和 Channel 組織，目的是防止資料洩漏與維護誤解。

**關鍵業務規則**：
- 上傳檔案必須檢查檔頭（magic bytes），僅接受 JPG、PNG、BMP 三種格式
- 單一檔案大小上限為 4MB
- 檔案在傳輸過程中必須加密，接收端需解密，以防止攔截洩漏（具體加解密方式未定義）
- 檔案儲存路徑格式：/mnt/{ImagePath}/{Date}/{Company}/{Channel}/xxxx.jpg（使用 Channel 取代 ConnectId 作為路徑節點）

**注意事項**：
- ⚠️ 加密/解密機制未具體定義（如演算法、金鑰管理），實作需人工補充
- ⚠️ 檔案名稱「xxxx.jpg」是否保留原上傳檔名或隨機生成未明確
- ⚠️ 文件最後更新於 2020-07-13，可能已過期，需確認目前規範

---

### TCZB-28 [LivechatService]-Create Channel

> Confluence 頁面 ID：2884478
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-28+%5BLivechatService%5D-Create+Channel)
> 摘要檔：[processed/2884478-summary.md](../../confluence/processed/2884478-summary.md)
> Confluence 最後更新：2020-07-10
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義建立聊天 Channel 的前置驗證與歡迎訊息流程。客戶連線前必須通過一次性 token 驗證，避免隨意進入其他 Channel；服務端生成 token 並儲存後回傳 token 和 issuetypes。連線建立時，後台自動發送可維護的歡迎訊息及用戶選擇的 issuetype。

**關鍵業務規則**：
- 建立連線前，客戶端必須提供 token 進行一次性驗證，阻止未授權進入其他 Channel
- 服務端生成 token 後，必須先儲存再回傳 client，回傳內容包含 token 和 issuetypes
- 客戶建立連線時，後台自動發送歡迎訊息（訊息內容由後台維護）
- 客戶建立連線時，必須送出選擇的 issuetype

**注意事項**：
- ⚠️ 文件最後更新於 2020-07-10，屬早期 Sprint2 產出，可能已過期或已被後續設計取代
- ⚠️ 需求 #2 未填標題，僅有說明，需人工確認 token 生成與回傳的完整流程

---

### TCZB-29 [LivechatService]-Feedback

> Confluence 頁面 ID：2884484
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-29+%5BLivechatService%5D-Feedback)
> 摘要檔：[processed/2884484-summary.md](../../confluence/processed/2884484-summary.md)
> Confluence 最後更新：2020-07-14
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義 Feedback 功能需求。對話結束後允許用戶填寫 1-10 分的滿意度評分和建議（Comment）。寫入前強制校驗：是否存在 Chat ID、Company ID，以及該公司是否擁有該 Chat ID；評分必須在 1-10 範圍內，否則放棄寫入。

**關鍵業務規則**：
- 儲存表格欄位必須包含 ChatID、Date、Score、Comment
- 寫入數據時必須校驗 Chat ID 存在，不存在則放棄寫入
- 必須校驗 Company ID 存在，不存在則放棄寫入
- 必須校驗該 Company ID 是否持有該 Chat ID，不持有則放棄寫入
- Score 必須為 1-10 之間的整數，否則放棄寫入
- 完成操作後必須通知調用方數據是否成功寫入數據庫
- 因數據量不大，不需要實現分頁查詢

**注意事項**：
- ⚠️ 文件未定義 Date 的格式（例如是否為對話結束時間，是否包含時區），需人工確認
- ⚠️ 「不需要設置Page」僅說明後端不分頁，但若後期數據量增長可能需要調整

---

### TCZB-7 [LivechatService]-SignalR Hub Sync message to redis & db

> Confluence 頁面 ID：2884476
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884476)
> 摘要檔：[processed/2884476-summary.md](../../confluence/processed/2884476-summary.md)
> Confluence 最後更新：2020-07-10
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義 SignalR Hub 將聊天訊息從 Redis 同步至 DB 的需求。包含定時作業檢查 Redis 中已結束的對話 Channel，將其備份到 DB 後清除 Redis 資料；以及當使用者或客服手動結束對話時，立即儲存訊息到 DB 並從 Redis 刪除。

**關鍵業務規則**：
- 定時作業需檢查 Redis 中所有已結束的聊天 Channel
- 對於已結束的 Channel，將資料從 Redis 備份至 DB
- 備份完成後，清除 Redis 中該 Channel 的資料
- 當 User 或 Agent 手動點選對話結束時，將該對話的 Message 資料儲存至 DB 並刪除 Redis 中的對應資料

**注意事項**：
- ⚠️ 文件中用戶交互設計部分為截圖，內容無法讀取，可能遺漏互動細節
- ⚠️ 文檔最後更新於 2020-07-10，距今較久，需確認現行系統是否仍遵循此規則

---

### TCZB-8 [LivechatService]-Manager Service API

> Confluence 頁面 ID：2884493
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-8+%5BLivechatService%5D-Manager+Service+API)
> 摘要檔：[processed/2884493-summary.md](../../confluence/processed/2884493-summary.md)
> Confluence 最後更新：2020-07-13
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義管理者 API 需求，包括對話紀錄查詢與 Feedback 查詢及分數統計。對話紀錄查詢基於 MessageLogs 結構，支援 ConnectId、AddDate（必填）、UserData、Agents 等條件，且必須隱含 CompanyCode 限制以確保公司隔離。查詢結果強制分頁，預設每頁 20 筆，最高不可超過 100 筆。

**關鍵業務規則**：
- 對話紀錄查詢功能需參考 Table/Redis Schema 中的 MessageLogs 結構
- 查詢條件包含 ConnectId、UserData、Agents，以及 CompanyCode（隱含必填，只能查詢所屬 Company 的對話紀錄）
- AddDate 為必填條件，必須提供 StartDate，可選擇性提供 EndDate；若只有 StartDate，則查詢範圍為 StartDate 當天 00:00:00 至 23:59:59
- StartDate 可僅提供年月日（無時間部分），表示查詢該日全天對話記錄
- 查詢結果必須實作分頁，預設每頁 20 筆，每頁最多不得超過 100 筆
- 需提供 Feedback 內容查詢及分數統計功能（具體規則未進一步說明，需人工確認）

**注意事項**：
- ⚠️ 文件最後更新於 2020-07-13，距今已久，需確認規則是否仍然適用
- ⚠️ 對話紀錄查詢依賴的 MessageLogs Schema 位於其他頁面（pageId=2884397），需人工查閱

---

### TCZB-93 [LivechatService]-Send to 3rd Chat platform via api - Telegram

> Confluence 頁面 ID：5341345
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-93+%5BLivechatService%5D-Send+to+3rd+Chat+platform+via+api+-+Telegram)
> 摘要檔：[processed/5341345-summary.md](../../confluence/processed/5341345-summary.md)
> Confluence 最後更新：2020-08-03
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義 LivechatService 整合 Telegram 的初期需求，目的是讓客戶能透過 Telegram 與 Agent 溝通。核心需求為：從 Telegram 讀取客戶訊息並存入 Redis，以及持續監聽 Redis 上 Agent 的訊息並發送到 Telegram。

**關鍵業務規則**：
- 客戶在 Telegram 傳送的訊息必須能被 LivechatService 接收並存入 Redis（需確認 Telegram API 是否支援服務端讀取訊息）
- Agent 回覆的訊息需寫入 Redis，再由 LivechatService 持續監聽並發送到 Telegram（需確認 Telegram API 是否支援發送訊息）
- Telegram Bot 帳號資訊需透過一個專用 API 寫入資料庫儲存

**注意事項**：
- ⚠️ 文件最後更新於 2020-08-03，距今已超過 3 年，需求可能已變更或實作方式已大幅不同
- ⚠️ 需求表格中兩項極高重要度條目都以「需要了解 telegram API 是否可行」為前提，表示撰寫當下技術可行性尚未驗證，只能視為探索性需求

---

### TCZB-98 [LivechatService] - Auto Clean disconnect / offline users

> Confluence 頁面 ID：5341341
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=5341341)
> 摘要檔：[processed/5341341-summary.md](../../confluence/processed/5341341-summary.md)
> Confluence 最後更新：2020-07-31
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
規定用戶非正常關閉頁面（如直接關機）時的處理規則：必須將相關會話數據持久化到數據庫，防止數據丟失。同時規劃了定時清理 Redis 中無活動用戶數據並同步到 DB 的功能。

**關鍵業務規則**：
- 用戶非正常關閉網頁（如不點擊關閉按鈕、直接關機）時，必須將關聯的會話信息保存到數據庫
- 需要實現定時檢測用戶無活動狀態，清空 Redis 中對應的用戶數據並存入數據庫，該能力通過 LivechatService 的 API 提供

**注意事項**：
- ⚠️ 文中提到「之後需要 User沒動靜一段時間清空Redis存到DB」，未明確具體活動超時時間或實現細節，需確認實際實現狀態
- ⚠️ 該文檔為 2020 年版本，當前系統可能已有變更

---

### TCZB-95 [LivechatService]-Send to 3rd Chat platform via api - LINE

> Confluence 頁面 ID：5341663
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-95+%5BLivechatService%5D-Send+to+3rd+Chat+platform+via+api+-+LINE)
> 摘要檔：[processed/5341663-summary.md](../../confluence/processed/5341663-summary.md)
> Confluence 最後更新：2020-08-18
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義 LivechatService 整合 LINE 即時通訊的基本需求：讓客戶可透過 LINE 與客服人員溝通。核心需求包含：(1) 服務必須能接收客戶在 LINE 傳送的訊息，並將訊息存入 Redis；(2) 服務必須能監聽 Redis 中的客服人員回覆訊息，並透過 LINE API 傳送給客戶。

**關鍵業務規則**：
- 客戶在 LINE 官方帳號中發送的訊息，必須由服務接收並寫入 Redis 暫存，供後續處理
- 服務必須持續監聽 Redis 中由客服人員發出的訊息，並即時透過 LINE API 將訊息傳送給對應的客戶

**注意事項**：
- ⚠️ 文件中兩個待確認問題皆無結論：LINE API 是否允許服務「讀取」用戶訊息、LINE API 是否允許服務「傳送」訊息
- ⚠️ 文件最後更新於 2020-08-18，距今已超過四年，LINE API 可能已發生變更

---

### LiveChat功能研究筆記

> Confluence 頁面 ID：2884101
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884101)
> 摘要檔：[processed/2884101-summary.md](../../confluence/processed/2884101-summary.md)
> Confluence 最後更新：2020-10-15
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
記錄 LiveChat 服務的需求探索與技術調研，包括前端嵌入、多租戶隔離、圖片安全、罐頭訊息自定義等需求。設計上討論了以 Redis 作為對話快取提升效能，使用 SignalR 實現即時通訊，並研究 Nginx 反向代理相容性。

**關鍵業務規則**：
- 系統必須區分不同網站（Website）的使用者，單一網站的客戶只能連接到該網站的客服，客服也只能處理所屬網站的對話（多租戶隔離）
- 歡迎訊息與罐頭語言包需支援按網站自定義
- 使用者上傳的圖片必須具備安全機制，能證明系統維護人員無法竊取

**注意事項**：
- ⚠️ 文件最後更新於 2020-10-15，內容距今已逾 4 年，技術版本與方案可能已過時
- ⚠️ 多處以「可能是解決方案」「參考」結尾，未形成最終決策，不宜直接當作實作規範

---

### LiveChat時序圖

> Confluence 頁面 ID：2884363
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884363)
> 摘要檔：[processed/2884363-summary.md](../../confluence/processed/2884363-summary.md)
> Confluence 最後更新：2020-08-12
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
以多個時序圖展示 LiveChat 服務的核心流程：建立 Channel、首次進入 Channel（含歡迎訊息與歷史訊息載入）、即時聊天（文字與圖片）、退出 Channel 以及 Telegram 整合聊天。明確各元件（www、Hub、Service、Redis、DB）的職責與訊息傳遞順序。

**關鍵業務規則**：
- 建立 Channel 前需先取得一次性 Token，Token 由 Hub 生成並儲存至 DB
- User 建立 Channel 後，Hub 自動發送歡迎訊息給 User，並透過 Service 監聽 Redis 通知 Agent 有新訊息
- Agent 首次加入 Channel 時，Hub 從 Redis 加載該 Channel 的歷史訊息回傳給 Agent
- 傳送訊息時，Hub 將訊息暫存至 Redis，再由 Hub 廣播給 User 和 Agent
- 傳送圖片時，圖片檔案由 Service 儲存至 HD（硬碟），只將圖片路徑存入 Redis 作為聊天紀錄，客戶端再依路徑向 HD 請求圖片
- 退出 Channel 時，Service 從 Redis 取出該 Channel 的完整聊天紀錄，並寫入 DB 進行持久化

**注意事項**：
- ⚠️ 文件最後更新於 2020-08-12，距今已有較長時間，部分流程可能已變更或重構
- ⚠️ 圖中使用的元件名稱（如 Hub、www、Service）與實際微服務部署名稱可能不完全對應

---

## 技術設計類


### TCZB-6 [LivechatService]-Build Client JS & SignalR Hub

> Confluence 頁面 ID：2884455
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884455)
> 摘要檔：[processed/2884455-summary.md](../../confluence/processed/2884455-summary.md)
> Confluence 最後更新：2020-07-10
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義 LiveChat 服務的客戶端 JS 與 SignalR Hub 設計。客戶端須為純 JS、區分前台（一般用戶）與後台（Agent），具備連線、傳送、接收訊息功能。後端 SignalR Hub 需區分不同公司的連線通道，並將訊息寫入 Redis 以保存歷史訊息。

**關鍵設計決策**：
- 選擇 SignalR 作為即時通訊框架，利用其前端簡化方法與後端 Hub API 控管連線
- 客戶端設計為純 JS，降低第三方整合門檻
- 使用 Redis 作為訊息暫存方案，解決 SignalR 不保存歷史訊息的限制

**影響範圍**：
- SignalR Hub 需能區分不同公司，發送訊息到對應公司與使用者，避免跨公司訊息流出
- SignalR Hub 必須將訊息寫入 Redis，使後加入使用者可取得歷史訊息

---

### TCZB-90 [LivechatService] - More User Info For agent

> Confluence 頁面 ID：5341330
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-90+%5BLivechatService%5D+-+More+User+Info+For+agent)
> 摘要檔：[processed/5341330-summary.md](../../confluence/processed/5341330-summary.md)
> Confluence 最後更新：2020-07-31
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義為客服 Agent 提供更多使用者資訊的技術需求。主要目標是在使用者進入線上客服時，自動收集並記錄 IP、地理位置、裝置、作業系統、瀏覽器和服務來源等六項資訊。

**關鍵設計決策**：
- 採用 UAParser Nuget 作為 User-Agent 解析工具，用於擷取裝置、作業系統和瀏覽器資訊
- UserInfo 的儲存結構參考既有的 MessageLogs Table 和 Redis 中的 LiveChat_{CompanyCode} Schema，表示是對現有結構的擴充而非新建
- 需要記錄的六個欄位：IP、Location、Device、OS、Browser、Service

**影響範圍**：
- Location 的來源和格式需人工確認（推測可能是透過 IP lookup 取得）
- Service 欄位推測為記錄使用者來自哪個產品服務（如 sports、lottery），具體枚舉值需人工確認

---

### TCZB-96 [LivechatService]-Send to 3rd Chat platform via api - Integration

> Confluence 頁面 ID：5341332
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-96+%5BLivechatService%5D-Send+to+3rd+Chat+platform+via+api+-+Integration)
> 摘要檔：[processed/5341332-summary.md](../../confluence/processed/5341332-summary.md)
> Confluence 最後更新：2020-08-03
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
描述在 LivechatService 中整合第三方聊天平台（如 Telegram）的設計。透過 Redis 讀寫聊天內容，第三方平台在寫入 Redis 後自動發送訊息。Channel UI 需顯示客戶的 IP、位置、裝置等資訊，並區分不同服務的聊天室。

**關鍵設計決策**：
- 使用 Redis 作為第三方聊天平台資料的中介儲存，寫入 Redis 後觸發發送
- 對於非 SignalR 的聊天室進行分類並另外處理更新機制
- 採用 timer 定時更新 Channel UI 資料

**影響範圍**：
- Channel 聊天室的新訊息標題必須包含 IP、location、Device、OS、Browser、Service 等客戶資訊
- 切換服務時必須中斷前一個 AJAX 調用或 SignalR 連線

---

### TCZB-99 [LivechatService] - Client JS包裝整合

> Confluence 頁面 ID：5341360
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=5341360)
> 摘要檔：[processed/5341360-summary.md](../../confluence/processed/5341360-summary.md)
> Confluence 最後更新：2020-07-30
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
目標是將現有在 Client.cshtml 頁面中的 JavaScript 代碼分離並包裝成獨立 JS 檔案，以便供其他團隊及 Agent 重複使用。這項工作屬於技術實作層面的前端模組化，不涉及業務邏輯變更。

**關鍵設計決策**：
- 決定將客戶端 JS 代碼從頁面內聯的方式改為獨立 JS 檔案，提高程式碼可維護性並讓外部團隊能直接引用，降低耦合
- 包裝過程需了解 JS 模組化機制，確保原有功能不受影響（具體實作細節未在文件中描述）

**影響範圍**：
- livechatservice 的客戶端互動邏輯被封裝為外部 JS 模組，有助於整合時的依賴分析與介面設計

---

### Table/Redis Schema

> Confluence 頁面 ID：2884397
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884397)
> 摘要檔：[processed/2884397-summary.md](../../confluence/processed/2884397-summary.md)
> Confluence 最後更新：2020-07-30
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義 LiveChat 服務的資料庫表格結構（Tokens、MessageLogs、Logs、QuickMessages、HelloMessages、Feedbacks、IssueType）及 Redis 鍵值設計（LiveChat_{CompanyCode}、LiveChat_Channel_{ConnectID} 等），說明每個欄位的資料型態與用途。

**關鍵設計決策**：
- 連線與使用者會話以 Tokens 表管理，以 HashKey 為主鍵，儲存 CompanyCode、AddTime、Enabled、UserData、UsedTime、ConnectID、IP，其中 CompanyCode 來自 Gateway Header X-Company
- 訊息記錄 MessageLogs 關聯 Token 的 HashKey 與 ConnectID，記錄內容、使用者資料、接聽客服 Agents（多人以逗號分隔）、客戶端環境資訊
- 快速回覆 QuickMessages 依 CompanyCode 與 GroupType（Common/Payment/Application/CS）分類，支援啟用與停用
- 公司迎賓訊息 HelloMessages 每個 CompanyCode 僅有一筆（CompanyCode 為 PK）
- 使用者回饋 Feedbacks 關聯 ConnectID（SignalRID），評分範圍 1~10
- Redis 設計使用 Set 集合與 Char 字串快取資料，但未定義 TTL

**影響範圍**：
- 所有涉及資料存取的實作都需遵循此 Schema 設計
- Redis 鍵的過期策略、儲存格式細節未說明，需人工確認現有快取機制
- QuickMessages.GroupType 使用 HardCode，若需擴充分類需修改程式碼

---

### APIs List

> Confluence 頁面 ID：2884399
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/APIs+List)
> 摘要檔：[processed/2884399-summary.md](../../confluence/processed/2884399-summary.md)
> Confluence 最後更新：2020-08-04
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
LiveChat 服務的 API 清單，涵蓋反饋寫入、SignalR 即時訊息與頻道操作、檔案上傳、快速訊息與歡迎訊息的 CRUD 及快取、訊息日誌查詢、反饋查詢統計，以及第三方整合。

**關鍵設計決策**：
- 快速訊息快取端點 (message/cache/{group}) 僅返回 enabled=1 的資料

**影響範圍**：
- 所有對外提供的 API 端點，開發時需遵循此清單定義
- 部分 API 可能已變更或廢棄，需與當前實作比對確認

---

### 時序圖 (LineBotService)

> Confluence 頁面 ID：5341645
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=5341645)
> 摘要檔：[processed/5341645-summary.md](../../confluence/processed/5341645-summary.md)
> Confluence 最後更新：2020-08-26
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
為 LiveChat Service 在 Line 平台上的訊息傳遞時序圖，展示了 User 與 Agent 透過 Line、LineProxy、LiveChatService、TranslateService 與 Redis 進行訊息收發的完整流程。

**關鍵設計決策**：
- 使用 Redis 作為訊息暫存與佇列，User 與 Agent 的訊息皆透過 Redis 進行傳遞
- LineProxy 採用輪詢機制持續監聽 Redis 中是否有 User 的新訊息，而非被動推送
- 翻譯功能由 TranslateService 獨立提供，LiveChatService 負責協調訊息流與翻譯請求
- Agent 端採用網頁（www）持續監聽 Redis 新訊息，實現即時通訊

**影響範圍**：
- 涉及 livechatservice 與 translateservice 的協作，以及 Line 平台的整合

---

### TCZB-92 [LivechatService] - Call TranslateService to realtime translate message

> Confluence 頁面 ID：5341665
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-92+%5BLivechatService%5D+-+Call+TranslateService+to+realtime+translate+message)
> 摘要檔：[processed/5341665-summary.md](../../confluence/processed/5341665-summary.md)
> Confluence 最後更新：2020-08-18
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
描述 LivechatService 整合 TranslateService 的即時訊息翻譯功能需求。核心目標是讓 Agent（客服）和 User（終端用戶）都能看到翻譯後的訊息。Agent 透過前端網頁查看翻譯，User 則透過 Line Bot 接收翻譯訊息。

**關鍵設計決策**：
- 選擇使用獨立的 TranslateService API 處理翻譯，而非在 LivechatService 內部實作翻譯邏輯，達到關注點分離
- 訊息翻譯採用即時（realtime）方式進行，而非批次處理，以確保客服對話的流暢性
- 提供兩種翻譯訊息呈現管道：前端網頁（給 Agent）和 Line Bot（給 User），滿足不同使用場景

**影響範圍**：
- 翻譯功能需依賴 TranslateService API 來實現
- 「需了解能否取得用戶端的語言」為待確認問題，文件中未記錄最終決策結果

---

### TCZB-826 [LiveChartService]-優化Service

> Confluence 頁面 ID：20873242
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=20873242)
> 摘要檔：[processed/20873242-summary.md](../../confluence/processed/20873242-summary.md)
> Confluence 最後更新：2021-06-04
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
記錄 LiveChartService 的優化任務清單，包含修復 MessageLogs 功能（如資料存取、換頁、預設顯示）、修正 Client 斷線後無法回到原先 Channel 的問題（透過 Client Finger 建立 Channel）、將 Client 端功能封裝成 JS、重新設計 UI，以及簡化 Token 驗證方式。

**關鍵設計決策**：
- 修正 Client 斷線重連無法回到原先 Channel 的問題：建立 Channel 時改用 Client Finger 作為 ID，確保重連時能定位至同一 Channel
- Token 驗證方式簡化：不再需要複雜的 Token 檢查，只需確認請求來自同一個程式即可
- Feedbacks 功能明確決定不修復
- MessageLogs 修復範圍包括：資料存取、換頁功能、畫面預設顯示 Log、以及 Messages 部分調整

**影響範圍**：
- 這些優化決策直接影響 Client 端連線機制和 Token 驗證邏輯的實作方式

---

### TCZB-939 [GameLiveService] - GameLive

> Confluence 頁面 ID：23429182
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-939++%5BGameLiveService%5D+-+GameLive)
> 摘要檔：[processed/23429182-summary.md](../../confluence/processed/23429182-summary.md)
> Confluence 最後更新：2021-07-23
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
定義賽事直播即時聊天室（LiveChat）的技術設計，包括 SignalR Hub 中央控制、REST API（頻道新增、編輯、開關、刪除、自動管理等）與 Invoke Function（加入/退出頻道、發送訊息、心跳等）。

**關鍵設計決策**：
- 採用 SignalR 為即時通訊核心，透過 Hub 管理頻道參與、訊息傳遞與人數通知
- 頻道啟用狀態由 Enabled (int) 與直播訊號 URL 決定，API 提供「已開啟且有直播訊號的頻道」查詢
- 提供自動管理頻道 (GET autocontrolchannel) 端點，推測由後台依賽事排程自動開關頻道
- 心跳機制用於維持連線並清除過時心跳的連線 (DELETE oldheartbeat)，確保資源釋放
- API 支援批次操作（multiple）以減少請求次數，提高效率

**影響範圍**：
- 提供完整的 API 合約與事件模型，可用於實作前後端互動、快取管理、信號直播頻道狀態控制
- DateTime 回傳順序有特別標示紅色，表示順序有要求，但未說明排序規則

---

### Client.js 說明文件

> Confluence 頁面 ID：20873635
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=20873635)
> 摘要檔：[processed/20873635-summary.md](../../confluence/processed/20873635-summary.md)
> Confluence 最後更新：2021-06-04
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
說明 Client.js 函式庫的使用方式，用於與 Hub 頻道服務建立連線、傳送訊息/圖片，以及監聽頻道事件。文中列出 ConnectionChannel、SendMessages、SendImg、QuitChannel 四個方法與對應的監聽事件。

**關鍵設計決策**：
- API '/api/v1/feedback' 回傳值 -1 代表 connectid 不存在，需確認 connectid 的來源與生命週期

**影響範圍**：
- 提供即時通訊客戶端的介面設計與整合方式
- Confidence 為 medium，文件最後更新於 2021-06-04，資訊可能已過時

---

## 歷史決策類


### LiveChat功能研究筆記

> Confluence 頁面 ID：2884101
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=2884101)
> 摘要檔：[processed/2884101-summary.md](../../confluence/processed/2884101-summary.md)
> Confluence 最後更新：2020-10-15
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**決策背景**：
2020 年進行 LiveChat 服務的技術調研，探索前端嵌入、多租戶隔離、圖片安全、罐頭訊息自定義等需求，以及各種技術方案的可行性。

**決策結論**：
- 為確保對話效能，採用 Redis 作為中介快取：寫入 DB，讀取從 Redis，定時將對話內容回寫 DB
- 考慮使用 SignalR 實現即時通訊，並調研其跨域、Nginx 反向代理支持、圖片上傳等
- 研究 Google Dialogflow、LINE Bot、WeChat Bot 等聊天機器人整合方案

**影響**：
- 這些早期技術選型奠定了整個 LiveChat 服務的架構基礎
- 多處以「可能是解決方案」「參考」結尾，未形成最終決策，不宜直接當作實作規範

---

## 操作手冊類


### Telegram Bot 操作手冊

> Confluence 頁面 ID：7110665
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=7110665)
> 摘要檔：[processed/7110665-summary.md](../../confluence/processed/7110665-summary.md)
> Confluence 最後更新：2021-05-31
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
說明如何在 Telegram 上透過 BotFather 建立新的 Bot，取得 API Token 與 BotToken 後，再到內部管理頁面將 APIToken、BotToken、BotName 儲存至資料庫，以便 LiveChat 服務整合 Telegram Bot 功能。

**AI 開發需要注意的部分**：
- Telegram Bot 的註冊流程與必要參數，有助於實作 LiveChat 服務與 Telegram 的對接
- 操作步驟可能與現行系統不一致，需人工確認管理頁面是否已變更
- 文中並未說明 APIToken 與 BotToken 的差異，以及何處產生 APIToken，可能需要額外釐清

---

### Line Bot 操作手冊

> Confluence 頁面 ID：7110691
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=7110691)
> 摘要檔：[processed/7110691-summary.md](../../confluence/processed/7110691-summary.md)
> Confluence 最後更新：2020-08-27
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
記錄如何在 LINE 官方後台申請帳號、啟用 Messaging API，並取得 Channel Secret、Bot basic ID、Channel access token 等必要金鑰，最後設定 Webhook URL 指向 ZB 的 livechatservice 接收端點。

**AI 開發需要注意的部分**：
- LINE Bot 整合所需的配置參數與流程，對理解和實作 LINE 整合有幫助
- 文件為 2020 年操作指引，LINE 後台介面可能已大幅變動，操作流程僅供參考
- 步驟 11 隱私權政策及服務條款「目前沒有先跳過」，為待補項目

---

### LiveChat使用

> Confluence 頁面 ID：20152365
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=20152365)
> 摘要檔：[processed/20152365-summary.md](../../confluence/processed/20152365-summary.md)
> Confluence 最後更新：2021-05-20
> 摘要最後同步：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
說明 LiveChat 服務的前台與後台使用方式：前台透過 WebSocket 連線至指定伺服器並攜帶 XAuth 認證，可參考 Demo 網頁自己設計聊天界面；後台提供基本對話、罐頭語言包、檔案上傳、翻譯、歡迎訊息、罐頭語言包維護、對話紀錄查詢及 Telegram 機器人設定等功能。

**AI 開發需要注意的部分**：
- 前端必須建立 WebSocket 連線至 livechat-pre.zbdigital.net，並於連線時附帶 XAuth 參數
- 後台可設定 Telegram 機器人，實現透過 Telegram 與使用者進行對話
- 前端設計指南僅提示參考 Demo 網頁原始碼，無詳細 API 規格，開發時須自行拆解訊息格式
- 文件僅提供 PRE 環境網址與測試用 XAuth Token，正式環境需更換，必須人工確認