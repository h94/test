# {serviceName} — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：{yyyy-MM-dd HH:mm}
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---


## 業務規範類


### Fix B365/Bwin/Pinnacle/Betfair PlayMode Mapping

> Confluence 頁面 ID：18644993
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=18644993)
> 摘要檔：[processed/18644993-summary.md](../../confluence/processed/18644993-summary.md)
> Confluence 最後更新：2021-05-04
> 摘要最後同步：2026-05-27
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
此文件定義 B365、Bwin 等數據源的玩法到系統內部 PlayMode 的映射規則，包括 Pregame/Inplay 下讓分/大小、上半場、單節等玩法的標準命名，並對 Bwin、B365 提出具體修正。開發第三方賠率標準化模組時，這是核心轉換規則。

**關鍵業務規則**：
- 讓分/大小 Pregame 對應 HA/OU，Inplay 對應 RBHA/RBOU
- Bwin 修正：1st Half Handicap 改為 HalfHA；1st Half Totals 改為 HalfOU；HA 類型 odds key 存 H/A、OU 類型 odds key 存 O/U
- B365 修正：1st Half 改為 HalfRBHA、HalfRBOU；Over/Under 改為 O/U
- 上半場或前5局 Pregame 對應 HalfHA/OU，Inplay 對應 HalfRBHA/RBOU
- 單節 Pregame 對應 1st/2nd/3rd/4th QuarterHA/OU，Inplay 對應 1st/2nd/3rd/4th QuarterRBHA/RBOU

**注意事項**：
- ⚠️ 文件最後更新於 2021-05-04，規則可能已變更或過時
- ⚠️ Bwin 修正中「框起來的玩法」依賴圖片，需人工對照原始文件確認具體範圍


### TCZB-3670 [PriceTools] - 商城管理

> Confluence 頁面 ID：55585023
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55585023)
> 摘要檔：[processed/55585023-summary.md](../../confluence/processed/55585023-summary.md)
> Confluence 最後更新：2025-03-31
> 摘要最後同步：2026-05-27

**摘要**：
統計需排除 Robot 帳號，定義後台商城管理需求，包含商品列表的篩選、CRUD、圖片預覽，以及商品進貨的輸入與顯示。明確排除卡片樣式，開發時應依據 Figma 設計稿。

**關鍵業務規則**：
- 商品列表必須支援篩選功能
- 商品列表必須支援新增、編輯、刪除單一商品、批量刪除商品
- 商品列表必須支援預覽商品圖片
- 商品進貨必須提供輸入進貨量並顯示進貨後總數
- 卡片樣式不在本次開發範圍內

**注意事項**：
- ⚠️ 文件明確標注「沒有做 - 卡片樣式」
- ⚠️ 商品進貨未說明進貨記錄、歷史查詢或審核流程，需人工確認


### TCZB-3672 [PriceBackendService] - 商城API

> Confluence 頁面 ID：55584936
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55584936)
> 摘要檔：[processed/55584936-summary.md](../../confluence/processed/55584936-summary.md)
> Confluence 最後更新：2025-04-01
> 摘要最後同步：2026-05-27

**摘要**：
定義後台商城管理 API，包含新增、更新、刪除商品，管理商品庫存與兌換紀錄。提供完整的請求格式、回應範例與嚴格的驗證規則，可直接作為 AI 生成前端表單或後端校驗邏輯的依據。

**關鍵業務規則**：
- 新增或更新商品時，商品名稱(zh-TW)、類別(PClass)、圖片路徑(title大圖)、原始價格(OriginalPrice)、來源網址(PSource) 不得為空
- 商品價格(Price)與原始價格(OriginalPrice)不得小於等於 0
- 商品狀態只能是「已上架」(1)或「已下架」(0)
- 非站台商品（PClass 非 inplayz）的商品狀態只能設定為「已下架」
- 欄位 popular 未傳值時，預設為 false
- 更新商品時，商品種類(PClass)與商品 ID(PID)不可更改
- 新增商品庫存紀錄時，PClass 與 PID 不得為空，數量(Quantity)不得小於 1
- 查詢兌換紀錄時，startTime 與 endTime 的時間單位為秒，預設為 0；若任一值為 0，則回傳 30 天內的提領紀錄
- 兌換紀錄狀態(Status)僅在值為「2」(審核中)時，才能更改為「1」(成功)或「0」(失敗)
- 兌換紀錄狀態為「0」(失敗)時，不可更改為非 0 的其他狀態
- 更新兌換紀錄時，Account 欄位在更新前後必須一致，且只能修改狀態(Status)、描述(Description)、配送時間(Deliverytime)
- 刪除商品前，必須確保該商品沒有任何兌換狀態為審核中(2)或其他非失敗/成功的記錄

**注意事項**：
- ⚠️ 文件列出了兌換狀態 0～7，但業務規則僅規範 0、1、2 的流轉，需人工確認狀態 3～7 的完整狀態機


### TCZB-3688 [PriceBackendService] - 社群管理API

> Confluence 頁面 ID：55585195
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55585195)
> 摘要檔：[processed/55585195-summary.md](../../confluence/processed/55585195-summary.md)
> Confluence 最後更新：2025-06-05
> 摘要最後同步：2026-05-27

**摘要**：
定義社群管理後台 API 規格，包含身分標籤與聯盟標籤的 CRUD。關鍵規則包括：聯盟標籤只能建立在可預測球種下；身分標籤僅限五種預定義身分；標籤資料最終儲存在 Meilisearch 中。

**關鍵業務規則**：
- 聯盟標籤只能建立在 GetGamePretictSetting 回傳的可預測球種下
- 創建聯盟標籤時，若某語系沒有對應資料，則預設使用 zh-TW 語系的資料作為備援值
- 更新身分標籤時，請求中的 id 只能是 admin、moderator、vlsport、killer、superkiller 五種身分之一
- 更新身分標籤時，data 中的 zh-TW 語系欄位不得為空；語系僅限 zh-TW 和 en-US 兩種
- 更新聯盟標籤時，id 和 data 中的 zh-TW 欄位不得為空
- 標籤資料儲存於 Meilisearch（http://192.168.55.90:7700/）

**注意事項**：
- ⚠️ 文件中未說明 Meilisearch 是唯一資料來源還是快取層
- ⚠️ 身分標籤表中包含 admin 身分，但取得標籤的範例回傳中不包含 admin


### TCZB-3765 [PriceTools] - 活動管理/電子布告欄/UI優化

> Confluence 頁面 ID：76547040
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76547040)
> 摘要檔：[processed/76547040-summary.md](../../confluence/processed/76547040-summary.md)
> Confluence 最後更新：2025-06-10
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceTools 後台的活動管理、電子布告欄及 UI 優化需求。主推活動模組增加活動選擇與兌獎人資訊；電子布告欄新增時間最小單位秒、多語必填及副標題樣式設定。

**關鍵業務規則**：
- 主推獎品頁面：上方新增活動選擇下拉
- 主推兌獎頁面：新增活動選擇、搜尋欄、兌獎人資訊（暱稱、電子郵件）
- 電子布告欄：時間設定最小單位為秒；繁體中文、簡體中文、英文為必填欄位
- 預測結果：新增刷新按鈕
- 商城兌換審核：新增電子郵件與商品名稱欄位；審核視窗中「ID」更名為「兌換ID」

**注意事項**：
- ⚠️ 「變更日期配置」未說明具體變更內容，需人工確認
- ⚠️ 電子布告欄「副標題樣式設定」僅示意圖，無詳細互動規則


### TCZB-3800 [PriceBackendService] - 機器人彩池遊戲預測API/社群API調整

> Confluence 頁面 ID：79462973
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79462973)
> 摘要檔：[processed/79462973-summary.md](../../confluence/processed/79462973-summary.md)
> Confluence 最後更新：2025-07-25
> 摘要最後同步：2026-05-27

**摘要**：
定義機器人彩池遊戲預測 API（根據請求生成機器人下注）及調整社群 API 以支援 AI 文章的聯盟標籤建立，包含可預測球種限制、語系回退機制等規則。

**關鍵業務規則**：
- 機器人彩池預測：Option 不可為空；RobotCount 必須大於 0；BetCount_Range.Start > 0 且 End >= Start
- 機器人彩池預測：可用機器人總數若小於需求數，回傳錯誤；被凍結的機器人帳號不會被選用
- 創建聯盟標籤：只能對可預測球種的聯盟建立標籤
- 創建聯盟標籤：僅當 gameType = AI 時才須帶 aiLidGameType 參數，值為 lid 對應的聯盟球種代碼
- 創建聯盟標籤：若無 zh-TW 語系資料則回傳錯誤；其他語系若無資料則回退為 zh-TW

**注意事項**：
- ⚠️ 「可預測球種」的定義未在文件中說明，需人工確認


### TCZB-3955 [PriceTools] - 至尊球王管理

> Confluence 頁面 ID：79464981
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464981)
> 摘要檔：[processed/79464981-summary.md](../../confluence/processed/79464981-summary.md)
> Confluence 最後更新：2025-09-25
> 摘要最後同步：2026-05-27

