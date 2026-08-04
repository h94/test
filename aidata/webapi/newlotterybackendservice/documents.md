# newlotterybackendservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-03-02 10:01
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB-4118 [NewLotteryTools] - 錦標賽、彩池管理

> Confluence 頁面 ID：79467392
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467392)
> 摘要檔：[../../confluence/processed/79467392-summary.md](../../confluence/processed/79467392-summary.md)
> Confluence 最後更新：2025-12-26
> 摘要最後同步：-
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了新運彩後台錦標賽與彩池管理的業務規範。彩池分為週彩、月彩、季彩三種類型，各有期數，每個彩池必須歸屬一個彩池群組；派彩分配可依名次自訂比例，未設定則平均分配，比例總和須為 100%。錦標賽需設定彩池群組、門票、賣牌與聯盟，賣牌抽成預設 10%、所有賣牌種類抽成總和必須為 30%，抽成會併入加碼彩池點數。對 AI 開發者而言，這份文件提供了彩池群組、彩池、錦標賽三者之間的關聯規則與驗證約束，是建立相關 API 和資料模型的核心需求依據。

**關鍵業務規則**：
- 彩池分為週彩、月彩、季彩三種類型，每種有各自的期數
- 每個彩池必須對應一個彩池群組
- 選擇彩池種類時，系統會自動填入預設時間與期數
- 派彩分配可根據名次自訂比例，若未設定則平均分配，所有設定名次的比例總和必須為 100%
- 一場錦標賽至少要包含一個聯盟
- 賣牌根據種類設定抽成比例，預設值為 10%
- 所有賣牌種類的抽成比例總和必須為 30%
- 賣牌抽成會併入加碼彩池點數
- 彩池群組可設定群組名稱，彩池內容需在彩池列表中設定

**注意事項**：
- ⚠️ 詳細設定參數定義在另一個文件 TCZB-4089 [PredictService] - 新運彩錦標賽、彩池系統（pageId=79466794），需交叉參照以取得完整規則
- ⚠️ 「賣牌抽成總和必須為 30%」這項規則需人工確認：是指所有賣牌種類的合計必須恰好 30%，還是至少一種賣牌設為 30%，文件描述可有多種解讀
- ⚠️ 文件中沒有明確說明「賣牌」的種類有多少種以及各自如何定義，需人工確認

---

## 技術設計類

### TCZB-4119 [NewLotteryBackEndService] - 錦標賽、彩池API

> Confluence 頁面 ID：79467346
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467346)
> 摘要檔：[../../confluence/processed/79467346-summary.md](../../confluence/processed/79467346-summary.md)
> Confluence 最後更新：2025-12-18
> 摘要最後同步：-
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了 NewLotteryBackEndService 的錦標賽與彩池管理後台 API 規格，包含彩池群組與錦標賽的 CRUD 操作、路由、Request/Response 格式與欄位說明。對 AI 開發的幫助在於：可據此理解各 API 的輸入輸出契約、彩池群組與錦標賽的狀態流轉規則（尤其啟用條件），以及 payout_Type 在 custom 與 avg 模式下參數結構的差異。

**關鍵業務規則**：
- 彩池群組新增後不會自動啟用，需滿足「至少有一個彩池」才能由管理員操作開啟（status 設為 1）
- 錦標賽新增後不會自動啟用，需管理員點擊「啟用」並確認錦標賽條件後才會開始
- 錦標賽狀態(status)定義：0=關閉、1=進行中、2=已結算
- payout_Type 為 custom 時，payout_Options 為物件，key=名次、value=獎金分配比例(%)；payout_Type 為 avg 時，payout_Options 為 null，獎金平均分配

**注意事項**：
- ⚠️ 文件中 Request Parameter 欄位標注為 **** Expand source，多數欄位僅能從範例 JSON 推斷，實際必填/選填、型態、長度限制需人工確認
- ⚠️ 第 9 項 API（更新彩池群組彩池）的 Route 與第 2 項（新增彩池）完全相同且使用 PUT method，但範例中未見 id 或 pid 來指定要更新的彩池，更新目標的識別方式需人工確認
- ⚠️ 文件提到「沒有做：新增錦標賽後的門票販賣」，表示錦標賽建立後尚無自動販賣門票功能，開發相關流程時需注意此限制
- ⚠️ API #4 取得球種聯盟名稱的回傳範例中 lid 與先前 API 的 leagues 欄位值格式相同，但與 gid 格式不同，需確認 lid 與 gid 的對應關係

### TCZB-4224 [NewLotteryBackEndService] - 交易管理API

> Confluence 頁面 ID：79468577
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79468577)
> 摘要檔：[../../confluence/processed/79468577-summary.md](../../confluence/processed/79468577-summary.md)
> Confluence 最後更新：2026-03-02
> 摘要最後同步：-
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義新運彩後台的交易管理 API，包含儲值方案的新增、查詢、更新，以及交易訂單的查詢與更新，分別列出 PaymentService（對外服務）與 NewLotteryBackEndService（後台服務）的路由、請求/回應格式與驗證規則。對 AI 開發的主要幫助在於明確 API 輸入輸出結構、欄位限制（如金額不得為負、enabled 為 0/1、時間順序、幣種固定為 TWD）以及查詢參數預設行為（空值回傳全會員或近兩個月記錄）。

**關鍵業務規則**：
- 新增/更新儲值方案時，amount 與 coin 欄位不得小於 0（兩個服務皆適用）
- Enabled 欄位只有 0（關閉）與 1（啟用）兩種值（兩個服務皆適用）
- NewLotteryBackEndService 新增儲值方案時，EndTime 必須大於 StartTime，且 currency 目前僅能為「TWD」；PaymentService 未列出此限制，需人工確認是否實際亦須遵守
- NewLotteryBackEndService 更新儲值方案時，若 amount、coin、starttime、endtime、enabled 未傳入，預設為 0；currency 不提供更新
- 查詢交易訂單時（PaymentService），若 account 為空則回傳全部會員的交易記錄，若 startDate 為空則回傳近兩個月的交易記錄
- 更新會員特定交易訂單（NewLotteryBackEndService）可修改 Card4No、Status、ThirdPartyOrderID，若三個參數都未帶入，預設為 null

**注意事項**：
- ⚠️ NewLotteryBackEndService 的「更新儲值方案」方法誤植為 GET，應為 PUT 或 PATCH，需人工確認正確的 HTTP method
- ⚠️ PaymentService 的新增儲值方案未記載 EndTime 必須大於 StartTime 與 currency 限制，可能存在服務間行為不一致，需人工確認是否為文件缺漏或實際邏輯差異
- ⚠️ 文件內 PaymentService 的 subID 範例為英文字串，NewLotteryBackEndService 的 subID 範例為數字「1」，可能代表兩個服務對方案識別碼的型態不同，需確認實際儲存與轉換機制