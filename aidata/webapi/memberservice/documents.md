# memberservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：{yyyy-MM-dd HH:mm}
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---


## 業務規範類


### TCZB-4041 [MemberService] - 新運彩會員系統 / 球王討論區黑名單

> Confluence 頁面 ID：79466160, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79466160)
> 摘要檔：[processed/79466160-summary.md](../../confluence/processed/79466160-summary.md)
> Confluence 最後更新：2025-12-10, 摘要最後同步：2026-05-27

**摘要**：
本文件定義了新運彩會員系統的資料庫設計（Cassandra：會員、錢包、交易紀錄、站內信記錄、VIP訂閱；Redis：個人站內信）以及 MemberService 的 RESTful API，涵蓋會員註冊、登入、黑名單管理、訂閱記錄、密碼更新、大頭貼上傳等功能。這是目前最權威且最新的會員系統規範。快取策略為 Redis 快取會員資料，可透過 cache 參數切換資料來源。

**關鍵業務規則**：
- 會員註冊：account 長度 6-20 碼，只允許英數字及 -_\./ 五種符號；password 長度 8-20 碼；username 長度不超過 10 且不得為空。
- 會員註冊：phone 必須為 10 碼數字，且一個手機號碼只能綁定一個帳號，不可重複。
- 會員註冊：contact_info 必須包含 line、wechat、whatsapp 至少一種通訊軟體。
- 會員註冊：account 和 phone 皆不可與現有用戶重複。
- 會員狀態碼：0=禁止使用, 1=正常, 2=手機尚未驗證。
- 黑名單新增/移除：request body 中 black_account 陣列即使有多個元素，也只處理第一個帳號；不可把自己加入黑名單。
- 取得會員基本資訊時，password 欄位永遠回傳 null，不可洩漏。
- 更新密碼：forgetPassword=true 時不需要提供舊密碼；false（預設）時必須提供 password 以驗證舊密碼。
- VIP 訂閱：subtime 和 subendtime 格式為 yyyy-MM-dd HH:mm:ss，autosub 預設 false。

**注意事項**：
- ⚠️ phone 欄位在資料表定義為 int 型態，但手機號碼範例為 '0912345678'，包含前導零且非整數，可能設計有誤，需人工確認應為 text。
- ⚠️ 黑名單操作只取 black_account 陣列的第一個元素，其餘忽略，此行為需明確告知使用者或前端，避免混淆。

---

### TCZB-3844 [MemberService] - 至尊球王系統

> Confluence 頁面 ID：79463242, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463242)
> 摘要檔：[processed/79463242-summary.md](../../confluence/processed/79463242-summary.md)
> Confluence 最後更新：2025-10-20, 摘要最後同步：2026-05-27

**摘要**：
本文件定義至尊球王服務的完整技術設計，包括 Cassandra 資料表 (supreme_cycles、supreme_winners、supreme_records)、REST API 規格、時序圖與加權計分規則。系統可依球種/聯盟設定週期、權重與彩池，收集各類玩家活動資料，結算後產生至尊球王獲得者。此功能與會員積分及排名密切相關。

**關鍵業務規則**：
- 新增週期時，cid 必須是目前已存在週期中最大的 cid 加 1，且不可與既有 cid 重複。
- 五項權重必須各自大於 0 且小於 1，總和必須為 1。
- 新增週期的 starttime 必須大於最新一個週期的 endtime；endtime 必須大於 starttime。
- 更新週期時，若該週期已結算 (settlement == 1)，則不得更新 starttime、endtime 或權重。
- ⚠️ 更新 settlement 欄位時，若欲設為 1，規則描述可能筆誤（『endtime小於現在的時間，settlement值不可為1』），需人工確認正確邏輯。
- 新增獲得者時，若各項原始值或分數未帶值，預設為 0。

**注意事項**：
- ⚠️ 「發文被按讚數與留言數」的合併計算方式未明確定義，需人工確認。
- ⚠️ supreme_cycles 的 bid (彩池 id) 欄位標注為未確定。

