# gamesettings DB — 完整使用脈絡

> 產出時間：2025-12-06 10:00
> 欄位結構定義：[gamesettings.json](./gamesettings.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| syncservice | owner / writer / reader | 讀、寫、刪。負責業務帳戶、商家訂閱、遊戲類型設定的同步與維護 |
| gamesettingservice | owner / writer / reader | 讀、寫、刪。核心業務邏輯，後台專用操作入口，所有寫入最終經由此服務 |
| gamesettingsite | owner / reader | 唯讀（透過 gamesettingservice 間接寫入）。提供前台 API，控管帳戶登入與遊戲設定讀取，不得繞過核心服務直接寫入 DB |
| zbaparser | owner / writer / reader | 讀、寫。負責業務帳戶初始化、內部維護與登入前狀態檢查，部分寫入動作須調用內部服務 |
| pricebackendservice | reader | 唯讀。讀取 `gametype_settings` 用於賠率計算，讀取 `businesses` 驗證訂閱有效性 |

---

## Table：businesses

### businesscode 欄位

**型別**：text（主鍵）

**值定義**：唯一業務識別碼，建立後永久不可變更。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gamesettingservice | INSERT | 建立新業務 (CreateBusiness) | 僅能 INSERT，不可 UPDATE |
| syncservice | INSERT | 同步建立業務帳戶 | 同上 |
| zbaparser | INSERT | 初始化業務帳戶 | 同上，在初始流程中寫入 |

**⚠️ 跨服務限制**：
- 任何服務均不得對 `businesscode` 執行 UPDATE；若需變更業務識別碼，應建立新紀錄，不可直接修改。

### authtoken 欄位

**型別**：text

**值定義**：業務 API 認證令牌，須包含過期時間與簽章，**不可由任何服務自行構造**，必須呼叫內部金鑰服務產生。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| syncservice | INSERT / UPDATE | 授權刷新（金鑰輪換） | 透過金鑰服務取得 token 後寫入 |
| gamesettingservice | INSERT / UPDATE | 管理後台 CreateBusiness / UpdateBusiness API | 必須調用內部金鑰服務取得 token，嚴禁以自訂字串寫入 |
| gamesettingsite | 透過 gamesettingservice 間接寫入 | 前端觸發 CreateBusiness / UpdateBusiness | 前端不可直接傳入 token 值；實際寫入由核心服務處理 |
| zbaparser | INSERT / UPDATE | 初始化或金鑰輪換流程 | 同樣須透過金鑰服務獲取 token |
| pricebackendservice | SELECT | 驗證 API 請求 | 以 businesscode 查詢後比對 token，不以此欄位作為查詢條件 |

**⚠️ 跨服務限制**：
- `authtoken` 在任何 GET / 列表 API 中**一律不得回傳**；僅在 token 刷新時作為一次性 Response 回傳。
- 所有服務在寫入此欄位時，**必須呼叫內部金鑰服務**取得合法 token，禁止以自行生成的任意字串寫入。
- 任何前端或外部請求（含 gamesettingsite 的前台）均不可直接指定或修改 authtoken 的值。

### email 欄位

**型別**：text

**值定義**：關聯業務的預設管理員信箱，建立後不可修改。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gamesettingservice | INSERT | 建立業務時設定 | 建立後即不可變更 |
| syncservice | INSERT | 同步建立業務 | 同上 |

**⚠️ 跨服務限制**：
- 任何服務均不得對 `email` 進行 UPDATE，僅 INSERT 時設定一次。
- 此欄位視為隱私資料，一般讀取 API 不應直接暴露（管理後台或特定匯出例外）。

### subenddate 欄位

**型別**：text（格式：`YYYY-MM-DD`）

**值定義與狀態流轉**：

此欄位控制業務訂閱的有效性，每次讀取需根據當前日期進行判斷：

```
     {syncservice / gamesettingservice}          
      UPDATE 設定到期日                         
     subenddate = "2026-12-31"                   
         │
         │ 每次讀取時強制檢查
         ▼
     當前日期 <= subenddate → 訂閱有效，允許服務
     當前日期 > subenddate  → 訂閱過期，拒絕提供任何服務，立即報錯或回傳空資料
```

| 檢查動作 | 意義 | 由誰執行 | 時機 |
|----|------|---------|------|
| subenddate >= today | 有效訂閱 | 所有讀取服務 | 每次查詢該業務時 |
| subenddate < today | 已過期 | 所有讀取服務 | 同上，立即拒絕服務 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| syncservice | UPDATE | 訂閱管理後台 API | 寫入前須驗證日期格式 `YYYY-MM-DD`，且日期不得小於當前日期 |
| gamesettingservice | UPDATE | 透過專屬訂閱更新 API | 同上，由管理後台觸發 |
| gamesettingsite | SELECT | 前台查詢，判斷過期狀態 | **每次查詢必須比對**當前日期，過期則拒絕服務 |
| pricebackendservice | SELECT | 賠率服務驗證 | 同樣須比對過期狀態，過期不得提供賠率數據 |
| zbaparser | SELECT | 內部操作前驗證 | 確保業務仍在訂閱有效期內才進行後續處理 |

**⚠️ 跨服務限制**：
- **zbaparser 與 gamesettingsite 不得直接變更 subenddate**，此欄位僅能由上游訂閱管理系統或 syncservice/gamesettingservice 透過專用流程更新。
- 所有服務讀取 `businesses` 時，**必須**將 `subenddate` 與當前日期比較：過期業務不可提供任何服務，應立即回傳錯誤或空資料。

### subgametypes 欄位

**型別**：list<text>

**值定義**：業務訂閱的遊戲類型代碼清單，僅能包含系統預定義的有效代碼（如 `BK`, `BS`, `FL`, `SC`, `TN`, `HL`, `VB` 等）。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| syncservice | UPDATE | 訂閱管理 API | 寫入前須校驗每個代碼是否為系統支援的合法遊戲類型 |
| gamesettingservice | UPDATE | 更新訂閱的遊戲類型 | 同上，由管理後台觸發 |

**⚠️ 跨服務限制**：
- 寫入時若包含未定義的遊戲類型代碼，可能導致前端無法匹配資源或下游服務查無對應設定，必須在前置校驗中拒絕。
- zbaparser 與 gamesettingsite 不得直接修改此欄位。

### subinprogresssites / subpregamesites 欄位

**型別**：map<text, text>

**值定義**：每個遊戲類型對應的站點清單（JSON 陣列字串）。`subinprogresssites` 用於走地賽事，`subpregamesites` 用於預售賽事。範例：
```
{
  "BK": "[\"1xbet.com\",\"sbo.com\",\"cloudbet.com\"]",
  "BS": "[\"1xbet.com\",\"asc.com\"]"
}
```

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| syncservice | UPDATE | 站點配置管理 API | 寫入前須驗證每個 value 為合法 JSON 陣列，且站點域名有效 |
| gamesettingservice | UPDATE | 更新訂閱站點 | 同上，管理後台操作 |
| pricebackendservice | SELECT | 讀取以過濾可用數據源 | 使用前須解析 JSON 並過濾有效站點 |

**⚠️ 跨服務限制**：
- **zbaparser 不得直接更新這兩個欄位**，站點配置僅能由上游管理系統維護。
- 寫入前必須將每個 value 解析成 JSON 物件進行格式與站點可用性校驗，否則下游服務可能因解析失敗而崩潰。

### extraplaymodes 欄位

**型別**：map<text, text>

**值定義**：擴展玩法模式配置，鍵為玩法識別碼，值為對應的設定（可為 JSON 字串）。範例：`{"playmode_extra": "{\"enabled\":true}"}`

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gamesettingservice | UPDATE | 調用 UpdateBusinessExtraPlayModes API | 寫入前須校驗 map 結構，更新時注意合併邏輯 |
| syncservice | UPDATE | 同步擴展玩法設定 | 同樣須校驗結構 |

**⚠️ 跨服務限制**：
- 其他服務不得直接操作此欄位。

### inplaycount 欄位

**型別**：int

**值定義**：業務允許的走地賽事數量上限，必須為正整數，預設 0 表示無限制（依實際業務邏輯定義）。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| syncservice | UPDATE | 內部同步排程調整上限 | 僅可增量（遞增/遞減），外部 API 不得直接設定全量 |
| gamesettingservice | UPDATE | 管理後台專用設定 API (SetBusinessInplayGame) | 僅能由管理後台操作 |
| zbaparser | SELECT | 檢查比賽數量是否超限 | 超限時拒絕操作或排隊 |
| gamesettingsite | SELECT | 前台顯示訂閱上限資訊 | 僅供讀取，不可寫入 |

**⚠️ 跨服務限制**：
- 任何客戶端 API（包含 gamesettingsite 的前台）**不得直接寫入** `inplaycount`，此欄位僅能由管理後台或 syncservice 變更。

### updatetime 欄位

**型別**：bigint（毫秒時間戳）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| 所有寫入服務 | 自動填充 | 每次 INSERT / UPDATE | 由服務端自動寫入當前時間戳，外部不得傳入或偽造 |

**⚠️ 跨服務限制**：
- 任何服務不得手動設定此欄位，必須由服務端系統時間自動賦值。

---

## Table：business_accounts

### businesscode + account 欄位（複合主鍵）

**型別**：text + text

**值定義**：識別特定業務下的帳戶，建立後不可修改任何一個主鍵部分。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gamesettingservice | INSERT | 建立業務帳戶 | 設定 businesscode 與 account，建立後不可 UPDATE 主鍵；新增必須使用 `INSERT … IF NOT EXISTS` |
| syncservice | INSERT | 同步建立帳戶 | 同上 |
| zbaparser | INSERT | 初始化帳戶 | 同上 |

**⚠️ 跨服務限制**：
- 此為複合主鍵，建立後兩個欄位皆不可透過 UPDATE 修改，僅允許 INSERT 時設定。

### password 欄位

**型別**：text

**值定義**：業務帳戶密碼的雜湊值，**絕對禁止儲存明文**，必須使用 bcrypt 等強雜湊演算法。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| syncservice | INSERT / UPDATE | 同步建立帳戶或變更密碼 | 必須以 BCrypt 雜湊後寫入 |
| gamesettingservice | INSERT / UPDATE | 管理後台建立帳戶或密碼修改 | 同上，寫入前強制雜湊 |
| zbaparser | INSERT / UPDATE | 初始化帳戶或內部變更 | 必須雜湊儲存，禁止明文 |
| gamesettingsite | SELECT | 登入驗證時比對雜湊值 | 僅用於密碼比對，不得直接回傳此欄位 |

**⚠️ 跨服務限制**：
- **password 欄位絕對不可在任何查詢 API 中回傳**，包含列表、詳情、管理後台介面。
- 內部服務之間無論何種場景，皆不得傳輸明文或雜湊後的 password 值（僅限密碼比對流程內部使用）。

### role 欄位

**型別**：text

**值定義**：帳戶角色，例如 `admin`、`operator` 等，決定該帳戶可執行的後台操作權限。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gamesettingservice | INSERT / UPDATE | 管理員變更權限 | 僅具有管理權限的帳戶可修改；變更須記錄操作日誌 |

**⚠️ 跨服務限制**：
- role 僅能由具有管理權限的帳戶透過 gamesettingservice 修改，zbaparser 或 gamesettingsite 不得直接變更。

### status 欄位

**型別**：int

**值定義與狀態流轉**：

```
     {gamesettingservice/syncservice/zbaparser}   {gamesettingservice/syncservice}
      INSERT (status=1)                              UPDATE (status=0)
     value=1（啟用） ────────────────────────────→ value=0（凍結）
         │                                                 │
         └─────── 可重新啟用 (UPDATE status=1) ────────────┘
                    {gamesettingservice 管理操作}
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 1 | 啟用 | gamesettingservice, syncservice, zbaparser | INSERT 時預設值 |
| 0 | 凍結 | gamesettingservice, syncservice | 管理員透過專用 API 停用，或上游同步停用 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gamesettingservice | INSERT status=1 | 建立業務帳戶 | 預設啟用 |
| gamesettingservice | UPDATE status=0 / 1 | 管理員手動停用或重新啟用 | **僅可透過專用 API (UpdateBusinessAccountStatus)** |
| syncservice | INSERT status=1 | 同步建立帳戶 | — |
| syncservice | UPDATE status=0 | 同步停用帳戶 | 上游觸發 |
| zbaparser | INSERT status=1 | 初始化帳戶 | — |
| zbaparser | SELECT WHERE status=1 | 登入或使用帳戶前驗證 | 確保帳戶為啟用狀態 |
| gamesettingsite | SELECT WHERE status=1 | 前台登入驗證與資訊查詢 | 停用帳戶不得登入 |

**⚠️ 跨服務限制**：
- **status=0（凍結）只能由帳戶管理專用 API 設定**，zbaparser 或 gamesettingsite 不得直接修改此欄位。
- 所有查詢 `business_accounts` 的服務**必須**加上 `WHERE status = 1` 條件，防止誤將凍結帳戶當作有效帳戶使用。

### updatetime 欄位

**型別**：bigint（毫秒時間戳）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| 所有寫入服務 | 自動填充 | 每次異動 | 自動寫入當前毫秒時間戳，禁止外部傳入 |

---

## Table：gametype_settings

### company + gametype 欄位（複合主鍵）

**型別**：text + text

**值定義**：標識特定公司下的遊戲類型設定，同一公司、同一遊戲類型僅會存在一筆設定。

**⚠️ 注意**：此組合唯一，建立後不可透過 UPDATE 修改主鍵值；若需調整應採刪除重建。

---

### settings 欄位

**型別**：text（內容為合法 JSON 字串）

**值定義**：包含 `PlayMode`、`Layout`、`SiteSetting`、`RadioCount`、`Rate`、`Places` 等子物件的遊戲設定陣列。結構範例：

```json
[{
  "PlayMode": "HA",
  "Layout": "LayoutOne",
  "SiteSetting": {
    "Mode": "Order",
    "SiteList": ["au8tw.com", "1xbet.com"],
    "SiteRate": null
  },
  "RadioCount": 1,
  "UseSuggest": false,
  "Rate": 1840,
  "RateType": 0,
  "Places": 2
}]
```

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gamesettingservice | INSERT / UPDATE | 後台設定遊戲類別 | 寫入前須驗證為合法 JSON；變更後應通知相關服務刷新快取 |
| syncservice | INSERT / UPDATE | 同步設定 | 資料源同步，同樣需 JSON 校驗 |
| zbaparser | UPDATE | 內部遊戲設定處理 | 寫入時須確保 JSON 結構一致，更新後觸發快取刷新 |
| pricebackendservice | SELECT | 賠率計算時讀取 PlayMode、SiteSetting 等配置 | 用於決定賠率來源與顯示邏輯 |

**⚠️ 跨服務限制**：
- 任何服務寫入 `settings` 前，**必須**進行嚴格的 JSON 格式校驗，避免寫入非法字串導致下游解析崩潰。
- 出於安全與結構可讀性，回傳給前端的 settings 建議由服務端解析後重新組裝，不應直接將原始 JSON 字串暴露。

---

### showstopplaymode 欄位

**型別**：boolean

**值定義**：控制前台是否顯示已停用的玩法模式。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gamesettingservice | INSERT / UPDATE | 管理後台設定顯示行為 | 影響前台過濾邏輯 |

---

### swap 欄位

**型別**：boolean

**值定義**：是否允許主客隊對調（如交換賠率顯示）。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gamesettingservice | INSERT / UPDATE | 管理後台設定交換開關 | 影響前端顯示 |

---

### name 欄位

**型別**：text

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gamesettingservice | INSERT / UPDATE | 建立或變更遊戲類別顯示名稱 | 後台操作 |
| syncservice | INSERT / UPDATE | 同步設定 | — |

---

### updater 欄位

**型別**：text

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| 所有寫入服務 | 自動填充 | 每次異動 | 記錄操作者的帳號，由服務端從語境中提取，不可由外部傳入 |

---

### updatetime 欄位

**型別**：bigint（毫秒時間戳）

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| 所有寫入服務 | 自動填充 | 每次異動 | 自動寫入當前毫秒時間戳，禁止外部傳入 |

---

## Redis — GamesettingsCache

### key pattern：`gamesettings:company:{company}:gametypes`

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| SET | syncservice, gamesettingservice | 初次載入或 gametype_settings 變更後 | TTL 3600s；快取該 company 下所有啟用的 gametype 設定清單 |
| GET | gamesettingsite, pricebackendservice, zbaparser | 需要取得該公司支援的遊戲類別設定時 | 若 cache miss 則 fallback 查詢 Cassandra |
| DEL | syncservice, gamesettingservice, zbaparser | gametype_settings 中任何欄位異動時 | **必須主動清除**，不可只依賴 TTL 過期，避免前台讀到舊版設定 |

**⚠️ 注意**：
- 當 `gametype_settings` 的 `settings`、`showstopplaymode`、`swap` 等欄位變更時，若未即時清除此快取，前台可能繼續顯示舊的玩法配置或站點清單，導致資料不一致。

### key pattern：`gamesettings:game:{id}`

⚠️ **衝突待人工**：此快取對應的 `game_settings` 表未出現在本次 dbSchema 中。若該表實際存在，當 `game_settings` 的任何欄位變更時，必須主動 DEL 對應 key。若表已不存在，請移除本節。

---

## 常見錯誤（跨服務）

- ❌ 任何服務直接以明文寫入 `business_accounts.password` → **正確做法**：必須先經過 bcrypt 雜湊才可儲存。
- ❌ 前端或外部請求直接指定 `businesses.authtoken` 的值 → **正確做法**：token 必須由內部金鑰服務生成，各服務調用金鑰服務後寫入，禁止接收外部傳入的 token。
- ❌ zbaparser 或 gamesettingsite 直接 UPDATE `business_accounts.status` → **正確做法**：只能透過帳戶管理模組（`UpdateBusinessAccountStatus` API）變更。
- ❌ zbaparser 或其他服務直接修改 `businesses.subenddate` → **正確做法**：此欄位僅能由上游訂閱系統或 syncservice/gamesettingservice 更新。
- ❌ 查詢 `business_accounts` 時忘記附加 `WHERE status = 1` → 已凍結的帳戶可能被當作正常帳戶使用，造成安全隱患。
- ❌ 將 `businesses.authtoken` 或 `business_accounts.password` 回傳至任何 API 回應 → 這些機敏欄位在任何場景下都不該暴露。
- ❌ 讀取 `businesses` 後未進行 `subenddate` 過期檢查 → 導致已過期業務仍能取得服務，所有服務必須強制比對 `subenddate` 與當前日期。
- ❌ 寫入 `gametype_settings.settings` 前未驗證 JSON 格式 → 非法 JSON 字串可能導致下游解析崩潰，應在前置校驗中攔截。
- ❌ `gametype_settings` 變更後未清除對應 Redis key → 前台可能持續讀取舊設定，應在異動完成後立即執行 `DEL` 或發佈快取失效訊息。