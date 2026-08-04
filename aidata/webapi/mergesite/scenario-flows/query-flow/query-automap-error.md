# 查詢聯盟自動比對錯誤紀錄

## 1. 場景目的

讓營運人員查看自動比對系統標記的聯盟（League）對應異常清單，藉此確認哪些聯盟配對需要人工介入，並驅動後續的強制合併操作（`POST /api/merge/leagues/{gameType}`）。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/system/automapteam/check` | 取得聯盟自動比對錯誤紀錄 |

> 需人工確認：API 是否接受 `gameType` 或其他過濾參數；目前 OpenAPI 未收錄此端點細節。

---

## 3. 流程總覽

1. 營運人員進入後台，發送 `GET /api/system/automapteam/check` 請求。
2. ECCore 驗證權限，只允許已授權的後台使用者。
3. Controller 轉交請求至對應的 Service。
4. Service 透過 Gateway 呼叫 **PriceCenterService** 的內部 API，取得原始比對錯誤紀錄（`AutoMapErrorLog` 模型）。
5. 若回傳資料非空，mergesite 將原始紀錄依 `LID`（主庫聯盟 ID）進行分組，轉換為前臺專用的彙總結構（`AutoMapErrorLogForUI`）。
6. 若無錯誤紀錄，回傳空集合。
7. 應用程式 Log 事件透過 **Kafka** 發送（不影響主要回應）。
8. 回傳 `200 OK` 與 `AutoMapErrorLogForUI` 清單給前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method（推測） | 動作 |
|------|-------|-----------------------|------|
| 1 | Controller | `SystemController` or `AutoMapController` | 接收 GET 請求，調用 `ECC Authorize` |
| 2 | Service | `AutoMapService.CheckLeagues()` | 調用 `PriceCenterService` 取得原始錯誤紀錄清單 |
| 3 | Provider | `PriceCenterGateway` | 發送 HTTP 請求至 `192.168.55.60` 的內部 API |
| 4 | Service | `AutoMapService.CheckLeagues()` | 將 `List<AutoMapErrorLog>` 依 `LID` 分組，映射為 `List<AutoMapErrorLogForUI>` |
| 5 | Controller | `SystemController` | 回傳 `JsonResult` 或 `Ok(result)` |

> 需人工確認：實際 Controller / Service 名稱與方法簽名。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| REST API | PriceCenterService | Read | 讀取比對錯誤紀錄原始資料 |
| Kafka | 應用程式 Logs | Publish（非同步） | 記錄操作軌跡，不影響回傳流程 |

**mergesite 本身無直接 DB 操作**，所有資料來自 PriceCenterService。

---

## 6. 重要規則

- **權限限制**：必須通過 `ECCore` 驗證，僅後臺授權使用者可存取。
- **分組邏輯**：回傳前須將原始錯誤紀錄依 `LID` 彙總，確保 `MapErrorSiteLeagues` 正確對應至各主庫聯盟。
- **不可暴露原始內部結構**：不可直接回傳 `AutoMapErrorLog`（含內部 `SiteLID`、`ErrType` 等未過濾欄位），應使用 `AutoMapErrorLogForUI` 輸出。
- **無快取機制**：未使用 Redis，每次請求皆即時查詢 PriceCenterService。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未通過 ECCore 驗證 | 回傳 `401` 或 `403` |
| PriceCenterService 無回應（網路 / 超時） | 回傳 `502 Bad Gateway` 或 `504 Gateway Timeout` |
| PriceCenterService 回傳內部錯誤 | 依錯誤碼回傳對應的 `4xx/5xx`，並發送 Log 至 Kafka |
| 無任何比對錯誤紀錄 | 回傳 `200 OK`，內容為空的 `AutoMapErrorLogForUI` 陣列 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| AUTOMAP-FLOW-01 | API Test | 不帶驗證 Headers 請求 | `401 Unauthorized` |
| AUTOMAP-FLOW-02 | Flow Test | PriceCenterService 回傳正常資料（含多筆同 LID） | `200`，`MapErrorSiteLeagues` 分組正確 |
| AUTOMAP-FLOW-03 | Integration Test | PriceCenterService 回傳空列表 | `200`，body 為 `[]` |
| AUTOMAP-FLOW-04 | Flow Test | PriceCenterService 延遲或 500 | mergesite 回傳 502/504，並記錄錯誤 Log |

---

## 9. 高風險區域

- **跨服務同步查詢**：強依賴 `PriceCenterService` 可用性；若其移除或 schema 變更，mergesite 可能直接報錯。
- **大量資料效能**：若某一 gameType 下比對錯誤紀錄極多，需確認 PriceCenterService 是否有分頁或限制，避免 timeout。
- **分組邏輯一致性**：`AutoMapErrorLogForUI` 的建構邏輯若有缺陷，可能導致站台漏列或重複。

---

## 10. 常見錯誤

- ❌ 將 `AutoMapErrorLog` 直接序列化回傳給前端 → ✅ 必須轉換為 `AutoMapErrorLogForUI`。
- ❌ 忽略 `ECCore` 驗證，誤以為此 API 為公開端點 → ✅ 務必加入 `[Authorize]` 或等校機制。
- ❌ 未處理 PriceCenterService 異常，導致 mergesite 本身回傳不完整 stack trace → ✅ 應包裝為統一的 `ServiceMsgCode` 錯誤回應。
- ❌ 在 Controller 內做分組邏輯 → ✅ 複雜業務邏輯應置於 Service 層，提高可測試性。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | `webapi/mergesite/README.md` - 系統 API 表格 |
| 需要驗證 | `webapi/mergesite/README.md` - 該 API 標記 ✅ |
| 場景目的 | `webapi/mergesite/README.md` - 常見使用場景第 2 點 |
| 無直接 DB | `webapi/mergesite/README.md` - 技術棧「資料庫：無」；`mergesite-detail.md` - pricecenter / sport 角色均為 writer/reader 透過 Gateway |
| 相依 PriceCenterService | `webapi/mergesite/README.md` - 服務相依表格 |
| Kafka Log 紀錄 | `webapi/mergesite/README.md` - 服務相依表格 |
| 回傳模型 | Phase1 程式語義：`AutoMapErrorLog` 與 `AutoMapErrorLogForUI` 結構 |
| 分組欄位 | Phase1 程式語義：`AutoMapErrorLogForUI.LID` 為分組鍵，`MapErrorSiteLeagues` 為站台列表 |