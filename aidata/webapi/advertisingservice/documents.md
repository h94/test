# advertisingservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 11:19
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### AdvertisingService 功能規格需求

> Confluence 頁面 ID：24086348
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24086348)
> 摘要檔：[processed/24086348-summary.md](../../confluence/processed/24086348-summary.md)
> Confluence 最後更新：2021-09-28
> 摘要最後同步：2026-05-26

**摘要**：
這篇文件定義了廣告服務上傳圖檔的規格限制。對於 AI 開發來說，這明確了在處理廣告圖檔上傳功能時，必須在前端或後端驗證檔案格式僅限於 .gif、.jpg、.jpeg、.png，且檔案大小不得超過 100KB。若違反此規則，服務應拒絕接收並回傳對應的錯誤訊息。

**關鍵業務規則**：
- 廣告上傳圖檔僅接受 .gif、.jpg、.jpeg、.png 四種格式，不符合格式的檔案不應接受上傳。
- 廣告上傳圖檔的容量限制為不能大於 100KB，超過此限制的檔案不應接受上傳。

**注意事項**：
- ⚠️ 文件最後更新於 2021-09-28，距今已久，檔案容量限制（100KB）在現行網路環境可能已不合時宜，建議人工確認此規格是否仍適用。

---

## 技術設計類

### AdvertisingService API

> Confluence 頁面 ID：24086483
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/AdvertisingService+API)
> 摘要檔：[processed/24086483-summary.md](../../confluence/processed/24086483-summary.md)
> Confluence 最後更新：2025-05-15
> 摘要最後同步：2026-05-26

**摘要**：
本文件定義了廣告服務 (AdvertisingService) 的 RESTful API 路由、請求參數與回應格式，涵蓋新增廣告、後台取得廣告列表、站台端依據語言與類型查詢廣告、更新廣告以及上傳廣告圖檔等功能。對於 AI 開發而言，可依據此規範正確呼叫廣告服務，建構自動化廣告管理或內容排程；特別是在站台端查詢廣告時，lang 參數為必填、type 為選填的設計，可實現多語系與分類篩選。文件提供了明確的請求/回應範例，降低整合出錯的風險。

**關鍵設計決策**：
- 取得廣告 (站台) GET /advertisingservice/api/ads/{lang} 時，路徑參數 lang 為必填，查詢參數 type 為選填，用於按廣告類型過濾。

**影響範圍**：
- 所有廣告查詢的 API 實作應遵循此路由定義和參數規則。

---

### AdvertisingService DB Table

> Confluence 頁面 ID：24086508
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/AdvertisingService+DB+Table)
> 摘要檔：[processed/24086508-summary.md](../../confluence/processed/24086508-summary.md)
> Confluence 最後更新：2025-05-15
> 摘要最後同步：2026-05-26

**摘要**：
本文定義 AdvertisingService 使用的 advertising 資料表結構，包含廣告編號、名稱、來源、位置、圖片、點擊行為、排序、啟用狀態、有效時間與語系等欄位。這些欄位規則是開發廣告查詢、展示、過濾與排序等 API 的基礎。

**關鍵設計決策**：
- 廣告啟用狀態由 enabled 控制：0 關閉，1 開啟。
- 廣告有效期間由 starttime 和 closetime 決定，查詢時需比對當前時間。
- 廣告排序根據 seq 欄位降冪排列，有效值 1~99，數值越大優先級越高。
- 廣告位置由 type 欄位定義：top, left, right, float。
- 點擊行為由 action 欄位控制：blank（新分頁）、location（直接導頁）、window（新視窗）。
- 廣告來源由 createby 區分：promotion（自家優惠）、sponsorship（贊助廣告）。
- 多語系支援：lang 欄位區分廣告語系。

**影響範圍**：
- 直接影響廣告資料庫的 CRUD 邏輯和前端展示的查詢條件。
- ⚠️ starttime 與 closetime 以 bigint 儲存，格式未說明（推測為 timestamp），需人工確認是否為 UNIX timestamp（秒或毫秒）。
- ⚠️ 文件中未定義廣告圖片路徑的儲存規則（相對路徑或完整 URL），開發時需與實作對照。

---

### AdvertisingService Flow

> Confluence 頁面 ID：21660162
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/AdvertisingService+Flow)
> 摘要檔：[processed/21660162-summary.md](../../confluence/processed/21660162-summary.md)
> Confluence 最後更新：2025-05-15
> 摘要最後同步：2026-05-26

**摘要**：
本文件以 PlantUML 序列圖說明 AdvertisingService 新增、更新及查詢廣告的完整流程。新增與更新廣告時，圖檔上傳由 AdvertisingService 負責驗證格式與上傳，再透過 PriceBackendService 進行資料的新增或更新；查詢廣告提供兩種路徑：Client 可直接呼叫 AdvertisingService，BackendTools 則需經過 PriceBackendService 轉送。

**關鍵設計決策**：
- 新增/更新廣告流程：圖檔上傳成功後，才能執行廣告資料的寫入操作，兩個步驟解耦。
- AdvertisingService 負責產生廣告資料 ID，而非依賴 DB 自動生成。
- 提供兩套取得廣告的介面：面向終端用戶（Client）的直接查詢，與面向內部工具（BackendTools）的間接查詢。

**影響範圍**：
- 影響廣告管理的實作流程，特別是檔案上傳與資料寫入的順序。
- ⚠️ PlantUML 中「Clint」應為「Client」筆誤，需人工確認正確的調用方名稱。

---

### TCZB-3746 [AdvertisingService] - 電子佈告欄服務

