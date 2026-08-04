# pricecentersite — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 12:00
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB-3687 [PriceCenterSite] - 球王商城API

> Confluence 頁面 ID：55585219
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55585219)
> 摘要檔：[processed/55585219-summary.md](../../confluence/processed/55585219-summary.md)
> Confluence 最後更新：2025-04-23
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了球王商城（PriceCenterSite）的四支核心 API，包括商品兌換、商品目錄查詢、兌換紀錄查詢、以及收件資訊更新。對 AI 開發而言，關鍵資訊有兩點：(1) 兌換商品的收件地址填寫規則——「球王站台以外的商品都要填入 Address」，這是判斷兌換請求是否需要地址的邏輯依據；(2) 收件資訊更新的狀態限制——「兌換紀錄狀態是 2 的情況下才可以更新」，這是實作更新 API 時必須檢查的前置條件。

**關鍵業務規則**：
- 商品兌換時，若兌換商品屬於「球王站台以外」，則必須填入 Address 欄位（需人工確認：如何判斷商品是否為球王站台商品）
- 更新會員兌換紀錄地址時，必須先檢查兌換紀錄的 status 欄位值是否為 "2"，只有在 status = "2" 的情況下才允許更新（需人工確認：status 欄位的完整枚舉值定義，如 "0", "1", "2" 各代表什麼狀態）
- 商品兌換請求的 PClass 和 PID 欄位對應商品目錄中的 pClass 和 pid

**注意事項**：
- ⚠️ 文件中未說明 status 欄位的完整枚舉值定義（"0", "1", "2" 各代表什麼狀態），需人工確認 db-context 或相關規格
- ⚠️ 「球王站台以外的商品」判斷邏輯未在文件中說明（是根據 PClass 判斷？還是商品有 site 屬性？），需人工確認
- ⚠️ 兌換紀錄中的 status 與更新規則中的狀態 "2" 是字串比對還是數字比對，文件中 Response 顯示字串型別，需確認
- ⚠️ 文件提及的 [TCZB-3655 [ProductService] - 球王商城商品系統] 連結頁面 ID 55584452 可能有商品相關的額外規則，建議一併查閱

### TCZB-3839 [PriceCenterSite] - 賽事API調整

> Confluence 頁面 ID：79463207
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463207)
> 摘要檔：[processed/79463207-summary.md](../../confluence/processed/79463207-summary.md)
> Confluence 最後更新：2025-08-11
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件說明為支援球王站台顯示 AI 分析文章及 twslfocus 內容，需在賽事 API 的 otherInfos 欄位中新增 twslfocusContent 與 ai 兩個屬性。twslfocusContent 包含 focus 和 tv 兩個 key，從外部來源取得；ai 為布林值，標記該賽事是否有 AI 分析文章可供展示。文件同時定義了文章檔案的儲存路徑規則。此變更影響四個賽事相關 API 的回應結構，對 AI 開發而言，需要知道何時該讀取、如何解析這些新欄位，以及文章內容的讀取規則。

**關鍵業務規則**：
- 賽事 API 回應中的 otherInfos 欄位新增 twslfocusContent 物件，包含 focus（字串）和 tv（字串）兩個 key，資料來源為 twslfocus。twslfocusContent 可為 null。
- 賽事 API 回應中的 otherInfos 欄位新增 ai 屬性（布林值），標記該賽事是否有對應的 AI 分析文章。
- AI 分析文章檔案儲存路徑規則為：/app/wwwroot/downloads/info/inplayz/{date}/{gid}_{語系參數}.txt。
- 取得球種賽事 API（games/{gameType}）的搜尋範圍為「前5天到明天共7天」的賽事。
- 取得球種聯盟日期範圍賽事賠率 API（games/odds/{gameType}/{lid}）的 endDate 參數預設為 searchDate 往後 99 天；若 startDate 或 endDate 任一未提供，皆使用預設值。
- 四個 API 中，「取得球種賽事」和「取得球種聯盟日期某場賽事資訊」的 twslfocusContent 是直接放在 otherInfos 下的巢狀物件；「取得球種聯盟日期範圍賽事賠率」和「取得熱門預測賽事」的 twslfocus 內容（focus、tv）是直接以 key-value 形式放在 otherInfo 物件的第一層，結構不同，需人工確認是否為設計不一致或文件筆誤。

