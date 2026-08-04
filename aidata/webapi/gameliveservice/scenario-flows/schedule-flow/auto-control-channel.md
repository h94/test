# 自動控制頻道開關

## 1. 場景目的
根據 `AppSettings.CloseGameLiveDeadline` 設定與比賽實際時間，由排程任務自動對 `gamelive` 表中的頻道進行啟用（Switch=1）或停用（Switch=0），確保直播訊號僅在賽事期間可用。

---

## 2. 入口 API
此流程為內部排程（Schedule），無對外 HTTP API，由背景服務定時觸發。  
**觸發方式**：需人工確認（可能為 Quartz.NET / Timer / Hangfire）。  
若需模擬手動觸發，可能透過內部 controller 提供測試端點（需人工確認）。

---

## 3. 流程總覽
1. 背景工作啟動自動控制方法（推測為 `SystemService.AutoControlChannel`）。
2. 從 `gamelive` 表取出所有現存頻道（不限開關狀態，推測用 `ChannelSwitch.All` 參數）。
3. 從組態讀取 `CloseGameLiveDeadline` 值（單位：分鐘，需人工確認）。
4. 對每個頻道，根據其 `GameType` 與 `Date`，查詢對應的 `games_{GameType}` 表，取得當日所有比賽。
5. 比對當前時間與每場比賽的 `gtime`，判斷是否超過「比賽時間 + CloseGameLiveDeadline」。
6. 若存在比賽尚未超過截止時間 → 頻道應設為啟用（Switch=1）。  
   若所有比賽皆已超過截止時間 → 頻道應設為停用（Switch=0）。
7. 根據判斷結果更新 `gamelive` 表中對應的 `ChannelSwitch` 欄位（可能批量更新）。
8. （推測）若有 `GlobalChannel` 設定，可能另外處理全站預設頻道邏輯（需人工確認）。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Scheduler | 未知（需人工確認） | 定時觸發背景作業 |
| 2 | Service | `SystemService.AutoControlChannel` | 呼叫 Provider 取得所有頻道 |
| 3 | Provider | `GameLiveDateProvider.GetPreviousChannels((int)ChannelSwitch.All)` | 讀取 `gamelive` 表所有頻道 |
| 4 | Service | `GameDataProvider.GetGameByGDateAfter` 或類似方法 | 根據頻道的 `GameType`、`Date` 查詢當日比賽 |
| 5 | Service | 自行邏輯 | 計算是否超過 `gtime + CloseGameLiveDeadline` |
| 6 | Provider | `GameLiveDateProvider` 更新方法 | 寫入 `ChannelSwitch` 欄位至 `gamelive` |
| 7 | Provider | 可能涉及 `SignalR` | 若頻道開關變更，推送給前端（需人工確認） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `gamelive` | Read | 取得所有頻道基本資訊 |
| DB | `games_{GameType}` | Read | 取得指定日期的所有比賽與時間 |
| DB | `leagues_{GameType}` | Read（可選） | 若需要聯賽名稱（頻道已存名稱則可能不需） |
| DB | `gamelive` | Update | 寫入新的 `ChannelSwitch` 狀態 |
| Cache | （未發現） | - | 推測無 Redis 參與，所有狀態直接讀寫 DB |
| Queue | （未發現） | - | 流程無 Kafka / Queue 事件 |

---

## 6. 重要規則

- **權限**：此為系統內部排程，不涉及使用者權限。
- **時間判斷**：必須使用伺服器當前時間，不可依賴前端時間。
- **截止緩衝**：`CloseGameLiveDeadline` 為整數，單位需確認（組態註解為「關閉賽事直播的期限(分鐘)」），**必須以分鐘為單位轉換後計算**。
- **頻道狀態值**：`ChannelSwitch`：1=啟用，0=停用。不可寫入其他值。
- **延遲開關**：不可在無比賽的時段還保持啟用；但須當該頻道任何比賽未超過 deadline 時即應啟用，而非等所有比賽結束才切換。
- **比賽資料來源**：只從 `games_{GameType}` 查詢 `gdate` 等於頻道 `Date` 的記錄，避免誤用日期。
- **跨日比賽**：若比賽時間跨日，需特別處理（目前未見相關邏輯，需人工確認）。
- **GlobalChannel**：可能為常開頻道，不受自動控制影響（需人工確認）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `gamelive` 表無任何頻道 | 流程正常結束，無動作 |
| `games_{GameType}` 表不存在或無資料 | 該頻道視為無比賽，應切換為停用 |
| `CloseGameLiveDeadline` 組態遺漏或值為 0 | 可能導致頻道永遠不關閉或異常，需人工確認預設行為 |
| 資料庫連線逾時 | 排程應記錄錯誤並重試，或跳過本輪（需人工確認） |
| 更新 `gamelive` 時發生鎖定 | 應使用樂觀鎖定或交易，避免部分更新成功部分失敗 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| AT-01 | Integration | 當前時間在比賽前 5 分鐘，有一場比賽 gtime 為 10 分鐘後，Deadline=10 分鐘 | 頻道應設為啟用 |
| AT-02 | Integration | 當前時間超過唯一比賽的 gtime+deadline | 頻道應設為停用 |
| AT-03 | Integration | 頻道關聯多場比賽，其中一場仍有效 | 頻道應保持啟用 |
| AT-04 | Boundary | deadline 設定為 0 | 開關行為符合規格（需人工確認） |
| AT-05 | Permission | 非排程身份直接呼叫內部服務 | 應被阻擋或無對外 API（需確認） |
| AT-06 | DB Fail | 資料庫不可用 | 排程應留下錯誤紀錄並於下輪重試 |

---

## 9. 高風險區域

- **高風險 Table**：`gamelive`（直接修改開關狀態，影響前端播放）。
- **高風險 API**：無對外 API，但內部 `AutoControlChannel` 若被錯誤排程並行執行，可能造成競爭條件。
- **Cache Consistency**：無 Cache 層，風險低。
- **Transaction**：多表讀取（gamelive + games_*）可能不一致（時間差），但非交易核心，風險尚可。
- **跨服務同步**：無。
- **Idempotency**：同一次執行結果應可重複，不會造成反覆切換。

---

## 10. 常見錯誤

- **新人誤解**：以為 `CloseGameLiveDeadline` 是從比賽開始時間算起，實為比賽結束後的緩衝。
- **AI 誤判**：可能將 `Deadline` 誤認為倒數計時觸發時間點，而忽略需要比對所有比賽。
- **漏檢查**：未考慮頻道可能無比賽（`games_*` 無資料）時應停用。
- **時間格式錯誤**：`gtime` 為字串，應轉換為正確的 `DateTime` 再計算，否則比對無效。
- **未處理多個 GameType**：頻道的 `GameType` 決定查詢哪張表，錯誤映射會導致找不到比賽。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| 組態 | `AppSettings.CloseGameLiveDeadline` (AppSettings.cs) |
| 頻道表 | `gamelive` (GameLiveDateProvider.cs, GameLive.cs) |
| 比賽表 | `games_{gameType}` (GameDataProvider.cs, GameInfo.cs) |
| 排程服務方法 | `SystemService.AutoControlChannel` (phase0/1 batch5 語意) |
| 取得所有頻道方法 | `GameLiveDateProvider.GetPreviousChannels((int)ChannelSwitch.All)` (phase0/1 batch5) |
| 開關狀態欄位 | `ChannelSwitch` (GameChannelController.cs, GameLive.cs) |