**摘要**：
定義後台至尊球王週期管理頁面的功能需求，包括週期的 CRUD、權重設定（總和必須為1）、查詢球王資訊、修復資料（預測單不得修改超過55天前的資料）以及重新結算功能。

**關鍵業務規則**：
- 新增週期時，週期編號會自動加1
- 新增或編輯週期時，權重相加必須等於1，否則顯示格式錯誤
- 已結算的週期不能被編輯更新
- 修復指定日期資料時，若選擇「預測單」，不得修改超過55天前的資料
- 重新結算可選擇是否補結算使用者資訊

**注意事項**：
- ⚠️ 文件中提到「（不會頻繁重新結算，僅人為提醒）」，暗示此功能為人工觸發的特殊操作
- ⚠️ API 和 DB schema 需參照「至尊球王系統」連結（pageId=79463242）


### TCZB-4142 [PriceTools] - 首頁熱門彩池

> Confluence 頁面 ID：79467662
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467662)
> 摘要檔：[processed/79467662-summary.md](../../confluence/processed/79467662-summary.md)
> Confluence 最後更新：2025-12-30
> 摘要最後同步：2026-05-27

**摘要**：
定義後台彩池管理新增「首頁顯示」選項的需求：只有在選項數量等於兩項時才能操作首頁顯示，且系統中僅允許一個彩池設為首頁顯示。

**關鍵業務規則**：
- 首頁顯示選項僅在該彩池的選項數量等於兩項時方可操作
- 同一時間全系統只能有一個彩池被設為首頁顯示

**注意事項**：
- ⚠️ 文件中的 UI 設計圖與外部簡報連結無法直接解析，具體互動細節需人工確認


### TCZB-4144 [PriceBackendService] - 彩池新增首頁熱門設定

> Confluence 頁面 ID：79467654
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467654)
> 摘要檔：[processed/79467654-summary.md](../../confluence/processed/79467654-summary.md)
> Confluence 最後更新：2025-12-29
> 摘要最後同步：2026-05-27

**摘要**：
在彩池遊戲相關服務中新增「Hot」欄位以支援首頁熱門設定，並強化原本的狀態更新限制：Status=1 時只能修改特定欄位，Status=0 時可修改全部。PriceBackEndService 和 PredictService 的相關 API 同步加入 Hot 欄位。

**關鍵業務規則**：
- 更新預測彩池遊戲時，如果 Status = 1，只能更改 FeedRate、BonusProfitZcoin、Status；如果 Status = 0，則可以更新全部欄位
- BasicProfitZcoin、FeedRate、ZcoinPrice、BonusProfitZcoin 不得小於 0
- Names 語系至少要有 zh-TW
- Status 只能是 0 或 1
- BetOptions 至少要有兩個，且內容中至少要包含 zh-TW 語系

**注意事項**：
- ⚠️ 文件中 Hot 欄位命名不一致（Request 範例 "Hot" vs PredictService Response 範例 "hot"）
- ⚠️ 文件未說明 Hot 欄位的具體業務用途，僅定義資料結構


### TCZB-4169 [PriceTools] - 熱門討論賽事設定、殺手落選名單查詢

> Confluence 頁面 ID：79467893
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467893)
> 摘要檔：[processed/79467893-summary.md](../../confluence/processed/79467893-summary.md)
> Confluence 最後更新：2026-01-19
> 摘要最後同步：2026-05-27

**摘要**：
描述後台 PriceTools 的熱門賽事設定與殺手落選名單查詢功能。熱門賽事僅列出未完賽賽事，日期範圍限制當天與前後各一天；殺手落選名單隱藏第三週獲利點數等於 1 的紀錄。

**關鍵業務規則**：
- 熱門賽事設定頁面僅列出未完賽的賽事
- 熱門賽事設定日期選擇範圍僅限於當天及前後一天（共三天）
- 點選「熱門」按鈕時，必須彈出確認視窗
- 殺手設定頁面新增「落選名單」按鈕，點選後彈出視窗顯示落選名單
- 殺手落選名單中，若第三週獲利點數等於 1，則不顯示該筆紀錄

**注意事項**：
- ⚠️ 日期範圍限制未說明時區標準


### TCZB-4334 [PriceTools] - 反饋UI更新

> Confluence 頁面 ID：79471113
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471113)
> 摘要檔：[processed/79471113-summary.md](../../confluence/processed/79471113-summary.md)
> Confluence 最後更新：2026-05-12
> 摘要最後同步：2026-05-27

**摘要**：
定義球王後台反饋頁面的 UI 更新需求，新增圖片顯示、圖片上傳、刪除圖片及刪除回覆功能。此需求涉及 PriceBackendService 後端 API（TCZB-4306）與 PriceTools 前端聯動。

**關鍵業務規則**：
- 後台反饋頁面必須顯示已上傳的圖片
- 後台反饋頁面必須提供圖片上傳功能
- 提供刪除圖片的功能
- 提供刪除回覆的功能

**注意事項**：
- ⚠️ 需求與使用者互動設計欄位皆為空白，詳細互動邏輯、圖片規格、上傳限制等尚未定義


### TCZB-3410 [PriceBackendService] - 分潤系統/冥燈排行榜

> Confluence 頁面 ID：55580994
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55580994)
> 摘要檔：[processed/55580994-summary.md](../../confluence/processed/55580994-summary.md)
> Confluence 最後更新：2024-08-27
> 摘要最後同步：2026-05-27

**摘要**：
定義預測分潤系統的調整規則：非殺手會員若當日成為高手，其當日預測解鎖分潤係數設為 0.7（殺手和超級殺手維持原規則）。同時新增冥燈排行榜功能，每日最多選出 10 名冥燈，篩選邏輯為高手篩選的反向。

**關鍵業務規則**：
- 非殺手會員在成為當日高手時，其當日預測賽事解鎖分潤係數為 0.7
- 殺手和超級殺手的分潤規則不作變動
- 冥燈排行榜每日最多選出 10 名，且僅當日有對應預測才會被寫入
- 冥燈的篩選邏輯為現有高手篩選規則的反向

**注意事項**：
- ⚠️ —


### TCZB-3091 [PriceTools] - 交易紀錄

> Confluence 頁面 ID：55576377
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55576377)
> 摘要檔：[processed/55576377-summary.md](../../confluence/processed/55576377-summary.md)
> Confluence 最後更新：2024-01-09
> 摘要最後同步：2026-05-27

**摘要**：
定義交易紀錄功能的 API 規格，包含取得與更新支付交易紀錄、取得會員訂閱紀錄以及贈送會員訂閱。重點在於請求參數的預設行為、更新交易狀態與卡號的規則，以及贈送訂閱時自動處理時間重疊的業務規則。

**關鍵業務規則**：
- 查詢交易紀錄時，若不提供 startDate 與 endDate，預設僅查詢當日的交易紀錄
- 更新交易紀錄時，Status 欄位可填 1 或 0，若不填則預設為 0
- 贈送會員訂閱時，所有欄位（SubID, PayType, PayMethod, TradeNo, AutoSub, SubTime）均為必填
- 贈送會員訂閱時，若訂閱開始時間與前一筆訂閱時間重疊，系統將自動把開始時間設定為前筆訂閱的結束時間

**注意事項**：
- ⚠️ —


### TCZB-1065 [PriceBackendService] - 文章審核功能

> Confluence 頁面 ID：24085796
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24085796)
> 摘要檔：[processed/24085796-summary.md](../../confluence/processed/24085796-summary.md)
> Confluence 最後更新：2021-09-10
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackendService 中專家文章審核功能的業務規則與 API 規格。從 Forum 取得待審核文章，依據價格限制規則進行審核，通過後建立會員購買記錄並發送郵件通知。

**關鍵業務規則**：
- 文章原始價格不能小於等於 0
- 文章優惠價格不能小於等於 0
- 文章原始價格不能小於優惠價格
- 審核通過的文章會建立購買此文章的會員紀錄
- 文章審核完成後發送 mail 通知
- 更新審核時，Result 為 0（未通過）需提供 Reason，為 1（通過）需指定 TargetForumID 發佈至特定討論區

**注意事項**：
- ⚠️ 文件最後更新於 2021-09-10，距今已較久，部分業務規則或 API 規格可能已調整


### Vbet 整合玩法列表

> Confluence 頁面 ID：40502795
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40502795)
> 摘要檔：[processed/40502795-summary.md](../../confluence/processed/40502795-summary.md)
> Confluence 最後更新：2022-10-06
> 摘要最後同步：2026-05-27

**摘要**：
此文件為一個外部 Google Sheets 連結，名稱為「Vbet 整合玩法列表」。推測其核心內容是定義球類/電競等各類遊戲在串接 Vbet 數據源時需要支援的具體玩法清單。因原始內容無法直接讀取，實際範圍和細節未知。

**關鍵業務規則**：
- 需人工確認：文件內容無法直接讀取，無法萃取具體業務規則

**注意事項**：
- ⚠️ 文件內容為外部 Google Sheets 連結，該檔案可能有權限限制、已被刪除或內容已過時


### TCZB-2911 [PriceBackendService] - 球王後台API

