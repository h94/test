# 更新商城兑换状态 (UpdateStoreProductRedeemLogStatus)

## 1. 場景目的

本文件描述商城商品兑换订单的状态更新流程。后台人员（或系统内部流程）通过调用专用方法更新 `product_store_redeem_logs` 表中的 `status` 字段，以推进订单的生命周期（如审核、出货、收货等）。此流程为纯后端内部操作，未发现有对外开放的 API 端点。

---

## 2. 入口 API

**需人工確認**：根據 README 與 OpenAPI 文件，未找到對應的公開 API 端點。根據寫入限制，此操作可能通過 `UpdateStoreProductRedeemLogStatus` 方法實現，為後台管理或內部服務間的 RPC 調用。

| Method | Path         | 說明                                                                                                     |
| ------ | ------------ | -------------------------------------------------------------------------------------------------------- |
| N/A    | N/A (Service) | 可能由後台內部服務 (productservice) 通過 Provider (DataProvider) 的方法更新。前端或外部系統無法直接調用此公開 HTTP API。 |

---

## 3. 流程總覽

1.  後台管理員或用戶操作（例如：出貨、確認收貨）觸發狀態更新。
2.  `productservice` 接收到更新請求，該請求包含訂單的唯一標識 (`pclass`, `pid`, `addtime`, `account`, `id`) 和目標狀態。
3.  系統通過 Provider 層查詢對應的兌換記錄。
4.  執行嚴格的業務規則校驗，確保狀態流轉合法。
5.  通過 Provider 更新記錄的 `status` 和 `updatetime` 欄位。
6.  更新成功後，返回成功結果。

---

## 4. 程式流程

> **說明**：由於未找到對應的 Controller，以下流程基於 Provider (DataProvider) 和 Service 層的資訊推斷。

| 順序 | Layer    | Class / Method        | 動作                                                                                                                              |
| ---- | -------- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| 1    | Provider | `IStoreDataProvider`  | 提供底層資料存取方法，包含 `UpdateStoreProductRedeemLogStatus`。                                                                 |
| 2    | Service  | `StoreService` (推斷)  | 呼叫 Provider 查詢現有兌換記錄。                                                                                                  |
| 3    | Service  | `StoreService` (推斷)  | **規則校驗**：<br>- 檢查當前狀態是否為終態 (Success(1) 或 Failure(0))，若是則拒絕更新。<br>- 校驗狀態轉換是否符合業務邏輯。 |
| 4    | Provider | `IStoreDataProvider`  | 執行 `UPDATE product.product_store_redeem_logs` 操作，更新 `status` 和 `updatetime`。                                           |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源                          | 操作   | 用途                                      |
| ---- | ----------------------------- | ------ | ----------------------------------------- |
| DB   | `product.product_store_redeem_logs` | Read   | 查詢當前兌換記錄，以進行狀態流轉校驗。    |
| DB   | `product.product_store_redeem_logs` | Update | 更新兌換記錄的 `status` 和 `updatetime`。 |

---

## 6. 重要規則

- **狀態流轉限制**（最高風險）：根據 `product-detail.md`，`product_store_redeem_logs` 的 `status` **一旦設為 `Success(1)` 或 `Failure(0)` 後不可再變更**。
- **寫入限定**：`status` 欄位**僅透過 `UpdateStoreProductRedeemLogStatus` 方法更新**，不可直接 `UPDATE` 或由其他 API 寫入。
- **不可變更欄位**：`account`、`pid`、`pclass` 作為 Clustering Key，寫入後不可變更。
- **狀態枚舉**：`status` 型別為 `text`，其值定義於 `StoreProductRedeemLogStatus` 枚舉：
  - `"0"` (Failure): 兌換失敗
  - `"1"` (Success): 兌換成功
  - `"2"` (UnderReview): 審核中
  - `"3"` (ReviewSuccessful): 審核通過
  - `"4"` (InTransit): 運送中
  - `"5"` (Delivered): 已送達
  - `"6"` (Received): 已收貨
  - `"7"` (UnReceived): 未收貨
