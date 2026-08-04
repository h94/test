# 查詢聊天歷史

## 1. 場景目的
查詢指定社群群組的歷史聊天訊息，支援依時間範圍篩選，回傳訊息內容、發送者資訊（帳號、名稱、頭像、等級）、訊息類型及按讚狀態，供前端渲染聊天記錄。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/Community/{groupId}/History` | 查詢群組聊天歷史，可帶 `startTime` 與 `endTime` 參數（Unix 毫秒時間戳） |

> **需人工確認**：實際路由、參數名稱與分頁機制需依 Controller 程式碼確認。

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，附帶 AuthKey（於 Header 或 Query）與群組 ID、時間範圍。
2. 驗證 AuthKey 有效性，取得目前使用者資訊（Account、UserName、HeadShotPath 等）。
3. 查詢目標群組 `Community_Groups`，確認群組存在且 `Enabled = 1`。
4. 查詢 `ChatRoomHistories` 資料表，條件：`GID = {groupId}` 且 `AddTime` 於指定區間內，依 `AddTime` 遞增排序。
5. 將訊息清單轉換為 DTO，包含：訊息 ID、內容、類型、發送者帳號、名稱、頭像、等級、回覆訊息 ID、按讚帳號列表（並判斷目前使用者是否已按讚）。
6. 回傳歷史訊息列表。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `CommunityController.GetHistory`（未確認） | 接收請求，呼叫 Service |
| 2 | Validator | `HistoryRequestValidator`（未確認） | 驗證參數必填、時間格式 |
| 3 | Service | `CommunityService.GetChatHistory`（未確認） | 組合查詢邏輯，呼叫 Provider |
| 4 | Provider | `CommunityDataProvider.GetGroup` | 查詢 `Community_Groups` 確認群組存在性 |
| 5 | Provider | `CommunityDataProvider.GetMessagesByGroupAndTime` | 查詢 `ChatRoomHistories` 資料 |
| 6 | Transfer | `ChatMessageToDtoMapper`（未確認） | 動態組合按讚狀態，轉換為 API 輸出格式 |
| 7 | Controller | 同上 | 序列化回傳 JSON |

> **需人工確認**：實際類別／方法名稱、Service/Provider 分層方式請參照原始碼。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `Community_Groups` | Read | 確認群組啟用狀態 |
| DB | `ChatRoomHistories` | Read | 查詢歷史訊息（主要資料來源） |
| Redis | 無 | – | 本案無使用快取 |
| Kafka / Queue | 無 | – | 本案為純查詢，不涉及隊列 |

> 若未來需加速查詢，可考慮為 `ChatRoomHistories` 加上 `(GID, AddTime)` 索引或分表策略。

---

## 6. 重要規則

- **權限限制**：查詢歷史訊息需有效的 `AuthKey`，但群組歷史訊息通常為公開可見（需人工確認是否限制會員專屬）。
- **時間範圍限制**：單次查詢時間跨度不得超過 N 天（需人工確認是否實施），避免大量資料拖垮資料庫。
- **不可暴露資料**：不應回傳額外的內部帳號資訊（如真實手機號等），僅回傳公開欄位。
- **按讚狀態計算**：`LikeAccount` 為 JSON 陣列，需即時判斷目前使用者是否包含於該陣列，並回傳 `isLiked` 布林值，不得只回傳原始陣列給前端。
- **排序規則**：訊息務必依 `AddTime` 升冪排列，確保前端顯示順序正確。
- **分頁**（若有）：應支援 `offset` 與 `limit` 參數，避免單次載入過多訊息。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 未帶 AuthKey 或 AuthKey 無效 | 回傳 401 Unauthorized |
| 群組 ID 不存在 | 回傳 404 Not Found 或空陣列（需人工確認） |
| 群組已停用 (`Enabled=0`) | 回傳 403 Forbidden 或 404（需人工確認） |
| 查詢時間參數格式錯誤（非合法 Unix 毫秒） | 回傳 400 Bad Request，說明格式錯誤 |
| 資料庫查詢逾時 | 回傳 500 Internal Server Error，後端記錄例外 |
| 時間範圍內無訊息 | 回傳 200 OK，空陣列 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| CH-01 | API Test | 正常查詢，提供有效群組 ID 與時間範圍 | 200，回傳訊息清單，按時間遞增排序，包含正確發送者資訊與按讚狀態 |
| CH-02 | Permission Test | 未帶 AuthKey | 401 |
| CH-03 | Param Test | 時間格式錯誤 | 400，錯誤訊息提示格式 |
| CH-04 | DB State Test | 群組停用 | 403 或 404（依實作） |
| CH-05 | Flow Test | 查詢無訊息區間 | 200，空陣列 |
| CH-06 | Flow Test | 多筆訊息，部分已按讚 | 驗證 `isLiked` 僅對目前使用者按讚的項目為 `true` |
| CH-07 | Performance Test | 查詢跨月大量資料（若無分頁） | 應有分頁或時間跨度限制 |

---

## 9. 高風險區域

- **高風險 table**：`ChatRoomHistories`，若查詢無時間索引可能發生 full scan，影響效能。
- **高風險 API**：此歷史查詢若被頻繁呼叫（如每次進入聊天室都載入大量歷史），需考慮快取或分頁。
- **Cache consistency**：無，本場景無快取，後續若引入 Redis 需考慮當新訊息寫入時快取失效策略。
- **Idempotency**：本查詢為冪等 GET 請求，無修改操作，無需要特別防呆。

---

## 10. 常見錯誤

- **新人容易犯錯**：忘記在 SQL 查詢加上 `AddTime` 索引或時間範圍條件，導致慢查詢。
- **AI 容易誤解**：誤解 `LikeAccount` 只是一個字串，實際為 JSON 陣列，處理時須 parse。
- **常見漏檢查項目**：未檢查群組是否啟用，導致已停用群組的歷史訊息仍可被查詢。
- **常見錯誤流程**：將當前使用者按讚狀態以靜態方式回傳，應即時比對；或未對 `ChatType=image` 等特殊訊息進行內容轉換，導致前端無法正確顯示圖片訊息。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB Table | `ChatRoomHistories` 欄位定義：Message, LikeAccount, Account, UserName, HeadShotPath, Rank, AddTime, ChatType |
| DB Table | `Community_Groups` 欄位定義：Enabled |
| Provider Code | `CommunityDataProvider.cs`（負責讀取 ChatRoomHistories 與 Community_Groups） |
| 系統概述 | README：即時聊天室 - 訊息歷史存檔並提供查詢 |
| 使用者驗證 | 需 AuthKey，來源 GameUserInfo table，但此場景細節需人工確認 |