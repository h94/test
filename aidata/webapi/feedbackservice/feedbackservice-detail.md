# feedbackservice — DB 操作邊界

> 產出時間：2025-09-26 10:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## feedback

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| feedback (Cassandra) | owner | Schema：[db/feedback.md](../../db/feedback.md) · 語意：[db/feedback-detail.md](../../db/feedback-detail.md) |

### 寫入限制

- **businessmessages.id / feedbacks\_sport.id / feedbacks\_stock.id / questions\_sport.id / questions\_stock.id / topics\_sport.id / topics\_stock.id**：由系統自動生成（UUID 或哈希），所有 API 均不得指定或覆蓋。
- **businessmessages.status**：僅可設定為 `0`（NoReply 未回覆）或 `1`（AlreadyResponded 已回覆）；禁止寫入其他值。
- **feedbacks\_sport.status / feedbacks\_stock.status**：僅可設定為 `0`（NoReply 未回覆）、`1`（AlreadyResponded 已回覆）、`2`（End 已結案）；狀態變更須由後端邏輯依序遞進，不允許跳級或降級（例如從 `0` 直接改為 `2`）。
- **feedbacks\_sport.tid / feedbacks\_stock.tid**：寫入前必須確認對應的 `topics_sport.id` 或 `topics_stock.id` 存在且為啟用狀態（`enabled = 1`），否則拒絕寫入。
- **businessmessages.site**：必須為已定義的站點代碼（如 `sport`、`stock`），寫入時須通過枚舉校驗。
- **businessmessages.datetime / feedbacks\_sport.datetime / feedbacks\_stock.datetime**：由系統於建立記錄時自動填入當前時間，不接受 API 傳入。
- **businessmessages.updatetime / feedbacks\_sport.updatetime / feedbacks\_stock.updatetime**：由系統於任何更新時自動刷新，API 傳入值將被忽略。
- **feedbacks\_sport.problem / feedbacks\_stock.problem**：內容須為 JSON 序列化後的字串列表（每項符合 `{"DateTime":"...","Message":"..."}` 格式）；寫入前須先完成序列化，若反序列化校驗失敗則拒絕寫入。
- **feedbacks\_sport.respcontent / feedbacks\_stock.respcontent**：同理，須為 JSON 字串列表，且僅管理後端可寫入。
- **feedbacks\_sport.adminimgpath**：只能由管理後台 API 更新（`UpdateSportFeedbackMessageRespImage`），普通用戶不可寫入。
- **feedbacks\_sport.imgpath**：僅在使用者建立反饋時可帶入，需為有效的圖片路徑字串列表。
- **topics\_sport.enabled & sort / topics\_stock.enabled & sort / questions\_sport.enabled & sort / questions\_stock.enabled & sort**：僅管理後台 API 有權修改；客戶端查詢介面一律唯讀。
- **topics\_sport.name**：為多語言 `map<text,text>`，寫入時每個 key 必須為合法的語系代碼（如 `zh-TW`），value 為主題名稱字串。
- **questions\_sport.question / questions\_sport.answer**：同樣為多語言 map，寫入規則同上；`questions_stock` 的對應欄位則為純文字，無多語言限制。

### 讀取規則

- **businessmessages**：查詢時必須同時指定 `site` 與 `datetime` 區間（例如某站點某期間的訊息），禁止不帶條件全表掃描。
- **feedbacks\_sport**：所有查詢必須提供 `tid` 作為分割鍵（partition key）；無 `tid` 的查詢（如僅用 `account`）會導致全叢集掃描，禁止此類用法。
- **feedbacks\_stock**：可直接以 `id` 主鍵單筆查詢；若使用 `account` 過濾，應避免大量結果並建議搭配分頁；不可僅用 `status` 等非索引欄位大範圍掃描。
- **topics\_sport / topics\_stock**：取得啟用主題列表時使用 `WHERE enabled = 1 ORDER BY sort ASC`。
- **questions\_sport / questions\_stock**：取得指定主題下的啟用問題使用 `WHERE tid = ? AND enabled = 1 ORDER BY sort ASC`。
- 因資料量小，topics 與 questions 表允許全表讀取（例如後台管理列表），但仍建議帶上 `enabled` 條件以提升效能。

### 不可回傳欄位

- 無。所有欄位均對外開放，但 `email` 屬個人隱私，建議僅在管理端或使用者本人查詢時回傳（此為應用層控制，DB 無強制）。

---

## stock

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| stock MySQL | reader（多數表）；writer（僅 `MessageLog` 由後台轉移任務寫入） | Schema：[db/stock.md](../../db/stock.md) · 語意：[db/stock-detail.md](../../db/stock-detail.md) |

### 寫入限制

- **`MessageLog`**：僅系統內部的「運動反饋轉移」任務可寫入，不允許外部 API 直接 INSERT／UPDATE。
  - `SendStatus` 僅可由系統設定（0 未發送；1 成功；2 失敗），不可由請求參數控制。
  - `Account` 須存在於 `Users` 表（外鍵約束由業務邏輯保證，資料庫無實際 FK）。
  - `Date` 必須填寫當日日期（yyyy-MM-dd），不可跨日寫入歷史紀錄。
  - `AddTime`、`LastUpdateTime` 由系統自動填入，不接受外界指定。
  - `MsgContent` 須為合法 JSON 或純文字訊息，具體格式由內建邏輯定義。
