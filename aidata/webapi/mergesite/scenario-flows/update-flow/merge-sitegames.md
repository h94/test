# 合併站台賽事

## 1. 場景目的

運營人員在賽事合併管理頁面，針對同一場實體賽事但被不同站台拆分為多筆記錄的 SiteGame，執行人工合併，將其關聯至一個主賽事 ID（gid），以統一後續賠率管理與資料展示。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | `/api/merge/sitegames/{gameType}` | 提交站台賽事合併操作 |

（註：依據 README.md 與 OpenAPI 路由推斷，缺少完整 request body schema，以下流程為合理推測）

---

## 3. 流程總覽

1. 後台頁面調用 GET API 取得待合併的站台賽事（可能來自 `/api/siteleagues/*` 或 `/api/merge/openclawmerge`，**需人工確認**）
2. 使用者選取多個站台賽事，指定目標主賽事（或系統自動計算），送出合併請求
3. 合併 API 接收請求，驗證 `gameType` 與參數
4. 透過 PriceCenterService 執行合併，更新站台賽事的主賽事關聯（**需人工確認 DB 實際操作**）
5. 必要時記錄操作日誌並推送到 Kafka
6. 回傳操作結果

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | MergeController.PutSitegames (推測) | 接收 PUT 請求，驗證 model binding |
| 2 | Validator | (推測) | 驗證 gameType 是否為合法球種代碼、body 參數完整性 |
| 3 | Service | MergeService.MergeSiteGames (推測) | 呼叫 PriceCenterService 執行合併 |
| 4 | Provider | PriceCenterService (透過 Gateway) | 實際執行合併操作（可能更新 site_game 表的 master_id 或合併表） |
| 5 | Provider / Log | 操作紀錄 | 調用 `/api/system/logs/action` 寫入使用者操作日誌，並透過 Kafka 記錄 log |

（由於缺乏 source code evidence，以上為基於一般架構的推測，**需人工確認**）

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | PriceCenter Cassandra（accounts_* 非直接相關） | 無 | 本場景不直接操作帳號表，但合併可能涉及帳號資訊，**需人工確認** |
| DB | Sport MySQL（bk_siteplayers） | 無 | 站台賽事記錄存在於 PriceCenter，不在 sport 庫，**需人工確認** |
| Gateway | PriceCenterService REST API | POST/PUT | 委託執行站台賽事合併，回傳成敗 |
| Queue | Kafka | Publish | 操作紀錄推送至 log topic |

---

## 6. 重要規則

- **權限限制**：僅限後台管理員操作，需通過 ECCore 驗證
- **gameType 必填**：必須為系統定義的合法球種代碼（如 `NBA`、`MLB` 等）
- **不可修改欄位**：主賽事 ID（gid）一經合併後不可再任意變更，除非另有強制合併 API（**需人工確認**）
- **Transaction 規則**：合併為「全有或全無」操作，失敗時應全部回滾，避免部分成功
- **冪等性**：相同合併請求重複提交不應產生副作用（**需人工確認設計**）
- **不可暴露資料**：不得回傳內部主鍵或敏感設定

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| gameType 不存在或格式錯誤 | 400 Bad Request |
| 缺少必要參數（如 gid、siteGameId list） | 400 Bad Request |
| 指定的站台賽事不存在或已被合併 | 409 Conflict 或 400，提示重複合併 |
| PriceCenterService 連線失敗或回傳錯誤 | 502 Bad Gateway 或對應錯誤碼，操作日誌記錄失敗 |
| 使用者未驗證或權限不足 | 401 Unauthorized 或 403 Forbidden |
| 合併過程中發生部分成功 | 系統應保證 transaction，全部回滾，回傳 500 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SG-01 | API Test | 正常合併一組站台賽事至主賽事 | 200 OK，後續查詢該主賽事可包含全部子賽事 |
| SG-02 | Permission Test | 未登入直接呼叫 PUT | 401 |
| SG-03 | Permission Test | 無合併權限角色呼叫 | 403 |
| SG-04 | Flow Test | 對已合併的賽事再次送出相同請求 | 冪等或 409 Conflict |
| SG-05 | Integration Test | 模擬 PriceCenterService 回傳失敗 | 客戶端收到 5xx 錯誤，站台賽事狀態不變 |
| SG-06 | API Test | gameType 參數不合法 | 400 Bad Request |

---

## 9. 高風險區域

- **高風險 API**：`PUT /api/merge/sitegames/{gameType}`，變更賽事關聯會直接影響後續賠率計算與顯示，錯誤合併可能導致賠率管理混亂
- **跨服務資料同步**：依賴 PriceCenterService，若該服務回應時間過長或失敗，需設計重試與最終一致性策略
- **Transaction**：合併涉及多筆記錄更新，須確保原子性
- **Idempotency**：重複提交合併請求時，需明確設計防重機制（如檢查合併狀態，**需人工確認**）

---

## 10. 常見錯誤

- ❌ 未檢查站台賽事是否已存在合併關聯，導致重複合併
- ❌ 未驗證 gameType 造成傳入非法球種，下游服務可能因找不到對應資料而失敗
- ❌ 忽略 PriceCenterService 回應中的錯誤碼，未正確回傳給前端
- ❌ 合併成功後未更新客戶端快取或通知相關服務，導致前端顯示不一致
- ❌ 日誌僅記錄成功，未記錄失敗詳情，增加排查難度

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API 路由 | README.md 賽事合併章節，OpenAPI 定義（部分截斷） |
| 服務相依 | README.md — PriceCenterService Gateway 用途 |
| 權限驗證 | README.md「需要驗證 ✅」 |
| 操作日誌 | `/api/system/logs/action` 路由 |
| Kafka | README.md 服務相依 — Kafka for Log |
| 強制合併賽事相關 | README.md 常見場景 2，但站台賽事為另一入口 |

**需人工確認**：
- 完整的 request body schema（包含哪些欄位）
- PriceCenterService 實際 API endpoint 與合併邏輯
- 是否直接操作 Cassandra 或僅透過 Gateway
- 冪等性設計與合併狀態儲存方式

---

## 建議新增文件

- `mergesite/api-merge-sitegames.md`：詳細描述站台賽事合併的 Request / Response 規格與錯誤碼
- `mergesite/sitegame-merge-flow.md`：內部流程圖與跨服務互動序列圖

## 建議新增規則

- 定義合併前的必備檢查清單（如：所有子賽事必須屬於同一 gameType、相同日期區間等）
- 明確定義合併後不可再拆分，防止運營誤操作

## 建議新增測試情境

- 模擬 PriceCenterService 逾時後的重試機制（若有）
- 並發提交相同合併請求的 race condition 測試