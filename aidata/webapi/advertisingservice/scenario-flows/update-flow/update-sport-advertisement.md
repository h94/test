# 更新體育廣告

## 1. 場景目的

後台人員更新已有的體育廣告（`advertising_sport`），修改廣告展示期間、支援語言、圖片、連結、排序等欄位。`adarea` 和 `id` 為不可變更欄位，需確保更新後的廣告符合所有業務規則。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/v1/sport/ads/{adArea}/{id}` | 根據 adArea 與 id 更新廣告 |

來源：README.md、OpenAPI。

---

## 3. 流程總覽

1. 接收 PUT 請求，包含 `adArea` 與 `id` 路徑參數及 JSON body（SportAdvertisement schema）。
2. 驗證使用者權限（ECFramework 驗證）。
3. 從 Cassandra `ads.advertising_sport` 讀取現有記錄（以 `adArea`, `id` 查詢）。若記錄不存在，回傳錯誤。
4. 比對路徑參數 `adArea` / `id` 與 body 中的 `adArea` / `id`（若 body 提供），必須一致，否則拒絕請求。
5. 驗證 body 中各欄位：
   - `startdate`, `closedate` 必須為 `yyyy-MM-dd` 格式，且 `startdate < closedate`（建議解析為日期物件比較，避免字串順序誤判）。
   - `supportlangs` 為 List，每個元素須為有效語言代碼，更新時全量覆蓋，不保留舊值。
   - `seq` 在同一 `adarea` 下不得重複（需先查詢同區域其他記錄的 seq）。
   - `enabled` 僅能由特定啟用／停用 API 變更，此更新 API 不應修改 `enabled`（若 body 包含，應忽略或回報錯誤，依實際實作而定）。
6. 更新 Cassandra `advertising_sport` 記錄，全量寫入所有欄位（包括未變動的欄位，以確保資料完整性與 `supportlangs` 全量覆蓋）。
7. 更新成功後，應清除對應 `adArea` 的 Redis 快取（SportAdCache），使前台查詢能反映最新廣告。  
   *⚠️ 需人工確認：Redis 快取失效的實作方式及是否真的使用 Redis（文件存在矛盾）。*
8. 回傳 200 OK。

---

## 4. 程式流程

（基於服務結構推測，無直接程式碼證據，部分需人工確認）

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SportAdvertisementController` | 接收請求，驗證授權，調用 Service |
| 2 | Service | `SportAdvertisementService.Update` | 業務驗證：檢查欄位規則、seq 唯一性 |
| 3 | Repository | `SportAdvertisementRepository.GetByAdAreaAndId` | 從 Cassandra `ads.advertising_sport` 讀取現有記錄 |
| 4 | Service | `SportAdvertisementService.Update` | 確定最終資料（合併不可變動欄位），執行寫入 |
| 5 | Repository | `SportAdvertisementRepository.Update` | 寫入 Cassandra，全量覆蓋整行資料 |
| 6 | CacheService | `RedisHelper.InvalidateSportAdCache` | 清除對應 `adArea` 的快取（**需人工確認**） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `ads.advertising_sport` | Read | 查詢現有廣告以便更新 |
| DB | Cassandra `ads.advertising_sport` | Write (全量覆蓋) | 更新廣告記錄 |
| Cache | Redis SportAdCache | Delete / Invalidate | 使該 adArea 快取失效，確保前台顯示最新廣告（**需人工確認是否存在**） |
| Queue | 無 | - | - |

---

## 6. 重要規則

