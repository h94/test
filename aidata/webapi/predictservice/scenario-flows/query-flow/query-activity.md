# 查询特殊活动记录与得奖

## 1. 场景目的

使用者查詢自己在特定站點（site）與活動（activityEvent）中的參與記錄，或者查詢某個活動週期（cid）的得獎帳號清單。此為前台用戶與後台管理員的唯讀查詢流程。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/special/records/{site}/{activityEvent}/{account}` | 查詢帳號活動記錄 |
| GET | `/api/v1/special/winners/{site}/{activityEvent}/{cid}` | 查詢周期得獎帳號 |

兩者皆為需要驗證的 API。

---

## 3. 流程總覽

### 查詢活動記錄
1. 接收包含 `site`、`activityEvent`、`account` 的 GET 請求。
2. 透過 ECFramework 驗證請求者身份（JWT / Token）。
3. 核對請求中的 `account` 參數是否屬於當前登入用戶（若非本人或管理員則拒絕）。
4. 查詢 Cassandra `predict.activities_record` 表，以 `site`、`activityEvent`、`account` 為複合主鍵。
5. 回傳活動記錄（`restday`、`winbets` 等），過濾敏感性資料。
6. 若無記錄則回傳空集合或明確的 404。

### 查詢周期得獎帳號
1. 接收包含 `site`、`activityEvent`、`cid` 的 GET 請求。
2. 驗證請求者身份。
3. 查詢 Cassandra `predict.activities_winneraccounts` 表，條件為 `site`、`activityEvent`、`cid`，並以 `rank` 排序。
4. 對外回傳時，對 `account` 欄位進行脫敏處理（如遮蔽後四碼），不可直接回傳帳號全名。
5. 回傳脫敏後的排行榜清單。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `SpecialController.GetRecords` | 接收參數，轉發請求 |
| 2 | Service | `SpecialService.GetActivityRecordAsync` | 驗證請求者權限，核對帳號歸屬 |
| 3 | Provider | `PredictDataProvider.GetRecord` | 組裝 Cassandra 查詢條件 |
| 4 | DB | `predict.activities_record` | Read：`WHERE site=X AND eventname=Y AND account=Z` |
| 5 | Service | `SpecialService.FilterSensitiveData` | 移除敏感欄位（如 `winbets` 對非本人查詢） |
| 6 | Controller | `SpecialController` | 序列化回傳 DTO |
| 7 | Controller | `SpecialController.GetWinners` | 接收參數 |
| 8 | Service | `SpecialService.GetWinnersAsync` | 驗證權限，呼叫 Provider |
| 9 | Provider | `PredictDataProvider.GetWinners` | Cassandra 查詢依 `site`、`activityEvent`、`cid` |
| 10 | DB | `predict.activities_winneraccounts` | Read：WHERE 條件，Order by `rank` |
| 11 | Service | `SpecialService.AnonymizeAccounts` | 對 `account` 脫敏 |
| 12 | Controller | `SpecialController` | 回傳結果 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.activities_record` | Read | 查詢用戶活動記錄（參與天數、獲勝注單） |
| DB | `predict.activities_winneraccounts` | Read | 查詢活動週期獲獎者清單與排名 |
| Cache | Redis（predict:activity:*） | GET | 從快取讀取活動相關資料（若有快取層） |
| Queue | N/A | N/A | 無佇列操作 |

---

## 6. 重要規則

- **權限限制**：
  - 查詢活動記錄時，僅允許用戶查詢自己的記錄（`account` 必須與 Token 相符），或具有管理員權限的帳號可查詢他人。
- **欄位限制**：
  - `activities_record.winbets`：非本人查詢時，不可回傳此欄位，避免暴露中獎注單資訊。
  - `activities_winneraccounts.account`：對外 API 必須進行脫敏（遮罩處理），不可暴露完整帳號。
- **不可暴露資料**：
  - 任何情況下皆不可回傳 `gameusers.password`、`email` 等欄位（即使有查詢關聯會員資訊的需求）。
- **TTL 規則**：
  - 若有使用 Redis 快取（如 `predict:activity_record:{site}:{eventname}:{account}`），TTL 建議設置為活動剩餘時間加 1 小時，避免活動結束後仍提供過期快取。
- **狀態值限制**：
  - 無特殊狀態值依賴。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求 `account` 與登入 Token 不符且非管理員 | 回傳 403 Forbidden 或權限不足 |
| 查詢不存在的活動記錄 | 回傳 200 OK 搭配空陣列（或 404，依業務習慣） |
| 活動週期 `cid` 不存在 | 回傳 200 OK 搭配空陣列 |
| 直接回傳原始 `activities_winneraccounts` 資料 | 錯誤：必須對 `account` 進行脫敏後回傳 |
| Redis 快取命中未脫敏的 `account` 資料 | 錯誤：快取寫入前應先脫敏，或讀取後在 Service 層脫敏 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| UT-SR-01 | Permission Test | 使用者 A 查詢使用者 B 的活動記錄 | 403 Forbidden |
| UT-SR-02 | Permission Test | 管理員查詢使用者 B 的活動記錄 | 200 OK，回傳完整記錄（含 winbets） |
| UT-SR-03 | API Test | 查詢存在的活動記錄 | 200 OK，回傳 `restday`、`updatedate`、`winbets`（若本人） |
| UT-SW-01 | API Test | 查詢周期得獎帳號 | 200 OK，回傳清單，且 `account` 欄位為 `***` 格式 |
| UT-SW-02 | Data Test | 查詢獲獎者排名順序 | 回傳清單應以 `rank` 升冪排序 |

---

## 9. 高風險區域

- **高風險 table**：
  - `activities_winneraccounts`：若未脫敏直接回傳，屬於個資外洩的高風險行為。
- **高風險 API**：
  - `GET /api/v1/special/winners/{site}/{activityEvent}/{cid}`：任何未登入或登入用戶皆可能嘗試查詢，需確保脫敏邏輯強制執行。
- **Cache consistency**：
  - 若快取了脫敏後的得獎清單，當活動結算更新排名時，需確保相關快取被清除，否則前端可能顯示舊排名。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 忘記對 `activities_winneraccounts.account` 做脫敏處理。
- **AI 容易誤解**：
  - 誤以為 `activities_record` 和 `activities_winneraccounts` 在同一個 API 中混合回傳。
- **常見漏檢查項目**：
  - 查詢活動記錄時未驗證 `account` 歸屬權。
  - 回傳時包含了內部使用的 `winbets` 列表給他人。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `SpecialController.GetRecords` / `SpecialController.GetWinners` (README / OpenAPI) |
| DB | `predict.activities_record` / `predict.activities_winneraccounts` (DB Schema / DB detail) |
| DTO/Filter | `SpecialService.AnonymizeAccounts` (需人工確認具體實作位置，Service Layer) |
| 權限規範 | `predictservice-detail.md` -> 不可回傳欄位 -> `activities_winneraccounts.account` |
| 脫敏規則 | `predict-detail.md` / `predictservice-detail.md` -> 公開 API 不可暴露 `account` 全名 |

---

## 建議新增文件

- **DB 使用規則強化**：建議在 `predict-detail.md` 明確標註 `activities_record` 表的 `winbets` 欄位用於 API 回傳時的過濾規則。
- **測試腳本**：建議為 `/winners` API 添加自動化迴歸測試腳本，專門驗證 `account` 欄位是否為脫敏格式（正則表達式校驗）。
- **API 文件補充**：建議在 OpenAPI 定義中為 `/special/winners` 的回傳物件增加 description，明確指出 `account` 為脫敏值。