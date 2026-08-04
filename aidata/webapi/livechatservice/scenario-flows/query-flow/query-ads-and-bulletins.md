# 查詢廣告與公告

## 1. 場景目的
根據前端請求（可能包含語言、廣告區域等參數），從 Cassandra `ads` keyspace 中讀取已啟用且符合時間範圍的廣告（`advertising`、`advertising_sport`）與公告（`bulletinboard_sport`），並以正確的順序回傳，供 LiveChat 前端展示。

---

## 2. 入口 API
> 需人工確認：目前提供的 OpenAPI 文件與 Code Evidence 中，未發現精準對應「查詢廣告與公告」的 API 端點。本場景推測可能由某個前端初始化或輪詢 API 觸發，或位於未掃描到的 Controller 中。

| Method | Path | 說明 |
|--------|------|------|
| 需人工確認 | 需人工確認 | 推測為 GET，用於取得廣告與公告。若無此 API，則需建立。 |

---

## 3. 流程總覽
1. 接收查詢請求（可能含 `adarea`、`lang` 等條件）。
2. 連線至 Cassandra `ads` keyspace。
3. 查詢 `advertising`：過濾 `enabled=1` 且當前時間戳（毫秒）在 `[starttime, closetime]` 內，依 `seq` 正序。
4. 查詢 `advertising_sport`：根據 `adarea` 過濾，`enabled=1`，且今日日期在 `[startdate, closedate]` 內（需解析字串），依 `seq` 正序。
5. 查詢 `bulletinboard_sport`：過濾 `status=1`，且當前時間在 `[starttime, endtime]` 範圍內（需解析字串），依 `sequence` 正序。
6. 組合結果並回傳。本流程無 Redis 或 Kafka 操作，亦無外部 API 呼叫。

---

## 4. 程式流程
> 需人工確認：Code Evidence 中未直接發現對應此流程的 Controller 或 Service 方法，以下為依賴 DB 使用規則推斷之標準分層。

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | 需人工確認 | 接收請求，呼叫 Service |
| 2 | Service | 需人工確認 | 組裝查詢條件，呼叫 Cassandra Provider |
| 3 | Provider | CassandraAdsProvider (推測) | 執行 CQL 查詢，回傳 DTO |
| 4 | Service | 需人工確認 | 組合三表結果，排序後回傳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `ads.advertising` | Read | 讀取通用廣告 |
| DB | `ads.advertising_sport` | Read | 讀取體育廣告，以 `adarea` 為分區鍵 |
| DB | `ads.bulletinboard_sport` | Read | 讀取公告 |

- Redis：無使用。
- Kafka：無使用。
- Queue：無使用。

---

## 6. 重要規則
- **權限限制**：livechatservice 僅為 `reader`，嚴禁對這三張表執行 INSERT / UPDATE / DELETE。
- **狀態過濾**：廣告 `enabled` 必須為 `1`；公告 `status` 必須為 `1`。
- **時間驗證**：
  - `advertising.starttime/closetime` 為 **bigint epoch 毫秒**，當前時間需在範圍內。
  - `advertising_sport.startdate/closedate` 為 **yyyy-MM-dd 字串**，必須解析為日期物件後比較，**禁止直接字串比對**。
  - `bulletinboard_sport.starttime/endtime` 為 **yyyy-MM-dd HH:mm:ss 字串**，必須解析後比較。
- **排序**：`advertising` 依 `seq` ASC；`advertising_sport` 在同一 `adarea` 內依 `seq` ASC；`bulletinboard_sport` 依 `sequence` ASC。
- **欄位暴露**：無特別敏感欄位需隱藏，但 `createdby`、`adclass` 不應回傳。
- **語言處理**：需人工確認：`advertising_sport.supportlangs` 的比對邏輯與 `bulletinboard_sport` 多語言欄位的選擇邏輯。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| Cassandra 連線失敗或超時 | 回傳 HTTP 500 或空陣列，記錄錯誤日誌 |
| 未過濾 `enabled=0` / `status=0` | 回傳不該出現的資料，視為邏輯錯誤 |
| `advertising_sport` 日期用字串比對 | 可能因字典序導致錯誤過濾，例如 `'2025-1-1' > '2025-02-01'` |
| 時間戳單位混淆（秒/毫秒） | 廣告在錯誤時間顯示或隱藏 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| ADS-01 | Flow Test | 請求廣告，存在 enabled=1 且在有效期內 | 成功回傳，依 seq 排序 |
| ADS-02 | Flow Test | 請求廣告，存在 enabled=0 或過期 | 該筆不出現 |
| ADS-03 | Boundary Test | `advertising_sport` 日期為 `startdate=closedate=今天` | 正確回傳今日廣告 |
| ADS-04 | Boundary Test | `bulletinboard_sport` 當前時間等於 `starttime` 或 `endtime` | 正確回傳範圍內公告 |
| ADS-05 | DB Error | Cassandra 不可用 | Graceful degradation，記錄 error |

---

## 9. 高風險區域
- **高風險 Table**：`ads.advertising`、`ads.advertising_sport`、`ads.bulletinboard_sport`。所有查詢都重度依賴時間處理與狀態過濾的正確性。
- **Cache Consistency**：本場景無快取，無此風險。
- **Idempotency**：讀取操作具有冪等性。

---

## 10. 常見錯誤
- 忘記過濾 `enabled = 1` 或 `status = 1`，導致未啟用或草稿內容曝光。
- 對 `advertising_sport` 的日期進行字串比對，而非日期物件比對。
- 混淆 `advertising.starttime` 的毫秒單位與其他表可能使用的秒單位，導致時間判斷失效。
- 忽略 Cassandra 分區鍵設計，對 `advertising_sport` 進行全表掃描而非指定 `adarea`（若前端未傳，需有預設策略）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | 需人工確認 |
| DB | `ads.advertising`, `ads.advertising_sport`, `ads.bulletinboard_sport` |
| Code | 需人工確認 Controller/Service/Provider 實作文件 |
| Rule | `livechatservice-detail.md` (讀取規則、常見錯誤) |
| Rule | `ads-detail.md` (服務角色、欄位規則) |
| Schema | `ads.md` (欄位定義) |