> Confluence 頁面 ID：47223381
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47223381)
> 摘要檔：[processed/47223381-summary.md](../../confluence/processed/47223381-summary.md)
> Confluence 最後更新：2023-09-21
> 摘要最後同步：2026-05-27

**摘要**：
定義球王後台的三大管理 API：預測管理（莊家殺手條件設定、週期查詢及賽事結算狀態管理）、通知中心（多語通知主題及訊息內容）、反饋系統（運動站台反饋管理）。有助於理解後台維護的資料結構與操作途徑。

**關鍵業務規則**：
- 新增或更新莊家殺手條件時，需提供 AvgOdd、MinCount、FirstWeekMinCount、SecondWeekMinCount、MinWinPercentage 等參數
- 賽事結算結果狀態僅有 0（未結算）與 1（已結算）兩種
- 通知項目須支援多語言名稱(zh-TW, zh-CN, en-US)
- 反饋狀態分為 0（尚未回覆）、1（已回覆）、2（結束）
- 更新反饋回覆時須提供 Message 欄位

**注意事項**：
- ⚠️ 請求參數欄位使用大寫開頭（如 AvgOdd），回應則為小寫開頭（如 avgOdd），需注意前後端命名不一致


### TCZB-3518 [PriceBackendService] - 活動商品API

> Confluence 頁面 ID：55581612
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55581612)
> 摘要檔：[processed/55581612-summary.md](../../confluence/processed/55581612-summary.md)
> Confluence 最後更新：2024-11-22
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackendService 中用於活動商品管理的新 API，具體為更新會員兌換紀錄狀態。狀態更新受限於當前狀態：若狀態已為 1 或 2，則禁止再修改為其他狀態。

**關鍵業務規則**：
- 若兌換紀錄狀態為 1 或 2，則不能再更新為其它狀態

**注意事項**：
- ⚠️ —


### PriceBackendService Flow

> Confluence 頁面 ID：24086044
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/PriceBackendService+Flow)
> 摘要檔：[processed/24086044-summary.md](../../confluence/processed/24086044-summary.md)
> Confluence 最後更新：2022-01-11
> 摘要最後同步：2026-05-27

**摘要**：
以流程圖描述 PriceBackendService 作為前後端中介層的設計，涵蓋審核文章、討論區列表、廣告管理、公司系統設定值及 playmode 站台管理等功能，每個流程均標示出關鍵驗證步驟。

**關鍵業務規則**：
- 取得需審核文章時，必須先驗證請求的時間區間
- 更新審核文章時，必須驗證原始價格和優惠價格
- 取得公司系統設定值時，必須驗證球種和公司
- 新增/修改/刪除設定值 playmode 時，必須驗證球種及 playmode
- playmode 新增支援站台時，必須驗證新增方式、球種及 playmode

**注意事項**：
- ⚠️ 文件最後更新於 2022-01-11，流程可能已變更


### TCZB-3786 [PriceBackendService] - 彩池預測/討論區水桶API

> Confluence 頁面 ID：76547359
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76547359)
> 摘要檔：[processed/76547359-summary.md](../../confluence/processed/76547359-summary.md)
> Confluence 最後更新：2025-07-14
> 摘要最後同步：2026-05-27

**摘要**：
定義兩組後台管理 API：會員討論區停權（Banned GameUser）與彩池預測（Bet Pool）的 CRUD 及結算派發。包含明確的狀態相依更新限制、派發 Z 幣的去重規則等。

**關鍵業務規則**：
- 新增/更新 Ban 單時，endTime 日期必須大於今日，且同一用戶只允許存在一筆 ban 單記錄
- 彩池遊戲的 Names 物件必須至少包含 zh-TW 語系，BetOptions 至少要有兩個選項且每個選項內容也必須包含 zh-TW
- 彩池遊戲的 Status 僅允許 0（未開始）或 1（進行中）
- 更新彩池遊戲時，若 Status=1 則只能修改 FeedRate、BonusProfitZcoin、Status；若 Status=0 則可修改全部欄位
- 彩池遊戲結果 WinResult 不可為「C」，其值必須對應 BetOptions 的某個 key
- 派發 Z 幣時，必須在尚未派發過（payout=false）的狀況下才能執行，且每個獲獎用戶的所有注單會合併為一筆交易

**注意事項**：
- ⚠️ 更新彩池遊戲結果規則中「WinResult，取消 C」需人工確認完整含義
- ⚠️ Ban 單的 endTime 是否含時分秒需確認


### TCZB-4281 [PriceBackendService] - 後台管理功能API

> Confluence 頁面 ID：79469569
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469569)
> 摘要檔：[processed/79469569-summary.md](../../confluence/processed/79469569-summary.md)
> Confluence 最後更新：2026-04-23
> 摘要最後同步：2026-05-27

**摘要**：
定義兩個功能模組的實作方案：熱門彩池賽事 API（透過 PriceBackendService 轉發 PriceCenter 請求，設定時若資料已存在則覆蓋式更新）；Z 幣排行過濾機制（在 Domain Layer 中使用 skipRobotUser() 過濾機器人，再依 email 過濾測試帳號）。

**關鍵業務規則**：
- 設定熱門場中競猜賽事時，若該賽事資料已存在，必須先清空原有資料後再寫入新資料
- 取得熱門場中競猜賽事時，「不需」判斷 GameLive 狀態
- Z 幣排行過濾邏輯直接寫在「取得錢包資訊」Domain Layer 函式中
- 機器人帳號使用 skipRobotUser() 函式過濾
- 測試帳號透過使用者 email 是否包含「zbdigital」進行過濾

**注意事項**：
- ⚠️ 測試帳號過濾邏輯：測試帳號 email 混用了 @zbdigital.net 與 @gmail.com，過濾規則需人工確認


### TCZB-2995 [PriceBackendService] - PriceTools API

> Confluence 頁面 ID：55574768
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-2995+%5BPriceBackendService%5D+-+PriceTools+API)
> 摘要檔：[processed/55574768-summary.md](../../confluence/processed/55574768-summary.md)
> Confluence 最後更新：2023-10-25
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackendService 須新增的廣告與賽事 API，包含廣告的新增、查詢、更新，以及賽事的查詢與比分狀態更新。規定更新比分時同步更新 zba 系統。

**關鍵業務規則**：
- 更新比賽比分和狀態時，必須同步更新 zba 系統中對應遊戲的比分和狀態
- 廣告圖片上傳後透過絕對路徑 https://inplayz.com/{imgPath} 存取
- 廣告分類（adClass）欄位僅允許 'self'（自家廣告）或 'sponsor'（贊助廣告）
- 更新廣告時，若未變更圖片則請求中不須傳遞 imgPath 參數

**注意事項**：
- ⚠️ 文件提到「目前只有 PRD 可以讀到圖片」，AI 服務若需讀取圖片須確認權限機制


### TCZB-3016 [PriceBackendService] - 訂閱方案API

> Confluence 頁面 ID：55574997
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55574997)
> 摘要檔：[processed/55574997-summary.md](../../confluence/processed/55574997-summary.md)
> Confluence 最後更新：2023-11-01
> 摘要最後同步：2026-05-27

**摘要**：
定義運動類訂閱方案及付費方式的 RESTful API。update 付費方式時，若停用（enabled=0）會自動停用所有關聯的訂閱方案。

**關鍵業務規則**：
- 付費方式由 payType（CreditCard, ATM, WebATM, CVS, Barcode）與 mode（disposable, period）組合識別
- 付費方式 enabled 為 1 表示啟用，0 表示停用；訂閱方案亦同
- 更新付費方式為停用（enabled=0）時，系統會自動停用所有已啟用且關聯該付費方式的訂閱方案
- 多語言名稱必須支援 zh-TW、zh-CN、en-US
- 訂閱方案支援一次性（disposable）與定期定額（period）兩種付費模式
- 更新訂閱方案時須傳入完整資訊，非部分欄位更新
- 訂閱方案 currency 固定為 TWD，subType 值為 D，effectiveLength 為有效天數

**注意事項**：
- ⚠️ 更新付費方式的 API 路徑前綴不一致（無 /sport），可能為錯誤或版本演進殘留
- ⚠️ subType 欄位僅出現 'D'，缺少文件說明


### [PriceBanckedService] - 預測單轉移API

> Confluence 頁面 ID：55577084
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55577084)
> 摘要檔：[processed/55577084-summary.md](../../confluence/processed/55577084-summary.md)
> Confluence 最後更新：2024-02-02
> 摘要最後同步：2026-05-27

**摘要**：
定義預測單轉移功能的 API，用於處理賽事因時間變更而需將用戶預測單轉移至新賽事的情境。轉移規則：只允許同日期且因時間改變的相同賽事轉移；重複玩法預測則保留主賽事預測；轉移後刪除舊預測單。

**關鍵業務規則**：
- 預測單轉移僅允許發生於同日期（GDate 相同）但因時間調整而變更的相同賽事
- 若轉移後出現重複的玩法預測，則系統自動保留主賽事的玩法預測，刪除非主賽事的重複預測
- 轉移操作完成後，舊的預測單必須被移除

**注意事項**：
- ⚠️ 文件未明確定義「主賽事」的判斷邏輯與「相同賽事」的匹配規則，需人工確認