**注意事項**：
- ⚠️ 文件中的 API 回應範例顯示 otherInfo 內同時存在 ai: true 和 ai: "false"（字串）兩種型別，需人工確認正規化後的型別（布林值或字串）。
- ⚠️「取得熱門預測賽事」和「取得球種聯盟日期範圍賽事賠率」的 otherInfo 結構與另外兩個 API 不同（focus/tv 直接放在 otherInfo 第一層而非 twslfocusContent 物件內），需確認是設計意圖還是文件錯誤。
- ⚠️ 最後更新日期為 2025-08-11，但文件中提及的日期範例為 2025-07-29 等，文件描述的實作可能已上線，需確認 latest 狀態。

### TCZB-4007 [PriceCenterSite] - 至尊球王API  / AI走地推薦解鎖機制

> Confluence 頁面 ID：79465581
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465581)
> 摘要檔：[processed/79465581-summary.md](../../confluence/processed/79465581-summary.md)
> Confluence 最後更新：2025-10-30
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件說明至尊球王球王榜 API 與 AI 走地推薦解鎖機制的運作規則。球王榜 API 提供球種聯盟排行、週期、多語系支援等資料，並定義每 3 小時快取及歷史預測即時查詢的緩存策略。AI 走地解鎖機制限制一般會員每日最多解鎖 3 場，VIP/admin 不設限；解鎖資訊以特定格式存於 Redis，並透過 MemberService 管理解鎖次數。對 AI 開發而言，必須遵守這些 API 的欄位省略規則、身分歧視邏輯、Redis 資料格式與每日解鎖上限。

**關鍵業務規則**：
- 球王榜 API 整體快取 3 小時，但近 30 天歷史預測資料每次即時查詢，不納入快取。
- 球王榜 API 的玩法資料 (lastThirtyDaysGameModesWinRate) 若無對應注單，該玩法 key 將不出現在 response 中。
- 取得球種聯盟項目的 API 支援多語系 (lang 參數)，預設 zh-TW；若該語系無資料，回退至 en-US。
- 排行榜 API 回傳前 10 名及使用者自身排名；leaderBoardDetails 最後一筆固定為查詢帳號的排名，若無帳號或未參賽則該筆為 null。
- 解鎖 AI 走地預測 (POST news/inplay/{gtype}/{gid}/unlock/{authKey})：VIP 與 admin 直接回傳成功，不會將解鎖記錄存入 Redis；一般會員每日最多解鎖 3 場。
- 取得近期 AI Inplay 預測內容 API：已完賽賽事回傳全部預測資訊；VIP/admin 開放所有賽事；一般會員同樣受每日 3 場解鎖限制。
- 會員免費解鎖 AI 走地預測資料 (MemberService) 最多存放 3 筆於 Redis，若已滿則不新增；資料格式為 List<string>，每個項目格式為 {GameType}_{LID}_{GID}。
- 僅一般會員有免費解鎖資料，VIP/admin 不產生該 Redis 記錄。

**注意事項**：
- ⚠️ 格式不一致：MemberService 解鎖 API request body 範例為 "SC_G2pOgrw3KUG"，僅含 GameType 與 GID，但文件定義格式為 {GameType}_{LID}_{GID}，需人工確認實際傳遞格式。
- ⚠️ 格式不一致：取得免費解鎖資料 API 回傳範例為 ["BK_GvWKrdemglU","BS_GTests4WQks"]，也是 {GameType}_{GID} 形式，缺少 LID，需確認是否統一。
- ⚠️ 拼寫錯誤：lastThirtyDaysZcoinsProfit 中的 totalZoins 可能是 totalZcoins，需以實際 API 為準。

### TCZB-4040 [PriceCenterSite] - 討論區黑名單API

> Confluence 頁面 ID：79466163
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79466163)
> 摘要檔：[processed/79466163-summary.md](../../confluence/processed/79466163-summary.md)
> Confluence 最後更新：2025-11-10
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義討論區黑名單功能的 API 規格與業務規則。對 AI 開發的幫助在於：1) 釐清黑名單的 CRUD 操作歸屬 MemberService，文章過濾邏輯歸屬 CommunityService；2) 明確黑名單的操作限制（一次只能處理一個會員、不能黑名單自己或官方帳號、輸入 account 由系統轉成 authKey 儲存）；3) 定義文章列表與詳情 API 需根據 visitors 參數過濾黑名單會員的內容。

