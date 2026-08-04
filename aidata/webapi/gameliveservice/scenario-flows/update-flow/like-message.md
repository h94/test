# 按讚訊息

## 1. 場景目的
使用者對聊天室中的特定訊息進行按讚，系統將按讚帳號加入訊息記錄的 `LikeAccount` 列表，並透過 SignalR 廣播按讚事件給群組內所有連線，以即時更新點讚狀態。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| SignalR Hub Method | `LikeMessage(gid, messageId)` *(推測)* | 要求對指定群組 `gid` 中的 `messageId` 進行按讚；用戶驗證透過連線內含的 `AuthKey` 進行 |

> **需人工確認**：實際 Hub 方法名稱與參數格式請參考 `ChatHub` 原始碼。

---

## 3. 流程總覽

1. 客戶端透過 SignalR 呼叫 `LikeMessage`，傳入 `gid`、`messageId` 與連線時帶有的 `AuthKey`。
2. 服務器從 `AuthKey` 解析出用戶 `Account`（參考 `GameUserInfo` 表）。
3. 驗證該 `Account` 是否具備群組參與權限（群組存在、用戶可存取該群組）。
4. 查詢 `ChatRoomHistories` 表，取得該 `messageId` 的 `GID`、`LikeAccount` 欄位，確認訊息存在且屬於該群組。
5. 檢查 `LikeAccount` 列表（JSON 字串）中是否已包含該 `Account`，若已點讚則直接回傳成功（冪等設計）或回傳重複錯誤（依實作）。
6. 若未點讚，將 `Account` 加入 `LikeAccount`，更新 `ChatRoomHistories` 對應記錄（`UPDATE` 語句）。
7. 透過 SignalR Hub 向群組 `gid` 廣播 `LikeNotification` 事件，攜帶 `messageId`、點讚帳號等資訊。
8. 回傳成功結果給請求者（可選的返回值，如最新按讚數或名單）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Hub | ChatHub.LikeMessage *(推測)* | 接收 client 呼叫，提取參數與連線身份 |
| 2 | Provider/Validator | UserProvider.GetAccountFromAuthKey | 從 `GameUserInfo` 表依據 `AuthKey` 取得 `Account` |
| 3 | Validator | GroupValidator.ValidateAccess | 確認用戶是否可存取該群組 |
| 4 | Provider | CommunityDataProvider.GetMessage | 從 `ChatRoomHistories` 讀取 `GID`、`LikeAccount` |
| 5 | Service | LikeService.ToggleLike | 檢查重複、更新 `LikeAccount` 字串 |
| 6 | Provider | CommunityDataProvider.UpdateLikeAccount | 執行 SQL `UPDATE` 更新 `LikeAccount` |
| 7 | Hub | ChatHub.BroadcastLikeEvent | 對群組內所有連線發送 `LikeNotification` |

> **需人工確認**：實際類別與方法名稱依專案結構，以上為基於命名慣例與表格欄位的推測。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `ChatRoomHistories` | Read | 取得訊息原始 `LikeAccount` 列表與 `GID` |
| DB | `ChatRoomHistories` | Update | 將 `Account` 加入 `LikeAccount` 並寫回 |
| DB | `GameUserInfo` | Read | 透過 `AuthKey` 取得使用者 `Account` |
| SignalR | Hub 群組 | Publish | 廣播 `LikeNotification` 給群組內所有連線 |

> 目前未發現 Redis 或 Kafka 明確用於此流程，若有快取訊息記錄則需額外處理緩存一致性（**需人工確認**）。

---

## 6. 重要規則