### TCZB-3358 [PriceBackendService] - 後台功能API

> Confluence 頁面 ID：55579946
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55579946)
> 摘要檔：[processed/55579946-summary.md](../../confluence/processed/55579946-summary.md)
> Confluence 最後更新：2024-07-16
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackendService 後台管理用的 RESTful API，涵蓋運動交易訂單新增、運動文章管理、App 版本控制、會員分潤與日報查詢、球種玩法開關、會員列表與身份管理、賽事結果更新等 14 個端點。

**關鍵業務規則**：
- 新增運動站台文章時，請求中的 id 欄位需為空值，由系統自動生成唯一識別碼
- 更新賽事結束資訊僅能新增或修改 resultInfo 內的欄位，傳入空物件 {} 不會刪除已存在的屬性
- 更新會員身份時，Memberships 陣列可填入的字串值為：admin、vlsport、moderator
- 取得 App 系統版本列表回傳的 device 欄位值為 'Android' 或 'IOS'
- 取得時間範圍內會員與預測報表時，gameType 為 'All' 時代表所有球種的總和

**注意事項**：
- ⚠️ 文件位於 Confluence 的「舊的 Projects 1-200」路徑，可能已有部分 API 被廢棄或修改


### TCZB-3542 [PriceBackendService] - 活動管理API

> Confluence 頁面 ID：55581795
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55581795)
> 摘要檔：[processed/55581795-summary.md](../../confluence/processed/55581795-summary.md)
> Confluence 最後更新：2025-02-21
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackendService 中球王活動管理的 REST API，包含活動商品的新增、查詢、更新、刪除以及會員兌換紀錄的查詢與狀態更新。定義了活動商品狀態（暫停、販售、售完）和兌換紀錄狀態的枚舉值。

**關鍵業務規則**：
- 活動商品僅設定原始數量 (Quantity)，剩餘數量由提領紀錄加總計算
- 刪除活動商品時，必須同時刪除該商品關聯的所有兌換紀錄
- 兌換紀錄狀態共有五種：0 處理中、1 成功、2 失敗、3 審查中、4 待撥款
- 活動商品狀態共有三種：0 暫停、1 販售、2 售完

**注意事項**：
- ⚠️ 文件內「設想」段落將兌換日誌狀態描述為「處理中、審核中、待撥款、完成、失敗」，與下方表格定義不一致


### TCZB-3568 [PriceBackendService] - 會員網域維護API

> Confluence 頁面 ID：55582012
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55582012)
> 摘要檔：[processed/55582012-summary.md](../../confluence/processed/55582012-summary.md)
> Confluence 最後更新：2024-12-11
> 摘要最後同步：2026-05-27

**摘要**：
定義會員網域維護相關的三個 API，用於管理禁用 Email 網域清單及查詢各網域當前使用數量，背景是為了防止活動期間大量免費信箱註冊，並可管理常見誤植網域。

**關鍵業務規則**：
- 管理員可透過 POST /pricebackendservice/api/member/forbidden/email/domains 傳入欲禁用的 Email 網域清單
- 管理員可透過 GET /pricebackendservice/api/member/forbidden/email/domains 查詢目前所有被禁用的 Email 網域清單
- 管理員可透過 GET /pricebackendservice/api/member/game/users/email/domains 取得各 Email 網域在賽事站台的當前會員數量

**注意事項**：
- ⚠️ —


---

## 技術設計類


### PriceBackendService API

> Confluence 頁面 ID：24086160
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/PriceBackendService+API)
> 摘要檔：[processed/24086160-summary.md](../../confluence/processed/24086160-summary.md)
> Confluence 最後更新：2022-06-09
> 摘要最後同步：2026-05-27

**摘要**：
此文件是 PriceBackendService 的 API 規格，列出所有端點的 HTTP 方法、路徑、請求參數、回應格式與欄位備註，涵蓋支付紀錄查詢、討論區管理、會員管理、賽事系統設定與訂閱者管理等後台功能。

**關鍵設計決策**：
- API 統一使用 /pricebackendservice/api/ 前綴，區分 Payment、Forum、Member、GameSetting 等模組
- 大部分 GET 請求使用 query string，POST/PUT 使用 JSON body
- 回應格式多數使用 Code + Message 結構表示操作結果

**影響範圍**：
- 所有模組依賴於此 API 規範，若 API 規格變更，前端介面和客戶端程式需同步調整

**注意事項**：
- ⚠️ 文件最後更新於 2022-06-09，部分 API 可能已變更或廢棄
- ⚠️ 管理者相關 API 路由與參數為空白，可能尚未實作或文件不完整


### 站台otherinfo資訊對照

> Confluence 頁面 ID：40501716
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=40501716)
> 摘要檔：[processed/40501716-summary.md](../../confluence/processed/40501716-summary.md)
> Confluence 最後更新：2022-09-08
> 摘要最後同步：2026-05-27

**摘要**：
定義 otherinfo 欄位在不同球種（SC、BS、FL、TN、CK）與不同資料來源（1xbet、HGA、188bet、Leisu、Betsapi）之間的支援對照表。188bet 僅支援 Country 和 Location，HGA 僅支援部分功能，Live 直播欄位在所有來源皆無對應資料。

**關鍵設計決策**：
- 採用分球種、分資料來源的稀疏矩陣設計來管理 otherinfo 欄位對應，避免強制補齊造成空值過多
- Live 欄位全數空白，可能表示直播資訊另有獨立的資料流或服務處理

**影響範圍**：
- 影響 PriceCenter 相關服務中環境資訊（天氣、溫度等）的擷取與保留邏輯

**注意事項**：
- ⚠️ Live 欄位全為空白，若後續有需求上線直播資訊，不可直接沿用此對照表


### TCZB-3637 [PriceBackendService] - 商城商品API

> Confluence 頁面 ID：55583629
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55583629)
> 摘要檔：[processed/55583629-summary.md](../../confluence/processed/55583629-summary.md)
> Confluence 最後更新：2025-08-11
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackEndService 的商城商品 CRUD API 設計，該服務作為後台管理層，調用 ProductService 進行實際資料操作。查詢時計算剩餘數量，新增/更新時驗證必填欄位，更新只能修改名稱、價格、數量、圖片。

**關鍵設計決策**：
- PriceBackEndService 不直接操作資料庫，所有持久化由 ProductService 負責
- 取得商品時，remain_Quantity 由 PriceBackEndService 計算（initial_Quantity - 已提領數量）
- 支援多語系商品名稱（PNames），儲存時使用語言代碼 key-value 結構

**影響範圍**：
- 商城功能的後端實作，依賴 ProductService 的 API 實現

**注意事項**：
- ⚠️ 刪除商品 API 的回應格式未定義
- ⚠️ 欄位命名風格混用（PNames vs pNames），開發時需與實際接口對齊


### TCZB-3707 [PriceBackendService] - 球王會員錢包報表API&分潤機制/退貨機制API更新

> Confluence 頁面 ID：55585585
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55585585)
> 摘要檔：[processed/55585585-summary.md](../../confluence/processed/55585585-summary.md)
> Confluence 最後更新：2025-05-08
> 摘要最後同步：2026-05-27

**摘要**：
描述球王會員分潤與退貨機制的技術調整：分潤改為直接發放Z幣，退貨需退還Z幣。新增多個 API 支援會員錢包查詢（最低顯示門檻 45000 Z幣）、90天交易紀錄、月報表生成、商品兌換紀錄更新等。

**關鍵設計決策**：
- 錢包顯示最低門檻 45000，理由是需 >= 商城商品最低價
- 採用 xxl-job 排程產生年月份報表，實現非同步處理
- 分潤報表相關操作由 PaymentService 提供，分離關注點
- DB 中 payment.sharereports_sport 新增 payout 與 sharezcoin 欄位

**影響範圍**：
- 會員錢包功能、分潤報表、退貨流程

**注意事項**：
- ⚠️ balanceConditions 預設 45000，若商品最低價變動需同步調整


### TCZB-3723 [PriceBackendService] - 預測賽事Z幣派彩/預測賽事Z幣交易紀錄

> Confluence 頁面 ID：76546196
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76546196)
> 摘要檔：[processed/76546196-summary.md](../../confluence/processed/76546196-summary.md)
> Confluence 最後更新：2025-05-02
> 摘要最後同步：2026-05-27

**摘要**：
定義兩個 API：POST 預測賽事Z幣派彩（手動針對單場賽事派發 Z 幣，用於自動派彩系統異常時）與 GET 賽事Z幣交易紀錄查詢。派彩流程包含查詢該場所有 Z 幣交易、找出贏的預測注單，並檢查是否已有對應派彩記錄以避免重複。

**關鍵設計決策**：
- 派彩前必須檢查是否已有對應的派彩交易紀錄，以防止重複派彩

**影響範圍**：
- 預測賽事 Z 幣派發的後端邏輯，關係到資金結算的正確性

**注意事項**：
- ⚠️ —


### TCZB-3766 [PriceBackendService] - 電子布告欄/社群管理API

