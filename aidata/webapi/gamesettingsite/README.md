# GameSettingSite — 內部服務目錄

## 概述

GameSettingSite 為 .NET 10 Web API 服務，負責**遊戲設定管理**與**業務後台配置**。提供站點、聯賽、玩法模式的動態設定，整合 AI 賽事預測新聞、商家帳號權限管理、賽事查詢及盤口變動日誌等功能。

## 主要功能

- **遊戲設定管理**
  - 系統層級設定（SystemSettings）：動態讀取玩法佈局映射（PlayModeLayoutMapping）、快取聯盟／隊伍多語名稱
  - 聯賽層級設定（LeagueSettings）：聯賽專屬玩法配置、啟用/停用管理、跨設定檔移動聯盟（MoveLeague）
  - 賽事層級設定（GameSettings）：單場賽事玩法覆蓋、依 GID 查詢與更新
  - 範本管理（TemplateSettings）：玩法範本 CRUD，供聯賽設定引用

- **業務後台配置**
  - 商家帳號登入／登出、密碼更新、權限驗證、帳號狀態管理（啟用/停用）
  - 商家訂閱資訊查詢（球種、站台、走地/早盤授權）
  - 商家操作記錄查詢（登入、站台配置、玩法配置等）
  - 商務號交易員帳號管理（admin 權限）

- **商家玩法與站台配置**
  - 球種站台啟用設定（SiteConfig）
  - 聯盟走地配置（LeagueInProgressConfig）
  - 聯盟／範本玩法設定值 CRUD（PlayModeConfig）
  - 賽事玩法設定值查詢與更新
  - 三級回退邏輯：賽事設定 → 聯盟設定 → 系統設定

- **AI 賽事新聞**
  - 依球種與日期查詢 AI 預測新聞（GS 版本，`ainews_gs`）
  - 多語系版本查詢
  - 近期 AI 預測新聞與結果查詢
  - 前台展示僅回傳 `status=1`（已回應）的新聞
  - AI 新聞標記已使用（Mark as used）功能，避免重複展示

- **賽事與盤口查詢**
  - 依站點、日期取得聯賽與賽事列表
  - 單場詳細資訊（含多語名稱映射）
  - 走地盤口變動日誌查詢
  - 站台賽事警報日誌查詢

- **預測策略**（預計廢除）
  - 機器學習預測結果查詢（依日期區間、聯賽）

## 技術棧

| 分類 | 技術 |
|------|-----|
| 語言／框架 | C# / .NET 10.0 |
| 部署平台 | Docker + Docker Swarm (Portainer Key: `PRD_Docker_Swarm`) |
| 基礎映像 | `mcr.microsoft.com/dotnet/sdk:10.0` |
| 外部依賴 | ECCore、GameDataModels、ECFramework.ECService |
| 訊息與日誌 | Kafka Logger（實際機制需人工確認） |
| 資料來源 | PriceCenter、BusinessProvider、MachineLearningDataProvider |
| 快取 | 檔案快取 (IFileCacheProvider，實際使用範圍需人工確認)、記憶體快取 |
| 資料庫 | Cassandra（news, gamesettings, pricecenter）、PostgreSQL（games）、MySQL（sport） |

> **Redis 使用狀況**：本服務**目前未使用 Redis**。

## 組態與部署注意

- **Dockerfile**
  - 使用 `mcr.microsoft.com/dotnet/sdk:10.0` 作為基底
  - 暴露 Port **5000**（容器內；Swarm 環境可透過 overlay 網路對映其他 Port）
  - 設定時區為 `Asia/Taipei`
  - 執行入口：`dotnet GameSettingSite.dll`

- **環境變數**
  - `TZ=Asia/Taipei`（時區設定）
  - 建議掛載 `appsettings.json` 或透過 Swarm config/secrets 注入連線字串與第三方服務金鑰

- **相依服務**
  - 需確保 PriceCenter、BusinessProvider 等內部服務可連線
  - 若啟用 AI 新聞功能，需有 `IAINewsService` 對應實作（依賴 news keyspace）

- **部署堆疊名稱**：`gamesettingsite`（依據 Portainer Key 推斷）

## 相關連結

- **原始碼**：`https://git.zbdigital.net/biz/gamesettingsite.git`
- **Portainer**：請參考內部 Portainer 管理介面，搜尋 `gamesettingsite` 堆疊
- **服務負責團隊**：後端平台組（如需要請聯繫）

## 主要 API 端點

