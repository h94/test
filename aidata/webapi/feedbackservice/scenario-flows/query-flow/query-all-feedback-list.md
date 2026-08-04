# 管理員查詢所有反饋列表

## 1. 場景目的
讓站台管理員依照站點（sport / stock）與自訂條件（狀態、帳號、時間區間等）查詢所有用戶提報的反饋記錄，並取得對應的主題名稱、處理狀態與最後更新時間，以便於客服追蹤與進度控管。

---

## 2. 入口 API
> 實際 API path 與 HTTP method 需人工確認（推測為後台限定的 GET 端點）

| Method | Path                              | 說明                           |
|--------|-----------------------------------|--------------------------------|
| GET    | `/api/admin/feedbacks?site=...`   | 查詢指定站點反饋列表（推測）   |

---

## 3. 流程總覽
1. 管理後台前端發出請求，攜帶 `site` 參數（`sport` / `stock`）與查詢條件（選填）。
2. 中間件或 Controller 驗證呼叫方是否具備管理員權限（需人工確認驗證機制）。
3. Controller 將參數傳遞給 Service 層。
4. Service 依據 `site` 選擇對應的 DataProvider：
   - `site = sport` → SportFeedbackDataProvider（操作 `feedbacks_sport`）
   - `site = stock` → MessageDataProvider（操作 `feedbacks_stock`）
5. DataProvider 組裝 CQL 查詢，取得符合條件的反饋記錄（僅選取必要欄位）。
6. 需取得每筆反饋所屬主題的名稱，根據 `TID` 查詢對應的主題表：
   - `topics_sport`（sport 站）或 `topics_stock`（stock 站）
7. Service 彙整主題名稱、狀態、時間等資訊，回傳列表至前端。
8. 若查詢成功，HTTP 狀態碼 200，失敗則依錯誤類型回傳對應的錯誤碼。

---

## 4. 程式流程
| 順序 | Layer      | Class / Method                     | 動作                                                   |
|------|------------|------------------------------------|--------------------------------------------------------|
| 1    | Middleware | AuthMiddleware                     | 驗證管理員 token（需人工確認）                          |
| 2    | Controller | FeedbackAdminController.GetList()  | 接收查詢參數（site, status, account, date range...）   |
| 3    | Service    | FeedbackService.GetFeedbackList()  | 依站台指派對應 Provider，組合查詢邏輯                  |
| 4    | Provider   | SportFeedbackDataProvider.Query()  | 查詢 `feedbacks_sport`（sport 站）                     |
| 5    | Provider   | MessageDataProvider.Query()        | 查詢 `feedbacks_stock`（stock 站）                     |
| 6    | Provider   | TopicDataProvider.GetName()        | 取得主題名稱（依據 TID 與站點）                        |
| 7    | Service    | FeedbackService                    | 組裝回應物件，包含主題名稱、狀態、最後更新時間等欄位   |

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源                      | 操作 | 用途                               |
|------|---------------------------|------|------------------------------------|
| DB   | `feedbacks_sport`         | Read | 篩選並撈取運動站反饋紀錄           |
| DB   | `feedbacks_stock`         | Read | 篩選並撈取股票站反饋紀錄           |
| DB   | `topics_sport`            | Read | 取得運動站主題多語言名稱           |
| DB   | `topics_stock`            | Read | 取得股票站主題名稱                 |
| -    | (無使用 Redis / Queue)   | -    | 此查詢流程無快取或訊息佇列         |

---

## 6. 重要規則
- **權限限制**：僅管理員角色可呼叫此 API，需透過 JWT / Session 驗證（具體實作需人工確認）。
- **欄位限制**：反饋列表不可暴露全量 `Problem`、`RespContent` 等長文字；回應時應只回傳摘要（如主題名稱、狀態、時間、帳號等）。
- **不可暴露資料**：圖片路徑 (`ImgPath` / `AdminImgPath`) 若存在，需確認對外是否回傳實際可存取的 URL；管理員列表可能允許，但仍需評估。
- **狀態值限制**：
  - sport 站：`Status` 使用 int（0=未回覆，1=已回覆，2=結束）（需人工確認）
  - stock 站：同上（推測，需人工確認）
