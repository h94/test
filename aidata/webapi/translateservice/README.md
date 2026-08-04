# TranslateService 內部服務目錄

## 概述
`TranslateService` 是基於 .NET 6 的 Web API，提供多語系關鍵字（Keyword）翻譯管理服務。支援關鍵字的新增、修改、查詢、翻譯（含 Google 翻譯建議）及 Redis 快取刷新。部署於 Docker Swarm 叢集（PRD 環境），Portainer 服務名稱為 `translateservice`。

## 主要功能
- **關鍵字管理**：CRUD 操作單一或批次關鍵字，支援分頁、模糊搜尋與分類（Group）篩選
- **多國翻譯查詢**：輸入繁體中文關鍵字與目標國家代碼（如 en-us, zh-cn），回傳對應翻譯內容（資料源：Redis 快取）
- **翻譯建議（Suggest）**：透過 Google Translate API 或 CHTCHSConv（繁簡轉換）自動產生翻譯建議，支援指定來源與目標語系
- **快取刷新**：可針對單一關鍵字或全部關鍵字手動刷新 Redis 快取內容
- **CSV 匯出**：依條件匯出關鍵字與多國翻譯資料

## 技術棧
- **語言／框架**：C# .NET 6 (WebApi)
- **資料庫**：MySQL（ECFramework.ECService 架構）
- **快取**：Redis（透過 IRedisManager / ECCore 操作）
- **日誌**：Kafka（IKafkaLogger）
- **翻譯引擎**：Google Cloud Translation API + CHTCHSConv（繁簡轉換）
- **容器化**：Docker (Linux, .NET 6 SDK)
- **編排**：Docker Swarm（Portainer 管理，服務名稱 `translateservice`）

## 組態與部署注意
- **環境變數**：時區已設為 `Asia/Taipei`；注意需設定 MySQL、Redis、Kafka 連線字串（透過 `ECCore.DefaultAppSettings` 繼承讀取）
- **Google 服務帳號**：金鑰檔案 `17ec39fef22d.json` 內嵌於專案目錄，用於 Google Translate API 驗證（請勿提交至公開儲存庫）
- **通訊埠**：Container 內部暴露 5000 Port，外部依 Swarm 服務設定對應
- **建置方式**：使用 Dockerfile 進行 dotnet publish 後複製 `bin/Debug/net6.0/` 與 `wwwroot/` 目錄
- **相依元件**：需確保 MySQL、Redis、Kafka 服務正常運作

## 相關連結
- **GitLab 儲存庫**：`https://git.zbdigital.net/biz/translateservice.git`
- **Portainer 服務**：`PRD_Docker_Swarm > swarm > translateservice`
- **API 文件**：可參考 `TranslateService.xml`（內含控制器端點說明）