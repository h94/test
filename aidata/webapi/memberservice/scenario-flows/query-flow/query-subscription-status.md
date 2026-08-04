# 查詢訂閱狀態

## 1. 場景目的

查詢會員的訂閱狀態，包括開始和結束時間，幫助用戶了解其當前的訂閱信息和狀態。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | /api/v1/game/subscription/status | 查詢會員的訂閱狀態 |

---

## 3. 流程總覽

1. 接收訂閱狀態查詢 request。
2. 驗證會員身份（authKey）。
3. 查詢 `gamesublogs` 資料表。
4. 檢查會員的訂閱有效性。
5. 回應訂閱的開始和結束日期。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | SubscriptionController.GetStatus | 接收 request 並進行初步驗證 |
| 2 | Service | SubscriptionService.GetStatus | 處理商業邏輯，查詢資料庫 |
| 3 | Provider | SubscriptionProvider.QueryGameSublogs | 查詢 `gamesublogs` 表獲取訂閱信息 |
| 4 | Validator | AuthValidator.ValidateMember | 確認會員身份有效性 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | member.gamesublogs | Read | 查詢會員訂閱歷史 |
| DB | member.gameusers | Read | 確認會員身份有效性 |

---

## 6. 重要規則

- 會員身份驗證必須通過 `authKey`。
- 查詢結果不可直接暴露敏感資訊，如支付方法。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 會員不存在 | 返回錯誤訊息「會員不存在」 |
| 訂閱記錄不存在 | 返回空結果或「無有效訂閱」 |
| 資料庫連接失敗 | 返回系統錯誤訊息 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| 1 | API Test | 無效 authKey | 錯誤訊息「會員不存在」 |
| 2 | API Test | 未訂閱會員 | 回傳空訂閱結果 |
| 3 | Integration Test | 訂閱有效性檢查 | 返回正確的訂閱開始和結束時間 |

---

## 9. 高風險區域

- `gamesublogs` 表的正確性和更新
- 會員身份驗證的安全性和完整性
- 訂閱有效時間計算邏輯

---

## 10. 常見錯誤

- 忽略會員身份驗證，導致未授權存取
- 查詢過程中未考慮訂閱記錄的有效性
- API 回應時未防止敏感資訊暴露

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| DB | `member.gamesublogs` |
| DB | `member.gameusers` |
| Code | SubscriptionController.GetStatus |