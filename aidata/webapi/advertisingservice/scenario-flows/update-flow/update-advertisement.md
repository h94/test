# 更新一般廣告

## 1. 場景目的

讓後台行銷人員更新已存在的 `advertising` 表格一般廣告內容。系統必須確保更新操作符合多項業務規則：禁止修改建立者身份、禁止透過此 API 變更啟用狀態、驗證顯示時間邏輯、語言代碼有效性，以及同類型下的排序欄位唯一性。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/v1/ad` | 更新一般廣告。需驗證。 |

> **注意**：此為 OpenAPI 定義之端點。`/api/v1/sport/ads/{adArea}/{id}` 用於更新 `advertising_sport`，非本場景使用。

---

## 3. 流程總覽

1. 接收 PUT 請求，內含完整的 `Advertising` 物件。
2. 驗證 authKey，確認操作者具備後台管理權限。
3. 依請求中的 `id` 查詢 `ads.advertising` 中現有記錄。
4. 檢查記錄是否存在，不存在則拒絕請求。
5. 從請求物件中**完全移除或忽略** `createdby` 與 `enabled` 欄位，確保不被更新。
6. 執行欄位驗證：
   - `starttime` 必須小於 `closetime`。
   - `lang` 必須是系統預定義的有效語言代碼。
   - 若更新了 `seq`，需確認在相同 `type` 下沒有其他記錄使用此 `seq`。
7. 執行 `UPDATE` 語句，將驗證後的資料寫入 `ads.advertising`。
8. 回傳成功訊息 `MsgCode`。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `AdvertisingServiceController.UpdateAdvertising` | 接收請求，轉交 Service 層。 |
| 2 | Service | `AdService.UpdateAdvertising` (需人工確認實際類別與方法名) | 協調查詢、驗證與更新。 |
| 3 | Provider | `AdDataProvider.GetAdById` (需人工確認) | 根據 `id` 從 `ads.advertising` 讀取現有廣告。 |
| 4 | Validator | `AdvertisingValidator` (需人工確認) | 驗證 `starttime < closetime`、`lang` 有效性。 |
| 5 | Validator | `AdvertisingValidator` (需人工確認) | 驗證 `seq` 在相同 `type` 下的唯一性。 |
| 6 | Provider | `AdDataProvider.UpdateAd` (需人工確認) | 執行 Cassandra `UPDATE`，寫入最終資料（不含 `createdby`, `enabled`）。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `ads.advertising` | Read | 取得現有記錄以確認存在，及驗證 `seq` 唯一性。 |
| DB | `ads.advertising` | Update | 寫入更新後的廣告資料。 |

> 本場景不使用 Redis 或 Kafka。

---

## 6. 重要規則

- **權限限制**：需要後台驗證，僅管理人員可操作。
- **不可修改欄位**：
  - `createdby`：更新時必須移除請求中的此欄位，禁止覆蓋。
  - `enabled`：不允許透過一般更新 API 變更。僅能由特定的啟用/停用 API 控制。
- **欄位驗證規則**：
  - `starttime` 與 `closetime`：必須為 Unix 時間戳（秒級），且 `starttime < closetime` 必須成立。
  - `lang`：必須是系統支援的語言代碼（如 `zh`, `en`）。空字串可能表示全部語言，需根據代碼邏輯確認。
  - `seq`（若更新）：在同一 `type` 下必須唯一。更新前應查詢該 `type` 下的所有記錄，確保新的 `seq` 值不與其他記錄衝突。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 權限不足（未登入或非管理員） | 回傳 401 Unauthorized 或 403 Forbidden。 |
| 請求中的 `id` 在 `ads.advertising` 中不存在 | 回傳錯誤，指出廣告不存在。 |
| `starttime >= closetime` | 回傳驗證錯誤，拒絕更新。 |
| `lang` 不在有效代碼清單中 | 回傳驗證錯誤。 |
| 更新的 `seq` 值與同一 `type` 下其他廣告衝突 | 回傳錯誤，提示排序序號重複。 |
| 請求物件中包含了 `createdby` 或 `enabled` 欄位 | 系統應忽略這些欄位，更新成功，或回傳警告但流程不受影響。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| `SF-AD-UPD-01` | Permission Test | 一般使用者呼叫更新API | 權限不足。 |
| `SF-AD-UPD-02` | Flow Test | 成功更新一個廣告的所有允許欄位 | 更新成功。 |
| `SF-AD-UPD-03` | Flow Test | 請求中嘗試修改 `createdby` | 更新成功，但 `createdby` 保持原值。 |
| `SF-AD-UPD-04` | Flow Test | 請求中嘗試修改 `enabled` | 更新成功，但 `enabled` 保持原值。 |
| `SF-AD-UPD-05` | Flow Test | 設定 `starttime` 大於 `closetime` | 回傳驗證錯誤。 |
| `SF-AD-UPD-06` | Flow Test | 設定無效的 `lang` | 回傳驗證錯誤。 |
| `SF-AD-UPD-07` | Flow Test | 將 `seq` 改為與同 `type` 廣告相同的值 | 回傳衝突錯誤。 |
| `SF-AD-UPD-08` | API Test | 指定不存在的 `id` | 回傳‘Not Found’錯誤。 |

---

## 9. 高風險區域

- **高風險 Table**：`ads.advertising`。不正確的 `UPDATE` 可能覆蓋 `createdby` 或 `enabled`，或寫入無效的時間/語言設定，導致前台顯示異常或管理數據錯亂。
- **高風險 API**：`PUT /api/v1/ad`。必須確保在寫入資料庫前，經過程式碼強制移除或忽略特定欄位，不能僅依賴前端或文件規範。
- **Transaction**：Cassandra 的批次操作或輕量級交易（LWT）使用方式。若更新前需查詢 `seq` 唯一性然後再更新，需注意競爭條件（race condition）。需人工確認實作是否使用了 `IF NOT EXISTS` 或 `IF seq = ?` 等機制來保證原子性。
- **Cache consistency**：本場景未使用。但需注意若有其他服務快取廣告，可能會有短暫不一致。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 在前端或中介層將 `createdby` 與 `enabled` 傳入後端，而後端未做防禦性移除，直接覆蓋資料庫。
  - 誤解時間戳單位（毫秒 vs. 秒），導致時間驗證失效。
- **AI 容易誤解**：
  - 可能會誤以為更新 `advertising` 需要同時處理 `seq` 的唯一性驗證，但若請求中未包含 `seq` 欄位，則不應觸發此驗證。
  - 可能會將更新 `advertising` 的邏輯套用到 `advertising_sport` 上，混淆 `starttime`（Unix 時間戳）與 `startdate`（日期字串）的驗證規則。
- **常見漏檢查項目**：
  - 忘記在更新時從請求物件中剝離 `createdby` 和 `enabled`。
  - 沒有對 `lang` 進行預定義清單的比對。
  - 更新 `seq` 時沒有先鎖定或查詢同類型下的最大值，僅做簡單的 `!=` 比對，無法處理多筆更新的競爭。
  - 未檢查目標廣告是否存在就直接執行更新，導致操作影響行數為 0 卻回傳成功。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI: `PUT /api/v1/ad` |
| DB | Cassandra schema: `ads.advertising` |
| 寫入限制 | `db/ads-detail.md` (ads.advertising 段落) |
| 語意 | Phase0/1 程式碼分析: `createdby` 為『建立者標識』, `enabled` 參照 `AppDefine.AdEnabled` |
| 規則 | `webapi/advertisingservice/advertisingservice-detail.md` - 寫入限制與常見錯誤 |