# 查詢所有 Bet365 頁面

## 1. 場景目的

管理後台查詢所有 Bet365 爬蟲頁面的設定資訊，用於顯示爬蟲監控儀表板上的頁面狀態與排程設定。讓管理員能快速了解目前系統監控的所有 Bet365 頁面及其設定，以便進行手動調整或排程管理。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/bet365/allpage` | 查詢所有 Bet365 頁面 |

---

## 3. 流程總覽

1. 接收查詢所有頁面請求。
2. 驗證使用者操作權限（呼叫 ECFramework）。
3. 從資料來源讀取「所有 Bet365 頁面」設定（依據現有文檔，推測為管理後台之 Cassandra 或對應 DB Table）。
4. 組裝 DTO 並回傳結果。
5. 回傳 Bet365 頁面設定列表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `Bet365Controller.GetAllPages` | 接收 GET request。驗證通過後，呼叫 Service 取得所有頁面資料（此為推測流程，需人工確認實際 Controller 命名）。 |
| 2 | Service | `IBet365Service.GetAllPages` | 透過 Provider 讀取所有頁面設定並組裝 DTO。 |
| 3 | Provider | `IBet365Provider.GetAllPages` | 執行資料讀取操作，從 Cassandra 或相關設定檔中取得所有 Bet365 頁面設定。 |
| 4 | Transfer | `Bet365PageDto` | 將 Provider 取得的資料物件映射為回傳用的 DTO。 |
| 5 | Controller | `Bet365Controller.GetAllPages` | 將結果組裝成 Response 回傳端點。 |

**需人工確認**：上述流程係基於系統架構推測，實際類別名稱、Provider 組合可能異動。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB（Cassandra） | pricecenter keyspace：Bet365 頁面設定 Table | Read | 讀取所有 Bet365 頁面設定、排程、狀態等資料。Table 名稱需人工確認。 |

**需人工確認**：`Bet365 頁面設定`確切 Cassandra Table 名稱，目前文檔未標示為標準 `accounts_*` 或 `predict.*` 範圍，可能屬於 pricecenter keyspace 內的動態生成或特定設定 Table。

---

## 6. 重要規則

- **權限限制**：需具備管理後台操作權限，由 ECFramework 驗證機制攔截，無權限者將被拒絕。
- **不可暴露欄位**：管理後台下的爬蟲帳號密碼（若存在相關設定關聯 `accounts_{source}.password`）不可回傳。
- **狀態值限制**：回傳之頁面狀態、排程設定值應以已定義的列舉值為準；不可回傳未定義的狀態碼。
- **不可修改**：此 API 為唯讀查詢，不應執行任何 INSERT、UPDATE 或 DELETE 操作。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求未帶有效驗證 token | 回傳 401 Unauthorized |
| 權限不足（token 所屬角色非管理後台） | 回傳 403 Forbidden |
| Cassandra 查詢逾時或無法連接 | 回傳 500 Internal Server Error，由系統全域例外處理機制攔截。管理後台前端應顯示資料撈取失敗。 |
| 資料 Table 不存在或不完整 | 可能回傳空陣列或拋出例外，依 Provider 內部實作而定。需人工確認實際對未初始化 Table 的行為。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-B365-01 | API Test (Integration) | 管理員權限呼叫 API | 回傳 200 OK，包含正確的 Bet365 頁面設定陣列 |
| UT-B365-02 | API Test (Integration) | 無 token / 使用過期 token 呼叫 API | 回傳 401 Unauthorized |
| UT-B365-03 | Permission Test | 一般使用者（不具後台權限）呼叫 API | 回傳 403 Forbidden |
| UT-B365-04 | API Test | Cassandra 無資料或查無頁面設定 | 回傳 200 OK，但結果陣列為空 `[]` |
| UT-B365-05 | Flow Test | Cassandra 連線中斷或查詢超時 | 回傳 500 Internal Server Error |

---

## 9. 高風險區域

- **crawler heartbeat 相依**：此查詢所得頁面設定，應對應到各爬蟲機器的回報狀態。若頁面設定與爬蟲機器心跳不同步，監控儀表板可能誤報或遺漏錯誤。此部分跨服務相依需特別注意。
- **跨站台（accounts）頁面**：需確認讀取範圍是否限定於特定站台（site）或涵蓋全部。若涵蓋全部，需注意跨品牌資料隔離問題。
- **非結構化 Table**：若頁面設定儲存於 Cassandra 中非標準結構的 Table（如 Map、List 等動態結構，因 Bet365 爬蟲提供者可隨時新增頁面），回傳 DTO 的結構設計需靈活，避免反序列化失敗。

---

## 10. 常見錯誤

- ❌ **呼叫時忽略 API 需驗證**：此為管理後台 API，需帶入完整驗證 header；遺漏將導致 401/403。
- ❌ **假設回傳資料精華**：新人不應預期回傳的頁面狀態可直接與爬蟲連線狀態畫等號，應確認端點回傳的「頁面設定」與經 `/api/v1/system/machines/crawler` 回報的「即時狀態」屬不同維度資訊。
- ❌ **跨 Keyspace 掃描**：若非必要，Provider 實作不應對 `pricecenter` 進行全區掃描。若 Table 設計以站台為分割鍵，應附加必要條件限制。
- ❌ **直接對外回傳 `handler` 或 `password` 等帳號資訊**：若內部實作為了取得頁面設定而同時撈取關聯的爬蟲帳號（accounts_*）資訊，必須確保最終 DTO 不包含任何密碼或內部管控欄位。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `Bet365Controller`（作為推測起點，需人工確認 Controller 完整路徑） |
| DB | Cassandra `pricecenter` keyspace（由 pricecentermanage 主要操作 Cassandra 推測） |
| Code | `IBet365Service.GetAllPages`、`IBet365Provider.GetAllPages` |
| 權限 | ECFramework（參考 README 技術棧描述） |