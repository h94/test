# Hub 連線驗證 (CompanyToken 驗證)

## 1. 場景目的

客戶端（InplayZ 前端）透過 SignalR 建立 WebSocket 連線至 PriceClientSystem 服務時，  
驗證連線要求中的 `CompanyToken`，確保只有授權的公司（ZB、BB、PC）可以接收即時比分推送。

---

## 2. 入口 API

SignalR 連線建立是透過 `/hub` 端點進行（並非 REST API），實際技術細節如下：

| Method | Path | 說明 |
|--------|------|------|
| WebSocket Upgrade | `/hub` | 客戶端發起 SignalR 連線，於連線查詢字串或 headers 中附帶 `CompanyToken` |

> **需人工確認**：OpenAPI 文件未描述 SignalR hub 協商方式；根據 README 所述，前端須攜帶 Token 進行連線，需向開發團隊確認具體傳遞欄位名稱與位置（如 `?token=xxx` 或自訂 header）。

---

## 3. 流程總覽

1. 客戶端發起 SignalR 連線要求至 `/hub`。
2. 服務端 `Hub` 的 `OnConnectedAsync()` 觸發。
3. 從連線內容中取得 `CompanyToken` 值。
4. 比對 `AppSettings:HubSettings:CompanyToken` 設定檔中的 Token 清單（ZB / BB / PC）。
5. 若 Token 存在且與任一預設值相符：
   - 放行連線。
   - 記錄連線資訊（ConnectId、GameType、IP、Token）至記憶體。
   - 回傳連線成功。
6. 若 Token 遺失或不相符：
   - 拒絕連線（可能透過中斷連線或擲回 `HubException`）。
   - 不回傳任何即時資料。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | SignalR Hub | `GamesHub.OnConnectedAsync()` | 取得連線 token，呼叫驗證邏輯 |
| 2 | Service（可能） | `TokenValidationService.Validate()` | 比對 Token 是否在設定檔的 CompanyToken 清單中 |
| 3 | 記憶體內集合 | `ConnectionStore.Add()` | 若驗證通過，寫入連線資訊供 `/api/v1/system/hubinfo` 查詢 |
| 4 | SignalR Hub | `GamesHub.OnConnectedAsync()` 完成 | 允許連線持續存在 |

> **需人工確認**：具體類別名稱與架構（是否抽離 Service）需依實際代碼為準，此流程基於 README 中對 Hub 連線管理的描述推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| 記憶體（Memory） | 內部集合（如 `ConcurrentDictionary`） | Write | 儲存活躍連線資訊供 `/api/v1/system/hubinfo` 回傳 |

> 本場景**不涉及** Cassandra、Redis、Kafka 等持久化或快取儲存，連線驗證完全在服務執行個體記憶體中進行。

---

## 6. 重要規則

- **Token 表列管理**：允許的 `CompanyToken` 定義於 `appsettings.json` → `HubSettings.CompanyToken`，為一組硬式編碼值（ZB、BB、PC）。
- **連線拒絕**：Token 驗證失敗時，必須立即中止連線，不可洩漏任何資料或連線狀態。
- **Token 不可記錄於日誌**：嚴禁將 Token 明文寫入 Log。
- **連線資訊生命週期**：記憶體中的連線紀錄僅存活於該服務實例中；當服務重啟或連線中斷時自動清除。
- **無需額外權限模型**：驗證僅比較字串相等，不涉及使用者帳號或 RBAC。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 客戶端未提供 `CompanyToken` | 拒絕連線，SignalR 連線中斷 |
| `CompanyToken` 值為空字串或 null | 同上 |
| `CompanyToken` 與設定檔中任何一組 Token 不符 | 拒絕連線，可能回傳 `401 Unauthorized`（視實作而定） |
| 設定檔中未配置 `CompanyToken` 區域 | 服務啟動失敗或所有連線皆被拒（依容錯設計） |
| Token 大小寫不符 | 若字串比對為 case-sensitive，則拒絕（需人工確認是否忽略大小寫） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | Integration Test | 使用正確的 Token (ZB) 建立 SignalR 連線 | 連線成功，可在 `/api/v1/system/hubinfo` 中看到該連線 |
| T2 | Integration Test | 使用不存在的 Token 建立連線 | 連線失敗，客戶端收到錯誤或被強制斷線 |
| T3 | Integration Test | 不攜帶 Token 建立連線 | 連線失敗 |
| T4 | API Test | 呼叫 `/api/v1/system/hubinfo` 查看連線 | 僅回傳驗證通過的連線資訊，不含敏感 Token 明細（需人工確認：OpenAPI schema 中 `HubConnectionInfo` 有 `token` 欄位，此處存在資安疑慮） |

---

## 9. 高風險區域

- **Token 外洩**：`CompanyToken` 為長期有效之密鑰，若洩漏可能導致未授權方監看即時比分。  
- **靜態設定管理**：Token 寫在 `appsettings.json`，若部署流程不嚴謹（如未區分環境），可能造成跨環境 Token 混用。  
- **HubInfo API 洩漏 Token**：OpenAPI schema 中 `/api/v1/system/hubinfo` 回傳物件包含 `token` 欄位，若此值為原始 Token，等同將憑證對外公開，需資安審查。
- **無速率限制**：若無連線頻率控管，可能被濫用於連線洪水攻擊。

---

## 10. 常見錯誤

- 前端未在連線時傳遞 Token，誤以為只要命中 `/hub` 即可連線。
- 設定檔中的 `CompanyToken` 未隨環境更新，導致正式線 Token 被用於測試環境。
- 比對 Token 時使用 `==` 而非常數比較，可能引入時間差攻擊（若為自行實作字串比較）。
- 管理端忘記對外隱藏 `/api/v1/system/hubinfo` 端點或未脫敏回傳的 Token 欄位。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| 需求描述 | README.md → 「Token 驗證：AppSettings:HubSettings:CompanyToken 定義每個客戶端公司的驗證 Token（ZB、BB、PC）」 |
| API 規格 | OpenAPI – `/api/v1/system/hubinfo` 回傳 `HubConnectionInfo`（含 `token` 欄位） |
| 連線管理功能 | README.md → 「連線管理：紀錄每個 Hub 連線的資訊（ConnectId、GameType、IP、Token 等）」 |
| 技術棧 | README.md – SignalR Core (MessagePack 協議) |