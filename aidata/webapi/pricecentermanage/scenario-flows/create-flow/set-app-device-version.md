# 設定 App 裝置版本

## 1. 場景目的

管理員設定各裝置 (iOS/Android) 的最低 App 版本，供終端用戶 App 啟動時查詢並判斷是否需要強制更新。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/appmanage/sport/appdevices` | 設定或更新指定裝置的最低版本需求 |
| GET | `/api/v1/appmanage/sport/appdevices` | 取得所有裝置的版本設定 (由用戶端 App 呼叫) |
| GET | `/api/v1/appmanage/sport/appdevices/{device}` | 取得指定裝置的版本設定 |

---

## 3. 流程總覽

1. 管理員經由後台 UI 提交表單資料。
2. UI 呼叫 `POST /api/v1/appmanage/sport/appdevices`，並在 Request Body 中包含 `Device` 與 `Version` 欄位。
3. `pricecentermanage` 驗證管理員權限。
4. 將收到的 `AppDevice` 資料寫入 MySQL `sport.app_devices` 表。
5. 寫入成功後，立即更新 Redis `SportCache` 中的 `AppDevices` 快取，以 Hash 結構儲存，確保終端 App 查詢時能取到最新版本。
6. 終端 App 啟動時，呼叫 `GET /api/v1/appmanage/sport/appdevices` 取得所有裝置的最低版本設定，與自身版本比對，決定是否強制更新。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `AppManagementController.SetSportAppDevice()` | 接收 HTTP POST 請求，調用 `AppManagementService`。API 路徑需包含前綴 `/api/v1/`。 |
| 2 | Model Transfer | `AppDevice` | 定義請求結構，包含 `Device` (string) 與 `Version` (string)。 |
| 3 | Service | `AppManagementService.SetSportAppDevice()` | 業務邏輯層，負責將資料傳遞給 Provider 進行寫入。 |
| 4 | Provider | (需人工確認) | 推測負責執行 MySQL `app_devices` 表的寫入操作，以及更新 Redis `AppDevices` 快取。將 `AppDevice` 物件序列化為 JSON 後，以 `HSET` 指令寫入 Redis Hash，field 為 `Device`。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | MySQL `sport` | Write | 將 App 裝置版本記錄持久化至 `app_devices` 表。 |
| Redis | `AppDevices` (Hash) | Write / Read | 使用 `HSET` 更新快取，供用戶端快速查詢。快取為永久保存，直到下次更新或被手動刪除。 |
| Redis | `AppDevices` (Hash) | Read | 使用 `HGETALL` 或 `HGET` 查詢所有或特定裝置版本設定。 |

---

## 6. 重要規則

- **權限限制**: 此 API 需要管理員權限，並通過 ECFramework 驗證才可呼叫。
- **欄位限制**: 請求的 JSON 物件必須符合 `AppDevice` 結構定義，包含必填的 `Device` (如 "IOS", "AOS") 和 `Version` (如 "1.2.0")。
- **不可暴露資料**: DB 及 Redis 快取皆為內部儲存，不可對外直接暴露。用戶端只能透過專用的 GET API 查詢。
- **TTL 規則**: Redis 快取為持久性快取，無 TTL，當 DB 資料更新時需主動覆寫。
- **Transaction 規則**: DB 寫入成功後才更新 Redis 快取。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 管理員權限不足 | 返回 401 Unauthorized 或 403 Forbidden。 |
| 請求的 JSON 格式錯誤或欄位缺失 | 返回 400 Bad Request，並提示驗證失敗的欄位。 |
| 寫入 MySQL `app_devices` 失敗 | 返回 500 Internal Server Error。Redis 快取保持舊值不變。 |
| Redis `AppDevices` 更新失敗 | 需人工確認處理方式。可能返回 500 Internal Server Error，或以 DB 中的資料為準，並記錄錯誤日誌。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| AD-01 | Permission Test | 無管理員權限的請求 | 返回 403。 |
| AD-02 | API Test | 傳入正確的 `Device` 和 `Version` | 返回 200。MySQL 與 Redis 的資料皆被更新。 |
| AD-03 | API Test | 傳入已存在的 `Device` 和新的 `Version` | 返回 200。MySQL 中的舊記錄被更新，Redis 快取被覆寫。 |
| AD-04 | Flow Test | 更新後，終端用戶查詢版本 | `GET /appdevices` 的結果應立刻反映新的版本號。 |

---

## 9. 高風險區域

- **Redis 快取一致性**: 
    - **風險**: 如果 DB 寫入成功但 Redis 寫入失敗，終端 App 將無法取得最新版本設定，導致強制更新功能失效。
    - **補償**: 需人工確認是否有重試機制或補償邏輯來確保 Redis 最終一致性。

---

## 10. 常見錯誤

- ❌ **Redis 快取未更新**: 開發時只記得寫 DB，卻忘記更新 Redis `AppDevices` 快取，導致終端 App 查到的仍是舊版本。
- ❌ **權限控管設定錯誤**: 忘記為此管理端 API 加上權限驗證，導致任意請求皆可修改裝置版本設定，造成資安風險。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `POST /api/v1/appmanage/sport/appdevices` |
| DB | MySQL `sport.app_devices` |
| Redis | `AppDevices` |
| Code | `AppManagementController.SetSportAppDevice` |