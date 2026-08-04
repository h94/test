# mqservice — DB 操作邊界

> 產出時間：2025-04-11 15:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## stock

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Stock MySQL | owner | Schema：[db/stock.md](../../db/stock.md) · 語意：[db/stock-detail.md](../../db/stock-detail.md) |

### 寫入限制

- `Users.Account`：主鍵，註冊後不可更新。
- `Users.Password`：僅註冊／密碼變更 API 可寫入，必須經雜湊（bcrypt 或 SHA-256 加鹽）。
- `Users.AddTime`：註冊時由系統寫入，後續不可修改。
- `Users.LastUpdateTime`：由 DB 自動更新（CURRENT_TIMESTAMP），應用程式不可直接寫入。
- `Users.Enabled`、`Users.Rank`、`Users.SendAction`、`Users.Phone`、`Users.Email`、`Users.ChatID`、`Users.SubEndTime`：可透過管理後台或使用者設定更新，但 `Phone`、`Email`、`ChatID` 更新前須驗證格式。
- `FavoriteBroker.Value`：必須為合法 JSON 陣列，每個元素為券商名稱字串；不得為空陣列，且限制陣列長度（例如 ≤200）防止異常資料。
- `FavoriteStock.Value`：必須為合法 JSON 陣列，每個元素為有效股票代碼格式；限制陣列長度（例如 ≤100）；寫入前驗證 JSON 格式。
- `FavoriteRule.Value`：策略參數，必須是合法 JSON 陣列，結構需與對應 `Rules.Parameter` 定義一致。
- `FavoriteRule.Strategy`：必須是存在於 `Rules` 表的有效 ID，寫入前應進行關聯檢查。
- `FavoriteRule.NeedSend`、`FavoriteRule.FirstMatch`、`FavoriteRule.Industry`、`FavoriteRule.FilterMarket`、`FavoriteRule.Country`：僅可由規則管理 API 寫入；`Country` 預設 'tw'，若未傳入則自動填入。
- `MessageLog.AddTime`、`MessageLog.LastUpdateTime`：`AddTime` 於建立時系統填入，`LastUpdateTime` 由 DB 自動維護，應用層不可手動設定。
- `MessageLog.SendStatus`：只允許發送服務更新狀態，其他模組不得竄改。
- `SubLogs` 整表：本服務僅讀取，所有寫入（`Account`、`AddTime`、`TradeNo`、`SubID`、`SubRank`、`SubTime`、`SubEndTime`）由 SubscriptionService 負責。
- `Rules.ID`：自增主鍵，不可手動寫入。
- `Rules.Parameter`：必須是合法 JSON 陣列，且與 `Indicator` 定義的參數個數一致。
- `Options.Value`：必須是合法 JSON 陣列，配置型資料，寫入時須確保與 `ID` 的唯一性（`ID` 為主鍵）。

### 讀取規則

- **用戶啟用檢查**：任何登入、規則觸發或查詢使用者資料的動作，WHERE 條件必須包含 `Users.Enabled = 1`，停用帳號禁止操作。
- **規則啟用過濾**：讀取觸發規則清單時，僅選取 `Rules.Enabled = 1` 且 `FavoriteRule.NeedSend = 1` 的記錄；停用規則不參與匹配。
- **首次匹配控制**：查詢 `FavoriteRule` 時，若 `FirstMatch = 1` 且已存在成功通知記錄（透過 `MessageLog` 關聯），則排除該規則避免重複發送。
- **訂閱到期過濾**：觸發通知前，必須檢查 `Users.SubEndTime` 是否大於當前時間，已過期會員不可推播。
- **行業／市場篩選**：當 `FavoriteRule.Industry` 或 `FavoriteRule.FilterMarket` 非空時，需與目標股票的所屬行業或市場相符才會觸發。
- **國家關聯查詢**：所有涉及 `FavoriteRule.Country`、`FavoriteStock.Country` 的查詢，預設以 'tw' 為值，若使用者指定國家則以該值為準。
- **訊息日誌查詢**：查詢 `MessageLog` 必須帶入 `Date` 範圍條件，且限制回傳筆數（如 ≤1000 筆），防止全表掃描；應提供 `Account` 及 `SendStatus` 作為可選過濾。
- **自選股查詢**：依 `User` 與 `Country` 過濾，若使用者未指定 `Country`，則預設讀取該使用者所有國家下的收藏；對外回傳時需確認使用者擁有權限。

