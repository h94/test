# pricecenter DB — 完整使用脈絡

> 產出時間：2026-06-11 14:24
> 欄位結構定義：[pricecenter.json](./pricecenter.json)
> ⚠️ 此文件由 AI 產出，需資深工程師審核後生效

---

## 服務角色總覽

| 服務 | 角色 | 可執行操作 |
|------|------|-----------|
| pricecenterservice | owner | 讀、寫、刪。帳號建立、密碼雜湊、啟用/停用等完整生命週期管理。 |
| priceclientsystem | owner | 讀、寫。客戶端帳號登入驗證、密碼修改、操作日誌寫入。 |
| tradegameservice | owner | 讀、寫。交易遊戲帳號的驗證、管理、stock_holdings 與 trade_log 寫入、快取管理。 |
| crawlerservice | owner | 讀、寫。爬蟲帳號的自動化管理、啟用/停用。 |
| crawlerflowservice | writer | 讀、寫。爬蟲任務帳號驗證、新增爬蟲帳號、crawler_log 寫入。 |
| flowcontrolservice | writer | 讀、寫。賠率流水線帳號驗證、games/sitegames/odds 資料更新、alertlog/fixdatalog 寫入。 |
| sitegameoddservice | writer / reader | 讀取帳號驗證，特定配置 API 可寫入 handler，讀取 sitegames/games。 |
| mergesite | writer / reader | 合併站點時寫入帳號及日誌，讀取對照資料，更新合併結果。 |
| openclawservice | writer / reader | 帳號驗證讀取，特定管理 API 可寫入。 |
| clientflowservice | writer / reader | 客戶端帳號驗證讀取，管理操作寫入。 |
| crawleragentstandings | writer | 僅寫入 standings 相關表。 |
| gamecombineservice | writer | 遊戲平台帳號整合建立，寫入 odds_{gameType}。 |
| tradegameresultservice | writer / reader | 交易結果結算時的帳號讀取與狀態變更，stock_holdings/result_log 寫入。 |
| zbaparser | writer / reader | ZBA 帳號的管理、啟用/停用。 |
| crawleroddtrend | owner* | 讀取 accounts_* 啟用站台清單；寫入 odds_his_* 歷史賠率。 *(該表 owner) |
| pricebackendservice | reader | 唯讀，後台交易記錄關聯查詢。 |
| pricecentermanage | reader | 唯讀，管理後台報表統計。 |
| pricecentersite | reader | 唯讀，站點設定資料查詢。 |
| newlotterysite | reader | 唯讀，彩券站台帳號驗證。 |
| newlotterybackendservice | reader | 唯讀，彩券後台帳號查詢。 |
| predictservice | reader | 唯讀，預測服務帳號驗證。 |
| pricesubscriptionsystem | reader / writer | 讀取帳號狀態，寫入操作日誌。 |
| zaiservice | reader | 唯讀，主要在 predict 和 member keyspace 操作。 |
| syncservice | writer / reader | 帳號狀態同步讀取，快取管理寫入。 |
| webpservice | writer / reader | 帳號驗證讀取，Redis 快取管理寫入。 |
| gamesettingsite | writer / reader | 站台設定帳號管理，寫入 gamesettings 相關表。 |
| pricecenterresult | writer / reader | 帳號驗證讀取，比賽數據快取管理。 |
| gameliveservice | 無 | 不操作 pricecenter keyspace。 |
| predictresultservice | 無 | 不操作 pricecenter keyspace。 |

*(註：上述角色基於服務摘要中的「資料來源與角色」定義，若服務同時為 owner 則以 owner 標示，否則標示 writer/reader 組合。)*

---

## Table：accounts_{brand}

此為品牌隔離的帳號表群，包含但不限於：`accounts_AU8`、`accounts_Fortuna888`、`accounts_HGA`、`accounts_HGA2`、`accounts_KKK`、`accounts_KU`、`accounts_NK`、`accounts_Panda`、`accounts_TG`、`accounts_TG999`。所有表結構相同，主鍵為 `account`，邏輯上隔離，不可跨表查詢。

### account 欄位

**型別**：text（Primary Key）

**值定義與狀態流轉**：

主鍵，由 `INSERT` 建立後**不可更新、不可刪除**。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 自訂字串 | 唯一帳號識別名稱 | pricecenterservice / tradegameservice / crawlerservice / mergesite | 帳號註冊或建立時 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | INSERT account=值 | 帳號建立 API | 主鍵，一次性寫入 |
| tradegameservice | INSERT account=值 | 交易遊戲帳號建立 | 主鍵，一次性寫入 |
| crawlerservice | INSERT account=值 | 爬蟲帳號建立 | 主鍵，一次性寫入 |
| crawlerflowservice | INSERT account=值 | 新增爬蟲帳號 | 主鍵，一次性寫入 |
| mergesite | INSERT account=值 | 合併站點帳號建立 | 主鍵，一次性寫入 |
| openclawservice | INSERT account=值 | 帳號註冊 API | 主鍵，一次性寫入 |
| clientflowservice | INSERT account=值 | 客戶端帳號建立 | 主鍵，一次性寫入 |
| gamecombineservice | INSERT account=值 | 遊戲平台帳號整合 | 主鍵，一次性寫入 |
| gamesettingservice | INSERT account=值 | 遊戲設定帳號建立 | 主鍵，一次性寫入 |
| gamesettingsite | INSERT account=值 | 站台帳號建立 | 主鍵，一次性寫入 |
| zbaparser | INSERT account=值 | ZBA 帳號初始化 | 主鍵，一次性寫入 |
| webpservice | INSERT account=值 | WebP 帳號建立 | 主鍵，一次性寫入 |

**⚠️ 跨服務限制**：
- `account` 一旦 INSERT 後不可被任何服務的 UPDATE 操作修改。若需變更，必須刪除後重建（由具刪除權限的服務處理）。
- 所有讀取操作必須以 `account` 為主鍵進行精確查詢，禁止全表掃描或以其他欄位（如 phone）進行範圍查詢。

---

### enabled 欄位

**型別**：int

**值定義與狀態流轉**：

