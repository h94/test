# 客戶端 SignalR 連線驗證

## 1. 場景目的

客戶端透過 SignalR 建立連線時，InplayzSubscriptionSystem 驗證連線請求中的商務代碼 (Site) 與授權 Token，並以 IP 為單位進行速率限制（每 3 分鐘最多 20 次）。驗證成功後，記錄連線資訊並允許客戶端接收後續賽事推送。

---

## 2. 入口 API

此流程的入口並非傳統 REST API，而是 SignalR 連線請求（WebSocket / HTTP 協商）。

| Method | Path | 說明 |
|---|---|---|
| SignalR 連線 | `/hub` (預設路徑，需人工確認) | 客戶端建立 SignalR 連線時觸發 |
| 中介軟體 / Hub 生命週期 | `OnConnectedAsync` | 由 ASP.NET Core SignalR Hub 或自訂驗證過濾器觸發 |

---

## 3. 流程總覽

1. 客戶端發起 SignalR 連線請求
2. 系統從連線上下文擷取 Client IP、Site（商務代碼）、Token
3. 執行 IP 速率檢查（Sliding Window / Fixed Window，需人工確認演算法）
4. 若超過限制，拒絕連線並回傳錯誤
5. 驗證 Token（呼叫授權服務或本地快取比對，需人工確認）
6. 驗證商務代碼 (Site) 有效性，並取得商務訂閱資訊、賽事需求（如比分、賠率，需人工確認）
7. 快取商務訂閱資訊（Redis，需人工確認）
8. 將連線資訊寫入內部記錄（DB / Redis，需人工確認）
9. 將連線加入 SignalR Group（以 Site 為群組名）以供後續訊息推送
10. 完成連線建立

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware / Hub | `OnConnectedAsync` | 接收連線請求，取得 `HttpContext` |
| 2 | Hub / Attribute | Extract `Site` from query string or headers | 自訂 Attribute 或 Hub 邏輯擷取 `Site` 代碼 |
| 3 | Hub / Attribute | Extract `Token` from query string or headers | 請參考 SignalR 連線攜帶 Token 方式 (JWT / OAuth) |
| 4 | Provider | `RateLimitProvider.CheckLimit(ip)` | 以 IP 檢查 Redis 速率記錄，更新計數並判斷是否超限 |
| 5 | Service | `BusinessVerificationService.Verify(site, token)` | 驗證 Token 有效性，需人工確認採用本地快取還是呼叫外部授權服務 |
| 6 | Service / Provider | 查詢快取或 DB 取得 `site` 對應的賽事訂閱資訊 | 需人工確認取得哪些設定（推送範圍、賽事過濾條件等） |
| 7 | Service | `BusinessVerificationService.GetBusinessInfo(site)` | 取得或快取商務資訊（訂閱時效、權限），需人工確認 DB 來源表名與 SQL |
| 8 | Hub | `Groups.AddToGroupAsync(connectionId, site)` | 將當前連線加入指定 Group |
| 9 | Hub | `ConnectionLogService.Log(connectionId, ip, site, time)` | 記錄連線資訊，需人工確認儲存至 DB（Cassandra / MySQL）還是 Redis |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | `ratelimit:{ip}` | Write / Read | 儲存該 IP 的連線嘗試次數與 TTL；需人工確認實際 Key 與 TTL 是否為 3min |
| Redis | `business:subscription:{site}` (推測) | Read | 快取商務訂閱資訊、訂閱時效 |
| Redis | `connections` (推測) | Write / Read | 記錄所有活躍連線 ID 與狀態，用於後續斷線清理 |
| DB (Cassandra) | `member.gameusers` (推測) | Read | 驗證 Token 對應使用者之狀態（`status`、`memberships`）；需人工確認此步驟是否由本服務執行 |
| DB (MySQL / Cassandra) | 商務訂閱表（待確認） | Read | 載入商務代碼、有效訂閱時效、相關設定值 |
| Kafka | － | － | 連線驗證階段未涉及 Kafka 操作 |

---

## 6. 重要規則

