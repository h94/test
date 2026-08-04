# leaderboardsite — DB 操作邊界

> 產出時間：2025-01-22 12:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member keyspace | reader / writer | Schema：[db/member.md](../../db/member.md) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **gameusers.authkey**：僅系統產生，任何 API 不可直接修改。
- **gameusers.password**：須透過 `ChangePassword` API，需舊密碼驗證；禁止明文儲存，須使用雜湊演算法。
- **gameusers.rank**：僅管理員可修改；rank=1 代表管理員權限。
- **gameusers.account**：註冊後不可修改，作為用戶唯一識別。
- **gameusers.email**：註冊時須檢查 `forbidden_email_domains`，禁止使用黑名單網域。
- **gameusers.status**：涉及帳號啟用/凍結，僅管理員可操作。
- **gameusers.memberships**：會員資格列表，須與訂閱記錄 `gamesublogs` 同步更新。
- **gameusers.focus_account / follow_account / black_account**：僅用戶本人可修改自己的社群關係列表，須透過對應 API 進行增刪（如 Follow / Unfollow / Blacklist），不可直接全量設定列表值。
- **gameusers.renamecount**：僅在使用者成功更名時由系統內部遞增，不允許 API 直接設定。
- **gameusers.showcode**：由系統自動生成，API 不可寫入。
- **gameusers.signindate / signindays**：由簽到服務維護，本服務僅讀取用於展示，不可由一般 API 修改。
- **gameusers.lastchecktime / lastactiontime**：系統自動更新（如後台定時任務或活動觸發），禁止手動寫入。
- **gameusers.headshotpath**：由媒體服務處理頭像上傳後回傳路徑並寫入，不可由 API 直接指定路徑或覆蓋。
- **gameusers.site / siteid**：第三方登入資訊，僅由 OAuth 服務寫入，API 不可修改。
- **gameusers_banned**：僅管理員可寫入 `description`、`endtime`、`addtime`；`authkey` 須為合法用戶；`cost` 與 `deducted` 由系統計算並執行，不可由管理員或用戶直接修改。
- **forbidden_email_domains**：僅管理員可新增/刪除域名；一般用戶無寫入權限。
- **gamerobots**：僅系統後台服務可管理 `account` 與 `enabled` 狀態，本服務僅作為讀取驗證（如判定是否為機器人）。
- **gamesublogs**：`authkey`、`subtime`、`tradeno`、`addtime` 為複合主鍵，僅由訂閱支付服務（或內部定時任務）寫入；本服務僅讀取 `autosub`、`subendtime` 等欄位；`paymethod`、`paytype` 等支付細節不應由對外 API 修改。
- **appleinfos_game**：僅第三方 OAuth 服務寫入 `id`、`email`、`name`；本服務僅關聯查詢。
- **gameusers_recommend**：`status`、`authkey`、`regdate`、`recommendaccount` 均由推薦服務寫入，本服務僅讀取；不可由排行榜 API 直接修改推薦狀態。

### 讀取規則

- **登入驗證**：`WHERE authkey = ? AND account = ?`，需同時匹配認證金鑰與帳號。
- **管理員權限檢查**：`WHERE account = ? AND rank = 1`，僅 `rank=1` 用戶可執行管理操作（`UpdateLeaderboardSetting`、`GetUserLeaderboards` 等）。
- **帳號狀態過濾**：登入時需檢查 `status` 欄位，非啟用狀態（`status != 1`）禁止登入。
- **封禁檢查**：登入前需查詢 `gameusers_banned WHERE authkey = ?`，若 `endtime > now()` 或 `endtime IS NULL`，則拒絕登入。
- **機器人檢查**：登入或排行榜操作前，須查詢 `gamerobots WHERE account = ? AND enabled = 1`，若命中則拒絕服務（防止機器人刷榜）。
- **付費用戶標記**：檢視玩家是否為付費用戶時，查詢 `gamesublogs WHERE authkey = ? AND subendtime > now()`，符合者標記為付費會員。
- **禁止域名檢查**：註冊或修改 Email 時，須查詢 `forbidden_email_domains` 全表，確認域名未被禁用。
- **排行榜瀏覽量統計**：`GetUserLeaderboards` 或排行榜展示相關邏輯會讀取 `gameuserviews` 與 `gameuserviewsv2`，須以 `account = ?` 過濾當前用戶；必要時可加入 `year`、`gtype` 等條件。
- **個人資料查詢**：查詢 `gameusers` 時須確保不帶出 `password`、`authkey` 等敏感欄位；可使用 DTO 或投影查詢僅選取必要欄位。
- **關注/粉絲列表讀取**：返回給用戶個人資料時，僅可回傳列表的數量或精簡資訊，不可回傳完整帳號清單（除非是查詢自己）。