- **`Users`、`FavoriteBroker`、`FavoriteRule`、`FavoriteStock`、`Options`、`Rules`、`SubLogs`**：此服務僅讀取，無寫入權限；任何寫入需求應由對應服務（如 `authservice`、`userprefservice`）處理。
- **`FavoriteBroker.Value`**：須為合法 JSON 陣列字串，陣列元素為券商名稱字串；寫入驗證時需確保可反序列化。
- **`FavoriteRule.Value`**：須為合法 JSON 陣列字串，結構應符合對應策略的參數定義（例如 `["投信","買超","5","1000"]`），驗證失敗則拒絕寫入。
- **`FavoriteStock.Value`**：須為合法 JSON 陣列字串，元素為股票代碼；不可寫入非字串或空陣列以外的格式。
- **`Options.Value`**：須為合法 JSON 陣列字串（如 `["1","2","3","4"]`），寫入時須檢查是否為有效選項列表。
- **`Rules.Parameter`**：須為合法 JSON 陣列字串，對應技術指標所需參數（例如 `["2","2","K"]`），參數個數與型態需符合 `Indicator` 定義。
- **`Rules.Countries`**：須為合法 JSON 陣列字串，元素為 ISO 國家代碼（如 `["tw"]`），不可包含未定義的地區代碼。
- 所有表若包含 `Country` 欄位，寫入時必須為系統支援的國家代碼（如 `"tw"`），預設值為 `"tw"`。
- `Users.Password` 寫入權限不歸本服務管轄，但任何儲存前必須進行不可逆雜湊（由負責服務確保）。

### 讀取規則

- **`Users`**：必須以 `Account` 做主鍵查詢（`WHERE Account = ?`），禁止無條件全表掃描；對外查詢一律加上 `Enabled = 1` 過濾，已停用帳號不可用於業務邏輯。
- **`FavoriteBroker`、`FavoriteRule`、`FavoriteStock`**：查詢時必須指定 `User`（當前登入者），並可選 `Name` 做進一步篩選；不允許跨使用者查詢。
  - `FavoriteStock` 可額外透過 `ID` 精確定位組合；跨組合查詢須避免全表掃描。
  - 所有自選組合查詢僅回傳該使用者的資料，不得洩漏他人設定。
- **`MessageLog`**：任何查詢須同時指定 `Account` 與 `Date` 範圍（例如 `WHERE Account = ? AND Date >= ? AND Date <= ?`），避免全表掃描；`Date` 格式為 `yyyy-MM-dd`。
  - 不允許僅用 `SendStatus` 或 `SendAction` 進行無帳號限定的範圍掃描。
- **`Options`**：一般用於提供下拉選單選項，可全表讀取（資料量小），建議加上 `Enabled = 1` 過濾。
- **`Rules`**：查詢時建議根據 `Type` 或 `Enabled` 過濾（例如 `WHERE Type = '技術面' AND Enabled = 1`）；取得完整規則列表時應限制筆數以利前端顯示。
- **`SubLogs`**：僅能查詢當前使用者（`Account = ?`），不做管理端的批量查詢；若需排序通常依 `AddTime` 降序。
- 所有包含 `Enabled` 欄位的表，讀取時預設帶上 `Enabled = 1` 以忽略已禁用資料，除非後臺管理明確需要查詢全部。

### 不可回傳欄位

- **`Users.Password`**：絕對不可回傳，所有 API（含內部）都必須遮蔽。
- **`Users.Phone`、`Users.ChatID`**：個人通訊資訊，僅在後臺管理或使用者本人查詳情時可揭露，任何 LIST / GET 多筆的 API 必須遮蔽。
- **`Users.Email`**：雖可作為聯絡依據（如反饋回覆通知），但不可在使用者列表類型的 API 中回傳；僅在單筆反饋詳情或後臺檢視時可帶出。
- 其餘表（`FavoriteBroker`、`FavoriteRule`、`FavoriteStock`、`MessageLog`、`Options`、`Rules`、`SubLogs`）無特殊敏感欄位，對應 API 可回傳全部欄位。

---

## sport

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Sport MySQL | reader | Schema：[db/sport.json](../../db/sport.json) · 語意：[db/sport-detail.md](../../db/sport-detail.md) |

### 寫入限制

無。所有 Sport 資料庫中的表僅供 feedbackservice 讀取，該服務不具備任何寫入（INSERT／UPDATE／DELETE）權限。

### 讀取規則

- **`Community_Groups`**
  - 供顯示群組選項時使用。查詢時須帶 `WHERE Enabled = 1`，並按 `Seq` 升冪排序（`ORDER BY Seq ASC`）。
  - 若僅需單一群組資訊，務必以 `ID` 精確查詢，禁止不帶條件全表掃描。

