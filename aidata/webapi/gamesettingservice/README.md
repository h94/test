# GameSettingService WebAPI

- **服務識別碼**：`PRD_Docker_Swarm|swarm|gamesettingservice|gamesettingservice_GameSettingService`
- **Git Repository**：https://git.zbdigital.net/biz/gamesettingservice.git

## 職責
負責管理**遊戲設定**與**商家（Business）管理**，提供系統設定、聯賽設定、模板設定、單場遊戲設定的 CRUD，以及商家帳號、站台設定、聯賽進行中設定、訂閱者管理與操作日誌查詢。是後台配置層的核心服務，所有 gameType 維度的玩法設定均由此服務統一管理。

## 技術棧
- 框架：ASP.NET Core (.NET 6.0)
- 資料庫：MySQL（GM DB）、Cassandra（Keyspace: `gamesettings` / `pricecenter`）、PostgreSQL（`games` DB，唯讀驗證賽事資料）、Redis（LoginCache / BusinessCache）
- 驗證：ECFramework.ECService 2.0.0（內部統一驗證框架）
- 配置中心：Zookeeper
- 日誌：Kafka + Cassandra
- 其他套件：ECCore 2.0.7、GameDataModels 2.0.205

## 資料庫重要 Table

| 儲存層 | Table | 用途 |
|--------|-------|------|
| MySQL GM | businesses | 商家主表（businessCode、名稱、站台） |
| MySQL GM | accounts | 商家帳號資料 |
| Cassandra gamesettings | businesses | 商家詳細資料、訂閱狀態、站台與玩法配置 |
| Cassandra gamesettings | business_accounts | 商家子帳號、角色、狀態、密碼（bcrypt 雜湊） |
| Cassandra gamesettings | gametype_settings | 遊戲類型維度的系統玩法設定（含 settings JSON 結構） |
| Cassandra gamesettings | league_settings | 聯賽層級玩法設定 |
| Cassandra gamesettings | template_settings | 玩法模板設定 |
| Cassandra gamesettings | game_settings | 單場遊戲玩法設定 |
| Cassandra gamesettings | league_logs | 聯賽使用記錄與進行中聯賽設定 |
| Cassandra gamesettings | logs / logs_business | 商家操作日誌（記錄設定變更前後值） |
| Cassandra pricecenter | action_logs | 通用操作日誌（審計追溯） |
| PostgreSQL games | games_{sport_code} | 賽事主檔（唯讀，驗證 Game/GID 是否存在） |
| Redis LoginCache | 登入快取 | 快取訂閱者登入狀態 |
| Redis BusinessCache | 商家快取 | 快取商家設定與站台資訊 |

## 對外 API 重點

