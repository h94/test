# 回覆訊息

## 1. 場景目的
在社群聊天室中針對特定訊息發送回覆，系統會記錄回覆關係（ResponseID）並將新訊息寫入資料庫，同時透過 SignalR 即時廣播給群組成員。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| SignalR | `ChatHub.SendMessage` | 客戶端透過 SignalR 呼叫，傳入群組 ID、訊息內容、訊息類型及欲回覆的訊息 ID（可選） |

---

## 3. 流程總覽

1. 客戶端透過 SignalR 呼叫 `SendMessage`，傳入 `GID`、`Message`、`ChatType` 以及可選的 `ResponseID`。
2. Hub 從連線 Context 取得 AuthKey，調用驗證服務取得 `GameUserInfo`。
3. 檢查目標群組是否存在且 `Enabled = 1`（查詢 `Community_Groups`）。
4. （可選）若 `ResponseID` 不為空，驗證該訊息存在且屬於同一群組 `GID`（**需人工確認**）。
5. 利用 GUID 產生新訊息唯一識別碼 `ID`，設定時間戳 `AddTime`。
6. 組合 `ChatRoomHistories` 紀錄：包含 `GID`、`ID`、`Message`、`ResponseID`（若無則 NULL）、`ChatType`、`Account`、`UserName`、`HeadShotPath`、`Rank` 等。
7. 透過 Provider 將訊息 INSERT 到 `ChatRoomHistories` 表。
8. 使用 `Clients.Group(GID)` 將完整訊息物件廣播給群組所有連線。
9. 前端收到訊息後根據 `ResponseID` 關聯原訊息顯示回覆結構。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Hub | `ChatHub.SendMessage` | 接收 client 參數，觸發內部服務 |
| 2 | Service | `ChatService.SendMessage` | 驗證權限、群組狀態，組合訊息物件 |
| 3 | Validator | `ChatMessageValidator` | 驗證訊息內容與類型合法性（**需人工確認具體類別**） |
| 4 | Provider | `CommunityDataProvider.InsertChatHistory` | 將訊息寫入 `ChatRoomHistories` |
| 5 | Hub | `ChatHub` 內部 `Clients.Group(GID).ReceiveMessage` | 即時廣播訊息至群組所有連線 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `Community_Groups` | Read | 確認群組存在且啟用 |
| DB | `GameUserInfo` | Read | 取得發送者顯示資訊（頭貼、名稱、等級） |
| DB | `ChatRoomHistories` | Write (INSERT) | 寫入新訊息，包含 `ResponseID` |
| DB | `ChatRoomHistories` | Read（可選） | 驗證被回覆訊息的存在性與群組歸屬（**需人工確認**） |

> 目前未發現使用 Redis 或 Message Queue 處理此流程。

---

## 6. 重要規則

- **權限限制**：必須提供有效 AuthKey，系統根據 `GameUserInfo` 確認會員身份與權限。
- **欄位限制**：
  - `ChatType` 僅允許 `text`、`image`、`predict`。
  - `ResponseID` 可為 NULL，若有值需符合 UUID 格式且與原訊息同群組（**需人工確認**）。
