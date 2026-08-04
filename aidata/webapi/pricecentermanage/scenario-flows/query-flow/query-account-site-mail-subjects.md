# 查詢帳號站內信主旨

## 1. 場景目的

後台管理員查詢指定帳號的所有站內信主旨與讀取狀態，優先從 Redis 快取 `SiteMails_{account}` 讀取；若快取未命中，則查詢 MySQL `sport.notification_sitemails` 表。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | `/api/v1/sport/notifications/sitemails/{account}/subjects` | 查詢帳號站內信主旨 |

---

## 3. 流程總覽

1. 接收 API request，取得 `account` 路徑參數
2. 驗證管理者 JWT token（ECFramework.ECService 驗證）
3. 嘗試從 Redis (`SportAccountCache`) 讀取 `SiteMails_{account}` Hash
4. 若 Redis 命中，直接回傳所有 fields (mail id → `SportSiteMailSubjectCache` JSON)
5. 若 Redis miss：
   - 查詢 MySQL `sport.notification_sitemails` WHERE `Account = {account}`
   - 選取 `ID`, `Subject`, `ReadStatus`
   - 將結果轉換為 `SportSiteMailSubjectCache` list
   - 寫回 Redis `SiteMails_{account}` Hash（永久 TTL）
   - 回傳結果
6. 回傳 JSON array of `SportSiteMailSubjectCache`

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `NotificationController.GetSiteMailSubjects` | 接收 account 參數，呼叫 Service |
| 2 | Service | `SportNotificationService.GetSiteMailSubjects` | 嘗試 Redis GET `SiteMails_{account}` |
| 3 | Service | `SportNotificationService.GetSiteMailSubjects` | 若 Redis miss：呼叫 Provider |
| 4 | Provider | `SportNotificationProvider.GetSiteMailSubjectsByAccount` | 查詢 MySQL `notification_sitemails` WHERE `Account = ?` |
| 5 | Provider | - | SELECT `ID`, `Subject`, `ReadStatus` |
| 6 | Service | `SportNotificationService.GetSiteMailSubjects` | 轉換為 `SportSiteMailSubjectCache` DTO |
| 7 | Service | `SportNotificationService.GetSiteMailSubjects` | Redis SET `SiteMails_{account}` fields |
| 8 | Service | `SportNotificationService.GetSiteMailSubjects` | 回傳 DTO list |

※ 需人工確認：實際 Service / Provider 命名。

---

## 5. DB / Cache 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| Redis | `SportAccountCache`:`SiteMails_{account}` | GET | 讀取帳號站內信主旨快取 |
| Redis | `SportAccountCache`:`SiteMails_{account}` | SET | 寫入帳號站內信主旨快取（永久 TTL） |
| DB (MySQL) | `sport.notification_sitemails` | SELECT | 當 Redis miss 時，依 Account 查詢站內信主旨與讀取狀態 |

---

## 6. 重要規則

- **權限限制**：此 API 必須通過 ECFramework.ECService 驗證，僅供後台管理者使用
- **參數限制**：`account` 為必填路徑參數，不可為空
- **不可暴露資料**：`Content` 欄位絕對不可在此 API 回傳；僅回傳 `ID`、`Subject`、`ReadStatus`
- **TTL 規則**：`SiteMails_{account}` Redis Key 無 TTL（永久），由後續站內信狀態更新或刪除時主動 `DEL` 或 `HDEL` field
- **查詢限制**：必須以 `Account` 主鍵精確匹配，不可跨帳號查詢
- **回傳格式**：回傳 `SportSiteMailSubjectCache` 物件列表，包含 `ID`、`Subject`、`ReadStatus`（0=未讀, 1=已讀）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| account 不存在或無站內信 | 回傳空陣列 `[]`，HTTP 200 |
| Redis 連線失敗或 GET 錯誤 | 降級查詢 MySQL（不中斷流程） |
| MySQL 查詢失敗 | HTTP 500 |
| 未帶驗證 token | HTTP 401 |
| token 無效/過期 | HTTP 401 |
| account 格式無效（如包含特殊字元） | 需人工確認：參數驗證邏輯 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SM-01 | API Test | 查詢存在帳號（有站內信） | 回傳主旨列表與讀取狀態 |
| SM-02 | API Test | 查詢不存在帳號 | 回傳空陣列 |
| SM-03 | Cache Test | Redis 快取命中 | 不回源 DB，直接回傳 |
| SM-04 | Cache Test | Redis 快取未命中 | 回源 DB 後寫入快取 |
| SM-05 | Permission Test | 未帶 token | HTTP 401 |
| SM-06 | Resilience Test | Redis 斷線 | 降級查詢 DB，不影響回應 |
| SM-07 | Data Test | 驗證 Content 不回傳 | 回應 body 不包含 `Content` 欄位 |

---

## 9. 高風險區域

- **Redis 快取一致性**：若站內信更新（新增、刪除、讀取狀態變更）時未主動 `DEL` 或 `HDEL` `SiteMails_{account}`，將導致前端看到過期資料
- **Redis 從未失效**：此 Key 無 TTL，若未正確刪除，快取可能永久留存
- **帳號隱私**：必須確保 `Account` 參數不會洩漏其他用戶的站內信主旨

---

## 10. 常見錯誤

- ❌ **直接查詢 MySQL 而不嘗試 Redis 快取** → 增加 DB 負載，違反設計意圖
- ❌ **更新站內信後未刪除 Redis 快取** → API 回傳舊資料
- ❌ **回傳包含 `Content`** → 列表 API 不可回傳全文內容
- ❌ **對 `account` 做模糊查詢或全表掃描** → 必須精確匹配 `Account` 主鍵
- ❌ **未處理 Redis 連線失敗例外** → 應降級查 DB，避免中斷

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | GET `/api/v1/sport/notifications/sitemails/{account}/subjects` (README / OpenAPI) |
| Redis | `SiteMails_{account}` Hash (pricecentermanage-detail.md Redis 操作) |
| DB | `sport.notification_sitemails` (MySQL Schema) |
| DB 規則 | `notification_sitemails` 不可回傳 Content (sport-detail.md) |
| DTO | `SportSiteMailSubjectCache` (OpenAPI response schema) |
| 服務角色 | pricecentermanage writer/reader for sitemails (sport-detail.md) |
| 驗證 | ECFramework.ECService 2.0.0 (README) |