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

**型別**：`varchar(500)`

**值定義與狀態流轉**：  
無狀態流轉，記錄使用者發送的文字內容（可能包含表情符號）。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 聊天服務 | INSERT | 寫入訊息內容；長度超過 500 字元時必須拒絕，不可截斷 |
| pricecenterservice | SELECT | 唯讀，前端展示 |
| memberservice | SELECT | 唯讀 |
| newlotterysite | SELECT（內部） | 不得回傳至對外 API |

**⚠️ 注意**：
- 訊息內容可能包含 Unicode 表情符號，資料庫連線與欄位編碼須為 `utf8mb4`。
- 寫入前應過濾潛在的 XSS 內容。

---

### ResponseID 欄位

**型別**：`varchar(20)`（可空）

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

**型別**：`varchar(4000)`（可空，逗號分隔帳號清單）

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
可能表示發言者在群組內的等級或訊息優先級。具體值域需人工確認。

**各服務操作明細**：

| 服務 | 操作 | 說明 |
|------|------|------|
| 聊天服務 | INSERT | 寫入等級 |
| pricecenterservice | SELECT | 唯讀 |
| memberservice | SELECT | 唯讀 |

---

### UserName 欄位

**型別**：`varchar(500)`

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
| 交易服務 | SELECT / UPDATE | 扣款／入帳時 | 精確匹配 |
| pricecenterservice | SELECT | 必須為會員本人查詢，且透過後端驗證身分後帶入 | **僅讀取**；不可掃表或跨使用者查詢 |
| memberservice | SELECT | 需通過身分驗證，用於錢包頁面 | 唯讀 |
| newlotterysite | SELECT（內部） | 統計報表，不得回傳至對外 API | 唯讀 |

**⚠️ 跨服務限制**：
- **任何對外 API 絕對不可回傳 `AuthKey`**，此為內部金鑰，洩漏將造成安全漏洞。
- 查詢錢包相關資料時，必須強制綁定當前登入使用者的 `AuthKey`，不可允許請求方任意傳入。

---

### Balance 欄位

**型別**：`int`

**值定義與狀態流轉**：  
無固定狀態，數值隨交易事件增減。所有餘額變動都必須伴隨 `GameUsers_Wallet_Transactions` 的記錄，並且在**同一交易**中完成。

```
     交易服務
      UPDATE Balance = Balance + Amount（正值增加，負值減少）
         └─ 同時 INSERT 一筆 GameUsers_Wallet_Transactions
```

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| 交易服務 | UPDATE | 原子操作，確保餘額正確 |
| pricecenterservice | SELECT | 會員查詢自身餘額時可回傳（僅限自己的錢包） |
| memberservice | SELECT | 同上，需通過身分驗證 |
| newlotterysite | SELECT（內部） | 統計報表，不可洩漏個人餘額 |

**⚠️ 跨服務限制**：
- `pricecenterservice`、`newlotterysite` **不可直接更新 Balance**，所有金額變動必須透過專用交易 API（由交易服務負責）。
- 對外回傳 `Balance` 時，必須確保請求者只能看見自己的餘額，且後端需記錄查詢日誌。

---

### LastUpdateTime 欄位

**型別**：`timestamp`（自動更新）

**值定義與狀態流轉**：  
由 MySQL 自動機制維護，每次該筆記錄發生任何變更時自動設為 `CURRENT_TIMESTAMP`。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| MySQL | AUTO | 觸發於 UPDATE 操作 |
| pricecenterservice | SELECT | 唯讀，可用於前端顯示「最後更新時間」或快取對比 |
| memberservice | SELECT | 唯讀 |

**⚠️ 注意**：
- 此時間為資料庫系統時間，應確保資料庫時區設定為 UTC。

---

## Table：GameUsers_Wallet_Transactions

### TID 欄位

**型別**：`int`（PK，自增）

**值定義與狀態流轉**：  
無狀態流轉，交易唯一識別碼，由交易服務 INSERT 時自動產生。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| 交易服務 | INSERT | 自動遞增 |
| pricecenterservice | SELECT | 用於查詢個人交易明細，不可跨使用者 |
| newlotterysite | SELECT（內部） | 對帳報表，不可回傳至對外 API |