```
     pricecenterservice / tradegameservice / crawlerservice
      INSERT (預設)
     value=1 (啟用) ───────────────────────────────────── value=0 (停用)
         │                   管理員/排程 UPDATE                │
         │                                                    │
         └─ 管理員/關閉流程 UPDATE ──────────────→ value=0 & closetime IS NOT NULL (已關閉)
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 1 | 啟用 | pricecenterservice / tradegameservice / crawlerservice / mergesite | INSERT 時預設值；或管理員重新啟用 |
| 0 | 停用 | pricecenterservice / gamesettingservice / tradegameresultservice / zbaparser | 管理員手動停用、系統排程停用、或帳號異常時 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | INSERT enabled=1 | 帳號建立 | 預設啟用 |
| pricecenterservice | UPDATE enabled=0 | 管理員停用 API | 可重新啟用 |
| tradegameservice | INSERT enabled=1 | 遊戲帳號建立 | 預設啟用 |
| tradegameservice | UPDATE enabled=0 | 管理員或排程停用 | 與交易功能掛鉤 |
| crawlerservice | INSERT enabled=1 | 爬蟲帳號建立 | 預設啟用 |
| crawlerservice | UPDATE enabled=0 | 管理員停用 | 任務不可執行 |
| gamesettingservice | UPDATE enabled=0 | 管理員停用 API | `POST /api/business/account/status` |
| tradegameresultservice | UPDATE enabled=0 | 結算流程或管理端 | 帳號異常時停用 |
| gamesettingsite | UPDATE enabled=0 | 管理員停用 | 站台帳號停用 |
| zbaparser | UPDATE enabled=0 | 內部狀態管理 | 帳號異常時停用 |
| openclawservice | UPDATE enabled=0 | 管理員停用 API | 帳號啟用/停用 |
| clientflowservice | UPDATE enabled=0 | 管理員或排程 | 帳號停用 |
| webpservice | UPDATE enabled=0 | 管理員或排程 | 帳號停用 |
| mergesite | INSERT enabled=1 | 合併建立 | 預設啟用 |
| mergesite | UPDATE enabled=0 | 帳號關閉流程 | 關閉後不可再次啟用 |
| syncservice | UPDATE enabled=0 | 同步流程 | 狀態同步至其他系統 |
| pricecentermanage | SELECT WHERE enabled=1 | 管理後台查詢 | 僅顯示啟用帳號 |
| pricecentersite | SELECT WHERE enabled=1 | 站台設定查詢 | 僅顯示啟用帳號 |
| pricebackendservice | SELECT WHERE enabled=1 | 交易記錄關聯 | 僅關聯啟用帳號 |
| crawleroddtrend | SELECT WHERE enabled=1 | 爬蟲任務配置查詢 | 僅取得啟用站台 |
| sitegameoddservice | SELECT WHERE enabled=1 | 帳號驗證 | 驗證時需要 |
| flowcontrolservice | SELECT WHERE enabled=1 | 賠率流水線驗證 | 驗證時需要 |
| openclawservice | SELECT WHERE enabled=1 | 登入驗證 | 驗證時需要 |
| crawlerflowservice | SELECT WHERE enabled=1 | 爬蟲任務驗證 | 驗證時需要 |
| pricecenterresult | SELECT WHERE enabled=1 | 帳號驗證 | 驗證時需要 |
| zaiservice | SELECT WHERE enabled=1 | 帳號驗證 | 驗證時需要 |

**⚠️ 跨服務限制**：
- `enabled=1` 是所有服務進行登入、交易、爬蟲等操作的**必要前置條件**。任何服務的 SELECT 查詢若未過濾此條件，可能導致已停用帳號被誤用。
- `enabled=0` 且 `closetime` 非空代表帳號已關閉，**不可被任何服務重新啟用**。
- 除 `pricecenterservice`、`tradegameservice`、`crawlerservice` 等具管理權限的服務外，其他服務（如 `sitegameoddservice`、`flowcontrolservice`）**不可直接 UPDATE 此欄位**。

---

### closetime 欄位

**型別**：text（格式 `yyyy-MM-dd HH:mm:ss`）

**值定義與狀態流轉**：

當不為空時，代表帳號已被永久關閉。

```
     管理員/關閉流程 UPDATE
      closetime=now() & enabled=0
     value=NULL / '' (正常) ───────────────── value=關閉時間戳 (已關閉，不可逆)
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| NULL / '' | 帳號未關閉 | 預設 | INSERT 時 |
| 時間戳字串 | 帳號已關閉 | pricecenterservice / mergesite / gamesettingservice / tradegameservice / crawlerservice | 管理員關閉帳號或系統排程關閉 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | UPDATE closetime=now() | 管理員關閉帳號 | 同步設定 enabled=0 |
| mergesite | UPDATE closetime=now() | 多站點帳號關閉 | 關閉後不可再次啟用 |
| tradegameservice | UPDATE closetime=now() | 排程或管理端關閉 | 同步設定 enabled=0 |
| crawlerservice | UPDATE closetime=now() | 爬蟲帳號終止 | 同步設定 enabled=0 |
| gamesettingservice | UPDATE closetime=now() | 管理員手動關閉 | enabled 由 1→0 時自動填入 |
| gamesettingsite | UPDATE closetime=now() | 關閉帳號 API | 同步設定 enabled=0 |
| zbaparser | UPDATE closetime=now() | 帳號關閉流程 | 同步設定 enabled=0 |
| openclawservice | UPDATE closetime=now() | 關閉帳號 API | 同步設定 enabled=0 |
| clientflowservice | UPDATE closetime=now() | 帳號關閉流程 | 同步設定 enabled=0 |
| webpservice | UPDATE closetime=now() | 帳號關閉流程 | 同步設定 enabled=0 |

**⚠️ 跨服務限制**：
- 帳號關閉為**不可逆操作**。所有服務的 SELECT 必須過濾 `closetime IS NULL OR closetime = ''`，否則已關閉帳號可能被誤用。
- 僅有 `pricecenterservice`、`tradegameservice`、`crawlerservice` 等具帳號生命週期管理權的服務可寫入此欄位。其他服務**嚴禁寫入**。
- 有效帳號的查詢條件必須完整：`WHERE account = ? AND enabled = 1 AND (closetime IS NULL OR closetime = '')`。

---

### password 欄位

**型別**：text

**值定義與狀態流轉**：