- **Transaction 規則**：本查詢為純讀取，不涉及跨表寫入，故無需分散式交易。
- **分頁 / 排序規則**：查詢必須支援分頁（應有 `limit` / `offset` 或 keyset pagination），避免一次性載回大量資料。
- **跨站點查詢限制**：不應允許不指定 `site` 的直接查詢，因為資料分表儲存，強制指定站點可避免全掃描與混淆。

---

## 7. 錯誤情境
| 情境                       | 預期結果                           |
|----------------------------|------------------------------------|
| 未登入或非管理員身分       | 回傳 401 / 403，拒絕存取           |
| site 參數缺失或非法值       | 回傳 400 Bad Request，說明允許值   |
| 時間格式錯誤               | 回傳 400，提示格式要求             |
| ScyllaDB 連線逾時或異常     | 回傳 500 Internal Server Error      |
| 查詢條件導致回傳 0 筆資料   | 回傳 200 OK，空陣列                |

---

## 8. 測試重點
| Test ID | 類型             | 情境                                  | 預期結果                     |
|---------|------------------|---------------------------------------|------------------------------|
| T1      | Permission Test  | 一般使用者呼叫此 API                  | 403 Forbidden                |
| T2      | API Test         | 管理員呼叫，帶合法的 site=sport       | 200，回傳 sport 站反饋       |
| T3      | API Test         | 管理員查詢帶 status=0                 | 回傳僅包含未回覆的記錄       |
| T4      | API Test         | 查詢不存在的 site=unknown             | 400 或明確錯誤訊息           |
| T5      | Flow Test        | 驗證回傳資料是否包含主題名稱          | 每筆記錄含有對應主題名稱     |
| T6      | Flow Test        | 測試分頁參數（limit, offset）         | 正確分頁，無缺漏或重複       |

---

## 9. 高風險區域
- **高風險 table**：`feedbacks_sport` 與 `feedbacks_stock` 為使用者提交的紀錄，若 CQL 查詢未加索引欄位可能造成全表掃描，導致 ScyllaDB 效能瓶頸。
- **跨服務資料同步**：主題資料 (`topics_*`) 由管理後台維護，若名稱更新後未即時反映，可能造成列表顯示不一致，但此為快取層面問題（目前無快取）。
- **Cache consistency**：無使用 Cache，故無此問題。
- **分頁實作風險**：若採用 `LIMIT` / `OFFSET`，大偏移量可能導致效能下降，建議使用 keyset pagination（以 `(site, updatetime)` 為基準）。
- **權限驗證失誤**：若驗證只在前端進行，後端未再次檢查，可能造成未授權存取；務必在 Controller 層強制驗證。

---

## 10. 常見錯誤
- **新人容易犯錯**：未在 CQL 中加上 `ALLOW FILTERING` 或忽略過濾條件順序，觸發 ScyllaDB 掃描，導致高延遲甚至被拒絕查詢。
- **AI 容易誤解**：直接將 `feedbacks_sport` 與 `feedbacks_stock` 當作 MySQL 表使用，誤用 JOIN 或寫入操作（ScyllaDB 僅支援有限 CQL）。
- **常見漏檢查項目**：忘記根據 `site` 選擇對應的主題表，導致主題名稱回傳為 null。
- **常見錯誤流程**：管理員想查詢「全部站點」時，API 未要求必須指定站點，服務嘗試 UNION 兩個表（ScyllaDB 不支援），引發錯誤。因此 API 設計應強制要求 `site` 參數，或提供獨立的匯總端點。

---

## 11. Evidence
| 類型     | 來源                                           |
|----------|------------------------------------------------|
| API      | FeedbackAdminController.GetList()（需人工確認） |
| DB       | `feedbacks_sport`（SportFeedbackDataProvider）  |
| DB       | `feedbacks_stock`（MessageDataProvider）        |
| Code     | SportFeedbackDataProvider.Query()              |
| Code     | TopicDataProvider.GetName()                    |
| SQL      | CQL: `SELECT tid, datetime, account, status, updatetime FROM feedbacks_sport WHERE ...` |
| 權限     | AuthMiddleware（需人工確認其驗證來源）          |