- **`Notification_Messages`**
  - 用於取得通知模板內容（如反饋回覆時附帶系統訊息）。查詢時必須提供 `TID`，且可選 `Enabled = 1` 以過濾有效的模板。
  - 禁止無 `TID` 條件的全表查詢；也不允許只使用 `ID` 而忽略 `TID` 的大範圍掃描。

- **`BK_SitePlayers`**
  - 用於驗證球員、賽季等關聯數據（例如確認運動反饋所屬主題）。查詢時必須同時提供 `Site` 與 `Year`；若鎖定特定球員，應一併帶入 `SiteID`。
  - 由於表中可能存有大量歷史記錄，禁止僅透過 `League`、`Team` 等非索引欄位進行查詢。

- **`ChatRoomHistories_Backup`**
  - 用於讀取聊天室歷史訊息（可能用於回溯與反饋相關的討論）。查詢時必須指定 `GID`（群組 ID），並強烈建議限制 `AddTime` 的時間範圍（例如 `WHERE GID=? AND AddTime>=? AND AddTime<=?`）。
  - 禁止跨群組或無時間範圍的全表掃描，避免影響資料庫效能。

- **`GameUsers_Wallet`**
  - 錢包查詢僅作內部驗證用途（如確認用戶身份關聯）。查詢時必須以 `AuthKey` 精確匹配（`WHERE AuthKey = ?`），不得使用 `Balance` 範圍進行篩選或執行無索引查詢。

- **`GameUsers_Wallet_Transactions`**
  - 交易紀錄查詢，如業務確需關聯交易記錄，必須指定 `AuthKey`，並限定 `TDate` 範圍（例如 `WHERE AuthKey = ? AND TDate >= ? AND TDate <= ?`）。
  - 禁止僅用 `Type` 或 `Amount` 等條件進行無帳號限制的查詢。

- **通用規則**
  - 所有包含 `Enabled` 欄位的表，讀取時預設加上 `Enabled = 1`，除非後臺管理明確需要檢視已禁用資料。
  - 禁止對任何表執行不帶 `WHERE` 條件的全表掃描，即使當前資料量小也應遵循此規範。

### 不可回傳欄位

- **`GameUsers_Wallet.Balance`**：錢包餘額為高度敏感資訊，feedbackservice 的任何 API 皆不得回傳此欄位。
- **`GameUsers_Wallet.AuthKey`**：雖為錢包唯一標識，但對外暴露可能引發安全風險；建議僅於服務內部使用，對外 API 應遮蔽。
- **`GameUsers_Wallet_Transactions.TypeInfo`**：可能內含用戶帳號、遊戲類型等隱私資料，回傳前務必移除敏感欄位或限制僅內部使用。
- **`ChatRoomHistories_Backup.LikeAccount`**：儲存點讚用戶帳號列表，對外回傳時應考量隱私，避免在非必要場景下完整揭露。

---

## Redis

無使用。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 用戶認證與授權 | authservice | 判定請求者身份與權限，feedbackservice 僅接收已驗證請求 |
| 郵件發送 | emailservice | 反饋回覆後的通知郵件由 emailservice 處理 |
| 檔案上傳儲存 | fileservice | 反饋附加圖片（imgpath / adminimgpath）由 fileservice 管理實際儲存 |
| 股票主題 CRUD | stockadmin / stock topic service | 股票端主題與問題管理由獨立後台服務維護 |
| 使用者偏好設定（自選股、規則） | userprefservice | 對應 `favoritebroker`、`favoriterule`、`favoritestock` 的新增／修改／刪除 |
| 使用者資料（Users）CRUD | authservice | stock.Users 表的維護（包含密碼雜湊、個人資訊更新）由 authservice 處理 |

---

## 常見錯誤

- ❌ 在 `feedbacks_sport` 或 `feedbacks_stock` 未指定 partition key（`tid`）即進行查詢 → 應強制前端或後端補上 `tid` 參數，或改用 `id` 主鍵查詢。
- ❌ 直接修改 `status` 值為 `2` 跳過 `1`（已處理）狀態 → 應由後端邏輯依序遞進，不允許外部直接設定。
- ❌ 未檢查 `topics_sport` / `topics_stock` 的 `enabled` 狀態即寫入反饋記錄 → 應先查驗主題有效後再允許寫入。
- ❌ 將 `problem` 欄位寫入非 JSON 序列化格式字串 → 寫入前務必以程式確保格式正確。
- ❌ 從 `stock.users` 讀取後直接回傳 `Password` → 必須攔截該欄位，所有 getUser API 均不可回傳密碼。
- ❌ 查詢 `messagelog` 時未帶 `Date` 條件，導致掃描全表 → 應強制要求日期區間參數。
- ❌ 跨使用者查詢 `FavoriteBroker` / `FavoriteStock` 等自選組合 → 任何對外 API 僅允許查詢當前登入者的資料。
- ❌ 將 `Users.Email` 回傳於使用者列表 API → 應遮蔽，僅在單筆詳情或後台揭露。