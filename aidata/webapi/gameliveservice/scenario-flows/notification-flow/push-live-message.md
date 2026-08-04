# 即時訊息推送

## 1. 場景目的
透過 SignalR Hub 即時將聊天訊息、按讚更新與預測發布等事件推送給同一社群群組（Community Group）內的所有線上使用者，確保訊息傳遞低延遲且一致。

---

## 2. 入口 API
| Method | Path / Hub | 說明 |
|---|---|---|
| SignalR Hub | `ChatHub` (需人工確認實際 Hub 名稱) | 用戶端建立 SignalR 連線並呼叫 Hub 方法以發送訊息、按讚或發布預測（需人工確認方法清單） |

> 需人工確認：SignalR Hub 具備哪些方法（例如 `SendMessage`, `LikeMessage`, `PublishPrediction`）以及對應參數。

---

## 3. 流程總覽
1. 使用者透過 SignalR 用戶端連線至 `ChatHub`，連線時附帶 `AuthKey` 參數進行身份驗證（需人工確認驗證方式）。
2. 驗證成功後，服務端將連線加入對應的 SignalR Group（Group 識別碼等於 `Community_Groups.ID`，即 `GID`）（需人工確認）。
3. 使用者呼叫 Hub 方法（例如送出訊息）。
   - 服務端依據 `AuthKey` 解析出使用者帳號，並從 `GameUserInfo` 取得使用者顯示資訊（`UserName`, `HeadShotPath`, `Rank` 等）。
   - 檢查目標群組 `GID` 存在且 `Enabled` = 1。
4. 針對不同事件類型：
   - **新訊息（文字、圖片、預測）**：產生唯一 `ID`，將訊息寫入 `ChatRoomHistories` 表，並將 `ChatType` 設為 `text`, `image` 或 `predict`。
   - **按讚**：更新目標訊息的 `LikeAccount` 欄位（JSON 陣列追加或移除）。需人工確認具體流程是否讀取後修改再寫回。
5. 寫入 DB 成功後，服務端透過 `IHubContext<ChatHub>.Clients.Group(GID)` 將事件物件推送給該群組的所有連線用戶。
6. 用戶端接收推送並更新 UI。

---

## 4. 程式流程
| 順序 | Layer | Class / Method (推測) | 動作 |
|---|---|---|---|
| 1 | Hub | `ChatHub.OnConnectedAsync` | 從 QueryString 或 Token 取得 `AuthKey`，驗證使用者身份，將連線加入 Group。 |
| 2 | Hub (需確認) | `ChatHub.SendMessage` | 接收訊息請求，解析參數，呼叫 Service。 |
| 3 | Service | `CommunityService.SendMessageAsync`（需確認） | 檢查群組啟用狀態、產生訊息 ID、取得使用者資訊，寫入 DB。 |
| 4 | Provider | `CommunityDataProvider.InsertMessage`（需確認） | 執行 SQL INSERT 至 `ChatRoomHistories`。 |
| 5 | Service | 同上 Service | 呼叫 Hub Context 推送。 |
| 6 | Hub Context | `IHubContext<ChatHub>.Clients.Group(GID).SendAsync(...)` | 推送訊息給群組。 |

> 需人工確認：以上 Class 與方法名稱來自推測，需根據實際代碼補充。

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `ChatRoomHistories` | Write (INSERT) | 儲存新訊息記錄 |
| DB | `ChatRoomHistories` | Update | 更新 `LikeAccount` 欄位（按讚時） |
| DB | `Community_Groups` | Read | 檢查群組 `Enabled` 狀態 |
| DB | `GameUserInfo` | Read | 根據帳號取得 `UserName`, `HeadShotPath`, `Rank` 等 |
| Cache | Redis (需人工確認) | 無證據 | 可能用於存儲線上使用者清單或連線狀態，若無則無需使用 |
| Queue | Kafka / MQ (需人工確認) | 無證據 | 系統架構未顯示使用非同步佇列處理訊息推送 |

> 若實際架構使用 Redis Pub/Sub 分發推送事件至多個 SignalR 節點，需人工補充。

---

