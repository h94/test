# 新增關注帳號

## 1. 場景目的

提供已驗證使用者透過專屬 API，將指定目標帳號加入個人 `gameusers.focus_account` 清單（關注清單）。此流程嚴禁直接覆寫整個 list，必須透過「新增元素」邏輯操作 Cassandrara list。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/GameUser/InsertGameUserFocusAccount` | 需傳入 authKey 與目標 account |

---

## 3. 流程總覽

1. 接收 API 請求，從 query 或 body 取得 authKey 與欲關注的目標帳號 (focusAccount)。
2. 透過 authKey 查詢 `member.gameusers` 驗證請求者身份與狀態（status=1）。
3. 驗證目標帳號是否存在且狀態正常（status=1）。
4. 檢查目標帳號是否已在請求者的 `focus_account` 清單中（避免重複）。
5. 檢查目標帳號是否已被請求者加入 `black_account`（互斥限制，**需人工確認**）。
6. 使用 Cassandra list append 操作，將目標帳號加入請求者的 `focus_account`。
7. 回傳操作成功結果（不含敏感欄位，如 authKey、password）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GameUserController.InsertGameUserFocusAccount` | 接收 `authKey` 與 `focusAccount` 參數，轉發 Service |
| 2 | Service | `GameUserService.InsertGameUserFocusAccount` | 執行帳號驗證、清單互斥檢查與寫入邏輯 |
| 3 | Provider | `MemberProvider`（推測） | 讀取 `member.gameusers`，取得請求者與目標帳號資料 |
| 4 | Provider | `MemberProvider`（推測） | 進行 Cassandrara `UPDATE ... SET focus_account = focus_account + ['target']` 操作 |
| 5 | Provider | 無 Redis 快取清理邏輯 | 若快取存在，建議失效 `GameUser:{authKey}`（**需人工確認**） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `member.gameusers` | Read | 驗證請求者 (`authKey`) 狀態、取得現有 `focus_account` 與 `black_account` |
| DB | `member.gameusers` | Read | 確認目標帳號 (`account`) 存在且 status=1（透過 `account` 查詢，**需人工確認**是否為 `account` 次級索引） |
| DB | `member.gameusers` | Write | Append 目標 `account` 至 `focus_account` list |
| Redis | 無明確 Key | — | 若使用者資料有快取，需失效相關 key（文件未明確定義此場景快取清理） |

---

## 6. 重要規則

- **權限限制**：必須提供有效的 `authKey`，且該 `authKey` 對應的 `gameusers.status` 必須為 `1`（已啟用）。
- **欄位限制**：`focus_account` 僅可新增，不可透過此 API 刪除或整筆覆寫。
- **不可暴露資料**：API 回應不可包含 `password`、`authkey`、目標帳號的 `email` 等敏感欄位。`black_account` 清單亦不應在回應中完整回傳。
- **TTL 規則**：DB 操作無 TTL。若後續加入 Redis 快取，更新後應主動失效（推測保留 `member-detail.md` 提及的快取慣例：5~10 分鐘）。
- **Transaction 規則**：當前無跨表交易需求。Cassandra list append 操作本身具備原子性，但與「檢查後寫入」之間存在競爭條件，必要時應使用 LWT（**需人工確認**）。
- **狀態值限制**：請求者與目標帳號的 `status` 皆必須為 `1`。
- **不可修改欄位**：無。此 API 僅操作 `focus_account` list。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求者 `authKey` 不存在 | 回傳驗證失敗或無此使用者錯誤 |
| 請求者 `status != 1`（停用、凍結） | 回傳權限不足或帳號已停用錯誤 |
| 目標 `account` 不存在 | 回傳目標帳號不存在或無效錯誤 |
| 目標 `account` 已在 `focus_account` 清單中 | 回傳重複關注錯誤（HTTP 409 或明確業務錯誤碼） |
| 目標 `account` 已在 `black_account` 清單中 | 回傳業務邏輯衝突錯誤（不可同時關注與封鎖） |
| Cassandra 寫入失敗 | 回傳服務暫不可用錯誤，不寫入部分記錄 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| IT-01 | Integration Test | 正常新增一個尚未在清單中的目標帳號 | `focus_account` 更新，回傳成功 |
| IT-02 | API Test | 重複呼叫同一 target | 第二次回傳錯誤（已關注） |
| IT-03 | Permission Test | 使用 `status=0` 的 authKey | 回傳 401/403 |
| IT-04 | Flow Test | 目標帳號已被請求者封鎖 | 回傳業務衝突錯誤 |
| IT-05 | API Test | 目標帳號不存在 | 回傳目標不存在錯誤 |

---

## 9. 高風險區域

- **高風險 table**：`member.gameusers` — `focus_account` 與 `black_account` 直接關聯社交關係與內容過濾。
- **高風險 API**：`InsertGameUserFocusAccount` — 若無互斥檢查，可能導致已封鎖使用者內容重新曝光。
- **跨服務資料同步**：無。但其他服務（如社群文章過濾）會讀取 `focus_account`，寫入錯誤將直接影響內容顯示。
- **Transaction**：Cassandra 的 read-before-write 流程若無 LWT，在高併發下可能產生重複寫入或狀態不一致。
- **Cache consistency**：若存在 `GameUser` 快取，寫入後未失效將使前端顯示過期清單。
- **Idempotency**：無自然等冪性，重複請求會產生錯誤（非靜默成功），需由客戶端處理。

---

## 10. 常見錯誤

- **新人容易犯錯**：直接以 `SET focus_account = ['target']` 取代 append 操作，導致原有清單遺失。
- **AI 容易誤解**：認為 `focus_account` 是普通 text 欄位，實為 Cassandrara `list<text>`，必須使用 `list` 專屬語法操作。
- **常見漏檢查項目**：忘記檢查目標帳號的 `status` 是否為 `1`，讓使用者可關注已停用或被凍結的幽靈帳號。
- **常見錯誤流程**：未檢查 `black_account` 互斥性，直接寫入 `focus_account`，違反業務規則。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `GameUserController.InsertGameUserFocusAccount`（OpenAPI 路徑推測 `/api/GameUser/InsertGameUserFocusAccount`） |
| DB | `member.gameusers` (schema: `focus_account list<text>`) |
| Code | `GameUserService.InsertGameUserFocusAccount`（流程主控） |
| SQL | `SELECT * FROM member.gameusers WHERE authkey = ?`；`UPDATE member.gameusers SET focus_account = focus_account + ['target'] WHERE authkey = ?` |
| 規則 | `pricecentersite-detail.md`：`focus_account` 僅可透過專屬 API 新增/移除元素，不可直接覆寫整個 list |