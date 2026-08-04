# AdvertisingService WebAPI

- **Git Repository**：https://git.zbdigital.net/biz/advertisingservice.git

## 職責
負責管理平台的**廣告投放**與**佈告欄公告**，提供廣告的建立、查詢、更新，以及公告的完整 CRUD。廣告資料依版位（adArea）分類管理，並支援圖片檔案上傳。

## 技術棧
- 框架：ASP.NET Core (.NET 8.0)
- 資料庫：Cassandra（Keyspace: `ads`）、Redis（SportAdCache）
- 驗證：ECFramework.ECService（內部統一驗證框架）
- 配置中心：Zookeeper
- 日誌：Kafka + Cassandra
- 其他套件：ECCore 3.0.2、AdvertisingModels 0.0.6

## 資料庫重要 Table

| 儲存層 | Table | 用途 |
|--------|-------|------|
| Cassandra ads | sport_advertisements | 體育廣告資料（版位、圖片、連結、啟用狀態） |
| Cassandra ads | announcements | 公告佈告欄資料（標題、內容、顯示期間） |
| Redis SportAdCache | 廣告快取 | 快取各版位廣告列表與公告，減少 DB 查詢 |

## 對外 API 重點

### 廣告管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/sport/ads` | 建立廣告 | ✅ |
| GET | `/api/v1/sport/ads` | 查詢所有廣告 | ✅ |
| GET | `/api/v1/sport/ads/{adArea}` | 查詢指定版位廣告 | ✅ |
| PUT | `/api/v1/sport/ads/{adArea}/{id}` | 更新廣告 | ✅ |

### 公告佈告欄
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/sport/bulletinboard/announcenments` | 建立公告 | ✅ |
| GET | `/api/v1/sport/bulletinboard/announcenments` | 查詢所有公告 | ✅ |
| GET | `/api/v1/sport/bulletinboard/announcenments/{aid}` | 查詢單一公告 | ✅ |
| PUT | `/api/v1/sport/bulletinboard/announcenments/{aid}` | 更新公告 | ✅ |
| DELETE | `/api/v1/sport/bulletinboard/announcenments/{aid}` | 刪除公告 | ✅ |

### 系統工具
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/system/upload/imgfile/{site}` | 上傳廣告圖片 | ✅ |
| POST | `/api/v1/system/autocreatetable` | 自動建立 Cassandra Table | ✅ |
| GET | `/api/heart` | Health Check | ❌ |
| GET | `/api/version` | 查詢版本號 | ❌ |

## 服務相依

| 相依服務 | 用途 |
|---------|------|
| _(無外部服務相依)_ | 獨立服務，資料自行儲存於 Cassandra / Redis |

## 常見使用場景

1. **後台新增廣告**
   - 觸發：行銷人員在後台建立新廣告活動
   - 流程：POST `/api/v1/system/upload/imgfile/{site}` 上傳圖片取得 URL → POST `/api/v1/sport/ads` 建立廣告（含版位、連結、圖片 URL）

2. **前台查詢指定版位廣告**
   - 觸發：前台頁面載入廣告版位
   - 流程：GET `/api/v1/sport/ads/{adArea}` → 從 Redis SportAdCache 讀取快取廣告資料

3. **後台發布公告**
   - 觸發：運營人員發布系統維護或活動公告
   - 流程：POST `/api/v1/sport/bulletinboard/announcenments` 建立公告 → 寫入 Cassandra + Redis 快取

4. **前台顯示公告**
   - 觸發：使用者進入網站首頁或公告頁
   - 流程：GET `/api/v1/sport/bulletinboard/announcenments` → 從 Redis 讀取快取公告列表

## AI 判斷關鍵字

廣告, 版位, 公告, 佈告欄, 圖片上傳, 行銷, 活動廣告, 跑馬燈, Banner, adArea, 宣傳, 通知公告