- **IP 速率限制**：每 IP 3 分鐘內最多允許 20 次連線嘗試，超過即拒絕。違規連線無需清除 Redis 計數，等待 TTL 自然過期。
- **權限限制**：只有通過 Token 驗證的客戶端可成功建立連線；一般使用者無法偽造連線參數。
- **不可暴露資料**：對外不可回傳內部 Token 驗證失敗的詳細錯誤原因；商務代碼清單與訂閱細節不可暴露。
- **TTL 規則**：Rate Limit Redis Key 的 TTL 需與限制時間同步（3分鐘）。商務快取的 TTL 需視訂閱時效變更而主動失效。
- **Group 機制**：所有連線必須加入對應的 `Site` Group，斷線時自動移除 Group；不重複建立相同 Group。
- **Token 格式**：預設為標準 JWT 或自訂簽章字串；過期時間不可超過商務訂閱時效。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 連線請求缺少 `Site` 參數 | 拒絕連線，回傳 `BusinessSiteMissing` |
| 連線請求缺少 `Token` 或 Token 格式錯誤 | 拒絕連線，回傳 `TokenInvalid` 或 `Unauthorized` |
| IP 連線次數超過限制 | 拒絕連線，回傳 `RateLimitExceeded` 或相似錯誤 |
| Token 已過期 | 拒絕連線，回傳 `TokenExpired`，不觸發速率限制計入 |
| 商務代碼不存在或訂閱已過期 | 拒絕連線，回傳 `BusinessUnavailable` |
| Redis 暫時無法存取 | 連線失敗，回傳內部錯誤（不應無限制放行），需人工確認是否使用 Circuit Breaker |
| SignalR 連線過程中 DB 查詢逾時 | 中止連線，回傳內部錯誤；不應保留未完成連線 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | Integration Test | 正常連線，帶合法 `site` 與 `token` | 成功連線，加入 Group，可接收推送 |
| T02 | Permission Test | 連線不帶 Token | 拒絕連線，錯誤回應 |
| T03 | Permission Test | Token 過期或廢棄 | 拒絕連線 |
| T04 | Flow Test | 同 IP 在 3 分鐘內快速連線 20+ 次 | 第 21 次開始拒絕連線 |
| T05 | Flow Test | 3 分鐘後再次連線（Rate Limit Key 過期） | 成功連線，計數重置 |
| T06 | Permission Test | 不存在的 `site` 代碼 | 拒絕連線 |
| T07 | API Test | 商務訂閱已過期 | 拒絕連線，錯誤回應 |
| T08 | Flow Test | 連線斷開再重新連線 | 重新驗證，原連線 ID 應從記錄清除 |
| T09 | Permission Test | 帶合法 Token 但對應使用者被停用（`status != 1`） | 拒絕連線（需人工確認本步驟是否執行） |

---

## 9. 高風險區域

- **高風險 API**：SignalR 連線端點，容易成為 DDoS 攻擊目標；速率限制為第一道防護。
- **高風險 Table**：商務訂閱資訊表（待確認表名與 keyspace），若資料不一致將導致合法商務無法連線。
- **Redis Rate Limit**：多實例部署下需確保 Redis Key 原子性（INCR + EXPIRE 一次執行）；需人工確認使用 Lua 腳本或 MULTI/EXEC 事務。
- **Token 驗證**：若驗證依賴外部服務（如 `memberservice`），需有重試、容錯機制；外部服務掛掉時不應癱瘓整個連線。
- **快取一致性**：商務訂閱變更時（如續訂、過期），需主動清除快取，不可只等 TTL。
- **Idempotency**：連線請求不可重試導致重複建立 Group；SignalR 內部已確保 ConnectionId 唯一。

---

## 10. 常見錯誤

- ❌ 忘記在連線時加入 Site Group，導致客戶端無法接收任何推送訊息。
- ❌ Rate Limit 使用 `SETEX` 或單獨 `EXPIRE` 而與計數邏輯不同步，導致計數未重設。
- ❌ Token 驗證成功後未再次確認商務訂閱時效，導致過期商務仍能連線。
- ❌ 連線記錄未寫入 Repository，斷線後無法清除或統計。
- ❌ 錯誤訊息洩漏內部 Token 格式或商務代碼列表給攻擊者。
- ❌ 將連線驗證的 Token 誤用於對外 API 的權限判斷。
- ❌ 假設 Redis Key 永不過期，未設定 TTL 或未考慮 Redis 記憶體上限。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| 速率限制規則 | `README.md` → 連線管理與安全：每 IP 3 分鐘內最多 20 次連線 |
| SignalR Hub 存在 | `README.md` → 主要功能：SignalR Hub 推送 |
| Group 機制 | `README.md` → SignalR Hub 支援 Group 推送（依 Site 分類） |
| Token 驗證需求 | `README.md` → 驗證商務代碼與授權 Token |
| Site 參數 | `README.md` → 商務驗證與快取 |
| Redis 快取 | `product-detail.md` / `README.md` → 商務快取與產品快取的使用模式（推測特定 key） |
| 無 Kafka 參與 | `README.md` → Kafka 僅用於賽事消費，與連線驗證無關 |
| Token 驗證細節 | **需人工確認** → 實際驗證機制程式碼路徑（`AuthService` / `TokenProvider`） |
| 商務 DB 操作 | **需人工確認** → 對應 Cassandra / MySQL Table 與 SQL 操作（如 `BusinessDataProvider`） |
| Redis Key | **需人工確認** → `rate_limit:{ip}`, `sites:{site}:info` 等實際名稱與 TTL |
| Hub 名稱 / 路由 | **需人工確認** → SignalR Hub 路徑 (ex: `/hubs/inplayz`) |