僅儲存經雜湊演算法（bcrypt/pbkdf2）處理後的密文。**任何 API 回應皆不可包含此欄位**。

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | INSERT/UPDATE | 帳號建立或密碼重設 API | 雜湊後寫入 |
| tradegameservice | INSERT/UPDATE | 遊戲帳號建立或密碼重設 | 雜湊後寫入 |
| crawlerservice | INSERT/UPDATE | 爬蟲帳號建立或密碼更新 | 雜湊後寫入 |
| mergesite | INSERT/UPDATE | 合併帳號建立或密碼重設 | 雜湊後寫入 |
| openclawservice | INSERT/UPDATE | 密碼修改 API | 雜湊後寫入 |
| gamesettingservice | INSERT/UPDATE | 帳號建立或密碼修改 API | 雜湊後寫入 |
| gamesettingsite | INSERT/UPDATE | 帳號建立或密碼修改 API | 雜湊後寫入 |
| zbaparser | INSERT/UPDATE | 帳號初始化或密碼更新 | 雜湊後寫入 |
| clientflowservice | INSERT/UPDATE | 密碼修改 API | 雜湊後寫入 |
| webpservice | INSERT/UPDATE | 密碼修改 API | 雜湊後寫入 |
| priceclientsystem | INSERT/UPDATE | 客戶端註冊或密碼修改 API | 雜湊後寫入 |
| sitegameoddservice | INSERT/UPDATE | 特定配置 API | 雜湊後寫入 |
| flowcontrolservice | INSERT/UPDATE | 內部初始化 API | 雜湊後寫入 |
| crawlerflowservice | INSERT/UPDATE | 新增爬蟲帳號 | 雜湊後寫入 |
| gamecombineservice | INSERT/UPDATE | 遊戲平台帳號建立 | 雜湊後寫入 |
| tradegameresultservice | INSERT | 外部遊戲平台帳號建立 | 雜湊後寫入 |

**⚠️ 跨服務限制**：
- **任何對外 API 皆不可回傳此欄位**（即使是雜湊值也不可暴露）。所有服務在 DTO 映射時必須明確排除。
- **明文寫入是嚴格禁止的**。所有 INSERT/UPDATE 必須經過服務端雜湊處理。
- 密碼驗證流程應由認證服務（如 `authservice`）統一處理，不應由各服務自行實現密碼比對。

---

### handler 欄位

**型別**：map<text, text>

**值定義與狀態流轉**：

內部配置的鍵值對映射，用於儲存帳號相關的擴展處理邏輯或第三方 API 配置。不直接對外暴露。

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | INSERT/UPDATE | 帳號初始化或管理後台配置更新 | 內部使用 |
| gamesettingservice | INSERT/UPDATE | 遊戲設定 Domain Service | 內部使用 |
| crawlerservice | INSERT/UPDATE | 爬蟲策略更新 API | 內部使用 |
| flowcontrolservice | INSERT/UPDATE | 系統內部擴展處理邏輯 | 內部使用 |
| sitegameoddservice | INSERT/UPDATE | 特定配置模組 | 內部使用 |
| tradegameservice | INSERT/UPDATE | 管理後台或配置流程 | 內部使用 |
| webpservice | INSERT/UPDATE | 服務內部邏輯 | 內部使用 |
| openclawservice | INSERT/UPDATE | 後台管理 API | 內部使用 |
| zbaparser | INSERT/UPDATE | 帳戶初始化流程 | 內部使用 |
| gamecombineservice | INSERT/UPDATE | 處理器配置映射 | 內部使用 |

**⚠️ 跨服務限制**：
- 此欄位**不應回傳至前端**。所有服務的 GET API 必須排除此欄位。
- 更新 `map` 時需使用 Cassandra 的 map 操作語法（如 `handler = handler + {'key': 'value'}`），避免覆蓋其他 key。
- `password`、`phone` 等敏感資訊**不可**寫入此 map。

---

### phone 欄位

**型別**：text

**值定義與狀態流轉**：

用戶手機號碼，屬於個人隱私資料。

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | INSERT/UPDATE | 帳號建立或資料更新 | 格式驗證後寫入 |
| tradegameservice | INSERT/UPDATE | 手機驗證或綁定 API | 僅限驗證流程 |
| mergesite | INSERT | 合併帳號建立 | 初始寫入 |
| openclawservice | INSERT/UPDATE | 註冊或資料更新 | 格式驗證後寫入 |
| zbaparser | INSERT/UPDATE | 帳號初始化或後台授權 | 授權後更新 |
| clientflowservice | INSERT/UPDATE | 註冊或資料更新 | 格式驗證後寫入 |

**⚠️ 跨服務限制**：
- `phone` 為個資。除非使用者本人或管理後台授權，否則對外 API 必須進行脫敏處理（如 `09*****123`）或直接不回傳。
- 寫入前需驗證格式合法性。

---

### username 欄位

**型別**：text（部分品牌表無此欄位，如 HGA、KKK、KU、NK、TG、TG999）

**值定義與狀態流轉**：

可選的顯示名稱，不強制唯一。

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | INSERT/UPDATE | 帳號建立或資料更新 | 非強制欄位 |
| mergesite | INSERT | 合併帳號建立 | 非強制欄位 |
| openclawservice | INSERT/UPDATE | 註冊或後台設定 | 非強制欄位 |
| zbaparser | INSERT/UPDATE | 帳號初始化 | 非強制欄位 |

**⚠️ 跨服務限制**：
- 部分品牌表無此欄位，操作前應確認表結構，避免執行無效的 INSERT/UPDATE。

---

## Table：actionlog

**引擎**：Cassandra  
**Primary Key**: `(date)` clustering: `(addtime, user, gametype)`

### 概述
操作日誌表，記錄所有後台關鍵操作（如帳號管理、站點合併、爬蟲控制等）。由各服務在執行重要變更時自動寫入，**僅允許 INSERT，禁止 UPDATE 或 DELETE**。查詢必須以分區鍵 `date` 為條件，全表掃描被嚴格禁止。

### date 欄位

**型別**：text (yyyy-MM-dd 格式)  

**值定義**：  
- 由系統依操作當日 UTC 日期自動產生，**不可由呼叫端指定**，用於分區。

### addtime 欄位

**型別**：text (時間戳字串)  

**值定義**：  
- 伺服器自動填入的當前時間戳，用作排序與範圍過濾。

### user 欄位

**型別**：text  

**值定義**：  
- 操作者帳號，由系統從認證上下文提取，不可偽造。

### gametype 欄位

**型別**：text (e.g., BS, BK, SC, HL, FL, TN …)  

**值定義**：  
- 標記操作所屬的遊戲類別，便於日誌分類查詢。

### action / actionclass / detail 欄位

