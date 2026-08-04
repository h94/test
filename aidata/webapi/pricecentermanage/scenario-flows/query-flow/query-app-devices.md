# 查詢所有裝置版本

## 1. 場景目的

查詢目前所有運動站台 App 裝置的最低版本設定，供管理後台監控或 App 端啟動時判斷是否需要強制更新。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/appmanage/sport/appdevices` | 查詢所有裝置版本清單 |

---

## 3. 流程總覽

1. 接收 GET 請求
2. 透過 ECFramework.ECService 驗證請求者身份與權限
3. 嘗試讀取 Redis 快取 `AppDevices`（Hash 結構）
4. 若快取命中 → 直接回傳
5. 若快取未命中 → 查詢 MySQL `sport.app_devices` 表
6. 將查詢結果寫入 Redis `AppDevices` 快取
7. 回傳裝置版本清單

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware | ECFramework Auth | 檢查 token，注入身份資訊 |
| 2 | Controller | AppManageController.GetAllDevices | 接收 query，呼叫 Service |
| 3 | Service | IAppDeviceService.GetAll | 處理業務邏輯，呼叫 Provider |
| 4 | Provider | AppDeviceCacheProvider.GetAllDevices | 先查 Redis `AppDevices` |
| 5 | Provider | AppDeviceRepository.GetAll （若 cache miss） | 查詢 MySQL `app_devices` |
| 6 | Provider | AppDeviceCacheProvider.SetAllDevices | 寫入 Redis 快取 |
| 7 | Controller | Return Ok(result) | 序列化並回傳 JSON |

> **需人工確認**：確切的 Controller / Service / Provider 名稱；Redis 讀寫方法名稱。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | MySQL `sport.app_devices` | Read | 查詢所有裝置版本設定 |
| Redis | SportAccountCache / `AppDevices` | Read / Write | 快取裝置版本清單，避免頻繁查 DB |
| Queue | 無 | – | 本場景未使用 |

---

## 6. 重要規則

- **權限限制**：需通過 ECFramework 驗證，確認為後台管理員身份。
- **不可暴露資料**：回應中不應包含任何敏感內部欄位（如 DB 自動生成 ID 等）。
- **TTL 規則**：Redis `AppDevices` 為永久保存，僅在 DB 更新時手動 `DEL` 以維護一致性。
- **快取一致性**：當 `POST /api/v1/appmanage/sport/appdevices` 寫入後，必須同步刪除 Redis 快取（由寫入端處理）。
- **欄位限制**：回應格式參考 `AppDevice` schema（含 `device` 類型、最低版本號等；**需人工確認**完整 schema）。
- **不可修改欄位**：本 API 為唯讀，不對任何 DB 欄位進行異動。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未帶驗證 token | 401 Unauthorized |
| token 過期或無效 | 401 Unauthorized |
| 權限不足（非管理員） | 403 Forbidden |
| Redis 快取讀取失敗（miss 正常 fallback） | 不影響回傳，改走 DB 查詢 |
| DB timeout 或連線失敗 | 500 Internal Server Error |
| `app_devices` 表為空 | 回傳空陣列 `[]` |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| AD-GET-01 | API Test | 正常查詢（已有資料） | 200 + 裝置版本陣列 |
| AD-GET-02 | API Test | 無任何裝置設定 | 200 + 空陣列 |
| AD-GET-03 | Permission Test | 未登入呼叫 | 401 |
| AD-GET-04 | Permission Test | 一般會員呼叫 | 403 |
| AD-GET-05 | Cache Test | 連續呼叫兩次，第二次命中快取 | 第二次不回查 DB |
| AD-GET-06 | Cache Test | 快取失效，強制 miss（模擬 Redis 異常） | 仍可正常回傳（fallback DB） |
| AD-GET-07 | DB Fail Test | MySQL 無法使用 | 500（需確認有無合適錯誤訊息） |

---

## 9. 高風險區域

- **快取一致性**：更新裝置版本後若未清除 Redis 快取，App 端將拿到過期版本設定，可能導致更新判斷錯誤。
- **權限誤配**：若驗證設定錯誤，可能允許未授權使用者看到敏感版本資訊，雖非高度敏感，但仍屬內部配置。
- **DB 空資料**：若表結構或種子資料錯誤，可能導致回傳格式與前端預期不符。

---

## 10. 常見錯誤

- ❌ 新人實作時直接查 DB 而略過 Redis 快取，導致後台查詢壓力。
- ❌ AI 產生程式碼時忘記加上授權標籤 `[Authorize]` 或等價驗證。
- ❌ 回應模型包含不必要的 DB 欄位（如內部 ID）。
- ❌ 誤將快取 `Key` 設為有 TTL 的短期快取，但實際應為永久並由寫入端主動刪除（依 db-usage 規範）。
- ❌ 在多服務環境下忘記共用 Redis Key 規範 `AppDevices`，自己定義不同前綴導致快取穿透。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI: `GET /api/v1/appmanage/sport/appdevices` |
| DB | MySQL `sport.app_devices` (README.md) |
| Redis | `AppDevices` hash (pricecentermanage-detail.md) |
| Auth | README.md: 需要驗證 ✅ |
| 寫入端快取清除 | pricecentermanage-detail.md: 「DB 更新時主動 DEL」 |
| 服務角色 | pricecentermanage 為 writer/reader (db/sport-detail.md) |