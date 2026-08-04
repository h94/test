# 查詢當前活動週期

## 1. 場景目的
提供前端查詢指定活動（activity event）在當前時間有效的活動週期設定。用於判斷活動是否進行中、取得週期編號（cid）以進行後續投注、排行榜等操作。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/activity/cycles/{site}/{activityEvent}/now` | 查詢當前有效的活動週期 |

---

## 3. 流程總覽

1. API 接收路徑參數 `site` 與 `activityEvent`
2. 由 Controller 調用對應 Service（推測為 `ActivityProcess.GetNowActivityCycleSetting`）
3. Service 透過 Cassandra Provider 查詢 `predict.activities_cycles` 表，條件 `site = ? AND activityevent = ?`
4. 對查詢結果集，逐一比對當前時間是否落於 `startdate`/`starttime` 至 `enddate`/`endtime` 區間內
5. 取第一筆符合時間範圍的記錄（或僅回傳該筆）
6. 若無符合記錄則回傳錯誤（推估 404）
7. 將結果映射為 `ActivityCycleSettingDTO` 回傳

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `ActivityController`（推測） | 接收參數，呼叫 Service |
| 2 | Service | `ActivityProcess.GetNowActivityCycleSetting`（推測） | 組合查詢條件，呼叫 Provider |
| 3 | Provider | `ActivityProvider`（推測） | 執行 Cassandra 查詢 |
| 4 | DB | `predict.activities_cycles` | 讀取指定 site 與 activityevent 的所有 cid 記錄 |
| 5 | Service | `ActivityProcess` | 在應用端過濾時間範圍，選擇有效週期 |
| 6 | Controller | 同上 | 將結果序列化回傳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.activities_cycles` | Read | 查詢活動週期記錄 |
| Redis | （目前無使用） | - | 無快取機制 |

> **需人工確認**：是否已在某版本加入 Redis 快取（如 `activity:cycle:{site}:{event}`）來降低 Cassandra 查詢頻率；目前所有來源皆未提及。

---

## 6. 重要規則

- **唯讀**：本服務僅讀取 `activities_cycles`，不可寫入或修改（週期設定由排程或管理後台負責）
- **時間判斷**：使用 Cassandra 查詢 `site` 與 `activityevent` 作為分區鍵，由於無法在 DB 層過濾時間欄位，必須在應用層逐一比對 `startdate/starttime` 與 `enddate/endtime`
- **唯一有效週期**：一次活動一次只有一個週期處於進行中，若有重疊則依定義僅回傳第一個符合的記錄（或報錯，需人工確認策略）
- **時區與格式**：`startdate`、`enddate` 為日期字串，`starttime`、`endtime` 為時間字串；需與當前伺服器時間比對，確保使用相同時區（通常為 UTC）
- **敏感資訊**：回傳的 DTO 不得包含內部稽核欄位（如 `resultcount` 可能僅內部使用，需確認是否對外回傳）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 找不到符合 `site` 或 `activityevent` 的資料 | 回傳空陣列或 404（需確認規格） |
| 存在記錄，但無任何一筆 `startdate <= now <= enddate` | 回傳 404 或特定錯誤碼（例如「活動尚未開始」或「已結束」） |
| 時間格式錯誤或 Cassandra 查詢逾時 | 回傳 500 系統錯誤 |
| 多筆記錄同時符合（理論上不該發生） | 取 cid 最小或最早開始的記錄，並記錄警告 log |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | API Test | 提供當前有效的 site/event，時間落在週期內 | 回傳 200，包含正確 cid 與時間 |
| T2 | API Test | 活動尚未開始（startdate > now） | 回傳 404 或相關錯誤訊息 |
| T3 | API Test | 活動已結束（enddate < now） | 回傳 404 或相關錯誤訊息 |
| T4 | API Test | site 或 activityevent 不存在 | 回傳 404 |
| T5 | Permission Test | 確認此 API 無需 authKey（若為公開） | 未登入也可成功呼叫（需人工確認） |
| T6 | Flow Test | DB 中僅有一筆 cid=1，時間包含現在 | 確保應用層過濾正確，不可因 cid 順序跳過 |

---

## 9. 高風險區域

- **時間比較邏輯**：若 `startdate`/`enddate` 格式不一致或未考慮時區，可能誤判活動狀態，導致前端不顯示或錯誤開放
- **Cassandra 全 partition 掃描**：查詢時必須提供 `site` 與 `activityevent`，否則可能導致跨分區掃描；此處已遵守，風險低
- **無快取**：大量請求可能直接打在 Cassandra 上，可評估加入本地快取（System.Runtime.Caching）或 Redis，但需注意活動時間變更時的快取失效策略
- **週期重疊**：若管理後台誤建多重疊週期，應用層僅取第一筆可能引發錯誤；建議增加防禦性檢查並記錄告警

---

## 10. 常見錯誤

- ❌ 未在應用層過濾時間，直接回傳查詢到的第一筆（可能為過期或未開始）  
- ❌ 時間比對使用不符合的字串格式（例如用 `DateTime.Parse` 未指定 Culture）  
- ❌ 將 `resultcount` 等內部欄位直接回傳給前端  
- ❌ 假設 `cid` 總是遞增代表時間順序，但業務上可能跳號  
- ❌ 忘記處理 `NULL` 或空字串的 `startdate`/`enddate`

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `ActivityController` — 由 OpenAPI path `/api/activity/cycles/{site}/{activityEvent}/now` 推斷 |
| DB | `predict.activities_cycles` — 來自 schema 與 db-usage 描述 |
| 讀取規則 | `db-usage` — 活動週期查詢需 `site=? AND activityevent=?` 且應用層過濾時間 |
| 服務角色 | `pricecentersite-detail.md` — predict 段中本服務僅讀取 `activities_cycles`，不寫入 |
| 流程 | 推測 `ActivityProcess.GetNowActivityCycleSetting` 方法 — 來自 `db-usage` 中的方法名稱 |

> **需人工確認**：
> - 實際 Controller 類別名稱與方法簽名
> - 錯誤回應格式（直接 404 或是包裝成特定 DTO）
> - 是否需要登入驗證（OpenAPI 未顯示強制 Token）
> - 是否已存在 Redis 快取機制