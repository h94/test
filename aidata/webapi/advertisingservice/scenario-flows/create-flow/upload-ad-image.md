# 上傳廣告圖片

## 1. 場景目的

後台人員於建立廣告前，先透過此流程上傳廣告圖片至指定站點（`site`），取得圖片的伺服器路徑（URL）。圖片實際儲存由外部 StorageService 或 CDN 處理，本服務不處理圖片壓縮或搬移，僅取得並回傳圖片路徑，供後續建立廣告時使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/system/upload/imgfile/{site}` | 上傳廣告圖片至指定 `site` 站點，回傳圖片 URL |
| POST | `/api/v1/upload/imgfile` | OpenAPI 定義之路由，功能相同，需人工確認實際使用版本 |

---

## 3. 流程總覽

1. 後台人員選擇要上傳的廣告圖片，指定目標 `{site}`（如 `sport`）。
2. 呼叫 `POST /api/v1/system/upload/imgfile/{site}`，以 `multipart/form-data` 形式傳送圖片檔案。
3. 系統驗證請求是否通過 ECFramework 驗證。
4. Controller 接收 `site` 參數與 `file` 檔案。
5. Service 層將 `site` 與檔案傳遞給負責圖片處理的 Provider 或直接呼叫外部儲存服務。
6. 外部 StorageService / CDN 儲存檔案後，回傳圖片的伺服器路徑（URL）。
7. 系統將取得的圖片 URL 回傳給前端。
8. 前端取得 URL 後，可在後續建立廣告的 API 請求中使用此路徑。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SystemController.UploadImgFile`（推測） | 接收 `site` 路徑參數與 `file` 檔案，呼叫 Service |
| 2 | Service | `SystemService` 或 `UploadService`（推測） | 處理圖片上傳邏輯，決定儲存目標 |
| 3 | Provider | 可能為 `ECService` 或內部 WebClient | 呼叫外部 StorageService 或 CDN，傳送檔案 |
| 4 | Provider | StorageService / CDN | 實際儲存圖片，回傳圖片的伺服器 URL |
| 5 | Controller | `SystemController` | 將 URL 封裝為 `MsgCode` 回傳 |

> **需人工確認**：實際的 Controller、Service、Provider 名稱與呼叫關係，因缺少直接程式碼證據，以上為基於 README 與 OpenAPI 的推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | 無 | 無 | 圖片上傳流程不涉及 Cassandra 寫入 |
| Redis | 無 | 無 | 不使用 Redis |
| Kafka | 無 | 無 | 不使用 Kafka 或 Queue |

---

## 6. 重要規則

- **權限限制**：必須通過 ECFramework 驗證（後台人員身份）。未驗證的請求應被拒絕。
- **欄位限制**：
  - `site` 必須為有效的站點代碼（如 `sport`），需人工確認是否有預定義清單。
  - `file` 必須為有效的圖片格式（如 `.jpg`, `.png`），且需限制檔案大小，防止惡意檔案上傳。
- **不可暴露資料**：回傳的圖片 URL 應為公開可存取的路徑，不應暴露服務內部路徑或憑證。
- **服務職責邊界**：本服務僅負責接收檔案並轉送至外部儲存服務，不負責實際的圖片壓縮、格式轉換或永久儲存。
- **TTL 規則**：無。
- **Transaction 規則**：無。
- **Retry 規則**：若外部 StorageService 上傳失敗，本服務應回傳對應的錯誤代碼，不應自動重試以免產生孤立檔案。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未通過驗證（無效或過期 token） | 回傳 401 Unauthorized |
| 上傳檔案超出大小限制 | 回傳 400 Bad Request，訊息提示檔案過大 |
| 上傳檔案格式不支援 | 回傳 400 Bad Request，訊息提示格式不符 |
| `{site}` 參數為空或不合法 | 回傳 400 Bad Request |
| 外部 StorageService 連線失敗或 timeout | 回傳 500 Internal Server Error |
| 外部 StorageService 回傳錯誤 | 回傳 502 Bad Gateway 或對應的錯誤訊息 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-UPL-01 | API Test | 上傳有效圖片檔案至合法 `site` | 回傳 200，包含圖片 URL |
| UT-UPL-02 | Permission Test | 未攜帶驗證 token 上傳 | 回傳 401 Unauthorized |
| UT-UPL-03 | API Test | 上傳檔案大小超過限制 | 回傳 400，包含明確錯誤訊息 |
| UT-UPL-04 | API Test | 上傳非圖片格式檔案 | 回傳 400，包含格式不符訊息 |
| UT-UPL-05 | API Test | 請求中缺少 `file` 欄位 | 回傳 400 Bad Request |
| UT-UPL-06 | Flow Test | 模擬 StorageService 回應失敗 | 回傳 502 或 500，日誌需記錄錯誤 |

---

## 9. 高風險區域

- **高風險 API**：`POST /api/v1/system/upload/imgfile/{site}`，因涉及檔案上傳，需注意安全性：
  - 必須驗證檔案類型，防止上傳可執行檔或惡意腳本。
  - 必須限制檔案大小，避免儲存空間耗盡。
  - 需記錄上傳者與時間，以利後續稽核（若未實作，建議新增）。
- **外部服務相依**：依賴外部 StorageService/CDN，若該服務不穩定，將直接影響本功能。

---

## 10. 常見錯誤

- ❌ 上傳圖片後，嘗試直接將檔名或暫存路徑寫入廣告 Table，但未先取得儲存服務的正式 URL。
  → ✅ 必須以 StorageService 或 CDN 回傳的完整 URL 為準，不可使用本機暫存檔路徑。
- ❌ 開發者誤以為 `advertising.path` 或 `advertising_sport.imgpath` 的寫入發生在此 API 中。
  → ✅ 本 API 僅負責檔案上傳與取得 URL，寫入 DB 發生在建立廣告的流程中。
- ❌ 忽略對 `site` 參數的驗證，接受任意字串。
  → ✅ 應驗證 `site` 是否為系統支援的站點代碼，避免傳送至錯誤的儲存目錄。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由與需求 | README.md「系統工具」表格：`POST /api/v1/system/upload/imgfile/{site}` |
| API 契約 | OpenAPI `/api/v1/upload/imgfile`（路徑差異需人工確認） |
| 服務職責邊界 | `advertisingservice-detail.md`「本服務不負責」章節：圖片上傳由 StorageService/CDN 處理 |
| DB 未使用 | `advertisingservice-detail.md`「Redis」章節：本服務未使用 Redis。所有資料存取均為 Cassandra，但圖片上傳流程不涉及 |
| 驗證需求 | README.md API 表格：需要驗證 ✅ |
| `path` / `imgpath` 語意 | Source Code Semantics Phase0：`path` 為廣告圖片的連結網址（上傳後的伺服器路徑），`imgpath` 為上傳生成 |
| 程式流程（推測） | 基於 Controller → Service → Provider 的標準分層架構，實際類別名稱需人工確認 |