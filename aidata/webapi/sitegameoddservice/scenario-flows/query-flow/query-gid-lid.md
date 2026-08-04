# 查詢 gid/lid 對應關係

## 1. 場景目的

根據傳入的 gid 或 lid，從 Cassandra 的賽事表中查詢並回傳對應的賽事編號。此流程用於內部系統（如爬蟲、後台管理）建立或校驗不同遊戲編號之間的關聯。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/get/lid` | 根據單一 gid 查詢對應的 lid |
| POST | `/api/get/lids` | 根據多個 gid 批次查詢對應的 lid |

---

## 3. 流程總覽

1. 接收請求參數：`site`（站台）、`gtype`（球種）、`gid`（賽事 ID）。
2. 參數驗證。
3. 根據 `gtype` 動態決定查詢的 Cassandra 表名：`sitegames_{gtype}` 或 `games_{gtype}`。
4. 對 Cassandra 執行讀取查詢，條件為 `site` 與 `gid`。
5. 從查詢結果中提取 `lid` 欄位。
6. 回傳 `lid` 或 `gid` 與 `lid` 的對照清單。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GetLid` | 接收 GET 請求，取得 `site`、`gtype`、`gid` 參數，呼叫 Service。 |
| 2 | Controller | `GetLids` | 接收 POST 請求，取得 `site`、`gtype`、`gids`（列表）參數，呼叫 Service。 |
| 3 | Service | `SiteGameOddService.get_lid` | 進行參數驗證，組裝 CQL 查詢語句。 |
| 4 | Provider | `CassandraProvider.execute` | 對 Cassandra 執行非同步查詢。 |
| 5 | Transfer | `ResponseTransfer.to_dict` | 將查詢結果轉換為 API 回傳格式。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `pricecenter.sitegames_{gtype}` | Read | 查詢尚未開打的賽事對照資料。 |
| DB | Cassandra `pricecenter.games_{gtype}` | Read | 查詢已開打或歷史賽事對照資料。 |
| Cache | N/A | 未使用 | 此流程無快取機制，直接查詢 DB。 |
| Queue | N/A | 未使用 | 此流程不涉及非同步訊息。 |

---

## 6. 重要規則

- **讀取限制**：本服務對 `sitegames_{gtype}` 與 `games_{gtype}` 表僅有唯讀權限，不可寫入。
- **參數驗證**：`gtype` 必須是系統支援的球種代碼，否則無法組合出正確的表名，可能導致查詢失敗。
- **查詢條件**：為避免全表掃描，必須以 `site` 和 `gid` 作為查詢條件。
- **帳戶驗證**：此場景為內部輔助工具 API，未直接涉及帳戶權限驗證（需人工確認是否有 API Key 或 IP 白名單驗證）。
- **不可暴露欄位**：若賽事表包含內部配置或敏感資訊，回傳時應僅包含 `gid` 與 `lid`，不應暴露其他欄位。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 缺少必要參數 (`site`, `gtype`, `gid`) | 回傳 400 Bad Request，提示參數不足。 |
| 提供的 `gtype` 不支援 | 查詢的表不存在，Cassandra 驅動拋出異常，可能導致 500 Internal Server Error。 |
| 依 `site` 與 `gid` 查無對應資料 | 回傳空值或空列表，前端應自行處理空結果。 |
| Cassandra 連線超時或節點無回應 | 拋出 Cassandra Driver 例外，應由 Global Exception Handler 攔截並回傳 503 Service Unavailable。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | API Test | 對 `/api/get/lid` 發送 GET 請求，附帶合法的 `site`, `gtype`, `gid`。 | HTTP 200，回應中包含對應的 `lid`。 |
| T2 | API Test | 對 `/api/get/lids` 發送 POST 請求，附帶含多個 `gid` 的列表。 | HTTP 200，回應為 `gid` 與 `lid` 的對照列表。 |
| T3 | API Test | 發送請求時缺少 `gtype` 參數。 | HTTP 400 或 500。 |
| T4 | Flow Test | 提供已存在的 `gid`，驗證其流程。 | 成功從 `sitegames_{gtype}` 讀取並回傳 `lid`。 |
| T5 | Flow Test | 提供一個不存在的 `gid`。 | 回傳空結果。 |

---

## 9. 高風險區域

- **表名注入風險**：`gtype` 參數用於拼接表名，若未嚴格白名單驗證，可能導致 Cassandra 查詢錯誤。
- **直接依賴 Cassandra**：此流程無快取層，Cassandra 叢集的任何抖動或延遲都會直接影響 API 的回應時間與可用性。
- **全表掃描風險**：若查詢未嚴格限制 `site` 和 `gid` 條件，可能導致大範圍掃描，影響 Cassandra 效能。

---

## 10. 常見錯誤

- 未對 `gtype` 做白名單驗證，導致傳入非法值後，Cassandra 驅動因表不存在而報錯。
- 混淆 `sitegames_{gtype}` 與 `games_{gtype}` 的用途：一個儲存賽前資料，另一個儲存賽中/賽後資料，查詢時選錯表會找不到資料。
- 在批次查詢 (`get_lids`) 時，對每個 `gid` 單獨發起同步查詢，可能導致效能瓶頸。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `README.md` - 輔助工具 API 列表 |
| DB (Read) | `sitegameoddservice-detail.md` - 讀取規則：賽事查詢 |
| DB (Write Limit) | `sitegameoddservice-detail.md` - 寫入限制：sitegames_{gtype}、games_{gtype} |
| Code | `SiteGameOddService.get_lid` (推測) |
| Schema | `pricecenter.md` - sitegames_{gtype}、games_{gtype} |