### 認證與使用者管理（Auth）
| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/auth/login` | 後台使用者登入 |
| POST | `/api/auth/logout` | 使用者登出 |
| GET | `/api/auth/check` | 檢查登入狀態 |
| POST | `/api/auth/update/password` | 更新密碼 |
| GET | `/api/auth/subscriber/{uid}` | 取得訂閱者資訊 |

### 商家管理（Business）
| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/businesses/{businessCode}/login` | 商家帳號登入 |
| GET | `/api/businesses/{businessCode}` | 取得商家訂閱資訊 |
| GET | `/api/businesses/{businessCode}/accounts` | 取得商家所有帳號（admin） |
| POST | `/api/businesses/{businessCode}/accounts` | 新增交易員帳號（admin） |
| PUT | `/api/businesses/{businessCode}/accounts/{account}/password` | 更新帳號密碼 |
| PUT | `/api/businesses/{businessCode}/accounts/{account}/status` | 更新帳號狀態 |
| GET | `/api/businesses/{businessCode}/logs/{actionType}` | 取得操作紀錄 |

### AI 新聞（AINews）
| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/ainews/{gameType}/{date}` | 取得站台賽事 AI 新聞（GS 版本）；回傳已發布（status=1）的預測資訊，組裝為 `AINewsDTO` 陣列 |
| GET | `/api/ainews/lang/{date}/{gid}` | 取得 AI 新聞多語版本 |
| GET | `/api/ainews/lastest/{gameType}` | 取得近期 AI 預測新聞與結果 |
| PUT / POST | （待人工確認） | 標記 AI 新聞為已使用（Mark as used），更新 `ainews.used=1` ；OpenAPI 未揭露具體路由 |

### 遊戲設定（GameSetting）
| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/mapping/league/{gameType}` | 取得聯盟對照列表 |
| GET | `/api/detail/game/{gameType}` | 取得系統賽事明細 |
| GET | `/api/list/sitegame/{gameType}/{site}` | 依站台/日期列出賽事 |
| — | — | 其餘設定 CRUD 端點請參考 Swagger 文件 |