- **不可暴露資料**：廣播訊息不得包含 AuthKey、金鑰、機敏訂閱明細，僅傳遞 `UserName`、`HeadShotPath`、`Rank` 等顯示欄位。
- **不可修改欄位**：訊息寫入後 `ResponseID` 不可更改。
- **Transaction 規則**：寫入 DB 與 SignalR 廣播之間無交易性保證，需考量發送失敗的重試或補償機制。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 群組不存在 | 拒絕發送，回傳群組無效錯誤 |
| 群組已停用（Enabled = 0） | 拒絕發送，提示群組未啟用 |
| AuthKey 無效或過期 | 連線建立失敗或訊息發送被拒絕 |
| `ResponseID` 指定的訊息不存在 | **需人工確認**：可能無視並照常發送，或回覆錯誤 |
| `Message` 為空 | 驗證失敗，回傳內容不可為空白 |
| DB 寫入失敗（逾時或連線中斷） | 不回傳成功，客戶端可重試；未寫入前不可廣播 |
| SignalR 廣播失敗 | 訊息已寫入 DB 但未送達在線成員，需人工確認是否影響一致性 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | Integration Test | 以有效 AuthKey 發送含 `ResponseID` 的回覆訊息 | DB 新增一筆，`ResponseID` 正確，群組全員即時收到訊息 |
| T2 | Flow Test | 不帶 `ResponseID` 的一般訊息 | `ResponseID` 為 NULL，流程仍正常 |
| T3 | Permission Test | 使用無效 AuthKey 發送 | 訊息不被處理，回覆授權錯誤 |
| T4 | API Test | `ResponseID` 指向不存在之訊息 | 依照產品規則驗證成功或失敗（**需確認**） |
| T5 | Flow Test | 目標群組已被停用 | 拒絕寫入，回覆群組不可用 |
| T6 | Flow Test | 同群組多使用者同時回覆同一訊息 | 每筆皆獨立寫入，`ResponseID` 相同，廣播順序合理 |
| T7 | Reliability Test | 模擬 DB 寫入失敗後成功重試 | 最終僅有一筆紀錄，無重複或遺失 |

---

## 9. 高風險區域

- **高風險 Table**：`ChatRoomHistories`（高頻寫入，`ResponseID` 無資料庫外鍵強制約束，完全依賴應用層邏輯）。
- **高風險 API**：SignalR `SendMessage`（即時性要求高，廣播延遲或遺漏直接影響使用者體驗）。
- **Transaction 缺口**：DB 寫入與廣播非 atomic，若寫入成功但廣播失敗會導致「已儲存但未推送」，需設計重送或事件記錄。
- **Cache Consistency**：目前流程未使用快取，無一致性風險。
- **Queue Retry**：未見佇列，失敗重試必須依靠客戶端或內部邏輯，須注意冪等性。
- **Idempotency**：若客戶端因 timeout 重送相同訊息，可能產生重複紀錄（除非使用 client 端產生的 idempotency key）。

---

## 10. 常見錯誤

- 新人容易誤填 `ResponseID`，例如填入其他群組的訊息 ID，而未驗證跨群組回覆（若系統不檢查將導致顯示錯亂）。
- AI 容易將 `ResponseID` 視為必填或誤建資料庫外鍵約束，導致錯誤的資料模型建議。
- 漏檢查：未驗證被回覆訊息的存在性，使得前端顯示空引用。
- 常見錯誤流程：僅寫入 DB 但未處理廣播異常，導致訊息延遲或遺失。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB Table | `ChatRoomHistories`（定義於 `CommunityDataProvider.cs`） |
| DB Field | `ResponseID`（備註：回覆訊息的 ID，若無為 NULL，出處同上） |
| 授權檢查 | `GameUserInfo`（定義於 `GameUserInfo.cs`） |
| 群組驗證 | `Community_Groups`（定義於 `CommunityDataProvider.cs`） |
| 訊息類型限制 | `ChatRoomHistories.ChatType`（定義於 `CommunityDataProvider.cs`） |
| SignalR Hub | `ChatHub`（README 提及「透過 SignalR 提供群組內文字、圖片、預測類型的訊息收發」） |

### 需人工確認
- 回覆時是否必須驗證被回覆訊息的存在性及群組一致性。
- 具體 `Validator` 類別及規則細節。
- 廣播失敗時的重試策略或記錄方式。
- 是否對 `ResponseID` 跨群組使用有明確禁止邏輯。

### 建議新增文件
- ChatHub API 合約詳細說明（含 SignalR 方法參數與回應結構）。

### 建議新增規則
- `ResponseID` 引用完整性策略（強驗證或弱驗證）及跨群組回覆的處理方式。

### 建議新增測試情境
- 無效 `ResponseID` 的行為測試。
- 訊息廣播失敗後的前端展示與重連機制測試。