---

### TCZB-3780 [MemberService] - 賽事會員水桶系統

> Confluence 頁面 ID：76547237, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76547237)
> 摘要檔：[processed/76547237-summary.md](../../confluence/processed/76547237-summary.md)
> Confluence 最後更新：2025-06-12, 摘要最後同步：2026-05-27

**摘要**：
本文件定義會員禁言（水桶）功能的技術實作：使用 Cassandra 儲存 ban 紀錄、Redis 作為快取，每日 00:00 自動任務更新過期狀態並清除快取，解 ban 後不留記錄。提供完整的 REST API（新增、查詢、更新、刪除 ban 單）。

**關鍵業務規則**：
- 新增 ban 單時，endTime 必須大於今日。
- 同一會員（authKey）最多只能有一筆 active ban 紀錄。
- 每日 00:00 系統自動檢查，將已到期的 ban 單從 Redis 刪除，並更改 Cassandra 中對應的狀態。
- 解 ban 後不留任何紀錄（依 2025-06-11 Ruei 指示）。

**注意事項**：
- ⚠️ 「解 ban 之後不留紀錄」與「更改 status 狀態」可能存在矛盾，需人工確認最終以何種方式實作（更改狀態會留下記錄，直接刪除則不留）。
- ⚠️ Cassandra 表格 gameusers_banned 缺少 status 欄位，需確認實際 schema。

---

### MemberService Msg Code

> Confluence 頁面 ID：18645310, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/MemberService+Msg+Code)
> 摘要檔：[processed/18645310-summary.md](../../confluence/processed/18645310-summary.md)
> Confluence 最後更新：2021-11-25, 摘要最後同步：2026-05-26

**摘要**：
這份文件定義了 MemberService API 在各個業務流程（註冊、登入、忘記/更改密碼、修改暱稱）中回傳的狀態碼與對應訊息。開發者能透過這些代碼快速判斷請求結果與錯誤原因。文件也標記了部分已停用的代碼（如 10402 暱稱重複），有助於避免使用過時的錯誤處理邏輯。

**關鍵業務規則**：
- 註冊時若 Email 已存在，回傳 10102 'Email已註冊'，禁止重複註冊。
- 登入時檢查帳號狀態：未開通回傳 10206 '帳號尚未開通'，已凍結回傳 10207 '帳號已凍結'。
- 忘記密碼流程中，信箱不存在(10302)、未開通(10303)、已凍結(10304)都應回傳對應錯誤。
- 修改暱稱重複檢查(10402 '暱稱重複')已停用，表示目前系統不再驗證暱稱唯一性。

**注意事項**：
- ⚠️ 此文件定義的錯誤碼（10xxx）與 TCZB-4041 新運彩會員系統等新文件中定義的狀態碼（Code:10200）格式不同，需確認不同服務之間的錯誤碼對應關係。
- ⚠️ 文件最後更新於 2021-11-25，部分代碼可能已經新增或調整。

---

### Msg Code To UI

> Confluence 頁面 ID：18645839, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/Msg+Code+To+UI)
> 摘要檔：[processed/18645839-summary.md](../../confluence/processed/18645839-summary.md)
> Confluence 最後更新：2021-05-14, 摘要最後同步：2026-05-26

**摘要**：
定義了 MemberService 錯誤碼、.Net 中間層轉換碼及對應的 UI 提示訊息，涵蓋註冊、登入、忘記/更改密碼、修改暱稱等流程。這份文件可用於理解前後端錯誤碼的映射關係，確保會員服務 API 的回傳內容與前端能正確串接。

**關鍵業務規則**：
- 成功：MemberService 10000 -> UI code 10000 (Success)。
- 登入成功：MemberService 10200 -> UI code 10200。
- 部分 UI code（如 10104 暱稱格式錯誤、10105 帳號驗證錯誤）缺少對應的 MemberService Code，可能由 .Net 層直接產生。