> Confluence 頁面 ID：76546672
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=76546672)
> 摘要檔：[processed/76546672-summary.md](../../confluence/processed/76546672-summary.md)
> Confluence 最後更新：2025-06-02
> 摘要最後同步：2026-05-27

**摘要**：
本文定義了體育電子佈告欄的技術設計，包含 Cassandra 儲存、Redis 快取與完整 CRUD API。重點在於多語系內容的強制性驗證、公告方式對欄位可見性的控制，以及快取查詢參數的資料來源切換。

**關鍵設計決策**：
- 採用 Cassandra 為主存儲，Redis 為快取，加速頻繁查詢。
- 多語系內容以 map<text,text> 儲存，並強制驗證 zh-CN、en-US、zh-TW 三個 key 不得為空。
- API 路徑前綴為 /advertisingservice/api/sport/bulletinboard/...。
- 公告方式 (announcementmethod) 為 1（靠中）、2（靠右）、3（三個內容區塊）。
- 僅當 announcementmethod == 3 時，text2 和 text3 才允許有值。
- 更新公告時，不可修改 aid、announcementmethod、addtime、sequence。
- 查詢公告支援 cache 參數：true（預設）從 Redis 讀取，false 從 Cassandra 讀取。

**影響範圍**：
- 影響體育電子佈告欄的資料模型、API 驗證邏輯和快取策略。
- ⚠️ sequence 欄位的排序邏輯和快取失效策略未明確定義，需人工確認。

---

### TCZB-2999 [AdvertisingService] - 球王廣告API

> Confluence 頁面 ID：55574773
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55574773)
> 摘要檔：[processed/55574773-summary.md](../../confluence/processed/55574773-summary.md)
> Confluence 最後更新：2023-10-24
> 摘要最後同步：2026-05-27

**摘要**：
本文件為球王站台廣告API設計，使用Cassandra儲存、Redis快取，提供廣告CRUD與圖片上傳API。廣告由區域(AdArea)和語系(SupportLangs)區分，並依Enabled狀態和有效期管理。

**關鍵設計決策**：
- 廣告由 AdArea 區分區域，每個區域多筆廣告由 Seq 排序。
- 僅 Enabled=1 的廣告應存入 Redis 快取；更新為 0 時，必須從 Redis 移除。
- 廣告有 StartDate 和 CloseDate，展示時需考慮有效期。
- 圖片需透過上傳 API 取得檔名後，設定於 ImgPath 欄位。

**影響範圍**：
- 影響球王站台的廣告查詢效能和資料一致性邏輯。
- ⚠️ 文件位於舊的 Sprint，可能已過時，需人工確認 API 與 DB 現狀。
- ⚠️ 未說明圖片儲存實體位置，實現時需確認。

---

## 歷史決策類

### TCZB-878 [AdvertisingService] - 廣告api

> Confluence 頁面 ID：21660158
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=21660158)
> 摘要檔：[processed/21660158-summary.md](../../confluence/processed/21660158-summary.md)
> Confluence 最後更新：2021-06-29
> 摘要最後同步：2026-05-27

**決策背景**：
早期定義廣告服務的 API 與資料庫結構，奠定了基本功能框架。

**決策結論**：
- 廣告展示依 seq 降冪排序。
- 廣告狀態 (enabled) 0 為關閉，1 為開啟。
- 取得廣告時傳入 Type 參數篩選。
- createdby 欄位區分 'promotion'（自家優惠）與 'advertising'（客戶廣告）。
- DB 主鍵 id 採用 text 類型，API 用 POST 進行新增/修改。

**影響**：
- 影響舊版 API 和廣告表結構的設計。
- ⚠️ 文件更新於 2021 年，API 與 DB 欄位可能已有變動，需人工確認。
- ⚠️ DB 欄位 starttime 與 closetime 為 text 類型，非標準時間格式，需確認轉換邏輯。

---

### FrontEndSite .NET Core Adv API Document

> Confluence 頁面 ID：21660236
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/FrontEndSite+.NET+Core+Adv+API+Document)
> 摘要檔：[processed/21660236-summary.md](../../confluence/processed/21660236-summary.md)
> Confluence 最後更新：2021-06-24
> 摘要最後同步：2026-05-26

**決策背景**：
為 FrontEndSite (.NET Core) 定義一個用於取得廣告資料的後端接口。

**決策結論**：
- 採用 HTTP GET /adv/advertisingData 端點，接受 type 參數。
- 回應模型統一包含 Type, Title, Path, Url, Seq 五個字串欄位。
- 此 API 作為 BFF (Backend For Frontend)，轉發請求至後端廣告服務。

**影響**：
- 影響 .NET Core 前端站點的廣告資料來源。
- ⚠️ 文件為 2021 年建立，API 或模型欄位可能已變更或擴充，實際串接時需確認。

---

### [FrontEndSite] 廣告api

> Confluence 頁面 ID：21660227
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=21660227)
> 摘要檔：[processed/21660227-summary.md](../../confluence/processed/21660227-summary.md)
> Confluence 最後更新：2021-06-25
> 摘要最後同步：2026-05-27

**決策背景**：
定義前端 AdvBar 區塊展示廣告所需的特定 API。

**決策結論**：
- 採用 GET 方法，路由為 GET adv/advertisingData，接受 Type 參數。
- 回應包含排序欄位 Seq 用於前端展示順序。

**影響**：
- 影響舊版前端 AdvBar 區塊的資料取得方式。
- ⚠️ 文件建立於 2021 年，需確認廣告服務 API 是否仍有效，且未說明 Type 參數的合法值。

---

## 操作手冊類

*目前暫無相關操作手冊類的 Confluence 文件摘要。*