**關鍵業務規則**：
- 新增/刪除黑名單時，black_account 陣列若含多個帳號，僅第一個帳號會被處理（新增或移除），其餘忽略
- 新增黑名單時，傳入的會員 account 會由系統轉換為 authKey 後存入資料庫
- 不能將自己加入黑名單
- 不能將官方帳號加入黑名單
- 刪除黑名單時一次只能移除一個會員，black_account 陣列僅第一個帳號生效
- 取得文章列表（community/{gameType}/article/filter/page）時，需移除 visitors（觀看者）黑名單會員所發佈的文章
- 取得社群球種文章頁面（community/{gameType}/article/page）時，需移除 visitors 黑名單會員的文章，visitors 透過 query string ?visitors={authKey} 傳入
- 取得社群球種某一文章（community/{gameType}/articles/{id}）時，需移除 visitors 黑名單會員的文章，visitors 透過 query string ?visitors={authKey} 傳入
- 文章回傳的 myEmoji 欄位：若使用者未點讚為 null，若有點讚則為字串（例如 "like"）

**注意事項**：
- ⚠️ 文件最後更新於 2025-11-10，但參考文件 TCZB-3619 的連結需人工確認是否仍為最新版本
- ⚠️ 「取得社群球種某一文章」API 的 Response 僅回傳單一文章物件而非陣列，且未包含 needClick/nextPage 等分頁欄位，與其他文章 API 的 Response 結構不同，需人工確認此為預期行為還是文件遺漏
- ⚠️ 黑名單新增/刪除的 black_account 參數型態為陣列，但實際只處理第一個元素，這個設計容易造成呼叫方誤解，建議標注為已知限制

### TCZB-4143 [PriceCenterSite] - 社群獎勵機制調整 / 會員殺手期數預測資訊調整

> Confluence 頁面 ID：79467660
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467660)
> 摘要檔：[processed/79467660-summary.md](../../confluence/processed/79467660-summary.md)
> Confluence 最後更新：2026-01-06
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文檔定義 PriceCenterSite 社群機制的獎勵規則調整與殺手期數預測 API 新增字段。社群回文、點讚等行為引入 Z 幣獎勵及每日上限，並規定回文字數限制為 2~200；BetPool API 新增熱門彩池查詢參數 hot，Killer API 新增三週獲利屬性及判斷邏輯。對 AI 開發提供可執行的業務計算規則與校驗條件。

**關鍵業務規則**：
- 社群回文最少字數為 2 字，上限 200 字。
- 回文非本人文章且內容超過 15 字時，每則贈送 20 Z 幣給回文者，每日最高 200 Z 幣。
- 文章收到讚數超過 10 個時，每個讚贈送 40 Z 幣給文章發布者；超過 30 個讚時，每個讚贈送 50 Z 幣。
- 對非本人的文章或回文按讚，每次贈送 20 Z 幣給按讚者（文章與回文合併計算），每日上限 200 Z 幣。
- 回文每收到一個讚，贈送 30 Z 幣給回文發布者，無上限。
- 编辑回文內容時亦須遵守 2~200 字限制。
- BetPool API 查詢全部彩池遊戲資訊，若 hot=true：後台有設定熱門彩池時取最接近結束時間的熱門彩池；無設定時取最接近結束時間且僅兩個選項的彩池。若 hot=false 則返回全部彩池。
- 殺手期數預測 API 新增 accountFirstWeekBetPointProfit、accountSecondWeekBetPointProfit、accountThirdWeekBetPointProfit 三個雙週獲利字段，其值由系統計算。
- 雙週獲利狀態定義：0 表示未獲利，1 表示有獲利，-1 表示殺手週期時間尚未到達該週（如第三週未到則為 -1）。

