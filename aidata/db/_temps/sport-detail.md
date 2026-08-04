# sport DB — 完整使用脈絡

> 產出時間：2025-08-16 02:00
> 欄位結構定義：[sport.json](./sport.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| pricecenterservice | reader | 唯讀，不可執行 INSERT / UPDATE / DELETE；需依摘要規範查詢 |
| pricecentermanage | writer / reader | 對 `Notification_Topics` / `Notification_Messages` / `Community_Groups` 有寫入權限；其餘表僅唯讀 |
| memberservice | reader | 唯讀，查詢聊天記錄、錢包資訊、通知訊息、社群群組、選手資料 |
| gameliveservice | writer / reader | 寫入／讀取 `BK_SitePlayers`（亦可能寫入其他表）；主要為資料同步與排程 |
| mergesite | writer / reader | 後台工具，可對所有表格進行讀寫（含維護性操作） |
| pricebackendservice | reader | 唯讀 |
| gamesettingsite | reader | 唯讀 |
| newlotterysite | reader | 唯讀 |
| webpservice | reader | 唯讀 |

---

## Table：BK_SitePlayers

### Site / SiteID / Year（複合主鍵）

**型別**：`varchar`

**值定義與狀態流轉**：  
無狀態流轉，僅為識別鍵。資料由 `gameliveservice` 同步寫入，建立後不可修改。

```
     gameliveservice
      INSERT
     (Site, SiteID, Year) 建立
```

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gameliveservice | INSERT | 外部賽程資料同步 | 將各來源站點的選手資料匯入 |
| gameliveservice | SELECT | 排程或存在性檢查 | 確認選手是否已存在 |
| pricecentermanage | SELECT | 後台查詢 | 僅讀取，可後續過濾 |
| pricecenterservice | SELECT | 需指定完整主鍵（Site, SiteID, Year） | **僅讀取**；不可進行範圍掃描 |
| memberservice | SELECT | 前台選手頁面 | 唯讀 |
| newlotterysite | SELECT | 選手展示 | 唯讀 |
| mergesite | SELECT / DELETE | 後台工具維護 | 可用於資料清理，但不可在一般業務流程中直接使用 |

**⚠️ 跨服務限制**：
- `pricecenterservice`、`newlotterysite`、`memberservice` **不可執行 INSERT / UPDATE / DELETE**，寫入僅由 `gameliveservice` 或 `mergesite` 負責。
- `SiteID` 為內部識別碼，對外 API 嚴禁回傳。
- 複合主鍵建立後不可修改，若需更新整筆資料請使用 DELETE + INSERT（需審慎）。
- 前端查詢需確保帶入完整的 PK 條件，避免全表掃描。

---

### League 欄位

**型別**：`varchar`

**值定義與狀態流轉**：  
無狀態流轉，僅記錄選手所屬聯盟（如 NBA、WNBA）。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| gameliveservice | INSERT / UPDATE | 同步時寫入 |
| pricecenterservice | SELECT | 唯讀，可作為過濾條件 |
| memberservice | SELECT | 唯讀 |
| newlotterysite | SELECT | 唯讀 |

---

### Name 欄位

**型別**：`varchar`

**值定義與狀態流轉**：  
無狀態流轉，選手名稱。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| gameliveservice | INSERT / UPDATE | 同步時寫入 |
| pricecenterservice | SELECT | 唯讀 |
| memberservice | SELECT | 唯讀 |
| newlotterysite | SELECT | 唯讀 |

---

### TeamID 欄位

**型別**：`varchar`

**值定義與狀態流轉**：  
無狀態流轉，記錄選手所屬球隊的內部代號。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| gameliveservice | INSERT / UPDATE | 同步時寫入 |
| pricecenterservice | SELECT（僅後台） | 唯讀，**不可在對外 API 中回傳** |
| memberservice | SELECT（內部） | 僅內部使用，**不可暴露至前端** |

**⚠️ 跨服務限制**：
- `TeamID` 為內部對應碼，任何對外服務（包含 `newlotterysite`、`pricecenterservice` 的會員端 API）**不得回傳**。

---

### Team 欄位

**型別**：`varchar`

**值定義與狀態流轉**：  
無狀態流轉，選手所屬球隊名稱。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| gameliveservice | INSERT / UPDATE | 同步時寫入 |
| pricecenterservice | SELECT | 唯讀 |
| memberservice | SELECT | 唯讀 |
| newlotterysite | SELECT | 唯讀 |

---

### Record 欄位

**型別**：`mediumtext`（儲存 JSON）

**值定義與狀態流轉**：  
無狀態流轉，存放選手該賽季的完整統計資料（如進球數、助攻、籃板等），每次同步時採**整份替換**方式更新。

```
     gameliveservice
      INSERT / UPDATE（全量替換）
     Record JSON 物件
```

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| gameliveservice | INSERT / UPDATE | 賽後資料同步，唯一寫入者 |
| pricecentermanage | SELECT | 後台查詢，僅內部使用 |
| pricecenterservice | SELECT（內部） | **不可在會員端 API 回傳**，僅管理用途 |
| newlotterysite | SELECT（內部） | 統計報表，嚴禁暴露至前台 |

**⚠️ 跨服務限制**：
- `Record` 內容龐大且可能包含衍生數據，**任何對外會員 API 皆禁止回傳此欄位**；僅限後台或內部服務使用。
- 更新時必須整份 JSON 替換，不可局部修改，避免資料不一致。

---

### LastUpdateTime 欄位

**型別**：`bigint`（Unix timestamp，秒級）

**值定義與狀態流轉**：  
無狀態流轉，記錄最後一次同步時間，由寫入服務自動設定。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| gameliveservice | UPDATE | 同步資料時設為當前時間戳 |
| pricecenterservice | SELECT | 內部監控，可判斷資料新鮮度 |
| newlotterysite | SELECT | 用於快取失效判斷 |
| memberservice | SELECT | 唯讀 |

**⚠️ 注意**：
- 所有服務讀取此時間戳時，建議統一轉換為 UTC 進行比較，避免時區混淆。
- 若欄位值長時間未更新，可能表示該筆資料已無效或同步中斷，需告警。

---

## Table：ChatRoomHistories_Backup

### GID / Account / ID（複合主鍵）

**型別**：`char`（GID 約 10 字元、Account 約 11 字元、ID 約 10 字元）

**值定義與狀態流轉**：  
無狀態流轉，為聊天訊息的唯一識別鍵，寫入後不可修改。

```
     mergesite（或專用聊天服務）
      INSERT
     (GID, Account, ID) 建立
```

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| 聊天服務（mergesite） | INSERT | 使用者發送訊息 | 分配唯一 ID |
| pricecentermanage | SELECT | 後台檢視 | 可查詢任意 GID |
| pricecenterservice | SELECT | 需指定 GID 與 Account（或 ID） | **僅讀取**；必須精確過濾，禁止全表掃描 |
| memberservice | SELECT | 依 GID 查詢群組聊天歷史 | 可加時間範圍 |
| newlotterysite | SELECT（內部） | 監控用途 | 唯讀，不可回傳至對外 API |

**⚠️ 跨服務限制**：
- `pricecenterservice`、`newlotterysite`、`memberservice` **不可執行 INSERT / UPDATE / DELETE**，寫入僅由聊天服務（透過 `mergesite`）負責。
- 任何對外 API 查詢必須綁定特定的 `GID`，嚴禁跨群組查詢或全表掃描。
- `Account` 為內部帳號識別，不可獨立暴露為公開資訊。

---

### AddTime 欄位

**型別**：`bigint`（Unix timestamp，毫秒級）

**值定義與狀態流轉**：  
無狀態流轉，訊息建立時由服務寫入，不可修改。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 聊天服務 | INSERT | 設定訊息時間戳 |
| pricecenterservice | SELECT | 唯讀，用於排序 |
| memberservice | SELECT | 顯示發送時間 |
| newlotterysite | SELECT（內部） | 唯讀 |

---

### Message 欄位

**型別**：`varchar`

**值定義與狀態流轉**：  
無狀態流轉，記錄使用者發送的文字內容（可能包含表情符號）。寫入時長度由應用層限制（建議不超過 500 字元），不可截斷。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 聊天服務 | INSERT | 寫入訊息內容；長度超過限制時必須拒絕 |
| pricecenterservice | SELECT | 唯讀，前端展示 |
| memberservice | SELECT | 唯讀 |
| newlotterysite | SELECT（內部） | 不得回傳至對外 API |

**⚠️ 注意**：
- 訊息內容可能包含 Unicode 表情符號，資料庫連線與欄位編碼須為 `utf8mb4`。
- 寫入前應過濾潛在的 XSS 內容。

---

### ResponseID 欄位

**型別**：`varchar`（可空）

**值定義**：  
可為 `NULL`，表示無回覆對象；若有值，指向同一聊天室中另一訊息的 `ID`，表示此訊息為回覆。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| `NULL` | 獨立訊息 | 聊天服務 | 一般發送 |
| `"某ID"` | 回覆指定訊息 | 聊天服務 | 使用者指定回覆對象時 |

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 聊天服務 | INSERT | 依前端傳入的「回覆對象」寫入 |
| pricecenterservice | SELECT | 唯讀，用於前端顯示引用關係 |
| memberservice | SELECT | 唯讀 |

**⚠️ 注意**：
- 更新或刪除原訊息時，不應連帶刪除 `ResponseID` 指向它的回覆（可保留為「已刪除訊息」顯示）。

---

### LikeAccount 欄位

**型別**：`varchar`（可空，逗號分隔帳號清單，長度由應用層控制）

**值定義與狀態流轉**：

```
     mergesite                    mergesite
      INSERT 空值                  UPDATE（APPEND/REMOVE）
     LikeAccount = NULL ────────→ LikeAccount = "acc1,acc2"
         │                              │
         └──────────────────────────────┘
                  持續更新（點讚／取消）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| `NULL` | 無人按讚 | 聊天服務 | 訊息建立初始值 |
| `"acc1,acc2"` | 按讚帳號清單 | mergesite 後台 API | 使用者點讚時加入，取消時移除 |

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| mergesite | UPDATE | 原子化操作，確保不重複、不殘留無效帳號 |
| pricecentermanage | UPDATE | 管理員清除不當內容時可一併重置 |
| pricecenterservice | SELECT | 唯讀，顯示按讚人數 |

**⚠️ 跨服務限制**：
- `pricecenterservice`、`newlotterysite`、`memberservice` **不可直接寫入 `LikeAccount`**。
- 寫入時需進行帳號存在性驗證（可非同步），避免寫入不存在的帳號。

---

### ChatType 欄位

**型別**：`char(10)`

**值定義與狀態流轉**：

```
     聊天服務                     （無後續變更）
      INSERT
     ChatType = 'text' （不可變更）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| `text` | 純文字訊息 | 聊天服務 | 使用者發送 |
| `system` | 系統訊息（入群、禁言等） | 聊天服務 | 事件觸發 |
| `image` | 圖片訊息 | 聊天服務 | 使用者上傳圖片 |

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 聊天服務 | INSERT | 根據訊息來源寫入對應類型 |
| pricecenterservice | SELECT | 唯讀，可依類型過濾 |
| memberservice | SELECT | 唯讀 |
| newlotterysite | SELECT（內部） | 不得回傳至對外 API |

---

### Rank 欄位

**型別**：`int`

**值定義**：  
可能表示發言者在群組內的等級或訊息優先級。⚠️ 具體值域與業務意義待人工確認。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 聊天服務 | INSERT | 寫入等級 |
| pricecenterservice | SELECT | 唯讀 |
| memberservice | SELECT | 唯讀 |

---

### UserName 欄位

**型別**：`varchar(500)`（實際長度由 schema 定義）

**值定義與狀態流轉**：  
無狀態流轉，記錄訊息發送者的顯示名稱，通常為 `memberservice` 中該帳號的快照，寫入後不再隨會員更名同步更新。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 聊天服務 | INSERT | 寫入使用者當時的暱稱 |
| pricecenterservice | SELECT | 唯讀，用於展示 |
| memberservice | SELECT | 唯讀 |

---

### HeadShotPath 欄位

**型別**：`varchar(500)`（可空）

**值定義與狀態流轉**：  
無狀態流轉，記錄訊息發送者的頭像路徑（快照），僅儲存相對路徑或 CDN URL，不可包含私人上傳目錄結構。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 聊天服務 | INSERT | 寫入頭像路徑 |
| pricecenterservice | SELECT | 唯讀 |
| memberservice | SELECT | 唯讀 |

**⚠️ 注意**：
- `HeadShotPath` 必須為經過審查的 CDN URL，避免洩漏內部檔案系統資訊。

---

## Table：Community_Groups

### ID 欄位

**型別**：`char(10)`（PK）

**值定義與狀態流轉**：  
無狀態流轉，群組唯一識別碼，由 `pricecentermanage` 建立時分配，不可變更。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | INSERT | 建立群組時寫入 |
| pricecenterservice | SELECT | 唯讀，用於精確查詢 |
| memberservice | SELECT | 唯讀 |
| newlotterysite | SELECT | 唯讀 |

---

### Name 欄位

**型別**：`varchar(1000)`（儲存多語系 JSON，例如 `{"zh-TW":"我的個人群組","en-US":"My Group"}`）

**值定義與狀態流轉**：  
無狀態流轉，內容可透過 `pricecentermanage` 更新。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 寫入時須確保 JSON 格式正確，並做 XSS 過濾 |
| pricecenterservice | SELECT | 依使用者語系解析對應文字並回傳 |
| memberservice | SELECT | 依語系顯示 |
| newlotterysite | SELECT | 唯讀 |

**⚠️ 注意**：
- 解析 `Name` 時，若該語系不存在，應 fallback 到 `zh-TW` 或 `en-US`。

---

### Enabled 欄位

**型別**：`int`

**值定義與狀態流轉**：

```
     pricecentermanage         pricecentermanage
      INSERT                    UPDATE
     Enabled=1 ──────────────→ Enabled=0（停用）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 1 | 啟用 | pricecentermanage | 建立時預設，或手動啟用 |
| 0 | 停用 | pricecentermanage | 管理員手動停用 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecentermanage | INSERT / UPDATE | 後台社群管理 | 唯一可修改 `Enabled` 的服務 |
| pricecenterservice | SELECT | 必須過濾 `WHERE Enabled = 1` | **僅讀取**；一般會員不可看見停用群組 |
| memberservice | SELECT | 同上 | 前台組合列表 |
| newlotterysite | SELECT | 必須過濾 `Enabled = 1` | 不可對外顯示停用群組 |

**⚠️ 跨服務限制**：
- 只有 `pricecentermanage` 可修改 `Enabled`，其他服務僅讀取。
- 任何對外 API（包括 `pricecenterservice` 會員端）查詢群組列表時，必須預設只回傳 `Enabled=1` 的記錄，除非請求來自管理後台。

---

### IconPath 欄位

**型別**：`varchar(500)`

**值定義與狀態流轉**：  
無狀態流轉，存放群組圖示的 CDN 路徑，由 `pricecentermanage` 設定。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 上傳圖示後寫入 URL |
| pricecenterservice | SELECT | 唯讀 |
| memberservice | SELECT | 唯讀 |

---

### Seq 欄位

**型別**：`int`

**值定義與狀態流轉**：  
無狀態流轉，用於前台群組列表的顯示排序，數字越小越前面。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | UPDATE | 調整排序 |
| pricecenterservice | SELECT | 依 `Seq` 排序後回傳 |
| memberservice | SELECT | 依排序顯示 |

---

### GType 欄位

**型別**：`char(10)`

**值定義**：

| 值 | 意義 | 由誰設定 |
|----|------|----------|
| `personal` | 個人創建的群組 | pricecentermanage |
| `official` | 官方群組 | pricecentermanage |
| `system` | 系統預設群組 | 後台建立或程式寫死 |

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 建立時設定，後續不建議變更 |
| pricecenterservice | SELECT | 可依類型過濾，唯讀 |
| memberservice | SELECT | 唯讀 |

---

### Owner 欄位

**型別**：`varchar(11)`（可空）

**值定義與狀態流轉**：  
無狀態流轉，記錄群組建立者帳號，建立後不可直接修改（如需轉移應透過專用 API）。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | INSERT | 建立時寫入 |
| pricecenterservice | SELECT | 唯讀，用於判斷管理權限 |
| newlotterysite | SELECT（內部） | 不可對外顯示原始帳號 |

**⚠️ 跨服務限制**：
- `Owner` 不可由一般服務直接 UPDATE；群組轉移必須使用專用的轉移 API，並記錄審計日誌。
- 對外 API 不應直接回傳 `Owner` 原始帳號，可改用暱稱或脫敏顯示。

---

### Description 欄位

**型別**：`text`

**值定義與狀態流轉**：  
無狀態流轉，群組描述文字，由 `pricecentermanage` 寫入，需過濾 XSS。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 寫入群組說明 |
| pricecenterservice | SELECT | 唯讀 |
| memberservice | SELECT | 唯讀 |

---

### UpdateTime 欄位

**型別**：`bigint`（Unix timestamp，秒級）

**值定義與狀態流轉**：  
無狀態流轉，記錄最後更新時間，由寫入服務自動設定。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | UPDATE | 任何欄位更新時一併設為當前時間 |
| pricecenterservice | SELECT | 唯讀，可用於快取更新判斷 |

---

## Table：GameUsers_Wallet

### AuthKey 欄位

**型別**：`char(10)`（PK）

**值定義與狀態流轉**：  
無狀態流轉，為錢包唯一識別金鑰，由帳號系統產生，**嚴禁對外暴露**。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| 交易服務（mergesite 或專用） | SELECT / UPDATE | 扣款／入帳時 | 精確匹配 |
| pricecenterservice | SELECT | 必須為會員本人查詢，且透過後端驗證身分後帶入 | **僅讀取**；不可掃表或跨使用者查詢 |
| memberservice | SELECT | 需通過身分驗證，用於錢包頁面 | 唯讀 |
| newlotterysite | SELECT（內部） | 統計報表，不得回傳至對外 API | 唯讀 |

**⚠️ 跨服務限制**：
- **任何對外 API 絕對不可回傳 `AuthKey`**，此為內部金鑰，洩漏將導致帳號安全風險。
- 寫入 `Balance` 時必須使用樂觀鎖或交易確保資料一致性，禁止直接賦值。

---

### Balance 欄位

**型別**：`int`

**值定義與狀態流轉**：  
用戶的虛擬貨幣餘額（整數，無小數），由交易服務根據 `GameUsers_Wallet_Transactions` 的記錄進行變更，不可由一般服務直接寫入數值。

```
     交易服務                    交易服務
      INSERT 初始值               UPDATE +Amount / -Amount
     Balance=初始額 ──────────→ Balance=新餘額
```

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 交易服務 | INSERT / UPDATE | 依交易記錄調整餘額，需搭配 `GameUsers_Wallet_Transactions` 記錄 |
| pricecenterservice | SELECT | **唯讀**；會員查詢自身餘額時使用 |
| memberservice | SELECT | 唯讀，用於錢包頁面顯示 |
| newlotterysite | SELECT | 內部統計，**不可直接將明細暴露給前端** |

**⚠️ 跨服務限制**：
- `Balance` 的變更必須由交易服務透過專用 API 進行，其他任何服務（包括 `pricecentermanage`）都**不可直接 UPDATE**。
- 對外查詢時需驗證會員身份，且只允許查詢自己的餘額，禁止批次撈取。

---

### LastUpdateTime 欄位

**型別**：`timestamp`（自動設為 CURRENT_TIMESTAMP，預設 UTC）

**值定義與狀態流轉**：  
記錄餘額最後一次變更時間，由 MySQL 自動管理，寫入服務無需手動設定。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 交易服務 | UPDATE（自動） | 每次餘額變更時由資料庫自動更新 |
| pricecenterservice | SELECT | 唯讀，可用於顯示最後更新時間（需轉換時區） |
| memberservice | SELECT | 唯讀 |

---

## Table：GameUsers_Wallet_Transactions

### TID 欄位

**型別**：`int`（PK，自動遞增）

**值定義與狀態流轉**：  
交易唯一序號，由資料庫自動產生，不可修改。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 交易服務 | INSERT（自動） | 寫入交易時由 DB 自動分配 |
| pricecentermanage | SELECT | 後台查詢交易明細 |
| pricecenterservice | SELECT | **唯讀**；會員查詢自身交易歷史時使用 |
| memberservice | SELECT | 唯讀 |
| newlotterysite | SELECT | 內部統計 |

---

### AddTime 欄位

**型別**：`timestamp`（自動設為 CURRENT_TIMESTAMP）

**值定義與狀態流轉**：  
交易發生時間，由資料庫自動設定，不可修改。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 交易服務 | INSERT（自動） | 由 DB 自動產生 |
| pricecenterservice | SELECT | 唯讀，用於顯示交易時間（需轉換時區） |
| memberservice | SELECT | 唯讀 |

---

### Amount 欄位

**型別**：`int`

**值定義與狀態流轉**：  
交易金額（正數為入帳，負數為扣款），由交易服務根據業務邏輯寫入。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 交易服務 | INSERT | 寫入交易金額，並同步更新 `GameUsers_Wallet.Balance` |
| pricecentermanage | SELECT | 後台稽核 |
| pricecenterservice | SELECT | 唯讀，會員可查詢自身交易記錄 |
| memberservice | SELECT | 唯讀 |

**⚠️ 注意**：
- `Amount` 的寫入必須與錢包餘額更新在同一個交易中，確保資料一致性。

---

### AuthKey 欄位

**型別**：`char(10)`

**值定義與狀態流轉**：  
對應的錢包金鑰，表示該交易隸屬的用戶。欄位意義同 `GameUsers_Wallet.AuthKey`。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 交易服務 | INSERT | 寫入對應的 AuthKey |
| pricecenterservice | SELECT | 唯讀，**只能用於驗證會員本人**，不可跨使用者查詢 |
| newlotterysite | SELECT | 內部統計，不可暴露 |

---

### TDate 欄位

**型別**：`date`

**值定義與狀態流轉**：  
記錄交易對應的業務日期（可能與系統時間不同，例如統計用日期）。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 交易服務 | INSERT | 根據業務規則寫入日期 |
| pricecentermanage | SELECT | 後台查詢 |
| pricecenterservice | SELECT | 唯讀 |
| memberservice | SELECT | 唯讀 |

---

### Type 欄位

**型別**：`int`

**值定義與狀態流轉**：  
交易類型代碼。⚠️ **具體列舉值需人工確認**，目前已知包含：
- `1`：預測獲利（betpool profit，參考現有樣本）
- 其他值可能代表充值、提現、投注等，須由業務團隊補充定義。

```
     交易服務
      INSERT
     Type = 對應業務類型
```

| 值 | 意義（推測） | 由誰設定 | 時機 |
|----|------------|---------|------|
| 1 | 預測獎勵 | 交易服務 | 預測活動結算時 |
| ? | 其他（待定義） | 交易服務 | ⚠️ 待人工確認 |

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 交易服務 | INSERT | 根據業務情境寫入正確類型 |
| pricecentermanage | SELECT | 後台查詢 |
| pricecenterservice | SELECT | 唯讀，前端可能根據 Type 顯示不同文字 |
| memberservice | SELECT | 唯讀 |
| newlotterysite | SELECT | 內部統計，不可回傳至對外 API |

**⚠️ 衝突待人工**：
- 現有程式碼或業務規範中可能已有完整的 Type 值映射表，此處為推測，需與開發團隊確認後更新。

---

### TypeInfo 欄位

**型別**：`varchar`（儲存 JSON）

**值定義與狀態流轉**：  
記錄交易的詳細資訊，例如關聯的遊戲編號、預測編號、帳號等，格式為 JSON。內容因 `Type` 而異。

```
     交易服務
      INSERT
     TypeInfo = 結構化 JSON
```

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 交易服務 | INSERT | 寫入相關上下文資訊 |
| pricecentermanage | SELECT | 後台稽核使用 |
| pricecenterservice | SELECT | **不可直接回傳給前端**；前端的交易細節應經過處理或格式轉換 |
| memberservice | SELECT | 內部查詢 |

**⚠️ 注意**：
- `TypeInfo` 中的原始 `Account`、`GID` 等欄位可能包含敏感資訊，對外輸出時必須過濾或遮蔽。
- JSON 結構應有版本控制，避免多版本並存導致解析異常。

---

## Table：Notification_Messages

### TID / ID（複合主鍵）

**型別**：`varchar`

**值定義與狀態流轉**：  
無狀態流轉。`TID` 對應 `Notification_Topics.ID`（主題），`ID` 為訊息唯一識別碼，由 `pricecentermanage` 在建立訊息時分配，不可變更。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecentermanage | INSERT | 管理員後台建立推播訊息 | 寫入 TID 與 ID |
| pricecenterservice | SELECT | 需依 TID 或 ID 精確查詢 | **僅讀取**，禁止無條件掃表 |
| memberservice | SELECT | 前端推播展示 | 唯讀 |
| newlotterysite | SELECT | 內部顯示 | 唯讀 |
| mergesite | DELETE | 後台清理 | 可用於刪除過期訊息 |

**⚠️ 跨服務限制**：
- `pricecenterservice`、`memberservice`、`newlotterysite` 只能 SELECT，不可寫入。
- 查詢時必須帶入有效的 `TID`，避免將不同主題的訊息混雜回傳。

---

### Enabled 欄位

**型別**：`int`

**值定義與狀態流轉**：

```
     pricecentermanage         pricecentermanage
      INSERT                    UPDATE
     Enabled=1 ──────────────→ Enabled=0（停用）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 1 | 啟用 | pricecentermanage | 建立時預設，或手動啟用 |
| 0 | 停用 | pricecentermanage | 管理員手動停用或過期 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecentermanage | INSERT / UPDATE | 後台推播管理 | 唯一可修改 `Enabled` 的服務 |
| pricecenterservice | SELECT | 必須過濾 `WHERE Enabled = 1` | **僅讀取**；停用訊息不應推播給用戶 |
| memberservice | SELECT | 同 pricecenterservice | 唯讀 |
| newlotterysite | SELECT | 需過濾 Enabled = 1 | 不可顯示已停用訊息 |

---

### Title 欄位

**型別**：`text`（儲存多語系 JSON，格式同 `Community_Groups.Name`）

**值定義與狀態流轉**：  
無狀態流轉，推播標題，由 `pricecentermanage` 設定，需經過 XSS 過濾。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 寫入時確保 JSON 格式正確 |
| pricecenterservice | SELECT | 依使用者語系解析顯示 |
| memberservice | SELECT | 唯讀 |

---

### TW_Content / EN_Content / CN_Content / JP_Content / TH_Content 欄位

**型別**：`text`（可空）

**值定義與狀態流轉**：  
分別存放各語系的推播內文。`TW_Content` 為必填（繁體中文），其餘語系可為 NULL（此時前端應 fallback 到 `TW_Content` 或 `EN_Content`）。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 填寫多語系內容 |
| pricecenterservice | SELECT | 依請求語系回傳對應內容；若該語系為 NULL，則 fallback 至 `EN_Content` 或 `TW_Content` |
| memberservice | SELECT | 唯讀 |
| newlotterysite | SELECT | 唯讀 |

**⚠️ 注意**：
- 內容應過濾 HTML/JavaScript，防止 XSS 攻擊。
- 若所有語系欄位皆為空，前端應給予適當提示或隱藏該訊息。

---

### UpdateTime 欄位

**型別**：`bigint`（Unix timestamp，秒級）

**值定義與狀態流轉**：  
記錄訊息最後更新時間，由 `pricecentermanage` 在每次修改時手動或自動寫入。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | UPDATE | 任何內容變更時更新 |
| pricecenterservice | SELECT | 唯讀，可用於判斷快取是否過期 |

---

## Table：Notification_Topics

### ID 欄位

**型別**：`varchar`（PK）

**值定義與狀態流轉**：  
無狀態流轉，主題唯一識別碼，由 `pricecentermanage` 建立時分配，不可變更。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | INSERT | 建立主題 |
| pricecenterservice | SELECT | 可依 ID 查詢主題詳情 |
| memberservice | SELECT | 唯讀 |
| newlotterysite | SELECT | 唯讀 |

---

### Enabled 欄位

**型別**：`int`

**值定義與狀態流轉**：

```
     pricecentermanage         pricecentermanage
      INSERT                    UPDATE
     Enabled=1 ──────────────→ Enabled=0（停用）
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 1 | 啟用 | pricecentermanage | 建立時預設，或手動啟用 |
| 0 | 停用 | pricecentermanage | 管理員停用整個主題（其下訊息亦不顯示） |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecentermanage | INSERT / UPDATE | 後台管理 | 唯一可修改 `Enabled` 的服務 |
| pricecenterservice | SELECT | 必須過濾 `WHERE Enabled = 1` | **僅讀取**；停用主題及其訊息皆不應對外顯示 |
| memberservice | SELECT | 同 pricecenterservice | 唯讀 |
| newlotterysite | SELECT | 需過濾 Enabled = 1 | 不可顯示停用主題 |

---

### NameMap 欄位

**型別**：`text`（多語系 JSON，結構同 `Community_Groups.Name`）

**值定義與狀態流轉**：  
無狀態流轉，存放主題的多語系顯示名稱，由 `pricecentermanage` 設定。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 寫入多語系名稱 |
| pricecenterservice | SELECT | 依語系解析回傳 |
| memberservice | SELECT | 唯讀 |

---

### IconPath 欄位

**型別**：`text`（CDN 路徑）

**值定義與狀態流轉**：  
無狀態流轉，主題圖示 URL，由 `pricecentermanage` 上傳後寫入。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 設定圖示路徑 |
| pricecenterservice | SELECT | 唯讀，用於前端展示 |
| memberservice | SELECT | 唯讀 |

---

### IconColorCode 欄位

**型別**：`text`（例如 `#97b4ff`）

**值定義與狀態流轉**：  
無狀態流轉，主題圖示的輔助色碼。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 設定色碼 |
| pricecenterservice | SELECT | 唯讀，用於前端樣式 |
| memberservice | SELECT | 唯讀 |

---

### Seq 欄位

**型別**：`int`

**值定義與狀態流轉**：  
無狀態流轉，用於主題在列表中的顯示排序。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | UPDATE | 調整排序 |
| pricecenterservice | SELECT | 依 `Seq` 排序後回傳 |

---

### UpdateTime 欄位

**型別**：`bigint`（Unix timestamp，秒級）

**值定義與狀態流轉**：  
記錄主題最後更新時間，由 `pricecentermanage` 維護。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| pricecentermanage | UPDATE | 任何欄位變更時寫入 |
| pricecenterservice | SELECT | 唯讀 |

---

## Redis — SportCache

### NotificationTopics
**Key pattern**：`NotificationTopics`（Hash）

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| GET | pricecenterservice, memberservice 等讀取服務 | 查詢通知主題列表時 | 若快取未命中，則 fallback 至 DB `Notification_Topics` 並重建快取 |
| DEL | pricecentermanage | 當 `Notification_Topics` 表的任何記錄被 INSERT / UPDATE / DELETE 時 | 刪除整個 Hash，確保下次 GET 重建，避免髒數據 |

**⚠️ 注意**：
- 快取為 Hash，field 為 topic ID，value 為 JSON 序列化的主題物件（含 NameMap, IconPath 等）。
- 必須在 DB 變更後主動刪除，不可僅依賴 TTL。
- 重建時應只快取 `Enabled=1` 的主題。

### NotificationMessages_{hashKey}
**Key pattern**：`NotificationMessages_{hashKey}`（Hash，hashKey 通常為 TID）

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| GET | pricecenterservice | 查詢特定主題下的訊息列表 | 若快取未命中，則從 DB `Notification_Messages` 載入並重建 |
| SET（重建時） | pricecenterservice 或 pricecentermanage 的觸發 | DB 更新後清除快取，下次 GET 時重建 | 永久，隨 DB 更新刪除 |
| DEL | pricecentermanage | 當 `Notification_Messages` 表中相對應 `TID` 的記錄有 INSERT / UPDATE / DELETE 時 | 刪除對應 Hash Key，強制重建 |

**⚠️ 注意**：
- Hash 的 field 為 message ID，value 為 JSON 序列化的訊息物件。
- 重建時必須過濾 `Enabled=1` 的訊息，並依 `AddTime` 或 `UpdateTime` 排序。

### SiteMails_{account}
**Key pattern**：`SiteMails_{account}`（Hash）

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| GET | pricecenterservice, memberservice | 查詢指定會員的站內信列表 | 若快取未命中，則從相關資料表查詢並重建 |
| DEL | 站內信服務或 pricecentermanage | 當該會員的站內信有新增、已讀狀態變更時 | 刪除整個 Hash，確保資料最新 |

**⚠️ 注意**：
- 此快取可能與 `member` 或其他模組的站內信共用，需確認跨服務的快取同步機制。

### AppDevices
**Key pattern**：`AppDevices`（Hash）

| 操作 | 由誰執行 | 時機 | 說明 |
|------|---------|------|------|
| GET | 各需要查詢 APP 裝置資訊的服務 | 查詢目前支援的 APP 裝置與版本 | 永久，手動管理 |
| SET | pricecentermanage | 管理員在後台更新 APP 裝置設定時 | 更新 Hash 內的對應 field |
| DEL | pricecentermanage | 管理員移除某裝置設定時 | 刪除特定 field 或整個 Key |

**⚠️ 注意**：
- 此快取為靜態設定，無 TTL，完全由管理後台手動控制。

---

## 常見錯誤（跨服務）

- ❌ **pricecenterservice 或 memberservice 直接寫入 `GameUsers_Wallet.Balance`** → 餘額必須透過交易服務的專用 API 變更，並同時記錄交易明細，確保一致性。
- ❌ **任何服務直接回傳 `AuthKey` 或 `SiteID` 給前端** → 這些為內部敏感欄位，必須在 API 輸出前過濾或加密。
- ❌ **查詢 `BK_SitePlayers` 時未帶入完整主鍵進行全表掃描** → 必須使用 `Site`、`SiteID`、`Year` 三條件精確查詢。
- ❌ **對外 API 回傳 `Record` 或 `TeamID`** → 這些欄位僅限內部使用，前台應使用經過處理的統計摘要。
- ❌ **變更 `Community_Groups.Enabled` 或 `Notification_Topics.Enabled` 後未同步清除 Redis 快取** → 導致前台仍顯示停用資料，必須主動 DEL 相關 Key。
- ❌ **`ChatRoomHistories_Backup` 查詢未限制 `GID`** → 可能導致跨群組資料洩漏，查詢務必帶入 `GID` 條件。
- ❌ **`Notification_Messages` 或 `Notification_Topics` 的查詢未過濾 `Enabled=1`** → 已停用的通知仍會推送給使用者，必須在 SQL 中加上該條件。
- ❌ **`LikeAccount` 更新時未使用原子操作** → 可能導致按讚數不一致或重複，應使用 `APPEND`/`REMOVE` 且確保帳號存在。
- ❌ **`TypeInfo` 中的原始 `Account` 或 `GID` 直接輸出到前端** → 必須進行脫敏或僅輸出必要的展示用欄位。
- ❌ **時區處理不一致**：`bigint` 時間戳（秒或毫秒）與 `timestamp` 欄位混用時，各服務未統一轉換為 UTC 比較 → 導致排序錯誤或過期判斷異常。