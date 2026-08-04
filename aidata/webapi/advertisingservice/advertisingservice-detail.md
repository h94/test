# advertisingservice — DB 操作邊界

> 產出時間：2025-04-03 15:30  
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）  
> ⚠️ AI 產出，需資深工程師審核後生效

---

## ads

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra (keyspace: ads) | owner | Schema：[db/ads.json](../../db/ads.json) · 語意：[db/ads-detail.md](../../db/ads-detail.md) |

### 寫入限制

- **advertising**  
  - `id`：主鍵，由應用層生成（生成規則見 CreateAd 的 HashKey），API 不可傳入自訂值。  
  - `createdby`：僅 CreateAds API 可寫入，UpdateAds 禁止修改。  
  - `enabled`：僅能由啟用/停用 API 變更（如 `POST /enable` / `POST /disable`），不允許一般 UPDATE 直接設定。  
  - `starttime` / `closetime`：必須為 Unix 時間戳（秒級），且 `starttime < closetime`；若 `closetime` 早於當前時間，新增時應拒絕。  
  - `lang`：支援的語言代碼字串，以 `&` 分隔（如 `zh-TW&en-US`），須符合系統預定義清單；禁止寫入未定義代碼或空值以外的非法代碼。  
  - `seq`：同一 `type` 下不可重複（避免排序不確定），更新時須確保不衝突。  
  - `path`：廣告圖片路徑，由圖片上傳 API（UploadImgFile）回傳並寫入，後台不可手動填入；存放位置僅限指定儲存區域。  
  - `action`：廣告行為（如 `blank` 表新視窗），僅後台可設定，須為系統支援的枚舉值。  
  - `type`：廣告類型（如 `right`），需對應既有顯示區域，不可隨意填充。

- **advertising_sport**  
  - `adarea`：分割區鍵（Partition Key），建立後不可變更。  
  - `id`：Clustering Key，由系統自動生成（UUID v4），建立請求不可傳入。  
  - `closedate` / `startdate`：必須符合日期字串格式 `yyyy-MM-dd`，不接受時間戳或時區偏移；且 `startdate ≤ closedate`，否則拒絕。  
  - `supportlangs`：List<text>，寫入時需**全量覆蓋**（非增量），每個元素須為有效語言代碼（如 `zh-TW`）。  
  - `imgpath` / `mobileimgpath`：圖片路徑，由圖片上傳相關 API 寫入；`mobileimgpath` 可為空。  
  - `adclass`：廣告分類（如 `self`），須為系統預設分類，不可任意填值。  
  - `enabled`、`seq`：同 `advertising`，僅特定 API 可變更，且需確保 `seq` 在分區內不重複。  
  - `tageturl`：目標網址，應經過合法 URL 校驗，禁止寫入惡意連結。

- **bulletinboard_sport**  
  - `aid`：分割區鍵，建立後不可修改。  
  - `addtime`：建立時自動填入當前伺服器時間戳（Unix 秒），API 不得傳入。  
  - `lastup_time`：系統自動記錄最後更新時間，API 不可覆寫。  
  - `announcementmethod`：僅接受 `1`、`2`、`3`，非法值拒絕。  
  - `status`：狀態變更須遵循合法流程（建議僅允許 `0→1`，禁止逆向轉換）；後台操作需審核。  
  - `maintopic`：Map<text,text>，key 為語言代碼（`zh-TW`、`zh-CN`、`en-US` 等），建立時**必須**包含 `zh-TW`、`zh-CN`、`en-US` 三個 key。  
  - `text1`：同上，建立時 key 必須包含 `zh-TW`、`zh-CN`、`en-US`。  
  - `text2` / `text3`：僅在 `announcementmethod=3` 時有效，此時也必須提供多語言內容（key 要求同 `text1`）；其他模式可為 null 或不提供。  
  - `starttime` / `endtime`：格式化字串 `yyyy-MM-dd HH:mm:ss`，必須校驗格式正確、`starttime ≤ endtime`，且時區應與系統一致（建議 GMT+8）。  
  - `sequence`：排序序號，僅後台可調整，須確保同區域不重複。  

### 讀取規則