> Confluence 頁面 ID：76546977
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76546977)
> 摘要檔：[processed/76546977-summary.md](../../confluence/processed/76546977-summary.md)
> Confluence 最後更新：2025-07-31
> 摘要最後同步：2026-05-27

**摘要**：
定義電子布告欄公告（AdvertisingService）與社群文章及標籤（CommunityService）的後台管理 API。涵蓋公告的 CRUD、文章分頁查詢、置頂文章、聯盟與身分標籤的 CRUD，每個端點都詳列請求格式、回應結構、必填欄位與語系要求。

**關鍵設計決策**：
- 公告的 localisation 強制使用 zh-CN、en-US、zh-TW 三語系為必填
- announcementmethod 欄位透過列舉值控制公告版型的三種佈局
- 社群文章分頁以 20 筆為一頁，回應中提供 next_Page 旗標
- 標籤語系預設回退策略：無對應語系資料時自動採用 zh-TW
- 只有當 gameType 為 AI 時才需附帶 aiLidGameType 參數

**影響範圍**：
- 電子布告欄與社群管理的後端功能

**注意事項**：
- ⚠️ 創建聯盟標籤時「可預測球種」的完整清單未列於本文，需參考其他文件


### TCZB-3843 [PriceBackendService] - 至尊球王API

> Confluence 頁面 ID：79463258
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463258)
> 摘要檔：[processed/79463258-summary.md](../../confluence/processed/79463258-summary.md)
> Confluence 最後更新：2025-10-17
> 摘要最後同步：2026-05-27

**摘要**：
定義至尊球王後台服務的 API 設計，包含週期管理、排行榜 JSON 寫檔、使用者活動資料設定與修復、自動/手動結算。結算前會重新比對冠軍，不一致則禁止結算；自動結算排程在每月 2 號執行。

**關鍵設計決策**：
- 排行榜標頭時間設定為週期結束日期後一天，以涵蓋跨天比賽及避免最後3小時資料遺漏
- 自動結算排程在每月 2 號執行：讓 1 號有時間修復週期結束日的資料
- 結算前再次比對冠軍，若不一致則禁止結算，防止資料異動導致結果失真
- 週期 CID 強制連續且不可跳號

**影響範圍**：
- 至尊球王活動的後台管理、自動結算流程

**注意事項**：
- ⚠️ —


### TCZB-3953 [PriceBackendService] - 至尊球王管理API

> Confluence 頁面 ID：79464955
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79464955)
> 摘要檔：[processed/79464955-summary.md](../../confluence/processed/79464955-summary.md)
> Confluence 最後更新：2025-11-19
> 摘要最後同步：2026-05-27

**摘要**：
定義至尊球王後台管理 API，包含週期的 CRUD、資料修復、重新結算、備份注單等端點，並提供嚴格的參數校驗規則（如權重值範圍、CID 遞增、時間順序等）。同時標記移除後台已不再使用的提領審核相關 API。

**關鍵設計決策**：
- 所有權重欄位必須大於 0 且小於 1，五者加總必須等於 1
- 手動修復 PredictBet 類型資料時，只能修復當天往前推算 56 天（含當天）的記錄
- 備份至尊球王注單紀錄的範圍為包含今天往前共 5 天的資料
- 刪除 PriceBackEndService 及 PriceCenterSite 中已無後台使用的運動站台提領審核相關 API

**影響範圍**：
- 至尊球王的後台管理功能

**注意事項**：
- ⚠️ withdrawlogs_activity 資料表在刪除 API 後仍保留，可能仍有殘留資料
- ⚠️ 權重加總必須為 1，需注意浮點數誤差


### TCZB-4009 [PriceBackendService] - 至尊球王計算調整

> Confluence 頁面 ID：79465583
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79465583)
> 摘要檔：[processed/79465583-summary.md](../../confluence/processed/79465583-summary.md)
> Confluence 最後更新：2025-10-21
> 摘要最後同步：2026-05-27

**摘要**：
記錄將至尊球王活動的百分比分數滿分從 10 分調整為 100 分的變更，並詳細定義 PriceBackEndService 與 MemberService 相關 API 的路由、請求與備註。包含資料修復的 56 天限制、結算時間檢查、冠軍存在性檢查，以及每月 2 號執行週期結算的排程原因。

**關鍵設計決策**：
- 每月 2 號結算：週期結束日設在月底，讓系統跑到隔月 1 號修復最後一天的資料後，於 2 號結算
- MemberService 設定資料時，data 必須依照各 type 的格式序列化為字串，且不會寫入不在週期時間內的資料

**影響範圍**：
- 至尊球王活動的計分邏輯與 API 驗證規則

**注意事項**：
- ⚠️ —


### TCZB-4171 [PriceBackendService] - 熱門討論賽事、殺手落選名單API

> Confluence 頁面 ID：79467895
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467895)
> 摘要檔：[processed/79467895-summary.md](../../confluence/processed/79467895-summary.md)
> Confluence 最後更新：2026-01-13
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackendService 的兩個新功能：管理熱門討論賽事與讀取殺手落選名單。殺手落選名單以讀取本地 JSON 檔案方式提供，API 可依球種、聯盟、週期查詢；熱門討論賽事提供設定、查詢、刪除三支 API。

**關鍵設計決策**：
- 殺手落選名單中 ThirdWeekBetProfitPoint 欄位預設值為 1（不確定是否有第三週，先預設）
- 設定熱門討論賽事時，gdate、gtype、lid、gid、title 五個欄位不得為空

**影響範圍**：
- 熱門討論賽事的後台管理功能、殺手落選名單的讀取機制

**注意事項**：
- ⚠️ 文件中提及「不確定有沒有第三週，先預設1」，語意與實際週數需人工確認
- ⚠️ 熱門討論賽事設定時可傳入 footer 欄位，但查詢回應中 footer 為 null，行為不一致


### 後台優化

> Confluence 頁面 ID：79469362
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469362)
> 摘要檔：[processed/79469362-summary.md](../../confluence/processed/79469362-summary.md)
> Confluence 最後更新：2026-03-26
> 摘要最後同步：2026-05-27

**摘要**：
描述後台會員查詢功能的優化方案：在既有查詢帳號資訊的彈窗中，新增會員訂閱紀錄的查詢。API 合併 Response，在同一個 endpoint 同時回傳錢包資訊（userWalletDTO）與訂閱紀錄（userSubLogs）。

**關鍵設計決策**：
- 選擇在既有查詢彈窗中擴充功能，而非建立獨立頁面
- API 設計採用合併 Response，一次呼叫即可取得完整會員資訊
- 訂閱紀錄以陣列形式回傳，支援多筆歷史紀錄

**影響範圍**：
- 會員查詢功能的後端 API

**注意事項**：
- ⚠️ API 備註欄標註「對外 API 還沒轉址」，需確認目前是否已完成轉址


### Z幣報表系統後台

> Confluence 頁面 ID：79469895
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469895)
> 摘要檔：[processed/79469895-summary.md](../../confluence/processed/79469895-summary.md)
> Confluence 最後更新：2026-04-13
> 摘要最後同步：2026-05-27

**摘要**：
詳述 Z 幣報表後台系統的實作方案，涵蓋 API 設計、前端組件規劃與資料聚合方式。系統提供玩家預測、賽事預測、其他 Z 幣來源及股票交易等維度的查詢報表，透過 predictservice、tradegameservice 等取得原始資料，再由後端整合會員資訊與賽事資料。

**關鍵設計決策**：
- 採用 Cursor AI 輔助開發，僅保留人工測試與 code review
- 取得比賽資料時使用 PriceCenterProvider.GetDateGames 批次查詢，避免逐個調用 API
- 報表資料聚合：以 beckendservice 的 PredictController 為中樞
- 前端每個 Tab 的查詢結果皆支援排序，排序以 API 輸出結果為準
- 一般玩家 Z 幣預測：predictbets_{gtype} 表中 strategy_id=0 且 usezcoins=true 才納入統計
- 排除機器人：多個報表 API 需調用 memberProvider.GetRobots(999) 取得機器人帳號進行過濾
- 股票交易報表收入計算：trade_type = 'buy' 時收入 = -(stock_price * num)；'sell' 時收入 = +(stock_price * num)

**影響範圍**：
- Z 幣報表系統的跨服務串接、資料過濾與畫面交互

**注意事項**：
- ⚠️ 文件為開發過程的 Cursor Prompt 記錄，部分內容可能已與實際程式碼不一致


### TCZB-4306 [PriceBackendService] - 社群水桶Z幣回收機制、反饋調整

> Confluence 頁面 ID：79470174
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79470174)
> 摘要檔：[processed/79470174-summary.md](../../confluence/processed/79470174-summary.md)
> Confluence 最後更新：2026-05-15
> 摘要最後同步：2026-05-27

**摘要**：
定義社群水桶的 Z 幣回收機制（包含 4 天暫緩期、遮文章、Redis 記錄待扣款資訊並由 XXL 排程執行），以及調整反饋功能（支援使用者上傳圖片限 3 張、管理者上傳及回收圖片、收回重複日期的回覆訊息）。