### 不可回傳欄位

- **gameusers.password**：加密密碼，任何 GET API 禁止回傳。
- **gameusers.authkey**：用戶認證金鑰，僅用於內部驗證，不可對外暴露。
- **gameusers.black_account**：黑名單帳號列表，涉及用戶隱私。
- **gameusers.focus_account / follow_account**：社群關係清單，禁止對外回傳完整列表，僅可回傳統計數量。
- **gameusers.email**：雖為基本資料，但對陌生請求不可暴露；應在授權驗證正確時才回傳給用戶本人。
- **gameusers.site / siteid**：第三方登入資訊，僅內部使用，禁止在對外 API 中回傳。
- **forbidden_email_domains**：完整黑名單清單，僅供內部驗證使用。
- **gamesublogs.tradeno**：交易編號，涉及第三方支付資訊，不對外暴露。
- **gamesublogs.paymethod / paytype**：支付方式與類型，涉及財務敏感資訊，不可在對外 API 中回傳。
- **gameusers_banned.description**：封禁描述內部稽核用，不對帳號本人顯示。
- **gameusers_recommend.authkey**：被推薦人的認證金鑰，不可在 API 回傳中暴露。

---

## leaderboard

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Leaderboard MySQL | owner | Schema：尚未收錄於 `aidata/db` · 語意：尚未收錄於 `aidata/db` |

### 寫入限制

- **users.Password**：僅註冊 API 與 `ChangePassword` 可寫入；須使用雜湊演算法；禁止直接 UPDATE。
- **users.Account**：註冊後不可修改，作為用戶唯一識別。
- **users.Rank**：僅管理員（`rank=1`）可修改；一般用戶無法變更自己或他人的權限等級。
- **users.LastLoginTime**：僅登入 API 可寫入，不可手動更新。
- **charts.Token**：寫入後不可修改（主鍵）；創建時由系統自動生成，不可重複。
- **charts.Account**：寫入時須驗證 `users` 表中存在該帳號，且當前請求帳號與該 `Account` 一致（除非管理員）。
- **charts.Template**：須參照 `templates.ID` 存在，寫入時做外鍵存在性檢查。
- **charts.Animation**：須為合法 JSON 字串，鍵值對格式（鍵為動畫標記，值為動畫 ID）。
- **charts.Style**：自訂 CSS 內容，需過濾 XSS 風險；長度不可超過 `text` 上限。
- **charts.ReloadTime / FlashTime / PreFlashTime**：僅管理員可調整；`ReloadTime` 最小值不得低於 1 秒。
- **chartscontents.Content**：寫入時須為標準 JSON 字串（包含排行榜各項目名稱、排名、分數等）；更新時觸發 Redis 快取清除。
- **animations**：僅管理員可新增/修改；`Name` 長度限制 10 字元，`Style` 須為有效 CSS。
- **templates**：僅管理員可新增/修改；`Name` 長度限制 10 字元；`Layout`、`LayoutContent` 中的 `@content`、`@title`、`@rank` 等佔位符不可遺漏。
- **chartscontents.Updater**：自動填入當前操作者帳號，不可由請求參數指定。

### 讀取規則