- **權限限制**：需通過 ECFramework 驗證，僅後台管理人員可操作。
- **不可修改欄位**：`adarea` 與 `id`（Partition Key 與 Clustering Column）。若請求 body 包含這兩個欄位，其值必須與路徑參數完全相同，否則拒絕請求。
- **enabled 欄位保護**：此端點不應修改 `enabled`，該欄位僅能透過專用啟用／停用 API 變更。若 body 中傳入，需確認服務端是忽略還是回報錯誤。
- **日期驗證**：`startdate < closedate`（建議使用日期物件比較，而非字串字典序），格式必須為 `yyyy-MM-dd`。
- **seq 唯一性**：同一 `adarea` 下，`seq` 不得與其他記錄重複（排除自身）。
- **supportlangs 全量覆蓋**：更新時必須傳入完整的支援語言清單，不進行增量合併。每個元素須為有效語言代碼（如 `zh-TW`、`en`）。
- **寫入方式**：Cassandra 更新即整行覆蓋，不支援部分欄位更新，需確保所有必要欄位均提供或沿用原值。
- **快取一致性**：更新後必須失效相關快取，否則前台查詢會持續返回舊資料。*注意：文件矛盾，advertisingservice-detail.md 說本服務未使用 Redis，README.md 則提到 Redis SportAdCache，需釐清後調整規則。*

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| adArea 或 id 對應記錄不存在 | 404 Not Found（需人工確認實際錯誤碼） |
| body 中的 adArea 或 id 與路徑不符 | 400 Bad Request，提示不允許修改分割鍵或ID |
| startdate >= closedate | 400 Bad Request，提示日期區間無效 |
| 日期格式非 yyyy-MM-dd | 400 Bad Request，提示格式錯誤 |
| supportlangs 包含無效語言代碼 | 400 Bad Request |
| seq 與其他廣告重複（同一 adarea） | 409 Conflict 或 400 Bad Request，提示 seq 不唯一 |
| 嘗試修改 enabled 欄位 | 403 Forbidden 或 400 Bad Request（依實作） |
| Cassandra 寫入失敗（如超時） | 500 Internal Server Error |
| Redis 快取清除失敗 | 可能仍回傳 200，但後台應記錄錯誤；前台需等快取自然過期（**需人工確認處理策略**） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-1 | API Test | 成功更新所有可變更欄位，seq 未衝突，supportlangs 合法 | 200 OK，Cassandra 記錄正確，快取失效 |
| UT-2 | Validation | startdate >= closedate | 400 Bad Request |
| UT-3 | Validation | supportlangs 包含非法語系 | 400 Bad Request |
| UT-4 | Validation | 請求 body 中 adArea 與路徑不同 | 400 Bad Request |
| UT-5 | Validation | 請求 body 中 id 與路徑不同 | 400 Bad Request |
| UT-6 | Business Rule | 嘗試修改 enabled | 應忽略或回報錯誤（根據實作決定） |
| UT-7 | Business Rule | 同一 adarea 下 seq 重複 | 409 Conflict（或 400） |
| UT-8 | Cache | 更新後立即用 GET `/api/v1/sport/ads/{adArea}` 查詢 | 返回更新後的廣告（若快取已失效） |
| UT-9 | Flow | 更新不存在的 adArea+id | 404 Not Found |

---

## 9. 高風險區域

- **高風險 table**：`ads.advertising_sport`，更新時若漏掉欄位可能導致資料遺失，尤其 `supportlangs`。
- **高風險 API**：`PUT /api/v1/sport/ads/{adArea}/{id}`，可影響前台廣告展示，應嚴格控制權限與輸入驗證。
- **Seq 衝突出現**：若未正確檢查唯一性，可能導致前台廣告排序錯亂。
- **Cache consistency**：更新後若未清除快取，前台將持續顯示舊廣告，影響時效。若 Redis 根本不使用則無此問題，但需釐清。
- **enabled 誤改**：若未過濾 enabled 欄位，可能因前台操作而錯誤停用廣告。
- **日期比較漏洞**：若僅用字串比較，跨年度時可能得到錯誤結果（例如 "2025-12-31" < "2025-01-01" 為 false），必須解析為日期物件比較。
- **並行更新衝突**：Cassandra 最後寫入者贏，無鎖定機制，若多人同時更新同一廣告可能造成 seq 意外重複或資料覆蓋，需考慮 business rules（如先到先贏或版本號檢查，目前無相關機制）。

---

## 10. 常見錯誤

- 更新 `supportlangs` 時使用了增量添加（例如從前端取得現有 list 後再 push 新語言），正確做法是請求 body 中必須包含最終完整清單。
- 忘記清除 Redis 快取，導致管理後台修改後前台未生效。
- 未檢查 `seq` 唯一性，造成同一區域內重複排序值，導致廣告排序不可預期。
- 請求 body 中無意或惡意帶入 `adArea` 或 `id` 且與路徑不匹配，系統未檢查直接覆蓋，造成資料錯亂。
- 日期驗證只做字串比較，未轉換為日期物件，導致跨月／跨年邏輯錯誤。
- 誤以為此 API 可以直接修改 `enabled`，違反業務規則。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由 | README.md, OpenAPI |
| DB Table Schema | db/ads.md (`advertising_sport` 定義) |
| 業務寫入限制 (adarea, id 不可變更) | advertisingservice-detail.md 寫入限制段落 |
| 業務寫入限制 (supportlangs 全量覆蓋) | advertisingservice-detail.md 常見錯誤段落 |
| 業務寫入限制 (seq 不可重複) | ads-detail.md `advertising_sport` seq 說明 |
| enabled 修改限制 | ads-detail.md `advertising_sport` enabled 說明：僅能由特定 API 變更 |
| 日期驗證規則 (startdate < closedate) | advertisingservice-detail.md 寫入限制 |
| Redis 使用矛盾 | README.md: 有 Redis SportAdCache；advertisingservice-detail.md: 本服務未使用 Redis。**需人工確認** |
| 日期格式 | 各文件共識：`startdate` / `closedate` 為 `yyyy-MM-dd` 字串 |
| 語言代碼有效性 | advertisingservice-detail.md: 每個元素須為有效語言代碼 |