**關鍵設計決策**：
- 選用 Redis 緩存待扣款資訊，並以 XXL 排程非同步執行扣款，實現 4 天延遲處罰與取消彈性
- 反饋圖片統一由 feedbackService 管理存儲，以日期分目錄組織
- 管理者圖片回收僅刪除資料庫路徑，保留實體檔案
- 收回留言採用覆蓋策略，基於相同日期判斷重複
- 會員 Z 幣系統新增第 4 類「處罰類」，TypeInfo dType 設定為 "Deduction"

**影響範圍**：
- 社群水桶的處罰機制、反饋系統的圖片管理

**注意事項**：
- ⚠️ 文中提到「等待遮蔽文章API處理好，就能了解傳遞參數是否有問題」，表示遮蔽API的參數仍待確認
- ⚠️ 扣款失敗的處理流程未定義，僅提到「執行扣款，並刪除Redis上的紀錄」


### TCZB-4336 [PriceBackendService] - Z幣排行榜

> Confluence 頁面 ID：79471001
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471001)
> 摘要檔：[processed/79471001-summary.md](../../confluence/processed/79471001-summary.md)
> Confluence 最後更新：2026-05-15
> 摘要最後同步：2026-05-27

**摘要**：
定義在 PriceBackendService 新增 Z幣排行榜功能，透過既有的會員錢包交易紀錄 API 取得全體用戶正收入交易（排除測試帳號與小編），並根據 Type 與 TypeInfo 將交易合併為 predict（競猜）、community（社群）與 membership（身份）三大類，分別計算月、週、日排名，生成 JSON 檔案。

**關鍵設計決策**：
- 採用靜態 JSON 檔案預先計算排行榜，而非即時 API 查詢
- 直接複用既有「取得會員錢包交易紀錄」API 作為資料來源
- 將多個相關的 TypeInfo 合併到三大類群組，簡化前端顯示
- 月排名計算過去30天（不含今天）；週排名計算過去7天（不含今天）；日排名計算昨天
- 交易類型分類規則：Type 1 下的 predict profit、profit correction、betpool profit、包含 'sell' 或 'reset' 字串的正收入合併為「predict」；Type 2 下的 article bonus、comment bonus、click like bonus 合併為「community」；Type 2 下的 killer bonus、supreme winner bonus、share bonus 合併為「membership」

**影響範圍**：
- Z幣排行榜的生成邏輯與輸出格式

**注意事項**：
- ⚠️ 新 API 的輸入參數與回應格式在文件中為空白，需人工確認補齊
- ⚠️ 分類規則依賴 TCZB-3654 的 Type 定義，若後續有變更需要同步調整


### PriceBackend查詢玩家商品兌換總計報表

> Confluence 頁面 ID：79471859
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471859)
> 摘要檔：[processed/79471859-summary.md](../../confluence/processed/79471859-summary.md)
> Confluence 最後更新：2026-05-25
> 摘要最後同步：2026-05-27

**摘要**：
一份 AI 輔助開發的紀錄，目標為後台 Z 幣報表新增商品兌換總計與玩家兌換總計兩個分頁。涉及 ProductService 提供交易記錄 API、pricebackendservice 計算已兌換 Z 幣、前端顯示。文件總結了 task-helper、plan-maker、pr-review 三個 AI 工具的協作流程與注意事項。

**關鍵設計決策**：
- ProductService 新 API 必須直接回傳 redeem logs + 商品內容，禁止在 pricebackendservice 再次調用 ProductService
- 統計需排除 Robot 帳號
- 不建議一次性同時開發三個 repo，因為需求演化時難以管理 plan 的歸屬

**影響範圍**：
- Z 幣報表的商品兌換相關功能

**注意事項**：
- ⚠️ 文件最後更新日期為 2026-05-25，需人工確認是否為未來日期或測試資料
- ⚠️ 文中所提 AI 工具流程可能隨團隊規範變動


### TCZB-4363 [PriceBackendService] - 社群報表API

> Confluence 頁面 ID：79471596
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471596)
> 摘要檔：[processed/79471596-summary.md](../../confluence/processed/79471596-summary.md)
> Confluence 最後更新：2026-05-25
> 摘要最後同步：2026-05-27

**摘要**：
定義球王後台社群報表的 API，提供討論版總數、按球種類型統計、用戶統計及對應的細項查詢功能。所有 API 均以 GET 方法提供，時間起訖為必填參數，統計數據排除運彩與公告板塊。

**關鍵設計決策**：
- 採用 pricebackendservice 統一提供後台報表 API，實際數據可能由 communityservice 聚合
- 提供獨立的彙總、分組與細項端點，符合後台常見的 drill-down 互動模式
- 統計資料必須排除運彩與公告
- 所有 API 的 startdatetime 與 enddatetime 為必填參數

**影響範圍**：
- 後台社群報表的 API 合約

**注意事項**：
- ⚠️ API 路徑均以 /communityservice/api/ 開頭，但在 PriceBackendService 的設計中列出，可能表示透過反向代理或內部調用整合


### [GS後台] - BC站台賽事查詢

> Confluence 頁面 ID：76546107
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76546107)
> 摘要檔：[processed/76546107-summary.md](../../confluence/processed/76546107-summary.md)
> Confluence 最後更新：2025-04-25
> 摘要最後同步：2026-05-27

**摘要**：
定義 GS 後台如何從 BC 站台（外部 odds 服務）取得賽事資料。包含兩個 API：使用帳密取得 Token，以及透過 MatchId 查詢賽事資訊（含盤口、賠率、比分等）。

**關鍵設計決策**：
- API 採用兩段式流程：先取得 Token，再查詢賽事資訊

**影響範圍**：
- GS 後台的賽事資料取得

**注意事項**：
- ⚠️ API 網址為 stage 環境，上線前需更換為正式環境
- ⚠️ 文件中明文包含帳號密碼（i2OF / 9o2-sPE=ogom），請勿用於正式環境


### TCZB-987[PriceBackendService] - 廣告資訊維護

> Confluence 頁面 ID：24086361
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24086361)
> 摘要檔：[processed/24086361-summary.md](../../confluence/processed/24086361-summary.md)
> Confluence 最後更新：2021-09-29
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackendService 的廣告資訊維護後台功能，包含取得廣告（支援多重選填過濾）、新增廣告（含圖片上傳）、編輯廣告（可選擇更新圖片）。廣告可分為 promotion（自家優惠）與 sponsorship（贊助廣告）。

**關鍵設計決策**：
- 廣告查詢 API 設計為 GET /pricebackendservice/api/advertising/{type}，透過 type 路徑參數區分 promotion 或 sponsorship
- 新增與編輯使用 POST，以 multipart/form-data 同時接受 JSON 與檔案上傳
- 回傳格式統一使用 Code/Message 結構（Code 10000 表示成功）
- 廣告的 action 欄位僅接受 'blank'（新分頁）、'location'（直接導頁）、'window'（新視窗）
- 上傳廣告圖檔副檔名必須為 .gif / .jpg / .jpeg / .png，且檔案容量不得超過 100KB

**影響範圍**：
- 後台廣告管理功能

**注意事項**：
- ⚠️ 文件最後更新於 2021-09-29，後續可能已有 API 改版


### TCZB-1767 [PriceBackEndService]-Log系統API

> Confluence 頁面 ID：32540569
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=32540569)
> 摘要檔：[processed/32540569-summary.md](../../confluence/processed/32540569-summary.md)
> Confluence 最後更新：2022-04-21
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackEndService 中兩個和股票使用者操作記錄相關的 API：取得所有有記錄的股票使用者帳號清單，以及根據帳號查詢其操作記錄。清楚說明查詢操作記錄時的查詢參數規則（startTime/endTime 的預設行為）。

**關鍵設計決策**：
- API 採用兩段式查詢：先取得帳號清單，再根據帳號查詢明細，降低單次回應資料量
- 時間查詢採用 Unix Timestamp，確保跨時區一致性
- LogInfoDTO 中包含 BrokerCondition 巢狀物件，嵌入當時的市場條件設定
- 若 startTime 沒帶值，則取一天內的紀錄；若 startTime 有帶值但 endTime 沒帶值，則取 startTime + 一天的紀錄

**影響範圍**：
- 股票使用者的操作記錄查詢

**注意事項**：
- ⚠️ 文件最後更新於 2022-04-21，API 路徑或參數名稱可能已變更
- ⚠️ API 2 的查詢參數拼寫為 'stratTime' 而非 'startTime'，可能是文件筆誤


### TCZB-2732 [PriceTools] - 預測管理功能

> Confluence 頁面 ID：47221158
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47221158)
> 摘要檔：[processed/47221158-summary.md](../../confluence/processed/47221158-summary.md)
> Confluence 最後更新：2023-05-26
> 摘要最後同步：2026-05-27

**摘要**：
定義預測管理功能的 API 設計，包含新增/更新/查詢莊家殺手週期設定，以及取得所有支援的球種與聯盟名稱對照。

**關鍵設計決策**：
- 莊家殺手週期以 CID 作為唯一識別，支援路徑參數 {gameType}/{lid}/{cid} 進行更新
- 球種聯盟設定回傳的結構按 gameType（如 BS, HL, SC, BK）分組，每個聯盟包含 name 與 name_Map 多國語系