### 商家管理（BusinessController）
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/businesses` | 建立商家 | ✅ |
| POST | `/api/v1/businesses/{businessCode}/accounts` | 建立商家帳號 | ✅ |
| POST | `/api/v1/businesses/{businessCode}/logininfos` | 登入並取得商家帳號登入資訊 | ✅ |
| POST | `/api/v1/businesses/{businessCode}/inplaygames` | 設定進行中賽事 | ✅ |
| POST | `/api/v1/businesses/{businessCode}/logs` | 寫入商家操作日誌 | ✅ |
| GET | `/api/v1/businesses` | 查詢所有商家 | ✅ |
| GET | `/api/v1/businesses/{businessCode}` | 查詢單一商家 | ✅ |
| GET | `/api/v1/businesses/{businessCode}/accounts` | 查詢商家帳號 | ✅ |
| GET | `/api/v1/businesses/{businessCode}/logininfos/{uid}` | 查詢登入資訊 | ✅ |
| GET | `/api/v1/businesses/{businessCode}/inplaygames/{month}` | 查詢月份進行中賽事 | ✅ |
| GET | `/api/v1/businesses/{businessCode}/logs/{actionType}` | 查詢商家操作日誌 | ✅ |
| PUT | `/api/v1/businesses` | 更新商家設定 | ✅ |
| PUT | `/api/v1/businesses/{businessCode}/extraplayModes` | 更新額外玩法模式 | ✅ |
| PUT | `/api/v1/businesses/{businessCode}/subsites` | 更新子站設定 | ✅ |
| PUT | `/api/v1/businesses/{businessCode}/accounts/{account}/status` | 更新帳號狀態 | ✅ |
| PUT | `/api/v1/businesses/{businessCode}/accounts/{account}/password` | 更新帳號密碼 | ✅ |
| DELETE | `/api/v1/businesses/{businessCode}/logininfos/{uid}` | 刪除登入資訊 | ✅ |

### 站台與玩法設定管理（ConfigController）
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/siteconfigs` | 建立站台設定 | ✅ |
| POST | `/api/v1/leagueinprogressconfigs` | 建立聯賽進行中設定 | ✅ |
| POST | `/api/v1/playmodeconfigs/gametype` | 建立 GameType 玩法設定 | ✅ |
| POST | `/api/v1/playmodeconfigs/league` | 建立聯賽玩法設定 | ✅ |
| POST | `/api/v1/playmodeconfigs/template` | 建立模板玩法設定 | ✅ |
| POST | `/api/v1/playmodeconfigs/game` | 建立單場玩法設定 | ✅ |
| GET | `/api/v1/siteconfigs/{businessCode}` | 查詢商家站台設定 | ✅ |
| GET | `/api/v1/siteconfigs/{businessCode}/{gameType}` | 查詢指定 GameType 站台設定 | ✅ |
| GET | `/api/v1/leagueinprogressconfigs/{businessCode}/{gameType}` | 查詢聯賽進行中設定 | ✅ |
| GET | `/api/v1/playmodeconfigs/all/{businessCode}` | 查詢所有玩法設定 (需帶 dateTime) | ✅ |
| GET | `/api/v1/playmodeconfigs/gametype/{businessCode}/{gameType}` | 查詢 GameType 玩法設定 | ✅ |
| GET | `/api/v1/playmodeconfigs/league/{businessCode}/{gameType}` | 查詢聯賽玩法設定列表 | ✅ |
| GET | `/api/v1/playmodeconfigs/league/{businessCode}/{gameType}/{id}` | 查詢單一聯賽玩法設定 | ✅ |
| GET | `/api/v1/playmodeconfigs/league/{businessCode}/logs/{gameType}` | 查詢聯賽玩法設定日誌 | ✅ |
| GET | `/api/v1/playmodeconfigs/template/{businessCode}/{gameType}` | 查詢模板玩法設定列表 | ✅ |
| GET | `/api/v1/playmodeconfigs/template/{businessCode}/{gameType}/{id}` | 查詢單一模板玩法設定 | ✅ |
| GET | `/api/v1/playmodeconfigs/game/{businessCode}/{gameType}/{gdate}` | 查詢日期單場玩法設定 | ✅ |
| GET | `/api/v1/playmodeconfigs/game/{businessCode}/{gameType}/{gdate}/{lid}/{gid}` | 查詢單場玩法設定 | ✅ |
| PUT | `/api/v1/siteconfigs` | 更新站台設定 | ✅ |
| PUT | `/api/v1/leagueconfigs` | 更新聯賽設定 | ✅ |
| PUT | `/api/v1/leagueinprogressconfigs` | 更新聯賽進行中設定 | ✅ |
| PUT | `/api/v1/playmodeconfigs/gametype` | 更新 GameType 玩法設定 | ✅ |
| PUT | `/api/v1/playmodeconfigs/league` | 更新聯賽玩法設定 | ✅ |
| PUT | `/api/v1/playmodeconfigs/template` | 更新模板玩法設定 | ✅ |
| PUT | `/api/v1/playmodeconfigs/game` | 更新單場玩法設定 | ✅ |

