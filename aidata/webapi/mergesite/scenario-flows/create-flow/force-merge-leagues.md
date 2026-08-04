# 強制合併聯盟

## 1. 場景目的
管理員在自動比對失敗時，手動指定聯盟的合併關聯，使相同賽事的聯盟資料得以統整，避免重複或錯誤的聯盟造成賽事混亂。

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/merge/leagues/{gameType}` | 強制合併指定球種下的聯盟，需驗證 |

## 3. 流程總覽

1. 管理員從自動比對錯誤列表 (`GET /api/system/automapteam/check`) 取得待處理的聯盟。
2. 管理員選擇欲合併的主庫聯盟 (target LID) 與站台聯盟 (source SiteLID)，發送合併請求。
3. `MergeSite` 接收請求，驗證請求人權限與參數。
4. 透過 `PriceCenterGateway` 呼叫遠端 `PriceCenterService` 的強制合併 API，傳入合併對應關係。
5. `PriceCenterService` 執行底層資料合併（如更新站台聯盟與主庫聯盟的關聯、重建索引等）。
6. 合併成功後回傳 `ServiceMsgCode`；若失敗則回傳對應錯誤碼。

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `MergeController.ForceMergeLeagues(gameType, request)` | 接收 HTTP POST，呼叫 Service 層 |
| 2 | Service | `MergeService.ForceMergeLeagues(gameType, dto)` | 驗證參數、組裝呼叫格式，呼叫 Provider |
| 3 | Provider | `PriceCenterGateway.ForceMergeLeagues(gameType, payload)` | 發送 HTTP PUT/POST 至 PriceCenterService `/merge/leagues` |
| 4 | (遠端) | `PriceCenterService` 內部邏輯 | 執行合併，更新相關資料表 |

> **需人工確認**：實際 Service 與 Gateway 方法名稱、遠端 API 確切端點應由程式碼確認。

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| - | - | - | 本服務無直接 DB/Cache/Queue 操作，所有資料操作委託給 PriceCenterService |

> **需人工確認**：PriceCenterService 的合併操作可能涉及 Cassandra 或 sport MySQL，但不在本服務邊界內。

## 6. 重要規則

- 僅具有管理員權限的帳號可呼叫此 API（由 ECCore 驗證過濾）。
- `gameType` 必須是有效的球種代碼（如 `NBA`, `MLB`）。
- 請求的 body 中必須包含合併對應，如 `{ "lid": "targetLID", "siteLeagues": [{"site": "AU8", "siteLid": "srcLID"}] }`（格式需參考現有 code）。
- 同一聯盟不可重複合併；若已存在關聯，應回傳錯誤或直接忽略。
- 合併後不得影響現有賽事賠率資料的運作，需確保 PriceCenterService 有適當的保護機制。
- 操作應記錄使用者操作紀錄（服務有提供 `/api/system/logs/action` 上傳，但此動作是否自動記錄需確認）。

## 7. 錯誤情境

| 情境 | 預期結果 |
|-------|----------|
| 未登入或權限不足 | 回傳 401 / 403 |
| `gameType` 不存在或不支援 | 回傳 400 並附帶錯誤訊息 |
| request body 缺少必要欄位 | 回傳 400，指出缺少的參數 |
| 指定的 lid 或 siteLid 不存在 | PriceCenterService 回傳錯誤，轉為 500 或自定義錯誤碼 |
| 合併關係已存在 | 依業務規則可能回傳 409 Conflict 或成功（冪等） |
| PriceCenterService 無回應或 timeout | 回傳 504 Gateway Timeout |

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC01 | Permission Test | 未帶 token 或一般會員呼叫 | 401 / 403 |
| TC02 | API Test | 傳入有效的 gameType 與正確的合併對應 | 200，合併成功 |
| TC03 | Flow Test | 重複發送相同的合併要求 | 依冪等設計，可能成功或回傳 409 |
| TC04 | Integration Test | PriceCenterService 回傳內部錯誤 | 5xx，錯誤訊息明確 |
| TC05 | Data Test | 合併後查詢站台聯盟列表，確認關聯已建立 | 查詢 API 返回合併後的資訊 |

## 9. 高風險區域

- **跨服務資料一致性**：合併操作影響多個站台的聯盟資料，若中途失敗可能殘留部分關聯，需確認 PriceCenterService 的 transaction 設計。
- **Cache 同步**：若 PriceCenterService 使用 Redis 快取，合併後可能需主動失效相關快取。
- **無本地 rollback 能力**：MergeSite 僅為代理，無法感知遠端執行狀態細節，錯誤需仰賴遠端回傳並呈現給使用者。
- **使用者操作紀錄**：需確保強制合併的操作被完整記錄，以便稽核（若未自動記錄需額外呼叫 `/api/system/logs/action`）。

## 10. 常見錯誤

- 誤解合併方向：不清楚哪一個是 source，哪一個是 target，導致反向操作。
- 未確認主庫 LID 是否正確即強制合併，可能導致資料連結錯誤。
- 未注意到 `gameType` 與聯盟的球種必須相符，跨球種合併會混淆資料。
- 在未確認自動比對狀態下即合併，可能覆蓋正確的自動比對結果。

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/merge/leagues/{gameType}` (OpenAPI / README) |
| 服務邊界 | 無直接 DB，透過 PriceCenterGateway 呼叫遠端 (README: 技術棧、服務相依) |
| 權限 | 需要驗證 (README API 表格) |
| 前導流程 | `GET /api/system/automapteam/check` (README 常見使用場景) |
| 錯誤資料模型 | `AutoMapErrorLogForUI`, `MapErrorSiteLeague` (Phase0/1 semantic) |
| 使用者操作紀錄 | `POST /api/system/logs/action` (OpenAPI / README) |

> **需人工確認**：  
> - Request body 的精確結構（建議補充 OpenAPI 或 DTO 定義）  
> - PriceCenterService 實際 endpoint 與合併邏輯  
> - 是否有冪等設計或重複合併保護  
> - 是否自動記錄操作行為至 action log