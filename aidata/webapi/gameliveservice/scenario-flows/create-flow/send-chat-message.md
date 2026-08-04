# 發送聊天訊息

## 1. 場景目的
允許已驗證使用者在遊戲直播社群的特定群組中發送文字、圖片或預測類型即時訊息，伺服器將訊息廣播給同群組其他線上使用者，並持久化儲存至聊天歷史資料表。

---

## 2. 入口 API
| Method | Path | 說明 |
|--------|------|------|
| SignalR Hub Method | CommunityHub.SendMessage | 客戶端透過 SignalR 連線呼叫，傳入群組 ID、訊息內容與類型 |

---

## 3. 流程總覽
1. 客戶端建立 SignalR 連線，通過 AuthKey 身分驗證。
2. 呼叫 Hub 方法 `SendMessage`，提供群組 ID、訊息內容、訊息類型（text / image / predict）及選填回覆訊息 ID。
3. Hub 從連線 Context 取得使用者帳號（Account）。
4. 查詢 `Community_Groups` 確認群組存在且 `Enabled = 1`。
5. 驗證訊息類型與內容格式（長度、非空等）。
6. 從使用者資訊來源（`GameUserInfo` 表或快取）取得 `UserName`、`Rank`、`HeadShotPath`。
7. 組合完整訊息物件，產生唯一 `ID`（GUID），設定 `AddTime` 為當前 Unix 毫秒時間戳。
8. 寫入 `ChatRoomHistories` 表（`INSERT`）。
9. 透過 SignalR Groups 機制，將訊息物件推送至群組內所有已連線使用者。
10. 回傳（或僅透過廣播告知）發送成功。

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Hub | CommunityHub.SendMessage | 接收客戶端要求，解析參數 |
| 2 | Hub | - | 從 HubCallerContext 提取已驗證的 Account (Claim) |
| 3 | Service | CommunityService (推測) | 呼叫資料層驗證群組存在與啟用狀態 |
| 4 | Provider | CommunityDataProvider | 執行 `SELECT Enabled FROM Community_Groups WHERE ID = @GID` |
| 5 | Service | CommunityService | 檢查回傳結果，若非啟用則擲回錯誤 |
| 6 | Service | - | 驗證 `ChatType` 限於 "text"、"image"、"predict"，內容不為空 |
| 7 | Service | - | 取得發送者資訊：查詢快取或 `GameUserInfo` 取得 Name、Rank、HeadShotPath |
| 8 | Service | - | 建立訊息物件，指定 GID、ID（GUID）、AddTime、Message、ChatType、ResponseID（若為回覆）、Account、UserName、Rank、HeadShotPath |
| 9 | Provider | CommunityDataProvider | `INSERT INTO ChatRoomHistories (...) VALUES (...)` |
| 10 | Hub | - | `await Clients.Group(GID).SendAsync("ReceiveMessage", messageObj)` |
| 11 | Hub | - | 可選回傳確認訊息給呼叫端或僅依賴廣播 |

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | Community_Groups | Read | 驗證群組存在且啟用 |
| DB | ChatRoomHistories | Write (INSERT) | 寫入訊息歷史 |
| DB (可能) | GameUserInfo | Read | 取得使用者顯示名稱、等級、頭像路徑 |
| Cache (推測) | 記憶體或 Redis | Read | 快取使用者資訊，減少重複查 DB |
| Queue | 無 | - | 未使用訊息佇列；直接同步寫入 DB 後廣播 |

---