### 系統設定、訂閱者與模板管理（GameSettingServiceController）
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/v1/settings/{company}` | 查詢公司所有系統設定 (需帶 `dateTime`) | ✅ |
| GET | `/api/v1/settings/system/{company}/{gameType}` | 查詢系統 GameType 設定 | ✅ |
| PATCH | `/api/v1/settings/playmodes/add/{gameType}` | 批次新增系統玩法模式 | ✅ |
| PATCH | `/api/v1/settings/playmodes/edit/{gameType}` | 批次編輯系統玩法模式 | ✅ |
| PATCH | `/api/v1/settings/playmodes/delete/{gameType}` | 批次刪除系統玩法模式 | ✅ |
| PATCH | `/api/v1/settings/playmodes/site` | 更新站台支援的玩法模式 | ✅ |
| PATCH | `/api/v1/settings/playmodes/alarm/add/{gameType}` | 新增玩法警報設定 | ✅ |
| POST | `/api/v1/subscriber/register` | 訂閱者註冊 | ✅ |
| GET | `/api/v1/subscriber` | 查詢訂閱者列表 | ✅ |
| GET | `/api/v1/subscriber/{uid}` | 查詢單一訂閱者 | ✅ |
| PATCH | `/api/v1/subscriber` | 更新訂閱者啟用狀態 | ✅ |
| POST | `/api/v1/subscriber/users/register` | 訂閱者用戶註冊 | ✅ |
| POST | `/api/v1/subscriber/users/login` | 訂閱者用戶登入 | ✅ |
| POST | `/api/v1/subscriber/users/logout` | 訂閱者用戶登出 | ✅ |
| GET | `/api/v1/subscriber/users/login/check` | 檢查登入狀態 | ✅ |
| GET | `/api/v1/subscriber/users` | 查詢訂閱者用戶列表 | ✅ |
| PUT | `/api/v1/subscriber/users/password/remake` | 重設用戶密碼 | ✅ |
| PATCH | `/api/v1/subscriber/users` | 更新訂閱者用戶 | ✅ |
| POST | `/api/v1/system/{gameType}` | 建立 GameType 系統設定 | ✅ |
| GET | `/api/v1/system/{gameType}` | 查詢 GameType 系統設定列表 | ✅ |
| GET | `/api/v1/system/{gameType}/{name}` | 查詢指定名稱系統設定 | ✅ |
| POST | `/api/v1/system/layout/{gameType}` | 建立系統佈局 (已廢棄或內部使用) | ✅ |
| GET | `/api/v1/system/playmodes/{gameType}` | 查詢系統玩法模式 (暫無路由，**需人工確認**) | ✅ |
| GET | `/api/v1/system/site/enabled` | 查詢所有啟用站台 | ✅ |
| GET | `/api/v1/system/site/stop` | 查詢所有停止站台 | ✅ |
| GET | `/api/v1/system/site/stop/{company}` | 查詢公司停止站台 | ✅ |
| POST | `/api/v1/system/site/stop/{gameType}` | 設定站台停止 | ✅ |
| DELETE | `/api/v1/system/overduedata` | 清除過期資料 | ✅ |
| POST | `/api/v1/template/{gameType}` | 建立玩法模板 | ✅ |
| GET | `/api/v1/template/{gameType}` | 查詢玩法模板列表 | ✅ |
| GET | `/api/v1/template/{gameType}/{id}` | 查詢單一玩法模板 | ✅ |
| PUT | `/api/v1/template/{gameType}/{id}` | 更新玩法模板 | ✅ |
| POST | `/api/v1/league/{gameType}` | 建立聯賽設定 | ✅ |
| GET | `/api/v1/league/{gameType}` | 查詢聯賽設定列表 | ✅ |
| GET | `/api/v1/league/all/{gameType}` | 查詢所有聯賽設定 | ✅ |
| GET | `/api/v1/league/{gameType}/{id}` | 查詢單一聯賽設定 | ✅ |
| GET | `/api/v1/leaguesetting/{gameType}/{lid}` | 查詢聯賽詳細設定 | ✅ |
| GET | `/api/v1/league/used/{gameType}` | 查詢使用中聯賽 | ✅ |
| PUT | `/api/v1/league/{gameType}/{id}` | 更新聯賽設定 | ✅ |
| PATCH | `/api/v1/league/{gameType}` | 批次更新聯賽設定對應 | ✅ |
| POST | `/api/v1/game/{gameType}/{gid}` | 建立單場遊戲設定 | ✅ |
| GET | `/api/v1/game/{gameType}` | 查詢遊戲設定列表 | ✅ |
| GET | `/api/v1/game/{gameType}/{id}` | 查詢單一遊戲設定 | ✅ |
| GET | `/api/v1/gamesetting/{gameType}/{gdate}/{gid}` | 查詢賽事遊戲設定 | ✅ |
| PUT | `/api/v1/game/{gameType}/{id}` | 更新遊戲設定 | ✅ |
| GET | `/api/v1/log/system/setting/{company}/{gameType}` | 查詢系統設定日誌 | ✅ |
| GET | `/api/v1/log/league/setting/{company}/{gameType}` | 查詢聯賽設定日誌 | ✅ |
| GET | `/api/v1/log/template/setting/{company}/{gameType}` | 查詢模板設定日誌 | ✅ |
| GET | `/api/v1/log/game/setting/{company}/{gameType}` | 查詢遊戲設定日誌 | ✅ |
| GET | `/api/v1/log/site/setting/{company}/{gameType}` | 查詢站台設定日誌 | ✅ |
| GET | `/api/v1/log/{company}/{date}/{id}` | 查詢單筆操作日誌 | ✅ |
| GET | `/api/v1/log/login/{company}` | 查詢商家登入日誌 | ✅ |

### 系統工具（SystemController）
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/system/autocreatetable` | 自動建立 DB Table | ✅ |
| POST | `/api/v1/system/fixapi` | 修復 API 設定 | ✅ |
| GET | `/api/heart` | Health Check | ❌ |
| GET | `/api/version` | 查詢版本號 | ❌ |

