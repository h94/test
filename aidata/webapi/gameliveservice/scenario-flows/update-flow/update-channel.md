# 編輯直播頻道

## 1. 場景目的
允許已授權的管理者修改現有直播頻道的基本設定，包括直播網址、聯賽、主客隊名稱、比賽時間、啟用狀態等，以維持頻道資訊正確性。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | /api/GameChannel/{channelId} | 編輯指定頻道設定（可能與新增共用同一端點，依實作而定） |

> 需人工確認：實際端點路徑與 HTTP Method 以 OpenAPI 或 Controller 定義為準。目前根據 `GameChannelController.cs (InsertOrUpdateChannel)` 推測可能提供通用 API。

---

## 3. 流程總覽
1. 接收編輯請求，內含 `ChannelID` 及欲修改的欄位（如 `Url`, `League`, `Team_H`, `Team_A`, `GTime`, `Enabled` 等）。
2. 驗證請求格式與必要欄位（透過 `ChannelValidator.cs`）。
3. 驗證使用者權限（需為後台管理員或具備頻道管理權限；檢查 `AuthKey` 對應的角色）。
4. 查詢 `gamelive` 資料表，確認頻道存在。
5. 將新值寫入 `gamelive` 表（更新對應紀錄）。
6. 若成功，可能觸發快取清除或通知 SignalR 客戶端以刷新前端顯示。
7. 回傳成功結果（可能包含最新的頻道資料）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GameChannelController.InsertOrUpdateChannel` (推測) | 接收請求並綁定模型，呼叫 Service |
| 2 | Validator | `ChannelValidator.cs` | 檢查必要欄位、格式、`GameType` 合法性等 |
| 3 | Service | `GameChannelService.cs`（或類似名稱） | 驗證權限、呼叫 Provider 進行資料讀寫 |
| 4 | Provider | `GameLiveDateProvider.cs` | 對 `gamelive` 執行 SELECT 確認存在、UPDATE 更新欄位 |
| 5 | Cache (若有) | RedisCacheProvider (未確認) | 若存在頻道快取，則清除或更新快取 |
| 6 | Hub (若有) | SignalR Hub | 推送頻道異動事件給前端 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `gamelive` | Read（WHERE ChannelID） | 確認頻道存在，避免更新不存在的記錄 |
| DB | `gamelive` | Update | 寫入新的頻道設定（URL、聯賽、隊伍、時間、啟用狀態） |
| Cache | Redis (需確認) | Delete / Refresh | 若前端使用快取，需使舊資料失效，避免顯示過時資訊 |
| Queue | 無 | — | 目前無證據顯示使用 Kafka/Queue |

---

## 6. 重要規則
- **權限限制**：僅允許具備「頻道管理」權限的後台帳號執行。需驗證 `AuthKey` 對應的角色（管理員或特定權限群組）。
- **欄位限制**：`GameType` 必須是系統支援的類型（如 `basketball`, `football`）；`Enabled` 僅可為 0（停用）或 1（啟用）。
- **不可暴露資料**：內部實作不得回傳敏感資訊（如資料庫連線字串、內部 IP）。
- **Transaction 規則**：更新 `gamelive` 時無跨表交易需求，單表更新即可；但若後續有快取更新，建議使用資料庫交易搭配補償機制，確保資料一致性（需人工確認）。
- **不可修改欄位**：`ChannelID` 作為主鍵，不可更新；`Date` 通常為建立時設定，但若有業務需要允許修改則例外（需確認）。
- **狀態值限制**：`Enabled` 修改時應注意是否影響正在進行中的直播；若啟用狀態變更，可能觸發自動控制頻道的背景服務（`SystemService.AutoControlChannel`），需注意副作用。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 缺少必填欄位（如 `GameType`） | 回傳 400 錯誤，包含驗證訊息 |
| `ChannelID` 不存在 | 回傳 404 錯誤（或 400），提示頻道不存在 |
| 使用者無效的 `AuthKey` 或權限不足 | 回傳 401 或 403 錯誤 |
| `Enabled` 傳入非 0/1 的值 | 回傳 400 錯誤，提示格式有誤 |
| 資料庫寫入失敗（如鎖定、逾時） | 回傳 500 錯誤，記錄例外並通知維運 |
| 快取清除失敗（若有使用快取） | 寫入資料庫成功，但前端可能看到舊資料（需考慮重試或標記快取過期；需人工確認） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC-01 | API Test | 以有效管理者身份修改 `Url` 及 `League` | 回傳 200，`gamelive` 中對應欄位已更新 |
| TC-02 | Permission Test | 以一般使用者 `AuthKey` 呼叫編輯 API | 回傳 403 或提示權限不足 |
| TC-03 | Flow Test | 嘗試編輯不存在的 `ChannelID` | 回傳 404，資料庫無異動 |
| TC-04 | API Test | 修改 `Enabled` 由 1 變為 0 | 頻道立即停用，前端不顯示該頻道 |
| TC-05 | Integration Test | 更新後檢查 Redis 快取是否失效（若有） | 快取被清除，下次查詢得到新資料 |
| TC-06 | Validation Test | 傳入不合法的 `GameType` | 回傳 400，`gamelive` 無異動 |

---

## 9. 高風險區域
- **高風險 table**：`gamelive` — 所有頻道設定皆集中於此，錯誤更新將直接影響前端顯示、訊號監控及派送。
- **高風險 API**：編輯 API 若缺少權限驗證，可能遭未授權人士竄改直播網址或停用頻道。
- **跨服務資料同步**：若有背景服務（如 `SystemService.AutoControlChannel`）依據 `Enabled` 或 `Url` 自動控制頻道，更新後可能立即觸發訊號開關，需確認行為符合預期。
- **Cache consistency**：若前端或 BFF 層有快取，更新後未清除會導致用戶看到舊網址或舊隊伍，應設計失效機制。
- **並行修改**：若多人同時編輯同一頻道，最後寫入者覆蓋先前更新，可能造成資料遺失；實作上可考慮樂觀鎖定（如比對 `UpdateTime`）或紀錄操作歷程。

---

## 10. 常見錯誤
- **新人容易犯錯**：
  - 直接使用前端傳入的 `ChannelID` 進行更新而未檢查是否存在，導致資料庫出現孤兒更新或錯誤日誌。
  - 忽略權限驗證，僅檢查 `AuthKey` 有效性而未確認角色。
  - 更新後未清除前端快取，誤以為 API 沒成功。
- **AI 容易誤解**：
  - 混淆 `gamelive` 與動態表 `games_{type}`、`teams_{type}`，誤以為修改聯賽或隊伍名稱需要同步更新這些表。
  - 將「編輯頻道」理解為建立新頻道，而使用 INSERT 邏輯。
- **常見漏檢查項目**：
  - 未驗證 `GameType` 是否為系統允許值。
  - 未處理 `Url` 長度或格式（如開頭需為 `http`）。
- **常見錯誤流程**：前端修改後未重新取得頻道清單，遇到畫面未更新時，誤認為後端寫入失敗，造成重複提交或客服回報。

---

## 11. Evidence

| 結論 | 證據類型 | 來源 |
|---|---|---|
| 存在 InsertOrUpdateChannel 方法 | Code | `GameChannelController.cs`（Phase1 batch-3） |
| `gamelive` 表包含設定欄位 | DB Schema | Phase1 batch-4 / batch-6 表定義列表 |
| 頻道驗證由 `ChannelValidator` 負責 | Code | Phase1 batch-3 |
| 權限驗證依賴 `AuthKey` 與會員等級 | Table Semantics | `GameUserInfo` 表包含 `Authkey`、`Rank` 等欄位 |
| 背景控制服務可根據 `Switch` / `Enabled` 操作頻道 | Code | `SystemService.AutoControlChannel` 引用 `Channels` 表（Phase1 batch-5） |

（部分細節如確切 API 路由、Service 命名、Redis 快取存在性、SignalR 推送等需人工核實程式碼後補足。）