**注意事項**：
- ⚠️ 此文件基於舊的 .Net 中介層架構，與目前可能使用的 PriceCenterSite 或其他 Gateway 的錯誤處理方式可能不同。需人工確認當前架構下的錯誤碼轉換規則。

---

### 功能差異

> Confluence 頁面 ID：38011847, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=38011847)
> 摘要檔：[processed/38011847-summary.md](../../confluence/processed/38011847-summary.md)
> Confluence 最後更新：2022-07-26, 摘要最後同步：2026-05-26

**摘要**：
本文件定義股票策略網站（非賽事）中，一般會員、正式會員、高級會員在選股策略、券商買賣超、自選股、回測系統、訊息推播及多設備登入的功能限制。雖然這是為非賽事的業務定義的，但其中的會員分級和控制模式可作為理解會員系統設計的參考。

**關鍵業務規則**：
- 多設備登入：高級會員無限制；正式會員兩部；一般會員僅允許一部。
- 不同會員等級對於功能使用次數、日期範圍、可用的分析工具等有精細的限制。
- 股票訊息推播：簡訊通知僅高級會員可用；其他會員只能使用 Email 與 Telegram 通知。

**注意事項**：
- ⚠️ 這些規則適用於股票策略網站，與賽事相關的會員系統規則可能不同，請勿直接套用，僅供參考。

---

### [MemberService/PriceCenterSite] - 第三方合作Partner登入驗證機制

> Confluence 頁面 ID：55575422, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55575422)
> 摘要檔：[processed/55575422-summary.md](../../confluence/processed/55575422-summary.md)
> Confluence 最後更新：2023-11-20, 摘要最後同步：2026-05-27

**摘要**：
本文件定義了第三方合作夥伴（Partner）登入驗證的完整業務規則，包含四種帳號類型（站台Email、Partner升級VIP、社群登入、純Partner）的判別邏輯與登入流程。核心規則是透過 account 前綴（E/P/G/L/D）區分使用者類型，並說明 Partner 升級 VIP 時必須驗證 Email 唯一性與密碼設置。

**關鍵業務規則**：
- 帳號類型由 account 欄位前綴區分：站台Email登入為 E 開頭且 site 為空；Partner 升級 VIP 為 P 開頭且 site、siteId、Email、密碼皆不為空；社群登入（Gmail/Line/Dcard）為 G/L/D 開頭且密碼為空；純 Partner 登入為 P 開頭且密碼和 Email 皆為空。
- Partner 升級 VIP 時必須驗證 Email 唯一性，若 Email 已存在於系統中則要求使用者重新輸入，改用正式登入方式。
- 註冊時不允許重複 Email，包含 Gmail、Line、Dcard 註冊也需檢查 Email 唯一性。
- thirdparties 資料表的 enable 欄位控制第三方站台啟用狀態：0 為停用、1 為啟用。

**注意事項**：
- ⚠️ 文件中「3rd Partner 升級VIP後改用Email登入」與「3rd Partner 登入」兩種類型皆為 P 開頭但驗證方式不同，容易混淆。

---

## 技術設計類


### 新運彩(金葡京) Member DB Tables

> Confluence 頁面 ID：79468184, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79468184)
> 摘要檔：[processed/79468184-summary.md](../../confluence/processed/79468184-summary.md)
> Confluence 最後更新：2026-04-30, 摘要最後同步：2026-05-26

**摘要**：
這份文件定義了新運彩（金葡京）會員系統的資料庫表格，這是當前最新、最權威的會員系統錢包相關 DB Schema。包含 MySQL 中的 CoinWallet 錢包表與 CoinWallet_Transactions 交易紀錄表，以及 Cassandra 中的 newlottery_users 使用者表，並詳細定義了交易類型代碼（T_Type）及其對應的 JSON 格式 T_Detail 內容。對於開發錢包、交易相關功能至關重要。

