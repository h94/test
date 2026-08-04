# 取得 Hub 連線資訊

## 1. 場景目的

查詢目前 SignalR Hub 的即時連線狀態，包括每個連線的 ConnectId、GameType、IP、Token 與選擇站點等，以及各站點的最後資料更新時間，用於監控與問題排查。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/system/hubinfo` | 查詢 SignalR Hub 連線與站點狀態，無須 body 參數 |

---

## 3. 流程總覽

1. 接收 HTTP GET 請求。
2. （推測）從 Hub 連線管理模組取得所有存活連線的資訊清單。
3. （推測）讀取站點資料最後更新時間（來源可能為記憶體或 Redis 快取）。
4. 組裝 `HubInfo` 回傳物件，包含 `connections` 與 `siteInfo` 兩部分。
5. 回傳 200 OK，內容為 JSON。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | (未知 Controller，推測為 `SystemController`) | 接收請求，呼叫對應 Service 方法 |
| 2 | Service | (未知 Hub 管理 Service，推測為 `HubConnectionService`) | 取得當前所有連線的 `HubConnectionInfo` 清單 |
| 3 | Service | 同上或獨立 `SiteStatusService` | 取得各站點最後更新時間 (`HubSiteInfo`) |
| 4 | Service/Controller | 組裝 `HubInfo` 並回傳 | — |

> 註：本流程僅依據 OpenAPI 結構推測，實際 Controller 與 Service 名稱需查閱原始碼（**需人工確認**）。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| 無已知 DB 操作 | — | — | 此查詢為記憶體資料，未涉及 Cassandra |
| 無已知 Cache | — | — | 此查詢即時性高，通常不啟用快取；若使用快取，僅為站點時間（**需人工確認**） |
| 無 Queue / Kafka | — | — | 不參與此場景 |

---

## 6. 重要規則

- **Token 欄位**：`HubConnectionInfo.token` 代表客戶端連線驗證用的 token，**對外暴露可能造成安全風險**，應在輸出前評估是否需脫敏或完全移除（**需人工確認**）。
- **權限限制**：此 API 為系統監控用途，**應限制僅內部管理網路/後台人員可存取**（現行未定義認證機制）（**需人工確認**）。
- **不可暴露資料**：連線的 IP 可能為內部 IP 或用戶真實 IP，若為用戶 IP，需考量隱私法規，必要時進行脫敏。
- **TTL / 快取規則**：此端點不建議快取，因為查詢的是即時連線狀態。
- **狀態值限制**：連線資訊若特定欄位為空，回傳時應保留 `null`，不應填入假資料。
- **Transaction / Retry**：此查詢為唯讀，不涉及交易或重試機制。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 無任何 SignalR 連線存在 | `connections` 為空陣列，`siteInfo` 可能為空或含有資料（需人工確認） |
| 內部無法取得連線清單（例如 Hub 服務異常） | 回傳 HTTP 500 或 503，內容為錯誤訊息（**需人工確認具體處理**） |
| 請求方未經授權（若有權限控制） | 回傳 401 或 403（若實作驗證，**需人工確認**） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC-HUB-01 | API Test | 正常請求，Hub 有多個連線 | 200 OK，connections 清單數量符合實際連線數 |
| TC-HUB-02 | API Test | 無任何連線時 | 200 OK，connections 為空陣列 |
| TC-HUB-03 | Schema Test | 驗證回傳 JSON 結構符合 OpenAPI | 欄位齊全，型別正確 |
| TC-HUB-04 | Permission Test | 未授權用戶（若實作）調用 API | 401/403（依實作決定，**需人工確認**） |
| TC-HUB-05 | Security Test | 確認回傳的 token 是否已脫敏 | token 不應為原始金鑰（依安全政策而定） |

---

## 9. 高風險區域

- **高風險 API**：`/api/v1/system/hubinfo` 若未保護，可能洩漏內部連線 IP、token 等敏感資訊。
- **資訊洩漏**：回傳物件包含 `connectId`、`ip`、`token`，若無權限控管，有被惡意掃描之虞。
- **無狀態擴展**：此 API 查詢的是單一節點的 Hub 連線，若服務有多個執行個體，需確認是否彙總所有節點的連線（**需人工確認**）。

---

## 10. 常見錯誤

- ❌ 將此 API 用於業務邏輯判斷（例如判斷用戶是否在線）——此 API 僅供監控，不宜做為在線狀態 API。
- ❌ 回傳未脫敏的 token 給前端，造成安全漏洞。
- ❌ 實作時直接序列化整個 Hub 內部物件，導致多餘欄位外洩。
- ❌ 忘記加入權限驗證，使任意網際網路用戶均可查閱內部連線明細。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OpenAPI 定義：`/api/v1/system/hubinfo` |
| 回傳結構 | OpenAPI 定義：`HubInfo`、`HubConnectionInfo`、`HubSiteInfo` |
| Hub 連線概念 | README「連線管理」段落：紀錄每個 Hub 連線的資訊（ConnectId、GameType、IP、Token 等） |
| 無 DB 操作 | 此場景無關 DB；priceclientsystem-detail 未提及此 API 使用 Cassandra |
| 需人工確認 | Controller/Service 具體名稱、權限控制、Token 揭露規則、多節點彙總行為 |