# 取得 OpenClaw 合併資料（列表）

## 1. 場景目的
營運人員在管理後台依球種與時間區間查詢待合併的 OpenClaw 賽事清單，作為確認是否需要人工強制合併的前置步驟。

---

## 2. 入口 API
| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/merge/openclawmerge/{gameType}` | 依球種與時間區間取得 OpenClaw 合併資料列表 |

參數（需人工確認具體欄位，根據同服務其他查詢 API 推斷）：
- `gameType`（路徑參數）：球種代碼，如 `NBA`、`MLB`
- `startDate`（Query）：起始日期
- `endDate`（Query）：結束日期
- 可能包含 `startTime`、`endTime` 或 `site` 等過濾條件

驗證：需要 ECCore 驗證（管理後台權限）

---

## 3. 流程總覽
1. 管理後台前端發送 GET 請求至 `/api/merge/openclawmerge/{gameType}`
2. ECCore 驗證機制檢查請求是否攜帶有效身份（JWT / Cookie）
3. Controller 解析 `gameType` 及 Query 參數
4. Service 層組裝呼叫 PriceCenterService 的參數（球種、時間區間）
5. 透過 Gateway（`192.168.55.60`）呼叫 PriceCenterService REST API，取得 OpenClaw 合併資料
6. Service 轉換回傳資料為本服務 DTO（視需求遮罩內部欄位）
7. 回傳 200 OK 與合併資料列表
8. 若 PriceCenterService 不可用或查詢失敗，回傳對應錯誤碼（如 502）

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Middleware | ECCore 驗證 | 攔截請求並驗證權限 |
| 2 | Controller | `MergeController.GetOpenClawMergeList`（推測） | 接收參數，呼叫 Service |
| 3 | Service | `MergeService.GetOpenClawMergeData`（推測） | 調用 PriceCenterService Proxy |
| 4 | Infrastructure | `PriceCenterServiceClient`（推測） | 發送 HTTP GET 至 PriceCenterService |
| 5 | Service | 同上 | 轉換回應為 `OpenClawMergeDTO` 列表 |
| 6 | Controller | 同上 | 回傳 JSON 結果 |

> **需人工確認**：實際 Controller / Service / Client 類別名稱與方法簽名，因現有程式碼分析未提供此 API 實作細節。

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| 遠端 API | PriceCenterService（REST） | Read（HTTP GET） | 取得 OpenClaw 合併原始資料 |
| Queue | Kafka | Publish（非同步） | 僅用於應用程式 Log（非本流程核心） |

> 本服務無直連資料庫，無 Redis 快取，無 Queue 消費於此查詢流程。

---

## 6. 重要規則
- **權限限制**：必須通過 ECCore 驗證（管理後台角色），未登入或權限不足拒絕存取（401/403）
- **球種限制**：`gameType` 必須為已定義的球種代碼，否則回應 400 錯誤
- **時間參數**：必須提供合法的時間區間（start ≤ end），未提供或格式錯誤應返回 400
- **回應過濾**：不可回傳 PriceCenterService 內部欄位（如 `handler`、`password` 等），需使用 DTO 重新組裝
- **無快取**：因資料為即時合併狀態，不適合長時間快取
- **無 Transaction**：純讀取作業，無跨服務寫入事務

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|------|----------|
| `gameType` 不存在或為空 | 400 Bad Request（含錯誤訊息） |
| 未提供 `startDate` 或 `endDate` | 400 Bad Request |
| 時間格式錯誤（例如非 `yyyy-MM-dd`） | 400 Bad Request |
| 無身份驗證 Header | 401 Unauthorized |
| 身份有效但權限不足 | 403 Forbidden |
| PriceCenterService 無回應或逾時 | 502 Bad Gateway（或 504） |
| PriceCenterService 回傳業務錯誤 | 傳遞其錯誤碼與訊息（如 500） |
| 查無資料 | 200 OK 並回傳空陣列（非錯誤） |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| OC-01 | API Test | 正常參數：`gameType=NBA`, 合法時間區間 | 200，回傳非空列表 |
| OC-02 | API Test | 無效球種：`gameType=INVALID` | 400 |
| OC-03 | API Test | 缺少 `startDate` | 400 |
| OC-04 | Permission Test | 無 Token 請求 | 401 |
| OC-05 | Integration Test | PriceCenterService 模擬回傳延遲 | 502（或自定義降級回應） |
| OC-06 | API Test | 時間區間無對應資料 | 200，回傳 `[]` |

---

## 9. 高風險區域
- **PriceCenterService 相依**：若該服務故障，本功能完全無法使用；需考慮重試機制或前端降級提示。
- **大時間範圍查詢**：可能導致 PriceCenterService 回應大量資料，需確認該服務是否有分頁或限制；必要時本側亦應加入限制。
- **內部資料洩漏**：若直接序列化 PriceCenterService 原始回應，可能外洩敏感欄位（如內部 ID、handler），必須映射為專用 DTO。
- **無快取策略**：大量且頻繁的查詢可能對 PriceCenterService 造成壓力，需評估是否應引入短暫快取（目前未實作）。

---

## 10. 常見錯誤
- ❌ **未驗證 `gameType` 合法性**，直接傳遞任意字串給 PriceCenterService，可能造成後端錯誤或異常回應。
- ❌ **忘記將 PriceCenterService 回傳物件轉換為本服務 DTO**，直接回傳原始結構，導致內部欄位外洩（如 `SiteID`、`handler`）。
- ❌ **未處理 Parameter Binding 失敗**，例如 `startDate` 型別錯誤（應為 `DateTime?`），應明確回傳 400。
- ❌ **假設查無資料為錯誤**，應視為正常空集合。
- ❌ **混淆此流程與強制合併流程**：此 API 僅查詢，不應觸發寫入動作（合併由 `PUT /api/merge/games/{gameType}` 執行）。

---

## 11. Evidence
| 類型 | 來源 |
|------|------|
| API 路由 | README.md：`GET /api/merge/openclawmerge/{gameType}` |
| 需要驗證 | README.md 欄位「需要驗證」標示為 ✅ |
| 服務無直接 DB | README.md 技術棧：「資料庫：無（透過 Gateway 呼叫 PriceCenterService REST API）」 |
| 服務相依 | README.md：PriceCenterService Gateway `192.168.55.60`；Kafka 僅用於 Log |
| 場景目的 | README.md 常見使用場景 1：「管理後台查看待合併賽事」 |
| 可能查詢參數 | OpenAPI `/api/leagues/{gameType}` 存在 `startDate`, `endDate` 等參數（推測合併搜尋亦有類似設計） |
| 權限機制 | ECCore 3.0.2 內建機制（README 技術棧） |
| 資料不可直接暴露 | mergesite-detail.md 提及 pricecenter 不可回傳欄位規則（如 `password`, `handler`），雖非直接 DB 操作但應遵循相同原則 |

> **需人工確認**：OpenAPI 中 `/api/merge/openclawmerge/{gameType}` 的具體 Query 參數、回應結構（Schema），以及 Controller/Service 實際命名與實作邏輯。