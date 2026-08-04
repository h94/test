# 建立商城兌換紀錄

## 1. 場景目的
使用者在商城中選擇商品並提交兌換請求後，系統在 `product_store_redeem_logs` 表中建立一筆兌換紀錄，狀態預設為「審核中」（`2`）。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/store/productredeemlogs` | 建立商城商品兌換紀錄（需驗證） |

---

## 3. 流程總覽

1. 已驗證的使用者向 `POST /api/v1/store/productredeemlogs` 發送請求。
2. 服務從驗證 Token 中取得 `account`。
3. 接收請求體中的兌換資訊（`pclass`, `pid`, `cname`, `recipient`, `phonenumber`, `address`, `cmemo` 等）。
4. 系統產生唯一的兌換紀錄 `id`（UUID）與當前時間戳 `addtime`, `updatetime`。
5. 插入一筆資料至 `product.product_store_redeem_logs` 表，`status` 強制設為 `2`（審核中）。
6. 回傳成功響應或失敗訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `StoreController.PostProductRedeemLog` | 接收請求，從 Token 取得 `account`，將請求轉交給 Service。 |
| 2 | Service | `StoreService.CreateRedeemLog` | 組合資料模型，設定 `status = "2"`, `addtime`, `updatetime`, `id`。 |
| 3 | Provider | `IStoreDataProvider.InsertRedeemLog` | 對 `product.product_store_redeem_logs` 執行 INSERT。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `product.product_store_redeem_logs` | Write (INSERT) | 寫入一筆新的兌換紀錄。 |

---

## 6. 重要規則

- **權限限制**：僅已驗證的使用者可呼叫。
- **不可暴露資料**：`account` 等隱私資訊僅供內部記錄，對外 API 不可回傳。
- **欄位限制**：
  - `account`, `pid`, `pclass` 為 Clustering Key 的一部分，寫入後不可變更。
  - `status` 僅可透過 `UpdateStoreProductRedeemLogStatus` 方法更新。
- **狀態值限制**：初始化 `status` 必須為 `"2"`（審核中）。
- **不可修改欄位**：`id` 為系統自動產生，`addtime` 為系統時間，兩者皆不允許從請求中指定。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 使用者未經驗證 | 返回 401 Unauthorized。 |
| 請求 Body 格式錯誤或缺少必填欄位 | 返回 400 Bad Request。 |
| 服務無法連接到 Cassandra | 返回 500 Internal Server Error。 |
| Cassandra Insert 失敗 | 服務拋出異常，返回 500。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| IT-01 | Integration Test | 提供合法 Token 與完整 Body 呼叫 API | 200 OK，DB 中新增一筆 `status="2"` 的兌換紀錄。 |
| API-T01 | API Test | 不帶 Token 呼叫 API | 401 Unauthorized。 |
| API-T02 | API Test | 請求 Body 缺少 `pclass` 或 `pid` | 400 Bad Request。 |
| FLOW-01 | Flow Test | 模擬建立兌換紀錄後，以相同 account 查詢 | 成功查詢到該筆審核中的紀錄（需驗證隱私遮罩）。 |

---

## 9. 高風險區域

- **高風險 Table**：`product.product_store_redeem_logs` — 任何寫入錯誤都可能導致使用者兌換權益受損。
- **Cache consistency**：⚠️ `Redis` 未直接參與此寫入流程，但在讀取商品快取或庫存時若未同步可能導致超賣（庫存扣減不在本次 scenario）。此場景需人工確認庫存扣減的時機。
- **跨服務資料同步**：productservice 不負責扣款，需確保金流服務已成功處理後才建立或更新成功狀態。本場景預設審核中，風險較低。

---

## 10. 常見錯誤

- ❌ **新人容易犯錯**：手動指定 `id`、`addtime`、`status` 等應由系統自動產生的欄位值。
- ❌ **AI 容易誤解**：從 OpenAPI 文件可能誤解 `status` 可以從請求中指定；實際上 service 層應強制複寫為 `UnderReview`。
- ❌ **常見漏檢查項目**：漏檢查使用者是否已針對該商品重複提交兌換，導致重複紀錄。
- ❌ **常見錯誤流程**：寫入紀錄前未驗證商品是否存在或為上架狀態，導致寫入無效的兌換紀錄。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/v1/store/productredeemlogs` |
| DB | `product.product_store_redeem_logs` |
| Rule | `product-detail.md`：`product_store_redeem_logs.status` 初始化為 `UnderReview(2)` |

---

## 建議

1.  **建議新增測試**：新增重複提交的冪等性檢查測試。
2.  **建議新增規則**：明確定義在建立兌換紀錄時是否需先完成庫存驗證與扣減（目前 README 描述為呼叫 API 後更新庫存，屬前後流程）。