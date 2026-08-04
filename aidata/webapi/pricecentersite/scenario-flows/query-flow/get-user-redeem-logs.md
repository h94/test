# 查詢兌換記錄（活動商品）

## 1. 場景目的

讓目前已登入的使用者查詢自己在指定活動中的兌換紀錄，後端根據 `authKey` 解析帳號，再讀取 `payment.products_activity_redeem_logs` 表，回傳去識別化後的列表。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/activity/productredeemlogs/{site}/{activityEvent}/{authKey}` | 取得使用者在該站點、該活動下的兌換紀錄 |
| GET | （一般商店兌換查詢，推測類似 `/api/store/redeemlogs/...`，OpenAPI 未列出，需人工確認） | 一般實體商品兌換紀錄查詢 |

---

## 3. 流程總覽

1. 接收 GET 請求，帶路徑參數 `site`、`activityEvent`、`authKey`。
2. 使用 `authKey` 查詢 `member.gameusers` 取得使用者 `account` 並驗證帳號狀態（`status=1`）。
3. 以 `site`、`activityEvent`、`account` 為完整分區鍵，查詢 `payment.products_activity_redeem_logs`。
4. 針對回傳結果進行必要欄位遮蔽（本活動表無個資，但仍需檢查帳號外洩風險）。
5. 回傳 `ActivityProductRedeemLogDTO` 陣列。

---

## 4. 程式流程

| 順序 | Layer | Class / Method（推測） | 動作 |
|------|-------|----------------------|------|
| 1 | Controller | `ActivityController.GetProductRedeemLogs` | 接收參數，呼叫 Service |
| 2 | Service | `ActivityService.GetProductRedeemLogs` | 組合查詢條件，調用 Provider |
| 3 | Provider | `MemberDataProvider` | 用 `authKey` 查 `member.gameusers`，得 `account`，並檢查 `status=1` |
| 4 | Provider | `PaymentDataProvider`（或 `ProductDataProvider`） | 以 `site`、`activityEvent`、`account` 查 `payment.products_activity_redeem_logs` |
| 5 | Transfer | DTO 映射 | 將查詢結果轉為 `ActivityProductRedeemLogDTO`，去除任何內部欄位（無） |
| 6 | Controller | 回傳 JSON | 返回清單 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB（Cassandra） | `member.gameusers` | Read | 由 `authKey` 取得 `account` 與驗證 `status` |
| DB（Cassandra） | `payment.products_activity_redeem_logs` | Read | 查詢特定使用者的活動兌換記錄 |
| Cache（Redis） | 無特定快取 | – | 目前未對兌換記錄做快取 |
| Queue（Kafka） | – | – | 此流程無佇列操作 |

---

## 6. 重要規則

- **權限限制**：只能查詢與 `authKey` 對應的 `account` 的記錄；不可跨使用者查詢。
- **分區鍵完整性**：查詢 `payment.products_activity_redeem_logs` 必須包含 `site`、`activityevent`、`account`，不得進行跨分區掃描。
- **不可暴露資料**：此表無高敏感欄位，但仍不可對外回傳其他帳號的記錄；若未來增加 `addr` 等欄位需遮蔽。
- **狀態值限制**：`status` 回傳原始數值（0=待處理、1=通過、2=拒絕），前端可據此顯示狀態。
- **帳號驗證**：從 `member.gameusers` 取得 `account` 時必須同時檢查 `status=1`（正常帳號），否則拒絕查詢。
- **逾時與重試**：Cassandra 查詢逾時應回傳 Server Error，不可重試造成重複查詢（僅讀取，無副作用）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|-------|
| `authKey` 不存在於 `member.gameusers` | 回傳 401 或「帳號不存在」 |
| 帳號 `status` ≠ 1（已凍結或未啟用） | 回傳 403 或「帳號已停用」 |
| 該使用者於此活動無任何兌換記錄 | 回傳空陣列 `[]` |
| Cassandra 連線失敗或逾時 | 回傳 503 Service Unavailable |
| `site` 或 `activityEvent` 為空或格式錯誤 | 回傳 400 Bad Request |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| QR-01 | API Test | 帶有效 `authKey`，有兌換記錄 | 回傳該帳號的記錄清單，欄位正確 |
| QR-02 | Permission Test | 帶有效 `authKey`，但查詢其他帳號的記錄（手動修改帳號參數？此API不提供帳號參數，故無法直接測試；若有內部參數可調整） | 僅能查到自身記錄，無法跨帳號 |
| QR-03 | Flow Test | 帳號 `status=0` | 回傳錯誤，不應查到任何記錄 |
| QR-04 | Flow Test | `authKey` 無效 | 回傳 401 |
| QR-05 | Flow Test | 使用者無兌換記錄 | 回傳 `[]` |
| QR-06 | Integration Test | Cassandra 不可用 | 回傳 503，不崩潰 |

---

## 9. 高風險區域

- **跨帳號資料外洩**：若查詢時未正確實作 `account` 過濾，可能回傳他人記錄。  
  *防範*：強制從 `authKey` 取得 `account`，並直接寫入查詢條件（程式端不可接受外部傳入的 `account` 參數）。
- **分區鍵缺失導致全表掃描**：Cassandra 查詢未帶 `account`，將掃描大量分區。  
  *防範*：Service 層強制要求必須有 `account`。
- **帳號驗證遺漏**：未檢查 `member.gameusers.status` 就回傳記錄，可能洩漏已停用帳號的歷史記錄。依業務需求，建議停用帳號仍可查自己的記錄（視同已登出則不可查），需與產品確認。

---

## 10. 常見錯誤

- ❌ 直接在 Controller 接受 `account` 參數而非從 `authKey` 推導 → 容易造成越權。
- ❌ 查詢 `products_activity_redeem_logs` 時未提供 `account` 作為叢集鍵條件 → 導致讀取過多資料，嚴重影響效能。
- ❌ 回傳時未過濾 `updatetime`（內部維護用）？此欄位可回傳用於顯示更新時間，但若內部敏感則需遮罩，目前規則允許。
- ❌ 誤用其他 keyspace 的同名表（`product.products_activity_redeem_logs` 結構雷同），因 pricecentersite 主要使用 `payment` keyspace，需注意切換正確的表。
- ❌ 混淆活動兌換與一般商店兌換：`product_store_redeem_logs` 含有地址、電話等個資，查詢後必須遮蔽。若為同一 API 則需依商品類別分流處理。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI: `GET /api/activity/productredeemlogs/{site}/{activityEvent}/{authKey}` |
| DB | `payment.products_activity_redeem_logs`（Cassandra payment keyspace）|
| DB | `member.gameusers`（Cassandra member keyspace）|
| Rules | pricecentersite-detail.md：「products_activity_redeem_logs 查詢時須依 site + activityevent + account 為分區鍵」 |
| Rules | member-detail.md：「登入驗證須 status=1」 |
| Code | 推測 Controller: `ActivityController`; Service: `ActivityService`; Provider: `MemberDataProvider`, `PaymentDataProvider` (需人工確認) |

> 若一般商店兌換查詢需要補充，須確認對應 API 路徑與遮蔽實作。建議新增 `ProductController.GetStoreRedeemLogs` 並於回傳前遮蔽 `phonenumber`, `address`, `recipient` 等欄位。