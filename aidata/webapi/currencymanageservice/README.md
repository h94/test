# CurrencyManageService

## 概述
CurrencyManageService 是一個內部貨幣管理服務，負責監控多種貨幣、外匯、股票資料的即時狀態，並管理分散式爬取任務的分發與機器健康度。該服務部署於 Docker Swarm 叢集，提供 Web API 及簡易管理介面。

## 主要功能
- **資料狀態檢查**：定期檢查幣種、外匯、穩定幣、各國股票解析器的最新更新時間，超時以紅字警示。
- **機器狀態管理**：收集各機器的控制器、代理程式、解析器等工作狀態，並視需要更新至資料庫。
- **頁面分發與排程**：根據頁面處理器的心跳與工作量，動態分配爬取任務給可用機器，確保資源有效利用。
- **儀表板呈現**：提供視覺化頁面，顯示各機器運作概況與資料延遲情形。

## 技術棧
- **開發框架**：.NET 6、ASP.NET Core Web API + MVC + Razor Pages
- **核心依賴**：ECCore、ECFramework.ECService（內部框架）
- **容器化**：Docker（.NET 6 SDK 映像），部署於 Docker Swarm
- **時區設定**：`Asia/Taipei`
- **暴露埠號**：`5000`

## 組態與部署注意
- **Dockerfile** 使用 `mcr.microsoft.com/dotnet/sdk:6.0` 作為基底，並將執行檔複製至 `/app`，工作目錄設為 `/app`。
- 需注意容器時區已固定為 `Asia/Taipei`，若主機時區不同可能影響時間判斷邏輯。
- 服務依賴內部 NuGet 套件 `ECCore` 與 `ECFramework.ECService`，建置時須確保可存取對應套件來源。
- 部署時請確認 `appsettings.json` 中的機器對應、檢查伺服器列表、儀表板站台等組態正確。

## 相關連結
- **GitLab 儲存庫**：[https://git.zbdigital.net/Currency/currencymanageservice.git](https://git.zbdigital.net/Currency/currencymanageservice.git)