---

### AddTime 欄位

**型別**：`timestamp`（預設 CURRENT_TIMESTAMP）

**值定義與狀態流轉**：  
無狀態流轉，記錄交易發生時間。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| 交易服務 | INSERT | 自動寫入 |
| pricecenterservice | SELECT | 唯讀，用於排序和篩選日期範圍 |

---

### Amount 欄位

**型別**：`int`

**值定義與狀態流轉**：  
無狀態流轉，記錄交易金額，**正數表示入帳（加錢），負數表示出帳（扣錢）**。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| 交易服務 | INSERT | 寫入正負數值 |
| pricecenterservice | SELECT | 唯讀，展示歷史交易金額 |
| memberservice | SELECT | 唯讀 |

**⚠️ 注意**：
- 前端展示時需根據正負號標示為「存入」或「支出」的格式。

---

### AuthKey 欄位

**型別**：`char(10)`

**值定義與狀態流轉**：  
無狀態流轉，關聯錢包，寫入後不可變更。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| 交易服務 | INSERT | 關聯至對應錢包 |
| pricecenterservice | SELECT | 查詢流水時必須過濾 `AuthKey = 當前使用者` |
| newlotterysite | SELECT（內部） | 內部對帳，不可暴露至對外 API |

**⚠️ 跨服務限制**：
- 任何對外查詢必須強制綁定登入使用者的 `AuthKey`，嚴禁跨帳號查詢他人交易記錄。

---

### TDate 欄位

**型別**：`date`

**值定義與狀態流轉**：  
無狀態流轉，記錄交易日期，供分區統計與查詢過濾使用。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| 交易服務 | INSERT | 寫入當日日期 |
| pricecenterservice | SELECT | 可依日期範圍查詢個人流水，例如 `WHERE AuthKey=? AND TDate BETWEEN ? AND ?` |

---

### Type 欄位

**型別**：`int`

**值定義**：  
⚠️ 以下型別值為推測，需人工與業務確認。

| 值 | 意義 | TypeInfo 說明 |
|----|------|---------------|
| 1 | 下注扣款 | `{"Account":"...","GameType":"BP","GDate":"...","GID":"...",...}` |
| 2 | 贏獎入帳 | 類似結構，`PredictMessage` 標註 `betpool win` |
| 3 | 充值 | 外部支付管道入帳 |
| 4 | 提款 | 轉出至會員指定帳戶 |

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| 交易服務 | INSERT | 寫入交易類型與對應 JSON 明細 |
| pricecenterservice | SELECT | 唯讀，用於前端顯示類別，但回傳時需脫敏（不可暴露其他會員資訊） |
| newlotterysite | SELECT（內部） | 統計用，不可回傳至對外 API |

**⚠️ 注意**：
- `TypeInfo` 中可能包含跨帳號資訊（如對手帳號），`pricecenterservice` 回傳給會員時必須過濾或僅回傳必要欄位。

---

### TypeInfo 欄位

**型別**：`varchar(4000)`（儲存 JSON）

**值定義與狀態流轉**：  
無狀態流轉，交易詳細資訊的結構化字串，內容依 `Type` 不同而變化。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| 交易服務 | INSERT | 寫入相關 JSON |
| pricecenterservice | SELECT | 唯讀，需根據業務過濾後回傳安全內容 |

**⚠️ 注意**：
- 寫入前務必驗證 JSON 格式，避免無效資料。
- 回傳前應移除 `Account` 等可能涉及隱私的欄位，或做脫敏處理。

---

## Table：Notification_Messages

### TID / ID（複合主鍵）

**型別**：`varchar(20)` / `varchar(20)`

**值定義與狀態流轉**：  
無狀態流轉，訊息唯一識別，`TID` 關聯至 `Notification_Topics`，`ID` 為該主題下訊息編號。