- **權限限制**：僅允許已加入該群組並持有有效 `AuthKey` 的使用者進行按讚（需驗證 `GameUserInfo` 及群組規則）。
- **不可重複按讚**：一個帳號對同一訊息僅能按讚一次，更新前需檢查 `LikeAccount` JSON 列表中是否已存在該帳號。
- **不可修改他人訊息**：僅能對訊息進行點讚，不能修改訊息內容或 `LikeAccount` 以外的欄位。
- **冪等性**：若偵測到重複按讚，建議直接回傳成功（或已存在狀態），避免拋錯。
- **Transaction 規則**：無跨表更新需求，單一 `UPDATE` 即可，但為防止並發覆蓋，建議使用 `WHERE` 條件帶上舊的 `LikeAccount` 值（樂觀鎖）或於應用層加上適當鎖定。
- **廣播可靠性**：SignalR 廣播可能因連線中斷丟失，但不影響 DB 狀態；若有嚴格需求，可考慮訊息佇列重試機制（目前未見實現，**需人工確認**）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 訊息 ID 不存在 | 回傳錯誤，提示訊息不存在 |
| `AuthKey` 無效或找不到對應使用者 | 回傳未授權錯誤 |
| 使用者不在該群組 | 回傳權限不足錯誤 |
| `LikeAccount` JSON 反序列化失敗 | 回傳伺服器錯誤，並記錄例外狀況 |
| DB 更新失敗 (timeout/lock) | 回傳伺服器錯誤，建議客戶端重試 |
| 重複按讚 (已存在於列表中) | 根據設計回傳成功或特定重複錯誤；不可重複備份 |
| SignalR 廣播失敗 | 本機端資料庫已更新，但客戶端未收到通知，下一輪查詢或重連後需能獲得正確點讚數 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| LK-001 | API Test | 正常按讚，`LikeAccount` 列表從空變為包含指定帳號 | DB 更新成功，SignalR 收到正確通知 |
| LK-002 | API Test | 同一帳號對同一訊息重複按讚 | 按設計返回成功（不重複寫入）或對應錯誤 |
| LK-003 | Flow Test | 多帳號同時對同一訊息按讚 | 最終 `LikeAccount` 列表包含所有帳號，無遺漏、無覆蓋 |
| LK-004 | Permission Test | 未登入或過期 `AuthKey` 呼叫 | 返回未授權錯誤 |
| LK-005 | API Test | 對不存在的 `messageId` 按讚 | 返回訊息不存在錯誤 |
| LK-006 | Integration Test | DB 暫時不可用 | 返回伺服器錯誤，不崩潰 |

---

## 9. 高風險區域

- **高風險 table**：`ChatRoomHistories`（`LikeAccount` 字段直接寫入，並發更新可能導致遺失按讚）。
- **快取一致性**：若前端或中間層快取了訊息資料，`LikeAccount` 更新後需確保快取失效或同步（現階段未見快取，**需人工確認**）。
- **並發控制**：無明確的樂觀鎖或悲觀鎖機制，多用戶同時按讚可能互相覆蓋。
- **SignalR 廣播可靠性**：無持久化重送機制，可能導致部分客戶端未即時更新，需前端配合輪詢或重新獲取資料補救。

---

## 10. 常見錯誤

- 未驗證使用者權限，直接允許按讚，導致非群組成員可修改資料。
- 忽略重複按讚的檢查，導致 `LikeAccount` 列表包含重複帳號。
- 更新 `LikeAccount` 時完全覆蓋原值，未在應用層或數據庫層做並發控制。
- 廣播事件時未正確使用群組名稱（`gid`），導致事件發送至錯誤群組。
- 序列化/反序列化 `LikeAccount` 時使用不可靠的方法，可能破壞 JSON 格式。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB Table | `ChatRoomHistories` 表中 `LikeAccount` 欄位，語義為「按讚帳號列表 (JSON 序列化字串)」（來自 `CommunityDataProvider.cs`） |
| DB Table | `GameUserInfo` 表中 `Authkey` 與 `Account` 欄位，用於身份映射（來自 `GameUserInfo` 定義） |
| 功能說明 | README 中「支援回覆、按讚及頭像顯示」指出系統包含按讚功能 |
| 即時通訊 | README 中提及使用 SignalR 提供群組內訊息收發，強烈暗示按讚事件會透過 SignalR 廣播 |
| API 定義 | **需人工確認** – 本文件未包含具體 Hub 方法定義與程式碼，請參考 `ChatHub.cs` 與相關 Service/Provider |

> 部分流程（如權限校驗、重複檢查精確邏輯）僅根據常見實作推測，已標注需人工確認處。