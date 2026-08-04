# 服務學習卡：GameSettingService（站台設定管理篇）

> 產出日期：2026-06-17 | 聚焦主題：站台設定管理（SiteConfig）

---

## 1. 這個服務是做什麼的

GameSettingService 是後台配置層的核心服務，負責管理「遊戲設定」與「商家（Business）管理」。  
你可以把它理解為：**所有遊戲玩法開關都在這裡設定、所有商家帳號也在這裡管理**。  
特別就「站台設定管理」而言，它定義每個商家在各遊戲類型下，前台玩家能看到哪些玩法、是否顯示停止賽事的玩法、是否交換主客隊等核心控制參數。

---

## 2. 在系統架構中的位置

- **類型**：WebAPI（ASP.NET Core .NET 6.0）
- **技術棧**：C#、Cassandra（`gamesettings` / `pricecenter`）、MySQL（GM DB）、Redis（LoginCache / BusinessCache）、ECFramework 驗證、Zookeeper（配置中心）、Kafka（日誌）
- **誰呼叫它**：
  - `GameSettingFrontEndSite`（前端管理介面）不直接呼叫，透過 `GameSettingSite`（BFF）作為中間層轉發
  - `GameSettingSite` → `GameSettingService`（分層架構，集中控制）
- **它呼叫誰**：
  - `pricecenterservice`：取得賽事 / 聯賽資訊供設定對照
  - `syncservice`：站台停止時，清除 Redis `BusinessCache`

（來源：README.md、documents.md 時序圖說明）

---

## 3. 它負責的資料（站台設定相關）

（來源：gamesettingservice-detail.md、db/_index.md）

| Table / 資料來源 | 角色 | 說明 |
|---|---|---|
| Cassandra `gamesettings.gametype_settings` | **主要寫入** | 商家於各 gameType 的站台設定，複合主鍵 `(company, gametype)`；`settings` 欄位為 JSON 字串 |
| Cassandra `gamesettings.businesses` | 唯讀（驗證用） | 驗證 businessCode 是否存在且有效；讀取 `subenddate` 判斷訂閱有效性 |
| Redis `BusinessCache` | 共用（清除） | 本服務不直接讀寫；站台停止時透過 syncservice 清除快取，確保下游服務讀到最新狀態 |

---

## 4. 主要功能一覽（站台設定管理）

（來源：README.md ConfigController API 清單、scenario-flows）

- **建立站台設定** `POST /api/v1/siteconfigs`：為指定商家建立某個 gameType 的站台設定，預設啟用（`enabled=1`），寫入 `gametype_settings` 表
- **查詢商家所有站台設定** `GET /api/v1/siteconfigs/{businessCode}`：依 `company` 取出所有 gameType 的設定清單
- **查詢指定 GameType 站台設定** `GET /api/v1/siteconfigs/{businessCode}/{gameType}`：以 `(company, gametype)` 複合主鍵精確查詢單一設定
- **更新站台設定** `PUT /api/v1/siteconfigs`：修改現有設定（若需停用，透過此 API 操作，不能在建立時直接設為 0）
- **設定站台停止** `POST /api/v1/system/site/stop/{gameType}`：將整個 gameType 下所有站台設定標記為 `site.stop=true`，並通知 syncservice 清除 Redis 快取

---

## 5. 典型業務場景

（來源：scenario-flows/create-flow/create-site-config.md、set-site-stop.md）

### 場景 1：管理員為商家建立站台設定

1. 後台管理員呼叫 `POST /api/v1/siteconfigs`，帶入 `businessCode`、`gameType`、`settings`（JSON 字串）
2. `ConfigController` 接收請求後交由 Service 處理
3. Service 驗證 `businessCode` 是否存在於 `businesses` 表
4. 驗證 `settings` 是否為合法 JSON
5. 自動填入 `updater`（操作者帳號），`enabled` 預設為 1
6. 寫入 Cassandra `gametype_settings` 表，主鍵 `(company, gametype)` 一旦建立不可修改
7. ⚠️ 重複建立同一 `company + gametype` 會產生主鍵衝突，前端需正確處理錯誤並引導使用更新 API

### 場景 2：設定站台緊急停止

1. 操作員呼叫 `POST /api/v1/system/site/stop/{gameType}`
2. `ConfigService.StopSite` 更新 `gametype_settings` 的 `settings` JSON，將 `site.stop` 設為 `true`
3. 呼叫 `syncservice` 清除所有關聯商家的 Redis `BusinessCache`
4. 下游服務（前台下注）在下次讀取時得到最新停止狀態
5. ⚠️ 高風險：若 syncservice 呼叫失敗，快取無法立即清除，下游服務在快取過期前仍會讀到舊的啟用狀態

---

## 6. 新人容易誤解的地方

（來源：scenario-flows 的常見錯誤與高風險區域、gamesettingservice-detail.md）

- ⚠️ **`settings` 欄位不是一般文字，是 JSON 字串**：寫入前必須驗證是否為合法 JSON，直接傳純文字或未序列化的物件會導致資料損毀
- ⚠️ **`updater` 不接受用戶端傳入**：後端自動填入當前操作者帳號，前端不能也不應該傳這個欄位
- ⚠️ **公司隔離（company isolation）是硬性規則**：查詢 `gametype_settings` 時 `company` 欄位必須嚴格等於請求的 `businessCode`，寫出無 `company` 條件的查詢會洩露其他商家設定
- ⚠️ **`businessCode` 是公司代碼，不是操作者帳號**：兩者經常被混淆，權限模型會因此判斷錯誤
- ⚠️ **建立 vs 更新**：`POST` 建立若重複主鍵會衝突報錯，不能用建立 API 來「覆蓋」設定，必須使用 `PUT` 更新 API
- ⚠️ **`authtoken` 與 `password` 絕不可出現在任何回傳中**：DTO 轉換時必須明確排除
- ⚠️ **前端不直接呼叫本服務**：請求路徑是 `GameSettingFrontEndSite → GameSettingSite (BFF) → GameSettingService`，新人容易誤以為前端直接對接
- ⚠️ **站台停止的 Winner 玩法**（高爾夫）：文件中雖然列出了支援站台，但 Memo 標記「不使用」，開發時需排除或隱藏，不可照單全開

---

## 7. 想深入了解，可以看

- 完整 API：`webapi/gamesettingservice/gamesettingservice.json`（禁止直接讀，數千行）
- 詳細說明：[gamesettingservice-detail.md](../../webapi/gamesettingservice/gamesettingservice-detail.md)
- 業務規範（Confluence 摘要）：[documents.md](../../webapi/gamesettingservice/documents.md)
- 建立站台設定流程：[create-site-config.md](../../webapi/gamesettingservice/scenario-flows/create-flow/create-site-config.md)
- 查詢站台設定流程：[get-site-configs.md](../../webapi/gamesettingservice/scenario-flows/query-flow/get-site-configs.md)
- 設定站台停止流程：[set-site-stop.md](../../webapi/gamesettingservice/scenario-flows/create-flow/set-site-stop.md)
- DB Schema：`db/gamesettings.md`、`db/gamesettings-detail.md`
