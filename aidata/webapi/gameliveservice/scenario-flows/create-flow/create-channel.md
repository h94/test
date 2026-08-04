# 建立直播頻道

## 1. 場景目的  
提供後台管理員新增或更新比賽直播頻道，設定頻道識別碼、遊戲類型、日期、聯賽、主客隊、直播網址等資訊，同時初始化訊號與開關狀態，供前端 SignalR 即時查詢。

---

## 2. 入口 API  

| Method | Path | 說明 |
|--------|------|------|
| POST (推測) | /api/GameChannel/InsertOrUpdateChannel | 建立或更新直播頻道，由 GameChannelController 處理 |

> **需人工確認**：確切 HTTP Method 與路由路徑，原始碼未直接提供。

---

## 3. 流程總覽  

1. 接收頻道資料（ChannelID、GameType、Date、Enabled、Url 等）。
2. 執行身分驗證（依 AuthKey 判斷管理權限，需人工確認權限規則）。
3. 呼叫 ChannelValidator 驗證必要欄位與格式。
4. 根據 ChannelID 查詢 `gamelive` 表是否已存在。
5. 若存在：更新該頻道資料；若不存在：新增一筆頻道。
6. 設定初始狀態（Enabled 依輸入，可能還有 ChannelSwitch、SignalStatus 等）。
7. 寫入資料庫 `gamelive` 表（單一 records 操作）。
8. 回傳成功結果或拋出例外（若驗證失敗或 DB 錯誤）。

---

## 4. 程式流程  

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | GameChannelController.InsertOrUpdateChannel | 接收請求、呼叫驗證器與服務 |
| 2 | Validator | ChannelValidator (推測方法名) | 驗證 GameType、Date、必填欄位 |
| 3 | Service | GameChannelService (推測) | 判斷新增或更新，準備資料物件 |
| 4 | Provider | GameLiveDateProvider (推測) | 執行 `gamelive` 表的 INSERT 或 UPDATE |
| 5 | - | - | 回傳影響筆數，Controller 組建回應 |

> **需人工確認**：Service 與 Provider 確切類別名稱，目前依 DB 分析推測為 GameLiveDateProvider。

---

## 5. DB / Cache / Queue 使用  

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `gamelive` | Insert / Update | 寫入或修改頻道資料 |

> 此流程無 Redis、Kafka 或 Queue 操作（依現有資訊未發現使用），若有快取清除或 SignalR 推送需額外確認。

---

## 6. 重要規則  

- **權限限制**：需具備管理員權限（需人工確認：可能比對 AuthKey 所屬角色）。  
- **ChannelID 唯一性**：若 `channelid` 已存在，執行更新而非新增（InsertOrUpdate）。  
- **必填欄位**：GameType、Date、ChannelID、Enabled 必須提供；格式如 Date 為 yyyy-MM-dd。  
- **欄位不可暴露**：內部狀態欄位（如 SignalStatus）不應由請求直接設定，由系統預設。  
- **狀態初始值**：SignalStatus 建議設為 0（異常）或 -1（未知），ChannelSwitch 預設可為 1（開啟）。  
- **不可修改欄位**：ChannelID 不可在更新時改變（作為 key）。  
- **Transaction**：單一記錄寫入，需確保 atom，無跨表事務。  

---

## 7. 錯誤情境  

| 情境 | 預期結果 |
|------|----------|
| 未提供 AuthKey 或權限不足 | 回傳 401 或 403，不執行寫入 |
| ChannelID 為空 | 回傳 400，提示必要欄位遺漏 |
| GameType 為不支援的值（非 basketball/football 等） | 回傳 400，提示參數無效 |
| Date 格式錯誤（非 yyyy-MM-dd） | 回傳 400，提示日期格式錯誤 |
| DB 連線失敗 / timeout | 回傳 500，記錄錯誤日誌 |
| 寫入時遇到唯一鍵衝突（非 ChannelID 的其他約束） | 回傳 409 或 500，視實現而定 |
| 更新時目標 ChannelID 不存在 | 通常仍執行 INSERT（視邏輯），若強制更新回傳 404（需人工確認） |

---

## 8. 測試重點  

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC-01 | API Test | 新增一個全新頻道，所有欄位合法 | 回傳 200，gamielive 表新增一筆 |
| TC-02 | API Test | 使用已存在的 ChannelID，傳入部分更新資料 | 回傳 200，對應記錄更新，未更新欄位保留 |
| TC-03 | Validation | 缺少 GameType 請求 | 回傳 400，錯誤訊息指明欄位 |
| TC-04 | Permission | 無 AuthKey 或非管理員呼叫 | 回傳 401/403 |
| TC-05 | Flow Test | 新增後查詢 GetChannels API 確認新頻道出現 | 頻道列表包含該頻道，Enabled 狀態正確 |
| TC-06 | DB | 模擬 DB 寫入失敗 | 回傳 500，且不影響其他資料 |

---

## 9. 高風險區域  

- **高風險 table**：`gamelive`，作為直播核心設定，錯誤更新可能影響前端顯示與 SignalR 通知。  
- **高風險 API**：InsertOrUpdateChannel，若無正確權限控制，可被任意篡改頻道開關或直播網址。  
- **競爭條件**：併發呼叫相同 ChannelID 的 InsertOrUpdate 可能造成更新遺失，建議使用 DB 層 `INSERT ... ON DUPLICATE KEY UPDATE` 或樂觀鎖。  
- **Cache consistency**：若有快取頻道列表，更新後未清除或通知，導致前端顯示舊資料（需人工確認快取機制）。  

---

## 10. 常見錯誤  

- **誤解聯賽/球隊來源**：以為需先從 `leagues_{type}` 或 `teams_{type}` 表取得 ID，實際上 `gamelive` 直接儲存文字名稱，無外部鍵。  
- **忘記設定初始狀態**：新增時未初始化 SignalStatus，導致後續訊號監控無法正常運作。  
- **日期格式錯誤**：使用當地時間格式而非固定的 yyyy-MM-dd，造成查詢排序錯誤。  
- **權限檢查遺漏**：實作時僅驗證 AuthKey 有效性，未確認該使用者是否具後台角色。  

---

## 11. Evidence  

| 類型 | 來源 |
|------|------|
| API | GameChannelController.InsertOrUpdateChannel（來自 phase 分析註解） |
| DB table | gamelive（來自 GameLiveDateProvider.cs 分析） |
| Validator | ChannelValidator.cs（來自 phase 分析，驗證 GameType/Date 等） |
| 欄位語義 | ChannelID、GameType、Date、Url 等（來自 GameChannelController 註解及 DB schema） |
| 權限推測 | 需 AuthKey（來自 README 訂閱機制，但未直接證明此 API 需要）— 需人工確認 |