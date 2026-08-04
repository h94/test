# 設定黑名單帳號

## 1. 場景目的

允許使用者將指定帳號加入黑名單，避免該帳號的內容出現在社群文章或預測列表。**與關注清單（focus_account）互斥**：同一帳號不得同時存在於黑名單與關注清單。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/GameUser/SetGameUserBlackAccount`（需人工確認實際路由） | 依據 `gameusers.black_account` 專屬 API 規則推測 |

相關介面命名來自 DB 操作邊界文件，實際路由與參數規格仍需人工對照 OpenAPI。

---

## 3. 流程總覽

1. 接收請求，提取操作者 `authKey`（或 token→authKey）與目標帳號 `targetAccount`
2. 驗證操作者是否存在且狀態正常（`status=1` 且未封禁）
3. 檢查目標帳號是否為有效帳號（存在且 `status=1`）
4. 讀取操作者的 `gameusers.black_account` 與 `focus_account`
5. 驗證互斥：若目標帳號已在 `focus_account` 中，**先將其移除**，再執行後續新增
6. 若目標帳號已在 `black_account` 中，則視為重複操作（可能直接回傳成功或忽略）
7. 將目標帳號附加到 `black_account` list（不可覆蓋整個 list）
8. 寫回 `gameusers` 並回傳成功

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GameUserController.SetGameUserBlackAccount` | 解析請求參數，呼叫 Service |
| 2 | Service | `GameUserService.SetBlackAccount` | 組合驗證、互斥邏輯、寫入操作 |
| 3 | Provider | `GameUserDataProvider` (或對應 Cassandra Provider) | 讀取 `gameusers` 並使用 Cassandra list append 更新 `black_account` |
| 4 | Validator | （內建於 Service／Provider） | 檢查帳號存在性、狀態、互斥規則 |

> ⚠️ 實際 class 名稱與方法需人工確認程式碼。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `member.gameusers` | Read | 查詢操作者與目標帳號資料（status, authkey, black_account, focus_account） |
| DB | `member.gameusers` | Write（Append） | 將目標帳號附加至 `black_account` list；若有互斥則需先移除 `focus_account` 中對應項目 |
| DB | `member.gameusers_banned` | Read（可能） | 確認目標帳號未被永久封禁（若系統需要） |
| Redis | — | 無直接操作 | 此場景無需操作快取；若後續其他服務快取使用者資料，需考慮失效，但本服務不負責 |

**重要限制**：不可直接覆蓋整個 `black_account` list；僅可透過專屬 API 新增/移除個別元素。

---

## 6. 重要規則

- **互斥規則**：`black_account` 與 `focus_account` 不可同時包含同一帳號。若目標已存在於 `focus_account`，必須先移除再新增至黑名單（或直接拒絕，依商業邏輯決定）。
- **不可直接覆蓋**：操作 `black_account` 時必須使用 list append／remove 元素，禁止直接 `UPDATE ... SET black_account = [...]` 覆蓋整個 list。
- **權限限制**：僅操作者本人可修改自己的黑名單（authKey 驗證）。
- **目標帳號存在性**：目標帳號必須存在且狀態為啟用（`status=1`）；已停用或被封禁的帳號可選擇是否允許加入黑名單，需人工確認。
- **不可回傳敏感欄位**：在回傳操作結果時，不可暴露 `password`、`authkey` 等欄位。
- **list 長度限制**：建議限制黑名單最大長度（如 1000），避免 Cassandra 大 list 效能問題（依既有規範）。
- **冪等性**：同一帳號重複加入黑名單應視為成功（不重複寫入相同元素），或回傳已存在。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 操作者 authKey 無效或狀態非啟用 | 回傳認證失敗（401／403） |
| 目標帳號不存在 | 回傳參數錯誤（目標帳號無效） |
| 目標帳號已在黑名單中 | 直接回傳成功（或冪等處理） |
| 目標帳號存在於 `focus_account` 中 | 依規則先移除關注再加入黑名單（或拒絕）；若移除失敗則回傳錯誤 |
| Cassandra 寫入失敗（如 timeout） | 回傳伺服器錯誤；記錄 log |
| 嘗試覆蓋整個 list（非合規呼叫） | 系統應阻止此操作（透過 Provider 強制使用 append） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| BL-01 | API Test | 正常新增黑名單 | 200，`black_account` 含目標帳號 |
| BL-02 | Permission Test | 使用無效 authKey | 403／401 |
| BL-03 | Flow Test | 目標帳號原本在 `focus_account` 中 | 互斥處理後 `black_account` 新增成功，`focus_account` 移除目標 |
| BL-04 | Flow Test | 重複新增同一目標 | `black_account` 不重複（元素僅出現一次） |
| BL-05 | API Test | 嘗試透過直接修改 list 的 API 覆蓋整個 `black_account` | 拒絕或僅 append 元素，不覆蓋 |
| BL-06 | Integration Test | Cassandra 模擬延遲或失敗 | 服務回傳適當錯誤碼與訊息 |

---

## 9. 高風險區域

- **互斥邏輯遺漏**：若未正確處理 `focus_account` 移除，可能導致資料不一致（同一個帳號同時在兩個 list）。
- **list 直接覆蓋風險**：若開發人員誤用一般 UPDATE 語句覆蓋整個 list，會遺失其他服務或過去操作所新增的元素，且可能造成互斥檢查失效。
- **目標帳號狀態變更時序問題**：若目標帳號在操作進行中被停用或刪除，雖可能性低，但仍需考慮最終一致性。
- **權限繞過**：需確保 API 僅能調整自己的黑名單，不可修改他人。

---

## 10. 常見錯誤

- ❌ 使用 `SET black_account = [...]` 直接覆蓋整個 list → 應使用 `black_account = black_account + ['目標帳號']`（Cassandra append）。
- ❌ 未檢查互斥就寫入，導致同一帳號同時出現在 `black_account` 與 `focus_account`。
- ❌ 未驗證操作者身份或目標帳號有效性（直接將任意字串塞入 list）。
- ❌ 未限制 list 最大長度，可能因大量黑名單導致資料列過大、讀取部分分割時斷裂。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB | member.gameusers |
| 規則（互斥） | db/member-detail.md：「black_account 與 focus_account 互斥（不可同時存在同一帳號）」 |
| 寫入限制 | pricecentersite-detail.md：「gameusers.focus_account / follow_account / black_account：僅透過專屬 API（InsertGameUserFocusAccount/SetGameUserBlackAccount）新增/移除元素；不可直接覆寫整個 list」 |
| API 名稱推測 | pricecentersite-detail.md 提及 `SetGameUserBlackAccount` 專屬 API |
| 服務權限 | pricecentersite 角色為 reader／writer，對 member keyspace 有寫入權限 |

> ⚠️ 缺少實際程式碼證據，建議人工確認 Controller 與 Service 方法名稱、路由、精確互斥處理邏輯（移除或拒絕）後更新。