# GameLiveService WebAPI

- **Git Repository**：https://git.zbdigital.net/biz/gameliveservice.git

## 職責
負責管理**賽事直播社群群組**與**頻道（Channel）**，提供社群聊天室、競猜下注群組、置頂訊息、直播頻道開關控制，以及 SignalR 即時推播功能。是前台直播互動體驗的核心後端服務。

## 技術棧
- 框架：ASP.NET Core (.NET 6.0)、SignalR（即時推播）
- 資料庫：MySQL（Sport DB）、Cassandra（Keyspace: `pricecenter`）、Redis（CommunityCache / GameUserCache）
- 驗證：ECFramework.ECService 1.0.11（內部統一驗證框架）
- 配置中心：Zookeeper
- 日誌：Kafka + Cassandra
- 其他套件：ECCore 2.0.7、GameDataModels 2.0.153、SixLabors.ImageSharp 3.0.2、SignalR 1.1.0

## 資料庫重要 Table

| 儲存層 | Table | 用途 |
|--------|-------|------|
| MySQL Sport | community_groups | 社群群組設定（名稱、對應賽事、圖片） |
| MySQL Sport | game_channels | 直播頻道設定（channelID、gameType、開關狀態） |
| Cassandra pricecenter | chatroom_history | 聊天室歷史訊息 |
| Redis CommunityCache | 群組快取 | 快取社群群組列表與最新聊天訊息 |
| Redis GameUserCache | 會員快取 | 快取線上會員資訊 |

## 對外 API 重點

### 社群群組管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/communities/groups` | 建立社群群組 | ✅ |
| POST | `/api/v1/communities/groups/{id}/topmessage` | 設定置頂訊息 | ✅ |
| POST | `/api/v1/communities/groups/{gid}/predictbet` | 設定群組競猜下注 | ✅ |
| POST | `/api/v1/communities/groups/{id}/upload` | 上傳群組圖片 | ✅ |
| GET | `/api/v1/communities/groups` | 查詢所有社群群組 | ✅ |
| GET | `/api/v1/communities/groups/{id}` | 查詢單一社群群組 | ✅ |
| GET | `/api/v1/communities/groups/chatroom/lastmessage` | 查詢各群組最新訊息 | ✅ |
| GET | `/api/v1/communities/chatrooms/{gid}/messages` | 查詢聊天室歷史訊息 | ✅ |
| GET | `/api/v1/communities/groups/{id}/predictbets` | 查詢群組競猜下注 | ✅ |
| GET | `/api/v1/communities/groups/{id}/predictcount/{date}/accounts/{account}` | 查詢帳號競猜次數 | ✅ |
| PUT | `/api/v1/communities/groups/{id}` | 更新社群群組 | ✅ |
| PUT | `/api/v1/communities/groups/{id}/livegame` | 更新群組直播賽事 | ✅ |

### 直播頻道管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/channel` | 建立或更新頻道 | ✅ |
| GET | `/api/v1/channels` | 查詢頻道列表 | ✅ |
| GET | `/api/v1/channel/single` | 查詢單一頻道 | ✅ |
| PUT | `/api/v1/channels` | 批次更新頻道 | ✅ |
| PUT | `/api/v1/channel/open` | 開啟頻道 | ✅ |
| PUT | `/api/v1/channel/close` | 關閉頻道 | ✅ |

### 系統工具
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/v1/autocontrolchannel` | 自動控制頻道開關 | ✅ |
| GET | `/api/v1/system/community/logs` | 查詢聊天室歷史（管理） | ✅ |
| GET | `/api/v1/system/community/editorlogs` | 查詢編輯者聊天記錄 | ✅ |
| PUT | `/api/v1/updateallowchannels` | 更新允許頻道清單 | ✅ |
| GET | `/api/heart` | Health Check | ❌ |
| GET | `/api/version` | 查詢版本號 | ❌ |

## 服務相依

| 相依服務 | 用途 |
|---------|------|
| `pricecenterservice` | 讀取賽事資料更新群組直播賽事資訊 |
| `memberservice` | 驗證會員身份（GameUserCache） |
| `predictservice` | 提供群組競猜下注資料 |

## 常見使用場景

1. **前台開啟直播社群群組**
   - 觸發：使用者進入直播賽事頁面
   - 流程：GET `/api/v1/communities/groups` → 從 Redis CommunityCache 讀取群組資料 → SignalR 連線加入聊天室

2. **後台建立新社群群組**
   - 觸發：管理員為新賽事建立對應社群群組
   - 流程：POST `/api/v1/communities/groups` → 寫入 MySQL → 更新 Redis 快取

3. **直播頻道開關控制**
   - 觸發：賽事開始/結束或管理員手動控制
   - 流程：PUT `/api/v1/channel/open` 或 `close` → 更新 MySQL game_channels → SignalR 廣播狀態變更

4. **群組競猜下注設定**
   - 觸發：管理員為群組設定對應競猜賽事
   - 流程：POST `/api/v1/communities/groups/{gid}/predictbet` → 寫入群組競猜設定 → 前台查詢競猜選項

5. **查詢聊天室歷史訊息**
   - 觸發：使用者進入聊天室，載入歷史訊息
   - 流程：GET `/api/v1/communities/chatrooms/{gid}/messages` → 從 Cassandra 讀取歷史訊息

## AI 判斷關鍵字

直播, 社群群組, 聊天室, 頻道, SignalR, 置頂訊息, 群組競猜, 頻道開關, 即時推播, 直播社群, 賽事直播, 聊天記錄