**注意事項**：
- ⚠️ 回文獎勵的字數條件為「非本人文章且字數超過 15 字」；若為回覆回文（RespCommentID 非 null）的場景，未明確是否同樣適用此規則，需人工確認。
- ⚠️ 文章點讚獎勵階梯式遞增（10 以上 40 Z 幣，30 以上 50 Z 幣），未說明是否從第 11 個開始以 40 計算、第 31 個開始以 50 計算，需確認計算方式。
- ⚠️ 按讚贈送 20 Z 幣的每日上限 200 Z 幣為文章按讚與回文按讚合併計算，實施時需確保計數器正確累計。
- ⚠️ 殺手雙週獲利字段的計算邏輯未在本文中詳述，僅定義狀態碼，實際獲利數值來源需確認是否來自後續計算服務。

---

## 技術設計類

### FrontEndSite .NET Core Game API Document

> Confluence 頁面 ID：21660232
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/FrontEndSite+.NET+Core+Game+API+Document)
> 摘要檔：[processed/21660232-summary.md](../../confluence/processed/21660232-summary.md)
> Confluence 最後更新：2022-05-19
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義了五個遊戲相關 API 的端點、參數與回傳模型 (GameDto、SiteGameDto、OddDto 等)，用於取得指定球種賽事、熱門賽事、特定賽事及今日賽事資料。對 AI 開發而言，能清楚了解取得賽事數據的介面與回應結構，便於整合與調用。

**注意事項**：
- ⚠️ 文件最後更新於 2022-05-19，可能已有異動或過時，使用前需確認 API 現狀
- ⚠️ SiteGameDto 中 Score2 欄位型別標為 'it'，疑似筆误，應為 int，需人工確認

### TCZB-3653 [PriceCenterSite] - 球王Z幣/商城API

> Confluence 頁面 ID：55584494
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55584494)
> 摘要檔：[processed/55584494-summary.md](../../confluence/processed/55584494-summary.md)
> Confluence 最後更新：2025-03-18
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件定義了球王 PriceCenterSite 新增的 Z 幣錢包和商城相關 API，包含取得錢包餘額、交易紀錄、簽到表、商城商品分類與詳細資訊、社群會員文章頁面及簽到更新。明確規範交易紀錄的三種類型（預測投注、獎勵、商品）及其對應的數據結構，並限制錢包交易紀錄僅提供 90 天內資料。同時列舉了獎勵類型、商品分類和兌換類型等枚舉值，並記錄商城 API 延後開發的決策。

**關鍵業務規則**：
- 錢包交易紀錄僅提供 90 天內的資料。
- 簽到表固定 30 天，每天對應的 coin 數量為：第1-6天 50 coin，第7天 100 coin，第8-13天 50 coin，第14天 100 coin，第15-20天 50 coin，第21天 100 coin，第22-29天 50 coin，第30天 500 coin。
- 交易紀錄類型：1 = 預測投注(predictInfo)，2 = 獎勵(bounsInfo)，3 = 商品(redeemInfo)。
- 獎勵類型(bType)：daily login(每日簽到)、article bonus(文章獎勵)、comment bonus(回文獎勵)、click like bonus(點擊獎勵)、bonus cancel(獎勵取消)。
- 兌換類型(pType)：purchase(購買)、refund(退款)。對應訊息(pMessage)：redeem product(兌換商品)、redeem product cancel(兌換商品取消)。
- 預測投注相關訊息類型(predictMessage)：predict betting(預測投注)、predict profit(預測獲利)、profit correction(獲利修正)。
- 商品分類：3C(手機平板家電類)、PC(電腦電競零組件)、HP(保健醫療保養品)、BH(圖書文具家居生活)、FT(食品零食旅遊票券)、inplayz(球王產品)。

**注意事項**：
- ⚠️ 3/14 記錄「商城API延後」，相關 API 可能尚未實作或啟用，需確認當前版本狀態。
- ⚠️ 簽到表回傳欄位 targetDays 與 todaySigin 的具體語義文件中未說明，可能分別代表「今天應簽到的天數」與「是否已簽到」，需人工確認。
- ⚠️ 商品狀態 status: 1 推測為有效，但未明確定義其他狀態值。

### TCZB-3745 [PriceCenterSite] - 電子布告欄API

