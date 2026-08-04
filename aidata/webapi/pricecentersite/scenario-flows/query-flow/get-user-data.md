# 查詢會員資料（GetGameUserData）

## 1. 場景目的

已登入用戶查閱自己的基本資料，回傳 `username`、`rank`、`headshotPath`、`account` 等非機敏欄位；絕對不可暴露 `password`、`authkey`；`email` 僅限用戶本人查詢時回傳。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/GameUserData/{authKey}?site={site}` | 根據 authKey 查詢本人會員資料（*路徑、參數需人工確認*） |

> **需人工確認**：此 API 可能由 MemberModels 或 GameUserController 定義，確切路由及 site 參數請以最新 OpenAPI 或 Controller 程式碼為準。

---

## 3. 流程總覽

1. 請求進入應用，ECCore 中介層驗證 `authKey`，提取 `authkey`（Cassandra 主鍵）及 `site`。
2. 查詢 `member.gameusers`：`SELECT * FROM member.gameusers WHERE authkey = ?`。
3. 檢查帳號狀態：
   - `status` 必須為 `1`（啟用），否則拒絕（0 未啟用、2 凍結皆不可查）。
   - 查詢 `member.gameusers_banned`，若有未過期或永久封禁記錄，則拒絕。
4. 建構回傳 DTO：
   - 不可回傳 `password`、`authkey`。
   - 回傳 `username`、`rank`、`headshotpath`、`account`、`gamecount`、`signindays`、`memberships`、`email`（**本人查詢，可返回**）等。
5. 更新最後活動時間：寫入 Redis Key `GameUserLastActionTime:{authkey}`（TTL 300 秒），減少直接寫入 Cassandra 頻率（非同步、不阻塞回應）。
6. 回傳 HTTP 200 與使用者資料 JSON。

---

## 4. 程式流程

| 順序 | Layer | Class / Method（推測） | 動作 |
|------|-------|------------------------|------|
| 1 | Middleware | ECCore AuthMiddleware | 驗證 `authKey`；解析為內部 `authkey` 與 `site`，設定 `HttpContext.Items` |
| 2 | Controller | GameUserController.GetGameUserData | 接收路徑參數 `authKey`，呼叫 Service |
| 3 | Service | GameUserService.GetUserProfile | 組合 Provider，處理業務邏輯（狀態檢查、封禁檢查、DTO 轉換） |
| 4 | Provider | GameUserProvider | 查詢 Cassandra：`SELECT * FROM member.gameusers WHERE authkey=?` |
| 5 | Provider | GameUserBanProvider | 查詢 Cassandra：`SELECT * FROM member.gameusers_banned WHERE authkey=? LIMIT 1` |
| 6 | Service / Provider | (optional) RedisProvider | 寫入 Redis：`SET GameUserLastActionTime:{authkey} <now> EX 300`（非同步） |
| 7 | Controller | GameUserController | 序列化為 GameUserProfileDTO，回傳 200 |

> **需人工確認**：以上類別名稱與專案實際命名可能不同，請對照原始碼（如 `PriceCenterSite.Controllers`、`Services` 等）。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `member.gameusers` | Read（主鍵查詢） | 取得使用者完整資料 |
| DB | `member.gameusers_banned` | Read（條件點查） | 檢查是否遭封禁且封禁未過期 |
| Redis | `GameUserLastActionTime:{authkey}` | Write（SET） | 快取最後活動時間，TTL 300 秒；降低 Cassandra 寫入壓力（用於後續可能非同步回寫） |

> **佇列**：本場景未使用 Kafka 或其他訊息佇列。

---

## 6. 重要規則

- **權限限制**：
  - 僅通過 `ECCore` 驗證的有效登入者方可存取。
  - 查詢對象**必須為本人**（authkey 與當前登入使用者匹配，不可跨使用者查詢）。
- **欄位限制**（不可暴露）：
  - `password`（明文或雜湊）→ 任何 API 皆不可回傳。
  - `authkey` → 僅登入成功時回傳一次，此處不可洩漏。
  - `email` → **僅限本人**，若未來提供批次或他人查詢 API 則必須遮蔽。
- **狀態值限制**：
  - `status` 必須等於 `1`（啟用）才可回傳資料。
  - 若 `status = 0`（未啟用）或 `status = 2`（凍結）則回傳錯誤。
- **封禁規則**：
  - 若 `gameusers_banned` 存在相符的 `authkey`，且 `endtime` 為空（永久封禁）或 `endtime > NOW()`，拒絕存取，對外僅回傳「帳號已停用」。
- **TTL 規則**：
  - Redis `GameUserLastActionTime` 的 TTL 為 300 秒，寫入時可能使用限流（60 秒內不重複寫入，需人工確認）。
- **Transaction 規則**：
  - 此為唯讀查詢，不涉及 ACID 交易，Cassandra 查詢可用 `QUORUM` 一致性。
- **不可修改欄位**：
  - 此 API 僅讀取，所有寫入（含 `lastactiontime` 真實寫入 Cassandra）可能由其他排程從 Redis 回寫，本介面不負責。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `authKey` 缺失或無效（ECCore 驗證失敗） | 回傳 401 Unauthorized |
| `authKey` 有效但 `gameusers` 不存在 | 回傳 404 或「使用者不存在」 |
| `status != 1`（未啟用或已凍結） | 回傳 403 或「帳號未啟用/已停用」 |
| 使用者存在有效封禁記錄（`gameusers_banned` 未過期） | 回傳 403，訊息「帳號已停用」 |
| Cassandra 查詢逾時或連線失敗 | 回傳 500 Internal Server Error |
| Redis 寫入 `lastactiontime` 失敗 | 正常回傳 200（不阻塞流程），記錄警告日誌 |
| 嘗試查詢他人的 `authKey` | ECCore 中介層應阻擋，回傳 403（需人工確認防禦機制） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| GT-01 | API Test | 持有效 `authKey`，帳號 `status=1`，無封禁 | 200，回傳 `username`、`rank` 等，不含 `password`、`authkey` |
| GT-02 | Permission Test | 傳入他人 `authKey` | 403 Forbidden（需人工確認中間層是否強制匹配） |
| GT-03 | Flow Test | 帳號 `status=0`（未啟用） | 403，提示帳號未啟用 |
| GT-04 | Flow Test | 帳號 `status=2`（凍結） | 403，提示帳號已停用 |
| GT-05 | Flow Test | 帳號存在有效封禁紀錄 | 403，僅回傳「帳號已停用」，不暴露封禁原因 |
| GT-06 | Resilience Test | 模擬 Redis 連線失敗 | 仍回傳 200，不影響主要功能 |
| GT-07 | Security Test | 檢查回應 JSON 是否意外包含 `password` 或 `authkey` 欄位 | 必須不存在 |
| GT-08 | Data Test | 正常帳號回傳內容應包含 `email`（本人） | `email` 存在且正確 |

---

## 9. 高風險區域

- **高風險 Table**：`member.gameusers` （包含機敏欄位 `password`、`authkey`），任何存取皆需嚴格控制欄位暴露。
- **高風險 API**：此 `GetGameUserData` 若有權限漏洞，可被惡意讀取大量用戶資料。
- **快取一致性**：`lastactiontime` 僅寫入 Redis，若排程回寫 Cassandra 失敗，線上狀態可能不準確，但不影響本功能。
- **跨服務資料同步**：本場景無跨服務寫入，僅讀取 member keyspace。
- **Transaction**：無需分散式交易，但查詢與封禁檢查間可能有短暫時間差，Cassandra 不保證線性隔離，但對本功能影響輕微。
- **Queue retry**：無。
- **Idempotency**：GET 請求本身具備冪等性。

---

## 10. 常見錯誤

- ❌ 新人在 DTO 中忘記排除 `password` 與 `authkey`，導致嚴重資安事件。
- ❌ AI 易誤解「回傳 user profile」而將所有 `gameusers` 欄位輸出，違反「不可回傳欄位」規則。
- ❌ 未檢查 `status=1` 就返回停用或凍結帳戶資料。
- ❌ 忽略 `gameusers_banned` 封禁檢查，使已被封禁用戶仍可讀取資料。
- ❌ 認為 `email` 必然可暴露，但若未來開發他人查詢功能時，應不忘遮蔽或移除。
- ❌ 試圖直接對 `gameusers` 進行 UPDATE（如最後活動時間）在本 API 中實現，導致效能或一致性問題；應使用 Redis 快取。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 端點 | 推測為 `GET /api/GameUserData/{authKey}`，須人工確認（來自 MemberModels 1.1.9 及 pricecentersite 職責） |
| DB 讀取表 | `member.gameusers`（member schema）、`member.gameusers_banned` |
| 不可回傳欄位 | `member-detail.md`：`password`、`authkey` 絕不可回傳；`email` 僅本人可看 |
| 狀態檢查 | `member-detail.md`：`status = 1` 為啟用，非 1 拒絕 |
| 封禁檢查 | `member-detail.md`：登入驗證需額外查詢 `gameusers_banned` 並檢查 `endtime` |
| Redis 操作 | `pricecentersite-detail.md`：Key `GameUserLastActionTime:{authKey}`，TTL 300 秒 |
| 驗證中間層 | `README.md`：使用 ECCore 3.0.2 authKey 驗證機制 |

---

## 建議新增／補強項目

- **需人工確認 API 路徑**：確切路由、參數結構、query string 需求。
- **建議新增文件**：`GameUserData API Spec`（明確列出可回傳欄位清單、遮蔽規則）。
- **建議新增規則**：於 `rules/PLAN_SPEC` 中定義「使用者資料查詢必須過濾狀態與封禁、遮蔽機敏欄位」。
- **建議新增測試**：自動化安全測試掃描回應 JSON 中是否出現 `password` 與 `authkey` 欄位。