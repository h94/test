# 建立訂單

## 1. 場景目的

用戶在系統中創建新訂單，並記錄相關交易細節。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | /api/v1/orders | 用戶提交訂單創建請求 |

---

## 3. 流程總覽

1. 接收用戶提出的訂單請求
2. 驗證用戶身份狀態與訂單參數
3. 寫入新訂單記錄至 Cassandra `orders` 表
4. 更新用戶錢包餘額
5. 寫入訂單交易記錄至 `order_transactions`
6. 若訂單包含活動，更新相關活動記錄
7. 回應用戶已創建訂單

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | OrderController.CreateOrder | 接收和驗證訂單請求 |
| 2 | Service | OrderService.ValidateOrder | 驗證訂單參數與用戶身份 |
| 3 | Service | OrderService.CreateNewOrder | 創建訂單與更新資料庫 |
| 4 | Provider | WalletProvider.UpdateBalance | 更新用戶錢包餘額 |
| 5 | Provider | TransactionProvider.LogTransaction | 記錄訂單交易 |
| 6 | Provider | ActivityProvider.UpdateActivity | 更新活動記錄（如適用） |
| 7 | Controller | OrderController.Response | 回應用戶結果 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | orders | Write | 儲存訂單詳細資訊 |
| DB | order_transactions | Write | 記錄訂單交易 |
| DB | user_wallets | Update | 更新用戶錢包餘額 |
| Cache | Redis | Update | 快取用戶訂單數據（如必要） |

---

## 6. 重要規則

- 用戶狀態需為已啟用 (`status=1`)
- 訂單金額不得超過用戶當前餘額
- 幣值僅支持合法框架中的選項
- 試算失敗的訂單需手動回滾或記錄
- 活動參與限指定訂單類型

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 用戶餘額不足 | 回應餘額不足錯誤 |
| 用戶未啟用 | 回應身份驗證失敗 |
| 訂單參數不合法 | 回應參數錯誤 |
| DB 寫入錯誤 | 錯誤記錄並通知運維 |
| 活動更新失敗 | 僅裹返回訂單創建結果 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T01 | API Test | 創建合法訂單 | 成功創建訂單 |
| T02 | Permission Test | 用戶未啟用下單 | 錯誤回應身份驗證問題 |
| T03 | Flow Test | 錢包餘額不足 | 錯誤回應餘額不足 |
| T04 | Integration Test | 訂單與活動更新 | 成功記錄訂單並更新活動 |

---

## 9. 高風險區域

- 用戶錢包餘額操作
- 訂單與交易寫入跨資料庫操作
- 訂單狀態與活動同步
- 訂單參數合法性檢查
- 操作重放（replay attack）管理

---

## 10. 常見錯誤

- 未檢查用戶 `status` 造成身份驗證問題
- 忽略快取刷新導致數據不一致
- 訂單交易日誌書寫邏輯錯誤
- 活動更新失敗未通知用戶或系統
- 錯誤處理流程不一致

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | OrderController.CreateOrder |
| DB | memberservice.orders |
| Cache | Redis usage in OrderService |
| Code | OrderService.CreateNewOrder |
| SQL | INSERT INTO orders (.. details omitted ..) |