> Confluence 頁面 ID：76546694
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76546694)
> 摘要檔：[processed/76546694-summary.md](../../confluence/processed/76546694-summary.md)
> Confluence 最後更新：2025-05-22
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了電子布告欄 API 的設計規格，用於取代原有的 banner 區塊。電子布告欄會根據 announementMethod 參數（1,2,3）對應不同的前端顯示樣式，若無資料則輸出中文預設訊息。文件也整理了「主推連勝王」各活動的 site 與 activityEvent 參數對應表，以及緯來活動相關 API 的路由調整。對 AI 開發而言，這份文件提供了 API 的完整契約，包括請求方法、路由、參數與回應結構。

**關鍵業務規則**：
- 電子布告欄若無資料時，API 必須直接輸出中文預設訊息（文件中列出了 4 組 default 訊息範例）
- announementMethod 欄位決定前端樣式：1 為樣式一、2 為樣式二、3 為樣式三
- 主推連勝王各活動使用相同的 API 路由 /activity/leaderboards/mainstreak/{site}/{activityEvent}，透過 site 與 activityEvent 參數區分活動，site 固定為 inplayz
- 緯來活動的勝率排行榜路由獨立為 /activity/leaderboards/winrate/vlsport/nba-finals，需附 authKey 參數

**注意事項**：
- ⚠️ 文件提到的「緯來活動調整」具體內容不明，需人工確認是否為一次性活動或長期功能
- ⚠️ announementMethod 的對應樣式以圖片呈現，無法從文字判斷各樣式的具體差異，開發時需參考原始圖片

### TCZB-3785 [PriceCenterSite] - 彩池預測API

> Confluence 頁面 ID：76547334
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76547334)
> 摘要檔：[processed/76547334-summary.md](../../confluence/processed/76547334-summary.md)
> Confluence 最後更新：2025-06-27
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義彩池預測API，包含新增彩池遊戲會員注單、取得全部彩池遊戲、取得彩池遊戲投注明細、取得會員彩池投注紀錄、取得社群會員水桶資訊五個端點。彩池預測投注無限制，可一次多筆。WinLose 狀態區分輸、贏、取消及未開獎。響應格式包含遊戲資訊、投注選項及玩家細節。對開發預測服務和社群服務整合很有幫助。

**關鍵業務規則**：
- 彩池預測投注沒有投注限制，一次可以投注多筆
- winLose欄位：null或空值表示沒結果，'L'表示輸，'W'表示贏，'C'表示取消
- 取得社群會員水桶資訊，若無資料回傳null

**注意事項**：
- ⚠️ 彩池遊戲響應中的字段（如basicProfitZcoin, bonusProfitZcoin, feedRate等）語義未在文件中解釋，需人工確認
- ⚠️ winResult字段在MEMO中說明可能為'C'取消，但示例中未出現，需確認取消邏輯

### TCZB-3865 [PriceCenterSite] - 賽事API調整/至尊球王API

> Confluence 頁面 ID：79463714
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463714)
> 摘要檔：[processed/79463714-summary.md](../../confluence/processed/79463714-summary.md)
> Confluence 最後更新：2025-10-07
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了 PriceCenterSite 的至尊球王與賽事相關 API 規格。包含取得進行中至尊球王球種聯盟與排行榜的介面，以及賽事查詢、單一賽事資訊、賠率範圍查詢、熱門預測賽事等 API。每個 API 均提供方法、路徑、參數、回應格式與備註，明確說明了排行榜的回應結構（前 10 名加上使用者自己排名）及日期參數的預設行為。這些規格是開發 AI 串接前台賽事與排行榜功能的接口基礎。

**關鍵業務規則**：
- 至尊球王進行中球種聯盟 API (GET /users/supreme/cycles/inprogressitems) 的 lang 參數預設值為 zh-TW。
- 至尊球王排行榜 API (GET /users/supreme/leaderboards/{gameType}/{lid}) 的回應 leaderBoardDetails 必定包含前 10 名資料，且最後一筆一定是 account 參數對應的使用者排名；若 account 未帶值或使用者未參加，則最後一筆為 null，表示未參加。
- 取得球種賽事 API (GET /games/{gameType}) 的 lang 預設 zh-TW，searchDate 預設當下日期，且只輸出從前 5 天到明天共 7 天的賽事。
- 取得球種聯盟日期範圍賽事賠率 API (GET /games/odds/{gameType}/{lid}) 的 lang 預設 zh-TW，searchDate 預設當下日期，endDate 預設當下日期往後 99 天；只要 searchDate 或 endDate 任一個未提供或兩者都未提供，就採用預設值。gid 預設為空。
- 取得熱門預測賽事 API (GET /predict/bets/popular) 的 lang 預設 zh-TW。
- 所有 GameType 代碼對照表：TN（網球）、BS（棒球）、FL（美足）、HL（冰球）、SC（足球）、ES（電競）、BK（籃球）。
- 國家語言代碼包含 zh-CN、en-US、ja-JP、ko-KR、th-TH、zh-TW、vi-VN。
- 轉播資訊格式：eltaottSportLive 和 vlSportLive 均為 JSON 字串，包含 Channels（字典，鍵為頻道名稱，值為直播連結，無連結則空字串）與 Competition（賽事名稱）。