- `action`: 預定義動作名稱（如 `Login`、`Update`、`Split`）。  
- `actionclass`: 業務分類（如 `SiteTeam`、`Account`）。  
- `detail`: JSON 字串，應包含操作前後內容，但**嚴禁包含密碼、Token 等敏感資料**。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricecenterservice | INSERT | 管理後台操作 | 寫入完整日誌 |
| priceclientsystem | INSERT | 帳號變更或密碼修改 | 僅寫入 |
| crawlerservice | INSERT | 爬蟲帳號管理操作 | 僅寫入 |
| crawlerflowservice | INSERT | 爬蟲任務開始/完成 | 僅寫入 |
| crawleragentstandings | INSERT | 資料轉換寫入 | 必須提供當日 `date`，`detail` 為結構化 JSON |
| flowcontrolservice | INSERT | 關鍵操作（Split、Update等） | 一次性寫入所有欄位，不可後續修改 |
| mergesite | INSERT | 站點合併操作 | 記錄合併過程 |
| openclawservice | INSERT | 後台管理操作 | 記錄合併/拆分/校正 |
| clientflowservice | INSERT | 管理操作 | 記錄重要變更 |
| gamecombineservice | INSERT | 遊戲映射流程 | 記錄操作日誌 |
| tradegameresultservice | INSERT | 結算完成/失敗 | 記錄結果處理 |
| pricesubscriptionsystem | INSERT | PriceCenterHub 或排程 | 記錄訂閱操作 |
| zbaparser | INSERT | 業務操作 | 自動寫入 |
| pricecenterresult | INSERT | API 層記錄 | 記錄結果查詢 |
| syncservice | INSERT | 資料同步操作 | 記錄同步過程 |
| webpservice | INSERT | 帳號管理操作 | 記錄變更 |

**⚠️ 跨服務限制**：
- `actionlog` **僅允許 INSERT**，任何 UPDATE / DELETE 操作皆被禁止。
- 查詢必須以 `date` 為分區鍵條件，違反會觸發全表掃描而影響效能。
- `detail` 欄位若包含敏感資料（密碼、Token），必須脫敏或過濾後再寫入。
- `addtime` 與 `date` 必須使用服務端時間，**不可由客戶端傳入**，防止日誌偽造。

---

## Table：agents

**引擎**：Cassandra  
**Primary Key**: `(site)` clustering: `(gametype)`

### 概述
用於管理各站點 (site) 的遊戲代理 (agent) 配置。每個站點針對不同遊戲類型，可設置最小代理工作數等參數。

### gametype 欄位

**型別**：text (Clustering Key)

**值定義與狀態流轉**：

遊戲類型縮寫，如 `BS`（籃球）、`BK`（足球）、`TN`（網球）等，與其他表一致。  
與 `site` 組成複合主鍵，建立記錄後不可變更。

### minworks 欄位

**型別**：int

**值定義與狀態流轉**：

最小工作代理數量，當啟用的可用代理少於此值時，系統可能觸發告警或自動擴展。

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| 正整數 | 最小代理工作數 | gamecombineservice / crawlermanager | 站點初始化或管理後台設定時 |

### lastupdtime 欄位

**型別**：map<text, bigint>

**值定義與狀態流轉**：

記錄各代理最後更新時間的時間戳映射 (key=代理ID, value=毫秒時間戳)。  
用於判斷代理是否仍活躍，過期代理不應參與任務分配。

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| flowcontrolservice | INSERT/UPDATE | 站點代理配置更新 | 寫入 `site`/`gametype` 組合 |
| gamecombineservice | SELECT | 遊戲映射流程 | 查詢代理可用性 |
| crawlerflowservice | SELECT | 爬蟲任務分配 | 查詢代理配置 |

**⚠️ 跨服務限制**：
- 查詢時必須搭配 `site` 分區鍵及 `gametype` 聚簇鍵，不可全表掃描。
- `lastupdtime` map 更新時應使用合併操作，避免覆蓋既有代理資訊。

---

## Table：aimerge_backtest_runs

**引擎**：Cassandra  
**Primary Key**: `(game_type)` clustering: `(backtest_date, executed_at)`

### 概述
紀錄 AI 合併 (AIMerge) 模型的回測執行結果，用於對比新舊模型的錯誤率、改善與回歸案例。

### backtest_date 欄位

**型別**：text (yyyy-MM-dd 格式, Clustering Key)

**值定義**：  
回測的目標日期。

### executed_at 欄位

**型別**：timestamp (Clustering Key)

**值定義**：  
回測執行的精確時間。

### before_error_count / after_error_count 欄位

**型別**：int

**值定義與狀態流轉**：

回測前後的錯誤樣本數，用於量化模型改善效果。  
`after` 應小於或等於 `before`；若增大代表回歸 (regression)。

### before_error_rate / after_error_rate 欄位

**型別**：float

**值定義**：  
回測前後的錯誤率 (0.0 ~ 1.0)。由 `error_count / sample_count` 計算。

### improved_samples / regression_samples 欄位

**型別**：text (JSON 陣列字串)

**值定義**：  
改善與回歸案例的樣本 ID 列表，用於進一步分析。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| openclawservice | INSERT | 回測任務完成 | 寫入回測結果 |
| openclawservice | SELECT | 查詢歷史回測 | 以 `game_type` + `backtest_date` 條件查詢 |
| aimerge-worker | INSERT/UPDATE | 回測 pipeline | 寫入各階段回測數據 |

**⚠️ 跨服務限制**：
- 此資料主要供內部 AIMerge 模組分析使用，不應直接對外暴露。  
- `improved_samples` / `regression_samples` 內容可能包含內部 sitegid，對外時需脫敏。

---

## Table：aimerge_daily_reports

**引擎**：Cassandra  
**Primary Key**: `(game_type)` clustering: `(report_date)`

### 概述
AI 合併模型的每日運作報告，彙總推論數量、自動確認/拒絕數量、衝突、建議事項等。

### report_date 欄位

**型別**：text (yyyy-MM-dd 格式, Clustering Key)

**值定義**：  
報告所屬日期。

### total_predictions 欄位

**型別**：int

**值定義**：  
當日總推論配對數（兩站點比賽配對）。

### auto_confirmed / auto_error 欄位

**型別**：int

**值定義與狀態流轉**：

- `auto_confirmed`：系統自動確認的推論數量（高信心度）。  
- `auto_error`：自動確認但後續驗證失敗的數量（用於監控模型品質）。

### conflict_count 欄位

**型別**：int

**值定義**：  
推論結果與現有合併記錄衝突的數量，需人工介入處理。

### error_breakdown 欄位

**型別**：text (JSON 字串)

**值定義**：  
按錯誤來源分類的統計（如 normalizer、feature_builder、threshold、odds_missing），包含樣本資訊供診斷。

### suggestions 欄位

**型別**：text (nullable)

**值定義**：  
報告產生的建議事項，可能為 null。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| openclawservice | INSERT | 每日排程結束 | 產生報告並寫入 |
| openclawservice | SELECT | 管理後台查詢 | 以 `game_type` + `report_date` 查詢歷史報告 |