## 6. 重要規則
- **身分驗證**：僅通過 SignalR 連線驗證（從 Claims 取得 Account）的使用者可發送訊息。
- **群組可用性**：`Community_Groups.Enabled = 1` 方可發言；停用群組拒絕操作。
- **訊息類型限制**：`ChatType` 只能為 `text`、`image`、`predict`，其餘回錯誤。
- **內容長度限制**：文字訊息長度上限（需人工確認具體數值）。
- **使用者資訊來源**：`UserName`、`Rank`、`HeadShotPath` 必須由伺服器從可靠來源（`GameUserInfo`）填入，不可信任客戶端傳入的值。
- **回覆關聯**：若提供 `ResponseID`，需確認該訊息存在於同一群組（非強制，但建議驗證）。
- **訊息順序**：不保證嚴格順序；若需排序，前端依 `AddTime` 顯示。
- **廣播範圍**：只廣播至同一 `GID` 的 SignalR Group，嚴防跨群組洩漏。
- **持久化優先**：DB 寫入成功後才廣播；若寫入失敗，不回傳成功也不廣播。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|------|----------|
| SignalR 連線未驗證 | Hub 拒絕呼叫，拋出未授權例外 |
| 群組 ID 不存在 | 回傳「群組不存在」錯誤 |
| 群組已停用 (`Enabled=0`) | 回傳「群組不可用」錯誤 |
| ChatType 為非法值 | 回傳參數無效提示 |
| 訊息內容為空或超長 | 回傳內容驗證失敗 |
| 取得使用者資訊失敗 (例如 `GameUserInfo` 查無) | 使用預設匿名資訊或回傳錯誤（需人工確認） |
| DB 寫入失敗 (連線逾時、死結) | 記錄錯誤日誌，回傳伺服器錯誤給呼叫端，不廣播 |
| SignalR 廣播時部分客戶端斷線 | 不影響整體；部分用戶離線未收到，但訊息已入 DB，可透過歷史 API 查詢 |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC-SEND-01 | Integration | 已驗證使用者發送 text 訊息至有效啟用群組 | 訊息成功寫入 DB，群組內其他連線收到相同內容廣播 |
| TC-SEND-02 | API | 未登入 SignalR 或連線無 Claims | Hub 拋出未授權異常，客戶端收到錯誤 |
| TC-SEND-03 | Flow | 發送訊息至不存在的 GID | 服務回傳明確「群組不存在」錯誤 |
| TC-SEND-04 | Permission | 停用群組 (`Enabled=0`) 發言 | 拒絕操作，回傳群組不可用 |
| TC-SEND-05 | Flow | 發送 image 類型訊息，附帶圖片 URL | 成功寫入及廣播，`ChatType=image`，內容為 URL |
| TC-SEND-06 | Flow | 發送 predict 類型訊息，附帶預測 JSON | 成功儲存，需確認 JSON 格式是否受檢核（可選） |
| TC-SEND-07 | Error | 模擬 DB 連線失敗 | 回應伺服器錯誤，不廣播，不寫入不完整資料 |
| TC-SEND-08 | Flow | 多個使用者併發發送訊息 | 訊息各自獨立寫入，廣播順序可能存在交錯，但不影響一致性 |

---

## 9. 高風險區域
- **高併發寫入**：`ChatRoomHistories` 同時大量 INSERT，需留意資料庫寫入效能及索引設計（`GID`, `AddTime`）。
- **廣播可靠性**：SignalR 群組廣播若連線瞬間中斷，部分客戶端可能漏接訊息；離線使用者無法收到即時訊息，需依賴歷史訊息 API 補償。
- **使用者資訊快取過期**：若 `GameUserInfo` 被快取，用戶變更頭像或名稱後可能短期內廣播舊資訊，需定義快取 TTL 或事件更新。
- **重複訊息**：缺乏 Idempotency 設計，客戶端若因超時重試，可能導致相同內容重複寫入並廣播兩次，形成洗版。
- **權限不足**：目前未限制群組成員資格，任何驗證使用者皆可向任何公開群組發言；若有私人或 VIP 群組，需額外成員檢查。

---

## 10. 常見錯誤
- **信任客戶端使用者資訊**：若直接使用客戶端傳入的 `UserName`，可能發生冒充他人發言，必須一律由後端查詢。
- **未檢查群組 Enabled 狀態**：停用群組仍能發言，導致管理失效。
- **SignalR Group 名稱錯誤**：加入錯誤的 Group 或廣播給錯誤群組，造成訊息洩漏或丟失。
- **訊息內容直接儲存未處理**：客戶端顯示時應注意 XSS 風險，服務端可選擇進行 HTML 編碼（視需求）。
- **忘記設定 `AddTime`**：導致訊息順序混亂；應統一在伺服器生成，避免使用客戶端時間。

---

## 11. Evidence
| 類型 | 來源 |
|------|------|
| API | SignalR Hub CommunityHub.SendMessage（由 README 即時聊天室功能推斷） |
| DB | Community_Groups、ChatRoomHistories（來自 db-usage 與語義摘要） |
| Code | CommunityDataProvider 處理群組查詢與訊息寫入；GameUserInfo 可能由 GameUserInfoService 提供 |
| 規則 | README：「即時聊天室 透過 SignalR 提供群組內文字、圖片、預測類型的訊息收發，支援回覆、按讚及頭像顯示」；ChatRoomHistories 欄位定義包含使用者顯示資訊 |
| 相關風險 | 無 Queue、無 Redis 寫入，僅 DB 操作（由技術棧推測） |