**注意事項**：
- ⚠️ 文件中 predictCount 和 predictCounters 結構在不同 API 中不一致：有的為物件有的為陣列，實作時需注意差異。
- ⚠️ 部分範例回應中的 otherInfo 包含 AI 欄位值為 "false"，但目的未說明，可能與 AI 分析整合有關，需釐清實際用途。
- ⚠️ 文件中未說明取得至尊球王排行榜時 account 參數的來源與驗證機制，需配合會員服務實作。

### TCZB-3919 [PriceCenterSite] - 球王名人堂 API / 停用API移除

> Confluence 頁面 ID：79464603
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464603)
> 摘要檔：[processed/79464603-summary.md](../../confluence/processed/79464603-summary.md)
> Confluence 最後更新：2025-10-21
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件定義了 PriceCenterSite 的「至尊球王名人堂」兩個 GET API，提供最新週期與名人堂詳細資料，回應包含用戶基礎資訊、近 30 天預測歷史、勝率、Z幣獲利及評分等欄位。同時列入一個 AI 預測內容的 API。另一方面，文件規劃要移除多個不再使用的舊 API，涵蓋活動提領、遊戲結果、使用者提領、特殊預測排行榜等，並列出對應的 Controller、Service/Provider 函數與資料表。對 AI 開發的幫助在於：能清楚理解名人堂 API 的資料結構與請求方式，以及即時識別哪些 API 正處於廢棄階段，避免新功能依賴已規劃移除的端點。

**關鍵業務規則**：
- 球王名人堂資料採用快取機制，每 3 小時刷新一次。
- 玩法資料僅在對應有注單數據時才包含於回應中，無數據的玩法不會出現在字典內。
- 支援的球種（GameType）代碼及名稱：TN(網球)、BS(棒球)、FL(美足)、HL(冰球)、SC(足球)、ES(電競)、BK(籃球)。
- AI 報表 API `news/lastest/{gtype}/{lid}` 的語系參數 `lang` 預設值為 `zh-TW`。
- 以下 API 已預計停用/廢除（應避免使用）：activity/withdrawlogs/{authKey}、games/results/{gameType}、games/live/{gametype}、games/homedefault、payment/withdrawlogs/{authKey}（新增）、payment/withdrawlogs/{authKey}（取得）、predict/leaderboard/special/{site}/{activityEvent}。

**注意事項**：
- ⚠️ 廢棄 API 清單中標註「預計停用」「後續廢除」，尚未確定實際下線時間，需人工確認現行環境是否仍提供。
- ⚠️ 名人堂回應欄位名稱存在拼寫錯誤：`lastThrityDaysHistoryPredictGames`（Thrity 應為 Thirty）及 `HighOdd` 值出現 `0.00&`，可能為原始文件誤植，整合時應使用正確欄位名或保留原樣。
- ⚠️ 文件中「AI報表」API 的請求參數 `lang` 雖說明預設 zh-TW，但未列出其他支援語系，需人工確認。

### TCZB-3980 [PriceCenterSite] - 球王名人堂API

> Confluence 頁面 ID：79465339
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465339)
> 摘要檔：[processed/79465339-summary.md](../../confluence/processed/79465339-summary.md)
> Confluence 最後更新：2025-10-08
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定义了至尊球王名人堂相关的三个API端点，包括获取特定球種联盟的名人堂数据、获取有数据之球種联盟项目列表、获取进行中的至尊球王球種联盟项目。接口返回用户基础信息、积分评分、近30天预测历史、玩法胜率等结构化数据，并明确缓存策略（3小时全局刷新，近30天预测历史实时查询）和多语言回退机制。为 pricecentersite 开发提供完整的请求响应规范与实现约束。

