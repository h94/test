# 查詢社群群組

## 1. 場景目的

供用戶或系統取得社群群組清單，包含群組名稱、類型、圖示、排序等基本資訊，前端可依據群組類型（官方、個人、VIP 等）與排序序號進行展示，無需登入即可查詢（需人工確認）。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | /api/Community/Groups（需人工確認） | 取得所有啟用中的社群群組列表，支援依 Seq 排序 |

---

## 3. 流程總覽

1. 接收 HTTP GET 請求，不帶任何必填參數（可能接受 opt 分頁或排序參數，需人工確認）
2. 檢查請求參數合法性（若存在）
3. 呼叫 CommunityDataProvider 查詢 `Community_Groups` 表，過濾條件 `Enabled = 1`（需人工確認是否過濾）
4. 依 `Seq` 升冪排序，可能依前端需求調整（需人工確認排序規則）
5. 回傳群組列表 JSON，每個群組包含 ID、Name、IconPath、GType、Description、Owner 等欄位
6. 若無任何群組，回傳空陣列與 HTTP 200

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | CommunityController.GetGroups（需人工確認） | 接收請求，呼叫 Service |
| 2 | Service | CommunityService.GetGroups（需人工確認） | 呼叫 Provider 取得群組資料 |
| 3 | Provider | CommunityDataProvider.GetGroups（需人工確認） | 執行 SQL 查詢 `Community_Groups`，依 Enabled=1 與排序條件 |
| 4 | Controller | （同上） | 將結果序列化為 JSON，回傳 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Community_Groups | Read | 取得群組基本資訊與排序 |

*未發現使用 Redis、Queue 或其他外部服務的證據。若存在快取，需人工確認。*

---

## 6. 重要規則

- **權限限制**：此查詢場景可能無需身份驗證，即任何訪客皆可取得群組列表（需人工確認實際權限設計）。
- **欄位限制**：回傳資料中不可包含敏感資訊（如內部擁有者帳號是否暴露，目前 `Owner` 欄位可能為個人帳號，需依業務決定是否遮蔽或僅對管理員顯示）。
- **不可暴露資料**：避免洩漏未啟用的群組（Enabled=0）或其他內部標記。
- **TTL 規則**：無快取則無 TTL 限制，若有快取需定義 TTL（需人工確認）。
- **Transaction 規則**：純讀取操作，不需 Transaction。
- **Retry 規則**：資料庫查詢失敗時，視重試機制處理（應於 Provider 層實作，需人工確認）。
- **狀態值限制**：`Enabled` 僅限 0 或 1，`GType` 應符合列舉值（official、normal、vip、personal、test）。
- **不可修改欄位**：查詢為唯讀，無修改行為。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 資料庫連線失敗 | HTTP 500，記錄錯誤，不回傳資料 |
| 資料表不存在 | HTTP 500，觸發系統告警 |
| 查詢回傳空集合 | HTTP 200，回傳空陣列 [] |
| 請求參數格式錯誤（若有排序或分頁參數） | HTTP 400，回傳錯誤訊息 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | API Test | 呼叫 API，無任何參數，資料庫有多筆啟用群組 | 回傳所有群組，排序依 Seq |
| T2 | API Test | 無任何群組 | 回傳 []，HTTP 200 |
| T3 | API Test | 資料庫中有停用群組（Enabled=0） | 停用群組不出現在回應中 |
| T4 | Permission Test | 未帶 AuthKey 呼叫 | 允許存取（若設定為公開） |
| T5 | Flow Test | DB 發生逾時 | 500，有 Log，服務不中斷 |

---

## 9. 高風險區域

- **高風險 table**：`Community_Groups` – 包含群組類型與擁有者，誤暴露可能引發資安問題。
- **高風險 API**：無寫入操作，風險較低；但若權限判斷有誤，可能洩漏未公開群組。
- **跨服務資料同步**：未發現跨服務寫入行為。
- **Transaction / Cache consistency / Queue retry / Idempotency**：本場景不涉及。

---

## 10. 常見錯誤

- 新人容易在 Provider 層忘記過濾 `Enabled = 1`，導致前台顯示停用群組。
- AI 容易誤將所有欄位全量輸出，未考量 `Owner` 是否可對外顯示。
- 常見漏檢查項目：未限制 `GType` 列舉值，若未來新增類型可能無法識別。
- 常見錯誤流程：將排序參數直接拼接 SQL，造成 SQL Injection 風險（需使用參數化查詢，需人工確認現有實作方式）。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | 需人工確認（推測為 CommunityController.GetGroups）|
| DB | Community_Groups (fields: ID, Name, Enabled, IconPath, GType, Owner, Description, Seq, UpdateTime) |
| Code | 需人工確認 Service / Provider（推測 CommunityService.GetGroups, CommunityDataProvider.GetGroups） |
| SQL | 需人工確認（推測為 SELECT * FROM Community_Groups WHERE Enabled = 1 ORDER BY Seq） |

---

## 需人工確認項目

- API 實際路由與 Controller 方法名稱
- 是否需要 AuthKey 才能查詢
- 是否支援分頁或篩選 GType
- 查詢是否有快取機制
- `Owner` 欄位是否對外暴露
- SQL 查詢是否使用參數化