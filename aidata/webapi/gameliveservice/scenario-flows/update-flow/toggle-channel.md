# 啟用/停用頻道

## 1. 場景目的
管理員變更直播頻道的 `Enabled` 狀態（1=啟用，0=停用），控制前檯是否顯示該頻道，並影響即時訊號與聊天室顯示。

---

## 2. 入口 API

| Method | Path                       | 說明                                           |
|--------|----------------------------|------------------------------------------------|
| PUT    | api/GameChannel/InsertOrUpdateChannel | 新增或更新頻道資訊，包含 `Enabled` 欄位   |

> **需人工確認**：API 路徑為根據 Controller 名稱與方法名推測，實際路由可能不同（例如 `/api/GameChannel` 搭配 HTTP PUT）。

---

## 3. 流程總覽
1. 接收頻道更新請求（含 `ChannelID` 與目標 `Enabled` 值）。
2. 驗證操作者權限（需為管理員，**需人工確認**）。
3. 由 `ChannelValidator` 驗證必須欄位（`ChannelID`、`GameType`、`Enabled` 等）。
4. 查詢 `gamelive` 表確認頻道存在。
5. 更新 `gamelive` 表該頻道的 `enabled` 欄位。
6. 如有必要，透過 SignalR 推送頻道狀態變更通知（**需人工確認**）。
7. 回傳成功或失敗回應。

---

## 4. 程式流程

| 順序 | Layer      | Class / Method                           | 動作                                                   |
|------|------------|------------------------------------------|--------------------------------------------------------|
| 1    | Controller | `GameChannelController.InsertOrUpdateChannel` | 接收請求，呼叫 Service                              |
| 2    | Service    | `GameChannelService.UpdateChannel`（推測） | 組合資料並呼叫 Validator                            |
| 3    | Validator  | `ChannelValidator`                       | 檢查 `ChannelID` 非空、`Enabled` 值為 0 或 1 等        |
| 4    | Provider   | `GameLiveDateProvider.UpdateGameLive`    | 執行 `UPDATE gamelive SET enabled = @Enabled WHERE channelid = @ChannelID` |
| 5    | Controller | –                                        | 回傳結果給前端                                     |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源         | 操作   | 用途                           |
|------|--------------|--------|--------------------------------|
| DB   | `gamelive` 表 | Update | 變更 `enabled` 狀態            |

- 無 Redis / Kafka 操作在此流程中。

---

## 6. 重要規則
- **Enabled 值限制**：僅允許 `0`（停用）或 `1`（啟用），不可為其他值。
- **頻道存在性**：更新前必須確認 `ChannelID` 存在，否則回應錯誤。
- **權限**：操作者必須具備管理員權限（**需人工確認**）。
- **不可修改欄位**：除了 `Enabled`，其他業務欄位（如 `GameType`、`Date`）應依實際需求決定是否可一併更新；純啟用／停用情境可能不允許變更其他欄位（**需人工確認**）。
- **Transaction**：單一 `UPDATE` 操作，無需跨表交易。

---

## 7. 錯誤情境

| 情境                         | 預期結果                         |
|------------------------------|----------------------------------|
| `ChannelID` 不存在           | 回傳錯誤碼，提示頻道不存在       |
| `Enabled` 值非 0 或 1        | 回傳驗證錯誤                     |
| 操作者無管理權限             | 回傳 403 Forbidden               |
| 資料庫更新失敗               | 回傳 500 內部錯誤                |
| 同時有其他人修改同一頻道     | 後寫入者覆蓋，無樂觀鎖保護（**需人工確認**） |

---

## 8. 測試重點

| Test ID | 類型               | 情境                         | 預期結果                         |
|---------|-------------------|------------------------------|----------------------------------|
| T1      | API Test          | 停用一個已存在且啟用的頻道     | `Enabled` 變為 0，前檯不再顯示    |
| T2      | API Test          | 啟用一個已停用的頻道           | `Enabled` 變為 1，前檯恢復顯示    |
| T3      | Permission Test   | 一般使用者呼叫 API            | 403 無權限                        |
| T4      | Validation Test   | `Enabled = 2`                 | 400 驗證錯誤                      |
| T5      | Flow Test         | 禁用後立即查詢頻道列表         | 回傳的 `Enabled` 為 0             |

---

## 9. 高風險區域
- **並發更新**：無防範機制（如 rowversion 或條件更新），可能導致狀態遺失。
- **前後端狀態不一致**：若未透過 SignalR 即時通知，前端可能顯示舊狀態。
- **外部相依**：若 `gamelive` 表更新失敗但未正確回報，管理員可能誤判狀態。

---

## 10. 常見錯誤
- 未檢查頻道是否存在就直接執行 `UPDATE`，SQL 未影響任何行卻回傳成功。
- 誤將 `Enabled` 與 `ChannelSwitch` 混淆（後者為整體開關，**需人工確認**）。
- 未記錄狀態變更的 Audit Log（目前無證據有此機制）。

---

## 11. Evidence

| 類型 | 來源                                |
|------|-------------------------------------|
| API  | `GameChannelController.InsertOrUpdateChannel` |
| DB   | `gamelive` 表，欄位 `enabled`       |
| Code | `GameLiveDateProvider`（更新操作）  |
| Code | `ChannelValidator`（驗證 Enabled）  |
| SQL  | `UPDATE gamelive SET enabled = @p0 WHERE channelid = @p1`（推測） |

> **需人工確認**：  
> - API 確切路由與 HTTP method  
> - 權限控管實作（是否僅管理員）  
> - 是否發送 SignalR 通知  
> - `ChannelSwitch` 與 `Enabled` 的區別與互動