```
     pricecentermanage
      INSERT
     (TID, ID) 建立
```

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 説明 |
|------|------|-----------|------|
| pricecentermanage | INSERT / DELETE | 後台新增或刪除訊息 | 唯一寫入者 |
| pricecenterservice | SELECT | 需指定 `TID`，並只回傳啟用的訊息 | 唯讀 |
| memberservice | SELECT | 依 `TID` 查詢，依 `UpdateTime` 排序 | 唯讀 |
| newlotterysite | SELECT（內部） | 必須根據使用者過濾 `TID` 權限 | 唯讀；不可洩漏他人訊息 |

**⚠️ 跨服務限制**：
- `pricecenterservice`、`newlotterysite` **不可 INSERT / UPDATE / DELETE**，僅 `pricecentermanage` 可寫入。
- 查詢時必須提供 `TID`，嚴禁全表掃描。

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

| 服務 | 操作 | 條件／時機 | 説明 |
|------|------|-----------|------|
| pricecentermanage | INSERT / UPDATE | 後台管理 | 唯一寫入者 |
| pricecenterservice | SELECT | 需過濾 `Enabled = 1` | 唯讀 |
| memberservice | SELECT | 同樣須過濾 `Enabled = 1` | 唯讀 |
| newlotterysite | SELECT | 僅回傳啟用訊息 | 唯讀 |

**⚠️ 跨服務限制**：
- 僅 `pricecentermanage` 可變更 `Enabled`，其他服務無寫入權。
- 任何對外 API 查詢訊息時必須預設只抓取 `Enabled=1` 的記錄。

---

### Title 欄位

**型別**：`text`（儲存多語系 JSON，例如 `{"zh-TW":"A","zh-CN":"B","en-US":"C"}`）

**值定義與狀態流轉**：  
無狀態流轉，內容由管理員透過後台設定，支援多語系。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 寫入多語系 JSON，須驗證格式與過濾 XSS |
| pricecenterservice | SELECT | 依使用者語系解析對應標題文字並回傳 |
| memberservice | SELECT | 同上 |
| newlotterysite | SELECT | 唯讀 |

---

### TW_Content / EN_Content / CN_Content / JP_Content / TH_Content 欄位

**型別**：`text`（JP_Content、TH_Content 可為 NULL）

**值定義與狀態流轉**：  
無狀態流轉，分別儲存繁體中文、英文、簡體中文、日文、泰文版本的訊息內容；至少需填寫 `TW_Content`。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 填寫各語系內容，寫入前過濾 XSS |
| pricecenterservice | SELECT | 根據使用者語系選擇對應欄位，若為空則 fallback 到 `TW_Content` 或 `EN_Content` |
| memberservice | SELECT | 同上 |
| newlotterysite | SELECT | 同上 |

**⚠️ 注意**：
- 所有內容欄位不得儲存可執行的腳本，必須在寫入前進行安全過濾。
- 查詢時若使用者語系對應欄位為空，服務端需實作 fallback 策略（例如 `TW_Content` → `EN_Content`）。

---

### UpdateTime 欄位

**型別**：`bigint`（Unix timestamp，秒級）

**值定義與狀態流轉**：  
無狀態流轉，記錄最後更新時間。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| pricecentermanage | UPDATE | 任何訊息內容變更時自動設定 |
| pricecenterservice | SELECT | 唯讀，可用於排序或判斷新訊息 |

---

## Table：Notification_Topics

### ID 欄位

**型別**：`varchar(20)`（PK）

**值定義與狀態流轉**：  
無狀態流轉，主題唯一識別碼，由 `pricecentermanage` 建立時分配。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| pricecentermanage | INSERT | 新增主題 |
| pricecenterservice | SELECT | 唯讀，用於精確查詢 |
| memberservice | SELECT | 唯讀 |

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
| 0 | 停用 | pricecentermanage | 管理員手動停用（停用後其下所有 `Notification_Messages` 也應視為停用） |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 説明 |
|------|------|-----------|------|
| pricecentermanage | INSERT / UPDATE | 後台主題管理 | 唯一寫入者 |
| pricecenterservice | SELECT | 必須過濾 `Enabled = 1` | 唯讀，前端僅顯示啟用的主題 |
| memberservice | SELECT | 同上 | 唯讀 |
| newlotterysite | SELECT | 同上 | 唯讀 |

