# TranslateService

## 概述
TranslateService 為內部多語系翻譯管理服務，提供關鍵詞（Keyword）的集中管理、多國語系翻譯儲存、自動補齊翻譯建議（整合 Google 翻譯），並透過 REST API 對外暴露查詢與維護功能。服務附有簡易 MVC 後台頁面，可進行關鍵詞清單瀏覽、編輯與 CSV 匯出。

## 主要功能
- **關鍵詞管理**：新增、修改、刪除關鍵詞，並維護各語系翻譯內容。
- **多語系支援**：可動態增加國別與語系，自動補齊缺失翻譯。
- **翻譯查詢 API**：提供 `GET /api/v1/translate` 指定目標語系與多個關鍵詞，取得對應翻譯。
- **Google 翻譯建議**：呼叫外部翻譯服務取得建議內容，加速人工維護。
- **分頁與搜尋**：支援依分類、關鍵字模糊查詢的關鍵詞分頁列表。
- **快取刷新**：提供單一關鍵詞或全部快取刷新機制。
- **CSV 匯出**：支援依分類與語系範圍匯出翻譯內容為 CSV 檔案。
- **後台頁面**：簡易 MVC 頁面顯示 Swagger 文件與關鍵詞管理介面。

## 技術棧
- **運行環境**：.NET 6.0
- **容器化**：Docker (Linux 容器)
- **相依套件**：`ECCORE`（內部組態管理）、`ZooKeeper`（可能用於分散式協調）
- **外部服務**：Google 翻譯 API（建議功能）
- **部署平台**：Docker Swarm (PRD)

## 組態與部署注意
- **Dockerfile** 基於 `mcr.microsoft.com/dotnet/sdk:6.0`，運行時暴露端口 `5000`。
- 容器內設定時區為 `Asia/Taipei`，確保日誌時間正確。
- 應用程式依賴 `ECCORE` 讀取環境相關組態，部署時需確保 `appsettings.json` 或環境變數正確設定（如版本號、ZooKeeper 連線字串、翻譯服務金鑰等）。
- 建議掛載 `wwwroot` 目錄以保存靜態資源（如有更新需求）。
- 使用 `dotnet TranslateService.dll` 啟動，不依賴 IIS。

## 相關連結
- 原始碼版本庫：`https://git.zbdigital.net/Biz/translateservice.git`
- 服務管理：Portainer（PRD_Docker_Swarm / container / translateservice）