**⚠️ 跨服務限制**：
- `error_breakdown` 中的 samples 資訊若包含原始賽事資料，對外回傳時應過濾或脫敏。  
- 報告為不可變記錄，不應有 UPDATE / DELETE 操作。

---

## Table：aimerge_historical_runs

**引擎**：Cassandra  
**Primary Key**: `(game_type, target_date)` clustering: `(started_at)`

### 概述
記錄 AIMerge 歷史合併執行的運行狀態，包括處理了多少配對、寫入了多少標記、完成時間等。

### target_date 欄位

**型別**：text (yyyy-MM-dd 格式, Partition Key)

**值定義**：  
合併目標日期。

### game_type 欄位

**型別**：text (Partition Key)

**值定義**：  
遊戲類型縮寫。

### status 欄位

**型別**：text

**值定義與狀態流轉**：

```
     openclawservice / aimerge-worker
      INSERT status='running'
                           ──────→ status='success' (完成)
                           ──────→ status='failed' (失敗，記錄 error_message)
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| running | 執行中 | openclawservice / aimerge-worker | 任務啟動時 |
| success | 執行成功 | openclawservice / aimerge-worker | 任務完成時 |
| failed | 執行失敗 | openclawservice / aimerge-worker | 任務失敗時 |

### processed_pairs / label_written / site_a_game_count 欄位

**型別**：int

**值定義**：  
- `processed_pairs`：已處理的站點配對數。  
- `label_written`：寫入的訓練標記數。  
- `site_a_game_count`：站點 A 的比賽總數。

### job_id 欄位

**型別**：text

**值定義**：  
關聯的 job 識別碼，可用於查詢 `aimerge_historical_runs_by_id`。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| openclawservice | INSERT | 任務啟動 | 寫入初始狀態 running |
| openclawservice | UPDATE status, label_written, etc. | 任務完成 | 更新最終狀態 |
| openclawservice | SELECT | 管理後台查詢 | 查詢歷史執行記錄 |

**⚠️ 跨服務限制**：
- 任務狀態不可跳躍變更（例如 running → final 必須經過 success/failed）。  
- 查詢必須搭配 `game_type` + `target_date` 分區鍵。

---

## Table：aimerge_historical_runs_by_id

**引擎**：Cassandra  
**Primary Key**: `(job_id)`

### 概述
與 `aimerge_historical_runs` 相同資料，但以 `job_id` 為主鍵，用於快速反查特定任務的執行狀態。

### job_id 欄位

**型別**：text (Partition Key)

**值定義**：  
任務唯一識別碼（UUID）。

### 其餘欄位

與 `aimerge_historical_runs` 一致：`game_type`, `target_date`, `status`, `processed_pairs`, `label_written`, `site_a_game_count`, `error_message`, `started_at`, `finished_at`。

**⚠️ 跨服務限制**：
- 此表為 `aimerge_historical_runs` 的索引備援，資料一致必須由寫入服務保證。

---

## Table：aimerge_label_overrides

**引擎**：Cassandra  
**Primary Key**: `(game_type, gdate)` clustering: `(prediction_id)`

### 概述
記錄管理員對 AIMerge 模型推論結果的人工覆蓋（override），用於修正錯誤標記或排除特定樣本。

### prediction_id 欄位

**型別**：text (Clustering Key)

**值定義**：  
推論 ID，對應一組比賽配對的模型判斷結果。

### override_label 欄位

**型別**：boolean

**值定義與狀態流轉**：

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| true | 強制標記為匹配 | openclawservice（管理員） | 人工修正錯誤的未匹配推論 |
| false | 強制標記為不匹配 | openclawservice（管理員） | 人工修正錯誤的匹配推論 |

### excluded_from_training 欄位

**型別**：boolean

**值定義**：  
是否從訓練資料集中排除此樣本（true=排除）。

### reason 欄位

**型別**：text

**值定義**：  
管理員覆蓋的原因說明。

### reviewed_by / reviewed_at 欄位

**型別**：text / timestamp

**值定義**：  
審查者帳號與審查時間。

### game_a_sitegid / source_b / source_b_sitegid 欄位

**型別**：text

**值定義**：  
被覆蓋的兩站點比賽 ID。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| openclawservice | INSERT/UPDATE | 管理員人工審查 | 寫入覆蓋資訊 |
| openclawservice | SELECT | 查詢審查記錄 | 以 `game_type` + `gdate` 條件查詢 |

**⚠️ 跨服務限制**：
- 此表記錄為不可變更的審查軌跡，建議記錄所有歷史版本（目前為 upsert，可能遺失舊覆蓋記錄）。
- 訓練流程必須讀取此表，排除 `excluded_from_training = true` 的樣本。

---

## Table：aimerge_match_predictions

**引擎**：Cassandra  
**Primary Key**: `(game_type, gdate)` clustering: `(prediction_id)`

### 概述
AIMerge 模型的核心推論結果表，記錄每日各遊戲類型的比賽配對推論，包含信心度、自動化決策、來源資訊等。

### prediction_id 欄位

**型別**：text (Clustering Key)

**值定義**：  
推論唯一識別碼（格式可能為 `{siteA}_{siteB}_{siteLID}_{gameID}` 等組合）。

### prediction_label 欄位

**型別**：boolean

**值定義與狀態流轉**：

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| true | 預測為匹配 | AIMerge 模型 | 推論階段 |
| false | 預測為不匹配 | AIMerge 模型 | 推論階段 |

### confidence 欄位

**型別**：float (推測，來源於模型)

**值定義**：  
模型信心度分數，用於判斷自動化決策閾值。高於 `auto_confirm_threshold` 可自動確認。

### auto_status 欄位

**型別**：text

**值定義與狀態流轉**：

```
     AIMerge 模型推論
     auto_status='pending'
         │
         ├─ confidence >= threshold ─→ auto_status='auto_confirmed'
         │
         ├─ confidence < threshold ──→ auto_status='pending'
         │
         └─ auto_confirmed 後驗證失敗 → auto_status='auto_error'
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| pending | 待人工審查 | AIMerge 模型 | 推論時信心度不足 |
| auto_confirmed | 自動確認 | AIMerge 模型 | 推論時信心度超過閾值 |
| auto_error | 自動確認後錯誤 | openclawservice（驗證流程） | 後續驗證發現錯誤 |

### source_a / source_a_sitegid / source_b / source_b_sitegid 欄位

**型別**：text

**值定義**：  
標記來源站點與比賽 GID，用於追溯推論的具體比賽。

