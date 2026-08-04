# 查詢廣告

## 1. 場景目的

後台管理員依據指定的廣告區域 (`adArea`) 查詢該區域內所有體育廣告的明細列表，以便進行廣告內容的審核、編輯或狀態管理。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/advertising/ads/{adArea}` | 依廣告區域查詢廣告列表 |

---

## 3. 流程總覽

1. 接收後台管理員的 HTTP GET 請求，路徑中包含 `adArea` 參數。
2. 系統驗證請求是否包含有效的管理員身份驗證憑證。
3. `pricebackendservice` (BFF層) 將請求轉發至下游 `advertisingservice`。
4. `advertisingservice` 根據 `adArea` 查詢 `ads.advertising_sport` 資料表。
5. 查詢結果依 `seq` (排序序號) 升冪排列。
6. `advertisingservice` 將廣告列表回傳給 `pricebackendservice`。
7. `pricebackendservice` 將結果返回給後台前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `AdvertisingController.GetAdsByArea` | 接收 `adArea` 參數，調用 Service 層。 |
| 2 | Service | `AdvertisingService.GetAdsByArea` | 將 `adArea` 傳遞給 Provider，呼叫下游服務。 |
| 3 | Provider | `AdvertisingProvider.GetAdsByArea` | 發送 GET 請求至 `advertisingservice` 的對應端點。 |
| 4 | (下游) | `advertisingservice` | 查詢 `ads.advertising_sport` 並返回結果。 |

- **需人工確認**：確切的 Controller, Service, Provider 名稱與方法簽名，需根據 `pricebackendservice` 原始碼的最終實作確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `ads.advertising_sport` | `SELECT` | 根據 `adarea` (Partition Key) 查詢該區域所有廣告的詳細資訊。 |

---

## 6. 重要規則

- **權限限制**：此 API 需要後台管理員的有效驗證 (Evidence: README.md 中標示為 ✅ 需要驗證)。
- **欄位限制**：
  - 查詢時，`adarea` 為 `advertising_sport` 表格的分區鍵 (Partition Key)，**必須**提供，以避免全表掃描 (Evidence: `ads-detail.md`)。
  - `enabled` 欄位決定廣告是否啟用。雖然此為管理後台查詢，但根據業務規則，後台查詢**應顯示所有狀態**的廣告，而非只顯示已啟用的廣告 (Evidence: `ads-detail.md`)。
  - 廣告排序應依 `seq` 欄位升冪排列 (Evidence: `ads-detail.md`)。
- **不可暴露資料**：
  - `imgpath` 和 `mobileimgpath`：可能為內部儲存路徑，對外 API 應回傳**完整可存取的 URL** (Evidence: `pricebackendservice-detail.md` 的 `ads` 章節)。
  - `tageturl`：若未經安全過濾，可能被用於釣魚攻擊，建議在回傳前或前端顯示時進行驗證 (Evidence: `pricebackendservice-detail.md` 的 `ads` 章節)。
  - `adclass` 欄位僅供後台統計使用，不應暴露給一般查詢，但此場景為後台查詢，**可以回傳** (Evidence: `ads-detail.md`)。
- **狀態值限制**：無。此場景為查詢，無狀態變更。
- **Transaction 規則**：無。此場景僅為單一讀取操作。
- **Retry 規則**：若下游 `advertisingservice` 呼叫失敗，BFF 層應實作重試機制或返回明確的錯誤訊息。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 管理員身份驗證失敗或 Token 過期 | 返回 HTTP 401 Unauthorized。 |
| 請求路徑中未提供 `{adArea}` 或為空 | 返回 HTTP 400 Bad Request。 |
| 下游 `advertisingservice` 無回應或逾時 | 返回 HTTP 502 Bad Gateway 或 504 Gateway Timeout。 |
| 資料庫中不存在對應的 `adArea` | 返回 HTTP 200 OK，Body 為一個空陣列 `[]`。 |
| 查詢時發生非預期的資料庫錯誤 | 返回 HTTP 500 Internal Server Error。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| `GET_ADS_BY_AREA_01` | API Test | 提供一個有效的 `adArea`。 | 返回 200 OK，且 Body 中包含該區域的所有廣告列表，按 `seq` 排序。 |
| `GET_ADS_BY_AREA_02` | Permission Test | 使用無效的 API 金鑰或過期的 Token。 | 返回 401 Unauthorized。 |
| `GET_ADS_BY_AREA_03` | Flow Test | 提供一個不存在的 `adArea`。 | 返回 200 OK，但 Body 為空陣列 `[]`。 |
| `GET_ADS_BY_AREA_04` | Data Integrity | 檢查回傳的 `imgpath`。 | 回傳的應為完整的圖片 URL，而非相對路徑。 |

---

## 9. 高風險區域

- **下游服務相依性**：`pricebackendservice` 完全依賴 `advertisingservice`，若下游服務不可用，此功能將直接中斷。
- **圖片路徑洩漏**：`pricebackendservice` 作為 BFF，必須確保在組裝資料時，將內部的圖片路徑轉換為外部可存取的完整 URL，否則前端將無法顯示圖片。
- **分區鍵查詢**：對 `advertising_sport` 的任何查詢都必須帶有 `adarea`，否則將導致 Cassandra 全表掃描，嚴重影響效能。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 誤解 `/api/v1/advertising/ads/{adArea}` 為查詢所有廣告，忽略了 `adArea` 是必填的分區鍵。
  - 在 BFF 層對返回結果進行了不必要的過濾，例如僅回傳 `enabled=1` 的廣告，導致後台無法看到已停用的廣告。
- **AI 容易誤解**：
  - 可能混淆 `advertising` 和 `advertising_sport` 兩張表，前者為普通廣告，後者為體育廣告。此場景應是查詢 `advertising_sport`。
  - 可能將 `adArea` 視為選填的過濾條件，而非必填的資料庫分區鍵。
- **常見漏檢查項目**：
  - 回傳的 `tageturl` 是否經過安全校驗。
  - 圖片路徑是否為完整的 URL。
  - 對下游服務呼叫失敗的錯誤處理是否完善。
- **常見錯誤流程**：
  - BFF 層直接將下游服務的內部錯誤訊息 (Stack Trace) 回傳給前端，造成資訊洩漏。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `README.md` 中的 `GET /api/v1/advertising/ads/{adArea}` 定義。 |
| API Auth | `README.md` 中該路由標示為需要驗證 ✅。 |
| DB Table | `ads.advertising_sport`，其 Partition Key 為 `adarea`。 |
| DB Rule | `ads-detail.md` 中關於 `adarea`, `enabled`, `seq` 的查詢規則。 |
| DB Rule | `pricebackendservice-detail.md` 中關於 `imgpath`, `mobileimgpath`, `tageturl` 的注意事項。 |
| Code | Controller/Service/Provider 層級方法為推測，**需人工確認**。 |
| Service Dep | `README.md` 中 `pricebackendservice` 相依於 `advertisingservice`。 |