**影響範圍**：
- 預測相關後端服務的 API

**注意事項**：
- ⚠️ 文件最後更新於 2023-05-26，部分 API 或路徑可能已變更
- ⚠️ 回應範例中的 name_Map 部分語系為空字串，開發時需處理缺值情況


### TCZB-2733 [PriceBackendService] - 預測管理功能API

> Confluence 頁面 ID：47221181
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47221181)
> 摘要檔：[processed/47221181-summary.md](../../confluence/processed/47221181-summary.md)
> Confluence 最後更新：2023-05-18
> 摘要最後同步：2026-05-27

**摘要**：
定義預測管理功能中莊家殺手週期相關的 API 設計，包含新增、查詢、更新週期設定，以及獲取預測球種聯盟設定和聯盟名稱/翻譯的接口。涉及 PriceBackendService、Predictservice 和 Pricecenter 之間的交互流程。

**關鍵設計決策**：
- 採用 RESTful API，路徑通過 {gameType}/{lid} 等參數區分資源
- PriceBackendService 作為编排層，聚合 Predictservice 和 Pricecenter 的資料
- 莊家殺手週期獨立管理，允許按球種、聯盟和週期進行增改查

**影響範圍**：
- 預測管理功能的 API 規範與服務間交互

**注意事項**：
- ⚠️ 文件最後更新於 2023-05-18，API 路由和參數結構可能已變更


### TCZB-2769 [PriceBackendService] - 莊家殺手條件設定功能API

> Confluence 頁面 ID：47221705
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47221705)
> 摘要檔：[processed/47221705-summary.md](../../confluence/processed/47221705-summary.md)
> Confluence 最後更新：2023-05-31
> 摘要最後同步：2026-05-27

**摘要**：
定義莊家殺手條件設定的查詢與新增/更新 API，包含兩組端點：一組由 PriceBackendService 代理轉發至 PredictService，另一組由 PredictService 直接暴露。killerType 參數可為 normal 或 super。

**關鍵設計決策**：
- PriceBackendService 作為中間層，收到請求後先驗證格式，再轉發給 PredictService 處理
- 管理後台可能直接調用 PredictService 的 API，跳過 PriceBackendService，因此提供兩組路徑
- KillerType 僅接受 normal 或 super

**影響範圍**：
- 莊家殺手條件設定的 API

**注意事項**：
- ⚠️ 請求參數命名不一致：POST 請求範例為大寫開頭，GET 回應範例使用小寫開頭
- ⚠️ 實際使用需確認哪一組為主要介面


### TCZB-2907 [PriceTools] - 預測管理

> Confluence 頁面 ID：47223389
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47223389)
> 摘要檔：[processed/47223389-summary.md](../../confluence/processed/47223389-summary.md)
> Confluence 最後更新：2023-09-27
> 摘要最後同步：2026-05-27

**摘要**：
定義預測管理中有關莊家殺手條件設定和預測結果重新計算所需的 API 端點。包含新增、取得、更新莊家殺手條件，以及查詢與更新日期/賽事的計算結果狀態等功能。

**關鍵設計決策**：
- API 路由按功能分組，涵蓋莊家殺手條件設定的 CRUD 和計算結果狀態的查詢與更新

**影響範圍**：
- 預測管理的 API 介面

**注意事項**：
- ⚠️ —


### TCZB-2967 [PriceBackendService] - PriceTools API

> Confluence 頁面 ID：55574631
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-2967+%5BPriceBackendService%5D+-+PriceTools+API)
> 摘要檔：[processed/55574631-summary.md](../../confluence/processed/55574631-summary.md)
> Confluence 最後更新：2023-10-06
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackendService 新增的預測管理與社群管理 API，包含球種預測設定的增/查/改、球種清單與聯盟名稱取得、週結算日誌與預測注單查詢，以及社群群組的 CRUD。回應格式與參數枚舉值均具體描述。

**關鍵設計決策**：
- 社群管理部分操作直接使用 WebSocket (WS)，因此 REST API 僅提供群組的基本 CRUD
- 預測相關 API 採用 RESTful 設計，路由包含 gameType 和 lid 作為路徑參數
- 多語系支援：社群群組名稱以 object 格式提供各語言版本
- 預測設定中 Classified 為 true 表示分聯盟，false 表示不分聯盟
- 預測注單中 mode 值代表玩法：1X2、HA、OU；winLoss 狀態包括 W、WR、L、LR、N、C
- 社群群組 GType 必須為 'official'、'normal' 或 'vip'

**影響範圍**：
- 預測管理與社群管理的 API 規格

**注意事項**：
- ⚠️ 文件提到「球種定義 : data define」，但未提供連結內容
- ⚠️ 文件位於「舊的Projects 1-200」目錄，可能部分 API 已廢棄


### TCZB-3041 [PriceBackendService] - 分潤系統API

> Confluence 頁面 ID：55575388
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55575388)
> 摘要檔：[processed/55575388-summary.md](../../confluence/processed/55575388-summary.md)
> Confluence 最後更新：2023-11-28
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackendService 分潤系統的 8 個 API，涵蓋運動站台報表的生成與查詢、提領紀錄的查詢與審核、以及會員驗證。

**關鍵設計決策**：
- 報表生成 API 由 xxl-job 定時任務觸發，非人工直接呼叫
- 驗證會員的 status 欄位值：0=處理中，1=完成，2=失敗；查詢時預設為 status=0
- 更新提領紀錄或驗證會員結果時，若 status 設為 2（失敗），Remark 欄位不可為空
- 更新運動站台報表結果接受 dateTime 參數，格式為 yyyy-MM，預設值為當月的前一個月

**影響範圍**：
- 分潤系統的後端流程

**注意事項**：
- ⚠️ —


### TCZB-3092 [PriceBackendService] - PriceTools API

> Confluence 頁面 ID：55576379
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/TCZB-3092+%5BPriceBackendService%5D+-+PriceTools+API)
> 摘要檔：[processed/55576379-summary.md](../../confluence/processed/55576379-summary.md)
> Confluence 最後更新：2024-01-09
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackendService 的後台管理工具 API，包含交易記錄查詢/更新、會員訂閱記錄查詢、贈送訂閱等功能。透過 PaymentService 與 MemberService 完成業務流程。

**關鍵設計決策**：
- 後台功能透過 PriceBackendService 作為入口，整合 PaymentService 與 MemberService 既有 API
- 訂閱贈送流程中，由 PriceBackendService 自行判斷時間重疊並調整起始時間
- 更新交易記錄 API 中，Status 值為 1 或 0，不填則設為 0
- 取得交易記錄 API 的日期參數不填則預設為今日

**影響範圍**：
- 後台管理工具 API

**注意事項**：
- ⚠️ 部分範例資料（如 payType: "Promation"）可能為測試或舊版欄位值


### [PriceBackendService][MemberService][PriceFrontEndTools]

> Confluence 頁面 ID：55578773
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55578773)
> 摘要檔：[processed/55578773-summary.md](../../confluence/processed/55578773-summary.md)
> Confluence 最後更新：2024-05-15
> 摘要最後同步：2026-05-27

**摘要**：
記錄後台會員管理功能的修改需求：將原有全玩家列表查詢改為通過 email 或 account 查詢單一玩家，並把編輯按鈕拆分為「重設密碼」和「修改狀態」兩個獨立操作。

**關鍵設計決策**：
- 複用既有 API GetGameUsers，改為僅返回單一玩家記錄
- 將編輯功能拆分為重設密碼和修改狀態兩個獨立 API
- 重置密碼接口直接設置新密碼，不要求驗證舊密碼
- 查詢玩家時，email 與 account 參數必須至少填寫其中一個

**影響範圍**：
- 後台會員管理功能

**注意事項**：
- ⚠️ —


### TCZB-3297 [PriceBackendService] - 分潤提領/社群功能API

> Confluence 頁面 ID：55579534
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55579534)
> 摘要檔：[processed/55579534-summary.md](../../confluence/processed/55579534-summary.md)
> Confluence 最後更新：2024-06-05
> 摘要最後同步：2026-05-27

**摘要**：
定義賽事社群管理功能的 API，包含新增與管理賽事小編及取得社群賽事預測資料的端點，所有端點均歸屬於 PriceBackendService。

**關鍵設計決策**：
- 賽事小編相關 API 使用路徑參數 {authKey} 區分不同編輯者
- 取得社群賽事預測的 API 支援查詢參數 searchAccount 與 lang，回應按遊戲類型及聯盟分組

**影響範圍**：
- 賽事社群管理的 API

**注意事項**：
- ⚠️ 文件缺少 API 的 Parameter 詳細規範，僅有路由與回應範例


### TCZB-3371 [PriceBackendService] - 預測篩選報表功能API

> Confluence 頁面 ID：55580439
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55580439)
> 摘要檔：[processed/55580439-summary.md](../../confluence/processed/55580439-summary.md)
> Confluence 最後更新：2024-07-26
> 摘要最後同步：2026-05-27