**⚠️ 跨服務限制**：
- 僅 `pricecentermanage` 可寫入，其他服務無權限。
- 主題停用時，其關聯的訊息即使 `Enabled=1` 也不可對外回傳。

---

### NameMap 欄位

**型別**：`text`（儲存多語系名稱 JSON，例如 `{"zh-TW":"平台活動","en-US":"Platform activities"}`）

**值定義與狀態流轉**：  
無狀態流轉，由管理員設定。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 寫入 JSON，需驗證格式與過濾 XSS |
| pricecenterservice | SELECT | 依語系解析對應名稱 |
| memberservice | SELECT | 唯讀 |

---

### IconPath 欄位

**型別**：`text`

**值定義與狀態流轉**：  
無狀態流轉，主題圖示的 CDN 路徑。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 設定圖示 URL |
| pricecenterservice | SELECT | 唯讀 |

---

### IconColorCode 欄位

**型別**：`text`

**值定義與狀態流轉**：  
無狀態流轉，主題圖示的背景色或輔助色碼（如 `#97b4ff`）。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| pricecentermanage | INSERT / UPDATE | 寫入色碼 |
| pricecenterservice | SELECT | 唯讀 |

---

### Seq 欄位

**型別**：`int`

**值定義與狀態流轉**：  
無狀態流轉，用於前台主題列表的顯示排序。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| pricecentermanage | UPDATE | 調整排序 |
| pricecenterservice | SELECT | 依 `Seq` 排序後回傳 |

---

### UpdateTime 欄位

**型別**：`bigint`（Unix timestamp，秒級）

**值定義與狀態流轉**：  
無狀態流轉，記錄最後更新時間。

**各服務操作明細**：

| 服務 | 操作 | 説明 |
|------|------|------|
| pricecentermanage | UPDATE | 任何欄位變更時自動寫入 |
| pricecenterservice | SELECT | 唯讀 |

---

## Redis

此 DB 目前無直接關聯的 Redis 快取章節（若後續增加，請補充於此）。

---

## 常見錯誤（跨服務）

- ❌ `pricecenterservice` 或 `newlotterysite` 直接寫入 `BK_SitePlayers` → 只有 `gameliveservice` 可以同步寫入選手資料。
- ❌ 對外 API 回傳 `SiteID`、`TeamID`、`Record`、`AuthKey` 等內部欄位 → 可能導致資料外洩或安全漏洞；這些欄位必須在回應前移除或脫敏。
- ❌ `pricecenterservice` 在查詢 `GameUsers_Wallet` 或 `GameUsers_Wallet_Transactions` 時未綁定使用者 `AuthKey` → 將暴露跨帳號的金額資訊；後端必須強制過濾。
- ❌ 停用群組或停用通知訊息未在查詢時過濾 `Enabled=1` → 前台可能顯示不該出現的內容。
- ❌ 聊天訊息寫入超過 `varchar(500)` 限制 → 應在前端或後端攔截並拒絕，不可截斷後存入，避免顯示不完整。
- ❌ `LikeAccount` 寫入未進行帳號存在驗證 → 可能殘留無效帳號或導致髒資料，需在更新時檢查或定期清理。
- ❌ 多語系內容欄位寫入時未過濾 XSS → 可能注入惡意腳本；必須在寫入前進行安全清理。
- ❌ `Community_Groups` 的 `Owner` 欄位被直接 UPDATE → 群組轉移應透過專用 API，並記錄日誌，不可直接修改該欄位。
- ❌ `ChatRoomHistories_Backup` 中的 `HeadShotPath` 儲存非 CDN 的內部路徑 → 可能洩漏伺服器目錄結構；應只允許審查過的 URL。
- ❌ 在沒有指定 `GID` 或 `TID` 的情況下查詢聊天記錄或通知訊息 → 容易造成全表掃描與效能問題；必須強制帶上過濾條件。