### inferred_label 欄位

**型別**：boolean (nullable, 推測)

**值定義**：  
若推論未直接產生標記，後續可透過二次推理補上，記錄於此欄位。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| openclawservice / aimerge-worker | INSERT | 每日推理流程 | 寫入推論結果 |
| openclawservice | UPDATE auto_status, inferred_label | 後續驗證或人工審查 | 更新狀態 |
| openclawservice | SELECT | 管理後台查詢/回測 | 以 `game_type` + `gdate` 條件查詢 |

**⚠️ 跨服務限制**：
- 推論結果不可直接作為最終合併依據 (`auto_status='auto_confirmed'` 才可自動合併)。
- `source_*` 欄位可能包含其他站台內部的 ID 格式，對外 API 應使用統一標準。

---

## Table：aimerge_predictions_by_id

**引擎**：Cassandra  
**Primary Key**: `(prediction_id)`

### 概述
與 `aimerge_match_predictions` 相同資料，但以 `prediction_id` 為主鍵，用於快速查詢特定推論記錄。

### prediction_id 欄位

**型別**：text (Partition Key)

**值定義**：  
推論唯一識別碼。

### 其餘欄位

與 `aimerge_match_predictions` 一致：`game_type`, `gdate`, `prediction_label`, `confidence`, `auto_status`, `source_a`, `source_a_sitegid`, `source_b`, `source_b_sitegid` 等。

**⚠️ 跨服務限制**：
- 此表為 `aimerge_match_predictions` 的索引備援，資料一致必須由寫入服務保證。

---

## Table：aimerge_training_labels

**引擎**：Cassandra  
**Primary Key**: `(game_type, gdate)` clustering: `(label_id)`

### 概述
AIMerge 模型的**訓練標記資料**，來自最終確認的合併結果或人工標記。用於模型再訓練。

### label 欄位

**型別**：boolean

**值定義與狀態流轉**：

| 值 | 意義 | 來源 |
|----|------|------|
| true | 兩個比賽確實匹配 | 最終合併結果 (openclaw_merge) |
| false | 兩個比賽不匹配 | 人工審查標記為不匹配或 negative samples |

### source_a / source_b / sitegid_a / sitegid_b 欄位

**型別**：text

**值定義**：  
訓練樣本的兩個比賽來源與 ID。

### merged_gid 欄位

**型別**：text (nullable)

**值定義**：  
若已合併，關聯的最終合併 GID。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| openclawservice | INSERT | 合併確認後 | 正樣本寫入 |
| openclawservice | INSERT | 人工審查後 | 負樣本或修正標記寫入 |
| openclawservice | SELECT | 模型訓練流程 | 以 `game_type` + `gdate` 讀取訓練資料 |

**⚠️ 跨服務限制**：
- 訓練標記必須經過驗證（人工或自動），不可直接使用推論結果作為訓練資料。  
- 查詢訓練資料時須排除被 `aimerge_label_overrides` 排除的樣本。

---

## Table：aimerge_runtime_config_active

**引擎**：Cassandra  
**Primary Key**: `(config_key)`

### 概述
儲存 AIMerge 運行時配置的**當前啟用版本**，提供給各服務快速讀取模型參數。

### config_value 欄位

**型別**：text (JSON 字串, 推測)

**值定義**：  
包含模型閾值、站點對權重、特徵工程參數等的 JSON 配置。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| openclawservice | INSERT/UPDATE | 配置更新時 | 寫入新配置並同步至 `aimerge_runtime_config_versions` |
| openclawservice | SELECT | 模型初始化 | 讀取當前啟用的配置 |
| aimerge-worker | SELECT | 每次推理啟動 | 獲取最新配置 |

**⚠️ 跨服務限制**：
- 更新配置時必須同步寫入版本歷史 (`aimerge_runtime_config_versions`)，保留變更軌跡。

---

## Table：aimerge_runtime_config_versions

**引擎**：Cassandra  
**Primary Key**: `(config_key)` clustering: `(version_timestamp)`

### 概述
AIMerge 配置的**歷史版本記錄**，用於回滾和稽核。

### version_timestamp 欄位

**型別**：timestamp (Clustering Key)

**值定義**：  
配置生效的時間點，用於版本排序。

### config_value 欄位

**型別**：text (JSON 字串)

**值定義**：  
該版本的完整配置。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| openclawservice | INSERT | 配置更新時 | 記錄歷史版本 |
| openclawservice | SELECT | 稽核或回滾 | 查詢特定時間點的配置 |

**⚠️ 跨服務限制**：
- 此表為不可變記錄（版本控制），不可對既有版本進行 UPDATE / DELETE。

---

## Table：aimerge_team_aliases

**引擎**：Cassandra  
**Primary Key**: `(game_type)` clustering: `(alias_key, site)`

### 概述
記錄站台間球隊名稱的**別名對照表**，用於標準化不同站台的隊名表示方式，輔助 AIMerge 模型進行比賽合併判斷。

### alias_key 欄位

**型別**：text (Clustering Key)

**值定義**：  
標準化後的別名鍵（如 `"lakers"`, `"celtics"` 等標準化縮寫）。

### site 欄位

**型別**：text (Clustering Key)

**值定義**：  
原始站台代碼（如 `panda`, `hga` 等）。

### site_team_name 欄位

**型別**：text (推測)

**值定義**：  
原始站台上的隊伍名稱（如原始資料中拼寫略有不同的隊名）。

### mapped_team_name 欄位

**型別**：text (推測)

**值定義**：  
對應的標準化隊伍名稱。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| openclawservice | INSERT/UPDATE | 管理員設定 | 建立或更新別名對照 |
| aimerge-worker | SELECT | 特徵工程階段 | 標準化隊伍名稱 |

**⚠️ 跨服務限制**：
- 此表資料由人工維護，錯誤的別名可能導致模型準確率下降，寫入前應驗證。

---

## Table：aimerge_tuning_pack_exports

**引擎**：Cassandra  
**Primary Key**: `(export_date, export_type)` (推測)

### 概述
記錄從 AIMerge 模型調參過程匯出的參數包或模型快照，用於模型版本管理與回溯。

**⚠️ 此表使用情境較少，主要為內部模型管理工具使用，不提供對外 API。**

---

## Table：aimerge_historical_jobs

**引擎**：Cassandra  
**Primary Key**: `(job_id)` (推測)

### 概述
類似 `aimerge_historical_runs_by_id`，記錄 AIMerge 相關的歷史任務執行狀態與結果。

**⚠️ 此表內容與 `aimerge_historical_runs` 相關，具體欄位細節以 Schema 為準。若有衝突待人工確認。**

