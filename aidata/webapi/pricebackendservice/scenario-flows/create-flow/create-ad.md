# 新增廣告

## 1. 場景目的

後台管理員通過後台管理頁面上傳圖片（支援桌面版與手機版），並建立一筆體育廣告記錄，該廣告可指定所屬區域（adarea）、支援的語言、開始與結束日期、排序序號等屬性，最終由下游 `advertisingservice` 儲存。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/advertising/ads` | 新增廣告（含圖片上傳） |

---

## 3. 流程總覽

1. 管理後台前端以 `multipart/form-data` 提交廣告表單，包含圖片檔案 `file`（桌面版）、`file2`（行動版）及廣告中繼資料。  
2. `AdvertisingController.CreateAds` 接收 Request，透過 Model Binding 將表單欄位映射至 `CreateAdsRequest` DTO。  
3. 調用 `AdvertisingService.CreateAds`，傳入 DTO 與圖片檔案串流。  
4. `AdvertisingService` 執行圖片上傳：  
   - 若 `file` 不為空，呼叫 `SystemProvider.UploadImg`，將圖片上傳至檔案儲存服務並取得回傳的圖片路徑。  
   - 若 `file2` 不為空，同樣透過 `SystemProvider.UploadImg` 上傳行動版圖片。  
   - 上傳成功後將回傳路徑分別寫入 `request.ImgPath` 與 `request.MobileImgPath`。  
5. `AdvertisingService` 產生廣告 ID (`UUID v4`)，並透過 `IMicroServiceProvider` 呼叫下游 `advertisingservice` 的 `POST /api/v1/advertising/ads`。  
6. 若 `advertisingservice` 回傳成功（HTTP 200），`AdvertisingService` 回傳成功結果給 Controller；否則拋出例外。  
7. Controller 回傳 HTTP 200 給前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `AdvertisingController.CreateAds` | 接收 multipart/form-data，驗證 ModelState，調用 Service |
| 2 | Service | `AdvertisingService.CreateAds` | 調用 `SystemProvider.UploadImg` 上傳圖片，填充 `ImgPath` / `MobileImgPath` |
| 3 | Provider | `SystemProvider.UploadImg` | 呼叫檔案儲存服務（`/api/v1/system/upload/img`），回傳圖片路徑 |
| 4 | Service | `AdvertisingService.CreateAds` | 產生廣告 ID（`Guid.NewGuid`），組裝 DTO，呼叫 `IMicroServiceProvider` |
| 5 | Provider | `IMicroServiceProvider`（實作細節需人工確認） | 發送 POST 請求至 `advertisingservice` 的 `/api/v1/advertising/ads` |
| 6 | 下游 | `advertisingservice` | 將廣告資料寫入 `ads.advertising_sport` 表，回傳成功 |
| 7 | Service | `AdvertisingService.CreateAds` | 判斷回應，若失敗則記錄日誌並拋出例外 |
| 8 | Controller | `AdvertisingController.CreateAds` | 回傳 `Ok()` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `ads.advertising_sport` (Cassandra) | Write (INSERT) | 由 `advertisingservice` 負責寫入，儲存廣告中繼資料與圖片路徑 |
| Kafka | `applogs`（預設日誌 Topic）| Publish | `AdvertisingService` 記錄上傳與建立成敗日誌 |

> ⚠️ **需人工確認**：`SystemProvider.UploadImg` 是否涉及額外的 DB / Redis / Queue 操作，原始碼未覆蓋。  
> ⚠️ **需人工確認**：`advertisingservice` 內部是否使用 Redis 快取廣告資料，此處僅描述 API 層面。

---

## 6. 重要規則

- **權限限制**：此 API 需要後台管理員權限（經由 `ECFramework.ECService` 統一驗證），未登入或權限不足者應被拒絕。  
- **欄位限制** (`ads.advertising_sport`)：  
  - `adarea`：分區鍵，建立後不可修改。  
  - `id`：由 `AdvertisingService` 以 UUID v4 自動生成，請求端不可傳入。  
  - `enabled`：預設由 `advertisingservice` 設為 `1`（啟用）。  
  - `startdate` / `closedate`：格式須為 `yyyy-MM-dd`，且 `startdate < closedate`。  
  - `supportlangs`：為 `list<text>`，更新時須全量覆蓋，每個元素須為有效語言代碼。  
  - `imgpath` / `mobileimgpath`：僅能透過圖片上傳流程（`SystemProvider.UploadImg`）寫入，不可由前端直接指定完整路徑。  
- **不可暴露資料**：  
  - `advertising_sport.adclass` 僅供後台統計使用，不應回傳給一般前端。  
- **TTL 規則**：無（`ads.advertising_sport` 無預設 TTL）。  
- **Transaction 規則**：此服務不直接操作 DB，無跨表 Transaction；但圖片上傳與廣告建立為兩步操作，若圖片上傳成功但下游廣告建立失敗，圖片將成為孤立檔案。  
- **Retry 規則**：目前 `AdvertisingService` 未實作自動 Retry，失敗即拋出例外。  
- **狀態值限制**：無（`enabled` 僅由後台後續 API 控制，此場景僅建立）。  
- **不可修改欄位**：`adarea`、`id` 建立後不可修改。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未登入或權限不足 | 回傳 401（Unauthorized）或 403（Forbidden） |
| 未上傳圖片 (`file` 為空) | 圖片路徑留空，廣告仍可建立（圖片為選填） |
| 圖片上傳失敗 (`SystemProvider.UploadImg` 拋出例外) | `AdvertisingService` 捕捉並記錄錯誤日誌，回傳 500（Internal Server Error）給前端 |
| `advertisingservice` 回傳非 200 | `AdvertisingService` 記錄日誌，回傳 502（Bad Gateway）或 500 |
| `startdate` 或 `closedate` 格式錯誤 | `advertisingservice` 可能會拒絕並回傳錯誤（需人工確認下游服務驗證邏輯） |
| `supportlangs` 包含無效語言代碼 | 同上，下游服務應驗證並拒絕 |
| 呼叫 `advertisingservice` 逾時 | 拋出 `HttpRequestException`，回傳 504（Gateway Timeout） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|--------|------|------|----------|
| ADS-001 | Integration Test | 正常上傳圖片（`file`）與中繼資料 | `advertisingservice` 收到正確的廣告物件，回傳 200，`advertising_sport` 寫入一筆新記錄 |
| ADS-002 | API Test | 只上傳桌面版圖片，不上傳行動版圖片 | 廣告建立成功，`MobileImgPath` 為空 |
| ADS-003 | Flow Test | 同時上傳桌面版與行動版圖片 | 兩張圖片皆上傳成功，路徑正確寫入 |
| ADS-004 | API Test | 未上傳任何圖片 | 廣告建立成功，`ImgPath` 與 `MobileImgPath` 皆為空 |
| ADS-005 | Error Test | 圖片上傳失敗（模擬 `SystemProvider` 拋出例外） | 回傳 500，廣告未被建立 |
| ADS-006 | Error Test | 下游 `advertisingservice` 無回應 | 回傳 504 或 502 |
| ADS-007 | Permission Test | 無效的認證 Token | 回傳 401 |
| ADS-008 | Validation Test | `startdate` 晚於 `closedate` | 下游應回傳錯誤，前端顯示對應訊息 |
| ADS-009 | Data Test | `supportlangs` 包含 `["zh-TW", "en-US"]` | 寫入正確，下游廣告查詢可依語言過濾 |

---

## 9. 高風險區域

- **圖片上傳與廣告建立的非原子性**：  
  目前為兩步驟操作，若第二步失敗，已上傳的圖片會成為孤立檔案，需考慮後續清理機制或改為先建立廣告再上傳（但路徑需回寫）。  
- **高風險 API**：`/api/v1/advertising/ads` 若被惡意調用，可能上傳大量無效圖片，需搭配 Rate Limiting 與檔案大小限制。  
- **跨服務資料同步**：`pricebackendservice` 本身不持有廣告狀態，所有狀態依賴下游 `advertisingservice`；若下游 Schema 異動，需同步更新 `AdvertisingModels` 套件版本。  
- **Cache consistency**：若 `advertisingservice` 使用 Redis 快取廣告清單，廣告新增後可能需要主動失效相關快取鍵，但目前 `pricebackendservice` 不負責此操作。  
- **Queue retry**：目前無非同步佇列機制，失敗即拋出例外，無自動重試。  
- **Idempotency**：前端重複提交相同 payload 會建立多筆廣告（ID 不同），需由前端防止重複送出。

---

## 10. 常見錯誤

- ❌ 新人直接在 `AdvertisingService` 中使用原始表單路徑當作 `ImgPath` → 應透過 `SystemProvider.UploadImg` 上傳後取得路徑。  
- ❌ 忘記產生 `id`，或讓前端傳入 `id` → 應由後端 `AdvertisingService` 以 `Guid.NewGuid().ToString()` 自動產生。  
- ❌ `supportlangs` 誤以 JSON 字串傳送而非陣列 → 應使用正確的 multipart/form-data 格式傳遞陣列。  
- ❌ `startdate` / `closedate` 使用錯誤的時間格式（如時間戳）→ 應使用 `yyyy-MM-dd` 字串。  
- ❌ AI 誤將此廣告寫入 `ads.advertising`（一般廣告表）而非 `ads.advertising_sport` → 體育廣告場景固定使用 `advertising_sport`。  
- ❌ 忽略 `file` 為選填，強制要求上傳圖片 → 可能導致無圖廣告無法建立。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `AdvertisingController.CreateAds` |
| Service | `AdvertisingService.CreateAds` |
| Provider | `SystemProvider.UploadImg` |
| DB Table | `ads.advertising_sport` |
| DTO | `CreateAdsRequest` |
| 下游 API | `advertisingservice POST /api/v1/advertising/ads` |