- **advertising 查詢**  
  - 一般展示 (GetAdsData, GetEnabledAds) 僅回傳 `enabled=1` 且 `starttime ≤ 當前時間戳 < closetime` 的記錄。  
  - 後台管理 API 可豁免 `enabled` 過濾。  
  - 語言過濾：`lang=""` 表示全語言；非空則檢查 `lang.IndexOf(請求語系) != -1`，因使用字形比對，前端應傳入完整語系代碼以避免假陽性（如 `en` 可能匹配 `en-US`，應避免）。  
  - 排序：依 `seq` 降冪（DESC）。  
  - 效能提醒：查詢常帶 `enabled`、`type` 等非主鍵條件，可能觸發 Cassandra `ALLOW FILTERING`；高流量時應考慮加二級索引或快取。

- **advertising_sport 查詢**  
  - 依 `adarea` 分區讀取 (GetAreaAdvertisements)。  
  - 僅回傳 `enabled=1` 且 `startdate ≤ 當天日期字串 ≤ closedate`（日期比較依字串字典序，因此 `yyyy-MM-dd` 格式與 GMT+8 時區務必一致，避免誤判）。  
  - 語言過濾：若傳入語言參數，篩選 `supportlangs CONTAINS 指定語言`；否則回傳所有。  
  - 排序：依 `seq` 降冪。

- **bulletinboard_sport 查詢**  
  - 對外公告 (GetAnnouncement) 僅回傳 `status=1` 且 `starttime ≤ 當前時間字串 ≤ endtime`（字串比較，時區需一致）。  
  - 管理端查詢可不過濾 `status`，但仍需考慮時效範圍。  
  - 排序：預設依 `addtime` 降冪或 `sequence` 升冪（視業務需求）。  
  - 多語言內容依請求的語言選擇對應的 `maintopic`、`text1` 等欄位。

### 不可回傳欄位

- **advertising**：`createdby` — 建立者資訊不對一般客戶端暴露，僅限後台使用。  
- **advertising_sport**：無（所有欄位公開展示）。  
- **bulletinboard_sport**：無（公告內容為公開資訊）。

---

## sport

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport MySQL | reader | Schema：[db/sport.json](../../db/sport.json) · 語意：[db/sport-detail.md](../../db/sport-detail.md) |

### 寫入限制

- 本服務對 Sport 資料庫僅有讀取權限，不執行任何 INSERT / UPDATE / DELETE。所有資料異動均由 SportService 或其他對應服務負責。

### 讀取規則

- **BK_SitePlayers**  
  - 業務用途：取得特定站點、賽季、聯賽的球員資訊，作為廣告關聯展示（例如球星代言廣告）。  
  - 過濾條件：`Site` 須為有效站點（必填）；可依 `Year` 指定賽季，若未提供則預設取最新；可選 `League` 縮小範圍。  
  - 建議：加上 `LIMIT` 控制回傳筆數；查詢可分頁以避免加載大量資料。

- **ChatRoomHistories_Backup**  
  - 業務用途：判斷聊天室活躍度以決定是否投放廣告（例如熱門聊天室顯示高價值廣告）。  
  - 過濾條件：`AddTime` 必須限定在最近 N 小時內（如 24 小時）；`GID` 必須明確指定，禁止全表掃描。

- **Community_Groups**  
  - 業務用途：取得廣告可顯示的群組版位，需排除非公開或已停用的群組。  
  - 過濾條件：`Enabled = 1`；`GType` 排除 `personal` 或其他非業務類型。  
  - 排序：依 `Seq` 順序，前端再依需求排序。

- **GameUsers_Wallet**  
  - 業務用途：查詢用戶錢包餘額，用於判斷是否顯示須付費才能看到的廣告（例如餘額為 0 時隱藏 VIP 廣告）。  
  - 過濾條件：**必須**以 `AuthKey` 為查詢條件，禁止無條件查詢。僅讀取 `Balance` 欄位，不回傳其他資訊。

- **GameUsers_Wallet_Transactions**  
  - 本服務不直接讀取此表，若需交易相關資訊，應透過 SportService 提供的業務 API 獲取。