## 6. 重要規則
- **身份驗證**：SignalR 連線必須提供合法 `AuthKey`，否則拒絕連線（需確認具體驗證位置）。
- **群組開關**：僅 `Enabled` = 1 的群組允許收發訊息。
- **訊息 ID 唯一性**：須由服務端產生全域唯一 ID（推測使用 GUID）。
- **不可暴露資料**：推送內容不可包含敏感內部資訊（如原始 `AuthKey`、點數餘額等）。
- **不可修改欄位**：訊息發送後，`Account`、`ChatType` 等核心欄位不應再變更；僅 `LikeAccount` 可被更新。
- **按讚權限**：需確認是否只有已驗證用戶能按讚，以及是否能重複按讚（需人工確認）。
- **TTL 規則**：無 (若無 Redis 則不適用)。
- **Transaction 規則**：寫入 DB 與推送之間不強制 Transaction；推送失敗不應回滾 DB 寫入。
- **Retry 規則**：SignalR 連線斷線時用戶端自動重連，服務端不需重發歷史訊息（除非另有設計）。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|---|---|
| `AuthKey` 無效或過期 | SignalR 連線失敗（Hub 拋出驗證錯誤） |
| 目標 `GID` 不存在 | Hub 方法回傳錯誤，不寫入 DB |
| 目標群組 `Enabled` = 0 | Hub 方法回傳「群組已停用」錯誤 |
| `GameUserInfo` 查無使用者 | 方法中斷，回傳授權失敗 |
| `ChatRoomHistories` INSERT 失敗 | 回傳服務器錯誤，不推送 |
| SignalR 推送時部分用戶端斷線 | 不影響其他用戶，亦不影響 DB 記錄 |
| 按讚請求中目標訊息 `ID` 不存在 | 回傳「訊息不存在」錯誤 |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| Noti-01 | Integration | 兩位使用者加入同一群組，A 送出文字訊息 | B 即時收到訊息，內容與 DB 一致 |
| Noti-02 | Integration | 群組停用 (`Enabled=0`) 時嘗試發送訊息 | 發送失敗，收到權限錯誤 |
| Noti-03 | API/Flow | 未帶 AuthKey 建立 SignalR 連線 | 連線遭拒絕 |
| Noti-04 | Flow | 按讚一則訊息 | DB 更新 LikeAccount，群組內所有人收到更新後的訊息物件 |
| Noti-05 | Flow | 發布預測訊息 (ChatType=predict) | 訊息存入 DB 並推送，內容包含預測數據 |
| Noti-06 | Permission | 使用者嘗試操作不存在的 GID | 返回錯誤 |
| Noti-07 | Stress | 1000 人同群組，同時發送訊息 | 所有用戶端收到訊息，服務端無崩潰 |

---

## 9. 高風險區域
- **高風險 table**：`ChatRoomHistories` (大量寫入可能影響效能，需正確索引 `GID, AddTime`)。
- **跨服務資料同步**：若系統擴充至多台 SignalR 伺服器，需考慮 Redis backplane 或自訂同步機制（目前無證據）。
- **訊息一致性**：DB 寫入成功但推送中斷，部分用戶未收到即時通知，但訊息已保存，可考慮後續拉取機制。
- **Idempotency**：按讚操作若多次重複請求可能導致 LikeAccount 重複帳號，需前端防重複或後端去重。
- **使用者資訊快取**：若每次推送都查 `GameUserInfo` 可能影響性能，必要時可快取使用者資料，但需注意資料更新。

---

## 10. 常見錯誤
- **忘記檢查群組 `Enabled`**，導致停用群組仍可發送訊息。
- **直接在前端產生訊息 ID**，導致重複或預測性衝突，應由後端生成。
- **推送物件遺漏必要欄位**（如 `HeadShotPath` 為空），導致前端顯示異常。
- **未處理 SignalR Group 加入失敗**，使用者仍在 Group 外，收不到訊息。
- **誤將重要資料（如原始點數）暴露在推送中**。

---

## 11. Evidence
| 類型 | 來源 |
|---|---|
| DB Table | `ChatRoomHistories` (GID, ID, Message, LikeAccount, ChatType, Account, HeadShotPath...) |
| DB Table | `Community_Groups` (ID, Enabled) |
| DB Table | `GameUserInfo` (AuthKey, Account, UserName, HeadShotPath, Rank) |
| 即時通訊技術 | README 明確記載使用 SignalR 作為即時通訊框架 |
| 訊息保存 | 同一 README 指出訊息歷史存檔並提供查詢（對應 `ChatRoomHistories`） |

> 需人工確認：實際 Controller / Service / Hub 程式碼位置與確切方法名稱、SignalR 驗證機制細節、是否有使用 Redis 或 Queue。建議補充相關原始碼索引以利後續 AI 準確引用。