**關鍵設計決策**：
- 錢包與交易紀錄採用 MySQL 儲存，以確保強交易一致性與關聯查詢。
- 使用者基本資料採用 Cassandra，因其適合大量寫入與水平擴展。
- T_Detail 以 JSON 字串形式儲存可變結構的交易明細，避免頻繁修改 schema。

**影響範圍**：
- 任何與會員錢包餘額、交易紀錄、代幣相關的功能開發都必須參考此文件。

**注意事項**：
- ⚠️ T_Type=8（VIP購買）為 2026-04-21 新增，文件未提供對應的 T_Detail 範例，實現時需人工確認格式。
- ⚠️ T_Type=6（抽成獲利）格式標注為「暫定」。

---

### SportKing DB Table

> Confluence 頁面 ID：18645111, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/SportKing+DB+Table)
> 摘要檔：[processed/18645111-summary.md](../../confluence/processed/18645111-summary.md)
> Confluence 最後更新：2023-01-18, 摘要最後同步：2026-05-26

**摘要**：
此文件定義了早期的 SportKing 會員系統的資料庫表格結構，使用 Cassandra。其中關於帳號（account）與設備指紋（finger）的雙向關聯（fingerlogs/accountlogs）、所有日誌類表格的按月分表策略等設計，是理解會員認證和設備關聯的關鍵。

**關鍵設計決策**：
- 帳號（account）與設備指紋（finger）之間透過 fingerlogs 和 accountlogs 兩張表建立雙向關聯，兩表均以 map<text,text> 記錄 {關聯對象, 建立時間} 的鍵值對。
- 所有日誌類表格採按月分表策略，表名格式為 {表名}_{YYYYMM}。

**影響範圍**：
- 此表格結構是早期設計的核心，但在 新運彩(金葡京) Member DB Tables 等新架構出現後，需確認哪些部分仍在使用。

**注意事項**：
- ⚠️ 文件最後更新於 2023-01-18，表格結構可能已有變更。需確認此 Schema 與新運彩會員系統的關聯，或是否已被完全取代。

---

### TCZB-3654 [MemberService] - 球王Z幣系統

> Confluence 頁面 ID：55584491, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55584491)
> 摘要檔：[processed/55584491-summary.md](../../confluence/processed/55584491-summary.md)
> Confluence 最後更新：2026-04-17, 摘要最後同步：2026-05-27

**摘要**：
本文件規範球王會員 Z 幣錢包系統的 API 與資料模型。提供 5 支 API：批次/單一新增交易紀錄、查詢會員餘額、查詢交易紀錄（支援日期範圍，預設當日，且限制 90 天內資料）。DB 使用 MySQL，快取用 Redis，新增交易時一併更新錢包餘額。此文件提供的 API 設計和資料模型可作為新運彩錢包功能的參考。

**關鍵設計決策**：
- 持久層使用 MySQL，快取使用 Redis。
- 新增交易紀錄時，同時更新錢包表中的 Balance 與 LastUpdateTime。
- 交易紀錄查詢僅提供 90 天內資料；API #4 若未指定日期區間，預設查詢當天。
- TypeInfo 以序列化 JSON 字串儲存，不同 Type 對應不同 JSON 結構。

**影響範圍**：
- ⚠️ 此為球王 Z 幣系統的設計，與新運彩的錢包系統（新運彩(金葡京) Member DB Tables）是獨立的。開發需根據業務需求選擇正確的錢包系統。

---

### TCZB-4041 [MemberService] - 新運彩會員系統 / 球王討論區黑名單 (技術部分)

> Confluence 頁面 ID：79466160, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79466160)
> 摘要檔：[processed/79466160-summary.md](../../confluence/processed/79466160-summary.md)
> Confluence 最後更新：2025-12-10, 摘要最後同步：2026-05-27

