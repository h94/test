# 建立獎池賽事

## 1. 場景目的

後台管理人員在指定競猜遊戲中，建立一筆全新的「獎池投注賽事（Betpool Game）」，設定投注選項、時間、賠率等基本資訊，供前台玩家進行投注。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/predict/betpool/games` | 建立獎池賽事 |

- **驗證**：✅ 需要
- **角色**：管理後台（BFF），由 `pricebackendservice` 接收請求，轉發至 `predictservice`。

---

## 3. 流程總覽

1. 後台前端發起 POST 請求，攜帶賽事設定 JSON。
2. `pricebackendservice` 驗證管理員權限。
3. `pricebackendservice` 呼叫 `predictservice` 建立賽事 API。
4. `predictservice` 寫入 `betpool_games` 資料表。
5. 回傳成功結果給後台前端。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `PredictController.CreateBetPoolGame` | 接收 API 請求，轉呼叫 Service |
| 2 | Service | `PredictService.CreateBetPoolGame` | 調用 `IPredictDataProvider` 介面 |
| 3 | Provider | `PredictDataProvider.CreateBetPoolGame` | 發送 HTTP 請求至 `predictservice` |
| 4 | Service (下游) | `predictservice` | 處理商業邏輯、驗證資料、產生 `id`、寫入 Cassandra |
| 5 | DB | `predict.betpool_games` | INSERT 一筆新賽事，`status` 預設 0（開放） |

| Evidence: |
|---|
| Controller: `Controllers/PredictController.cs` |
| Service: `Services/PredictService.cs` |
| Provider: `DataProviders/PredictDataProvider.cs` |
| DB: `db/predict-detail.md` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.betpool_games` | Write (INSERT) | 儲存新獎池賽事的主要資訊 |
| Cache | `predict:game:{gid}:status` | Write (DEL) | 建立後，無舊快取需要清除；但若後續更新狀態，需主動刪除快取 |

| Evidence: |
|---|
| DB Schema: `db/predict.md` |
| Cache Rule: `db/predict-detail.md` |

---

## 6. 重要規則

- **權限限制**：僅限通過驗證的管理後台使用者。
- **不可修改欄位**：
  - `id`：系統自動生成（UUID），不允許請求中指定。
  - `starttime`, `endtime`：建立時設定，後續不可動態修改（僅管理後台更新狀態時可使用）。
  - `payout`, `winresult`：建立時恆為 `false` / `NULL`，僅在結算時由系統更新。
- **狀態機規則**：
  - 新賽事 `status` 固定為 `0`（開放）。
  - 狀態流轉：`0（開放）→ 1（關閉）→ 2（結算）`，不可跳躍或回退。
- **資料校驗**：
  - `starttime < endtime`（bigint，UTC 時間戳）。
  - `betoptions` 與 `names` 必須提供，且為有效 map 格式。
- **不可暴露資料**：
  - `feedrate`（內部派彩計算參數）不可回傳給前端，或僅限後台查詢。

| Evidence: |
|---|
| Rules: `db/predict-detail.md` — `betpool_games` 寫入限制 |

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 缺少必要欄位（如 `starttime`, `endtime`, `betoptions`） | 回傳 400 Bad Request，附帶驗證錯誤訊息 |
| `starttime >= endtime` | 回傳 400 Bad Request |
| 後台使用者未驗證 | 回傳 401 Unauthorized |
| 下游 `predictservice` 無回應 | 回傳 502 Bad Gateway 或 504 Gateway Timeout |
| 寫入 Cassandra 失敗 | 回傳 500 Internal Server Error |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| BP-01 | API Test | 正常建立獎池賽事 | 回傳 200，DB 寫入一筆 `status=0` 的新賽事 |
| BP-02 | Validation | 缺少 `starttime` | 回傳 400 |
| BP-03 | Validation | `starttime` > `endtime` | 回傳 400 |
| BP-04 | Permission | 未帶 Token 請求 | 回傳 401 |
| BP-05 | Flow Test | 建立後，查詢賽事列表 | 新賽事應出現，`status` 為 0 |

---

## 9. 高風險區域

- **高風險 Table**：`predict.betpool_games`
  - `status` 狀態流轉若錯誤，會導致賽事無法關閉或結算。
- **高風險 API**：無，此為單純建立操作。
- **跨服務資料同步**：
  - `predictservice` 為 owner，`pricebackendservice` 為 BFF。無跨服務同步風險，但需確保 BFF 傳遞的資料正確性。
- **Cache consistency**：
  - 建立時無快取風險。但後續狀態更新時，**必須**刪除 `predict:game:{gid}:status` 快取，避免不一致。
- **Idempotency**：
  - 若前端因網路問題重複提交，會建立多筆賽事。需人工確認是否需要冪等性機制（如基於業務唯一鍵）。

---

## 10. 常見錯誤

- **新人常犯**：
  - 手動指定 `id`，導致系統生成的 UUID 機制被繞過。
  - 誤將 `starttime` / `endtime` 設定為非 UTC 時間戳。
- **AI 容易誤解**：
  - 以為可以透過同一 API 更新賽事，實際上更新應走後續的 `PUT` 或結算 API。
  - 誤將 `feedrate` 作為可選參數回傳給前台。
- **常見漏檢查**：
  - 未驗證 `betoptions` 的 key 格式，導致後續投注匹配錯誤。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `Controllers/PredictController.cs` |
| Service | `Services/PredictService.cs` |
| Provider | `DataProviders/PredictDataProvider.cs` |
| DB | `predict.betpool_games` |
| DB Rules | `db/predict-detail.md` |
| Service Dep. | `README.md` (predictservice) |