### 日誌（Log）
| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/logs/alertlogs/sitegames/{gameType}/{site}` | 取得站台賽事警報日誌 |
| GET | `/api/logs/inplayspreadlogs/games/{gameType}/{gdate}/{gid}` | 取得走地盤口變化日誌 |

### 主要業務場景（Scenario Flows）

> 以下場景流程文件提供端到端的詳細規範，涵蓋 DB 操作、權限規則、錯誤處理與測試重點：

| 場景 | 文件 |
|------|------|
| 商家後台登入 | [auth-flow/business-login.md](./webapi/gamesettingsite/scenario-flows/auth-flow/business-login.md) |
| 取得站台賽事 AI 新聞 | [query-flow/get-ainews-by-gametype-date.md](./webapi/gamesettingsite/scenario-flows/query-flow/get-ainews-by-gametype-date.md) |
| 取得 AI 新聞多語版本 | [query-flow/get-ainews-lang-version.md](./webapi/gamesettingsite/scenario-flows/query-flow/get-ainews-lang-version.md) |
| 取得近期 AI 預測新聞 | [query-flow/get-latest-ainews-predictions.md](./webapi/gamesettingsite/scenario-flows/query-flow/get-latest-ainews-predictions.md) |
| 取得聯賽設定 | [query-flow/query-league-settings.md](./webapi/gamesettingsite/scenario-flows/query-flow/query-league-settings.md) |
| 取得賽事與盤口資訊 | [query-flow/query-match-list.md](./webapi/gamesettingsite/scenario-flows/query-flow/query-match-list.md) |
| 標記 AI 新聞已使用 | [update-flow/mark-ainews-used.md](./webapi/gamesettingsite/scenario-flows/update-flow/mark-ainews-used.md) |
| 更新商家帳號狀態 | [update-flow/update-business-account-status.md](./webapi/gamesettingsite/scenario-flows/update-flow/update-business-account-status.md) |

## DB 操作邊界摘要

| 資料庫 | 角色 | 主要操作 |
|--------|------|---------|
| `gamesettings` | owner / writer / reader | 商家帳號 CRUD、遊戲設定與玩法配置 |
| `news` | primary writer / reader（⚠️ 寫入權限衝突待人工） | AI 新聞查詢、`used` 欄位標記；服務摘要聲明有 `owner/writer/reader` 權限，但部分跨服務文件建議為 `reader`，需人工確認最終角色 |
| `games` (PostgreSQL) | reader | 賽事、隊伍查詢（唯讀） |
| `pricecenter` | owner / writer / reader（⚠️ 角色定義差異待人工） | 對 `accounts_*` 系列表有完整的讀寫權限；對 `actionlog` 為 `writer/reader`，可寫入操作日誌。**gamesettingsite 自行管理**，不經由其他服務層 |
| `sport` (MySQL) | owner / writer / reader（⚠️ 權限範圍待人工） | 對 `BK_SitePlayers` 表讀寫；對 `ChatRoomHistories_Backup`、`Community_Groups`、`GameUsers_Wallet`、`Notification_Messages` 等表僅有讀取權限 |

> **`gamesettings` 寫入限制**：`gamesettingsite` 對 `gamesettings` keyspace 擁有 `owner/writer/reader` 權限，但實際寫入操作須透過 `gamesettingservice` 核心服務執行（如 `business_accounts.status` 變更），不可繞過核心服務直接寫入 DB。詳見 DB 詳細文件中的跨服務限制。
>
> **`pricecenter` 帳號管理**：`gamesettingsite` 對 `accounts_*` 表擁有 `owner/writer/reader` 權限，可直接進行帳號 CRUD 操作，不需經由其他服務層。`actionlog` 的寫入亦由 `gamesettingsite` 自行處理。⚠️ 此部分與 `gamesettings` 的寫入路徑不同，需人工確認實際實作架構是否與 DB 角色定義一致。
>
> 詳細 DB 欄位限制、讀寫規則、敏感欄位不可回傳規則與所有「⚠️ 衝突待人工」項目，請參閱 [gamesettingsite-detail.md](./webapi/gamesettingsite/gamesettingsite-detail.md) 及各 DB 詳細文件。

## 不負責事項

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| AI 回答生成 | gamesetting-llm / newsservice | 僅負責查詢與展示，實際 LLM 生成由上游服務處理 |
| 賽事資料維護 | gameliveservice / gamesetting-match | 賽事主資料由上游服務寫入 |
| 投注盤口即時更新 | pricecenterservice | 盤口資料來自外部服務，本服務僅查詢與展示 |
| 商家本體帳號同步建立 | syncservice / zbaparser | 本服務可建立交易員帳號與管理 `business_accounts.status`，但商家本體（`businesses`）由上游同步 |
| 遊戲設定核心寫入 | gamesettingservice | `gamesettingsite` 為 `gamesettings` 的 `owner`，但部分業務規則要求寫入經 `gamesettingservice` 處理（詳見 DB 操作邊界） |

## 需人工確認事項

- **Kafka Logger**：現有 README 標示使用 Kafka Logger（需人工確認），但提供的程式碼片段未見直接引用，需確認實際日誌機制
- **IFileCacheProvider**：現有 README 標示使用檔案快取，需確認實際使用範圍與實作
- **sport DB 寫入範圍**：`gamesettingsite` 對 `sport` MySQL 的寫入權限與具體操作需進一步確認
- **token 管理機制**：登入後的 token 格式（JWT/Session）、TTL、儲存位置需人工確認
- **gamesettingsite 對 news keyspace 的寫入權限**：服務摘要聲明有 `owner/writer/reader` 權限，但部分跨服務文件標記為 `reader`；`used`、`llmsettings` 等欄位的寫入操作衝突需人工審核確認最終角色
- **`pricecenter` 帳號管理架構**：`gamesettingsite` 對 `pricecenter.accounts_*` 為 `owner/writer/reader`，可自行管理帳號（不經由其他服務），需確認與 `gamesettings` 寫入須經 `gamesettingservice` 的架構差異是否符合設計意圖
- **`pricecenter` 服務角色全局定義差異**：服務摘要將 `gamesettingsite` 對 `pricecenter` 的全局角色定義為 `reader`（唯讀），但 DB 詳細文件中 `accounts_*` 帳號相關表與 `pricecenter-detail.md` 的角色總覽均記為 `writer/reader`，兩者不一致，需人工確認並統一
- **`actionlog.date` 欄位**：寫入時由服務端自動填充，不可由外部指定
- **API 路徑更新**：部分 API 路徑已確認（如 `POST /api/auth/login`、`POST /api/businesses/{businessCode}/login` 等），但仍有部分非公開 API 需人工確認
- **AINews 標記已使用 API**：OpenAPI 未揭露具體路由
- **`ainews.status` 語意衝突**：`gamesettingsite-detail.md` 與 `news-detail.md` 對 `status` 之值定義（待處理/已回應/已修正 vs 賽前/實況/賽後）不一致，需人工確認並統一
- **`gamesettingsite` 寫入 `news` 權限衝突**：多處跨服務文件對同一服務在 `news` keyspace 的寫入角色描述不一致，需資深工程師全面複核並統一修正
- **Docker 內部 Port（5000）與 Swarm 環境對外 Port**：Dockerfile 暴露容器內 5000 Port，Swarm 部署時需透過 Portainer 設定實際外部 Port 映射