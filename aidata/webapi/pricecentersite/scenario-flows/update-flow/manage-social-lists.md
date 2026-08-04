# 管理社交清單 (新增/移除個別元素)

## 1. 場景目的

允許使用者透過專用 API 對 `gameusers` 資料表中的 `focus_account`、`black_account`、`follow_account` 清單進行**新增或移除單一元素**的操作，嚴禁直接覆寫整個 list，以確保多請求併發時的資料安全性。

---

## 2. 入口 API

**需人工確認**：OpenAPI 文件中未明確提供「管理社交清單」專屬端點。推測為以下路徑，需與開發團隊確認。

| Method | Path | 說明 |
|---|---|---|
| POST | /api/GameUser/InsertFocusAccount | 新增關注帳號 |
| POST | /api/GameUser/RemoveFocusAccount | 移除關注帳號 |
| POST | /api/GameUser/SetBlackAccount | 新增黑名單帳號 |
| POST | /api/GameUser/RemoveBlackAccount | 移除黑名單帳號 |
| POST | /api/GameUser/InsertFollowAccount | 新增追蹤帳號 |
| POST | /api/GameUser/RemoveFollowAccount | 移除追蹤帳號 |

---

## 3. 流程總覽

1. 接收帶有 `authKey` 的 API 請求，包含目標帳號。
2. 驗證 `authKey` 有效性並查詢 `member.gameusers` 取得當前使用者資料。
3. 檢查目標帳號是否存在（必要時查詢 `member.gameusers`）。
4. 根據操作類型（新增/移除），對特定清單欄位進行原子操作（append/remove）。
5. 將更新後的資料寫入 `member.gameusers`。
6. 回傳操作結果。

---

## 4. 程式流程

**需人工確認**：以下為符合最佳實踐的推測，實際 Controller/Service 路徑需審查程式碼確認。

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GameUserController` | 接收 request，驗證參數 |
| 2 | Provider | `GameUserDataProvider` | 查詢 `gameusers` 取得當前使用者資料 |
| 3 | Validator | - | 驗證目標帳號是否存在 |
| 4 | Service | `GameUserService` | 判斷操作類型，調用 Provider 更新 |
| 5 | Provider | `GameUserDataProvider` | 對 `focus_account` 等使用 Cassandra list append/remove |
| 6 | Controller | `GameUserController` | 回傳成功訊息 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `member.gameusers` | Read | 讀取當前使用者清單以確認操作前狀態 |
| DB | `member.gameusers` | Update | 對 `focus_account`, `black_account`, `follow_account` 進行原子新增或移除元素 |
| Cache | Redis `GameUser:{authkey}` | DELETE | 更新 DB 後，必須使快取失效，確保下次讀取為最新資料 |

---

## 6. 重要規則

- **不可直接覆寫整個 list**：必須使用 Cassandra list 的「append」或「remove」操作，不得先讀取整個 list 修改後再 SET。
  - *Evidence: `pricecentersite-detail.md` - gameusers.focus_account / follow_account / black_account 僅透過專屬 API 新增/移除元素；不可直接覆寫整個 list*
- **互斥規則**：`black_account` 與 `focus_account` 不應同時存在同一帳號。
  - *Evidence: `member-detail.md` - black_account 與 focus_account 互斥（不可同時存在同一帳號）。* 需在寫入前檢查。
- **清單過大**：清單過大時應分頁存取，避免全表讀取影響效能。
  - *Evidence: `member-detail.md` - 清單過大時應分頁存取，避免全表讀取。*
- **權限限制**：僅 `memberservice` 和 `pricecentersite`（特定流程）有權限執行此操作。
  - *Evidence: `member-detail.md` - 寫入由 memberservice, webpservice 透過專用 API 執行；`pricecentersite` 為 reader/writer。*
- **不可回傳敏感欄位**：回傳使用者資料時，不可包含 `password`、`authkey` 等。
  - *Evidence: `member-detail.md` - 對外 API 不可回傳 password, authkey。*

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| authKey 無效或過期 | 回傳 401 Unauthorized |
| 目標帳號不存在 | 回傳錯誤：目標帳號不存在 |
| 嘗試新增已存在的帳號 | 靜默成功（idempotent）或回傳重複操作提示 |
| 嘗試移除不存在的帳號 | 靜默成功（idempotent）或回傳操作失敗提示 |
| 嘗試新增/移除時違反互斥規則（e.g., 加關注又加黑名單） | 回傳錯誤：操作衝突 |
| Cassandra 寫入失敗 | 回傳 500 Internal Server Error，記錄錯誤日誌，觸發重試機制 |
| Redis 快取刪除失敗 | 記錄警告日誌，不影響主要流程，快取將於 TTL 後自動過期 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SCL-01 | API Test | 正常新增一個關注帳號 | 200 OK，DB list append 成功 |
| SCL-02 | API Test | 正常移除一個關注帳號 | 200 OK，DB list remove 成功 |
| SCL-03 | Permission Test | 使用無效 authKey 操作 | 401 Unauthorized |
| SCL-04 | Flow Test | 重複新增同一帳號 | 200 OK (冪等)，list 中只有一個該帳號 |
| SCL-05 | Flow Test | 新增關注帳號後，檢查快取 | 下次讀取時應取得最新 list（快取已被刪除） |
| SCL-06 | Integration Test | 模擬 Cassandra 寫入時發生錯誤 | 500 Internal Server Error，操作未執行 |

---

## 9. 高風險區域

- **資料覆蓋風險**：若未使用 Cassandra list 原子操作（如先讀後寫），高併發下會導致資料被覆蓋遺失。
- **Cache consistency**：更新 DB 後必須同步失效 Redis 快取 (`GameUser:{authkey}`)，否則用戶端將看到舊資料。
  - *Evidence: `member-detail.md` - 會員資格變更（memberships、subendtime）必須主動 DEL 快取。*
- **跨服務權限**：須確保只有 pricecentersite 的特定受控 API 可執行此寫入，`predictservice` 等 reader 服務無法誤寫。
  - *Evidence: `pricecentersite-detail.md` - 僅透過專屬 API 新增/移除元素。*

---

## 10. 常見錯誤

- **新人錯誤**：直接讀取整個 list，在應用端修改後，再將整個 list 寫回 DB。這會在高併發時造成資料遺失。
- **AI 容易誤解**：可能生成直接 UPDATE `gameusers SET focus_account = ?` 的 SQL/CQL，這是被禁止的。
- **常見漏檢查項目**：更新後忘記刪除 Redis 快取，導致客戶端顯示不一致。
- **常見錯誤流程**：在新增黑名單時，未檢查該帳號是否已在關注清單中（違反互斥規則），直接 append 導致資料語意錯誤。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB write rule | pricecentersite-detail.md: gameusers.focus_account / follow_account / black_account 僅透過專屬 API 新增/移除元素；不可直接覆寫整個 list |
| DB read rule | member-detail.md: 清單過大時應分頁存取，避免全表讀取。 |
| DB list exclusion | member-detail.md: black_account 與 focus_account 互斥（不可同時存在同一帳號）。 |
| Redis cache rule | member-detail.md: 會員資格變更（memberships、subendtime）必須主動 DEL 快取。 |

## 建議新增事項

- **建議新增 API 與測試**：在 OpenAPI 中明確此場景的端點定義、request body 和 response。
- **建議新增規則**：在一份統一的「API Rules」文件中，明確禁止對 `gameusers` 表中的任何 `list` 欄位執行整體覆寫操作。