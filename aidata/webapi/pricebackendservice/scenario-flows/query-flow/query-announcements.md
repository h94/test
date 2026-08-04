# 查詢所有公告（後台）

## 1. 場景目的
後台管理員查詢所有已發佈（status=1）及草稿（status=0）的公告，用於列表管理或後續編輯／更新操作。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/advertising/bulletinboard/announcenments` | 查詢所有公告（含草稿與已發佈） |

- 需要驗證：✅（後台管理員 token）
- 無 Query Parameters

---

## 3. 流程總覽

1. 後台管理員呼叫 API，請求中攜帶有效 JWT Token
2. 由 `ECFramework.ECService` 驗證 Token 合法性與權限
3. 若驗證失敗，回傳 401 或 403
4. PriceBackendService 向 `advertisingservice` 發送內部 REST 請求，要求取得公告列表（通常無參數）
5. `advertisingservice` 查詢 `ads.bulletinboard_sport` 表，過濾 `status IN (0, 1)`，依 `addtime` 降序排列
6. `advertisingservice` 回傳公告資料
7. PriceBackendService 組合回應 DTO，確保不回傳內部路徑（如 `imgpath`）時轉換為完整 URL
8. 回傳 `200 OK` 及公告列表

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `AdvertisingController.GetAnnouncements` | 接收 GET 請求，呼叫 Service |
| 2 | Service | `IAdvertisingService.GetAllAnnoucements` | 組合請求參數，呼叫 advertisingservice API |
| 3 | Provider | `AdvertisingProvider` (透過 HttpClient/ECService) | 呼叫下游 `advertisingservice` 的公告查詢端點 |
| 4 | (remote) | `advertisingservice` → `BulletinBoardService` | 查詢 `ads.bulletinboard_sport` where status in (0,1) order by addtime desc |
| 5 | Service | `IAdvertisingService` | 轉換遙測結果為 DTO，處理多語言 fallback、圖片路徑轉 URL |
| 6 | Controller | `AdvertisingController` | 回傳 `ActionResult<IEnumerable<Announcement>>` |

> 實際類名與方法名需人工確認，此推測以常見架構命名為準。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `ads.bulletinboard_sport`（由 advertisingservice 操作） | Read | 查詢 status=0,1 的公告清單，按 addtime 降序排序 |
| Cache (Redis) | 無 | — | 本場景無使用 Redis |

> PriceBackendService 本身不直接操作 DB，所有資料操作均透過下游 REST API。

---

## 6. 重要規則

- **權限限制**：僅後台管理員可呼叫，需攜帶有效後台管理 Token；前台使用者不可查詢草稿公告。
- **欄位限制**：回傳時不可直接暴露 `imgpath`、`mobileimgpath` 等內部儲存路徑，必須轉換為完整 CDN URL。
- **狀態值限制**：查詢條件必須過濾 `status IN (0,1)`，排除下架狀態 `2`。
- **多語言處理**：`maintopic`、`text1` 等為 `map<text,text>`，回傳時應根據前端可接受的語言版本進行 fallback（若無對應語言則回傳預設語系）。
- **不可修改欄位**：本 API 僅讀取，不回傳任何敏感設計欄位（如 `announcementmethod` 等內部用欄位）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未提供 Token 或 Token 無效 | 401 Unauthorized |
| Token 有效但權限不足（非後台管理員） | 403 Forbidden |
| advertisingservice 無法連線或回應錯誤 | 502 Bad Gateway 或自定義錯誤碼 |
| advertisingservice 查詢超時 | 504 Gateway Timeout |
| 公告資料不完整（如缺少 must-have 欄位） | 200 但回傳空陣列或忽略該筆（應記錄 error log） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | API Test | 後台管理員帶有效 Token 查詢 | 200 OK，回傳陣列包含 status=0 與 status=1 的公告 |
| T2 | API Test | 回傳公告中不含 status=2 的項目 | 陣列無 status=2 的 item |
| T3 | API Test | 公告順序依照 `addtime` 降序排列 | 第一筆時間最新 |
| T4 | Permission Test | 一般使用者 Token 呼叫 | 403 Forbidden（因無後台權限） |
| T5 | Flow Test | advertisingservice 回傳空列表 | 200 OK，回傳空陣列 |
| T6 | Integration Test | 圖片路徑轉換為 CDN URL | 公告物件的 `ImgPath` 為完整 https URL |
| T7 | Integration Test | 多語言欄位依據 Accept-Language 或固定語系回傳 | 公告內容顯示正確語言 |

---

## 9. 高風險區域

- 無直接 DB 操作，風險在於下游 `advertisingservice` 的可用性及回應時間；需有 timeout 與 retry 機制。
- 公告內容可能包含使用者上傳的連結（如 `tageturl`），回傳時應確保無 XSS 風險。
- `advertisingservice` 若因內部錯誤回傳 status=2 的下架公告，後台列表有可能顯示不該出現的資料，需主動防禦（本 API 應在收到後可再次過濾 status）。

---

## 10. 常見錯誤

- ❌ 後端直接回傳 `imgpath` 原始路徑，導致前端無法顯示圖片。
- ❌ 查詢時未過濾 status，可能拿到已下架（status=2）的公告干擾後台操作。
- ❌ 忘記處理多語言 map 的 fallback，導致部分語言顯示空白。
- ❌ 認為本服務直接讀取 DB，但實際是呼叫 advertisingservice，導致在新人實作時誤建 DB 連線。
- ❌ 未對 advertisingservice 回應做空值防禦，若公告物件缺少某欄位可能引發 NullReferenceException。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | README.md：`GET /api/v1/advertising/bulletinboard/announcenments` |
| DB Table | `ads.bulletinboard_sport`（由 advertisingservice 管理，Schema 見 `db/ads.md`） |
| DB Status Rule | `db/ads-detail.md`：公告 status 0=草稿, 1=發布, 2=下架；後台查詢使用 status IN (0,1) |
| Service Role | `pricebackendservice-detail.md`：本服務不直接存取 DB，透過 REST 呼叫 advertisingservice |
| Auth Requirement | README.md：所有公告管理 API 皆需要驗證 |
| Response Structure | OpenAPI：`GET /api/v1/advertising/bulletinboard/announcenments` 回傳 `array[Announcement]` |
| Code | （需人工確認）推測 Controller `AdvertisingController` 與 Service `IAdvertisingService.GetAllAnnoucements` |

---

## 建議新增文件或規則

- **建議新增規則**：公告查詢回應應明確排除 `announcementmethod`、`lastup_time` 等非必要欄位。
- **建議新增測試情境**：advertisingservice 回應延遲超過 timeout 是否能正確回傳 504，並記錄 trace log。