# 建立體育廣告

## 1. 場景目的

後台人員建立一筆體育廣告（advertising_sport），設定廣告版位、圖片、連結、顯示日期與語言，系統自動生成 ID 並寫入 Cassandr
a 及 Redis 快取。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/sport/ads` | 建立體育廣告。需要驗證。 |

---

## 3. 流程總覽

1. 後台呼叫 POST `/api/v1/sport/ads`，帶入廣告內容（adarea、title、imgpath、mobileimgpath、startdate、
closedate、supportlangs 等）。
2. 系統驗證：
   * 請求不可包含 `id`（由系統自動生成 UUID v4）。
   * `startdate` 與 `closedate` 格式為 `yyyy-MM-dd`。
   * `startdate < closedate`。
   * `supportlangs` 每個元素皆為有效語言代碼。
   * `seq` 在相同 `adarea` 下不可重複。
3. 生成 `id`（UUID v4）。
4. 設定 `enabled` 為 1。
5. 將廣告寫入 Cassandra `ads.advertising_sport` 表。
6. 寫入 Redis 快取（SportAdCache）。（需人工確認）
7. 回傳成功。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | SportAdvertisementController.Create | 接收 POST request，呼叫 Service |
| 2 | Validator | SportAdvertisementValidator | 驗證參數（日期格式、語言代碼、seq 唯一性等） |
| 3 | Service | SportAdvertisementService.CreateAsync | 產生 `id`、設定 `enabled=1`，呼叫 Provider |
| 4 | Provider | AdvertisingSportProvider.InsertAsync | 寫入 Cassandra |
| 5 | Service | SportAdvertisementService.UpdateCache | 寫入 Redis SportAdCache（需人工確認） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `ads.advertising_sport` | Write | 持久儲存廣告資料 |
| Cache | Redis `SportAdCache`（需人工確認） | Write | 更新版位廣告快取 |
| Queue | 無 | - | - |

---

## 6. 重要規則

### 權限限制
- API 需要驗證（後台人員）。
- `id` 由系統生成，請求不可傳入。

### 欄位限制
- **adarea**：Partition Key，建立後不可更新。
- **id**：Clustering Column，系統自動生成 UUID v4。
- **startdate / closedate**：格式 `yyyy-MM-dd`，且 `startdate < closedate`。
- **supportlangs**：`list<text>`，寫入時全量覆蓋，每個元素須為有效語言代碼。
- **enabled**：建立時預設為 `1`。
- **seq**：同 `adarea` 下不可重複。
- **imgpath / mobileimgpath**：須先透過 `/api/v1/upload/imgfile` 上傳取得。

### 不可暴露資料
- 所有欄位均需公開展示，唯 `createdby` 此表無此欄位。

### TTL 規則
- 無。

### Transaction 規則
- 無跨表交易。

### Retry 規則
- 無。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求包含 `id` | 拒絕請求，提示 `id` 不可傳入 |
| `startdate` 格式錯誤 | 拒絕請求，提示日期格式須為 `yyyy-MM-dd` |
| `startdate >= closedate` | 拒絕請求，提示開始日期須早於結束日期 |
| `supportlangs` 包含無效語言代碼 | 拒絕請求，提示語言代碼無效 |
| 相同 `adarea` 下 `seq` 重複 | 拒絕請求，提示 `seq` 衝突 |
| adarea 不存在或未提供 | 拒絕請求，Missing required field |
| Redis 寫入失敗 | 記錄錯誤日誌，廣告仍建立成功，後續查詢可能讀不到快取 |
| 無效的圖片路徑 | 拒絕請求（需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC01 | 正常流程測試 | 提供完整有效參數 | 廣告建立成功，資料庫與快取皆有正確資料 |
| TC02 | 參數驗證測試 | 未提供 `adarea` | 400 Bad Request |
| TC03 | 參數驗證測試 | `seq` 重複 | 409 Conflict 或自訂錯誤訊息 |
| TC04 | 日期驗證測試 | `startdate` > `closedate` | 400 Bad Request |
| TC05 | 日期格式測試 | `startdate` = "2025/12/31" | 400 Bad Request（格式不符） |
| TC06 | 語言驗證測試 | `supportlangs = ["zz"]` | 400 Bad Request（語言代碼無效） |
| TC07 | Redis 失效測試 | Redis 服務暫停 | 廣告建立成功，前端查詢(需人工確認)應 fallback 至 DB |

---

## 9. 高風險區域

* **`seq` 唯一性衝突**：未校驗同 `adarea` 下 `seq` 是否重複，導致前台排序錯亂。
* **adarea 錯誤輸入**：後台選錯版位，建立後無法修改，只能刪除重建。
* **快取一致性**：Redis 寫入失敗可能造成短暫不一致，需明確回補機制。（需人工確認）
* **時間格式**：`startdate` 與 `closedate` 使用字串字典序比較，若格式不符可能造成誤判。
* **權限控制**：API 需嚴格限制僅後台人員可呼叫。

---

## 10. 常見錯誤

* ❌ 前端試圖傳入自訂 `id` → ✅ 系統應拒絕並自動生成 UUID。
* ❌ `supportlangs` 使用增量添加（push）進行更新 → ✅ 寫入時應傳入完整 List，全量覆蓋。
* ❌ 未先上傳圖片直接傳入自訂路徑 → ✅ 應要求先呼叫上傳 API。
* ❌ 未檢查 `seq` 唯一性 → ✅ 建立前需查詢同 `adarea` 下現有 `seq`，避免衝突。
* ❌ 誤用其他服務的時間格式（如時間戳）傳入 `startdate`/`closedate` → ✅ 必須使用 `yyyy-MM-dd` 字串。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由 | OpenAPI `POST /api/v1/sport/ads` |
| DB 操作 | `advertisingservice-detail.md` 寫入限制、讀取規則 |
| 欄位結構 | `ads.advertising_sport` Cassandra schema |
| `id` 生成規則 | `advertisingservice-detail.md`：「id 由系統自動生成（UUID v4），建立請求不可傳入」 |
| 日期限制 | `advertisingservice-detail.md`：「closedate / startdate 必須符合日期字串格式（建議 yyyy-MM-dd），不支援時間戳或時區偏移」 |
| 語言限制 | `advertisingservice-detail.md`：「supportlangs 更新時需全量覆蓋，且每個元素須為有效語言代碼」 |
| 圖片路徑 | 來源參數，README 常見場景「上傳圖片取得 URL」 |
| Redis 使用衝突 | README：「Redis SportAdCache 廣告快取」vs `advertisingservice-detail.md`：「本服務未使用 Redis」 → 需人工確認 |