- **不可回傳欄位**：`product_store_redeem_logs` 中的 `account`、`phonenumber`、`address`、`recipient` 等為個人隱私資訊，在前端查詢時不可回傳或應做遮罩處理。

---

## 7. 錯誤情境

| 情境                                 | 預期結果                                                             |
| ------------------------------------ | -------------------------------------------------------------------- |
| 嘗試將已是最終狀態的訂單設為其他狀態 | 系統應拒絕操作，並回傳錯誤（如「訂單已完成，無法變更」）。             |
| 請求更新的訂單記錄不存在             | 系統應回傳 `NotFound` 錯誤。                                         |
| 請求更新的狀態值不在枚舉定義中       | 系統應回傳 `BadRequest` 錯誤，指出無效的狀態值。                       |
| 無權限更新兌換狀態                   | **需人工確認**（若為內部 RPC，可能無此檢查；若為對外 API，則需驗證）。 |

---

## 8. 測試重點

| Test ID | 類型          | 情境                                       | 預期結果                  |
| ------- | ------------- | ------------------------------------------ | ------------------------- |
| UT-01   | Unit Test     | 嘗試將 `status="1"` (Success) 的訂單設為 `"3"` | 應拋出異常或回傳失敗結果。 |
| UT-02   | Unit Test     | 將 `status="2"` (UnderReview) 設為 `"3"` (ReviewSuccessful) | 更新成功。                |
| FT-01   | Flow Test     | 管理員審核通過一個待審核的兌換訂單         | 訂單狀態成功由審核中轉為審核通過。 |
| FT-02   | Flow Test     | 管理員對已成功的訂單執行出貨操作           | 系統拒絕操作，狀態未被改變。 |

---

## 9. 高風險區域

- **狀態機一致性**：`product_store_redeem_logs` 的 `status` 流轉是整個業務的核心。必須確保程式邏輯完全符合 `product-detail.md` 中定義的規則，特別是終態的不可逆性。
- **並發更新**：在多個管理員或排程任務同時對同一訂單進行操作時，必須通過樂觀鎖或原子操作保證狀態更新的一致性，防止狀態跳躍。
- **資料一致性**：`product_store_redeem_logs` 跨多個服務讀取/寫入（如 `inplayzsubscriptionsystem`， `cryptoflowservice`），必須確保任何服務在更新此表時都遵循相同的規則。

---

## 10. 常見錯誤

- ❌ **新人**：直接對 `product_store_redeem_logs` 執行 SQL `UPDATE` 語句來改變狀態。
    - ✅ 正確做法：必須使用 `IStoreDataProvider.UpdateStoreProductRedeemLogStatus` 方法。
- ❌ **新人/AI**：在程式碼中未做終態檢查，允許將 `Success(1)` 或 `Failure(0)` 的訂單流轉到其他狀態。
    - ✅ 正確做法：在執行 UPDATE 前必須檢查當前狀態。
- ❌ **AI 容易誤解**：為此流程生成一個公開的 RESTful API 端點（如後台 API）。
    - ✅ 正確做法：根據現有資料，這是一個內部操作，沒有公開的 HTTP API，應生成內部 Service 方法或 RPC 接口實現。

---

## 11. Evidence

| 類型   | 來源                                                                                                                                                                                  |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DB     | `product.product_store_redeem_logs` (Schema: `db/product.md`)                                                                                                                         |
| 規則   | `webapi/productservice/productservice-detail.md` - 寫入限制與讀取規則                                                                                                                    |
| 規則   | `db/product-detail.md` - Table: `product_store_redeem_logs`，status 欄位的值定義、狀態流轉與跨服務限制                                                                                   |
| Code   | `StoreProductRedeemLogStatus` 枚舉定義 (source: `ProductService.Model/AppDefine.cs`)                                                                                                   |
| Code   | `IStoreDataProvider` interface 中的 `UpdateStoreProductRedeemLogStatus` 方法命名 (推斷自寫入限制與 DB 操作邊界文件)                                                                  |