**摘要**：
描述一個新的定時任務觸發的 API，用於生成預測篩選排行榜快照文件。流程由 xxl-job 調度 PriceBackendService，依次調用 PredictService、MemberService、PriceCenterService 獲取資料，最終組裝排行榜並存儲到 NAS 路徑。

**關鍵設計決策**：
- 排行榜採用離線生成方案，由 xxl-job 定時觸發，避免即時計算壓力
- 快照文件存儲於 NAS，路徑格式為 downloads/leaderboard/sportsite/filter/{gameType}/{date}
- API 僅暴露 POST 方法同步生成，但實際依賴多個下游服務並行獲取資料
- 排行榜排序依據為 ProfitPoint 或 Seq_Score 等欄位

**影響範圍**：
- 預測篩選排行榜的生成與數據流轉

**注意事項**：
- ⚠️ 序列圖中兩處 TODO 提示可能在設計階段尚未完成具體邏輯


### TCZB-3430 [PriceBackendService] - 站內信API/主推排行榜

> Confluence 頁面 ID：55581189
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55581189)
> 摘要檔：[processed/55581189-summary.md](../../confluence/processed/55581189-summary.md)
> Confluence 最後更新：2024-09-06
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackendService 中站內信管理與主推連勝排行榜生成/更新的 API 設計。包含四個端點：生成/更新主推連勝排行榜、新增通知站內信、上傳信件內文圖片、取得通知站內信。

**關鍵設計決策**：
- 主推連勝排行榜採用 POST 生成或更新，無需額外請求參數
- 站內信收件人採帳號清單而非單一收件人
- 圖片上傳直接回傳已轉存的完整 URL
- 站內信內容支援 HTML 格式
- 查詢站內信時，若未指定 startDate 與 endDate，預設查詢範圍為昨日 00:00:00 至今日 23:59:59

**影響範圍**：
- 站內信與主推排行榜的 API

**注意事項**：
- ⚠️ 主推連勝排行榜的請求參數與回應均未詳細定義
- ⚠️ 上傳圖片的請求參數僅提供截圖，缺少文字描述


---

## 歷史決策類


### TCZB-2336[Stock] - Stock Redis 美韓中

> Confluence 頁面 ID：44663494
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44663494)
> 摘要檔：[processed/44663494-summary.md](../../confluence/processed/44663494-summary.md)
> Confluence 最後更新：2022-12-20
> 摘要最後同步：2026-05-27

**決策背景**：
需要將美國、韓國、中國的股票數據存入 Redis db10。

**決策結論**：
通過國家名稱迴圈動態調用各國股市 API 獲取數據，選擇 Redis db10 作為股票資料的存儲數據庫。

**影響**：
- 股票數據的獲取和存儲方式，擴展新國家時無需修改核心邏輯

**注意事項**：
- ⚠️ 文件最後更新於 2022-12-20，可能 Redis 結構或 API 已有變更


### TCZB-3804 [PriceTools] - 機器人彩池預測功能/AI文章審核發布

> Confluence 頁面 ID：79462982
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79462982)
> 摘要檔：[processed/79462982-summary.md](../../confluence/processed/79462982-summary.md)
> Confluence 最後更新：2025-07-17
> 摘要最後同步：2026-05-27

**決策背景**：
一份極簡略的功能初步規劃文件，提出新增「機器人彩池預測」以自動下注分攤彩池獎金，以及「AI文章審核發布」以簡化審核流程。

**決策結論**：
採用機器人加注機制來分攤過多的彩池總獎金（具體觸發條件與演算法未定）。對 AI 開發的幫助僅止於了解功能方向，尚無可執行的規則或設計細節。

**影響**：
- 功能方向參考，後續需參照詳細規格實作

**注意事項**：
- ⚠️ 問題列表為空，可能代表需求尚未釐清或待補全
- ⚠️ 文件內容極少，大部分功能描述僅為設想


---

## 操作手冊類


### PriceBackendService Flow

> Confluence 頁面 ID：24086044
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/PriceBackendService+Flow)
> 摘要檔：[processed/24086044-summary.md](../../confluence/processed/24086044-summary.md)
> Confluence 最後更新：2022-01-11
> 摘要最後同步：2026-05-27

**摘要**：
以流程圖描述 PriceBackendService 如何作為前後端中介層，將來自 Tools 的請求轉送至 ForumService、GameSettingService、AdvertisingService 等後端服務，包含審核文章、討論區列表、廣告管理等主要功能。

**AI 開發需要注意的部分**：
- PriceBackendService 作為中介層，不直接操作資料庫，主要負責驗證、轉發和業務邏輯編排


### TCZB-3637 [PriceBackendService] - 商城商品API

> Confluence 頁面 ID：55583629
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55583629)
> 摘要檔：[processed/55583629-summary.md](../../confluence/processed/55583629-summary.md)
> Confluence 最後更新：2025-08-11
> 摘要最後同步：2026-05-27

**摘要**：
定義 PriceBackEndService 的商城商品 CRUD API 設計，該服務調用 ProductService 進行實際資料操作，並在查詢時計算剩餘數量。

**AI 開發需要注意的部分**：
- PriceBackEndService 不直接操作資料庫，所有持久化由 ProductService 負責
- remain_Quantity = initial_Quantity - 已提領數量，由 PriceBackEndService 計算
- 更新與刪除商品前需先調用 ProductService 確認商品存在


### TCZB-3843 [PriceBackendService] - 至尊球王API

> Confluence 頁面 ID：79463258
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79463258)
> 摘要檔：[processed/79463258-summary.md](../../confluence/processed/79463258-summary.md)
> Confluence 最後更新：2025-10-17
> 摘要最後同步：2026-05-27

**摘要**：
定義至尊球王後台服務的 API 設計，包含週期管理、排行榜 JSON 寫檔、使用者活動資料設定與修復、自動/手動結算。

**AI 開發需要注意的部分**：
- 結算週期時會重新比對排行榜冠軍與最新資料運算的冠軍，不一致則禁止結算
- 排行榜標頭時間設定為週期結束日期後一天，以涵蓋跨天比賽
- 週期 CID 強制連續且不可跳號
- 修復參與者活動資料：Type 為 PredictBet 時，只能修復距今 56 天內的資料
- ⚠️ 與 TCZB-3955 文件中規定的 55 天限制存在差異，請人工確認


### Z幣報表系統後台

> Confluence 頁面 ID：79469895
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469895)
> 摘要檔：[processed/79469895-summary.md](../../confluence/processed/79469895-summary.md)
> Confluence 最後更新：2026-04-13
> 摘要最後同步：2026-05-27

**摘要**：
詳述 Z 幣報表後台系統的實作方案，包括 API 設計、前端組件規劃與資料聚合方式。開發過程大量使用 Cursor AI 生成程式碼。

**AI 開發需要注意的部分**：
- Z 幣其他來源過濾規則：GameUserWallet.Type = 1 且 typeInfo 中不包含「betpool 」則跳過不處理
- 股票交易報表收入計算：trade_type = 'buy' 時收入 = -(stock_price * num)
- 報表查詢參數：start_date/end_date 若未提供則預設為今天
- 文件為 Cursor Prompt 記錄，非最終規格，需對照實際程式碼


### TCZB-4306 [PriceBackendService] - 社群水桶Z幣回收機制、反饋調整

> Confluence 頁面 ID：79470174
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79470174)
> 摘要檔：[processed/79470174-summary.md](../../confluence/processed/79470174-summary.md)
> Confluence 最後更新：2026-05-15
> 摘要最後同步：2026-05-27

**摘要**：
定義社群水桶的 Z 幣回收機制：4 天暫緩期、遮文章、Redis 記錄待扣款資訊並由 XXL 排程執行。同時調整反饋功能，支援圖片上傳與管理。

**AI 開發需要注意的部分**：
- 社群水桶後有 4 天暫緩期，期滿後扣除 ban 期間由社群文章獲得的 Z 幣總額
- 待扣款資訊暫存於 Redis（包含 authKey、預計扣款日期、Z 幣總額），由 XXL 排程每日檢查
- 反饋系統中使用者上傳圖片限制最多 3 張，管理者上傳無限制
- 圖片上傳：部分成功寫 LogInformation，全部失敗必須直接拋出 Error
- 會員 Z 幣系統新增第 4 類「處罰類」，TypeInfo dType 設定為 "Deduction"


### TCZB-4336 [PriceBackendService] - Z幣排行榜

> Confluence 頁面 ID：79471001
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79471001)
> 摘要檔：[processed/79471001-summary.md](../../confluence/processed/79471001-summary.md)
> Confluence 最後更新：2026-05-15
> 摘要最後同步：2026-05-27

**摘要**：
定義 Z幣排行榜功能的實作方案，透過既有的會員錢包交易紀錄 API 取得資料，按 predict、community、membership 分類計算排名，生成 JSON 檔案。

**AI 開發需要注意的部分**：
- 只統計正收入（正收益）的交易紀錄，負值不列入排名
- 必須排除測試帳號與小編的交易紀錄
- 月排名計算過去30天（不含今天）；週排名計算過去7天（不含今天）；日排名計算昨天
- 排行榜結果以 JSON 檔案輸出，存放於 downloads/leaderboard/sportsite/zcoin 目錄