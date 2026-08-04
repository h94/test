# GameTools — 內部服務目錄

## 概述
GameTools 是一套基於 **Blazor WebAssembly** 的內部前端工具，主要用於管理與維護遊戲賽事資料。系統透過 REST API 與後端服務互動，提供賽事、聯盟、隊伍的合併、編輯、分割、翻譯及強制合併等功能，支援多站台資料比對與操作。

## 主要功能
- **賽事管理**：檢視、編輯、刪除、強制合併賽事資料，支援依球種、日期、時間篩選。
- **聯盟管理**：合併原始聯盟、編輯聯盟名稱映射、刪除聯盟。
- **隊伍管理**：合併原始隊伍、編輯隊伍名稱映射、刪除隊伍。
- **站台資料管理**：管理各站台的原始聯盟與原始隊伍，支援取消合併、編輯名稱映射。
- **強制合併**：針對特定聯盟、隊伍、賽事進行強制合併操作。
- **翻譯建議**：串接翻譯 API (`TranslateApiBaseUrl`)，提供多語系名稱建議。
- **操作記錄**：查閱 API 操作日誌與錯誤訊息。
- **單元測試**：使用 xUnit + Moq 對核心邏輯進行測試。

## 技術棧
| 類別 | 技術 |
|------|------|
| 前端框架 | Blazor WebAssembly (.NET 6) |
| 後端通訊 | Flurl.Http / Flurl |
| 序列化 | Newtonsoft.Json |
| 單元測試 | xUnit, Moq |
| 專案結構 | Solution 包含 `GameTools` (Blazor 前端) 與 `UnitTestProject` (測試) |
| 容器化 | Docker (Linux 基底映像) |
| 部署環境 | Docker Swarm (PRD) |

## 組態與部署注意
- **環境變數**：部署時需設定 `ApiUrl` 變數（對應 `AppState.ApiUrl`），支援三種預設位址：
  - 本機開發閘道：`http://192.168.9.232/pricecenter/api`
  - 正式環境閘道：`http://192.168.55.60/pricecenter/api`
  - 公開域名：`https://ls.zbdigital.net/api`
  實際使用位址需依部署環境指定。
- **容器建置**：使用 `dotnet publish` 產出 WebAssembly 靜態檔，以 Dockerfile 建置 Linux 容器。
- **Portainer 管理**：服務已註冊於 Portainer，對應 Key `PRD_Docker_Swarm|swarm|gametools|gametools_GameTools`。
- **資料庫與 API**：GameTools 本身不直接連接資料庫，所有資料查詢與操作均透過後端 PriceCenter REST API 進行，請確保 API 服務正常運作。
- **安全注意**：`AppState.cs` 中包含測試用帳號密碼，正式環境應移除或使用外部機密管理。

## 相關連結
- **GitLab 倉庫**：[https://git.zbdigital.net/biz/gametools.git](https://git.zbdigital.net/biz/gametools.git)
- **Portainer**：請洽維運團隊取得存取權限
- **API 文件**：請參考 PriceCenter API 規格