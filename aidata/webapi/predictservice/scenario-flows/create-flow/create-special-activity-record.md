# 設定特殊活動記錄

## 1. 場景目的

記錄特定用戶在特殊活動（如連贏活動）中的累積資訊，包含獲勝注單列表、休息天數等，供後續排行榜計算或查詢使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/special/records/{site}/{activityEvent}` | 設定活動記錄，需驗證 |

---

## 3. 流程總覽

1. 驗證請求者身份（透過內部驗證框架 ECFramework.ECService）。  
2. 檢查 request body 必要欄位（`account`, `winbets` 等）。  
3. (選擇性) 查詢 `predict.activities_cycles` 確認該 `site` 與 `activityEvent` 的活動存在且有效。  
4. 針對該用戶 (`account`) 在 `predict.activities_record` 中寫入或更新記錄。  
5. 若已有該用戶記錄，則對 `winbets` 欄位使用 `APPEND` 方式合併新增的獲勝注單，避免覆蓋歷史數據；若無則建立新記錄。  
6. 回傳成功狀態。  

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `SpecialController.PostRecords` (推斷) | 接收 request body，調用驗證 |
| 2 | Service | `SpecialActivityService.SetRecord` (推斷) | 驗證帳號權限、活動有效性 |
| 3 | Provider | `PredictCassandraProvider.UpsertActivityRecord` (推斷) | 寫入 `predict.activities_record`，處理 winbets APPEND |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `predict.activities_record` | Write (INSERT / UPDATE) | 儲存或更新用戶活動記錄 |
| DB | `predict.activities_cycles`（選擇性） | Read | 確認活動是否存在且處於有效時間範圍內 |
| Redis | 無明確使用 | - | 本場景未使用快取 |
| Queue | 無 | - | 無非同步處理 |

---

## 6. 重要規則

- **權限限制**：API 需要驗證（`README` 標記 ✅），推測僅後台管理員或具有特定角色的帳號可呼叫；前台用戶無法直接設定自己的記錄。  
- **欄位限制**：`winbets` 欄位只能使用 `APPEND` 方式新增元素，**禁止直接覆蓋整個 list**，否則將遺失歷史注單（`predict-detail.md`）。  
- **不可回傳欄位**：此 API 為寫入操作，無敏感資料回傳風險。  
- **Transaction 規則**：Cassandra 無傳統事務；一次寫入即 Upsert；`winbets` 的 APPEND 應藉由 Cassandra 的 list append 語法達成，避免併發覆蓋。  
- **狀態值限制**：`restday` 應為非負整數。  
- **不可修改欄位**：本表無不可修改欄位，但建議 `site`、`eventname`、`account` 組合為主鍵，因此一旦建立，主鍵不可變更。  

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未附帶有效驗證 Token | 回傳 401 Unauthorized |
| Request body 缺少 `account` 或 `winbets` | 回傳 400 Bad Request |
| `account` 不存在於系統中 | 回傳 400 Bad Request（需驗證 account 有效，否則回傳錯誤） |
| `site`/`activityEvent` 對應的活動週期不存在或已結束（若實作強校驗） | 回傳 400 Bad Request |
| Cassandra 寫入失敗或超時 | 回傳 500 Internal Server Error |
| 對已存在的記錄進行操作時，錯誤使用覆蓋而非 APPEND 寫入 `winbets` | 導致歷史獲勝記錄丟失（後端設計錯誤） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| SR001 | Permission Test | 無 Token 呼叫 | 401 |
| SR002 | Permission Test | 一般用戶 Token 呼叫（推測無權限） | 403（需人工確認權限設計） |
| SR003 | API Test | 正常請求（首次寫入） | 200，DB 建立新記錄 |
| SR004 | API Test | 對同一帳號再次呼叫，提供新的 `winbets` 元素 | 200，DB 中 `winbets` list 新增元素，舊元素保留 |
| SR005 | API Test | 提供 `restday` 更新 | 200，DB 中 `restday` 值更新 |
| SR006 | Flow Test | 活動不存在時呼叫 | 400（若實作校驗） |
| SR007 | API Test | 提供非法 `restday`（如負數） | 400（若實作驗證） |

---

## 9. 高風險區域

- **高風險 table**：`predict.activities_record` — 若 `winbets` 處理不當（直接覆蓋），將導致累積勝場數據永久丟失。  
- **高風險 API**：此 endpoint 若缺乏嚴格的授權控制，可能被惡意用戶篡改活動記錄。  
- **跨服務資料同步**：本表由 `predictservice` 寫入，`predictresultservice` 在結算時也可能寫入 `winbets`（APPEND）。若未使用合適的併發控制，可能發生 list 遺失。  
- **Cache consistency**：無快取，風險較低。  
- **Queue retry**：無 queue，未涉及。  
- **Idempotency**：請求重試可能導致相同 `winbets` 元素重複 APPEND，需考慮去重機制（或由呼叫方保證冪等性）。  

---

## 10. 常見錯誤

- ❌ 直接使用 `UPDATE ... SET winbets = [...]` 覆蓋整個 list → 應採用 Cassandra 的 `UPDATE ... SET winbets = winbets + [...]` 執行 APPEND。  
- ❌ 未驗證 `account` 是否為有效會員 → 導致幽靈帳號寫入，需查詢 `member.gameusers` 驗證狀態。  
- ❌ 假設 `winbets` 總是存在 → 首次寫入時應建立新的 list。  
- ❌ 忽略 `restday` 合法性檢查 → 可能寫入不合理數值，影響活動邏輯。  
- ❌ 混淆 `eventname` 與 `activityEvent` 路徑參數 → 在 Cassandra 主鍵中為 `eventname`，路由參數為 `activityEvent`，應正確映射。  

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `README.md` – 特殊活動 POST `/api/v1/special/records/{site}/{activityEvent}` |
| DB Table | `predict.activities_record` – 記錄 site, eventname, account, winbets, restday 欄位 |
| 寫入規則 | `predict-detail.md` – `predictservice` 可 INSERT；`winbets` 僅 APPEND，不可覆寫 |
| 週期驗證（選擇性） | `predict-detail.md` – `activities_cycles` 包含 startdate, starttime, enddate, endtime 供判斷有效性 |
| 驗證需求 | `README.md` 該 API 標記 ✅ (需驗證) |
| 權限設計 | 無明確文件；需人工確認僅後台角色可呼叫（推斷基於 API 用途） |

> 標記「需人工確認」的項目：API 的授權角色、`restday` 的值範圍、`winbets` 的去重機制、對 `account` 存在與活動狀態的強校驗。