---

## Table：gamecombines_{businesscode}

**引擎**：Cassandra  
**Primary Key**: `(businesscode, betbar_combine_id)` (推測)

### 概述
儲存個別商務平台 (businesscode) 的交易遊戲合併規則及對應的賠率組合。  
⚠️ **此表為推測名稱，實際表名可能依 businesscode 動態建立。Schema 細節可能有衝突，待人工確認。**

### betbar_combine_id 欄位

**型別**：text (Partition Key，推測)

**值定義**：  
投注列合併規則的唯一識別碼，由 gamecombineservice 產生。

### game_type 欄位

**型別**：text

**值定義**：  
遊戲類型縮寫（如 BK, BS, TN 等）。

### combine_rule 欄位

**型別**：text (JSON 字串, 推測)

**值定義**：  
合併規則定義，包含可選擇的投注選項組合方式、賠率計算公式等。

### enabled 欄位

**型別**：boolean (推測)

**值定義與狀態流轉**：

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| true | 啟用此合併規則 | gamecombineservice | 管理後台設定 |
| false | 停用此合併規則 | gamecombineservice | 管理後台停用 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| gamecombineservice | INSERT | 建立合併規則 | 寫入規則定義 |
| gamecombineservice | UPDATE enabled / combine_rule | 管理後台操作 | 更新規則 |
| gamecombineservice | SELECT | 遊戲映射流程 | 讀取規則進行組合 |
| tradegameservice | SELECT | 交易遊戲初始化 | 讀取合併規則設定 |


**⚠️ 跨服務限制**：
- 此表為 gamecombineservice 負責建立與維護，其他服務僅可讀取。  
- 啟用/停用操作應立即生效，若有 Redis 快取需同步清除。

---

## Table：openclaw_merge

**引擎**：Cassandra  
**Primary Key**: `(merged_gid)` (推測，或用 site + sitegid 組合)

### 概述
記錄合併後的比賽資訊，儲存透過人工或 AI 合併流程產生的最終合併結果。此表作為跨站點比賽對照的核心來源。

### merged_gid 欄位

**型別**：text (Partition Key，推測)

**值定義**：  
合併後的唯一比賽識別碼。

### game 欄位

**型別**：text (JSON 字串)

**值定義**：  
合併後的比賽資料快照（JSON 格式），包含標準化的比賽名稱、隊伍、聯賽等。

### main_site_game 欄位

**型別**：text (JSON 字串)

**值定義**：  
主要站點的原始比賽資料快照。

### site_game_mappings 欄位

**型別**：text (JSON 陣列字串)

**值定義**：  
關聯的所有站點比賽對照清單。

### status 欄位

**型別**：text

**值定義與狀態流轉**：

```
     mergesite / openclawservice
      INSERT status='active'
                           ──────→ status='inactive' (管理員手動標記為失效)
```

| 值 | 意義 | 由誰設定 | 時機 |
|----|------|---------|------|
| active | 合併有效 | mergesite / openclawservice | 合併建立時 |
| inactive | 合併失效 | mergesite / openclawservice | 管理員解除合併 |

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| mergesite | INSERT | 站點合併流程 | 寫入合併結果 |
| openclawservice | INSERT/UPDATE | AI 或人工合併確認 | 寫入或修正合併結果 |
| openclawservice | SELECT | 查詢合併對照 | 讀取已合併比賽資訊 |
| gamecombineservice | SELECT | 遊戲映射流程 | 查詢合併後的比賽資料 |
| flowcontrolservice | SELECT | 賠率比對 | 查詢合併對照進行跨站比對 |

**⚠️ 跨服務限制**：
- `openclaw_merge` 為不可變更的合併快照，若需修正應新建記錄而非 UPDATE 既有記錄。  
- 記錄中的 `game` 與 `main_site_game` JSON 可能包含站台內部 ID，對外提供時應過濾。

---

## Table：aimerge_conflicts_queue

**引擎**：Cassandra  
**Primary Key**: `(game_type, gdate)` clustering: `(conflict_id)` (推測)

### 概述
記錄 AIMerge 推論結果與現有合併記錄之間的衝突，作為待處理隊列，供管理員人工介入。

### conflict_id 欄位

**型別**：text (Clustering Key，推測)

**值定義**：  
衝突唯一識別碼。

### conflict_type 欄位

**型別**：text (推測)

**值定義與狀態流轉**：

| 值 | 意義 | 說明 |
|----|------|------|
| model_merge_conflict | 模型推論合併 vs 既有合併 | 模型認為應合併，但已有合併記錄衝突 |
| model_split_conflict | 模型推論拆分 vs 既有合併 | 模型認為不應合併，但已有合併記錄 |

### resolved 欄位

**型別**：boolean (推測)

**值定義**：  
是否已解決。

### resolved_by / resolved_at 欄位

**型別**：text / timestamp (推測)

**值定義**：  
解決者帳號與解決時間。

---

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| openclawservice | INSERT | 模型推論後 | 寫入待處理衝突 |
| openclawservice | UPDATE resolved=true | 管理員解決 | 標記為已解決 |

**⚠️ 跨服務限制**：
- 衝突未解決時，不應允許自動合併流程繼續進行。必須人工介入或等待排程回退。

---

## Table：crawler_log

**引擎**：Cassandra  
**Primary Key**: `(machine)` clustering: `(site, starttime)` (推測)

### 概述
記錄爬蟲任務的執行日誌，包含任務開始/結束時間、處理數量、執行時間等。

### machine 欄位

**型別**：text (Partition Key，推測)

**值定義**：  
執行爬蟲任務的機器識別碼。

### site 欄位

**型別**：text (Clustering Key，推測)

**值定義**：  
執行爬蟲的目標站台。

### starttime / addtime 欄位

**型別**：text (時間戳字串)

**值定義**：  
任務開始時間（由 crawlerflowservice 建立時寫入，不可修改）。

### processcount / exectime 欄位

**型別**：int / bigint

**值定義**：  
處理的比賽數量與執行時間。僅在爬蟲完成後一次更新。

### status 欄位

**型別**：text (推測)

**值定義與狀態流轉**：

```
     crawlerflowservice
      INSERT status='processing'
                           ──────→ status='done' (完成)
                           ──────→ status='error' (失敗)
```

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| crawlerflowservice | INSERT | 任務初始化 | 寫入 `machine`, `site`, `starttime` |
| crawlerflowservice | UPDATE processcount, exectime, status | 任務完成 | 一次性更新 |
| crawlerflowservice | SELECT | 任務監控查詢 | 以 `machine` + `starttime` 範圍過濾 |