## 服務相依

| 相依服務 | 用途 |
|---------|------|
| `pricecenterservice` | 提供賽事 / 聯賽資訊供設定對照 |
| `syncservice` | 負責本服務寫入設定後，更新 Redis 快取（BusinessCache）供前台讀取，本服務本身不直接操作 Redis。 |
| `games` (PostgreSQL) | 驗證賽事 `game` 與 `gdate` 是否存在，確保寫入的遊戲設定合法。 |

## 常見使用場景

1. **後台設定 GameType 玩法模式**
   - 觸發：運營人員調整足球、籃球等玩法開關。
   - 流程：PATCH `/api/v1/settings/playmodes/add/{gameType}` → 寫入 Cassandra `gamesettings.gametype_settings`，並可選擇性更新商家設定。本服務不直接操作 Redis，快取更新由 syncservice 負責（需人工確認）。

2. **商家新增子站帳號**
   - 觸發：管理員為商家新增操作帳號。
   - 流程：POST `/api/v1/businesses/{businessCode}/accounts` → 寫入 `gamesettings.business_accounts`，密碼經 bcrypt 雜湊。

3. **後台設定聯賽玩法**
   - 觸發：上架新聯賽時設定對應玩法。
   - 流程：POST `/api/v1/playmodeconfigs/league` → 驗證 `settings` 為合法 JSON → 寫入 `gamesettings.league_settings` → 記錄操作日誌至 `pricecenter.action_logs`。

4. **訂閱者用戶登入後台工具**
   - 觸發：外部系統訂閱者登入管理介面。
   - 流程：POST `/api/v1/subscriber/users/login` → 驗證帳密 → Redis LoginCache 記錄登入狀態。

5. **查詢聯賽設定日誌**
   - 觸發：後台追蹤設定變更記錄。
   - 流程：GET `/api/v1/log/league/setting/{company}/{gameType}` → 從 Cassandra `action_logs` 讀取操作記錄。

## AI 判斷關鍵字

遊戲設定, 玩法模式, PlayMode, 商家, businessCode, 聯賽設定, 模板, 站台設定, 訂閱者, 系統設定, GameType, 設定管理, 後台配置, 遊戲配置, ConfigController, BusinessController