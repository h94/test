# 建立冠軍賽周期

## 1. 場景目的

後台管理員在冠軍賽活動開始前，於系統中建立一個新的活動週期記錄（包含站點、活動事件、週期編號、起訖時間），供後續競猜、結算與排行榜使用。本流程為後台 BFF（PriceBackendService）接收請求，轉交下游微服務寫入 `predict.activities_cycles` 資料表。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/member/supreme/cycles` | 建立冠軍賽週期 |

> 依 README 路由表，此 API 需驗證（✅）。

---

## 3. 流程總覽

1. 後台前端發出 POST 請求，攜帶 `site`、`activityEvent`、`cid`、`startDate`、`endDate` 等參數。
2. `PriceBackendService` 中介層驗證請求格式與操作權限。
3. 將請求轉換為下游服務所需的 DTO，呼叫下游服務（推測為 `predictservice` 或經由 `memberservice` 間接呼叫）。
4. 下游服務檢查資料合法性（例如週期是否已存在、時間範圍是否合理）。
5. 通過檢查後，於 `predict.activities_cycles` 表寫入一筆新週期記錄。
6. 回傳成功結果給前端。

⚠️ 下游服務實際呼叫鏈（是否直接 `predictservice` 或透過 `memberservice`）需人工確認，目前文件顯示 `activities_cycles` 位於 `predict` keyspace，而 README 中冠軍賽週期功能歸在 `memberservice` 相依項下，可能為內部轉發。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `MemberController.CreateSupremeCycle`（推測） | 接收請求，驗證 model 有效性 |
| 2 | Service（應用層） | `MemberService.CreateSupremeCycle`（推測） | 轉換 DTO，調用下游客戶端 |
| 3 | Provider / Client | `IMemberGameService` 或 `IPredictService` 介面實作 | 發送 HTTP/gRPC 請求到下游微服務 |
| 4 | 下游服務 | `predictservice` 或 `gamecombineservice` 的對應端點 | 權限驗證、業務校驗、寫入 Cassandra |

> 因缺少 source code，以上類別與方法名稱為基於常見命名慣例推測，實際名稱**需人工確認**。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `predict.activities_cycles` | Write（INSERT） | 新建冠軍賽週期記錄 |

- 暫無發現使用 Redis 快取或 Kafka Queue 於此流程。
- 若後續需快取週期列表，應於新建後主動清除相關快取 key（如 `predict:activity:{site}:{eventname}:*`），見 predict-detail Redis 段落。

---

## 6. 重要規則

- **權限限制**：僅後台管理員可呼叫，一般使用者無權。
- **複合主鍵不可變**：`site`、`activityevent`、`cid` 在建立後**不允許任何更新**（predict-detail 寫入限制）。
- **時間欄位保護**：`startdate`、`starttime`、`enddate`、`endtime` 由服務端根據請求參數計算後寫入，API 不可直接設定原始字串（predict-detail）。推測請求應只傳入業務日期／時間，由下游服務轉成內部格式並校驗。
- **不可手動寫入 `resultcount`**：該欄位由系統在結算時自動累加，新建時應為 0 或不寫入。
- **冪等性**：若重複以相同 `(site, activityevent, cid)` 提交，應回傳「已存在」錯誤，不可覆蓋。
- **不允許跨服務直接 INSERT**：根據架構，本服務不直接存取 DB，所有寫入必須透過下游 REST API 完成。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 缺少必填欄位（如 site 或 cid） | 回傳 400 Bad Request，附註錯誤欄位 |
| 該週期 (`site`, `activityevent`, `cid`) 已存在 | 回傳 409 Conflict 或業務錯誤代碼（重新建立前需先刪除？依業務規則，**需人工確認**） |
| startDate 晚於 endDate | 回傳 422 或 400，提示時間區間不合理 |
| 使用者無管理權限 | 回傳 401 或 403 |
| 下游 predictservice 呼叫逾時 | 回傳 504 Gateway Timeout；BFF 不可重試寫入以避免重複建立（需下游支援冪等） |
| Cassandra 寫入失敗（例如 partition key 衝突） | 下游服務回傳 500，BFF 轉發為 502 Bad Gateway |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| SC-01 | API Test | 正常建立一個完整週期 | 回傳 200，資料庫查詢到該週期且 `resultcount=0` |
| SC-02 | Permission Test | 使用一般使用者 token 呼叫 | 回傳 403 |
| SC-03 | Flow Test | 重複以相同參數建立 | 回傳非 200（如 409），且 DB 中只有一筆記錄 |
| SC-04 | Validation Test | 傳入 `endDate < startDate` | 回傳 400 或 422，訊息明確 |
| SC-05 | Integration Test | 模擬下游服務 unavailable | BFF 回傳 502，前端顯示錯誤，不重複寫入 |

---

## 9. 高風險區域

- **資料一致性**：若 BFF 收到下游成功回應後卻因網路問題無法回傳前端，前端可能重試，需依靠下游服務的冪等性（基於複合主鍵）避免重複寫入。
- **時間格式轉換**：前端傳入的日期格式與 Cassandra 儲存格式（`text`）若不一致，可能導致查詢失敗；需在 BFF 或下游強制轉換（**需人工確認格式規範**）。
- **跨服務相依**：`activities_cycles` 寫入成功後，若有其他服務依賴此週期（如活動商品、排程結算），則須確保這些服務能正確讀取新週期，可能涉及快取清除（目前無觀察到相關機制，**需人工確認**）。

---

## 10. 常見錯誤

- ❌ 前端直接傳入 `starttime`、`endtime` 字串並期望原樣寫入 → 違反 predict-detail 限制，應由服務端產生。
- ❌ 開發者或 AI 誤以為 `resultcount` 可在建立時設定 → 新建應為 0，否則導致後續結算錯誤。
- ❌ 未檢查 `activityevent` 是否為系統預定義的活動事件名稱 → 可能建立無效週期，影響後續流程。
- ❌ 誤將此 API 視為可直接操作 DB 的端點 → PriceBackendService 不直接存取資料庫，必須走下游服務，否則違反架構設計。
- ❌ 未處理重複建立時的錯誤響應，導致前端或測試誤判為成功。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由與方法 | README · `/api/v1/member/supreme/cycles` |
| 服務相依 | README · 相依服務 `memberservice`（負責冠軍賽周期） |
| DB 寫入限制 | `db/predict-detail.md` · activities_cycles 寫入限制段落 |
| BFF 不直接存取 DB | README · 職責「本服務不直接存取資料庫」 |
| 複合主鍵不可變 | `db/predict-detail.md` · activities_cycles.site、activityevent、cid |
| 時間欄位禁止直接寫入 | `db/predict-detail.md` · startdate、starttime…API 不可直接修改 |
| `resultcount` 自動更新 | `db/predict-detail.md` · activities_cycles.resultcount |
| 需驗證 | README API 表標記 ✅ |
| 無 Redis / Kafka 使用 | 現有 detail 文件中未提及相關快取或佇列 |

> ⚠️ 缺少部份 code evidence（Controller / Service 具體實作），目前流程基於架構文檔推導。**建議取得 `pricebackendservice` 的 `MemberController` 與下游 client 宣告以補足詳細呼叫鏈。**