- **排行榜顯示（GetLeaderBoardHtmlContent）**：`WHERE Token = ?`，無須過濾 `Account`（所有人可訪問該 Token 的排行榜）；但若排行榜設定為私有（需由 `GetUserLeaderboards` 搭配用戶權限），則前端自行控制。
- **用戶排行榜列表（GetUserLeaderboards）**：`WHERE Account = ?`，僅返回當前登入用戶的排行榜；管理員可透過指定 `Account` 查詢其他用戶的列表。
- **管理員操作（UpdateLeaderboardSetting / UpdateLeaderboardContent）**：須先查詢 `users WHERE Account = ? AND Rank = 1`，確認管理員權限後方可執行。
- **動畫與模板列表（GetAnimations / GetTemplates）**：全表查詢，無權限過濾（所有用戶皆可讀取）。
- **排行榜內容更新時**：讀取 `charts` 與 `chartscontents` 的 `Token` 關聯，確保兩表一致。

### 不可回傳欄位

- **users.Password**：雜湊密碼，任何 GET API 禁止回傳。
- **charts.Token**：為避免安全猜測，管理員列表 API 不可回傳所有 Token；一般用戶僅能取得自己擁有的 Token。
- **users.LastUpdater / charts.LastUpdater**：內部稽核欄位，不對外暴露。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `leaderboard:html:{token}` | `GetLeaderBoardHtmlContent` 時快取渲染後的 HTML | 未明確設定，建議 1 小時（需 code review 確認） |
| DEL | `leaderboard:html:{token}` | `UpdateLeaderboardSetting`、`UpdateLeaderboardContent` 後主動失效 | 確保排行榜更新後立即反映 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 用戶訂閱支付處理 | payment / subscription service | 本服務僅記錄 `gamesublogs`，支付流程由專屬服務負責 |
| 用戶頭像上傳/儲存 | media / storage service | `gameusers.headshotpath` 僅儲存路徑，實際檔案由媒體服務管理 |
| 廣告來源追蹤 | analytics service | `gameusers.adsource` 由外部分析服務寫入，本服務僅讀取 |
| Apple 登入認證 | oauth / identity service | `appleinfos_game` 資料由第三方登入服務寫入，本服務僅關聯查詢 |
| 機器人帳號管理 | admin / system service | `gamerobots` 的啟用/停用由後台管理服務維護，本服務僅作為驗證參考 |
| 用戶推薦記錄管理 | recommendation service | `gameusers_recommend` 的寫入由推薦服務負責，本服務僅讀取 |
| 用戶瀏覽統計收集 | analytics / statistics service | `gameuserviews` 與 `gameuserviewsv2` 的統計數據由其他服務寫入，本服務僅讀取用於排行榜顯示 |

---

## 常見錯誤

- ❌ 直接 UPDATE `gameusers.password` → ✅ 須透過 `ChangePassword` API，驗證舊密碼並雜湊新密碼。
- ❌ 未檢查 `rank` 就執行管理操作 → ✅ 所有管理 API 須先執行 `checkPermission(authkey)` 驗證 `rank=1`。
- ❌ 註冊時未驗證 `forbidden_email_domains` → ✅ 註冊前須查詢黑名單，拒絕禁用網域。
- ❌ 更新排行榜後未清除 Redis 快取 → ✅ `UpdateLeaderboardSetting` / `Content` 後須 DEL `leaderboard:html:{token}`。
- ❌ 查詢 `gameusers` 時回傳完整物件（包含 `password`） → ✅ 使用 DTO 模式，明確排除敏感欄位。
- ❌ 封禁邏輯僅檢查 `gameusers.status` → ✅ 須同時查詢 `gameusers_banned`，檢查 `endtime`。
- ❌ 允許非管理員修改其他用戶的 `account` → ✅ 用戶僅能查詢/修改自己的資料，除非 `rank=1`。
- ❌ 未過濾 `gamerobots` 就讓機器人存取排行榜 → ✅ 登入或排名操作前須查詢 `gamerobots WHERE account=? AND enabled=1`，命中則拒絕。
- ❌ 新增排行榜時未驗證 `charts.Template` 是否存在 → ✅ 寫入前先查詢 `templates` 表確認 `ID` 有效。
- ❌ `charts.Animation` 欄位寫入非 JSON 字串 → ✅ 寫入前須嘗試解析 JSON，若失敗則拒絕請求。
- ❌ 直接暴露 `charts.Token` 給未授權用戶（如管理員 API 回傳全部 Token） → ✅ 非管理員僅能查詢自己擁有的 Token，管理員查詢時可過濾指定 `Account`。