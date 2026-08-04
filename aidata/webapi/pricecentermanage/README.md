# PriceCenterManage WebAPI

- **Git Repository**：https://git.zbdigital.net/biz/pricecentermanage.git
- **PortainerKey**：PRD_Docker_Swarm|swarm|pricecentermanage|pricecentermanage_PriceCenterManage
- **Kind**：webapi

## 職責
負責**價格中心管理後台**的通知、站內信、App 裝置版本、每日報表，以及爬蟲機器（Crawler）心跳監控與 Bet365、Pinnacle 等爬蟲頁面排程管理。本服務是後台管理層與底層爬蟲系統之間的橋接服務。

## 技術棧
- 框架：ASP.NET Core (.NET 6.0)
- 資料庫：MySQL（Sport DB）、Cassandra（Keyspace: `pricecenter`、`predict`）、Redis（SportCache / SportAccountCache）
- 驗證：ECFramework.ECService 2.0.0（內部統一驗證框架）
- 配置中心：Zookeeper
- 日誌：Kafka + Cassandra
- 其他套件：ECCore 2.0.5、GameDataModels 2.0.1

## 資料庫重要 Table

| 儲存層 | Table | 用途 |
|--------|-------|------|
| MySQL Sport | notification_topics | 通知主題 |
| MySQL Sport | notification_messages | 通知訊息內容 |
| MySQL Sport | notification_sitemails | 站內信記錄 |
| MySQL Sport | app_devices | App 裝置版本設定 |
| Cassandra pricecenter | member_daily_reports | 會員每日統計報表 |
| Cassandra pricecenter | predict_daily_reports | 競猜每日統計報表 |
| Cassandra pricecenter | bet365pages | Bet365 爬蟲頁面排程設定 |
| Redis SportCache | NotificationTopics | 快取通知主題清單（Hash，field 為 tid） |
| Redis SportAccountCache | SiteMails_{account} | 快取帳號站內信主旨（Hash，field 為 mail id） |
| Redis SportCache | AppDevices | 快取 App 裝置版本（Hash，field 為 device） |
| Redis SportCache | NotificationMessages_{hashKey} | 快取通知訊息（Hash，field 為 message id） |

## 對外 API 重點

### 推播通知管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/sport/notifications/topics` | 建立通知主題 | ✅ |
| POST | `/api/v1/sport/notifications/messages/{tid}` | 建立通知訊息 | ✅ |
| GET | `/api/v1/sport/notifications/topics` | 查詢通知主題列表（支援 cacheData 參數） | ✅ |
| GET | `/api/v1/sport/notifications/messages/{tid}` | 查詢主題訊息列表 | ✅ |
| GET | `/api/v1/sport/notifications/messages` | 查詢所有通知訊息（快取彙總） | ✅ |
| PUT | `/api/v1/sport/notifications/topics/{id}` | 更新通知主題 | ✅ |
| PUT | `/api/v1/sport/notifications/messages/{tid}/{id}` | 更新通知訊息 | ✅ |

### 站內信管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/sport/notifications/sitemails` | 建立站內信（群發） | ✅ |
| POST | `/api/v1/sport/notifications/sitemails/delete` | 批次刪除站內信 | ✅ |
| GET | `/api/v1/sport/notifications/sitemails` | 查詢站內信列表（後台，依時間區間） | ✅ |
| GET | `/api/v1/sport/notifications/sitemails/{account}/subjects` | 查詢帳號站內信主旨 | ✅ |
| GET | `/api/v1/sport/notifications/sitemails/{account}/{id}` | 查詢單封站內信完整內容 | ✅ |
| PUT | `/api/v1/sport/notifications/sitemails/{account}/{id}/readstatus` | 更新單封信件讀取狀態 | ✅ |

### App 裝置版本管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/appmanage/sport/appdevices` | 設定 App 裝置版本 | ✅ |
| GET | `/api/v1/appmanage/sport/appdevices` | 查詢所有裝置版本 | ✅ |
| GET | `/api/v1/appmanage/sport/appdevices/{device}` | 查詢指定裝置版本 | ✅ |

