# 查詢單封站內信內容

## 1. 場景目的

管理後台人員查詢指定帳號的某一封站內信完整內容，包含信件主旨、發送時間、內容與已讀狀態。此流程用於客服查證或內容審查。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sport/notifications/sitemails/{account}/{id}` | 查詢指定帳號及信件 ID 的完整內容 |

---

## 3. 流程總覽

1. 接收 request，取得路徑參數 `account` 與 `id`。
2. 透過 ECFramework 驗證呼叫端擁有管理後台權限。
3. Controller 呼叫 SportService 的 `GetSitemailAsync(account, id)` 方法。
4. Service 層直接透過 Repository（或 Provider）查詢 MySQL Sport DB 的 `notification_sitemails` 表（不經過 Redis 快取）。
5. 將 `Subject`、`SendTime`、`Content`、`ReadStatus` 等欄位組裝為 DTO 回傳。
6. 回傳 200 OK 與信件內容。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware | ECFramework | 驗證 Token 權限，確保為後台管理員身份 |
| 2 | Controller | `NotificationController.GetSitemailByAccount` | 接收 `account`、`id` 參數 |
| 3 | Service | `SportService.GetSitemailAsync(account, id)` | 呼叫 DataProvider 查詢 DB |
| 4 | Provider | `SportDataProvider.GetSitemailAsync(account, id)` | 使用 SQL 查詢 `notification_sitemails` 表 |
| 5 | Transfer | `SportSiteMailDTO` | 將 DB Model 轉換為 API 回傳物件（需妥適處理 Content 欄位） |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | MySQL `sport.notification_sitemails` | Read | 依 `Account` 與 `ID` 精確查詢信件完整內容 |
| Redis | ❌ 不使用 | - | 主旨列表快取用於其他列表 API，本單封查詢流程不命中 Redis |

---

## 6. 重要規則

- **權限限制**：僅限管理後台人員操作，前端會員不可存取後台 API；需由 ECFramework 驗證。
- **欄位限制**：單封查詢可回傳 `Content` 欄位，但此為高敏感資料，不可在列表型查詢（如 `/subjects`）中回傳。
- **不可暴露資料**：API 回傳不得包含 `notification_sitemails` 表中無關欄位（若存在）。
- **Account 查詢規則**：須以 `Account` 精確匹配，不可跨帳號查詢；`Account` 為 partition key。
- **不可修改規則**：此 API 為純讀取查詢，禁止 Create/Update/Delete 操作。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 呼叫端未攜帶合法 Token | 回傳 401 Unauthorized |
| Token 權限不足（非管理後台角色） | 回傳 403 Forbidden |
| 指定的 `account` 不存在 | 回傳 404 Not Found 或空結果 |
| 指定的 `id` 不存在於該帳號下 | 回傳 404 Not Found 或空結果 |
| SQL 連線Timeout或Cassandra超時（若誤用） | 回傳 500 Internal Server Error |
| `account` 參數為空字串 | 回傳 400 Bad Request |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| IT-1 | Integration Test | 正常查詢存在的 `account` + `id` | 200 OK，回傳完整信件 DTO |
| IT-2 | Permission Test | 使用一般會員 Token 呼叫 | 403 Forbidden |
| IT-3 | API Test | 查詢不存在的 `id` | 404 Not Found |
| IT-4 | Flow Test | 模擬 SQL 時間異常 | 500 Internal Server Error |
| IT-5 | API Test | `account` 路徑參數為空 | 400 Bad Request |
| IT-6 | Data Privacy Test | 檢查回傳的 `Content` 欄位是否存在 | `Content` 存在且為 string |

---

## 9. 高風險區域

- **高風險 API**：此 API 直接暴露用戶私人訊息全文（`Content`），授權驗證為高風險點，需嚴格確保只有適當的管理角色可呼叫。
- **DB 查詢**：須以 `Account` 為主鍵查詢，避免因實作錯誤導致全表掃描，影響 MySQL 效能。
- **Sensitive Data Logging**：服務端記錄 Log 或錯誤訊息時，必須避免將 `Content` 欄位寫入 log，防止個資洩漏。

---

## 10. 常見錯誤

- ❌ 忘了在列表 API（`/subjects`）中排除 `Content`，但在單封查詢中卻必須包含 `Content`。兩者的回傳物件若共用，需小心設定 `[JsonIgnore]` 條件。
- ❌ Service 層多餘的快取邏輯：新手可能誤將單封查詢結果也寫入 Redis，但原有架構中主旨列表才有快取（`SiteMails_{account}`），單封內容應直讀 DB。
- ❌ 誤用 Cassandra `pricecenter` 或 `predict` keyspace 查表，正確資源為 MySQL `sport` 資料庫。
- ❌ 忘記檢查 `notification_sitemails` 的 `ReadStatus` 欄位是否有格式錯誤（非 0 或 1），若出現異常值需做防禦性轉換或報錯。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `NotificationController` (推測) `GetSitemailByAccount` 或 `GetSiteMail` |
| DB | MySQL Sport `notification_sitemails` (schema confirmed) |
| Code | `SportService.GetSitemailAsync` (推測) 搭配 `SportDataProvider` |
| DB Detail | `sport-detail.md` 規範：僅單筆詳細查詢時提供 `Content` |
| DB Detail | `pricecentermanage-detail.md` 確認該服務對 `notification_sitemails` 有寫入及讀取權限 |
| Code Semantics | batch 分析確認 `notification_sitemails` 欄位語意 (`Account`, `ID`, `Subject`, `SendTime`, `Content`, `ReadStatus`) |