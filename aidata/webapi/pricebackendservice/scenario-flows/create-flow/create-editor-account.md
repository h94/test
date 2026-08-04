# 建立編輯者帳號

## 1. 場景目的

後台管理員為指定的 `authKey` 建立一個具備編輯權限的遊戲會員帳號，用於內容管理或客服操作。此流程由 pricebackendservice 作為 BFF 聚合層，轉送請求至下游 memberservice 完成實際建立。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/member/game/editors/{authKey}` | 建立編輯者帳號，需管理後台驗證 |

---

## 3. 流程總覽

1. 管理後台通過驗證框架（ECFramework.ECService）的後端 token 驗證。
2. Controller 接收 `authKey` 路徑參數及建立編輯者所需的請求體（如帳號、密碼、暱稱等）。
3. 呼叫 MemberService（Service 層）進行參數校驗與轉換。
4. MemberService 呼叫 Provider 層（如 `MemberProvider`），向 `memberservice` 發送 REST 請求。
5. `memberservice` 檢查 `authKey` 是否已存在，並執行帳號建立邏輯（雜湊密碼、寫入 `member.gameusers` 表、初始化狀態）。
6. 建立成功後回傳編輯者基本資訊（不含密碼及 authKey）。
7. （必要時）更新 Redis 快取 `GameUser:{authKey}` 以確保一致性。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `MemberController.CreateEditor(authKey, request)` | 接收 HTTP 請求，檢查權限，轉交 Service |
| 2 | Service | `MemberService.CreateEditor(authKey, request)` | 校驗 request body（如帳號格式、密碼強度），轉換為 DTO |
| 3 | Provider | `MemberProvider.CreateEditor(dto)` | 包裝 REST 請求，呼叫 `memberservice` 內部 API |
| 4 | (下游) | `memberservice` → `IGameSettingService.CreateUser` | 執行 `INSERT` 至 `member.gameusers`，寫入 `authkey`、`account`、`password`（雜湊）、`status=0` 等，回傳成功結果 |
| 5 | Provider / Service | (同層) | 處理下游回應，映射為對外 DTO（隱藏敏感欄位） |
| 6 | Controller | (返回) | 回傳 200 與編輯者資訊（無密碼、authKey） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (member keyspace) | `member.gameusers` | INSERT | 寫入編輯者帳號資料（authkey, account, password, status, 等） |
| Cache (Redis) | `GameUser:{authKey}` | SET / DEL | 建立後可選擇寫入快取，或因狀態變更清除舊快取（由 memberservice 管理） |

> pricebackendservice 本身不直接操作 DB 或 Redis，所有操作透過 memberservice 完成。

---

## 6. 重要規則

- **權限限制**：僅後台管理員（經過 `ECService` 驗證）可呼叫此 API。
- **不可修改欄位**：`authkey`、`account`、`password` 建立後不可透過本 API 更新；任何修改需走專用流程。
- **不可暴露資料**：API 回應不得包含 `password`（明文或雜湊）、`email` 及原始 `authkey`。對外僅回傳 username、status 等必要資訊。
- **狀態值限制**：新建立的編輯者 `status` 預設值應為 0 或 1（依業務規則），需人工確認（推測為 0，待啟用）。
- **密碼規則**：密碼須符合強度要求（如長度、字元類型），並在 `memberservice` 端進行雜湊（BCrypt 或等效）。
- **唯一性檢查**：`authKey` 為全域唯一，若已存在則拒絕建立。
- **Transaction 規則**：本服務無跨資料庫交易；一致性由 `memberservice` 的單一 keyspace 寫入保證。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未提供有效後台 token | 回傳 401 Unauthorized |
| `authKey` 已存在於 `member.gameusers` | 回傳 409 Conflict 或業務錯誤碼 |
| 請求體缺少必填欄位（如 account, password） | 回傳 400 Bad Request |
| 密碼強度不足 | 回傳 422 或業務錯誤，附帶規則說明 |
| 下游 `memberservice` 無回應或逾時 | 回傳 502 Bad Gateway |
| `memberservice` 寫入失敗（如主鍵衝突） | 回傳 500 或特定錯誤，後台提示重新操作 |
| 快取寫入失敗（Redis 異常） | 不影響主要流程，記錄告警，下次查詢時 miss 快取會查 DB |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC01 | Permission Test | 無 token 呼叫 | 401 |
| TC02 | Permission Test | 非管理角色 token | 401 或 403 |
| TC03 | API Test | 成功建立（全新 authKey） | 200，回傳編輯者資訊無敏感欄位 |
| TC04 | API Test | 重複 authKey | 409 或業務錯誤 |
| TC05 | API Test | 缺 account 欄位 | 400 |
| TC06 | API Test | 弱密碼 | 422 或業務錯誤 |
| TC07 | Integration Test | memberservice 離線 | 502 或自定義錯誤 |
| TC08 | Flow Test | 建立後查詢 `member.gameusers`（透過內部 API） | 確認 `password` 為雜湊、`authkey` 正確 |

---

## 9. 高風險區域

- **authKey 唯一性**：若下游未正確檢查，可能導致覆蓋既有帳號；需確保 `memberservice` 使用 `INSERT` 並檢查 primary key。
- **密碼安全**：密碼絕不可明文寫入，且不得回傳。對外 API 若誤傳將為資安重大漏洞。
- **快取一致性**：若建立後未清除或更新 `GameUser:{authKey}` 快取，後續查詢可能得到舊資料或 nil；但通常新帳號尚無快取，風險較低。
- **跨服務呼叫**：pricebackendservice 完全依賴下游 `memberservice`，若下游無法水平擴容或回應延遲，會直接影響後台體驗。應設定合理的 timeout 與 retry 策略。

---

## 10. 常見錯誤

- 新人或 AI 直接嘗試寫入 `member.gameusers` 表 → **本服務禁止直接 DB 操作**，必須透過 `memberservice`。
- 忘記在 DTO 中排除 `password` 而直接序列化回應 → 導致密碼雜湊外洩。
- 假設 `authKey` 由用戶提供，而未檢查其安全性 → `authKey` 應由系統生成（如 `Hash.HashAuthString(account)`），不可由前端直接指定。
- 未檢查請求體的帳號格式（如是否允許特殊字元）→ 可能導致下游無法處理。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/v1/member/game/editors/{authKey}`（README） |
| 寫入限制 | `authkey`, `account`, `password` 僅由 `IGameSettingService.CreateUser` 寫入（pricebackendservice-detail.md / member-detail.md） |
| 不可回傳欄位 | `password`, `authkey` 不可對外暴露（pricebackendservice-detail.md） |
| 服務相依 | `memberservice` 負責編輯者帳號（README） |
| 快取 | `GameUser:{authKey}` Redis key（member-detail.md），由 memberservice 管理 |
| 驗證 | 所有 `/api/v1/member/...` 需要驗證（README） |