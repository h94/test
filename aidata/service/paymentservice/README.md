# PaymentService

## 概述
PaymentService 為內部核心支付服務，負責處理運動賽事、新彩、活動商品等多站台的交易金流、訂閱儲值方案、第三方支付（綠界）、報表分潤及提領等功能。服務以 ASP.NET Core 8.0 建置，並在 Docker Swarm 叢集中以容器方式運行，由 Portainer 統一管理。

## 主要功能
- **第三方支付整合**  
  支援綠界（ECPay）多種付款方式：信用卡一次付清／定期定額、WebATM、ATM 虛擬帳號、超商代碼、超商條碼，具備訂單建立、狀態驗證與更新回呼。
- **活動商品管理**  
  活動商品（ActivityProduct）之批次匯入、查詢、更新與刪除；會員兌換紀錄（RedeemLog）與提領紀錄（WithdrawLog）的新增、狀態變更及查詢。
- **運動站台服務**  
  - 訂閱方案（SubPlan）CRUD，支援快取讀取。  
  - 交易訂單（TradeOrder）建立、查詢與更新。  
  - 提領紀錄管理，依日期區間、帳號查詢，並更新提領結果。  
  - 月報、分潤報表、推薦報表、推薦分潤報表的產生、查詢與維護。
  - 付款方式（PayMethod）管理，可動態調整方案可用的金流選項。
- **新彩（NewLottery）服務**  
  - 彩池抽成（BetPoolCommission）紀錄新增與查詢。  
  - 儲值方案（RechargePlan）CRUD 與快取讀取。  
  - 交易訂單（TradeOrder）管理，介面與運動站台類似但獨立實作。
- **股票服務**  
  - 股票訂閱方案（StockSubPlan）查詢。  
  - 股票交易紀錄（StockTradeOrder）分頁查詢、依帳號查詢、狀態更新。
- **系統維運**  
  - 自動建立資料表（含運動站台與新彩相關表）。  
  - 心跳檢查 `GET /api/heart` 與版本查詢 `GET /api/version`。  
  - 排程用清除端點：刪除運動交握紀錄、手動清除分潤報表（供 xxl-job 觸發）。

## 技術棧
- **執行環境**：.NET 8、ASP.NET Core Web API
- **語言**：C#
- **容器化**：Docker（基於 `mcr.microsoft.com/dotnet/sdk:8.0`）
- **編排與管理**：Docker Swarm + Portainer
- **依賴注入**：透過 Interface 定義服務合約，於 DI 容器註冊實作
- **快取**：部分讀取介面支援 `cache` 參數，底層應使用 Redis 或記憶體快取
- **時區**：設定為 `Asia/Taipei`

## 組態與部署注意
- **服務埠號**：容器內部暴露 `5000`，對外需透過 Swarm 網路或反向代理對應。
- **時區設定**：Dockerfile 中強制設定 `TZ=Asia/Taipei`，確保日誌與時間相關邏輯正確。
- **建置與發佈**：Dockerfile 直接複製 `bin/Debug/net8.0/` 產物，正式部署應改用 `Release` 組態或透過 CI 產出發佈檔。
- **組態檔**：依賴 `appsettings.json`，其中 `Version` 與 `Environment` 區段用於 `/api/version` 端點顯示；部署時需掛載正確的環境組態。
- **資料庫初始化**：首次部署須呼叫 `POST /api/v1/system/autocreatetable`，或由排程／初始腳本觸發自動建表。
- **健康檢查**：Kubernetes/Swarm 可配置 liveness probe 為 `GET /api/heart`，就緒探針可選用 `GET /api/version`。
- **外部排程依賴**：部分清除任務（如刪除交握紀錄）對外提供端點供 xxl-job 呼叫，需確保網路可達。

## 相關連結
- **原始碼倉庫**：  
  [https://git.zbdigital.net/Biz/paymentservice.git](https://git.zbdigital.net/Biz/paymentservice.git)