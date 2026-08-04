# 建立社群群組

## 1. 場景目的
後台管理人員透過此流程建立一個新的直播社群群組，並設定其基本資訊（如名稱、圖示、排序、所屬遊戲類型等），供前台用戶加入及使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/gamelive/communities/groups` | 建立新的直播社群群組 |

---

## 3. 流程總覽

1. 後台管理前端的 CreateGroup 請求被 `GameliveController` 接收。
2. 系統進行身份驗證 (Authentication) 與授權 (Authorization)。
3. `GameliveController` 將請求參數（DTO）轉交給 `IGameLiveService`。
4. `IGameLiveService` 實作呼叫下游微服務 `gameliveservice` 的對應 API。
5. `gameliveservice` 處理請求，產生群組 ID，並將資料寫入 MySQL 的 `community_groups` 資料表。
6. `gameliveservice` 回傳成功結果給 PriceBackendService。
7. PriceBackendService 將成功結果（可能包含新群組 ID）回傳給前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GameliveController.CreateCommunityGroup` | 接收 HTTP POST 請求與 DTO 資料 |
| 2 | Service | `GameLiveService.CreateCommunityGroup` | 轉發請求至下游 `gameliveservice` |
| 3 | Provider | `GameLiveProvider` (需人工確認) | 將請求序列化並透過 HTTP Client 呼叫下游 API |
| 4 | **External** | **`gameliveservice`** | **負責實際業務邏輯、產生 ID 並寫入資料庫** |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | MySQL `community_groups` | Write (`INSERT`) | 建立一筆新的社群群組記錄 |
| Cache | (無) | — | 此流程中未使用 Redis |
| Queue | (無) | — | 此流程中未使用 Kafka |

---

## 6. 重要規則

- **權限限制**：所有操作必須經過後台權限驗證 (Authentication required)。
- **欄位限制**：
    - `ID`：由 `gameliveservice` 自動生成，不可由前端傳入或後續修改。
    - `UpdateTime`：由 `gameliveservice` 在寫入時自動設定。
- **不可修改欄位**：`ID`、`Owner`、`GType` 等建立後不可更改（需人工確認 GType 是否可更改）。
- **狀態值限制**：`Enabled` 的初始值需確定（需人工確認初始是啟用還是停用）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求缺少必填欄位（如 `Name`） | 回傳 400 Bad Request 及驗證錯誤訊息 |
| 未攜帶有效的身份驗證 Token | 回傳 401 Unauthorized |
| 呼叫下游 `gameliveservice` 失敗（如 timeout） | 回傳 502 Bad Gateway 或 500 Internal Server Error |
| 嘗試建立重複名稱的群組（若有此限制） | 需人工確認是否有限制及對應的錯誤訊息 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| CG-01 | API Test | 以管理員身份，傳送完整的有效參數請求 | 回傳 200 OK，且資料庫中新增一筆記錄 |
| CG-02 | Permission Test | 以未經授權的使用者身份發送請求 | 回傳 401 Unauthorized |
| CG-03 | API Test | 傳送缺少 `Name` 欄位的請求 | 回傳 400 Bad Request |
| CG-04 | Integration Test | 模擬下游 `gameliveservice` 發生錯誤 | 回傳 502 或 500 錯誤 |

---

## 9. 高風險區域

- **下游服務依賴**：`pricebackendservice` 完全依賴 `gameliveservice` 來完成操作。下游服務的可用性、效能及資料一致性是主要風險。
- **ID 生成**：群組 ID 的生成邏輯在 `gameliveservice`，若其 ID 生成策略（如 UUID 或自增序號）有問題，會直接影響此功能。

---

## 10. 常見錯誤

- **新人容易犯錯**：試圖在 `pricebackendservice` 端處理複雜的商業邏輯或直接操作資料庫。應理解此服務僅為 BFF 層，所有邏輯都在下游。
- **AI 容易誤解**：為此流程生成包含 Redis 快取更新或 Kafka 事件發送的程式碼。從目前證據來看，建立群組的過程沒有這些步驟。
- **常見漏檢查項目**：請求參數驗證（如 `Name` 是否為空）、下游服務回傳的錯誤處理與轉譯。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `GameliveController.CreateCommunityGroup` (需人工確認) |
| DB | `community_groups` (see `webapi/pricebackendservice/db/sport-detail.md`) |
| Code | `GameLiveService.CreateCommunityGroup` (需人工確認) |
| Service Dependency | `gameliveservice` (see `webapi/pricebackendservice/README.md`) |