**關鍵業務規則**：
- GET users/supreme/halloffame/{gameType}/{lid}/{cid} 返回特定联盟的名人堂数据，包含用户信息、评分、近7天解锁数、近30天Z币盈利、近30天历史预测赛事、各玩法胜率等。
- GET users/supreme/halloffame/items 返回有名人堂数据的球種联盟项目，支持查询参数 lang，缺省为 zh-TW。
- GET users/supreme/cycles/inprogressitems 返回进行中的至尊球王球種联盟项目，支持 query lang，缺省 zh-TW。
- 所有3个端点均采用缓存，每3小时刷新一次，但 halloffame 接口中的近30天历史预测数据（lastThirtyDaysHistoryPredictGames）不缓存，每次请求即时查询。
- 若请求的语系没有对应数据，则回退至 en-US 语系的数据。
- 玩法资料（如游戏模式胜率）仅在有对应注单时才会出现在响应字典中，无数据时不包含该键。

**注意事項**：
- ⚠️ 响应示例中 lastThirtyDaysGameModesWinRate.HighOdd 的值为 "0.00&"，应为 "0.00%"，疑似笔误，需人工确认。
- ⚠️ 注意缓存机制：全局数据每3小时才更新一次，业务上需容忍最长3小时的延迟（近30天预测除外）。

### TCZB-4331 [PriceCenterSite] - 賽事交易所API

> Confluence 頁面 ID：79471136
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471136)
> 摘要檔：[processed/79471136-summary.md](../../confluence/processed/79471136-summary.md)
> Confluence 最後更新：2026-05-13
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件是 PriceCenterSite 中「賽事交易所」BFF API 的完整技術設計方案，定義了七支 REST API 端點（持倉寫入、可交易項目列表、批次股價、聯盟股價、持倉查詢、交易歷史選項、交易歷史）。核心架構為 BFF 層對前端提供統一介面，對內串接 tradegameservice、pricecenterservice、memberservice 等下游微服務。文件包含詳細的 I/O 設計、服務層分層架構、Z 幣扣款/入帳流程（買入先下單後扣款、賣出先下單後入帳+profitpoint）、錯誤碼映射、快取策略等完整實作指引，並已確認所有 Q1-Q15 的業務決策，可直接作為開發規格書使用。

**關鍵業務規則**：
- 交易提交前需驗證 authKey 並轉換為 account，僅允許操作本人帳戶的持倉和交易
- 買入流程：交易資料驗證 → 查詢 Z 幣餘額 → 餘額足夠則呼叫 tradegameservice 下單 → 扣款；扣款失敗時呼叫 CancelTrade 取消該筆交易
- 賣出流程：交易資料驗證 + 持倉驗證 → 呼叫 tradegameservice → 交易成功後錢包餘額加上 profitpoint；入帳失敗時呼叫 CancelTrade 取消該筆交易
- 買賣款金額公式 = 股價 × 張數（trade_price × stock_num），賣出暫不計手續費
- profitpoint 僅賣出時有有意義的回傳值，買入等情況一般為 0，交易成功後錢包直接加上 profitpoint
- Z 幣錢包 TypeInfo 格式使用 TransactionPredictInfo 序列化，PredictMessage 為 buy_{股價}_{張數}（買入）或 sell_{股價}_{張數}（賣出）
- 可預測聯盟列表來源為 IFileProvider.GetPredictSettings（讀取 PredictSetting.json），不經 predictservice 取得
- 列表端點可以快取，股價可短快取但需人工確認實作細節，會員持倉、交易歷史、下單端點不可快取
- 餘額不足或持倉不足回傳 HTTP 400，股價不存在或賽事不可交易回傳 HTTP 403，扣款或入帳失敗回傳 HTTP 500

**注意事項**：
- ⚠️ 文件中多處提及「Phase 2 可經 PM／開發微調路徑名稱」，表示端點路徑仍有變更可能，開發前應確認最終路由
- ⚠️ 文件提及「Z 幣扣款時機依 §14.3 Q1」、「買賣款與錢包 TypeInfo 依 §14.3 Q2／Q5」等多處引用 §14.3 決策結論，若該章節日後更新，本文件可能需同步修正
- ⚠️ 所有待確認問題（Q1-Q15）在文件中標注為「均已確認」，但日期為 2026-05，後續若有業務變更需確認此文件是否仍為最新版本