### 不可回傳欄位

- `Users.Password`：任何對外 API（含管理端）皆不得回傳，僅供內部雜湊比對。
- `Users.Phone`、`Users.Email`、`Users.ChatID`：個人聯絡資訊，對外查詢時必須遮蔽或排除。
- `MessageLog.TargetAddress`：包含完整的 Email、電話號碼或聊天 ID，對外查詢時應遮蔽中間字元（如 `a***@example.com`）或直接省略。
- `MessageLog.MsgContent`：可能包含個股推薦或隱私內容，非必要對外顯示時建議隱藏。

---

## Redis

本服務未使用 Redis。所有資料操作均直接讀寫 Stock MySQL。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 使用者註冊／帳號管理 | UserService | 本服務僅讀取 `users` 表判斷啟用與訂閱狀態，不處理註冊流程 |
| SMS／Email／Telegram 實際發送 | 外部閘道服務（如 AWS SES、Telegram Bot） | 本服務負責產出待發送資料並寫入 `messagelog`，但不負責連線 SMTP 或呼叫 Telegram API |
| 訂閱付費與方案管理 | SubscriptionService | `sublogs` 與 `users.SubEndTime` 由該服務維護，本服務僅讀取 `SubEndTime` 判斷是否過期 |
| 股票行情資料爬取 | StockDataService | `favoritestock` 僅為使用者自選清單，不包含即時股價 |

---

## 常見錯誤

- ❌ 直接在 `messagelog` 中明文儲存 `TargetAddress`（如 Email 或手機）而未遮蔽保護 → ✅ 應僅用於發送記錄，對外查詢時遮蔽中間字元，或透過獨立欄位存取。
- ❌ 寫入 `users.Password` 時未經雜湊處理 → ✅ 密碼須經 BCrypt 或 SHA-256 加鹽再儲存。
- ❌ 讀取 `favoriterule` 時未檢查 `NeedSend=1` 與 `FirstMatch` 條件，導致重複發送或誤發 → ✅ 在 SQL WHERE 子句明確加入發送條件。
- ❌ 未過濾已停用使用者（`users.Enabled = 0`）即觸發規則 → ✅ 所有使用者操作前先檢查啟用狀態與訂閱到期日。
- ❌ 將自增主鍵 `favoritestock.ID` 當作業務編號直接由前端傳入寫入 → ✅ 應由 DB 自動產生，應用層僅插入其他欄位。
- ❌ 寫入 `favoritebroker.Value` 或 `favoritestock.Value` 時未驗證 JSON 格式 → ✅ 必須在前端或後端校驗為合法 JSON 陣列，避免後續解析崩潰。
- ❌ 寫入 `FavoriteRule.Strategy` 時未檢查是否存在於 `Rules` 表，造成孤兒記錄 → ✅ 必須先驗證 `Rules.ID` 存在。
- ❌ 對外查詢 `MessageLog` 時直接回傳 `TargetAddress` 完整資訊 → ✅ 應遮蔽中間字元，或對外結果移除該欄位。
- ❌ 寫入 `FavoriteStock.Value` 時未限制股票代碼數量，導致單筆資料過大 → ✅ 限制陣列長度（例如 ≤100）並檢查每個元素長度。
- ❌ 將 `SubLogs` 視為本服務可寫入的對象 → ✅ `SubLogs` 僅由 SubscriptionService 寫入，本服務只讀取。