- **Notification_Messages**  
  - 業務用途：取得廣告推播用的通知範本內容。  
  - 過濾條件：`Enabled = 1`，且根據請求語系選擇對應的內容欄位（如 `TW_Content`、`EN_Content`）。`TID`、`ID` 用於內部查詢，不對外暴露。

### 不可回傳欄位

- **GameUsers_Wallet**：`AuthKey`、`Balance` — 敏感金流與身份資訊，禁止直接回傳給客戶端。  
- **GameUsers_Wallet_Transactions**：`AuthKey`、`Amount`、`TypeInfo` — 含用戶帳號及交易細節，不得對外暴露。  
- **Notification_Messages**：`TID`、`ID` — 內部模板識別碼，不應洩漏。  
- **ChatRoomHistories_Backup**：`Account`、`GID` 原始值 — 若需對外回傳，應去識別化或使用代號。

---

## Redis

> 本服務未使用 Redis，所有資料均直接讀寫 Cassandra 或 MySQL。  
> 無 Redis Key / TTL 定義。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 廣告圖片/資源儲存 | StorageService (或 CDN) | 本服務僅儲存圖片路徑 (`path`, `imgpath`, `mobileimgpath`) 與點擊 URL (`url`, `tageturl`)，不處理圖片上傳、壓縮、搬移。 |
| 廣告點擊統計、曝光追蹤 | AnalyticsService | 本服務不處理點擊計數、曝光事件、轉換率，僅提供廣告展示資料。 |
| 公告多語言渲染、前端轉譯 | Frontend | 本服務以 Map 形式儲存多語言文字 (`maintopic`, `text1` ~ `text3`)，前端依當前語系選擇顯示文案。 |
| 日期時間時區轉換 | Client / API Gateway | `starttime` / `closetime` 以 UTC 時間戳傳入；`startdate` / `closedate` 以 GMT+8 日期字串傳入；服務端不進行時區換算。 |

---

## 常見錯誤

- ❌ 建立廣告時未檢查 `starttime < closetime`，導致顯示時間區間異常。  
  → ✅ 新增與更新均須校驗時間順序，若無效應拒絕請求。

- ❌ 修改 `seq` 時未判斷同 `type` 下的重複值，導致排序錯亂。  
  → ✅ 更新前先查詢當前最大 `seq`，確認唯一性或提示衝突。

- ❌ 針對 `advertising_sport` 更新 `supportlangs` 時使用增量添加（如 `push`），實際 Cassandra List 為全量替換。  
  → ✅ 寫入時應傳入完整 List，前端或中介層先讀取現有資料後合併再寫入。

- ❌ 公告 `status` 狀態從 `1` 直接回退到 `0`（已公告→未公告），違反業務邏輯。  
  → ✅ 狀態機應限制只允許順向轉換（如 0→1）；回退應由管理端審核或使用刪除操作。

- ❌ 對 `bulletinboard_sport` 查詢時未過濾 `starttime` / `endtime`，導致已過期或未生效的公告被展示。  
  → ✅ 所有對外查詢均需加上時間範圍條件；管理後台可選擇不過濾。

- ❌ 廣告讀取使用 `IndexOf` 進行語言比對，可能出現部分匹配假陽性（例如 `en` 匹配到 `en-US`）。  
  → ✅ 前端應傳遞完整語言代碼（如 `en-US`），或服務端改用精確拆分比對，避免誤判。

- ❌ 廣告服務直接對 Sport 資料庫執行全表掃描（例如查詢所有用戶錢包餘額）。  
  → ✅ 必須依據索引欄位進行查詢（如 `AuthKey`），並限制返回筆數；高頻查詢可要求 SportService 提供專用 API。

- ❌ 讀取 `Community_Groups` 時未過濾 `Enabled`，導致已停用群組仍顯示廣告。  
  → ✅ 任何對外展示查詢必須加上 `WHERE Enabled = 1`。

- ❌ 廣告服務內部直接修改 Sport 資料表（如手動更新用戶餘額）。  
  → ✅ 所有寫入操作應透過 SportService 的 API 進行，禁止廣告服務操作 Sport DB。