**關鍵設計決策**：
- 採用 Cassandra 作為主要儲存，Redis 作為會員資料快取與個人站內信儲存。
- 會員資料表以 authKey 為 partition key，對外使用 id（開頭 N 表示一般會員）作為站台識別碼，分離內部與外部標識。
- 錢包拆分為一般錢包（newlotteryusers_wallet）與錦標賽錢包（newlotteryusers_tournamentwallet）兩張表，交易紀錄獨立一張表。
- 黑名單限制單次只能操作一個帳號；儲存時使用 authKey，對外回應轉換為 account 等可讀資訊。
- 站內信採用雙層設計：所有信件記錄存於 Cassandra，個人信件存於 Redis (key={authKey}_notification)。
- 會員註冊 token 生成與驗證透過 ValidateType 區分場景（註冊驗證、忘記密碼），令牌由系統生成。

---

### TCZB-2712 [MemberService] - 新增SportKing機器人會員

> Confluence 頁面 ID：47220842, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47220842)
> 摘要檔：[processed/47220842-summary.md](../../confluence/processed/47220842-summary.md)
> Confluence 最後更新：2023-05-09, 摘要最後同步：2026-05-27

**摘要**：
此文件定義如何在 MemberService 中建立機器人會員帳號。機器人帳號的生成規則為：Email 經過 hash 後作為帳號，帳號字首固定為 'E'；再將帳號 hash 後得到 authkey。這對於自動化測試或批量帳號創建至關重要。

**關鍵設計決策**：
- 使用 Email hash 作為帳號，字首固定 'E' 以區分機器人帳號。
- authkey 由帳號再次 hash 生成。

**注意事項**：
- ⚠️ 文件未指定 hash 演算法（如 SHA256, MD5 等）以及 Email 是否需標準化（如轉小寫），實作時需人工確認。

---

### TCZB-3467 [MemberService] - Apple第三方註冊登入

> Confluence 頁面 ID：55581387, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55581387)
> 摘要檔：[processed/55581387-summary.md](../../confluence/processed/55581387-summary.md)
> Confluence 最後更新：2024-10-08, 摘要最後同步：2026-05-27

**摘要**：
因 Apple SDK 限制，使用者 email 僅在首次授權時提供，故設計 appleinfos_game 資料表儲存 Apple ID 與 email 的對應關係，以解決後續登入時 email 缺失的問題。此設計體現了因第三方限制而產生的關鍵適配方案。

**關鍵設計決策**：
- 採用獨立資料表（appleinfos_game）儲存 Apple 帳號資訊，而非直接修改會員主表。
- 重複使用現有的第三方登入 API 端點（/game/user/login/site），僅透過 Site=apple 參數區分。

---

### TCZB-2799 [MemberService] - 最多追蹤賽事會員API

> Confluence 頁面 ID：47222052, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47222052)
> 摘要檔：[processed/47222052-summary.md](../../confluence/processed/47222052-summary.md)
> Confluence 最後更新：2023-06-21, 摘要最後同步：2026-05-27

**摘要**：
這個功能透過定時任務 (xxl-job) 每小時生成「最多追蹤賽事會員」的排行榜資料存入 Redis，並提供 API 查詢。這是一個典型的用於解決高效能查詢排行榜場景的設計模式。

**關鍵設計決策**：
- 使用 xxl-job 每小時定時生成資料，寫入 Redis，以兼顧資料新鮮度與系統負載。
- 資料存放於 Redis 而不使用資料庫，以提高前端查詢效能。

---

## 歷史決策類


### [MemberService/PriceCenterSite] - 第三方合作Partner登入驗證機制

> (內容同上方的業務規範類)

**決策背景**：
為了支援第三方合作夥伴（Partner）快速接入並使用體育賽事服務，需要提供一種無需複雜註冊流程的登入機制，同時又要為其預留升級為正式會員（VIP）的路徑。

**決策結論**：
採用 account 欄位前綴（E/P/G/L/D）的方式來區分不同類型的帳號，實現了不同登入和身份驗證邏輯的統一處理。純 Partner 登入的 account 由 site+siteId hash 產生，authKey 再由 account hash 產生。

