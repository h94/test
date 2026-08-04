# 取得服務版本號

## 1. 場景目的
提供一個不需驗證的系統端點，供外部監控、部署工具或維運團隊查詢 `paymentservice` 的目前部署版本，以便確認服務更新狀態或進行健康檢查以外的版本比對。

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/version` | 回傳目前服務的版本號字串。不需驗證。 |

## 3. 流程總覽
1.  `paymentservice` 接收對 `/api/version` 的 GET 請求。
2.  返回服務版本號資訊，此流程無任何權限驗證、資料庫查詢或外部服務呼叫。

## 4. 程式流程
根據現有文件，無法確切得知 Controller 與 Service 類別名稱，基於一般 .NET 慣例推測如下，**需人工確認**。

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware / Filter | Auth | 此端點為匿名存取，跳過驗證。 |
| 2 | Controller | VersionController.Get | 接收請求。 |
| 3 | Controller | VersionController.Get | 從應用程式組態（如 `appsettings.json`、環境變數，或程式集資訊）讀取版本字串。 |
| 4 | Controller | VersionController.Get | 回傳版本號。HTTP 200 OK。 |

## 5. DB / Cache / Queue 使用
此查詢流程為單純的系統資訊回傳，無任何相關操作。

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| ✖ | ✖ | ✖ | 無任何資料庫、快取或佇列使用行為。 |

## 6. 重要規則
- **權限限制**：無。此端點公開存取。
- **不可暴露資訊**：避免在版本號字串中洩漏內部 IP、主機名稱或資料庫連線字串等敏感系統資訊。

## 7. 錯誤情境
此流程極為簡單，預期的錯誤狀況非常少。

| 情境 | 預期結果 |
|---|---|
| `paymentservice` 應用程式未正確啟動 | 請求無法到達此端點，負載平衡器或閘道器回傳 HTTP 502/503。 |
| 路由設定錯誤 | 觸發 ASP.NET Core 的 HTTP 404 或 405。 |

## 8. 測試重點
由於此流程不涉及寫入或複雜邏輯，主要在於確認端點可用性。

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| `API-VER-01` | API Test | 直接對 `/api/version` 發出 GET 請求 | HTTP 200，回應內容為非空字串。 |
| `API-VER-02` | Smoke Test | 部署後自動化測試確認端點存活 | 能成功取得版本號，無例外錯誤。 |

## 9. 高風險區域
- **無**。此為唯讀、無狀態、無相依性的公開端點，風險極低。

## 10. 常見錯誤
- **新人疑慮**：誤認為所有 `/api/*` 路徑都需驗證。此端點在 README 中明確標示為不需要驗證。（**Evidence**: README_API_Table）
- **AI 誤判**：AI 可能基於一般安全原則，預設為所有 API 加上權限檢查邏輯。在生成此類端點程式碼時，應明確標註 `[AllowAnonymous]`。

## 11. Evidence
| 類型 | 來源 |
|---|---|
| API | README: `GET /api/version`，標示為「不需要驗證」 |
| 實作細節 | 需人工確認。現有文件無 VersionController 或 VersionService 的 source code evidence。 |