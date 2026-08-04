# 查詢頻道列表

## 1. 場景目的
取得可用直播頻道清單，供前端顯示比賽資訊、直播網址及訊號狀態，支援依啟用狀態篩選。

## 2. 入口 API
| Method | Path | 說明 |
|---|---|---|
| GET | /GameChannel/GetChannels（需人工確認） | 查詢頻道列表，可帶 `enabled` 參數過濾啟用頻道（例如 `?enabled=1`） |

## 3. 流程總覽
1. 前端發送 GET 請求，可選擇性附帶 `enabled` 參數（1：僅啟用，0 或不帶：全部）。
2. Controller 接收請求，調用 `GameChannelService.GetChannels`。
3. Service 查詢 `gamelive` 表，依 `enabled` 參數決定是否過濾 `Enabled` 欄位。
4. 針對每筆查詢結果，依據 `Url` 欄位是否存在或有效串流，設定 `SignalStatus`（1 正常 / 0 異常）— **需人工確認實際邏輯**。
5. 回傳頻道物件陣列，包含 `ChannelID`、`GameType`、`Date`、`League`、`Team_H`、`Team_A`、`GTime`、`Url`、`ChannelSwitch`、`SignalStatus` 等。
6. 前端接收並渲染直播頻道列表。

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GameChannelController.GetChannels` | 解析請求參數，呼叫 Service |
| 2 | Service | `GameChannelService.GetChannels` | 向 Data Provider 請求資料，組合輸出欄位 |
| 3 | Provider | `GameLiveDateProvider`（推測） | 執行 SQL 從 `gamelive` 載入符合條件的記錄 |
| 4 | Service | `GameChannelService` | 遍歷結果，依據 `Url` 狀態設定 `SignalStatus` |
| 5 | Controller | `GameChannelController` | 序列化並回傳 JSON |

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `gamelive` | Read | 查詢頻道基本資訊，篩選啟用狀態 |

目前無 Redis Cache 或 Message Queue 參與此流程的證據。

## 6. 重要規則
- **啟用狀態過濾**：  
  若參數 `enabled = 1`，僅回傳 `Enabled = 1` 的頻道；若參數為其他值或未提供，行為需人工確認（推測為回傳全部或不加過濾）。
- **訊號狀態**：  
  `SignalStatus` 可能依 `Url` 是否為空或即時連線檢測決定，**實際計算公式需人工確認**。
- **權限限制**：  
  推測此查詢為公開 API，**無需 AuthKey 驗證**，但仍需人工確認對應 Controller 是否有 `[Authorize]` 標籤。
- **欄位保護**：  
  頻道物件不得暴露內部管理資訊（如備註、創建者）。

## 7. 錯誤情境
| 情境 | 預期結果 |
|---|---|
| 資料庫連線失敗 | HTTP 500，記錄例外錯誤 |
| 查無任何符合條件的頻道 | HTTP 200，回傳空陣列 `[]` |
| `enabled` 參數非整數 | HTTP 400 或忽略非法參數（需人工確認） |

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC-01 | API Test | 不帶 `enabled`，查詢全部 | 回傳所有頻道，不分啟用狀態 |
| TC-02 | API Test | 帶 `enabled=1` | 僅回傳 `Enabled=1` 的記錄 |
| TC-03 | Flow Test | 某頻道 `Url` 有值 vs. 無值 | 確認 `SignalStatus` 分別為 1 和 0（依實作） |
| TC-04 | Integration Test | `gamelive` 表無資料 | 回傳空陣列，HTTP 200 |
| TC-05 | Permission Test | 若 API 需要驗證 | 無效 AuthKey 應回傳 401 |

## 9. 高風險區域
- **`SignalStatus` 即時判斷**：  
  若檢查串流可用性，可能導致請求逾時或阻塞，應採用非同步或預先標記機制。
- **資料一致性**：  
  目前無快取層，直接查庫無過期風險，但須注意大量請求時 DB 壓力。
- **SQL 注入**：  
  必須使用參數化查詢，不可直接拼接 `enabled` 條件。

## 10. 常見錯誤
- **誤解 `SignalStatus`**：以為是 DB 儲存欄位而忽略動態計算邏輯。
- **遺漏 `ChannelSwitch`**：前端可能判斷直播可用性時未同時考慮此欄位。
- **未處理額外參數**：可能因為僅處理已知參數而遭注入其他查詢條件。
- **權限配置錯誤**：若未來加上會員限制，新人可能誤開所有頻道給未登入用戶。

## 11. Evidence
| 類型 | 來源 |
|---|---|
| DB Table | `gamelive` 欄位定義來自 `GameLiveDateProvider.cs` 及 `GameChannelService.cs` |
| API 方法 | `GameChannelController.GetChannels` 註解與 `GameChannelService.GetChannels` 實作 |
| 訊號邏輯 | `GameChannelService.cs` 中使用 `x.Url` 設定 `SignalStatus` |

**待人工確認事項**：
- 確切 API 路由與 Swagger 定義。
- `SignalStatus` 計算方式（靜態欄位或動態檢測）。
- 是否需要身份驗證。
- `enabled` 參數未提供時的預設行為。