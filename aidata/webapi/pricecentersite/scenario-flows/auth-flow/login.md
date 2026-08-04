# 用戶登入

## 1. 場景目的
驗證使用者 email 與密碼，確認帳號狀態為啟用且未被封禁，成功後回傳 `authkey` 作為後續 API 請求的 token。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/auth/login` (需人工確認) | 接收 email、password，回傳 authkey 與基本資料 |

---

## 3. 流程總覽
1. 接收登入請求，取出 `email`、`password`
2. 查詢 `member.gameusers`，使用二級索引 `WHERE email = ? AND status = 1`
3. 若找不到記錄或 status ≠ 1，回傳「帳號不存在或已停用」
4. 比對密碼（BCrypt / 雜湊）
5. 根據查出的 `authkey` 查詢 `member.gameusers_banned`
6. 若存在封禁記錄且 `endtime` 未過期（或為 null 代表永久封禁），拒絕登入
7. 成功則回傳該使用者的 `authkey`（作為 token），以及必要的基本資料（不含密碼）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `AuthController.Login` (需人工確認) | 接收 HTTP request，調用 Service |
| 2 | Service | `AuthService.Login` (需人工確認) | 組合查詢邏輯 |
| 3 | Provider / Repository | `GameUserRepository` (需人工確認) | 執行 Cassandra 查詢 |
| 4 | Provider / Repository | `BannedUserRepository` (需人工確認) | 查詢封禁表 |
| 5 | Service | 密碼比對雜湊（例如 `Hash.Verify`） | 驗證密碼 |
| 6 | Controller | 成功時 return `authkey` | 回傳 response |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `member.gameusers` | Read (`SELECT ... WHERE email = ? AND status = 1`) | 查詢啟用帳號 |
| DB (Cassandra) | `member.gameusers_banned` | Read (`SELECT ... WHERE authkey = ?`) | 檢查是否被封禁 |
| Redis | 無 | – | 登入流程未直接使用 Redis |
| Queue | 無 | – | – |

---

## 6. 重要規則

- **不可回傳欄位**：`password` 在任何 API 回傳中都不可出現；`authkey` 僅於登入成功時回傳一次。
- **狀態過濾**：僅 `status = 1` 的帳號可登入；查詢時必須帶此條件。
- **封禁檢查**：每次登入必須查詢 `gameusers_banned`，並依據 `endtime` 判斷封禁是否仍有效 (`endtime` 為空表示永久封禁，大於當前時間表示尚未解封)。
- **密碼儲存**：儲存與比對皆使用雜湊值，不可明文比對。
- **錯誤訊息**：為防止帳號列舉，錯誤回應不應區分「帳號不存在」與「密碼錯誤」，建議統一使用「帳號或密碼錯誤」。
- **速率限制**：需人工確認是否有登入嘗試次數限制（API 層或 Middleware 可能實作）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| email 不存在 | 回傳「帳號或密碼錯誤」 |
| email 存在但 `status = 0`（停用） | 回傳「帳號已停用」或「帳號或密碼錯誤」 |
| 密碼比對失敗 | 回傳「帳號或密碼錯誤」 |
| 帳號已被封禁（`endtime` 有效） | 回傳「帳號已停用」或類似封禁訊息 |
| 帳號曾被封禁但 `endtime` 已過期 | 視為未被封禁，正常登入 |
| `gameusers` 查詢時 Cassandra 逾時 | 回傳系統錯誤（5xx） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | API Test | 有效 email 與正確密碼 | 200, 回傳 authkey |
| T2 | API Test | 錯誤 email | 401 或 400，訊息不可洩漏存在性 |
| T3 | API Test | 正確 email 但錯誤密碼 | 401 或 400，與 T2 回應一致 |
| T4 | API Test | status = 0 的帳號 | 401 或 400 |
| T5 | API Test | 被封禁且未過期的帳號 | 403 或 401 |
| T6 | API Test | 封禁記錄存在但 endtime 已過期 | 登入成功 |
| T7 | Integration Test | 模擬 Cassandra 不可用 | 5xx 錯誤 |
| T8 | Permission Test | 登入成功後取得 authkey | authkey 可於後續請求中作為驗證 token |
| T9 | Security Test | 回傳內容檢查 | 確認 response 不含 password 欄位 |

---

## 9. 高風險區域

- **密碼比對**：雜湊比對邏輯若未正確實作，可能導致繞過驗證；需使用標準 BCrypt 或 PBKDF2。
- **二級索引查詢**：`gameusers` 表對 `email` 使用二級索引，在高流量下可能導致 Cassandra 節點負載升高；需評估是否需要更高效查詢方式（例如另建表以 email 為 partition key）。
- **封禁判斷時序**：`gameusers_banned.endtime` 為字串格式，比較時需確保時區一致，否則可能錯誤允取已封禁帳號登入。
- **不可逆回傳**：`password` 雜湊值即便在內部 log 中也不應出現，避免誤輸出。

---

## 10. 常見錯誤

- ❌ 查詢 `gameusers` 時未加上 `status = 1` 條件，導致停用帳號仍可登入。
- ❌ 忘記檢查 `gameusers_banned`，導致被封禁使用者可直接登入。
- ❌ 在錯誤訊息中直接區分「帳號不存在」與「密碼錯誤」，提供攻擊者列舉帳號。
- ❌ 登入後回傳了 `password` 雜湊值或完整 `gameusers` 紀錄。
- ❌ 未處理 `endtime` 為空字串或 NULL 的狀況（永久封禁）。
- ❌ 直接使用明文比對密碼（如果歷史上有此問題，應檢查）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| 登入驗證規則 | `webapi/pricecentersite/pricecentersite-detail.md` - member 讀取規則 |
| 帳號狀態檢查 | `member-detail.md` - `gameusers.status` 欄位定義，登入驗證章節 |
| 封禁判斷 | `member-detail.md` - `gameusers_banned` 使用說明 |
| 密碼處理 | `member-detail.md` - `password` 不可回傳及必須雜湊 |
| DB schema | `member.md` - `gameusers`、`gameusers_banned` 結構 |
| 回傳限制 | `pricecentersite-detail.md` - 不可回傳欄位清單 |

> 以下項目 **需人工確認**：實際 Controller 類別名稱、登入 API 路徑、速率限制實作、測試腳本是否存在。