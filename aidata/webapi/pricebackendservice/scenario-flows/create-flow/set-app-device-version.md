# 設定 App 裝置版本

## 1. 場景目的

管理後台設定 App 支援的最低或特定裝置版本，讓後台管理員可以針對不同平台（如 iOS、Android）及不同 App ID，配置允許使用的版本號，以控管用戶端 App 相容性。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/manage/appdevices` | 設定 App 裝置版本 |

---

## 3. 流程總覽

1. 接收管理後台請求，包含 App ID、平台類型、版本號
2. 驗證管理員權限（需通過 ECFramework 驗證）
3. 呼叫下游微服務 `pricecentermanage` 寫入 App 裝置版本設定
4. `pricecentermanage` 將資料寫入 `sport.appdevices` 表
5. 回傳操作結果

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `ManageController` | 接收 POST request，解析 `AppDevice` 參數 |
| 2 | Service | `ManageService` | 處理業務邏輯，組裝請求 |
| 3 | Provider | `ManageProvider` | 呼叫 `pricecentermanage` 下游 API 寫入資料 |
| 4 | 下游服務 | `pricecentermanage` | 負責實際寫入 `sport.appdevices` 表 |
| 5 | Controller | `ManageController` | 回傳 200 OK 或錯誤 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `sport.appdevices` | Write | 儲存 App 裝置版本設定 (由下游 `pricecentermanage` 操作) |

---

## 6. 重要規則

- **權限限制**：需通過 ECFramework 驗證，僅管理後台人員可操作
- **欄位限制**：
  - `Id` (text)：App 識別碼，需人工確認是否為既有枚舉值或可自由定義
  - `Platform` (int)：平台類型，需人工確認平台枚舉定義（如 0=iOS, 1=Android）
  - `Version` (text)：版本號字串
- **不可修改欄位**：`Id` 與 `Platform` 為複合主鍵，建立後不可修改；相同組合會覆蓋既有版本設定
- **Transaction 規則**：本服務不涉及 Transaction，由下游 `pricecentermanage` 處理

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 未通過驗證 | 回傳 401 Unauthorized |
| 必要參數缺失（Id、Platform、Version） | 回傳 400 Bad Request |
| 下游 `pricecentermanage` 服務不可用 | 回傳 502 Bad Gateway 或 500 Internal Server Error |
| 下游寫入失敗 | 回傳錯誤訊息，由 `ManageProvider` 拋出例外 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| TC-01 | API Test | 正常設定 App 裝置版本 | 200 OK，資料成功寫入 |
| TC-02 | Permission Test | 無驗證 token 呼叫 | 401 Unauthorized |
| TC-03 | API Test | 缺少 Version 參數 | 400 Bad Request |
| TC-04 | Flow Test | 下游服務超時 | 回傳錯誤，不 crash |

---

## 9. 高風險區域

- **下游依賴**：本服務完全依賴 `pricecentermanage`，若下游故障則功能完全無法使用
- **主鍵覆蓋**：相同 `(Id, Platform)` 組合會直接覆蓋舊版本設定，無歷史記錄
- **無版本驗證**：需人工確認是否需驗證版本號格式（如語意化版本 `1.0.0`）

---

## 10. 常見錯誤

- 新人容易漏掉驗證機制，直接呼叫下游
- 忽略下游服務回傳的錯誤碼，未做適當處理
- `Platform` 欄位型別為 `int`，誤傳字串導致型別錯誤
- 未確認 `Id` 是否需要預先註冊或可自由建立

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | POST `/api/v1/manage/appdevices` |
| DB | `sport.appdevices` (Id, Platform, Version) |
| 服務相依 | README.md: `pricecentermanage` 負責 App 裝置版本管理 |
| 驗證 | README.md: 使用 ECFramework.ECService |

---

## 12. 建議（非 Evidence，僅供參考）

- 建議在本服務 README 或 `manage` 模組中補充 `AppDevice` 的 request schema 定義
- 建議明確定義 `Platform` 的枚舉值（如 0=iOS, 1=Android）
- 建議確認是否需保留版本設定的歷史記錄，避免誤覆蓋無法回溯
- 建議新增 integration test 涵蓋下游失敗情境