**⚠️ 跨服務限制**：
- `processcount` 不可增量累加，必須在任務完成後一次計算並更新。  
- 查詢需以 `machine` 分區鍵為條件，不可全表掃描。

---

## Table：alertlog

**引擎**：Cassandra  
**Primary Key**: `(site)` clustering: `(gtype, addtime, sitegid)` (推測)

### 概述
記錄爬蟲或賠率比對過程中的異常告警，用於監控與診斷。

### site / gtype / sitegid / gid / gdate / gtime 欄位

**型別**：text

**值定義**：  
標記告警所屬的站台、遊戲類型、比賽識別碼、日期時間。

### content 欄位

**型別**：text (JSON 字串)

**值定義**：  
告警內容，包含異常描述、賠率差異、時間戳等資訊。

### addtime 欄位

**型別**：text / bigint

**值定義**：  
告警發生的時間（Unix 秒）。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| flowcontrolservice | INSERT | 檢測到異常時 | 寫入告警記錄 |
| pricesubscriptionsystem | INSERT | 訂閱流程異常 | `AlertLogDataProvider` 寫入 |

**⚠️ 跨服務限制**：
- `alertlog` 為不可變記錄，寫入後不可 UPDATE / DELETE。

---

## Table：fixdatalog

**引擎**：Cassandra  
**Primary Key**: `(gtype)` clustering: `(gdate, gtime)` (推測)

### 概述
記錄自動或手動修復比賽資料的操作日誌，用於稽核修復過程。

### fixed 欄位

**型別**：int (推測)

**值定義與狀態流轉**：

| 值 | 意義 | 說明 |
|----|------|------|
| 0 | 未修復 | 初始狀態 |
| 1 | 已修復 | flowcontrolservice 標記修復完成 |

### addtime 欄位

**型別**：text (時間戳)

**值定義**：  
修復完成時間。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| flowcontrolservice | UPDATE fixed=1, addtime=now() | 修復完成 | `FixDataProvider` 寫入 |
| flowcontrolservice | INSERT | 資料異常檢測 | 初始化修復記錄 |

**⚠️ 跨服務限制**：
- 僅 `fixed` 和 `addtime` 可 UPDATE。其餘欄位（`gtype`, `gdate`, `gtime` 等）建立後不可變更。

---

## Table：inplaysrepadlogs

**引擎**：Cassandra  
**Primary Key**: `(gtype, gid)` clustering: `(addtime)` (推測)

### 概述
記錄滾球盤 (inplay) 的賠率變更歷程，用於追蹤盤口變動。

### logs 欄位

**型別**：list<text> (推測，或 map)

**值定義**：  
賠率變更的附加記錄（append-only）。每次變更以 `SET logs = logs + ['新記錄']` 方式追加。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| flowcontrolservice | UPDATE logs = logs + [新記錄] | 檢測到賠率變更 | 僅追加，不覆蓋 |

**⚠️ 跨服務限制**：
- `logs` 欄位**僅允許追加，不允許覆蓋或刪除**。

---

## Table：kupages

**引擎**：Cassandra  
**Primary Key**: `(pagename)` (推測)

### 概述
用於管理 KU 平台上的頁面配置或狀態。

### pagename 欄位

**型別**：text (Partition Key)

**值定義**：  
頁面名稱識別碼。

### adddate 欄位

**型別**：timestamp (推測)

**值定義**：  
頁面新增或最後更新的日期。

**各服務操作明細**：

| 服務 | 操作 | 條件／時機 | 說明 |
|------|------|-----------|------|
| pricesubscriptionsystem | UPDATE adddate | 管理資料更新 | `ManagerDataProvider` 執行 |

**⚠️ 跨服務限制**：
- 僅支援 UPDATE，不支援 INSERT 或 DELETE。

---

## ✅ 本次進度確認

- 已完成：accounts_{brand}（含所有欄位），actionlog，agents，aimerge 系列表（backtest_runs, daily_reports, historical_runs, label_overrides, match_predictions, predictions_by_id, training_labels, runtime_configs, team_aliases, tuning_pack_exports, historical_jobs, conflicts_queue），gamecombines_{businesscode}，openclaw_merge，crawler_log，alertlog，fixdatalog，inplaysrepadlogs，kupages 等核心表。
- 待補充：games_{gameType} 系列、odds_{gameType} 系列、odds_his_{gameType}_{date} 系列、matches_his_{gameType}_{date} 系列、sitegames_{gameType} 系列、leagues_{gameType}/teams_{gameType}/siteleagues_{gameType}/siteteams_{gameType} 系列、standings 系列等。涉及結構類似，可抽共通段落簡化。

---

## 常見錯誤（跨服務）

- ❌ 忘記檢查 `enabled = 1 AND closetime IS NULL` 就使用帳號 → ✅ 必須完整過濾，已關閉或停用帳號不可用於任何業務流程。
- ❌ 對外 API 回傳了 `password` 或完整 `handler` 欄位 → ✅ GET API 永遠排除密碼，handler 僅內部使用。
- ❌ 查詢 `actionlog` 忘了加 `date` 條件 → ✅ 所有查詢必須以 `date` 作為分區鍵過濾。
- ❌ 直接 `UPDATE` 覆蓋 `accounts_*` 的主鍵 `account` → ✅ 主鍵建立後不可修改。
- ❌ 未確認表結構（如某些品牌表無 `username` 欄位）就執行寫入 → ✅ 操作前應確認目標表的欄位是否存在。
- ❌ AIMerge 自動確認的推論 (`auto_status='auto_confirmed'`) 在有未解決衝突時直接合併 → ✅ 衝突未解決前應暫停自動合併。
- ❌ 更新 `handler` map 時使用整個覆蓋，造成其他配置遺失 → ✅ 使用 `handler = handler + {'new_key': 'value'}` 語法追加/更新。
- ❌ 多個服務同時寫入同一筆 `actionlog` 或 `odds_his_*` 記錄 → ✅ 各服務需確保寫入時序一致，避免 race condition。
- ❌ 在 AIMerge 訓練流程中未排除 `excluded_from_training = true` 的樣本 → ✅ 訓練前必須過濾，確保資料品質。
- ❌ 回傳 `aimerge_*` 表的原始 JSON（含內部 sitegid）給前端 → ✅ 對外 API 應使用標準化格式，遮蔽內部 ID 映射。
- ❌ `crawler_log.processcount` 使用增量更新而非一次計算 → ✅ 任務完成後一次性計算並更新，避免不準確。