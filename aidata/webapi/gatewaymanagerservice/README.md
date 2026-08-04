# GatewayManagerService 內部服務目錄

## 概述

GatewayManagerService 是一個基於 .NET 6 的 Web API 容器化服務，負責管理 API 閘道的設定、日誌查詢及團隊協作報表。它整合了 MySQL、Kafka、Jira 與郵件服務，提供統一的閘道管理與維運監控介面。

## 主要功能

- **API 閘道管理**  
  - 新增、查詢、更新 API 路由、叢集分配、團隊開關設定  
  - 支援多環境（Local、PRE、PRD 等）組態  
  - 自動補齊叢集與團隊對應關係  

- **日誌查詢與報表**  
  - 存取日誌（Access Log）查詢（依時間、URI、狀態碼、回應時間等過濾）  
  - 應用程式日誌（App Log）查詢與詳細內容檢視  
  - 日誌統計報表與即時異常監控（錯誤次數、預警）  

- **Jira 整合**  
  - 取得 Sprint 及其 Issue 進度、子任務完成度  
  - 產生週報（工時統計、專案/訓練/內務/線上問題占比）  
  - 年度 KPI 報表（Bug 數、PRD Bug 數）  

- **郵件通知**  
  - 自動寄送週報郵件（HTML 格式，包含 Sprint 進度與工時報表）  

## 技術棧

- **語言與框架**：C# / .NET 6 / ASP.NET Core Web API  
- **容器**：Docker（基礎映像 `mcr.microsoft.com/dotnet/sdk:6.0`）  
- **資料庫**：MySQL（透過 IGMProvider 操作）  
- **訊息佇列**：Kafka（用於日誌傳輸與警示）  
- **外部整合**：Jira REST API、MailKit  
- **內部套件**：ECCore / ECFramework.ECService（依賴注入、設定管理）  

## 組態與部署注意

- **Port**：容器內部監聽 **5000**（Dockerfile EXPOSE 5000）  
- **時區**：強制設定為 `Asia/Taipei`（`ENV TZ=Asia/Taipei`）  
- **DNS 設定**：於 Dockerfile 中執行 `echo 'options single-request-reopen' >> /etc/resolv.conf`，解決 DNS 查詢問題  
- **環境變數**：需提供 `ECCore` 框架所需的連線字串與 Kafka 設定（透過 appsettings.json 或環境變數）  
- **相依服務**：需確保 MySQL、Kafka、Jira（可選）、SMTP（可選）可連線  

## 相關連結

- **GitLab Repository**：[https://git.zbdigital.net/biz/gatewaymanagerservice.git](https://git.zbdigital.net/biz/gatewaymanagerservice.git)  
- **Portainer Key**：`SRV60|container|gatewaymanagerservice`