**影響**：
- 帳號前綴的規則成為判斷會員類型和權限的核心邏輯之一。
- 所有涉及登入、註冊和會員資訊查詢的服務都需要能正確處理這些不同前綴的帳號。

---

### TCZB-2799 [MemberService] - 最多追蹤賽事會員API

> (內容同上方的技術設計類)

**決策背景**：
為了應對前端高頻率、高效能的熱門會員排行榜查詢需求，同時避免對主資料庫造成壓力。

**決策結論**：
採用定時任務（xxl-job）預先計算並將結果寫入 Redis，前端查詢直接讀取快取。同時將郵件發送等非核心功能從 MemberService 抽離至 PriceCenterSite 服務。

**影響**：
- 排行榜資料並非絕對即時，有至多一小時的延遲。
- 郵件發送的職責歸屬於 PriceCenterSite，MemberService 不再直接處理。

---

### TCZB-3048 [球王] - 第三方站台登入

> Confluence 頁面 ID：55575490, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55575490)
> 摘要檔：[processed/55575490-summary.md](../../confluence/processed/55575490-summary.md)
> Confluence 最後更新：2023-11-22, 摘要最後同步：2026-05-27

**決策背景**：
需要為第三方合作網站提供一個輕量級的整合方案，讓其用戶可以透過點擊廣告直接登入主站。

**決策結論**：
開發了一套純前端 JavaScript 套件 (InplayzThirdPartyLogin)，第三方只需引入 JS/CSS 並設定 authKey, thirdPartyID, thirdPartyNickName 等參數即可實現自動登入。

**影響**：
- 此方案提供了一種非標準的登入方式，其安全性依賴於 authKey 的保密性。
- 該設計屬於特定歷史時期的產物，可能已被更標準的 OAuth 或 API Key 方式取代。

---

## 操作手冊類


### Discord 第三方登入

> Confluence 頁面 ID：21659917, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=21659917)
> 摘要檔：[processed/21659917-summary.md](../../confluence/processed/21659917-summary.md)
> Confluence 最後更新：2021-06-30, 摘要最後同步：2026-05-27

**摘要**：
本文件說明如何從 Discord 開發者平台建立應用程式、取得 OAuth2 密鑰，並實現 Discord 第三方登入的完整流程。這是一份純操作指南。

**AI 開發需要注意的部分**：
- 若需重現或測試 Discord 登入流程，可參考此文件中的步驟獲取必要參數。但平台的 UI 和流程可能已變更。

---

### Facebook 第三方登入

> Confluence 頁面 ID：21659846, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=21659846)
> 摘要檔：[processed/21659846-summary.md](../../confluence/processed/21659846-summary.md)
> Confluence 最後更新：2022-08-23, 摘要最後同步：2026-05-27

**摘要**：
這份文件提供在 Vue 前端整合 Facebook 登入的完整操作流程。登入後可透過 FB.api 取得使用者公開資料與 email，並處理三種登入狀態（connected、not_authorized、unknown）。

**AI 開發需要注意的部分**：
- 必須在 Facebook 應用程式設定中填寫隱私政策網址，否則應用程式會被停用。
- 必須開通進階服務中的 public_profile 和 email 權限（如需 email）。

---

### 備援機部署

> Confluence 頁面 ID：24084624, 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24084624)
> 摘要檔：[processed/24084624-summary.md](../../confluence/processed/24084624-summary.md)
> Confluence 最後更新：2021-07-26, 摘要最後同步：2026-05-26

**摘要**：
記錄了 Member Service 在 83 PRD、84 Backup PRD、233 PRE 及 Local 環境的功能可用性，並提供檢查 Member Service 可用性的具體方法（如 curl 健康檢查）。

**AI 開發需要注意的部分**：
- 可用於理解不同環境的服務部署和健康檢查方式，對 CI/CD 或環境配置有參考意義，但資訊可能已過時。