---

## 歷史決策類

### TCZB-3919 [PriceCenterSite] - 球王名人堂 API / 停用API移除

> Confluence 頁面 ID：79464603
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464603)
> 摘要檔：[processed/79464603-summary.md](../../confluence/processed/79464603-summary.md)
> Confluence 最後更新：2025-10-21
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
文件定義了 PriceCenterSite 的「至尊球王名人堂」兩個 GET API，提供最新週期與名人堂詳細資料，回應包含用戶基礎資訊、近 30 天預測歷史、勝率、Z幣獲利及評分等欄位。同時列入一個 AI 預測內容的 API。另一方面，文件規劃要移除多個不再使用的舊 API，涵蓋活動提領、遊戲結果、使用者提領、特殊預測排行榜等，並列出對應的 Controller、Service/Provider 函數與資料表。對 AI 開發的幫助在於：能清楚理解名人堂 API 的資料結構與請求方式，以及即時識別哪些 API 正處於廢棄階段，避免新功能依賴已規劃移除的端點。

**決策結論**：
- 為降低服務負擔，名人堂資料採用客戶端快取，固定每 3 小時刷新，不回傳即時資料。
- 為清理 PriceCenterSite 中未使用的程式碼，決定移除多個舊 API，包含活動提領、遊戲結果、預設首頁球種、使用者提領紀錄及特殊活動預測排行榜等。

**影響**：
- 廢棄 API 清單中標註「預計停用」「後續廢除」，尚未確定實際下線時間，需人工確認現行環境是否仍提供。

---

## 操作手冊類

### 忘記密碼

> Confluence 頁面 ID：34767561
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=34767561)
> 摘要檔：[processed/34767561-summary.md](../../confluence/processed/34767561-summary.md)
> Confluence 最後更新：2022-05-25
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件透過截圖展示 PriceCenter 前端的忘記密碼流程：使用者點選「忘記密碼」後，輸入電子信箱（即帳號），系統發送重設密碼郵件，使用者點擊郵件內連結進入密碼重設頁面。文件僅說明操作步驟，未定義任何業務規則或技術細節。對 AI 開發的幫助在於確認前端互動順序，可作為 E2E 測試腳本或 API 串接場景的基礎。

**注意事項**：
- ⚠️ 文件僅包含操作截圖，未列出任何業務規則（如密碼複雜度、連結有效期限、重設頻率限制等），開發時需另由規格文件補齊
- ⚠️ 未說明後端對應服務與 API，若直接實作需人工確認 memberservice 或 pricecenterservice 的相關端點

### 站台賽事資訊

> Confluence 頁面 ID：40503258
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40503258)
> 摘要檔：[processed/40503258-summary.md](../../confluence/processed/40503258-summary.md)
> Confluence 最後更新：2022-10-17
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這是一份後台操作手冊，說明如何透過球種、站台、日期、時間(整點區間)、聯盟名稱等條件查詢歷史賽事資料。對 AI 開發的幫助在於：若需開發查詢賽事資料的功能或 API，可參考此文件的查詢參數設計（球種選單、站台選單、整點時間搜尋邏輯、即時搜尋行為）。

**關鍵業務規則**：
- 時間搜尋以「整點」為單位，選擇 6 代表查詢 6:00~6:59 之間的賽事
- 時間欄位右方按鈕可調整增加或減少一小時
- 選擇選單內的時間或點擊按鈕都會直接觸發搜尋，不需再點擊搜尋按鈕
- 若不選擇時間，則顯示當天全部賽事
- 球種選項來自選單內的球類比賽簡稱（需人工確認：選單資料來源與維護方式）

**注意事項**：
- ⚠️ 文件最後更新於 2022-10-17，距今已超過兩年，頁面功能或操作流程可能已有變更
- ⚠️ 文件僅描述操作方式，未說明搜尋 API 的介面規格、回傳格式或錯誤處理邏輯
- ⚠️ 球種選單、站台選單的資料來源未說明，需人工確認