# 查詢指定裝置版本

## 1. 場景目的
後台管理員或自動化排程根據裝置名稱（例如 `iOS`、`Android`）查詢對應的最低版本要求，供後續版本強制更新判斷或設定參考。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/appmanage/sport/appdevices/{device}` | 查詢指定裝置的最低版本設定 |

---

## 3. 流程總覽

1. 接收 GET request，路徑參數包含 `device` 名稱（如 `iOS`, `Android`）。
2. ECFramework 驗證 Bearer token（需為有效的管理後台登入 session）。
3. Controller 調用 Service 層，傳入 `device` 字串。
4. Service 層優先查詢 Redis 快取（Key: `AppDevices`，Hash 結構）。
5. 若 Redis 命中，直接將 JSON 反序列化為 `AppDevice` 物件並回傳。
6. 若 Redis 未命中，查詢 MySQL `sport` 資料庫的 `app_devices` 表。
7. 根據 `WHERE device = ?` 條件取得一筆紀錄。
8. 若 DB 亦無資料，回傳 404 或空物件（需人工確認）。
9. 回傳 `AppDevice` 物件，包含 `device`、`version` 等欄位。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware | ECFramework Auth | 驗證 JWT token 有效性與權限 |
| 2 | Controller | AppManagementController.Get | 接收 `{device}` 路徑參數，調用 Service |
| 3 | Service | IAppDeviceService.Get | 組合 Redis Key `AppDevices`，執行 `HashGet(device)` |
| 4 | Provider | RedisCacheProvider | 執行 Redis `HGET AppDevices {device}` |
| 5 | Service | IAppDeviceService.Get | 若 Redis 回傳非空，反序列化回 `AppDevice` |
| 6 | Service | IAppDeviceService.Get | 若 Redis 未命中，調用 DB Provider 查詢 MySQL |
| 7 | Provider | SportDbContext / Dapper | 查詢 `app_devices` 表 `WHERE device = ?` |
| 8 | Provider | RedisCacheProvider | 非同步將查詢結果寫入 Redis `HSET AppDevices {device}`（無 TTL） |
| 9 | Controller | AppManagementController.Get | 序列化 `AppDevice` 為 JSON response |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | MySQL `sport.app_devices` | Read | 當 Redis 未命中時，查詢指定 `device` 的版本資料 |
| Redis | Redis (SportCache) `AppDevices` | Read / Write | Hash 結構，field=`device`，value=`AppDevice` JSON；永久有效，僅管理者手動刪除或 DB 更新時失效 |

---

## 6. 重要規則

- **權限限制**：必須通過管理後台權限驗證（Bearer token），不可匿名存取。
- **資料來源優先序**：Redis 快取為主要讀取來源，DB 為備用。讀取到 DB 資料時應回寫 Redis。
- **不可暴露欄位**：無敏感欄位，但需確保 `AppDevice` 回傳結構僅包含必要資訊（如 `device`, `minVersion` 等）。
- **TTL 規則**：Redis Key `AppDevices` 無 TTL，永久有效。在透過 `POST /api/v1/appmanage/sport/appdevices` 更新 DB 時，必須同步 `HDEL AppDevices {device}` 刪除對應 field，以保證快取一致性。
- **Transaction 規則**：DB 查詢為單一 `SELECT`，不涉及 Transaction。
- **Retry 規則**：無。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 無效或過期的 token | 回傳 401 Unauthorized |
| 權限不足（非管理後台角色） | 回傳 403 Forbidden |
| Redis 命中，正常流程 | 回傳 200，body 含 `AppDevice` 物件 |
| Redis 未命中但 DB 存在 | 查詢 DB 後回傳 200，並異步寫入 Redis |
| Redis 與 DB 皆查無此 `device` | 回傳 404 Not Found 或狀態碼 200 但回傳空物件（需人工確認專案慣例） |
| Redis 連線失敗 | Service 需有 fallback 到 DB 的機制，不可讓 request 直接失敗 |
| DB 連線逾時 | 回傳 503 Service Unavailable |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | API Test | 查詢已知裝置（如 `iOS`），Redis 命中 | 200 OK，回傳 `AppDevice` JSON |
| T2 | Integration Test | 查詢已知裝置，但手動刪除 Redis 快取 | 200 OK，Service 查詢 DB 後回傳正確資料，且 Redis 被重新寫入 |
| T3 | API Test | 查詢不存在的裝置（如 `Windows`） | 404 Not Found 或 200 且 body 為空 |
| T4 | Permission Test | 不帶 token 請求 | 401 Unauthorized |
| T5 | Flow Test | 先更新 `app_devices`，再立刻查詢 | 第一次查到舊快取，更新後因 DEL 了快取，第二次查詢會讀 DB 得到新版本 |

---

## 9. 高風險區域

- **Cache Consistency**：`POST /api/v1/appmanage/sport/appdevices` 更新版本時，若忘記 `HDEL AppDevices {device}`，將導致此查詢 API 長期返回過期版本資訊，造成前端強制更新判斷失靈。
- **單點依賴**：此流程高度依賴 `Redis (SportCache)` 健康狀態。若 Redis 故障，雖然有 DB fallback，但需確保程式碼中已實作錯誤處理，不會 crash。

---

## 10. 常見錯誤

- **AI 誤解資料源**：可能會誤以為 Cassandra `pricecenter.extension_version` 或 `AppDevices` 是其主儲存。實際上，根據 `detail` 文件，`app_devices` 是 MySQL Table，且 Redis `AppDevices` 是為此設計的快取。
- **未同步快取與 DB**：在更新 DB 後忘記清除 Redis 的特定 field，違反 `db-usage` 中「DB 更新時 DEL」的規則。
- **全表查詢**：在查詢時可能誤用 `GET /api/v1/appmanage/sport/appdevices` 的邏輯去查詢所有設備再過濾，而非使用單一查詢的 Hash 或 DB 精確查詢。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | AppManagementController.Get (by `OpenAPI` path `/api/v1/appmanage/sport/appdevices/{device}`) |
| DB | MySQL `sport.app_devices` (by `sport-detail.md` "Table：app_devices" - 需人工確認) |
| Redis | `AppDevices` (Hash, field=device, value=AppDevice) (by `db-usage` & `pricecentermanage-detail.md`) |
| Code Semantics | `AppDevice` model 欄位包含 `device`、`enabled` 等 (by `Code semantics Phase0/1`) |
| Rules | DB 寫入時需主動 `DEL` Redis 對應 field (by `pricecentermanage-detail.md` _Redis-DEL_) |