### 每日報表
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/sport/report/member` | 建立會員每日報表 | ✅ |
| POST | `/api/v1/sport/report/predict` | 建立競猜每日報表 | ✅ |
| GET | `/api/v1/sport/report/member` | 查詢會員每日報表（sdate, edate 必填） | ✅ |
| GET | `/api/v1/sport/report/predict` | 查詢競猜每日報表（sdate, edate 必填） | ✅ |

### 系統監控與爬蟲管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/v1/system/info` | 查詢系統資訊（機器狀態、爬蟲狀態） | ✅ |
| GET | `/api/v1/system/sites/infos` | 查詢站台即時狀態 | ✅ |
| POST | `/api/v1/system/machines/{machinename}/{program}` | 機器心跳回報 | ✅ |
| POST | `/api/v1/system/machines/crawler` | CrawlerService 狀態回報 | ✅ |
| GET | `/api/v1/bet365/allpage` | 查詢所有 Bet365 頁面 | ✅ |
| GET | `/api/v1/bet365/pages` | 依類型查詢 Bet365 頁面 | ✅ |
| POST | `/api/v1/bet365/page/{pagename}` | 更新指定頁面排程設定 | ✅ |
| POST | `/api/v1/bet365/pages/{pagetype}` | 批次更新頁面排程 | ✅ |
| GET | `/api/v1/bet365/sendstop/{provider}/{pagename}` | 停止指定爬蟲頁面 | ✅ |
| GET | `/api/heart` | Health Check（回傳伺服器時間 yyyy-MM-dd HH:mm:ss.fff） | ❌ |
| GET | `/api/version` | 查詢版本號（回傳版本、環境、組件建置時間） | ❌ |

## 服務相依

| 相依服務 | 用途 |
|---------|------|
| `pricecenterservice` | 提供賽事資料供報表統計、站台資訊查詢 |
| `mq`（Message Queue） | 發送推播通知至 App 裝置 |
| Bet365 / Pinnacle 爬蟲機器群 | 受管控的爬蟲程序，進行心跳回報與頁面排程同步 |
| `memberservice`（推測） | 驗證管理員帳號權限、取得會員資訊用於報表 |
| `crawlerservice`（推測） | 爬蟲任務調度與執行 |

## 常見使用場景

1. **後台發送活動推播通知**
   - 觸發：後台管理員建立活動推播
   - 流程：POST `/api/v1/sport/notifications/topics` 建立主題 → POST `/api/v1/sport/notifications/messages/{tid}` 新增訊息 → 透過 mq 推播至 App

2. **發送站內信給會員**
   - 觸發：後台客服或行銷人員群發信件
   - 流程：POST `/api/v1/sport/notifications/sitemails` → 寫入 MySQL 並同步更新 Redis `SiteMails_{Account}` → 前台查詢時讀取快取

3. **App 版本強制更新設定**
   - 觸發：新版 App 上線，需強制舊版用戶更新
   - 流程：POST `/api/v1/appmanage/sport/appdevices` 設定最低版本號 → 同步更新 Redis `AppDevices` → App 啟動時查詢版本判斷是否強制更新

4. **每日統計報表產生**
   - 觸發：每日排程自動執行
   - 流程：POST `/api/v1/sport/report/member` + POST `/api/v1/sport/report/predict` → 寫入 Cassandra `pricecenter` keyspace

5. **監控爬蟲機器健康狀態**
   - 觸發：各爬蟲機器定時回報心跳
   - 流程：POST `/api/v1/system/machines/crawler` → 記錄各爬蟲狀態 → 後台管理員透過 GET `/api/v1/system/info` 查看儀表板

## AI 判斷關鍵字

通知, 推播, 站內信, App 版本, 裝置管理, 每日報表, 爬蟲監控, Bet365, Pinnacle, 頁面排程, 心跳, 管理後台, 價格中心管理